"""
Reverse-engineer armor mm -> BG letter conversion formula.

Strategy:
1. Find vehicles that exist in BOTH equipment (mm data) AND bg_builder/bg_reference (BG letter)
2. Analyze the correlation between mm thickness and BG letter ratings
3. Build conversion ranges (e.g., 60-80mm = K)
4. Test formula accuracy against known vehicles
"""

import sqlite3
from collections import defaultdict


def reverse_engineer_armor_formula():
    """Build armor mm -> BG letter conversion formula from matched vehicles."""

    conn = sqlite3.connect('database/master_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("REVERSE-ENGINEERING ARMOR FORMULA (mm -> BG letter)")
    print("=" * 80)

    # Find vehicles with BOTH mm data (equipment) AND BG letter (bg_builder/bg_reference)
    cursor.execute("""
        SELECT
            e.name,
            e.armor_front_mm,
            e.armor_side_mm,
            e.armor_rear_mm,
            e.turret_front_mm,
            e.turret_side_mm,
            e.turret_rear_mm,
            COALESCE(r.armor_front, b.armor_front) as bg_armor_front,
            COALESCE(r.armor_side, b.armor_side) as bg_armor_side,
            COALESCE(r.armor_rear, b.armor_rear) as bg_armor_rear,
            CASE
                WHEN r.id IS NOT NULL THEN 'bg_reference'
                ELSE 'bg_builder'
            END as bg_source
        FROM equipment e
        LEFT JOIN bg_reference_vehicles r ON LOWER(TRIM(e.name)) = LOWER(TRIM(r.name))
        LEFT JOIN bg_builder_vehicles b ON LOWER(TRIM(e.name)) = LOWER(TRIM(b.name))
        WHERE e.armor_front_mm IS NOT NULL
          AND (r.armor_front IS NOT NULL OR b.armor_front IS NOT NULL)
        ORDER BY e.armor_front_mm
    """)

    matches = cursor.fetchall()

    print(f"\nFound {len(matches)} vehicles with BOTH mm data AND BG letter ratings\n")

    if len(matches) == 0:
        print("ERROR: No vehicles found with both data types!")
        print("Cannot reverse-engineer formula without training data.")
        conn.close()
        return None

    # Display all matches
    print("TRAINING DATA:")
    print("-" * 120)
    print(f"{'Vehicle':30} {'Front mm':>10} {'BG':>4} | {'Side mm':>9} {'BG':>4} | {'Rear mm':>9} {'BG':>4} | {'Source':15}")
    print("-" * 120)

    front_mapping = defaultdict(list)
    side_mapping = defaultdict(list)
    rear_mapping = defaultdict(list)

    for row in matches:
        # Use turret armor if higher than hull (common for tanks)
        front_mm = max(row['armor_front_mm'] or 0, row['turret_front_mm'] or 0) if row['turret_front_mm'] else row['armor_front_mm']
        side_mm = max(row['armor_side_mm'] or 0, row['turret_side_mm'] or 0) if row['turret_side_mm'] else row['armor_side_mm']
        rear_mm = max(row['armor_rear_mm'] or 0, row['turret_rear_mm'] or 0) if row['turret_rear_mm'] else row['armor_rear_mm']

        print(f"{row['name']:30} {front_mm:>10} {row['bg_armor_front']:>4} | {side_mm or '--':>9} {row['bg_armor_side'] or '--':>4} | {rear_mm or '--':>9} {row['bg_armor_rear'] or '--':>4} | {row['bg_source']:15}")

        # Build mappings
        if front_mm and row['bg_armor_front']:
            front_mapping[row['bg_armor_front']].append(front_mm)
        if side_mm and row['bg_armor_side']:
            side_mapping[row['bg_armor_side']].append(side_mm)
        if rear_mm and row['bg_armor_rear']:
            rear_mapping[row['bg_armor_rear']].append(rear_mm)

    # Analyze mm ranges for each BG letter
    print("\n" + "=" * 80)
    print("MM RANGES FOR EACH BG LETTER")
    print("=" * 80)

    def analyze_mapping(mapping, facing):
        print(f"\n{facing} Armor:")
        print(f"{'Letter':>6} | {'Count':>5} | {'Min mm':>7} | {'Max mm':>7} | {'Avg mm':>7} | {'Range':>15}")
        print("-" * 60)

        for letter in sorted(mapping.keys()):
            mm_values = mapping[letter]
            min_mm = min(mm_values)
            max_mm = max(mm_values)
            avg_mm = sum(mm_values) / len(mm_values)
            print(f"{letter:>6} | {len(mm_values):>5} | {min_mm:>7} | {max_mm:>7} | {avg_mm:>7.1f} | {min_mm}-{max_mm}mm")

    analyze_mapping(front_mapping, "FRONT")
    analyze_mapping(side_mapping, "SIDE")
    analyze_mapping(rear_mapping, "REAR")

    # Build conversion table
    print("\n" + "=" * 80)
    print("PROPOSED ARMOR CONVERSION FORMULA")
    print("=" * 80)

    def build_ranges(mapping, facing):
        print(f"\n{facing} Armor Conversion:")
        ranges = []
        for letter in sorted(mapping.keys()):
            mm_values = mapping[letter]
            min_mm = min(mm_values)
            max_mm = max(mm_values)
            avg_mm = sum(mm_values) / len(mm_values)
            ranges.append({
                'letter': letter,
                'min_mm': min_mm,
                'max_mm': max_mm,
                'avg_mm': avg_mm,
                'samples': len(mm_values)
            })

        for r in ranges:
            confidence = "HIGH" if r['samples'] >= 3 else "MEDIUM" if r['samples'] == 2 else "LOW"
            print(f"  {r['min_mm']:3}-{r['max_mm']:3}mm -> {r['letter']:2} (avg: {r['avg_mm']:5.1f}mm, {r['samples']:2} samples, {confidence})")

        return ranges

    front_ranges = build_ranges(front_mapping, "FRONT")
    side_ranges = build_ranges(side_mapping, "SIDE")
    rear_ranges = build_ranges(rear_mapping, "REAR")

    # Test accuracy
    print("\n" + "=" * 80)
    print("FORMULA VALIDATION")
    print("=" * 80)

    def apply_formula(mm_value, ranges):
        """Apply conversion formula to get BG letter."""
        if mm_value is None or mm_value == 0:
            return 'SS'  # Soft-skinned

        # Find matching range
        for r in ranges:
            if r['min_mm'] <= mm_value <= r['max_mm']:
                return r['letter']

        # No exact match - find closest
        for r in sorted(ranges, key=lambda x: abs(x['avg_mm'] - mm_value)):
            return r['letter']

        return None

    correct_front = 0
    correct_side = 0
    correct_rear = 0
    total_front = 0
    total_side = 0
    total_rear = 0

    print("\nTesting formula against training data:")
    print("-" * 100)
    print(f"{'Vehicle':30} {'Front':>25} {'Side':>25} {'Rear':>25}")
    print("-" * 100)

    for row in matches:
        front_mm = max(row['armor_front_mm'] or 0, row['turret_front_mm'] or 0) if row['turret_front_mm'] else row['armor_front_mm']
        side_mm = max(row['armor_side_mm'] or 0, row['turret_side_mm'] or 0) if row['turret_side_mm'] else row['armor_side_mm']
        rear_mm = max(row['armor_rear_mm'] or 0, row['turret_rear_mm'] or 0) if row['turret_rear_mm'] else row['armor_rear_mm']

        calc_front = apply_formula(front_mm, front_ranges) if front_mm else None
        calc_side = apply_formula(side_mm, side_ranges) if side_mm else None
        calc_rear = apply_formula(rear_mm, rear_ranges) if rear_mm else None

        front_match = "[OK]" if calc_front == row['bg_armor_front'] else "[!!]"
        side_match = "[OK]" if calc_side == row['bg_armor_side'] else "[!!]"
        rear_match = "[OK]" if calc_rear == row['bg_armor_rear'] else "[!!]"

        if front_mm and row['bg_armor_front']:
            total_front += 1
            if calc_front == row['bg_armor_front']:
                correct_front += 1

        if side_mm and row['bg_armor_side']:
            total_side += 1
            if calc_side == row['bg_armor_side']:
                correct_side += 1

        if rear_mm and row['bg_armor_rear']:
            total_rear += 1
            if calc_rear == row['bg_armor_rear']:
                correct_rear += 1

        front_str = f"{front_mm}mm->{calc_front}(exp:{row['bg_armor_front']}) {front_match}" if front_mm else "--"
        side_str = f"{side_mm}mm->{calc_side}(exp:{row['bg_armor_side']}) {side_match}" if side_mm else "--"
        rear_str = f"{rear_mm}mm->{calc_rear}(exp:{row['bg_armor_rear']}) {rear_match}" if rear_mm else "--"

        print(f"{row['name']:30} {front_str:>25} {side_str:>25} {rear_str:>25}")

    print("\n" + "=" * 80)
    print("ACCURACY RESULTS")
    print("=" * 80)

    front_pct = (correct_front / total_front * 100) if total_front > 0 else 0
    side_pct = (correct_side / total_side * 100) if total_side > 0 else 0
    rear_pct = (correct_rear / total_rear * 100) if total_rear > 0 else 0

    print(f"\nFront Armor: {correct_front}/{total_front} correct ({front_pct:.1f}%)")
    print(f"Side Armor:  {correct_side}/{total_side} correct ({side_pct:.1f}%)")
    print(f"Rear Armor:  {correct_rear}/{total_rear} correct ({rear_pct:.1f}%)")

    overall = ((correct_front + correct_side + correct_rear) / (total_front + total_side + total_rear) * 100) if (total_front + total_side + total_rear) > 0 else 0
    print(f"\nOVERALL: {correct_front + correct_side + correct_rear}/{total_front + total_side + total_rear} correct ({overall:.1f}%)")

    if overall >= 90:
        print("\n[SUCCESS] Formula achieves >90% accuracy - ready for use!")
    elif overall >= 70:
        print("\n[CAUTION] Formula achieves 70-90% accuracy - needs more training data")
    else:
        print("\n[INSUFFICIENT] Formula <70% accurate - not reliable for production use")

    conn.close()

    return {
        'front_ranges': front_ranges,
        'side_ranges': side_ranges,
        'rear_ranges': rear_ranges,
        'accuracy': {
            'front': front_pct,
            'side': side_pct,
            'rear': rear_pct,
            'overall': overall
        },
        'training_samples': len(matches)
    }


if __name__ == '__main__':
    results = reverse_engineer_armor_formula()
