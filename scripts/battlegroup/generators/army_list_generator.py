#!/usr/bin/env python3
"""
Phase 9B Step 5 Part 6: Enhanced Army List Generator
Generates BattleGroup force selection lists from Phase 6 unit data.

Integrates Phase6UnitParser to extract equipment from historical unit JSONs.
Organizes by force structure (HQ, Infantry, Armor, Artillery, AT, AA, Recon, Support).
Applies historical restrictions (date-based availability, rarity enforcement).

Usage:
    python army_list_generator.py --nation german --quarter 1941q2
    python army_list_generator.py --nation british --quarter 1942q3 --print
    python army_list_generator.py --nation american --quarter 1943q1 --output custom.txt
"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Import Phase 6 unit parser
from scripts.battlegroup.generators.phase6_unit_parser import Phase6UnitParser, MappedEquipment

DATABASE_PATH = project_root / "database" / "master_database.db"
TEMPLATE_DIR = project_root / "scripts" / "battlegroup" / "templates"
OUTPUT_DIR = project_root / "data" / "output" / "battlegroup" / "army_lists"


class ArmyListGenerator:
    """Generate BattleGroup army lists with Phase 6 integration."""

    NATION_NAMES = {
        'german': 'German',
        'british': 'British & Commonwealth',
        'american': 'American',
        'italian': 'Italian',
        'french': 'Free French'
    }

    # Force organization categories
    CATEGORY_MAPPINGS = {
        'tanks': 'ARMOR',
        'halftracks': 'INFANTRY',
        'armored_cars': 'RECONNAISSANCE',
        'trucks': 'SUPPORT',
        'field_artillery': 'ARTILLERY',
        'anti_tank_guns': 'ANTI-TANK',
        'anti_aircraft_guns': 'ANTI-AIRCRAFT',
        'mortars': 'INFANTRY',
        'small_arms': 'INFANTRY',
        'engineer_equipment': 'SUPPORT'
    }

    # Rarity levels (from BattleGroup rules)
    RARITY_LEVELS = {
        'UNLIMITED': '',  # No marker
        'LIMITED': '[Limited]',
        'RESTRICTED': '[Restricted]',
        'UNIQUE': '[Unique]'
    }

    def __init__(self):
        """Initialize generator with database connection and Phase 6 parser."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.phase6_parser = Phase6UnitParser()

        # Load force list template
        template_path = TEMPLATE_DIR / "force_list.txt"
        with open(template_path, 'r') as f:
            self.force_list_template = f.read()

    def get_phase6_equipment_for_quarter(
        self,
        nation: str,
        quarter: str
    ) -> Dict[str, List[MappedEquipment]]:
        """
        Get equipment from Phase 6 units, organized by category.

        Args:
            nation: Nation code (e.g., 'german')
            quarter: Quarter code (e.g., '1941q2')

        Returns:
            Dict mapping force categories to equipment lists
        """
        # Get all units for this quarter
        units = self.phase6_parser.get_units_for_quarter(nation, quarter)

        if not units:
            print(f"  [WARNING] No Phase 6 units found for {nation} {quarter}")
            return {}

        # Extract all equipment from all units
        all_equipment = []
        for unit in units:
            equipment_list = self.phase6_parser.extract_equipment_from_unit(unit)
            all_equipment.extend(equipment_list)

        # Organize by force category
        categorized = {
            'HQ': [],
            'INFANTRY': [],
            'ARMOR': [],
            'ARTILLERY': [],
            'ANTI-TANK': [],
            'ANTI-AIRCRAFT': [],
            'RECONNAISSANCE': [],
            'SUPPORT': []
        }

        for equipment in all_equipment:
            category = self.CATEGORY_MAPPINGS.get(equipment.category, 'SUPPORT')
            categorized[category].append(equipment)

        # Remove duplicates and sort by points
        for category in categorized:
            seen = set()
            unique = []
            for item in categorized[category]:
                if item.canonical_id not in seen:
                    seen.add(item.canonical_id)
                    unique.append(item)
            # Sort by points (ascending)
            categorized[category] = sorted(unique, key=lambda x: x.points_regular)

        return categorized

    def get_rarity(self, equipment_name: str) -> str:
        """
        Determine rarity level for equipment.

        Args:
            equipment_name: Equipment display name

        Returns:
            Rarity level string
        """
        # Simple heuristic (can be enhanced with database lookups)
        name_lower = equipment_name.lower()

        # Unique (very rare or special variants)
        if any(keyword in name_lower for keyword in ['command', 'ace', 'prototype']):
            return 'UNIQUE'

        # Restricted (heavy tanks, rare vehicles)
        if any(keyword in name_lower for keyword in ['tiger', 'panther', 'churchill', 'kv-', 'pershing']):
            return 'RESTRICTED'

        # Limited (mid-range equipment)
        if any(keyword in name_lower for keyword in ['sherman', 'pz.iv', 'crusader', 'grant']):
            return 'LIMITED'

        # Unlimited (common equipment)
        return 'UNLIMITED'

    def format_equipment_line(self, equipment: MappedEquipment) -> str:
        """
        Format equipment as army list line with rarity indicator.

        Args:
            equipment: MappedEquipment object

        Returns:
            Formatted string
        """
        name = equipment.name
        points = equipment.points_regular
        br = equipment.br_regular
        rarity = self.get_rarity(name)
        rarity_marker = self.RARITY_LEVELS[rarity]

        if rarity_marker:
            return f"  □ {name:38s} {rarity_marker:12s} {points:3d} pts, {br:2d} BR"
        else:
            return f"  □ {name:52s} {points:3d} pts, {br:2d} BR"

    def generate_army_list(
        self,
        nation: str,
        quarter: str,
        battle: str = None,
        date: str = None
    ) -> str:
        """
        Generate army list for nation and quarter using Phase 6 data.

        Args:
            nation: Nation code (e.g., 'german')
            quarter: Quarter code (e.g., '1941q2')
            battle: Optional battle name
            date: Optional date override

        Returns:
            Formatted army list text
        """

        print(f"\nGenerating army list for {self.NATION_NAMES.get(nation, nation)} ({quarter})...")

        # Get equipment from Phase 6 units
        categorized_equipment = self.get_phase6_equipment_for_quarter(nation, quarter)

        if not categorized_equipment:
            print("  [ERROR] No equipment found - falling back to generic list")
            return self._generate_fallback_list(nation, quarter)

        # Auto-generate battle name and date from quarter if not provided
        if not battle:
            battle = f"{quarter.upper()} Operations"
        if not date:
            # Parse quarter (e.g., '1941q2' -> 'April-June 1941')
            year = quarter[:4]
            q = quarter[5]
            quarters_map = {'1': 'Jan-Mar', '2': 'Apr-Jun', '3': 'Jul-Sep', '4': 'Oct-Dec'}
            date = f"{quarters_map.get(q, 'Unknown')} {year}"

        # Format headquarters section
        headquarters_section = "  □ Divisional HQ ................................. 45 pts, 10 BR"

        # Format core units (Infantry + Armor)
        core_lines = []
        if categorized_equipment.get('INFANTRY'):
            core_lines.append("\n--- Infantry ---")
            for item in categorized_equipment['INFANTRY'][:15]:
                core_lines.append(self.format_equipment_line(item))

        if categorized_equipment.get('ARMOR'):
            core_lines.append("\n--- Armor ---")
            for item in categorized_equipment['ARMOR'][:15]:
                core_lines.append(self.format_equipment_line(item))

        core_section = "\n".join(core_lines) if core_lines else "  (No core units available)"

        # Format support units (Artillery, AT, AA, Recon, Support)
        support_lines = []

        if categorized_equipment.get('ARTILLERY'):
            support_lines.append("\n--- Artillery ---")
            for item in categorized_equipment['ARTILLERY'][:10]:
                support_lines.append(self.format_equipment_line(item))

        if categorized_equipment.get('ANTI-TANK'):
            support_lines.append("\n--- Anti-Tank ---")
            for item in categorized_equipment['ANTI-TANK'][:10]:
                support_lines.append(self.format_equipment_line(item))

        if categorized_equipment.get('ANTI-AIRCRAFT'):
            support_lines.append("\n--- Anti-Aircraft ---")
            for item in categorized_equipment['ANTI-AIRCRAFT'][:8]:
                support_lines.append(self.format_equipment_line(item))

        if categorized_equipment.get('RECONNAISSANCE'):
            support_lines.append("\n--- Reconnaissance ---")
            for item in categorized_equipment['RECONNAISSANCE'][:10]:
                support_lines.append(self.format_equipment_line(item))

        if categorized_equipment.get('SUPPORT'):
            support_lines.append("\n--- Support ---")
            for item in categorized_equipment['SUPPORT'][:10]:
                support_lines.append(self.format_equipment_line(item))

        support_section = "\n".join(support_lines) if support_lines else "  (No support units available)"

        # Fire support (generic for now)
        fire_support_section = """  □ 1st Target Priority (3+) ................. 20 pts, 0 BR
  □ 2nd Target Priority (4+) ................. 10 pts, 0 BR
  □ Timed Artillery Barrage .................. 20 pts, 0 BR"""

        # Generate restrictions with rarity rules
        restrictions = self._generate_restrictions(nation, quarter)

        # Fill template
        title = f"{self.NATION_NAMES.get(nation, nation).upper()} FORCE LIST"

        army_list = self.force_list_template.format(
            title=title,
            battle=battle,
            date=date,
            nation=self.NATION_NAMES.get(nation, nation),
            headquarters_section=headquarters_section,
            min_core=2,
            max_core=6,
            core_section=core_section,
            max_support=4,
            support_section=support_section,
            max_fire_support=2,
            fire_support_section=fire_support_section,
            restrictions=restrictions
        )

        return army_list

    def _generate_restrictions(self, nation: str, quarter: str) -> str:
        """Generate historical restrictions for force composition."""
        year = int(quarter[:4])
        q = int(quarter[5])

        restrictions = []
        restrictions.append("COMPOSITION RULES:")
        restrictions.append("- Minimum 1 HQ unit (required)")
        restrictions.append("- Infantry/Armor core: 2-6 units")
        restrictions.append("- Support units: Maximum 4 units")
        restrictions.append("- Support may not exceed 50% of total points")
        restrictions.append("")

        restrictions.append("RARITY RESTRICTIONS:")
        restrictions.append("- [Unique]: Maximum 0-1 per force")
        restrictions.append("- [Restricted]: Maximum 0-1 per force")
        restrictions.append("- [Limited]: No specific limit")
        restrictions.append("- No marker = Unlimited")
        restrictions.append("")

        restrictions.append("HISTORICAL NOTES:")
        if year == 1940:
            restrictions.append("- Early war equipment only")
            restrictions.append("- Limited tank availability")
        elif year == 1941:
            restrictions.append("- Transitional period equipment")
            restrictions.append("- Mix of pre-war and new models")
        elif year == 1942:
            restrictions.append("- Mid-war equipment becoming standard")
            restrictions.append("- Lend-lease equipment appearing (British/Soviet)")
        elif year >= 1943:
            restrictions.append("- Late-war equipment available")
            restrictions.append("- Heavy tanks and advanced variants")

        restrictions.append("")
        restrictions.append("Generated from Phase 6 unit data (historical TO&E)")

        return "\n".join(restrictions)

    def _generate_fallback_list(self, nation: str, quarter: str) -> str:
        """Generate fallback list when no Phase 6 data available."""
        return f"""
{self.NATION_NAMES.get(nation, nation).upper()} FORCE LIST

Quarter: {quarter}
Status: NO PHASE 6 DATA AVAILABLE

This quarter/nation combination has no extracted unit data yet.
Please check that Phase 6 extraction has been completed for this period.
"""

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
        description="Phase 9B Step 5 Part 6: Enhanced Army List Generator with Phase 6 Integration"
    )
    parser.add_argument(
        "--nation",
        choices=['german', 'british', 'american', 'italian', 'french'],
        required=True,
        help="Nation for army list"
    )
    parser.add_argument(
        "--quarter",
        required=True,
        help="Quarter code (e.g., '1941q2', '1942q3')"
    )
    parser.add_argument(
        "--battle",
        help="Optional battle name (auto-generated if not provided)"
    )
    parser.add_argument(
        "--date",
        help="Optional date override (auto-generated if not provided)"
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
            args.quarter,
            args.battle,
            args.date
        )

        # Save to file
        if args.output:
            generator.save_army_list(army_list, args.output)
        else:
            # Default output path
            default_output = OUTPUT_DIR / f"{args.nation}_{args.quarter}_force_list.txt"
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
