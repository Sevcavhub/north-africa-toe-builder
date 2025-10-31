#!/usr/bin/env python3
"""
Migrate BattleGroup Reference Tables to Master Database

Moves bg_reference_vehicles, bg_reference_guns, and extraction_log tables
from battlegroup_reference.db into master_database.db for unified integration.

Also creates bg_equipment_mapping table to link BattleGroup vehicles to our
equipment table (469 items).

Usage:
    python scripts/battlegroup/migrate_to_master_db.py
    python scripts/battlegroup/migrate_to_master_db.py --verify  # Verify only, no changes
"""

import sqlite3
from pathlib import Path
import argparse
from typing import Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
MASTER_DB = PROJECT_ROOT / "database" / "master_database.db"
BG_DB = PROJECT_ROOT / "database" / "battlegroup_reference.db"


def verify_databases():
    """Check that both databases exist and have expected tables"""
    print("Verifying databases...")

    if not MASTER_DB.exists():
        print(f"[ERROR] Master database not found: {MASTER_DB}")
        return False

    if not BG_DB.exists():
        print(f"[ERROR] BattleGroup database not found: {BG_DB}")
        return False

    # Check BG database has expected tables
    bg_conn = sqlite3.connect(BG_DB)
    bg_cursor = bg_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE 'bg_%' OR name = 'extraction_log')"
    )
    bg_tables = [row[0] for row in bg_cursor.fetchall()]
    bg_conn.close()

    expected = ['bg_reference_vehicles', 'bg_reference_guns', 'extraction_log']
    missing = [t for t in expected if t not in bg_tables]

    if missing:
        print(f"[ERROR] Missing tables in BG database: {missing}")
        return False

    print(f"[OK] Master DB: {MASTER_DB}")
    print(f"[OK] BattleGroup DB: {BG_DB}")
    print(f"[OK] Found tables: {', '.join(bg_tables)}")

    return True


def get_table_counts(db_path: Path) -> Dict[str, int]:
    """Get row counts for all BattleGroup tables"""
    conn = sqlite3.connect(db_path)
    counts = {}

    for table in ['bg_reference_vehicles', 'bg_reference_guns', 'extraction_log']:
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            counts[table] = 0

    conn.close()
    return counts


