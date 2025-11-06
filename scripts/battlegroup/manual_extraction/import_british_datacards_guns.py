#!/usr/bin/env python3
"""
Import British DataCards Guns from CSV to bg_reference_guns table.

This script:
- Maps CSV fields to database columns
- Detects duplicates (guns already in database from Canadian data)
- Merges nations for duplicates (adds "British" to existing nation)
- Inserts new British-only guns
- Validates that penetration data is filled in before import
"""

import csv
import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
CSV_PATH = Path(__file__).parent.parent.parent.parent / "british_datacards_ALL_GUNS.csv"

def clean_value(value):
    """Clean CSV value - handle empty strings, strip whitespace."""
    if value is None or value == '' or value == '-':
        return None
    return value.strip()

def parse_he_target(value):
    """Parse HE target format like '4+', '5+', '6+' to just the number part."""
    if not value:
        return None
    # Remove '+' if present
    cleaned = value.strip().replace('+', '')
    return cleaned if cleaned else None

def map_csv_to_db_row(csv_row):
    """
    Map CSV row to database row with field transformations.

    CSV columns:
    - name, nation, caliber_mm, he_dice, he_target,
      ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70

    DB columns:
    - name, nation, caliber_mm, barrel_length, he_dice, he_target,
      ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
      points_cost, battle_rating, source_file, source_page,
      extraction_confidence, notes, source_battle, source_date,
      unit_experience, source_document, extraction_notes, master_id,
      extraction_method, verified_by, verification_date, screenshot_file
    """

    # Map CSV to database fields
    db_row = {
        'name': clean_value(csv_row['name']),
        'nation': 'British',  # Always set to British for initial import
        'caliber_mm': clean_value(csv_row['caliber_mm']),
        'barrel_length': None,  # Not in CSV
        'he_dice': clean_value(csv_row['he_dice']),
        'he_target': parse_he_target(clean_value(csv_row['he_target'])),
        'ap_0_10': clean_value(csv_row['ap_0_10']),
        'ap_10_20': clean_value(csv_row['ap_10_20']),
        'ap_20_30': clean_value(csv_row['ap_20_30']),
        'ap_30_40': clean_value(csv_row['ap_30_40']),
        'ap_40_50': clean_value(csv_row['ap_40_50']),
        'ap_50_70': clean_value(csv_row['ap_50_70']),
        'points_cost': None,  # Not in CSV
        'battle_rating': None,  # Not in CSV
        'source_file': 'Battlegroup-DataCards-British.pdf',
        'source_page': None,  # Not in CSV
        'extraction_confidence': 'High',  # Manual data entry
        'notes': None,
        'source_battle': None,
        'source_date': None,
        'unit_experience': None,
        'source_document': 'Battlegroup DataCards - British',
        'extraction_notes': 'Imported from manually-entered CSV (british_datacards_ALL_GUNS.csv)',
        'master_id': None,  # Will be linked later
        'extraction_method': 'manual_csv_entry',
        'verified_by': None,
        'verification_date': None,
        'screenshot_file': None
    }

    return db_row

def check_duplicate(cursor, gun_name):
    """Check if gun already exists in database."""
    cursor.execute('SELECT id, nation FROM bg_reference_guns WHERE name = ?', (gun_name,))
    return cursor.fetchone()

def update_nation(cursor, gun_id, existing_nation):
    """Update nation field to add 'British' to existing nation."""
    if 'British' in existing_nation:
        return existing_nation  # Already includes British

    # Add British to nation field
    new_nation = f"{existing_nation}, British"
    cursor.execute('UPDATE bg_reference_guns SET nation = ? WHERE id = ?', (new_nation, gun_id))
    return new_nation

def insert_gun(cursor, db_row):
    """Insert new gun into database."""
    columns = ', '.join(db_row.keys())
    placeholders = ', '.join(['?' for _ in db_row])
    values = tuple(db_row.values())

    cursor.execute(f'INSERT INTO bg_reference_guns ({columns}) VALUES ({placeholders})', values)
    return cursor.lastrowid

