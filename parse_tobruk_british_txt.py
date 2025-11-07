#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse Tobruk British.txt and import into copy tables for comparison

Creates:
- bg_reference_vehicles_txt_import
- bg_reference_guns_txt_import

Then compares with manually entered British data in original tables.
"""

import sys
import io
import re
import sqlite3
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_tobruk_british_txt(file_path):
    """
    Parse Tobruk British.txt file into structured vehicle and gun data

    The file has a specific table format with headers:
    VEHICLE | MOVEMENT | ARMOUR | ARMAMENT
    Off-Road | Road | Special | Front | Side | Rear | Weapon | Mount | Ammo
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove BOM
    content = content.replace('\ufeff', '')

    vehicles = []
    guns = []

    print("📖 Parsing Tobruk British.txt...")
    print("="*70)

    # Split into lines
    lines = content.split('\n')

    # Current vehicle being parsed
    current_vehicle = None
    current_section = None
    parsing_mode = None  # 'vehicle' or 'gun'

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Detect section headers
        if 'LIGHT TANKS' in line:
            current_section = 'LIGHT TANKS'
            parsing_mode = 'vehicle'
            print(f"\n🏷️  Section: {current_section}")
            continue
        elif 'INFANTRY TANKS' in line:
            current_section = 'INFANTRY TANKS'
            parsing_mode = 'vehicle'
            print(f"\n🏷️  Section: {current_section}")
            continue
        elif 'CRUISER TANKS' in line:
            current_section = 'CRUISER TANKS'
            parsing_mode = 'vehicle'
            print(f"\n🏷️  Section: {current_section}")
            continue
        elif 'ARMOURED CARS' in line:
            current_section = 'ARMOURED CARS'
            parsing_mode = 'vehicle'
            print(f"\n🏷️  Section: {current_section}")
            continue
        elif 'SOFT-SKINNED VEHICLES' in line:
            current_section = 'SOFT-SKINNED VEHICLES'
            parsing_mode = 'vehicle'
            print(f"\n🏷️  Section: {current_section}")
            continue
        elif "PORTEE'D GUNS" in line or 'PORTEE' in line:
            current_section = 'PORTEE GUNS'
            parsing_mode = 'vehicle'
            print(f"\n🏷️  Section: {current_section}")
            continue
        elif 'ANTI-TANK GUNS' in line:
            current_section = 'ANTI-TANK GUNS'
            parsing_mode = 'gun'
            print(f"\n🏷️  Section: {current_section}")
            continue
        elif 'FIELD ARTILLERY' in line:
            current_section = 'FIELD ARTILLERY'
            parsing_mode = 'gun'
            print(f"\n🏷️  Section: {current_section}")
            continue
        elif 'ANTI-AIRCRAFT GUNS' in line:
            current_section = 'ANTI-AIRCRAFT GUNS'
            parsing_mode = 'gun'
            print(f"\n🏷️  Section: {current_section}")
            continue

        # Skip header lines
        if 'VEHICLE' in line or 'MOVEMENT' in line or 'ARMOUR' in line or 'ARMAMENT' in line:
            continue
        if 'Off-Road' in line or 'Road' in line or 'Special' in line:
            continue
        if 'Front' in line or 'Side' in line or 'Rear' in line:
            continue
        if 'Weapon' in line or 'Mount' in line or 'Ammo' in line:
            continue

        # Try to detect vehicle/gun names (usually longer names, not stats)
        # Vehicle names: Vickers, Matilda, Valentine, M3, A9, etc.
        vehicle_name_patterns = [
            r'^(Vickers\s+VI?\s*[A-Z]?(?:-[A-Z])?)',
            r'^(M3\s+.*?Honey.*?)',
            r'^(Matilda\s+II(?:\s+CS)?)',
            r'^(Valentine\s+II)',
            r'^(A\d+(?:\s+\w+)?)',
            r'^(Crusader\s+\w+)',
            r'^(Morris\s+\w+)',
            r'^(Austin\s+\w+)',
            r'^(Bedford\s+\w+)',
            r'^(Scammel\s+\w+)',
            r'^(Hippo\s+\w+)',
            r'^(Matador\s+\w+)',
            r'^(Chev.*?\d+\s*cwt)',
            r'^(Humber\s+\w+)',
            r'^(Daimler\s+\w+)',
            r'^(Marmon\s+\w+)',
        ]

        gun_name_patterns = [
            r'^(\d+\s*pdr(?:\s+\w+)?)',
            r'^(\d+mm(?:\s+\w+)?)',
            r'^(Boys\s+\w+)',
            r'^(\d+\s*mm)',
            r'^(\d+\s*pdr)',
        ]

        # Check if this is a vehicle name
        is_vehicle_name = False
        if parsing_mode == 'vehicle':
            for pattern in vehicle_name_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    vehicle_name = match.group(1).strip()

                    # Create new vehicle entry
                    current_vehicle = {
                        'name': vehicle_name,
                        'nation': 'British',
                        'vehicle_type': current_section,
                        'year_range': '1940-41',
                        'off_road_inches': None,
                        'road_inches': None,
                        'armor_front': None,
                        'armor_side': None,
                        'armor_rear': None,
                        'weapons': [],
                        'special_rules': [],
                        'source_file': 'Tobruk British.txt',
                        'extraction_method': 'automated_txt_parsing'
                    }

                    print(f"   🚗 Found vehicle: {vehicle_name}")
                    is_vehicle_name = True
                    break

        # Check if this is a gun name
        elif parsing_mode == 'gun':
            for pattern in gun_name_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    gun_name = match.group(1).strip()

                    print(f"   🔫 Found gun: {gun_name}")
                    # Guns are handled differently - will extract from their stat lines
                    is_vehicle_name = False
                    break

        # If not a name, try to extract stats
        if not is_vehicle_name and current_vehicle:
            # Try to extract movement values (e.g., 12" 18")
            movement_match = re.findall(r'(\d+)"', line)
            if len(movement_match) >= 2 and not current_vehicle['off_road_inches']:
                current_vehicle['off_road_inches'] = int(movement_match[0])
                current_vehicle['road_inches'] = int(movement_match[1])

            # Try to extract armor values (letters I-O)
            armor_match = re.findall(r'\b([I-O])\b', line)
            if len(armor_match) >= 2:
                if not current_vehicle['armor_front']:
                    current_vehicle['armor_front'] = armor_match[0] if len(armor_match) > 0 else None
                    current_vehicle['armor_side'] = armor_match[1] if len(armor_match) > 1 else armor_match[0]
                    current_vehicle['armor_rear'] = armor_match[2] if len(armor_match) > 2 else armor_match[1] if len(armor_match) > 1 else armor_match[0]

            # Try to extract weapons
            weapon_patterns = [
                r'(\d+\s*pdr)',
                r'(\d+mm[A-Z]*\d*)',
                r'\b(MG)\b',
                r'(Besa)',
                r'(\d+\s*mm)',
            ]

            for pattern in weapon_patterns:
                weapon_matches = re.findall(pattern, line, re.IGNORECASE)
                for weapon in weapon_matches:
                    if weapon not in current_vehicle['weapons']:
                        current_vehicle['weapons'].append(weapon)

        # If we detect a new vehicle name, save the previous one
        if is_vehicle_name and current_vehicle:
            # Check if we have enough data
            if current_vehicle.get('name'):
                vehicles.append(current_vehicle)

    # Add the last vehicle
    if current_vehicle and current_vehicle.get('name'):
        vehicles.append(current_vehicle)

    print(f"\n{'='*70}")
    print(f"✅ Parsing complete!")
    print(f"   Vehicles extracted: {len(vehicles)}")
    print(f"   Guns extracted: {len(guns)}")

    return vehicles, guns

