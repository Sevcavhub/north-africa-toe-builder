#!/usr/bin/env python3
"""Check real WITW ID collisions (numeric IDs only)."""

import sqlite3
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def main():
    """Find all current real WITW ID collisions."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=== Real WITW ID Collision Analysis (Numeric IDs Only) ===\n")

    # Find all collisions with numeric witw_ids
    cursor.execute("""
        SELECT
            CAST(witw_id AS INTEGER) as witw_id_num,
            COUNT(*) as collision_count,
            json_group_array(
                json_object('id', canonical_id, 'name', name, 'category', category)
            ) as items_json
        FROM equipment
        WHERE witw_id IS NOT NULL
          AND witw_id != 'NOT_IN_DATABASE'
          AND CAST(witw_id AS INTEGER) > 0
        GROUP BY CAST(witw_id AS INTEGER)
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC, CAST(witw_id AS INTEGER)
    """)

    collisions = cursor.fetchall()

    if not collisions:
        print("No numeric WITW ID collisions found!")
        print("\nChecking for aircraft-as-tanks...")
    else:
        print(f"Found {len(collisions)} numeric WITW ID collisions:\n")

        total_items = 0
        for row in collisions:
            print(f"WITW ID {row['witw_id_num']}: {row['collision_count']} items")
            total_items += row['collision_count']

            # Parse JSON
            import json
            items = json.loads(row['items_json'])

            for i, item in enumerate(items):
                name_safe = item['name'].encode('ascii', 'ignore').decode('ascii')
                print(f"  {i+1}. {item['id']}: {name_safe} ({item['category']})")
            print()

        print(f"Total: {len(collisions)} collisions affecting {total_items} equipment items\n")

    # Check aircraft-as-tanks
    cursor.execute("""
        SELECT canonical_id, name, witw_id, witw_name, category
        FROM equipment
        WHERE category IN ('tanks', 'main_tanks', 'light_tanks', 'medium_tanks', 'heavy_tanks')
          AND (witw_name LIKE '%(FI)%' OR witw_name LIKE '%(LB)%' OR witw_name LIKE '%aircraft%')
    """)

    aircraft_tanks = cursor.fetchall()

    if aircraft_tanks:
        print(f"Found {len(aircraft_tanks)} aircraft-as-tanks:")
        for row in aircraft_tanks:
            print(f"  {row['canonical_id']}: witw_name={row['witw_name']}")
    else:
        print("No aircraft-as-tanks found (already fixed!)")

    # Check 'NOT_IN_DATABASE' count
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM equipment
        WHERE witw_id = 'NOT_IN_DATABASE'
    """)
    not_in_db_count = cursor.fetchone()['count']
    print(f"\nNote: {not_in_db_count} items have witw_id='NOT_IN_DATABASE' (not yet matched to WITW)")

    conn.close()

if __name__ == "__main__":
    main()
