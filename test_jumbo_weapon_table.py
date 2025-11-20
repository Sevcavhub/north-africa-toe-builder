#!/usr/bin/env python3
"""Test Sherman Jumbo weapon performance table with V6.1 fallback fix"""

import sqlite3
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards_v6 import BookDatacardGenerator

DATABASE_PATH = project_root / "database" / "master_database.db"

def test_jumbo_weapon_table():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    generator = BookDatacardGenerator()

    # Sherman Jumbo test
    cursor.execute("SELECT id FROM bg_builder_vehicles WHERE name = ?", ('M4A3E2 Sherman Jumbo',))
    jumbo_row = cursor.fetchone()

    equipment = {
        'bg_builder_vehicle_id': jumbo_row['id'],
        'name': 'M4A3E2 Sherman Jumbo',
        'nation_override': 'american'
    }

    print("="*70)
    print("Testing: M4A3E2 Sherman Jumbo - Weapon Performance Table")
    print("="*70)

    datacard = generator.generate_datacard_markdown(equipment, 'r')

    # Check for weapon name in Table 1
    if '75mmL40' in datacard:
        print("SUCCESS: Table 1 has weapon name (75mmL40)")
    else:
        print("FAIL: Table 1 missing weapon name")

    # Check for HE data in Table 2
    if 'D6 HE' in datacard:
        print("SUCCESS: Table 2 has HE data")
    else:
        print("FAIL: Table 2 missing HE data")

    # Check for AP data in Table 2
    import re
    ap_pattern = r'\d+/\d+/\d+'  # Pattern like "5/5/4/3"
    if re.search(ap_pattern, datacard):
        print("SUCCESS: Table 2 has AP penetration data")
    else:
        print("FAIL: Table 2 missing AP penetration data")

    # Save output
    output_file = project_root / "test_jumbo_weapon_fix.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Jumbo Weapon Fix</title></head><body>")
        f.write(datacard)
        f.write("</body></html>")

    print(f"\nFull datacard saved to: {output_file}")
    print("\nExpected Table 2 data:")
    print("  Weapon: 75mmL40")
    print("  HE: 6D6 HE")
    print("  AP: 5/5/4/3/2 (or similar)")

    generator.close()
    conn.close()

if __name__ == "__main__":
    test_jumbo_weapon_table()
