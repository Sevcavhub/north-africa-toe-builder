#!/usr/bin/env python3
"""
Phase 3B Task 4: Populate equipment_guns Table

Parse bg_reference_vehicles.weapons JSON and create equipment->gun linkages
using the name variants table from Task 3.
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def find_gun(cursor, weapon_name):
    """Find gun_id by matching weapon name to guns table"""

    # Try exact match first
    cursor.execute("SELECT gun_id FROM guns WHERE name = ?", (weapon_name,))
    result = cursor.fetchone()
    if result:
        return result[0]

    # Try case-insensitive match
    cursor.execute("SELECT gun_id FROM guns WHERE LOWER(name) = LOWER(?)", (weapon_name,))
    result = cursor.fetchone()
    if result:
        return result[0]

    # Try partial match
    cursor.execute("SELECT gun_id FROM guns WHERE LOWER(name) LIKE LOWER(?)", (f'%{weapon_name}%',))
    result = cursor.fetchone()
    if result:
        return result[0]

    # Caliber normalization for fuzzy matching
    caliber_map = {
        '2pdr': ('40mm', '2 pdr', '2-pdr', '2-pounder'),
        '6pdr': ('57mm', '6 pdr', '6-pdr', '6-pounder'),
        '17pdr': ('76.2mm', '76mm', '17 pdr', '17-pdr', '17-pounder'),
        '25pdr': ('87.6mm', '88mm', '25 pdr', '25-pdr', '25-pounder'),
        '3.7cm': ('37mm', '37 mm', '3.7 cm'),
        '5cm': ('50mm', '50 mm', '5 cm'),
        '7.5cm': ('75mm', '75 mm', '7.5 cm'),
        '8.8cm': ('88mm', '88 mm', '8.8 cm'),
        '2cm': ('20mm', '20 mm', '2 cm'),
    }

    weapon_lower = weapon_name.lower()
    for pattern, alternatives in caliber_map.items():
        if pattern in weapon_lower:
            # Try each alternative
            for alt in alternatives:
                cursor.execute("SELECT gun_id FROM guns WHERE LOWER(name) LIKE ?", (f'%{alt}%',))
                result = cursor.fetchone()
                if result:
                    return result[0]

    return None

def determine_mount_position(mount_type):
    """Determine mount position from mount type"""
    mount_lower = mount_type.lower()

    if 'turret' in mount_lower:
        return 'turret'
    elif 'hull' in mount_lower:
        return 'hull'
    elif 'co-axial' in mount_lower or 'coaxial' in mount_lower:
        return 'coaxial'
    elif 'pintle' in mount_lower:
        return 'pintle'
    elif 'bow' in mount_lower:
        return 'bow'
    else:
        return 'unknown'

def populate_equipment_guns(cursor):
    """Parse bg_reference_vehicles.weapons and create equipment_guns linkages"""

    print("Populating equipment_guns table...\n")

    # Get all bg_reference_vehicles with weapons
    cursor.execute("""
        SELECT name, weapons
        FROM bg_reference_vehicles
        WHERE weapons IS NOT NULL AND weapons != '[]'
    """)

    bg_vehicles = cursor.fetchall()
    print(f"Found {len(bg_vehicles)} bg_reference_vehicles with weapons\n")

    linkages_created = 0
    equipment_matched = 0
    equipment_unmatched = 0
    guns_not_found = []

    for bg_name, weapons_json in bg_vehicles:
        try:
            weapons = json.loads(weapons_json)
        except json.JSONDecodeError:
            print(f"  ERROR: Invalid JSON for {bg_name}")
            continue

        # Find matching equipment via variants table
        cursor.execute("""
            SELECT canonical_id
            FROM equipment_name_variants
            WHERE variant_name = ?
            ORDER BY confidence_score DESC
            LIMIT 1
        """, (bg_name,))

        result = cursor.fetchone()
        if not result:
            equipment_unmatched += 1
            continue

        equipment_id = result[0]
        equipment_matched += 1

        # Process each weapon
        for weapon in weapons:
            weapon_name = weapon.get('weapon')
            mount = weapon.get('mount', 'unknown')

            if not weapon_name:
                continue

            # Find gun in guns table
            gun_id = find_gun(cursor, weapon_name)
            if not gun_id:
                if weapon_name not in [g[0] for g in guns_not_found]:
                    guns_not_found.append((weapon_name, bg_name))
                continue

            # Determine mount position
            mount_position = determine_mount_position(mount)

            # Insert linkage
            try:
                cursor.execute("""
                    INSERT INTO equipment_guns (equipment_id, gun_id, mount_type, mount_position)
                    VALUES (?, ?, ?, ?)
                """, (equipment_id, gun_id, mount.lower(), mount_position))

                linkages_created += 1

                # Audit logging
                cursor.execute("""
                    INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ('equipment_guns', f'{equipment_id}_{gun_id}', 'linkage', 'NULL', 'created',
                      'gun_linkage', f'Parsed from bg_reference_vehicles.weapons JSON: {bg_name}'))

            except sqlite3.IntegrityError as e:
                # Duplicate linkage, skip
                pass

    print(f"Equipment matched: {equipment_matched}")
    print(f"Equipment unmatched: {equipment_unmatched}")
    print(f"Linkages created: {linkages_created}\n")

    if guns_not_found:
        print(f"Guns not found in guns table: {len(guns_not_found)}")
        if len(guns_not_found) <= 20:
            for gun_name, vehicle in guns_not_found[:20]:
                print(f"  - {gun_name} (from {vehicle})")
        else:
            print("  (Too many to list)")
        print()

    return linkages_created

