#!/usr/bin/env python3
"""
Extract Canadian Soft Skinned Vehicles from Canada's Crucible supplement
Populates bg_reference_vehicles table for reverse engineering formulas
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Soft Skinned Vehicles.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Soft Skinned Vehicles...')
    print()

    vehicles = [
        {
            'name': 'Motorcycle',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 6,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '1 Hit, 1 Transport, no BR counter',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Jeep',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 9,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '2 Hits, 3 Transport',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Bedford MWD',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 6,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '2 Hits, 6 Transport',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Bedford QL',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 6,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '3 Hits, 12 Transport',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'CMP',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 6,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '3 Hits, 12 Transport',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Bedford QLT / QLD',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 6,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '3 Hits, 22 Transport',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'Scammell Pioneer',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 6,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '4 Hits, vehicle recovery',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'M1 Wrecker',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 6,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '4 Hits, 1 vehicle recovery',
            'points_cost': None,
            'battle_rating': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE
        },
        {
            'name': 'M5 / M5 Ambulance',
            'nation': 'canadian',
            'year_range': '1941-1945',
            'vehicle_type': 'Soft-Skinned Vehicle',
            'off_road_inches': 6,
            'road_inches': 24,
            'armor_front': None,
            'armor_side': None,
            'armor_rear': None,
            'weapons': None,
            'special_rules': '2 Hits, Medical',
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
                vehicle.get('armor_front'),
                vehicle.get('armor_side'),
                vehicle.get('armor_rear'),
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
    AND vehicle_type = 'Soft-Skinned Vehicle'
    AND extraction_method = 'manual_screenshot'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total Canadian soft-skinned vehicles extracted: {count}')

    cursor.execute('''
    SELECT name, off_road_inches, road_inches, special_rules
    FROM bg_reference_vehicles
    WHERE source_file = 'Battlegroup-Canadas-Crucible'
    AND vehicle_type = 'Soft-Skinned Vehicle'
    ORDER BY name
    ''')

    print()
    print('Extracted vehicles:')
    for row in cursor.fetchall():
        name, off_road, road, special = row
        print(f'  {name}: {off_road}"/{road}" movement, {special}')

    conn.close()

if __name__ == "__main__":
    main()
