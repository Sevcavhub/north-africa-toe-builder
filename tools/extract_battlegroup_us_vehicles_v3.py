#!/usr/bin/env python3
"""
Extract US vehicle profiles from BattleGroup datacard PDF
Uses manual parsing of the text structure
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

    # Look for the pattern:
    # Off-Road  Road    Special FSR Weapon      Mount     Ammo
    # VehicleName Movement_vals Armor Weapons
    # This appears after "VEHICLE MOVEMENT ARMOUR ARMAMENT"

    pattern = r'Off-Road\s+Road\s+Special\s+[FfSsRr]+\s+Weapon\s+Mount\s+Ammo\s*\n([^\n]+)'

    matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)

    for match in matches:
        vehicle_line = match.group(1).strip()
        vehicle = parse_vehicle_line(vehicle_line, full_text, match.start())
        if vehicle:
            vehicles.append(vehicle)
            print(f"[OK] Extracted: {vehicle['name']}")

    return vehicles

def parse_vehicle_line(line, full_text, position):
    """Parse a vehicle data line"""

    # Example lines:
    # "M5  Stuart 12" 18" L N N37mmL53 Turret 12"
    # "M4 Sheman 9" 14" K L N75mmL40 Turret 9"
    # "M4A3E8 10" 15" HVSS K L M 76mmL53MGMG TurretCo-axialHu]] 7"

    # Clean up the line
    line = line.replace('�', '"').replace('`', "'")

    # Extract vehicle name (starts with alphanumeric, may have spaces/dashes)
    name_match = re.match(r'^([A-Z0-9]+(?:\s+[A-Z0-9]+)*(?:\s+[A-Za-z\'\-`]+)*?)\s+(\d+)', line)
    if not name_match:
        return None

    name = name_match.group(1).strip()

    # Clean up common OCR errors in names
    name = name.replace('Sheman', 'Sherman')
    name = name.replace('Call,Ope', 'Calliope')
    name = name.replace('Prlest', 'Priest')

    # Extract movement (inches)
    movement_pattern = r'(\d+)["\s]+(\d+)["\s]+'
    movement_match = re.search(movement_pattern, line)
    if not movement_match:
        return None

    off_road = int(movement_match.group(1))
    road = int(movement_match.group(2))

    # Check for special movement indicator
    special = None
    after_movement = line[movement_match.end():].strip()

    # Special movement keywords
    special_keywords = ['HVSS', 'Engineer', 'Open-topped', 'Amphibious', 'Half-track']
    for keyword in special_keywords:
        if after_movement.startswith(keyword):
            special = keyword
            after_movement = after_movement[len(keyword):].strip()
            break

    # Extract armor (3 single letters)
    armor_pattern = r'([A-O])\s*([A-O])\s*([A-O])'
    armor_match = re.search(armor_pattern, after_movement)
    if not armor_match:
        return None

    armor_front = armor_match.group(1)
    armor_side = armor_match.group(2)
    armor_rear = armor_match.group(3)

    after_armor = after_movement[armor_match.end():].strip()

    # Extract weapons
    weapons = []

    # Parse weapons from remaining line
    # Format: WeaponName Mount [Ammo]
    # Multiple weapons may be concatenated: "75mmL40MGMG TurretCo-axialHull 9"

    weapon_tokens = re.findall(r'([\d.]+mm[A-Z]*\d*|MG|HMG|Flamethrower|[\d.]+"\s*launcher)([A-Za-z\-]+)?(\d+)?', after_armor)

    for weapon, mount, ammo in weapon_tokens:
        if weapon and mount:
            weapons.append({
                'weapon': weapon.strip(),
                'mount': mount.strip(),
                'ammo': int(ammo) if ammo else None
            })

    # Alternative: look for Mount keywords separately
    if not weapons:
        mount_keywords = ['Turret', 'Co-axial', 'Hull', 'Fixed', 'Pintle', 'Open-topped']
        for keyword in mount_keywords:
            if keyword in after_armor:
                # Find weapon before this mount
                before_mount = after_armor[:after_armor.index(keyword)].strip()
                weapon_match = re.search(r'([\d.]+mm[A-Z]*\d*|MG|HMG|Flamethrower|[\d.]+"\s*launcher)\s*$', before_mount)
                if weapon_match:
                    # Find ammo after mount
                    after_mount = after_armor[after_armor.index(keyword) + len(keyword):].strip()
                    ammo_match = re.match(r'^\s*(\d+)', after_mount)
                    weapons.append({
                        'weapon': weapon_match.group(1),
                        'mount': keyword,
                        'ammo': int(ammo_match.group(1)) if ammo_match else None
                    })

    # Find year range by looking backwards in text
    year_range = None
    text_before = full_text[max(0, position - 300):position]
    year_match = re.search(r'(\d{4})(-\d{4})?', text_before)
    if year_match:
        year_range = year_match.group(0)

    return {
        'name': name,
        'year_range': year_range,
        'off_road_inches': off_road,
        'road_inches': road,
        'special_movement': special,
        'armor_front': armor_front,
        'armor_side': armor_side,
        'armor_rear': armor_rear,
        'weapons': weapons if weapons else []
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
        year_str = v['year_range'] or 'N/A'
        print(f"  - {v['name']:30} ({year_str:10}) Armor:{v['armor_front']}/{v['armor_side']}/{v['armor_rear']} Movement:{v['off_road_inches']}\"{v['road_inches']}\" Weapons:{weapons_str}")

    # Also print full JSON of first vehicle as example
    if vehicles:
        print(f"\nExample vehicle (JSON):")
        print(json.dumps(vehicles[0], indent=2))

if __name__ == '__main__':
    main()
