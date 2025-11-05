#!/usr/bin/env python3
"""
Extract German Guns from Canada's Crucible supplement
Appends to BG_Reference_Guns table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Guns.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Guns...')
    print()

    guns = [
        # ANTI-TANK
        {
            'name': '37mm PAK35/36',
            'nation': 'german',
            'caliber_mm': 37,
            'he_dice': 1,
            'he_target': '5+',
            'ap_0_10': 3,
            'ap_10_20': 2,
            'ap_20_30': 2,
            'ap_30_40': 1,
            'ap_40_50': 1,
            'ap_50_70': 1,
        },
        {
            'name': '50mm PAK38',
            'nation': 'german',
            'caliber_mm': 50,
            'he_dice': 1,
            'he_target': '5+',
            'ap_0_10': 5,
            'ap_10_20': 4,
            'ap_20_30': 3,
            'ap_30_40': 3,
            'ap_40_50': 2,
            'ap_50_70': 2,
        },
        {
            'name': '75mm PAK40',
            'nation': 'german',
            'caliber_mm': 75,
            'he_dice': 2,
            'he_target': '5+',
            'ap_0_10': 7,
            'ap_10_20': 6,
            'ap_20_30': 5,
            'ap_30_40': 5,
            'ap_40_50': 4,
            'ap_50_70': 4,
        },
        # WEAPON
        {
            'name': 'PaK97/38',
            'nation': 'german',
            'caliber_mm': 75,
            'he_dice': 2,
            'he_target': '4+',
            'ap_0_10': 4,
            'ap_10_20': 3,
            'ap_20_30': 2,
            'ap_30_40': 2,
            'ap_40_50': 1,
            'ap_50_70': 1,
        },
        # VERY LIGHT GUNS
        {
            'name': '75mm leIG18',
            'nation': 'german',
            'caliber_mm': 75,
            'he_dice': 2,
            'he_target': '5+',
            'ap_0_10': None,
            'ap_10_20': None,
            'ap_20_30': None,
            'ap_30_40': None,
            'ap_40_50': None,
            'ap_50_70': None,
        },
        # HOWITZERS
        {
            'name': 'PzKPfw 38(sf) 2cm',
            'nation': 'german',
            'caliber_mm': 20,
            'he_dice': 1,
            'he_target': '6+',
            'ap_0_10': 2,
            'ap_10_20': 1,
            'ap_20_30': 1,
            'ap_30_40': None,
            'ap_40_50': None,
            'ap_50_70': None,
        },
        {
            'name': 'PzKPfw II 2cm',
            'nation': 'german',
            'caliber_mm': 20,
            'he_dice': 1,
            'he_target': '6+',
            'ap_0_10': 2,
            'ap_10_20': 1,
            'ap_20_30': 1,
            'ap_30_40': None,
            'ap_40_50': None,
            'ap_50_70': None,
        },
        {
            'name': 'PzKPfw IV 5cm',
            'nation': 'german',
            'caliber_mm': 50,
            'he_dice': 1,
            'he_target': '5+',
            'ap_0_10': 4,
            'ap_10_20': 3,
            'ap_20_30': 3,
            'ap_30_40': 2,
            'ap_40_50': 2,
            'ap_50_70': 1,
        },
        # LIGHT GUNS
        {
            'name': 'PzKPfw 38(sf) 3.7cm',
            'nation': 'german',
            'caliber_mm': 37,
            'he_dice': 1,
            'he_target': '5+',
            'ap_0_10': 3,
            'ap_10_20': 2,
            'ap_20_30': 2,
            'ap_30_40': 1,
            'ap_40_50': 1,
            'ap_50_70': 1,
        },
        {
            'name': 'PzKPfw II 3.7cm',
            'nation': 'german',
            'caliber_mm': 37,
            'he_dice': 1,
            'he_target': '5+',
            'ap_0_10': 3,
            'ap_10_20': 2,
            'ap_20_30': 2,
            'ap_30_40': 1,
            'ap_40_50': 1,
            'ap_50_70': 1,
        },
        {
            'name': 'PzKPfw IV 7.5cm',
            'nation': 'german',
            'caliber_mm': 75,
            'he_dice': 2,
            'he_target': '4+',
            'ap_0_10': 4,
            'ap_10_20': 3,
            'ap_20_30': 2,
            'ap_30_40': 2,
            'ap_40_50': 1,
            'ap_50_70': 1,
        },
        # MEDIUM GUNS
        {
            'name': '88mm FlaK18',
            'nation': 'german',
            'caliber_mm': 88,
            'he_dice': 3,
            'he_target': '4+',
            'ap_0_10': 7,
            'ap_10_20': 7,
            'ap_20_30': 6,
            'ap_30_40': 6,
            'ap_40_50': 5,
            'ap_50_70': 5,
        },
        {
            'name': '88mm FlaK36/37',
            'nation': 'german',
            'caliber_mm': 88,
            'he_dice': 3,
            'he_target': '4+',
            'ap_0_10': 7,
            'ap_10_20': 7,
            'ap_20_30': 6,
            'ap_30_40': 6,
            'ap_40_50': 5,
            'ap_50_70': 5,
        },
        {
            'name': '88mm FlaK41',
            'nation': 'german',
            'caliber_mm': 88,
            'he_dice': 3,
            'he_target': '4+',
            'ap_0_10': 8,
            'ap_10_20': 8,
            'ap_20_30': 7,
            'ap_30_40': 7,
            'ap_40_50': 6,
            'ap_50_70': 6,
        },
        {
            'name': '88mm PaK43',
            'nation': 'german',
            'caliber_mm': 88,
            'he_dice': 3,
            'he_target': '4+',
            'ap_0_10': 9,
            'ap_10_20': 8,
            'ap_20_30': 8,
            'ap_30_40': 7,
            'ap_40_50': 7,
            'ap_50_70': 6,
        },
        {
            'name': '88mm PaK43/41',
            'nation': 'german',
            'caliber_mm': 88,
            'he_dice': 3,
            'he_target': '4+',
            'ap_0_10': 9,
            'ap_10_20': 8,
            'ap_20_30': 8,
            'ap_30_40': 7,
            'ap_40_50': 7,
            'ap_50_70': 6,
        }
    ]

    for gun in guns:
        try:
            cursor.execute('''
            INSERT INTO BG_Reference_Guns (
                name, nation, caliber_mm, he_dice, he_target,
                ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                source_document, screenshot_file,
                extraction_method, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gun['name'],
                gun['nation'],
                gun.get('caliber_mm'),
                gun.get('he_dice'),
                gun.get('he_target'),
                gun.get('ap_0_10'),
                gun.get('ap_10_20'),
                gun.get('ap_20_30'),
                gun.get('ap_30_40'),
                gun.get('ap_40_50'),
                gun.get('ap_50_70'),
                'Battlegroup-Canadas-Crucible',
                SCREENSHOT_FILE,
                'manual_screenshot',
                'claude'
            ))
            print(f"  [OK] Inserted: {gun['name']}")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {gun['name']}: {e}")

    conn.commit()

    # Verification
    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print()

    cursor.execute('''
    SELECT COUNT(*) FROM BG_Reference_Guns
    WHERE nation = 'german'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total German guns in database: {count}')

    cursor.execute('''
    SELECT name, caliber_mm, he_dice, he_target, ap_0_10, ap_50_70
    FROM BG_Reference_Guns
    WHERE screenshot_file = ?
    ORDER BY caliber_mm, name
    ''', (SCREENSHOT_FILE,))

    print()
    print('Guns from this screenshot:')
    for row in cursor.fetchall():
        name, caliber, he_dice, he_target, ap_close, ap_far = row
        ap_close_str = str(ap_close) if ap_close else 'N/A'
        ap_far_str = str(ap_far) if ap_far else 'N/A'
        print(f'  {name}: {caliber}mm, HE {he_dice}D{he_target}, AP {ap_close_str}-{ap_far_str}')

    conn.close()

if __name__ == "__main__":
    main()
