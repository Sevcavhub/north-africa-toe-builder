#!/usr/bin/env python3
"""
Add missing guns from Battlegroup-Canadas-Crucible.txt that the scraper missed.

The scraper only extracted 11 guns, but there are 30+ guns in the file.
This script manually adds the missing ones with data from the text file.
"""

import sqlite3
from datetime import datetime

DB_PATH = 'D:/north-africa-toe-builder/database/master_database.db'

# Missing Canadian guns from Crucible text file
canadian_guns = [
    # Mortars (lines 2325-2327)
    {
        'name': '2" Mortar',
        'nation': 'canadian',
        'caliber_mm': 51,  # 2 inches = 51mm
        'he_dice': 3,
        'he_target': '5+',
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    {
        'name': '3" Mortar',
        'nation': 'canadian',
        'caliber_mm': 76,  # 3 inches = 76mm
        'he_dice': 4,
        'he_target': '4+',
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    {
        'name': '4.2" Mortar',
        'nation': 'canadian',
        'caliber_mm': 107,  # 4.2 inches = 107mm
        'he_dice': 6,
        'he_target': '4+',
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    # Autocannons (line 2336)
    {
        'name': '40mmL60 Bofors',
        'nation': 'canadian',
        'caliber_mm': 40,
        'barrel_length': 'L60',
        'he_dice': None,  # Shows "-" for HE dice
        'he_target': None,
        'ap_0_10': 3,
        'ap_10_20': 3,
        'ap_20_30': 2,
        'ap_30_40': 2,
        'ap_40_50': 1,
        'ap_50_70': None,
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    # Very Light Guns (line 2347)
    {
        'name': '6 pdr',
        'nation': 'canadian',
        'caliber_mm': 57,  # 6-pounder = 57mm
        'he_dice': 3,
        'he_target': '5+',
        'ap_0_10': 7,
        'ap_10_20': 7,
        'ap_20_30': 6,
        'ap_30_40': 5,
        'ap_40_50': 4,
        'ap_50_70': None,
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    # Light Guns (line 2357)
    {
        'name': '17 pdr',
        'nation': 'canadian',
        'caliber_mm': 76,  # 17-pounder = 76mm
        'he_dice': None,  # Only has AP, no HE
        'he_target': None,
        'ap_0_10': 11,
        'ap_10_20': 11,
        'ap_20_30': 10,
        'ap_30_40': 9,
        'ap_40_50': 8,
        'ap_50_70': 7,
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
]

# Missing German guns from Crucible text file
german_guns = [
    # Autocannons (line 2605)
    {
        'name': '37mmL57',
        'nation': 'german',
        'caliber_mm': 37,
        'barrel_length': 'L57',
        'he_dice': None,  # Shows "-" for HE dice
        'he_target': None,
        'ap_0_10': 3,
        'ap_10_20': 3,
        'ap_20_30': 2,
        'ap_30_40': 2,
        'ap_40_50': 1,
        'ap_50_70': None,
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    # Light Guns (lines 2626-2630)
    {
        'name': '75mmL46 (PaK40)',
        'nation': 'german',
        'caliber_mm': 75,
        'barrel_length': 'L46',
        'he_dice': 4,
        'he_target': '4+',
        'ap_0_10': 8,
        'ap_10_20': 8,
        'ap_20_30': 7,
        'ap_30_40': 6,
        'ap_40_50': 5,
        'ap_50_70': 4,
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    {
        'name': '75mmL48',
        'nation': 'german',
        'caliber_mm': 75,
        'barrel_length': 'L48',
        'he_dice': 4,
        'he_target': '4+',
        'ap_0_10': 8,
        'ap_10_20': 8,
        'ap_20_30': 7,
        'ap_30_40': 6,
        'ap_40_50': 5,
        'ap_50_70': 4,
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    {
        'name': '75mmL70',
        'nation': 'german',
        'caliber_mm': 75,
        'barrel_length': 'L70',
        'he_dice': 4,
        'he_target': '4+',
        'ap_0_10': 11,
        'ap_10_20': 11,
        'ap_20_30': 10,
        'ap_30_40': 9,
        'ap_40_50': 8,
        'ap_50_70': 7,
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    # Medium Guns (lines 2640-2644)
    {
        'name': '100mmL52 (K18)',
        'nation': 'german',
        'caliber_mm': 100,
        'barrel_length': 'L52',
        'he_dice': 5,
        'he_target': '3+',
        'ap_0_10': 10,
        'ap_10_20': 10,
        'ap_20_30': 9,
        'ap_30_40': 8,
        'ap_40_50': 7,
        'ap_50_70': 6,
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    {
        'name': '105mmL28',
        'nation': 'german',
        'caliber_mm': 105,
        'barrel_length': 'L28',
        'he_dice': 5,
        'he_target': '3+',
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    {
        'name': '150mmL12 (sIG33)',
        'nation': 'german',
        'caliber_mm': 150,
        'barrel_length': 'L12',
        'he_dice': 7,
        'he_target': '3+',
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
    {
        'name': '150mmL30',
        'nation': 'german',
        'caliber_mm': 150,
        'barrel_length': 'L30',
        'he_dice': 7,
        'he_target': '3+',
        'source_file': 'Battlegroup-Canadas-Crucible.txt',
        'source_document': 'Battlegroup-Canadas-Crucible',
        'extraction_method': 'manual',
        'verified_by': 'claude'
    },
]

def insert_guns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    all_guns = canadian_guns + german_guns

    print(f"Adding {len(all_guns)} missing guns to database")
    print(f"  Canadian: {len(canadian_guns)}")
    print(f"  German: {len(german_guns)}")
    print()

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    inserted = 0
    for gun in all_guns:
        # Check if gun already exists
        cursor.execute("SELECT id FROM bg_reference_guns WHERE name = ? AND nation = ?",
                      (gun['name'], gun['nation']))
        if cursor.fetchone():
            print(f"  [SKIP] {gun['name']:30s} - already exists")
            continue

        # Insert gun
        cursor.execute("""
            INSERT INTO bg_reference_guns (
                name, nation, caliber_mm, barrel_length,
                he_dice, he_target,
                ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                source_file, source_document, extraction_method, verified_by,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gun['name'], gun['nation'], gun.get('caliber_mm'), gun.get('barrel_length'),
            gun.get('he_dice'), gun.get('he_target'),
            gun.get('ap_0_10'), gun.get('ap_10_20'), gun.get('ap_20_30'),
            gun.get('ap_30_40'), gun.get('ap_40_50'), gun.get('ap_50_70'),
            gun.get('source_file'), gun.get('source_document'),
            gun.get('extraction_method'), gun.get('verified_by'),
            created_at
        ))

        gun_id = cursor.lastrowid
        print(f"  [+] ID {gun_id:3d}: {gun['name']:30s} ({gun['nation']})")
        inserted += 1

    conn.commit()
    conn.close()

    print()
    print(f"Added {inserted} new guns")

if __name__ == '__main__':
    insert_guns()
