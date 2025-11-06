"""
Remove exact duplicate records from bg_reference_vehicles table.

A duplicate is defined as: all fields identical except for 'id'.
Keeps the record with the lowest ID and deletes duplicates.
"""

import sqlite3
from datetime import datetime

DB_PATH = 'database/master_database.db'

def find_exact_duplicates(dry_run=True):
    """
    Find and optionally remove exact duplicate records.

    Args:
        dry_run: If True, only print what would be done without making changes
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all columns except 'id' and timestamp/metadata fields
    cursor.execute('PRAGMA table_info(bg_reference_vehicles)')
    all_columns = [col[1] for col in cursor.fetchall()]

    # Exclude fields that don't affect whether records are functionally identical
    exclude_fields = [
        'id',              # Auto-increment primary key
        'created_at',      # Timestamp - meaningless for duplication
        'verification_date', # Timestamp - meaningless for duplication
    ]

    compare_columns = [col for col in all_columns if col not in exclude_fields]

    print(f"Comparing {len(compare_columns)} fields (excluding: {', '.join(exclude_fields)})")
    print()

    # Build query to find duplicates
    # Group by all fields except id, and find groups with COUNT > 1
    group_by_clause = ', '.join(compare_columns)

    # Use a CTE to find duplicate groups
    find_duplicates_sql = f"""
    WITH duplicate_groups AS (
        SELECT
            {', '.join(compare_columns)},
            COUNT(*) as dup_count,
            GROUP_CONCAT(id) as id_list
        FROM bg_reference_vehicles
        GROUP BY {group_by_clause}
        HAVING COUNT(*) > 1
    )
    SELECT * FROM duplicate_groups
    ORDER BY dup_count DESC
    """

    cursor.execute(find_duplicates_sql)
    duplicate_groups = cursor.fetchall()

    if not duplicate_groups:
        print("No exact duplicates found.")
        conn.close()
        return

    print(f"Found {len(duplicate_groups)} groups of exact duplicates:\n")

    total_duplicates_to_delete = 0
    records_to_delete = []

    for group in duplicate_groups:
        group_dict = dict(group)
        id_list = group_dict['id_list'].split(',')
        id_list = [int(id_str) for id_str in id_list]
        dup_count = group_dict['dup_count']

        # Keep the first (lowest ID), delete the rest
        keep_id = min(id_list)
        delete_ids = [id for id in id_list if id != keep_id]

        total_duplicates_to_delete += len(delete_ids)

        # Get details for display
        name = group_dict.get('name', 'Unknown')
        nation = group_dict.get('nation', 'Unknown')
        vehicle_type = group_dict.get('vehicle_type', 'Unknown')

        print(f"Duplicate group: {name} ({nation} {vehicle_type})")
        print(f"  Total copies: {dup_count}")
        print(f"  Keep ID: {keep_id}")
        print(f"  Delete IDs: {', '.join(map(str, delete_ids))}")

        for delete_id in delete_ids:
            records_to_delete.append({
                'id': delete_id,
                'name': name,
                'keep_id': keep_id
            })
        print()

    if not dry_run:
        try:
            conn.execute('BEGIN TRANSACTION')

            for record in records_to_delete:
                cursor.execute("DELETE FROM bg_reference_vehicles WHERE id = ?", (record['id'],))
                print(f"Deleted ID {record['id']}: {record['name']} (duplicate of ID {record['keep_id']})")

            conn.commit()
            print(f"\n[SUCCESS] Deleted {total_duplicates_to_delete} duplicate records.")
        except Exception as e:
            conn.rollback()
            print(f"\n[ERROR] {e}")
            raise
    else:
        print(f"[DRY RUN] Would delete {total_duplicates_to_delete} duplicate records.")
        print("   Run with dry_run=False to apply changes.")

    # Summary
    print(f"\nSummary:")
    print(f"  Duplicate groups found: {len(duplicate_groups)}")
    print(f"  Records to keep: {len(duplicate_groups)}")
    print(f"  Records to delete: {total_duplicates_to_delete}")

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
        print("To execute changes, run: python deduplicate_exact_records.py --execute")
        print("=" * 60)

    print()
    find_exact_duplicates(dry_run=dry_run)
