#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse special_rules field - Step 3: Separate special rules from descriptive metadata"""

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
print("SPECIAL_RULES PARSING - STEP 3: RULES vs METADATA")
print("=" * 100)

# Add dc_meta and ss_special fields if needed
try:
    cursor.execute("ALTER TABLE bg_reference_vehicles ADD COLUMN dc_meta TEXT")
    print("✅ Added dc_meta column")
except sqlite3.OperationalError:
    print("⚠️  dc_meta already exists")

try:
    cursor.execute("ALTER TABLE bg_reference_vehicles ADD COLUMN ss_special TEXT")
    print("✅ Added ss_special column")
except sqlite3.OperationalError:
    print("⚠️  ss_special already exists")

conn.commit()

# Define special rules keywords (game mechanics)
special_rules_keywords = [
    'Recce',
    'Reserve',
    'Medical',
    'no BR counter',
    'Radio',
    'CP Type',  # Command Post
    'vehicle recovery',
    'repair recovery',
    'amphibious',
    'Engineer',
    'Scout',
    'liason',
]

# Define descriptive text patterns (metadata/notes)
descriptive_patterns = [
    r'.*Tank.*',  # "Heavy infantry tank", "Light Tank", etc.
    r'.*cruiser.*',  # "Fast, cruiser Tank"
    r'.*conversion.*',  # "Specialist swimming conversion"
    r'.*armoured car.*',  # "US supplied armoured car"
    r'.*Version.*',  # "British Version of Stuart"
    r'.*supplied.*',  # "US supplied"
    r'.*improved.*',  # "Updated with improved armour"
    r'.*Specialist.*',  # "Specialist Beach Armoured Recovery"
    r'Self-propelled.*',  # "Self-propelled 25 pdr Gun"
    r'.*chasis.*',  # "conversion of Crusader chasis"
    r'.*with.*',  # "Standard Sherman with improved 76mm gun"
    r'.*vehicle.*',  # Various vehicle descriptions
    r'rare.*',  # "rare, pre-war"
    r'.*dozerblade.*',  # "Engineering vehicle with dozerblade"
    r'.*gun.*',  # "Replacement main gun"
]

# Fetch vehicles with remaining temp data
cursor.execute("""
    SELECT id, name, special_rules_temp
    FROM bg_reference_vehicles
    WHERE special_rules_temp IS NOT NULL AND special_rules_temp != ''
""")

vehicles = cursor.fetchall()
print(f"\nProcessing {len(vehicles)} vehicles with unparsed data...\n")

stats = {
    'rules_extracted': 0,
    'metadata_extracted': 0,
    'combined': 0,
    'unchanged': 0
}

for vehicle_id, name, special_rules_temp in vehicles:
    if not special_rules_temp:
        continue

    remaining = special_rules_temp
    special_rules = []
    metadata = []

    # Split by comma to handle compound entries
    parts = [p.strip() for p in remaining.split(',')]

    for part in parts:
        # Check if it's a special rule
        is_special_rule = False
        for keyword in special_rules_keywords:
            if keyword.lower() in part.lower():
                special_rules.append(part)
                is_special_rule = True
                break

        # If not a special rule, check if it's descriptive metadata
        if not is_special_rule:
            is_metadata = False
            for pattern in descriptive_patterns:
                if re.search(pattern, part, re.IGNORECASE):
                    metadata.append(part)
                    is_metadata = True
                    break

            # If not matched as either, treat as metadata by default
            if not is_metadata and part:
                metadata.append(part)

    # Update fields
    if special_rules:
        ss_special_value = ', '.join(special_rules)
        cursor.execute("UPDATE bg_reference_vehicles SET ss_special = ? WHERE id = ?", (ss_special_value, vehicle_id))
        stats['rules_extracted'] += 1

    if metadata:
        dc_meta_value = ', '.join(metadata)
        cursor.execute("UPDATE bg_reference_vehicles SET dc_meta = ? WHERE id = ?", (dc_meta_value, vehicle_id))
        stats['metadata_extracted'] += 1

    if special_rules and metadata:
        stats['combined'] += 1

    if not special_rules and not metadata:
        stats['unchanged'] += 1

    # Clear temp field
    cursor.execute("UPDATE bg_reference_vehicles SET special_rules_temp = NULL WHERE id = ?", (vehicle_id,))

conn.commit()

print("=" * 100)
print("EXTRACTION STATISTICS")
print("=" * 100)
print(f"  Vehicles with special rules extracted: {stats['rules_extracted']}")
print(f"  Vehicles with metadata extracted: {stats['metadata_extracted']}")
print(f"  Vehicles with BOTH: {stats['combined']}")
print(f"  Unchanged: {stats['unchanged']}")

# Show results
print("\n" + "=" * 100)
print("SAMPLE RESULTS (first 30 vehicles with special rules or metadata)")
print("=" * 100)

cursor.execute("""
    SELECT id, name, ss_special, dc_meta
    FROM bg_reference_vehicles
    WHERE ss_special IS NOT NULL OR dc_meta IS NOT NULL
    ORDER BY id
    LIMIT 30
""")

print("\nID  | Name                           | ss_special                  | dc_meta")
print("-" * 120)
for row in cursor.fetchall():
    vid, vname, ss_special, dc_meta = row
    print(f"{vid:3d} | {str(vname)[:30]:30s} | {str(ss_special or '')[:27]:27s} | {str(dc_meta or '')[:40]}")

# Check what's left in temp field (should be empty now)
cursor.execute("""
    SELECT COUNT(*)
    FROM bg_reference_vehicles
    WHERE special_rules_temp IS NOT NULL AND special_rules_temp != ''
""")

remaining_count = cursor.fetchone()[0]

print("\n" + "=" * 100)
print("VERIFICATION")
print("=" * 100)
print(f"Vehicles with data still in special_rules_temp: {remaining_count}")

if remaining_count > 0:
    cursor.execute("""
        SELECT id, name, special_rules_temp
        FROM bg_reference_vehicles
        WHERE special_rules_temp IS NOT NULL AND special_rules_temp != ''
    """)
    print("\nRemaining unparsed:")
    for row in cursor.fetchall():
        print(f"  ID {row[0]:3d}: {row[1]:30s} | {row[2]}")

# Summary by category
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE ss_hits IS NOT NULL")
hits_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE ss_transport_capacity IS NOT NULL")
transport_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE armor_modifier IS NOT NULL")
armor_mod_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE mount_1 IS NOT NULL")
mount_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE ss_special IS NOT NULL")
ss_special_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE dc_meta IS NOT NULL")
dc_meta_count = cursor.fetchone()[0]

print("\n" + "=" * 100)
print("FINAL SUMMARY - ALL PARSED FIELDS")
print("=" * 100)
print(f"  ss_hits: {hits_count} vehicles")
print(f"  ss_transport_capacity: {transport_count} vehicles")
print(f"  armor_modifier (Open-Topped): {armor_mod_count} vehicles")
print(f"  mount_1/2/3: {mount_count} vehicles")
print(f"  ss_special (game rules): {ss_special_count} vehicles")
print(f"  dc_meta (descriptive text): {dc_meta_count} vehicles")

conn.close()

print("\n" + "=" * 100)
print("✅ PARSING COMPLETE")
print("=" * 100)