def create_copy_tables(conn):
    """Create copy tables for txt import"""

    cursor = conn.cursor()

    print("\n📋 Creating copy tables...")

    # Drop if exists
    cursor.execute("DROP TABLE IF EXISTS bg_reference_vehicles_txt_import")
    cursor.execute("DROP TABLE IF EXISTS bg_reference_guns_txt_import")

    # Create vehicles copy table (same schema)
    cursor.execute("""
        CREATE TABLE bg_reference_vehicles_txt_import (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            nation TEXT,
            year_range TEXT,
            vehicle_type TEXT,
            off_road_inches INTEGER,
            road_inches INTEGER,
            special_movement TEXT,
            armor_front TEXT,
            armor_side TEXT,
            armor_rear TEXT,
            weapons TEXT,
            special_rules TEXT,
            source_file TEXT,
            source_page TEXT,
            extraction_confidence TEXT,
            notes TEXT,
            source_battle TEXT,
            source_date TEXT,
            source_document TEXT,
            extraction_notes TEXT,
            master_id INTEGER,
            extraction_method TEXT,
            screenshot_file TEXT,
            armor_modifier TEXT,
            armor_side_schurzen TEXT
        )
    """)

    # Create guns copy table (same schema)
    cursor.execute("""
        CREATE TABLE bg_reference_guns_txt_import (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            nation TEXT,
            caliber_mm INTEGER,
            barrel_length TEXT,
            he_dice INTEGER,
            he_target TEXT,
            ap_0_10 INTEGER,
            ap_10_20 INTEGER,
            ap_20_30 INTEGER,
            ap_30_40 INTEGER,
            ap_40_50 INTEGER,
            ap_50_70 INTEGER,
            points_cost INTEGER,
            battle_rating INTEGER,
            source_file TEXT,
            source_page TEXT,
            extraction_confidence TEXT,
            notes TEXT,
            created_at TIMESTAMP,
            source_battle TEXT,
            source_date TEXT,
            unit_experience TEXT,
            source_document TEXT,
            extraction_notes TEXT,
            master_id INTEGER,
            extraction_method TEXT,
            verified_by TEXT,
            verification_date TIMESTAMP,
            screenshot_file TEXT,
            he_10_20 INTEGER,
            he_20_30 INTEGER,
            he_30_40 INTEGER,
            he_40_50 INTEGER,
            he_50_70 INTEGER,
            he_0_10 INTEGER,
            common_name TEXT,
            he_shell_classification TEXT,
            rof INTEGER,
            weapon_category TEXT,
            category_confidence INTEGER,
            gun_role TEXT,
            max_range_inches INTEGER,
            special_rules TEXT,
            import_date TEXT,
            import_source TEXT,
            validation_notes TEXT
        )
    """)

    conn.commit()
    print("✅ Copy tables created")

