"""
Phase B2: De-duplicate master_equipment table

Similar to Phase A1 but for master_equipment table.
Merges 60 duplicate rows (20 groups) into 20 unique records.
"""

import sqlite3
from typing import Dict, List, Tuple


def find_duplicates(conn: sqlite3.Connection) -> Dict[str, List[Tuple]]:
    """Find duplicate equipment_name in master_equipment."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT equipment_name, COUNT(*) as count
        FROM master_equipment
        GROUP BY equipment_name
        HAVING count > 1
        ORDER BY count DESC, equipment_name
    """)

    duplicate_names = cursor.fetchall()

    # Get full records for each duplicate group
    duplicates = {}
    for name, count in duplicate_names:
        cursor.execute("""
            SELECT * FROM master_equipment
            WHERE equipment_name = ?
            ORDER BY id
        """, (name,))

        duplicates[name] = cursor.fetchall()

    return duplicates


def choose_best_record(records: List[Tuple]) -> Tuple:
    """
    Choose best record from duplicate group.

    Criteria:
    1. Most complete (count non-null fields)
    2. Highest completeness_score
    3. Lowest ID (first imported)
    """
    def score_record(record):
        # Record structure: (id, equipment_name, ..., completeness_score, ...)
        non_null_count = sum(1 for field in record if field not in (None, '', 'null', 'NULL', 0, 0.0))

        # Get completeness_score (second to last field typically)
        try:
            completeness_score = float(record[-2]) if record[-2] else 0.0
        except:
            completeness_score = 0.0

        return (non_null_count, completeness_score, -record[0])  # Negative ID to prefer lower

    scored = [(score_record(r), r) for r in records]
    scored.sort(reverse=True)  # Highest score first

    return scored[0][1]


def deduplicate_master_equipment(db_path: str, dry_run: bool = True):
    """De-duplicate master_equipment table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 100)
    print("PHASE B2: DE-DUPLICATE MASTER_EQUIPMENT")
    print("=" * 100)
    print()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM master_equipment")
    total_before = cursor.fetchone()[0]
    print(f"Records before de-duplication: {total_before}")
    print()

    # Find duplicates
    print("Finding duplicates...")
    duplicates = find_duplicates(conn)

    total_duplicate_rows = sum(len(records) for records in duplicates.values())
    records_to_delete = sum(len(records) - 1 for records in duplicates.values())

    print(f"Duplicate groups found: {len(duplicates)}")
    print(f"Total duplicate rows: {total_duplicate_rows}")
    print(f"Records to delete: {records_to_delete}")
    print(f"Records after de-duplication: {total_before - records_to_delete}")
    print()

    # Show sample duplicates
    print("Sample duplicate groups (first 10):")
    print("-" * 100)
    for i, (name, records) in enumerate(list(duplicates.items())[:10]):
        print(f"\\n{i+1}. '{name}' -> {len(records)} records:")
        for record in records:
            id_ = record[0]
            equipment_name = record[1]
            completeness = record[-2] if len(record) > 2 else None
            print(f"    id={id_:4} | {equipment_name:50} | completeness={completeness}")

        # Show winner
        winner = choose_best_record(records)
        winner_id = winner[0]
        print(f"    ==> WINNER: id={winner_id}")

    if len(duplicates) > 10:
        print(f"\\n... and {len(duplicates) - 10} more duplicate groups")
    print()

    # Apply de-duplication
    if not dry_run:
        print("Applying de-duplication...")

        deletes_made = 0

        for name, records in duplicates.items():
            # Choose best record
            winner = choose_best_record(records)
            winner_id = winner[0]

            # Get loser IDs
            loser_ids = [r[0] for r in records if r[0] != winner_id]

            if loser_ids:
                # Delete losers
                placeholders = ','.join('?' * len(loser_ids))
                cursor.execute(f"""
                    DELETE FROM master_equipment
                    WHERE id IN ({placeholders})
                """, loser_ids)
                deletes_made += len(loser_ids)

        conn.commit()

        print(f"[OK] Deleted {deletes_made} duplicate records")
        print()

        # Verify
        cursor.execute("SELECT COUNT(*) FROM master_equipment")
        total_after = cursor.fetchone()[0]

        print(f"Records after de-duplication: {total_after}")
        print(f"Reduction: {total_before - total_after} records ({100 * (total_before - total_after) / total_before:.1f}%)")
        print()

        # Check for remaining duplicates
        remaining_duplicates = find_duplicates(conn)
        if remaining_duplicates:
            print(f"[WARNING] {len(remaining_duplicates)} duplicate groups still exist")
        else:
            print("[OK] No duplicate equipment_name remaining - all unique")
        print()

    else:
        print("DRY RUN - No changes applied. Run with --execute to apply de-duplication.")
        print()

    conn.close()

    return len(duplicates), records_to_delete


def main():
    import argparse

    parser = argparse.ArgumentParser(description="De-duplicate master_equipment table")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')
    parser.add_argument('--execute', action='store_true', help='Apply de-duplication (default: dry run)')

    args = parser.parse_args()

    deduplicate_master_equipment(args.db, dry_run=not args.execute)


if __name__ == '__main__':
    main()
