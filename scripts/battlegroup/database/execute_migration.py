#!/usr/bin/env python3
"""
Execute BattleGroup Database Migration
Date: 2025-11-04
Purpose: Archive corrupted scraped data, create fresh tables, clear bad linkages

This script executes the three-phase migration:
1. Archive existing bg_reference_guns/vehicles tables
2. Create fresh tables with manual extraction audit fields
3. Clear corrupted HE/AP linkages from equipment_battlegroup

IMPORTANT: This is destructive! Make a database backup first.
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def execute_sql_file(conn: sqlite3.Connection, sql_file: Path) -> None:
    """Execute SQL file and print results"""
    print(f"\n{'='*80}")
    print(f"Executing: {sql_file.name}")
    print('='*80)

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    # Execute script
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()

    print(f"[OK] {sql_file.name} executed successfully")

def backup_database(db_path: Path) -> Path:
    """Create timestamped database backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"master_database_backup_{timestamp}.db"

    print(f"\nCreating database backup...")
    print(f"  Source: {db_path}")
    print(f"  Backup: {backup_path}")

    import shutil
    shutil.copy2(db_path, backup_path)

    print(f"[OK] Backup created successfully")
    return backup_path

def verify_tables_exist(conn: sqlite3.Connection, tables: list) -> bool:
    """Verify that tables exist before migration"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}

    missing = [t for t in tables if t not in existing_tables]
    if missing:
        print(f"\n[WARNING] Expected tables not found: {missing}")
        return False
    return True

def print_migration_summary(conn: sqlite3.Connection):
    """Print summary of migration results"""
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print("MIGRATION SUMMARY")
    print('='*80)

    # Check archived tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_scraped_archive'")
    archived = cursor.fetchall()
    print(f"\n[OK] Archived Tables ({len(archived)}):")
    for table in archived:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    {table[0]}: {count} rows preserved")

    # Check new tables
    print(f"\n[OK] Fresh Tables Created:")
    for table in ['bg_reference_guns', 'bg_reference_vehicles']:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"    {table}: {count} rows (ready for manual entry)")
        except sqlite3.OperationalError:
            print(f"    {table}: [WARNING] NOT FOUND")

    # Check extraction_audit
    cursor.execute("SELECT COUNT(*) FROM extraction_audit")
    audit_count = cursor.fetchone()[0]
    print(f"\n[OK] Audit Log: {audit_count} records")

    # Show recent audit entries
    cursor.execute("""
        SELECT timestamp, table_name, action, notes
        FROM extraction_audit
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    print(f"\n  Recent Audit Entries:")
    for row in cursor.fetchall():
        print(f"    [{row[0]}] {row[1]}: {row[2]}")
        if row[3]:
            print(f"      -> {row[3]}")

    # Check equipment_battlegroup cleanup
    cursor.execute("SELECT COUNT(*) FROM equipment_battlegroup WHERE he_value IS NOT NULL")
    he_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_gun_id IS NOT NULL")
    gun_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_vehicle_id IS NOT NULL")
    veh_count = cursor.fetchone()[0]

    print(f"\n[OK] Equipment Cleanup Status:")
    print(f"    Items with HE values: {he_count} (should be 0)")
    print(f"    Items with reference_gun_id: {gun_count} (should be 0)")
    print(f"    Items with reference_vehicle_id: {veh_count} (should be 0)")

    if he_count == 0 and gun_count == 0 and veh_count == 0:
        print(f"\n[OK] All corrupted data successfully cleared!")
    else:
        print(f"\n[WARNING] Some data not cleared - check manually")

    print(f"\n{'='*80}")
    print("Migration complete. Ready for manual screenshot extraction.")
    print('='*80)

def main():
    """Execute migration"""
    print("="*80)
    print("BattleGroup Database Migration")
    print("Purpose: Archive corrupted scraped data, start fresh with manual extraction")
    print("="*80)

    # Verify database exists
    if not DB_PATH.exists():
        print(f"\n[ERROR] Database not found at {DB_PATH}")
        return

    print(f"\nDatabase: {DB_PATH}")

    # Ask for confirmation
    print(f"\n! WARNING: This will archive existing bg_reference_guns and bg_reference_vehicles tables")
    print(f"! A backup will be created first for safety")
    response = input("\nProceed with migration? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\nMigration cancelled by user")
        return

    # Create backup
    backup_path = backup_database(DB_PATH)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    # Verify expected tables exist
    expected_tables = ['bg_reference_guns', 'bg_reference_vehicles', 'equipment_battlegroup']
    if not verify_tables_exist(conn, expected_tables):
        print("\nX Migration aborted - unexpected database state")
        conn.close()
        return

    # Get SQL file paths
    script_dir = Path(__file__).parent
    sql_files = [
        script_dir / "archive_scraped_tables.sql",
        script_dir / "create_manual_extraction_tables.sql",
        script_dir / "clear_corrupted_linkages.sql"
    ]

    # Verify SQL files exist
    for sql_file in sql_files:
        if not sql_file.exists():
            print(f"\n[ERROR] SQL file not found: {sql_file}")
            conn.close()
            return

    # Execute migration scripts
    try:
        for sql_file in sql_files:
            execute_sql_file(conn, sql_file)

        # Print summary
        print_migration_summary(conn)

        print(f"\n[OK] Migration completed successfully!")
        print(f"\nBackup saved to: {backup_path}")
        print(f"\nNext steps:")
        print(f"  1. Extract reference data from BattleGroup supplements")
        print(f"  2. Validate conversion formulas")
        print(f"  3. Apply formulas to ALL 469 North Africa equipment items")

    except Exception as e:
        print(f"\n[ERROR] during migration: {e}")
        print(f"\nRolling back...")
        conn.rollback()
        print(f"\nDatabase unchanged. Backup available at: {backup_path}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
