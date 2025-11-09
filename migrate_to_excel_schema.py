#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migrate bg_reference_vehicles to Excel template schema with correct field order"""

import sys
import io
import sqlite3
import re
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("SCHEMA MIGRATION: bg_reference_vehicles → Excel Template")
print("=" * 100)

# Step 1: Backup
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"\n💾 STEP 1: Creating backup...")
cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM bg_reference_vehicles")
conn.commit()

cursor.execute(f"SELECT COUNT(*) FROM {backup_table}")
backup_count = cursor.fetchone()[0]
print(f"   ✅ Backup created: {backup_table} ({backup_count} records)")

# Step 2: Create new schema with correct field order
print(f"\n🔧 STEP 2: Creating new schema with correct field order...")

# Field order: Excel template fields first, then additional fields, then id
new_schema_sql = """
CREATE TABLE bg_reference_vehicles_new (
    -- Excel Template Fields (in order from left to right)
    name TEXT,
    off_road_inches INTEGER,
    road_inches INTEGER,
    special_movement TEXT,
    armor_front TEXT,
    armor_side TEXT,
    armor_rear TEXT,
    weapon_1 TEXT,
    weapon_2 TEXT,
    weapon_3 TEXT,
    weapon_4 TEXT,
    mount_1 TEXT,
    mount_2 TEXT,
    mount_3 TEXT,
    mount_4 TEXT,
    ammo TEXT,
    armor_modifier TEXT,
    armor_side_schurzen TEXT,
    ss_hits INTEGER,
    ss_transport_capacity INTEGER,
    ss_special TEXT,
    year_range TEXT,
    vehicle_type TEXT,
    nation TEXT,
    dc_meta TEXT,

    -- Additional fields (end of row)
    source_file TEXT,
    source_document TEXT,
    source_battle TEXT,
    extraction_method TEXT,
    screenshot_file TEXT,

    -- ID at the very end
    id INTEGER PRIMARY KEY
)
"""

cursor.execute(new_schema_sql)
print(f"   ✅ New schema created with 31 columns")

# Step 3: Migrate data with transformations
print(f"\n📊 STEP 3: Migrating data with transformations...")

cursor.execute("SELECT * FROM bg_reference_vehicles")
old_data = cursor.fetchall()

# Get column names from old schema
cursor.execute("PRAGMA table_info(bg_reference_vehicles)")
old_columns = {col[1]: idx for idx, col in enumerate([(c[0], c[1]) for c in cursor.fetchall()])}

stats = {
    'total': len(old_data),
    'weapons_split': 0,
    'ammo_parsed': 0,
    'mount_4_added': 0
}

