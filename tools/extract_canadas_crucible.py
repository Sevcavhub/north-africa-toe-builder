#!/usr/bin/env python3
"""
Extract vehicles and guns from Battlegroup Canada's Crucible
Check for duplicates against existing database
Import only new entries
"""

import json
import sqlite3
import re
from pathlib import Path

# Define base paths
BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "database" / "master_database.db"
SOURCE_FILE = BASE_DIR / "Resource Documents" / "Battlegroup Game" / "Battlegroup-Canadas-Crucible.txt"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# Armor value mapping (from BattleGroup game rules)
ARMOR_MAP = {
    'H': 13, 'I': 12, 'J': 11, 'K': 10,
    'L': 9, 'M': 8, 'N': 7, 'O': 6
}

def parse_armor_value(armor_str):
    """Parse armor value like 'K', 'N(M)', etc."""
    if not armor_str or armor_str == '-':
        return None
    # Handle cases like 'N(M)' - take the primary value
    match = re.match(r'([A-Z])', armor_str.strip())
    if match:
        letter = match.group(1)
        return ARMOR_MAP.get(letter)
    return None

def classify_vehicle_type(name, special):
    """Classify vehicle type based on name and special characteristics"""
    name_lower = name.lower()

    if any(x in name_lower for x in ['panther', 'panzer iv', 'sherman', 'panzer iii']):
        return 'tank'
    elif any(x in name_lower for x in ['half', 'sdkfz 251']):
        return 'armored_personnel_carrier'
    elif 'carrier' in name_lower and ('bren' in name_lower or 'loyd' in name_lower):
        return 'carrier'
    elif any(x in name_lower for x in ['truck', 'bedford', 'opel', 'jeep']):
        return 'truck'
    elif any(x in name_lower for x in ['sdkfz 222', 'sdkfz 234', 'dingo', 'humber', 'greyhound']):
        return 'armored_car'
    elif any(x in name_lower for x in ['wolverine', 'm10']):
        return 'tank_destroyer'
    elif any(x in name_lower for x in ['wespe', 'hummel']):
        return 'self_propelled_artillery'
    elif 'wirbelwind' in name_lower or 'flakpanzer' in name_lower:
        return 'self_propelled_anti_aircraft'
    elif any(x in name_lower for x in ['sdkfz 250', 'scout']):
        return 'reconnaissance'
    elif 'recovery' in str(special).lower() or 'arv' in name_lower or 'berge' in name_lower:
        return 'recovery_vehicle'
    elif 'bulldozer' in name_lower or 'crab' in name_lower or 'engineer' in str(special).lower():
        return 'engineering_vehicle'
    else:
        return 'other'

def detect_nation(name, section):
    """Detect nation from vehicle name or section"""
    if 'CANADIAN' in section:
        return 'canadian'
    elif 'GERMAN' in section:
        return 'german'
    else:
        return 'unknown'

