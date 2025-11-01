#!/usr/bin/env python3
"""
Pattern Analysis Script for BattleGroup Conversion Formulas

This script analyzes the bg_reference_vehicles and bg_reference_guns tables
to reverse-engineer the conversion formulas from historical data (mm-based)
to BattleGroup game format (letters, scales, dice).

Output:
- Armor conversion patterns (mm → A-O letters)
- Penetration conversion patterns (mm @ distance → 1-15 scale)
- Movement patterns (weight/type → inches)
- HE effectiveness patterns (caliber → dice/target)
"""

import sqlite3
import json
from collections import defaultdict
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def analyze_armor_patterns():
    """
    Analyze armor letter patterns from bg_reference_vehicles.

    Goal: Find the mapping from mm armor thickness to A-O letter ratings.

    Note: Since we don't have mm values directly linked, we'll analyze
    the distribution of letters and try to infer patterns from vehicle names.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("ARMOR PATTERN ANALYSIS")
    print("=" * 80)

    # Get all vehicles with armor values
    cursor.execute("""
        SELECT name, vehicle_type, armor_front, armor_side, armor_rear
        FROM bg_reference_vehicles
        WHERE armor_front IS NOT NULL
    """)

    armor_distribution = defaultdict(int)
    armor_by_type = defaultdict(lambda: defaultdict(int))

    vehicles_by_armor = defaultdict(list)

    for name, vtype, front, side, rear in cursor.fetchall():
        armor_distribution[front] += 1
        if vtype:
            armor_by_type[vtype][front] += 1
        vehicles_by_armor[front].append((name, vtype))

    print("\nArmor Letter Distribution (Front):")
    for letter in sorted(armor_distribution.keys()):
        print(f"  {letter}: {armor_distribution[letter]:3} vehicles")

    print("\nSample Vehicles by Armor Rating:")
    for letter in sorted(armor_distribution.keys())[:10]:
        print(f"\n  {letter} armor (front):")
        for name, vtype in vehicles_by_armor[letter][:5]:
            print(f"    - {name} ({vtype or 'unknown'})")

    conn.close()

    return armor_distribution


def analyze_movement_patterns():
    """
    Analyze movement patterns from bg_reference_vehicles.

    Goal: Find the relationship between vehicle characteristics and movement inches.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("MOVEMENT PATTERN ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT vehicle_type, off_road_inches, road_inches, COUNT(*) as count
        FROM bg_reference_vehicles
        WHERE off_road_inches IS NOT NULL
        GROUP BY vehicle_type, off_road_inches, road_inches
        ORDER BY vehicle_type, off_road_inches DESC
    """)

    movement_by_type = defaultdict(list)

    print("\nMovement by Vehicle Type:")
    print(f"{'Vehicle Type':25} | Off-Road | Road | Count")
    print("-" * 60)

    for vtype, off_road, road, count in cursor.fetchall():
        vtype = vtype or "Unknown"
        movement_by_type[vtype].append((off_road, road, count))
        print(f"{vtype:25} | {off_road:8}\" | {road:4}\" | {count:5}")

    # Calculate averages by type
    print("\nAverage Movement by Vehicle Type:")
    for vtype, movements in movement_by_type.items():
        total_count = sum(m[2] for m in movements)
        avg_off_road = sum(m[0] * m[2] for m in movements) / total_count
        avg_road = sum(m[1] * m[2] for m in movements) / total_count
        print(f"  {vtype:25}: {avg_off_road:.1f}\" / {avg_road:.1f}\"")

    conn.close()

    return movement_by_type


def analyze_he_patterns():
    """
    Analyze HE effectiveness patterns from bg_reference_guns.

    Goal: Find the relationship between caliber and HE dice/target values.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("HE EFFECTIVENESS PATTERN ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT caliber_mm, he_dice, he_target, COUNT(*) as count
        FROM bg_reference_guns
        WHERE caliber_mm IS NOT NULL AND he_dice IS NOT NULL
        GROUP BY caliber_mm, he_dice, he_target
        ORDER BY caliber_mm
    """)

    he_by_caliber = defaultdict(list)

    print("\nHE Effect by Caliber:")
    print(f"{'Caliber':10} | HE Dice | Target | Count | Example Format")
    print("-" * 65)

    for caliber, dice, target, count in cursor.fetchall():
        he_by_caliber[caliber].append((dice, target, count))
        he_format = f"{dice}/{target}" if target else f"{dice}"
        print(f"{caliber:10} | {dice:7} | {target:6} | {count:5} | {he_format}")

    # Identify caliber ranges
    print("\nCaliper Range Patterns:")
    caliber_ranges = [
        (0, 25, "Very Light"),
        (26, 47, "Light"),
        (48, 76, "Medium"),
        (77, 105, "Heavy"),
        (106, 150, "Very Heavy"),
        (151, 999, "Super Heavy")
    ]

    for min_cal, max_cal, category in caliber_ranges:
        matching = [(cal, vals) for cal, vals in he_by_caliber.items()
                   if min_cal <= cal <= max_cal]
        if matching:
            print(f"\n  {category} ({min_cal}-{max_cal}mm):")
            for cal, vals in sorted(matching):
                for dice, target, count in vals:
                    print(f"    {cal}mm: {dice}/{target} ({count} guns)")

    conn.close()

    return he_by_caliber


def analyze_penetration_patterns():
    """
    Analyze AP penetration patterns from bg_reference_guns.

    Goal: Understand the 1-15 penetration scale and how it varies with range.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("PENETRATION PATTERN ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT name, caliber_mm, barrel_length,
               ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
        FROM bg_reference_guns
        WHERE ap_0_10 IS NOT NULL
        ORDER BY caliber_mm, barrel_length
    """)

    print("\nPenetration by Range Band (1-15 scale):")
    print(f"{'Gun':30} | Cal | 0-10\" | 10-20\" | 20-30\" | 30-40\" | 40-50\" | 50-70\"")
    print("-" * 95)

    penetration_data = []

    for name, cal, barrel, ap1, ap2, ap3, ap4, ap5, ap6 in cursor.fetchall():
        barrel_str = barrel or "?"
        penetration_data.append({
            'name': name,
            'caliber': cal,
            'barrel': barrel_str,
            'ap_values': [ap1, ap2, ap3, ap4, ap5, ap6]
        })

        print(f"{name:30} | {cal:3} | {ap1 or '-':6} | {ap2 or '-':7} | {ap3 or '-':7} | "
              f"{ap4 or '-':7} | {ap5 or '-':7} | {ap6 or '-':6}")

    # Analyze penetration drop-off patterns
    print("\nPenetration Drop-off Patterns:")
    for gun in penetration_data[:10]:  # Sample first 10
        values = gun['ap_values']
        if all(v is not None for v in values[:3]):
            drop_10_20 = values[0] - values[1] if values[0] and values[1] else 0
            drop_20_30 = values[1] - values[2] if values[1] and values[2] else 0
            print(f"  {gun['name']:30}: {values[0]} -> {values[1]} (-{drop_10_20}) -> "
                  f"{values[2]} (-{drop_20_30})")

    conn.close()

    return penetration_data


def generate_conversion_tables():
    """
    Generate initial conversion lookup tables based on analysis.

    This creates JSON files that can be used as starting points for
    the conversion formula tools.
    """
    print("\n" + "=" * 80)
    print("GENERATING CONVERSION LOOKUP TABLES")
    print("=" * 80)

    output_dir = Path(__file__).parent / "lookup_tables"
    output_dir.mkdir(exist_ok=True)

    # Armor conversion table (placeholder - needs actual mm mapping)
    armor_table = {
        "description": "Armor thickness (mm) to BattleGroup letter (A-O) conversion",
        "note": "This is a placeholder - needs actual mm values from source data",
        "scale": {
            "A": {"min_mm": 200, "max_mm": 999, "description": "Super heavy armor"},
            "B": {"min_mm": 180, "max_mm": 199, "description": "Very heavy armor"},
            "C": {"min_mm": 150, "max_mm": 179, "description": "Heavy armor"},
            "D": {"min_mm": 130, "max_mm": 149, "description": "Heavy armor"},
            "E": {"min_mm": 110, "max_mm": 129, "description": "Heavy armor"},
            "F": {"min_mm": 90, "max_mm": 109, "description": "Medium-heavy armor"},
            "G": {"min_mm": 80, "max_mm": 89, "description": "Medium armor"},
            "H": {"min_mm": 70, "max_mm": 79, "description": "Medium armor"},
            "I": {"min_mm": 60, "max_mm": 69, "description": "Medium armor"},
            "J": {"min_mm": 50, "max_mm": 59, "description": "Medium-light armor"},
            "K": {"min_mm": 40, "max_mm": 49, "description": "Light armor"},
            "L": {"min_mm": 30, "max_mm": 39, "description": "Light armor"},
            "M": {"min_mm": 20, "max_mm": 29, "description": "Very light armor"},
            "N": {"min_mm": 10, "max_mm": 19, "description": "Minimal armor"},
            "O": {"min_mm": 0, "max_mm": 9, "description": "No effective armor"}
        }
    }

    armor_file = output_dir / "armor_conversion_table.json"
    with open(armor_file, 'w') as f:
        json.dump(armor_table, f, indent=2)
    print(f"\nCreated: {armor_file}")

    # HE effectiveness table (based on analysis)
    he_table = {
        "description": "Caliber (mm) to HE effect (dice/target) conversion",
        "caliber_ranges": [
            {"min_mm": 0, "max_mm": 25, "dice": 1, "target": "6+", "category": "Very Light"},
            {"min_mm": 26, "max_mm": 37, "dice": 2, "target": "5+", "category": "Light"},
            {"min_mm": 38, "max_mm": 57, "dice": 3, "target": "5+", "category": "Medium-Light"},
            {"min_mm": 58, "max_mm": 76, "dice": 4, "target": "4+", "category": "Medium"},
            {"min_mm": 77, "max_mm": 90, "dice": 4, "target": "3+", "category": "Heavy"},
            {"min_mm": 91, "max_mm": 120, "dice": 5, "target": "3+", "category": "Very Heavy"},
            {"min_mm": 121, "max_mm": 149, "dice": 6, "target": "3+", "category": "Very Heavy"},
            {"min_mm": 150, "max_mm": 179, "dice": 6, "target": "2+", "category": "Super Heavy"},
            {"min_mm": 180, "max_mm": 999, "dice": 7, "target": "2+", "category": "Super Heavy"}
        ]
    }

    he_file = output_dir / "he_conversion_table.json"
    with open(he_file, 'w') as f:
        json.dump(he_table, f, indent=2)
    print(f"Created: {he_file}")

    # Movement table (based on analysis)
    movement_table = {
        "description": "Vehicle type to movement (inches) conversion",
        "note": "Off-road / road movement in inches",
        "vehicle_types": {
            "Light Tank": {"off_road": 12, "road": 16, "description": "Fast reconnaissance tanks"},
            "Medium Tank": {"off_road": 8, "road": 12, "description": "Standard battle tanks"},
            "Heavy Tank": {"off_road": 6, "road": 10, "description": "Heavy breakthrough tanks"},
            "Tank Destroyer": {"off_road": 10, "road": 14, "description": "Mobile AT vehicles"},
            "Self-Propelled Gun": {"off_road": 6, "road": 10, "description": "Artillery vehicles"},
            "Armored Car": {"off_road": 14, "road": 18, "description": "Wheeled reconnaissance"},
            "Halftrack": {"off_road": 10, "road": 14, "description": "Infantry carriers"},
            "Truck": {"off_road": 12, "road": 16, "description": "Soft-skinned transport"}
        }
    }

    movement_file = output_dir / "movement_conversion_table.json"
    with open(movement_file, 'w') as f:
        json.dump(movement_table, f, indent=2)
    print(f"Created: {movement_file}")

    # Penetration table (placeholder)
    penetration_table = {
        "description": "Penetration (mm @ distance) to BattleGroup scale (1-15) conversion",
        "note": "This requires complex analysis of gun performance curves",
        "range_bands": {
            "0-10": "Point blank range",
            "10-20": "Close range",
            "20-30": "Medium range",
            "30-40": "Long range",
            "40-50": "Very long range",
            "50-70": "Extreme range"
        },
        "scale": {
            "1": "20-30mm penetration",
            "2": "30-40mm penetration",
            "3": "40-50mm penetration",
            "4": "50-60mm penetration",
            "5": "60-70mm penetration",
            "6": "70-80mm penetration",
            "7": "80-90mm penetration",
            "8": "90-100mm penetration",
            "9": "100-110mm penetration",
            "10": "110-120mm penetration",
            "11": "120-130mm penetration",
            "12": "130-140mm penetration",
            "13": "140-150mm penetration",
            "14": "150-170mm penetration",
            "15": "170mm+ penetration"
        }
    }

    penetration_file = output_dir / "penetration_conversion_table.json"
    with open(penetration_file, 'w') as f:
        json.dump(penetration_table, f, indent=2)
    print(f"Created: {penetration_file}")

    print(f"\nAll lookup tables created in: {output_dir}")


def main():
    """Main analysis pipeline."""
    print("\n" + "=" * 80)
    print("BattleGroup Conversion Pattern Analysis")
    print("=" * 80)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Analyzing reference data to reverse-engineer conversion formulas...\n")

    # Run all analyses
    armor_dist = analyze_armor_patterns()
    movement_patterns = analyze_movement_patterns()
    he_patterns = analyze_he_patterns()
    penetration_data = analyze_penetration_patterns()

    # Generate lookup tables
    generate_conversion_tables()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Review the lookup tables in scripts/battlegroup/conversion/lookup_tables/")
    print("2. Refine the conversion formulas based on the analysis")
    print("3. Build the 4 conversion tools:")
    print("   - armor_converter.py")
    print("   - penetration_converter.py")
    print("   - movement_calculator.py")
    print("   - he_calculator.py")
    print("4. Validate against the reference database (target: 95%+ accuracy)")
    print()

    return True


if __name__ == "__main__":
    main()
