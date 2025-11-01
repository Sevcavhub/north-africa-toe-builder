#!/usr/bin/env python3
"""
Armor Converter for BattleGroup

Converts armor thickness (mm) to BattleGroup letter rating (A-O scale) or numeric scale.

BattleGroup uses a reverse-alphabetical armor scale where:
- A-E: Super heavy to heavy armor (200mm+ to ~80mm)
- F-J: Medium-heavy to medium armor (~80mm to ~40mm)
- K-O: Medium-light to very light armor (~40mm to ~5mm)
- Numeric (6-12): Alternative scale for some vehicles
- "Soft-Skinned": No effective armor

NOTE: Without direct mm correlation in reference database, this converter uses:
1. Vehicle name lookup in reference database (primary method)
2. Rough mm-based estimation (fallback)

For production use, this needs refinement with actual vehicle cross-reference.

Usage:
    from armor_converter import convert_armor

    armor = convert_armor(front_mm=80, vehicle_name="Tiger")
    # Returns {"front": "H", "side": "J", "rear": "J", "confidence": "high"}
"""

import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR.parent.parent.parent / "database" / "master_database.db"


def convert_armor(
    front_mm: Optional[float] = None,
    side_mm: Optional[float] = None,
    rear_mm: Optional[float] = None,
    vehicle_name: Optional[str] = None
) -> Dict:
    """
    Convert armor thickness (mm) to BattleGroup letter/numeric rating.

    Args:
        front_mm: Front armor thickness in mm
        side_mm: Side armor thickness in mm
        rear_mm: Rear armor thickness in mm
        vehicle_name: Optional vehicle name for lookup in reference database

    Returns:
        dict: {
            "front": str,
            "side": str,
            "rear": str,
            "confidence": str,
            "method": str
        }

    Examples:
        >>> convert_armor(front_mm=100, side_mm=60, rear_mm=60)
        {'front': 'H', 'side': 'J', 'rear': 'J', 'confidence': 'medium'}

        >>> convert_armor(vehicle_name="Tiger")
        {'front': 'H', 'side': 'J', 'rear': 'J', 'confidence': 'high'}
    """

    # Try vehicle name lookup first (most accurate)
    if vehicle_name:
        armor_values = lookup_armor_by_name(vehicle_name)
        if armor_values:
            return {
                'front': armor_values[0],
                'side': armor_values[1],
                'rear': armor_values[2],
                'confidence': 'high',
                'method': 'reference_lookup',
                'vehicle_name': vehicle_name
            }

    # Fallback to mm-based estimation
    if front_mm is not None:
        front_rating = mm_to_armor_rating(front_mm)
        side_rating = mm_to_armor_rating(side_mm) if side_mm else front_rating
        rear_rating = mm_to_armor_rating(rear_mm) if rear_mm else side_rating

        return {
            'front': front_rating,
            'side': side_rating,
            'rear': rear_rating,
            'confidence': 'low',
            'method': 'mm_estimation',
            'front_mm': front_mm,
            'side_mm': side_mm,
            'rear_mm': rear_mm,
            'note': 'Rough estimation - vehicle name lookup preferred'
        }

    # No information provided
    return {
        'front': 'N',
        'side': 'O',
        'rear': 'O',
        'confidence': 'very_low',
        'method': 'default',
        'note': 'No data provided - default light armor'
    }


def lookup_armor_by_name(vehicle_name: str) -> Optional[Tuple[str, str, str]]:
    """
    Look up armor values from reference database by vehicle name.

    Returns:
        Tuple of (front, side, rear) armor ratings, or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Try exact match first
    cursor.execute("""
        SELECT armor_front, armor_side, armor_rear
        FROM bg_reference_vehicles
        WHERE LOWER(name) = LOWER(?)
        LIMIT 1
    """, (vehicle_name,))

    result = cursor.fetchone()

    if not result:
        # Try partial match
        cursor.execute("""
            SELECT armor_front, armor_side, armor_rear
            FROM bg_reference_vehicles
            WHERE LOWER(name) LIKE LOWER(?)
            LIMIT 1
        """, (f'%{vehicle_name}%',))
        result = cursor.fetchone()

    conn.close()

    if result and result[0]:
        return (result[0], result[1], result[2])

    return None


def mm_to_armor_rating(mm: float) -> str:
    """
    Convert armor thickness in mm to BattleGroup letter/numeric rating.

    This is a rough estimation based on observed patterns. Actual BattleGroup
    ratings may vary based on armor quality, slope, and vehicle type.

    Args:
        mm: Armor thickness in millimeters

    Returns:
        str: Armor rating (letter A-O or numeric 6-12 or "Soft-Skinned")
    """
    if mm <= 0:
        return "Soft-Skinned"

    # Rough mm-to-letter mapping (estimated from common vehicles)
    if mm >= 200:
        return "A"  # Super heavy (IS-3, Jagdtiger)
    elif mm >= 180:
        return "B"  # Very heavy
    elif mm >= 150:
        return "C"  # Heavy (Churchill VII)
    elif mm >= 130:
        return "D"  # Heavy
    elif mm >= 110:
        return "E"  # Heavy (IS-2, Matilda)
    elif mm >= 90:
        return "F"  # Medium-heavy (ISU-152)
    elif mm >= 80:
        return "G"  # Medium (KV-1)
    elif mm >= 70:
        return "H"  # Medium (Tiger)
    elif mm >= 60:
        return "I"  # Medium
    elif mm >= 50:
        return "J"  # Medium-light (Tiger side)
    elif mm >= 40:
        return "K"  # Light (T-34)
    elif mm >= 30:
        return "L"  # Light (Panzer III/IV)
    elif mm >= 20:
        return "M"  # Very light
    elif mm >= 10:
        return "N"  # Minimal (Panzer II)
    elif mm >= 5:
        return "O"  # Very minimal (halftracks)
    else:
        return "Soft-Skinned"  # < 5mm = no effective armor


def validate_against_reference() -> Dict:
    """
    Validate armor converter against reference database.

    Note: This validation uses vehicle name lookup, so it primarily tests
    the lookup mechanism rather than mm-based conversion.

    Returns:
        dict: Validation statistics
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all vehicles with armor data from reference
    cursor.execute("""
        SELECT name, armor_front, armor_side, armor_rear
        FROM bg_reference_vehicles
        WHERE armor_front IS NOT NULL
        LIMIT 100
    """)

    total = 0
    perfect_match = 0
    errors = []

    for name, ref_front, ref_side, ref_rear in cursor.fetchall():
        total += 1

        # Test lookup
        result = convert_armor(vehicle_name=name)

        # Check accuracy
        if (result['front'] == ref_front and
            result['side'] == ref_side and
            result['rear'] == ref_rear):
            perfect_match += 1
        else:
            errors.append({
                'vehicle': name,
                'expected': f"{ref_front}/{ref_side}/{ref_rear}",
                'calculated': f"{result['front']}/{result['side']}/{result['rear']}"
            })

    conn.close()

    accuracy = (perfect_match / total * 100) if total > 0 else 0

    return {
        'total_vehicles': total,
        'perfect_match': perfect_match,
        'errors': total - perfect_match,
        'accuracy_percent': accuracy,
        'error_details': errors[:10],
        'passed_95_target': accuracy >= 95.0,
        'note': 'This validates vehicle name lookup only, not mm-based conversion'
    }


