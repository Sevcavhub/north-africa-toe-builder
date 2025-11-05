#!/usr/bin/env python3
"""
Extract Canadian Recon and Engineer Support units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Recon  and Engineer Support.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Recon and Engineer Support units...')
    print()

    units = [
        # Reconnaissance Support Units
        {
            'unit_name': 'Recon Patrol',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 man',
            'men_count': 1,
            'points_cost': 10,
            'br_rating': '0+1 BR',
            'transport': 'None',
            'special_rules': 'Recce',
            'optional_upgrades': 'Add a runner (+3 pts), Spotter, upgrade, etc (partially visible)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Armoured Car Recon Patrol',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 Armoured Car',
            'men_count': None,
            'points_cost': 10,
            'br_rating': '2+1 BR',
            'transport': 'Armoured Car',
            'special_rules': 'Recce, Towing Spotter',
            'optional_upgrades': 'Upgrade Humber IV armoured car, Humber III armoured car, Daimler armoured car',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Carrier Team',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '3 men, 1 Carrier Rifle Team',
            'men_count': 3,
            'points_cost': 28,
            'br_rating': '1+1 BR',
            'transport': 'Bren Carrier',
            'special_rules': None,
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Rifle Section',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '3 men with a Bren',
            'men_count': 3,
            'points_cost': None,
            'br_rating': None,
            'transport': 'Mounted in a Bren Carrier',
            'special_rules': None,
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Recce Platoon Command',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '3 men',
            'men_count': 3,
            'points_cost': 28,
            'br_rating': '2+1 BR',
            'transport': None,
            'special_rules': 'Platoon Command',
            'optional_upgrades': 'Options: Replace 3 men with Scout Cars, Bren Carriers, Daimler, Humber Scout Car',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        # Engineer Support Units
        {
            'unit_name': 'Recovery Vehicle',
            'category': 'Engineer Support Units',
            'unit_composition': '1 Recovery Vehicle',
            'men_count': None,
            'points_cost': 34,
            'br_rating': '3+1 BR',
            'transport': 'Recovery Vehicle',
            'special_rules': 'Vehicle Recovery, Unique, Please note: M4 Recovery AFV (+2 pts), M32 Armoured Recovery (+8 pts), M3 Wrecker Heavy Truck',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Engineer Section',
            'category': 'Engineer Support Units',
            'unit_composition': '1 Armoured Engineering Vehicle',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': 'Armoured Engineering Vehicle',
            'special_rules': 'Engineers, Bren Team',
            'optional_upgrades': 'Combat Engineer Section, Add up to 1 flamethrower, Add up to 2 demolition charge',
            'nation': 'canadian',
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
    WHERE source_supplement = 'Battlegroup-Canadas-Crucible'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total Canadian army list units extracted: {count}')

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
