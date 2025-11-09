#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import vehicles from Manual Entry Form Excel"""

import sys
import io
import sqlite3
import pandas as pd
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

excel_path = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Vehicles Manual Entry Form.xlsx"
db_path = r"D:\north-africa-toe-builder\database\master_database.db"

print("=" * 100)
print("IMPORT MANUAL ENTRY FORM VEHICLES")
print("=" * 100)

# Read Excel file
df = pd.read_excel(excel_path)
print(f"\n📋 Reading Manual Entry Form: {len(df)} records")

# Connect to database with timeout
import time

max_retries = 5
for attempt in range(max_retries):
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        break
    except sqlite3.OperationalError as e:
        if attempt < max_retries - 1:
            print(f"Database locked, retrying... (attempt {attempt + 1}/{max_retries})")
            time.sleep(2)
        else:
            raise

# Backup (use transaction-safe method)
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
try:
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {backup_table} AS SELECT * FROM bg_reference_vehicles WHERE 1=0")
    cursor.execute(f"INSERT INTO {backup_table} SELECT * FROM bg_reference_vehicles")
    conn.commit()
    print(f"💾 Backup created: {backup_table}")
except Exception as e:
    print(f"⚠️  Warning: Could not create backup table: {e}")
    print(f"⚠️  Proceeding without backup...")

# Build lookup of existing vehicles
cursor.execute("SELECT id, name, nation FROM bg_reference_vehicles")
existing = cursor.fetchall()

existing_lookup = {}
for row in existing:
    key = (row['name'].lower().strip(), (row['nation'] or '').lower().strip())
    existing_lookup[key] = row['id']

print(f"\n📋 Existing database: {len(existing)} records")

# Process each Excel record
stats = {
    'total': 0,
    'imported': 0,
    'skipped_duplicate': 0,
    'errors': 0
}

print("\n" + "=" * 100)
print("PROCESSING RECORDS")
print("=" * 100)

for idx, row in df.iterrows():
    stats['total'] += 1

    excel_name = str(row['name']).strip()
    excel_nation = str(row['nation']).strip() if pd.notna(row['nation']) else ''

    # Check for duplicate
    key = (excel_name.lower(), excel_nation.lower())
    if key in existing_lookup:
        db_id = existing_lookup[key]
        print(f"⏭️  SKIP (duplicate): {excel_name} ({excel_nation}) - already ID {db_id}")
        stats['skipped_duplicate'] += 1
        continue

    # Get next available ID
    cursor.execute("SELECT MAX(id) FROM bg_reference_vehicles")
    max_id = cursor.fetchone()[0]
    new_id = (max_id or 0) + 1

    # Helper function to clean values
    def clean_value(val):
        if pd.isna(val) or val is None:
            return None
        if isinstance(val, str):
            return val.strip() if val.strip() else None
        return val

    try:
        # Insert record
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
                source_file, source_document, source_battle,
                extraction_method, screenshot_file
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?
            )
        """, (
            new_id,
            clean_value(row['name']),
            clean_value(row['off_road_inches']),
            clean_value(row['road_inches']),
            clean_value(row['special_movement']),
            clean_value(row['armor_front']),
            clean_value(row['armor_side']),
            clean_value(row['armor_rear']),
            clean_value(row['weapon_1']),
            clean_value(row['weapon_2']),
            clean_value(row['weapon_3']),
            clean_value(row['weapon_4']),
            clean_value(row['mount_1']),
            clean_value(row['mount_2']),
            clean_value(row['mount_3']),
            clean_value(row['mount_4']),
            clean_value(row['ammo_1']),
            clean_value(row['ammo_2']),
            clean_value(row['ammo_3']),
            clean_value(row['ammo_4']),
            clean_value(row['armor_modifier']),
            clean_value(row['armor_side_schurzen']),
            clean_value(row['ss_hits']),
            clean_value(row['ss_transport_capacity']),
            clean_value(row['ss_special']),
            clean_value(row['year_range']),
            clean_value(row['vehicle_type']),
            clean_value(row['nation']),
            clean_value(row['dc_meta']),
            'Vehicles Manual Entry Form.xlsx',  # source_file
            'BattleGroup Manual Entry',  # source_document
            clean_value(row.get('source_battle', '')),  # source_battle from Excel if exists
            clean_value(row.get('extraction_method', 'manual_excel_import')),  # extraction_method
            None  # screenshot_file
        ))

        stats['imported'] += 1
        print(f"✅ IMPORT: ID {new_id:3d} - {excel_name} ({excel_nation})")

    except Exception as e:
        print(f"❌ ERROR: {excel_name} - {e}")
        stats['errors'] += 1

conn.commit()

print("\n" + "=" * 100)
print("IMPORT SUMMARY")
print("=" * 100)
print(f"""
Total records in Excel:       {stats['total']}
Successfully imported:        {stats['imported']}
Skipped (duplicates):         {stats['skipped_duplicate']}
Errors:                       {stats['errors']}

Backup: {backup_table}
""")

# Verify final counts
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
total_after = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation = 'british'")
british_count = cursor.fetchone()[0]

print("Database counts after import:")
print(f"  Total vehicles:     {total_after}")
print(f"  British vehicles:   {british_count}")

# Show newly imported
print("\n" + "=" * 100)
print("NEWLY IMPORTED VEHICLES")
print("=" * 100)

cursor.execute("""
    SELECT id, name, nation, weapon_1, ammo_1, vehicle_type
    FROM bg_reference_vehicles
    WHERE source_file = 'Vehicles Manual Entry Form.xlsx'
    ORDER BY id
""")

for row in cursor.fetchall():
    ammo_str = row['ammo_1'] or ''
    vtype = row['vehicle_type'] or ''
    print(f"ID {row['id']:3d}: {row['name'][:35]:35s} | {row['nation']:10s} | W1: {row['weapon_1'] or 'None':15s} | Ammo: {ammo_str:5s} | Type: {vtype}")

conn.close()

print("\n" + "=" * 100)
print("✅ IMPORT COMPLETE")
print("=" * 100)
