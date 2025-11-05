#!/usr/bin/env python3
"""
Extract Canadian Specialist Support and Additional Fire Support units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Specialist Support and Additional Fire Support.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Specialist Support and Additional Fire Support units...')
    print()

    units = [
        # Specialist Support Units
        {
            'unit_name': 'Heavy Anti-Tank Gun',
            'category': 'Specialist Support Units',
            'unit_composition': '1 light anti-tank gun with crew',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': 'None',
            'special_rules': None,
            'optional_upgrades': 'Replace with specific guns, Medium Truck/tow, +4 pts, +5 pts',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Heavy Anti-Tank Gun (with crew)',
            'category': 'Specialist Support Units',
            'unit_composition': '1 anti-tank gun with crew',
            'men_count': None,
            'points_cost': None,
            'br_rating': '1+1 BR',
            'transport': 'None',
            'special_rules': None,
            'optional_upgrades': 'Replace Medium Truck/tow, +4 pts, Dog tow, +2 pts',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        # Additional Fire Support
        {
            'unit_name': 'Canadian Battery Fire Mission',
            'category': 'Additional Fire Support',
            'unit_composition': 'Fire mission',
            'men_count': None,
            'points_cost': 10,
            'br_rating': '0 BR',
            'transport': 'None',
            'special_rules': None,
            'optional_upgrades': None,
            'nation': 'canadian',
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
            'points_cost': None,
            'br_rating': None,
            'transport': 'None',
            'special_rules': 'Free to a higher rank officer, 5 pts otherwise',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Canadian Fire Mission Request',
            'category': 'Additional Fire Support',
            'unit_composition': 'Fire mission levels 1-6',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': 'None',
            'special_rules': 'Multiple levels: 1-6 with varying mortars, 3-4 with 4.2" mortar, 5-6 with multiple guns',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Timed Invasion Barrage',
            'category': 'Additional Fire Support',
            'unit_composition': 'Barrage',
            'men_count': None,
            'points_cost': 15,
            'br_rating': '0 BR',
            'transport': 'None',
            'special_rules': 'Fires for a higher rank officer on a turn selected by the player, 15 pts per target point of selected pre-registered target or target point of the barrage',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Timed Projectile, no Scatter',
            'category': 'Additional Fire Support',
            'unit_composition': 'Projectile',
            'men_count': None,
            'points_cost': 10,
            'br_rating': '0 BR',
            'transport': 'None',
            'special_rules': 'Can either be a higher rank officer, use their points and calculate a pre-registered target or target point marked on the forces, will not scatter. A higher rank only, you will end the call request',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Forward Air Support Table (top)',
            'category': 'Additional Fire Support',
            'unit_composition': 'Air support levels 1-6',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': 'None',
            'special_rules': 'D6 levels: 1=Absent, 2-3=Typhoon, 4-5=2x Typhoon, 6=Choose',
            'optional_upgrades': 'Select from above aircraft',
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
