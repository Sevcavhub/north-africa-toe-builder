#!/usr/bin/env python3
"""
Import vehicles from easy-entry CSV format.
Reconstructs special_rules from hits/transport/open_topped columns.
"""

import csv
import sqlite3
from pathlib import Path
import sys

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def reconstruct_special_rules(hits, transport, open_topped, other_rules):
    """Reconstruct special_rules string from separate fields"""

    parts = []

    # Add hits
    if hits and str(hits).strip():
        parts.append(f"{hits} Hits")

    # Add transport
    if transport and str(transport).strip():
        parts.append(f"{transport} Transport")

    # Add open-topped
    if open_topped and str(open_topped).strip().lower() in ('yes', 'y', 'true', '1'):
        parts.append("Open-Topped")

    # Add other rules
    if other_rules and str(other_rules).strip():
        parts.append(str(other_rules).strip())

    return ', '.join(parts) if parts else None

def import_vehicles(nation: str):
    """Import vehicles from CSV"""

    csv_path = Path(__file__).parent.parent.parent.parent / f"{nation}_vehicles_review.csv"

    print(f"Reading: {csv_path}")

    if not csv_path.exists():
        print(f"ERROR: File not found: {csv_path}")
        return 0

    vehicles = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vehicles.append(row)

    print(f"Found {len(vehicles)} {nation} vehicles to import")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Delete existing vehicles for this nation
    cursor.execute(f"DELETE FROM bg_reference_vehicles WHERE nation = '{nation}' OR nation LIKE '%{nation}%'")
    deleted = cursor.rowcount
    print(f"Deleted {deleted} existing {nation} vehicles")

    # Insert vehicles
    insert_sql = """
    INSERT INTO bg_reference_vehicles (
        name, nation, year_range, vehicle_type,
        off_road_inches, road_inches, special_movement,
        armor_front, armor_side, armor_rear,
        armor_modifier, armor_side_schurzen,
        weapons, special_rules,
        source_file, source_page
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    inserted = 0
    for vehicle in vehicles:
        # Convert empty strings to None
        def clean(val):
            return None if (not val or val == '') else val

        # Reconstruct special_rules from discrete fields
        special_rules = reconstruct_special_rules(
            vehicle.get('hits'),
            vehicle.get('transport'),
            vehicle.get('open_topped'),
            vehicle.get('special_rules')
        )

        values = (
            vehicle['name'],
            vehicle['nation'],
            clean(vehicle.get('year_range')),
            clean(vehicle.get('vehicle_type')),
            clean(vehicle.get('off_road_inches')),
            clean(vehicle.get('road_inches')),
            clean(vehicle.get('special_movement')),
            clean(vehicle.get('armor_front')),
            clean(vehicle.get('armor_side')),
            clean(vehicle.get('armor_rear')),
            clean(vehicle.get('armor_top')),
            clean(vehicle.get('Schurzen_side')),
            clean(vehicle.get('weapons')),
            special_rules,
            clean(vehicle.get('source_file')),
            clean(vehicle.get('page_number'))
        )

        cursor.execute(insert_sql, values)
        inserted += 1

        # Show special_rules reconstruction
        if special_rules:
            print(f"  [+] {vehicle['name']:30s} | {special_rules}")
        else:
            print(f"  [+] {vehicle['name']}")

    conn.commit()
    conn.close()

    print(f"\n=== IMPORT COMPLETE ===")
    print(f"Imported: {inserted} {nation} vehicles")
    print(f"Database: {DB_PATH}")

    return inserted

def main():
    """Import vehicles for specified nation"""

    if len(sys.argv) != 2 or sys.argv[1] not in ['canadian', 'german']:
        print("Usage: python import_vehicles_corrected.py [canadian|german]")
        sys.exit(1)

    nation = sys.argv[1]

    print("="*80)
    print(f"IMPORTING {nation.upper()} VEHICLES")
    print("="*80)
    print("\nReconstructing special_rules from:")
    print("  hits + transport + open_topped + special_rules\n")

    count = import_vehicles(nation)

    if count > 0:
        print(f"\n[SUCCESS] Imported {count} {nation} vehicles")
    else:
        print(f"\n[FAILED] No vehicles imported")
        sys.exit(1)

if __name__ == '__main__':
    main()
