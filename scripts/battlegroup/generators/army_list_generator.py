#!/usr/bin/env python3
"""
Phase 9B Step 4: Army List Generator
Generates BattleGroup force selection lists from equipment database.

This is a simplified implementation for Step 4 demonstration.
Full implementation requires Phase 6 unit JSON integration.

Usage:
    python army_list_generator.py --nation german --battle kursk
    python army_list_generator.py --nation british --date 1942-06
"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"
TEMPLATE_DIR = project_root / "scripts" / "battlegroup" / "templates"
OUTPUT_DIR = project_root / "data" / "output" / "battlegroup" / "army_lists"


class ArmyListGenerator:
    """Generate BattleGroup army lists."""

    NATION_NAMES = {
        'german': 'German',
        'british': 'British',
        'american': 'American',
        'italian': 'Italian',
        'french': 'Free French'
    }

    def __init__(self):
        """Initialize generator with database connection."""
        self.conn = sqlite3.connect(DATABASE_PATH)

        # Load force list template
        template_path = TEMPLATE_DIR / "force_list.txt"
        with open(template_path, 'r') as f:
            self.force_list_template = f.read()

    def get_equipment_by_nation(
        self,
        nation: str,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Get equipment for a nation.

        Args:
            nation: Nation code
            category: Optional category filter

        Returns:
            List of equipment dicts with BattleGroup stats
        """
        cursor = self.conn.cursor()

        query = """
            SELECT
                e.name, e.equipment_type, e.category,
                eb.points_regular, eb.battle_rating_regular,
                eb.armor_front, eb.off_road_movement
            FROM equipment e
            JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            WHERE e.nation = ?
        """
        params = [nation]

        if category:
            query += " AND e.category = ?"
            params.append(category)

        query += " ORDER BY e.equipment_type, eb.points_regular"

        cursor.execute(query, params)

        columns = ['name', 'equipment_type', 'category', 'points', 'br', 'armor', 'movement']
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def format_equipment_line(self, equipment: Dict) -> str:
        """Format equipment as army list line."""
        name = equipment['name']
        points = equipment['points']
        br = equipment['br']
        return f"  □ {name:40s} {points:3d} pts, {br:2d} BR"

    def generate_army_list(
        self,
        nation: str,
        battle: str = "Generic",
        date: str = "1940-1943"
    ) -> str:
        """
        Generate army list for nation.

        Args:
            nation: Nation code
            battle: Battle name
            date: Battle date

        Returns:
            Formatted army list text
        """

        print(f"\nGenerating army list for {self.NATION_NAMES.get(nation, nation)}...")

        # Get equipment by category
        tanks = self.get_equipment_by_nation(nation, 'tanks')
        halftracks = self.get_equipment_by_nation(nation, 'halftracks')
        artillery = self.get_equipment_by_nation(nation, 'field_artillery')
        at_guns = self.get_equipment_by_nation(nation, 'anti_tank_guns')

        # Format sections
        headquarters_section = self.format_equipment_line({
            'name': 'Divisional HQ',
            'points': 45,
            'br': 10
        })

        # Core units (tanks/infantry)
        core_lines = []
        if tanks:
            core_lines.append("\n--- Armor ---")
            for tank in tanks[:10]:  # Limit to 10 for demo
                core_lines.append(self.format_equipment_line(tank))
        core_section = "\n".join(core_lines) if core_lines else "  (No core units found in database)"

        # Support units (artillery, AT guns)
        support_lines = []
        if artillery:
            support_lines.append("\n--- Artillery ---")
            for gun in artillery[:5]:
                support_lines.append(self.format_equipment_line(gun))
        if at_guns:
            support_lines.append("\n--- Anti-Tank ---")
            for gun in at_guns[:5]:
                support_lines.append(self.format_equipment_line(gun))
        support_section = "\n".join(support_lines) if support_lines else "  (No support units found in database)"

        # Fire support (simplified)
        fire_support_section = """  □ 1st Target Priority (3+) ................. 20 pts, 0 BR
  □ 2nd Target Priority (4+) ................. 10 pts, 0 BR
  □ Timed 105mm Barrage ...................... 20 pts, 0 BR"""

        # Restrictions (generic)
        restrictions = """- Minimum 40% of points in infantry (not yet implemented)
- Date restrictions apply for late-war equipment
- Maximum 1 heavy tank per company (if applicable)

NOTE: This is a simplified demonstration army list.
Full implementation requires Phase 6 unit JSON integration."""

        # Fill template
        title = f"{self.NATION_NAMES.get(nation, nation).upper()} FORCE LIST"

        army_list = self.force_list_template.format(
            title=title,
            battle=battle,
            date=date,
            nation=self.NATION_NAMES.get(nation, nation),
            headquarters_section=headquarters_section,
            min_core=1,
            max_core=4,
            core_section=core_section,
            max_support=3,
            support_section=support_section,
            max_fire_support=2,
            fire_support_section=fire_support_section,
            restrictions=restrictions
        )

        return army_list

    def save_army_list(
        self,
        army_list: str,
        output_file: Path
    ):
        """Save army list to file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(army_list)
        print(f"  [OK] Saved to: {output_file}")

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution function."""

    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 4: Army List Generator (Simplified Demo)"
    )
    parser.add_argument(
        "--nation",
        choices=['german', 'british', 'american', 'italian', 'french'],
        required=True,
        help="Nation for army list"
    )
    parser.add_argument(
        "--battle",
        default="Generic",
        help="Battle name"
    )
    parser.add_argument(
        "--date",
        default="1940-1943",
        help="Battle date"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path"
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print army list to console"
    )

    args = parser.parse_args()

    generator = ArmyListGenerator()

    try:
        # Generate army list
        army_list = generator.generate_army_list(
            args.nation,
            args.battle,
            args.date
        )

        # Save to file
        if args.output:
            generator.save_army_list(army_list, args.output)
        else:
            # Default output path
            default_output = OUTPUT_DIR / f"{args.nation}_{args.battle.lower().replace(' ', '_')}.txt"
            generator.save_army_list(army_list, default_output)

        # Print if requested
        if args.print:
            print()
            print(army_list)

    finally:
        generator.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
