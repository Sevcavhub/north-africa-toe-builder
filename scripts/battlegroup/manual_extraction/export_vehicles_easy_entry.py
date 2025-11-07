#!/usr/bin/env python3
"""
Export vehicles with separate columns for Hits, Transport, Open-Topped
for easier manual data entry.
"""

import csv
import sqlite3
import re
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent

def parse_special_rules(special_rules_text: str):
    """Extract hits, transport, open-topped from special_rules text"""

    hits = ''
    transport = ''
    open_topped = ''
    other_rules = []

    if not special_rules_text:
        return hits, transport, open_topped, ''

    # Split by comma
    parts = [p.strip() for p in special_rules_text.split(',')]

    for part in parts:
        # Check for hits: "2 Hits", "3 Hits"
        hits_match = re.search(r'^(\d+)\s+Hits?$', part, re.IGNORECASE)
        if hits_match:
            hits = hits_match.group(1)
            continue

        # Check for transport: "6 Transport", "12 Transport"
        transport_match = re.search(r'^(\d+)\s+Transport$', part, re.IGNORECASE)
        if transport_match:
            transport = transport_match.group(1)
            continue

        # Check for open-topped: "Open-Topped", "Open Topped"
        if re.search(r'^Open[-\s]?Topped$', part, re.IGNORECASE):
            open_topped = 'Yes'
            continue

        # Everything else goes to other_rules
        other_rules.append(part)

    return hits, transport, open_topped, ', '.join(other_rules)

def export_vehicles_easy_entry(nation: str):
    """Export vehicles with easy-entry column structure"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

    # Column names with separate hits/transport/open_topped
    columns = [
        'name', 'nation', 'year_range', 'vehicle_type',
        'off_road_inches', 'road_inches', 'special_movement',
        'armor_front', 'armor_side', 'armor_rear', 'armor_top', 'Schurzen_side',
        'weapons', 'mount', 'ammo',
        'hits', 'transport', 'open_topped',
        'special_rules',
        'source_file', 'page_number'
    ]

    output_file = OUTPUT_DIR / f"{nation}_vehicles_review.csv"

    rows_written = 0
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for row in cursor.fetchall():
            # row: name, nation, year_range, vehicle_type, off_road, road, special_mov,
            #      armor_f, armor_s, armor_r, armor_top, schurzen,
            #      weapons, special_rules, source_file, source_page

            special_rules_text = row[13] or ''

            # Parse special_rules to extract hits, transport, open_topped
            hits, transport, open_topped, other_rules = parse_special_rules(special_rules_text)

            # Build output row:
            # name ... schurzen, weapons, mount(empty), ammo(empty), hits, transport, open_topped, special_rules, source...
            output_row = list(row[:13]) + ['', ''] + [hits, transport, open_topped, other_rules] + list(row[14:])

            writer.writerow(output_row)
            rows_written += 1

    conn.close()

    print(f"[OK] {nation.title()} vehicles: {output_file.name} ({rows_written} vehicles)")
    return rows_written

def main():
    """Export both nations with easy-entry format"""

    print("="*80)
    print("EXPORTING VEHICLES WITH EASY-ENTRY FORMAT")
    print("="*80)
    print("\nSeparate columns for:")
    print("  - hits (number: 2, 3, etc.)")
    print("  - transport (number: 6, 12, 22, etc.)")
    print("  - open_topped (Yes/blank)")
    print("  - special_rules (everything else)\n")

    canadian_count = export_vehicles_easy_entry('canadian')
    german_count = export_vehicles_easy_entry('german')

    print("\n" + "="*80)
    print("EXPORT COMPLETE")
    print("="*80)
    print(f"\nCanadian vehicles: {canadian_count:3d} -> canadian_vehicles_review.csv")
    print(f"German vehicles:   {german_count:3d} -> german_vehicles_review.csv")
    print(f"\nTotal: {canadian_count + german_count} vehicles")

    print("\n" + "="*80)
    print("EASY DATA ENTRY")
    print("="*80)
    print("Instead of: special_rules = '3 Hits, 12 Transport, Open-Topped'")
    print("Just fill:")
    print("  hits: 3")
    print("  transport: 12")
    print("  open_topped: Yes")
    print("  special_rules: (leave blank or add other rules)")
    print("\nThe import script will reconstruct the full special_rules text.")

if __name__ == '__main__':
    main()
