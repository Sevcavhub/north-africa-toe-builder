#!/usr/bin/env python3
"""
Extract Soviet vehicle profiles from BattleGroup datacard PDF using pdfplumber.
"""

import pdfplumber
import json
import re
from pathlib import Path

def parse_vehicle_data(text_lines):
    """Parse vehicle profile data from text lines."""
    vehicles = []

    # Soviet vehicle name patterns: T-34, KV-1, BA-10, SU-76, IS-2, etc.
    # Also: BT-7, T-26, T-60, T-70, ISU-152, etc.
    vehicle_patterns = [
        r'^(T-\d+(?:/\d+)?[A-Za-z]?)\s',  # T-34, T-34/76, T-60, etc.
        r'^(KV-\d+[A-Za-z]?)\s',           # KV-1, KV-2, etc.
        r'^(IS-\d+[A-Za-z]?)\s',           # IS-2, IS-3, etc.
        r'^(ISU-\d+)\s',                   # ISU-152, ISU-122
        r'^(SU-\d+)\s',                    # SU-76, SU-85, SU-100
        r'^(BT-\d+[A-Za-z]?)\s',           # BT-7, BT-5
        r'^(BA-\d+)\s',                    # BA-10, BA-64
        r'^(GAZ-\d+)\s',                   # GAZ-AA, etc.
        r'^(ZIS-\d+)\s',                   # ZIS-5, etc.
    ]

    i = 0
    while i < len(text_lines):
        line = text_lines[i].strip()

        # Check if line matches any vehicle pattern
        vehicle_name = None
        for pattern in vehicle_patterns:
            match = re.match(pattern, line)
            if match:
                vehicle_name = match.group(1)
                break

        if vehicle_name:
            print(f"  Found vehicle: {vehicle_name}")

            vehicle_data = {
                "vehicle_name": vehicle_name,
                "year_range": None,
                "movement": {
                    "off_road": None,
                    "road": None,
                    "special": None
                },
                "armor": {
                    "front": None,
                    "side": None,
                    "rear": None
                },
                "weapons": []
            }

            # Parse the rest of the line and following lines
            full_line = line[len(vehicle_name):].strip()

            # Look for year in parentheses (e.g., "(1941-43)")
            year_match = re.search(r'\((\d{4})-?(\d{2,4})?\)', full_line)
            if year_match:
                if year_match.group(2):
                    year2 = year_match.group(2)
                    # Convert 2-digit year to 4-digit
                    if len(year2) == 2:
                        year2 = "19" + year2
                    vehicle_data["year_range"] = f"{year_match.group(1)}-{year2}"
                else:
                    vehicle_data["year_range"] = year_match.group(1)

            # Look ahead for movement, armor, weapons in next ~10 lines
            for j in range(i, min(i+15, len(text_lines))):
                next_line = text_lines[j].strip()

                # Movement: look for pattern like "8\" 16\"" or "Movement: 8 16"
                if not vehicle_data["movement"]["off_road"]:
                    movement_match = re.search(r'(\d+)["″]?\s+(\d+)["″]?', next_line)
                    if movement_match and "armor" not in next_line.lower():
                        vehicle_data["movement"]["off_road"] = f"{movement_match.group(1)}\""
                        vehicle_data["movement"]["road"] = f"{movement_match.group(2)}\""

                # Armor: look for three letters A-O
                if not vehicle_data["armor"]["front"]:
                    armor_match = re.search(r'\b([A-O])\s+([A-O])\s+([A-O])\b', next_line)
                    if armor_match:
                        vehicle_data["armor"]["front"] = armor_match.group(1)
                        vehicle_data["armor"]["side"] = armor_match.group(2)
                        vehicle_data["armor"]["rear"] = armor_match.group(3)

                # Weapons: look for mm guns or MG designations
                weapon_patterns = [
                    r'(\d+(?:\.\d+)?mm\s+[A-Z][A-Za-z0-9/.\s]+)',  # e.g., "76.2mm L/30.5"
                    r'(DT\s+MG|DTM\s+MG|DShK\s+HMG|SGMT)',          # Soviet MGs
                    r'(\d+mm)',                                      # Simple caliber
                ]

                for wp in weapon_patterns:
                    for weapon_match in re.finditer(wp, next_line):
                        weapon_desc = weapon_match.group(1).strip()

                        # Avoid duplicates
                        if not any(w["weapon"] == weapon_desc for w in vehicle_data["weapons"]):
                            # Determine mount type
                            mount = "hull"
                            if "turret" in next_line.lower():
                                mount = "turret"
                            elif "coax" in next_line.lower():
                                mount = "coaxial"

                            vehicle_data["weapons"].append({
                                "weapon": weapon_desc,
                                "mount": mount,
                                "ammo": None
                            })

            vehicles.append(vehicle_data)

        i += 1

    return vehicles

def main():
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-Soviets.pdf")

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        return

    print(f"Processing PDF: {pdf_path}")

    all_vehicles = []
    seen_names = set()

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}\n")

            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}/{total_pages}...")

                # Extract text
                text = page.extract_text()

                if text:
                    # Split into lines
                    lines = text.split('\n')

                    # Parse vehicles
                    vehicles = parse_vehicle_data(lines)

                    # Add unique vehicles
                    for vehicle in vehicles:
                        name = vehicle["vehicle_name"]
                        if name not in seen_names:
                            seen_names.add(name)
                            all_vehicles.append(vehicle)

    except Exception as e:
        print(f"ERROR processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return

    # Sort by vehicle name
    all_vehicles.sort(key=lambda x: x["vehicle_name"])

    # Write output
    output_path = Path(r"D:\north-africa-toe-builder\data\output\battlegroup_soviet_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_vehicles, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Extracted {len(all_vehicles)} vehicles")
    print(f"[OK] Output written to: {output_path}")

    # Print summary
    print("\nVehicles found:")
    for v in all_vehicles:
        print(f"  - {v['vehicle_name']}")
        print(f"    Year: {v.get('year_range', 'Unknown')}")
        print(f"    Movement: {v['movement']['off_road']} / {v['movement']['road']}")
        print(f"    Armor: {v['armor']['front']}/{v['armor']['side']}/{v['armor']['rear']}")
        print(f"    Weapons: {len(v['weapons'])}")

if __name__ == "__main__":
    main()
