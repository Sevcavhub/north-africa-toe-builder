#!/usr/bin/env python3
"""
Extract German Engineer-Logistics-Specialist Support units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Engineer-Logistics_Specialist Support.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Engineer-Logistics-Specialist Support units...')
    print()

    units = [
        # Engineer Support Units
        {
            'unit_name': 'Assault Pioneer Squad',
            'category': 'Engineer Support Units',
            'unit_composition': '8 men with MG, Panzerfaust and 2 Demolition charges',
            'men_count': 8,
            'points_cost': 38,
            'br_rating': '3+1 BR',
            'transport': None,
            'special_rules': 'Engineers, Assault',
            'optional_upgrades': 'Squad may take 1 flamethrower (+24 pts), Upgrade SdKfz 251 (+0 pts), Upgrade Maultier Truck (+4 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Recovery Vehicle',
            'category': 'Engineer Support Units',
            'unit_composition': '1 Recovery Vehicle',
            'men_count': None,
            'points_cost': 34,
            'br_rating': '3+1 BR',
            'transport': 'Recovery Vehicle',
            'special_rules': 'Vehicle Recovery, Unique',
            'optional_upgrades': 'Bergepanther (+8 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Armoured Engineer Vehicle',
            'category': 'Engineer Support Units',
            'unit_composition': '1 unit with a Flegel SdKfz 251 Armoured Engineer Vehicle',
            'men_count': None,
            'points_cost': 80,
            'br_rating': '2+0 BR',
            'transport': 'Armoured Engineer Vehicle',
            'special_rules': 'Unique',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        # Logistics Units
        {
            'unit_name': 'Supply Column',
            'category': 'Logistics Support Units',
            'unit_composition': '1 Medium Truck',
            'men_count': None,
            'points_cost': 8,
            'br_rating': '1+1 BR',
            'transport': 'Medium Truck',
            'special_rules': 'Resupply, Unique',
            'optional_upgrades': 'Add up to 2 Medium Trucks (+8 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Stretcher Party',
            'category': 'Logistics Support Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 10,
            'br_rating': '1+1 BR',
            'transport': None,
            'special_rules': 'Medic',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        # Recce Units
        {
            'unit_name': 'Armoured Car Patrol',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 Armoured Car with additional options',
            'men_count': None,
            'points_cost': 34,
            'br_rating': '2+1 BR',
            'transport': 'Armoured Car',
            'special_rules': 'Restricted, Recce',
            'optional_upgrades': 'Upgrade SdKfz 251, 2 Armoured cars',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Armoured Recce Patrol',
            'category': 'Reconnaissance Support Units',
            'unit_composition': '1 unit with 1 Armoured Car',
            'men_count': None,
            'points_cost': 38,
            'br_rating': '2+1 BR',
            'transport': 'Armoured Car',
            'special_rules': 'Restricted, Recce',
            'optional_upgrades': 'Add 1 SdKfz 250 (+9 pts), SdKfz 251, 3 Armoured cars (+4 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        # Specialist Support Units
        {
            'unit_name': 'Light Anti-tank Vehicle',
            'category': 'Specialist Support Units',
            'unit_composition': 'Vehicle with AT gun',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': 'Vehicle',
            'special_rules': 'Restricted',
            'optional_upgrades': 'SdKfz 6 with 37mm AT gun (30 pts, 1+1 BR), SdKfz 6 with 50mm gun (39 pts, 2+1 BR)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Assault Gun',
            'category': 'Specialist Support Units',
            'unit_composition': '1 Assault Gun',
            'men_count': None,
            'points_cost': 38,
            'br_rating': '3+1 BR',
            'transport': 'Assault Gun',
            'special_rules': None,
            'optional_upgrades': 'Add 1 main loader team (+10 pts), SdKfz 7 tow (+8 pts)',
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Heavy AA Gun',
            'category': 'Specialist Support Units',
            'unit_composition': '88mm Flak gun',
            'men_count': None,
            'points_cost': 34,
            'br_rating': '2+1 BR',
            'transport': None,
            'special_rules': 'Restricted',
            'optional_upgrades': None,
            'nation': 'german',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Quad AA',
            'category': 'Specialist Support Units',
            'unit_composition': 'Quad AA vehicle',
            'men_count': None,
            'points_cost': None,
            'br_rating': None,
            'transport': 'Vehicle',
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
