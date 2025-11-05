#!/usr/bin/env python3
"""
Extract Canadian Tanks and Artillery Units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Tanks and Artillery Units.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Tanks and Artillery Units...')
    print()

    units = [
        # Tank Units
        {
            'unit_name': 'Sherman Tank Troop',
            'category': 'Tank Units',
            'unit_composition': '3 M4A4 Sherman Tanks, 1 M4A4 Sherman (Officer, Mortar Spotter), 3 M4A1 Sherman Tanks',
            'men_count': None,
            'points_cost': 146,
            'br_rating': '8+1 BR',
            'transport': 'Sherman Tanks',
            'special_rules': None,
            'optional_upgrades': 'For 2 tanks you may take 2 Support units',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Additional Tank',
            'category': 'Tank Units',
            'unit_composition': 'M4A1 Sherman or M4A4 Sherman',
            'men_count': None,
            'points_cost': 36,
            'br_rating': '3+1 BR',
            'transport': 'Sherman Tank',
            'special_rules': None,
            'optional_upgrades': 'Add up to 3 Additional Tanks',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Self-Propelled Anti-Tank Gun',
            'category': 'Tank Units',
            'unit_composition': '1 SP Anti-Tank Gun with Weapon',
            'men_count': None,
            'points_cost': None,
            'br_rating': '2+1 BR',
            'transport': 'SP Anti-Tank Gun',
            'special_rules': 'Towed Weapon',
            'optional_upgrades': 'For 2 Tank Platoon you may take 2 Support units',
            'nation': 'canadian',
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
            'points_cost': 30,
            'br_rating': '1+1 BR',
            'transport': 'Jeep',
            'special_rules': 'Artillery Spotter, Senior Officer',
            'optional_upgrades': 'Replace Jeep with Bren Carrier (+4 pts)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Royal Artillery Observer',
            'category': 'Artillery Units',
            'unit_composition': '3 men',
            'men_count': 3,
            'points_cost': 60,
            'br_rating': '3+1 BR',
            'transport': 'None',
            'special_rules': 'Artillery Spotter, Unique',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Heavy Mortar Team',
            'category': 'Artillery Units',
            'unit_composition': '4.2" mortar and crew',
            'men_count': None,
            'points_cost': 20,
            'br_rating': '1+1 BR',
            'transport': 'Bren Carrier',
            'special_rules': 'Includes 1 3 man loader team, Mounted in Bren Carrier',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Off-Table Mortar Fire',
            'category': 'Artillery Units',
            'unit_composition': '1 4.2" mortar',
            'men_count': None,
            'points_cost': 24,
            'br_rating': '0 BR',
            'transport': 'None',
            'special_rules': 'Off-table fire',
            'optional_upgrades': '3 x 4.2" mortars (72 pts, 0 BR)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Off-Table Artillery Fire',
            'category': 'Artillery Units',
            'unit_composition': '1 25pdr',
            'men_count': None,
            'points_cost': 90,
            'br_rating': '0 BR',
            'transport': 'None',
            'special_rules': 'Off-table fire',
            'optional_upgrades': '2 25pdr (90 pts, 0 BR), 3 x 25 pdr (140 pts, 0 BR)',
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
