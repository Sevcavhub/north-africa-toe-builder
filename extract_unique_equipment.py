#!/usr/bin/env python3
"""
Extract unique vehicle and gun names from Phase 6 unit JSONs
"""

import json
import os
from pathlib import Path
from typing import Set

def extract_equipment_from_json(file_path: Path) -> tuple[Set[str], Set[str], Set[str]]:
    """Extract all equipment names from a single JSON file

    Returns:
        tuple of (tanks, guns, other_vehicles)
    """
    tanks = set()
    guns = set()
    other_vehicles = set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract from tanks section
        if 'tanks' in data:
            tank_data = data['tanks']
            for category in ['heavy_tanks', 'medium_tanks', 'light_tanks']:
                if category in tank_data:
                    tank_cat = tank_data[category]
                    if isinstance(tank_cat, dict) and 'count' in tank_cat:
                        count_data = tank_cat['count']
                        if isinstance(count_data, dict) and 'variants' in count_data:
                            variants = count_data['variants']
                            if isinstance(variants, dict):
                                tanks.update(variants.keys())

        # Extract from armored_cars section
        if 'armored_cars' in data:
            ac_data = data['armored_cars']
            if isinstance(ac_data, dict) and 'variants' in ac_data:
                variants_data = ac_data['variants']
                if isinstance(variants_data, dict) and 'count' in variants_data:
                    count_data = variants_data['count']
                    if isinstance(count_data, dict):
                        other_vehicles.update(count_data.keys())

        # Extract from field_artillery section
        if 'field_artillery' in data:
            field_arty = data['field_artillery']
            if isinstance(field_arty, dict) and 'variants' in field_arty:
                variants = field_arty['variants']
                if isinstance(variants, dict):
                    guns.update(variants.keys())

        # Extract from anti_tank section
        if 'anti_tank' in data:
            at_guns = data['anti_tank']
            if isinstance(at_guns, dict) and 'variants' in at_guns:
                variants = at_guns['variants']
                if isinstance(variants, dict):
                    guns.update(variants.keys())

        # Extract from anti_aircraft section
        if 'anti_aircraft' in data:
            aa_guns = data['anti_aircraft']
            if isinstance(aa_guns, dict) and 'variants' in aa_guns:
                variants = aa_guns['variants']
                if isinstance(variants, dict):
                    guns.update(variants.keys())

        # Extract from mortars section
        if 'mortars' in data:
            mortars_data = data['mortars']
            if isinstance(mortars_data, dict) and 'variants' in mortars_data:
                variants_data = mortars_data['variants']
                if isinstance(variants_data, dict) and 'count' in variants_data:
                    count_data = variants_data['count']
                    if isinstance(count_data, dict):
                        guns.update(count_data.keys())

        # Extract from trucks section
        if 'trucks' in data:
            trucks_data = data['trucks']
            if isinstance(trucks_data, dict) and 'variants' in trucks_data:
                variants = trucks_data['variants']
                if isinstance(variants, dict):
                    other_vehicles.update(variants.keys())

        # Extract from motorcycles section
        if 'motorcycles' in data:
            mc_data = data['motorcycles']
            if isinstance(mc_data, dict) and 'variants' in mc_data:
                variants = mc_data['variants']
                if isinstance(variants, dict):
                    other_vehicles.update(variants.keys())

        # Extract from support_vehicles section
        if 'support_vehicles' in data:
            support_data = data['support_vehicles']
            if isinstance(support_data, dict) and 'variants' in support_data:
                variants = support_data['variants']
                if isinstance(variants, dict):
                    other_vehicles.update(variants.keys())

    except Exception as e:
        # Silently skip problematic files
        pass

    return tanks, guns, other_vehicles

def main():
    # Find all unit JSON files
    units_dir = Path('data/output/units')
    json_files = list(units_dir.glob('*.json'))

    print(f"Found {len(json_files)} JSON files")

    # Extract all unique equipment names
    all_tanks = set()
    all_guns = set()
    all_other_vehicles = set()

    for json_file in json_files:
        tanks, guns, other_vehicles = extract_equipment_from_json(json_file)
        all_tanks.update(tanks)
        all_guns.update(guns)
        all_other_vehicles.update(other_vehicles)

    # Sort and display
    sorted_tanks = sorted(all_tanks)
    sorted_guns = sorted(all_guns)
    sorted_other_vehicles = sorted(all_other_vehicles)

    print(f"\n{'='*80}")
    print(f"UNIQUE EQUIPMENT FROM PHASE 6 UNIT JSONS")
    print(f"{'='*80}")
    print(f"Total tanks: {len(sorted_tanks)}")
    print(f"Total guns (artillery, AT, AA, mortars): {len(sorted_guns)}")
    print(f"Total other vehicles (armored cars, trucks, etc.): {len(sorted_other_vehicles)}")
    print(f"GRAND TOTAL: {len(sorted_tanks) + len(sorted_guns) + len(sorted_other_vehicles)}\n")

    # Save to file
    output_file = Path('unique_equipment_list.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("UNIQUE EQUIPMENT FROM PHASE 6 UNIT JSONS\n")
        f.write("="*80 + "\n\n")

        f.write(f"TANKS ({len(sorted_tanks)} items)\n")
        f.write("="*80 + "\n")
        for i, name in enumerate(sorted_tanks, 1):
            f.write(f"{i:3d}. {name}\n")

        f.write(f"\n\nGUNS - Artillery, AT, AA, Mortars ({len(sorted_guns)} items)\n")
        f.write("="*80 + "\n")
        for i, name in enumerate(sorted_guns, 1):
            f.write(f"{i:3d}. {name}\n")

        f.write(f"\n\nOTHER VEHICLES - Armored Cars, Trucks, Support ({len(sorted_other_vehicles)} items)\n")
        f.write("="*80 + "\n")
        for i, name in enumerate(sorted_other_vehicles, 1):
            f.write(f"{i:3d}. {name}\n")

        f.write(f"\n\nGRAND TOTAL: {len(sorted_tanks) + len(sorted_guns) + len(sorted_other_vehicles)} items\n")

    print(f"{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}")

    # Also print the lists to console
    print(f"\n\nTANKS ({len(sorted_tanks)} items)")
    print("="*80)
    for i, name in enumerate(sorted_tanks, 1):
        print(f"{i:3d}. {name}")

    print(f"\n\nGUNS - Artillery, AT, AA, Mortars ({len(sorted_guns)} items)")
    print("="*80)
    for i, name in enumerate(sorted_guns, 1):
        print(f"{i:3d}. {name}")

    print(f"\n\nOTHER VEHICLES - Armored Cars, Trucks, Support ({len(sorted_other_vehicles)} items)")
    print("="*80)
    for i, name in enumerate(sorted_other_vehicles, 1):
        print(f"{i:3d}. {name}")

if __name__ == '__main__':
    main()
