#!/usr/bin/env python3
"""
Extract US vehicle profiles from BattleGroup datacard PDF
Handles large PDFs by processing page-by-page
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

def extract_vehicle_data(pdf_path):
    """Extract all vehicle profiles from PDF"""
    vehicles = []

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)
        print(f"Processing {total_pages} pages...")

        for page_num in range(total_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            # Process text to find vehicle entries
            # BattleGroup format typically has:
            # Vehicle Name
            # Year range
            # Movement stats
            # Armor values
            # Weapons list

            # Look for vehicle patterns
            lines = text.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Vehicle name pattern (typically all caps or mixed case)
                # Followed by year range like "1942-1945" or "1944"
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()

                    # Check if this looks like a year range
                    year_match = re.search(r'(\d{4}(-\d{4})?)', next_line)

                    if year_match and len(line) > 2 and not line.isdigit():
                        vehicle = extract_vehicle_entry(lines, i)
                        if vehicle:
                            vehicles.append(vehicle)
                            print(f"Found: {vehicle['name']}")

                i += 1

    return vehicles

def extract_vehicle_entry(lines, start_idx):
    """Extract single vehicle entry from text lines"""
    vehicle = {}

    # Get vehicle name
    name = lines[start_idx].strip()

    # Skip if this doesn't look like a vehicle name
    if len(name) < 3 or name.isdigit():
        return None

    vehicle['name'] = name

    # Try to get year range from next few lines
    year_range = None
    movement_data = None
    armor_data = None
    weapons = []

    for offset in range(1, min(15, len(lines) - start_idx)):
        line = lines[start_idx + offset].strip()

        # Year range pattern
        if not year_range:
            year_match = re.search(r'(\d{4})(-\d{4})?', line)
            if year_match:
                year_range = year_match.group(0)

        # Movement pattern: numbers followed by inch marks or numbers
        # e.g., "9\" 14\" -" or "9 14 -"
        if not movement_data:
            movement_match = re.search(r'(\d+)["\s]+(\d+)["\s]+(.+)?', line)
            if movement_match:
                movement_data = {
                    'off_road': int(movement_match.group(1)),
                    'road': int(movement_match.group(2)),
                    'special': movement_match.group(3).strip() if movement_match.group(3) else None
                }

        # Armor pattern: typically 3 letters (A-O)
        # e.g., "K L N" or "KLN"
        if not armor_data:
            armor_match = re.search(r'\b([A-O])\s+([A-O])\s+([A-O])\b', line)
            if armor_match:
                armor_data = {
                    'front': armor_match.group(1),
                    'side': armor_match.group(2),
                    'rear': armor_match.group(3)
                }

        # Weapon pattern: caliber + mount type + ammo count
        # e.g., "75mmL40 Turret 9" or "MG Co-axial"
        weapon_match = re.search(r'([\d.]+mm[A-Z]*\d*|MG|HMG|LMG)\s+(Turret|Co-axial|Hull|Fixed|Pintle)\s*(\d+)?', line)
        if weapon_match:
            weapons.append({
                'weapon': weapon_match.group(1),
                'mount': weapon_match.group(2),
                'ammo': int(weapon_match.group(3)) if weapon_match.group(3) else None
            })

    # Only return if we got core data
    if year_range and movement_data and armor_data:
        vehicle['year_range'] = year_range
        vehicle['off_road_inches'] = movement_data['off_road']
        vehicle['road_inches'] = movement_data['road']
        vehicle['special_movement'] = movement_data['special'] if movement_data['special'] and movement_data['special'] != '-' else None
        vehicle['armor_front'] = armor_data['front']
        vehicle['armor_side'] = armor_data['side']
        vehicle['armor_rear'] = armor_data['rear']
        vehicle['weapons'] = weapons if weapons else []

        return vehicle

    return None

def main():
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-US.pdf")

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        sys.exit(1)

    print("Extracting US vehicle profiles from BattleGroup datacard PDF...")
    vehicles = extract_vehicle_data(pdf_path)

    print(f"\n{'='*60}")
    print(f"Extracted {len(vehicles)} vehicle profiles")
    print(f"{'='*60}\n")

    # Save to JSON
    output_path = Path(r"D:\north-africa-toe-builder\data\output\battlegroup_us_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vehicles, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {output_path}")

    # Print sample
    if vehicles:
        print(f"\nSample vehicle:")
        print(json.dumps(vehicles[0], indent=2))

if __name__ == '__main__':
    main()
