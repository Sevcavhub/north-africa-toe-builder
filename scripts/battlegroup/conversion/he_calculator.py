#!/usr/bin/env python3
"""
HE Effectiveness Calculator for BattleGroup

Converts caliber (mm) to BattleGroup HE effect format (dice/target).

Based on reference database analysis showing clear caliber-based patterns:
- 37mm: 2/5+
- 50mm: 3/5+ or 3/6+
- 75mm: 4/4+
- 88mm: 4/3+
- 120mm: 6/4+
- 150mm+: 7/3+ or higher

Usage:
    from he_calculator import calculate_he_effect

    he = calculate_he_effect(75)  # Returns {"dice": 4, "target": "4+", "format": "4/4+"}
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR.parent.parent.parent / "database" / "master_database.db"
LOOKUP_TABLE_PATH = SCRIPT_DIR / "lookup_tables" / "he_conversion_table.json"


def load_lookup_table() -> Dict:
    """Load the HE conversion lookup table."""
    with open(LOOKUP_TABLE_PATH, 'r') as f:
        return json.load(f)


def calculate_he_effect(caliber_mm: int, gun_name: Optional[str] = None) -> Dict:
    """
    Calculate BattleGroup HE effect from caliber.

    Based on actual reference database analysis showing exact caliber patterns.

    Args:
        caliber_mm: Gun caliber in millimeters
        gun_name: Optional gun name for special case handling (e.g., "PaK38", "IG18", "mortar")

    Returns:
        dict: {"dice": int, "target": str, "format": str, "confidence": str}

    Examples:
        >>> calculate_he_effect(37)
        {'dice': 2, 'target': '5+', 'format': '2/5+', 'confidence': 'high'}

        >>> calculate_he_effect(75)
        {'dice': 4, 'target': '4+', 'format': '4/4+', 'confidence': 'high'}

        >>> calculate_he_effect(88)
        {'dice': 4, 'target': '3+', 'format': '4/3+', 'confidence': 'high'}
    """

    # Exact caliber-based mapping from reference database analysis
    caliber_map = {
        # Light guns (37mm)
        37: (2, '5+', 'high'),

        # Medium-light guns (50mm) - varies by gun type
        50: (3, '5+', 'high'),  # Default, PaK38 uses 6+

        # Medium guns (75-82mm)
        75: (4, '4+', 'high'),  # Most 75mm, IG18 uses 3/4+
        80: (4, '4+', 'high'),
        82: (4, '4+', 'high'),

        # Heavy guns (85-88mm)
        85: (4, '3+', 'high'),
        88: (4, '3+', 'high'),

        # Very heavy guns (100-105mm)
        100: (5, '3+', 'high'),
        105: (5, '3+', 'high'),

        # Super heavy mortars/howitzers (120mm+)
        120: (6, '4+', 'high'),  # Mortar - different target
        122: (6, '3+', 'high'),
        150: (7, '3+', 'high'),

        # Heavy artillery (170mm+)
        170: (6, '2+', 'high'),
        203: (8, '2+', 'high'),
        210: (7, '2+', 'high'),
    }

    # Check for exact caliber match
    if caliber_mm in caliber_map:
        dice, target, confidence = caliber_map[caliber_mm]

        # Special case handling based on gun name
        if gun_name:
            gun_lower = gun_name.lower()

            # PaK38 (50mm AT gun) uses 6+ instead of 5+
            if 'pak38' in gun_lower or ('pak' in gun_lower and caliber_mm == 50):
                target = '6+'

            # IG18 (75mm infantry gun) uses 3 dice instead of 4
            elif 'ig18' in gun_lower or ('ig' in gun_lower and caliber_mm == 75):
                dice = 3
                target = '4+'

            # Mortars generally have easier to hit (better target number)
            elif 'mortar' in gun_lower and caliber_mm == 120:
                target = '4+'  # Already set correctly

        return {
            'dice': dice,
            'target': target,
            'format': f"{dice}/{target}",
            'confidence': confidence,
            'caliber_mm': caliber_mm
        }

    # Interpolation for unlisted calibers
    # Find closest caliber in map
    sorted_calibers = sorted(caliber_map.keys())

    # Below smallest caliber
    if caliber_mm < sorted_calibers[0]:
        return {'dice': 1, 'target': '6+', 'format': '1/6+', 'confidence': 'medium', 'caliber_mm': caliber_mm}

    # Above largest caliber
    if caliber_mm > sorted_calibers[-1]:
        return {'dice': 8, 'target': '2+', 'format': '8/2+', 'confidence': 'medium', 'caliber_mm': caliber_mm}

    # Find surrounding calibers and interpolate
    for i in range(len(sorted_calibers) - 1):
        if sorted_calibers[i] < caliber_mm < sorted_calibers[i + 1]:
            # Use the higher caliber's values (conservative)
            dice, target, confidence = caliber_map[sorted_calibers[i + 1]]
            return {
                'dice': dice,
                'target': target,
                'format': f"{dice}/{target}",
                'confidence': 'medium',
                'caliber_mm': caliber_mm,
                'note': f'Interpolated from {sorted_calibers[i + 1]}mm'
            }

    # Fallback (shouldn't reach here)
    return {
        'dice': max(1, caliber_mm // 40),
        'target': '5+',
        'format': f"{max(1, caliber_mm // 40)}/5+",
        'confidence': 'low',
        'caliber_mm': caliber_mm
    }


def validate_against_reference() -> Dict:
    """
    Validate HE calculator against reference database.

    Returns:
        dict: Validation statistics including accuracy percentage
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all guns with HE data from reference
    cursor.execute("""
        SELECT name, caliber_mm, he_dice, he_target
        FROM bg_reference_guns
        WHERE caliber_mm IS NOT NULL AND he_dice IS NOT NULL
    """)

    total = 0
    correct = 0
    errors = []

    for name, caliber, ref_dice, ref_target in cursor.fetchall():
        total += 1

        # Calculate HE effect (pass gun name for special case handling)
        calculated = calculate_he_effect(caliber, gun_name=name)

        # Check if matches reference
        if calculated['dice'] == ref_dice and calculated['target'] == ref_target:
            correct += 1
        else:
            errors.append({
                'gun': name,
                'caliber': caliber,
                'expected': f"{ref_dice}/{ref_target}",
                'calculated': calculated['format'],
                'dice_diff': calculated['dice'] - ref_dice,
                'target_match': calculated['target'] == ref_target
            })

    conn.close()

    accuracy = (correct / total * 100) if total > 0 else 0

    return {
        'total_guns': total,
        'correct': correct,
        'incorrect': total - correct,
        'accuracy_percent': accuracy,
        'errors': errors[:10],  # First 10 errors
        'passed_95_target': accuracy >= 95.0
    }


