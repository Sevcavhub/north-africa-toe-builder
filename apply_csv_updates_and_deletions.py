#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply updates from CSV:
1. Delete records 5, 30, 31
2. Expand ammo to ammo_1, ammo_2, ammo_3, ammo_4
3. Import corrected weapon_1 names and ammo values
"""

import sys
import io
import sqlite3
import csv
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
input_csv = r"D:\north-africa-toe-builder\vehicles_ammo_entry.csv"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 100)
print("APPLY CSV UPDATES AND DELETIONS")
print("=" * 100)

# Backup
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM bg_reference_vehicles")
conn.commit()
print(f"\n💾 Backup created: {backup_table}")

# Step 1: Delete records 5, 30, 31
print(f"\n🗑️  Step 1: Deleting records 5, 30, 31...")

records_to_delete = [5, 30, 31]
for record_id in records_to_delete:
    cursor.execute("SELECT name FROM bg_reference_vehicles WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    if row:
        print(f"   Deleting ID {record_id:3d}: {row['name']}")
        cursor.execute("DELETE FROM bg_reference_vehicles WHERE id = ?", (record_id,))
    else:
        print(f"   ⚠️  ID {record_id} not found")

conn.commit()
print(f"   ✅ Deleted {len(records_to_delete)} records")

# Step 2: Expand ammo to ammo_1, ammo_2, ammo_3, ammo_4
print(f"\n🔧 Step 2: Expanding ammo field to ammo_1, ammo_2, ammo_3, ammo_4...")

# Get current schema
cursor.execute("PRAGMA table_info(bg_reference_vehicles)")
columns = cursor.fetchall()

# Create new schema with ammo_1, ammo_2, ammo_3, ammo_4
print(f"   Creating new schema...")

cursor.execute("""
CREATE TABLE bg_reference_vehicles_new (
    -- ID first (far left column)
    id INTEGER PRIMARY KEY,

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
    ammo_1 TEXT,
    ammo_2 TEXT,
    ammo_3 TEXT,
    ammo_4 TEXT,
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
    screenshot_file TEXT
)
""")

# Copy data (migrate ammo to ammo_1)
cursor.execute("""
INSERT INTO bg_reference_vehicles_new
SELECT id, name, off_road_inches, road_inches, special_movement,
       armor_front, armor_side, armor_rear,
       weapon_1, weapon_2, weapon_3, weapon_4,
       mount_1, mount_2, mount_3, mount_4,
       ammo, NULL, NULL, NULL,  -- ammo -> ammo_1, rest NULL
       armor_modifier, armor_side_schurzen,
       ss_hits, ss_transport_capacity, ss_special,
       year_range, vehicle_type, nation, dc_meta,
       source_file, source_document, source_battle,
       extraction_method, screenshot_file
FROM bg_reference_vehicles
""")

cursor.execute("DROP TABLE bg_reference_vehicles")
cursor.execute("ALTER TABLE bg_reference_vehicles_new RENAME TO bg_reference_vehicles")
conn.commit()

print(f"   ✅ Ammo field expanded to ammo_1, ammo_2, ammo_3, ammo_4")

# Step 3: Import CSV updates (weapon_1 and ammo values)
print(f"\n📥 Step 3: Importing CSV updates...")

stats = {
    'total': 0,
    'updated_weapon': 0,
    'updated_ammo': 0,
    'skipped': 0,
    'errors': 0
}

with open(input_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for row in reader:
        stats['total'] += 1
        vehicle_id = int(row['id'])

        # Skip deleted records
        if vehicle_id in records_to_delete:
            stats['skipped'] += 1
            continue

        weapon_1_value = row['weapon_1'].strip() if row['weapon_1'] else None
        ammo_value = row['ammo'].strip() if row['ammo'] else None

        # Check if record exists
        cursor.execute("SELECT id FROM bg_reference_vehicles WHERE id = ?", (vehicle_id,))
        if not cursor.fetchone():
            stats['skipped'] += 1
            continue

        try:
            # Update weapon_1 (user corrected German gun names)
            if weapon_1_value:
                cursor.execute("""
                    UPDATE bg_reference_vehicles
                    SET weapon_1 = ?
                    WHERE id = ?
                """, (weapon_1_value, vehicle_id))
                stats['updated_weapon'] += 1

            # Update ammo_1 (default for weapon_1)
            if ammo_value:
                cursor.execute("""
                    UPDATE bg_reference_vehicles
                    SET ammo_1 = ?
                    WHERE id = ?
                """, (ammo_value, vehicle_id))
                stats['updated_ammo'] += 1

        except Exception as e:
            print(f"  ⚠️  Error updating ID {vehicle_id}: {e}")
            stats['errors'] += 1

# Special case: Churchill Crocodile - ammo_3 = 4 for flamethrower
print(f"\n🔥 Step 4: Handling Churchill Crocodile special case...")
cursor.execute("""
    UPDATE bg_reference_vehicles
    SET ammo_3 = '4'
    WHERE name = 'Churchill Crocodile'
""")
print(f"   ✅ Set ammo_3=4 for Churchill Crocodile (flamethrower)")

conn.commit()

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"""
Records deleted:          3 (IDs: 5, 30, 31)
Ammo schema expanded:     ammo → ammo_1, ammo_2, ammo_3, ammo_4

CSV Import:
  Total records in CSV:     {stats['total']}
  Weapon_1 updated:         {stats['updated_weapon']}
  Ammo_1 updated:           {stats['updated_ammo']}
  Records skipped:          {stats['skipped']}
  Errors:                   {stats['errors']}

Special cases handled:
  Churchill Crocodile:      ammo_3 = 4 (flamethrower)

Backup: {backup_table}
""")

# Verify
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
total_records = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*)
    FROM bg_reference_vehicles
    WHERE ammo_1 IS NOT NULL AND ammo_1 != ''
""")
total_with_ammo = cursor.fetchone()[0]

print(f"✅ Total vehicles in database: {total_records}")
print(f"✅ Total vehicles with ammo_1: {total_with_ammo}")

# Show sample of German vehicles (weapon_1 corrections)
print(f"\n📋 Sample German vehicles (corrected weapon_1):")
print("=" * 100)
cursor.execute("""
    SELECT id, name, weapon_1, ammo_1
    FROM bg_reference_vehicles
    WHERE nation = 'German'
      AND weapon_1 IS NOT NULL
      AND weapon_1 != 'MG'
    ORDER BY id
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"ID {row['id']:3d}: {row['name'][:35]:35s} | Weapon: {row['weapon_1'][:25]:25s} | Ammo: {row['ammo_1'] or ''}")

# Show Crocodile
print(f"\n📋 Churchill Crocodile (multi-weapon ammo):")
print("=" * 100)
cursor.execute("""
    SELECT id, name, weapon_1, weapon_2, weapon_3, ammo_1, ammo_2, ammo_3
    FROM bg_reference_vehicles
    WHERE name = 'Churchill Crocodile'
""")
row = cursor.fetchone()
if row:
    print(f"ID {row['id']:3d}: {row['name']}")
    print(f"  Weapon_1: {row['weapon_1']:20s} | Ammo_1: {row['ammo_1'] or 'None'}")
    print(f"  Weapon_2: {row['weapon_2']:20s} | Ammo_2: {row['ammo_2'] or 'None'}")
    print(f"  Weapon_3: {row['weapon_3']:20s} | Ammo_3: {row['ammo_3'] or 'None'}")

conn.close()

print("\n" + "=" * 100)
print("✅ ALL UPDATES COMPLETE")
print("=" * 100)
