#!/usr/bin/env python3
"""Extract all vehicle IDs from Tobruk/Torch force lists"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "master_database.db"

def extract_vehicle_ids(sections):
    """Recursively extract all 'v' values from force sections"""
    vehicle_ids = set()

    def recurse(obj):
        if isinstance(obj, dict):
            if 'v' in obj:
                v = obj['v']
                if isinstance(v, int):
                    vehicle_ids.add(v)
                elif isinstance(v, list):
                    for vid in v:
                        if isinstance(vid, int):
                            vehicle_ids.add(vid)
            for value in obj.values():
                recurse(value)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)

    recurse(sections)
    return vehicle_ids

conn = sqlite3.connect(DB_PATH, timeout=60)
cursor = conn.cursor()

# Extract all vehicle IDs from Tobruk/Torch forces
cursor.execute("""
    SELECT force_id, force_name, force_group, sections
    FROM bg_builder_forces
    WHERE force_group IN ('Battlegroup Tobruk', 'Battlegroup Torch')
""")

all_vehicle_ids = set()
force_count = 0

for force in cursor.fetchall():
    force_count += 1
    sections = json.loads(force[3]) if force[3] else []
    vehicle_ids = extract_vehicle_ids(sections)
    all_vehicle_ids.update(vehicle_ids)
    print(f"[{force[0]}] {force[1]} ({force[2]}): {len(vehicle_ids)} vehicles")

print(f"\n{'='*80}")
print(f"Total forces processed: {force_count}")
print(f"Total unique vehicle IDs: {len(all_vehicle_ids)}")
print(f"{'='*80}")

# Save to file for export script
with open('tobruk_torch_vehicle_ids.txt', 'w') as f:
    for vid in sorted(all_vehicle_ids):
        f.write(f"{vid}\n")

print(f"\nVehicle IDs saved to: tobruk_torch_vehicle_ids.txt")

# Sample some vehicle names
cursor.execute(f"""
    SELECT id, name
    FROM bg_builder_vehicles
    WHERE id IN ({','.join(map(str, list(all_vehicle_ids)[:20]))})
    ORDER BY name
""")

print(f"\nSample vehicles (first 20):")
for v in cursor.fetchall():
    print(f"  [{v[0]:3d}] {v[1]}")

conn.close()
