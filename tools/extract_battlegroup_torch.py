#!/usr/bin/env python3
"""
Extract ALL vehicle and gun profiles from Battlegroup Torch PDF with duplicate detection.

Operation Torch (November 1942) - First US combat in North Africa
- American forces: M3 Grant, M3 Lee, M3 Stuart, M4 Sherman (early)
- British forces: Crusader, Valentine, Matilda
- Free French: R-35, H-39, S-35, Char B1
- Vichy French: Same as Free French
- German forces: Panzer III, Panzer IV (rushed from Tunisia)
"""

import pdfplumber
import json
import re
import sqlite3
from pathlib import Path

# Paths
PDF_PATH = Path("D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Battlegroup-Torch-Mission.pdf")
OUTPUT_DIR = Path("D:/north-africa-toe-builder/data/output")
DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")

# Output files
VEHICLES_JSON = OUTPUT_DIR / "battlegroup_torch_vehicles.json"
GUNS_JSON = OUTPUT_DIR / "battlegroup_torch_guns.json"


def get_existing_entries():
    """Query database for existing vehicles and guns to detect duplicates."""
    vehicles = set()
    guns = set()

    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return vehicles, guns

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    if 'bg_reference_vehicles' in tables:
        cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
        vehicles = {(row[0], row[1]) for row in cursor.fetchall()}
        print(f"Found {len(vehicles)} existing vehicles in database")
    else:
        print("Table 'bg_reference_vehicles' not found in database")

    if 'bg_reference_guns' in tables:
        cursor.execute("SELECT name, nation FROM bg_reference_guns")
        guns = {(row[0], row[1]) for row in cursor.fetchall()}
        print(f"Found {len(guns)} existing guns in database")
    else:
        print("Table 'bg_reference_guns' not found in database")

    conn.close()
    return vehicles, guns


def normalize_nation(raw_nation):
    """Normalize nation names to canonical values."""
    raw_nation = raw_nation.lower().strip()

    nation_map = {
        'american': 'american',
        'us': 'american',
        'usa': 'american',
        'united states': 'american',

        'british': 'british',
        'britain': 'british',
        'uk': 'british',
        'commonwealth': 'british',
        'australian': 'british',
        'australian': 'british',
        'new zealand': 'british',
        'indian': 'british',
        'south african': 'british',
        'canadian': 'british',

        'german': 'german',
        'germany': 'german',
        'dak': 'german',
        'afrika korps': 'german',

        'italian': 'italian',
        'italy': 'italian',

        'french': 'french',
        'free french': 'french',
        'vichy french': 'french',
        'vichy': 'french',
    }

    return nation_map.get(raw_nation, raw_nation)


def extract_armor_value(text):
    """Extract armor values like 'N', 'O', 'K', etc."""
    match = re.search(r'\b([A-P])\b', text)
    return match.group(1) if match else None


