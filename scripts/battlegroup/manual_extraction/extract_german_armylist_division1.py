#!/usr/bin/env python3
"""
Extract German Division 1 units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Division1.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Division 1 units...')
    print()

    units = [
        {
            'unit_name': 'Forward HQ Officer',
            'category': 'Forward Headquarters Units',
            'unit_composition': '1 man',
            'men_count': 1,
            'points_cost': 23,
            'br_rating': '5+1 BR',
            'transport': 'Utility (4x2)',
            'special_rules': 'Dispatches',
            'optional_upgrades': 'Replace 1 man and Utility (4x2) (+5 pts), Panther or SdKfz 250 Observation (+17 pts or +3 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Radio Truck',
            'category': 'Forward Headquarters Units',
            'unit_composition': '1 man',
            'men_count': 1,
            'points_cost': 17,
            'br_rating': '1+1 BR',
            'transport': 'Opel Blitz (6x4)',
            'special_rules': 'Radio/Communications',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Motorcycle Dispatch Rider',
            'category': 'Forward Headquarters Units',
            'unit_composition': '1 man',
            'men_count': 1,
            'points_cost': 12,
            'br_rating': '0+1 BR',
            'transport': 'Motorcycle',
            'special_rules': 'Dispatches',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'SdKfz 250 Observation Vehicle',
            'category': 'Forward Headquarters Units',
            'unit_composition': '1 man',
            'men_count': 1,
            'points_cost': 13,
            'br_rating': '1+1 BR',
            'transport': 'SdKfz 250',
            'special_rules': 'Observation Vehicle',
            'optional_upgrades': 'Upgrade Medium Truck to Opel Blitz with Driver (+6 pts), SdKfz 250/7 Half-track (+20 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Mortar Spotter',
            'category': 'Forward Headquarters Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 12,
            'br_rating': '0+1 BR',
            'transport': None,
            'special_rules': 'Mortar Spotter',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Forward Observer Team',
            'category': 'Forward Headquarters Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 33,
            'br_rating': '1+1 BR',
            'transport': 'Utility Truck',
            'special_rules': 'Artillery Spotter, Senior Officer',
            'optional_upgrades': 'Replace Utility Truck with: SdKfz 250 (+24 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        }
    ]

    for unit in units:
        try:
            cursor.execute('''
            INSERT INTO BG_Reference_ArmyList_Examples (
                unit_name, category, unit_composition, men_count,
                points_cost, br_rating, transport, special_rules,
                optional_upgrades, nation, source_supplement,
                source_image_location, extraction_method, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                unit['unit_name'],
                unit['category'],
                unit['unit_composition'],
                unit.get('men_count'),
                unit.get('points_cost'),
                unit.get('br_rating'),
                unit.get('transport'),
                unit.get('special_rules'),
                unit.get('optional_upgrades'),
                unit['nation'],
                unit['source_supplement'],
                unit['source_image_location'],
                unit['extraction_method'],
                unit['verified_by']
            ))
            print(f"  [OK] Inserted: {unit['unit_name']}")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {unit['unit_name']}: {e}")

    conn.commit()

    # Verification
    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print()

    cursor.execute('''
    SELECT COUNT(*) FROM BG_Reference_ArmyList_Examples
    WHERE nation = 'german'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total German army list units extracted: {count}')

    cursor.execute('''
    SELECT unit_name, category, points_cost, br_rating
    FROM BG_Reference_ArmyList_Examples
    WHERE source_image_location = ?
    ORDER BY category, unit_name
    ''', (SCREENSHOT_FILE,))

    print()
    print('Units from this screenshot:')
    for row in cursor.fetchall():
        name, category, points, br = row
        pts_str = f'{points} pts' if points else 'N/A'
        br_str = br if br else 'N/A'
        print(f'  {name} ({category}): {pts_str}, {br_str}')

    conn.close()

if __name__ == "__main__":
    main()
