#!/usr/bin/env python3
"""
Base Scenario Exporter - Abstract class for game system exports

Purpose: Provide pluggable architecture for multi-game scenario generation
Supports: WITW, BattleGroup, Achtung Panzer, Flames of War

Architecture:
- ScenarioExporter: Base class with common functionality
- Game-specific exporters inherit and override format-specific methods
- Converters: Modular utilities for penetration, armor, points calculations
- Templates: Game-specific narrative formats

Usage:
    from scenario_exporters.witw_exporter import WITWExporter

    exporter = WITWExporter()
    scenario = exporter.export_scenario(unit_json_path)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import csv
from datetime import datetime

class ScenarioExporter(ABC):
    """Base class for scenario exporters - all game systems inherit from this"""

    def __init__(self, project_root: Path = None):
        """
        Initialize exporter with project paths

        Args:
            project_root: Path to project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent

        self.project_root = project_root
        self.units_dir = project_root / "data" / "output" / "units"
        self.air_summaries_dir = project_root / "data" / "output" / "air_summaries"
        self.scenarios_dir = project_root / "data" / "output" / "scenarios"

        # Game-specific output directory (override in subclasses)
        self.game_name = "generic"
        self.output_dir = self.scenarios_dir / self.game_name

    def load_unit_json(self, unit_file_path: Path) -> Dict:
        """Load unit JSON file"""
        with open(unit_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_air_summary(self, nation: str, quarter: str) -> Optional[Dict]:
        """
        Load quarterly air summary if available

        Args:
            nation: Nation code (german, british, american, italian)
            quarter: Quarter code (1941q2)

        Returns:
            Air summary dict or None if not found
        """
        air_summary_file = self.air_summaries_dir / f"{nation}_{quarter}_air_summary.json"

        if not air_summary_file.exists():
            return None

        with open(air_summary_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_supply_states(self, unit_data: Dict) -> Dict:
        """
        Extract supply/logistics data from unit JSON (Schema v3.0+)

        Returns dict with fuel_days, ammunition_days, water, food_days, operational_radius
        """
        supply = {}

        # Schema v3.0 location
        if 'supply_status' in unit_data:
            supply_status = unit_data['supply_status']
            supply['fuel_days'] = supply_status.get('fuel_days', 0)
            supply['ammunition_days'] = supply_status.get('ammunition_days', 0)
            supply['water_liters_per_day'] = supply_status.get('water_liters_per_day', 0)
            supply['food_days'] = supply_status.get('food_days', 0)
            supply['notes'] = supply_status.get('notes', '')

        # Schema v3.0 logistics field
        if 'supply_logistics' in unit_data:
            logistics = unit_data['supply_logistics']
            supply['fuel_reserves_days'] = logistics.get('fuel_reserves_days', 0)
            supply['ammunition_stock_days'] = logistics.get('ammunition_stock_days', 0)
            supply['water_liters_per_man'] = logistics.get('water_liters_per_man', 0)
            supply['operational_radius_km'] = logistics.get('operational_radius_km', 0)
            supply['supply_line_status'] = logistics.get('supply_line_status', 'unknown')

        return supply

    def extract_weather_environment(self, unit_data: Dict) -> Dict:
        """
        Extract weather/environment data from unit JSON (Schema v3.0+)

        Returns dict with terrain, temperature, seasonal impacts, environmental challenges
        """
        environment = {}

        if 'weather_environment' in unit_data:
            weather = unit_data['weather_environment']
            environment['terrain_type'] = weather.get('terrain_type', 'Desert')
            environment['temperature_range_celsius'] = weather.get('temperature_range_celsius', 'Unknown')
            environment['seasonal_impacts'] = weather.get('seasonal_impacts', [])
            environment['environmental_challenges'] = weather.get('environmental_challenges', [])
            environment['visibility_conditions'] = weather.get('visibility_conditions', 'Clear')

        return environment

    def extract_air_support(self, unit_data: Dict) -> Optional[Dict]:
        """
        Extract air support references from unit JSON (Phase 8 cross-linking)

        Returns dict with air summary reference or None
        """
        if 'air_support' not in unit_data:
            return None

        air_support = unit_data['air_support']

        # Load referenced air summary
        if 'air_summary_reference' in air_support:
            nation = unit_data.get('nation', 'unknown')
            quarter = unit_data.get('quarter', 'unknown')
            air_summary = self.load_air_summary(nation, quarter)

            if air_summary:
                return {
                    'reference': air_support,
                    'summary': air_summary
                }

        return {'reference': air_support, 'summary': None}

    def parse_quarter(self, quarter_str: str) -> str:
        """
        Parse quarter string to date

        Args:
            quarter_str: Quarter code like '1941q2'

        Returns:
            Date string like '1941-06-01'
        """
        import re

        match = re.match(r'(\d{4})q(\d)', quarter_str.lower())
        if not match:
            return f"{quarter_str}-01-01"

        year, quarter = match.groups()
        year = int(year)
        quarter = int(quarter)

        # Convert quarter to month (Q1=March, Q2=June, Q3=September, Q4=December)
        month_map = {1: 3, 2: 6, 3: 9, 4: 12}
        month = month_map.get(quarter, 6)

        return f"{year}-{month:02d}-01"

    def extract_scenario_metadata(self, unit_data: Dict, filename: str) -> Dict:
        """
        Extract common scenario metadata

        Args:
            unit_data: Unit JSON dict
            filename: Source filename

        Returns:
            Metadata dict with nation, quarter, date, unit info
        """
        # Parse filename: nation_quarter_unit_designation_toe.json
        parts = filename.replace('_toe.json', '').split('_')

        if len(parts) < 3:
            return {}

        nation = parts[0]
        quarter = parts[1]
        unit_designation = '_'.join(parts[2:])

        metadata = {
            'nation': nation.title(),
            'quarter': quarter,
            'date': self.parse_quarter(quarter),
            'unit_designation': unit_designation.replace('_', ' ').title(),
            'unit_type': unit_data.get('unit_type', 'Division'),
            'organization_level': unit_data.get('organization_level', 'division'),
            'theater': unit_data.get('theater', 'North Africa')
        }

        # Add commander if available
        if 'command' in unit_data and 'commander' in unit_data['command']:
            commander = unit_data['command']['commander']
            metadata['commander_name'] = commander.get('name', 'Unknown')
            metadata['commander_rank'] = commander.get('rank', 'Unknown')

        return metadata

    # Abstract methods - must be implemented by subclasses

    @abstractmethod
    def export_scenario(self, unit_file_path: Path) -> Dict:
        """
        Export scenario from unit JSON to game-specific format

        Args:
            unit_file_path: Path to unit JSON file

        Returns:
            Export result dict with scenario_name, files_created, etc.
        """
        pass

    @abstractmethod
    def format_equipment_data(self, unit_data: Dict) -> List[Dict]:
        """
        Convert unit equipment data to game-specific format

        Args:
            unit_data: Unit JSON dict

        Returns:
            List of equipment records in game-specific format
        """
        pass

    @abstractmethod
    def generate_narrative(self, metadata: Dict, unit_data: Dict,
                          supply: Dict, environment: Dict, air_support: Optional[Dict]) -> Dict:
        """
        Generate scenario narrative and objectives

        Args:
            metadata: Scenario metadata
            unit_data: Unit JSON dict
            supply: Supply states
            environment: Weather/environment data
            air_support: Air support references

        Returns:
            Narrative dict with title, situation, objectives, conditions
        """
        pass

    def export_all_scenarios(self) -> Dict:
        """
        Export scenarios from all unit JSON files

        Returns:
            Summary dict with export statistics
        """
        print('=' * 80)
        print(f'GENERATING {self.game_name.upper()} SCENARIO EXPORTS')
        print('=' * 80)
        print(f'\nInput directory: {self.units_dir}')
        print(f'Output directory: {self.output_dir}\n')

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get all unit files
        unit_files = list(self.units_dir.glob('*_toe.json'))
        print(f'Found {len(unit_files)} unit files\n')

        exported = 0
        skipped = 0
        errors = 0
        results = []

        for unit_file in unit_files:
            try:
                result = self.export_scenario(unit_file)
                if result:
                    results.append(result)
                    exported += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"  [ERROR] Failed to export {unit_file.name}: {e}")
                errors += 1

        print('\n' + '=' * 80)
        print(f'{self.game_name.upper()} SCENARIO EXPORT SUMMARY')
        print('=' * 80)
        print(f'Scenarios exported: {exported}')
        print(f'Scenarios skipped: {skipped}')
        print(f'Errors: {errors}')
        print(f'\n[OK] Scenario export complete!')
        print(f'\nScenarios saved to: {self.output_dir}')
        print('=' * 80)

        return {
            'game_system': self.game_name,
            'exported': exported,
            'skipped': skipped,
            'errors': errors,
            'results': results
        }
