#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean up bg_reference_vehicles - keep only manual entries (CORRECT VERSION)"""

import sys
import io
import sqlite3
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("CLEANUP: bg_reference_vehicles (CORRECT VERSION)")
print("=" * 100)

# Step 1: Check current state
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
total_before = cursor.fetchone()[0]

cursor.execute("""
    SELECT extraction_method, COUNT(*)
    FROM bg_reference_vehicles
    GROUP BY extraction_method
""")
methods = cursor.fetchall()

print(f"\n📊 BEFORE CLEANUP:")
print(f"   Total records: {total_before}")
print(f"\n   Breakdown by extraction_method:")
for method, count in methods:
    marker = "← KEEP" if method and 'manual' in method.lower() else "← DELETE"
    print(f"      {str(method or 'NULL')[:30]:30s}: {count:3d} records {marker}")

# Calculate what will remain
cursor.execute("""
    SELECT COUNT(*) FROM bg_reference_vehicles
    WHERE extraction_method LIKE '%manual%'
""")
will_remain = cursor.fetchone()[0]

print(f"\n   Will keep (manual entries): {will_remain}")
print(f"   Will delete (non-manual): {total_before - will_remain}")

# Step 2: Backup table
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"\n💾 CREATING BACKUP: {backup_table}")
cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM bg_reference_vehicles")
conn.commit()
print(f"   Backup created with {total_before} records")

# Step 3: Delete non-manual entries
print(f"\n🗑️  DELETING NON-MANUAL ENTRIES...")
cursor.execute("""
    DELETE FROM bg_reference_vehicles
    WHERE extraction_method IS NULL
       OR extraction_method NOT LIKE '%manual%'
""")
deleted_count = cursor.rowcount
conn.commit()
print(f"   Deleted {deleted_count} records")

# Step 4: Drop temp table
print(f"\n🗑️  DROPPING TEMP TABLE: bg_reference_vehicles_txt_final")
try:
    cursor.execute("DROP TABLE IF EXISTS bg_reference_vehicles_txt_final")
    conn.commit()
    print(f"   Table dropped")
except Exception as e:
    print(f"   Error: {e}")

# Step 5: Show final state
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
total_after = cursor.fetchone()[0]

cursor.execute("""
    SELECT nation, COUNT(*)
    FROM bg_reference_vehicles
    GROUP BY nation
    ORDER BY nation
""")
nations = cursor.fetchall()

print("\n" + "=" * 100)
print("CLEANUP COMPLETE")
print("=" * 100)
print(f"\nRecords before: {total_before}")
print(f"Records deleted: {deleted_count}")
print(f"Records remaining: {total_after}")

print(f"\n📊 Remaining records by nation:")
for nation, count in nations:
    print(f"   {str(nation)[:20]:20s}: {count:3d} vehicles")

# Show sample records
print(f"\n📋 Sample of remaining records (first 10):")
cursor.execute("""
    SELECT id, name, nation, vehicle_type, weapons, extraction_method
    FROM bg_reference_vehicles
    ORDER BY id
    LIMIT 10
""")
print("ID  | Name                           | Nation      | Type              | Weapons            | Method")
print("-" * 110)
for row in cursor.fetchall():
    print(f"{row[0]:3d} | {str(row[1])[:30]:30s} | {str(row[2])[:11]:11s} | {str(row[3] or '')[:17]:17s} | {str(row[4] or '')[:18]:18s} | {str(row[5] or '')[:20]}")

conn.close()

print("\n" + "=" * 100)
print(f"Backup table: {backup_table}")
print("=" * 100)
