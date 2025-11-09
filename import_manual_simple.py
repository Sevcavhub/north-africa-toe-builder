#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple import without backup"""

import sys
import io
import sqlite3
import pandas as pd

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

excel_path = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Vehicles Manual Entry Form.xlsx"
db_path = r"D:\north-africa-toe-builder\database\master_database.db"

# Read Excel
df = pd.read_excel(excel_path)
print(f"Records to import: {len(df)}")

# Connect
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get max ID
cursor.execute("SELECT MAX(id) FROM bg_reference_vehicles")
max_id = cursor.fetchone()[0] or 0

print(f"Starting ID: {max_id + 1}")

imported = 0

for idx, row in df.iterrows():
    new_id = max_id + idx + 1

    def cv(val):
        return None if pd.isna(val) else (val.strip() if isinstance(val, str) else val)

    cursor.execute("""
        INSERT INTO bg_reference_vehicles (
            id, name, off_road_inches, road_inches, special_movement,
            armor_front, armor_side, armor_rear,
            weapon_1, weapon_2, weapon_3, weapon_4,
            mount_1, mount_2, mount_3, mount_4,
            ammo_1, ammo_2, ammo_3, ammo_4,
            armor_modifier, armor_side_schurzen,
            ss_hits, ss_transport_capacity, ss_special,
            year_range, vehicle_type, nation, dc_meta,
            source_file, source_document, source_battle, extraction_method
        ) VALUES (?,?,?,?,?, ?,?,?, ?,?,?,?, ?,?,?,?, ?,?,?,?, ?,?, ?,?,?, ?,?,?,?, ?,?,?,?)
    """, (
        new_id, cv(row['name']), cv(row['off_road_inches']), cv(row['road_inches']), cv(row['special_movement']),
        cv(row['armor_front']), cv(row['armor_side']), cv(row['armor_rear']),
        cv(row['weapon_1']), cv(row['weapon_2']), cv(row['weapon_3']), cv(row['weapon_4']),
        cv(row['mount_1']), cv(row['mount_2']), cv(row['mount_3']), cv(row['mount_4']),
        cv(row['ammo_1']), cv(row['ammo_2']), cv(row['ammo_3']), cv(row['ammo_4']),
        cv(row['armor_modifier']), cv(row['armor_side_schurzen']),
        cv(row['ss_hits']), cv(row['ss_transport_capacity']), cv(row['ss_special']),
        cv(row['year_range']), cv(row['vehicle_type']), cv(row['nation']), cv(row['dc_meta']),
        'Vehicles Manual Entry Form.xlsx', 'BattleGroup Manual Entry',
        cv(row.get('source_battle', '')), cv(row.get('extraction_method', 'manual_excel_import'))
    ))

    imported += 1
    print(f"{imported}. ID {new_id}: {row['name']}")

conn.commit()
conn.close()

print(f"\n✅ Imported {imported} vehicles")
