#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "master_database.db"

conn = sqlite3.connect(DB_PATH, timeout=60)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT id, name, armor_front, armor_side, armor_rear,
           movement_off_road, movement_road, weapon_1, nation, source
    FROM bg_reference_vehicles
    WHERE bg_builder_id IS NULL
""")

unlinked = cursor.fetchall()

print("=" * 80)
print(f"UNLINKED VEHICLES: {len(unlinked)}")
print("=" * 80)

for v in unlinked:
    print(f"\nID: {v['id']}")
    print(f"  Name: {v['name']}")
    print(f"  Armor: {v['armor_front']}/{v['armor_side']}/{v['armor_rear']}")
    print(f"  Movement: {v['movement_off_road']}\"{v['movement_road']}\"")
    print(f"  Weapon: {v['weapon_1']}")
    print(f"  Nation: {v['nation']}")
    print(f"  Source: {v['source']}")

conn.close()
