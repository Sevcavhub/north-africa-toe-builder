#!/usr/bin/env python3
"""
Extract vehicle profiles from BattleGroup French/Polish/Romanian/Hungarian PDF
Handles large PDFs by processing page-by-page
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path

def extract_vehicle_data(pdf_path):
    """Extract all vehicle profiles from the BattleGroup datacard PDF"""

    vehicles = []
    doc = fitz.open(pdf_path)

    print(f"Processing {len(doc)} pages from {pdf_path}")

    # Process each page
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        # Print first 500 chars of first few pages to understand format
        if page_num < 5:
            print(f"\n=== PAGE {page_num + 1} (first 500 chars) ===")
            print(text[:500])
            print("=" * 50)

    doc.close()

    # Now we'll analyze the format and extract vehicles
    # Re-open to extract based on patterns we discover
    doc = fitz.open(pdf_path)

    current_nation = None

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        # Detect nation headers (FRENCH, POLISH, ROMANIAN, HUNGARIAN)
        if "FRENCH" in text.upper() and len(text) < 100:
            current_nation = "french"
            continue
        elif "POLISH" in text.upper() and len(text) < 100:
            current_nation = "polish"
            continue
        elif "ROMANIAN" in text.upper() and len(text) < 100:
            current_nation = "romanian"
            continue
        elif "HUNGARIAN" in text.upper() and len(text) < 100:
            current_nation = "hungarian"
            continue

        # Look for vehicle patterns
        lines = text.split('\n')

        # Try to identify vehicle entries by looking for armor values
        for i, line in enumerate(lines):
            line = line.strip()

            # Look for armor pattern
            armor_match = re.search(r'[Ff]ront[:\s]+([A-O]|\d+).*[Ss]ide[:\s]+([A-O]|\d+).*[Rr]ear[:\s]+([A-O]|\d+)', line, re.IGNORECASE)
            if armor_match:
                # Found armor line - vehicle data likely nearby
                vehicle_name = None
                for j in range(max(0, i-5), i):
                    potential_name = lines[j].strip()
                    if potential_name and len(potential_name) < 50 and not any(keyword in potential_name.lower() for keyword in ['movement', 'armor', 'weapon', 'front', 'side', 'rear']):
                        vehicle_name = potential_name
                        break

                if vehicle_name:
                    vehicle = {
                        "name": vehicle_name,
                        "nation": current_nation or "unknown",
                        "armor": {
                            "front": armor_match.group(1),
                            "side": armor_match.group(2),
                            "rear": armor_match.group(3)
                        },
                        "page": page_num + 1
                    }

                    # Look for movement data
                    for k in range(max(0, i-3), min(len(lines), i+3)):
                        move_line = lines[k]
                        move_match = re.search(r'(?:Off-?Road|Off Road)[:\s]+(\d+).*?(?:Road)[:\s]+(\d+)', move_line, re.IGNORECASE)
                        if move_match:
                            vehicle["movement"] = {
                                "off_road": int(move_match.group(1)),
                                "road": int(move_match.group(2))
                            }
                            break

                    vehicles.append(vehicle)

    doc.close()

    return vehicles

if __name__ == "__main__":
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf")

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        exit(1)

    vehicles = extract_vehicle_data(pdf_path)

    print(f"\n\nExtracted {len(vehicles)} vehicles")
    print(json.dumps(vehicles, indent=2))

    # Save to output file
    output_path = Path("D:/north-africa-toe-builder/data/output/battlegroup_french_polish_romanian_hungarian_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vehicles, indent=2, fp=f)

    print(f"\nSaved to: {output_path}")
