#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check earliest backup for ammo data in special_rules field"""

import sys
import io
import sqlite3
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

backup_table = 'bg_reference_vehicles_backup_20251107_222712'

print("=" * 100)
print(f"CHECKING {backup_table} FOR AMMO DATA")
print("=" * 100)

# Search for 'ammo' keyword in special_rules
cursor.execute(f"""
    SELECT id, name, special_rules
    FROM {backup_table}
    WHERE special_rules LIKE '%ammo%'
""")

ammo_in_special = cursor.fetchall()
print(f"\nRecords with 'ammo' in special_rules: {len(ammo_in_special)}")
print("=" * 100)
for row in ammo_in_special:
    print(f"ID {row['id']:3d}: {row['name'][:35]:35s} | {row['special_rules']}")

# Search for number patterns that might indicate ammo counts
# Pattern: standalone numbers (not part of armor values or calibers)
print(f"\n\nSearching for potential ammo patterns (numbers not already parsed)...")
print("=" * 100)

cursor.execute(f"""
    SELECT id, name, special_rules
    FROM {backup_table}
    WHERE special_rules IS NOT NULL
      AND special_rules != ''
      AND (special_rules LIKE '% 12 %'
           OR special_rules LIKE '% 20 %'
           OR special_rules LIKE '% 30 %'
           OR special_rules LIKE '% 40 %'
           OR special_rules LIKE '% 50 %'
           OR special_rules LIKE '%ammo%')
""")

potential_ammo = cursor.fetchall()
print(f"\nRecords with potential ammo numbers: {len(potential_ammo)}")
for row in potential_ammo:
    print(f"\nID {row['id']:3d}: {row['name'][:35]:35s}")
    print(f"  special_rules: {row['special_rules']}")

# Now check current table to see what we have
print("\n\n" + "=" * 100)
print("CURRENT TABLE - AMMO STATUS")
print("=" * 100)

cursor.execute("""
    SELECT id, name, ammo, dc_meta
    FROM bg_reference_vehicles
    WHERE ammo IS NOT NULL AND ammo != ''
""")

current_ammo = cursor.fetchall()
print(f"\nRecords with ammo in current table: {len(current_ammo)}")
for row in current_ammo:
    print(f"ID {row['id']:3d}: {row['name'][:35]:35s} | ammo={row['ammo']} | dc_meta={row['dc_meta']}")

# Check dc_meta field for any ammo references
cursor.execute("""
    SELECT id, name, dc_meta
    FROM bg_reference_vehicles
    WHERE dc_meta LIKE '%ammo%'
""")

ammo_in_dc_meta = cursor.fetchall()
print(f"\n\nRecords with 'ammo' in dc_meta: {len(ammo_in_dc_meta)}")
for row in ammo_in_dc_meta:
    print(f"ID {row['id']:3d}: {row['name'][:35]:35s} | {row['dc_meta']}")

conn.close()

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"""
Ammo data in earliest backup (special_rules): {len(ammo_in_special)} records
Ammo data in current table (ammo field):      {len(current_ammo)} records
Ammo references in dc_meta:                   {len(ammo_in_dc_meta)} records

CONCLUSION:
- If backup shows more ammo data than current, we may have lost data during parsing
- If backup shows same amount, no data loss occurred
""")
print("=" * 100)
