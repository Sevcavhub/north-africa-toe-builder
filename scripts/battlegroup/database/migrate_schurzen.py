"""
Migrate Schürzen data from armor_side field to armor_side_schurzen field.

Schürzen are side skirts that provide additional armor protection.
They display as: base(schurzen) e.g., "N(M)"

This script:
1. Finds records with parentheses in armor_side field like "N(M)"
2. Extracts base armor (N) and Schürzen value (M)
3. Sets armor_side = "N" and armor_side_schurzen = "M"
4. Adds "Schürzen" to armor_modifier if not already present
"""

import sqlite3
import re

DB_PATH = 'database/master_database.db'

def migrate_schurzen(dry_run=True):
    """
    Extract Schürzen values from armor_side field.

    Args:
        dry_run: If True, only show what would be done
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Find all records with parentheses in armor_side
    # Pattern: "N(M)" or "K(J)" etc.
    cursor.execute("""
        SELECT id, name, armor_front, armor_side, armor_rear, armor_modifier
        FROM bg_reference_vehicles
        WHERE armor_side LIKE '%(%'
        ORDER BY id
    """)

    records = cursor.fetchall()

    if not records:
        print("No records found with Schürzen pattern in armor_side field.")
        conn.close()
        return

    print(f"Found {len(records)} records with Schürzen:\n")

    updates = []

    for record in records:
        record_id = record['id']
        name = record['name']
        armor_side = record['armor_side']
        armor_modifier = record['armor_modifier']

        # Parse pattern: "N(M)" or "K+1(J)" etc.
        # Match: letter(s), optional +N, then (letter(s), optional +N)
        match = re.match(r'^([A-Z]+(?:\+\d+)?)\(([A-Z]+(?:\+\d+)?)\)$', armor_side or '')

        if not match:
            print(f"WARNING: ID {record_id} ({name}) has unrecognized pattern: '{armor_side}'")
            continue

        base_armor = match.group(1)
        schurzen_armor = match.group(2)

        # Update or add "Schürzen" to armor_modifier
        new_modifier = armor_modifier
        if armor_modifier:
            if 'Schürzen' not in armor_modifier:
                new_modifier = f"{armor_modifier}, Schürzen"
        else:
            new_modifier = "Schürzen"

        print(f"ID {record_id}: {name}")
        print(f"  OLD armor_side: {armor_side}")
        print(f"  NEW armor_side: {base_armor}")
        print(f"  NEW armor_side_schurzen: {schurzen_armor}")
        print(f"  armor_modifier: {armor_modifier} -> {new_modifier}")
        print()

        updates.append({
            'id': record_id,
            'armor_side': base_armor,
            'armor_side_schurzen': schurzen_armor,
            'armor_modifier': new_modifier
        })

    if not dry_run:
        try:
            conn.execute('BEGIN TRANSACTION')

            for update in updates:
                cursor.execute("""
                    UPDATE bg_reference_vehicles
                    SET armor_side = ?,
                        armor_side_schurzen = ?,
                        armor_modifier = ?
                    WHERE id = ?
                """, (update['armor_side'], update['armor_side_schurzen'],
                      update['armor_modifier'], update['id']))

            conn.commit()
            print(f"\n[SUCCESS] Updated {len(updates)} records.")

        except Exception as e:
            conn.rollback()
            print(f"\n[ERROR] {e}")
            raise
    else:
        print(f"\n[DRY RUN] Would update {len(updates)} records.")
        print("   Run with dry_run=False to apply changes.")

    conn.close()


if __name__ == '__main__':
    import sys

    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("EXECUTING CHANGES")
        print("=" * 60)
    else:
        print("DRY RUN MODE")
        print("=" * 60)
        print("To execute: python migrate_schurzen.py --execute")
        print("=" * 60)

    print()
    migrate_schurzen(dry_run=dry_run)
