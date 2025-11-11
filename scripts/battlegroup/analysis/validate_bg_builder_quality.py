"""
Cross-validate bg_builder_vehicles against bg_reference_vehicles.

Purpose: Determine if bg_builder scraped data is accurate enough to use
for formula reverse-engineering.

Method: Compare overlapping vehicles between the two tables and calculate
match rates for armor and movement data.

Decision Criteria:
- If >90% match: bg_builder data is CLEAN, use all 602 vehicles
- If 70-90% match: bg_builder data is USABLE but needs manual review
- If <70% match: bg_builder data is UNRELIABLE, use only bg_reference (281 vehicles)
"""

import sqlite3
from collections import defaultdict


def validate_bg_builder_quality():
    """Compare bg_builder to bg_reference for overlapping vehicles."""

    conn = sqlite3.connect('database/master_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("BG_BUILDER DATA QUALITY VALIDATION")
    print("=" * 80)

    # Find ALL overlapping vehicles (not just 10)
    cursor.execute("""
        SELECT
            r.id as ref_id,
            r.name as ref_name,
            r.armor_front as ref_armor_front,
            r.armor_side as ref_armor_side,
            r.armor_rear as ref_armor_rear,
            r.off_road_inches as ref_off_road,
            r.road_inches as ref_road,
            r.nation as ref_nation,
            b.id as builder_id,
            b.name as builder_name,
            b.armor_front as builder_armor_front,
            b.armor_side as builder_armor_side,
            b.armor_rear as builder_armor_rear,
            b.movement_off_road as builder_off_road,
            b.movement_road as builder_road
        FROM bg_reference_vehicles r
        LEFT JOIN bg_builder_vehicles b ON LOWER(TRIM(r.name)) = LOWER(TRIM(b.name))
        WHERE b.id IS NOT NULL
        ORDER BY r.name
    """)

    overlaps = cursor.fetchall()

    print(f"\nFound {len(overlaps)} overlapping vehicles between tables\n")

    # Statistics
    armor_front_matches = 0
    armor_side_matches = 0
    armor_rear_matches = 0
    movement_off_road_matches = 0
    movement_road_matches = 0

    armor_front_total = 0
    armor_side_total = 0
    armor_rear_total = 0
    movement_off_road_total = 0
    movement_road_total = 0

    mismatches = {
        'armor_front': [],
        'armor_side': [],
        'armor_rear': [],
        'movement_off_road': [],
        'movement_road': []
    }

    for row in overlaps:
        # Armor front comparison
        if row['ref_armor_front'] and row['builder_armor_front']:
            armor_front_total += 1
            if row['ref_armor_front'].strip() == row['builder_armor_front'].strip():
                armor_front_matches += 1
            else:
                mismatches['armor_front'].append(row)

        # Armor side comparison
        if row['ref_armor_side'] and row['builder_armor_side']:
            armor_side_total += 1
            if row['ref_armor_side'].strip() == row['builder_armor_side'].strip():
                armor_side_matches += 1
            else:
                mismatches['armor_side'].append(row)

        # Armor rear comparison
        if row['ref_armor_rear'] and row['builder_armor_rear']:
            armor_rear_total += 1
            if row['ref_armor_rear'].strip() == row['builder_armor_rear'].strip():
                armor_rear_matches += 1
            else:
                mismatches['armor_rear'].append(row)

        # Off-road movement comparison
        if row['ref_off_road'] is not None and row['builder_off_road'] is not None:
            movement_off_road_total += 1
            if row['ref_off_road'] == row['builder_off_road']:
                movement_off_road_matches += 1
            else:
                mismatches['movement_off_road'].append(row)

        # Road movement comparison
        if row['ref_road'] is not None and row['builder_road'] is not None:
            movement_road_total += 1
            if row['ref_road'] == row['builder_road']:
                movement_road_matches += 1
            else:
                mismatches['movement_road'].append(row)

    # Calculate match rates
    print("MATCH RATES (bg_reference vs bg_builder)")
    print("-" * 80)

    armor_front_rate = (armor_front_matches / armor_front_total * 100) if armor_front_total > 0 else 0
    armor_side_rate = (armor_side_matches / armor_side_total * 100) if armor_side_total > 0 else 0
    armor_rear_rate = (armor_rear_matches / armor_rear_total * 100) if armor_rear_total > 0 else 0
    movement_off_road_rate = (movement_off_road_matches / movement_off_road_total * 100) if movement_off_road_total > 0 else 0
    movement_road_rate = (movement_road_matches / movement_road_total * 100) if movement_road_total > 0 else 0

    print(f"Armor Front:      {armor_front_matches}/{armor_front_total} ({armor_front_rate:.1f}%)")
    print(f"Armor Side:       {armor_side_matches}/{armor_side_total} ({armor_side_rate:.1f}%)")
    print(f"Armor Rear:       {armor_rear_matches}/{armor_rear_total} ({armor_rear_rate:.1f}%)")
    print(f"Movement Off-Road: {movement_off_road_matches}/{movement_off_road_total} ({movement_off_road_rate:.1f}%)")
    print(f"Movement Road:    {movement_road_matches}/{movement_road_total} ({movement_road_rate:.1f}%)")

    overall_armor = (armor_front_matches + armor_side_matches + armor_rear_matches) / (armor_front_total + armor_side_total + armor_rear_total) * 100 if (armor_front_total + armor_side_total + armor_rear_total) > 0 else 0
    overall_movement = (movement_off_road_matches + movement_road_matches) / (movement_off_road_total + movement_road_total) * 100 if (movement_off_road_total + movement_road_total) > 0 else 0

    print(f"\nOVERALL MATCH RATES:")
    print(f"  Armor (all facings): {overall_armor:.1f}%")
    print(f"  Movement (both types): {overall_movement:.1f}%")

    # Show sample mismatches
    print("\n" + "=" * 80)
    print("SAMPLE MISMATCHES (First 10 of each type)")
    print("=" * 80)

    for field, mismatch_list in mismatches.items():
        if len(mismatch_list) > 0:
            print(f"\n{field.upper()} MISMATCHES ({len(mismatch_list)} total):")
            for i, row in enumerate(mismatch_list[:10]):
                if 'armor' in field:
                    ref_val = row[f'ref_{field}']
                    builder_val = row[f'builder_{field}']
                else:
                    ref_val = row[f'ref_{field.replace("movement_", "")}']
                    builder_val = row[f'builder_{field.replace("movement_", "")}']

                print(f"  {i+1}. {row['ref_name'][:40]:40} | REF: {ref_val:6} | BUILDER: {builder_val:6}")

    # Decision logic
    print("\n" + "=" * 80)
    print("QUALITY ASSESSMENT")
    print("=" * 80)

    avg_match_rate = (overall_armor + overall_movement) / 2

    print(f"\nAverage match rate across all fields: {avg_match_rate:.1f}%")

    if avg_match_rate >= 90:
        quality = "HIGH"
        recommendation = "USE bg_builder data (602 vehicles) for formula building"
        print(f"\nQUALITY: {quality}")
        print(f"RECOMMENDATION: {recommendation}")
        print("  - bg_builder data is sufficiently accurate")
        print("  - Increases sample size from 281 to 602 vehicles (+114%)")
        print("  - Recommend using bg_builder as primary source with bg_reference as validation")
    elif avg_match_rate >= 70:
        quality = "MEDIUM"
        recommendation = "USE bg_builder with CAUTION - manual review recommended"
        print(f"\nQUALITY: {quality}")
        print(f"RECOMMENDATION: {recommendation}")
        print("  - bg_builder data has some errors but may be usable")
        print("  - Recommend spot-checking 50 random vehicles manually")
        print("  - Consider using bg_reference as primary with bg_builder as supplement")
    else:
        quality = "LOW"
        recommendation = "DO NOT USE bg_builder - use only bg_reference_vehicles (281 vehicles)"
        print(f"\nQUALITY: {quality}")
        print(f"RECOMMENDATION: {recommendation}")
        print("  - bg_builder data has too many errors for reliable formula building")
        print("  - Stick with manually-entered bg_reference_vehicles")
        print("  - Consider this a validation that original OCR scraping was flawed")

    # Check coverage gap
    print("\n" + "=" * 80)
    print("COVERAGE ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM bg_builder_vehicles b
        WHERE NOT EXISTS (
            SELECT 1 FROM bg_reference_vehicles r
            WHERE LOWER(TRIM(r.name)) = LOWER(TRIM(b.name))
        )
    """)
    builder_only = cursor.fetchone()['count']

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM bg_reference_vehicles r
        WHERE NOT EXISTS (
            SELECT 1 FROM bg_builder_vehicles b
            WHERE LOWER(TRIM(b.name)) = LOWER(TRIM(r.name))
        )
    """)
    reference_only = cursor.fetchone()['count']

    print(f"\nVehicles only in bg_builder: {builder_only} (potential new data if quality is high)")
    print(f"Vehicles only in bg_reference: {reference_only} (manually-entered but not in builder)")
    print(f"Overlapping vehicles: {len(overlaps)}")

    conn.close()

    return {
        'quality': quality,
        'recommendation': recommendation,
        'avg_match_rate': avg_match_rate,
        'armor_match_rate': overall_armor,
        'movement_match_rate': overall_movement,
        'overlaps': len(overlaps),
        'builder_only': builder_only,
        'reference_only': reference_only
    }


if __name__ == '__main__':
    results = validate_bg_builder_quality()
