#!/usr/bin/env python3
"""
WITW (War in the West) Scenario Exporter

Purpose: Generate WITW-compatible scenario files with enhanced data
- Equipment CSVs with WITW IDs
- Supply states (fuel, ammo, water)
- Weather/environment conditions
- Air support integration
- Battle narratives and victory conditions

Enhanced in Phase 9A (October 2025):
- Added supply_status integration from Schema v3.0
- Added weather_environment integration from Schema v3.0
- Added air_support references from Phase 8 cross-linking
- Refactored into pluggable architecture (inherits from ScenarioExporter)
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from base.scenario_exporter import ScenarioExporter
from typing import Dict, List, Optional
import csv
import json
from datetime import datetime

class WITWExporter(ScenarioExporter):
    """War in the West scenario exporter"""

    def __init__(self, project_root: Path = None):
        super().__init__(project_root)
        self.game_name = "witw"
        self.output_dir = self.scenarios_dir / self.game_name

    def format_equipment_data(self, unit_data: Dict) -> List[Dict]:
        """
        Convert unit equipment data to WITW CSV format

        Returns list of equipment rows with:
        - equipment_id (WITW ID)
        - equipment_name
        - equipment_type
        - count
        - section
        - ready (operational)
        - damaged
        - operational_readiness (percentage)
        """
        equipment_rows = []

        # Equipment sections to export
        equipment_sections = [
            'tanks',
            'armored_cars',
            'artillery',
            'anti_tank_guns',
            'anti_aircraft_guns',
            'ground_vehicles',
            'aircraft',
            'halftracks',
            'trucks',
            'motorcycles',
            'field_artillery',
            'anti_tank',
            'anti_aircraft'
        ]

        for section in equipment_sections:
            if section not in unit_data:
                continue

            section_data = unit_data[section]
            if not isinstance(section_data, dict):
                continue

            # Handle nested variant structure (Architecture v3.0+)
            if 'variants' in section_data:
                equipment_rows.extend(
                    self._process_variants(section_data['variants'], section, unit_data.get('nation', 'unknown'))
                )

            # Handle tank subcategories (heavy_tanks, medium_tanks, light_tanks)
            elif 'heavy_tanks' in section_data or 'medium_tanks' in section_data or 'light_tanks' in section_data:
                for tank_category in ['heavy_tanks', 'medium_tanks', 'light_tanks']:
                    if tank_category not in section_data:
                        continue

                    tank_cat_data = section_data[tank_category]
                    if 'variants' not in tank_cat_data:
                        continue

                    equipment_rows.extend(
                        self._process_variants(tank_cat_data['variants'], 'tanks', unit_data.get('nation', 'unknown'))
                    )

        return equipment_rows

    def _process_variants(self, variants: Dict, section: str, nation: str) -> List[Dict]:
        """Process equipment variants into WITW format"""
        rows = []

        for equipment_name, equipment_info in variants.items():
            if not isinstance(equipment_info, dict):
                continue

            count = equipment_info.get('count', 0)
            if count == 0:
                continue

            operational = equipment_info.get('operational', count)

            # Generate WITW ID from nation and equipment name
            witw_id = f"{nation.upper()[:3]}_{equipment_name.upper().replace(' ', '_').replace('-', '_')}"

            # Calculate operational readiness
            readiness = int((operational / count * 100) if count > 0 else 100)

            rows.append({
                'equipment_id': witw_id,
                'equipment_name': equipment_name,
                'equipment_type': section,
                'count': count,
                'section': section,
                'ready': operational,
                'damaged': count - operational,
                'operational_readiness': readiness
            })

        return rows

    def generate_narrative(self, metadata: Dict, unit_data: Dict,
                          supply: Dict, environment: Dict, air_support: Optional[Dict]) -> Dict:
        """
        Generate WITW scenario narrative with enhanced data

        Includes:
        - Historical situation
        - Axis and Allied objectives
        - Supply states
        - Weather/environment conditions
        - Air support summary
        - Special rules
        """
        narrative = {
            'title': f"{metadata['unit_designation']} - {metadata['quarter'].upper()}",
            'date': metadata['date'],
            'location': metadata['theater'],
            'nation': metadata['nation'],
            'unit_type': metadata['unit_type'],
        }

        # Historical situation
        if 'historical_context' in unit_data:
            historical = unit_data['historical_context']
            if isinstance(historical, dict):
                narrative['situation'] = historical.get('formation',
                    f"{metadata['nation']} {metadata['unit_type']} deployed in {metadata['theater']} during {metadata['quarter'].upper()}.")
            else:
                narrative['situation'] = str(historical)
        else:
            narrative['situation'] = f"{metadata['nation']} {metadata['unit_type']} deployed in {metadata['theater']} during {metadata['quarter'].upper()}."

        # Objectives (customized by unit data if available)
        if 'tactical_doctrine' in unit_data:
            doctrine = unit_data['tactical_doctrine']
            narrative['objectives'] = doctrine.get('role', 'Secure assigned objectives')

        # Default objectives by nation
        if metadata['nation'].lower() in ['german', 'italian']:
            narrative['axis_objective'] = "Maintain defensive positions and inflict maximum casualties on Allied forces."
            narrative['allied_objective'] = "Advance and secure strategic objectives while minimizing casualties."
        else:
            narrative['axis_objective'] = "Hold current positions and prevent Allied breakthrough."
            narrative['allied_objective'] = "Advance and neutralize Axis defensive positions."

        # Supply states (Phase 9A enhancement)
        narrative['supply'] = {
            'fuel_days': supply.get('fuel_days') or supply.get('fuel_reserves_days', 'Unknown'),
            'ammunition_days': supply.get('ammunition_days') or supply.get('ammunition_stock_days', 'Unknown'),
            'water_supply': supply.get('water_liters_per_day') or supply.get('water_liters_per_man', 'Unknown'),
            'supply_status': supply.get('supply_line_status', 'Unknown'),
            'notes': supply.get('notes', '')
        }

        # Weather/environment (Phase 9A enhancement)
        narrative['weather'] = {
            'terrain': environment.get('terrain_type', 'Desert'),
            'temperature': environment.get('temperature_range_celsius', 'Unknown'),
            'visibility': environment.get('visibility_conditions', 'Clear'),
            'seasonal_impacts': environment.get('seasonal_impacts', []),
            'environmental_challenges': environment.get('environmental_challenges', [])
        }

        # Air support (Phase 9A enhancement)
        if air_support and air_support.get('summary'):
            air_summary = air_support['summary']
            aggregate = air_summary.get('aggregate_strength', {})

            narrative['air_support'] = {
                'theater_command': air_summary.get('air_command_structure', {}).get('theater_command', {}).get('designation', 'Unknown'),
                'total_aircraft': aggregate.get('total_aircraft', 0),
                'operational_aircraft': aggregate.get('operational_aircraft', 0),
                'serviceability_rate': aggregate.get('serviceability_rate', 'Unknown'),
                'summary_file': air_support['reference'].get('data_source', {}).get('summary_file', 'Unknown')
            }
        else:
            narrative['air_support'] = {
                'note': 'No theater air summary available for this quarter'
            }

        # Special rules
        narrative['special_rules'] = []
        if 'tactical_doctrine' in unit_data and 'special_capabilities' in unit_data['tactical_doctrine']:
            narrative['special_rules'] = unit_data['tactical_doctrine']['special_capabilities']

        return narrative

    def export_scenario(self, unit_file_path: Path) -> Dict:
        """
        Export WITW scenario from unit JSON

        Creates:
        - equipment.csv (WITW equipment list)
        - scenario_metadata.json (complete scenario data)
        - README.md (human-readable scenario description)
        """
        filename = unit_file_path.name
        print(f"\nExporting WITW scenario: {filename}")

        # Load unit data
        unit_data = self.load_unit_json(unit_file_path)

        # Extract metadata
        metadata = self.extract_scenario_metadata(unit_data, filename)
        if not metadata:
            print(f"  [SKIP] Cannot extract metadata from {filename}")
            return None

        scenario_name = f"{metadata['nation']}_{metadata['quarter']}_{metadata['unit_designation'].replace(' ', '_')}"
        print(f"  Scenario name: {scenario_name}")

        # Extract enhanced data (Phase 9A)
        supply = self.extract_supply_states(unit_data)
        environment = self.extract_weather_environment(unit_data)
        air_support = self.extract_air_support(unit_data)

        # Generate equipment CSV
        equipment_csv = self.format_equipment_data(unit_data)
        print(f"  Equipment items: {len(equipment_csv)}")

        # Generate narrative
        narrative = self.generate_narrative(metadata, unit_data, supply, environment, air_support)

        # Create scenario directory
        scenario_dir = self.output_dir / scenario_name
        scenario_dir.mkdir(parents=True, exist_ok=True)

        # Write equipment CSV
        equipment_csv_file = scenario_dir / 'equipment.csv'
        with open(equipment_csv_file, 'w', newline='', encoding='utf-8') as f:
            if equipment_csv:
                fieldnames = ['equipment_id', 'equipment_name', 'equipment_type', 'count',
                             'section', 'ready', 'damaged', 'operational_readiness']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(equipment_csv)
        print(f"  [OK] Wrote equipment CSV: {equipment_csv_file.name}")

        # Write scenario metadata (enhanced with supply/weather/air)
        metadata_file = scenario_dir / 'scenario_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': metadata,
                'narrative': narrative,
                'supply_states': supply,
                'environment': environment,
                'air_support': air_support['reference'] if air_support else None,
                'exported_at': datetime.now().isoformat(),
                'source_file': filename,
                'exporter_version': 'Phase 9A Enhanced (October 2025)'
            }, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Wrote scenario metadata: {metadata_file.name}")

        # Write README with enhanced battle context
        readme_file = scenario_dir / 'README.md'
        self._write_readme(readme_file, narrative, equipment_csv, supply, environment, air_support)
        print(f"  [OK] Wrote README: {readme_file.name}")

        return {
            'scenario_name': scenario_name,
            'equipment_count': len(equipment_csv),
            'scenario_dir': str(scenario_dir),
            'has_supply_data': bool(supply),
            'has_weather_data': bool(environment),
            'has_air_support': bool(air_support and air_support.get('summary'))
        }

    def _write_readme(self, readme_file: Path, narrative: Dict, equipment_csv: List[Dict],
                     supply: Dict, environment: Dict, air_support: Optional[Dict]):
        """Write enhanced README with supply/weather/air support"""
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(f"# {narrative['title']}\n\n")
            f.write(f"**Date**: {narrative['date']}\n")
            f.write(f"**Location**: {narrative['location']}\n")
            f.write(f"**Nation**: {narrative['nation']}\n")
            f.write(f"**Unit Type**: {narrative['unit_type']}\n\n")

            f.write(f"## Situation\n\n{narrative['situation']}\n\n")

            f.write(f"## Objectives\n\n")
            f.write(f"### Axis\n{narrative['axis_objective']}\n\n")
            f.write(f"### Allied\n{narrative['allied_objective']}\n\n")

            # Supply states (Phase 9A enhancement)
            f.write(f"## Supply States\n\n")
            supply_data = narrative.get('supply', {})
            f.write(f"- **Fuel**: {supply_data.get('fuel_days', 'Unknown')} days\n")
            f.write(f"- **Ammunition**: {supply_data.get('ammunition_days', 'Unknown')} days\n")
            f.write(f"- **Water**: {supply_data.get('water_supply', 'Unknown')} liters/day\n")
            f.write(f"- **Supply Status**: {supply_data.get('supply_status', 'Unknown')}\n")
            if supply_data.get('notes'):
                f.write(f"- **Notes**: {supply_data['notes']}\n")
            f.write("\n")

            # Weather/environment (Phase 9A enhancement)
            f.write(f"## Weather & Environment\n\n")
            weather = narrative.get('weather', {})
            f.write(f"- **Terrain**: {weather.get('terrain', 'Unknown')}\n")
            f.write(f"- **Temperature**: {weather.get('temperature', 'Unknown')}\n")
            f.write(f"- **Visibility**: {weather.get('visibility', 'Unknown')}\n")
            if weather.get('seasonal_impacts'):
                f.write(f"- **Seasonal Impacts**: {', '.join(weather['seasonal_impacts'])}\n")
            if weather.get('environmental_challenges'):
                f.write(f"- **Challenges**: {', '.join(weather['environmental_challenges'])}\n")
            f.write("\n")

            # Air support (Phase 9A enhancement)
            f.write(f"## Air Support\n\n")
            air = narrative.get('air_support', {})
            if 'note' in air:
                f.write(f"{air['note']}\n\n")
            else:
                f.write(f"- **Theater Command**: {air.get('theater_command', 'Unknown')}\n")
                f.write(f"- **Total Aircraft**: {air.get('total_aircraft', 0)}\n")
                f.write(f"- **Operational**: {air.get('operational_aircraft', 0)}\n")
                f.write(f"- **Serviceability**: {air.get('serviceability_rate', 'Unknown')}\n")
                f.write(f"- **Data Source**: {air.get('summary_file', 'Unknown')}\n\n")

            # Special rules
            if narrative.get('special_rules'):
                f.write(f"## Special Rules\n\n")
                for rule in narrative['special_rules']:
                    f.write(f"- {rule}\n")
                f.write("\n")

            # Equipment summary
            f.write(f"## Equipment\n\n")
            f.write(f"Total equipment items: {len(equipment_csv)}\n\n")
            f.write(f"See `equipment.csv` for complete WITW equipment list.\n")


def main():
    """Export all WITW scenarios with enhanced Phase 9A data"""
    exporter = WITWExporter()
    results = exporter.export_all_scenarios()

    # Print enhancement statistics
    enhanced_count = sum(1 for r in results['results'] if r.get('has_supply_data') or r.get('has_weather_data') or r.get('has_air_support'))
    print(f"\n[Phase 9A] Enhanced scenarios: {enhanced_count}/{results['exported']}")
    print(f"  - With supply data: {sum(1 for r in results['results'] if r.get('has_supply_data'))}")
    print(f"  - With weather data: {sum(1 for r in results['results'] if r.get('has_weather_data'))}")
    print(f"  - With air support: {sum(1 for r in results['results'] if r.get('has_air_support'))}")

    return results


if __name__ == '__main__':
    main()
