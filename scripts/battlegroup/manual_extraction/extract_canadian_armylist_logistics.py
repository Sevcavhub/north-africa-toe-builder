#!/usr/bin/env python3
"""
Extract Canadian Logistics Support units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Logistics Support.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Logistics Support units...')
    print()

    units = [
        {
            'unit_name': 'Ambulance',
            'category': 'Logistics Support Units',
            'unit_composition': '1 Jeep Ambulance',
            'men_count': None,
            'points_cost': 14,
            'br_rating': '2+1 BR (Restricted)',
            'transport': 'Jeep Ambulance',
            'special_rules': 'Medic',
            'optional_upgrades': 'Upgrade Jeep Ambulance to: Ambulance Medium Truck (+2 pts)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Forward Aid Post',
            'category': 'Logistics Support Units',
            'unit_composition': '4 men with a tent',
            'men_count': 4,
            'points_cost': 20,
            'br_rating': '5+1 BR (Restricted)',
            'transport': 'None',
            'special_rules': 'Unique',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Supply Column',
            'category': 'Logistics Support Units',
            'unit_composition': '1 Medium Truck',
            'men_count': None,
            'points_cost': 8,
            'br_rating': '1+1 BR',
            'transport': 'Medium Truck',
            'special_rules': 'Resupply, Unique',
            'optional_upgrades': 'Add up to 2 Medium Trucks (+4 pts each)',
            'nation': 'canadian',
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
            'transport': 'None',
            'special_rules': 'Medic',
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
                unit['points_cost'],
                unit['br_rating'],
                unit['transport'],
                unit['special_rules'],
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
    ORDER BY unit_name
    ''', (SCREENSHOT_FILE,))

    print()
    print('Units from this screenshot:')
    for row in cursor.fetchall():
        name, category, points, br = row
        print(f'  {name} ({category}): {points} pts, {br}')

    conn.close()

if __name__ == "__main__":
    main()
