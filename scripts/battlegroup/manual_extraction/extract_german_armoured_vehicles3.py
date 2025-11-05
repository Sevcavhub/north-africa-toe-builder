#!/usr/bin/env python3
"""
Extract German Armoured Vehicles 3 from Canada's Crucible supplement
Appends to BG_Reference_Vehicles table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Armoured Vehicles3.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Armoured Vehicles 3...')
    print()

    vehicles = [
        {
            'name': 'SdKfz 222',
            'nation': 'german',
            'vehicle_type': 'Armoured Car',
            'off_road_inches': 8,
            'road_inches': 24,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '20mm&20 (Turret), MG',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'SdKfz 234/1',
            'nation': 'german',
            'vehicle_type': 'Armoured Car',
            'off_road_inches': 8,
            'road_inches': 24,
            'armor_front': 'N',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '20mm (Turret), MG',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'SdKfz 234/2',
            'nation': 'german',
            'vehicle_type': 'Armoured Car',
            'off_road_inches': 8,
            'road_inches': 24,
            'armor_front': 'N',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '50mm L/60 (Open-Topped/Co-axial), MG',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'SdKfz 234/3',
            'nation': 'german',
            'vehicle_type': 'Armoured Car',
            'off_road_inches': 8,
            'road_inches': 24,
            'armor_front': 'N',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '75mm L/24 (Hull)',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Flakpanzer 38(t)',
            'nation': 'german',
            'vehicle_type': 'Self-Propelled AA',
            'off_road_inches': 9,
            'road_inches': 15,
            'armor_front': 'M',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '20mm&20 (Turret)',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Wespe',
            'nation': 'german',
            'vehicle_type': 'Self-Propelled Artillery',
            'off_road_inches': 8,
            'road_inches': 12,
            'armor_front': 'N',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '105mm&12 (Hull, Open-Topped)',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Hummel',
            'nation': 'german',
            'vehicle_type': 'Self-Propelled Artillery',
            'off_road_inches': 8,
            'road_inches': 12,
            'armor_front': 'N',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': '150mm&15 (Hull, Open-Topped)',
            'special_rules': None,
            'source_document': 'Battlegroup-Canadas-Crucible',
            'screenshot_file': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Wirbelwind',
            'nation': 'german',
            'vehicle_type': 'Self-Propelled AA',
            'off_road_inches': 8,
            'road_inches': 12,
            'armor_front': 'N',
            'armor_side': 'O',
            'armor_rear': 'O',
            'weapons': 'Quad-20mm&15 (Turret, Open-Topped), MG (Bow)',
            'special_rules': None,
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
