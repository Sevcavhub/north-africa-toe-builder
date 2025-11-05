#!/usr/bin/env python3
"""
Extract Canadian Aircraft from Canada's Crucible supplement
Appends to BG_Reference_Aircraft table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Canadian Aircraft.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Canadian Aircraft...')
    print()

    aircraft = [
        {
            'aircraft_name': 'Typhoon',
            'nation': 'canadian',
            'role': 'Fighter Bomber',
            'hits': 4,
            'weaponry_full': '4 20mm cannons, 8 60 lbs rockets, or 2 medium bombs, or 2 large bombs',
            'cannon_count': 4,
            'cannon_caliber': '20mm',
            'machine_guns': None,
            'rockets': '8x 60lb rockets',
            'bombs': '2x medium bombs OR 2x large bombs',
            'special_notes': None,
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'aircraft_name': 'Spitfire',
            'nation': 'canadian',
            'role': 'Fighter',
            'hits': 3,
            'weaponry_full': '2 20mm cannons, 4 .303 cal machine guns',
            'cannon_count': 2,
            'cannon_caliber': '20mm',
            'machine_guns': '4x .303 cal',
            'rockets': None,
            'bombs': None,
            'special_notes': None,
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'aircraft_name': 'Auster III',
            'nation': 'canadian',
            'role': 'Spotter Plane',
            'hits': 2,
            'weaponry_full': None,
            'cannon_count': None,
            'cannon_caliber': None,
            'machine_guns': None,
            'rockets': None,
            'bombs': None,
            'special_notes': None,
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
    ]

    for plane in aircraft:
        try:
            cursor.execute('''
            INSERT INTO BG_Reference_Aircraft (
                aircraft_name, nation, role, hits, weaponry_full,
                cannon_count, cannon_caliber, rockets, bombs, machine_guns,
                special_notes, source_supplement, source_image_location,
                extraction_method, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plane['aircraft_name'],
                plane['nation'],
                plane['role'],
                plane['hits'],
                plane.get('weaponry_full'),
                plane.get('cannon_count'),
                plane.get('cannon_caliber'),
                plane.get('rockets'),
                plane.get('bombs'),
                plane.get('machine_guns'),
                plane.get('special_notes'),
                plane['source_supplement'],
                plane['source_image_location'],
                plane['extraction_method'],
                plane['verified_by']
            ))
            print(f"  [OK] Inserted: {plane['aircraft_name']}")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {plane['aircraft_name']}: {e}")

    conn.commit()

    # Verification
    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print()

    cursor.execute('''
    SELECT COUNT(*) FROM BG_Reference_Aircraft
    WHERE nation = 'canadian'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total Canadian aircraft in database: {count}')

    cursor.execute('''
    SELECT aircraft_name, role, hits, weaponry_full
    FROM BG_Reference_Aircraft
    WHERE screenshot_file = ?
    ORDER BY aircraft_name
    ''', (SCREENSHOT_FILE,))

    print()
    print('Aircraft from this screenshot:')
    for row in cursor.fetchall():
        name, role, hits, weapons = row
        weapons_str = f', {weapons}' if weapons else ', unarmed'
        print(f'  {name} ({role}): {hits} hits{weapons_str}')

    conn.close()

if __name__ == "__main__":
    main()
