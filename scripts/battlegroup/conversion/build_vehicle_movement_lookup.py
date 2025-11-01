#!/usr/bin/env python3
"""
Build Vehicle Movement Lookup Table

Extracts all vehicle movement data from reference database and creates
a comprehensive lookup table for the movement calculator.

This solves the 61% accuracy issue by using vehicle name lookup instead
of generic type-based formulas.

Output: vehicle_movement_lookup.json
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR.parent.parent.parent / "database" / "master_database.db"
OUTPUT_FILE = SCRIPT_DIR / "lookup_tables" / "vehicle_movement_lookup.json"


def extract_vehicle_movement_data():
    """
    Extract all vehicle movement data from reference database.

    Returns:
        dict: Vehicle name -> movement data mapping
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all vehicles with movement data
    cursor.execute("""
        SELECT name, vehicle_type, off_road_inches, road_inches,
               special_movement, notes
        FROM bg_reference_vehicles
        WHERE off_road_inches IS NOT NULL AND road_inches IS NOT NULL
        ORDER BY name
    """)

    # Track all occurrences of each vehicle name
    vehicle_occurrences = defaultdict(list)

    for name, vtype, off_road, road, special, notes in cursor.fetchall():
        # Create entry
        entry = {
            "off_road": off_road,
            "road": road,
            "vehicle_type": vtype,
            "format": f'{off_road}\"/{road}\"'
        }

        if special:
            entry["special_movement"] = special

        if notes:
            entry["notes"] = notes

        vehicle_occurrences[name].append(entry)

    # Build lookup table, using most common value for duplicates
    vehicle_lookup = {}
    duplicates = {}

    for name, entries in vehicle_occurrences.items():
        if len(entries) == 1:
            # Single occurrence - use it
            vehicle_lookup[name] = entries[0]
        else:
            # Multiple occurrences - find most common movement value
            movement_counts = defaultdict(int)
            for entry in entries:
                key = (entry["off_road"], entry["road"])
                movement_counts[key] += 1

            # Get most common movement
            most_common_movement = max(movement_counts.items(), key=lambda x: x[1])
            off_road, road = most_common_movement[0]

            # Find first entry with this movement
            for entry in entries:
                if entry["off_road"] == off_road and entry["road"] == road:
                    vehicle_lookup[name] = entry
                    break

            # Track as duplicate
            duplicates[name] = {
                "total_occurrences": len(entries),
                "unique_movements": len(movement_counts),
                "most_common": f'{off_road}\"/{road}\"',
                "count": most_common_movement[1]
            }

    conn.close()

    return vehicle_lookup, duplicates


def generate_name_variations(vehicle_name):
    """
    Generate common variations of a vehicle name for fuzzy matching.

    Args:
        vehicle_name: Original vehicle name

    Returns:
        list: List of name variations
    """
    variations = [vehicle_name]

    # Remove common prefixes/suffixes
    name_lower = vehicle_name.lower()

    # Add version without parentheses
    if '(' in vehicle_name:
        variations.append(vehicle_name.split('(')[0].strip())

    # Add version without designation suffixes
    if ' or ' in name_lower:
        variations.append(vehicle_name.split(' or ')[0].strip())

    # Common abbreviations
    abbreviations = {
        'SdKfz': 'Sonderkraftfahrzeug',
        'Pz': 'Panzer',
        'Kfz': 'Kraftfahrzeug',
        'M3': 'M-3',
        'M4': 'M-4',
        'T-34': 'T34',
        'Mk': 'Mark',
    }

    for abbr, full in abbreviations.items():
        if abbr.lower() in name_lower:
            variations.append(vehicle_name.replace(abbr, full))
            variations.append(vehicle_name.replace(abbr.upper(), full))

    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for v in variations:
        v_lower = v.lower()
        if v_lower not in seen:
            seen.add(v_lower)
            unique_variations.append(v)

    return unique_variations


