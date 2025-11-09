#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import ammo data from CSV back into database"""

import sys
import io
import sqlite3
import csv
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
input_csv = r"D:\north-africa-toe-builder\vehicles_ammo_entry.csv"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("IMPORT AMMO DATA FROM CSV")
print("=" * 100)

# Backup
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM bg_reference_vehicles")
conn.commit()
print(f"\n💾 Backup created: {backup_table}")

# Read CSV
print(f"\n📖 Reading {input_csv}...")

stats = {
    'total': 0,
    'updated': 0,
    'skipped': 0,
    'errors': 0
}

with open(input_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for row in reader:
        stats['total'] += 1
        vehicle_id = int(row['id'])
        ammo_value = row['ammo'].strip() if row['ammo'] else None

        # Skip if ammo is empty
        if not ammo_value:
            stats['skipped'] += 1
            continue

        # Update database
        try:
            cursor.execute("""
                UPDATE bg_reference_vehicles
                SET ammo = ?
                WHERE id = ?
            """, (ammo_value, vehicle_id))

            stats['updated'] += 1

            # Show updates
            if stats['updated'] <= 10:
                print(f"  ID {vehicle_id:3d}: {row['name'][:35]:35s} → ammo={ammo_value}")

        except Exception as e:
            print(f"  ⚠️  Error updating ID {vehicle_id}: {e}")
            stats['errors'] += 1

conn.commit()

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"""
Total records in CSV:     {stats['total']}
Records updated:          {stats['updated']}
Records skipped (blank):  {stats['skipped']}
Errors:                   {stats['errors']}

Backup: {backup_table}
""")

# Verify
cursor.execute("""
    SELECT COUNT(*)
    FROM bg_reference_vehicles
    WHERE ammo IS NOT NULL AND ammo != ''
""")
total_with_ammo = cursor.fetchone()[0]

print(f"✅ Total vehicles with ammo after import: {total_with_ammo}")

# Show sample
cursor.execute("""
    SELECT id, name, weapon_1, ammo
    FROM bg_reference_vehicles
    WHERE ammo IS NOT NULL AND ammo != ''
    ORDER BY id
    LIMIT 15
""")

print(f"\n📋 Sample of vehicles with ammo:")
print("=" * 100)
for row in cursor.fetchall():
    print(f"ID {row[0]:3d}: {row[1][:35]:35s} | Weapon: {row[2][:20]:20s} | Ammo: {row[3]}")

conn.close()

print("\n" + "=" * 100)
print("✅ IMPORT COMPLETE")
print("=" * 100)
