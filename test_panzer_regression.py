#!/usr/bin/env python3
"""Test regression with Panzer III H (linked vehicle)"""

import sqlite3
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards_v6_1 import BookDatacardGenerator

DATABASE_PATH = project_root / "database" / "master_database.db"

def test_panzer_regression():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    generator = BookDatacardGenerator()

    # Find Panzer III H (should be linked in bg_reference_vehicles)
    cursor.execute("""
        SELECT bgv.id, bgv.name, bref.weapon_1
        FROM bg_builder_vehicles bgv
        LEFT JOIN bg_reference_vehicles bref ON bref.bg_builder_id = bgv.id
        WHERE bgv.name LIKE '%Panzer III%' AND bref.weapon_1 IS NOT NULL
        LIMIT 1
    """)
    panzer_row = cursor.fetchone()

    if not panzer_row:
        print("WARNING: No linked Panzer III found, trying any Panzer III...")
        cursor.execute("SELECT id, name FROM bg_builder_vehicles WHERE name LIKE '%Panzer III%' LIMIT 1")
        panzer_row = cursor.fetchone()
        if not panzer_row:
            print("ERROR: No Panzer III found!")
            return

    equipment = {
        'bg_builder_vehicle_id': panzer_row['id'],
        'name': panzer_row['name'],
        'nation_override': 'german'
    }

    print("="*70)
    print(f"Testing: {panzer_row['name']} (Regression Test)")
    print("="*70)
    print(f"Vehicle ID: {panzer_row['id']}")
    if 'weapon_1' in panzer_row.keys() and panzer_row['weapon_1']:
        print(f"Expected weapon from bg_reference_vehicles: {panzer_row['weapon_1']}")
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
            print("\nFAIL: Weapon is None")
        else:
            print("\nSUCCESS: Weapon populated correctly!")
            if 'weapon_1' in panzer_row.keys() and panzer_row['weapon_1']:
                if panzer_row['weapon_1'] in weapon:
                    print(f"VERIFIED: Matches expected weapon from bg_reference_vehicles")
                else:
                    print(f"NOTE: Different from bg_reference_vehicles ({panzer_row['weapon_1']})")
    else:
        print("FAIL: Could not find weapon in datacard")

    # Save full datacard to file for inspection
    output_file = project_root / "test_panzer_output.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Panzer Test</title></head><body>")
        f.write(datacard)
        f.write("</body></html>")

    print(f"\nFull datacard saved to: {output_file}")

    generator.close()
    conn.close()

if __name__ == "__main__":
    test_panzer_regression()
