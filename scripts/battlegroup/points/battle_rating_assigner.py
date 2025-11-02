#!/usr/bin/env python3
"""
Phase 9B Step 3 Part 6: Battle Rating Assigner
Assigns Battle Rating (BR) values based on unit type, size, and importance.

BR represents unit importance to force morale, NOT combat power.
"""

import sqlite3
import sys
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"


@dataclass
class BRAssignment:
    """Battle Rating assignment breakdown."""
    base_br: int
    size_modifier: int
    importance_modifier: int
    final_br: int
    experience: str
    confidence: str
    method: str


class BattleRatingAssigner:
    """
    Assign Battle Rating values for BattleGroup units.

    BR = Unit importance to battlegroup morale/breaking point
    NOT the same as combat effectiveness (points cost)

    Key principles (from BattleGroup rules):
    - BR 0: Unimportant (e.g., extra transport, some support)
    - BR 1-2: Minor importance (individual vehicles, small teams)
    - BR 3-5: Standard importance (typical combat units)
    - BR 6-10: Important (platoons, key assets)
    - BR 11+: Vital (companies, HQ elements, critical units)
    """

    # Base BR by unit type and size
    BR_BASE = {
        # Support units (typically low BR regardless of cost)
        'headquarters': 3,
        'signals': 1,
        'wire_team': 0,
        'dispatch_rider': 0,
        'supply': 1,
        'ambulance': 2,
        'medic': 0,
        'aid_station': 5,  # Vital for morale despite low cost

        # Infantry scale
        'infantry_individual': 0,
        'infantry_team': 2,
        'infantry_squad': 3,
        'infantry_section': 3,
        'infantry_platoon': 11,
        'infantry_company': 16,

        # Armor scale
        'tank_individual': 2,
        'tank_troop': 5,
        'tank_platoon': 9,
        'tank_squadron': 12,
        'tank_company': 15,

        # Artillery
        'gun_individual': 2,
        'gun_battery': 4,

        # Reconnaissance
        'recon_individual': 1,
        'recon_section': 3,
        'recon_platoon': 7,

        # Engineers
        'engineer_team': 2,
        'engineer_platoon': 11,
    }

    # Experience modifiers (from variance analysis)
    EXPERIENCE_BR_MOD = {
        'i': -1,  # Inexperienced: -1 BR
        'r': 0,   # Regular: no change
        'v': 0,   # Veteran: no change (same BR as regular typically)
        'e': +1,  # Elite: +1 BR
    }

    def __init__(self):
        """Initialize assigner with database connection."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self._build_lookup_table()

    def _build_lookup_table(self):
        """Build lookup table from extracted data."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT name, battle_rating, unit_experience, points_cost
            FROM bg_reference_vehicles
            WHERE source_document IS NOT NULL
              AND battle_rating IS NOT NULL
        """)

        self.name_lookup = {}
        for row in cursor.fetchall():
            name, br, exp, pts = row

            clean_name = self._clean_name(name)

            if clean_name not in self.name_lookup:
                self.name_lookup[clean_name] = []

            self.name_lookup[clean_name].append({
                'br': br,
                'experience': exp,
                'points': pts
            })

        print(f"[OK] Loaded {len(self.name_lookup)} unit BRs")

    def _clean_name(self, name: str) -> str:
        """Clean unit name for matching."""
        if not name:
            return ""

        clean = re.sub(r'\.+', '', name)
        clean = re.sub(r'\s+', ' ', clean).strip().lower()
        return clean

    def assign_br(
        self,
        unit_name: str,
        points_cost: Optional[int] = None,
        experience: str = 'r',
        unit_type: Optional[str] = None
    ) -> BRAssignment:
        """
        Assign Battle Rating for a unit.

        Args:
            unit_name: Name of unit
            points_cost: Points cost (for correlation)
            experience: Experience level (i/r/v/e)
            unit_type: Type hint (infantry/armor/artillery/support)

        Returns:
            BRAssignment with calculation details
        """

        # Strategy 1: Name lookup (highest confidence)
        clean_name = self._clean_name(unit_name)

        if clean_name in self.name_lookup:
            matches = self.name_lookup[clean_name]

            # Find best match by experience
            best_match = None
            for match in matches:
                if match['experience'] == experience:
                    best_match = match
                    break

            if not best_match and matches:
                best_match = matches[0]

            if best_match:
                return BRAssignment(
                    base_br=best_match['br'],
                    size_modifier=0,
                    importance_modifier=0,
                    final_br=best_match['br'],
                    experience=experience,
                    confidence="High",
                    method="Name Lookup"
                )

        # Strategy 2: Pattern-based assignment
        return self._assign_from_pattern(unit_name, points_cost, experience, unit_type)

    def _assign_from_pattern(
        self,
        unit_name: str,
        points_cost: Optional[int],
        experience: str,
        unit_type: Optional[str]
    ) -> BRAssignment:
        """Assign BR from unit name and type patterns."""

        name_lower = unit_name.lower()

        # Determine unit type and size
        base_br = 2  # Default

        # Size detection
        is_company = 'company' in name_lower or 'battalion' in name_lower
        is_platoon = 'platoon' in name_lower
        is_squadron = 'squadron' in name_lower
        is_troop = 'troop' in name_lower
        is_battery = 'battery' in name_lower
        is_squad = 'squad' in name_lower or 'section' in name_lower
        is_team = 'team' in name_lower

        # Type detection
        is_infantry = any(word in name_lower for word in [
            'infantry', 'rifle', 'grenadier', 'pioneer', 'engineer'
        ])
        is_tank = any(word in name_lower for word in [
            'panzer', 'tank', 'sherman', 't-34', 'tiger', 'panther'
        ])
        is_support = any(word in name_lower for word in [
            'headquarters', 'signals', 'wire', 'supply', 'medic', 'ambulance'
        ])
        is_artillery = any(word in name_lower for word in [
            'artillery', 'howitzer', 'gun', 'mortar'
        ])

        # Assign base BR by type and size
        if is_company:
            if is_infantry:
                base_br = 16
            elif is_tank:
                base_br = 15
            else:
                base_br = 14
        elif is_platoon:
            if is_infantry or 'engineer' in name_lower:
                base_br = 11
            elif is_tank:
                base_br = 9
            elif 'recon' in name_lower:
                base_br = 7
            else:
                base_br = 8
        elif is_squadron:
            base_br = 12
        elif is_troop:
            base_br = 5
        elif is_battery:
            base_br = 4
        elif is_squad or is_section:
            base_br = 3
        elif is_team:
            if is_support:
                base_br = 0 if 'wire' in name_lower else 1
            else:
                base_br = 2
        elif is_support:
            if 'headquarters' in name_lower or 'command' in name_lower:
                base_br = 3
            elif 'aid' in name_lower and 'post' in name_lower:
                base_br = 5  # Aid posts are vital
            elif 'ambulance' in name_lower:
                base_br = 2
            else:
                base_br = 1
        elif is_tank or is_artillery:
            # Individual vehicle/gun
            base_br = 2
        else:
            # Default: use points to estimate
            if points_cost:
                if points_cost > 150:
                    base_br = 9
                elif points_cost > 100:
                    base_br = 7
                elif points_cost > 50:
                    base_br = 4
                elif points_cost > 20:
                    base_br = 2
                else:
                    base_br = 1

        # Apply experience modifier
        exp_mod = self.EXPERIENCE_BR_MOD.get(experience, 0)
        final_br = max(0, base_br + exp_mod)

        return BRAssignment(
            base_br=base_br,
            size_modifier=0,
            importance_modifier=exp_mod,
            final_br=final_br,
            experience=experience,
            confidence="Medium",
            method="Pattern-Based"
        )

    def validate(self) -> Dict:
        """Validate assigner against all extracted data."""

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT name, battle_rating, unit_experience, points_cost
            FROM bg_reference_vehicles
            WHERE source_document IS NOT NULL
              AND battle_rating IS NOT NULL
        """)

        results = {
            'total': 0,
            'exact_match': 0,
            'within_1': 0,
            'within_2': 0,
            'within_3': 0,
            'errors': []
        }

        for row in cursor.fetchall():
            name, actual_br, exp, pts = row

            results['total'] += 1

            # Assign predicted BR
            assignment = self.assign_br(
                unit_name=name,
                points_cost=pts,
                experience=exp or 'r'
            )

            predicted = assignment.final_br

            # Check accuracy
            diff = abs(predicted - actual_br)

            if diff == 0:
                results['exact_match'] += 1
            if diff <= 1:
                results['within_1'] += 1
            if diff <= 2:
                results['within_2'] += 1
            if diff <= 3:
                results['within_3'] += 1

            # Track large errors
            if diff > 2:
                results['errors'].append({
                    'name': name,
                    'actual': actual_br,
                    'predicted': predicted,
                    'diff': diff,
                    'method': assignment.method
                })

        return results

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 3: Battle Rating Assigner"
    )
    parser.add_argument(
        "--unit",
        type=str,
        help="Unit name to assign BR for"
    )
    parser.add_argument(
        "--points",
        type=int,
        help="Points cost of unit"
    )
    parser.add_argument(
        "--experience",
        type=str,
        default="r",
        choices=['i', 'r', 'v', 'e'],
        help="Experience level (i/r/v/e)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate assigner against all data"
    )

    args = parser.parse_args()

    assigner = BattleRatingAssigner()

    if args.validate:
        print("\nValidating Battle Rating Assigner...")
        print("=" * 60)

        results = assigner.validate()

        total = results['total']
        exact = results['exact_match']
        within_1 = results['within_1']

        accuracy_exact = (exact / total * 100) if total > 0 else 0
        accuracy_within_1 = (within_1 / total * 100) if total > 0 else 0

        print(f"\nTotal units tested: {total}")
        print(f"Exact match: {exact} ({accuracy_exact:.1f}%)")
        print(f"Within 1 BR: {within_1} ({accuracy_within_1:.1f}%)")
        print(f"Within 2 BR: {results['within_2']} ({results['within_2']/total*100:.1f}%)")
        print(f"Within 3 BR: {results['within_3']} ({results['within_3']/total*100:.1f}%)")
        print()

        if accuracy_exact >= 90:
            print(f"[SUCCESS] Exact match accuracy: {accuracy_exact:.1f}% (target: 90%)")
        else:
            print(f"[INFO] Exact match: {accuracy_exact:.1f}%, Within ±1: {accuracy_within_1:.1f}%")

            if results['errors']:
                print(f"\nLargest errors (showing first 10):")
                for err in sorted(results['errors'], key=lambda x: x['diff'], reverse=True)[:10]:
                    print(f"  {err['name']:45} Actual:{err['actual']:2} Predicted:{err['predicted']:2} Diff:{err['diff']:+2} ({err['method']})")

    elif args.unit:
        assignment = assigner.assign_br(
            unit_name=args.unit,
            points_cost=args.points,
            experience=args.experience
        )

        print(f"\nBattle Rating Assignment for: {args.unit}")
        print("=" * 60)
        print(f"Experience: {args.experience}")
        if args.points:
            print(f"Points cost: {args.points}")
        print()
        print(f"Base BR: {assignment.base_br}")
        print(f"Size modifier: {assignment.size_modifier}")
        print(f"Importance modifier: {assignment.importance_modifier}")
        print()
        print(f"Final BR: {assignment.final_br}")
        print(f"Confidence: {assignment.confidence}")
        print(f"Method: {assignment.method}")

    else:
        parser.print_help()

    assigner.close()


if __name__ == "__main__":
    main()
