#!/usr/bin/env python3
"""
Import British DataCards Vehicles from CSV to bg_reference_vehicles table.

This script:
- Maps CSV fields to database columns
- Detects duplicates (vehicles already in database from Canadian data)
- Merges nations for duplicates (adds "British" to existing nation)
- Inserts new British-only vehicles
- Stores unmapped CSV fields (mount, ammo, armor_top) in notes
"""

import csv
import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
CSV_PATH = Path(__file__).parent.parent.parent.parent / "british_datacards_ALL_VEHICLES.csv"

def clean_value(value):
    """Clean CSV value - handle empty strings, strip whitespace."""
    if value is None or value == '' or value == '-':
        return None
    return value.strip()

def normalize_special_movement(value):
    """Normalize special_movement values to match database format."""
    if not value:
        return None

    # Common normalizations
    normalizations = {
        'open-topped': 'Open-topped',
        'Open-Topped': 'Open-topped',
        'OPEN-TOPPED': 'Open-topped',
        'amphib repair': 'Amphib Repair',
        'Amphib repair': 'Amphib Repair',
        'recovery, repair': 'Recovery, Repair',
        'Recovery, Repair': 'Recovery, Repair',
        'bridgelayer': 'Bridgelayer',
        'Bridge': 'Bridgelayer',
        'engineer': 'Engineer',
        'Engineer': 'Engineer',
        'unrel': 'Unreliable',
        'Unrel': 'Unreliable',
    }

    # Check for direct match
    if value in normalizations:
        return normalizations[value]

    # Return as-is if no normalization needed
    return value

def map_csv_to_db_row(csv_row):
    """
    Map CSV row to database row with field transformations.

    CSV columns:
    - name, nation, year_range, vehicle_type, off_road_inches, road_inches,
      special_movement, armor_front, armor_side, armor_rear, armor_top,
      Schürzen_side, weapons, mount, ammo, special_rules, source_file, page_number

    DB columns:
    - name, nation, year_range, vehicle_type, off_road_inches, road_inches,
      special_movement, armor_front, armor_side, armor_rear, weapons,
      special_rules, source_file, source_page, extraction_confidence, notes,
      source_battle, source_date, source_document, extraction_notes, master_id,
      extraction_method, screenshot_file, armor_modifier, armor_side_schurzen
    """

    # Build notes from unmapped fields
    notes_parts = []
    if clean_value(csv_row['mount']):
        notes_parts.append(f"Mount: {csv_row['mount']}")
    if clean_value(csv_row['ammo']):
        notes_parts.append(f"Ammo: {csv_row['ammo']}")
    if clean_value(csv_row['armor_top']):
        notes_parts.append(f"Armor Top: {csv_row['armor_top']}")
    notes = '; '.join(notes_parts) if notes_parts else None

    # Map CSV to database fields
    db_row = {
        'name': clean_value(csv_row['name']),
        'nation': 'British',  # Always set to British for initial import
        'year_range': clean_value(csv_row['year_range']),
        'vehicle_type': clean_value(csv_row['vehicle_type']),
        'off_road_inches': clean_value(csv_row['off_road_inches']),
        'road_inches': clean_value(csv_row['road_inches']),
        'special_movement': normalize_special_movement(clean_value(csv_row['special_movement'])),
        'armor_front': clean_value(csv_row['armor_front']),
        'armor_side': clean_value(csv_row['armor_side']),
        'armor_rear': clean_value(csv_row['armor_rear']),
        'armor_side_schurzen': clean_value(csv_row['Schürzen_side']),
        'weapons': clean_value(csv_row['weapons']),
        'special_rules': clean_value(csv_row['special_rules']),
        'source_file': clean_value(csv_row['source_file']),
        'source_page': clean_value(csv_row['page_number']),
        'extraction_confidence': 'High',  # Manual data entry
        'notes': notes,
        'source_battle': None,  # Not in CSV
        'source_date': None,    # Not in CSV
        'source_document': 'Battlegroup DataCards - British',
        'extraction_notes': 'Imported from manually-entered CSV (british_datacards_ALL_VEHICLES.csv)',
        'master_id': None,      # Will be linked later
        'extraction_method': 'manual_csv_entry',
        'screenshot_file': None,
        'armor_modifier': None
    }

    return db_row

