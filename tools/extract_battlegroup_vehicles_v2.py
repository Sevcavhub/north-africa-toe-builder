#!/usr/bin/env python3
"""
Extract vehicle profiles from BattleGroup French/Polish/Romanian/Hungarian PDF
v2 - Better pattern matching based on actual PDF structure
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path

def extract_vehicle_data(pdf_path):
    """Extract all vehicle profiles from the BattleGroup datacard PDF"""

    vehicles = []
    doc = fitz.open(pdf_path)

    print(f"Processing {len(doc)} pages")

    current_nation = "french"  # Default assumption based on filename

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        print(f"\n=== PAGE {page_num + 1} ===")
        print(text)
        print("=" * 80)

        # Look for vehicle entries
        # Pattern 1: Looking for "VEHICLE" header followed by data
        # Pattern 2: Looking for movement values (Off-Road, Road)
        # Pattern 3: Looking for armor values (F S R or Front Side Rear)

        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # Find vehicle markers
        for i, line in enumerate(lines):
            # Check if this line contains "VEHICLE" or movement headers
            if 'VEHICLE' in line.upper() or ('MOVEMENT' in line.upper() and 'ARMOUR' in line.upper()):
                # This is likely a header line for vehicle stats
                # Look ahead for actual data
                vehicle_data = {}

                # Scan next 20 lines for vehicle information
                scan_lines = lines[i:min(i+20, len(lines))]

                # Look for vehicle name (usually before or after VEHICLE header)
                for j, scan_line in enumerate(scan_lines):
                    # Check for movement values (numbers followed by inches/quotes)
                    movement_match = re.search(r'(\d+)["\']?\s+(\d+)["\']?', scan_line)
                    if movement_match and 'MOVEMENT' not in scan_line and 'ARMOUR' not in scan_line:
                        vehicle_data['movement'] = {
                            'off_road': int(movement_match.group(1)),
                            'road': int(movement_match.group(2))
                        }

                    # Check for armor values (single letters or numbers)
                    armor_match = re.search(r'\b([0-9A-O])\s+([0-9A-O])\s+([0-9A-O])\b', scan_line)
                    if armor_match and 'AMMO' not in scan_line:
                        vehicle_data['armor'] = {
                            'front': armor_match.group(1),
                            'side': armor_match.group(2),
                            'rear': armor_match.group(3)
                        }

                    # Check for weapon information
                    weapon_match = re.search(r'(37mm|20mm|47mm|75mm|MG|mg)', scan_line, re.IGNORECASE)
                    if weapon_match:
                        if 'weapons' not in vehicle_data:
                            vehicle_data['weapons'] = []
                        vehicle_data['weapons'].append(scan_line)

                # If we found meaningful data, try to find the vehicle name
                if 'movement' in vehicle_data or 'armor' in vehicle_data:
                    # Look backwards for vehicle name
                    for j in range(max(0, i-10), i):
                        potential_name = lines[j]
                        # Vehicle names are usually short, alphanumeric with dashes
                        if re.match(r'^[A-Z0-9][A-Z0-9\-\s]{1,30}$', potential_name) and len(potential_name) < 40:
                            if not any(keyword in potential_name.upper() for keyword in ['VEHICLE', 'MOVEMENT', 'ARMOUR', 'WEAPON', 'MOUNT', 'AMMO', 'SPECIAL', 'OFF-ROAD']):
                                vehicle_data['name'] = potential_name
                                break

                    if vehicle_data:
                        vehicle_data['nation'] = current_nation
                        vehicle_data['page'] = page_num + 1
                        vehicles.append(vehicle_data)

    doc.close()

    # Deduplicate by name
    seen = set()
    unique_vehicles = []
    for v in vehicles:
        if v.get('name') and v['name'] not in seen:
            seen.add(v['name'])
            unique_vehicles.append(v)

    return unique_vehicles

if __name__ == "__main__":
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf")

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        exit(1)

    vehicles = extract_vehicle_data(pdf_path)

    print(f"\n\n{'='*80}")
    print(f"EXTRACTED {len(vehicles)} VEHICLES")
    print('='*80)
    print(json.dumps(vehicles, indent=2))

    # Save to output file
    output_path = Path("D:/north-africa-toe-builder/data/output/battlegroup_french_polish_romanian_hungarian_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vehicles, indent=2, fp=f)

    print(f"\nSaved to: {output_path}")
