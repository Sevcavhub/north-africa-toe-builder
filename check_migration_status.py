#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check current schema vs Excel template - what's left to do?"""

import sys
import io
import sqlite3
import pandas as pd

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
excel_file = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Vehicles Tobruk Input form for OCR.xlsx"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("SCHEMA MIGRATION STATUS")
print("=" * 100)

# Get current schema
cursor.execute("PRAGMA table_info(bg_reference_vehicles)")
current_columns = {col[1]: col[2] for col in cursor.fetchall()}

# Get Excel template schema
df = pd.read_excel(excel_file)
excel_columns = list(df.columns)

# Additional fields to keep
additional_fields = ['source_file', 'source_document', 'source_battle', 'extraction_method', 'screenshot_file']

print("\n📊 EXCEL TEMPLATE (23 columns):")
for i, col in enumerate(excel_columns, 1):
    status = "✅" if col in current_columns else "❌ MISSING"
    print(f"   {i:2d}. {col:30s} {status}")

print("\n📊 ADDITIONAL FIELDS TO KEEP (5 columns):")
for col in additional_fields:
    status = "✅" if col in current_columns else "❌ MISSING"
    print(f"       {col:30s} {status}")

print("\n📊 CURRENT SCHEMA FIELDS NOT IN TEMPLATE:")
current_only = set(current_columns.keys()) - set(excel_columns) - set(additional_fields)
for col in sorted(current_only):
    keep = col in ['id', 'ss_hits', 'ss_transport_capacity', 'mount_1', 'mount_2', 'mount_3', 'dc_meta', 'ss_special', 'armor_modifier', 'armor_side_schurzen']
    marker = "KEEP (parsed from special_rules)" if keep else "DELETE (old field)"
    print(f"   {col:30s} - {marker}")

print("\n" + "=" * 100)
print("FIELD MAPPING ANALYSIS")
print("=" * 100)

# Check if weapons need to be split
cursor.execute("SELECT id, name, weapons FROM bg_reference_vehicles WHERE weapons IS NOT NULL LIMIT 10")
print("\n📋 WEAPONS FIELD (needs splitting to weapon_1, weapon_2, weapon_3):")
for row in cursor.fetchall():
    weapon_list = [w.strip() for w in row[2].split(',')] if row[2] else []
    print(f"   ID {row[0]:3d}: {row[1]:30s} | {len(weapon_list)} weapons | {row[2][:60]}")

# Check for vehicles with >3 weapons
cursor.execute("SELECT id, name, weapons FROM bg_reference_vehicles WHERE weapons IS NOT NULL")
max_weapons = 0
max_vehicle = None
for row in cursor.fetchall():
    weapon_list = [w.strip() for w in row[2].split(',')] if row[2] else []
    if len(weapon_list) > max_weapons:
        max_weapons = len(weapon_list)
        max_vehicle = (row[0], row[1], row[2])

if max_weapons > 3:
    print(f"\n⚠️  WARNING: Vehicle with {max_weapons} weapons found:")
    print(f"   ID {max_vehicle[0]}: {max_vehicle[1]}")
    print(f"   Weapons: {max_vehicle[2]}")
else:
    print(f"\n✅ Max weapons per vehicle: {max_weapons} (fits in 3 columns)")

# Check ammo field
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE ammo IS NOT NULL")
ammo_count = cursor.fetchone()[0]
if ammo_count > 0:
    print(f"\n📋 AMMO field: EXISTS with {ammo_count} vehicles")
    cursor.execute("SELECT id, name, ammo FROM bg_reference_vehicles WHERE ammo IS NOT NULL LIMIT 5")
    for row in cursor.fetchall():
        print(f"   ID {row[0]:3d}: {row[1]:30s} | ammo = {row[2]}")
else:
    print(f"\n❌ AMMO field: Does not exist or is empty")

# Check data types
print("\n" + "=" * 100)
print("DATA TYPE CHECK")
print("=" * 100)

cursor.execute("SELECT off_road_inches, road_inches FROM bg_reference_vehicles WHERE off_road_inches IS NOT NULL LIMIT 5")
print("\nCurrent movement values (should be INT, Excel wants TEXT with quotes):")
for row in cursor.fetchall():
    print(f"   off_road: {row[0]} (type: {type(row[0]).__name__}), road: {row[1]} (type: {type(row[1]).__name__})")

conn.close()

print("\n" + "=" * 100)
print("OUTSTANDING QUESTIONS")
print("=" * 100)
print("""
1. ✅ RESOLVED: special_rules → ss_special/dc_meta mapping (DONE!)

2. ✅ RESOLVED: mount_1/mount_2/mount_3 exist (parsed from special_rules)

3. ❓ WEAPON SPLITTING:
   - Split weapons field on comma to weapon_1, weapon_2, weapon_3?
   - What if vehicle has >3 weapons?

4. ❓ AMMO FIELD:
   - Exists in current schema?
   - Need to add it?

5. ❓ ID COLUMN:
   - Keep (for foreign keys) or delete?

6. ❓ DATA TYPES:
   - Keep movement as INTEGER or convert to TEXT ("9\\")?

7. ❓ FIELDS TO DELETE:
   - Confirm deletion of: source_page, extraction_confidence, notes,
     source_date, extraction_notes, master_id

8. ❓ NEW FIELDS:
   - year_range, vehicle_type, nation already exist ✅
   - Need to add: weapon_1, weapon_2, weapon_3, ammo (if missing)
""")