def build_lookup_table():
    """
    Build the complete vehicle movement lookup table.

    Returns:
        dict: Complete lookup table with metadata
    """
    print("=" * 80)
    print("BUILDING VEHICLE MOVEMENT LOOKUP TABLE")
    print("=" * 80)
    print()

    # Extract data
    print("Extracting vehicle movement data from reference database...")
    vehicle_lookup, duplicates = extract_vehicle_movement_data()

    print(f"Extracted {len(vehicle_lookup)} unique vehicles")

    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate vehicle names - using most common movement:")
        for name, info in list(duplicates.items())[:5]:
            print(f"  - {name}: {info['total_occurrences']} occurrences, using {info['most_common']} ({info['count']}x)")

    # Build lookup table with metadata
    lookup_table = {
        "metadata": {
            "description": "Vehicle name to movement (inches) lookup table",
            "source": "bg_reference_vehicles table",
            "total_vehicles": len(vehicle_lookup),
            "duplicate_names": len(duplicates),
            "format": "off_road\"/road\"",
            "usage": "Primary lookup for movement_calculator.py"
        },
        "vehicles": vehicle_lookup
    }

    # Add common name variations for top vehicles
    common_vehicles = [
        "Tiger", "Panther", "Panzer IV", "Sherman", "T-34",
        "Churchill", "Cromwell", "M3 Lee", "Sturmgeschütz",
        "Panzerjäger", "Marder", "Hetzer"
    ]

    print("\nGenerating name variations for common vehicles...")

    # Collect variations first (don't modify dict during iteration)
    variations_to_add = {}
    for common_name in common_vehicles:
        # Find vehicles matching this common name
        for full_name, data in vehicle_lookup.items():
            if common_name.lower() in full_name.lower():
                variations = generate_name_variations(full_name)
                for variation in variations:
                    if variation not in lookup_table["vehicles"] and variation not in variations_to_add:
                        variations_to_add[variation] = data

    # Now add all variations
    lookup_table["vehicles"].update(variations_to_add)
    print(f"Added {len(variations_to_add)} name variations")

    # Save to file
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(lookup_table, f, indent=2, ensure_ascii=False)

    print(f"\nLookup table saved to: {OUTPUT_FILE}")
    print(f"  Total entries (including variations): {len(lookup_table['vehicles'])}")

    return lookup_table


def analyze_movement_patterns(lookup_table):
    """
    Analyze movement patterns in the lookup table.

    Args:
        lookup_table: The generated lookup table
    """
    print("\n" + "=" * 80)
    print("MOVEMENT PATTERN ANALYSIS")
    print("=" * 80)

    vehicles = lookup_table["vehicles"]

    # Group by movement values
    movement_groups = defaultdict(list)
    for name, data in vehicles.items():
        key = f'{data["off_road"]}/{data["road"]}'
        movement_groups[key].append(name)

    # Show most common movement values
    print("\nMost Common Movement Values:")
    print(f"{'Movement':12} | {'Count':5} | Examples")
    print("-" * 70)

    sorted_groups = sorted(movement_groups.items(),
                          key=lambda x: len(x[1]),
                          reverse=True)

    for movement, vehicles_list in sorted_groups[:15]:
        examples = ', '.join(vehicles_list[:3])
        if len(vehicles_list) > 3:
            examples += f", ... ({len(vehicles_list) - 3} more)"
        print(f'{movement:12} | {len(vehicles_list):5} | {examples}')

    # Analyze by type
    print("\nMovement by Vehicle Type:")
    type_movements = defaultdict(lambda: defaultdict(int))

    for name, data in vehicles.items():
        vtype = data.get("vehicle_type") or "unknown"
        movement = f'{data["off_road"]}/{data["road"]}'
        type_movements[vtype][movement] += 1

    for vtype in sorted(type_movements.keys()):
        movements = type_movements[vtype]
        total = sum(movements.values())
        print(f"\n  {vtype} ({total} vehicles):")
        for movement, count in sorted(movements.items(),
                                     key=lambda x: x[1],
                                     reverse=True)[:3]:
            pct = (count / total * 100)
            print(f"    {movement:12} - {count:3} vehicles ({pct:.1f}%)")


def main():
    """Main execution."""
    lookup_table = build_lookup_table()
    analyze_movement_patterns(lookup_table)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review the lookup table: lookup_tables/vehicle_movement_lookup.json")
    print("2. Update movement_calculator.py to use this lookup table")
    print("3. Re-validate to confirm 95%+ accuracy")
    print()


if __name__ == "__main__":
    main()
