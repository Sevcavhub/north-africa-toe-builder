"""
Analyze armor conversion patterns from BattleGroup reference data.

Since WWIITANKS armor data is unavailable (0% populated), we'll analyze
the BG armor letter distribution and vehicle type patterns to build a
lookup-based armor assignment system.

Strategy:
1. Analyze armor letter frequency by vehicle type
2. Build vehicle name -> armor mapping from combined datasets
3. Create armor assignment rules by vehicle class/variant
4. Generate lookup table for 602+ vehicles
"""

import sqlite3
import json
from collections import defaultdict


def analyze_armor_patterns():
    """Analyze BattleGroup armor letter patterns across all vehicles."""

    conn = sqlite3.connect('database/master_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("ARMOR CONVERSION PATTERN ANALYSIS")
    print("=" * 80)

    # Combine data from both bg_reference and bg_builder (97.7% accurate)
    # Use UNION to simulate FULL OUTER JOIN
    cursor.execute("""
        SELECT name, armor_front, armor_side, armor_rear, nation, source
        FROM (
            SELECT
                r.name as name,
                r.armor_front as armor_front,
                r.armor_side as armor_side,
                r.armor_rear as armor_rear,
                r.nation as nation,
                'bg_reference' as source
            FROM bg_reference_vehicles r
            WHERE r.armor_front IS NOT NULL OR r.armor_side IS NOT NULL OR r.armor_rear IS NOT NULL

            UNION

            SELECT
                b.name as name,
                b.armor_front as armor_front,
                b.armor_side as armor_side,
                b.armor_rear as armor_rear,
                '' as nation,
                'bg_builder' as source
            FROM bg_builder_vehicles b
            WHERE (b.armor_front IS NOT NULL OR b.armor_side IS NOT NULL OR b.armor_rear IS NOT NULL)
              AND NOT EXISTS (
                  SELECT 1 FROM bg_reference_vehicles r
                  WHERE LOWER(TRIM(r.name)) = LOWER(TRIM(b.name))
              )
        )
        ORDER BY name
    """)

    vehicles = cursor.fetchall()

    print(f"\nTotal vehicles with armor data: {len(vehicles)}")

    # Armor letter distribution
    armor_front_dist = defaultdict(int)
    armor_side_dist = defaultdict(int)
    armor_rear_dist = defaultdict(int)

    for v in vehicles:
        if v['armor_front']:
            armor_front_dist[v['armor_front']] += 1
        if v['armor_side']:
            armor_side_dist[v['armor_side']] += 1
        if v['armor_rear']:
            armor_rear_dist[v['armor_rear']] += 1

    print("\nARMOR LETTER DISTRIBUTION")
    print("-" * 80)

    print("\nFront Armor:")
    for letter in sorted(armor_front_dist.keys()):
        count = armor_front_dist[letter]
        pct = count / len([v for v in vehicles if v['armor_front']]) * 100
        bar = "#" * int(pct / 2)
        print(f"  {letter:2}: {count:3} ({pct:5.1f}%) {bar}")

    print("\nSide Armor:")
    for letter in sorted(armor_side_dist.keys()):
        count = armor_side_dist[letter]
        pct = count / len([v for v in vehicles if v['armor_side']]) * 100
        bar = "#" * int(pct / 2)
        print(f"  {letter:2}: {count:3} ({pct:5.1f}%) {bar}")

    print("\nRear Armor:")
    for letter in sorted(armor_rear_dist.keys()):
        count = armor_rear_dist[letter]
        pct = count / len([v for v in vehicles if v['armor_rear']]) * 100
        bar = "#" * int(pct / 2)
        print(f"  {letter:2}: {count:3} ({pct:5.1f}%) {bar}")

    # Analyze patterns by vehicle type/class
    print("\n" + "=" * 80)
    print("ARMOR PATTERNS BY VEHICLE CLASS")
    print("=" * 80)

    vehicle_classes = {
        'Heavy Tanks': ['Tiger', 'Churchill', 'KV-', 'IS-'],
        'Medium Tanks': ['Panzer III', 'Panzer IV', 'Sherman', 'T-34', 'Crusader', 'Valentine', 'Grant', 'Lee'],
        'Light Tanks': ['Panzer II', 'Panzer I', 'Stuart', 'Honey', 'Tetrarch'],
        'Tank Destroyers': ['StuG', 'Marder', 'Hetzer', 'Panzerjager', 'Achilles', 'Wolverine', 'M10'],
        'Armored Cars': ['SdKfz 2', 'Dingo', 'Humber', 'AEC', 'Autoblinda'],
        'Halftracks': ['SdKfz 25', 'M3 Half', 'M2 Half', 'Carrier'],
        'Soft-Skin': ['Truck', 'Jeep', 'Kubelwagen', 'Car', 'Motorcycle']
    }

    class_armor = defaultdict(lambda: {'front': [], 'side': [], 'rear': []})

    for v in vehicles:
        for vclass, patterns in vehicle_classes.items():
            if any(p in v['name'] for p in patterns):
                if v['armor_front']:
                    class_armor[vclass]['front'].append(v['armor_front'])
                if v['armor_side']:
                    class_armor[vclass]['side'].append(v['armor_side'])
                if v['armor_rear']:
                    class_armor[vclass]['rear'].append(v['armor_rear'])
                break

    for vclass, armor_data in sorted(class_armor.items()):
        print(f"\n{vclass}:")
        if armor_data['front']:
            front_common = max(set(armor_data['front']), key=armor_data['front'].count)
            print(f"  Front: Most common = {front_common} (range: {min(armor_data['front'])} to {max(armor_data['front'])})")
        if armor_data['side']:
            side_common = max(set(armor_data['side']), key=armor_data['side'].count)
            print(f"  Side:  Most common = {side_common} (range: {min(armor_data['side'])} to {max(armor_data['side'])})")
        if armor_data['rear']:
            rear_common = max(set(armor_data['rear']), key=armor_data['rear'].count)
            print(f"  Rear:  Most common = {rear_common} (range: {min(armor_data['rear'])} to {max(armor_data['rear'])})")

    # Build complete vehicle name -> armor mapping
    print("\n" + "=" * 80)
    print("BUILDING VEHICLE ARMOR LOOKUP TABLE")
    print("=" * 80)

    armor_lookup = {}

    for v in vehicles:
        armor_lookup[v['name']] = {
            'front': v['armor_front'],
            'side': v['armor_side'],
            'rear': v['armor_rear'],
            'source': v['source']
        }

    print(f"\nCreated armor lookup for {len(armor_lookup)} vehicles")

    # Save to JSON
    with open('scripts/battlegroup/lookup_tables/vehicle_armor_lookup.json', 'w') as f:
        json.dump(armor_lookup, f, indent=2)

    print("Saved to: scripts/battlegroup/lookup_tables/vehicle_armor_lookup.json")

    # Generate armor assignment function
    print("\n" + "=" * 80)
    print("ARMOR ASSIGNMENT STRATEGY")
    print("=" * 80)

    print("""
RECOMMENDED APPROACH: Name-based lookup with fallback rules

1. PRIMARY: Vehicle name exact match in lookup table (602 vehicles)
2. FALLBACK: Fuzzy name matching (e.g., "Sherman V" -> "M4 Sherman")
3. FALLBACK: Vehicle class-based defaults (e.g., all Panzers III = L/L/L)
4. FALLBACK: Manual assignment for unmatched vehicles

Confidence Levels:
- 100%: Exact name match from bg_reference (manual entry)
- 95%: Exact name match from bg_builder (97.7% validated)
- 85%: Fuzzy match (partial name)
- 70%: Class-based default
- 0%: No match found (require manual entry)

Coverage:
- With 602 vehicles in lookup: Estimated 85-90% of WITW equipment
- Remaining 10-15%: Require manual assignment or research
    """)

    # Sample lookups
    print("SAMPLE LOOKUPS:")
    sample_vehicles = ['Panzer IV', 'M4 Sherman', 'Tiger I', 'Crusader', 'SdKfz 222']

    for vname in sample_vehicles:
        matches = [name for name in armor_lookup.keys() if vname in name]
        if matches:
            print(f"\n'{vname}' matches:")
            for match in matches[:3]:
                armor = armor_lookup[match]
                print(f"  {match:40} F:{armor['front']:2} S:{armor['side']:2} R:{armor['rear']:2} ({armor['source']})")

    conn.close()

    return {
        'total_vehicles': len(vehicles),
        'armor_lookup_size': len(armor_lookup),
        'front_distribution': dict(armor_front_dist),
        'side_distribution': dict(armor_side_dist),
        'rear_distribution': dict(armor_rear_dist),
        'class_patterns': {k: {
            'front_common': max(set(v['front']), key=v['front'].count) if v['front'] else None,
            'side_common': max(set(v['side']), key=v['side'].count) if v['side'] else None,
            'rear_common': max(set(v['rear']), key=v['rear'].count) if v['rear'] else None
        } for k, v in class_armor.items()}
    }


if __name__ == '__main__':
    results = analyze_armor_patterns()
    print("\n[ANALYSIS COMPLETE]")
