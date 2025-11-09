#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check imported vehicles from final parser"""

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
print("IMPORTED VEHICLES FROM FINAL PARSER")
print("=" * 100)

cursor.execute("""
    SELECT name, off_road_inches, road_inches, special_movement,
           armor_front, armor_side, armor_rear,
           weapons, mount, ammo, open_topped
    FROM bg_reference_vehicles_txt_final
    ORDER BY name
""")

vehicles = cursor.fetchall()

print(f"\nTotal vehicles: {len(vehicles)}\n")

for v in vehicles:
    name, off, road, special, af, aside, ar, weapons, mount, ammo, open_top = v
    print(f"📋 {name:30s}")
    print(f"   Move: {off}/{road}  Special: {special or '-'}")
    print(f"   Armor: {af}-{aside}-{ar}")
    print(f"   Weapons: {weapons or 'NONE'}")
    print(f"   Mount:   {mount or 'NONE'}")
    print(f"   Ammo:    {ammo or 'NONE'}")
    print(f"   Open-topped: {open_top or '-'}")
    print()

conn.close()

print("\n" + "=" * 100)
print("ANALYSIS")
print("=" * 100)
print(f"✅ Vehicles with weapons: {sum(1 for v in vehicles if v[7])}")
print(f"✅ Vehicles with mounts: {sum(1 for v in vehicles if v[8])}")
print(f"✅ Vehicles with ammo: {sum(1 for v in vehicles if v[9])}")
print(f"✅ Vehicles with special movement: {sum(1 for v in vehicles if v[3])}")
print(f"⚠️  Expected total: 29")
print(f"⚠️  Actual total: {len(vehicles)}")
print(f"⚠️  Missing: {29 - len(vehicles)}")
