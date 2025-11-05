#!/usr/bin/env python3
"""
Extract Canadian Guns from Canada's Crucible supplement
Populates bg_reference_guns table for reverse engineering formulas
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE1 = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Guns.png"
SCREENSHOT_FILE2 = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Guns2.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Guns...')
    print()

    # Guns from Canadian Guns.png
    guns = [
        # HE
        {
            'name': '2" Mortar',
            'nation': 'canadian',
            'gun_type': 'HE',
            'caliber_mm': 50,
            'barrel_length': None,
            'he_dice': 10,
            'he_target': '8',
            'ap_0_10': 2,
            'ap_10_20': 1,
            'ap_20_30': 1,
            'ap_30_40': 1,
            'ap_40_50': 1,
            'ap_50_70': 1,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE1
        },
        # Anti-Tank Cannon
        {
            'name': '2 pounder',
            'nation': 'canadian',
            'gun_type': 'Anti-Tank Gun',
            'caliber_mm': 40,
            'barrel_length': None,
            'he_dice': None,
            'he_target': None,
            'ap_0_10': 5,
            'ap_10_20': 4,
            'ap_20_30': 3,
            'ap_30_40': 2,
            'ap_40_50': 1,
            'ap_50_70': 1,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE1
        },
        # Mortars
        {
            'name': '3" Mortar',
            'nation': 'canadian',
            'gun_type': 'Mortar',
            'caliber_mm': 76,
            'barrel_length': None,
            'he_dice': 10,
            'he_target': '5',
            'ap_0_10': None,
            'ap_10_20': None,
            'ap_20_30': None,
            'ap_30_40': None,
            'ap_40_50': None,
            'ap_50_70': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE1
        },
        # Very Light Guns
        {
            'name': '6 pdr',
            'nation': 'canadian',
            'gun_type': 'Very Light Gun',
            'caliber_mm': 57,
            'barrel_length': None,
            'he_dice': None,
            'he_target': 'D6',
            'ap_0_10': 8,
            'ap_10_20': 7,
            'ap_20_30': 6,
            'ap_30_40': 5,
            'ap_40_50': 4,
            'ap_50_70': 3,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE1
        },
        # Light Guns
        {
            'name': '17 pdr',
            'nation': 'canadian',
            'gun_type': 'Light Gun',
            'caliber_mm': 76,
            'barrel_length': None,
            'he_dice': None,
            'he_target': 'D6',
            'ap_0_10': 13,
            'ap_10_20': 12,
            'ap_20_30': 11,
            'ap_30_40': 10,
            'ap_40_50': 9,
            'ap_50_70': 8,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE1
        },
        # Medium Guns
        {
            'name': '25 pdr',
            'nation': 'canadian',
            'gun_type': 'Medium Gun',
            'caliber_mm': 88,
            'barrel_length': None,
            'he_dice': 10,
            'he_target': 'D6',
            'ap_0_10': 6,
            'ap_10_20': 5,
            'ap_20_30': 4,
            'ap_30_40': 3,
            'ap_40_50': 2,
            'ap_50_70': 1,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE1
        },
        # Heavy Guns
        {
            'name': '4.5" gun',
            'nation': 'canadian',
            'gun_type': 'Heavy Gun',
            'caliber_mm': 114,
            'barrel_length': None,
            'he_dice': 15,
            'he_target': None,
            'ap_0_10': None,
            'ap_10_20': None,
            'ap_20_30': None,
            'ap_30_40': None,
            'ap_40_50': None,
            'ap_50_70': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE1
        },
        {
            'name': '5.5" medium gun',
            'nation': 'canadian',
            'gun_type': 'Heavy Gun',
            'caliber_mm': 140,
            'barrel_length': None,
            'he_dice': 20,
            'he_target': None,
            'ap_0_10': None,
            'ap_10_20': None,
            'ap_20_30': None,
            'ap_30_40': None,
            'ap_40_50': None,
            'ap_50_70': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE1
        },
        # Infantry Anti-Tank Weapons
        {
            'name': 'PIAT',
            'nation': 'canadian',
            'gun_type': 'Infantry AT',
            'caliber_mm': 83,
            'barrel_length': None,
            'he_dice': None,
            'he_target': None,
            'ap_0_10': 5,
            'ap_10_20': None,
            'ap_20_30': None,
            'ap_30_40': None,
            'ap_40_50': None,
            'ap_50_70': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE2
        },
        # Aircraft Weapons
        {
            'name': '60lb Rocket',
            'nation': 'canadian',
            'gun_type': 'Aircraft Weapon',
            'caliber_mm': None,
            'barrel_length': None,
            'he_dice': 5,
            'he_target': '4+',
            'ap_0_10': None,
            'ap_10_20': None,
            'ap_20_30': 8,
            'ap_30_40': None,
            'ap_40_50': None,
            'ap_50_70': None,
            'source_file': 'Battlegroup-Canadas-Crucible',
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude',
            'screenshot_file': SCREENSHOT_FILE2
        }
    ]

    for gun in guns:
        try:
            cursor.execute('''
            INSERT INTO bg_reference_guns (
                name, nation, caliber_mm, barrel_length,
                he_dice, he_target,
                ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                notes, source_file, extraction_method, verified_by, screenshot_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gun['name'],
                gun['nation'],
                gun.get('caliber_mm'),
                gun.get('barrel_length'),
                gun.get('he_dice'),
                gun.get('he_target'),
                gun.get('ap_0_10'),
                gun.get('ap_10_20'),
                gun.get('ap_20_30'),
                gun.get('ap_30_40'),
                gun.get('ap_40_50'),
                gun.get('ap_50_70'),
                gun['gun_type'],  # Store gun_type in notes field
                gun['source_file'],
                gun['extraction_method'],
                gun['verified_by'],
                gun['screenshot_file']
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
    SELECT COUNT(*) FROM bg_reference_guns
    WHERE source_file = 'Battlegroup-Canadas-Crucible'
    AND extraction_method = 'manual_screenshot'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total Canadian guns extracted: {count}')

    cursor.execute('''
    SELECT name, notes, caliber_mm, he_dice, he_target
    FROM bg_reference_guns
    WHERE source_file = 'Battlegroup-Canadas-Crucible'
    ORDER BY notes, name
    ''')

    print()
    print('Extracted guns:')
    for row in cursor.fetchall():
        name, gun_type, caliber, he_dice, he_target = row
        caliber_str = f'{caliber}mm' if caliber else 'N/A'
        he_str = f'HE {he_dice}D6' if he_dice else 'No HE'
        if he_target:
            he_str += f' ({he_target})'
        print(f'  {name} ({gun_type}): {caliber_str}, {he_str}')

    conn.close()

if __name__ == "__main__":
    main()
