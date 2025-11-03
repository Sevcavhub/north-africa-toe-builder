#!/usr/bin/env python3
"""
Generate BattleGroup Army Lists for North Africa battles.

Extracts unit compositions from Phase 6 unit JSONs and matches to equipment
datacards to create army lists with points costs and battle ratings.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Battle to quarter mapping
BATTLES = {
    'battleaxe': {'quarter': '1941q2', 'name': 'Operation Battleaxe', 'display': '1941 Q2'},
    'crusader': {'quarter': '1941q4', 'name': 'Operation Crusader', 'display': '1941 Q4'},
    'gazala': {'quarter': '1942q2', 'name': 'Battle of Gazala', 'display': '1942 Q2'},
    'first_alamein': {'quarter': '1942q3', 'name': 'First Battle of El Alamein', 'display': '1942 Q3'}
}

# Nation display names
NATION_NAMES = {
    'british': 'British & Commonwealth',
    'german': 'German',
    'italian': 'Italian',
    'american': 'American',
    'french': 'Free French'
}

class EquipmentDatabase:
    """Database of equipment from datacards with points and BR."""

    def __init__(self):
        self.equipment = {}  # witw_id -> {name, points, br, type}

    def load_from_datacards(self, books_dir: Path):
        """Parse all datacard markdown files to extract equipment data."""
        print("Loading equipment from datacards...")

        for battle_dir in books_dir.iterdir():
            if not battle_dir.is_dir():
                continue

            chapter2_dir = battle_dir / 'chapter2'
            if not chapter2_dir.exists():
                continue

            for datacard_file in chapter2_dir.glob('*.md'):
                self._parse_datacard_file(datacard_file)

        print(f"  Loaded {len(self.equipment)} equipment items from datacards")

    def _parse_datacard_file(self, filepath: Path):
        """Parse a single datacard markdown file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into individual equipment entries (## headings)
        entries = re.split(r'\n## ', content)

        for entry in entries[1:]:  # Skip file header
            # Extract equipment name
            name_match = re.match(r'(.+?)\n', entry)
            if not name_match:
                continue
            name = name_match.group(1).strip()

            # Extract points and battle rating
            points_match = re.search(r'\*\*Points:\*\* (\d+)', entry)
            br_match = re.search(r'\*\*Battle Rating:\*\* (\d+)', entry)

            if points_match and br_match:
                points = int(points_match.group(1))
                br = int(br_match.group(1))

                # Try to extract WITW ID from context (equipment type)
                # For now, use normalized name as key
                equipment_key = self._normalize_name(name)

                self.equipment[equipment_key] = {
                    'name': name,
                    'points': points,
                    'br': br,
                    'category': self._get_category_from_file(filepath)
                }

    def _normalize_name(self, name: str) -> str:
        """Normalize equipment name for matching."""
        # Remove punctuation, lowercase, collapse spaces
        normalized = re.sub(r'[^\w\s]', '', name.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def _get_category_from_file(self, filepath: Path) -> str:
        """Get equipment category from filename."""
        filename = filepath.stem
        if 'tank' in filename:
            return 'Tanks'
        elif 'gun' in filename or 'artillery' in filename:
            return 'Artillery & Anti-Tank'
        elif 'infantry_weapon' in filename:
            return 'Infantry Weapons'
        elif 'vehicle' in filename:
            return 'Vehicles'
        else:
            return 'Support Equipment'

    def lookup(self, equipment_name: str) -> Optional[Dict]:
        """Look up equipment by name."""
        key = self._normalize_name(equipment_name)
        return self.equipment.get(key)

    def fuzzy_lookup(self, equipment_name: str) -> Optional[Dict]:
        """Fuzzy lookup for equipment by partial name match."""
        key = self._normalize_name(equipment_name)

        # Try exact match first
        if key in self.equipment:
            return self.equipment[key]

        # Try partial match
        for eq_key, eq_data in self.equipment.items():
            if key in eq_key or eq_key in key:
                return eq_data

        return None


class UnitExtractor:
    """Extract unit compositions from Phase 6 JSONs."""

    def __init__(self, equipment_db: EquipmentDatabase):
        self.equipment_db = equipment_db

    def extract_units_for_quarter(self, units_dir: Path, nation: str, quarter: str) -> List[Dict]:
        """Extract all units for a specific nation and quarter."""
        units = []

        # Find all unit files matching nation and quarter
        pattern = f"{nation}_{quarter}_*.json"
        for unit_file in units_dir.glob(pattern):
            if unit_file.stem.endswith('.backup'):
                continue

            unit_data = self._parse_unit_file(unit_file)
            if unit_data:
                units.append(unit_data)

        return units

    def _parse_unit_file(self, filepath: Path) -> Optional[Dict]:
        """Parse a single unit JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"  Error parsing {filepath.name}: {e}")
            return None

        unit = {
            'name': data.get('unit_designation', 'Unknown Unit'),
            'type': data.get('unit_type', 'Unknown'),
            'organization_level': data.get('organization_level', 'unknown'),
            'personnel': data.get('total_personnel', 0),
            'equipment': self._extract_equipment(data),
            'composition': []
        }

        return unit

    def _extract_equipment(self, data: Dict) -> List[Dict]:
        """Extract equipment items from unit JSON recursively."""
        equipment_list = []

        # Extract tanks
        if 'tanks' in data:
            equipment_list.extend(self._extract_from_section(data['tanks'], 'Tank'))

        # Extract artillery
        if 'artillery' in data:
            equipment_list.extend(self._extract_from_section(data['artillery'], 'Artillery'))

        # Extract anti-tank guns
        if 'anti_tank_guns' in data:
            equipment_list.extend(self._extract_from_section(data['anti_tank_guns'], 'Anti-Tank'))

        # Extract vehicles
        if 'vehicles' in data:
            equipment_list.extend(self._extract_from_section(data['vehicles'], 'Vehicle'))

        # Extract infantry weapons (top 3 only)
        if 'top_3_infantry_weapons' in data:
            weapons_data = data['top_3_infantry_weapons']

            # Handle both dict and list formats
            if isinstance(weapons_data, dict):
                weapon_items = weapons_data.values()
            elif isinstance(weapons_data, list):
                weapon_items = weapons_data
            else:
                weapon_items = []

            for weapon in weapon_items:
                if isinstance(weapon, dict) and 'weapon' in weapon:
                    equipment_list.append({
                        'name': weapon['weapon'],
                        'count': weapon.get('count', 0),
                        'type': 'Infantry Weapon',
                        'witw_id': weapon.get('witw_id')
                    })

        return equipment_list

    def _extract_from_section(self, section: Dict, equipment_type: str) -> List[Dict]:
        """Recursively extract equipment from a JSON section."""
        equipment = []

        if not isinstance(section, dict):
            return equipment

        for key, value in section.items():
            if isinstance(value, dict):
                # Check for count and variants
                if 'count' in value:
                    count_data = value['count']
                    if isinstance(count_data, dict) and 'variants' in count_data:
                        # Extract variants
                        for variant_name, variant_data in count_data['variants'].items():
                            if isinstance(variant_data, dict):
                                equipment.append({
                                    'name': variant_name,
                                    'count': variant_data.get('count', 0),
                                    'type': equipment_type,
                                    'witw_id': variant_data.get('witw_id')
                                })

                # Recurse into nested structures
                equipment.extend(self._extract_from_section(value, equipment_type))

        return equipment


class ArmyListGenerator:
    """Generate army list markdown files."""

    def __init__(self, equipment_db: EquipmentDatabase, unit_extractor: UnitExtractor):
        self.equipment_db = equipment_db
        self.unit_extractor = unit_extractor

    def generate_army_lists(self, battle_key: str, output_dir: Path, units_dir: Path):
        """Generate army lists for all nations in a battle."""
        battle_info = BATTLES[battle_key]
        quarter = battle_info['quarter']

        print(f"\nGenerating army lists for {battle_info['name']}...")

        # Create chapter3 directory
        chapter3_dir = output_dir / battle_key / 'chapter3'
        chapter3_dir.mkdir(parents=True, exist_ok=True)

        # Generate for each nation
        for nation in ['british', 'german', 'italian']:
            units = self.unit_extractor.extract_units_for_quarter(units_dir, nation, quarter)

            if not units:
                print(f"  No {nation} units found for {quarter}")
                continue

            markdown = self._generate_army_list_markdown(
                nation, battle_info, units
            )

            output_file = chapter3_dir / f'army_lists_{nation}.md'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            print(f"  -> {output_file.name} ({len(units)} units)")

    def _generate_army_list_markdown(self, nation: str, battle_info: Dict, units: List[Dict]) -> str:
        """Generate markdown for a single nation's army list."""
        nation_name = NATION_NAMES.get(nation, nation.title())

        # Organize units by type
        units_by_category = self._categorize_units(units)

        # Build sections
        sections = {
            'hq_units_section': self._build_unit_section(units_by_category.get('HQ', [])),
            'infantry_units_section': self._build_unit_section(units_by_category.get('Infantry', [])),
            'armoured_units_section': self._build_unit_section(units_by_category.get('Armoured', [])),
            'artillery_units_section': self._build_unit_section(units_by_category.get('Artillery', [])),
            'support_units_section': self._build_unit_section(units_by_category.get('Support', [])),
            'special_rules_section': self._build_special_rules_section(nation),
            'historical_notes': self._build_historical_notes(nation, battle_info)
        }

        # Load template
        template_path = Path(__file__).parent.parent / 'templates' / 'army_list_template.md'
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Fill template
        markdown = template.format(
            nation_name=nation_name,
            battle_name=battle_info['name'],
            quarter_display=battle_info['display'],
            **sections
        )

        return markdown

    def _categorize_units(self, units: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize units by type."""
        categories = defaultdict(list)

        for unit in units:
            org_level = unit.get('organization_level', '').lower()
            unit_type = unit.get('type', '').lower()

            if 'corps' in unit_type or 'army' in unit_type:
                categories['HQ'].append(unit)
            elif 'armour' in unit_type or 'tank' in unit_type:
                categories['Armoured'].append(unit)
            elif 'infantry' in unit_type or 'division' in unit_type:
                categories['Infantry'].append(unit)
            elif 'artillery' in unit_type:
                categories['Artillery'].append(unit)
            else:
                categories['Support'].append(unit)

        return dict(categories)

    def _build_unit_section(self, units: List[Dict]) -> str:
        """Build markdown section for a category of units."""
        if not units:
            return "*No units available in this category.*\n"

        markdown_lines = []

        for unit in units:
            # Calculate total points and BR
            total_points, total_br = self._calculate_unit_points_br(unit)

            markdown_lines.append(f"### {unit['name']}\n")
            markdown_lines.append(f"**Points:** {total_points} | **Battle Rating:** {total_br} | **Personnel:** {unit['personnel']:,}\n")
            markdown_lines.append(f"\n**Unit Type:** {unit['type']}\n")

            # Equipment breakdown
            if unit['equipment']:
                markdown_lines.append(f"\n**Equipment:**\n")

                # Group by type
                by_type = defaultdict(list)
                for eq in unit['equipment']:
                    by_type[eq['type']].append(eq)

                for eq_type, items in sorted(by_type.items()):
                    markdown_lines.append(f"\n*{eq_type}:*\n")
                    for item in items:
                        eq_data = self.equipment_db.fuzzy_lookup(item['name'])
                        if eq_data:
                            item_points = eq_data['points'] * item['count']
                            markdown_lines.append(
                                f"- {item['count']}x {item['name']} "
                                f"({eq_data['points']} pts each, {item_points} pts total)\n"
                            )
                        else:
                            markdown_lines.append(f"- {item['count']}x {item['name']} (points TBD)\n")

            markdown_lines.append(f"\n---\n\n")

        return ''.join(markdown_lines)

    def _calculate_unit_points_br(self, unit: Dict) -> Tuple[int, int]:
        """Calculate total points and battle rating for a unit."""
        total_points = 0
        total_br = 0

        for eq in unit['equipment']:
            eq_data = self.equipment_db.fuzzy_lookup(eq['name'])
            if eq_data:
                total_points += eq_data['points'] * eq['count']
                total_br += eq_data['br'] * eq['count']

        return total_points, total_br

    def _build_special_rules_section(self, nation: str) -> str:
        """Build special rules section for a nation."""
        rules = {
            'british': [
                "**British Resolve:** British units have +1 morale in defensive positions",
                "**Desert Adapted:** All Commonwealth forces are considered acclimatized to desert conditions",
                "**Combined Arms:** May mix infantry and tank units in same platoon"
            ],
            'german': [
                "**German Tactical Doctrine:** +1 to initiative rolls",
                "**Panzer Doctrine:** Tank units may operate independently without HQ attachment",
                "**Experienced Crews:** Veteran tank crews get +1 to gunnery rolls"
            ],
            'italian': [
                "**Reluctant Warriors:** -1 morale in certain circumstances (see rulebook)",
                "**Defensive Positions:** +1 to cover saves when in prepared positions",
                "**Limited Supplies:** Must pass supply check for artillery barrages"
            ]
        }

        nation_rules = rules.get(nation, ["*Standard special rules apply*"])
        return '\n'.join(f"- {rule}" for rule in nation_rules)

    def _build_historical_notes(self, nation: str, battle_info: Dict) -> str:
        """Build historical notes section."""
        return f"""
This army list represents {NATION_NAMES.get(nation, nation.title())} forces during {battle_info['name']} in {battle_info['display']}.

Unit compositions are based on historical tables of organization and equipment from Phase 6 extraction. Points costs are derived from equipment datacards matching BattleGroup game system specifications.

**Historical Context:**
- Battle: {battle_info['name']}
- Period: {battle_info['display']}
- Theater: North Africa

For detailed equipment specifications, see Chapter 2 (Equipment Datacards).
"""


def main():
    """Main entry point."""
    # Set up paths
    project_root = Path(__file__).parent.parent.parent.parent
    books_dir = project_root / 'books'
    units_dir = project_root / 'data' / 'output' / 'units'

    print("=== BattleGroup Army List Generator ===\n")

    # Initialize components
    equipment_db = EquipmentDatabase()
    equipment_db.load_from_datacards(books_dir)

    unit_extractor = UnitExtractor(equipment_db)
    generator = ArmyListGenerator(equipment_db, unit_extractor)

    # Generate for all battles
    for battle_key in BATTLES.keys():
        generator.generate_army_lists(battle_key, books_dir, units_dir)

    print("\n=== Army List Generation Complete ===")
    print(f"Generated army lists in books/{{battle}}/chapter3/")


if __name__ == '__main__':
    main()
