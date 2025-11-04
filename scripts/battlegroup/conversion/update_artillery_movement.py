#!/usr/bin/env python3
"""
Update Artillery Movement Values

Extracts caliber for artillery items and updates movement values in equipment_battlegroup
using the enhanced movement calculator with BattleGroup rules.

Strategy:
1. Query equipment_battlegroup for artillery items with NULL movement
2. Extract caliber from multiple sources (priority order):
   a) bg_reference_guns (highest confidence - exact matches)
   b) WWIITANKS guns table (medium confidence - name matching)
   c) Parse from equipment name (low confidence - regex extraction)
3. Apply enhanced movement calculator with caliber
4. Update equipment_battlegroup with confidence scoring

Usage:
    python scripts/battlegroup/conversion/update_artillery_movement.py
    python scripts/battlegroup/conversion/update_artillery_movement.py --dry-run
"""

import sqlite3
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Import our enhanced movement calculator
import sys
sys.path.insert(0, str(Path(__file__).parent))
from movement_calculator import calculate_movement, classify_gun_weight

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"


def extract_caliber_from_name(name: str) -> Optional[Tuple[float, str]]:
    """
    Extract caliber from equipment name using regex patterns.

    Returns:
        Tuple of (caliber_mm, confidence_note) or None
    """
    # Pattern 1: Direct mm notation (e.g., "Bofors 40mm", "88mm FlaK")
    match = re.search(r'(\d+(?:\.\d+)?)\s*mm', name, re.IGNORECASE)
    if match:
        caliber = float(match.group(1))
        return (caliber, "Extracted from name (mm notation)")

    # Pattern 2: Pounder notation (British - need conversion)
    # 2-pounder = 40mm, 6-pounder = 57mm, 17-pounder = 76.2mm, 25-pounder = 87.6mm
    pounder_map = {
        2: 40,
        3: 47,
        6: 57,
        17: 76.2,
        25: 87.6,
        32: 94
    }
    match = re.search(r'(\d+)[- ]?pounder', name, re.IGNORECASE)
    if match:
        pounder = int(match.group(1))
        if pounder in pounder_map:
            return (pounder_map[pounder], f"Converted from {pounder}-pounder notation")

    # Pattern 3: Inch notation (need conversion: 1 inch = 25.4mm)
    # Examples: "3.7-inch AA", "4.5-inch Howitzer"
    match = re.search(r'(\d+(?:\.\d+)?)[- ]?inch', name, re.IGNORECASE)
    if match:
        inches = float(match.group(1))
        caliber = inches * 25.4
        return (caliber, f"Converted from {inches} inch notation")

    # Pattern 4: Caliber as first number in parentheses
    match = re.search(r'\((\d+(?:\.\d+)?)\)', name)
    if match:
        caliber = float(match.group(1))
        if 7 <= caliber <= 300:  # Sanity check for realistic caliber range
            return (caliber, "Extracted from parentheses")

    return None


def get_caliber_from_bg_reference(conn: sqlite3.Connection, equipment_name: str) -> Optional[Tuple[float, str, int]]:
    """
    Try to match equipment to bg_reference_guns and get caliber.

    Returns:
        Tuple of (caliber_mm, source_note, confidence) or None
    """
    cursor = conn.cursor()

    # Try exact name match first
    cursor.execute("""
        SELECT caliber_mm, name
        FROM bg_reference_guns
        WHERE LOWER(name) = LOWER(?)
        AND caliber_mm IS NOT NULL
    """, (equipment_name,))

    result = cursor.fetchone()
    if result:
        return (result[0], f"BG reference exact match: {result[1]}", 100)

    # Try partial name match (fuzzy)
    cursor.execute("""
        SELECT caliber_mm, name
        FROM bg_reference_guns
        WHERE caliber_mm IS NOT NULL
    """)

    eq_lower = equipment_name.lower()
    for ref_caliber, ref_name in cursor.fetchall():
        ref_lower = ref_name.lower()

        # Check if equipment name contains reference name or vice versa
        if ref_lower in eq_lower or eq_lower in ref_lower:
            # Require at least 5 characters match
            if len(ref_lower) >= 5 or len(eq_lower) >= 5:
                return (ref_caliber, f"BG reference partial match: {ref_name}", 85)

    return None


def get_caliber_from_wwiitanks(conn: sqlite3.Connection, equipment_id: str, equipment_name: str) -> Optional[Tuple[float, str, int]]:
    """
    Try to get caliber from WWIITANKS guns table via equipment linkage.

    Returns:
        Tuple of (caliber_mm, source_note, confidence) or None
    """
    cursor = conn.cursor()

    # Try to link via equipment → wwiitanks_id → guns
    cursor.execute("""
        SELECT g.caliber_mm, g.name
        FROM equipment e
        JOIN guns g ON e.wwiitanks_id = g.wwiitanks_id
        WHERE e.canonical_id = ?
        AND g.caliber_mm IS NOT NULL
    """, (equipment_id,))

    result = cursor.fetchone()
    if result:
        return (result[0], f"WWIITANKS guns table: {result[1]}", 80)

    # Try name-based matching as fallback
    cursor.execute("""
        SELECT caliber_mm, name
        FROM guns
        WHERE caliber_mm IS NOT NULL
    """)

    eq_lower = equipment_name.lower()
    for gun_caliber, gun_name in cursor.fetchall():
        gun_lower = gun_name.lower()

        # Check for partial match
        if gun_lower in eq_lower or eq_lower in gun_lower:
            if len(gun_lower) >= 5 or len(eq_lower) >= 5:
                return (gun_caliber, f"WWIITANKS name match: {gun_name}", 70)

    return None


