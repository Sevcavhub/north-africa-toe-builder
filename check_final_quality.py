#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check final parser data quality"""

import sys
import io
import sqlite3

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("FINAL PARSER DATA QUALITY CHECK")
print("=" * 100)

# Check specific vehicles mentioned by user
test_vehicles = ['Crusader I', 'A10', 'Matilda II', 'Matilda II CS']

for vname in test_vehicles:
    cursor.execute("""
        SELECT name, off_road_inches, road_inches, special_movement,
               armor_front, armor_side, armor_rear,
               weapons, mount, ammo, open_topped
        FROM bg_reference_vehicles_txt_final
        WHERE name = ?
    """, (vname,))

    row = cursor.fetchone()
    if row:
        print(f"\n📋 {row[0]}")
        print(f"   Movement: {row[1]}/{row[2]}  Special: {row[3] or '-'}")
        print(f"   Armor: {row[4]}-{row[5]}-{row[6]}")
        print(f"   Weapons: [{row[7]}]")
        print(f"   Mount:   [{row[8]}]")
        print(f"   Ammo:    [{row[9]}]")
        print(f"   Open-topped: {row[10] or '-'}")

# Count summary
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles_txt_final")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles_txt_final WHERE weapons IS NOT NULL AND weapons != ''")
with_weapons = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles_txt_final WHERE mount IS NOT NULL AND mount != ''")
with_mounts = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles_txt_final WHERE armor_rear IS NOT NULL")
with_rear_armor = cursor.fetchone()[0]

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Total vehicles: {total}")
print(f"Vehicles with weapons: {with_weapons}/{total} ({100*with_weapons/total:.1f}%)")
print(f"Vehicles with mounts: {with_mounts}/{total} ({100*with_mounts/total:.1f}%)")
print(f"Vehicles with rear armor: {with_rear_armor}/{total} ({100*with_rear_armor/total:.1f}%)")

# Find duplicates
cursor.execute("""
    SELECT name, COUNT(*) as cnt
    FROM bg_reference_vehicles_txt_final
    GROUP BY name
    HAVING cnt > 1
""")
dupes = cursor.fetchall()
if dupes:
    print(f"\n⚠️  Duplicates found:")
    for name, count in dupes:
        print(f"   - {name} (x{count})")

conn.close()
