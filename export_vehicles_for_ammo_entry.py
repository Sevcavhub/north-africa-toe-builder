#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export vehicles for ammo data entry (weapon_1 not null and not MG-only)"""

import sys
import io
import sqlite3
import csv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
output_csv = r"D:\north-africa-toe-builder\vehicles_ammo_entry.csv"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 100)
print("EXPORT VEHICLES FOR AMMO DATA ENTRY")
print("=" * 100)

# Get vehicles with weapon_1 that is not null and not just 'MG'
cursor.execute("""
    SELECT id, name, weapon_1, weapon_2, weapon_3, weapon_4,
           mount_1, mount_2, mount_3, mount_4,
           ammo, nation, vehicle_type
    FROM bg_reference_vehicles
    WHERE weapon_1 IS NOT NULL
      AND weapon_1 != 'MG'
      AND weapon_1 != ''
    ORDER BY nation, name
""")

vehicles = cursor.fetchall()

print(f"\nFound {len(vehicles)} vehicles with weapon_1 (not MG)")

# Write to CSV
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Header
    writer.writerow([
        'id',
        'name',
        'nation',
        'vehicle_type',
        'weapon_1',
        'mount_1',
        'weapon_2',
        'mount_2',
        'weapon_3',
        'mount_3',
        'weapon_4',
        'mount_4',
        'ammo'
    ])

    # Data rows
    for row in vehicles:
        writer.writerow([
            row['id'],
            row['name'],
            row['nation'],
            row['vehicle_type'],
            row['weapon_1'],
            row['mount_1'],
            row['weapon_2'],
            row['mount_2'],
            row['weapon_3'],
            row['mount_3'],
            row['weapon_4'],
            row['mount_4'],
            row['ammo']
        ])

conn.close()

print(f"\n✅ CSV exported: {output_csv}")
print(f"✅ Total records: {len(vehicles)}")

# Show sample
print(f"\n📋 Sample (first 10 records):")
print("=" * 100)
print(f"{'ID':<5} {'Name':<30} {'Nation':<10} {'Weapon 1':<20} {'Mount':<12} {'Ammo':<6}")
print("-" * 100)

with open(output_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 10:
            break
        print(f"{row['id']:<5} {row['name']:<30} {row['nation']:<10} {row['weapon_1']:<20} {row['mount_1'] or 'None':<12} {row['ammo'] or '':<6}")

print("\n" + "=" * 100)
print("INSTRUCTIONS")
print("=" * 100)
print("""
1. Open vehicles_ammo_entry.csv in Excel
2. Fill in the 'ammo' column for each vehicle
3. Save the CSV
4. Run import script to update database

Note:
- MG-only vehicles excluded (no main gun ammo needed)
- All weapons shown to help identify correct ammo values
- Leave blank if vehicle has no ammo limitation
""")
print("=" * 100)
