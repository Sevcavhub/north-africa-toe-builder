#!/usr/bin/env python3
"""Check where points and BR values are stored in bg_builder_forces"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "master_database.db"

conn = sqlite3.connect(DB_PATH, timeout=60)
cursor = conn.cursor()

# Get sample force with vehicle
cursor.execute("""
    SELECT force_id, force_name, force_group, sections
    FROM bg_builder_forces
    WHERE force_group = 'Battlegroup Tobruk'
    LIMIT 1
""")
row = cursor.fetchone()

print("Sample Tobruk force:")
print(f"  Force: {row[1]}")
print(f"  Group: {row[2]}")

sections = json.loads(row[3]) if row[3] else []

# Find entry with vehicle and points/BR
found_vehicle = False
for section in sections:
    if 'entries' in section:
        for entry in section['entries']:
            if 'options' in entry:
                for option in entry['options']:
                    if 'choices' in option:
                        for choice in option['choices']:
                            if 'v' in choice and not found_vehicle:
                                print("\n" + "=" * 80)
                                print("FOUND VEHICLE CHOICE:")
                                print("=" * 80)
                                print(json.dumps(choice, indent=2))
                                found_vehicle = True
                                break
                    if found_vehicle:
                        break

            # Check if entry itself has vehicle
            if 'v' in entry and not found_vehicle:
                print("\n" + "=" * 80)
                print("FOUND VEHICLE ENTRY:")
                print("=" * 80)
                print(json.dumps(entry, indent=2))
                found_vehicle = True
                break

            if found_vehicle:
                break
    if found_vehicle:
        break

# Also check section-level data
print("\n" + "=" * 80)
print("SAMPLE SECTION (with entries):")
print("=" * 80)
for section in sections:
    if 'entries' in section and len(section['entries']) > 0:
        print(json.dumps(section, indent=2)[:1500])
        break

conn.close()
