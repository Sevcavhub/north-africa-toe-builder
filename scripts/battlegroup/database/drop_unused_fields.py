"""
Drop unused fields from bg_reference_vehicles table.

Fields to remove:
- points_cost (handled in army lists instead)
- battle_rating (handled in army lists instead)
- created_at (unnecessary timestamp)
- unit_experience (not applicable to reference data)
- verified_by (unnecessary metadata)
- verification_date (unnecessary timestamp)

These were accidentally included during initial extraction.
"""

import sqlite3

DB_PATH = 'database/master_database.db'

FIELDS_TO_DROP = [
    'points_cost',
    'battle_rating',
    'created_at',
    'unit_experience',
    'verified_by',
    'verification_date'
]

def check_sqlite_version():
    """Check if SQLite supports ALTER TABLE DROP COLUMN (v3.35.0+)"""
    conn = sqlite3.connect(':memory:')
    version = conn.execute('SELECT sqlite_version()').fetchone()[0]
    conn.close()

    major, minor, patch = map(int, version.split('.'))
    supports_drop = (major > 3) or (major == 3 and minor >= 35)

    return version, supports_drop


def check_data_loss(cursor):
    """Check if any of the fields contain non-NULL data"""
    print("Checking for data in fields to be dropped:\n")

    has_data = {}

    for field in FIELDS_TO_DROP:
        cursor.execute(f"SELECT COUNT(*) FROM bg_reference_vehicles WHERE {field} IS NOT NULL")
        count = cursor.fetchone()[0]
        has_data[field] = count

        if count > 0:
            print(f"  {field}: {count} records with data")
            # Show sample values
            cursor.execute(f"SELECT DISTINCT {field} FROM bg_reference_vehicles WHERE {field} IS NOT NULL LIMIT 3")
            samples = cursor.fetchall()
            for sample in samples:
                print(f"    Sample: {sample[0]}")
        else:
            print(f"  {field}: 0 records (all NULL)")

    return has_data


def drop_fields_modern(cursor):
    """Drop columns using ALTER TABLE DROP COLUMN (SQLite 3.35+)"""
    for field in FIELDS_TO_DROP:
        print(f"Dropping column: {field}")
        cursor.execute(f"ALTER TABLE bg_reference_vehicles DROP COLUMN {field}")


def drop_fields_legacy(conn, cursor):
    """
    Drop columns using table recreation (for older SQLite versions).

    Steps:
    1. Create new table without unwanted columns
    2. Copy data
    3. Drop old table
    4. Rename new table
    """
    print("Using legacy method (table recreation)...")

    # Get current schema
    cursor.execute('PRAGMA table_info(bg_reference_vehicles)')
    all_columns = cursor.fetchall()

    # Filter out columns to drop
    keep_columns = [col for col in all_columns if col[1] not in FIELDS_TO_DROP]

    # Build new table schema
    new_columns = []
    for col in keep_columns:
        col_def = f"{col[1]} {col[2]}"
        if col[3]:  # NOT NULL
            col_def += " NOT NULL"
        if col[4] is not None:  # DEFAULT value
            col_def += f" DEFAULT {col[4]}"
        if col[5]:  # PRIMARY KEY
            col_def += " PRIMARY KEY"
        new_columns.append(col_def)

    create_sql = f"CREATE TABLE bg_reference_vehicles_new ({', '.join(new_columns)})"

    print("\nCreating new table...")
    cursor.execute(create_sql)

    # Copy data
    keep_column_names = [col[1] for col in keep_columns]
    columns_str = ', '.join(keep_column_names)

    print("Copying data...")
    cursor.execute(f"""
        INSERT INTO bg_reference_vehicles_new ({columns_str})
        SELECT {columns_str}
        FROM bg_reference_vehicles
    """)

    # Drop old table
    print("Dropping old table...")
    cursor.execute("DROP TABLE bg_reference_vehicles")

    # Rename new table
    print("Renaming new table...")
    cursor.execute("ALTER TABLE bg_reference_vehicles_new RENAME TO bg_reference_vehicles")


def drop_unused_fields(dry_run=True):
    """
    Drop unused fields from bg_reference_vehicles table.

    Args:
        dry_run: If True, only show what would be done
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check SQLite version
    version, supports_drop = check_sqlite_version()
    print(f"SQLite version: {version}")
    print(f"Supports ALTER TABLE DROP COLUMN: {supports_drop}")
    print()

    # Check current schema
    cursor.execute('PRAGMA table_info(bg_reference_vehicles)')
    current_columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {len(current_columns)}")

    # Verify fields exist
    fields_exist = [f for f in FIELDS_TO_DROP if f in current_columns]
    fields_missing = [f for f in FIELDS_TO_DROP if f not in current_columns]

    if fields_missing:
        print(f"\nWARNING: Fields not found in table: {', '.join(fields_missing)}")

    if not fields_exist:
        print("\nNo fields to drop.")
        conn.close()
        return

    print(f"\nFields to drop: {len(fields_exist)}")
    for field in fields_exist:
        print(f"  - {field}")
    print()

    # Check for data loss
    has_data = check_data_loss(cursor)
    total_data = sum(has_data.values())

    if total_data > 0:
        print(f"\nWARNING: {total_data} total non-NULL values will be lost")
    else:
        print("\nNo data will be lost (all fields are NULL)")

    if not dry_run:
        try:
            conn.execute('BEGIN TRANSACTION')

            if supports_drop:
                drop_fields_modern(cursor)
            else:
                drop_fields_legacy(conn, cursor)

            conn.commit()

            # Verify final schema
            cursor.execute('PRAGMA table_info(bg_reference_vehicles)')
            final_columns = [col[1] for col in cursor.fetchall()]

            print(f"\n[SUCCESS] Dropped {len(fields_exist)} columns.")
            print(f"Final column count: {len(final_columns)} (was {len(current_columns)})")

        except Exception as e:
            conn.rollback()
            print(f"\n[ERROR] {e}")
            raise
    else:
        print(f"\n[DRY RUN] Would drop {len(fields_exist)} columns.")
        print(f"   Final column count: {len(current_columns) - len(fields_exist)} (currently {len(current_columns)})")
        print("   Run with dry_run=False to apply changes.")

    conn.close()


if __name__ == '__main__':
    import sys

    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("EXECUTING CHANGES")
        print("=" * 60)
    else:
        print("DRY RUN MODE")
        print("=" * 60)
        print("To execute: python drop_unused_fields.py --execute")
        print("=" * 60)

    print()
    drop_unused_fields(dry_run=dry_run)
