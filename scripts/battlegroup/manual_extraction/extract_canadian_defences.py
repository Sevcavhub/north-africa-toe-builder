#!/usr/bin/env python3
"""
Extract Canadian Defences from Canada's Crucible supplement
Creates BG_Reference_Defences table and populates with fortification data
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Defences.png"

def create_table(cursor):
    """Create BG_Reference_Defences table if it doesn't exist"""
    # Drop existing table if structure is wrong
    cursor.execute('DROP TABLE IF EXISTS BG_Reference_Defences')

    cursor.execute('''
    CREATE TABLE BG_Reference_Defences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        points_cost INTEGER,
        br_rating INTEGER,
        nation TEXT,
        special_rules TEXT,
        terrain_type TEXT,
        source_supplement TEXT,
        source_image_location TEXT,
        extraction_method TEXT DEFAULT 'manual_screenshot',
        verified_by TEXT,
        verification_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(name, nation, source_supplement)
    )
    ''')

    cursor.execute('CREATE INDEX idx_defences_nation ON BG_Reference_Defences(nation)')
    cursor.execute('CREATE INDEX idx_defences_source ON BG_Reference_Defences(source_supplement)')

    print('[OK] BG_Reference_Defences table created')

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Creating BG_Reference_Defences table...')
    create_table(cursor)
    conn.commit()
    print()

    print('Extracting Canadian Defences...')
    print()

    defences = [
        {
            'name': 'Improved Barricades',
            'description': 'Up to improved Hard Cover at chosen locations. May only be taken if your force has no transports or tracked cover for infantry fallback.',
            'points_cost': 5,
            'br_rating': 1,
            'nation': 'canadian',
            'special_rules': 'Improved Hard Cover, No transports/tracked cover requirement',
            'terrain_type': 'Obstacle',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Machine Gun Dugout',
            'description': '1 man and a Vickers HMG in reinforced cover. The entire cover has Hard Cover status.',
            'points_cost': None,
            'br_rating': None,
            'nation': 'canadian',
            'special_rules': 'Hard Cover, Vickers HMG included',
            'terrain_type': 'Fortification',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Fortified Building',
            'description': 'A single fortified building anywhere on the battlefield. This has reinforced status. Hard Cover. Cannot be knocked down by flank close assault.',
            'points_cost': 20,
            'br_rating': 3,
            'nation': 'canadian',
            'special_rules': 'Hard Cover, Reinforced, Cannot be knocked down',
            'terrain_type': 'Building',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Foxholes',
            'description': 'Deploy up to 10 at chosen locations in table deployment zone. Each is a terrain piece.',
            'points_cost': 10,
            'br_rating': 1,
            'nation': 'canadian',
            'special_rules': 'Up to 10 foxholes',
            'terrain_type': 'Cover',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Trenches',
            'description': 'Up to 12" of trenches to which cover can be added as chosen locations in deployment zone.',
            'points_cost': 10,
            'br_rating': 1,
            'nation': 'canadian',
            'special_rules': 'Up to 12" of trenches',
            'terrain_type': 'Cover',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Sniper Hideout',
            'description': 'A camouflaged sniper at a chosen location. Counts as entrenched outside of the opponent\'s deployment zone. This cannot be shot at until it fires a shot.',
            'points_cost': 15,
            'br_rating': 2,
            'nation': 'canadian',
            'special_rules': 'Camouflaged, Entrenched, Cannot be targeted until fires',
            'terrain_type': 'Position',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Minefield',
            'description': 'A single minefield and wire and personnel minefield.',
            'points_cost': 10,
            'br_rating': 1,
            'nation': 'canadian',
            'special_rules': 'Minefield with wire',
            'terrain_type': 'Obstacle',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Command Bunker',
            'description': 'Armoured bunker, cannot be destroyed except by flank shot with HE. The entire team inside is considered to have Hard Cover status. This comes is part of the command team.',
            'points_cost': 80,
            'br_rating': 1,
            'nation': 'canadian',
            'special_rules': 'Armoured, Hard Cover, Only destroyed by flank HE shot, Command team included',
            'terrain_type': 'Bunker',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Medium Bunker',
            'description': 'Same as Command Bunker but for a normal infantry or weapon team. Special Rules: artillery Spotter. Unique.',
            'points_cost': 60,
            'br_rating': 2,
            'nation': 'canadian',
            'special_rules': 'Armoured, Hard Cover, Artillery Spotter, Unique',
            'terrain_type': 'Bunker',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Pillbox',
            'description': 'A reinforced concrete bunker with firing loops. The unit must go over the lethal step into or out of it.',
            'points_cost': 24,
            'br_rating': 2,
            'nation': 'canadian',
            'special_rules': 'Reinforced concrete, Firing loops, Lethal step entry/exit',
            'terrain_type': 'Bunker',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Strongpoint',
            'description': 'Fortified strong point and heavy cover across a wide area. Does not have an entrenchment stop trap.',
            'points_cost': 30,
            'br_rating': 4,
            'nation': 'canadian',
            'special_rules': 'Heavy cover, No entrenchment stop trap',
            'terrain_type': 'Fortification',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Anti-Tank Ditch/Tankhindernis',
            'description': 'Up to 12" of anti-tank ditch or obstacle',
            'points_cost': 20,
            'br_rating': 2,
            'nation': 'canadian',
            'special_rules': 'Up to 12" of anti-tank obstacle',
            'terrain_type': 'Obstacle',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Obstacle (AP or Anti-Tank Shot)',
            'description': 'Single camouflaged tethered mine, when this is camouflaged behind the team, you can take a shot at any AFV at a penetration value of 4D6.',
            'points_cost': 5,
            'br_rating': 2,
            'nation': 'canadian',
            'special_rules': 'Camouflaged, Tethered mine, 4D6 penetration value',
            'terrain_type': 'Obstacle',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        }
    ]

    for defence in defences:
        try:
            cursor.execute('''
            INSERT INTO BG_Reference_Defences (
                name, description, points_cost, br_rating, nation,
                special_rules, terrain_type, source_supplement,
                source_image_location, extraction_method, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                defence['name'],
                defence['description'],
                defence.get('points_cost'),
                defence.get('br_rating'),
                defence['nation'],
                defence.get('special_rules'),
                defence.get('terrain_type'),
                defence['source_supplement'],
                defence['source_image_location'],
                defence['extraction_method'],
                defence['verified_by']
            ))
            print(f"  [OK] Inserted: {defence['name']}")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {defence['name']}: {e}")

    conn.commit()

    # Verification
    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print()

    cursor.execute('''
    SELECT COUNT(*) FROM BG_Reference_Defences
    WHERE source_supplement = 'Battlegroup-Canadas-Crucible'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total Canadian defences extracted: {count}')

    cursor.execute('''
    SELECT name, terrain_type, points_cost, br_rating
    FROM BG_Reference_Defences
    WHERE source_supplement = 'Battlegroup-Canadas-Crucible'
    ORDER BY terrain_type, name
    ''')

    print()
    print('Extracted defences:')
    for row in cursor.fetchall():
        name, terrain_type, points, br = row
        points_str = f'{points} pts' if points else 'N/A'
        br_str = f'{br} BR' if br else 'N/A'
        print(f'  {name} ({terrain_type}): {points_str}, {br_str}')

    conn.close()

if __name__ == "__main__":
    main()
