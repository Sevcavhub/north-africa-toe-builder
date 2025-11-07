#!/usr/bin/env python3
"""
Export Canadian and German guns in the same format as British CSV for easy review.

Column order matches: british_datacards_ALL_GUNS_UPDATED.csv
"""

import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def export_guns_for_review(nation: str, output_file: str):
    """Export guns in British CSV column order"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Column order matching British CSV
    columns = [
        'name',
        'common_name',
        'nation',
        'caliber_mm',
        'rof',  # Note: ROF uppercase in British CSV
        'he_dice',
        'he_target',
        'he_shell_classification',
        'he_0_10',
        'he_10_20',
        'he_20_30',
        'he_30_40',
        'he_40_50',
        'he_50_70',
        'ap_0_10',
        'ap_10_20',
        'ap_20_30',
        'ap_30_40',
        'ap_40_50',
        'ap_50_70'
    ]

    # Query guns
    cursor.execute(f"""
        SELECT {', '.join(columns)}
        FROM bg_reference_guns
        WHERE nation = ?
        ORDER BY caliber_mm, name
    """, (nation,))

    rows = cursor.fetchall()

    # Write CSV
    output_path = Path(__file__).parent.parent.parent.parent / output_file

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header - use ROF uppercase to match British format
        header = columns.copy()
        header[4] = 'ROF'  # Uppercase for consistency
        writer.writerow(header)

        # Data rows
        for row in rows:
            # Convert None to empty string for CSV
            clean_row = ['' if val is None else val for val in row]
            writer.writerow(clean_row)

    conn.close()

    print(f"[+] Exported {len(rows)} {nation} guns to: {output_file}")
    print(f"    Column order matches: british_datacards_ALL_GUNS_UPDATED.csv")

    return len(rows)

def main():
    print("="*80)
    print("EXPORT GUNS FOR REVIEW")
    print("="*80)
    print("Format matches: british_datacards_ALL_GUNS_UPDATED.csv")
    print()

    canadian_count = export_guns_for_review('canadian', 'canadian_guns_review.csv')
    german_count = export_guns_for_review('german', 'german_guns_review.csv')

    print()
    print("="*80)
    print("EXPORT COMPLETE")
    print("="*80)
    print(f"Canadian guns: {canadian_count} guns → canadian_guns_review.csv")
    print(f"German guns:   {german_count} guns → german_guns_review.csv")
    print()
    print("Next steps:")
    print("  1. Open CSVs in Excel/spreadsheet")
    print("  2. Compare with Crucible PDF datacards")
    print("  3. Make corrections as needed")
    print("  4. Add missing mortars if needed")
    print("  5. Save and re-import")

if __name__ == '__main__':
    main()
