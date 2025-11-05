#!/usr/bin/env python3
"""
Extract German Division 2 units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Division2.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Division 2 units...')
    print()

    units = [
        {
            'unit_name': 'Armoured Panzer Grenadier Platoon',
            'category': 'Infantry Units',
            'unit_composition': 'Platoon composition with support options',
            'men_count': None,
            'points_cost': 153,
            'br_rating': '11+4 BR',
            'transport': 'SdKfz 251 Half-tracks',
            'special_rules': 'Up to 4 Platoon Support Options',
            'optional_upgrades': 'Add up to 4 Panzerschrecks (+75 pts total), Upgrade SdKfz 251/10 (+6 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Panzer Grenadier Platoon',
            'category': 'Infantry Units',
            'unit_composition': 'Infantry platoon with support options',
            'men_count': None,
            'points_cost': 121,
            'br_rating': '11+4 BR',
            'transport': None,
            'special_rules': 'Up to 4 Platoon Support Options',
            'optional_upgrades': 'Add up to 4 Panzerschrecks (+75 pts total)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Medium Mortar team',
            'category': 'Infantry Units',
            'unit_composition': '80mm mortar with crew',
            'men_count': None,
            'points_cost': 24,
            'br_rating': '1+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Replace with SdKfz 251/2 (+9 pts), Include 3 man loader crew (+10 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Light Mortar Team',
            'category': 'Infantry Units',
            'unit_composition': 'Light mortar with crew',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
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
            'unit_name': 'Anti-tank Gun',
            'category': 'Infantry Units',
            'unit_composition': '75mm Pak gun with crew',
            'men_count': None,
            'points_cost': 34,
            'br_rating': '2+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Include 3 man loader team (+10 pts), Medium Truck tow (+4 pts), SdKfz 11 tow (+9 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Heavy Machine Gun team',
            'category': 'Infantry Units',
            'unit_composition': '3 men with tripod MG34',
            'men_count': 3,
            'points_cost': 24,
            'br_rating': '1+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Replace MG34 with tripod MG42 (+2 pts), Include 3 man loader team (+10 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Panzerschreck team',
            'category': 'Infantry Units',
            'unit_composition': '2 men with Panzerschreck',
            'men_count': 2,
            'points_cost': 24,
            'br_rating': '1+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Add up to 2 Panzerschrecks (+75 pts total), Upgrade SdKfz 251/10 (+6 pts), SdKfz 251 with Signal MG34 (+4 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Self Propelled Infantry Gun',
            'category': 'Infantry Units',
            'unit_composition': 'SPG with gun',
            'men_count': None,
            'points_cost': None,
            'br_rating': '1+1 BR',
            'transport': 'Self-propelled',
            'special_rules': None,
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Towed Anti-Aircraft gun',
            'category': 'Infantry Units',
            'unit_composition': 'AA gun with crew',
            'men_count': None,
            'points_cost': 18,
            'br_rating': '2+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Include 3 man loader team (+10 pts), Medium Truck tow (+4 pts), SdKfz 11 Medium tow (+9 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Combat Medic',
            'category': 'Infantry Units',
            'unit_composition': '1 man',
            'men_count': 1,
            'points_cost': 8,
            'br_rating': '0+1 BR',
            'transport': None,
            'special_rules': 'Medic',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Panzer Grenadier Squad',
            'category': 'Infantry Units',
            'unit_composition': '1 Panzer Grenadier Squad',
            'men_count': None,
            'points_cost': 21,
            'br_rating': '2+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Add up to 3 SdKfz 251 half-tracks (+33 pts total), Upgrade squad to a squad MG34 (+4 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Panzer Support Squad',
            'category': 'Infantry Units',
            'unit_composition': 'Support squad',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': None,
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
