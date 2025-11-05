#!/usr/bin/env python3
"""
Extract German Defences from Canada's Crucible supplement
Appends to BG_Reference_Defences table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Defences.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Defences...')
    print()

    defences = [
        {
            'name': 'Improvised Barricades',
            'description': "10' of improvised barricades made of earth-filled boxes, rubble, furniture, destroyed vehicles etc. Counts as hard cover for infantry behind it.",
            'points_cost': 5,
            'br_rating': 0,
            'nation': 'german',
            'special_rules': None,
            'terrain_type': 'Barricade',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Machine Gun Dug-out',
            'description': '3 men and a tripod MG34 in reinforced cover. The cover is lost if the MG moves.',
            'points_cost': 32,
            'br_rating': 1,
            'nation': 'german',
            'special_rules': None,
            'terrain_type': 'Dug-out',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Mortar Pit',
            'description': '3 men and an 80mm mortar in reinforced cover. The cover is lost if the mortar team moves.',
            'points_cost': 32,
            'br_rating': 1,
            'nation': 'german',
            'special_rules': None,
            'terrain_type': 'Dug-out',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Fortified Building',
            'description': 'A chosen building or ruin on the table counts as reinforced cover rather than hard cover.',
            'points_cost': 30,
            'br_rating': 0,
            'nation': 'german',
            'special_rules': None,
            'terrain_type': 'Building',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Foxholes',
            'description': 'Deploy up to 10 infantry in foxholes; they count as in reinforced cover until they move.',
            'points_cost': 10,
            'br_rating': 0,
            'nation': 'german',
            'special_rules': None,
            'terrain_type': 'Foxholes',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Sniper Hideout',
            'description': 'A single sniper in reinforced cover. It can be placed anywhere outside of the opponent\'s deployment zone. The cover is lost if the sniper moves.',
            'points_cost': 15,
            'br_rating': 0,
            'nation': 'german',
            'special_rules': 'Restricted',
            'terrain_type': 'Hideout',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'AT Gun Dug-out',
            'description': 'Reinforced cover for a single anti-tank gun and crew until the gun moves. The gun must be purchased separately from the army list.',
            'points_cost': 20,
            'br_rating': 0,
            'nation': 'german',
            'special_rules': 'Restricted, Gun cost additional',
            'terrain_type': 'Dug-out',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Booby-Trapped Building',
            'description': 'Any chosen building on the table has been wired with booby-traps. The first time an enemy unit enters the building roll 2D6. On a 2-4 detonate. 5+ it detonates and the unit takes a 3/3+ HE hit. On a 1, there is a fault and the booby-trap fails to go off!',
            'points_cost': 25,
            'br_rating': 0,
            'nation': 'german',
            'special_rules': None,
            'terrain_type': 'Building',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'name': 'Improvised Road Block',
            'description': 'Something large and heavy across a road. Place on any road or track, anywhere on the table. It counts as an obstacle.',
            'points_cost': 5,
            'br_rating': 0,
            'nation': 'german',
            'special_rules': None,
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
                name, description, points_cost, br_rating,
                nation, special_rules, terrain_type,
                source_supplement, source_image_location,
                extraction_method, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                defence['name'],
                defence['description'],
                defence['points_cost'],
                defence['br_rating'],
                defence['nation'],
                defence.get('special_rules'),
                defence['terrain_type'],
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
    WHERE nation = 'german'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total German defences in database: {count}')

    cursor.execute('''
    SELECT name, terrain_type, points_cost, br_rating
    FROM BG_Reference_Defences
    WHERE source_image_location = ?
    ORDER BY name
    ''', (SCREENSHOT_FILE,))

    print()
    print('Defences from this screenshot:')
    for row in cursor.fetchall():
        name, terrain, points, br = row
        print(f'  {name} ({terrain}): {points} pts, {br} BR')

    conn.close()

if __name__ == "__main__":
    main()
