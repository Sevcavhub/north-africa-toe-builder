#!/usr/bin/env python3
"""
Detailed weapon data diagnostic
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "master_database.db"

conn = sqlite3.connect(str(DB_PATH))

# Get items with bg_reference_vehicles_weapons
query = """
SELECT master_id, display_name, equipment_category, historical_specs_json
FROM equipment_master_new
WHERE historical_specs_json LIKE '%bg_reference_vehicles_weapons%'
LIMIT 5
"""

print("=" * 80)
print("ITEMS WITH BG_REFERENCE_VEHICLES_WEAPONS")
print("=" * 80)

for row in conn.execute(query):
    master_id, display_name, category, specs_json = row
    specs = json.loads(specs_json)

    print(f"\n[{master_id}] {display_name} ({category})")

    if 'bg_reference_vehicles_weapons' in specs:
        weapons = specs['bg_reference_vehicles_weapons']
        print(f"  Weapons data: {json.dumps(weapons, indent=4)}")

# Check artillery items (which ARE the weapons)
print("\n" + "=" * 80)
print("ARTILLERY ITEMS (SHOULD BE WEAPONS)")
print("=" * 80)

query2 = """
SELECT master_id, display_name, equipment_category, historical_specs_json
FROM equipment_master_new
WHERE equipment_category = 'artillery'
LIMIT 5
"""

for row in conn.execute(query2):
    master_id, display_name, category, specs_json = row

    print(f"\n[{master_id}] {display_name} ({category})")

    if specs_json:
        specs = json.loads(specs_json)
        print(f"  Keys: {', '.join(specs.keys())}")

        # Check for caliber references
        for key, value in specs.items():
            if isinstance(value, (str, int, float)) and (
                'mm' in str(value).lower() or
                'pounder' in str(value).lower() or
                'pdr' in str(value).lower() or
                'cm' in str(value).lower()
            ):
                print(f"    {key}: {value}")

# Check tanks with main_gun in display_name
print("\n" + "=" * 80)
print("CHECKING TANKS FOR GUN DATA IN DISPLAY NAME")
print("=" * 80)

query3 = """
SELECT master_id, display_name, equipment_category
FROM equipment_master_new
WHERE equipment_category = 'tank'
AND (
    display_name LIKE '%mm%'
    OR display_name LIKE '%pounder%'
    OR display_name LIKE '%pdr%'
)
LIMIT 10
"""

for row in conn.execute(query3):
    master_id, display_name, category = row
    print(f"  [{master_id}] {display_name}")

conn.close()
