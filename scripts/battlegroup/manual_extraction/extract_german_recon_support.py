#!/usr/bin/env python3
"""
Extract German Reconnaissance Support Units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Recon Support.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Reconnaissance Support Units...')
    print()

    units = [
        {
            'unit_name': 'Sniper',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 man',
            'men_count': 1,
            'points_cost': 10,
            'br_rating': '1+0 BR',
            'transport': None,
            'special_rules': 'Sniper Scout',
            'optional_upgrades': 'Add a spotter (+5 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Armoured Panzer Grenadier Patrol',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '4 men with bipod MG34s',
            'men_count': 4,
            'points_cost': 36,
            'br_rating': '3+0 BR',
            'transport': 'SdKfz 250/1',
            'special_rules': 'Scout, Mortar Spotter',
            'optional_upgrades': 'Add a Panzerfaust (+5 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Motorised Reconnaissance Patrol',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 18,
            'br_rating': '1+0 BR',
            'transport': 'Schwimmwagen',
            'special_rules': 'Scout, Mortar Spotter',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Recon Platoon Command',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 36,
            'br_rating': '2+0 BR',
            'transport': 'SdKfz 250/10',
            'special_rules': 'Officer, Scout, Artillery Spotter, Unique',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Panzer Grenadier Foot Patrol',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '5 Panzer Grenadier squad and 1 MG Team',
            'men_count': None,
            'points_cost': 36,
            'br_rating': '3+0 BR',
            'transport': None,
            'special_rules': 'Scout, Mortar Spotter',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Panzer Grenadier Squad (Recon)',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '5 men',
            'men_count': 5,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'May take up to 2 Panzerfausts (+5 pts each)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'MG Team (Recon)',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '3 men with bipod MG34',
            'men_count': 3,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Upgrade any MG34 for bipod MG42 (+4 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        # Armoured Car variants
        {
            'unit_name': 'Armoured Car - SdKfz 222',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 Armoured Car',
            'men_count': None,
            'points_cost': 20,
            'br_rating': '1+0 BR',
            'transport': 'Armoured Car',
            'special_rules': 'Scout, Mortar Spotter',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Armoured Car - SdKfz 231/6 Rad',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 Armoured Car',
            'men_count': None,
            'points_cost': 22,
            'br_rating': '1+0 BR',
            'transport': 'Armoured Car',
            'special_rules': 'Scout, Mortar Spotter',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Armoured Car - SdKfz 234/2 Puma',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 Armoured Car',
            'men_count': None,
            'points_cost': 28,
            'br_rating': '1+0 BR',
            'transport': 'Armoured Car',
            'special_rules': 'Scout, Mortar Spotter',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Armoured Car - SdKfz 250/9',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 Armoured Car',
            'men_count': None,
            'points_cost': 24,
            'br_rating': '1+0 BR (Restricted)',
            'transport': 'Armoured Car',
            'special_rules': 'Scout, Mortar Spotter',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Armoured Car - SdKfz 250/1',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 Armoured Car',
            'men_count': None,
            'points_cost': 22,
            'br_rating': '1+0 BR (Restricted)',
            'transport': 'Armoured Car',
            'special_rules': 'Scout, Mortar Spotter',
            'optional_upgrades': None,
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
    ORDER BY unit_name
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
