#!/usr/bin/env python3
"""
Compile Operation Torch equipment from existing Battlegroup extractions.

Operation Torch (November 1942) - North Africa
Filter criteria:
- Timeline: 1942 (Nov 1942 specifically)
- Nations: american, british, french, german, italian
- Source: Already-extracted high-quality datacard files
"""

import json
import sqlite3
from pathlib import Path
from typing import Set, Tuple, List, Dict

# Paths
OUTPUT_DIR = Path("D:/north-africa-toe-builder/data/output")
DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")

# Source files (already extracted)
SOURCES = {
    'american': OUTPUT_DIR / 'battlegroup_us_vehicles.json',
    'british': OUTPUT_DIR / 'battlegroup_british_vehicles.json',
    'french': OUTPUT_DIR / 'battlegroup_french_polish_romanian_hungarian_complete.json',
    'german': OUTPUT_DIR / 'battlegroup_early_german_vehicles_complete.json',
}

# Output files
TORCH_VEHICLES = OUTPUT_DIR / 'battlegroup_torch_vehicles.json'
TORCH_GUNS = OUTPUT_DIR / 'battlegroup_torch_guns.json'


def get_database_entries() -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    """Get existing vehicles and guns from database for duplicate detection."""
    vehicles = set()
    guns = set()

    if not DB_PATH.exists():
        print(f"⚠️  Database not found: {DB_PATH}")
        return vehicles, guns

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        print(f"Database tables: {', '.join(sorted(tables))}")

        # Try bg_reference_vehicles table
        if 'bg_reference_vehicles' in tables:
            cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
            vehicles = {(row[0], row[1]) for row in cursor.fetchall()}
            print(f"✓ Found {len(vehicles)} vehicles in bg_reference_vehicles")
        else:
            print(f"⚠️  Table 'bg_reference_vehicles' does not exist")

        # Try bg_reference_guns table
        if 'bg_reference_guns' in tables:
            cursor.execute("SELECT name, nation FROM bg_reference_guns")
            guns = {(row[0], row[1]) for row in cursor.fetchall()}
            print(f"✓ Found {len(guns)} guns in bg_reference_guns")
        else:
            print(f"⚠️  Table 'bg_reference_guns' does not exist")

        # Fallback: Check extraction_log or equipment_variants
        if not vehicles and 'equipment_variants' in tables:
            cursor.execute("SELECT DISTINCT name FROM equipment_variants")
            equipment_names = {row[0] for row in cursor.fetchall()}
            print(f"ℹ️  Found {len(equipment_names)} items in equipment_variants (no nation field)")

        conn.close()

    except Exception as e:
        print(f"❌ Database error: {e}")

    return vehicles, guns


def is_torch_timeline(year_range: str) -> bool:
    """Check if equipment was available during Operation Torch (Nov 1942)."""
    if not year_range:
        return False

    year_range = year_range.lower().strip()

    # Handle various formats:
    # "1942", "1942-1943", "1940-42", "1941-1945", etc.

    # Split on '-' or ' to '
    parts = year_range.replace(' to ', '-').split('-')

    # Extract start and end years
    start_year = None
    end_year = None

    for part in parts:
        # Extract 4-digit year
        digits = ''.join(c for c in part if c.isdigit())
        if len(digits) == 4:
            year = int(digits)
            if start_year is None:
                start_year = year
            else:
                end_year = year
        elif len(digits) == 2:  # Handle '40', '42', etc.
            if int(digits) <= 50:  # Assume 1940-1950
                year = 1900 + int(digits)
            else:
                year = 1800 + int(digits)
            if start_year is None:
                start_year = year
            else:
                end_year = year

    if start_year and not end_year:
        end_year = start_year

    # Check if 1942 falls within range
    if start_year and end_year:
        return start_year <= 1942 <= end_year

    return False


def classify_equipment(item: Dict) -> str:
    """Classify if item is a vehicle or gun."""
    # Check if it has movement characteristics (vehicle)
    if item.get('off_road_inches') or item.get('road_inches'):
        return 'vehicle'

    # Check weapons
    weapons = item.get('weapons', [])
    if weapons:
        # If has ammo/mount data, likely a vehicle
        for weapon in weapons:
            if weapon.get('mount'):
                return 'vehicle'

    # Default to gun if has caliber info
    name = item.get('name', '').lower()
    if any(x in name for x in ['mm', 'pdr', 'howitzer', 'gun', 'at', 'anti-tank']):
        return 'gun'

    # Default to vehicle
    return 'vehicle'


def load_source_data() -> Dict[str, List[Dict]]:
    """Load all source extraction files."""
    data = {}

    for nation, filepath in SOURCES.items():
        if not filepath.exists():
            print(f"⚠️  Missing source: {filepath}")
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                items = json.load(f)
                data[nation] = items
                print(f"✓ Loaded {len(items)} items from {filepath.name}")
        except Exception as e:
            print(f"❌ Error loading {filepath.name}: {e}")

    return data