def determine_equipment_category(equipment_name: str, eq_category: str) -> str:
    """
    Determine if equipment is a mortar or regular gun.
    """
    name_lower = equipment_name.lower()

    if 'mortar' in name_lower:
        return 'Mortar'
    elif 'howitzer' in name_lower:
        return 'Howitzer'
    elif 'at' in name_lower or 'anti-tank' in name_lower or 'anti tank' in name_lower:
        return 'Anti-Tank Gun'
    elif 'aa' in name_lower or 'anti-aircraft' in name_lower or 'flak' in name_lower:
        return 'Anti-Aircraft Gun'
    elif 'field' in eq_category.lower():
        return 'Field Gun'
    else:
        return 'Artillery'


def update_artillery_movement(dry_run: bool = False):
    """
    Main function to update artillery movement values.

    Args:
        dry_run: If True, don't actually update database, just report what would be done
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 90)
    print("ARTILLERY MOVEMENT UPDATE")
    print("=" * 90)
    print()

    if dry_run:
        print("DRY RUN MODE - No database changes will be made")
        print()

    # Get artillery items needing movement updates
    cursor.execute("""
        SELECT
            e.canonical_id,
            e.name,
            e.category,
            e.equipment_type,
            eb.off_road_movement,
            eb.road_movement
        FROM equipment e
        LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
        WHERE (e.equipment_type = 'artillery'
               OR e.category IN ('artillery', 'anti_tank_guns', 'anti_aircraft_guns', 'field_artillery', 'anti_tank', 'anti_aircraft', 'towed_artillery'))
        ORDER BY e.name
    """)

    artillery_items = cursor.fetchall()

    print(f"Found {len(artillery_items)} artillery items needing movement values")
    print()

    # Track results
    results = {
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'by_source': {
            'bg_reference': 0,
            'wwiitanks': 0,
            'name_parsing': 0,
            'failed': 0
        }
    }

    updates = []

    for eq_id, eq_name, eq_category, eq_type, current_off, current_road in artillery_items:
        print(f"Processing: {eq_name[:60]}")

        # Try to extract caliber from multiple sources
        caliber = None
        source_note = None
        confidence = 0

        # Source 1: bg_reference_guns (highest priority)
        bg_result = get_caliber_from_bg_reference(conn, eq_name)
        if bg_result:
            caliber, source_note, confidence = bg_result
            results['by_source']['bg_reference'] += 1
            print(f"  [OK] Caliber: {caliber}mm (confidence: {confidence}%)")
            print(f"       Source: {source_note}")

        # Source 2: WWIITANKS guns table
        if not caliber:
            ww2_result = get_caliber_from_wwiitanks(conn, eq_id, eq_name)
            if ww2_result:
                caliber, source_note, confidence = ww2_result
                results['by_source']['wwiitanks'] += 1
                print(f"  [OK] Caliber: {caliber}mm (confidence: {confidence}%)")
                print(f"       Source: {source_note}")

        # Source 3: Parse from name
        if not caliber:
            name_result = extract_caliber_from_name(eq_name)
            if name_result:
                caliber, extract_note = name_result
                source_note = extract_note
                confidence = 60
                results['by_source']['name_parsing'] += 1
                print(f"  [OK] Caliber: {caliber}mm (confidence: {confidence}%)")
                print(f"       Source: {source_note}")

        # If we have caliber, calculate movement
        if caliber:
            eq_cat = determine_equipment_category(eq_name, eq_category)

            # Calculate movement using enhanced calculator
            movement_result = calculate_movement(
                caliber_mm=caliber,
                equipment_category=eq_cat
            )

            print(f"    Category: {eq_cat}")
            print(f"    Gun Weight: {movement_result.get('gun_category', 'N/A')}")
            print(f"    Movement: {movement_result['format']}")
            print(f"    Note: {movement_result['note']}")

            updates.append({
                'equipment_id': eq_id,
                'off_road': movement_result['off_road'],
                'road': movement_result['road'],
                'confidence': confidence,
                'method': f"caliber_based_{movement_result.get('method', 'unknown')}",
                'notes': f"{source_note} | {movement_result['note']}"
            })

            results['updated'] += 1
        else:
            print(f"  [FAIL] Could not determine caliber")
            results['by_source']['failed'] += 1
            results['skipped'] += 1

        print()

    # Apply updates to database
    if not dry_run and updates:
        print("=" * 90)
        print("APPLYING UPDATES TO DATABASE")
        print("=" * 90)
        print()

        for update in updates:
            cursor.execute("""
                UPDATE equipment_battlegroup
                SET off_road_movement = ?,
                    road_movement = ?,
                    generation_method = ?,
                    confidence_score = ?,
                    validation_notes = ?,
                    generated_date = ?
                WHERE equipment_id = ?
            """, (
                update['off_road'],
                update['road'],
                update['method'],
                update['confidence'],
                update['notes'],
                datetime.now().isoformat(),
                update['equipment_id']
            ))

        conn.commit()
        print(f"[OK] Updated {len(updates)} artillery items in equipment_battlegroup")

    # Print summary
    print()
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)
    print(f"Total artillery items: {len(artillery_items)}")
    print(f"Successfully updated: {results['updated']}")
    print(f"Skipped (no caliber): {results['skipped']}")
    print(f"Errors: {results['errors']}")
    print()
    print("Caliber sources:")
    print(f"  - BG reference guns: {results['by_source']['bg_reference']}")
    print(f"  - WWIITANKS guns: {results['by_source']['wwiitanks']}")
    print(f"  - Name parsing: {results['by_source']['name_parsing']}")
    print(f"  - Failed to extract: {results['by_source']['failed']}")

    if dry_run:
        print()
        print("DRY RUN COMPLETE - No changes made to database")

    conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Update artillery movement values in equipment_battlegroup')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without updating database')

    args = parser.parse_args()

    update_artillery_movement(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
