#!/usr/bin/env python3
"""
Extract Canadian Infantry Division 2 units from Canada's Crucible supplement
Appends to BG_Reference_ArmyList_Examples table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Infantry Division2.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Infantry Division 2 units...')
    print()

    units = [
        {
            'unit_name': 'Motorcycle Dispatch Rider',
            'category': 'Forward Headquarters Units',
            'unit_composition': '1 man',
            'men_count': 1,
            'points_cost': 12,
            'br_rating': '0+1 BR',
            'transport': 'Motorcycle',
            'special_rules': 'Dispatches',
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
    cursor.execute('''
    SELECT COUNT(*) FROM BG_Reference_ArmyList_Examples
    WHERE source_supplement = 'Battlegroup-Canadas-Crucible'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total Canadian army list units: {count}')

    conn.close()

if __name__ == "__main__":
    main()
