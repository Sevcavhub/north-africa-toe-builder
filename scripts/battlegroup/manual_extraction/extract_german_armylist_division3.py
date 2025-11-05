#!/usr/bin/env python3
"""
Extract German Division 3 units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Division3.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Division 3 units...')
    print()

    units = [
        # Tank Units
        {
            'unit_name': 'Panther IV Platoon',
            'category': 'Tank Units',
            'unit_composition': '3 Panthers IV (H or J), 1 Panther IV Officer (H/J/K)',
            'men_count': None,
            'points_cost': 135,
            'br_rating': '8+1 BR',
            'transport': None,
            'special_rules': 'Officer, Radio',
            'optional_upgrades': 'Add up to 3 additional Panther IV (+90 pts total), Panther IV (+30 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Additional Panther IV',
            'category': 'Tank Units',
            'unit_composition': '1 Panther IV',
            'men_count': None,
            'points_cost': 30,
            'br_rating': '3+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Panther',
            'category': 'Tank Units',
            'unit_composition': '1 Panther G',
            'men_count': None,
            'points_cost': 59,
            'br_rating': '3+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        # Artillery Units
        {
            'unit_name': 'Forward Observer Team',
            'category': 'Artillery Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 33,
            'br_rating': '1+1 BR',
            'transport': 'Utility Truck',
            'special_rules': 'Artillery Spotter, Senior Officer',
            'optional_upgrades': 'Upgrade to SdKfz 250 (+24 pts), SdKfz 251 (+27 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Light Panzer Artillery Battery',
            'category': 'Artillery Units',
            'unit_composition': '3 Self Propelled guns',
            'men_count': None,
            'points_cost': 63,
            'br_rating': '6+1 BR',
            'transport': 'Self-propelled',
            'special_rules': None,
            'optional_upgrades': 'Include additional half-tracks',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Heavy Mortar Team',
            'category': 'Artillery Units',
            'unit_composition': '1 Heavy mortar',
            'men_count': None,
            'points_cost': 20,
            'br_rating': '1+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Include 3 man loader team (+10 pts), Bren Carrier available',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Off-Table Mortar Fire',
            'category': 'Artillery Units',
            'unit_composition': '1 or 3 x 80mm mortars',
            'men_count': None,
            'points_cost': 24,
            'br_rating': '1 BR',
            'transport': None,
            'special_rules': 'Off-table fire',
            'optional_upgrades': '3 x 80mm mortars (72 pts, 1 BR)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Light Artillery Battery',
            'category': 'Artillery Units',
            'unit_composition': '3 x 105mm guns',
            'men_count': None,
            'points_cost': 93,
            'br_rating': '6+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Include 3 man loader teams (+30 pts), SdKfz 11 half-track tows (+27 pts)',
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
