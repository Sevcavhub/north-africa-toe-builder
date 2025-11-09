#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check which table is which and weapon counts"""

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
print("TABLE COMPARISON")
print("=" * 100)

# Check bg_reference_vehicles
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
bg_ref_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation = 'British'")
bg_ref_british = cursor.fetchone()[0]

print(f"\n📊 bg_reference_vehicles:")
print(f"   Total records: {bg_ref_count}")
print(f"   British vehicles: {bg_ref_british}")

# Check bg_reference_vehicles_txt_final
try:
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles_txt_final")
    txt_final_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles_txt_final WHERE nation = 'British'")
    txt_final_british = cursor.fetchone()[0]

    print(f"\n📊 bg_reference_vehicles_txt_final:")
    print(f"   Total records: {txt_final_count}")
    print(f"   British vehicles: {txt_final_british}")
except:
    print(f"\n📊 bg_reference_vehicles_txt_final: Does not exist")

print("\n" + "=" * 100)
print("MANUAL BRITISH ENTRIES - WHERE ARE THEY?")
print("=" * 100)

# Check for manually entered British vehicles
cursor.execute("""
    SELECT id, name, weapons, extraction_method, source_file
    FROM bg_reference_vehicles
    WHERE nation = 'British'
    ORDER BY id
    LIMIT 10
""")

print("\nFirst 10 British vehicles in bg_reference_vehicles:")
print("ID  | Name                           | Weapons              | Method       | Source")
print("-" * 100)
for row in cursor.fetchall():
    print(f"{row[0]:3d} | {str(row[1])[:30]:30s} | {str(row[2] or '')[:20]:20s} | {str(row[3] or '')[:12]:12s} | {str(row[4] or '')[:20]:20s}")

print("\n" + "=" * 100)
print("MORRIS CS9 CHECK (ID 165)")
print("=" * 100)

cursor.execute("SELECT id, name, weapons FROM bg_reference_vehicles WHERE id = 165")
row = cursor.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"Name: {row[1]}")
    print(f"Weapons: {row[2]}")

    if row[2]:
        weapon_list = [w.strip() for w in row[2].split(',')]
        print(f"Weapon count: {len(weapon_list)}")
        for i, w in enumerate(weapon_list, 1):
            print(f"  {i}. {w}")
else:
    print("ID 165 not found")

# Check for Morris in general
cursor.execute("SELECT id, name, weapons FROM bg_reference_vehicles WHERE name LIKE '%Morris%'")
morris_vehicles = cursor.fetchall()
print(f"\nAll Morris vehicles in bg_reference_vehicles:")
for row in morris_vehicles:
    weapon_count = len(row[2].split(',')) if row[2] else 0
    print(f"  ID {row[0]:3d}: {row[1]:30s} - {weapon_count} weapons")

print("\n" + "=" * 100)
print("VEHICLES WITH >3 WEAPONS")
print("=" * 100)

cursor.execute("SELECT id, name, weapons FROM bg_reference_vehicles WHERE weapons IS NOT NULL")
vehicles_with_many_weapons = []
for row in cursor.fetchall():
    weapon_list = [w.strip() for w in row[2].split(',')]
    if len(weapon_list) > 3:
        vehicles_with_many_weapons.append((row[0], row[1], len(weapon_list), row[2]))

if vehicles_with_many_weapons:
    print(f"Found {len(vehicles_with_many_weapons)} vehicles with >3 weapons:")
    for vid, vname, count, weapons in vehicles_with_many_weapons:
        print(f"\n  ID {vid:3d}: {vname} ({count} weapons)")
        print(f"    Weapons: {weapons}")
else:
    print("No vehicles with >3 weapons found in bg_reference_vehicles")

conn.close()