def extract_vehicles_from_text():
    """Extract all vehicles from the text file using line-by-line parsing"""
    vehicles = []

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_section = None

    # Parse vehicles starting from line 2178 (CANADIAN EQUIPMENT)
    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect section headers
        if 'CANADIAN EQUIPMENT' in line:
            current_section = 'CANADIAN'
            print(f"Found CANADIAN EQUIPMENT section at line {i}")
        elif 'GERMAN EQUIPMENT' in line:
            current_section = 'GERMAN'
            print(f"Found GERMAN EQUIPMENT section at line {i}")

        # Look for VEHICLE header lines
        if current_section and 'VEHICLE' in line and 'MOVEMENT' in line and 'ARMOUR' in line:
            # Next line is column headers (Off-Road, Road, etc.)
            i += 1
            if i >= len(lines):
                break

            # Next line should be blank
            i += 1
            if i >= len(lines):
                break

            # Next line is the vehicle data
            i += 1
            if i >= len(lines):
                break

            data_line = lines[i]

            # Parse the vehicle data line
            # Format: VehicleName   Off-Road  Road  Special  Front  Side  Rear  Weapon  Mount  Ammo
            # Use regex to extract fields

            # First, get the vehicle name (non-digit chars at start)
            match = re.match(r'^([A-Za-z0-9/\s\-\(\)]+?)\s+(\d+)"?\s+(\d+)"?', data_line)
            if match:
                vehicle_name = match.group(1).strip()
                off_road = int(match.group(2))
                road = int(match.group(3))

                # Parse rest of line after the road speed
                rest = data_line[match.end():]
                parts = rest.split()

                special = None
                armor_front = None
                armor_side = None
                armor_rear = None
                weapons = []

                if len(parts) >= 1:
                    special_val = parts[0].strip()
                    if special_val != '-':
                        special = special_val

                # Armor values
                if len(parts) >= 4:
                    armor_front = parse_armor_value(parts[1])
                    armor_side = parse_armor_value(parts[2])
                    armor_rear = parse_armor_value(parts[3])

                # Weapons
                if len(parts) >= 7:
                    weapon = parts[4]
                    mount = parts[5]
                    ammo = parts[6] if parts[6] != '-' else None
                    weapons.append({
                        'weapon': weapon,
                        'mount': mount,
                        'ammo': ammo
                    })

                vehicle = {
                    'name': vehicle_name,
                    'nation': detect_nation(vehicle_name, current_section or ''),
                    'year_range': '1944-1945',
                    'off_road_inches': off_road,
                    'road_inches': road,
                    'special_movement': special,
                    'armor_front': armor_front,
                    'armor_side': armor_side,
                    'armor_rear': armor_rear,
                    'weapons': weapons,
                    'vehicle_type': classify_vehicle_type(vehicle_name, special),
                    'source_file': 'Battlegroup-Canadas-Crucible.txt',
                    'extraction_confidence': 'high'
                }
                vehicles.append(vehicle)
                print(f"  Extracted vehicle: {vehicle_name}")

        i += 1

    return vehicles