def main():
    """CLI interface for HE calculator."""
    import argparse

    parser = argparse.ArgumentParser(description='Calculate BattleGroup HE effect from caliber')
    parser.add_argument('caliber', type=int, nargs='?', help='Gun caliber in mm')
    parser.add_argument('--type', help='Gun type (howitzer, at gun, mortar)')
    parser.add_argument('--validate', action='store_true', help='Validate against reference database')
    parser.add_argument('--test', action='store_true', help='Run test examples')

    args = parser.parse_args()

    if args.validate:
        print("=" * 70)
        print("HE CALCULATOR VALIDATION")
        print("=" * 70)
        print("\nValidating against reference database...")

        results = validate_against_reference()

        print(f"\nTotal guns tested: {results['total_guns']}")
        print(f"Correct predictions: {results['correct']}")
        print(f"Incorrect predictions: {results['incorrect']}")
        print(f"Accuracy: {results['accuracy_percent']:.1f}%")
        print(f"Target (95%): {'PASS' if results['passed_95_target'] else 'FAIL'}")

        if results['errors']:
            print(f"\nFirst {len(results['errors'])} errors:")
            print(f"{'Gun':30} | Cal | Expected | Calculated | Dice Diff")
            print("-" * 70)
            for err in results['errors']:
                print(f"{err['gun']:30} | {err['caliber']:3} | {err['expected']:8} | "
                      f"{err['calculated']:10} | {err['dice_diff']:+d}")

        return

    if args.test:
        print("=" * 70)
        print("HE CALCULATOR TEST EXAMPLES")
        print("=" * 70)

        test_calibers = [
            (20, None),
            (37, None),
            (50, 'at gun'),
            (75, 'howitzer'),
            (75, 'tank gun'),
            (88, None),
            (105, 'howitzer'),
            (120, None),
            (150, None),
            (210, None)
        ]

        print(f"\n{'Caliber':8} | {'Type':15} | HE Effect | Confidence | Category")
        print("-" * 75)

        for caliber, gun_type in test_calibers:
            result = calculate_he_effect(caliber, gun_type)
            type_str = gun_type or "standard"
            print(f"{caliber:3}mm   | {type_str:15} | {result['format']:9} | "
                  f"{result['confidence']:10} | {result['category']}")

        return

    if args.caliber:
        result = calculate_he_effect(args.caliber, args.type)

        print(f"\nCalliber: {args.caliber}mm")
        if args.type:
            print(f"Type: {args.type}")
        print(f"HE Effect: {result['format']}")
        print(f"  Dice: {result['dice']}")
        print(f"  Target: {result['target']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Category: {result['category']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
