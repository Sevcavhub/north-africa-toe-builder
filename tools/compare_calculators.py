#!/usr/bin/env python3
"""
Compare battlegroup_stat_calculator.py results with existing validated calculators
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Add scripts to path
project_root = Path(__file__).parent.parent
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path / "battlegroup" / "conversion"))
sys.path.insert(0, str(scripts_path / "battlegroup" / "points"))

# Import existing validated calculators
try:
    from he_calculator import calculate_he_effect
    from movement_calculator import calculate_movement
    print("[OK] Imported existing calculators")
except ImportError as e:
    print(f"[ERROR] Could not import calculators: {e}")
    sys.exit(1)

DB_PATH = project_root / "database" / "master_database.db"

def extract_caliber_from_name(name: str) -> Optional[int]:
    """Extract caliber from equipment name."""
    import re

    patterns = [
        r'(\d+)mm',
        r'(\d+\.?\d*)cm',
        r'(\d+)-?pounder',
        r'(\d+)pdr',
    ]

    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            if 'cm' in pattern:
                value *= 10
            if 'pounder' in pattern or 'pdr' in pattern:
                pounder_to_mm = {2: 40, 6: 57, 17: 76.2, 25: 87.6}
                value = pounder_to_mm.get(int(value), value * 25)
            return int(value)
    return None

def main():
    conn = sqlite3.connect(DB_PATH)

    print("=" * 80)
    print("CALCULATOR COMPARISON TEST")
    print("=" * 80)

    # Create temp table for validated calculator results
    print("\n1. Creating temp table for validated calculator results...")
    conn.execute("DROP TABLE IF EXISTS equipment_stats_battlegroup_validated")
    conn.execute("""
        CREATE TABLE equipment_stats_battlegroup_validated (
            stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER NOT NULL,
            armor_front TEXT,
            armor_side TEXT,
            armor_rear TEXT,
            movement_offroad INTEGER,
            movement_road INTEGER,
            he_rating TEXT,
            ap_rating TEXT,
            weapon_description TEXT,
            points INTEGER,
            battle_rating INTEGER,
            special_rules TEXT,
            conversion_confidence REAL,
            conversion_method TEXT,
            generated_date TEXT,
            notes TEXT,
            UNIQUE(master_id)
        )
    """)
    print("[OK] Temp table created")

    # Get North Africa equipment
    print("\n2. Loading North Africa equipment...")
    query = """
    SELECT em.master_id, em.display_name, em.equipment_category,
           em.historical_specs_json
    FROM equipment_master_new em
    JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
    WHERE etu.theater = 'north_africa'
    ORDER BY em.master_id
    """

    equipment = conn.execute(query).fetchall()
    print(f"[OK] Loaded {len(equipment)} items")

    # Run validated calculators
    print("\n3. Running validated calculators on all items...")

    stats = {
        'total': 0,
        'he_calculated': 0,
        'movement_calculated': 0,
        'both_calculated': 0
    }

    for master_id, display_name, category, specs_json in equipment:
        stats['total'] += 1

        specs = json.loads(specs_json) if specs_json else {}

        # Calculate HE rating using validated calculator
        he_rating = None
        weapon_desc = None

        # Strategy 1: Check for bg_reference_vehicles_weapons
        if 'bg_reference_vehicles_weapons' in specs:
            try:
                weapons = json.loads(specs['bg_reference_vehicles_weapons']) if isinstance(specs['bg_reference_vehicles_weapons'], str) else specs['bg_reference_vehicles_weapons']
                if weapons and isinstance(weapons, list):
                    for weapon in weapons:
                        if isinstance(weapon, dict):
                            weapon_name = weapon.get('weapon', '')
                            if weapon_name and weapon_name != 'MG' and 'MG' not in weapon_name:
                                caliber = extract_caliber_from_name(weapon_name)
                                if caliber:
                                    he_result = calculate_he_effect(caliber, gun_name=weapon_name)
                                    he_rating = he_result['format']
                                    weapon_desc = f"HE {he_rating}"
                                    break
            except:
                pass

        # Strategy 2: For artillery, extract from display name
        if not he_rating and category in ['artillery', 'gun', 'anti_tank_gun', 'anti_aircraft_gun', 'mortar']:
            caliber = extract_caliber_from_name(display_name)
            if caliber:
                he_result = calculate_he_effect(caliber, gun_name=display_name)
                he_rating = he_result['format']
                weapon_desc = f"HE {he_rating}"

        if he_rating:
            stats['he_calculated'] += 1

        # Calculate movement using validated calculator
        movement_offroad = None
        movement_road = None

        # Try vehicle name lookup
        movement_result = calculate_movement(vehicle_name=display_name, vehicle_type=category)
        if movement_result and movement_result.get('confidence') in ['high', 'medium']:
            movement_offroad = movement_result['off_road']
            movement_road = movement_result['road']
            stats['movement_calculated'] += 1

        if he_rating and movement_offroad:
            stats['both_calculated'] += 1

        # Insert into validated table
        conn.execute("""
            INSERT INTO equipment_stats_battlegroup_validated (
                master_id, movement_offroad, movement_road,
                he_rating, weapon_description,
                conversion_method, generated_date, notes
            ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
        """, (
            master_id, movement_offroad, movement_road,
            he_rating, weapon_desc,
            'validated_calculators',
            f'HE: {he_rating is not None}, Movement: {movement_offroad is not None}'
        ))

    conn.commit()

    print(f"\n[OK] Validated calculator stats:")
    print(f"  Total items: {stats['total']}")
    print(f"  HE calculated: {stats['he_calculated']} ({stats['he_calculated']/stats['total']*100:.1f}%)")
    print(f"  Movement calculated: {stats['movement_calculated']} ({stats['movement_calculated']/stats['total']*100:.1f}%)")
    print(f"  Both calculated: {stats['both_calculated']} ({stats['both_calculated']/stats['total']*100:.1f}%)")

    # Compare results
    print("\n4. Comparing results...")
    print("=" * 80)

    comparison_query = """
    SELECT
        em.master_id,
        em.display_name,
        em.equipment_category,
        -- My results
        esb.movement_offroad as my_movement_off,
        esb.movement_road as my_movement_road,
        esb.he_rating as my_he,
        esb.weapon_description as my_weapon_desc,
        -- Validated results
        esb_val.movement_offroad as val_movement_off,
        esb_val.movement_road as val_movement_road,
        esb_val.he_rating as val_he,
        esb_val.weapon_description as val_weapon_desc
    FROM equipment_master_new em
    JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
    LEFT JOIN equipment_stats_battlegroup esb ON em.master_id = esb.master_id
    LEFT JOIN equipment_stats_battlegroup_validated esb_val ON em.master_id = esb_val.master_id
    WHERE etu.theater = 'north_africa'
    ORDER BY em.master_id
    """

    comparison = {
        'total': 0,
        'movement_match': 0,
        'movement_differ': 0,
        'movement_mine_only': 0,
        'movement_validated_only': 0,
        'he_match': 0,
        'he_differ': 0,
        'he_mine_only': 0,
        'he_validated_only': 0,
        'differences': []
    }

    for row in conn.execute(comparison_query):
        (master_id, name, category,
         my_mv_off, my_mv_road, my_he, my_weapon,
         val_mv_off, val_mv_road, val_he, val_weapon) = row

        comparison['total'] += 1

        # Compare movement
        if my_mv_off and val_mv_off:
            if my_mv_off == val_mv_off and my_mv_road == val_mv_road:
                comparison['movement_match'] += 1
            else:
                comparison['movement_differ'] += 1
                comparison['differences'].append({
                    'id': master_id,
                    'name': name,
                    'field': 'movement',
                    'mine': f"{my_mv_off}\"{my_mv_road}\"",
                    'validated': f"{val_mv_off}\"{val_mv_road}\""
                })
        elif my_mv_off and not val_mv_off:
            comparison['movement_mine_only'] += 1
        elif val_mv_off and not my_mv_off:
            comparison['movement_validated_only'] += 1

        # Compare HE
        if my_he and val_he:
            if my_he == val_he:
                comparison['he_match'] += 1
            else:
                comparison['he_differ'] += 1
                comparison['differences'].append({
                    'id': master_id,
                    'name': name,
                    'field': 'HE',
                    'mine': my_he,
                    'validated': val_he
                })
        elif my_he and not val_he:
            comparison['he_mine_only'] += 1
        elif val_he and not my_he:
            comparison['he_validated_only'] += 1

    # Print results
    print("\nMOVEMENT COMPARISON:")
    print(f"  Exact matches: {comparison['movement_match']}")
    print(f"  Different values: {comparison['movement_differ']}")
    print(f"  Mine only: {comparison['movement_mine_only']}")
    print(f"  Validated only: {comparison['movement_validated_only']}")

    print("\nHE/WEAPON COMPARISON:")
    print(f"  Exact matches: {comparison['he_match']}")
    print(f"  Different values: {comparison['he_differ']}")
    print(f"  Mine only: {comparison['he_mine_only']}")
    print(f"  Validated only: {comparison['he_validated_only']}")

    # Show sample differences
    if comparison['differences']:
        print(f"\nSAMPLE DIFFERENCES (first 20):")
        print("-" * 80)
        for diff in comparison['differences'][:20]:
            print(f"[{diff['id']}] {diff['name'][:40]:40} {diff['field']:10}")
            print(f"  Mine:      {diff['mine']}")
            print(f"  Validated: {diff['validated']}")

    # Check what I added that wasn't in validated
    print("\n5. Checking for NEW functionality...")
    print("=" * 80)

    # Check if I calculated anything validated didn't
    new_coverage = conn.execute("""
        SELECT COUNT(*) FROM equipment_stats_battlegroup esb
        WHERE esb.weapon_description IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM equipment_stats_battlegroup_validated esb_val
            WHERE esb_val.master_id = esb.master_id
            AND esb_val.weapon_description IS NOT NULL
        )
    """).fetchone()[0]

    print(f"Items where I calculated weapons but validated didn't: {new_coverage}")

    # Check armor (validated calculators don't do armor)
    armor_count = conn.execute("""
        SELECT COUNT(*) FROM equipment_stats_battlegroup
        WHERE armor_front IS NOT NULL
    """).fetchone()[0]

    print(f"Items with armor values (NEW): {armor_count}")

    # Check points/BR (validated has points_calculator but not run here)
    points_count = conn.execute("""
        SELECT COUNT(*) FROM equipment_stats_battlegroup
        WHERE points IS NOT NULL
    """).fetchone()[0]

    print(f"Items with points/BR values (NEW): {points_count}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_with_data = comparison['movement_match'] + comparison['movement_differ']
    if total_with_data > 0:
        match_rate = comparison['movement_match'] / total_with_data * 100
        print(f"Movement match rate: {match_rate:.1f}% ({comparison['movement_match']}/{total_with_data})")

    total_he_data = comparison['he_match'] + comparison['he_differ']
    if total_he_data > 0:
        he_match_rate = comparison['he_match'] / total_he_data * 100
        print(f"HE match rate: {he_match_rate:.1f}% ({comparison['he_match']}/{total_he_data})")

    print(f"\nNEW functionality added:")
    print(f"  - Armor conversion: {armor_count} items (NOT in validated calculators)")
    print(f"  - Points/BR estimation: {points_count} items (calculator exists but not integrated)")
    print(f"  - Additional weapon extraction: {new_coverage} items")

    conn.close()
    print("\n[COMPLETE] Comparison test finished")

if __name__ == "__main__":
    main()