def check_duplicate(cursor, vehicle_name):
    """Check if vehicle already exists in database."""
    cursor.execute('SELECT id, nation FROM bg_reference_vehicles WHERE name = ?', (vehicle_name,))
    return cursor.fetchone()

def update_nation(cursor, vehicle_id, existing_nation):
    """Update nation field to add 'British' to existing nation."""
    if 'British' in existing_nation:
        return existing_nation  # Already includes British

    # Add British to nation field
    new_nation = f"{existing_nation}, British"
    cursor.execute('UPDATE bg_reference_vehicles SET nation = ? WHERE id = ?', (new_nation, vehicle_id))
    return new_nation

def insert_vehicle(cursor, db_row):
    """Insert new vehicle into database."""
    columns = ', '.join(db_row.keys())
    placeholders = ', '.join(['?' for _ in db_row])
    values = tuple(db_row.values())

    cursor.execute(f'INSERT INTO bg_reference_vehicles ({columns}) VALUES ({placeholders})', values)
    return cursor.lastrowid

def main():
    """Main import process."""

    # Verify files exist
    if not CSV_PATH.exists():
        print(f"[!] ERROR: CSV file not found at {CSV_PATH}")
        return

    if not DB_PATH.exists():
        print(f"[!] ERROR: Database not found at {DB_PATH}")
        return

    print(f"[*] Reading CSV: {CSV_PATH}")
    print(f"[*] Database: {DB_PATH}")
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read CSV (using windows-1252 encoding to handle Schürzen character)
    with open(CSV_PATH, 'r', encoding='windows-1252') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f"[*] Total vehicles in CSV: {len(csv_rows)}")
    print()

    # Process each vehicle
    duplicates_updated = 0
    new_vehicles_inserted = 0
    skipped = 0

    for idx, csv_row in enumerate(csv_rows, 1):
        vehicle_name = clean_value(csv_row['name'])

        if not vehicle_name:
            print(f"[!] Row {idx}: Skipping row with empty name")
            skipped += 1
            continue

        # Check for duplicate
        existing = check_duplicate(cursor, vehicle_name)

        if existing:
            vehicle_id, existing_nation = existing
            new_nation = update_nation(cursor, vehicle_id, existing_nation)
            print(f"[~] {idx:2d}. {vehicle_name:40s} - DUPLICATE (updated: {existing_nation} -> {new_nation})")
            duplicates_updated += 1
        else:
            # Insert new vehicle
            db_row = map_csv_to_db_row(csv_row)
            new_id = insert_vehicle(cursor, db_row)
            print(f"[+] {idx:2d}. {vehicle_name:40s} - NEW (ID: {new_id})")
            new_vehicles_inserted += 1

    # Commit changes
    conn.commit()

    # Summary
    print()
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"Total CSV rows processed:    {len(csv_rows)}")
    print(f"Duplicates updated:          {duplicates_updated}")
    print(f"New vehicles inserted:       {new_vehicles_inserted}")
    print(f"Skipped (empty name):        {skipped}")
    print()

    # Verify final count
    cursor.execute('SELECT COUNT(*) FROM bg_reference_vehicles')
    total_vehicles = cursor.fetchone()[0]
    print(f"Total vehicles in database:  {total_vehicles}")

    # Show nation breakdown
    cursor.execute('''
        SELECT
            CASE
                WHEN nation LIKE '%,%' THEN 'Multi-Nation'
                ELSE nation
            END as nation_category,
            COUNT(*) as count
        FROM bg_reference_vehicles
        GROUP BY nation_category
        ORDER BY count DESC
    ''')

    print()
    print("Nation breakdown:")
    for row in cursor.fetchall():
        print(f"  {row[0]:20s}: {row[1]:3d}")

    conn.close()

    print()
    print("[*] Import complete!")

if __name__ == '__main__':
    main()
