#!/usr/bin/env python3
"""
Extract Sample Maps from Canada's Crucible supplement
Appends to BG_Sample_maps table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
IMAGE_DIR = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Sample Maps...')
    print()

    maps = [
        {
            'map_name': 'Black Sabbath 1st Hussars Attack',
            'image_location': IMAGE_DIR + 'Black Sabath 1st Hussars Map.png',
            'scenario_title': 'Black Sabbath - 1st Hussar\'s Attack',
            'scenario_size': 'Company'
        },
        {
            'map_name': 'First Assault on Norrey',
            'image_location': IMAGE_DIR + 'First Assualt on Norrey Map.png',
            'scenario_title': 'First Assault on Norrey',
            'scenario_size': None
        },
        {
            'map_name': 'Surrounded at La Ferme',
            'image_location': IMAGE_DIR + 'SURROUNDED AT La Ferme Map.png',
            'scenario_title': 'Surrounded at La Ferme',
            'scenario_size': None
        }
    ]

    for map_record in maps:
        try:
            cursor.execute('''
            INSERT INTO BG_Sample_maps (
                map_name, image_location, scenario_title, scenario_size
            ) VALUES (?, ?, ?, ?)
            ''', (
                map_record['map_name'],
                map_record['image_location'],
                map_record.get('scenario_title'),
                map_record.get('scenario_size')
            ))
            print(f"  [OK] Inserted: {map_record['map_name']}")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {map_record['map_name']}: {e}")

    conn.commit()

    # Verification
    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print()

    cursor.execute('SELECT COUNT(*) FROM BG_Sample_maps')
    count = cursor.fetchone()[0]
    print(f'Total sample maps in database: {count}')

    cursor.execute('''
    SELECT map_name, scenario_title, scenario_size
    FROM BG_Sample_maps
    ORDER BY map_name
    ''')

    print()
    print('All sample maps:')
    for row in cursor.fetchall():
        name, title, size = row
        size_str = f' ({size})' if size else ''
        print(f'  {name}{size_str}: {title}')

    conn.close()

if __name__ == "__main__":
    main()
