#!/usr/bin/env python3
"""Fix remaining WITW ID 100044 collision - NULL all to keep separate."""

import sqlite3
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def main():
    """Fix WITW ID 100044 collision by NULLing all witw_ids."""

    print("=== Fixing Remaining WITW ID 100044 Collision ===\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Get items
        cursor.execute("""
            SELECT canonical_id, name FROM equipment WHERE witw_id = 100044
        """)
        items = cursor.fetchall()

        print(f"Found {len(items)} items with WITW ID 100044:")
        for item in items:
            print(f"  - {item['canonical_id']}: {item['name']}")

        if len(items) == 0:
            print("\nNo collision found! Already fixed.")
            return 0

        print(f"\nUser decision: Keep all separate (NULL all witw_ids)")
        print("Reason: WC-52 and WC-62 are different models\n")

        canonical_ids = [item['canonical_id'] for item in items]

        # Audit logging
        for item in items:
            cursor.execute("""
                INSERT INTO normalization_audit
                (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('equipment', item['canonical_id'], 'witw_id', '100044', 'NULL',
                  'collision_fix_final', 'User decision: Keep WC-52 and WC-62 separate (different models)'))

        # Resolution logging
        cursor.execute("""
            INSERT INTO witw_collision_resolutions
            (witw_id, collision_count, resolution_strategy, retained_canonical_id,
             nulled_canonical_ids, escalated, user_decision)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (100044, len(items), 'keep_separate', None, ','.join(canonical_ids), 1,
              'User decision: Keep WC-52 and WC-62 separate (different models)'))

        # NULL all
        cursor.execute("UPDATE equipment SET witw_id = NULL, witw_name = NULL WHERE witw_id = 100044")

        conn.commit()

        print("=== Fixed Successfully ===")
        print(f"NULL'd witw_ids for {len(items)} items")
        print("Transaction committed!\n")

        # Check remaining collisions
        cursor.execute("""
            SELECT COUNT(DISTINCT witw_id) as collision_count
            FROM (
                SELECT witw_id, COUNT(*) as cnt
                FROM equipment
                WHERE witw_id IS NOT NULL
                  AND witw_id != 'NOT_IN_DATABASE'
                  AND CAST(witw_id AS INTEGER) > 0
                GROUP BY witw_id
                HAVING COUNT(*) > 1
            )
        """)

        remaining = cursor.fetchone()['collision_count']
        print(f"Remaining collisions: {remaining}")

        if remaining == 0:
            print("\nSUCCESS: All WITW ID collisions resolved!")

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
