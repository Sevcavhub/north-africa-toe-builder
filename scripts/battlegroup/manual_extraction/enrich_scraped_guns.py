#!/usr/bin/env python3
"""
Enrich Scraped Canadian/German Guns

Updates existing gun records with missing HE range bands, HE classification, and ROF data.

Process:
1. Read enrichment CSV (gun_name + 8 missing fields)
2. Match gun_name to existing database records
3. Update ONLY the missing fields (preserve existing data)
4. Log all changes
5. Generate validation report

Usage:
    python enrich_scraped_guns.py --csv canadian_guns_enrichment.csv --nation canadian
    python enrich_scraped_guns.py --csv german_guns_enrichment.csv --nation german
"""

import csv
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def clean_value(value):
    """Clean CSV value - handle empty strings, strip whitespace."""
    if value is None or value == '' or value == '-':
        return None
    return value.strip()

def find_gun_by_name(cursor, gun_name, nation):
    """Find gun ID by name and nation."""
    # Try exact match first
    cursor.execute('''
        SELECT id, name, nation
        FROM bg_reference_guns
        WHERE name = ? AND nation LIKE ?
    ''', (gun_name, f'%{nation}%'))
    result = cursor.fetchone()

    if result:
        return result

    # Try case-insensitive match
    cursor.execute('''
        SELECT id, name, nation
        FROM bg_reference_guns
        WHERE LOWER(name) = LOWER(?) AND nation LIKE ?
    ''', (gun_name, f'%{nation}%'))
    result = cursor.fetchone()

    return result

def update_gun_enrichment(cursor, gun_id, enrichment_data):
    """Update gun with enrichment data (only update NULL fields)."""

    # Build UPDATE statement dynamically (only update if field is currently NULL)
    updates = []
    values = []

    fields_to_update = {
        'he_0_10': enrichment_data.get('he_0_10'),
        'he_10_20': enrichment_data.get('he_10_20'),
        'he_20_30': enrichment_data.get('he_20_30'),
        'he_30_40': enrichment_data.get('he_30_40'),
        'he_40_50': enrichment_data.get('he_40_50'),
        'he_50_70': enrichment_data.get('he_50_70'),
        'he_shell_classification': enrichment_data.get('he_shell_classification'),
        'rof': enrichment_data.get('rof')
    }

    # Check which fields are currently NULL
    cursor.execute(f'''
        SELECT he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
               he_shell_classification, rof
        FROM bg_reference_guns
        WHERE id = ?
    ''', (gun_id,))
    current_values = cursor.fetchone()

    field_names = ['he_0_10', 'he_10_20', 'he_20_30', 'he_30_40', 'he_40_50', 'he_50_70',
                   'he_shell_classification', 'rof']

    updated_fields = []
    for idx, field_name in enumerate(field_names):
        new_value = fields_to_update[field_name]
        current_value = current_values[idx]

        # Update if: new value provided AND (current is NULL OR current is empty string)
        if new_value is not None and (current_value is None or current_value == ''):
            updates.append(f'{field_name} = ?')
            values.append(new_value)
            updated_fields.append(field_name)

    if not updates:
        return []  # Nothing to update

    # Execute update
    sql = f"UPDATE bg_reference_guns SET {', '.join(updates)} WHERE id = ?"
    values.append(gun_id)
    cursor.execute(sql, values)

    return updated_fields

