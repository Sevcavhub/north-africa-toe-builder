#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse mount data from weapon fields (e.g., 'MG (Pintle)' -> weapon='MG', mount='Pintle')"""

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
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 100)
print("PARSE MOUNTS FROM WEAPON FIELDS")
print("=" * 100)

# Backup
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM bg_reference_vehicles")
conn.commit()
print(f"\n💾 Backup created: {backup_table}")

# Find all records with mount data in weapon fields
cursor.execute("""
    SELECT id, name, weapon_1, weapon_2, weapon_3, weapon_4,
           mount_1, mount_2, mount_3, mount_4
    FROM bg_reference_vehicles
    WHERE weapon_1 LIKE '%(%' OR weapon_2 LIKE '%(%' OR weapon_3 LIKE '%(%' OR weapon_4 LIKE '%(%'
""")

records_to_fix = cursor.fetchall()
print(f"\n📊 Found {len(records_to_fix)} records with mount data in weapon fields")

stats = {
    'records_fixed': 0,
    'weapons_parsed': 0
}

print("\n🔧 Parsing and fixing...")
print("=" * 100)

for row in records_to_fix:
    vehicle_id = row['id']
    vehicle_name = row['name']
    changes = []

    # Check each weapon field
    for i in range(1, 5):
        weapon = row[f'weapon_{i}']
        current_mount = row[f'mount_{i}']

        if weapon and '(' in weapon:
            # Extract mount from parentheses
            match = re.search(r'(.+?)\s*\((.+?)\)', weapon)
            if match:
                weapon_cleaned = match.group(1).strip()
                mount_extracted = match.group(2).strip()

                # Update weapon (remove parentheses and mount)
                cursor.execute(f"""
                    UPDATE bg_reference_vehicles
                    SET weapon_{i} = ?
                    WHERE id = ?
                """, (weapon_cleaned, vehicle_id))

                # Update mount (overwrite if exists)
                cursor.execute(f"""
                    UPDATE bg_reference_vehicles
                    SET mount_{i} = ?
                    WHERE id = ?
                """, (mount_extracted, vehicle_id))

                changes.append(f"  W{i}: '{weapon}' → weapon='{weapon_cleaned}', mount='{mount_extracted}'")
                stats['weapons_parsed'] += 1

    if changes:
        print(f"\nID {vehicle_id:3d}: {vehicle_name[:40]:40s}")
        for change in changes:
            print(change)
        stats['records_fixed'] += 1

conn.commit()

print("\n" + "=" * 100)
print("VERIFICATION")
print("=" * 100)

# Verify no more parentheses in weapon fields
cursor.execute("""
    SELECT COUNT(*)
    FROM bg_reference_vehicles
    WHERE weapon_1 LIKE '%(%' OR weapon_2 LIKE '%(%' OR weapon_3 LIKE '%(%' OR weapon_4 LIKE '%(%'
""")
remaining = cursor.fetchone()[0]

print(f"\n✅ Records with mount data in weapons (before): {len(records_to_fix)}")
print(f"✅ Records with mount data in weapons (after):  {remaining}")
print(f"✅ Total records fixed: {stats['records_fixed']}")
print(f"✅ Total weapons parsed: {stats['weapons_parsed']}")

# Show sample of corrected data
print("\n📋 Sample of corrected records:")
print("=" * 100)
cursor.execute("""
    SELECT id, name, weapon_1, weapon_2, mount_1, mount_2
    FROM bg_reference_vehicles
    WHERE id IN (24, 25, 38, 40, 80, 85)
""")

for row in cursor.fetchall():
    print(f"\nID {row['id']:3d}: {row['name'][:40]:40s}")
    if row['weapon_1']:
        print(f"  W1: {row['weapon_1']:30s} | M1: {row['mount_1'] or 'None'}")
    if row['weapon_2']:
        print(f"  W2: {row['weapon_2']:30s} | M2: {row['mount_2'] or 'None'}")

conn.close()

print("\n" + "=" * 100)
print("✅ MOUNT PARSING COMPLETE")
print("=" * 100)
print(f"\nBackup: {backup_table}")
print("=" * 100)
