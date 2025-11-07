#!/usr/bin/env python3
"""
Import user-corrected Canadian guns from CSV to database.
"""

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
CSV_PATH = Path(__file__).parent.parent.parent.parent / "canadian_guns_review.csv"

def import_canadian_guns():
    """Import corrected Canadian guns"""

    print(f"Reading: {CSV_PATH}")

    guns = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            guns.append(row)

    print(f"Found {len(guns)} Canadian guns to import")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Delete existing Canadian guns
    cursor.execute("DELETE FROM bg_reference_guns WHERE nation = 'canadian'")
    deleted = cursor.rowcount
    print(f"Deleted {deleted} existing Canadian guns")

    # Insert corrected guns
    insert_sql = """
    INSERT INTO bg_reference_guns (
        name, common_name, nation, caliber_mm, rof, weapon_category,
        he_dice, he_target, he_shell_classification,
        he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
        ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    inserted = 0
    for gun in guns:
        # Convert empty strings to None
        def clean(val):
            return None if val == '' else val

        values = (
            gun['name'],
            clean(gun.get('common_name')),
            gun['nation'],
            clean(gun['caliber_mm']),
            clean(gun.get('ROF')),
            clean(gun.get('weapon_category')),
            clean(gun['he_dice']),
            clean(gun['he_target']),
            clean(gun['he_shell_classification']),
            clean(gun['he_0_10']),
            clean(gun['he_10_20']),
            clean(gun['he_20_30']),
            clean(gun['he_30_40']),
            clean(gun['he_40_50']),
            clean(gun['he_50_70']),
            clean(gun['ap_0_10']),
            clean(gun['ap_10_20']),
            clean(gun['ap_20_30']),
            clean(gun['ap_30_40']),
            clean(gun['ap_40_50']),
            clean(gun['ap_50_70'])
        )

        cursor.execute(insert_sql, values)
        inserted += 1
        print(f"  [+] {gun['name']}")

    conn.commit()
    conn.close()

    print(f"\n=== IMPORT COMPLETE ===")
    print(f"Imported: {inserted} Canadian guns")
    print(f"Database: {DB_PATH}")

if __name__ == '__main__':
    import_canadian_guns()
