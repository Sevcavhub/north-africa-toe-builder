#!/usr/bin/env python3
"""
Phase 9B Step 5 Part 3: Force Roster Builder (Complete Implementation)
Builds complete force rosters with selection tracking, budget management, and validation.

Usage:
    python force_roster_builder_v2.py --interactive
    python force_roster_builder_v2.py --load roster.json --validate
    python force_roster_builder_v2.py --nation german --battle kursk --points 1000
"""

import sqlite3
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"
TEMPLATE_DIR = project_root / "scripts" / "battlegroup" / "templates"
OUTPUT_DIR = project_root / "data" / "output" / "battlegroup" / "rosters"


class Rarity(Enum):
    """Equipment rarity levels."""
    UNLIMITED = "unlimited"
    LIMITED = "limited"
    RESTRICTED = "restricted"
    UNIQUE = "unique"


class UnitCategory(Enum):
    """Unit category for composition rules."""
    HQ = "hq"
    INFANTRY = "infantry"
    ARMOR = "armor"
    ARTILLERY = "artillery"
    ANTI_TANK = "anti_tank"
    ANTI_AIRCRAFT = "anti_aircraft"
    RECONNAISSANCE = "reconnaissance"
    ENGINEER = "engineer"
    SUPPORT = "support"


@dataclass
class RosterUnit:
    """Represents a unit in the roster."""
    equipment_id: str
    equipment_name: str
    nation: str
    equipment_type: str
    experience: str
    points: int
    battle_rating: int
    category: str
    rarity: str
    quantity: int = 1
    notes: str = ""

    def total_points(self) -> int:
        """Calculate total points for this unit."""
        return self.points * self.quantity

    def total_br(self) -> int:
        """Calculate total BR for this unit."""
        return self.battle_rating * self.quantity


