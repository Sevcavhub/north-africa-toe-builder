#!/usr/bin/env python3
"""
Extract Battlegroup Wacht Am Rhein vehicle and gun equipment.

This supplement primarily references Battlegroup Overlord for datacards,
but includes army lists for Volksgrenadier Division. It covers the Battle
of the Bulge (December 1944-January 1945) in the Ardennes.

Expected equipment:
- German: Panther, Panzer IV, StuG III, Hetzer, Tigers
- American: M4 Sherman, M5 Stuart, M10, M36, M18
"""

import json
import re
import sqlite3
from pathlib import Path

# File paths
WACHT_AM_RHEIN_FILE = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-Wacht-Am-Rhein.txt")
DATABASE_FILE = Path(r"D:\north-africa-toe-builder\database\master_database.db")
OUTPUT_DIR = Path(r"D:\north-africa-toe-builder\data\output")

def load_existing_equipment(db_path):
    """Load existing vehicles and guns from database for duplicate detection."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if battlegroup tables exist
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ('battlegroup_vehicles', 'battlegroup_guns')
    """)
    tables = [row[0] for row in cursor.fetchall()]

    existing_vehicles = {}
    existing_guns = {}

    if 'battlegroup_vehicles' in tables:
        cursor.execute("SELECT name, nation FROM battlegroup_vehicles")
        for name, nation in cursor.fetchall():
            key = f"{name}||{nation}"
            existing_vehicles[key] = True

    if 'battlegroup_guns' in tables:
        cursor.execute("SELECT name, nation FROM battlegroup_guns")
        for name, nation in cursor.fetchall():
            key = f"{name}||{nation}"
            existing_guns[key] = True

    conn.close()

    return existing_vehicles, existing_guns

