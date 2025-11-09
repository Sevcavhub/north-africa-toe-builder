#!/usr/bin/env python3
"""
Parse Jane's WWII Tanks Guide - Version 2
Improved vehicle-ammunition association

Strategy:
1. Split text into vehicle sections (based on vehicle name headers)
2. For each section, extract:
   - Vehicle name from header
   - Ammunition capacity from description
   - Specs from table (weight, armor, etc.)
3. Create structured output with confident vehicle-ammo associations

Pattern: Vehicle sections typically structured as:
  [Vehicle Name Header]
  [Description paragraph with "X rounds" mention]
  [Spec table with Weight, Armor, etc.]
"""

import re
from pathlib import Path
import csv
import json

JANES_PATH = Path("Resource Documents/Janes-WorldWarIiTanksAndFightingVehicles-TheCompleteGuide-text-pdf.txt")


def split_into_sections(text):
    """
    Split text into vehicle sections based on patterns.

    Headers typically look like:
    - "Mark VI Tetrarch light tank"
    - "M3 Stuart"
    - "Panzer IV"
    - "Valentine Mk II"
    """

    # Common vehicle type keywords
    vehicle_types = [
        r'tank', r'Tank', r'TANK',
        r'carrier', r'Carrier',
        r'car', r'Car',
        r'vehicle', r'Vehicle',
        r'halftrack', r'Halftrack',
        r'Panzer', r'PzKw',
        r'gun', r'Gun',
        r'howitzer', r'Howitzer'
    ]

    sections = []
    current_section = {'name': None, 'text': '', 'start_line': 0}

    lines = text.split('\n')

    for i, line in enumerate(lines):
        # Check if this line is a potential vehicle header
        # Criteria: Contains vehicle type keyword and is relatively short (< 80 chars)
        is_header = False

        if len(line.strip()) < 80 and len(line.strip()) > 5:
            for vtype in vehicle_types:
                if re.search(vtype, line):
                    # Additional checks: line shouldn't have too many words
                    words = line.strip().split()
                    if 2 <= len(words) <= 8:
                        is_header = True
                        break

        if is_header and current_section['text']:
            # Save previous section
            sections.append(current_section)
            current_section = {'name': line.strip(), 'text': line + '\n', 'start_line': i + 1}
        else:
            current_section['text'] += line + '\n'

    # Save last section
    if current_section['text']:
        sections.append(current_section)

    return sections


def extract_ammunition_from_section(section_text):
    """Extract ammunition count from section text."""

    # Patterns for ammunition
    patterns = [
        r'(\d+)\s+rounds',                    # "50 rounds"
        r'with\s+(\d+)\s+rounds',             # "with 50 rounds"
        r'\((\d+)\s+rounds\)',                # "(50 rounds)"
        r'carried\s+(\d+)\s+rounds',          # "carried 50 rounds"
        r'stowed\s+(\d+)\s+rounds',           # "stowed 50 rounds"
        r'provided.*?(\d+)\s+rounds',         # "provided with 50 rounds"
        r'ammunition.*?(\d+)\s+rounds',       # "ammunition 50 rounds"
        r'(\d+)\s+rounds.*?ammunition',       # "50 rounds of ammunition"
    ]

    matches = []
    for pattern in patterns:
        found = re.findall(pattern, section_text, re.IGNORECASE)
        matches.extend(found)

    # Return most common match if multiple found
    if matches:
        # Convert to integers
        ammo_counts = [int(m) for m in matches]
        # Return most common, or first if all different
        from collections import Counter
        most_common = Counter(ammo_counts).most_common(1)[0][0]
        return most_common

    return None


def extract_specs_from_section(section_text):
    """Extract vehicle specs from section (weight, armor, etc.)."""

    specs = {}

    # Weight
    weight_match = re.search(r'Weight\s*\(tonnes\)\s+(\d+(?:\.\d+)?)', section_text)
    if weight_match:
        specs['weight_tonnes'] = float(weight_match.group(1))

    # Front armor
    armor_match = re.search(r'Front\s+Armor\s*\(mm\)\s+(\d+)', section_text)
    if armor_match:
        specs['armor_front_mm'] = int(armor_match.group(1))

    # Side armor
    side_match = re.search(r'Side\s+Armor\s*\(mm\)\s+(\d+)', section_text)
    if side_match:
        specs['armor_side_mm'] = int(side_match.group(1))

    # Engine HP
    hp_match = re.search(r'Engine\s+HP\s+(\d+)', section_text)
    if hp_match:
        specs['engine_hp'] = int(hp_match.group(1))

    # Road speed
    speed_match = re.search(r'Road\s+Speed\s*\(km/h\)\s+(\d+)', section_text)
    if speed_match:
        specs['road_speed_kmh'] = int(speed_match.group(1))

    return specs


