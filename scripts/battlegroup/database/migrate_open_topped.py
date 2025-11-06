"""
Migrate "Open-Topped" from weapons field to new armor_modifier field.

This script:
1. Finds all records where weapons field contains "Open-Topped"
2. Extracts "Open-Topped" from weapons
3. Sets armor_modifier = "Open-Topped"
4. Removes "Open-Topped" from weapons field
"""

import sqlite3
import re

DB_PATH = 'database/master_database.db'

def migrate_open_topped(dry_run=True):
    """
    Move "Open-Topped" from weapons to armor_modifier field.

    Args:
        dry_run: If True, only show what would be done
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Find all records with "Open-Topped" in weapons
    cursor.execute("""
        SELECT id, name, weapons
        FROM bg_reference_vehicles
        WHERE weapons LIKE '%Open-Topped%'
        ORDER BY id
    """)

    records = cursor.fetchall()

    if not records:
        print("No records found with 'Open-Topped' in weapons field.")
        conn.close()
        return

    print(f"Found {len(records)} records with 'Open-Topped':\n")

    updates = []

    for record in records:
        record_id = record['id']
        name = record['name']
        weapons = record['weapons'] or ''

        # Extract "Open-Topped" and clean up weapons field
        # Handle variations: "Open-Topped", "open-topped", "(Open-Topped)", etc.

        # Pattern to match "Open-Topped" with optional parentheses and surrounding punctuation
        patterns = [
            r'\(Open-Topped\)',
            r'Open-Topped',
            r'\(open-topped\)',
            r'open-topped',
        ]

        cleaned_weapons = weapons
        found_modifier = None

        for pattern in patterns:
            if re.search(pattern, cleaned_weapons, re.IGNORECASE):
                found_modifier = "Open-Topped"
                # Remove the pattern
                cleaned_weapons = re.sub(pattern, '', cleaned_weapons, flags=re.IGNORECASE)
                break

        # Clean up resulting punctuation issues
        # Apply multiple passes to handle complex cases
        cleaned_weapons = re.sub(r'\s*,\s*,\s*', ', ', cleaned_weapons)  # Double commas
        cleaned_weapons = re.sub(r'^\s*,\s*', '', cleaned_weapons)        # Leading comma
        cleaned_weapons = re.sub(r'\s*,\s*$', '', cleaned_weapons)        # Trailing comma
        cleaned_weapons = re.sub(r'\s+', ' ', cleaned_weapons)            # Multiple spaces
        cleaned_weapons = re.sub(r'\(\s*,\s*\)', '', cleaned_weapons)     # Empty parens with comma
        cleaned_weapons = re.sub(r',\s*\)', ')', cleaned_weapons)         # Comma before closing paren
        cleaned_weapons = re.sub(r'\(\s*/\s*', '(', cleaned_weapons)      # Orphaned slash in parens
        cleaned_weapons = re.sub(r'/\s*,', ',', cleaned_weapons)          # Slash before comma
        cleaned_weapons = re.sub(r'\s+,', ',', cleaned_weapons)           # Space before comma
        cleaned_weapons = re.sub(r'\(\s+', '(', cleaned_weapons)          # Space after open paren
        cleaned_weapons = re.sub(r'\s+\)', ')', cleaned_weapons)          # Space before close paren
        cleaned_weapons = cleaned_weapons.strip()

        # If weapons is now empty, set to NULL
        if not cleaned_weapons:
            cleaned_weapons = None

        print(f"ID {record_id}: {name}")
        print(f"  OLD weapons: {weapons}")
        print(f"  NEW weapons: {cleaned_weapons}")
        print(f"  armor_modifier: {found_modifier}")
        print()

        updates.append({
            'id': record_id,
            'armor_modifier': found_modifier,
            'weapons': cleaned_weapons
        })

    if not dry_run:
        try:
            conn.execute('BEGIN TRANSACTION')

            for update in updates:
                cursor.execute("""
                    UPDATE bg_reference_vehicles
                    SET armor_modifier = ?, weapons = ?
                    WHERE id = ?
                """, (update['armor_modifier'], update['weapons'], update['id']))

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
        print("To execute: python migrate_open_topped.py --execute")
        print("=" * 60)

    print()
    migrate_open_topped(dry_run=dry_run)
