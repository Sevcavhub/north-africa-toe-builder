#!/usr/bin/env python3
"""
Penetration Converter for BattleGroup

Converts penetration (mm @ distance) to BattleGroup 1-15 penetration scale.

Based on reference database analysis showing:
- 20mm guns: 2 scale (light AT rifles)
- 37mm guns: 4 scale (light AT guns)
- 50mm guns: 5 scale (medium AT guns)
- 75mm guns: 4-5 scale (varies by barrel length)
- 88mm guns: 9 scale (heavy AT guns)

Penetration drops with range:
- 0-10" and 10-20": Same value
- 20-30": -1
- 30-40": -1
- 40-50": -1
- 50-70": -1

Usage:
    from penetration_converter import convert_penetration

    pen = convert_penetration(caliber_mm=88, barrel_length="L56")
    # Returns {"ap_0_10": 9, "ap_10_20": 9, "ap_20_30": 8, ... }
"""

import sqlite3
from pathlib import Path
from typing import Dict, Optional, List

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR.parent.parent.parent / "database" / "master_database.db"


def convert_penetration(
    caliber_mm: int,
    barrel_length: Optional[str] = None,
    gun_name: Optional[str] = None
) -> Dict:
    """
    Convert gun characteristics to BattleGroup penetration scale (1-15).

    Args:
        caliber_mm: Gun caliber in millimeters
        barrel_length: Optional barrel length designation (e.g., "L56", "L/48")
        gun_name: Optional gun name for special case handling

    Returns:
        dict: {
            "ap_0_10": int,
            "ap_10_20": int,
            "ap_20_30": int,
            "ap_30_40": int,
            "ap_40_50": int,
            "ap_50_70": int or None,
            "confidence": str
        }

    Examples:
        >>> convert_penetration(88, "L56")
        {'ap_0_10': 9, 'ap_10_20': 9, 'ap_20_30': 8, 'ap_30_40': 7, 'ap_40_50': 6, 'ap_50_70': 5}

        >>> convert_penetration(50, "L60")
        {'ap_0_10': 5, 'ap_10_20': 5, 'ap_20_30': 4, 'ap_30_40': 3, 'ap_40_50': 2, 'ap_50_70': None}
    """

    # Exact gun mappings from reference database
    gun_penetration_map = {
        # Light AT weapons (20mm)
        (20, None): 2,
        (20, 'L55'): 2,

        # Light AT guns (37mm)
        (37, None): 4,
        (37, 'L43'): 4,
        (37, 'L45'): 4,
        (37, 'L53'): 4,

        # Medium AT guns (50mm)
        (50, None): 5,
        (50, 'L60'): 5,

        # Medium guns (75mm) - varies significantly by barrel
        (75, None): 4,
        (75, 'L24'): 4,  # Short barrel tank gun
        (75, 'L30'): 5,
        (75, 'L40'): 5,
        (75, 'L46'): 5,
        (75, 'L48'): 5,
        (75, 'L70'): 6,  # Long barrel (Panther)

        # Heavy AT guns (85-88mm)
        (85, None): 9,
        (85, 'L54'): 9,
        (88, None): 9,
        (88, 'L56'): 9,
    }

    # Normalize barrel length (remove "/" if present)
    if barrel_length:
        barrel_length = barrel_length.replace('/', '').replace('l', 'L').upper()
        if not barrel_length.startswith('L'):
            barrel_length = 'L' + barrel_length

    # STEP 1: Try bg_penetration_scale table lookup (highest confidence)
    base_pen = None
    confidence = 'medium'

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Try exact caliber + barrel match first
        if barrel_length:
            cursor.execute("""
                SELECT value_0_10, value_10_20, value_20_30,
                       value_30_40, value_40_50, value_50_70
                FROM bg_penetration_scale
                WHERE caliber_mm = ? AND barrel_length = ?
            """, (caliber_mm, barrel_length))
            row = cursor.fetchone()

            if row and row['value_0_10'] is not None:
                # Found exact match in scale table - return immediately
                conn.close()
                return {
                    'ap_0_10': row['value_0_10'],
                    'ap_10_20': row['value_10_20'],
                    'ap_20_30': row['value_20_30'],
                    'ap_30_40': row['value_30_40'],
                    'ap_40_50': row['value_40_50'],
                    'ap_50_70': row['value_50_70'],
                    'base_penetration': row['value_0_10'],
                    'confidence': 'very_high',
                    'caliber_mm': caliber_mm,
                    'barrel_length': barrel_length
                }

        # Try caliber-only match (ignoring barrel length)
        cursor.execute("""
            SELECT value_0_10, value_10_20, value_20_30,
                   value_30_40, value_40_50, value_50_70
            FROM bg_penetration_scale
            WHERE caliber_mm = ?
            LIMIT 1
        """, (caliber_mm,))
        row = cursor.fetchone()

        if row and row['value_0_10'] is not None:
            # Found caliber match - return with adjusted confidence
            conn.close()
            return {
                'ap_0_10': row['value_0_10'],
                'ap_10_20': row['value_10_20'],
                'ap_20_30': row['value_20_30'],
                'ap_30_40': row['value_30_40'],
                'ap_40_50': row['value_40_50'],
                'ap_50_70': row['value_50_70'],
                'base_penetration': row['value_0_10'],
                'confidence': 'high',
                'caliber_mm': caliber_mm,
                'barrel_length': barrel_length
            }

        conn.close()
    except Exception as e:
        # Database lookup failed, continue to fallback methods
        pass

    # STEP 2: Try hardcoded gun_penetration_map
    if (caliber_mm, barrel_length) in gun_penetration_map:
        base_pen = gun_penetration_map[(caliber_mm, barrel_length)]
        confidence = 'high'
    elif (caliber_mm, None) in gun_penetration_map:
        base_pen = gun_penetration_map[(caliber_mm, None)]
        confidence = 'medium'
    else:
        # Estimate based on caliber alone
        if caliber_mm <= 25:
            base_pen = 2
        elif caliber_mm <= 45:
            base_pen = 4
        elif caliber_mm <= 57:
            base_pen = 5
        elif caliber_mm <= 76:
            base_pen = 5
        elif caliber_mm <= 90:
            base_pen = 9
        elif caliber_mm <= 100:
            base_pen = 10
        elif caliber_mm <= 122:
            base_pen = 11
        else:
            base_pen = 12
        confidence = 'low'

    # Adjust for barrel length if known
    if barrel_length and base_pen and confidence != 'high':
        # Extract numeric part of barrel length
        try:
            length_value = int(barrel_length.replace('L', ''))
            # Longer barrels get better penetration
            if length_value >= 70:
                base_pen = min(base_pen + 2, 15)
            elif length_value >= 55:
                base_pen = min(base_pen + 1, 15)
            elif length_value <= 30:
                base_pen = max(base_pen - 1, 1)
        except:
            pass

    # Calculate range degradation (standard BattleGroup pattern)
    # - Same pen at 0-10" and 10-20"
    # - Drop by 1 per range band thereafter
    # - Only 88mm+ guns get the 50-70" range band
    ap_0_10 = base_pen
    ap_10_20 = base_pen
    ap_20_30 = max(base_pen - 1, 1)
    ap_30_40 = max(base_pen - 2, 1)
    ap_40_50 = max(base_pen - 3, 1)

    # Only heavy AT guns (88mm+) get extreme range penetration
    # Based on reference database: only 88mm L56 has ap_50_70 value
    if caliber_mm >= 88 and base_pen >= 9:
        ap_50_70 = base_pen - 4 if base_pen > 4 else None
    else:
        ap_50_70 = None

    return {
        'ap_0_10': ap_0_10,
        'ap_10_20': ap_10_20,
        'ap_20_30': ap_20_30,
        'ap_30_40': ap_30_40,
        'ap_40_50': ap_40_50,
        'ap_50_70': ap_50_70,
        'base_penetration': base_pen,
        'confidence': confidence,
        'caliber_mm': caliber_mm,
        'barrel_length': barrel_length
    }


