#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 9B Phase 2.3: BG Builder JSON Export

Exports scenarios to BattlegroupBuilder.io compatible JSON format.

Allows users to:
1. Export complete scenarios to BG Builder format
2. Import scenarios back into BattlegroupBuilder.io
3. Share scenarios with other players
4. Use BG Builder web interface for force customization

Export Format (BG Builder compatible):
{
  "name": "Fort Capuzzo Defense",
  "forceName": "German Panzer Division Battlegroup",
  "battleRating": 42,
  "units": [
    {
      "name": "Panzer III",
      "quantity": 3,
      "cost": 30,
      "br": 3,
      "options": ["Veteran"]
    }
  ],
  "metadata": {
    "source": "North Africa TO&E Builder",
    "scenario": "Fort Capuzzo",
    "date": "1941q2"
  }
}

Author: North Africa TO&E Builder
Date: November 11, 2025
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
SCENARIOS_DIR = Path("D:/north-africa-toe-builder/data/output/bg_builder_scenarios")
EXPORT_DIR = Path("D:/north-africa-toe-builder/data/bg_builder_exports")

class BGBuilderExporter:
    """Export scenarios to BG Builder JSON format."""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        self.conn.close()

    def load_complete_scenario(self, scenario_path: Path) -> Optional[Dict]:
        """Load complete scenario JSON."""
        try:
            with open(scenario_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def export_force_to_bg_builder(self, force_data: Dict, scenario_metadata: Dict) -> Dict:
        """
        Export single force to BG Builder format.

        Args:
            force_data: Force dictionary from scenario
            scenario_metadata: Scenario metadata

        Returns:
            BG Builder compatible JSON
        """
        bg_builder = {
            "name": scenario_metadata.get('title', 'Exported Force'),
            "forceName": force_data.get('force_name', 'Unknown Force'),
            "battleRating": force_data.get('battle_rating', 0),
            "totalPoints": force_data.get('total_points', 0),
            "units": [],
            "metadata": {
                "source": "North Africa TO&E Builder - Phase 9B",
                "scenario": scenario_metadata.get('location', 'Unknown'),
                "date": scenario_metadata.get('quarter', 'Unknown'),
                "export_date": "2025-11-11",
                "original_file": scenario_metadata.get('import_file', 'Unknown')
            }
        }

        # Export units
        for unit in force_data.get('units', []):
            bg_unit = {
                "name": unit.get('name', 'Unknown'),
                "quantity": unit.get('quantity', 1),
                "cost": unit.get('cost_per_unit', 0),
                "br": unit.get('br_per_unit', 0),
                "options": unit.get('options', [])
            }

            # Add vehicle_id if available for re-import
            if unit.get('vehicle_id'):
                bg_unit['vehicle_id'] = unit['vehicle_id']

            bg_builder['units'].append(bg_unit)

        return bg_builder

    def export_scenario_both_forces(self, scenario: Dict) -> Dict:
        """
        Export scenario with both attacker and defender forces.

        Args:
            scenario: Complete scenario dictionary

        Returns:
            Dictionary with attacker and defender exports
        """
        exports = {
            "scenario_title": scenario.get('title', 'Unknown'),
            "location": scenario.get('location', 'Unknown'),
            "date": scenario.get('quarter', 'Unknown'),
            "forces": {}
        }

        # Export each force
        for nation, force_data in scenario.get('forces', {}).items():
            exports['forces'][nation] = self.export_force_to_bg_builder(
                force_data,
                scenario
            )

        # Add scenario details
        exports['scenario_details'] = {
            "table_size": scenario.get('table_size', '6x4 feet'),
            "turn_limit": scenario.get('turn_limit', 10),
            "terrain": scenario.get('terrain', 'Desert'),
            "weather": scenario.get('weather', 'Clear'),
            "victory_conditions": scenario.get('victory_conditions', []),
            "special_rules": scenario.get('special_rules', [])
        }

        return exports

    def export_all_scenarios(self) -> int:
        """
        Export all complete scenarios to BG Builder format.

        Returns:
            Number of scenarios exported
        """
        if not SCENARIOS_DIR.exists():
            print(f"No scenarios directory: {SCENARIOS_DIR}")
            return 0

        # Create export directory
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        # Find complete scenarios
        complete_scenarios = list(SCENARIOS_DIR.glob('complete_*.json'))
        print(f"Found {len(complete_scenarios)} complete scenarios")

        exported = 0

        for scenario_file in complete_scenarios:
            print(f"\nExporting: {scenario_file.name}")

            # Load scenario
            scenario = self.load_complete_scenario(scenario_file)
            if not scenario:
                continue

            # Export both forces
            exports = self.export_scenario_both_forces(scenario)

            # Save complete export
            export_file = EXPORT_DIR / f"bg_builder_{scenario_file.stem}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(exports, f, indent=2)

            print(f"  Exported to: {export_file.name}")
            print(f"  Forces: {list(exports['forces'].keys())}")

            # Save individual force exports (for direct BG Builder import)
            for nation, force_export in exports['forces'].items():
                force_file = EXPORT_DIR / f"bg_builder_{nation}_{scenario['quarter']}_{scenario['location'].replace(' ', '_').lower()}.json"
                with open(force_file, 'w', encoding='utf-8') as f:
                    json.dump(force_export, f, indent=2)

                print(f"  {nation.title()}: {force_file.name}")

            exported += 1

        return exported

    def generate_import_instructions(self) -> str:
        """Generate instructions for importing to BattlegroupBuilder.io."""
        instructions = """
# BattleGroup Builder Import Instructions

## How to Import These Forces to BattlegroupBuilder.io

1. Open https://osjones.github.io/BattlegroupBuilder/

2. Click the "Import" or "Load List" button (typically in top menu)

3. Select one of the force JSON files:
   - `bg_builder_german_*.json` - German forces
   - `bg_builder_british_*.json` - British forces
   - `bg_builder_italian_*.json` - Italian forces

4. The force will load with:
   - All units pre-selected
   - Correct points costs
   - Battle Rating calculated
   - Troop quality options (Veteran/Regular/Elite)

5. Customize the force:
   - Add/remove units
   - Adjust troop quality
   - Add special rules or upgrades
   - View army list printout

6. Export back:
   - Use "Export" button to save customized list
   - Import back to North Africa TO&E Builder with bg_builder_import.py

## File Format

Each force file contains:
```json
{
  "name": "Force Name",
  "forceName": "BattleGroup Type",
  "battleRating": 42,
  "totalPoints": 190,
  "units": [...]
}
```

## Scenario Files

Complete scenario exports include both forces:
- `bg_builder_complete_scenario_*.json` - Full scenario with attacker/defender

These include:
- Both forces (attacker and defender)
- Terrain setup
- Victory conditions
- Special rules
- Turn limit and table size

## Re-importing to Phase 9B

To re-import customized forces:

1. Export from BG Builder (same JSON format)
2. Place in `data/bg_builder_imports/`
3. Run: `python scripts/phase9b/bg_builder_import.py`
4. Generate scenario: `python scripts/phase9b/scenario_auto_generator.py`

This creates a bidirectional workflow between Phase 9B and BattlegroupBuilder.io!
"""
        return instructions

def main():
    """Main execution."""
    print("="*80)
    print("PHASE 9B PHASE 2.3: BG BUILDER JSON EXPORT")
    print("="*80)

    exporter = BGBuilderExporter()

    try:
        # Export all scenarios
        exported = exporter.export_all_scenarios()

        if exported > 0:
            print(f"\n✓ Exported {exported} scenarios")
            print(f"✓ Saved to: {EXPORT_DIR}")

            # Generate import instructions
            instructions = exporter.generate_import_instructions()
            instructions_file = EXPORT_DIR / "IMPORT_INSTRUCTIONS.md"
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(instructions)

            print(f"\n✓ Import instructions: {instructions_file.name}")

            # List exported files
            print("\nExported files:")
            for export_file in sorted(EXPORT_DIR.glob('*.json')):
                print(f"  {export_file.name}")

        else:
            print("\nNo complete scenarios found.")
            print("Run scenario_auto_generator.py first to generate scenarios.")

        print("\n" + "="*80)
        print("✅ EXPORT COMPLETE")
        print("="*80)

    finally:
        exporter.close()

if __name__ == '__main__':
    main()
