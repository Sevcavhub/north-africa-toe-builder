#!/usr/bin/env python3
"""
Compare scraper extraction vs. user corrections to identify accuracy gaps.
"""

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def compare_canadian_guns():
    """Compare scraped Canadian guns vs. corrected CSV"""

    # Read user corrections
    csv_path = Path(__file__).parent.parent.parent.parent / "canadian_guns_review.csv"

    corrected_guns = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            corrected_guns[row['name']] = row

    # Read scraped data from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, caliber_mm, he_dice, he_target, he_shell_classification,
               he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
               ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
               rof
        FROM bg_reference_guns
        WHERE nation = 'canadian'
        ORDER BY name
    """)

    scraped_guns = {}
    for row in cursor.fetchall():
        scraped_guns[row[0]] = {
            'caliber_mm': row[1],
            'he_dice': row[2],
            'he_target': row[3],
            'he_shell_classification': row[4],
            'he_0_10': row[5], 'he_10_20': row[6], 'he_20_30': row[7],
            'he_30_40': row[8], 'he_40_50': row[9], 'he_50_70': row[10],
            'ap_0_10': row[11], 'ap_10_20': row[12], 'ap_20_30': row[13],
            'ap_30_40': row[14], 'ap_40_50': row[15], 'ap_50_70': row[16],
            'rof': row[17]
        }

    conn.close()

    print("="*120)
    print("SCRAPER vs CORRECTIONS COMPARISON - CANADIAN GUNS")
    print("="*120)
    print(f"\nUser corrected: {len(corrected_guns)} guns")
    print(f"Scraper extracted: {len(scraped_guns)} guns")
    print(f"Missing from scraper: {len(corrected_guns) - len(scraped_guns)} guns\n")

    # Show missing guns
    missing_guns = set(corrected_guns.keys()) - set(scraped_guns.keys())
    if missing_guns:
        print(f"MISSING GUNS ({len(missing_guns)}):")
        print("-"*120)
        for gun in sorted(missing_guns):
            row = corrected_guns[gun]
            he_str = f"{row['he_dice']}D6/{row['he_target']}" if row['he_dice'] else "No HE"
            print(f"  - {gun:30s} | {row['caliber_mm']:>4s}mm | HE:{he_str:12s} | Type:{row['weapon_category']}")
        print()

    # Compare extracted guns
    print(f"EXTRACTED GUNS COMPARISON ({len(scraped_guns)}):")
    print("-"*120)

    for gun_name in sorted(scraped_guns.keys()):
        if gun_name not in corrected_guns:
            print(f"\n[!] {gun_name}: In scraper but NOT in corrections (extra gun?)")
            continue

        scraped = scraped_guns[gun_name]
        corrected = corrected_guns[gun_name]

        errors = []

        # Compare each field
        if str(scraped['caliber_mm'] or '') != str(corrected['caliber_mm'] or ''):
            errors.append(f"Caliber: {scraped['caliber_mm']} vs {corrected['caliber_mm']}")

        if str(scraped['he_dice'] or '') != str(corrected['he_dice'] or ''):
            errors.append(f"HE dice: {scraped['he_dice']} vs {corrected['he_dice']}")

        if str(scraped['he_target'] or '') != str(corrected['he_target'] or ''):
            errors.append(f"HE target: {scraped['he_target']} vs {corrected['he_target']}")

        # Compare HE ranges
        he_fields = ['he_0_10', 'he_10_20', 'he_20_30', 'he_30_40', 'he_40_50', 'he_50_70']
        scraped_he_ranges = [str(scraped[f] or '') for f in he_fields]
        corrected_he_ranges = [str(corrected[f] or '') for f in he_fields]

        if scraped_he_ranges != corrected_he_ranges:
            errors.append(f"HE ranges: {'/'.join(scraped_he_ranges)} vs {'/'.join(corrected_he_ranges)}")

        # Compare AP ranges
        ap_fields = ['ap_0_10', 'ap_10_20', 'ap_20_30', 'ap_30_40', 'ap_40_50', 'ap_50_70']
        scraped_ap_ranges = [str(scraped[f] or '') for f in ap_fields]
        corrected_ap_ranges = [str(corrected[f] or '') for f in ap_fields]

        if scraped_ap_ranges != corrected_ap_ranges:
            errors.append(f"AP ranges: {'/'.join(scraped_ap_ranges)} vs {'/'.join(corrected_ap_ranges)}")

        # Show results
        if errors:
            print(f"\n[X] {gun_name}")
            for error in errors:
                print(f"    - {error}")
        else:
            print(f"[OK] {gun_name}")

    # Summary statistics
    print("\n" + "="*120)
    print("SUMMARY")
    print("="*120)
    print(f"Guns in corrections:  {len(corrected_guns)}")
    print(f"Guns scraped:         {len(scraped_guns)}")
    print(f"Missing from scraper: {len(missing_guns)} ({len(missing_guns)/len(corrected_guns)*100:.1f}%)")
    print(f"Extraction rate:      {len(scraped_guns)}/{len(corrected_guns)} ({len(scraped_guns)/len(corrected_guns)*100:.1f}%)")

if __name__ == '__main__':
    compare_canadian_guns()