def import_vehicles(conn, vehicles):
    """Import parsed vehicles into copy table"""

    cursor = conn.cursor()

    print(f"\n📥 Importing {len(vehicles)} vehicles...")

    for vehicle in vehicles:
        # Convert weapons list to JSON or comma-separated string
        weapons_str = ', '.join(vehicle.get('weapons', []))
        special_rules_str = ', '.join(vehicle.get('special_rules', []))

        cursor.execute("""
            INSERT INTO bg_reference_vehicles_txt_import
            (name, nation, year_range, vehicle_type, off_road_inches, road_inches,
             armor_front, armor_side, armor_rear, weapons, special_rules,
             source_file, extraction_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vehicle['name'],
            vehicle['nation'],
            vehicle['year_range'],
            vehicle['vehicle_type'],
            vehicle.get('off_road_inches'),
            vehicle.get('road_inches'),
            vehicle.get('armor_front'),
            vehicle.get('armor_side'),
            vehicle.get('armor_rear'),
            weapons_str,
            special_rules_str,
            vehicle['source_file'],
            vehicle['extraction_method']
        ))

    conn.commit()
    print(f"✅ Imported {len(vehicles)} vehicles")

def compare_with_manual_data(conn):
    """
    Compare txt-imported data with manually entered British data
    Match by vehicle name and compare all fields
    """

    cursor = conn.cursor()

    print(f"\n{'='*70}")
    print("COMPARISON: Manual Entry vs TXT Parsing")
    print(f"{'='*70}\n")

    # Get all British vehicles from manual entry
    cursor.execute("""
        SELECT name, vehicle_type, off_road_inches, road_inches,
               armor_front, armor_side, armor_rear, weapons, special_rules
        FROM bg_reference_vehicles
        WHERE nation LIKE '%British%'
        ORDER BY name
    """)

    manual_vehicles = cursor.fetchall()

    # Get all vehicles from txt import
    cursor.execute("""
        SELECT name, vehicle_type, off_road_inches, road_inches,
               armor_front, armor_side, armor_rear, weapons, special_rules
        FROM bg_reference_vehicles_txt_import
        ORDER BY name
    """)

    txt_vehicles = cursor.fetchall()

    print(f"📊 Dataset Sizes:")
    print(f"   Manual entry: {len(manual_vehicles)} British vehicles")
    print(f"   TXT parsing:  {len(txt_vehicles)} vehicles")

    # Create dictionaries for easier matching
    manual_dict = {v[0]: v for v in manual_vehicles}
    txt_dict = {v[0]: v for v in txt_vehicles}

    # Find matches
    manual_names = set(manual_dict.keys())
    txt_names = set(txt_dict.keys())

    common_names = manual_names & txt_names
    manual_only = manual_names - txt_names
    txt_only = txt_names - manual_names

    print(f"\n📋 Name Matching:")
    print(f"   Common names: {len(common_names)}")
    print(f"   Manual only:  {len(manual_only)}")
    print(f"   TXT only:     {len(txt_only)}")

    if manual_only:
        print(f"\n   ⚠️  In manual but not in TXT ({len(manual_only)}):")
        for name in sorted(list(manual_only))[:10]:
            print(f"      - {name}")
        if len(manual_only) > 10:
            print(f"      ... and {len(manual_only) - 10} more")

    if txt_only:
        print(f"\n   ℹ️  In TXT but not in manual ({len(txt_only)}):")
        for name in sorted(list(txt_only))[:10]:
            print(f"      - {name}")
        if len(txt_only) > 10:
            print(f"      ... and {len(txt_only) - 10} more")

    # Field-by-field comparison for matched names
    print(f"\n{'='*70}")
    print(f"FIELD-BY-FIELD COMPARISON ({len(common_names)} matched vehicles)")
    print(f"{'='*70}\n")

    field_matches = {
        'vehicle_type': 0,
        'off_road_inches': 0,
        'road_inches': 0,
        'armor_front': 0,
        'armor_side': 0,
        'armor_rear': 0,
        'weapons': 0,
        'special_rules': 0
    }

    field_total = len(common_names)

    mismatches = []

    for name in sorted(common_names):
        manual_data = manual_dict[name]
        txt_data = txt_dict[name]

        # Compare each field (indices 1-8)
        field_names = ['vehicle_type', 'off_road_inches', 'road_inches',
                       'armor_front', 'armor_side', 'armor_rear', 'weapons', 'special_rules']

        vehicle_mismatches = []

        for idx, field_name in enumerate(field_names):
            manual_val = manual_data[idx + 1]  # +1 because name is at index 0
            txt_val = txt_data[idx + 1]

            if manual_val == txt_val:
                field_matches[field_name] += 1
            else:
                vehicle_mismatches.append({
                    'field': field_name,
                    'manual': manual_val,
                    'txt': txt_val
                })

        if vehicle_mismatches:
            mismatches.append({
                'name': name,
                'mismatches': vehicle_mismatches
            })

    # Print field match percentages
    print("📊 Field Match Rates:")
    for field_name in field_names:
        if field_total > 0:
            match_pct = (field_matches[field_name] / field_total) * 100
            print(f"   {field_name:20s}: {field_matches[field_name]:3d}/{field_total} ({match_pct:5.1f}%)")

    # Calculate overall match rate
    total_comparisons = field_total * len(field_names)
    total_matches = sum(field_matches.values())
    overall_match_pct = (total_matches / total_comparisons * 100) if total_comparisons > 0 else 0

    print(f"\n✅ OVERALL FIELD MATCH: {total_matches}/{total_comparisons} ({overall_match_pct:.1f}%)")

    # Show detailed mismatches
    if mismatches:
        print(f"\n{'='*70}")
        print(f"DETAILED MISMATCHES ({len(mismatches)} vehicles)")
        print(f"{'='*70}\n")

        for vehicle in mismatches[:15]:  # Show first 15
            print(f"🔍 {vehicle['name']}:")
            for mismatch in vehicle['mismatches']:
                print(f"   {mismatch['field']:20s}: Manual='{mismatch['manual']}' | TXT='{mismatch['txt']}'")
            print()

        if len(mismatches) > 15:
            print(f"   ... and {len(mismatches) - 15} more vehicles with mismatches\n")

    # Save detailed report
    report = {
        'comparison_date': datetime.now().isoformat(),
        'manual_count': len(manual_vehicles),
        'txt_count': len(txt_vehicles),
        'common_names': len(common_names),
        'manual_only_count': len(manual_only),
        'txt_only_count': len(txt_only),
        'manual_only_names': sorted(list(manual_only)),
        'txt_only_names': sorted(list(txt_only)),
        'field_match_rates': {k: f"{v}/{field_total} ({(v/field_total*100):.1f}%)" for k, v in field_matches.items()},
        'overall_match_percentage': overall_match_pct,
        'total_comparisons': total_comparisons,
        'total_matches': total_matches,
        'mismatch_count': len(mismatches),
        'mismatches': mismatches
    }

    import json
    with open('tobruk_british_manual_vs_txt_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved: tobruk_british_manual_vs_txt_comparison.json")

    return report

def main():
    print("="*70)
    print("Tobruk British TXT Parser & Comparison Tool")
    print("="*70)

    txt_file = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Tobruk British.txt"
    db_file = r"D:\north-africa-toe-builder\database\master_database.db"

    # Parse txt file
    vehicles, guns = parse_tobruk_british_txt(txt_file)

    # Connect to database
    conn = sqlite3.connect(db_file)

    # Create copy tables
    create_copy_tables(conn)

    # Import vehicles
    import_vehicles(conn, vehicles)

    # Run comparison
    report = compare_with_manual_data(conn)

    # Close connection
    conn.close()

    print(f"\n{'='*70}")
    print("✨ Analysis Complete!")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