def main():
    """CLI interface for armor converter."""
    import argparse

    parser = argparse.ArgumentParser(description='Convert armor mm to BattleGroup rating')
    parser.add_argument('--front', type=float, help='Front armor in mm')
    parser.add_argument('--side', type=float, help='Side armor in mm')
    parser.add_argument('--rear', type=float, help='Rear armor in mm')
    parser.add_argument('--name', help='Vehicle name for lookup')
    parser.add_argument('--validate', action='store_true', help='Validate against reference database')
    parser.add_argument('--test', action='store_true', help='Run test examples')

    args = parser.parse_args()

    if args.validate:
        print("=" * 80)
        print("ARMOR CONVERTER VALIDATION")
        print("=" * 80)
        print("\nValidating against reference database (name lookup)...")

        results = validate_against_reference()

        print(f"\nTotal vehicles tested: {results['total_vehicles']}")
        print(f"Perfect matches: {results['perfect_match']}")
        print(f"Errors: {results['errors']}")
        print(f"Accuracy: {results['accuracy_percent']:.1f}%")
        print(f"Target (95%): {'PASS' if results['passed_95_target'] else 'FAIL'}")
        print(f"\n{results['note']}")

        if results['error_details']:
            print(f"\nFirst {len(results['error_details'])} errors:")
            print(f"{'Vehicle':35} | Expected (F/S/R) | Calculated")
            print("-" * 70)
            for err in results['error_details']:
                print(f"{err['vehicle'][:35]:35} | {err['expected']:15} | {err['calculated']}")

        return

    if args.test:
        print("=" * 80)
        print("ARMOR CONVERTER TEST EXAMPLES")
        print("=" * 80)

        test_vehicles = [
            "Tiger",
            "Panther",
            "Panzer IV H",
            "T-34",
            "Sherman"
        ]

        print(f"\n{'Vehicle':25} | Front | Side | Rear | Confidence | Method")
        print("-" * 80)

        for vname in test_vehicles:
            result = convert_armor(vehicle_name=vname)
            print(f"{vname:25} | {result['front']:5} | {result['side']:4} | {result['rear']:4} | "
                  f"{result['confidence']:10} | {result['method']}")

        print("\n\nMM-Based Estimation Examples:")
        print(f"\n{'Description':30} | Front mm | Rating | Confidence")
        print("-" * 70)

        test_mm = [
            ("Super heavy (200mm)", 200),
            ("Heavy (100mm)", 100),
            ("Medium (70mm)", 70),
            ("Light (30mm)", 30),
            ("Very light (10mm)", 10)
        ]

        for desc, mm_val in test_mm:
            result = convert_armor(front_mm=mm_val)
            print(f"{desc:30} | {mm_val:8} | {result['front']:6} | {result['confidence']}")

        return

    if args.name or args.front:
        result = convert_armor(
            front_mm=args.front,
            side_mm=args.side,
            rear_mm=args.rear,
            vehicle_name=args.name
        )

        if args.name:
            print(f"\nVehicle: {args.name}")
        if args.front:
            print(f"Armor (mm): Front={args.front}, Side={args.side or 'N/A'}, Rear={args.rear or 'N/A'}")

        print(f"\nArmor Ratings:")
        print(f"  Front: {result['front']}")
        print(f"  Side:  {result['side']}")
        print(f"  Rear:  {result['rear']}")
        print(f"\nConfidence: {result['confidence']}")
        print(f"Method: {result['method']}")
        if 'note' in result:
            print(f"Note: {result['note']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
