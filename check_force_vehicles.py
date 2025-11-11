#!/usr/bin/env python3
"""Check how vehicles link to Tobruk/Torch forces"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "master_database.db"

conn = sqlite3.connect(DB_PATH, timeout=60)
cursor = conn.cursor()

# Get sample Tobruk force
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
print(f"\nSections: {len(sections)}")

if sections:
    print("\nFirst section sample:")
    print(json.dumps(sections[0], indent=2)[:800])

# Extract all vehicle IDs from Tobruk/Torch forces
cursor.execute("""
    SELECT force_id, force_name, force_group, sections
    FROM bg_builder_forces
    WHERE force_group IN ('Battlegroup Tobruk', 'Battlegroup Torch')
""")

all_vehicle_ids = set()
for force in cursor.fetchall():
    sections = json.loads(force[3]) if force[3] else []
    for section in sections:
        if 'units' in section:
            for unit in section['units']:
                if 'vehicle_id' in unit:
                    all_vehicle_ids.add(unit['vehicle_id'])

print(f"\n\nTotal unique vehicle IDs in Tobruk/Torch forces: {len(all_vehicle_ids)}")

conn.close()
