#!/usr/bin/env python3
"""
Extract German Additional Fire Support units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Additinal Fire Support.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Additional Fire Support units...')
    print()

    units = [
        {
            'unit_name': 'Off-Table Artillery Support Request',
            'category': 'Additional Fire Support',
            'unit_composition': 'Artillery support with priority levels',
            'men_count': None,
            'points_cost': None,
            'br_rating': '0 BR',
            'transport': None,
            'special_rules': '1st Target Priority (5 pts), 2nd Target Priority (A+) (10 pts), 3rd Target Priority (A++) (20 pts)',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'German Army Fire Mission Request - Regimental Battery',
            'category': 'Additional Fire Support',
            'unit_composition': 'Fire mission levels 1-6',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': 'D6 levels: 1-2=2 x 80mm mortar, 3-4=2 x 105mm howitzer, 5-6=2 x 150mm howitzer',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'German Army Fire Mission Request - Divisional Battery',
            'category': 'Additional Fire Support',
            'unit_composition': 'Fire mission levels 1-6',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': 'D6 levels: 1-2=3 x 105mm (12) howitzer, 3-4=3 x 150mm (15) cannon, 5-6=2 x 150mm (15) howitzer',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'German Close Air Support Table 1944',
            'category': 'Additional Fire Support',
            'unit_composition': 'Air support levels 1-6',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': None,
            'special_rules': 'D6 levels: 1-3=Me Bf109 G, 4-5=Fw-190 G, 6=Choose. Select any aircraft from lower dice score. May charge choice as an aircraft from a higher roll',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Pre-Registered Target Point',
            'category': 'Additional Fire Support',
            'unit_composition': 'Target point',
            'men_count': None,
            'points_cost': 15,
            'br_rating': '0 BR',
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
            'unit_name': 'Counter-Battery Fire Mission',
            'category': 'Additional Fire Support',
            'unit_composition': 'Fire mission',
            'men_count': None,
            'points_cost': 10,
            'br_rating': '0 BR',
            'transport': None,
            'special_rules': 'Fire counter-battery mission at battery or 3+ save',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Timed 80mm Mortar Barrage',
            'category': 'Additional Fire Support',
            'unit_composition': 'Barrage',
            'men_count': None,
            'points_cost': 5,
            'br_rating': '0 BR',
            'transport': None,
            'special_rules': 'Fired by a battery of four 80mm mortars. Before the game, write down which turn the guns will fire on. The points cost includes a pre-registered target at the target point of the barrage',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Timed 105mm Barrage',
            'category': 'Additional Fire Support',
            'unit_composition': 'Barrage',
            'men_count': None,
            'points_cost': 10,
            'br_rating': '0 BR',
            'transport': None,
            'special_rules': 'Fired by a battery of four 105mm(12) howitzers. Before the game, write down which turn the guns will fire on. The points cost includes a pre-registered target at the target point of the barrage',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Timed 150mm Barrage',
            'category': 'Additional Fire Support',
            'unit_composition': 'Barrage',
            'men_count': None,
            'points_cost': 20,
            'br_rating': '0 BR',
            'transport': None,
            'special_rules': 'Fired by a battery of four 150mm(20) howitzers. Before the game, write down which turn the guns will fire on. The points cost includes a pre-registered target at the target point of the barrage',
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
