#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 9B Phase 2.1: BG Builder JSON Import Parser

Parses army list JSON files exported from https://osjones.github.io/BattlegroupBuilder/
to create scenarios with historical context from Phase 6 data.

JSON Format (from BG Builder):
{
  "name": "German Panzer Company",
  "forceName": "German Panzer Division Battlegroup",
  "battleRating": 45,
  "units": [
    {
      "name": "Panzer III",
      "quantity": 3,
      "cost": 30,
      "br": 3,
      "options": ["Veteran"]
    }
  ]
}

Output: Enhanced scenario JSON with Phase 6 historical context

Author: North Africa TO&E Builder
Date: November 11, 2025
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
IMPORTS_DIR = Path("D:/north-africa-toe-builder/data/bg_builder_imports")

@dataclass
class BGBuilderUnit:
    """Unit from BG Builder army list."""
    name: str
    quantity: int
    cost: int
    br: int
    options: List[str]
    vehicle_id: Optional[int] = None

@dataclass
class BGBuilderArmyList:
    """Army list from BG Builder."""
    name: str
    force_name: str
    battle_rating: int
    total_points: int
    units: List[BGBuilderUnit]
    import_date: str
    import_file: str

class BGBuilderImporter:
    """Import and parse BG Builder army lists."""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        self.conn.close()

    def parse_json(self, json_path: Path) -> Optional[BGBuilderArmyList]:
        """
        Parse BG Builder JSON export.

        Args:
            json_path: Path to JSON file

        Returns:
            BGBuilderArmyList object or None if parse failed
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {json_path}: {e}")
            return None

        # Parse units
        units = []
        total_points = 0

        for unit_data in data.get('units', []):
            unit = BGBuilderUnit(
                name=unit_data.get('name', 'Unknown'),
                quantity=unit_data.get('quantity', 1),
                cost=unit_data.get('cost', 0),
                br=unit_data.get('br', 0),
                options=unit_data.get('options', [])
            )
            units.append(unit)
            total_points += unit.cost * unit.quantity

        army_list = BGBuilderArmyList(
            name=data.get('name', 'Unnamed Force'),
            force_name=data.get('forceName', 'Unknown'),
            battle_rating=data.get('battleRating', 0),
            total_points=total_points,
            units=units,
            import_date='2025-11-11',  # Current date
            import_file=json_path.name
        )

        return army_list

    def link_units_to_database(self, army_list: BGBuilderArmyList) -> int:
        """
        Link army list units to bg_builder_vehicles.

        Args:
            army_list: BGBuilderArmyList object

        Returns:
            Number of units successfully linked
        """
        cursor = self.conn.cursor()
        linked = 0

        for unit in army_list.units:
            # Try to find matching vehicle in bg_builder_vehicles
            cursor.execute('''
                SELECT id FROM bg_builder_vehicles
                WHERE LOWER(REPLACE(name, '.', '')) = LOWER(REPLACE(?, '.', ''))
                LIMIT 1
            ''', (unit.name,))

            row = cursor.fetchone()
            if row:
                unit.vehicle_id = row['id']
                linked += 1

        return linked

    def generate_scenario_from_army_list(self, army_list: BGBuilderArmyList,
                                         quarter: str, nation: str) -> Dict:
        """
        Generate enhanced scenario JSON from army list + Phase 6 historical context.

        Args:
            army_list: BGBuilderArmyList object
            quarter: Quarter identifier (e.g., "1941q2")
            nation: Nation code (german, british, italian)

        Returns:
            Enhanced scenario dictionary with historical context
        """
        cursor = self.conn.cursor()

        # Get historical units from Phase 6 for this quarter/nation
        # Note: units table uses '1941-Q2' format, need to convert from '1941q2'
        quarter_formatted = quarter[:4] + '-Q' + quarter[5]  # '1941q2' -> '1941-Q2'

        cursor.execute('''
            SELECT designation, unit_type, organization_level
            FROM units
            WHERE nation = ? AND quarter = ?
            ORDER BY organization_level DESC
            LIMIT 5
        ''', (nation, quarter_formatted))

        historical_units = [dict(row) for row in cursor.fetchall()]

        # Build scenario
        scenario = {
            'title': army_list.name,
            'date': quarter,
            'location': 'North Africa',
            'forces': {
                nation: {
                    'force_name': army_list.force_name,
                    'battle_rating': army_list.battle_rating,
                    'total_points': army_list.total_points,
                    'units': []
                }
            },
            'historical_context': {
                'quarter': quarter,
                'nation': nation,
                'referenced_units': historical_units
            },
            'metadata': {
                'import_source': 'bg_builder',
                'import_file': army_list.import_file,
                'import_date': army_list.import_date,
                'generated_by': 'Phase 9B BG Builder Importer'
            }
        }

        # Add units
        for unit in army_list.units:
            scenario['forces'][nation]['units'].append({
                'name': unit.name,
                'quantity': unit.quantity,
                'cost_per_unit': unit.cost,
                'br_per_unit': unit.br,
                'total_cost': unit.cost * unit.quantity,
                'total_br': unit.br * unit.quantity,
                'options': unit.options,
                'vehicle_id': unit.vehicle_id
            })

        return scenario

    def import_directory(self, imports_dir: Path) -> List[Dict]:
        """
        Import all JSON files from directory.

        Args:
            imports_dir: Directory containing BG Builder JSON exports

        Returns:
            List of generated scenario dictionaries
        """
        if not imports_dir.exists():
            print(f"Imports directory not found: {imports_dir}")
            return []

        json_files = list(imports_dir.glob('*.json'))
        print(f"Found {len(json_files)} JSON files in {imports_dir}")

        scenarios = []

        for json_file in json_files:
            print(f"\nProcessing: {json_file.name}")

            # Parse JSON
            army_list = self.parse_json(json_file)
            if not army_list:
                continue

            # Link units to database
            linked = self.link_units_to_database(army_list)
            print(f"  Linked {linked}/{len(army_list.units)} units to database")

            # Infer quarter and nation from filename or force name
            # Example: "german_1941q2_panzer_company.json"
            filename_lower = json_file.stem.lower()
            quarter = '1941q2'  # Default
            nation = 'german'   # Default

            if 'british' in filename_lower:
                nation = 'british'
            elif 'italian' in filename_lower:
                nation = 'italian'
            elif 'german' in filename_lower:
                nation = 'german'

            # Extract quarter from filename
            import re
            quarter_match = re.search(r'(19\d{2}q[1-4])', filename_lower)
            if quarter_match:
                quarter = quarter_match.group(1)

            # Generate scenario
            scenario = self.generate_scenario_from_army_list(army_list, quarter, nation)
            scenarios.append(scenario)

            print(f"  Generated scenario: {scenario['title']}")
            print(f"  Battle Rating: {army_list.battle_rating}, Points: {army_list.total_points}")

        return scenarios

def main():
    """Main execution."""
    print("="*80)
    print("PHASE 9B PHASE 2.1: BG BUILDER JSON IMPORT PARSER")
    print("="*80)

    # Create imports directory if not exists
    IMPORTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nImports directory: {IMPORTS_DIR}")

    importer = BGBuilderImporter()

    try:
        # Import all JSON files
        scenarios = importer.import_directory(IMPORTS_DIR)

        if scenarios:
            # Save scenarios to output
            output_dir = Path("D:/north-africa-toe-builder/data/output/bg_builder_scenarios")
            output_dir.mkdir(parents=True, exist_ok=True)

            for i, scenario in enumerate(scenarios):
                output_file = output_dir / f"scenario_{i+1}_{scenario['title'].replace(' ', '_').lower()}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(scenario, f, indent=2)

            print(f"\n✓ Generated {len(scenarios)} scenarios")
            print(f"✓ Saved to: {output_dir}")
        else:
            print("\nNo JSON files found to import.")
            print(f"Place BG Builder JSON exports in: {IMPORTS_DIR}")
            print("\nExample JSON format:")
            print(json.dumps({
                "name": "German Panzer Company",
                "forceName": "German Panzer Division Battlegroup",
                "battleRating": 45,
                "units": [
                    {
                        "name": "Panzer III",
                        "quantity": 3,
                        "cost": 30,
                        "br": 3,
                        "options": ["Veteran"]
                    }
                ]
            }, indent=2))

        print("\n" + "="*80)
        print("✅ IMPORT COMPLETE")
        print("="*80)

    finally:
        importer.close()

if __name__ == '__main__':
    main()
