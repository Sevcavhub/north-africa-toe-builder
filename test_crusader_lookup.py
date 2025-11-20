#!/usr/bin/env python3
"""Test Crusader I lookup in database"""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path("database/master_database.db")

conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Search for Crusader I
print("Searching for 'Crusader I' in bg_builder_vehicles...")
cursor.execute("SELECT id, name, weapon_1_id, weapon_2_id FROM bg_builder_vehicles WHERE name LIKE '%Crusader I%'")
results = cursor.fetchall()

if results:
    print(f"Found {len(results)} matches:")
    for row in results:
        print(f"  ID: {row['id']}, Name: {row['name']}, weapon_1_id: {row['weapon_1_id']}, weapon_2_id: {row['weapon_2_id']}")
else:
    print("No matches found for 'Crusader I'")

# Try exact match
print("\nTrying exact match 'Crusader I'...")
cursor.execute("SELECT id, name FROM bg_builder_vehicles WHERE name = 'Crusader I'")
exact = cursor.fetchone()
if exact:
    print(f"  Found: {exact['name']}")
else:
    print("  Not found")

# Search for all Crusader variants
print("\nAll Crusader variants:")
cursor.execute("SELECT id, name FROM bg_builder_vehicles WHERE name LIKE '%Crusader%' ORDER BY name")
crusaders = cursor.fetchall()
for c in crusaders:
    print(f"  {c['name']}")

conn.close()
