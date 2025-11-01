#!/usr/bin/env python3
"""
Movement Calculator for BattleGroup

Converts vehicle type/weight to BattleGroup movement (inches).

Based on reference database analysis showing type-based patterns:
- Heavy tanks: 6" off-road / 10" road
- Medium tanks: 8-9" off-road / 12-16" road
- Light tanks: 9-12" off-road / 13-18" road
- Tank destroyers: 8-10" off-road / 13-16" road
- Halftracks: 12" off-road / 16-18" road
- Armored cars: 8-18" off-road / 12-26" road (varies widely)
- Trucks: 6-8" off-road / 16-24" road

Usage:
    from movement_calculator import calculate_movement

    mv = calculate_movement(vehicle_type="Medium Tank")
    # Returns {"off_road": 8, "road": 12, "format": "8\"/12\"", "confidence": "high"}
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR.parent.parent.parent / "database" / "master_database.db"
LOOKUP_TABLE_PATH = SCRIPT_DIR / "lookup_tables" / "vehicle_movement_lookup.json"

# Cache for lookup table
_LOOKUP_TABLE_CACHE = None


def load_lookup_table() -> Dict:
    """Load the vehicle movement lookup table (cached)."""
    global _LOOKUP_TABLE_CACHE
    if _LOOKUP_TABLE_CACHE is None:
        try:
            with open(LOOKUP_TABLE_PATH, 'r', encoding='utf-8') as f:
                _LOOKUP_TABLE_CACHE = json.load(f)
        except FileNotFoundError:
            print(f"WARNING: Lookup table not found at {LOOKUP_TABLE_PATH}")
            print("Run build_vehicle_movement_lookup.py to generate it.")
            _LOOKUP_TABLE_CACHE = {"vehicles": {}}
    return _LOOKUP_TABLE_CACHE


def lookup_movement_by_name(vehicle_name: str) -> Optional[Tuple[int, int, str]]:
    """
    Look up movement from vehicle name in lookup table.

    Args:
        vehicle_name: Vehicle name to look up

    Returns:
        Tuple of (off_road, road, confidence) or None if not found
    """
    lookup_table = load_lookup_table()
    vehicles = lookup_table.get("vehicles", {})

    # Try exact match first (case-insensitive)
    for name, data in vehicles.items():
        if name.lower() == vehicle_name.lower():
            return (data["off_road"], data["road"], "high")

    # Try partial match (vehicle name contains lookup name or vice versa)
    vehicle_lower = vehicle_name.lower()
    for name, data in vehicles.items():
        name_lower = name.lower()
        if name_lower in vehicle_lower or vehicle_lower in name_lower:
            # Require at least 5 characters match to avoid false positives
            if len(name_lower) >= 5 or len(vehicle_lower) >= 5:
                return (data["off_road"], data["road"], "medium")

    return None


def calculate_movement(
    vehicle_name: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    weight_tonnes: Optional[float] = None,
    power_hp: Optional[int] = None
) -> Dict:
    """
    Calculate BattleGroup movement from vehicle characteristics.

    Uses a lookup-first approach:
    1. Try vehicle name lookup in reference table (most accurate)
    2. Fall back to vehicle type formula
    3. Fall back to weight-based estimation

    Args:
        vehicle_name: Vehicle name for lookup (e.g., "Tiger", "Panzer IV H")
        vehicle_type: Vehicle type/class (e.g., "Heavy Tank", "Halftrack", "Armored Car")
        weight_tonnes: Optional vehicle weight in tonnes (for refinement)
        power_hp: Optional engine power in horsepower (for refinement)

    Returns:
        dict: {"off_road": int, "road": int, "format": str, "confidence": str}

    Examples:
        >>> calculate_movement(vehicle_name="Tiger")
        {'off_road': 8, 'road': 12, 'format': '8"/12"', 'confidence': 'high'}

        >>> calculate_movement(vehicle_type="Halftrack")
        {'off_road': 12, 'road': 16, 'format': '12"/16"', 'confidence': 'high'}
    """

    # METHOD 1: Try vehicle name lookup first (MOST ACCURATE)
    if vehicle_name:
        lookup_result = lookup_movement_by_name(vehicle_name)
        if lookup_result:
            off_road, road, confidence = lookup_result
            return {
                'off_road': off_road,
                'road': road,
                'format': f'{off_road}\"/{road}\"',
                'confidence': confidence,
                'method': 'name_lookup',
                'vehicle_name': vehicle_name
            }

    # METHOD 2: Try vehicle type-based formula (FALLBACK)
    type_movement_map = {
        # Tanks
        'heavy tank': (6, 10),
        'heavy_tank': (6, 10),
        'medium tank': (8, 12),
        'medium_tank': (8, 12),
        'tank': (8, 12),  # Generic tank
        'light tank': (12, 18),
        'light_tank': (12, 18),

        # Tank destroyers & assault guns
        'tank destroyer': (8, 14),
        'tank_destroyer': (8, 14),
        'assault gun': (8, 12),
        'assault_gun': (8, 12),
        'self-propelled gun': (8, 12),
        'self_propelled_artillery': (8, 14),

        # Armored vehicles
        'armored car': (12, 20),
        'armored_car': (12, 20),
        'armoured car': (12, 20),
        'scout car': (14, 22),

        # Infantry carriers
        'halftrack': (12, 16),
        'half-track': (12, 16),
        'armored personnel carrier': (12, 16),
        'armored_personnel_carrier': (12, 16),
        'armoured personnel carrier': (12, 16),

        # Soft-skinned vehicles
        'truck': (6, 24),
        'lorry': (6, 24),
        'car': (6, 24),
        'jeep': (18, 26),  # Fast reconnaissance

        # Specialized vehicles
        'motorcycle': (6, 24),
        'tractor': (10, 16),
        'engineering vehicle': (4, 6),
        'engineering_vehicle': (4, 6),
        'recovery vehicle': (6, 24),
        'ambulance': (6, 24),

        # Artillery
        'self-propelled anti-aircraft': (8, 12),
        'self_propelled_anti_aircraft': (8, 12),
        'self-propelled artillery': (8, 14),

        # Misc
        'amphibious vehicle': (6, 24),
        'amphibious_vehicle': (6, 24),
        'horse drawn': (4, 6),
        'horse_drawn': (4, 6),
    }

    confidence = 'medium'  # Default

    # Try to match vehicle type
    if vehicle_type:
        vtype_lower = vehicle_type.lower().strip()

        # Direct match
        if vtype_lower in type_movement_map:
            off_road, road = type_movement_map[vtype_lower]
            confidence = 'high'
        else:
            # Fuzzy matching - check if any key is in the vehicle type
            matched = False
            for key, (off, rd) in type_movement_map.items():
                if key in vtype_lower or vtype_lower in key:
                    off_road, road = off, rd
                    confidence = 'medium'
                    matched = True
                    break

            if not matched:
                # Default to medium tank if no match
                off_road, road = 8, 12
                confidence = 'low'

        # Refine based on weight if available
        if weight_tonnes and weight_tonnes > 0:
            if weight_tonnes < 10:
                # Light vehicle - might be faster
                if 'tank' in vtype_lower:
                    off_road = max(off_road, 10)
                    road = max(road, 16)
            elif weight_tonnes > 40:
                # Heavy vehicle - slower
                off_road = min(off_road, 6)
                road = min(road, 10)

        return {
            'off_road': off_road,
            'road': road,
            'format': f'{off_road}\"/{road}\"',
            'confidence': confidence,
            'vehicle_type': vehicle_type
        }

    # Fallback to weight-based estimation
    if weight_tonnes and weight_tonnes > 0:
        if weight_tonnes < 5:
            off_road, road = 14, 22  # Very light (scout car, motorcycle)
        elif weight_tonnes < 15:
            off_road, road = 10, 16  # Light (light tank, halftrack)
        elif weight_tonnes < 30:
            off_road, road = 8, 12  # Medium (medium tank)
        elif weight_tonnes < 45:
            off_road, road = 7, 11  # Heavy (heavy tank)
        else:
            off_road, road = 5, 8  # Super heavy

        return {
            'off_road': off_road,
            'road': road,
            'format': f'{off_road}\"/{road}\"',
            'confidence': 'low',
            'note': 'Weight-based estimate (vehicle type preferred)'
        }

    # No information provided
    return {
        'off_road': 8,
        'road': 12,
        'format': '8\"/12\"',
        'confidence': 'very low',
        'note': 'Default medium vehicle movement'
    }


def validate_against_reference() -> Dict:
    """
    Validate movement calculator against reference database.

    Returns:
        dict: Validation statistics including accuracy percentage
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all vehicles with movement data from reference
    cursor.execute("""
        SELECT name, vehicle_type, off_road_inches, road_inches
        FROM bg_reference_vehicles
        WHERE off_road_inches IS NOT NULL AND road_inches IS NOT NULL
    """)

    total = 0
    exact_match = 0
    close_match = 0  # Within 2 inches
    errors = []

    for name, vtype, ref_off_road, ref_road in cursor.fetchall():
        total += 1

        # Calculate movement (pass both name and type)
        calculated = calculate_movement(vehicle_name=name, vehicle_type=vtype)

        # Check accuracy
        off_diff = abs(calculated['off_road'] - ref_off_road)
        road_diff = abs(calculated['road'] - ref_road)

        if off_diff == 0 and road_diff == 0:
            exact_match += 1
            close_match += 1
        elif off_diff <= 2 and road_diff <= 4:
            close_match += 1
        else:
            errors.append({
                'vehicle': name,
                'type': vtype or 'unknown',
                'expected': f'{ref_off_road}\"/{ref_road}\"',
                'calculated': calculated['format'],
                'off_diff': off_diff,
                'road_diff': road_diff
            })

    conn.close()

    exact_accuracy = (exact_match / total * 100) if total > 0 else 0
    close_accuracy = (close_match / total * 100) if total > 0 else 0

    return {
        'total_vehicles': total,
        'exact_match': exact_match,
        'close_match': close_match,
        'errors': total - close_match,
        'exact_accuracy_percent': exact_accuracy,
        'close_accuracy_percent': close_accuracy,
        'error_details': errors[:15],  # First 15 errors
        'passed_95_target': close_accuracy >= 95.0
    }


