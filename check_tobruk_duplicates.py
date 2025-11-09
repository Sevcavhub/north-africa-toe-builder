#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check for duplicates between Tobruk Excel and existing database"""

import sys
import io
import sqlite3
import pandas as pd

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

excel_path = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Vehicles Tobruk Input form for OCR.xlsx"
db_path = r"D:\north-africa-toe-builder\database\master_database.db"

print("=" * 100)
print("CHECK FOR DUPLICATES: Tobruk Excel vs Existing Database")
print("=" * 100)

# Read Excel file
df = pd.read_excel(excel_path)
print(f"\n📋 Tobruk Excel: {len(df)} records")
print(f"   German: {len(df[df['nation'] == 'German'])}")
print(f"   Italian: {len(df[df['nation'] == 'Italian'])}")

# Read existing database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, name, nation FROM bg_reference_vehicles ORDER BY name")
existing = cursor.fetchall()
print(f"\n📋 Existing database: {len(existing)} records")

# Build lookup of existing vehicles (name -> (id, nation))
existing_lookup = {}
for vid, name, nation in existing:
    key = name.lower().strip()
    existing_lookup[key] = (vid, name, nation)

# Check for duplicates
duplicates = []
new_records = []

for idx, row in df.iterrows():
    excel_name = str(row['name']).strip()
    excel_nation = str(row['nation']).strip()
    key = excel_name.lower()

    if key in existing_lookup:
        db_id, db_name, db_nation = existing_lookup[key]
        duplicates.append({
            'excel_name': excel_name,
            'excel_nation': excel_nation,
            'db_id': db_id,
            'db_name': db_name,
            'db_nation': db_nation
        })
    else:
        new_records.append({
            'name': excel_name,
            'nation': excel_nation
        })

print("\n" + "=" * 100)
print("DUPLICATE ANALYSIS")
print("=" * 100)

if duplicates:
    print(f"\n⚠️  Found {len(duplicates)} potential duplicates:\n")
    print(f"{'Excel Name':<35s} {'Excel Nation':<12s} | {'DB ID':<6s} {'DB Name':<35s} {'DB Nation':<12s}")
    print("-" * 100)
    for dup in duplicates:
        print(f"{dup['excel_name']:<35s} {dup['excel_nation']:<12s} | {dup['db_id']:<6d} {dup['db_name']:<35s} {dup['db_nation'] or 'None':<12s}")
else:
    print("\n✅ No duplicates found")

print("\n" + "=" * 100)
print("NEW RECORDS TO IMPORT")
print("=" * 100)

if new_records:
    print(f"\n✅ {len(new_records)} new records ready to import:\n")

    # Group by nation
    german_new = [r for r in new_records if r['nation'] == 'German']
    italian_new = [r for r in new_records if r['nation'] == 'Italian']

    if german_new:
        print(f"\nGerman ({len(german_new)}):")
        for r in german_new[:10]:
            print(f"  - {r['name']}")
        if len(german_new) > 10:
            print(f"  ... and {len(german_new) - 10} more")

    if italian_new:
        print(f"\nItalian ({len(italian_new)}):")
        for r in italian_new[:10]:
            print(f"  - {r['name']}")
        if len(italian_new) > 10:
            print(f"  ... and {len(italian_new) - 10} more")
else:
    print("\n⚠️  All records already exist in database")

conn.close()

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"""
Total records in Excel:     {len(df)}
Duplicates found:           {len(duplicates)}
New records to import:      {len(new_records)}

Recommendation:
- Review duplicates above (if any)
- Proceed with import if counts look correct
""")
print("=" * 100)
