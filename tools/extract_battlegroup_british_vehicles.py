#!/usr/bin/env python3
"""
Extract British vehicle profiles from BattleGroup datacard PDF.
Uses page-by-page processing to handle large PDFs.
"""

import json
import re
import fitz  # PyMuPDF
from pathlib import Path

def extract_british_vehicles():
    """Extract all British vehicle profiles from the datacard PDF."""

    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-British.pdf")
    output_path = Path(r"D:\north-africa-toe-builder\data\output\battlegroup_british_vehicles.json")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}")

    vehicles = []
    current_vehicle = None

    # Process page by page
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        # Split into lines for processing
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Look for vehicle names (typically at start of datacard)
            # Common British vehicles: Matilda, Crusader, Valentine, Churchill, Cromwell, etc.
            vehicle_patterns = [
                r'^(Matilda\s*(?:I{1,3})?)\s*$',
                r'^(Crusader\s*(?:I{1,3}|Mk\s*[IVX]+)?(?:\s*CS)?)\s*$',
                r'^(Valentine\s*(?:I{1,3}|Mk\s*[IVX]+)?)\s*$',
                r'^(Churchill\s*(?:I{1,3}|Mk\s*[IVX]+)?(?:\s*CS)?)\s*$',
                r'^(Cromwell\s*(?:I{1,3}|Mk\s*[IVX]+)?(?:\s*CS)?)\s*$',
                r'^(Sherman\s*(?:I{1,3}|Mk\s*[IVX]+)?(?:\s*Firefly)?)\s*$',
                r'^(Grant\s*(?:I{1,3}|Mk\s*[IVX]+)?)\s*$',
                r'^(Lee\s*(?:I{1,3}|Mk\s*[IVX]+)?)\s*$',
                r'^(Stuart\s*(?:I{1,3}|Mk\s*[IVX]+)?)\s*$',
                r'^(Honey)\s*$',
                r'^(Humber\s*(?:Mk\s*[IVX]+)?)\s*$',
                r'^(Daimler\s*(?:Mk\s*[IVX]+)?)\s*$',
                r'^(AEC\s*(?:Mk\s*[IVX]+)?)\s*$',
                r'^(Morris\s*(?:CS9)?)\s*$',
                r'^(Marmon[- ]Herrington)\s*$',
                r'^(Universal\s*Carrier)\s*$',
                r'^(Bren\s*Carrier)\s*$',
                r'^(Loyd\s*Carrier)\s*$',
                r'^(Deacon)\s*$',
                r'^(Archer)\s*$',
                r'^(Achilles)\s*$',
                r'^(Bishop)\s*$',
                r'^(Priest)\s*$',
                r'^(Sexton)\s*$',
            ]

            for pattern in vehicle_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Save previous vehicle if exists
                    if current_vehicle and current_vehicle.get('name'):
                        vehicles.append(current_vehicle)

                    # Start new vehicle
                    current_vehicle = {
                        'name': match.group(1).strip(),
                        'year_range': None,
                        'off_road_inches': None,
                        'road_inches': None,
                        'special_movement': None,
                        'armor_front': None,
                        'armor_side': None,
                        'armor_rear': None,
                        'weapons': []
                    }
                    print(f"Found vehicle: {current_vehicle['name']} (page {page_num + 1})")
                    break

            if current_vehicle:
                # Extract year range (e.g., "1940-1943", "1941-45")
                year_match = re.search(r'(19\d{2})[- ](19)?(\d{2})', line)
                if year_match:
                    year1 = year_match.group(1)
                    year2 = year_match.group(3)
                    if len(year2) == 2:
                        year2 = '19' + year2
                    current_vehicle['year_range'] = f"{year1}-{year2}"

                # Extract movement (e.g., "Off-Road: 5   Road: 8")
                movement_match = re.search(r'(?:Off[- ]?Road|OFF\s*ROAD)[:\s]+(\d+).*?(?:Road|ROAD)[:\s]+(\d+)', line, re.IGNORECASE)
                if movement_match:
                    current_vehicle['off_road_inches'] = int(movement_match.group(1))
                    current_vehicle['road_inches'] = int(movement_match.group(2))

                # Extract armor values (e.g., "Front: K  Side: K  Rear: L")
                armor_match = re.search(r'(?:Front|FRONT)[:\s]+([A-O])', line, re.IGNORECASE)
                if armor_match:
                    current_vehicle['armor_front'] = armor_match.group(1).upper()

                armor_match = re.search(r'(?:Side|SIDE)[:\s]+([A-O])', line, re.IGNORECASE)
                if armor_match:
                    current_vehicle['armor_side'] = armor_match.group(1).upper()

                armor_match = re.search(r'(?:Rear|REAR)[:\s]+([A-O])', line, re.IGNORECASE)
                if armor_match:
                    current_vehicle['armor_rear'] = armor_match.group(1).upper()

                # Extract weapons (look for weapon patterns)
                # Common British weapons: 2-pdr, 6-pdr, 17-pdr, 75mm, QF, HMG, MMG, etc.
                weapon_patterns = [
                    r'(2[- ]pdr|2\s*pounder)',
                    r'(6[- ]pdr|6\s*pounder)',
                    r'(17[- ]pdr|17\s*pounder)',
                    r'(75mm)',
                    r'(76mm)',
                    r'(3\.7[- ]inch)',
                    r'(25[- ]pdr)',
                    r'(QF\s+\d+(?:\.\d+)?[- ]?(?:inch|pdr))',
                    r'(HMG|Heavy\s*MG)',
                    r'(MMG|Medium\s*MG)',
                    r'(LMG|Light\s*MG)',
                    r'(Bren)',
                    r'(Vickers)',
                    r'(BESA)',
                ]

                for wp in weapon_patterns:
                    if re.search(wp, line, re.IGNORECASE):
                        # Extract weapon details if found
                        # This is a simplified extraction - may need refinement
                        weapon_info = {
                            'weapon': line.strip(),
                            'mount': 'Unknown',
                            'ammo': 'Unknown'
                        }
                        # Avoid duplicates
                        if weapon_info not in current_vehicle['weapons']:
                            current_vehicle['weapons'].append(weapon_info)

    # Save last vehicle
    if current_vehicle and current_vehicle.get('name'):
        vehicles.append(current_vehicle)

    doc.close()

    # Save to JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vehicles, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Extraction complete!")
    print(f"📊 Total vehicles extracted: {len(vehicles)}")
    print(f"💾 Saved to: {output_path}")

    # Print summary
    print("\n📋 Vehicle Summary:")
    for v in vehicles:
        print(f"  - {v['name']} ({v.get('year_range', 'Unknown years')})")

    return vehicles

if __name__ == '__main__':
    vehicles = extract_british_vehicles()
