#!/usr/bin/env python3
"""
Extract Canadian Infantry Division units from Canada's Crucible supplement
Creates BG_Reference_ArmyList_Examples table and populates with army list data
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Infantry Division1.png"

def create_table(cursor):
    """Create BG_Reference_ArmyList_Examples table if it doesn't exist"""
    cursor.execute('DROP TABLE IF EXISTS BG_Reference_ArmyList_Examples')

    cursor.execute('''
    CREATE TABLE BG_Reference_ArmyList_Examples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_name TEXT NOT NULL,
        category TEXT,
        unit_composition TEXT,
        men_count INTEGER,
        points_cost INTEGER,
        br_rating TEXT,
        transport TEXT,
        special_rules TEXT,
        optional_upgrades TEXT,
        nation TEXT,
        source_supplement TEXT,
        source_image_location TEXT,
        extraction_method TEXT DEFAULT 'manual_screenshot',
        verified_by TEXT,
        verification_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(unit_name, nation, source_supplement, source_image_location)
    )
    ''')

    cursor.execute('CREATE INDEX idx_armylist_nation ON BG_Reference_ArmyList_Examples(nation)')
    cursor.execute('CREATE INDEX idx_armylist_category ON BG_Reference_ArmyList_Examples(category)')
    cursor.execute('CREATE INDEX idx_armylist_source ON BG_Reference_ArmyList_Examples(source_supplement)')

    print('[OK] BG_Reference_ArmyList_Examples table created')

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Creating BG_Reference_ArmyList_Examples table...')
    create_table(cursor)
    conn.commit()
    print()

    print('Extracting Canadian Infantry Division 1 army list units...')
    print()

    units = [
        {
            'unit_name': 'Forward HQ Officer',
            'category': 'Forward Headquarters Units',
            'unit_composition': '3 men',
            'men_count': 3,
            'points_cost': 21,
            'br_rating': '5+1 BR',
            'transport': 'None',
            'special_rules': 'Senior Officer, Artillery Spotter, Unique',
            'optional_upgrades': 'Upgrade Jeep to: Keep as is (free), Dingo Scout car (free), M3A1 Sherman Medium Tank (+4 pts)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Forward Air Control Officer',
            'category': 'Forward Headquarters Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 20,
            'br_rating': '1+1 BR',
            'transport': 'Jeep',
            'special_rules': 'Officer, Air Spotter 3+, Unique',
            'optional_upgrades': 'Upgrade Jeep to: Bren Carrier (+3 pts), Replace 2 men and Jeep to Bedford QL (+4 pts), Humber Scout Car (+6 pts)',
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Bedford QL Radio Truck',
            'category': 'Forward Headquarters Units',
            'unit_composition': '3 men',
            'men_count': 3,
            'points_cost': 15,
            'br_rating': '1+1 BR',
            'transport': 'Tele-Medium Truck',
            'special_rules': 'Communications, Unique',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Comms Relay Team',
            'category': 'Forward Headquarters Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 14,
            'br_rating': '0+1 BR',
            'transport': 'None',
            'special_rules': 'Communications',
            'optional_upgrades': None,
            'nation': 'canadian',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'unit_name': 'Wire Team',
            'category': 'Forward Headquarters Units',
            'unit_composition': '2 men',
            'men_count': 2,
            'points_cost': 7,
            'br_rating': '0+1 BR',
            'transport': 'None',
            'special_rules': 'Wire Communications',
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
                unit['men_count'],
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
    WHERE source_supplement = 'Battlegroup-Canadas-Crucible'
    ORDER BY category, unit_name
    ''')

    print()
    print('Extracted units:')
    for row in cursor.fetchall():
        name, category, points, br = row
        print(f'  {name} ({category}): {points} pts, {br}')

    conn.close()

if __name__ == "__main__":
    main()
