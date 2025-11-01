#!/usr/bin/env python3
"""
Extract Soviet vehicle profiles from BattleGroup datacard PDF.
Processes PDF in chunks to avoid token limits.
"""

import PyPDF2
import json
import re
from pathlib import Path

def extract_vehicle_from_text(text):
    """Extract vehicle profile data from PDF text."""
    vehicles = []

    # Look for vehicle name patterns (all caps, possibly with numbers/slashes)
    # Soviet vehicles: T-34, KV-1, BA-10, SU-76, etc.
    vehicle_pattern = r'^([A-Z]{1,3}[-/]?\d+(?:[A-Z])?(?:/\d+)?)\s*$'

    lines = text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Check if this line is a vehicle name
        match = re.match(vehicle_pattern, line)
        if match:
            vehicle_name = match.group(1)

            # Try to extract data from following lines
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

            # Look ahead for year range (e.g., "1941-1943")
            for j in range(i+1, min(i+10, len(lines))):
                next_line = lines[j].strip()

                # Year range pattern
                year_match = re.search(r'(\d{4})-?(\d{4})?', next_line)
                if year_match:
                    if year_match.group(2):
                        vehicle_data["year_range"] = f"{year_match.group(1)}-{year_match.group(2)}"
                    else:
                        vehicle_data["year_range"] = year_match.group(1)

                # Movement pattern (e.g., "8\" 16\"" or "8 16")
                movement_match = re.search(r'(\d+)[""]?\s+(\d+)[""]?', next_line)
                if movement_match and not vehicle_data["movement"]["off_road"]:
                    vehicle_data["movement"]["off_road"] = f"{movement_match.group(1)}\""
                    vehicle_data["movement"]["road"] = f"{movement_match.group(2)}\""

                # Armor pattern (letters A-O)
                armor_match = re.search(r'([A-O])\s+([A-O])\s+([A-O])', next_line)
                if armor_match:
                    vehicle_data["armor"]["front"] = armor_match.group(1)
                    vehicle_data["armor"]["side"] = armor_match.group(2)
                    vehicle_data["armor"]["rear"] = armor_match.group(3)

                # Weapon patterns (e.g., "76.2mm L/30.5", "45mm", "DT MG")
                weapon_match = re.search(r'(\d+(?:\.\d+)?mm|DT|DTM|DSHK|SGMT?)\s*([A-Za-z/\d.]*)?', next_line)
                if weapon_match and len(vehicle_data["weapons"]) < 5:  # Limit weapons
                    weapon_desc = weapon_match.group(0)
                    # Try to determine mount type
                    mount = "turret" if "turret" in next_line.lower() else "hull"
                    if "coax" in next_line.lower() or "co-ax" in next_line.lower():
                        mount = "coaxial"

                    vehicle_data["weapons"].append({
                        "weapon": weapon_desc.strip(),
                        "mount": mount,
                        "ammo": None  # Not always specified in PDF
                    })

            # Only add if we found some actual data
            if (vehicle_data["movement"]["off_road"] or
                vehicle_data["armor"]["front"] or
                len(vehicle_data["weapons"]) > 0):
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
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            print(f"Total pages: {total_pages}")

            # Process in chunks
            for page_num in range(total_pages):
                print(f"Processing page {page_num + 1}/{total_pages}...")

                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                # Extract vehicles from this page
                vehicles = extract_vehicle_from_text(text)

                # Add unique vehicles only
                for vehicle in vehicles:
                    name = vehicle["vehicle_name"]
                    if name not in seen_names:
                        seen_names.add(name)
                        all_vehicles.append(vehicle)
                        print(f"  Found: {name}")

    except Exception as e:
        print(f"ERROR processing PDF: {e}")
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
        print(f"  - {v['vehicle_name']} ({v.get('year_range', 'Unknown year')})")

if __name__ == "__main__":
    main()
