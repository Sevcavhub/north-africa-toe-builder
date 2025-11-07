#!/usr/bin/env python3
"""
Export all data scraped from Crucible PDF for manual review.
OCR quality issues confirmed in guns suggest vehicles will have same issues.
"""

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent

def export_german_guns():
    """Export German guns for review"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, common_name, nation, caliber_mm, rof, weapon_category,
               he_dice, he_target, he_shell_classification,
               he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
               ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
        FROM bg_reference_guns
        WHERE nation = 'german'
        ORDER BY name
    """)

    columns = [
        'name', 'common_name', 'nation', 'caliber_mm', 'ROF', 'weapon_category',
        'he_dice', 'he_target', 'he_shell_classification',
        'he_0_10', 'he_10_20', 'he_20_30', 'he_30_40', 'he_40_50', 'he_50_70',
        'ap_0_10', 'ap_10_20', 'ap_20_30', 'ap_30_40', 'ap_40_50', 'ap_50_70'
    ]

    output_file = OUTPUT_DIR / "german_guns_review.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for row in cursor.fetchall():
            writer.writerow(row)

    conn.close()

    print(f"[OK] German guns: {output_file.name}")
    return cursor.rowcount

def export_canadian_vehicles():
    """Export Canadian vehicles for review"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, nation, vehicle_type, year_range,
               armor_front, armor_side, armor_rear,
               off_road_inches, road_inches, special_movement,
               weapons, special_rules,
               source_file, source_page, extraction_confidence
        FROM bg_reference_vehicles
        WHERE nation = 'canadian' OR nation LIKE '%canadian%'
        ORDER BY name
    """)

    columns = [
        'name', 'nation', 'vehicle_type', 'year_range',
        'armor_front', 'armor_side', 'armor_rear',
        'off_road_inches', 'road_inches', 'special_movement',
        'weapons', 'special_rules',
        'source_file', 'source_page', 'extraction_confidence'
    ]

    output_file = OUTPUT_DIR / "canadian_vehicles_review.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for row in cursor.fetchall():
            writer.writerow(row)

    count = cursor.rowcount
    conn.close()

    print(f"[OK] Canadian vehicles: {output_file.name}")
    return count

def export_german_vehicles():
    """Export German vehicles for review"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, nation, vehicle_type, year_range,
               armor_front, armor_side, armor_rear,
               off_road_inches, road_inches, special_movement,
               weapons, special_rules,
               source_file, source_page, extraction_confidence
        FROM bg_reference_vehicles
        WHERE nation = 'german'
        ORDER BY name
    """)

    columns = [
        'name', 'nation', 'vehicle_type', 'year_range',
        'armor_front', 'armor_side', 'armor_rear',
        'off_road_inches', 'road_inches', 'special_movement',
        'weapons', 'special_rules',
        'source_file', 'source_page', 'extraction_confidence'
    ]

    output_file = OUTPUT_DIR / "german_vehicles_review.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for row in cursor.fetchall():
            writer.writerow(row)

    count = cursor.rowcount
    conn.close()

    print(f"[OK] German vehicles: {output_file.name}")
    return count

def main():
    """Export all Crucible data for manual review"""

    print("="*80)
    print("EXPORTING CRUCIBLE DATA FOR MANUAL REVIEW")
    print("="*80)
    print("\nReason: OCR quality issues confirmed in gun data suggest")
    print("        vehicle data from same txt file will have same issues.\n")

    gun_count = export_german_guns()
    canadian_vehicle_count = export_canadian_vehicles()
    german_vehicle_count = export_german_vehicles()

    print("\n" + "="*80)
    print("EXPORT COMPLETE")
    print("="*80)
    print(f"\nGerman guns:        {gun_count:3d} items -> german_guns_review.csv")
    print(f"Canadian vehicles:  {canadian_vehicle_count:3d} items -> canadian_vehicles_review.csv")
    print(f"German vehicles:    {german_vehicle_count:3d} items -> german_vehicles_review.csv")
    print(f"\nTotal items:        {gun_count + canadian_vehicle_count + german_vehicle_count:3d}")

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Open each CSV in Excel/LibreOffice")
    print("2. Compare with Battlegroup-Canadas-Crucible.pdf directly")
    print("3. Correct any OCR errors (armor values, gun stats, etc.)")
    print("4. Save corrected CSVs")
    print("5. Run import scripts to update database")

    print("\nKnown OCR Issues from Canadian Guns:")
    print("  - 75mmL40 AP: txt had 6/6/5/4/3/-, actually 11/11/10/9/8/7")
    print("  - Missing guns: 4.2\" Mortar, 105mmL22, 6\" naval gun")
    print("  - Expect similar issues in vehicle armor/weapon data")

if __name__ == '__main__':
    main()