def extract_movement(text):
    """Extract movement values like '8/12' or '10/16'."""
    match = re.search(r'(\d+)[\s/]+(\d+)', text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def parse_vehicle_data(text, page_num):
    """
    Parse vehicle data from PDF text.

    Expected format examples:
    - M3 Lee (american) - Front: K, Side: L, Rear: N, Move: 9/14
    - Panzer III Ausf F (german) - Front: K, Side: M, Rear: M, Move: 10/16
    """
    vehicles = []

    # Look for vehicle patterns
    # Pattern: Vehicle name, nation, armor values, movement
    lines = text.split('\n')

    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            continue

        # Look for vehicle entries (this is a simplified parser)
        # We'll need to adapt this based on the actual PDF structure
        if any(keyword in line.lower() for keyword in ['tank', 'panzer', 'sherman', 'grant', 'lee', 'stuart', 'crusader', 'valentine', 'matilda', 'tiger', 'panther']):
            print(f"Page {page_num}: Found potential vehicle: {line[:80]}")

    return vehicles


def parse_gun_data(text, page_num):
    """Parse gun/weapon data from PDF text."""
    guns = []

    lines = text.split('\n')

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        # Look for gun entries
        if any(keyword in line.lower() for keyword in ['pdr', 'mm', 'howitzer', 'gun', 'anti-tank', 'at']):
            print(f"Page {page_num}: Found potential gun: {line[:80]}")

    return guns


def extract_from_pdf():
    """Extract all vehicles and guns from Battlegroup Torch PDF."""
    print(f"\nExtracting from: {PDF_PATH}")

    if not PDF_PATH.exists():
        print(f"ERROR: PDF not found at {PDF_PATH}")
        return [], []

    vehicles = []
    guns = []

    with pdfplumber.open(PDF_PATH) as pdf:
        print(f"Total pages: {len(pdf.pages)}")

        for page_num, page in enumerate(pdf.pages, 1):
            print(f"\nProcessing page {page_num}...")

            # Extract text
            text = page.extract_text()
            if not text:
                continue

            # Parse vehicles and guns from this page
            page_vehicles = parse_vehicle_data(text, page_num)
            page_guns = parse_gun_data(text, page_num)

            vehicles.extend(page_vehicles)
            guns.extend(page_guns)

            # Show sample text from each page (for debugging)
            print(f"Sample text: {text[:200]}")

    print(f"\n\nExtraction complete:")
    print(f"  Vehicles found: {len(vehicles)}")
    print(f"  Guns found: {len(guns)}")

    return vehicles, guns


def main():
    print("=" * 80)
    print("BATTLEGROUP TORCH EXTRACTION")
    print("Operation Torch (November 1942) - North Africa")
    print("=" * 80)

    # Get existing entries from database
    existing_vehicles, existing_guns = get_existing_entries()

    # Extract from PDF
    vehicles, guns = extract_from_pdf()

    # Detect duplicates
    new_vehicles = []
    duplicate_vehicles = []

    for vehicle in vehicles:
        key = (vehicle.get('name'), vehicle.get('nation'))
        if key in existing_vehicles:
            duplicate_vehicles.append(vehicle)
        else:
            new_vehicles.append(vehicle)

    new_guns = []
    duplicate_guns = []

    for gun in guns:
        key = (gun.get('name'), gun.get('nation'))
        if key in existing_guns:
            duplicate_guns.append(gun)
        else:
            new_guns.append(gun)

    # Save to JSON
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(VEHICLES_JSON, 'w', encoding='utf-8') as f:
        json.dump(new_vehicles, f, indent=2, ensure_ascii=False)

    with open(GUNS_JSON, 'w', encoding='utf-8') as f:
        json.dump(new_guns, f, indent=2, ensure_ascii=False)

    # Report
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Vehicles extracted: {len(vehicles)}")
    print(f"  New: {len(new_vehicles)}")
    print(f"  Duplicates skipped: {len(duplicate_vehicles)}")
    print(f"\nGuns extracted: {len(guns)}")
    print(f"  New: {len(new_guns)}")
    print(f"  Duplicates skipped: {len(duplicate_guns)}")
    print(f"\nOutput files:")
    print(f"  {VEHICLES_JSON}")
    print(f"  {GUNS_JSON}")
    print("=" * 80)

    if duplicate_vehicles:
        print("\nDuplicate vehicles skipped:")
        for v in duplicate_vehicles[:10]:
            print(f"  - {v.get('name')} ({v.get('nation')})")
        if len(duplicate_vehicles) > 10:
            print(f"  ... and {len(duplicate_vehicles) - 10} more")

    if duplicate_guns:
        print("\nDuplicate guns skipped:")
        for g in duplicate_guns[:10]:
            print(f"  - {g.get('name')} ({g.get('nation')})")
        if len(duplicate_guns) > 10:
            print(f"  ... and {len(duplicate_guns) - 10} more")


if __name__ == '__main__':
    main()
