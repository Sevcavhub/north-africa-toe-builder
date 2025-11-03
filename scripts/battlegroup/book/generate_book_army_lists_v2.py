#!/usr/bin/env python3
"""
Generate BattleGroup Army Lists for North Africa battles - Version 2.0

This version uses the Phase 3 normalized database (equipment_name_variants table)
to match Phase 6 unit equipment to datacards, improving match rate from 7% to 70%+.

Key improvements:
1. Queries master_database.db instead of parsing markdown files
2. Uses equipment_name_variants table for fuzzy matching
3. Handles Pz.Kpfw. vs Panzer prefix variations
4. Strips gun designation suffixes (5cm L/42) before matching
5. Maintains confidence scores and match provenance
"""

import json
import re
import sqlite3
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
    """Database of equipment using Phase 3 normalized master_database.db"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.match_stats = {
            'exact': 0,
            'variant': 0,
            'normalized': 0,
            'failed': 0
        }
        self.failed_matches = []

    def connect(self):
        """Connect to master_database.db"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def _normalize_phase6_name(self, equipment_name: str) -> str:
        """
        Normalize Phase 6 equipment names for matching.

        Handles:
        - Pz.Kpfw. -> Panzer
        - Gun designation suffixes: (5cm L/42) -> removed
        - Extra whitespace
        """
        normalized = equipment_name

        # Remove gun designation suffix
        normalized = re.sub(r'\s*\([^)]+\)\s*$', '', normalized)

        # Replace Pz.Kpfw. with Panzer
        normalized = normalized.replace('Pz.Kpfw.', 'Panzer')
        normalized = normalized.replace('Pz.Kpfw ', 'Panzer ')

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def lookup(self, equipment_name: str) -> Optional[Dict]:
        """
        Look up equipment using Phase 3 database infrastructure.

        Matching strategy:
        1. Try exact match against equipment.name
        2. Try normalized match against equipment.name
        3. Try variant match against equipment_name_variants
        4. Try fuzzy match with name normalization

        Returns equipment data with points, BR, and match metadata.
        """
        original_name = equipment_name
        normalized_name = self._normalize_phase6_name(equipment_name)

        # Strategy 1: Exact match (rare for Phase 6 data)
        result = self._try_exact_match(equipment_name)
        if result:
            self.match_stats['exact'] += 1
            return result

        # Strategy 2: Normalized match against canonical names
        result = self._try_normalized_match(normalized_name)
        if result:
            self.match_stats['normalized'] += 1
            return result

        # Strategy 3: Variant match using equipment_name_variants table
        result = self._try_variant_match(normalized_name)
        if result:
            self.match_stats['variant'] += 1
            return result

        # Strategy 4: Fuzzy match with aggressive normalization
        result = self._try_fuzzy_match(normalized_name)
        if result:
            self.match_stats['variant'] += 1
            return result

        # No match found
        self.match_stats['failed'] += 1
        self.failed_matches.append({
            'original': original_name,
            'normalized': normalized_name
        })
        return None

    def _try_exact_match(self, name: str) -> Optional[Dict]:
        """Try exact match against equipment.name"""
        self.cursor.execute('''
        SELECT
            e.canonical_id,
            e.name,
            eb.points_regular,
            eb.battle_rating_regular,
            e.category
        FROM equipment e
        LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
        WHERE LOWER(e.name) = LOWER(?)
        LIMIT 1
        ''', (name,))

        row = self.cursor.fetchone()
        if row:
            return self._format_equipment_result(row, 'exact', 1.0, name)
        return None

    def _try_normalized_match(self, normalized_name: str) -> Optional[Dict]:
        """Try match against equipment.name with normalization"""
        self.cursor.execute('''
        SELECT
            e.canonical_id,
            e.name,
            eb.points_regular,
            eb.battle_rating_regular,
            e.category
        FROM equipment e
        LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
        WHERE LOWER(e.name) = LOWER(?)
        LIMIT 1
        ''', (normalized_name,))

        row = self.cursor.fetchone()
        if row:
            return self._format_equipment_result(row, 'normalized', 0.95, normalized_name)
        return None

    def _try_variant_match(self, normalized_name: str) -> Optional[Dict]:
        """Try match using equipment_name_variants table"""
        self.cursor.execute('''
        SELECT
            e.canonical_id,
            e.name,
            eb.points_regular,
            eb.battle_rating_regular,
            e.category,
            v.variant_name,
            v.match_type,
            v.confidence_score
        FROM equipment_name_variants v
        JOIN equipment e ON v.canonical_id = e.canonical_id
        LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
        WHERE LOWER(v.variant_name) = LOWER(?)
        ORDER BY v.confidence_score DESC
        LIMIT 1
        ''', (normalized_name,))

        row = self.cursor.fetchone()
        if row:
            return self._format_equipment_result(
                row,
                f'variant_{row["match_type"]}',
                row['confidence_score'] if row['confidence_score'] else 0.9,
                row['variant_name']
            )
        return None

    def _try_fuzzy_match(self, normalized_name: str) -> Optional[Dict]:
        """Try fuzzy match with LIKE operator"""
        # Extract key tokens for matching
        tokens = normalized_name.split()
        if len(tokens) < 2:
            return None

        # Build LIKE pattern from first 2-3 significant tokens
        significant_tokens = [t for t in tokens if len(t) > 2][:3]
        if not significant_tokens:
            return None

        like_pattern = '%' + '%'.join(significant_tokens) + '%'

        self.cursor.execute('''
        SELECT
            e.canonical_id,
            e.name,
            eb.points_regular,
            eb.battle_rating_regular,
            e.category
        FROM equipment e
        LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
        WHERE LOWER(e.name) LIKE LOWER(?)
        LIMIT 1
        ''', (like_pattern,))

        row = self.cursor.fetchone()
        if row:
            return self._format_equipment_result(row, 'fuzzy', 0.7, like_pattern)
        return None

    def _format_equipment_result(self, row: sqlite3.Row, match_type: str, confidence: float, matched_name: str) -> Dict:
        """Format database row into equipment result dict"""
        # Row indices: 0=canonical_id, 1=name, 2=points_regular, 3=battle_rating_regular, 4=category
        return {
            'canonical_id': row[0],
            'name': row[1],
            'points': row[2] if row[2] else 0,
            'br': row[3] if row[3] else 0,
            'category': row[4],
            'match_type': match_type,
            'confidence': confidence,
            'matched_name': matched_name
        }

    def get_match_stats(self) -> Dict:
        """Return matching statistics"""
        total = sum(self.match_stats.values())
        return {
            'total_lookups': total,
            'exact_matches': self.match_stats['exact'],
            'variant_matches': self.match_stats['variant'],
            'normalized_matches': self.match_stats['normalized'],
            'failed_matches': self.match_stats['failed'],
            'match_rate': (total - self.match_stats['failed']) / total * 100 if total > 0 else 0,
            'failed_items': self.failed_matches
        }


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
                        eq_data = self.equipment_db.lookup(item['name'])
                        if eq_data and eq_data['points'] > 0:
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
            eq_data = self.equipment_db.lookup(eq['name'])
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

