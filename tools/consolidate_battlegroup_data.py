#!/usr/bin/env python3
"""
Consolidate all BattleGroup vehicle and gun extractions.
Check for duplicates and create a master list.
"""

import json
from pathlib import Path
from collections import defaultdict

def load_all_battlegroup_data():
    """Load all BattleGroup JSON files."""
    output_dir = Path(r'D:\north-africa-toe-builder\data\output')

    # Find all vehicle and gun files
    vehicle_files = list(output_dir.glob('battlegroup*vehicles*.json'))
    gun_files = list(output_dir.glob('battlegroup*guns*.json'))

    print(f"Found {len(vehicle_files)} vehicle files:")
    for f in vehicle_files:
        print(f"  - {f.name}")

    print(f"\nFound {len(gun_files)} gun files:")
    for f in gun_files:
        print(f"  - {f.name}")

    # Load all data
    all_vehicles = []
    all_guns = []

    for vfile in vehicle_files:
        with open(vfile, 'r', encoding='utf-8') as f:
            vehicles = json.load(f)
            for v in vehicles:
                v['source_file'] = vfile.name
                all_vehicles.append(v)

    for gfile in gun_files:
        with open(gfile, 'r', encoding='utf-8') as f:
            guns = json.load(f)
            for g in guns:
                g['source_file'] = gfile.name
                all_guns.append(g)

    print(f"\nTotal loaded: {len(all_vehicles)} vehicles, {len(all_guns)} guns")
    return all_vehicles, all_guns


def check_duplicates(items, item_type="item"):
    """Check for duplicates based on name and nation."""
    seen = {}  # (name, nation) -> list of sources
    duplicates = []
    unique_items = []

    for item in items:
        name = item.get('name', '')
        nation = item.get('nation', '')
        key = (name.lower().strip(), nation.lower().strip())

        if key not in seen:
            seen[key] = []
            unique_items.append(item)

        seen[key].append(item.get('source_file', 'unknown'))

    # Find duplicates
    for (name, nation), sources in seen.items():
        if len(sources) > 1:
            duplicates.append({
                'name': name,
                'nation': nation,
                'count': len(sources),
                'sources': sources
            })

    print(f"\n=== {item_type.upper()} DUPLICATE ANALYSIS ===")
    print(f"Total {item_type}s: {len(items)}")
    print(f"Unique {item_type}s: {len(unique_items)}")
    print(f"Duplicate {item_type}s: {len(duplicates)}")

    if duplicates:
        print(f"\nDuplicate {item_type}s found:")
        for dup in sorted(duplicates, key=lambda x: x['count'], reverse=True):
            print(f"  - {dup['name']} ({dup['nation']}): appears {dup['count']} times")
            for src in set(dup['sources']):
                print(f"    -> {src}")

    return unique_items, duplicates


def main():
    """Main consolidation function."""
    print("=" * 80)
    print("BATTLEGROUP DATA CONSOLIDATION")
    print("=" * 80)

    # Load all data
    all_vehicles, all_guns = load_all_battlegroup_data()

    # Check for duplicates
    unique_vehicles, vehicle_duplicates = check_duplicates(all_vehicles, "vehicle")
    unique_guns, gun_duplicates = check_duplicates(all_guns, "gun")

    # Create summary report
    summary = {
        'consolidation_date': '2025-10-31',
        'total_files_processed': {
            'vehicles': len(set(v.get('source_file', '') for v in all_vehicles)),
            'guns': len(set(g.get('source_file', '') for g in all_guns))
        },
        'vehicles': {
            'total_entries': len(all_vehicles),
            'unique_entries': len(unique_vehicles),
            'duplicates': len(vehicle_duplicates)
        },
        'guns': {
            'total_entries': len(all_guns),
            'unique_entries': len(unique_guns),
            'duplicates': len(gun_duplicates)
        },
        'by_nation': {
            'vehicles': {},
            'guns': {}
        }
    }

    # Count by nation
    for v in unique_vehicles:
        nation = v.get('nation', 'unknown')
        summary['by_nation']['vehicles'][nation] = summary['by_nation']['vehicles'].get(nation, 0) + 1

    for g in unique_guns:
        nation = g.get('nation', 'unknown')
        summary['by_nation']['guns'][nation] = summary['by_nation']['guns'].get(nation, 0) + 1

    print("\n" + "=" * 80)
    print("CONSOLIDATION SUMMARY")
    print("=" * 80)
    print(json.dumps(summary, indent=2))

    # Save consolidated data
    output_dir = Path(r'D:\north-africa-toe-builder\data\output')

    consolidated_vehicles_file = output_dir / 'battlegroup_all_vehicles_consolidated.json'
    consolidated_guns_file = output_dir / 'battlegroup_all_guns_consolidated.json'

    with open(consolidated_vehicles_file, 'w', encoding='utf-8') as f:
        json.dump(unique_vehicles, f, indent=2, ensure_ascii=False)

    with open(consolidated_guns_file, 'w', encoding='utf-8') as f:
        json.dump(unique_guns, f, indent=2, ensure_ascii=False)

    print(f"\nSaved consolidated vehicles to: {consolidated_vehicles_file}")
    print(f"Saved consolidated guns to: {consolidated_guns_file}")

    # Save summary
    summary_file = output_dir / 'battlegroup_consolidation_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Saved summary to: {summary_file}")

    return summary


if __name__ == '__main__':
    main()
