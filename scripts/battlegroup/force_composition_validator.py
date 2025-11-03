#!/usr/bin/env python3
"""
BattleGroup Force Composition Validator

Implements official Infantry Requirement Tables from Operation Torch book.
Validates generated forces against BattleGroup rules to ensure playability.

Based on official rules from BattleGroup Torch book (Infantry Requirement Tables).

Author: North Africa TO&E Builder
Date: November 2025
Version: 1.0.0
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict


# ============================================================================
# OFFICIAL INFANTRY REQUIREMENT TABLES (from BattleGroup Torch book)
# ============================================================================

# Infantry Requirement Table 1942
# For games representing 1941-1942 battles
INFANTRY_REQUIREMENTS_1942 = {
    # Format: points: {min_platoons, max_platoons, restricted_units}
    350: {"min": 0, "max_squads": 1, "max_platoons": 0, "restricted_units": 2},
    750: {"min": 0, "max_squads": 0, "max_platoons": 1, "restricted_units": 3},
    1500: {"min": 1, "max_squads": 0, "max_platoons": 3, "restricted_units": 4},
    3000: {"min": 2, "max_squads": 0, "max_platoons": 6, "restricted_units": 5}
}

# Infantry Requirement Table 1943
# For games representing 1943 battles (stricter requirements)
INFANTRY_REQUIREMENTS_1943 = {
    350: {"min": 1, "max_squads": 1, "max_platoons": 1, "restricted_units": 2},
    750: {"min": 1, "max_squads": 0, "max_platoons": 2, "restricted_units": 3},
    1500: {"min": 2, "max_squads": 0, "max_platoons": 3, "restricted_units": 4},
    3000: {"min": 3, "max_squads": 0, "max_platoons": 6, "restricted_units": 5}
}


@dataclass
class ForceCompositionReport:
    """Report of force composition validation"""
    is_valid: bool
    warnings: List[str]
    errors: List[str]
    infantry_count: int
    infantry_min: int
    infantry_max: int
    afv_percent: float
    infantry_percent: float
    artillery_percent: float
    force_diversity: int  # Number of different unit types


def get_infantry_requirements(points: int, year: int) -> Dict:
    """
    Get infantry requirements for given points and year.

    Interpolates between brackets for non-standard point values.

    Args:
        points: Points budget
        year: Year of battle (1941-1943)

    Returns:
        Dictionary with min/max requirements
    """
    # Choose table based on year
    table = INFANTRY_REQUIREMENTS_1942 if year <= 1942 else INFANTRY_REQUIREMENTS_1943

    # Find bracket
    brackets = sorted(table.keys())

    # Exact match
    if points in brackets:
        return table[points]

    # Find surrounding brackets for interpolation
    lower_bracket = None
    upper_bracket = None

    for i, bracket in enumerate(brackets):
        if points < bracket:
            upper_bracket = bracket
            if i > 0:
                lower_bracket = brackets[i-1]
            break

    # Below lowest bracket - use first bracket
    if lower_bracket is None:
        return table[brackets[0]]

    # Above highest bracket - use last bracket
    if upper_bracket is None:
        return table[brackets[-1]]

    # Interpolate between brackets
    lower_reqs = table[lower_bracket]
    upper_reqs = table[upper_bracket]

    # Calculate interpolation factor (0.0 to 1.0)
    factor = (points - lower_bracket) / (upper_bracket - lower_bracket)

    # Interpolate min (round up to ensure minimum met)
    min_platoons = lower_reqs["min"] + int((upper_reqs["min"] - lower_reqs["min"]) * factor + 0.5)

    # Interpolate max (round down to ensure maximum not exceeded)
    max_platoons = lower_reqs["max_platoons"] + int((upper_reqs["max_platoons"] - lower_reqs["max_platoons"]) * factor)

    return {
        "min": min_platoons,
        "max_squads": 0,
        "max_platoons": max_platoons,
        "restricted_units": lower_reqs["restricted_units"]
    }


def count_infantry_platoons(units: List[Dict]) -> int:
    """
    Count total infantry platoons in force.

    Args:
        units: List of unit dictionaries

    Returns:
        Total number of infantry platoons
    """
    platoon_count = 0

    for unit in units:
        unit_type = unit.get("type", "")

        if unit_type in ["infantry_platoon", "infantry"]:
            # If it's already organized as platoons
            platoon_count += unit.get("count", 0)

    return platoon_count


def calculate_category_percentages(units: List[Dict], total_points: int) -> Dict[str, float]:
    """
    Calculate percentage of points in each category.

    Categories: afv, infantry, artillery, support

    Args:
        units: List of unit dictionaries
        total_points: Total points budget

    Returns:
        Dictionary of category -> percentage
    """
    category_points = defaultdict(int)

    for unit in units:
        unit_type = unit.get("type", "unknown")
        points = unit.get("points", 0)

        # Categorize unit type
        if unit_type in ["infantry_platoon", "infantry"]:
            category = "infantry"
        elif unit_type in ["matilda", "crusader", "panzer_iii", "panzer_iv", "panzer_ii",
                            "m13_40", "m3_stuart", "m3_grant", "a9", "a10", "a13",
                            "tank_medium", "tank_light", "tank_heavy"]:
            category = "afv"
        elif unit_type in ["25pdr", "88mm", "pak_38", "2pdr", "6pdr", "bofors",
                            "artillery", "at_gun", "aa_gun"]:
            category = "artillery"
        else:
            category = "support"

        category_points[category] += points

    # Calculate percentages
    percentages = {}
    for category, points in category_points.items():
        percentages[category] = (points / total_points) * 100 if total_points > 0 else 0

    return percentages


def validate_force_composition(
    units: List[Dict],
    points_budget: int,
    year: int,
    historical_description: str = ""
) -> ForceCompositionReport:
    """
    Validate force composition against BattleGroup rules.

    Checks:
    1. Infantry requirement tables (min/max platoons)
    2. Combined arms balance (no mono-type forces)
    3. Historical accuracy (units match description)

    Args:
        units: List of unit dictionaries
        points_budget: Points budget for the force
        year: Year of battle (for infantry table selection)
        historical_description: Historical force description (for validation)

    Returns:
        ForceCompositionReport with validation results
    """
    warnings = []
    errors = []

    # Count infantry platoons
    infantry_platoons = count_infantry_platoons(units)

    # Get requirements for this point level
    reqs = get_infantry_requirements(points_budget, year)

    # Validate infantry count
    min_required = reqs["min"]
    max_allowed = reqs["max_platoons"]

    if infantry_platoons < min_required:
        errors.append(
            f"Insufficient infantry: {infantry_platoons} platoons "
            f"(minimum {min_required} for {points_budget} pts in {year})"
        )

    if infantry_platoons > max_allowed:
        errors.append(
            f"Excessive infantry: {infantry_platoons} platoons "
            f"(maximum {max_allowed} for {points_budget} pts in {year})"
        )

    # Calculate category percentages
    percentages = calculate_category_percentages(units, points_budget)

    afv_percent = percentages.get("afv", 0)
    infantry_percent = percentages.get("infantry", 0)
    artillery_percent = percentages.get("artillery", 0)

    # Check for historical tank forces
    has_historical_tanks = any(
        keyword in historical_description.lower()
        for keyword in ["tank", "panzer", "matilda", "crusader", "sherman", "squadron"]
    )

    if has_historical_tanks and afv_percent < 10:
        warnings.append(
            f"Historical force had tanks but only {afv_percent:.1f}% AFV points "
            f"(recommend 20%+)"
        )

    # Check for mono-type forces (bad gameplay)
    max_category_percent = max(percentages.values()) if percentages else 0

    if max_category_percent > 70:
        max_category = max(percentages, key=percentages.get)
        warnings.append(
            f"Force is {max_category_percent:.1f}% {max_category} "
            f"(recommend max 60% for combined arms gameplay)"
        )

    # Check force diversity
    unit_types = set(unit.get("type", "unknown") for unit in units)
    force_diversity = len(unit_types)

    if force_diversity < 2:
        warnings.append(
            f"Force has only {force_diversity} unit type "
            f"(recommend 2+ types for combined arms)"
        )

    # Overall validity
    is_valid = len(errors) == 0

    return ForceCompositionReport(
        is_valid=is_valid,
        warnings=warnings,
        errors=errors,
        infantry_count=infantry_platoons,
        infantry_min=min_required,
        infantry_max=max_allowed,
        afv_percent=afv_percent,
        infantry_percent=infantry_percent,
        artillery_percent=artillery_percent,
        force_diversity=force_diversity
    )


def print_validation_report(report: ForceCompositionReport, force_name: str = "Force"):
    """
    Print validation report to console.

    Args:
        report: ForceCompositionReport to print
        force_name: Name of the force being validated
    """
    print(f"\n{'='*60}")
    print(f"FORCE COMPOSITION VALIDATION: {force_name}")
    print(f"{'='*60}")

    if report.is_valid:
        print("[VALID] Force meets BattleGroup requirements")
    else:
        print("[INVALID] Force violates BattleGroup rules")

    print(f"\nInfantry: {report.infantry_count} platoons (min: {report.infantry_min}, max: {report.infantry_max})")
    print(f"AFV: {report.afv_percent:.1f}% of points")
    print(f"Infantry: {report.infantry_percent:.1f}% of points")
    print(f"Artillery: {report.artillery_percent:.1f}% of points")
    print(f"Force Diversity: {report.force_diversity} different unit types")

    if report.errors:
        print(f"\n[ERRORS] ({len(report.errors)}):")
        for error in report.errors:
            print(f"  - {error}")

    if report.warnings:
        print(f"\n[WARNINGS] ({len(report.warnings)}):")
        for warning in report.warnings:
            print(f"  - {warning}")

    print(f"{'='*60}\n")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for testing validation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate BattleGroup force composition"
    )
    parser.add_argument("--points", type=int, default=900, help="Points budget")
    parser.add_argument("--year", type=int, default=1942, help="Year (1941-1943)")
    parser.add_argument("--infantry", type=int, default=0, help="Number of infantry platoons")

    args = parser.parse_args()

    # Example validation
    print(f"Testing infantry requirements for {args.points} points in {args.year}")

    reqs = get_infantry_requirements(args.points, args.year)
    print(f"\nRequirements:")
    print(f"  Minimum infantry: {reqs['min']} platoons")
    print(f"  Maximum infantry: {reqs['max_platoons']} platoons")

    # Test with sample force
    sample_units = [
        {"type": "infantry_platoon", "count": args.infantry, "points": args.infantry * 160},
    ]

    report = validate_force_composition(sample_units, args.points, args.year)
    print_validation_report(report, f"Test Force ({args.points}pts, {args.year})")


if __name__ == "__main__":
    main()
