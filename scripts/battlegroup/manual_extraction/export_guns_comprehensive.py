#!/usr/bin/env python3
"""
Export Comprehensive Gun Data to CSV

Exports ALL fields from bg_reference_guns for QA and editing.

Usage:
    python export_guns_comprehensive.py --nation canadian --output canadian_guns_comprehensive.csv
    python export_guns_comprehensive.py --nation german --output german_guns_comprehensive.csv
"""

import csv
import sqlite3
import argparse
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def export_guns_to_csv(nation, output_path):
    """Export all gun fields to CSV."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all columns from bg_reference_guns
    cursor.execute("PRAGMA table_info(bg_reference_guns)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    print(f"[*] Exporting {nation} guns...")
    print(f"[*] Database: {DB_PATH}")
    print(f"[*] Output: {output_path}")
    print(f"[*] Columns: {len(column_names)}")
    print()

    # Query all guns for this nation
    cursor.execute(f'''
        SELECT *
        FROM bg_reference_guns
        WHERE nation LIKE '%{nation}%'
        ORDER BY name
    ''')

    guns = cursor.fetchall()

    print(f"[+] Found {len(guns)} {nation} guns")
    print()

    # Write to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(column_names)

        # Write gun data
        for gun in guns:
            writer.writerow(gun)

    print(f"[+] Exported to: {output_path}")
    print()
    print("Columns exported:")
    for i, col_name in enumerate(column_names, 1):
        print(f"  {i:2d}. {col_name}")

    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Export comprehensive gun data to CSV')
    parser.add_argument('--nation', required=True, choices=['canadian', 'german', 'british'], help='Nation to export')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    args = parser.parse_args()

    output_path = Path(args.output)
    export_guns_to_csv(args.nation, output_path)

if __name__ == '__main__':
    main()
