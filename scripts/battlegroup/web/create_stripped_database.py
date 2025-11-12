#!/usr/bin/env python3
"""
Create a stripped-down database for web deployment.
Includes only essential tables needed for equipment search and display.
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# Source and destination paths
source_db = Path("../../../database/master_database.db")
dest_db = Path("database/web_database.db")

# Ensure destination directory exists
dest_db.parent.mkdir(parents=True, exist_ok=True)

# Essential tables for web equipment search/display
ESSENTIAL_TABLES = [
    # Core equipment data
    "equipment",
    "equipment_battlegroup",

    # BattleGroup reference data (manually extracted)
    "bg_reference_vehicles",
    "bg_reference_guns",
    "bg_special_rules",

    # Technical specifications
    "guns",
    "wwiitanks_afv_data",
    "wwiitanks_gun_data",
    "penetration_data",
    "ammunition",

    # Conversion formulas
    "bg_armor_conversion",
    "bg_penetration_scale",
    "bg_movement_values",
    "bg_he_effectiveness",

    # Equipment linkages
    "equipment_special_rules",

    # Optional but useful
    "afv_data",  # OnWar data for additional specs

    # Schema tracking
    "schema_version",
]

print("=" * 70)
print("CREATING STRIPPED DATABASE FOR WEB DEPLOYMENT")
print("=" * 70)
print(f"\nSource: {source_db}")
print(f"Destination: {dest_db}")
print(f"Tables to include: {len(ESSENTIAL_TABLES)}\n")

# Connect to source database
source_conn = sqlite3.connect(source_db)
source_cursor = source_conn.cursor()

# Create new destination database
if dest_db.exists():
    backup_name = f"web_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print(f"Backing up existing database to: {backup_name}")
    shutil.copy(dest_db, dest_db.parent / backup_name)
    dest_db.unlink()

dest_conn = sqlite3.connect(dest_db)
dest_cursor = dest_conn.cursor()

# Track statistics
total_rows = 0
table_stats = []

print("Copying tables:")
print("-" * 70)

for table in ESSENTIAL_TABLES:
    try:
        # Get table schema
        source_cursor.execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'"
        )
        result = source_cursor.fetchone()

        if not result:
            print(f"  ! {table:<40} NOT FOUND (skipping)")
            continue

        create_statement = result[0]

        # Create table in destination
        dest_cursor.execute(create_statement)

        # Copy data
        source_cursor.execute(f'SELECT * FROM "{table}"')
        rows = source_cursor.fetchall()

        if rows:
            # Get column count
            source_cursor.execute(f'PRAGMA table_info("{table}")')
            columns = source_cursor.fetchall()
            placeholders = ','.join(['?' for _ in columns])

            dest_cursor.executemany(
                f'INSERT INTO "{table}" VALUES ({placeholders})',
                rows
            )

        row_count = len(rows)
        total_rows += row_count
        table_stats.append((table, row_count))

        print(f"  + {table:<40} {row_count:>10,} rows")

    except Exception as e:
        print(f"  X {table:<40} ERROR: {e}")

# Copy indexes
print("\nCopying indexes:")
print("-" * 70)

source_cursor.execute(
    "SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL"
)
indexes = source_cursor.fetchall()

index_count = 0
for (index_sql,) in indexes:
    # Check if index belongs to one of our tables
    for table in ESSENTIAL_TABLES:
        if f'"{table}"' in index_sql or f'`{table}`' in index_sql or f' {table} ' in index_sql:
            try:
                dest_cursor.execute(index_sql)
                index_count += 1
                # Extract index name for display
                index_name = index_sql.split('INDEX')[1].split('ON')[0].strip()
                print(f"  + {index_name}")
                break
            except Exception as e:
                print(f"  X Index failed: {e}")

print(f"\nTotal indexes copied: {index_count}")

# Commit and close
dest_conn.commit()
source_conn.close()
dest_conn.close()

# Get file sizes
source_size = source_db.stat().st_size
dest_size = dest_db.stat().st_size
reduction = 100 * (1 - dest_size / source_size)

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Tables copied: {len([t for t, _ in table_stats])}")
print(f"Total rows: {total_rows:,}")
print(f"\nOriginal database: {source_size / (1024*1024):.2f} MB")
print(f"Stripped database: {dest_size / (1024*1024):.2f} MB")
print(f"Size reduction: {reduction:.1f}%")

# Show largest tables
print("\nLargest tables in stripped database:")
print("-" * 70)
table_stats.sort(key=lambda x: x[1], reverse=True)
for table, count in table_stats[:10]:
    print(f"  {table:<40} {count:>10,} rows")

print("\n" + "=" * 70)
print("SUCCESS: Stripped database created successfully!")
print("=" * 70)
print(f"\nNext step: Upload to Render")
print(f"File to upload: {dest_db}")
print(f"Size: {dest_size / (1024*1024):.2f} MB")
