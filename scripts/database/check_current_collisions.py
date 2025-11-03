#!/usr/bin/env python3
"""Check current WITW ID collisions in the database."""

import sqlite3
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def main():
    """Find all current WITW ID collisions."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=== Current WITW ID Collision Analysis ===\n")

    # Find all collisions
    cursor.execute("""
        SELECT
            witw_id,
            COUNT(*) as collision_count,
            GROUP_CONCAT(canonical_id) as canonical_ids,
            GROUP_CONCAT(name) as names,
            GROUP_CONCAT(category) as categories
        FROM equipment
        WHERE witw_id IS NOT NULL
        GROUP BY witw_id
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC, witw_id
    """)

    collisions = cursor.fetchall()

    if not collisions:
        print("✓ No WITW ID collisions found!")
    else:
        print(f"Found {len(collisions)} WITW ID collisions:\n")

        for row in collisions:
            print(f"WITW ID {row['witw_id']}: {row['collision_count']} items")
            ids = row['canonical_ids'].split(',')
            names = row['names'].split(',')
            cats = row['categories'].split(',')

            for i, (cid, name, cat) in enumerate(zip(ids, names, cats)):
                print(f"  {i+1}. {cid}: {name} ({cat})")
            print()

    # Also check aircraft-as-tanks
    cursor.execute("""
        SELECT canonical_id, name, witw_id, witw_name, category
        FROM equipment
        WHERE category IN ('tanks', 'main_tanks', 'light_tanks', 'medium_tanks', 'heavy_tanks')
          AND (witw_name LIKE '%(FI)%' OR witw_name LIKE '%(LB)%' OR witw_name LIKE '%aircraft%')
    """)

    aircraft_tanks = cursor.fetchall()

    if aircraft_tanks:
        print(f"\n⚠️  Found {len(aircraft_tanks)} aircraft-as-tanks:")
        for row in aircraft_tanks:
            print(f"  {row['canonical_id']}: witw_name={row['witw_name']}")
    else:
        print("\n✓ No aircraft-as-tanks found!")

    conn.close()

if __name__ == "__main__":
    main()
