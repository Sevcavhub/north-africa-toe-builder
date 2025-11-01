#!/usr/bin/env python3
"""
Extract vehicle and gun profiles from Battlegroup Westwall text file.
Includes duplicate detection against existing database.
"""

import json
import re
import sqlite3
from pathlib import Path

# Paths
WESTWALL_FILE = Path("D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Battlegroup-Westwall.txt")
DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
OUTPUT_DIR = Path("D:/north-africa-toe-builder/data/output")

def load_existing_equipment():
    """Load existing vehicles and guns from database to check for duplicates."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    # Get existing vehicles
    existing_vehicles = set()
    try:
        cursor.execute("SELECT name, nation FROM battlegroup_vehicles")
        for row in cursor.fetchall():
            existing_vehicles.add((row[0], row[1]))
    except sqlite3.OperationalError:
        print("Note: battlegroup_vehicles table not found - will create new entries")

    # Get existing guns
    existing_guns = set()
    try:
        cursor.execute("SELECT name, nation FROM battlegroup_guns")
        for row in cursor.fetchall():
            existing_guns.add((row[0], row[1]))
    except sqlite3.OperationalError:
        print("Note: battlegroup_guns table not found - will create new entries")

    conn.close()
    return existing_vehicles, existing_guns

def parse_armor_value(armor_str):
    """Parse armor notation (e.g., 'H', 'M(L)', 'N', 'o')."""
    if not armor_str or armor_str.strip() == '':
        return None
    return armor_str.strip()

def parse_movement(move_str):
    """Parse movement value (e.g., '8"', '12"')."""
    if not move_str:
        return None
    # Remove quotes and convert to int
    match = re.search(r'(\d+)', move_str)
    if match:
        return int(match.group(1))
    return None

def extract_vehicles_from_text(text_content):
    """Extract vehicle profiles from text content."""
    vehicles = []

    # Pattern to match vehicle data tables
    # Looking for: VEHICLE name, then MOVEMENT/ARMOUR/ARMAMENT headers, then data rows

    lines = text_content.split('\n')

    i = 0
    current_nation = None

    while i < len(lines):
        line = lines[i].strip()

        # Detect nation sections
        if 'GERMAN ARMOURED VEHICLE' in line:
            current_nation = 'German'
            print(f"Found German vehicle section at line {i}")
        elif 'US ARMOURED VEHICLE' in line or 'AMERICAN ARMOURED VEHICLE' in line:
            current_nation = 'American'
            print(f"Found American vehicle section at line {i}")

        # Look for vehicle data pattern
        # Typical format has headers: VEHICLE, MOVEMENT (Off-Road, Road), ARMOUR (Front, Side, Rear), ARMAMENT
        if 'VEHICLE' in line and 'MOVEMENT' in line:
            # Found a table header, look for data in next few lines
            j = i + 1
            while j < min(i + 10, len(lines)):
                data_line = lines[j].strip()

                # Skip empty lines and header continuation
                if not data_line or 'Off-Road' in data_line or 'Front' in data_line or 'Weapon' in data_line:
                    j += 1
                    continue

                # Try to parse vehicle data
                # Pattern: Name, off-road, road, special?, armor values, weapons
                parts = re.split(r'\s{2,}', data_line)

                if len(parts) >= 5 and current_nation:
                    vehicle_name = parts[0].strip()

                    # Skip if it looks like a header or empty
                    if not vehicle_name or vehicle_name in ['VEHICLE', 'Off-Road', 'Front']:
                        j += 1
                        continue

                    # Parse the data
                    vehicle = {
                        'name': vehicle_name,
                        'nation': current_nation,
                        'source': 'Battlegroup Westwall',
                        'type': 'AFV',  # Default, refine later
                        'off_road_movement': None,
                        'road_movement': None,
                        'armor_front': None,
                        'armor_side': None,
                        'armor_rear': None,
                        'primary_weapon': None,
                        'weapon_mount': None,
                        'ammo_count': None
                    }

                    # Extract movement values
                    for part in parts[1:]:
                        if '"' in part or '„' in part:
                            move = parse_movement(part)
                            if move and not vehicle['off_road_movement']:
                                vehicle['off_road_movement'] = move
                            elif move and not vehicle['road_movement']:
                                vehicle['road_movement'] = move

                    vehicles.append(vehicle)
                    print(f"  Extracted: {vehicle_name} ({current_nation})")

                j += 1

        i += 1

    return vehicles

def extract_guns_from_text(text_content):
    """Extract gun profiles from text content."""
    guns = []

    lines = text_content.split('\n')

    i = 0
    current_nation = None

    while i < len(lines):
        line = lines[i].strip()

        # Detect nation sections for guns
        if 'GERMAN' in line and ('GUN' in line or 'ARTILLERY' in line or 'AT GUN' in line):
            current_nation = 'German'
            print(f"Found German gun section at line {i}")
        elif ('US' in line or 'AMERICAN' in line) and ('GUN' in line or 'ARTILLERY' in line or 'AT GUN' in line):
            current_nation = 'American'
            print(f"Found American gun section at line {i}")

        # Look for gun data tables
        # Format varies but typically has caliber and penetration data

        i += 1

    return guns

def main():
    print("=" * 80)
    print("BATTLEGROUP WESTWALL EXTRACTION")
    print("=" * 80)

    # Check if database exists
    if not DATABASE_PATH.exists():
        print(f"ERROR: Database not found at {DATABASE_PATH}")
        return

    # Load existing equipment for duplicate detection
    print("\n1. Loading existing database entries...")
    existing_vehicles, existing_guns = load_existing_equipment()
    print(f"   Found {len(existing_vehicles)} existing vehicles")
    print(f"   Found {len(existing_guns)} existing guns")

    # Read Westwall text file
    print("\n2. Reading Westwall text file...")
    with open(WESTWALL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        text_content = f.read()
    print(f"   Read {len(text_content)} characters, {len(text_content.splitlines())} lines")

    # Extract vehicles
    print("\n3. Extracting vehicle profiles...")
    vehicles = extract_vehicles_from_text(text_content)
    print(f"   Extracted {len(vehicles)} vehicles")

    # Extract guns
    print("\n4. Extracting gun profiles...")
    guns = extract_guns_from_text(text_content)
    print(f"   Extracted {len(guns)} guns")

    # Check for duplicates
    print("\n5. Checking for duplicates...")
    new_vehicles = []
    duplicate_vehicles = []

    for vehicle in vehicles:
        key = (vehicle['name'], vehicle['nation'])
        if key in existing_vehicles:
            duplicate_vehicles.append(vehicle)
        else:
            new_vehicles.append(vehicle)

    new_guns = []
    duplicate_guns = []

    for gun in guns:
        key = (gun['name'], gun['nation'])
        if key in existing_guns:
            duplicate_guns.append(gun)
        else:
            new_guns.append(gun)

    print(f"   New vehicles: {len(new_vehicles)}")
    print(f"   Duplicate vehicles: {len(duplicate_vehicles)}")
    print(f"   New guns: {len(new_guns)}")
    print(f"   Duplicate guns: {len(duplicate_guns)}")

    # Save results
    print("\n6. Saving extracted data...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save all vehicles (including duplicates for review)
    vehicles_file = OUTPUT_DIR / "battlegroup_westwall_vehicles.json"
    with open(vehicles_file, 'w', encoding='utf-8') as f:
        json.dump({
            'source': 'Battlegroup Westwall',
            'extraction_date': '2025-10-31',
            'total_extracted': len(vehicles),
            'new_entries': len(new_vehicles),
            'duplicates': len(duplicate_vehicles),
            'vehicles': vehicles,
            'duplicate_list': duplicate_vehicles
        }, f, indent=2)
    print(f"   Saved vehicles to: {vehicles_file}")

    # Save all guns
    guns_file = OUTPUT_DIR / "battlegroup_westwall_guns.json"
    with open(guns_file, 'w', encoding='utf-8') as f:
        json.dump({
            'source': 'Battlegroup Westwall',
            'extraction_date': '2025-10-31',
            'total_extracted': len(guns),
            'new_entries': len(new_guns),
            'duplicates': len(duplicate_guns),
            'guns': guns,
            'duplicate_list': duplicate_guns
        }, f, indent=2)
    print(f"   Saved guns to: {guns_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Vehicles extracted: {len(vehicles)}")
    print(f"  - New: {len(new_vehicles)}")
    print(f"  - Duplicates: {len(duplicate_vehicles)}")
    print(f"\nGuns extracted: {len(guns)}")
    print(f"  - New: {len(new_guns)}")
    print(f"  - Duplicates: {len(duplicate_guns)}")
    print("\nOutput files:")
    print(f"  - {vehicles_file}")
    print(f"  - {guns_file}")

    if duplicate_vehicles:
        print("\nDuplicate vehicles found:")
        for v in duplicate_vehicles:
            print(f"  - {v['name']} ({v['nation']})")

    if duplicate_guns:
        print("\nDuplicate guns found:")
        for g in duplicate_guns:
            print(f"  - {g['name']} ({g['nation']})")

if __name__ == '__main__':
    main()