def main():
    parser = argparse.ArgumentParser(description='Enrich scraped gun data with HE ranges, ROF, classification')
    parser.add_argument('--csv', required=True, help='Path to enrichment CSV file')
    parser.add_argument('--nation', required=True, choices=['canadian', 'german'], help='Nation to enrich')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[!] ERROR: CSV file not found: {csv_path}")
        return

    print("="*80)
    print(f"GUN ENRICHMENT: {args.nation.upper()}")
    print("="*80)
    print(f"[*] CSV: {csv_path}")
    print(f"[*] Database: {DB_PATH}")
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read enrichment CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        enrichment_rows = list(reader)

    print(f"[*] Loaded {len(enrichment_rows)} enrichment records")
    print()

    # Process each enrichment row
    matched = 0
    not_found = 0
    updated = 0
    skipped = 0

    for idx, row in enumerate(enrichment_rows, 1):
        gun_name = clean_value(row['gun_name'])

        if not gun_name:
            print(f"[!] Row {idx}: Skipping empty gun_name")
            skipped += 1
            continue

        # Find gun in database
        result = find_gun_by_name(cursor, gun_name, args.nation)

        if not result:
            print(f"[!] Row {idx}: Gun not found: {gun_name}")
            not_found += 1
            continue

        gun_id, db_name, db_nation = result
        matched += 1

        # Prepare enrichment data
        enrichment_data = {
            'he_0_10': clean_value(row.get('he_0_10')),
            'he_10_20': clean_value(row.get('he_10_20')),
            'he_20_30': clean_value(row.get('he_20_30')),
            'he_30_40': clean_value(row.get('he_30_40')),
            'he_40_50': clean_value(row.get('he_40_50')),
            'he_50_70': clean_value(row.get('he_50_70')),
            'he_shell_classification': clean_value(row.get('he_shell_classification')),
            'rof': clean_value(row.get('rof'))
        }

        # Check if any enrichment data provided
        has_data = any(v is not None for v in enrichment_data.values())
        if not has_data:
            print(f"[~] {idx:2d}. {gun_name:30s} - SKIPPED (no enrichment data provided)")
            skipped += 1
            continue

        # Update gun
        updated_fields = update_gun_enrichment(cursor, gun_id, enrichment_data)

        if updated_fields:
            updated += 1
            fields_str = ', '.join(updated_fields)
            print(f"[+] {idx:2d}. {gun_name:30s} - UPDATED ({len(updated_fields)} fields: {fields_str})")
        else:
            print(f"[~] {idx:2d}. {gun_name:30s} - NO UPDATE (all fields already populated)")

    # Commit changes
    conn.commit()

    # Summary
    print()
    print("="*80)
    print("ENRICHMENT SUMMARY")
    print("="*80)
    print(f"Total rows processed:     {len(enrichment_rows)}")
    print(f"Guns matched:             {matched}")
    print(f"Guns updated:             {updated}")
    print(f"Guns not found:           {not_found}")
    print(f"Skipped (no data):        {skipped}")
    print()

    # Validation: Check completeness after enrichment
    cursor.execute(f'''
        SELECT
            COUNT(*) as total,
            COUNT(he_0_10) as he_0_10_count,
            COUNT(he_shell_classification) as he_class_count,
            COUNT(rof) as rof_count
        FROM bg_reference_guns
        WHERE nation LIKE '%{args.nation}%'
    ''')
    stats = cursor.fetchone()

    print(f"[*] {args.nation.upper()} guns after enrichment:")
    print(f"    Total guns:              {stats[0]}")
    print(f"    HE 0-10\" populated:      {stats[1]}/{stats[0]} ({stats[1]/stats[0]*100:.1f}%)")
    print(f"    HE classification:       {stats[2]}/{stats[0]} ({stats[2]/stats[0]*100:.1f}%)")
    print(f"    ROF populated:           {stats[3]}/{stats[0]} ({stats[3]/stats[0]*100:.1f}%)")
    print()

    # Show sample enriched guns
    print("Sample enriched guns:")
    cursor.execute(f'''
        SELECT name, he_0_10, he_10_20, he_20_30, he_shell_classification, rof
        FROM bg_reference_guns
        WHERE nation LIKE '%{args.nation}%'
        ORDER BY name
        LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"  {row[0]:30s} HE:{row[1]}/{row[2]}/{row[3]} Class:{row[4]} ROF:{row[5]}")

    conn.close()

    print()
    print("[*] Enrichment complete!")
    print()
    print("Next steps:")
    print("  1. Review enriched data in database")
    print("  2. Run validation: python scripts/battlegroup/manual_extraction/audit_scraped_data.py")
    print("  3. If satisfied, proceed with German enrichment (if Canadian)")

if __name__ == '__main__':
    main()
