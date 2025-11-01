#!/usr/bin/env python3
"""
Extract US vehicle profiles from BattleGroup datacard PDF
Parses the standard datacard format with VEHICLE/MOVEMENT/ARMOUR/ARMAMENT tables
"""

import json
import re
import sys
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("Installing PyPDF2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2

def extract_vehicles(pdf_path):
    """Extract all vehicle profiles from PDF"""
    vehicles = []

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        # Combine all pages
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"

    # Split by VEHICLE keyword to find datacards
    vehicle_sections = re.split(r'VEHICLE\s+MOVEMENT\s+ARMOUR\s+ARMAMENT', full_text)

    print(f"Found {len(vehicle_sections) - 1} potential vehicle entries")

    for section in vehicle_sections[1:]:  # Skip first empty section
        vehicle = parse_vehicle_section(section)
        if vehicle:
            vehicles.append(vehicle)
            print(f"✓ Extracted: {vehicle['name']}")

    return vehicles

def parse_vehicle_section(section):
    """Parse a single vehicle datacard section"""
    lines = [l.strip() for l in section.split('\n') if l.strip()]

    if len(lines) < 2:
        return None

    # First line: Off-Road Road Special F S R Weapon Mount Ammo
    # Second line: Vehicle name, movement values, armor values, weapon data

    # Get the vehicle data line (typically line 1)
    data_line = lines[0] if lines else ""

    # Pattern: Vehicle_Name Movement_Vals Armor_Vals Weapon_Data
    # Example: "M5  Stuart 12" 18" L N N37mmL53 Turret 12"
    # Example: "M4 Sheman 9" 14" K L N75mmL40 Turret 9"

    # Extract vehicle name (first word(s) before numbers)
    name_match = re.match(r'^([A-Z0-9]+\s*[A-Z0-9]*\s*[A-Za-z`\'\-]*)', data_line)
    if not name_match:
        return None

    vehicle_name = name_match.group(1).strip()
    remaining = data_line[len(vehicle_name):].strip()

    # Extract movement values: two numbers with " marks or spaces
    movement_match = re.search(r'(\d+)["\s�]+(\d+)["\s�]+', remaining)
    if not movement_match:
        return None

    off_road = int(movement_match.group(1))
    road = int(movement_match.group(2))

    # Move past movement data
    remaining = remaining[movement_match.end():].strip()

    # Check for special movement (some vehicles have HVSS, Engineer, etc.)
    special_movement = None
    special_match = re.match(r'^([A-Za-z\-]+)\s+', remaining)
    if special_match and special_match.group(1) not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']:
        special_movement = special_match.group(1)
        remaining = remaining[len(special_movement):].strip()

    # Extract armor values: 3 letters (F S R)
    armor_match = re.match(r'^([A-O])\s*([A-O])\s*([A-O])\s*', remaining)
    if not armor_match:
        return None

    armor_front = armor_match.group(1)
    armor_side = armor_match.group(2)
    armor_rear = armor_match.group(3)

    remaining = remaining[armor_match.end():].strip()

    # Extract weapons
    weapons = []

    # First weapon is usually in the data line
    weapon_match = re.match(r'^([\d.]+mm[A-Z]*\d*|MG|HMG|Flamethrower|[\d.]+"\s*launcher)\s*([A-Za-z\-]+)\s*(\d+)?', remaining)
    if weapon_match:
        weapons.append({
            'weapon': weapon_match.group(1),
            'mount': weapon_match.group(2),
            'ammo': int(weapon_match.group(3)) if weapon_match.group(3) else None
        })
        remaining = remaining[weapon_match.end():].strip()

    # Additional weapons may be on following lines
    for line in lines[1:5]:  # Check next few lines
        # Skip lines that are headers or weapon stats tables
        if any(keyword in line for keyword in ['WEAPON', 'AMMO', 'RANGE', 'HE', 'AP', '0-10"', 'Off-Road']):
            continue

        # Look for weapon patterns
        weapon_match = re.search(r'([\d.]+mm[A-Z]*\d*|MG|HMG|Flamethrower|[\d.]+"\s*launcher)\s*([A-Za-z\-]+)\s*(\d+)?', line)
        if weapon_match:
            weapon_name = weapon_match.group(1).strip()
            mount = weapon_match.group(2).strip()
            ammo = int(weapon_match.group(3)) if weapon_match.group(3) else None

            # Avoid duplicates
            if not any(w['weapon'] == weapon_name and w['mount'] == mount for w in weapons):
                weapons.append({
                    'weapon': weapon_name,
                    'mount': mount,
                    'ammo': ammo
                })

    # Try to find year range in nearby text
    year_range = None
    for line in lines[:10]:
        year_match = re.search(r'(\d{4})(-\d{4})?', line)
        if year_match:
            year_range = year_match.group(0)
            break

    # Look backwards in the original section for year (before VEHICLE header)
    section_before = section[:200]  # Look at text before the data table
    if not year_range:
        year_match = re.search(r'(\d{4})(-\d{4})?', section_before)
        if year_match:
            year_range = year_match.group(0)

    return {
        'name': vehicle_name,
        'year_range': year_range,
        'off_road_inches': off_road,
        'road_inches': road,
        'special_movement': special_movement,
        'armor_front': armor_front,
        'armor_side': armor_side,
        'armor_rear': armor_rear,
        'weapons': weapons
    }

def main():
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-US.pdf")

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        sys.exit(1)

    print("Extracting US vehicle profiles from BattleGroup datacard PDF...")
    print()

    vehicles = extract_vehicles(pdf_path)

    print()
    print(f"{'='*60}")
    print(f"Extracted {len(vehicles)} vehicle profiles")
    print(f"{'='*60}")

    # Save to JSON
    output_path = Path(r"D:\north-africa-toe-builder\data\output\battlegroup_us_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vehicles, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {output_path}")

    # Print summary
    print(f"\nVehicle Summary:")
    for v in vehicles:
        weapons_str = ', '.join([w['weapon'] for w in v['weapons']])
        print(f"  - {v['name']:25} ({v['year_range'] or 'N/A':10}) Armor:{v['armor_front']}/{v['armor_side']}/{v['armor_rear']} Weapons:{weapons_str}")

if __name__ == '__main__':
    main()