def read_file_content(file_path):
    """Read the text file content."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_army_list_equipment(content):
    """
    Extract equipment mentions from army lists.

    Wacht Am Rhein references Battlegroup Overlord for most datacards.
    We extract unit names and nations from the Volksgrenadier army list.
    """
    vehicles = []
    guns = []

    # Find Volksgrenadier army list section (lines 1880-2150 approximately)
    army_list_match = re.search(
        r'VOLKSGRENADIER.*?DIVISION.*?BATTLEGROUP(.*?)(?:RECONNAISSANCE|$)',
        content,
        re.DOTALL | re.IGNORECASE
    )

    if army_list_match:
        army_list_section = army_list_match.group(1)

        # Extract tank entries - German vehicles
        tank_patterns = [
            r'(StuG III G)',
            r'(StuG IV)',
            r'(Hetzer)',
            r'(Panzer IV [GH])',
            r'(Panther [AG])',
        ]

        for pattern in tank_patterns:
            matches = re.findall(pattern, army_list_section)
            for match in matches:
                name = match.strip()
                if name:
                    vehicles.append({
                        'name': name,
                        'nation': 'german',
                        'source': 'Wacht Am Rhein Volksgrenadier Division',
                        'type': 'AFV'
                    })

        # Extract captured US vehicles mentioned
        captured_patterns = [
            r'(M5 Stuart)',
            r'(M4 Sherman \(75mm\))',
            r'(M4 Sherman \(76mm\))',
            r'(M10 Wolverine)',
        ]

        for pattern in captured_patterns:
            matches = re.findall(pattern, army_list_section)
            for match in matches:
                name = match.strip()
                if name:
                    # These are captured vehicles used by Germans
                    vehicles.append({
                        'name': name,
                        'nation': 'american',
                        'source': 'Wacht Am Rhein (captured)',
                        'type': 'AFV'
                    })

        # Extract artillery/guns
        gun_patterns = [
            r'(\d+mm\w+\s+(?:Light\s+)?Howitzer)',
            r'(\d+mm\w+\s+Field\s+Gun)',
            r'(PaK\s*\d+(?:/\d+)?(?:\([a-z]\))?)',
            r'(\d+mm\s+infantry\s+gun)',
            r'(\d+mm\s+mortar)',
            r'(\d+mm\s+Nebelwerfer)',
        ]

        for pattern in gun_patterns:
            matches = re.findall(pattern, army_list_section, re.IGNORECASE)
            for match in matches:
                name = match.strip()
                if name and not name.startswith('2 '):  # Skip battery listings
                    # Normalize gun names
                    name = re.sub(r'(\d+)mm(\w)', r'\1mm \2', name)
                    guns.append({
                        'name': name,
                        'nation': 'german',
                        'source': 'Wacht Am Rhein Volksgrenadier Division',
                        'type': 'Artillery'
                    })

    # Also check scenario sections for vehicle mentions
    scenario_section = re.search(
        r'BATTLES IN THE BULGE(.*?)(?:AFTERMATH|$)',
        content,
        re.DOTALL
    )

    if scenario_section:
        scenario_text = scenario_section.group(1)

        # Extract vehicles from scenario forces
        scenario_vehicles = [
            r'(Panther G)',
            r'(M4 Sherman)',
            r'(SdKfz \d+/\d+)',
        ]

        for pattern in scenario_vehicles:
            matches = re.findall(pattern, scenario_text)
            for match in matches:
                name = match.strip()
                nation = 'german' if 'SdKfz' in name or 'Panther' in name else 'american'
                if name:
                    vehicles.append({
                        'name': name,
                        'nation': nation,
                        'source': 'Wacht Am Rhein Scenarios',
                        'type': 'AFV'
                    })

    return vehicles, guns

def deduplicate_equipment(equipment_list):
    """Remove duplicates while preserving order."""
    seen = set()
    unique = []

    for item in equipment_list:
        key = f"{item['name']}||{item['nation']}"
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique

def filter_new_equipment(vehicles, guns, existing_vehicles, existing_guns):
    """Filter out equipment that already exists in database."""
    new_vehicles = []
    new_guns = []
    skipped_vehicles = []
    skipped_guns = []

    for vehicle in vehicles:
        key = f"{vehicle['name']}||{vehicle['nation']}"
        if key not in existing_vehicles:
            new_vehicles.append(vehicle)
        else:
            skipped_vehicles.append(vehicle)

    for gun in guns:
        key = f"{gun['name']}||{gun['nation']}"
        if key not in existing_guns:
            new_guns.append(gun)
        else:
            skipped_guns.append(gun)

    return new_vehicles, new_guns, skipped_vehicles, skipped_guns

def main():
    """Main extraction process."""
    print("=" * 80)
    print("BATTLEGROUP WACHT AM RHEIN EXTRACTION")
    print("=" * 80)
    print()

    # Load existing equipment
    print("Loading existing equipment from database...")
    existing_vehicles, existing_guns = load_existing_equipment(DATABASE_FILE)
    print(f"  Found {len(existing_vehicles)} existing vehicles")
    print(f"  Found {len(existing_guns)} existing guns")
    print()

    # Read source file
    print("Reading Wacht Am Rhein text file...")
    content = read_file_content(WACHT_AM_RHEIN_FILE)
    print(f"  File size: {len(content):,} characters")
    print()

    # Extract equipment
    print("Extracting equipment from army lists and scenarios...")
    vehicles, guns = extract_army_list_equipment(content)

    # Deduplicate
    vehicles = deduplicate_equipment(vehicles)
    guns = deduplicate_equipment(guns)

    print(f"  Extracted {len(vehicles)} unique vehicles")
    print(f"  Extracted {len(guns)} unique guns")
    print()

    # Filter new equipment
    print("Filtering for new equipment not in database...")
    new_vehicles, new_guns, skipped_v, skipped_g = filter_new_equipment(
        vehicles, guns, existing_vehicles, existing_guns
    )
    print(f"  NEW vehicles: {len(new_vehicles)}")
    print(f"  NEW guns: {len(new_guns)}")
    print(f"  Skipped (already in DB) vehicles: {len(skipped_v)}")
    print(f"  Skipped (already in DB) guns: {len(skipped_g)}")
    print()

    # Save outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    vehicles_file = OUTPUT_DIR / "battlegroup_wacht_am_rhein_vehicles.json"
    guns_file = OUTPUT_DIR / "battlegroup_wacht_am_rhein_guns.json"

    with open(vehicles_file, 'w', encoding='utf-8') as f:
        json.dump({
            'source': 'Battlegroup Wacht Am Rhein',
            'theater': 'Western Europe - Ardennes',
            'period': 'December 1944 - January 1945',
            'extraction_date': '2025-10-31',
            'new_vehicles': new_vehicles,
            'skipped_vehicles': skipped_v,
            'total_new': len(new_vehicles),
            'total_skipped': len(skipped_v)
        }, f, indent=2)

    with open(guns_file, 'w', encoding='utf-8') as f:
        json.dump({
            'source': 'Battlegroup Wacht Am Rhein',
            'theater': 'Western Europe - Ardennes',
            'period': 'December 1944 - January 1945',
            'extraction_date': '2025-10-31',
            'new_guns': new_guns,
            'skipped_guns': skipped_g,
            'total_new': len(new_guns),
            'total_skipped': len(skipped_g)
        }, f, indent=2)

    print("Output files created:")
    print(f"  {vehicles_file}")
    print(f"  {guns_file}")
    print()

    # Summary
    print("=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    if new_vehicles:
        print("\nNEW VEHICLES:")
        for v in new_vehicles:
            print(f"  - {v['name']} ({v['nation']})")

    if new_guns:
        print("\nNEW GUNS:")
        for g in new_guns:
            print(f"  - {g['name']} ({g['nation']})")

    if skipped_v:
        print(f"\nSKIPPED VEHICLES (already in database): {len(skipped_v)}")

    if skipped_g:
        print(f"\nSKIPPED GUNS (already in database): {len(skipped_g)}")

    print()
    print("=" * 80)
    print(f"TOTAL NEW EQUIPMENT: {len(new_vehicles)} vehicles + {len(new_guns)} guns = {len(new_vehicles) + len(new_guns)}")
    print("=" * 80)

    return {
        'new_vehicles': len(new_vehicles),
        'new_guns': len(new_guns),
        'skipped_vehicles': len(skipped_v),
        'skipped_guns': len(skipped_g)
    }

if __name__ == '__main__':
    main()
