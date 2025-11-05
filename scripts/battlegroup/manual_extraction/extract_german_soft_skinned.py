#!/usr/bin/env python3
"""
Extract German Soft Skinned Vehicles from Canada's Crucible supplement
Appends to BG_Reference_Vehicles table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Soft Skinned Vehicles.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Soft Skinned Vehicles...')
    print()

    vehicles = [
        {
            'name': 'Motorcycle',
            'nation': 'german',
            'vehicle_type': 'Motorcycle',
            'off_road_inches': 6,
            'road_inches': 24,
            'special_rules': 'no BR counter',
            'notes': '1 hit, 1 transport capacity'
        },
        {
            'name': 'Motorcycle and sidecar',
            'nation': 'german',
            'vehicle_type': 'Motorcycle',
            'off_road_inches': 6,
            'road_inches': 24,
            'special_rules': 'no BR counter',
            'notes': '1 hit, 2 transport capacity'
        },
        {
            'name': 'Staff car',
            'nation': 'german',
            'vehicle_type': 'Car',
            'off_road_inches': 6,
            'road_inches': 24,
            'special_rules': None,
            'notes': '2 hits, 3 transport capacity'
        },
        {
            'name': 'Kubelwagen',
            'nation': 'german',
            'vehicle_type': 'Car',
            'off_road_inches': 6,
            'road_inches': 24,
            'special_rules': None,
            'notes': '2 hits, 3 transport capacity'
        },
        {
            'name': 'Medium Truck',
            'nation': 'german',
            'vehicle_type': 'Truck',
            'off_road_inches': 6,
            'road_inches': 24,
            'special_rules': 'amphibious',
            'notes': '2 hits, 5 transport capacity'
        },
        {
            'name': 'Steyr/Horch Heavy Car',
            'nation': 'german',
            'vehicle_type': 'Car',
            'off_road_inches': 6,
            'road_inches': 24,
            'special_rules': None,
            'notes': '2 hits, 5 transport capacity'
        },
        {
            'name': 'Opel Blitz (medium truck)',
            'nation': 'german',
            'vehicle_type': 'Truck',
            'off_road_inches': 6,
            'road_inches': 24,
            'special_rules': None,
            'notes': '3 hits, 12 transport capacity'
        },
        {
            'name': 'Opel Maultier',
            'nation': 'german',
            'vehicle_type': 'Truck',
            'off_road_inches': 12,
            'road_inches': 16,
            'special_rules': None,
            'notes': '3 hits, 12 transport capacity'
        },
        {
            'name': 'Heavy Truck',
            'nation': 'german',
            'vehicle_type': 'Truck',
            'off_road_inches': 6,
            'road_inches': 24,
            'special_rules': None,
            'notes': '4 hits, 24 transport capacity'
        },
        {
            'name': '1 tonne SdKfz 10',
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'special_rules': None,
            'notes': '5 transport capacity'
        },
        {
            'name': '3 tonne SdKfz 11',
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'special_rules': None,
            'notes': '8 transport capacity'
        },
        {
            'name': '5 tonne SdKfz 6',
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'special_rules': None,
            'notes': '3 hits, 10 transport capacity'
        },
        {
            'name': '8 tonne SdKfz 7',
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'special_rules': None,
            'notes': '4 hits, 12 transport capacity'
        },
        {
            'name': '12 tonne SdKfz 8',
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'special_rules': None,
            'notes': '4 hits, 15 transport capacity'
        },
        {
            'name': "18 tonne SdKfz 9 'Famo'",
            'nation': 'german',
            'vehicle_type': 'Half-track',
            'off_road_inches': 12,
            'road_inches': 16,
            'special_rules': 'repair recovery',
            'notes': '5 hits'
        }
    ]

    for vehicle in vehicles:
        try:
            cursor.execute('''
            INSERT INTO BG_Reference_Vehicles (
                name, nation, vehicle_type,
                off_road_inches, road_inches,
                special_rules, notes,
                source_document, screenshot_file,
                extraction_method, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle['name'],
                vehicle['nation'],
                vehicle['vehicle_type'],
                vehicle['off_road_inches'],
                vehicle['road_inches'],
                vehicle.get('special_rules'),
                vehicle.get('notes'),
                'Battlegroup-Canadas-Crucible',
                SCREENSHOT_FILE,
                'manual_screenshot',
                'claude'
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
    SELECT name, vehicle_type, off_road_inches, road_inches, special_rules
    FROM BG_Reference_Vehicles
    WHERE screenshot_file = ?
    ORDER BY vehicle_type, name
    ''', (SCREENSHOT_FILE,))

    print()
    print('Vehicles from this screenshot:')
    for row in cursor.fetchall():
        name, vtype, off_road, road, special = row
        special_str = f', {special}' if special else ''
        print(f'  {name} ({vtype}): {off_road}\"/{road}\"{special_str}')

    conn.close()

if __name__ == "__main__":
    main()
