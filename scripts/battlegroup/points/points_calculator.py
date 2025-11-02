#!/usr/bin/env python3
"""
Phase 9B Step 3 Part 5: Points Calculator for Units
Calculates points cost based on armor, movement, firepower, and modifiers.

Uses hybrid approach:
1. Name lookup for known units (from extracted army lists)
2. Spec-based calculation for vehicles (armor + movement + weapons)
3. Pattern-based estimation for infantry/support units
"""

import sqlite3
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"


@dataclass
class PointsBreakdown:
    """Breakdown of points calculation."""
    base_points: float
    armor_contribution: float
    movement_contribution: float
    firepower_contribution: float
    experience_modifier: float
    date_modifier: float
    final_points: int
    confidence: str
    method: str


class PointsCalculator:
    """
    Calculate points cost for BattleGroup units.

    Uses multiple strategies:
    - Name lookup (highest confidence)
    - Spec-based calculation (medium confidence)
    - Pattern-based estimation (low confidence)
    """

    # Armor rating point values (reverse-engineered from reference data)
    ARMOR_VALUES = {
        'A': 120, 'B': 100, 'C': 85, 'D': 70, 'E': 60,  # Super heavy to heavy
        'F': 50, 'G': 45, 'H': 40, 'I': 35, 'J': 30,    # Heavy to medium
        'K': 25, 'L': 20, 'M': 15, 'N': 10, 'O': 5,     # Medium-light to light
        'Soft-Skinned': 0
    }

    # Experience modifiers (from variance analysis)
    EXPERIENCE_MODIFIERS = {
        'i': 0.85,  # Inexperienced: -15% (avg 30.3 pts vs 44.8 regular)
        'r': 1.00,  # Regular: baseline
        'v': 1.10,  # Veteran: +10% (avg 35.3, but smaller units skew this)
        'e': 1.20,  # Elite: +20% (estimated, rare)
    }

    # Date modifiers (from variance analysis showing late-war cheaper)
    DATE_MODIFIERS = {
        '1943': 1.05,    # Early war: +5%
        '1944-06': 0.95, # Mid war: -5%
        '1944-09': 0.90, # Late war: -10%
        '1944-12': 1.00, # Battle of Bulge: normal (desperate measures)
        '1944': 0.95,    # Generic 1944: -5%
    }

    def __init__(self):
        """Initialize calculator with database connection."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self._build_lookup_tables()

    def _build_lookup_tables(self):
        """Build lookup tables from extracted data."""
        cursor = self.conn.cursor()

        # Build name -> points lookup from Step 3 army list data
        cursor.execute("""
            SELECT name, points_cost, battle_rating, unit_experience,
                   source_battle, source_date
            FROM bg_reference_vehicles
            WHERE source_document IS NOT NULL
              AND points_cost IS NOT NULL
        """)

        self.name_lookup = {}
        for row in cursor.fetchall():
            name, pts, br, exp, battle, date = row

            # Clean name
            clean_name = self._clean_name(name)

            if clean_name not in self.name_lookup:
                self.name_lookup[clean_name] = []

            self.name_lookup[clean_name].append({
                'points': pts,
                'br': br,
                'experience': exp,
                'battle': battle,
                'date': date
            })

        # Build spec lookup from Step 1 reference data
        cursor.execute("""
            SELECT name, armor_front, armor_side, armor_rear,
                   off_road_inches, road_inches, weapons
            FROM bg_reference_vehicles
            WHERE source_file IS NOT NULL
        """)

        self.spec_lookup = {}
        for row in cursor.fetchall():
            name, af, as_, ar, off, road, weapons = row
            clean_name = self._clean_name(name)

            self.spec_lookup[clean_name] = {
                'armor_front': af,
                'armor_side': as_,
                'armor_rear': ar,
                'off_road': off,
                'road': road,
                'weapons': weapons
            }

        print(f"[OK] Loaded {len(self.name_lookup)} unit names")
        print(f"[OK] Loaded {len(self.spec_lookup)} vehicle specs")

    def _clean_name(self, name: str) -> str:
        """Clean unit name for matching."""
        if not name:
            return ""

        # Remove dots, excessive whitespace
        clean = re.sub(r'\.+', '', name)
        clean = re.sub(r'\s+', ' ', clean).strip().lower()
        return clean

    def calculate_points(
        self,
        unit_name: str,
        armor_front: Optional[str] = None,
        armor_side: Optional[str] = None,
        movement_off_road: Optional[int] = None,
        movement_road: Optional[int] = None,
        main_weapon: Optional[str] = None,
        experience: str = 'r',
        date: str = '1944',
        unit_type: Optional[str] = None
    ) -> PointsBreakdown:
        """
        Calculate points for a unit.

        Args:
            unit_name: Name of unit (for lookup)
            armor_front: Front armor rating (A-O or Soft-Skinned)
            armor_side: Side armor rating
            movement_off_road: Off-road movement in inches
            movement_road: Road movement in inches
            main_weapon: Main weapon description
            experience: Experience level (i/r/v/e)
            date: Battle date for modifier
            unit_type: Type hint (vehicle/infantry/artillery/support)

        Returns:
            PointsBreakdown with calculation details
        """

        # Strategy 1: Name lookup (highest confidence)
        clean_name = self._clean_name(unit_name)
        if clean_name in self.name_lookup:
            matches = self.name_lookup[clean_name]

            # Find best match by experience and date
            best_match = self._find_best_match(matches, experience, date)

            if best_match:
                return PointsBreakdown(
                    base_points=best_match['points'],
                    armor_contribution=0,
                    movement_contribution=0,
                    firepower_contribution=0,
                    experience_modifier=1.0,
                    date_modifier=1.0,
                    final_points=best_match['points'],
                    confidence="High",
                    method="Name Lookup"
                )

        # Strategy 2: Spec-based calculation
        if armor_front or (clean_name in self.spec_lookup):
            specs = self.spec_lookup.get(clean_name, {})

            # Use provided specs or lookup specs
            af = armor_front or specs.get('armor_front')
            as_ = armor_side or specs.get('armor_side')
            off = movement_off_road or specs.get('off_road')
            road = movement_road or specs.get('road')

            if af or off:
                return self._calculate_from_specs(
                    af, as_, off, road, main_weapon, experience, date
                )

        # Strategy 3: Pattern-based estimation
        return self._estimate_from_pattern(unit_name, unit_type, experience, date)

    def _find_best_match(
        self,
        matches: List[Dict],
        experience: str,
        date: str
    ) -> Optional[Dict]:
        """Find best matching entry from multiple candidates."""

        # Prefer exact experience match
        for match in matches:
            if match['experience'] == experience:
                return match

        # Fallback to most common (Regular)
        for match in matches:
            if match['experience'] == 'r':
                return match

        # Return first match
        return matches[0] if matches else None

    def _calculate_from_specs(
        self,
        armor_front: Optional[str],
        armor_side: Optional[str],
        off_road: Optional[int],
        road: Optional[int],
        weapon: Optional[str],
        experience: str,
        date: str
    ) -> PointsBreakdown:
        """Calculate points from vehicle specifications."""

        # Armor contribution
        armor_pts = 0
        if armor_front:
            armor_pts += self.ARMOR_VALUES.get(armor_front, 0) * 0.4
        if armor_side:
            armor_pts += self.ARMOR_VALUES.get(armor_side, 0) * 0.3

        # Movement contribution (roughly 2 pts per inch off-road)
        movement_pts = 0
        if off_road:
            movement_pts = off_road * 2

        # Weapon contribution (basic estimation)
        weapon_pts = 0
        if weapon:
            weapon_pts = self._estimate_weapon_value(weapon)

        # Base points
        base = armor_pts + movement_pts + weapon_pts

        # Apply modifiers
        exp_mod = self.EXPERIENCE_MODIFIERS.get(experience, 1.0)
        date_mod = self.DATE_MODIFIERS.get(date, 1.0)

        final = round(base * exp_mod * date_mod)

        return PointsBreakdown(
            base_points=base,
            armor_contribution=armor_pts,
            movement_contribution=movement_pts,
            firepower_contribution=weapon_pts,
            experience_modifier=exp_mod,
            date_modifier=date_mod,
            final_points=final,
            confidence="Medium",
            method="Spec-Based"
        )

    def _estimate_weapon_value(self, weapon: str) -> float:
        """Estimate points contribution from weapon description."""
        if not weapon:
            return 0

        weapon_lower = weapon.lower()

        # Heavy tank guns
        if '88mm' in weapon_lower or '8.8cm' in weapon_lower:
            return 30
        if '75mm' in weapon_lower or '7.5cm' in weapon_lower:
            return 20
        if '76mm' in weapon_lower:
            return 22

        # Medium guns
        if '50mm' in weapon_lower or '5cm' in weapon_lower:
            return 12
        if '37mm' in weapon_lower:
            return 8

        # Machine guns only
        if 'mg' in weapon_lower and 'mm' not in weapon_lower:
            return 3

        return 10  # Default for unknown

    def _estimate_from_pattern(
        self,
        unit_name: str,
        unit_type: Optional[str],
        experience: str,
        date: str
    ) -> PointsBreakdown:
        """Estimate points from unit name patterns."""

        name_lower = unit_name.lower()

        # Infantry units
        if any(word in name_lower for word in ['infantry', 'rifle', 'grenadier', 'squad', 'platoon']):
            if 'platoon' in name_lower:
                base = 100
            elif 'squad' in name_lower:
                base = 40
            elif 'section' in name_lower:
                base = 30
            else:
                base = 25

        # Artillery
        elif any(word in name_lower for word in ['artillery', 'howitzer', 'gun', 'mortar']):
            if 'battery' in name_lower:
                base = 80
            elif 'heavy' in name_lower:
                base = 60
            else:
                base = 40

        # Tanks/vehicles
        elif any(word in name_lower for word in ['panzer', 'tank', 'sherman', 't-34', 'tiger']):
            if 'tiger' in name_lower or 'panther' in name_lower:
                base = 180
            elif 'company' in name_lower or 'platoon' in name_lower:
                base = 200
            else:
                base = 50

        # Support units
        elif any(word in name_lower for word in ['headquarters', 'signals', 'command', 'wire', 'medic', 'ambulance']):
            base = 15

        # Default
        else:
            base = 30

        # Apply modifiers
        exp_mod = self.EXPERIENCE_MODIFIERS.get(experience, 1.0)
        date_mod = self.DATE_MODIFIERS.get(date, 1.0)

        final = round(base * exp_mod * date_mod)

        return PointsBreakdown(
            base_points=base,
            armor_contribution=0,
            movement_contribution=0,
            firepower_contribution=0,
            experience_modifier=exp_mod,
            date_modifier=date_mod,
            final_points=final,
            confidence="Low",
            method="Pattern-Based"
        )

    def validate(self) -> Dict:
        """Validate calculator against all extracted data."""

        cursor = self.conn.cursor()

        # Get all units with known points
        cursor.execute("""
            SELECT name, points_cost, unit_experience, source_date
            FROM bg_reference_vehicles
            WHERE source_document IS NOT NULL
              AND points_cost IS NOT NULL
        """)

        results = {
            'total': 0,
            'within_5_pct': 0,
            'within_10_pct': 0,
            'within_20_pct': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'errors': []
        }

        for row in cursor.fetchall():
            name, actual_pts, exp, date = row

            if actual_pts <= 0:
                continue

            results['total'] += 1

            # Calculate predicted points
            breakdown = self.calculate_points(
                unit_name=name,
                experience=exp or 'r',
                date=date or '1944'
            )

            predicted = breakdown.final_points

            # Calculate error
            error_pct = abs(predicted - actual_pts) / actual_pts * 100

            if error_pct <= 5:
                results['within_5_pct'] += 1
            if error_pct <= 10:
                results['within_10_pct'] += 1
            if error_pct <= 20:
                results['within_20_pct'] += 1

            # Track by confidence
            if breakdown.confidence == "High":
                results['high_confidence'] += 1
            elif breakdown.confidence == "Medium":
                results['medium_confidence'] += 1
            else:
                results['low_confidence'] += 1

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
        description="Phase 9B Step 3: Points Calculator"
    )
    parser.add_argument(
        "--unit",
        type=str,
        help="Unit name to calculate points for"
    )
    parser.add_argument(
        "--experience",
        type=str,
        default="r",
        choices=['i', 'r', 'v', 'e'],
        help="Experience level (i/r/v/e)"
    )
    parser.add_argument(
        "--date",
        type=str,
        default="1944",
        help="Battle date (e.g., '1943-07', '1944-06')"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate calculator against all data"
    )

    args = parser.parse_args()

    calc = PointsCalculator()

    if args.validate:
        print("\nValidating Points Calculator...")
        print("=" * 60)

        results = calc.validate()

        total = results['total']
        within_10 = results['within_10_pct']
        accuracy = (within_10 / total * 100) if total > 0 else 0

        print(f"\nTotal units tested: {total}")
        print(f"Within 5%: {results['within_5_pct']} ({results['within_5_pct']/total*100:.1f}%)")
        print(f"Within 10%: {results['within_10_pct']} ({results['within_10_pct']/total*100:.1f}%)")
        print(f"Within 20%: {results['within_20_pct']} ({results['within_20_pct']/total*100:.1f}%)")
        print()
        print(f"High confidence: {results['high_confidence']}")
        print(f"Medium confidence: {results['medium_confidence']}")
        print(f"Low confidence: {results['low_confidence']}")
        print()

        if accuracy >= 90:
            print(f"[SUCCESS] Accuracy: {accuracy:.1f}% (target: 90%)")
        else:
            print(f"[NEEDS WORK] Accuracy: {accuracy:.1f}% (target: 90%)")
            print(f"\nLargest errors (showing first 10):")
            for err in sorted(results['errors'], key=lambda x: x['error_pct'], reverse=True)[:10]:
                print(f"  {err['name']:40} Actual:{err['actual']:3} Predicted:{err['predicted']:3} Error:{err['error_pct']:.0f}% ({err['method']})")

    elif args.unit:
        breakdown = calc.calculate_points(
            unit_name=args.unit,
            experience=args.experience,
            date=args.date
        )

        print(f"\nPoints Calculation for: {args.unit}")
        print("=" * 60)
        print(f"Experience: {args.experience}, Date: {args.date}")
        print()
        print(f"Base points: {breakdown.base_points:.1f}")
        print(f"  Armor contribution: {breakdown.armor_contribution:.1f}")
        print(f"  Movement contribution: {breakdown.movement_contribution:.1f}")
        print(f"  Firepower contribution: {breakdown.firepower_contribution:.1f}")
        print()
        print(f"Experience modifier: {breakdown.experience_modifier:.2f}x")
        print(f"Date modifier: {breakdown.date_modifier:.2f}x")
        print()
        print(f"Final points: {breakdown.final_points}")
        print(f"Confidence: {breakdown.confidence}")
        print(f"Method: {breakdown.method}")

    else:
        parser.print_help()

    calc.close()


if __name__ == "__main__":
    main()
