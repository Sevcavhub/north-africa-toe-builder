"""
Analyze clean armor correlations from exact name matches.

With 39 exact matches between master_equipment and bg_builder,
we can now properly reverse-engineer BattleGroup's armor letter system.
"""

import sqlite3
from collections import defaultdict


def analyze_clean_correlations():
    """Analyze armor mm -> BG letter using only exact name matches."""

    conn = sqlite3.connect('database/master_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("REVERSE-ENGINEERING BG ARMOR SYSTEM (Clean Data Only)")
    print("=" * 80)

    # Get exact matches
    cursor.execute("""
        SELECT
            m.equipment_name,
            m.armor_hull_front_mm,
            m.armor_hull_side_mm,
            m.armor_hull_rear_mm,
            m.armor_turret_front_mm,
            m.armor_turret_side_mm,
            m.armor_turret_rear_mm,
            b.armor_front,
            b.armor_side,
            b.armor_rear
        FROM master_equipment m
        INNER JOIN bg_builder_vehicles b
            ON LOWER(TRIM(m.equipment_name)) = LOWER(TRIM(b.name))
        WHERE m.armor_hull_front_mm IS NOT NULL
          AND b.armor_front IS NOT NULL
        ORDER BY m.armor_hull_front_mm
    """)

    matches = cursor.fetchall()

    print(f"\n{len(matches)} vehicles with exact name matches\n")

    # Build correlations
    front_correlations = []
    side_correlations = []
    rear_correlations = []

    for row in matches:
        # BG uses MAX of hull and turret armor for front
        front_mm = max(row['armor_hull_front_mm'] or 0, row['armor_turret_front_mm'] or 0)
        side_mm = max(row['armor_hull_side_mm'] or 0, row['armor_turret_side_mm'] or 0) if row['armor_turret_side_mm'] else (row['armor_hull_side_mm'] or 0)
        rear_mm = max(row['armor_hull_rear_mm'] or 0, row['armor_turret_rear_mm'] or 0) if row['armor_turret_rear_mm'] else (row['armor_hull_rear_mm'] or 0)

        if front_mm > 0 and row['armor_front']:
            front_correlations.append((front_mm, row['armor_front'], row['equipment_name']))
        if side_mm > 0 and row['armor_side']:
            side_correlations.append((side_mm, row['armor_side'], row['equipment_name']))
        if rear_mm > 0 and row['armor_rear']:
            rear_correlations.append((rear_mm, row['armor_rear'], row['equipment_name']))

    # Analyze mm ranges for each BG letter
    def analyze_letter_ranges(correlations, facing):
        """Group by BG letter and show mm ranges."""
        letter_to_data = defaultdict(list)

        for mm, letter, name in correlations:
            letter_to_data[letter].append((mm, name))

        print(f"\n{facing} ARMOR:")
        print("-" * 80)

        ranges = []
        for letter in sorted(letter_to_data.keys()):
            data = letter_to_data[letter]
            mm_values = [d[0] for d in data]
            min_mm = min(mm_values)
            max_mm = max(mm_values)
            avg_mm = sum(mm_values) / len(mm_values)

            ranges.append({
                'letter': letter,
                'min_mm': min_mm,
                'max_mm': max_mm,
                'avg_mm': avg_mm,
                'count': len(mm_values),
                'examples': data[:3]
            })

            print(f"\n{letter}: {min_mm:.0f}-{max_mm:.0f}mm (avg: {avg_mm:.1f}mm, {len(mm_values)} samples)")
            print(f"  Examples:")
            for mm, name in data[:3]:
                print(f"    {mm:.0f}mm -> {name}")

        return ranges

    front_ranges = analyze_letter_ranges(front_correlations, "FRONT")
    side_ranges = analyze_letter_ranges(side_correlations, "SIDE")
    rear_ranges = analyze_letter_ranges(rear_correlations, "REAR")

    # Build proposed conversion table
    print("\n" + "=" * 80)
    print("PROPOSED MM -> BG LETTER CONVERSION TABLE")
    print("=" * 80)

    def propose_ranges(ranges, facing):
        print(f"\n{facing}:")
        print(f"{'BG Letter':>10} | {'MM Range':>15} | {'Samples':>8} | {'Confidence':>12}")
        print("-" * 60)

        for r in ranges:
            confidence = "HIGH" if r['count'] >= 5 else "MEDIUM" if r['count'] >= 2 else "LOW"
            mm_range = f"{r['min_mm']:.0f}-{r['max_mm']:.0f}mm"
            print(f"{r['letter']:>10} | {mm_range:>15} | {r['count']:>8} | {confidence:>12}")

    propose_ranges(front_ranges, "FRONT")
    propose_ranges(side_ranges, "SIDE")
    propose_ranges(rear_ranges, "REAR")

    # Create conversion function
    def mm_to_bg_letter(mm_value, ranges):
        """Convert mm to BG letter using learned ranges."""
        if mm_value is None or mm_value <= 0:
            return 'SS'

        # Find matching range
        for r in ranges:
            if r['min_mm'] <= mm_value <= r['max_mm']:
                return r['letter']

        # No match - find closest by average
        if ranges:
            closest = min(ranges, key=lambda r: abs(r['avg_mm'] - mm_value))
            return closest['letter']

        return 'O'

    # Test accuracy
    print("\n" + "=" * 80)
    print("FORMULA ACCURACY TEST (on training data)")
    print("=" * 80)

    correct = {'front': 0, 'side': 0, 'rear': 0}
    total = {'front': 0, 'side': 0, 'rear': 0}
    errors = []

    for row in matches:
        front_mm = max(row['armor_hull_front_mm'] or 0, row['armor_turret_front_mm'] or 0)
        side_mm = max(row['armor_hull_side_mm'] or 0, row['armor_turret_side_mm'] or 0) if row['armor_turret_side_mm'] else (row['armor_hull_side_mm'] or 0)
        rear_mm = max(row['armor_hull_rear_mm'] or 0, row['armor_turret_rear_mm'] or 0) if row['armor_turret_rear_mm'] else (row['armor_hull_rear_mm'] or 0)

        if front_mm > 0 and row['armor_front']:
            total['front'] += 1
            calc = mm_to_bg_letter(front_mm, front_ranges)
            if calc == row['armor_front']:
                correct['front'] += 1
            else:
                errors.append(f"{row['equipment_name']}: Front {front_mm:.0f}mm -> {calc} (expected {row['armor_front']})")

        if side_mm > 0 and row['armor_side']:
            total['side'] += 1
            calc = mm_to_bg_letter(side_mm, side_ranges)
            if calc == row['armor_side']:
                correct['side'] += 1
            else:
                errors.append(f"{row['equipment_name']}: Side {side_mm:.0f}mm -> {calc} (expected {row['armor_side']})")

        if rear_mm > 0 and row['armor_rear']:
            total['rear'] += 1
            calc = mm_to_bg_letter(rear_mm, rear_ranges)
            if calc == row['armor_rear']:
                correct['rear'] += 1
            else:
                errors.append(f"{row['equipment_name']}: Rear {rear_mm:.0f}mm -> {calc} (expected {row['armor_rear']})")

    front_pct = (correct['front'] / total['front'] * 100) if total['front'] > 0 else 0
    side_pct = (correct['side'] / total['side'] * 100) if total['side'] > 0 else 0
    rear_pct = (correct['rear'] / total['rear'] * 100) if total['rear'] > 0 else 0
    overall_pct = ((correct['front'] + correct['side'] + correct['rear']) /
                   (total['front'] + total['side'] + total['rear']) * 100)

    print(f"\nFront: {correct['front']}/{total['front']} ({front_pct:.1f}%)")
    print(f"Side:  {correct['side']}/{total['side']} ({side_pct:.1f}%)")
    print(f"Rear:  {correct['rear']}/{total['rear']} ({rear_pct:.1f}%)")
    print(f"\nOVERALL: {correct['front']+correct['side']+correct['rear']}/{total['front']+total['side']+total['rear']} ({overall_pct:.1f}%)")

    if errors:
        print(f"\nERRORS ({len(errors)} total):")
        for err in errors[:10]:
            print(f"  {err}")

    conn.close()

    return {
        'front_ranges': front_ranges,
        'side_ranges': side_ranges,
        'rear_ranges': rear_ranges,
        'accuracy': overall_pct
    }


if __name__ == '__main__':
    results = analyze_clean_correlations()
