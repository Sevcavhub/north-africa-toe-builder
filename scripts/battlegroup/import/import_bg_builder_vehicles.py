#!/usr/bin/env python3
"""
Import BG Builder vehicles (601 entries) to database.
"""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
JSON_PATH = Path(__file__).parent.parent.parent.parent / "sources" / "bg_builder_vehicles.json"

def import_vehicles():
    print("BG Builder Vehicles Import")
    print("=" * 80)

    # Load JSON
    print(f"\nLoading: {JSON_PATH}")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        vehicles = json.load(f)
    print(f"   Loaded {len(vehicles)} vehicle entries")

    # Connect to database
    print(f"\nConnecting to: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH, timeout=60)
    cursor = conn.cursor()

    # Import vehicles
    print("\nImporting vehicles...")
    imported = 0
    skipped = 0
    errors = []

    for vehicle in vehicles:
        try:
            # Skip blank entry (id 0 or no name)
            if not vehicle.get('name') or vehicle.get('name') == 'Blank':
                skipped += 1
                continue

            # Parse movement array ['8','12'] → off_road=8, road=12
            move = vehicle.get('move', [])
            if isinstance(move, list):
                off_road = int(move[0]) if len(move) > 0 and move[0] else None
                road = int(move[1]) if len(move) > 1 and move[1] else None
            else:
                off_road = None
                road = None

            # Parse armor array ['L','N','N'] → front=L, side=N, rear=N
            armour = vehicle.get('armour', [])
            if not isinstance(armour, list):
                armour = []
            armor_front = armour[0] if len(armour) > 0 else None
            armor_side = armour[1] if len(armour) > 1 else None
            armor_rear = armour[2] if len(armour) > 2 else None

            # Parse weapons (can be array or single integer)
            weapons_raw = vehicle.get('weapons', [])
            if isinstance(weapons_raw, int):
                weapons = [weapons_raw]
            elif isinstance(weapons_raw, list):
                weapons = weapons_raw
            else:
                weapons = []

            weapon_1 = weapons[0] if len(weapons) > 0 else None
            weapon_2 = weapons[1] if len(weapons) > 1 else None
            weapon_3 = weapons[2] if len(weapons) > 2 else None
            weapon_4 = weapons[3] if len(weapons) > 3 else None

            # Insert vehicle
            cursor.execute("""
                INSERT INTO bg_builder_vehicles
                (id, name, movement_off_road, movement_road,
                 armor_front, armor_side, armor_rear,
                 weapon_1_id, weapon_2_id, weapon_3_id, weapon_4_id,
                 has_mg, has_ammo, special_rules, hits, capacity, movement_special, unique_flag)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle.get('id'),
                vehicle['name'],
                off_road, road,
                armor_front, armor_side, armor_rear,
                weapon_1, weapon_2, weapon_3, weapon_4,
                1 if vehicle.get('mg') else 0,
                1 if vehicle.get('ammo') else 0,
                vehicle.get('special'),
                vehicle.get('hits'),
                vehicle.get('capacity'),
                vehicle.get('movement'),
                1 if vehicle.get('unique') else 0
            ))
            imported += 1

            # Progress indicator every 50 vehicles
            if imported % 50 == 0:
                print(f"   Imported {imported} vehicles...")

        except Exception as e:
            errors.append((vehicle.get('id', 'unknown'), vehicle.get('name', 'unknown'), str(e)))
            continue

    conn.commit()

    # Summary
    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"\nImported:  {imported} vehicles")
    print(f"Skipped:   {skipped} vehicles (blank entries)")
    print(f"Errors:    {len(errors)} vehicles")

    if errors:
        print("\nErrors encountered:")
        for vid, vname, error in errors[:10]:  # Show first 10
            print(f"   ID {vid} ({vname}): {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")

    # Sample data check
    print("\nVerifying data...")
    cursor.execute("""
        SELECT id, name, movement_off_road, movement_road, armor_front, armor_side, armor_rear
        FROM bg_builder_vehicles
        WHERE name = 'Panzer III J'
    """)
    sample = cursor.fetchone()
    if sample:
        print(f"\nSample: Panzer III J")
        print(f"   ID: {sample[0]}")
        print(f"   Movement: {sample[2]}/{sample[3]} inches")
        print(f"   Armor: {sample[4]}/{sample[5]}/{sample[6]}")

    cursor.execute("SELECT COUNT(*) FROM bg_builder_vehicles")
    total = cursor.fetchone()[0]
    print(f"\nTotal vehicles in database: {total}")

    conn.close()

if __name__ == '__main__':
    import_vehicles()
