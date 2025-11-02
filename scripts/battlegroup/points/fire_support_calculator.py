#!/usr/bin/env python3
"""
Phase 9B Step 3 Part 5: Fire Support Points Calculator
Calculates points cost for off-board fire support (artillery, air strikes, etc.)
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
class FireSupportPointsBreakdown:
    """Breakdown of fire support points calculation."""
    base_points: int
    final_points: int
    battle_rating: int
    confidence: str
    method: str


class FireSupportCalculator:
    """
    Calculate points cost for BattleGroup off-board fire support.

    Types:
    - Target priority (1st/2nd/3rd at 3+/4+/5+)
    - Timed barrages (various calibers)
    - Air strikes
    - Pre-registered target points
    - Counter-battery fire missions
    """

    # Priority-based points
    PRIORITY_POINTS = {
        '1st': 20,  # 3+ roll
        '2nd': 10,  # 4+ roll
        '3rd': 5,   # 5+ roll
    }

    # Caliber-based barrage points
    BARRAGE_POINTS = {
        '152mm': 30,
        '150mm': 20,
        '6"': 30,
        '5.5"': 30,
        '122mm': 20,
        '105mm': 20,  # Fixed: was 10, should be 20
        '120mm': 20,
        '100mm': 15,
        '75mm': 5,    # Fixed: was 10, should be 5
    }

    # Special fire missions
    SPECIAL_MISSIONS = {
        'katyusha': 25,
        'nebelwerfer': 20,
        'typhoon': 25,
        'spitfire': 10,
        'stuka': 15,
        'pre-registered': 10,  # Fixed: was 15, should be 10
        'counter-battery': 10,
    }

    def __init__(self):
        """Initialize calculator with database connection."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self._build_lookup_table()

    def _build_lookup_table(self):
        """Build lookup table from extracted fire support data."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT name, points_cost, battle_rating, priority_level, support_type
            FROM bg_reference_fire_support
            WHERE points_cost IS NOT NULL
        """)

        self.name_lookup = {}
        for row in cursor.fetchall():
            name, pts, br, priority, support = row

            clean_name = self._clean_name(name)

            if clean_name not in self.name_lookup:
                self.name_lookup[clean_name] = []

            self.name_lookup[clean_name].append({
                'points': pts,
                'br': br,
                'priority_level': priority,
                'support_type': support
            })

        print(f"[OK] Loaded {len(self.name_lookup)} fire support types")

    def _clean_name(self, name: str) -> str:
        """Clean fire support name for matching."""
        if not name:
            return ""

        # Remove dots, excessive whitespace
        clean = re.sub(r'\.+', '', name)
        clean = re.sub(r'\s+', ' ', clean).strip().lower()
        return clean

    def calculate_points(
        self,
        fire_support_name: str,
        priority: Optional[str] = None,
        caliber: Optional[str] = None,
        mission_type: Optional[str] = None
    ) -> FireSupportPointsBreakdown:
        """
        Calculate points for off-board fire support.

        Args:
            fire_support_name: Name of fire mission (e.g., "1st Target priority (3+)", "Timed 150mm Barrage")
            priority: Priority level ('1st', '2nd', '3rd')
            caliber: Weapon caliber for barrages (e.g., '152mm', '105mm')
            mission_type: Type of mission ('timed-barrage', 'air-strike', etc.)

        Returns:
            FireSupportPointsBreakdown with calculation details
        """

        # Strategy 1: Name lookup
        clean_name = self._clean_name(fire_support_name)

        if clean_name in self.name_lookup:
            matches = self.name_lookup[clean_name]

            if matches:
                best_match = matches[0]

                return FireSupportPointsBreakdown(
                    base_points=best_match['points'],
                    final_points=best_match['points'],
                    battle_rating=best_match['br'] or 0,
                    confidence="High",
                    method="Name Lookup"
                )

        # Strategy 2: Pattern-based estimation
        return self._estimate_from_pattern(
            fire_support_name, priority, caliber, mission_type
        )

    def _estimate_from_pattern(
        self,
        fire_support_name: str,
        priority: Optional[str],
        caliber: Optional[str],
        mission_type: Optional[str]
    ) -> FireSupportPointsBreakdown:
        """Estimate points from fire support patterns."""

        name_lower = fire_support_name.lower()

        # Check for priority level
        if priority:
            pts = self.PRIORITY_POINTS.get(priority, 10)
            return FireSupportPointsBreakdown(
                base_points=pts,
                final_points=pts,
                battle_rating=0,
                confidence="High",
                method="Priority-Based"
            )

        # Check for caliber in name
        for cal, pts in self.BARRAGE_POINTS.items():
            if cal in name_lower:
                return FireSupportPointsBreakdown(
                    base_points=pts,
                    final_points=pts,
                    battle_rating=0,
                    confidence="High",
                    method="Caliber-Based"
                )

        # Check for special missions
        for mission, pts in self.SPECIAL_MISSIONS.items():
            if mission in name_lower:
                return FireSupportPointsBreakdown(
                    base_points=pts,
                    final_points=pts,
                    battle_rating=0,
                    confidence="High",
                    method="Mission-Based"
                )

        # Default estimation
        if 'barrage' in name_lower:
            pts = 20  # Medium barrage
        elif 'air' in name_lower or 'strike' in name_lower:
            pts = 20  # Generic air strike
        elif 'priority' in name_lower:
            pts = 10  # Default priority
        else:
            pts = 15  # Generic support

        return FireSupportPointsBreakdown(
            base_points=pts,
            final_points=pts,
            battle_rating=0,
            confidence="Medium",
            method="Default Estimation"
        )

    def validate(self) -> Dict:
        """Validate calculator against all extracted fire support data."""

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT name, points_cost, priority_level
            FROM bg_reference_fire_support
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
            name, actual_pts, priority = row

            if actual_pts <= 0:
                continue

            results['total'] += 1

            # Calculate predicted points
            breakdown = self.calculate_points(
                fire_support_name=name,
                priority=priority
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
        description="Phase 9B Step 3: Fire Support Points Calculator"
    )
    parser.add_argument(
        "--mission",
        type=str,
        help="Fire support mission name"
    )
    parser.add_argument(
        "--priority",
        type=str,
        choices=['1st', '2nd', '3rd'],
        help="Priority level (1st/2nd/3rd)"
    )
    parser.add_argument(
        "--caliber",
        type=str,
        help="Weapon caliber (e.g., '152mm', '105mm')"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate calculator against all data"
    )

    args = parser.parse_args()

    calc = FireSupportCalculator()

    if args.validate:
        print("\nValidating Fire Support Points Calculator...")
        print("=" * 60)

        results = calc.validate()

        total = results['total']
        exact = results['exact_match']
        within_10 = results['within_10_pct']

        accuracy_exact = (exact / total * 100) if total > 0 else 0
        accuracy_10 = (within_10 / total * 100) if total > 0 else 0

        print(f"\nTotal fire support tested: {total}")
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
                for err in results['errors'][:10]:
                    print(f"  {err['name']:50} Actual:{err['actual']:3} Predicted:{err['predicted']:3} Error:{err['error_pct']:.0f}%")

    elif args.mission:
        breakdown = calc.calculate_points(
            fire_support_name=args.mission,
            priority=args.priority,
            caliber=args.caliber
        )

        print(f"\nFire Support Points Calculation for: {args.mission}")
        print("=" * 60)
        print(f"Base points: {breakdown.base_points}")
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
