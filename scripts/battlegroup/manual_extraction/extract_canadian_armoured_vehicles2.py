#!/usr/bin/env python3
"""
Extract Canadian Armoured Vehicles (2nd screenshot) from Canada's Crucible supplement
Populates bg_reference_vehicles table for reverse engineering formulas
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Armoured Vehicles2.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Armoured Vehicles (2)...')
    print()

    vehicles = [
        {
            'name': 'Humber IV',
            'nation': 'canadian',
            'year_range': '1943-1945',
            'vehicle_type': 'Armoured Car',
            'off_road_inches': 8,
            'road_inches': 24,
            'armor_front': 'M',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '37mmL53',
            'special_rules': 'Turret mount, 12 ammo',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Humber Light Recon Vehicle',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Recon Vehicle',
            'off_road_inches': 8,
            'road_inches': 24,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': 'LMG',
            'special_rules': 'Hull mount',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'M5/M9 Halftrack',
            'nation': 'canadian',
            'year_range': '1942-1945',
            'vehicle_type': 'Halftrack',
            'off_road_inches': 12,
            'road_inches': 24,
            'armor_front': 'N',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': 'MG2',
            'special_rules': 'Open-Topped, Pintle mount',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Loyd Carrier',
            'nation': 'canadian',
            'year_range': '1940-1945',
            'vehicle_type': 'Carrier',
            'off_road_inches': 10,
            'road_inches': 15,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': None,
            'special_rules': 'Open-Topped',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Armoured Bulldozer',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Engineer Vehicle',
            'off_road_inches': 4,
            'road_inches': 6,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': None,
            'special_rules': 'Engineer',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Bren Carrier',
            'nation': 'canadian',
            'year_range': '1937-1945',
            'vehicle_type': 'Carrier',
            'off_road_inches': 10,
            'road_inches': 15,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': 'LMG',
            'special_rules': 'Open-Topped, Hull mount',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        }
    ]

    for vehicle in vehicles:
        try:
            cursor.execute('''
            INSERT INTO bg_reference_vehicles (
                name, nation, year_range, vehicle_type,
                off_road_inches, road_inches,
                armor_front, armor_side, armor_rear,
                weapons, special_rules, points_cost, battle_rating,
                source_file, extraction_method, verified_by, screenshot_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle['name'],
                vehicle['nation'],
                vehicle['year_range'],
                vehicle['vehicle_type'],
                vehicle['off_road_inches'],
                vehicle['road_inches'],
                vehicle['armor_front'],
                vehicle['armor_side'],
                vehicle['armor_rear'],
                vehicle.get('weapons'),
                vehicle.get('special_rules'),
                vehicle.get('points_cost'),
                vehicle.get('battle_rating'),
                vehicle['source_file'],
                vehicle['extraction_method'],
                vehicle['verified_by'],
                vehicle['screenshot_file']
            ))
            print(f"  [OK] Inserted: {vehicle['name']}")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {vehicle['name']}: {e}")

    conn.commit()

    # Verification
    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print()

    cursor.execute('''
    SELECT COUNT(*) FROM bg_reference_vehicles
    WHERE source_file = 'Battlegroup-Canadas-Crucible'
    AND extraction_method = 'manual_screenshot'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total Canadian vehicles extracted from all screenshots: {count}')

    cursor.execute('''
    SELECT name, vehicle_type, off_road_inches, road_inches, armor_front, weapons
    FROM bg_reference_vehicles
    WHERE screenshot_file = ?
    ORDER BY vehicle_type, name
    ''', (SCREENSHOT_FILE,))

    print()
    print('Vehicles from this screenshot:')
    for row in cursor.fetchall():
        name, vtype, off_road, road, armor, weapons = row
        weapons_str = weapons if weapons else 'Unarmed'
        print(f'  {name} ({vtype}): {off_road}"/{road}" movement, {armor} armor front, {weapons_str}')

    conn.close()

if __name__ == "__main__":
    main()
