#!/usr/bin/env python3
"""
Generate BattleGroup datacards from a text army list.

This script:
1. Parses a simple text army list (equipment names, one per line)
2. Looks up equipment in bg_builder_vehicles and bg_builder_weapons tables
3. Generates V5.5 format datacards using our existing generator

Input formats supported:
- Plain text list: "Panzer III\nPanzer IV\n88mm FlaK"
- TSV/CSV with quantities: "3x Panzer III, 2x Panzer IV"
- Scenario format: "- 3x Panzer III (veteran) - 150 pts"

Usage:
    python generate_datacards_from_army_list.py --input army_list.txt --output datacards/
    python generate_datacards_from_army_list.py --equipment "Panzer III,Panzer IV,88mm FlaK" --output test/
"""

import sqlite3
import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Import existing V5.5 generator for datacard rendering
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.battlegroup.book.generate_book_datacards_v5_5 import BookDatacardGenerator

# Support environment variable for database path (for Render.com deployment)
# Default to main database, but Render uses web database
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = os.environ.get('DATABASE_PATH', str(PROJECT_ROOT / "database" / "master_database.db"))
if not Path(DATABASE_PATH).exists():
    # Fallback to web database if main database doesn't exist (Render deployment)
    WEB_DATABASE = PROJECT_ROOT / "scripts" / "battlegroup" / "web" / "database" / "web_database.db"
    if WEB_DATABASE.exists():
        DATABASE_PATH = str(WEB_DATABASE)


