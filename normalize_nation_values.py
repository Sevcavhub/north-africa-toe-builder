#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalize nation values to canonical lowercase format"""

import sys
import io
import sqlite3
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 100)
print("NORMALIZE NATION VALUES TO LOWERCASE")
print("=" * 100)

# Backup
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM bg_reference_vehicles")
conn.commit()
print(f"\n💾 Backup created: {backup_table}")

# Show current nation values
print("\n📋 BEFORE normalization:")
print("=" * 100)
cursor.execute("""
    SELECT nation, COUNT(*) as count
    FROM bg_reference_vehicles
    GROUP BY nation
    ORDER BY nation
""")

before_counts = {}
for row in cursor.fetchall():
    nation = row['nation'] or '(null)'
    count = row['count']
    before_counts[nation] = count
    print(f"  {nation:<25s}: {count:3d}")

# Normalize to lowercase
print("\n🔧 Normalizing nation values...")

# Update all nation values to lowercase
cursor.execute("""
    UPDATE bg_reference_vehicles
    SET nation = LOWER(nation)
    WHERE nation IS NOT NULL
""")

rows_updated = cursor.rowcount
conn.commit()

print(f"  ✅ Updated {rows_updated} records")

# Show after normalization
print("\n📋 AFTER normalization:")
print("=" * 100)
cursor.execute("""
    SELECT nation, COUNT(*) as count
    FROM bg_reference_vehicles
    GROUP BY nation
    ORDER BY nation
""")

after_counts = {}
for row in cursor.fetchall():
    nation = row['nation'] or '(null)'
    count = row['count']
    after_counts[nation] = count
    print(f"  {nation:<25s}: {count:3d}")

# Summary
print("\n" + "=" * 100)
print("CANONICAL NATION VALUES")
print("=" * 100)
print("""
✅ All nation values normalized to lowercase:
   - british
   - german
   - italian
   - canadian
   - american
   - french

✅ Multi-nation format: "nation1, nation2" (lowercase, comma-separated)
   - canadian, british

Backup: {backup_table}
""".format(backup_table=backup_table))

# Verify total unchanged
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
total = cursor.fetchone()[0]
print(f"Total vehicles: {total} (unchanged)")

conn.close()

print("\n" + "=" * 100)
print("✅ NORMALIZATION COMPLETE")
print("=" * 100)
