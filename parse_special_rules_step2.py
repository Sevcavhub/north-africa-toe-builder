#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse special_rules field - Step 2: Extract patterns and clean temp field"""

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
print("SPECIAL_RULES PARSING - STEP 2: EXTRACTION")
print("=" * 100)

# Fetch all vehicles with special_rules_temp
cursor.execute("""
    SELECT id, name, special_rules_temp
    FROM bg_reference_vehicles
    WHERE special_rules_temp IS NOT NULL
""")

vehicles = cursor.fetchall()
print(f"\nProcessing {len(vehicles)} vehicles...")

stats = {
    'hits_extracted': 0,
    'transport_extracted': 0,
    'open_topped_extracted': 0,
    'mount_extracted': 0
}

for vehicle_id, name, special_rules_temp in vehicles:
    if not special_rules_temp:
        continue

    remaining = special_rules_temp

    # Extract hits: "X Hit" or "X Hits"
    hits_match = re.search(r'(\d+)\s+Hits?', remaining, re.IGNORECASE)
    if hits_match:
        hits_value = int(hits_match.group(1))
        cursor.execute("UPDATE bg_reference_vehicles SET ss_hits = ? WHERE id = ?", (hits_value, vehicle_id))
        remaining = re.sub(r'\d+\s+Hits?,?\s*', '', remaining, flags=re.IGNORECASE)
        stats['hits_extracted'] += 1

    # Extract transport: "X Transport"
    transport_match = re.search(r'(\d+)\s+Transport', remaining, re.IGNORECASE)
    if transport_match:
        transport_value = int(transport_match.group(1))
        cursor.execute("UPDATE bg_reference_vehicles SET ss_transport_capacity = ? WHERE id = ?", (transport_value, vehicle_id))
        remaining = re.sub(r'\d+\s+Transport,?\s*', '', remaining, flags=re.IGNORECASE)
        stats['transport_extracted'] += 1

    # Extract Open-Topped (move to armor_modifier)
    if re.search(r'Open-?Topped', remaining, re.IGNORECASE):
        cursor.execute("UPDATE bg_reference_vehicles SET armor_modifier = 'Open-Topped' WHERE id = ?", (vehicle_id,))
        remaining = re.sub(r'Open-?Topped,?\s*', '', remaining, flags=re.IGNORECASE)
        stats['open_topped_extracted'] += 1

    # Extract mount keywords (Turret, Hull, Co-axial, Bow, Pintle)
    mount_patterns = [
        (r'Turret\s+mount', 'Turret'),
        (r'Hull\s+mount', 'Hull'),
        (r'Co-axial\s+mount', 'Co-axial'),
        (r'Bow\s+mount', 'Bow'),
        (r'Pintle\s+mount', 'Pintle')
    ]

    mounts = []
    for pattern, mount_type in mount_patterns:
        if re.search(pattern, remaining, re.IGNORECASE):
            mounts.append(mount_type)
            remaining = re.sub(pattern + r',?\s*', '', remaining, flags=re.IGNORECASE)

    # Update mount fields
    if mounts:
        for i, mount in enumerate(mounts[:3]):  # Max 3 mounts
            mount_field = f'mount_{i+1}'
            cursor.execute(f"UPDATE bg_reference_vehicles SET {mount_field} = ? WHERE id = ?", (mount, vehicle_id))
        stats['mount_extracted'] += 1

    # Clean up remaining text (remove leading/trailing commas and spaces)
    remaining = re.sub(r'^[,\s]+|[,\s]+$', '', remaining)
    remaining = re.sub(r',\s*,', ',', remaining)  # Remove double commas

    # Update temp field with remaining text
    cursor.execute("UPDATE bg_reference_vehicles SET special_rules_temp = ? WHERE id = ?", (remaining if remaining else None, vehicle_id))

conn.commit()

print("\n" + "=" * 100)
print("EXTRACTION STATISTICS")
print("=" * 100)
print(f"  Hits extracted: {stats['hits_extracted']}")
print(f"  Transport extracted: {stats['transport_extracted']}")
print(f"  Open-Topped extracted: {stats['open_topped_extracted']}")
print(f"  Mounts extracted: {stats['mount_extracted']}")

# Show results
print("\n" + "=" * 100)
print("SAMPLE RESULTS (first 20 vehicles)")
print("=" * 100)

cursor.execute("""
    SELECT id, name, ss_hits, ss_transport_capacity, armor_modifier, mount_1, mount_2, mount_3, special_rules_temp
    FROM bg_reference_vehicles
    WHERE special_rules IS NOT NULL
    ORDER BY id
    LIMIT 20
""")

print("\nID  | Name                     | Hits | Transport | Open-T | M1      | M2   | M3   | Remaining")
print("-" * 110)
for row in cursor.fetchall():
    vid, vname, hits, transport, armor_mod, m1, m2, m3, remaining = row
    print(f"{vid:3d} | {str(vname)[:24]:24s} | {str(hits or '-'):4s} | {str(transport or '-'):9s} | {str(armor_mod or '-')[:6]:6s} | {str(m1 or '-')[:7]:7s} | {str(m2 or '-')[:4]:4s} | {str(m3 or '-')[:4]:4s} | {str(remaining or '')[:30]}")

# Show what's left in temp field
cursor.execute("""
    SELECT special_rules_temp, COUNT(*)
    FROM bg_reference_vehicles
    WHERE special_rules_temp IS NOT NULL AND special_rules_temp != ''
    GROUP BY special_rules_temp
    ORDER BY COUNT(*) DESC
""")

remaining_patterns = cursor.fetchall()

print("\n" + "=" * 100)
print("REMAINING UNPARSED DATA (grouped by pattern)")
print("=" * 100)
print(f"\nTotal unique patterns remaining: {len(remaining_patterns)}\n")

for pattern, count in remaining_patterns[:30]:  # Show top 30
    print(f"  [{count:2d}x] {pattern}")

conn.close()

print("\n" + "=" * 100)
print("✅ EXTRACTION COMPLETE")
print("=" * 100)
