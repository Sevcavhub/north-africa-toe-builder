"""
Restore equipment table from backup to current master_database.db

The web API (equipment_resolver.py) requires an 'equipment' table with:
- canonical_id
- name
- category
- nation

This script copies the equipment table from the Phase 5.5 backup to the
current database which only has Phase 6 unit-centric schema.
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKUP_DB = PROJECT_ROOT / "database" / "master_database_backup_20251104_165608.db"
CURRENT_DB = PROJECT_ROOT / "database" / "master_database.db"


def restore_equipment_table():
    """Copy equipment table from backup to current database."""

    print("Restoring equipment table for web API compatibility")
    print("=" * 60)

    # Connect to both databases
    backup_conn = sqlite3.connect(BACKUP_DB)
    current_conn = sqlite3.connect(CURRENT_DB)

    backup_cursor = backup_conn.cursor()
    current_cursor = current_conn.cursor()

    # Check if equipment table already exists
    current_cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='equipment'
    """)

    if current_cursor.fetchone():
        print("WARNING: equipment table already exists")
        print("Dropping existing table...")
        current_cursor.execute("DROP TABLE equipment")
        current_conn.commit()

    # Get CREATE TABLE statement from backup
    backup_cursor.execute("""
        SELECT sql FROM sqlite_master
        WHERE type='table' AND name='equipment'
    """)

    create_statement = backup_cursor.fetchone()[0]
    print(f"\nCreating equipment table...")

    # Create table in current database
    current_cursor.execute(create_statement)
    current_conn.commit()

    # Copy data
    print("Copying equipment data...")
    backup_cursor.execute("SELECT * FROM equipment")
    rows = backup_cursor.fetchall()

    # Get column count for placeholders
    backup_cursor.execute("PRAGMA table_info(equipment)")
    columns = backup_cursor.fetchall()
    placeholders = ','.join(['?' for _ in columns])

    current_cursor.executemany(
        f"INSERT INTO equipment VALUES ({placeholders})",
        rows
    )
    current_conn.commit()

    # Verify
    current_cursor.execute("SELECT COUNT(*) FROM equipment")
    count = current_cursor.fetchone()[0]
    print(f"\n[OK] Copied {count} equipment rows")

    # Sample data
    current_cursor.execute("""
        SELECT canonical_id, name, category, nation
        FROM equipment
        WHERE category IN ('tanks', 'anti_tank_guns', 'field_artillery')
        LIMIT 10
    """)

    print("\nSample equipment data:")
    for row in current_cursor.fetchall():
        print(f"  {row[0]}: {row[1]} ({row[2]}, {row[3]})")

    # Close connections
    backup_conn.close()
    current_conn.close()

    print("\n" + "=" * 60)
    print("COMPLETE - equipment table restored")
    print("=" * 60)
    print("\nWeb API equipment_resolver.py can now query:")
    print("  SELECT canonical_id, name, category FROM equipment")


if __name__ == "__main__":
    restore_equipment_table()