def extract_guns_from_text():
    """Extract all guns from the text file"""
    guns = []

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_section = None
    current_category = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect section headers
        if 'CANADIAN GUNS' in line:
            current_section = 'canadian'
            print(f"Found CANADIAN GUNS section at line {i}")
        elif 'GERMAN GUNS' in line:
            current_section = 'german'
            print(f"Found GERMAN GUNS section at line {i}")

        # Detect gun categories
        if current_section:
            if line.strip() in ['MORTARS', 'AUTOCANNONS', 'VERY LIGHT GUNS', 'LIGHT GUNS', 'MEDIUM GUNS', 'HEAVY GUNS']:
                current_category = line.strip()
                print(f"  Found category: {current_category}")

        # Look for gun data lines (starts with weapon name)
        if current_section and current_category:
            # Match lines like: " 75mmL40           HE      4/4+        3       3        3           3      3         -"
            match = re.match(r'^\s+([A-Za-z0-9/\-\(\)\s]+?)\s+(HE|AP)\s+(.+)$', line)
            if match:
                weapon_name = match.group(1).strip()
                ammo_type = match.group(2)
                values_str = match.group(3)

                # Parse HE effect and range values
                parts = values_str.split()

                if ammo_type == 'HE' and len(parts) >= 7:
                    # HE line: effect + 6 range values
                    he_effect = parts[0]
                    he_dice = None
                    he_target = None

                    he_match = re.match(r'(\d+)/(\d+\+)', he_effect)
                    if he_match:
                        he_dice = int(he_match.group(1))
                        he_target = he_match.group(2)

                    # Create or find gun entry
                    existing_gun = None
                    for gun in guns:
                        if gun['name'] == weapon_name and gun['nation'] == current_section:
                            existing_gun = gun
                            break

                    if not existing_gun:
                        # Parse caliber from weapon name
                        caliber_match = re.search(r'(\d+)mm', weapon_name)
                        caliber = int(caliber_match.group(1)) if caliber_match else None

                        # Parse barrel length
                        barrel_match = re.search(r'L(\d+)', weapon_name)
                        barrel_length = f"L{barrel_match.group(1)}" if barrel_match else None

                        gun = {
                            'name': weapon_name,
                            'caliber_mm': caliber,
                            'barrel_length': barrel_length,
                            'he_dice': he_dice,
                            'he_target': he_target,
                            'ap_0_10': None,
                            'ap_10_20': None,
                            'ap_20_30': None,
                            'ap_30_40': None,
                            'ap_40_50': None,
                            'ap_50_70': None,
                            'nation': current_section,
                            'source_file': 'Battlegroup-Canadas-Crucible.txt'
                        }
                        guns.append(gun)
                        print(f"  Extracted gun: {weapon_name} (HE)")

                elif ammo_type == 'AP' and len(parts) >= 6:
                    # AP line: 6 range values
                    ap_values = []
                    for j in range(6):
                        val = parts[j]
                        if val != '-':
                            try:
                                # Handle special cases like "4 (7)*"
                                val_clean = val.split('(')[0].strip()
                                ap_values.append(int(val_clean))
                            except ValueError:
                                ap_values.append(None)
                        else:
                            ap_values.append(None)

                    # Find existing gun and update
                    for gun in guns:
                        if gun['name'] == weapon_name and gun['nation'] == current_section:
                            gun['ap_0_10'] = ap_values[0]
                            gun['ap_10_20'] = ap_values[1]
                            gun['ap_20_30'] = ap_values[2]
                            gun['ap_30_40'] = ap_values[3]
                            gun['ap_40_50'] = ap_values[4]
                            gun['ap_50_70'] = ap_values[5]
                            print(f"  Updated gun with AP: {weapon_name}")
                            break

        i += 1

    return guns

def check_duplicates(extracted_vehicles, extracted_guns):
    """Check for duplicates against existing database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get existing vehicle names
    cursor.execute('SELECT name FROM bg_reference_vehicles')
    existing_vehicle_names = {row[0].lower() for row in cursor.fetchall()}

    # Get existing gun names
    cursor.execute('SELECT name FROM bg_reference_guns')
    existing_gun_names = {row[0].lower() for row in cursor.fetchall()}

    conn.close()

    # Filter out duplicates
    new_vehicles = []
    duplicate_vehicles = []

    for vehicle in extracted_vehicles:
        if vehicle['name'].lower() in existing_vehicle_names:
            duplicate_vehicles.append(vehicle['name'])
        else:
            new_vehicles.append(vehicle)

    new_guns = []
    duplicate_guns = []

    for gun in extracted_guns:
        gun_name_lower = gun['name'].lower()

        if gun_name_lower in existing_gun_names:
            duplicate_guns.append(gun['name'])
        else:
            new_guns.append(gun)

    return new_vehicles, duplicate_vehicles, new_guns, duplicate_guns

def import_to_database(new_vehicles, new_guns):
    """Import new vehicles and guns to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    vehicles_imported = 0
    guns_imported = 0

    # Import vehicles
    for vehicle in new_vehicles:
        try:
            # Convert weapons array to JSON string
            import json as json_lib
            weapons_json = json_lib.dumps(vehicle['weapons']) if vehicle['weapons'] else None

            cursor.execute('''
                INSERT INTO bg_reference_vehicles (
                    name, nation, year_range, vehicle_type,
                    off_road_inches, road_inches, special_movement,
                    armor_front, armor_side, armor_rear,
                    weapons, source_file, extraction_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle['name'],
                vehicle['nation'],
                vehicle['year_range'],
                vehicle['vehicle_type'],
                vehicle['off_road_inches'],
                vehicle['road_inches'],
                vehicle['special_movement'],
                str(vehicle['armor_front']) if vehicle['armor_front'] else None,
                str(vehicle['armor_side']) if vehicle['armor_side'] else None,
                str(vehicle['armor_rear']) if vehicle['armor_rear'] else None,
                weapons_json,
                vehicle['source_file'],
                vehicle['extraction_confidence']
            ))
            vehicles_imported += 1
        except sqlite3.Error as e:
            print(f"Error importing vehicle {vehicle['name']}: {e}")

    # Import guns
    for gun in new_guns:
        try:
            cursor.execute('''
                INSERT INTO bg_reference_guns (
                    name, caliber_mm, barrel_length,
                    he_dice, he_target,
                    ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                    nation, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gun['name'],
                gun['caliber_mm'],
                gun['barrel_length'],
                gun['he_dice'],
                gun['he_target'],
                gun['ap_0_10'],
                gun['ap_10_20'],
                gun['ap_20_30'],
                gun['ap_30_40'],
                gun['ap_40_50'],
                gun['ap_50_70'],
                gun['nation'],
                gun['source_file']
            ))
            guns_imported += 1
        except sqlite3.Error as e:
            print(f"Error importing gun {gun['name']}: {e}")

    conn.commit()
    conn.close()

    return vehicles_imported, guns_imported

