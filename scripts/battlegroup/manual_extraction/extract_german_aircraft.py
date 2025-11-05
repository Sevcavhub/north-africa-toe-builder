#!/usr/bin/env python3
"""
Extract German Aircraft from Canada's Crucible supplement
Populates BG_Reference_Aircraft table for reverse engineering formulas
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/German Aircraft.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting German Aircraft...')
    print()

    aircraft = [
        {
            'aircraft_name': 'Fw-190 G',
            'nation': 'german',
            'role': 'Fighter',
            'hits': 3,
            'weaponry_full': '2 x MG, 8 x small bombs or 1 x large bomb and 4 x small bombs',
            'cannon_count': None,
            'cannon_caliber': None,
            'rockets': None,
            'bombs': '8 x small bombs or 1 x large bomb and 4 x small bombs',
            'machine_guns': '2 x MG',
            'special_notes': None,
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
        {
            'aircraft_name': 'Me Bf109 G',
            'nation': 'german',
            'role': 'Fighter',
            'hits': 3,
            'weaponry_full': '4 x MGs, 1 x 30mm cannon (as 37mm), 2 x small bombs',
            'cannon_count': 1,
            'cannon_caliber': '30mm (as 37mm)',
            'rockets': None,
            'bombs': '2 x small bombs',
            'machine_guns': '4 x MG',
            'special_notes': '30mm cannon counts as 37mm',
            'source_supplement': 'Battlegroup-Canadas-Crucible',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        }
    ]

    for ac in aircraft:
        try:
            cursor.execute('''
            INSERT INTO BG_Reference_Aircraft (
                aircraft_name, nation, role, hits, weaponry_full,
                cannon_count, cannon_caliber, rockets, bombs, machine_guns,
                special_notes, source_supplement, source_image_location,
                extraction_method, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ac['aircraft_name'],
                ac['nation'],
                ac['role'],
                ac['hits'],
                ac['weaponry_full'],
                ac.get('cannon_count'),
                ac.get('cannon_caliber'),
                ac.get('rockets'),
                ac.get('bombs'),
                ac.get('machine_guns'),
                ac.get('special_notes'),
                ac['source_supplement'],
                ac['source_image_location'],
                ac['extraction_method'],
                ac['verified_by']
            ))
            print(f"  [OK] Inserted: {ac['aircraft_name']}")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {ac['aircraft_name']}: {e}")

    conn.commit()

    # Verification
    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print()

    cursor.execute('''
    SELECT COUNT(*) FROM BG_Reference_Aircraft
    WHERE source_supplement = 'Battlegroup-Canadas-Crucible'
    AND nation = 'german'
    ''')
    count = cursor.fetchone()[0]
    print(f'Total German aircraft extracted: {count}')

    cursor.execute('''
    SELECT aircraft_name, role, hits, weaponry_full
    FROM BG_Reference_Aircraft
    WHERE source_supplement = 'Battlegroup-Canadas-Crucible'
    AND nation = 'german'
    ORDER BY aircraft_name
    ''')

    print()
    print('Extracted aircraft:')
    for row in cursor.fetchall():
        name, role, hits, weaponry = row
        print(f'  {name} ({role}): {hits} hits, {weaponry}')

    conn.close()

if __name__ == "__main__":
    main()
