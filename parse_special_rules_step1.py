#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse special_rules field - Step 1: Setup and initial parsing"""

import sys
import io
import sqlite3
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("SPECIAL_RULES PARSING - STEP 1: SETUP")
print("=" * 100)

# Step 1: Add temp field and copy data
print("\n📋 Step 1: Creating temp field...")

try:
    cursor.execute("ALTER TABLE bg_reference_vehicles ADD COLUMN special_rules_temp TEXT")
    print("   ✅ Added special_rules_temp column")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("   ⚠️  special_rules_temp already exists")
    else:
        raise

cursor.execute("UPDATE bg_reference_vehicles SET special_rules_temp = special_rules")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE special_rules IS NOT NULL")
count_with_rules = cursor.fetchone()[0]
print(f"   ✅ Copied {count_with_rules} special_rules values to temp field")

# Step 2: Add new fields if needed
print("\n📋 Step 2: Adding new fields...")

new_fields = [
    ("ss_hits", "INTEGER"),
    ("ss_transport_capacity", "INTEGER"),
    ("mount_1", "TEXT"),
    ("mount_2", "TEXT"),
    ("mount_3", "TEXT")
]

for field_name, field_type in new_fields:
    try:
        cursor.execute(f"ALTER TABLE bg_reference_vehicles ADD COLUMN {field_name} {field_type}")
        print(f"   ✅ Added {field_name} column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print(f"   ⚠️  {field_name} already exists")
        else:
            raise

conn.commit()

# Step 3: Show sample of what we're working with
print("\n" + "=" * 100)
print("SAMPLE DATA (vehicles with special_rules)")
print("=" * 100)

cursor.execute("""
    SELECT id, name, special_rules_temp
    FROM bg_reference_vehicles
    WHERE special_rules_temp IS NOT NULL
    ORDER BY id
    LIMIT 20
""")

print("\nID  | Name                           | special_rules_temp")
print("-" * 100)
for row in cursor.fetchall():
    print(f"{row[0]:3d} | {str(row[1])[:30]:30s} | {str(row[2])[:60]}")

print("\n" + "=" * 100)
print(f"Total vehicles with special_rules: {count_with_rules}")
print("=" * 100)

conn.close()

print("\n✅ Setup complete. Ready for parsing.")
