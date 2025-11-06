"""
Split bg_reference_vehicles records with "or" in name into separate records.

Example:
  "Panzer IV H or J" -> "Panzer IV H" + "Panzer IV J"
  "SdKfz 251/3 or 251/4" -> "SdKfz 251/3" + "SdKfz 251/4"
"""

import sqlite3
import re
from datetime import datetime

DB_PATH = 'database/master_database.db'

def parse_or_name(name):
    """
    Parse a name with 'or' and return two separate names.

    Examples:
        "Panzer IV H or J" -> ["Panzer IV H", "Panzer IV J"]
        "SdKfz 251/3 or 251/4" -> ["SdKfz 251/3", "SdKfz 251/4"]
    """
    # Pattern: "Base Variant1 or Variant2"
    # We need to identify where the base ends and variants begin

    parts = name.split(' or ')
    if len(parts) != 2:
        raise ValueError(f"Expected exactly one 'or' in name: {name}")

    left_part = parts[0].strip()
    right_variant = parts[1].strip()

    # Reconstruct the two names
    name1 = left_part

    # Detect separator type and extract base name
    if '/' in left_part and left_part.rindex('/') > left_part.rfind(' '):
        # Slash separator is used (e.g., "SdKfz 251/3")
        last_slash_idx = left_part.rindex('/')
        base_name = left_part[:last_slash_idx]

        # Check if right_variant starts with slash (like "251/4")
        if '/' in right_variant:
            # Right variant has its own base (e.g., "251/4")
            # Extract just the variant after the slash
            variant_only = right_variant.split('/')[-1]
            name2 = base_name + '/' + variant_only
        else:
            # Right variant is just the variant (e.g., "4")
            name2 = base_name + '/' + right_variant
    else:
        # Space separator (e.g., "Panzer IV H")
        tokens = left_part.split()
        base_name = ' '.join(tokens[:-1])
        name2 = base_name + ' ' + right_variant

    return [name1, name2]


def split_or_records(dry_run=True):
    """
    Split all bg_reference_vehicles records with 'or' in the name.

    Args:
        dry_run: If True, only print what would be done without making changes
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all records with 'or' in name
    cursor.execute("""
        SELECT * FROM bg_reference_vehicles
        WHERE name LIKE '% or %'
        ORDER BY id
    """)

    records = cursor.fetchall()

    if not records:
        print("No records found with 'or' in name.")
        conn.close()
        return

    print(f"Found {len(records)} records to split:\n")

    # Get column names (excluding 'id' which is auto-increment)
    cursor.execute('PRAGMA table_info(bg_reference_vehicles)')
    all_columns = [col[1] for col in cursor.fetchall()]
    insert_columns = [col for col in all_columns if col != 'id']

    splits_performed = []
    created_names = {}  # Track names we've already created: {name: new_id}
    skipped_duplicates = []

    try:
        if not dry_run:
            conn.execute('BEGIN TRANSACTION')

        for record in records:
            record_dict = dict(record)
            original_name = record_dict['name']
            record_id = record_dict['id']

            # Parse the two names
            try:
                new_names = parse_or_name(original_name)
            except ValueError as e:
                print(f"ERROR: Could not parse record ID {record_id}: {e}")
                continue

            print(f"ID {record_id}: \"{original_name}\"")
            print(f"  -> Split into: \"{new_names[0]}\" and \"{new_names[1]}\"")

            if not dry_run:
                # Create two new records
                for new_name in new_names:
                    # Check if we already created this name (from a previous split in this batch)
                    if new_name in created_names:
                        print(f"    -> SKIPPED (duplicate): \"{new_name}\" (already created as ID {created_names[new_name]})")
                        skipped_duplicates.append({
                            'name': new_name,
                            'original_id': record_id,
                            'existing_id': created_names[new_name]
                        })
                        continue

                    # Check if this name already exists in the database
                    cursor.execute("SELECT id FROM bg_reference_vehicles WHERE name = ?", (new_name,))
                    existing = cursor.fetchone()
                    if existing:
                        print(f"    -> SKIPPED (already exists): \"{new_name}\" (ID {existing[0]})")
                        skipped_duplicates.append({
                            'name': new_name,
                            'original_id': record_id,
                            'existing_id': existing[0]
                        })
                        continue

                    # Prepare insert values
                    insert_values = []
                    for col in insert_columns:
                        if col == 'name':
                            insert_values.append(new_name)
                        elif col == 'notes':
                            # Add note about the split
                            original_notes = record_dict['notes'] or ''
                            split_note = f"Split from '{original_name}' on {datetime.now().strftime('%Y-%m-%d')}"
                            new_notes = f"{original_notes}\n{split_note}".strip()
                            insert_values.append(new_notes)
                        else:
                            insert_values.append(record_dict[col])

                    # Insert new record
                    placeholders = ','.join(['?'] * len(insert_columns))
                    insert_sql = f"INSERT INTO bg_reference_vehicles ({','.join(insert_columns)}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, insert_values)
                    new_id = cursor.lastrowid
                    created_names[new_name] = new_id
                    print(f"    -> Created new record ID {new_id}: \"{new_name}\"")

                # Delete original record
                cursor.execute("DELETE FROM bg_reference_vehicles WHERE id = ?", (record_id,))
                print(f"    -> Deleted original record ID {record_id}")

            splits_performed.append({
                'original_id': record_id,
                'original_name': original_name,
                'new_names': new_names
            })
            print()

        if not dry_run:
            conn.commit()
            print(f"\n[SUCCESS] Successfully split {len(splits_performed)} records.")
            print(f"  - Created {len(created_names)} unique records")
            print(f"  - Skipped {len(skipped_duplicates)} duplicates")
        else:
            print(f"\n[DRY RUN] Would split {len(splits_performed)} records.")
            print("   Run with dry_run=False to apply changes.")

        # Summary
        print("\nSummary of splits:")
        for split in splits_performed:
            print(f"  {split['original_name']} -> {split['new_names'][0]} + {split['new_names'][1]}")

        if skipped_duplicates and not dry_run:
            print("\nSkipped duplicates:")
            for dup in skipped_duplicates:
                print(f"  \"{dup['name']}\" (from ID {dup['original_id']}, already exists as ID {dup['existing_id']})")

    except Exception as e:
        if not dry_run:
            conn.rollback()
        print(f"\n[ERROR] {e}")
        raise

    finally:
        conn.close()


if __name__ == '__main__':
    import sys

    # Check for command line argument
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("EXECUTING CHANGES (not a dry run)")
        print("=" * 60)
    else:
        print("DRY RUN MODE (no changes will be made)")
        print("=" * 60)
        print("To execute changes, run: python split_or_records.py --execute")
        print("=" * 60)

    print()
    split_or_records(dry_run=dry_run)