def main():
    """CLI interface for movement calculator."""
    import argparse

    parser = argparse.ArgumentParser(description='Calculate BattleGroup movement from vehicle type/weight')
    parser.add_argument('--type', help='Vehicle type (e.g., "Medium Tank", "Halftrack")')
    parser.add_argument('--weight', type=float, help='Vehicle weight in tonnes')
    parser.add_argument('--power', type=int, help='Engine power in horsepower')
    parser.add_argument('--validate', action='store_true', help='Validate against reference database')
    parser.add_argument('--test', action='store_true', help='Run test examples')

    args = parser.parse_args()

    if args.validate:
        print("=" * 80)
        print("MOVEMENT CALCULATOR VALIDATION")
        print("=" * 80)
        print("\nValidating against reference database...")

        results = validate_against_reference()

        print(f"\nTotal vehicles tested: {results['total_vehicles']}")
        print(f"Exact matches: {results['exact_match']}")
        print(f"Close matches (±2\"/±4\"): {results['close_match']}")
        print(f"Errors: {results['errors']}")
        print(f"Exact accuracy: {results['exact_accuracy_percent']:.1f}%")
        print(f"Close accuracy: {results['close_accuracy_percent']:.1f}%")
        print(f"Target (95%): {'PASS' if results['passed_95_target'] else 'FAIL'}")

        if results['error_details']:
            print(f"\nFirst {len(results['error_details'])} errors:")
            print(f"{'Vehicle':35} | {'Type':20} | Expected | Calculated | Off Diff | Road Diff")
            print("-" * 110)
            for err in results['error_details']:
                print(f"{err['vehicle'][:35]:35} | {err['type'][:20]:20} | "
                      f"{err['expected']:8} | {err['calculated']:10} | {err['off_diff']:8} | {err['road_diff']:9}")

        return

    if args.test:
        print("=" * 80)
        print("MOVEMENT CALCULATOR TEST EXAMPLES")
        print("=" * 80)

        test_types = [
            "Heavy Tank",
            "Medium Tank",
            "Light Tank",
            "Tank Destroyer",
            "Halftrack",
            "Armored Car",
            "Truck",
            "Jeep"
        ]

        print(f"\n{'Vehicle Type':25} | Movement  | Confidence")
        print("-" * 60)

        for vtype in test_types:
            result = calculate_movement(vehicle_type=vtype)
            print(f"{vtype:25} | {result['format']:9} | {result['confidence']}")

        return

    if args.type or args.weight:
        result = calculate_movement(
            vehicle_type=args.type,
            weight_tonnes=args.weight,
            power_hp=args.power
        )

        print(f"\nVehicle Type: {args.type or 'Not specified'}")
        if args.weight:
            print(f"Weight: {args.weight} tonnes")
        if args.power:
            print(f"Power: {args.power} hp")
        print(f"\nMovement: {result['format']}")
        print(f"  Off-road: {result['off_road']}\"")
        print(f"  Road: {result['road']}\"")
        print(f"  Confidence: {result['confidence']}")
        if 'note' in result:
            print(f"  Note: {result['note']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