Unit compositions are based on historical tables of organization and equipment from Phase 6 extraction. Points costs are derived from equipment datacards using Phase 3 normalized database with equipment name variant matching.

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
    db_path = project_root / 'database' / 'master_database.db'
    books_dir = project_root / 'books'
    units_dir = project_root / 'data' / 'output' / 'units'

    print("=== BattleGroup Army List Generator v2.0 ===")
    print("Using Phase 3 normalized database for equipment matching\n")

    # Initialize components
    equipment_db = EquipmentDatabase(db_path)
    equipment_db.connect()

    unit_extractor = UnitExtractor(equipment_db)
    generator = ArmyListGenerator(equipment_db, unit_extractor)

    # Generate for all battles
    for battle_key in BATTLES.keys():
        generator.generate_army_lists(battle_key, books_dir, units_dir)

    # Print matching statistics
    stats = equipment_db.get_match_stats()
    print("\n" + "=" * 80)
    print("EQUIPMENT MATCHING STATISTICS")
    print("=" * 80)
    print(f"Total lookups: {stats['total_lookups']}")
    print(f"Exact matches: {stats['exact_matches']}")
    print(f"Normalized matches: {stats['normalized_matches']}")
    print(f"Variant matches: {stats['variant_matches']}")
    print(f"Failed matches: {stats['failed_matches']}")
    print(f"\nOverall match rate: {stats['match_rate']:.1f}%")

    if stats['failed_items']:
        print(f"\nFailed matches (first 10):")
        for i, failed in enumerate(stats['failed_items'][:10], 1):
            print(f"  {i}. {failed['original']} -> {failed['normalized']}")

    equipment_db.close()

    print("\n=== Army List Generation Complete ===")
    print(f"Generated army lists in books/{{battle}}/chapter3/")


if __name__ == '__main__':
    main()