def validate_against_reference() -> Dict:
    """
    Validate penetration converter against reference database.

    Returns:
        dict: Validation statistics including accuracy percentage
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all guns with penetration data from reference
    cursor.execute("""
        SELECT name, caliber_mm, barrel_length,
               ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
        FROM bg_reference_guns
        WHERE ap_0_10 IS NOT NULL
    """)

    total = 0
    perfect_match = 0
    close_match = 0  # Within ±1 on most ranges
    errors = []

    for name, caliber, barrel, ref_ap1, ref_ap2, ref_ap3, ref_ap4, ref_ap5, ref_ap6 in cursor.fetchall():
        total += 1

        # Calculate penetration
        calculated = convert_penetration(caliber, barrel, name)

        # Check accuracy across all 6 range bands
        ref_values = [ref_ap1, ref_ap2, ref_ap3, ref_ap4, ref_ap5, ref_ap6]
        calc_values = [
            calculated['ap_0_10'],
            calculated['ap_10_20'],
            calculated['ap_20_30'],
            calculated['ap_30_40'],
            calculated['ap_40_50'],
            calculated['ap_50_70']
        ]

        # Count matches
        exact_matches = sum(1 for r, c in zip(ref_values, calc_values)
                           if r == c or (r is None and c is None))

        # Calculate differences
        diffs = []
        for r, c in zip(ref_values, calc_values):
            if r is None or c is None:
                if r == c:
                    diffs.append(0)
                else:
                    diffs.append(99)  # Major difference
            else:
                diffs.append(abs(r - c))

        max_diff = max(diffs)

        if exact_matches == 6:
            perfect_match += 1
            close_match += 1
        elif max_diff <= 1:
            close_match += 1
        else:
            errors.append({
                'gun': name,
                'caliber': caliber,
                'barrel': barrel or '?',
                'expected': f'{ref_ap1}/{ref_ap2}/{ref_ap3}/{ref_ap4}/{ref_ap5}/{ref_ap6 or "-"}',
                'calculated': f'{calc_values[0]}/{calc_values[1]}/{calc_values[2]}/{calc_values[3]}/{calc_values[4]}/{calc_values[5] or "-"}',
                'max_diff': max_diff
            })

    conn.close()

    perfect_accuracy = (perfect_match / total * 100) if total > 0 else 0
    close_accuracy = (close_match / total * 100) if total > 0 else 0

    return {
        'total_guns': total,
        'perfect_match': perfect_match,
        'close_match': close_match,
        'errors': total - close_match,
        'perfect_accuracy_percent': perfect_accuracy,
        'close_accuracy_percent': close_accuracy,
        'error_details': errors[:10],
        'passed_95_target': close_accuracy >= 95.0
    }


def main():
    """CLI interface for penetration converter."""
    import argparse

    parser = argparse.ArgumentParser(description='Convert penetration to BattleGroup 1-15 scale')
    parser.add_argument('caliber', type=int, nargs='?', help='Gun caliber in mm')
    parser.add_argument('--barrel', help='Barrel length (e.g., L56, L/48)')
    parser.add_argument('--name', help='Gun name for special case handling')
    parser.add_argument('--validate', action='store_true', help='Validate against reference database')
    parser.add_argument('--test', action='store_true', help='Run test examples')

    args = parser.parse_args()

    if args.validate:
        print("=" * 80)
        print("PENETRATION CONVERTER VALIDATION")
        print("=" * 80)
        print("\nValidating against reference database...")

        results = validate_against_reference()

        print(f"\nTotal guns tested: {results['total_guns']}")
        print(f"Perfect matches (all 6 bands): {results['perfect_match']}")
        print(f"Close matches (±1 max diff): {results['close_match']}")
        print(f"Errors: {results['errors']}")
        print(f"Perfect accuracy: {results['perfect_accuracy_percent']:.1f}%")
        print(f"Close accuracy: {results['close_accuracy_percent']:.1f}%")
        print(f"Target (95%): {'PASS' if results['passed_95_target'] else 'FAIL'}")

        if results['error_details']:
            print(f"\nFirst {len(results['error_details'])} errors:")
            print(f"{'Gun':25} | Cal | Barrel | Expected (6 bands) | Calculated | Max Diff")
            print("-" * 100)
            for err in results['error_details']:
                print(f"{err['gun'][:25]:25} | {err['caliber']:3} | {err['barrel']:6} | "
                      f"{err['expected']:19} | {err['calculated']:10} | {err['max_diff']}")

        return

    if args.test:
        print("=" * 80)
        print("PENETRATION CONVERTER TEST EXAMPLES")
        print("=" * 80)

        test_guns = [
            (20, 'L55', '20mm AT rifle'),
            (37, 'L43', '37mm PaK36'),
            (50, 'L60', '50mm PaK38'),
            (75, 'L24', '75mm short (Panzer IV F1)'),
            (75, 'L48', '75mm long (Panzer IV H)'),
            (75, 'L70', '75mm Panther'),
            (88, 'L56', '88mm Flak/Tiger'),
            (85, 'L54', '85mm Soviet')
        ]

        print(f"\n{'Gun':30} | Cal | Barrel | 0-10 | 10-20 | 20-30 | 30-40 | 40-50 | 50-70 | Conf")
        print("-" * 105)

        for caliber, barrel, desc in test_guns:
            result = convert_penetration(caliber, barrel)
            ap6_str = str(result['ap_50_70']) if result['ap_50_70'] else '-'
            print(f"{desc:30} | {caliber:3} | {barrel:6} | {result['ap_0_10']:4} | {result['ap_10_20']:5} | "
                  f"{result['ap_20_30']:5} | {result['ap_30_40']:5} | {result['ap_40_50']:5} | {ap6_str:5} | {result['confidence']}")

        return

    if args.caliber:
        result = convert_penetration(args.caliber, args.barrel, args.name)

        print(f"\nCalliber: {args.caliber}mm")
        if args.barrel:
            print(f"Barrel: {args.barrel}")
        if args.name:
            print(f"Gun: {args.name}")

        print(f"\nPenetration Values (1-15 scale):")
        print(f"  0-10\":   {result['ap_0_10']}")
        print(f"  10-20\":  {result['ap_10_20']}")
        print(f"  20-30\":  {result['ap_20_30']}")
        print(f"  30-40\":  {result['ap_30_40']}")
        print(f"  40-50\":  {result['ap_40_50']}")
        print(f"  50-70\":  {result['ap_50_70'] or 'N/A'}")
        print(f"\nBase penetration: {result['base_penetration']}")
        print(f"Confidence: {result['confidence']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