def validate_gun_data(csv_row, row_num):
    """
    Validate that gun has required penetration data.

    Returns (is_valid, warning_message)
    """
    gun_name = clean_value(csv_row['name'])

    # Check if any penetration values are filled
    ap_values = [
        clean_value(csv_row['ap_0_10']),
        clean_value(csv_row['ap_10_20']),
        clean_value(csv_row['ap_20_30']),
        clean_value(csv_row['ap_30_40']),
        clean_value(csv_row['ap_40_50']),
        clean_value(csv_row['ap_50_70'])
    ]

    he_dice = clean_value(csv_row['he_dice'])
    he_target = clean_value(csv_row['he_target'])

    # Check if gun has ANY data filled in
    has_ap_data = any(ap_values)
    has_he_data = he_dice or he_target

    if not has_ap_data and not has_he_data:
        return (False, f"Row {row_num} ({gun_name}): No HE or AP data - CSV appears incomplete")

    return (True, None)

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

    # Read CSV (using windows-1252 encoding)
    with open(CSV_PATH, 'r', encoding='windows-1252') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f"[*] Total guns in CSV: {len(csv_rows)}")
    print()

    # Validate CSV data completeness
    print("[*] Validating CSV data completeness...")
    incomplete_rows = []
    for idx, csv_row in enumerate(csv_rows, 1):
        is_valid, warning = validate_gun_data(csv_row, idx)
        if not is_valid:
            incomplete_rows.append(warning)

    if incomplete_rows:
        print()
        print("[!] WARNING: CSV appears to have incomplete data:")
        for warning in incomplete_rows:
            print(f"    {warning}")
        print()
        response = input("Continue with import anyway? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("[*] Import cancelled by user")
            conn.close()
            return
        print()

    # Process each gun
    duplicates_updated = 0
    new_guns_inserted = 0
    skipped = 0

    for idx, csv_row in enumerate(csv_rows, 1):
        gun_name = clean_value(csv_row['name'])

        if not gun_name:
            print(f"[!] Row {idx}: Skipping row with empty name")
            skipped += 1
            continue

        # Check for duplicate
        existing = check_duplicate(cursor, gun_name)

        if existing:
            gun_id, existing_nation = existing
            new_nation = update_nation(cursor, gun_id, existing_nation)
            print(f"[~] {idx:2d}. {gun_name:30s} - DUPLICATE (updated: {existing_nation} -> {new_nation})")
            duplicates_updated += 1
        else:
            # Insert new gun
            db_row = map_csv_to_db_row(csv_row)
            new_id = insert_gun(cursor, db_row)

            # Show what data was imported
            ap_0_10 = clean_value(csv_row['ap_0_10'])
            he_dice = clean_value(csv_row['he_dice'])
            data_status = []
            if ap_0_10:
                data_status.append(f"AP:{ap_0_10}")
            if he_dice:
                data_status.append(f"HE:{he_dice}")
            status_str = ', '.join(data_status) if data_status else "NO DATA"

            print(f"[+] {idx:2d}. {gun_name:30s} - NEW (ID: {new_id}) [{status_str}]")
            new_guns_inserted += 1

    # Commit changes
    conn.commit()

    # Summary
    print()
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"Total CSV rows processed:    {len(csv_rows)}")
    print(f"Duplicates updated:          {duplicates_updated}")
    print(f"New guns inserted:           {new_guns_inserted}")
    print(f"Skipped (empty name):        {skipped}")
    print()

    # Verify final count
    cursor.execute('SELECT COUNT(*) FROM bg_reference_guns')
    total_guns = cursor.fetchone()[0]
    print(f"Total guns in database:      {total_guns}")

    # Show nation breakdown
    cursor.execute('''
        SELECT
            CASE
                WHEN nation LIKE '%,%' THEN 'Multi-Nation'
                ELSE nation
            END as nation_category,
            COUNT(*) as count
        FROM bg_reference_guns
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
