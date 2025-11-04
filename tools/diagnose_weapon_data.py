#!/usr/bin/env python3
"""
Diagnostic script to check why weapon extraction is failing
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "master_database.db"

conn = sqlite3.connect(str(DB_PATH))

# Sample 10 equipment items
query = """
SELECT master_id, display_name, equipment_category, historical_specs_json
FROM equipment_master_new
WHERE master_id <= 10
ORDER BY master_id
"""

print("=" * 80)
print("WEAPON DATA DIAGNOSTIC")
print("=" * 80)

for row in conn.execute(query):
    master_id, display_name, category, specs_json = row

    print(f"\n[{master_id}] {display_name} ({category})")
    print("-" * 80)

    if specs_json:
        try:
            specs = json.loads(specs_json)

            # Check for weapon-related keys
            weapon_keys = [k for k in specs.keys() if 'gun' in k.lower() or 'weapon' in k.lower() or 'armament' in k.lower()]

            if weapon_keys:
                print("  Weapon keys found:")
                for key in weapon_keys:
                    value = specs[key]
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"    {key}: {value}")
            else:
                print("  No weapon keys found")

            # Check all keys for debugging
            print(f"  All keys ({len(specs)} total): {', '.join(list(specs.keys())[:15])}...")

        except Exception as e:
            print(f"  Error parsing specs: {e}")
    else:
        print("  No historical_specs_json")

conn.close()
