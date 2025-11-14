"""
Restore equipment and bg_builder tables for Render.com deployment.

The web API requires:
1. equipment table (equipment_resolver.py) with: canonical_id, name, category, nation
2. bg_builder tables (OSJones army list datacards) with:
   - bg_builder_vehicles (602 vehicles)
   - bg_builder_weapons (239 weapons)
   - bg_builder_vehicle_costs (703 cost entries)

This script copies:
- equipment table from Phase 5.5 backup (November 4, 2025)
- bg_builder tables from current database (November 14, 2025)

Usage during Render.com deployment:
- Render.com starts with empty master_database.db
- This script populates it with necessary tables
- Called from render.yaml buildCommand
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKUP_DB = PROJECT_ROOT / "database" / "master_database_backup_20251104_165608.db"
SOURCE_DB = PROJECT_ROOT / "database" / "master_database.db"
CURRENT_DB = PROJECT_ROOT / "database" / "master_database.db"


def copy_table(backup_conn, current_conn, table_name):
    """Helper function to copy a table from backup to current database."""

    backup_cursor = backup_conn.cursor()
    current_cursor = current_conn.cursor()

    # Check if table already exists
    current_cursor.execute(f"""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='{table_name}'
    """)

    if current_cursor.fetchone():
        print(f"  WARNING: {table_name} already exists, dropping...")
        current_cursor.execute(f"DROP TABLE {table_name}")
        current_conn.commit()

    # Get CREATE TABLE statement from backup
    backup_cursor.execute(f"""
        SELECT sql FROM sqlite_master
        WHERE type='table' AND name='{table_name}'
    """)

    result = backup_cursor.fetchone()
    if not result:
        print(f"  ERROR: {table_name} not found in backup database")
        return 0

    create_statement = result[0]
    print(f"  Creating {table_name}...")

    # Create table in current database
    current_cursor.execute(create_statement)
    current_conn.commit()

    # Copy data
    print(f"  Copying {table_name} data...")
    backup_cursor.execute(f"SELECT * FROM {table_name}")
    rows = backup_cursor.fetchall()

    if rows:
        # Get column count for placeholders
        backup_cursor.execute(f"PRAGMA table_info({table_name})")
        columns = backup_cursor.fetchall()
        placeholders = ','.join(['?' for _ in columns])

        current_cursor.executemany(
            f"INSERT INTO {table_name} VALUES ({placeholders})",
            rows
        )
        current_conn.commit()

    # Verify
    current_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = current_cursor.fetchone()[0]
    print(f"  [OK] Copied {count} rows from {table_name}")

    return count


def restore_equipment_table():
    """Copy equipment table from backup to current database."""

    print("Restoring equipment table for web API compatibility")
    print("=" * 60)

    # Connect to both databases
    backup_conn = sqlite3.connect(BACKUP_DB)
    current_conn = sqlite3.connect(CURRENT_DB)

    try:
        # Copy equipment table
        count = copy_table(backup_conn, current_conn, 'equipment')

        # Sample data
        current_cursor = current_conn.cursor()
        current_cursor.execute("""
            SELECT canonical_id, name, category, nation
            FROM equipment
            WHERE category IN ('tanks', 'anti_tank_guns', 'field_artillery')
            LIMIT 5
        """)

        print("\n  Sample equipment data:")
        for row in current_cursor.fetchall():
            print(f"    {row[0]}: {row[1]} ({row[2]}, {row[3]})")

        print("\n" + "=" * 60)
        print("COMPLETE - equipment table restored")
        print("=" * 60)

    finally:
        # Close connections
        backup_conn.close()
        current_conn.close()


def restore_bg_builder_tables():
    """Copy bg_builder tables from backup to current database for OSJones tool."""

    print("\nRestoring bg_builder tables for OSJones Army List tool")
    print("=" * 60)

    # Connect to both databases
    backup_conn = sqlite3.connect(BACKUP_DB)
    current_conn = sqlite3.connect(CURRENT_DB)

    try:
        tables_to_restore = [
            'bg_builder_vehicles',
            'bg_builder_weapons',
            'bg_builder_vehicle_costs'
        ]

        total_rows = 0
        for table_name in tables_to_restore:
            count = copy_table(backup_conn, current_conn, table_name)
            total_rows += count

        print("\n" + "=" * 60)
        print(f"COMPLETE - bg_builder tables restored ({total_rows} total rows)")
        print("=" * 60)
        print("\nOSJones Army List tool can now query:")
        print("  bg_builder_vehicles (vehicles with armor/weapons/movement)")
        print("  bg_builder_weapons (weapons with HE/AP values)")
        print("  bg_builder_vehicle_costs (points/BR by force/experience)")

    finally:
        # Close connections
        backup_conn.close()
        current_conn.close()


if __name__ == "__main__":
    restore_equipment_table()
    restore_bg_builder_tables()
