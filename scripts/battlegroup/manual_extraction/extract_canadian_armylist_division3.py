#!/usr/bin/env python3
"""
Extract Canadian Infantry Division 3 units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Infantry Division3.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Infantry Division 3 units...')
    print()

    units = [
        {
            'unit_name': 'Infantry Platoon',
            'category': 'Infantry Units',
            'unit_composition': '3 Rifle Sections, 1 Platoon Command Section, 4 Light Mortar Teams and up to 4 Platoon Support Options',
            'men_count': None,
            'points_cost': 94,
            'br_rating': '11+3 BR',
            'transport': None,
            'special_rules': 'Can only choose 4 Support units',
            'optional_upgrades': 'Up to 4 Platoon Support Options',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Platoon Command Section',
            'category': 'Infantry Units',
            'unit_composition': '5 men',
            'men_count': 5,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Section may include a PIAT (+5 pts), Includes 1 2" Mortar Team',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': '3 Rifle Sections',
            'category': 'Infantry Units',
            'unit_composition': '3 teams with a rifle',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': 'Bren Team',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Light Mortar Team',
            'category': 'Infantry Units',
            'unit_composition': '2 man with mortar',
            'men_count': 2,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': None,
            'optional_upgrades': None,
            'nation': 'canadian',
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
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Rifle Section',
            'category': 'Infantry Units',
            'unit_composition': '1 Rifle Section',
            'men_count': None,
            'points_cost': 21,
            'br_rating': '2+1 BR',
            'transport': None,
            'special_rules': 'Bren Team',
            'optional_upgrades': 'Section may include a Bren',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Heavy Machine Gun team',
            'category': 'Infantry Units',
            'unit_composition': '3 men with a Vickers HMG',
            'men_count': 3,
            'points_cost': 22,
            'br_rating': '1+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Includes 3 man loader team (+10 pts), Include a Bren Carrier (+8 pts)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'PIAT team',
            'category': 'Infantry Units',
            'unit_composition': '2 men (PIAT)',
            'men_count': 2,
            'points_cost': 14,
            'br_rating': '1+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Medium Mortar team',
            'category': 'Infantry Units',
            'unit_composition': '3" mortar with crew',
            'men_count': None,
            'points_cost': 24,
            'br_rating': '1+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Includes a 3 man loader team (+10 pts), Include a Bren Carrier (+8 pts)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Anti-tank Gun',
            'category': 'Infantry Units',
            'unit_composition': '6 pdr gun with 3 crew',
            'men_count': 3,
            'points_cost': 34,
            'br_rating': '2+1 BR',
            'transport': None,
            'special_rules': None,
            'optional_upgrades': 'Includes a 3 man loader team (+10 pts), Royal Carrier tow (+5 pts)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Carrier Section',
            'category': 'Infantry Units',
            'unit_composition': '1 Carrier Rifle Team, 3 Carrier Light Mortar Teams, 1 Carrier PIAT Team, mounted in Bren Carriers',
            'men_count': None,
            'points_cost': 51,
            'br_rating': '0+3 BR (Restricted)',
            'transport': 'Bren Carriers',
            'special_rules': '1 Carrier Platoon Command (a Support unit)',
            'optional_upgrades': None,
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