def normalize_vehicle_name(name):
    """Normalize vehicle name for matching."""

    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # Common normalizations
    replacements = {
        'Mk ': 'Mark ',
        'MK ': 'Mark ',
        'mk ': 'Mark ',
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    return name


def main():
    """Main execution."""

    print("=" * 80)
    print("JANE'S WWII TANKS AMMUNITION EXTRACTION V2")
    print("Improved Vehicle-Ammunition Association")
    print("=" * 80)

    # Read file
    if not JANES_PATH.exists():
        print(f"\nERROR: File not found: {JANES_PATH}")
        return

    print(f"\nReading: {JANES_PATH.name}")
    with open(JANES_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    print(f"File size: {len(text):,} characters")

    # Split into sections
    print("\nSplitting into vehicle sections...")
    sections = split_into_sections(text)

    print(f"Found {len(sections)} potential vehicle sections")

    # Extract ammunition data from each section
    print("\nExtracting ammunition data...")
    vehicle_data = []

    for section in sections:
        ammo_count = extract_ammunition_from_section(section['text'])

        if ammo_count:
            specs = extract_specs_from_section(section['text'])
            vehicle_name = normalize_vehicle_name(section['name'])

            vehicle_data.append({
                'vehicle_name': vehicle_name,
                'ammunition_count': ammo_count,
                'start_line': section['start_line'],
                **specs
            })

    print(f"Found {len(vehicle_data)} vehicles with ammunition data\n")

    # Save to CSV
    output_csv = "janes_ammunition_v2.csv"

    # Get all possible fieldnames
    all_fields = set()
    for entry in vehicle_data:
        all_fields.update(entry.keys())

    fieldnames = ['vehicle_name', 'ammunition_count', 'start_line', 'weight_tonnes',
                  'armor_front_mm', 'armor_side_mm', 'engine_hp', 'road_speed_kmh']

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        if vehicle_data:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(vehicle_data)

    print(f"Saved: {output_csv}")

    # Save to JSON for easier import
    output_json = "janes_ammunition_v2.json"

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(vehicle_data, f, indent=2)

    print(f"Saved: {output_json}")

    # Display sample
    print(f"\nSample extractions (first 30):\n")
    print(f"{'Vehicle Name':50} | {'Ammo':>5} | {'Weight':>6} | {'Armor':>5} | {'Line':>5}")
    print("-" * 100)

    for entry in vehicle_data[:30]:
        weight = f"{entry.get('weight_tonnes', 0):.1f}t" if 'weight_tonnes' in entry else "n/a"
        armor = f"{entry.get('armor_front_mm', 0)}mm" if 'armor_front_mm' in entry else "n/a"

        print(f"{entry['vehicle_name'][:50]:50} | {entry['ammunition_count']:5} | "
              f"{weight:>6} | {armor:>5} | {entry['start_line']:5}")

    if len(vehicle_data) > 30:
        print(f"\n... ({len(vehicle_data) - 30} more entries in files)")

    # Statistics
    print(f"\n" + "=" * 80)
    print("EXTRACTION STATISTICS")
    print("=" * 80)

    ammo_counts = [v['ammunition_count'] for v in vehicle_data]

    print(f"\nAmmunition capacity range:")
    print(f"  Minimum: {min(ammo_counts)} rounds")
    print(f"  Maximum: {max(ammo_counts)} rounds")
    print(f"  Average: {sum(ammo_counts) / len(ammo_counts):.1f} rounds")

    # Count how many have full specs
    with_weight = sum(1 for v in vehicle_data if 'weight_tonnes' in v)
    with_armor = sum(1 for v in vehicle_data if 'armor_front_mm' in v)

    print(f"\nVehicles with additional specs:")
    print(f"  Weight data: {with_weight} ({with_weight/len(vehicle_data)*100:.1f}%)")
    print(f"  Armor data: {with_armor} ({with_armor/len(vehicle_data)*100:.1f}%)")

    print(f"\n" + "=" * 80)
    print("READY FOR DATABASE IMPORT")
    print("=" * 80)
    print(f"\nFiles created:")
    print(f"  - {output_csv} (for spreadsheet review)")
    print(f"  - {output_json} (for database import)")
    print(f"\nNext step: Import to bg_reference_vehicles ammo_1-4 fields")


if __name__ == "__main__":
    main()
