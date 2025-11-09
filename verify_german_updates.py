#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify German vehicle weapon_1 and ammo_1 updates"""

import sys
import io
import sqlite3

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 100)
print("VERIFICATION: German Vehicles (Corrected Weapon_1 and Ammo_1)")
print("=" * 100)

cursor.execute("""
    SELECT id, name, weapon_1, ammo_1
    FROM bg_reference_vehicles
    WHERE nation = 'german'
      AND weapon_1 IS NOT NULL
      AND weapon_1 != 'MG'
    ORDER BY id
""")

german_vehicles = cursor.fetchall()
print(f"\nTotal German vehicles with main guns: {len(german_vehicles)}\n")

for row in german_vehicles:
    ammo_str = row['ammo_1'] or '(none)'
    print(f"ID {row['id']:3d}: {row['name'][:35]:35s} | Weapon: {row['weapon_1'][:25]:25s} | Ammo: {ammo_str}")

# Also show final schema
print("\n" + "=" * 100)
print("FINAL SCHEMA")
print("=" * 100)

cursor.execute("PRAGMA table_info(bg_reference_vehicles)")
columns = cursor.fetchall()

print("\nColumn order (first 25 columns):")
for i, col in enumerate(columns[:25], 1):
    print(f"  {i:2d}. {col[1]:30s} {col[2]}")

print(f"  ... ({len(columns)} total columns)")

# Summary stats
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE ammo_1 IS NOT NULL AND ammo_1 != ''")
with_ammo = cursor.fetchone()[0]

print(f"\n" + "=" * 100)
print("DATABASE SUMMARY")
print("=" * 100)
print(f"Total vehicles:         {total}")
print(f"Vehicles with ammo_1:   {with_ammo}")
print(f"Coverage:               {with_ammo}/{total} ({100*with_ammo/total:.1f}%)")

conn.close()