class ArmyListDatacardGenerator:
    """Generate datacards from army list text input."""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
        self.datacard_gen = BookDatacardGenerator()

    def close(self):
        """Close database connections."""
        self.conn.close()
        self.datacard_gen.close()

    def parse_army_list_text(self, text: str) -> List[str]:
        """
        Parse army list text and extract equipment names.

        Supports multiple formats:
        - "Panzer III" (plain name)
        - "3x Panzer III" (with quantity)
        - "- 3x Panzer III (veteran) - 150 pts" (scenario format)
        - "Panzer III, Panzer IV, 88mm FlaK" (comma-separated)

        Returns:
            List of equipment names (deduplicated)
        """
        equipment_names = set()

        # Split by newlines and commas
        lines = text.replace(',', '\n').split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove leading dash/bullet
            line = re.sub(r'^[-•*]\s*', '', line)

            # Pattern 1: "3x Equipment Name (veteran) - 150 pts"
            match = re.match(r'^\d+x\s+([^(]+?)(?:\s*\([^)]+\))?(?:\s*-\s*\d+\s*pts)?', line, re.IGNORECASE)
            if match:
                equipment_names.add(match.group(1).strip())
                continue

            # Pattern 2: "Equipment Name (veteran)"
            match = re.match(r'^([^(]+?)(?:\s*\([^)]+\))?$', line)
            if match:
                equipment_names.add(match.group(1).strip())

        return list(equipment_names)

    def lookup_bg_builder_vehicle(self, name: str) -> Dict:
        """
        Look up vehicle in bg_builder_vehicles table.

        Returns vehicle data with weapons resolved.
        """
        cursor = self.conn.cursor()

        # Try exact match first
        cursor.execute("""
            SELECT * FROM bg_builder_vehicles
            WHERE LOWER(name) = LOWER(?)
            LIMIT 1
        """, (name,))

        result = cursor.fetchone()
        if result:
            vehicle = dict(result)

            # Resolve weapon IDs to weapon names/stats
            for i in range(1, 6):  # weapon_1_id through weapon_5_id
                weapon_id_col = f'weapon_{i}_id'
                if weapon_id_col in vehicle and vehicle[weapon_id_col]:
                    weapon_data = self.lookup_bg_builder_weapon_by_id(vehicle[weapon_id_col])
                    vehicle[f'weapon_{i}_data'] = weapon_data

            return vehicle

        # Try fuzzy match
        cursor.execute("""
            SELECT * FROM bg_builder_vehicles
            WHERE LOWER(name) LIKE LOWER(?)
            ORDER BY LENGTH(name) ASC
            LIMIT 1
        """, (f'%{name}%',))

        result = cursor.fetchone()
        if result:
            vehicle = dict(result)
            print(f"[FUZZY MATCH] '{name}' -> '{vehicle['name']}'")

            # Resolve weapons
            for i in range(1, 6):
                weapon_id_col = f'weapon_{i}_id'
                if weapon_id_col in vehicle and vehicle[weapon_id_col]:
                    weapon_data = self.lookup_bg_builder_weapon_by_id(vehicle[weapon_id_col])
                    vehicle[f'weapon_{i}_data'] = weapon_data

            return vehicle

        print(f"[NOT FOUND] Vehicle not in bg_builder_vehicles: {name}")
        return None

    def lookup_bg_builder_weapon_by_id(self, weapon_id: int) -> Dict:
        """Look up weapon by ID in bg_builder_weapons table."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM bg_builder_weapons
            WHERE weapon_id = ?
        """, (weapon_id,))

        result = cursor.fetchone()
        return dict(result) if result else None

    def lookup_bg_builder_weapon_by_name(self, name: str) -> Dict:
        """Look up weapon by name in bg_builder_weapons table."""
        cursor = self.conn.cursor()

        # Try exact match
        cursor.execute("""
            SELECT * FROM bg_builder_weapons
            WHERE LOWER(weapon_name) = LOWER(?)
            LIMIT 1
        """, (name,))

        result = cursor.fetchone()
        if result:
            return dict(result)

        # Try fuzzy match
        cursor.execute("""
            SELECT * FROM bg_builder_weapons
            WHERE LOWER(weapon_name) LIKE LOWER(?)
            ORDER BY LENGTH(weapon_name) ASC
            LIMIT 1
        """, (f'%{name}%',))

        result = cursor.fetchone()
        if result:
            weapon = dict(result)
            print(f"[FUZZY MATCH] '{name}' -> '{weapon['weapon_name']}'")
            return weapon

        print(f"[NOT FOUND] Weapon not in bg_builder_weapons: {name}")
        return None

    def convert_bg_builder_to_equipment(self, bg_vehicle: Dict) -> Dict:
        """
        Convert bg_builder_vehicles row to equipment format for datacard generator.

        Maps bg_builder schema to our equipment/equipment_battlegroup schema.
        """
        if not bg_vehicle:
            return None

        equipment = {
            'canonical_id': f"BG_BUILDER_{bg_vehicle['id']}",
            'name': bg_vehicle['name'],
            'nation': self.infer_nation_from_name(bg_vehicle['name']),
            'category': 'Armoured Fighting Vehicle',  # Assume AFV for now

            # Movement
            'off_road': bg_vehicle.get('movement_off_road', ''),
            'road': bg_vehicle.get('movement_road', ''),

            # Armor
            'armor_front': bg_vehicle.get('armor_front', ''),
            'armor_side': bg_vehicle.get('armor_side', ''),
            'armor_rear': bg_vehicle.get('armor_rear', ''),

            # Weapons (build armament table rows)
            'armament_rows': self.build_armament_rows(bg_vehicle),

            # Special rules
            'special_rules': self.extract_special_rules(bg_vehicle),

            # Points/BR (if available in bg_builder_vehicle_costs)
            'points_regular': None,
            'points_veteran': None,
            'br': None,
        }

        # Look up costs if available
        costs = self.lookup_vehicle_costs(bg_vehicle['id'])
        if costs:
            equipment['points_regular'] = costs.get('cost_regular')
            equipment['points_veteran'] = costs.get('cost_veteran')
            equipment['br'] = costs.get('br_veteran')

        return equipment

    def build_armament_rows(self, bg_vehicle: Dict) -> List[Dict]:
        """Build armament table rows from weapon data."""
        rows = []

        for i in range(1, 6):
            weapon_data_key = f'weapon_{i}_data'
            if weapon_data_key not in bg_vehicle or not bg_vehicle[weapon_data_key]:
                continue

            weapon = bg_vehicle[weapon_data_key]

            # Build HE string (e.g., "6D6 HE")
            he_effect = weapon.get('he_effect', '')
            he_type = weapon.get('he_type', '')
            he_str = f"{he_effect} {he_type}".strip() if he_effect or he_type else '-'

            # Build AP string (penetration at ranges)
            ap_values = []
            for range_col in ['ap_strength_0', 'ap_strength_10', 'ap_strength_20',
                              'ap_strength_30', 'ap_strength_40', 'ap_strength_50', 'ap_strength_70']:
                if range_col in weapon and weapon[range_col]:
                    ap_values.append(str(weapon[range_col]))
            ap_str = '/'.join(ap_values) if ap_values else '-'

            # HE range
            he_range_str = self.build_he_range_string(weapon)

            row = {
                'weapon': weapon.get('weapon_name', 'Unknown'),
                'he': he_str,
                'ap': ap_str,
                'he_range': he_range_str
            }
            rows.append(row)

        return rows

    def build_he_range_string(self, weapon: Dict) -> str:
        """Build HE range string (e.g., '0-10"/10-20"/20-30"')."""
        ranges = []

        # Standard range bands
        range_bands = [
            ('he_strength_0', '0-10"'),
            ('he_strength_10', '10-20"'),
            ('he_strength_20', '20-30"'),
            ('he_strength_30', '30-40"'),
            ('he_strength_40', '40-50"'),
            ('he_strength_50', '50-70"'),
        ]

        for col, label in range_bands:
            if col in weapon and weapon[col]:
                ranges.append(f"{weapon[col]}@{label}")

        return ' / '.join(ranges) if ranges else '-'

    def extract_special_rules(self, bg_vehicle: Dict) -> str:
        """Extract special rules from vehicle data."""
        rules = []

        if 'special_rules' in bg_vehicle and bg_vehicle['special_rules']:
            rules.append(bg_vehicle['special_rules'])

        # Check for specific indicators
        armor_front = bg_vehicle.get('armor_front')
        if armor_front and armor_front.upper() == 'OPEN':
            rules.append('Open-topped')

        return ', '.join(rules) if rules else None

    def lookup_vehicle_costs(self, vehicle_id: int) -> Dict:
        """Look up vehicle costs in bg_builder_vehicle_costs."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM bg_builder_vehicle_costs
            WHERE vehicle_id = ?
            LIMIT 1
        """, (vehicle_id,))

        result = cursor.fetchone()
        return dict(result) if result else None

    def infer_nation_from_name(self, name: str) -> str:
        """Infer nation from equipment name."""
        name_lower = name.lower()

        if any(word in name_lower for word in ['panzer', 'pz.kpfw', 'pak', 'flak', 'sdkfz', 'stug']):
            return 'german'
        elif any(word in name_lower for word in ['matilda', 'crusader', 'churchill', 'valentine', 'grant', 'stuart']):
            return 'british'
        elif any(word in name_lower for word in ['sherman', 'm3', 'm4', 'm5', 'm10', 'halftrack']):
            return 'american'
        elif any(word in name_lower for word in ['m13', 'm14', 'semovente', 'l3', 'l6', 'ab']):
            return 'italian'
        elif any(word in name_lower for word in ['char', 'somua', 'hotchkiss']):
            return 'french'
        else:
            return 'unknown'

    def generate_datacards_from_list(self, equipment_names: List[str], output_dir: Path):
        """
        Generate datacards for list of equipment names.

        Args:
            equipment_names: List of equipment names
            output_dir: Output directory for datacard markdown files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*70}")
        print(f"Generating datacards from army list")
        print(f"{'='*70}\n")

        # Look up each equipment item
        equipment_data = []
        for name in equipment_names:
            print(f"Looking up: {name}")

            # Try vehicle lookup first
            bg_vehicle = self.lookup_bg_builder_vehicle(name)
            if bg_vehicle:
                equipment = self.convert_bg_builder_to_equipment(bg_vehicle)
                if equipment:
                    equipment_data.append(equipment)
                    print(f"  [OK] Found vehicle: {equipment['name']}")
                continue

            # Try weapon lookup
            bg_weapon = self.lookup_bg_builder_weapon_by_name(name)
            if bg_weapon:
                # Weapons need different handling - treat as towed guns
                equipment = {
                    'canonical_id': f"BG_WEAPON_{bg_weapon['weapon_id']}",
                    'name': bg_weapon['weapon_name'],
                    'nation': self.infer_nation_from_name(bg_weapon['weapon_name']),
                    'category': 'Towed Gun',
                    'armament_rows': [{
                        'weapon': bg_weapon['weapon_name'],
                        'he': f"{bg_weapon.get('he_effect', '')} {bg_weapon.get('he_type', '')}".strip(),
                        'ap': '/'.join([str(bg_weapon.get(f'ap_strength_{r}', '')) for r in [0, 10, 20, 30, 40, 50, 70] if bg_weapon.get(f'ap_strength_{r}')]),
                        'he_range': '-'
                    }],
                    'special_rules': None,
                }
                equipment_data.append(equipment)
                print(f"  [OK] Found weapon: {equipment['name']}")
                continue

            print(f"  [X] Not found in database")

        if not equipment_data:
            print("\n[ERROR] No equipment found in database")
            return

        print(f"\nFound {len(equipment_data)}/{len(equipment_names)} equipment items")

        # Generate datacards by category
        categorized = self.categorize_equipment(equipment_data)

        for category, items in categorized.items():
            if not items:
                continue

            print(f"\n{category}: {len(items)} items")

            # Generate markdown file
            category_file = category.lower().replace(' ', '_').replace('&', 'and') + '.md'
            output_file = output_dir / category_file

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# {category}\n\n")
                f.write(self.get_v55_css())
                f.write('\n<div class="datacard-grid">\n\n')

                for equipment in items:
                    datacard_md = self.generate_v55_datacard(equipment)
                    f.write(datacard_md)
                    f.write('\n')

                f.write("</div>\n")

            print(f"  -> {output_file.name}")

        print(f"\n{'='*70}")
        print(f"Datacard generation complete")
        print(f"{'='*70}\n")

    def categorize_equipment(self, equipment_list: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize equipment for organization."""
        categories = {
            'Tanks': [],
            'Guns & Artillery': [],
            'Vehicles': [],
            'Other Equipment': []
        }

        for eq in equipment_list:
            category = eq.get('category', '')

            if 'tank' in category.lower() or 'afv' in category.lower() or 'armoured' in category.lower():
                categories['Tanks'].append(eq)
            elif 'gun' in category.lower() or 'artillery' in category.lower():
                categories['Guns & Artillery'].append(eq)
            elif 'vehicle' in category.lower() or 'transport' in category.lower():
                categories['Vehicles'].append(eq)
            else:
                categories['Other Equipment'].append(eq)

        return categories

    def generate_v55_datacard(self, equipment: Dict) -> str:
        """
        Generate V5.5 format datacard markdown.

        Simplified version - full implementation would call existing generator.
        """
        nation = equipment.get('nation', 'unknown')
        name = equipment.get('name', 'Unknown')

        # Build datacard HTML
        html = f'<div class="datacard datacard-{nation}">\n'
        html += '  <div class="datacard-header">\n'
        html += f'    <div class="datacard-title-block">\n'
        html += f'      <p class="datacard-title">{name.upper()}</p>\n'

        # Special rules
        if equipment.get('special_rules'):
            html += f'      <p class="datacard-special-rules">{equipment["special_rules"]}</p>\n'

        html += '    </div>\n'
        html += '  </div>\n'

        # Armor table
        armor_front = equipment.get('armor_front', '-')
        armor_side = equipment.get('armor_side', '-')
        armor_rear = equipment.get('armor_rear', '-')

        html += '  <table>\n'
        html += '    <tr>\n'
        html += '      <th>Front</th><th>Side</th><th>Rear</th>\n'
        html += '    </tr>\n'
        html += '    <tr>\n'
        html += f'      <td>{armor_front}</td><td>{armor_side}</td><td>{armor_rear}</td>\n'
        html += '    </tr>\n'
        html += '  </table>\n'

        # Armament table
        if equipment.get('armament_rows'):
            html += '  <table>\n'
            html += '    <tr>\n'
            html += '      <th>Weapon</th><th>HE</th><th>AP</th><th>HE Range</th>\n'
            html += '    </tr>\n'

            for row in equipment['armament_rows']:
                html += '    <tr>\n'
                html += f'      <td>{row.get("weapon", "-")}</td>\n'
                html += f'      <td>{row.get("he", "-")}</td>\n'
                html += f'      <td>{row.get("ap", "-")}</td>\n'
                html += f'      <td>{row.get("he_range", "-")}</td>\n'
                html += '    </tr>\n'

            html += '  </table>\n'

        # Movement table
        off_road = equipment.get('off_road', '-')
        road = equipment.get('road', '-')

        html += '  <table>\n'
        html += '    <tr>\n'
        html += '      <th>Off-Road</th><th>Road</th>\n'
        html += '    </tr>\n'
        html += '    <tr>\n'
        html += f'      <td>{off_road}"</td><td>{road}"</td>\n'
        html += '    </tr>\n'
        html += '  </table>\n'

        # Footer (points/BR if available)
        if equipment.get('points_veteran') or equipment.get('br'):
            html += '  <div class="datacard-footer">\n'
            if equipment.get('points_veteran'):
                html += f'    <div class="footer-stat">Points: {equipment["points_veteran"]}</div>\n'
            if equipment.get('br'):
                html += f'    <div class="footer-stat">BR: {equipment["br"]}</div>\n'
            html += '  </div>\n'

        html += '</div>\n'

        return html

    def get_v55_css(self) -> str:
        """Return V5.5 datacard CSS (simplified version)."""
        return """<style>
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

.datacard.datacard-german {
    background-color: #797768;
    border-color: #1a1a1a;
}

.datacard.datacard-german .datacard-title,
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

.datacard-title {
    font-weight: bold;
    font-size: 16px;
    margin: 0 0 5px 0;
    line-height: 1.2;
    text-align: center;
}

.datacard-special-rules {
    font-size: 9px;
    font-style: italic;
    margin: 2px 0;
    line-height: 1.2;
    color: #5a4a3a;
    text-align: center;
}

.datacard table {
    width: 100%;
    border-collapse: collapse;
    margin: 5px 0;
    font-size: 8px;
}

.datacard th {
    background-color: #8b7355;
    color: white;
    font-weight: bold;
    padding: 2px;
    border: 1px solid #2c2416;
    text-align: center;
    font-size: 8px;
}

.datacard td {
    background-color: #f5f5dc;
    border: 1px solid #2c2416;
    padding: 2px;
    text-align: center;
    font-size: 8px;
}

.datacard-footer {
    display: flex;
    justify-content: space-around;
    margin-top: 5px;
    font-size: 9px;
    font-weight: bold;
}
</style>

---

"""


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate BattleGroup datacards from army list",
        epilog="""
Examples:
  %(prog)s --input my_army.txt --output datacards/
  %(prog)s --equipment "Panzer III,Panzer IV,88mm FlaK" --output test/

Input file format (one equipment per line):
  Panzer III
  Panzer IV
  88mm FlaK 18/36
  Matilda II

Or with quantities (ignored for datacard generation):
  3x Panzer III
  2x Panzer IV
  1x 88mm FlaK 18/36
        """
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Input text file with equipment list (one per line)"
    )
    parser.add_argument(
        "--equipment",
        type=str,
        help="Comma-separated equipment names (alternative to --input)"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output directory for datacard markdown files"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.input and not args.equipment:
        parser.error("Must specify --input or --equipment")

    # Read equipment list
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.equipment

    generator = ArmyListDatacardGenerator()

    try:
        # Parse equipment names
        equipment_names = generator.parse_army_list_text(text)

        if not equipment_names:
            print("[ERROR] No equipment names found in input")
            return 1

        print(f"Parsed {len(equipment_names)} equipment items:")
        for name in equipment_names:
            print(f"  - {name}")
        print()

        # Generate datacards
        generator.generate_datacards_from_list(equipment_names, args.output)

    finally:
        generator.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
