#!/usr/bin/env python3
"""
Generate hierarchical forces structure markdown files from Phase 6 unit JSONs.

Creates Theater → Army → Corps → Division hierarchy with variant-level equipment detail.
Output: north_africa_campaign_book/src/forces/[nation]/[echelon]/[quarter]_[unit].md
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class ForcesMarkdownGenerator:
    """Generates markdown files for hierarchical forces structure."""

    def __init__(self, json_dir: Path, output_dir: Path):
        self.json_dir = Path(json_dir)
        self.output_dir = Path(output_dir)
        self.all_units = []
        self.unit_lookup = {}  # For cross-referencing subordinate units

    def load_all_jsons(self) -> None:
        """Load all unit JSONs into memory."""
        print(f"Loading unit JSONs from {self.json_dir}...")

        for json_file in self.json_dir.glob('*_toe.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_filename'] = json_file.name
                    self.all_units.append(data)

                    # Create lookup key for cross-referencing
                    nation = data.get('nation', '')
                    quarter = data.get('quarter', '')
                    designation = data.get('unit_designation', '')
                    key = f"{nation}_{quarter}_{designation}".lower()
                    self.unit_lookup[key] = data

            except Exception as e:
                print(f"Error loading {json_file.name}: {e}")

        print(f"Loaded {len(self.all_units)} unit JSONs")

    def slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text

    def format_number(self, num) -> str:
        """Format number with thousand separators."""
        if isinstance(num, (int, float)):
            return f"{int(num):,}"
        return str(num)

    def generate_all(self, nation: Optional[str] = None, echelon: Optional[str] = None) -> None:
        """Generate all markdown files."""

        nations = [nation] if nation else ['british', 'german', 'italian', 'american', 'french']

        stats = defaultdict(int)

        for nat in nations:
            units = [u for u in self.all_units if u.get('nation') == nat]

            if echelon:
                units = [u for u in units if u.get('organization_level') == echelon]

            # Group by echelon
            armies = [u for u in units if u.get('organization_level') == 'army']
            corps = [u for u in units if u.get('organization_level') == 'corps']
            divisions = [u for u in units if u.get('organization_level') == 'division']

            print(f"\n{nat.upper()}: {len(armies)} armies, {len(corps)} corps, {len(divisions)} divisions")

            # Generate files
            for unit in armies:
                self.generate_army_page(unit, nat)
                stats['armies'] += 1

            for unit in corps:
                self.generate_corps_page(unit, nat)
                stats['corps'] += 1

            for unit in divisions:
                self.generate_division_page(unit, nat)
                stats['divisions'] += 1

        print(f"\n=== GENERATION COMPLETE ===")
        print(f"Armies: {stats['armies']}")
        print(f"Corps: {stats['corps']}")
        print(f"Divisions: {stats['divisions']}")
        print(f"Total: {sum(stats.values())} files")

    def extract_tank_variants(self, tank_data: Dict) -> List[Dict]:
        """Extract variant-level tank details from nested JSON structure."""
        variants = []

        for category in ['heavy_tanks', 'medium_tanks', 'light_tanks']:
            if category not in tank_data:
                continue

            category_data = tank_data[category]
            category_label = category.replace('_tanks', '').replace('_', ' ').title()

            # Handle nested 'count' object
            if 'count' in category_data and isinstance(category_data['count'], dict):
                count_obj = category_data['count']

                if 'variants' in count_obj:
                    for variant_name, variant_details in count_obj['variants'].items():
                        variants.append({
                            'category': category_label,
                            'name': variant_name,
                            'total': variant_details.get('count', 0),
                            'operational': variant_details.get('operational', 0),
                            'witw_id': variant_details.get('witw_id', ''),
                            'notes': variant_details.get('notes', variant_details.get('note', ''))
                        })

        return variants

    def extract_artillery_variants(self, arty_data: Dict, arty_type: str) -> List[Dict]:
        """Extract artillery variants with caliber details."""
        variants = []

        if not arty_data or not isinstance(arty_data, dict):
            return variants

        if 'variants' in arty_data:
            for gun_name, gun_details in arty_data['variants'].items():
                variants.append({
                    'name': gun_name,
                    'type': arty_type,
                    'count': gun_details.get('count', 0),
                    'operational': gun_details.get('operational', gun_details.get('count', 0)),
                    'caliber': gun_details.get('caliber', 'Unknown'),
                    'witw_id': gun_details.get('witw_id', ''),
                    'notes': gun_details.get('notes', gun_details.get('note', ''))
                })

        return variants

    def format_tank_table(self, variants: List[Dict]) -> str:
        """Generate markdown table from tank variant list."""
        if not variants:
            return "*No tank data available*\n"

        lines = [
            "| Category | Variant | Total | Operational | Notes |",
            "|----------|---------|-------|-------------|-------|"
        ]

        for v in variants:
            # Truncate notes to 70 chars for table readability
            notes = v['notes'][:67] + '...' if len(v['notes']) > 70 else v['notes']
            lines.append(
                f"| {v['category']} | {v['name']} | {v['total']} | {v['operational']} | {notes} |"
            )

        return '\n'.join(lines) + '\n'

    def format_artillery_table(self, variants: List[Dict]) -> str:
        """Generate markdown table from artillery variant list."""
        if not variants:
            return "*No artillery data available*\n"

        lines = [
            "| Gun Type | Caliber | Count | Operational | Notes |",
            "|----------|---------|-------|-------------|-------|"
        ]

        for v in variants:
            notes = v['notes'][:60] + '...' if len(v['notes']) > 60 else v['notes']
            operational = v['operational'] if v['operational'] else v['count']
            lines.append(
                f"| {v['name']} | {v['caliber']} | {v['count']} | {operational} | {notes} |"
            )

        return '\n'.join(lines) + '\n'

    def extract_subordinate_units(self, unit_json: Dict) -> List[Dict]:
        """Extract subordinate units array."""
        subordinates = unit_json.get('subordinate_units', [])

        if not subordinates:
            return []

        # Normalize structure (handle both string arrays and object arrays)
        normalized = []
        for sub in subordinates:
            if isinstance(sub, str):
                normalized.append({'designation': sub})
            elif isinstance(sub, dict):
                normalized.append(sub)

        return normalized

    def generate_division_page(self, unit_json: Dict, nation: str) -> None:
        """Generate division-level markdown page."""

        quarter = unit_json.get('quarter', 'unknown')
        designation = unit_json.get('unit_designation', 'Unknown Unit')
        slug = self.slugify(designation)
        filename = f"{quarter}_{slug}.md"

        output_path = self.output_dir / nation / 'divisions' / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Extract data
        total_personnel = unit_json.get('total_personnel', 0)
        officers = unit_json.get('officers', 0)
        ncos = unit_json.get('ncos', 0)
        enlisted = unit_json.get('enlisted', 0)

        commander_data = unit_json.get('command', {}).get('commander', {})
        if isinstance(commander_data, str):
            commander_name = commander_data
            commander_rank = ''
        elif isinstance(commander_data, dict):
            commander_name = commander_data.get('name', 'Unknown')
            commander_rank = commander_data.get('rank', '')
        else:
            commander_name = 'Unknown'
            commander_rank = ''

        parent_formation = unit_json.get('parent_formation', 'Unknown')
        unit_type = unit_json.get('unit_type', 'Unknown')

        # Extract equipment
        tanks_data = unit_json.get('tanks', {})
        tank_variants = self.extract_tank_variants(tanks_data)

        tank_total = tanks_data.get('total', {}).get('count', 0)
        tank_operational = tanks_data.get('operational', {}).get('count', 0)

        # Extract artillery
        field_artillery = self.extract_artillery_variants(
            unit_json.get('field_artillery', {}), 'Field Artillery'
        )
        anti_tank = self.extract_artillery_variants(
            unit_json.get('anti_tank', {}), 'Anti-Tank'
        )
        anti_aircraft = self.extract_artillery_variants(
            unit_json.get('anti_aircraft', {}), 'Anti-Aircraft'
        )

        # Extract subordinate units
        subordinates = self.extract_subordinate_units(unit_json)

        # Build markdown content
        content = []
        content.append(f"# {designation} ({quarter.upper()})\n")

        # Command structure
        content.append("## Command Structure\n")
        content.append(f"**Commander**: {commander_rank} {commander_name}  ")
        content.append(f"**Parent Formation**: {parent_formation}  ")
        content.append(f"**Type**: {unit_type}\n")

        # Personnel
        if total_personnel > 0:
            content.append("## Personnel\n")
            content.append(f"- **Total**: {self.format_number(total_personnel)} ")
            content.append(f"({self.format_number(officers)} officers, ")
            content.append(f"{self.format_number(ncos)} NCOs, ")
            content.append(f"{self.format_number(enlisted)} enlisted)\n")

        # Subordinate units
        if subordinates:
            content.append("## Subordinate Units\n")
            for sub in subordinates:
                sub_designation = sub.get('unit_designation', sub.get('designation', 'Unknown'))
                content.append(f"\n### {sub_designation}\n")

                if 'commander' in sub:
                    content.append(f"- **Commander**: {sub['commander']}\n")
                if 'strength' in sub:
                    content.append(f"- **Strength**: {self.format_number(sub['strength'])} personnel\n")
                if 'tanks' in sub:
                    content.append(f"- **Tank Strength**: {sub['tanks']} tanks\n")
                if 'role' in sub:
                    content.append(f"- **Role**: {sub['role']}\n")
                if 'notes' in sub:
                    content.append(f"- **Composition**: {sub['notes']}\n")

        # Equipment - Tanks
        if tank_variants:
            content.append(f"## Division Equipment\n")
            content.append(f"\n### Tanks ({tank_total} total")
            if tank_operational:
                readiness = (tank_operational * 100 // tank_total) if tank_total > 0 else 0
                content.append(f", {tank_operational} operational, {readiness}% readiness")
            content.append(")\n\n")
            content.append(self.format_tank_table(tank_variants))

        # Artillery
        all_artillery = field_artillery + anti_tank + anti_aircraft
        if all_artillery:
            content.append("\n### Artillery\n\n")

            if field_artillery:
                content.append("#### Field Artillery\n")
                content.append(self.format_artillery_table(field_artillery))

            if anti_tank:
                content.append("\n#### Anti-Tank Guns\n")
                content.append(self.format_artillery_table(anti_tank))

            if anti_aircraft:
                content.append("\n#### Anti-Aircraft Guns\n")
                content.append(self.format_artillery_table(anti_aircraft))

        # Supply & Logistics
        supply = unit_json.get('supply_logistics', {})
        if supply:
            content.append("\n## Supply & Logistics\n\n")
            if 'supply_status' in supply:
                content.append(f"**Supply Status**: {supply['supply_status']}\n\n")
            if 'operational_radius' in supply:
                content.append(f"- **Operational Radius**: {supply['operational_radius']}\n")
            if 'fuel' in supply:
                content.append(f"- **Fuel Reserves**: {supply['fuel']}\n")
            if 'ammunition' in supply:
                content.append(f"- **Ammunition Reserves**: {supply['ammunition']}\n")
            if 'water' in supply:
                content.append(f"- **Water**: {supply['water']}\n")

        # Data quality
        validation = unit_json.get('validation', {})
        confidence = validation.get('overall_confidence', 0)
        tier = validation.get('data_tier', 'unknown')

        content.append(f"\n---\n\n")
        content.append(f"**Confidence**: {confidence}% (Tier {tier})  \n")
        content.append(f"**Generated from**: `{unit_json['_filename']}`\n")

        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(content))

    def generate_corps_page(self, unit_json: Dict, nation: str) -> None:
        """Generate corps-level markdown page."""
        # Similar structure to division, but may include aggregation
        # For now, use same template
        self.generate_division_page(unit_json, nation)

    def generate_army_page(self, unit_json: Dict, nation: str) -> None:
        """Generate army-level markdown page."""
        # Similar structure to division, but at army echelon
        # For now, use same template
        self.generate_division_page(unit_json, nation)


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate forces markdown from Phase 6 JSONs')
    parser.add_argument('--input', default='D:/north-africa-toe-builder/data/output/units',
                       help='Input directory with unit JSONs')
    parser.add_argument('--output', default='D:/north-africa-toe-builder/north_africa_campaign_book/src/forces',
                       help='Output directory for markdown files')
    parser.add_argument('--nation', choices=['british', 'german', 'italian', 'american', 'french'],
                       help='Generate only specified nation')
    parser.add_argument('--echelon', choices=['army', 'corps', 'division'],
                       help='Generate only specified echelon level')

    args = parser.parse_args()

    generator = ForcesMarkdownGenerator(args.input, args.output)
    generator.load_all_jsons()
    generator.generate_all(nation=args.nation, echelon=args.echelon)


if __name__ == '__main__':
    main()
