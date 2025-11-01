#!/usr/bin/env python3
"""
Extract vehicle profiles from BattleGroup Early German datacard PDF.
Uses PyMuPDF for better text extraction.
"""

import fitz  # PyMuPDF
import json
import re
from pathlib import Path

def clean_text(text):
    """Remove garbled characters and normalize spacing."""
    # Remove common OCR artifacts
    text = re.sub(r'[±„"'']', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_vehicles_from_pdf(pdf_path):
    """Extract all vehicle profiles from the PDF."""

    vehicles = []
    doc = fitz.open(pdf_path)

    print(f"Processing {len(doc)} pages from Early German PDF...")

    all_text = ""

    # First pass: collect all text
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        all_text += f"\n\n=== PAGE {page_num + 1} ===\n{text}"

        if page_num < 3:  # Print first few pages for debugging
            print(f"\n--- PAGE {page_num + 1} (first 1000 chars) ---")
            print(text[:1000])

    # Save raw text for manual inspection
    with open("D:/north-africa-toe-builder/early_german_raw.txt", "w", encoding="utf-8") as f:
        f.write(all_text)
    print("\nRaw text saved to early_german_raw.txt")

    # Second pass: try to extract structured data
    # Looking for patterns like:
    # - Vehicle name (e.g., "Panzer IV", "SdKfz 222")
    # - Movement: Off-Road/Road (e.g., "8" 12"")
    # - Armor: F/S/R (letters A-O or numbers)
    # - Weapons: (e.g., "75mmL24", "MG")

    doc.close()

    # Manual parsing based on known BattleGroup format
    # From the sample, I can see entries like:
    # Panzer lvA- 8" 12" M 0 0 75mmL24 Turret 8

    lines = all_text.split('\n')

    # Common German vehicle names from Early War period
    vehicle_patterns = [
        r'Panzer\s*[IVX]+\w*[-\s]*\w*',
        r'Panzer\s*\d+\([a-z]\)',
        r'Pz\.?Kpfw\.?\s*[IVX]+',
        r'SdKfz\s*\d+',
        r'[Pp]z\.\s*[IVX]+',
        r'Marder',
        r'Sturm\w+',
        r'Flamm\w+',
        r'Half[-\s]?track',
        r'Kubelwagen',
        r'Truck',
        r'ADGz',
        r'JU-87',
        r'Stuka'
    ]

    for i, line in enumerate(lines):
        line = clean_text(line)
        if not line or len(line) < 5:
            continue

        # Check if line contains a vehicle name
        for pattern in vehicle_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                vehicle_name = match.group(0).strip()

                # Look for movement data in same line or nearby
                movement_match = re.search(r'(\d+)["\']?\s+(\d+)["\']?', line)

                # Look for armor values (letters A-O)
                armor_match = re.findall(r'\b([A-O])\b', line)

                # Look for weapons
                weapon_matches = re.findall(r'(\d+mm\w+|MG)', line, re.IGNORECASE)

                vehicle = {
                    "name": vehicle_name,
                    "movement": {},
                    "armour": {},
                    "armament": []
                }

                if movement_match:
                    vehicle["movement"]["off_road"] = f'{movement_match.group(1)}"'
                    vehicle["movement"]["road"] = f'{movement_match.group(2)}"'

                if len(armor_match) >= 3:
                    vehicle["armour"]["front"] = armor_match[0]
                    vehicle["armour"]["side"] = armor_match[1]
                    vehicle["armour"]["rear"] = armor_match[2]

                for weapon in weapon_matches:
                    vehicle["armament"].append({
                        "weapon": weapon,
                        "mount": "Unknown",
                        "ammo": None
                    })

                # Only add if we got some meaningful data
                if vehicle["movement"] or vehicle["armour"] or vehicle["armament"]:
                    # Check if not duplicate
                    if not any(v["name"] == vehicle["name"] for v in vehicles):
                        vehicles.append(vehicle)
                        print(f"Found vehicle: {vehicle_name}")

                break  # Don't match multiple patterns on same line

    return vehicles

if __name__ == "__main__":
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-Early-German.pdf")

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        exit(1)

    vehicles = extract_vehicles_from_pdf(pdf_path)

    print(f"\n\nExtracted {len(vehicles)} vehicles:")
    print(json.dumps(vehicles, indent=2))

    # Save to output file
    output_path = Path("D:/north-africa-toe-builder/data/output/battlegroup_early_german_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vehicles, indent=2, fp=f)

    print(f"\n\nSaved to: {output_path}")
