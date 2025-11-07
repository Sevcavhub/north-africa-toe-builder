#!/usr/bin/env python3
"""
Import Comprehensive Gun Data from CSV

Updates ALL fields from comprehensive CSV export.
Matches guns by ID, updates all columns from CSV.

Usage:
    python import_guns_comprehensive.py --csv canadian_guns_comprehensive.csv --nation canadian
    python import_guns_comprehensive.py --csv german_guns_comprehensive.csv --german
"""

import csv
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def clean_value(value):
    """Clean CSV value - handle empty strings, convert types."""
    if value is None or value == '' or value == 'None':
        return None
    return value.strip()

def compare_values(old, new):
    """Compare old and new values, handling NULL/None/empty."""
    # Normalize for comparison
    old_norm = None if old in [None, '', 'None'] else str(old).strip()
    new_norm = None if new in [None, '', 'None'] else str(new).strip()
    return old_norm != new_norm

def import_guns_from_csv(csv_path, nation):
    """Import comprehensive gun data from CSV."""

    if not csv_path.exists():
        print(f"[!] ERROR: CSV file not found: {csv_path}")
        return

    print("="*80)
    print(f"COMPREHENSIVE GUN IMPORT: {nation.upper()}")
    print("="*80)
    print(f"[*] CSV: {csv_path}")
    print(f"[*] Database: {DB_PATH}")
    print()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f"[*] Loaded {len(csv_rows)} guns from CSV")
    print()

    # Get current database state for comparison
    cursor.execute("PRAGMA table_info(bg_reference_guns)")
    db_columns = [col[1] for col in cursor.fetchall()]

    # Process each gun
    updated_count = 0
    unchanged_count = 0
    not_found_count = 0

    for idx, row in enumerate(csv_rows, 1):
        gun_id = clean_value(row.get('id'))

        if not gun_id:
            print(f"[!] Row {idx}: Missing ID, skipping")
            continue

        gun_name = clean_value(row.get('name'))

        # Get current gun data
        cursor.execute('SELECT * FROM bg_reference_guns WHERE id = ?', (gun_id,))
        current = cursor.fetchone()

        if not current:
            print(f"[!] Row {idx}: Gun ID {gun_id} not found in database")
            not_found_count += 1
            continue

        # Build update data (exclude id, created_at)
        update_fields = []
        update_values = []
        changes = []

        for col_idx, col_name in enumerate(db_columns):
            if col_name in ['id', 'created_at']:
                continue  # Don't update these

            csv_value = clean_value(row.get(col_name))
            current_value = current[col_idx]

            # Check if value changed
            if compare_values(current_value, csv_value):
                update_fields.append(f'{col_name} = ?')
                update_values.append(csv_value)
                changes.append(f"{col_name}: '{current_value}' → '{csv_value}'")

        if not update_fields:
            print(f"[~] {idx:2d}. {gun_name:30s} - UNCHANGED")
            unchanged_count += 1
            continue

        # Execute update
        sql = f"UPDATE bg_reference_guns SET {', '.join(update_fields)} WHERE id = ?"
        update_values.append(gun_id)
        cursor.execute(sql, update_values)

        # Show changes
        print(f"[+] {idx:2d}. {gun_name:30s} - UPDATED ({len(changes)} changes)")
        for change in changes[:5]:  # Show first 5 changes
            print(f"         {change}")
        if len(changes) > 5:
            print(f"         ... and {len(changes) - 5} more changes")

        updated_count += 1

    # Commit changes
    conn.commit()

    # Summary
    print()
    print("="*80)
    print("IMPORT SUMMARY")
    print("="*80)
    print(f"Total rows processed:     {len(csv_rows)}")
    print(f"Guns updated:             {updated_count}")
    print(f"Guns unchanged:           {unchanged_count}")
    print(f"Guns not found:           {not_found_count}")
    print()

    # Validation statistics
    cursor.execute(f'''
        SELECT
            COUNT(*) as total,
            COUNT(he_0_10) as he_range_count,
            COUNT(he_shell_classification) as he_class_count,
            COUNT(rof) as rof_count,
            COUNT(caliber_mm) as caliber_count
        FROM bg_reference_guns
        WHERE nation LIKE '%{nation}%'
    ''')
    stats = cursor.fetchone()

    print(f"[*] {nation.upper()} guns after import:")
    print(f"    Total guns:              {stats[0]}")
    print(f"    Caliber populated:       {stats[4]}/{stats[0]} ({stats[4]/stats[0]*100:.1f}%)")
    print(f"    HE ranges populated:     {stats[1]}/{stats[0]} ({stats[1]/stats[0]*100:.1f}%)")
    print(f"    HE classification:       {stats[2]}/{stats[0]} ({stats[2]/stats[0]*100:.1f}%)")
    print(f"    ROF populated:           {stats[3]}/{stats[0]} ({stats[3]/stats[0]*100:.1f}%)")
    print()

    conn.close()

    print("[*] Import complete!")
    print()
    print("Next steps:")
    print("  1. Run audit: python scripts/battlegroup/manual_extraction/audit_scraped_data.py")
    print("  2. Manual review in database")
    print("  3. If issues found, re-edit CSV and re-import")

def main():
    parser = argparse.ArgumentParser(description='Import comprehensive gun data from CSV')
    parser.add_argument('--csv', required=True, help='Path to comprehensive CSV file')
    parser.add_argument('--nation', required=True, choices=['canadian', 'german', 'british'], help='Nation being imported')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    import_guns_from_csv(csv_path, args.nation)

if __name__ == '__main__':
    main()
