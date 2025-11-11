"""
Build armor mm -> BG letter conversion formula using master_equipment + bg_builder.

Process:
1. Find vehicles in BOTH master_equipment (mm data) AND bg_builder (BG letters)
2. Analyze correlation between mm thickness and BG letter ratings
3. Build conversion ranges (e.g., 40-50mm = K)
4. Test formula accuracy
5. Apply to Soviet tanks to calculate their BG letters
"""

import sqlite3
from collections import defaultdict


def build_armor_conversion_formula():
    """Build mm -> BG letter conversion using matched data."""

    conn = sqlite3.connect('database/master_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("BUILDING ARMOR CONVERSION FORMULA (mm -> BG letter)")
    print("=" * 80)

    # Find vehicles in BOTH tables with data
    cursor.execute("""
        SELECT
            m.equipment_name,
            m.armor_hull_front_mm,
            m.armor_hull_side_mm,
            m.armor_hull_rear_mm,
            m.armor_turret_front_mm,
            m.armor_turret_side_mm,
            m.armor_turret_rear_mm,
            COALESCE(r.armor_front, b.armor_front) as bg_front,
            COALESCE(r.armor_side, b.armor_side) as bg_side,
            COALESCE(r.armor_rear, b.armor_rear) as bg_rear,
            CASE
                WHEN r.id IS NOT NULL THEN 'bg_reference'
                ELSE 'bg_builder'
            END as source
        FROM master_equipment m
        LEFT JOIN bg_reference_vehicles r
            ON LOWER(TRIM(m.equipment_name)) LIKE '%' || LOWER(TRIM(r.name)) || '%'
            OR LOWER(TRIM(r.name)) LIKE '%' || LOWER(TRIM(m.equipment_name)) || '%'
        LEFT JOIN bg_builder_vehicles b
            ON LOWER(TRIM(m.equipment_name)) LIKE '%' || LOWER(TRIM(b.name)) || '%'
            OR LOWER(TRIM(b.name)) LIKE '%' || LOWER(TRIM(m.equipment_name)) || '%'
        WHERE m.armor_hull_front_mm IS NOT NULL
          AND (r.armor_front IS NOT NULL OR b.armor_front IS NOT NULL)
        ORDER BY m.armor_hull_front_mm
    """)

    matches = cursor.fetchall()

    print(f"\nFound {len(matches)} vehicles with BOTH mm data AND BG letters\n")

    # Build correlation mappings
    front_correlations = []
    side_correlations = []
    rear_correlations = []

    print("TRAINING DATA:")
    print("-" * 120)
    print(f"{'Vehicle':35} {'Front mm':>10} {'BG':>4} | {'Side mm':>9} {'BG':>4} | {'Rear mm':>9} {'BG':>4} | {'Source':12}")
    print("-" * 120)

    for row in matches:
        # Use max of hull/turret armor (turret usually stronger on front)
        front_mm = max(row['armor_hull_front_mm'] or 0, row['armor_turret_front_mm'] or 0)
        side_mm = max(row['armor_hull_side_mm'] or 0, row['armor_turret_side_mm'] or 0) if row['armor_turret_side_mm'] else row['armor_hull_side_mm']
        rear_mm = max(row['armor_hull_rear_mm'] or 0, row['armor_turret_rear_mm'] or 0) if row['armor_turret_rear_mm'] else row['armor_hull_rear_mm']

        print(f"{row['equipment_name'][:35]:35} {front_mm:>10.0f} {row['bg_front']:>4} | "
              f"{side_mm or '--':>9} {row['bg_side'] or '--':>4} | "
              f"{rear_mm or '--':>9} {row['bg_rear'] or '--':>4} | {row['source']:12}")

        # Store correlations
        if front_mm and row['bg_front']:
            front_correlations.append((front_mm, row['bg_front']))
        if side_mm and row['bg_side']:
            side_correlations.append((side_mm, row['bg_side']))
        if rear_mm and row['bg_rear']:
            rear_correlations.append((rear_mm, row['bg_rear']))

    # Analyze mm ranges for each BG letter
    print("\n" + "=" * 80)
    print("MM RANGES FOR EACH BG LETTER (derived from training data)")
    print("=" * 80)

    def analyze_correlations(correlations, facing_name):
        """Group mm values by BG letter and find ranges."""
        letter_to_mm = defaultdict(list)
        for mm, letter in correlations:
            letter_to_mm[letter].append(mm)

        print(f"\n{facing_name} Armor:")
        print(f"{'BG Letter':>10} | {'Count':>5} | {'Min mm':>7} | {'Max mm':>7} | {'Avg mm':>7} | {'Confidence':>10}")
        print("-" * 70)

        ranges = []
        for letter in sorted(letter_to_mm.keys()):
            mm_values = letter_to_mm[letter]
            min_mm = min(mm_values)
            max_mm = max(mm_values)
            avg_mm = sum(mm_values) / len(mm_values)
            confidence = "HIGH" if len(mm_values) >= 5 else "MEDIUM" if len(mm_values) >= 2 else "LOW"

            print(f"{letter:>10} | {len(mm_values):>5} | {min_mm:>7.0f} | {max_mm:>7.0f} | {avg_mm:>7.1f} | {confidence:>10}")

            ranges.append({
                'letter': letter,
                'min_mm': min_mm,
                'max_mm': max_mm,
                'avg_mm': avg_mm,
                'samples': len(mm_values)
            })

        return ranges

    front_ranges = analyze_correlations(front_correlations, "FRONT")
    side_ranges = analyze_correlations(side_correlations, "SIDE")
    rear_ranges = analyze_correlations(rear_correlations, "REAR")

    # Create conversion function
    def mm_to_bg_letter(mm_value, ranges, facing):
        """Convert mm armor to BG letter using learned ranges."""
        if mm_value is None or mm_value <= 5:
            return 'SS'  # Soft-skinned

        # Find exact range match first
        for r in ranges:
            if r['min_mm'] <= mm_value <= r['max_mm']:
                return r['letter']

        # No exact match - find nearest by average
        if ranges:
            closest = min(ranges, key=lambda r: abs(r['avg_mm'] - mm_value))
            return closest['letter']

        return 'O'  # Default to very light armor

    # Test formula accuracy
    print("\n" + "=" * 80)
    print("FORMULA ACCURACY TEST")
    print("=" * 80)

    correct = {'front': 0, 'side': 0, 'rear': 0}
    total = {'front': 0, 'side': 0, 'rear': 0}

    print(f"\n{'Vehicle':35} {'Front Calc':>15} {'Side Calc':>15} {'Rear Calc':>15}")
    print("-" * 85)

    for row in matches:
        front_mm = max(row['armor_hull_front_mm'] or 0, row['armor_turret_front_mm'] or 0)
        side_mm = max(row['armor_hull_side_mm'] or 0, row['armor_turret_side_mm'] or 0) if row['armor_turret_side_mm'] else row['armor_hull_side_mm']
        rear_mm = max(row['armor_hull_rear_mm'] or 0, row['armor_turret_rear_mm'] or 0) if row['armor_turret_rear_mm'] else row['armor_hull_rear_mm']

        calc_front = mm_to_bg_letter(front_mm, front_ranges, 'front') if front_mm else None
        calc_side = mm_to_bg_letter(side_mm, side_ranges, 'side') if side_mm else None
        calc_rear = mm_to_bg_letter(rear_mm, rear_ranges, 'rear') if rear_mm else None

        front_str = f"{calc_front}(exp:{row['bg_front']})" if front_mm else "--"
        side_str = f"{calc_side}(exp:{row['bg_side']})" if side_mm else "--"
        rear_str = f"{calc_rear}(exp:{row['bg_rear']})" if rear_mm else "--"

        front_match = "[OK]" if calc_front == row['bg_front'] else "[!!]"
        side_match = "[OK]" if calc_side == row['bg_side'] else "[!!]"
        rear_match = "[OK]" if calc_rear == row['bg_rear'] else "[!!]"

        if front_mm and row['bg_front']:
            total['front'] += 1
            if calc_front == row['bg_front']:
                correct['front'] += 1

        if side_mm and row['bg_side']:
            total['side'] += 1
            if calc_side == row['bg_side']:
                correct['side'] += 1

        if rear_mm and row['bg_rear']:
            total['rear'] += 1
            if calc_rear == row['bg_rear']:
                correct['rear'] += 1

        print(f"{row['equipment_name'][:35]:35} {front_str:>9}{front_match:>6} {side_str:>9}{side_match:>6} {rear_str:>9}{rear_match:>6}")

    # Calculate accuracy
    front_pct = (correct['front'] / total['front'] * 100) if total['front'] > 0 else 0
    side_pct = (correct['side'] / total['side'] * 100) if total['side'] > 0 else 0
    rear_pct = (correct['rear'] / total['rear'] * 100) if total['rear'] > 0 else 0
    overall_pct = ((correct['front'] + correct['side'] + correct['rear']) /
                   (total['front'] + total['side'] + total['rear']) * 100) if sum(total.values()) > 0 else 0

    print("\n" + "=" * 80)
    print("ACCURACY RESULTS")
    print("=" * 80)
    print(f"\nFront: {correct['front']}/{total['front']} ({front_pct:.1f}%)")
    print(f"Side:  {correct['side']}/{total['side']} ({side_pct:.1f}%)")
    print(f"Rear:  {correct['rear']}/{total['rear']} ({rear_pct:.1f}%)")
    print(f"\nOVERALL: {correct['front']+correct['side']+correct['rear']}/{total['front']+total['side']+total['rear']} ({overall_pct:.1f}%)")

    # Now apply to Soviet tanks
    print("\n" + "=" * 80)
    print("APPLYING FORMULA TO SOVIET TANKS")
    print("=" * 80)

    cursor.execute("""
        SELECT equipment_name,
               armor_hull_front_mm, armor_hull_side_mm, armor_hull_rear_mm,
               armor_turret_front_mm, armor_turret_side_mm, armor_turret_rear_mm
        FROM master_equipment
        WHERE LOWER(equipment_name) LIKE '%su-85%'
           OR LOWER(equipment_name) LIKE '%bt-7%'
           OR LOWER(equipment_name) LIKE '%t-34%85%'
           OR LOWER(equipment_name) LIKE '%t-34-85%'
    """)

    soviet_tanks = cursor.fetchall()

    print(f"\n{'Vehicle':35} {'MM Values (F/S/R)':>30} {'Calculated BG (F/S/R)':>25}")
    print("-" * 95)

    for tank in soviet_tanks:
        front_mm = max(tank['armor_hull_front_mm'] or 0, tank['armor_turret_front_mm'] or 0)
        side_mm = tank['armor_hull_side_mm'] or 0
        rear_mm = tank['armor_hull_rear_mm'] or 0

        calc_front = mm_to_bg_letter(front_mm, front_ranges, 'front')
        calc_side = mm_to_bg_letter(side_mm, side_ranges, 'side')
        calc_rear = mm_to_bg_letter(rear_mm, rear_ranges, 'rear')

        mm_str = f"{front_mm:.0f}/{side_mm:.0f}/{rear_mm:.0f}mm"
        bg_str = f"{calc_front}/{calc_side}/{calc_rear}"

        print(f"{tank['equipment_name']:35} {mm_str:>30} {bg_str:>25}")

    print("\n" + "=" * 80)
    print("COMPARE THESE CALCULATED VALUES TO YOUR OFFICIAL BG CARDS")
    print("=" * 80)

    conn.close()

    return {
        'front_ranges': front_ranges,
        'side_ranges': side_ranges,
        'rear_ranges': rear_ranges,
        'accuracy': {
            'front': front_pct,
            'side': side_pct,
            'rear': rear_pct,
            'overall': overall_pct
        }
    }


if __name__ == '__main__':
    results = build_armor_conversion_formula()
