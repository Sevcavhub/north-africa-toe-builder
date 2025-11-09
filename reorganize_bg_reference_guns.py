#!/usr/bin/env python3
"""
Reorganize bg_reference_guns table to match Excel Manual Entry Form

Excel form column order (27 columns):
1. id, 2. name, 3. common_name, 4. weapon_category, 5. nation, 6. caliber_mm,
7. he_shell_classification, 8. he_dice, 9. he_target,
10-15. he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
16-21. ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
22. source_file, 23. source_battle, 24. extraction_method,
25. verification_date, 26. screenshot_file, 27. notes

Current table: 47 columns (many duplicates, deprecated fields)

Strategy:
1. Create new table with Excel form schema
2. Copy data from old table (map old columns to new)
3. Drop old table
4. Rename new table
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DATABASE_PATH = Path(__file__).parent / "database" / "master_database.db"


def create_backup(conn):
    """Backup current table data to JSON."""
    import json

    cur = conn.cursor()
    cur.execute('SELECT * FROM bg_reference_guns')

    # Get column names
    columns = [desc[0] for desc in cur.description]

    # Fetch all data
    rows = cur.fetchall()

    # Convert to list of dicts
    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))

    # Save to file
    backup_file = f"bg_reference_guns_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"Backup created: {backup_file}")
    print(f"Backed up {len(data)} records with {len(columns)} columns")

    return backup_file


def create_new_schema(conn, dry_run=False):
    """Create new table with Excel form schema."""

    create_sql = """
    CREATE TABLE IF NOT EXISTS bg_reference_guns_new (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        common_name TEXT,
        weapon_category TEXT,
        nation TEXT,
        caliber_mm INTEGER,
        he_shell_classification TEXT,
        he_dice INTEGER,
        he_target TEXT,
        he_0_10 INTEGER,
        he_10_20 INTEGER,
        he_20_30 INTEGER,
        he_30_40 INTEGER,
        he_40_50 INTEGER,
        he_50_70 INTEGER,
        ap_0_10 INTEGER,
        ap_10_20 INTEGER,
        ap_20_30 INTEGER,
        ap_30_40 INTEGER,
        ap_40_50 INTEGER,
        ap_50_70 INTEGER,
        source_file TEXT,
        source_battle TEXT,
        extraction_method TEXT,
        verification_date TIMESTAMP,
        screenshot_file TEXT,
        notes TEXT,
        UNIQUE(name, nation)
    )
    """

    print("\n" + "=" * 80)
    print("NEW TABLE SCHEMA (27 columns)")
    print("=" * 80)
    print("\nColumns:")
    columns = [
        "1. id (INTEGER PRIMARY KEY)",
        "2. name (TEXT NOT NULL)",
        "3. common_name (TEXT)",
        "4. weapon_category (TEXT)",
        "5. nation (TEXT)",
        "6. caliber_mm (INTEGER)",
        "7. he_shell_classification (TEXT)",
        "8. he_dice (INTEGER)",
        "9. he_target (TEXT)",
        "10-15. he_0_10 through he_50_70 (INTEGER)",
        "16-21. ap_0_10 through ap_50_70 (INTEGER)",
        "22. source_file (TEXT)",
        "23. source_battle (TEXT)",
        "24. extraction_method (TEXT)",
        "25. verification_date (TIMESTAMP)",
        "26. screenshot_file (TEXT)",
        "27. notes (TEXT)"
    ]

    for col in columns:
        print(f"  {col}")

    if not dry_run:
        cur = conn.cursor()
        cur.execute(create_sql)
        conn.commit()
        print("\nOK - New table created: bg_reference_guns_new")
    else:
        print("\n[DRY-RUN] Would create table: bg_reference_guns_new")


def copy_data(conn, dry_run=False):
    """Copy data from old table to new table."""

    copy_sql = """
    INSERT INTO bg_reference_guns_new (
        id, name, common_name, weapon_category, nation, caliber_mm,
        he_shell_classification, he_dice, he_target,
        he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
        ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
        source_file, source_battle, extraction_method,
        verification_date, screenshot_file, notes
    )
    SELECT
        id, name, common_name, weapon_category, nation, caliber_mm,
        he_shell_classification, he_dice, he_target,
        he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
        ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
        source_file, source_battle, extraction_method,
        verification_date, screenshot_file, notes
    FROM bg_reference_guns
    """

    print("\n" + "=" * 80)
    print("DATA MIGRATION")
    print("=" * 80)

    if not dry_run:
        cur = conn.cursor()

        # Count rows before
        cur.execute('SELECT COUNT(*) FROM bg_reference_guns')
        old_count = cur.fetchone()[0]

        # Copy data
        cur.execute(copy_sql)
        conn.commit()

        # Count rows after
        cur.execute('SELECT COUNT(*) FROM bg_reference_guns_new')
        new_count = cur.fetchone()[0]

        print(f"\nMigrated {new_count} / {old_count} records")

        if old_count != new_count:
            print(f"WARNING: Row count mismatch! ({old_count} -> {new_count})")
        else:
            print("OK - All records migrated successfully")

    else:
        print("\n[DRY-RUN] Would copy all records from bg_reference_guns to bg_reference_guns_new")


def replace_table(conn, dry_run=False):
    """Drop old table and rename new table."""

    print("\n" + "=" * 80)
    print("TABLE REPLACEMENT")
    print("=" * 80)

    if not dry_run:
        cur = conn.cursor()

        # Drop old table
        cur.execute('DROP TABLE bg_reference_guns')

        # Rename new table
        cur.execute('ALTER TABLE bg_reference_guns_new RENAME TO bg_reference_guns')

        conn.commit()

        print("\nOK - Old table dropped")
        print("OK - New table renamed to: bg_reference_guns")

    else:
        print("\n[DRY-RUN] Would:")
        print("  1. DROP TABLE bg_reference_guns")
        print("  2. ALTER TABLE bg_reference_guns_new RENAME TO bg_reference_guns")


def verify_schema(conn):
    """Verify new table schema matches Excel form."""

    print("\n" + "=" * 80)
    print("SCHEMA VERIFICATION")
    print("=" * 80)

    cur = conn.cursor()
    cur.execute('PRAGMA table_info(bg_reference_guns)')
    columns = cur.fetchall()

    expected_columns = [
        'id', 'name', 'common_name', 'weapon_category', 'nation', 'caliber_mm',
        'he_shell_classification', 'he_dice', 'he_target',
        'he_0_10', 'he_10_20', 'he_20_30', 'he_30_40', 'he_40_50', 'he_50_70',
        'ap_0_10', 'ap_10_20', 'ap_20_30', 'ap_30_40', 'ap_40_50', 'ap_50_70',
        'source_file', 'source_battle', 'extraction_method',
        'verification_date', 'screenshot_file', 'notes'
    ]

    actual_columns = [col[1] for col in columns]

    print(f"\nExpected columns: {len(expected_columns)}")
    print(f"Actual columns:   {len(actual_columns)}")

    if actual_columns == expected_columns:
        print("\nOK - Schema matches Excel form perfectly!")
        print("\nColumn order:")
        for i, col in enumerate(actual_columns, 1):
            print(f"  {i:2}. {col}")
    else:
        print("\nERROR - Schema mismatch!")
        print("\nMissing columns:", set(expected_columns) - set(actual_columns))
        print("Extra columns:", set(actual_columns) - set(expected_columns))
        print("Order mismatch:", actual_columns != expected_columns)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Reorganize bg_reference_guns to match Excel form"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database"
    )

    args = parser.parse_args()

    conn = sqlite3.connect(DATABASE_PATH)

    try:
        if not args.dry_run:
            # Create backup first
            backup_file = create_backup(conn)

        # Create new schema
        create_new_schema(conn, dry_run=args.dry_run)

        # Copy data
        copy_data(conn, dry_run=args.dry_run)

        # Replace table
        replace_table(conn, dry_run=args.dry_run)

        # Verify
        if not args.dry_run:
            verify_schema(conn)

            print("\n" + "=" * 80)
            print("REORGANIZATION COMPLETE")
            print("=" * 80)
            print(f"\nBackup saved to: {backup_file}")
            print("Table reorganized to match Excel form (27 columns)")

        else:
            print("\n" + "=" * 80)
            print("[DRY-RUN] No changes applied")
            print("=" * 80)
            print("\nRun without --dry-run to apply changes")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