class ForceRoster:
    """Represents a complete force roster."""

    def __init__(
        self,
        name: str,
        nation: str,
        battle: str,
        points_budget: int,
        date: Optional[str] = None
    ):
        """
        Initialize force roster.

        Args:
            name: Force name
            nation: Nation
            battle: Battle/campaign name
            points_budget: Points budget for force
            date: Optional date (YYYY-MM format)
        """
        self.name = name
        self.nation = nation
        self.battle = battle
        self.points_budget = points_budget
        self.date = date
        self.units: List[RosterUnit] = []

    def add_unit(self, unit: RosterUnit) -> Tuple[bool, str]:
        """
        Add unit to roster with validation.

        Args:
            unit: Unit to add

        Returns:
            Tuple of (success, message)
        """
        # Validate points budget
        current_points = self.total_points()
        new_total = current_points + unit.total_points()

        if new_total > self.points_budget:
            return False, f"Exceeds points budget: {new_total}/{self.points_budget}"

        # Validate rarity
        rarity_valid, rarity_msg = self._validate_rarity(unit)
        if not rarity_valid:
            return False, rarity_msg

        # Add unit
        self.units.append(unit)
        return True, f"Added {unit.equipment_name} ({unit.total_points()} pts, {unit.total_br()} BR)"

    def remove_unit(self, index: int) -> Tuple[bool, str]:
        """
        Remove unit from roster by index.

        Args:
            index: Unit index

        Returns:
            Tuple of (success, message)
        """
        if 0 <= index < len(self.units):
            unit = self.units.pop(index)
            return True, f"Removed {unit.equipment_name}"
        return False, "Invalid unit index"

    def _validate_rarity(self, unit: RosterUnit) -> Tuple[bool, str]:
        """
        Validate rarity restrictions.

        Args:
            unit: Unit to validate

        Returns:
            Tuple of (valid, message)
        """
        if unit.rarity == Rarity.UNIQUE.value:
            # Check if already in roster
            existing = [u for u in self.units if u.equipment_id == unit.equipment_id]
            if existing:
                return False, f"{unit.equipment_name} is Unique (max 0-1)"

        elif unit.rarity == Rarity.RESTRICTED.value:
            # Check if already in roster
            existing = [u for u in self.units if u.equipment_id == unit.equipment_id]
            if existing:
                return False, f"{unit.equipment_name} is Restricted (max 0-1)"

        return True, "OK"

    def validate_composition(self) -> Tuple[bool, List[str]]:
        """
        Validate force composition rules.

        Returns:
            Tuple of (valid, list of issues)
        """
        issues = []

        # Check HQ requirement
        hq_units = [u for u in self.units if u.category == UnitCategory.HQ.value]
        if not hq_units:
            issues.append("⚠️ Force must include at least 1 HQ unit")

        # Check support restrictions (max 50% of points)
        support_units = [u for u in self.units if u.category == UnitCategory.SUPPORT.value]
        support_points = sum(u.total_points() for u in support_units)
        total_points = self.total_points()

        if total_points > 0 and support_points > (total_points * 0.5):
            issues.append(f"⚠️ Support units exceed 50% of force ({support_points}/{total_points} pts)")

        # Check points budget
        if total_points > self.points_budget:
            issues.append(f"❌ Force exceeds points budget ({total_points}/{self.points_budget})")

        return len(issues) == 0, issues

    def total_points(self) -> int:
        """Calculate total points."""
        return sum(u.total_points() for u in self.units)

    def total_br(self) -> int:
        """Calculate total battle rating."""
        return sum(u.total_br() for u in self.units)

    def points_remaining(self) -> int:
        """Calculate remaining points."""
        return self.points_budget - self.total_points()

    def to_text(self) -> str:
        """
        Format roster as text.

        Returns:
            Formatted text roster
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"BATTLEGROUP FORCE ROSTER: {self.name.upper()}")
        lines.append("=" * 70)
        lines.append(f"Nation: {self.nation.title()}")
        lines.append(f"Battle: {self.battle}")
        if self.date:
            lines.append(f"Date: {self.date}")
        lines.append(f"Points Budget: {self.points_budget}")
        lines.append("")

        # Group units by category
        categories = {}
        for unit in self.units:
            cat = unit.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(unit)

        # Display by category
        for category in [UnitCategory.HQ, UnitCategory.INFANTRY, UnitCategory.ARMOR,
                         UnitCategory.ARTILLERY, UnitCategory.ANTI_TANK,
                         UnitCategory.ANTI_AIRCRAFT, UnitCategory.RECONNAISSANCE,
                         UnitCategory.ENGINEER, UnitCategory.SUPPORT]:

            cat_units = categories.get(category.value, [])
            if not cat_units:
                continue

            lines.append(f"--- {category.value.upper().replace('_', ' ')} ---")
            for unit in cat_units:
                qty_str = f" x{unit.quantity}" if unit.quantity > 1 else ""
                lines.append(f"  • {unit.equipment_name}{qty_str}")
                lines.append(f"    Experience: {unit.experience.title()}")
                lines.append(f"    Points: {unit.total_points()} ({unit.points} each)")
                lines.append(f"    Battle Rating: {unit.total_br()} ({unit.battle_rating} each)")
                if unit.rarity != Rarity.UNLIMITED.value:
                    lines.append(f"    Rarity: {unit.rarity.title()}")
                if unit.notes:
                    lines.append(f"    Notes: {unit.notes}")
                lines.append("")

        # Totals
        lines.append("=" * 70)
        lines.append(f"TOTAL POINTS: {self.total_points()} / {self.points_budget}")
        lines.append(f"POINTS REMAINING: {self.points_remaining()}")
        lines.append(f"TOTAL BATTLE RATING: {self.total_br()}")
        lines.append("=" * 70)

        # Validation
        valid, issues = self.validate_composition()
        if valid:
            lines.append("✅ Force composition is VALID")
        else:
            lines.append("❌ Force composition has ISSUES:")
            for issue in issues:
                lines.append(f"   {issue}")

        lines.append("=" * 70)

        return "\n".join(lines)

    def to_json(self) -> str:
        """
        Export roster as JSON.

        Returns:
            JSON string
        """
        data = {
            'name': self.name,
            'nation': self.nation,
            'battle': self.battle,
            'points_budget': self.points_budget,
            'date': self.date,
            'units': [asdict(u) for u in self.units],
            'totals': {
                'points': self.total_points(),
                'battle_rating': self.total_br(),
                'points_remaining': self.points_remaining()
            },
            'validation': {
                'valid': self.validate_composition()[0],
                'issues': self.validate_composition()[1]
            }
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'ForceRoster':
        """
        Load roster from JSON.

        Args:
            json_str: JSON string

        Returns:
            ForceRoster instance
        """
        data = json.loads(json_str)
        roster = cls(
            data['name'],
            data['nation'],
            data['battle'],
            data['points_budget'],
            data.get('date')
        )

        for unit_data in data['units']:
            unit = RosterUnit(**unit_data)
            roster.units.append(unit)

        return roster


class ForceRosterBuilder:
    """Build force rosters with database integration."""

    def __init__(self):
        """Initialize builder with database connection."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def get_available_equipment(
        self,
        nation: str,
        category: Optional[str] = None,
        experience: str = 'r'
    ) -> List[Dict]:
        """
        Get available equipment for nation.

        Args:
            nation: Nation
            category: Optional equipment category filter
            experience: Experience level

        Returns:
            List of equipment dicts
        """
        cursor = self.conn.cursor()

        # Build query
        query = """
            SELECT
                e.canonical_id, e.name, e.nation, e.equipment_type,
                eb.points_regular, eb.points_inexperienced,
                eb.points_veteran, eb.points_elite,
                eb.battle_rating_regular, eb.battle_rating_inexperienced,
                eb.battle_rating_veteran, eb.battle_rating_elite
            FROM equipment e
            JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            WHERE e.nation = ?
        """
        params = [nation]

        if category:
            query += " AND e.equipment_type = ?"
            params.append(category)

        query += " ORDER BY e.name"

        cursor.execute(query, params)

        equipment_list = []
        for row in cursor.fetchall():
            # Get experience-specific values
            if experience == 'i':
                points = row['points_inexperienced']
                br = row['battle_rating_inexperienced']
            elif experience == 'v':
                points = row['points_veteran']
                br = row['battle_rating_veteran']
            elif experience == 'e':
                points = row['points_elite']
                br = row['battle_rating_elite']
            else:
                points = row['points_regular']
                br = row['battle_rating_regular']

            equipment_list.append({
                'canonical_id': row['canonical_id'],
                'name': row['name'],
                'nation': row['nation'],
                'equipment_type': row['equipment_type'],
                'points': points,
                'battle_rating': br
            })

        return equipment_list

    def create_unit_from_equipment(
        self,
        equipment: Dict,
        experience: str = 'r',
        quantity: int = 1,
        category: str = UnitCategory.SUPPORT.value,
        rarity: str = Rarity.UNLIMITED.value
    ) -> RosterUnit:
        """
        Create RosterUnit from equipment data.

        Args:
            equipment: Equipment dict
            experience: Experience level
            quantity: Quantity
            category: Unit category
            rarity: Rarity level

        Returns:
            RosterUnit instance
        """
        return RosterUnit(
            equipment_id=equipment['canonical_id'],
            equipment_name=equipment['name'],
            nation=equipment['nation'],
            equipment_type=equipment['equipment_type'],
            experience=experience,
            points=equipment['points'],
            battle_rating=equipment['battle_rating'],
            category=category,
            rarity=rarity,
            quantity=quantity
        )

    def close(self):
        """Close database connection."""
        self.conn.close()


