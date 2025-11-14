#!/usr/bin/env python3
"""
Phase 9B: Generate Datacards ONLY from Equipment in Scenarios

This script generates datacards by parsing scenario markdown files,
extracting equipment names from the FORCES sections, and creating
datacards only for equipment actually used in those specific scenarios.

This fixes the issue where datacards were being generated for ALL
equipment in a quarter, regardless of whether it appeared in scenarios.

Usage:
    python generate_book_datacards_from_scenarios.py --battle tobruk
    python generate_book_datacards_from_scenarios.py --all
"""

import sqlite3
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Import the existing V5.5 generator's datacard generation logic
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.battlegroup.book.generate_book_datacards_v5_5 import BookDatacardGenerator, BATTLES

DATABASE_PATH = Path(__file__).resolve().parents[3] / "database" / "master_database.db"
BOOKS_BASE = Path(__file__).resolve().parents[3] / "books"


class ScenarioBasedDatacardGenerator(BookDatacardGenerator):
    """Generate datacards based ONLY on equipment in scenario files."""

    def parse_scenario_equipment(self, scenario_path: Path) -> Set[str]:
        """
        Parse a scenario markdown file and extract equipment names.

        Returns:
            Set of equipment names (not IDs) found in scenario
        """
        equipment_names = set()

        if not scenario_path.exists():
            print(f"[WARNING] Scenario not found: {scenario_path}")
            return equipment_names

        with open(scenario_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract equipment from unit lines like:
        # - "8x Matilda II (veteran) - 400 pts, BR: 2"
        # - "4x 88mm FlaK 18/36 (veteran) - 200 pts, BR: 1"
        # - "2x Infantry Platoon (veteran) - 620 pts, BR: 2"

        # Pattern: number + 'x' + equipment name + optional experience + optional stats
        # Match: "- 8x Matilda II (veteran)" or "- 2x 25-pdr (veteran)"
        # Capture equipment name until we hit experience level in parentheses
        unit_pattern = r'-\s+\d+x\s+([A-Za-z0-9][\w\s\-/.,]+?)\s*\((?:veteran|regular|elite|inexperienced)\)'

        matches = re.findall(unit_pattern, content, re.IGNORECASE)

        for equipment_name in matches:
            # Clean up equipment name
            equipment_name = equipment_name.strip()

            # Skip generic unit types (we want specific equipment only)
            skip_terms = [
                'infantry platoon', 'infantry company', 'infantry section', 'infantry',
                'motorized infantry', 'british infantry', 'german infantry', 'italian infantry',
                'rifle platoon', 'rifle section', 'rifle company',
                'panzergrenadier', 'grenadier', 'bersaglieri',
                'engineers', 'engineer platoon', 'reconnaissance',
                'command section', 'hq section', 'artillery observer',
                'forward observer', 'spotter', 'staff team'
            ]

            # Check if it's a generic unit type
            is_generic = False
            for term in skip_terms:
                if equipment_name.lower() == term or equipment_name.lower().startswith(term + ' '):
                    is_generic = True
                    break

            if not is_generic and len(equipment_name) > 2:
                equipment_names.add(equipment_name)

        return equipment_names

    def normalize_equipment_name(self, name: str) -> str:
        """
        Normalize equipment name for better matching.

        Converts:
        - "88mm" → "8.8cm" (German notation)
        - "50mm" → "5.0cm"
        - "20mm" → "2.0cm"
        - Removes "AT guns", "heavy MG" suffixes

        Returns:
            Normalized name
        """
        normalized = name

        # German guns use centimeters (e.g., 8.8cm not 88mm)
        mm_match = re.search(r'(\d+)mm', normalized, re.IGNORECASE)
        if mm_match:
            mm_value = int(mm_match.group(1))
            cm_value = mm_value / 10.0
            # Replace with German notation
            normalized = re.sub(r'\d+mm', f'{cm_value}cm', normalized, flags=re.IGNORECASE)

        # Remove common suffixes that aren't in database names
        suffixes_to_remove = [
            ' AT guns', ' AT gun', ' heavy MG', ' MG', ' artillery',
            ' tanks', ' tank'
        ]
        for suffix in suffixes_to_remove:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]

        return normalized

    def resolve_equipment_name_to_id(self, equipment_name: str, nation: str = None) -> str:
        """
        Resolve equipment name from scenario to canonical_id in database.

        Args:
            equipment_name: Equipment name from scenario (e.g., "Matilda II", "88mm FlaK 18/36")
            nation: Optional nation filter to narrow search

        Returns:
            canonical_id if found, None otherwise
        """
        # Manual mappings for common scenario names that don't match database names
        manual_mappings = {
            '25-pdr': 'QF 25-pounder',
            '2-pdr': 'QF 2-pounder',
            '2-pdr AT guns': 'QF 2-pounder',
            '6-pdr': 'QF 6-pounder',
            'Breda M37 heavy MG': '20mm Breda',  # Breda M37 is 20mm machine gun
            'Breda M37': '20mm Breda',
            'Bren Carriers': 'Bren Carrier',
            'Cruiser tanks': 'Crusader',  # Generic - will need fuzzy match
            '47mm Cannone da 47/32 AT guns': 'Cannone DA 47/32',
            '47mm Cannone da 47/32': 'Cannone DA 47/32',
            '105mm artillery': '105mm M2A1',  # Common WW2 howitzer
            'Motorcycle Troops': None,  # Generic unit type, not equipment
            'German Panzergrenadier Company': None,  # Generic unit type
            'tanks': None,  # Skip - too generic
        }

        # Check manual mappings first
        if equipment_name in manual_mappings:
            mapped_name = manual_mappings[equipment_name]
            if mapped_name is None:
                return None  # Explicitly skipped
            equipment_name = mapped_name

        cursor = self.conn.cursor()

        # Strategy 1: Exact name match
        if nation:
            cursor.execute("""
                SELECT canonical_id, name FROM equipment
                WHERE LOWER(name) = LOWER(?) AND LOWER(nation) = LOWER(?)
                LIMIT 1
            """, (equipment_name, nation))
        else:
            cursor.execute("""
                SELECT canonical_id, name FROM equipment
                WHERE LOWER(name) = LOWER(?)
                LIMIT 1
            """, (equipment_name,))

        result = cursor.fetchone()
        if result:
            return result['canonical_id']

        # Strategy 1.5: Try normalized name (for German guns)
        normalized_name = self.normalize_equipment_name(equipment_name)
        if normalized_name != equipment_name:
            if nation:
                cursor.execute("""
                    SELECT canonical_id, name FROM equipment
                    WHERE LOWER(name) = LOWER(?) AND LOWER(nation) = LOWER(?)
                    LIMIT 1
                """, (normalized_name, nation))
            else:
                cursor.execute("""
                    SELECT canonical_id, name FROM equipment
                    WHERE LOWER(name) = LOWER(?)
                    LIMIT 1
                """, (normalized_name,))

            result = cursor.fetchone()
            if result:
                print(f"[NORMALIZED MATCH] '{equipment_name}' -> '{result['name']}' ({result['canonical_id']})")
                return result['canonical_id']

        # Strategy 2: Fuzzy name match (contains)
        if nation:
            cursor.execute("""
                SELECT canonical_id, name FROM equipment
                WHERE LOWER(name) LIKE LOWER(?) AND LOWER(nation) = LOWER(?)
                ORDER BY LENGTH(name) ASC
                LIMIT 1
            """, (f'%{equipment_name}%', nation))
        else:
            cursor.execute("""
                SELECT canonical_id, name FROM equipment
                WHERE LOWER(name) LIKE LOWER(?)
                ORDER BY LENGTH(name) ASC
                LIMIT 1
            """, (f'%{equipment_name}%',))

        result = cursor.fetchone()
        if result:
            print(f"[FUZZY MATCH] '{equipment_name}' -> '{result['name']}' ({result['canonical_id']})")
            return result['canonical_id']

        # Strategy 3: Try extracting key model numbers/names
        # e.g., "88mm FlaK 18/36" → search for "88mm" and "flak"
        words = equipment_name.lower().split()
        key_terms = [w for w in words if len(w) >= 3 and not w in ['the', 'and', 'gun']]

        if key_terms:
            search_pattern = '%' + '%'.join(key_terms) + '%'
            if nation:
                cursor.execute("""
                    SELECT canonical_id, name FROM equipment
                    WHERE LOWER(name) LIKE ? AND LOWER(nation) = LOWER(?)
                    ORDER BY LENGTH(name) ASC
                    LIMIT 1
                """, (search_pattern, nation))
            else:
                cursor.execute("""
                    SELECT canonical_id, name FROM equipment
                    WHERE LOWER(name) LIKE ?
                    ORDER BY LENGTH(name) ASC
                    LIMIT 1
                """, (search_pattern,))

            result = cursor.fetchone()
            if result:
                print(f"[PATTERN MATCH] '{equipment_name}' -> '{result['name']}' ({result['canonical_id']})")
                return result['canonical_id']

        print(f"[NOT FOUND] Could not resolve equipment: {equipment_name}")
        return None

    def get_all_scenarios_for_battle(self, battle_key: str) -> List[Path]:
        """
        Get all scenario markdown files for a battle.

        Args:
            battle_key: Battle key (e.g., 'tobruk')

        Returns:
            List of scenario file paths
        """
        battle = BATTLES[battle_key]
        output_dir = battle['output_dir']

        scenarios_dir = BOOKS_BASE / output_dir / "book" / "src" / "scenarios"

        if not scenarios_dir.exists():
            print(f"[WARNING] Scenarios directory not found: {scenarios_dir}")
            return []

        # Get all scenario_*.md files (exclude overview.md)
        scenario_files = sorted(scenarios_dir.glob("scenario_*.md"))

        print(f"Found {len(scenario_files)} scenario files for {battle['name']}")
        return scenario_files

    def extract_all_equipment_from_scenarios(self, battle_key: str) -> Tuple[Set[str], Dict[str, List[str]]]:
        """
        Extract all unique equipment from all scenarios in a battle.

        Args:
            battle_key: Battle key

        Returns:
            Tuple of (set of canonical_ids, dict mapping scenario to equipment names)
        """
        scenario_files = self.get_all_scenarios_for_battle(battle_key)

        all_equipment_names = set()
        scenario_equipment_map = {}

        for scenario_file in scenario_files:
            equipment_names = self.parse_scenario_equipment(scenario_file)
            scenario_equipment_map[scenario_file.name] = equipment_names
            all_equipment_names.update(equipment_names)

            print(f"  {scenario_file.name}: {len(equipment_names)} equipment items")

        print(f"\nTotal unique equipment names across all scenarios: {len(all_equipment_names)}")

        # Resolve names to canonical IDs
        equipment_ids = set()
        unresolved = []

        for name in all_equipment_names:
            canonical_id = self.resolve_equipment_name_to_id(name)
            if canonical_id:
                equipment_ids.add(canonical_id)
            else:
                unresolved.append(name)

        print(f"\nResolved {len(equipment_ids)} equipment IDs")
        if unresolved:
            print(f"[WARNING] Could not resolve {len(unresolved)} equipment names:")
            for name in unresolved:
                print(f"  - {name}")

        return equipment_ids, scenario_equipment_map

    def generate_scenario_based_datacards(self, battle_key: str):
        """
        Generate datacards ONLY for equipment found in scenario files.

        Args:
            battle_key: Battle key (e.g., 'tobruk')
        """
        battle = BATTLES[battle_key]
        print(f"\n{'='*70}")
        print(f"Generating SCENARIO-BASED datacards for: {battle['name']}")
        print(f"{'='*70}\n")

        # Extract equipment from scenarios
        equipment_ids, scenario_map = self.extract_all_equipment_from_scenarios(battle_key)

        if not equipment_ids:
            print("[ERROR] No equipment found in scenarios. Check scenario parsing logic.")
            return

        # Categorize equipment
        categorized_equipment = self.categorize_equipment(equipment_ids)

        # Create output directory
        output_dir = BOOKS_BASE / battle['output_dir'] / 'book' / 'src' / 'chapter2'
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nOutput directory: {output_dir}")

        # Generate datacards by category (reuse existing logic)
        for category, equipment_list in categorized_equipment.items():
            # Deduplicate by canonical_id
            seen_ids = set()
            unique_equipment = []
            for equipment in equipment_list:
                if equipment['canonical_id'] not in seen_ids:
                    seen_ids.add(equipment['canonical_id'])
                    unique_equipment.append(equipment)

            print(f"\n{category}: {len(unique_equipment)} items")

            # Sort by nation then name
            unique_equipment.sort(key=lambda x: (x['nation'], x['name']))

            # Generate markdown file
            category_file = category.lower().replace(' ', '_').replace('&', 'and') + '.md'
            output_file = output_dir / category_file

            with open(output_file, 'w', encoding='utf-8') as f:
                # Write title
                f.write(f"# {category}\n\n")

                # Write CSS (same as V5.5)
                css = """<style>
@media print {
    @page {
        size: A4 landscape;
        margin: 10mm;
    }

    .datacard-grid {
        page-break-after: always;
    }

    .datacard {
        page-break-inside: avoid;
    }
}

.datacard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 20px 0;
}

.datacard {
    border: 3px solid #2c2416;
    padding: 8px;
    background-color: #d4c5a0;
    box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
}

/* Nation-Specific Color Themes */
.datacard.datacard-german {
    background-color: #797768;
    border-color: #1a1a1a;
}

.datacard.datacard-german .datacard-title {
    color: white;
}

.datacard.datacard-german .datacard-subtitle {
    color: white;
}

.datacard.datacard-german .datacard-special-rules {
    color: white;
}

.datacard.datacard-german th {
    background-color: #ECD1A2;
    color: #1a1a1a;
}

.datacard.datacard-german td {
    background-color: #e8dcc8;
    color: #1a1a1a;
}

.datacard.datacard-british {
    background-color: #d4c5a0;
    border-color: #2c2416;
}

.datacard.datacard-british th {
    background-color: #8b7355;
    color: white;
}

.datacard.datacard-british td {
    background-color: #f5f5dc;
    color: #1a1a1a;
}

.datacard.datacard-italian {
    background-color: #739A64;
    border-color: #5a4a2a;
}

.datacard.datacard-italian th {
    background-color: #6b5d3f;
    color: white;
}

.datacard.datacard-italian td {
    background-color: #e8dcc0;
    color: #1a1a1a;
}

.datacard.datacard-american {
    background-color: #b8c5a0;
    border-color: #3a4a2a;
}

.datacard.datacard-american th {
    background-color: #5a6d45;
    color: white;
}

.datacard.datacard-american td {
    background-color: #dce8cf;
    color: #1a1a1a;
}

.datacard.datacard-french {
    background-color: #b8c4d4;
    border-color: #2a3a4a;
}

.datacard.datacard-french th {
    background-color: #4a5a6d;
    color: white;
}

.datacard.datacard-french td {
    background-color: #d8e4f4;
    color: #1a1a1a;
}

.datacard-header {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
    align-items: center;
}

.datacard-silhouette {
    width: 140px;
    height: 70px;
    background-color: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    padding: 5px;
}

.datacard-silhouette img {
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    object-fit: contain;
    mix-blend-mode: multiply;
}

.datacard-title-block {
    flex: 1;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.datacard-title {
    font-weight: bold;
    font-size: 16px;
    margin: 0;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.datacard-subtitle {
    font-size: 9px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
}

.datacard-special-rules {
    font-size: 7px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
    color: #5a4a3a;
}

.datacard table {
    width: 100%;
    border-collapse: collapse;
    margin: 2px 0;
    font-size: 8px;
}

.datacard th {
    background-color: #8b7355;
    color: white;
    font-weight: bold;
    padding: 1px 2px;
    border: 1px solid #2c2416;
    text-align: center;
    font-size: 7px;
    line-height: 1.0;
}

.datacard td {
    background-color: #f5f5dc;
    border: 1px solid #2c2416;
    padding: 1px 2px;
    text-align: center;
    font-size: 8px;
    line-height: 1.0;
}

.datacard .main-header {
    font-size: 8px;
    font-weight: bold;
}

.armor-modifier-row td {
    font-style: italic;
    font-size: 7px;
    padding: 1px 3px;
}

.datacard-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 5px;
    padding: 3px 5px;
    font-size: 9px;
    font-weight: bold;
}

.datacard-footer .footer-stat {
    flex: 1;
    text-align: center;
}
</style>

---

"""
                f.write(css)

                # Open single grid for all datacards
                f.write('<div class="datacard-grid">\n\n')

                # Generate all datacards in one continuous grid
                for equipment in unique_equipment:
                    datacard = self.generate_datacard_markdown(equipment, 'r')
                    f.write(datacard)
                    f.write('\n')

                # Close grid
                f.write("</div>\n")

            print(f"  -> {output_file.name}")

        print(f"\n{'='*70}")
        print(f"Scenario-based datacard generation complete for {battle['name']}")
        print(f"{'='*70}\n")

    def generate_all_books_from_scenarios(self):
        """Generate scenario-based datacards for all 12 battle books."""
        for battle_key in BATTLES.keys():
            self.generate_scenario_based_datacards(battle_key)
            print()  # Blank line between battles


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate datacards ONLY from equipment in scenario files",
        epilog="""
Examples:
  %(prog)s --battle tobruk              # Generate datacards only for equipment in Tobruk scenarios
  %(prog)s --all                        # Generate datacards for all 12 battles (scenario-based)
        """
    )
    parser.add_argument(
        "--battle",
        choices=list(BATTLES.keys()),
        help="Generate scenario-based datacards for specific battle"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate scenario-based datacards for all 12 battles"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.battle and not args.all:
        parser.error("Must specify --battle or --all")

    generator = ScenarioBasedDatacardGenerator()

    try:
        if args.all:
            generator.generate_all_books_from_scenarios()
        elif args.battle:
            generator.generate_scenario_based_datacards(args.battle)
        else:
            parser.print_help()
            return 1
    finally:
        generator.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
