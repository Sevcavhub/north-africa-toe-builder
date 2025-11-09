#!/usr/bin/env python3
"""
Query BG Builder vehicles view with weapon names resolved
Usage: python query_bg_builder_vehicles.py [search_term]
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def query_vehicles(search_term=None):
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if search_term:
        # Search by name
        cursor.execute("""
            SELECT id, name, weapon_1, weapon_2, weapon_3, weapon_4,
                   armor_front, armor_side, armor_rear,
                   movement_off_road, movement_road,
                   special_rules, hits, capacity, has_mg, has_ammo,
                   armor_class
            FROM v_bg_builder_vehicles_detailed
            WHERE name LIKE ? OR weapon_1 LIKE ?
            ORDER BY name
        """, (f'%{search_term}%', f'%{search_term}%'))
    else:
        # Show all
        cursor.execute("""
            SELECT id, name, weapon_1, weapon_2, weapon_3, weapon_4,
                   armor_front, armor_side, armor_rear,
                   movement_off_road, movement_road,
                   special_rules, hits, capacity, has_mg, has_ammo,
                   armor_class
            FROM v_bg_builder_vehicles_detailed
            ORDER BY name
        """)

    results = cursor.fetchall()

    if not results:
        print(f"No results found for: {search_term}")
        conn.close()
        return

    print("=" * 120)
    print(f"BG BUILDER VEHICLES ({len(results)} results)")
    print("=" * 120)
    print()

    for vehicle in results:
        print(f"ID: {vehicle['id']:3d} | {vehicle['name']:45s}")
        print(f"  Armor: {vehicle['armor_front'] or '?'}/{vehicle['armor_side'] or '?'}/{vehicle['armor_rear'] or '?'} ({vehicle['armor_class']})")
        print(f"  Movement: {vehicle['movement_off_road'] or '?'}\" off-road, {vehicle['movement_road'] or '?'}\" road")

        weapons = []
        if vehicle['weapon_1']:
            weapons.append(f"1: {vehicle['weapon_1']}")
        if vehicle['weapon_2']:
            weapons.append(f"2: {vehicle['weapon_2']}")
        if vehicle['weapon_3']:
            weapons.append(f"3: {vehicle['weapon_3']}")
        if vehicle['weapon_4']:
            weapons.append(f"4: {vehicle['weapon_4']}")

        if weapons:
            print(f"  Weapons: {', '.join(weapons)}")
        else:
            print(f"  Weapons: None")

        details = []
        if vehicle['hits']:
            details.append(f"Hits: {vehicle['hits']}")
        if vehicle['capacity']:
            details.append(f"Capacity: {vehicle['capacity']}")
        if vehicle['has_mg']:
            details.append(f"Has MG: Yes")
        if vehicle['has_ammo']:
            details.append(f"Has Ammo: Yes")

        if details:
            print(f"  Details: {', '.join(details)}")

        if vehicle['special_rules']:
            print(f"  Special Rules: {vehicle['special_rules']}")

        print()

    conn.close()

if __name__ == '__main__':
    search = sys.argv[1] if len(sys.argv) > 1 else None
    query_vehicles(search)
