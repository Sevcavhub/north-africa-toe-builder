#!/usr/bin/env python3
"""
Re-export vehicles with proper column structure matching British vehicles format.
"""

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent

def export_vehicles_proper_format(nation: str):
    """Export vehicles with British CSV column structure"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query with proper columns
    cursor.execute(f"""
        SELECT
            name, nation, year_range, vehicle_type,
            off_road_inches, road_inches, special_movement,
            armor_front, armor_side, armor_rear,
            armor_modifier as armor_top,
            armor_side_schurzen as Schurzen_side,
            weapons,
            special_rules,
            source_file, source_page
        FROM bg_reference_vehicles
        WHERE nation = '{nation}' OR nation LIKE '%{nation}%'
        ORDER BY name
    """)

    # Column names matching British CSV format
    columns = [
        'name', 'nation', 'year_range', 'vehicle_type',
        'off_road_inches', 'road_inches', 'special_movement',
        'armor_front', 'armor_side', 'armor_rear', 'armor_top', 'Schurzen_side',
        'weapons', 'mount', 'ammo', 'special_rules',
        'source_file', 'page_number'
    ]

    output_file = OUTPUT_DIR / f"{nation}_vehicles_review.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for row in cursor.fetchall():
            # row has: name, nation, year_range, vehicle_type, off_road, road, special_mov,
            #          armor_f, armor_s, armor_r, armor_top, schurzen,
            #          weapons, special_rules, source_file, source_page

            # Need to add empty columns for: mount, ammo (these need manual entry)
            expanded_row = list(row[:13]) + ['', ''] + list(row[13:])
            writer.writerow(expanded_row)

    count = cursor.rowcount
    conn.close()

    print(f"[OK] {nation.title()} vehicles: {output_file.name} ({count} vehicles)")
    return count

def main():
    """Export both Canadian and German vehicles with proper format"""

    print("="*80)
    print("RE-EXPORTING VEHICLES WITH PROPER COLUMN FORMAT")
    print("="*80)
    print("\nMatching British vehicles CSV structure:")
    print("  - armor_top, Schurzen_side, mount, ammo columns included\n")

    canadian_count = export_vehicles_proper_format('canadian')
    german_count = export_vehicles_proper_format('german')

    print("\n" + "="*80)
    print("EXPORT COMPLETE")
    print("="*80)
    print(f"\nCanadian vehicles: {canadian_count:3d} -> canadian_vehicles_review.csv")
    print(f"German vehicles:   {german_count:3d} -> german_vehicles_review.csv")
    print(f"\nTotal: {canadian_count + german_count} vehicles")

    print("\n" + "="*80)
    print("SCHURZEN USAGE")
    print("="*80)
    print("For vehicles with side skirts (e.g., Panzer IV H):")
    print("  armor_side:    J   (base side armor)")
    print("  Schurzen_side: H   (skirt armor)")
    print("  Display:       J(H) (automatic on datacard)")
    print("\nLeave Schurzen_side blank for vehicles without skirts.")

if __name__ == '__main__':
    main()
