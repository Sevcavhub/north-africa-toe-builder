#!/usr/bin/env python3
"""
Database Audit - Analyze all SQLite databases in project
"""

import sqlite3
import os
from pathlib import Path

# All databases found
databases = [
    "./data/iterations/iteration_1/North Africa Campaign Production/_MASTER_CONTROL/DATABASES/ARCHIVES/north_africa_wargame_backup_pre_correction.db",
    "./data/iterations/iteration_1/North Africa Campaign Production/_MASTER_CONTROL/DATABASES/ARCHIVES/pre_consolidation_backup_20250911_170116.db",
    "./data/iterations/iteration_1/North Africa Campaign Production/_MASTER_CONTROL/DATABASES/ARCHIVES/pre_consolidation_backup_20250911_170154.db",
    "./data/iterations/iteration_1/North Africa Campaign Production/_MASTER_CONTROL/SCRIPTS/VALIDATION/game_systems_validation.db",
    "./data/iterations/iteration_1/North Africa Campaign Production/08_Database/north_africa_wargame.db",
    "./data/iterations/iteration_1/North Africa Campaign Production/08_Database/north_africa_wargame_backup_before_cleanup.db",
    "./data/iterations/iteration_1/North Africa Campaign Production/08_Database/north_africa_wargame_backup_datasette.db",
    "./data/iterations/iteration_1/North Africa Campaign Production/08_Database/witw_data.db",
    "./data/iterations/iteration_1/North Africa Campaign Production/TEMP_WORKSPACE/web_research_reference.db",
    "./data/iterations/iteration_2/Timeline_TOE_Reconstruction/ARCHIVES/witw_data_backup_20250929_130139.db",
    "./data/iterations/iteration_2/Timeline_TOE_Reconstruction/witw_data.db",
    "./data/toe_database.db",
    "./database/master_database.db",
    "./database/master_database_backup_20251029.db",
    "./master_database.db"
]

print("=" * 100)
print("DATABASE AUDIT REPORT")
print("=" * 100)

for db_path in databases:
    full_path = Path(db_path)

    if not full_path.exists():
        print(f"\n{db_path}")
        print(f"  STATUS: FILE NOT FOUND")
        continue

    # Get file size
    size = full_path.stat().st_size
    size_mb = size / (1024 * 1024)

    print(f"\n{db_path}")
    print(f"  Size: {size_mb:.2f} MB ({size:,} bytes)")

    # Try to open and get tables
    try:
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"  Tables: {len(tables)}")

        if tables:
            # Get row counts for each table
            table_info = []
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_info.append((table, count))
                except:
                    table_info.append((table, "ERROR"))

            # Show tables with counts
            for table, count in table_info:
                print(f"    - {table:40s}: {count:>10s} rows" if isinstance(count, str) else f"    - {table:40s}: {count:>10,} rows")

        conn.close()

    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 100)
print("AUDIT COMPLETE")
print("=" * 100)
