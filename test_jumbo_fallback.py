#!/usr/bin/env python3
"""Test the weapon fallback with Sherman Jumbo"""

import sqlite3
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards_v6_1 import BookDatacardGenerator

DATABASE_PATH = project_root / "database" / "master_database.db"

def test_jumbo():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    generator = BookDatacardGenerator()

    # Test Sherman Jumbo (unlinked vehicle - should use fallback)
    cursor.execute("SELECT id FROM bg_builder_vehicles WHERE name = ?", ('M4A3E2 Sherman Jumbo',))
    jumbo_row = cursor.fetchone()

    if not jumbo_row:
        print("ERROR: Sherman Jumbo not found!")
        return

    equipment = {
        'bg_builder_vehicle_id': jumbo_row['id'],
        'name': 'M4A3E2 Sherman Jumbo',
        'nation_override': 'american'
    }

    print("="*70)
    print("Testing: M4A3E2 Sherman Jumbo (Fallback Test)")
    print("="*70)
    print(f"Vehicle ID: {jumbo_row['id']}")
    print("\nGenerating datacard...\n")

    # Generate datacard
    datacard = generator.generate_datacard_markdown(equipment, 'r')

    # Extract weapon info from generated HTML
    import re

    # Check if main gun is populated
    weapon_match = re.search(r'<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*</tr>', datacard)
    if weapon_match:
        weapon = weapon_match.group(1)
        mount = weapon_match.group(2)
        ammo = weapon_match.group(3)
        print(f"SUCCESS - WEAPON FOUND:")
        print(f"   Name: {weapon}")
        print(f"   Mount: {mount}")
        print(f"   Ammo: {ammo}")

        if weapon == 'None' or weapon == '-':
            print("\nFAIL: Weapon is None (fallback didn't work)")
        elif '75mm' in weapon or '76mm' in weapon:
            print("\nSUCCESS: Fallback weapon lookup working!")
        else:
            print(f"\nWARNING: Unexpected weapon: {weapon}")
    else:
        print("FAIL: Could not find weapon in datacard")

    # Save full datacard to file for inspection
    output_file = project_root / "test_jumbo_output.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Jumbo Test</title></head><body>")
        f.write(datacard)
        f.write("</body></html>")

    print(f"\nFull datacard saved to: {output_file}")

    generator.close()
    conn.close()

if __name__ == "__main__":
    test_jumbo()