def migrate_tables():
    """Migrate BattleGroup tables to master database"""
    print("\n" + "="*70)
    print("MIGRATING BATTLEGROUP TABLES TO MASTER DATABASE")
    print("="*70)

    # Get pre-migration counts
    bg_counts = get_table_counts(BG_DB)
    print("\n[SOURCE] BattleGroup database row counts:")
    for table, count in bg_counts.items():
        print(f"  - {table}: {count} rows")

    # Connect to both databases
    master_conn = sqlite3.connect(MASTER_DB)
    bg_conn = sqlite3.connect(BG_DB)

    try:
        # 1. Create tables in master database (if they don't exist)
        print("\n[STEP 1] Creating tables in master database...")

        # Get table schemas from BG database
        for table in ['bg_reference_vehicles', 'bg_reference_guns', 'extraction_log']:
            # Get CREATE TABLE statement
            cursor = bg_conn.execute(
                f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            create_sql = cursor.fetchone()[0]

            # Create table in master database (will fail if exists, which is fine)
            try:
                master_conn.execute(create_sql)
                print(f"  [OK] Created table: {table}")
            except sqlite3.OperationalError as e:
                if "already exists" in str(e):
                    print(f"  [EXISTS] Table already exists: {table}")
                else:
                    raise

        master_conn.commit()

        # 2. Copy data from BG database to master database
        print("\n[STEP 2] Copying data to master database...")

        for table in ['bg_reference_vehicles', 'bg_reference_guns', 'extraction_log']:
            # Get all rows from BG database
            cursor = bg_conn.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            if not rows:
                print(f"  [SKIP] No data in {table}")
                continue

            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            columns_str = ", ".join(column_names)
            placeholders = ", ".join(["?" for _ in column_names])

            # Insert into master database (ON CONFLICT IGNORE to skip duplicates)
            insert_sql = f"INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})"

            inserted = 0
            for row in rows:
                try:
                    master_conn.execute(insert_sql, row)
                    inserted += 1
                except sqlite3.IntegrityError:
                    pass  # Duplicate, skip

            master_conn.commit()
            print(f"  [OK] {table}: {inserted}/{len(rows)} rows inserted (duplicates skipped)")

        # 3. Create equipment mapping table
        print("\n[STEP 3] Creating equipment mapping table...")

        master_conn.execute("""
            CREATE TABLE IF NOT EXISTS bg_equipment_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bg_vehicle_id INTEGER REFERENCES bg_reference_vehicles(id),
                equipment_id INTEGER REFERENCES equipment(id),
                match_confidence INTEGER,  -- 100=exact, 85=partial, 70=fuzzy
                match_method TEXT,  -- 'manual', 'name_exact', 'name_fuzzy', 'alias'
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(bg_vehicle_id, equipment_id)
            )
        """)
        master_conn.commit()
        print("  [OK] Created bg_equipment_mapping table")

        # 4. Verify migration
        print("\n[STEP 4] Verifying migration...")
        master_counts = get_table_counts(MASTER_DB)

        print("\n[TARGET] Master database row counts:")
        for table, count in master_counts.items():
            print(f"  - {table}: {count} rows")

        # Check if counts match
        all_good = True
        for table in ['bg_reference_vehicles', 'bg_reference_guns', 'extraction_log']:
            if master_counts[table] < bg_counts[table]:
                print(f"  [WARN] {table}: Expected {bg_counts[table]}, got {master_counts[table]}")
                all_good = False

        if all_good:
            print("\n[OK] Migration successful! All data verified.")
        else:
            print("\n[WARN] Some data may not have migrated completely. Review warnings above.")

    finally:
        master_conn.close()
        bg_conn.close()

    print("\n" + "="*70)
    print("MIGRATION COMPLETE")
    print("="*70)
    print(f"\nMaster database: {MASTER_DB}")
    print("\nNext steps:")
    print("1. Update scripts/battlegroup/scrapers/datacard_scraper.py to use master_database.db")
    print("2. Delete database/battlegroup_reference.db (no longer needed)")
    print("3. Test extraction to verify new configuration")


def verify_only():
    """Verify migration without making changes"""
    print("\n" + "="*70)
    print("VERIFICATION MODE - NO CHANGES WILL BE MADE")
    print("="*70)

    # Check BG database
    bg_counts = get_table_counts(BG_DB)
    print("\n[SOURCE] BattleGroup database:")
    for table, count in bg_counts.items():
        print(f"  - {table}: {count} rows")

    # Check master database
    master_counts = get_table_counts(MASTER_DB)
    print("\n[TARGET] Master database:")
    for table, count in master_counts.items():
        status = "[EXISTS]" if count > 0 else "[MISSING]"
        print(f"  {status} {table}: {count} rows")

    # Check if migration is needed
    needs_migration = False
    for table in ['bg_reference_vehicles', 'bg_reference_guns']:
        if master_counts.get(table, 0) == 0 and bg_counts.get(table, 0) > 0:
            needs_migration = True
            break

    if needs_migration:
        print("\n[ACTION] Migration needed - run without --verify to migrate")
    else:
        print("\n[OK] Tables already exist in master database")

    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(description="Migrate BattleGroup tables to master database")
    parser.add_argument('--verify', action='store_true', help="Verify only, no changes")
    args = parser.parse_args()

    if not verify_databases():
        print("\n[ERROR] Database verification failed. Aborting.")
        return 1

    if args.verify:
        verify_only()
    else:
        response = input("\nProceed with migration? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            migrate_tables()
        else:
            print("Migration cancelled.")

    return 0


if __name__ == "__main__":
    exit(main())
