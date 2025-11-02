#!/usr/bin/env python3
"""
Phase 9B Step 3 Part 5: Defence Points Calculator
Calculates points cost for defensive structures (pillboxes, minefields, obstacles, etc.)
"""

import sqlite3
import sys
import re
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"


@dataclass
class DefencePointsBreakdown:
    """Breakdown of defence points calculation."""
    base_points: int
    class_modifier: float
    final_points: int
    battle_rating: int
    confidence: str
    method: str


class DefencePointsCalculator:
    """
    Calculate points cost for BattleGroup defensive structures.

    Primary strategy: Name lookup (defences are standardized)
    Fallback: Pattern-based estimation by type
    """

    # Base points by defence type (pattern-based fallback)
    BASE_POINTS = {
        'pillbox': 54,
        'bunker': 30,
        'fortification': 40,
        'minefield': 20,
        'hideout': 15,
        'trench': 10,
        'foxhole': 10,
        'barbed_wire': 10,
        'obstacle': 10,
        'road_block': 15,
        'barricade': 5,
        'building': 25,
    }

    def __init__(self):
        """Initialize calculator with database connection."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self._build_lookup_table()

    def _build_lookup_table(self):
        """Build lookup table from extracted defence data."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT name, points_cost, battle_rating, class_rating, defence_type
            FROM bg_reference_defences
            WHERE points_cost IS NOT NULL
        """)

        self.name_lookup = {}
        for row in cursor.fetchall():
            name, pts, br, class_r, def_type = row

            clean_name = self._clean_name(name)

            if clean_name not in self.name_lookup:
                self.name_lookup[clean_name] = []

            self.name_lookup[clean_name].append({
                'points': pts,
                'br': br,
                'class_rating': class_r,
                'defence_type': def_type
            })

        print(f"[OK] Loaded {len(self.name_lookup)} defence types")

    def _clean_name(self, name: str) -> str:
        """Clean defence name for matching."""
        if not name:
            return ""

        # Remove dots, excessive whitespace
        clean = re.sub(r'\.+', '', name)
        clean = re.sub(r'\s+', ' ', clean).strip().lower()
        return clean

    def calculate_points(
        self,
        defence_name: str,
        class_rating: Optional[str] = None
    ) -> DefencePointsBreakdown:
        """
        Calculate points for a defensive structure.

        Args:
            defence_name: Name of defence (e.g., "Machine Gun Pillbox", "Minefield")
            class_rating: Class rating if applicable (e.g., "Class 1", "Class 2")

        Returns:
            DefencePointsBreakdown with calculation details
        """

        # Strategy 1: Name lookup
        clean_name = self._clean_name(defence_name)

        if clean_name in self.name_lookup:
            matches = self.name_lookup[clean_name]

            # Find match by class rating if specified
            best_match = None
            if class_rating:
                for match in matches:
                    if match.get('class_rating') == class_rating:
                        best_match = match
                        break

            # Otherwise use first match
            if not best_match and matches:
                best_match = matches[0]

            if best_match:
                return DefencePointsBreakdown(
                    base_points=best_match['points'],
                    class_modifier=1.0,
                    final_points=best_match['points'],
                    battle_rating=best_match['br'] or 0,
                    confidence="High",
                    method="Name Lookup"
                )

        # Strategy 2: Pattern-based estimation
        return self._estimate_from_pattern(defence_name, class_rating)

    def _estimate_from_pattern(
        self,
        defence_name: str,
        class_rating: Optional[str]
    ) -> DefencePointsBreakdown:
        """Estimate points from defence name patterns."""

        name_lower = defence_name.lower()

        # Determine type
        base_pts = 10  # Default

        for def_type, pts in self.BASE_POINTS.items():
            if def_type in name_lower:
                base_pts = pts
                break

        # Class modifier for pillboxes
        class_mod = 1.0
        if class_rating:
            # Extract number from "Class X"
            class_match = re.search(r'(\d+)', class_rating)
            if class_match:
                class_num = int(class_match.group(1))
                # Higher class = more points
                class_mod = 1.0 + (class_num - 1) * 0.3

        final_pts = round(base_pts * class_mod)

        # Estimate BR (most defences have 0 or 1 BR)
        br = 0
        if 'bunker' in name_lower or 'command' in name_lower:
            br = 3
        elif 'pillbox' in name_lower or 'hideout' in name_lower:
            br = 1

        return DefencePointsBreakdown(
            base_points=base_pts,
            class_modifier=class_mod,
            final_points=final_pts,
            battle_rating=br,
            confidence="Medium",
            method="Pattern-Based"
        )

    def validate(self) -> Dict:
        """Validate calculator against all extracted defence data."""

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT name, points_cost, class_rating
            FROM bg_reference_defences
            WHERE points_cost IS NOT NULL
        """)

        results = {
            'total': 0,
            'within_5_pct': 0,
            'within_10_pct': 0,
            'within_20_pct': 0,
            'exact_match': 0,
            'errors': []
        }

        for row in cursor.fetchall():
            name, actual_pts, class_r = row

            if actual_pts <= 0:
                continue

            results['total'] += 1

            # Calculate predicted points
            breakdown = self.calculate_points(
                defence_name=name,
                class_rating=class_r
            )

            predicted = breakdown.final_points

            # Check for exact match
            if predicted == actual_pts:
                results['exact_match'] += 1

            # Calculate error percentage
            error_pct = abs(predicted - actual_pts) / actual_pts * 100

            if error_pct <= 5:
                results['within_5_pct'] += 1
            if error_pct <= 10:
                results['within_10_pct'] += 1
            if error_pct <= 20:
                results['within_20_pct'] += 1

            # Track large errors
            if error_pct > 20:
                results['errors'].append({
                    'name': name,
                    'actual': actual_pts,
                    'predicted': predicted,
                    'error_pct': error_pct,
                    'method': breakdown.method
                })

        return results

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 3: Defence Points Calculator"
    )
    parser.add_argument(
        "--defence",
        type=str,
        help="Defence name to calculate points for"
    )
    parser.add_argument(
        "--class",
        type=str,
        dest="class_rating",
        help="Class rating (e.g., 'Class 1', 'Class 2')"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate calculator against all data"
    )

    args = parser.parse_args()

    calc = DefencePointsCalculator()

    if args.validate:
        print("\nValidating Defence Points Calculator...")
        print("=" * 60)

        results = calc.validate()

        total = results['total']
        exact = results['exact_match']
        within_10 = results['within_10_pct']

        accuracy_exact = (exact / total * 100) if total > 0 else 0
        accuracy_10 = (within_10 / total * 100) if total > 0 else 0

        print(f"\nTotal defences tested: {total}")
        print(f"Exact match: {exact} ({accuracy_exact:.1f}%)")
        print(f"Within 5%: {results['within_5_pct']} ({results['within_5_pct']/total*100:.1f}%)")
        print(f"Within 10%: {within_10} ({accuracy_10:.1f}%)")
        print(f"Within 20%: {results['within_20_pct']} ({results['within_20_pct']/total*100:.1f}%)")
        print()

        if accuracy_10 >= 90:
            print(f"[SUCCESS] Accuracy: {accuracy_10:.1f}% (target: 90%)")
        else:
            print(f"[NEEDS WORK] Accuracy: {accuracy_10:.1f}% (target: 90%)")

            if results['errors']:
                print(f"\nErrors:")
                for err in results['errors']:
                    print(f"  {err['name']:40} Actual:{err['actual']:3} Predicted:{err['predicted']:3} Error:{err['error_pct']:.0f}%")

    elif args.defence:
        breakdown = calc.calculate_points(
            defence_name=args.defence,
            class_rating=args.class_rating
        )

        print(f"\nDefence Points Calculation for: {args.defence}")
        if args.class_rating:
            print(f"Class Rating: {args.class_rating}")
        print("=" * 60)
        print(f"Base points: {breakdown.base_points}")
        print(f"Class modifier: {breakdown.class_modifier:.2f}x")
        print()
        print(f"Final points: {breakdown.final_points}")
        print(f"Battle Rating: {breakdown.battle_rating}")
        print(f"Confidence: {breakdown.confidence}")
        print(f"Method: {breakdown.method}")

    else:
        parser.print_help()

    calc.close()


if __name__ == "__main__":
    main()