def safe_print(text: str):
    """Print text with ASCII fallback for Windows console."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


def interactive_mode(builder: ForceRosterBuilder):
    """Interactive roster building mode."""
    safe_print("\n=== BATTLEGROUP FORCE ROSTER BUILDER ===\n")

    # Get basic info
    name = input("Force name: ")
    nation = input("Nation (german/british/american/italian/french): ").lower()
    battle = input("Battle: ")
    points_budget = int(input("Points budget: "))

    # Create roster
    roster = ForceRoster(name, nation, battle, points_budget)

    # Interactive loop
    while True:
        safe_print("\n" + "=" * 70)
        safe_print(f"Current: {roster.total_points()}/{roster.points_budget} pts, {roster.total_br()} BR")
        safe_print(f"Remaining: {roster.points_remaining()} pts")
        safe_print("=" * 70)

        safe_print("\nOptions:")
        safe_print("  1. Add unit")
        safe_print("  2. Remove unit")
        safe_print("  3. View roster")
        safe_print("  4. Validate roster")
        safe_print("  5. Save roster")
        safe_print("  6. Exit")

        choice = input("\nChoice: ").strip()

        if choice == '1':
            # Add unit
            experience = input("Experience (i/r/v/e) [r]: ").strip() or 'r'
            equipment_list = builder.get_available_equipment(nation, experience=experience)

            safe_print(f"\nAvailable equipment ({len(equipment_list)} items):")
            for i, eq in enumerate(equipment_list[:20]):  # Show first 20
                safe_print(f"  {i+1}. {eq['name']} ({eq['points']} pts, {eq['battle_rating']} BR)")

            if len(equipment_list) > 20:
                safe_print(f"  ... and {len(equipment_list) - 20} more")

            eq_idx = int(input("\nSelect equipment number: ")) - 1
            if 0 <= eq_idx < len(equipment_list):
                equipment = equipment_list[eq_idx]

                quantity = int(input("Quantity [1]: ") or "1")
                category = input(f"Category ({', '.join([c.value for c in UnitCategory])}) [support]: ") or "support"
                rarity = input(f"Rarity ({', '.join([r.value for r in Rarity])}) [unlimited]: ") or "unlimited"

                unit = builder.create_unit_from_equipment(
                    equipment, experience, quantity, category, rarity
                )

                success, msg = roster.add_unit(unit)
                if success:
                    safe_print(f"✅ {msg}")
                else:
                    safe_print(f"❌ {msg}")

        elif choice == '2':
            # Remove unit
            if not roster.units:
                safe_print("❌ No units to remove")
                continue

            safe_print("\nCurrent units:")
            for i, unit in enumerate(roster.units):
                safe_print(f"  {i+1}. {unit.equipment_name} ({unit.total_points()} pts)")

            unit_idx = int(input("\nRemove unit number: ")) - 1
            success, msg = roster.remove_unit(unit_idx)
            if success:
                safe_print(f"✅ {msg}")
            else:
                safe_print(f"❌ {msg}")

        elif choice == '3':
            # View roster
            safe_print("\n" + roster.to_text())

        elif choice == '4':
            # Validate
            valid, issues = roster.validate_composition()
            if valid:
                safe_print("✅ Force composition is VALID")
            else:
                safe_print("❌ Force composition has ISSUES:")
                for issue in issues:
                    safe_print(f"   {issue}")

        elif choice == '5':
            # Save
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            safe_name = name.replace('/', '_').replace('\\', '_').replace(':', '_')

            # Save text
            text_path = OUTPUT_DIR / f"{safe_name}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(roster.to_text())
            safe_print(f"✅ Saved text roster: {text_path}")

            # Save JSON
            json_path = OUTPUT_DIR / f"{safe_name}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(roster.to_json())
            safe_print(f"✅ Saved JSON roster: {json_path}")

        elif choice == '6':
            # Exit
            safe_print("\nExiting...")
            break

        else:
            safe_print("❌ Invalid choice")


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Phase 9B Step 5: Force Roster Builder")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--load", type=Path, help="Load roster from JSON file")
    parser.add_argument("--validate", action="store_true", help="Validate loaded roster")
    parser.add_argument("--nation", help="Nation for roster")
    parser.add_argument("--battle", help="Battle for roster")
    parser.add_argument("--points", type=int, help="Points budget")

    args = parser.parse_args()

    builder = ForceRosterBuilder()

    try:
        if args.interactive:
            interactive_mode(builder)

        elif args.load:
            # Load and display roster
            with open(args.load, 'r', encoding='utf-8') as f:
                json_str = f.read()

            roster = ForceRoster.from_json(json_str)
            safe_print(roster.to_text())

            if args.validate:
                valid, issues = roster.validate_composition()
                if valid:
                    safe_print("\n✅ Roster is VALID")
                    return 0
                else:
                    safe_print("\n❌ Roster has issues")
                    return 1

        elif args.nation and args.battle and args.points:
            # Create basic roster
            roster = ForceRoster(f"{args.nation.title()} Force", args.nation, args.battle, args.points)
            safe_print(roster.to_text())

        else:
            parser.print_help()
            return 1

    finally:
        builder.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