def main():
    print("=" * 80)
    print("Extracting Battlegroup Canada's Crucible Data")
    print("=" * 80)

    # Extract vehicles and guns
    print("\n1. Extracting vehicles from text file...")
    extracted_vehicles = extract_vehicles_from_text()
    print(f"   Total found: {len(extracted_vehicles)} vehicles")

    print("\n2. Extracting guns from text file...")
    extracted_guns = extract_guns_from_text()
    print(f"   Total found: {len(extracted_guns)} guns")

    # Check for duplicates
    print("\n3. Checking for duplicates against database...")
    new_vehicles, duplicate_vehicles, new_guns, duplicate_guns = check_duplicates(
        extracted_vehicles, extracted_guns
    )

    print(f"   Vehicles: {len(new_vehicles)} new, {len(duplicate_vehicles)} duplicates")
    print(f"   Guns: {len(new_guns)} new, {len(duplicate_guns)} duplicates")

    # Save extracted data to JSON
    print("\n4. Saving extracted data to JSON files...")

    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    vehicles_output = OUTPUT_DIR / "battlegroup_canadas_crucible_vehicles.json"
    with open(vehicles_output, 'w', encoding='utf-8') as f:
        json.dump(extracted_vehicles, f, indent=2, ensure_ascii=False)
    print(f"   Saved: {vehicles_output}")

    guns_output = OUTPUT_DIR / "battlegroup_canadas_crucible_guns.json"
    with open(guns_output, 'w', encoding='utf-8') as f:
        json.dump(extracted_guns, f, indent=2, ensure_ascii=False)
    print(f"   Saved: {guns_output}")

    # Import new entries
    print("\n5. Importing new entries to database...")
    vehicles_imported, guns_imported = import_to_database(new_vehicles, new_guns)

    print(f"   Imported {vehicles_imported} vehicles")
    print(f"   Imported {guns_imported} guns")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total vehicles extracted:     {len(extracted_vehicles)}")
    print(f"  - New vehicles:             {len(new_vehicles)}")
    print(f"  - Duplicate vehicles:       {len(duplicate_vehicles)}")
    print(f"  - Vehicles imported:        {vehicles_imported}")
    print()
    print(f"Total guns extracted:         {len(extracted_guns)}")
    print(f"  - New guns:                 {len(new_guns)}")
    print(f"  - Duplicate guns:           {len(duplicate_guns)}")
    print(f"  - Guns imported:            {guns_imported}")
    print()

    if duplicate_vehicles:
        print(f"\nDuplicate vehicles: {', '.join(duplicate_vehicles[:20])}")
    if duplicate_guns:
        print(f"\nDuplicate guns: {', '.join(duplicate_guns[:20])}")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
