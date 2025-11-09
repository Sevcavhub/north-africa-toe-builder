#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import Tobruk Excel vehicles, skipping duplicates"""

import sys
import io
import sqlite3
import pandas as pd
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

excel_path = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Vehicles Tobruk Input form for OCR.xlsx"
db_path = r"D:\north-africa-toe-builder\database\master_database.db"

print("=" * 100)
print("IMPORT TOBRUK VEHICLES (WITH DUPLICATE CHECKING)")
print("=" * 100)

# Read Excel file
df = pd.read_excel(excel_path)
print(f"\n📋 Reading Tobruk Excel: {len(df)} records")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Backup
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM bg_reference_vehicles")
conn.commit()
print(f"💾 Backup created: {backup_table}")

# Build lookup of existing vehicles (name + nation -> id)
cursor.execute("SELECT id, name, nation FROM bg_reference_vehicles")
existing = cursor.fetchall()

existing_lookup = {}
for vid, name, nation in existing:
    key = (name.lower().strip(), (nation or '').lower().strip())
    existing_lookup[key] = (vid, name, nation)

print(f"\n📋 Existing database: {len(existing)} records")

# Process each Excel record
stats = {
    'total': 0,
    'imported': 0,
    'skipped_exact_duplicate': 0,
    'skipped_different_nation': 0,
    'errors': 0
}

print("\n" + "=" * 100)
print("PROCESSING RECORDS")
print("=" * 100)

for idx, row in df.iterrows():
    stats['total'] += 1

    excel_name = str(row['name']).strip()
    excel_nation = str(row['nation']).strip()

    # Check for exact duplicate (same name + same nation)
    key = (excel_name.lower(), excel_nation.lower())

    if key in existing_lookup:
        db_id, db_name, db_nation = existing_lookup[key]
        print(f"⏭️  SKIP (exact duplicate): {excel_name} ({excel_nation}) - already in DB as ID {db_id}")
        stats['skipped_exact_duplicate'] += 1
        continue

    # Check for same name but different nation
    name_only_key = excel_name.lower()
    same_name_different_nation = any(
        k[0] == name_only_key and k[1] != excel_nation.lower()
        for k in existing_lookup.keys()
    )

    if same_name_different_nation:
        print(f"✅ IMPORT (different nation): {excel_name} ({excel_nation}) - name exists but different nation")

    # Import the record
    try:
        # Get next available ID
        cursor.execute("SELECT MAX(id) FROM bg_reference_vehicles")
        max_id = cursor.fetchone()[0]
        new_id = (max_id or 0) + 1

        # Prepare fields (handle NaN/None values)
        def clean_value(val):
            if pd.isna(val) or val is None:
                return None
            if isinstance(val, str):
                return val.strip() if val.strip() else None
            return val

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
            clean_value(row.get('off_road_inches')),
            clean_value(row.get('road_inches')),
            clean_value(row.get('special_movement')),
            clean_value(row.get('armor_front')),
            clean_value(row.get('armor_side')),
            clean_value(row.get('armor_rear')),
            clean_value(row.get('weapon_1')),
            clean_value(row.get('weapon_2')),
            clean_value(row.get('weapon_3')),
            None,  # weapon_4 (not in Excel)
            clean_value(row.get('mount_1')),
            clean_value(row.get('mount_2')),
            clean_value(row.get('mount_3')),
            None,  # mount_4 (not in Excel)
            clean_value(row.get('ammo')),  # ammo -> ammo_1
            None, None, None,  # ammo_2, ammo_3, ammo_4
            clean_value(row.get('armor_modifier')),
            clean_value(row.get('armor_side_schurzen')),
            clean_value(row.get('ss_hits')),
            clean_value(row.get('ss_transport_capacity')),
            clean_value(row.get('ss_special')),
            clean_value(row.get('year_range')),
            clean_value(row.get('vehicle_type')),
            clean_value(row['nation']),
            clean_value(row.get('dc_meta')),
            'Vehicles Tobruk Input form for OCR.xlsx',  # source_file
            'Battlegroup Tobruk',  # source_document
            'Tobruk',  # source_battle
            'manual_excel_import',  # extraction_method
            None  # screenshot_file
        ))

        stats['imported'] += 1

        if not same_name_different_nation:
            if stats['imported'] <= 15:
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
Skipped (exact duplicates):   {stats['skipped_exact_duplicate']}
Errors:                       {stats['errors']}

Backup: {backup_table}
""")

# Verify final counts
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
total_after = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation = 'German'")
german_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation = 'Italian'")
italian_count = cursor.fetchone()[0]

print("Database counts after import:")
print(f"  Total vehicles:     {total_after}")
print(f"  German vehicles:    {german_count}")
print(f"  Italian vehicles:   {italian_count}")

# Show sample of newly imported
print("\n" + "=" * 100)
print("SAMPLE OF NEWLY IMPORTED VEHICLES")
print("=" * 100)

cursor.execute("""
    SELECT id, name, nation, weapon_1, ammo_1
    FROM bg_reference_vehicles
    WHERE source_file = 'Vehicles Tobruk Input form for OCR.xlsx'
    ORDER BY nation, name
    LIMIT 20
""")

for row in cursor.fetchall():
    ammo_str = row[4] or ''
    print(f"ID {row[0]:3d}: {row[1][:40]:40s} | {row[2][:10]:10s} | W1: {row[3] or 'None':20s} | Ammo: {ammo_str}")

conn.close()

print("\n" + "=" * 100)
print("✅ IMPORT COMPLETE")
print("=" * 100)