for row in old_data:
    # Extract old data
    vehicle_id = row[old_columns['id']]
    name = row[old_columns['name']]
    off_road = row[old_columns['off_road_inches']]
    road = row[old_columns['road_inches']]
    special_movement = row[old_columns['special_movement']]
    armor_front = row[old_columns['armor_front']]
    armor_side = row[old_columns['armor_side']]
    armor_rear = row[old_columns['armor_rear']]
    weapons = row[old_columns['weapons']]
    armor_modifier = row[old_columns['armor_modifier']]
    armor_side_schurzen = row[old_columns['armor_side_schurzen']]
    ss_hits = row[old_columns['ss_hits']]
    ss_transport_capacity = row[old_columns['ss_transport_capacity']]
    ss_special = row[old_columns['ss_special']]
    year_range = row[old_columns['year_range']]
    vehicle_type = row[old_columns['vehicle_type']]
    nation = row[old_columns['nation']]
    dc_meta = row[old_columns['dc_meta']]
    mount_1 = row[old_columns['mount_1']]
    mount_2 = row[old_columns['mount_2']]
    mount_3 = row[old_columns['mount_3']]
    source_file = row[old_columns['source_file']]
    source_document = row[old_columns['source_document']]
    source_battle = row[old_columns['source_battle']]
    extraction_method = row[old_columns['extraction_method']]
    screenshot_file = row[old_columns['screenshot_file']]

    # Split weapons into weapon_1, weapon_2, weapon_3, weapon_4
    weapon_1 = weapon_2 = weapon_3 = weapon_4 = None
    if weapons:
        weapon_list = [w.strip() for w in weapons.split(',')]
        if len(weapon_list) >= 1:
            weapon_1 = weapon_list[0]
        if len(weapon_list) >= 2:
            weapon_2 = weapon_list[1]
        if len(weapon_list) >= 3:
            weapon_3 = weapon_list[2]
        if len(weapon_list) >= 4:
            weapon_4 = weapon_list[3]
            stats['weapons_split'] += 1

    # Parse ammo from dc_meta (look for "X ammo" pattern)
    ammo = None
    if dc_meta:
        ammo_match = re.search(r'(\d+)\s*ammo', dc_meta, re.IGNORECASE)
        if ammo_match:
            ammo = ammo_match.group(1)
            # Remove the ammo from dc_meta
            dc_meta = re.sub(r'\d+\s*ammo,?\s*', '', dc_meta, flags=re.IGNORECASE).strip()
            dc_meta = re.sub(r'^,\s*|,\s*$', '', dc_meta)  # Clean commas
            stats['ammo_parsed'] += 1

    # Add mount_4 if we have weapon_4
    mount_4 = None
    if weapon_4:
        stats['mount_4_added'] += 1

    # Insert into new table
    cursor.execute("""
        INSERT INTO bg_reference_vehicles_new (
            name, off_road_inches, road_inches, special_movement,
            armor_front, armor_side, armor_rear,
            weapon_1, weapon_2, weapon_3, weapon_4,
            mount_1, mount_2, mount_3, mount_4,
            ammo, armor_modifier, armor_side_schurzen,
            ss_hits, ss_transport_capacity, ss_special,
            year_range, vehicle_type, nation, dc_meta,
            source_file, source_document, source_battle,
            extraction_method, screenshot_file, id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, off_road, road, special_movement,
        armor_front, armor_side, armor_rear,
        weapon_1, weapon_2, weapon_3, weapon_4,
        mount_1, mount_2, mount_3, mount_4,
        ammo, armor_modifier, armor_side_schurzen,
        ss_hits, ss_transport_capacity, ss_special,
        year_range, vehicle_type, nation, dc_meta,
        source_file, source_document, source_battle,
        extraction_method, screenshot_file, vehicle_id
    ))

conn.commit()

print(f"   ✅ Migrated {stats['total']} vehicles")
print(f"   ✅ Weapons split: {stats['weapons_split']} vehicles with 4 weapons")
print(f"   ✅ Ammo parsed: {stats['ammo_parsed']} vehicles")
print(f"   ✅ mount_4 added: {stats['mount_4_added']} vehicles")

# Step 4: Replace old table
print(f"\n🔄 STEP 4: Replacing old table...")
cursor.execute("DROP TABLE bg_reference_vehicles")
cursor.execute("ALTER TABLE bg_reference_vehicles_new RENAME TO bg_reference_vehicles")
conn.commit()
print(f"   ✅ Table replaced")

# Step 5: Verify
print(f"\n✅ STEP 5: Verification...")

cursor.execute("PRAGMA table_info(bg_reference_vehicles)")
new_columns = cursor.fetchall()

print(f"\n   New schema has {len(new_columns)} columns:")
print(f"\n   Column order (left to right):")
for i, col in enumerate(new_columns, 1):
    print(f"      {i:2d}. {col[1]:30s} {col[2]}")

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
final_count = cursor.fetchone()[0]
print(f"\n   Total records: {final_count}")

# Show sample with new fields
cursor.execute("""
    SELECT id, name, weapon_1, weapon_2, weapon_3, weapon_4, mount_1, mount_2, mount_3, mount_4, ammo
    FROM bg_reference_vehicles
    WHERE weapon_4 IS NOT NULL OR ammo IS NOT NULL
    LIMIT 10
""")

print(f"\n   Sample vehicles with 4 weapons or ammo:")
print("   ID  | Name                           | W1      | W2      | W3  | W4  | M1   | M2   | M3 | M4 | Ammo")
print("   " + "-" * 100)
for row in cursor.fetchall():
    print(f"   {row[0]:3d} | {str(row[1])[:30]:30s} | {str(row[2] or '')[:7]:7s} | {str(row[3] or '')[:7]:7s} | {str(row[4] or '')[:3]:3s} | {str(row[5] or '')[:3]:3s} | {str(row[6] or '')[:4]:4s} | {str(row[7] or '')[:4]:4s} | {str(row[8] or '')[:2]:2s} | {str(row[9] or '')[:2]:2s} | {str(row[10] or '')}")

conn.close()

print("\n" + "=" * 100)
print("✅ MIGRATION COMPLETE")
print("=" * 100)
print(f"\nBackup table: {backup_table}")
print(f"\nDeleted fields:")
print(f"   - weapons (split to weapon_1/2/3/4)")
print(f"   - source_page")
print(f"   - extraction_confidence")
print(f"   - notes")
print(f"   - source_date")
print(f"   - extraction_notes")
print(f"   - master_id")
print(f"\nAdded fields:")
print(f"   - weapon_1, weapon_2, weapon_3, weapon_4")
print(f"   - mount_4")
print(f"   - ammo")
print("\n" + "=" * 100)
