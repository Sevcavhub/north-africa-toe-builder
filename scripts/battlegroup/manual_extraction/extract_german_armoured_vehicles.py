#!/usr/bin/env python3
"""
Extract German Armoured Vehicles from Canada's Crucible supplement
Appends to BG_Reference_Vehicles table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Armoured Vehicles.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Armoured Vehicles...')
    print()

    vehicles = [
        {
            'name': 'Panzer IV H or J',
            'nation': 'german',
            'vehicle_type': 'Tank',
            'off_road_inches': 12,
            'road_inches': 20,
            'armor_front': 'H',
            'armor_side': 'K',
            'armor_rear': 'L',
            'weapons': '75mm L/48 (Turret), MG (Coaxial), HMG',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Panther',
            'nation': 'german',
            'vehicle_type': 'Tank',
            'off_road_inches': 10,
            'road_inches': 14,
            'armor_front': 'H',
            'armor_side': 'K',
            'armor_rear': 'L',
            'weapons': '75mm L/70 (Turret), MG (Coaxial), HMG',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Sturmgeschutz',
            'nation': 'german',
            'vehicle_type': 'Assault Gun',
            'off_road_inches': 10,
            'road_inches': 14,
            'armor_front': 'L',
            'armor_side': 'K',
            'armor_rear': 'L',
            'weapons': 'MG (Pintle)',
            'special_rules': 'Recce, Reserve',
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'SdKfz 251/1',
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': 'MG (Pintle)',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'SdKfz 251/2',
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '80mm mortar (Hull)',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'SdKfz 251/3 or 251/4',
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': 'MG (Pintle)',
            'special_rules': 'Radio, CP Type4',
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        }
    ]

    for vehicle in vehicles:
        try:
            cursor.execute('''
            INSERT INTO BG_Reference_Vehicles (
                name, nation, vehicle_type,
                off_road_inches, road_inches,
                armor_front, armor_side, armor_rear,
                weapons, special_rules,
                source_document, screenshot_file,
                extraction_method, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle['name'],
                vehicle['nation'],
                vehicle['vehicle_type'],
                vehicle['off_road_inches'],
                vehicle['road_inches'],
                vehicle['armor_front'],
                vehicle['armor_side'],
                vehicle['armor_rear'],
                vehicle['weapons'],
                vehicle.get('special_rules'),
                vehicle['source_document'],
                vehicle['screenshot_file'],
                vehicle['extraction_method'],
                vehicle['verified_by']
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
    SELECT COUNT(*) FROM BG_Reference_Vehicles
    WHERE nation = 'german'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total German vehicles in database: {count}')

    cursor.execute('''
    SELECT name, vehicle_type, armor_front, weapons
    FROM BG_Reference_Vehicles
    WHERE screenshot_file = ?
    ORDER BY name
    ''', (SCREENSHOT_FILE,))

    print()
    print('Vehicles from this screenshot:')
    for row in cursor.fetchall():
        name, vtype, armor, weapons = row
        weapons_short = weapons[:50] + '...' if len(weapons) > 50 else weapons
        print(f'  {name} ({vtype}): Armor {armor}, {weapons_short}')

    conn.close()

if __name__ == "__main__":
    main()
