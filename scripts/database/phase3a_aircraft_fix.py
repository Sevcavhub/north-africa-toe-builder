#!/usr/bin/env python3
"""Phase 3A Batch 1: Fix aircraft-as-tanks (4 records)"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def main():
    """Fix 4 aircraft-as-tanks records."""

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=== Phase 3A Batch 1: Aircraft-as-Tanks Fix ===\n")

    # Check if equipment table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='equipment'")
    if not cursor.fetchone():
        print("ERROR: equipment table not found!")
        sys.exit(1)

    # Check if audit tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='normalization_audit'")
    audit_exists = cursor.fetchone() is not None

    if not audit_exists:
        print("Creating audit infrastructure...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS normalization_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                table_name TEXT NOT NULL,
                record_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                change_type TEXT NOT NULL,
                change_reason TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS witw_collision_resolutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                witw_id INTEGER NOT NULL,
                collision_count INTEGER NOT NULL,
                resolution_strategy TEXT NOT NULL,
                retained_canonical_id TEXT,
                nulled_canonical_ids TEXT,
                escalated INTEGER DEFAULT 0,
                escalation_reason TEXT,
                user_decision TEXT
            )
        """)
        print("Audit tables created.\n")

    # Get current state
    affected_ids = ['GBR_CRUSADER_I', 'GBR_SHERMAN_I_M4', 'GBR_SHERMAN_II_M4A1', 'GBR_SHERMAN_III_M4A4']

    print("Current state:")
    cursor.execute("""
        SELECT canonical_id, name, witw_id, witw_name, category
        FROM equipment
        WHERE canonical_id IN (?, ?, ?, ?)
    """, affected_ids)

    rows = cursor.fetchall()
    if not rows:
        print("WARNING: No affected records found!")
        return

    for row in rows:
        print(f"  {row['canonical_id']}: witw_id={row['witw_id']}, witw_name={row['witw_name']}")

    print("\nBeginning transaction...")

    try:
        # Insert audit records
        audit_data = [
            ('equipment', 'GBR_CRUSADER_I', 'witw_id', '116', 'NULL', 'collision_fix', 'Aircraft-as-tank: Lysander I assigned to Crusader I tank'),
            ('equipment', 'GBR_CRUSADER_I', 'witw_name', 'Lysander I (FI)', 'NULL', 'collision_fix', 'Aircraft-as-tank: Lysander I assigned to Crusader I tank'),
            ('equipment', 'GBR_SHERMAN_I_M4', 'witw_id', '115', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman I tank'),
            ('equipment', 'GBR_SHERMAN_I_M4', 'witw_name', 'Hurricane I (FI)', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman I tank'),
            ('equipment', 'GBR_SHERMAN_II_M4A1', 'witw_id', '115', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman II tank'),
            ('equipment', 'GBR_SHERMAN_II_M4A1', 'witw_name', 'Hurricane I (FI)', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman II tank'),
            ('equipment', 'GBR_SHERMAN_III_M4A4', 'witw_id', '115', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman III tank'),
            ('equipment', 'GBR_SHERMAN_III_M4A4', 'witw_name', 'Hurricane I (FI)', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman III tank'),
        ]

        cursor.executemany("""
            INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, audit_data)

        print(f"Inserted {len(audit_data)} audit records.")

        # Fix the records
        for canonical_id in affected_ids:
            cursor.execute("""
                UPDATE equipment
                SET witw_id = NULL, witw_name = NULL
                WHERE canonical_id = ?
            """, (canonical_id,))
            print(f"Fixed: {canonical_id}")

        # Validation
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM equipment
            WHERE category IN ('tanks', 'main_tanks')
              AND (witw_name LIKE '%(FI)%' OR witw_name LIKE '%(LB)%')
        """)
        aircraft_count = cursor.fetchone()['count']

        if aircraft_count > 0:
            print(f"\nERROR: Validation failed! Still {aircraft_count} aircraft names in tank records.")
            conn.rollback()
            sys.exit(1)

        # Commit transaction
        conn.commit()
        print("\nTransaction committed successfully!")

        # Show final state
        print("\nFinal state:")
        cursor.execute("""
            SELECT canonical_id, name, witw_id, witw_name, category
            FROM equipment
            WHERE canonical_id IN (?, ?, ?, ?)
        """, affected_ids)

        for row in cursor.fetchall():
            print(f"  {row['canonical_id']}: witw_id={row['witw_id']}, witw_name={row['witw_name']}")

        print("\n=== Batch 1 Complete: 4 aircraft-as-tanks fixed ===")

    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