def validation_report(cursor):
    """Generate validation report"""
    print("=" * 80)
    print("\n=== Validation Report ===\n")

    # Count linkages
    cursor.execute("SELECT COUNT(*) FROM equipment_guns")
    linkage_count = cursor.fetchone()[0]
    print(f"Total equipment_guns linkages: {linkage_count}\n")

    # Count equipment with linkages
    cursor.execute("SELECT COUNT(DISTINCT equipment_id) FROM equipment_guns")
    equipment_count = cursor.fetchone()[0]
    print(f"Equipment items with guns: {equipment_count}\n")

    # Count by mount_position
    cursor.execute("""
        SELECT mount_position, COUNT(*) AS count
        FROM equipment_guns
        GROUP BY mount_position
        ORDER BY count DESC
    """)

    print("Linkages by mount position:")
    for position, count in cursor.fetchall():
        print(f"  {position}: {count}")
    print()

    # Find tanks still missing guns
    cursor.execute("""
        SELECT e.canonical_id, e.name, e.category
        FROM equipment e
        WHERE e.category IN ('tanks', 'main_tanks', 'light_tanks')
          AND NOT EXISTS (
              SELECT 1 FROM equipment_guns eg WHERE eg.equipment_id = e.canonical_id
          )
        ORDER BY e.name
        LIMIT 30
    """)

    unlinked = cursor.fetchall()
    print(f"Tanks still without guns: {len(unlinked)}")
    if len(unlinked) <= 20:
        for eq_id, name, category in unlinked:
            print(f"  - {eq_id}: {name} ({category})")
    else:
        print("  (Showing first 20)")
        for eq_id, name, category in unlinked[:20]:
            print(f"  - {eq_id}: {name} ({category})")

    print("\n" + "=" * 80)

def main():
    """Execute Phase 3B Task 4: Populate equipment_guns"""

    print("=" * 80)
    print("=== Phase 3B Task 4: Populate equipment_guns Table ===")
    print("=" * 80)
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Populate equipment_guns
        linkages_created = populate_equipment_guns(cursor)

        # Commit changes
        conn.commit()

        # Validation
        validation_report(cursor)

        print("\n=== Task 4 Complete ===")
        print(f"Total linkages created: {linkages_created}")
        print("Transaction committed successfully!\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return 1
    finally:
        conn.close()

    return 0

if __name__ == "__main__":
    exit(main())
