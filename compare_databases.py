#!/usr/bin/env python3
"""Compare web_database.db vs master_database.db"""

import sqlite3
from pathlib import Path

def get_table_counts(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    counts = {}
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except:
            counts[table] = "ERROR"

    conn.close()
    return counts

print("Database Comparison")
print("=" * 70)

web_db = Path("scripts/battlegroup/web/database/web_database.db")
master_db = Path("database/master_database.db")

print(f"\nWEB_DATABASE.DB ({web_db}):")
if web_db.exists():
    web_counts = get_table_counts(web_db)
    for table, count in web_counts.items():
        print(f"  {table}: {count} rows")
else:
    print("  NOT FOUND")

print(f"\nMASTER_DATABASE.DB ({master_db}):")
if master_db.exists():
    master_counts = get_table_counts(master_db)
    for table, count in master_counts.items():
        print(f"  {table}: {count} rows")
else:
    print("  NOT FOUND")

# Check for bg_builder tables specifically
print("\n" + "=" * 70)
print("BG_BUILDER TABLES COMPARISON:")
print("=" * 70)

bg_tables = ['bg_builder_vehicles', 'bg_builder_weapons', 'bg_builder_vehicle_costs']

for table in bg_tables:
    web_count = web_counts.get(table, 0) if web_db.exists() else 0
    master_count = master_counts.get(table, 0) if master_db.exists() else 0

    print(f"{table}:")
    print(f"  web_database.db: {web_count}")
    print(f"  master_database.db: {master_count}")

    if master_count > 0:
        print(f"  RECOMMENDATION: Use master_database.db (has {master_count} rows)")
    elif web_count > 0:
        print(f"  RECOMMENDATION: Use web_database.db (has {web_count} rows)")
    else:
        print(f"  WARNING: Table missing in both databases!")