def compile_torch_equipment(source_data: Dict[str, List[Dict]],
                           db_vehicles: Set[Tuple[str, str]],
                           db_guns: Set[Tuple[str, str]]) -> Tuple[List[Dict], List[Dict]]:
    """Filter and compile Torch-relevant equipment."""
    torch_vehicles = []
    torch_guns = []

    duplicate_count = 0
    filtered_timeline = 0
    total_processed = 0

    for nation, items in source_data.items():
        print(f"\n📋 Processing {nation.upper()}...")

        for item in items:
            total_processed += 1
            name = item.get('name')
            year_range = item.get('year_range', '')

            # Check timeline
            if not is_torch_timeline(year_range):
                filtered_timeline += 1
                continue

            # Classify as vehicle or gun
            item_type = classify_equipment(item)

            # Add nation field if missing
            if 'nation' not in item:
                item['nation'] = nation

            # Add source file
            item['source_file'] = 'Battlegroup Torch compilation'
            item['operation'] = 'Operation Torch'
            item['timeline'] = 'November 1942'

            # Check for duplicates
            key = (name, nation)
            if item_type == 'vehicle':
                if key in db_vehicles:
                    duplicate_count += 1
                    continue
                torch_vehicles.append(item)
            else:
                if key in db_guns:
                    duplicate_count += 1
                    continue
                torch_guns.append(item)

    print(f"\n📊 Compilation Statistics:")
    print(f"  Total items processed: {total_processed}")
    print(f"  Filtered (wrong timeline): {filtered_timeline}")
    print(f"  Duplicates skipped: {duplicate_count}")
    print(f"  Torch vehicles: {len(torch_vehicles)}")
    print(f"  Torch guns: {len(torch_guns)}")

    return torch_vehicles, torch_guns


def save_results(vehicles: List[Dict], guns: List[Dict]):
    """Save compiled Torch equipment to JSON files."""
    # Sort by nation then name
    vehicles.sort(key=lambda x: (x.get('nation', ''), x.get('name', '')))
    guns.sort(key=lambda x: (x.get('nation', ''), x.get('name', '')))

    # Save vehicles
    with open(TORCH_VEHICLES, 'w', encoding='utf-8') as f:
        json.dump(vehicles, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved {len(vehicles)} vehicles to: {TORCH_VEHICLES}")

    # Save guns
    with open(TORCH_GUNS, 'w', encoding='utf-8') as f:
        json.dump(guns, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(guns)} guns to: {TORCH_GUNS}")


def generate_summary(vehicles: List[Dict], guns: List[Dict]):
    """Generate human-readable summary by nation."""
    print("\n" + "=" * 80)
    print("OPERATION TORCH EQUIPMENT SUMMARY (November 1942)")
    print("=" * 80)

    # Group by nation
    nation_vehicles = {}
    nation_guns = {}

    for v in vehicles:
        nation = v.get('nation', 'unknown')
        if nation not in nation_vehicles:
            nation_vehicles[nation] = []
        nation_vehicles[nation].append(v['name'])

    for g in guns:
        nation = g.get('nation', 'unknown')
        if nation not in nation_guns:
            nation_guns[nation] = []
        nation_guns[nation].append(g['name'])

    # Print by nation
    for nation in ['american', 'british', 'french', 'german', 'italian']:
        if nation in nation_vehicles or nation in nation_guns:
            print(f"\n{nation.upper()}:")
            if nation in nation_vehicles:
                print(f"  Vehicles ({len(nation_vehicles[nation])}):")
                for name in sorted(nation_vehicles[nation])[:10]:
                    print(f"    - {name}")
                if len(nation_vehicles[nation]) > 10:
                    print(f"    ... and {len(nation_vehicles[nation]) - 10} more")

            if nation in nation_guns:
                print(f"  Guns ({len(nation_guns[nation])}):")
                for name in sorted(nation_guns[nation])[:10]:
                    print(f"    - {name}")
                if len(nation_guns[nation]) > 10:
                    print(f"    ... and {len(nation_guns[nation]) - 10} more")

    print("\n" + "=" * 80)


def main():
    print("=" * 80)
    print("OPERATION TORCH EQUIPMENT COMPILATION")
    print("November 1942 - North Africa")
    print("=" * 80)

    # Get database entries for duplicate detection
    print("\n🔍 Checking database for duplicates...")
    db_vehicles, db_guns = get_database_entries()

    # Load source data
    print("\n📂 Loading source extraction files...")
    source_data = load_source_data()

    if not source_data:
        print("❌ No source data loaded. Aborting.")
        return

    # Compile Torch equipment
    print("\n⚙️  Compiling Torch equipment (1942 timeline)...")
    vehicles, guns = compile_torch_equipment(source_data, db_vehicles, db_guns)

    # Save results
    save_results(vehicles, guns)

    # Generate summary
    generate_summary(vehicles, guns)

    print("\n✅ Compilation complete!")
    print(f"\n📁 Output files:")
    print(f"  • {TORCH_VEHICLES}")
    print(f"  • {TORCH_GUNS}")


if __name__ == '__main__':
    main()
