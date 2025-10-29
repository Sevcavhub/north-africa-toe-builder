#!/usr/bin/env python3
"""
BattleGroup Scenario Exporter

Purpose: Generate BattleGroup tabletop wargaming scenarios with:
- Points costs (estimated from armor/penetration/special rules)
- Battle Rating values (unit importance)
- Force lists with BattleGroup stats
- Scenario narratives and objectives

Inherits from ScenarioExporter base class (Phase 9A architecture)
Uses converters: penetration, armor, points, battle rating
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from base.scenario_exporter import ScenarioExporter
from typing import Dict, List, Optional
import json
from datetime import datetime

# Import converters
sys.path.append(str(Path(__file__).parent.parent / "converters"))
from armor_converter import convert_tank_armor, get_armor_category
from penetration_converter import convert_penetration_to_battlegroup, estimate_penetration_from_caliber
from points_estimator import estimate_tank_points, estimate_infantry_points, estimate_gun_points, estimate_vehicle_points
from battle_rating_assigner import assign_tank_br, assign_infantry_br, assign_gun_br, assign_vehicle_br, assign_experience_level, calculate_force_br


class BattleGroupExporter(ScenarioExporter):
    """BattleGroup scenario exporter"""

    def __init__(self, project_root: Path = None):
        super().__init__(project_root)
        self.game_name = "battlegroup"
        self.output_dir = self.scenarios_dir / self.game_name

    def format_equipment_data(self, unit_data: Dict) -> List[Dict]:
        """
        Convert unit equipment data to BattleGroup format

        Returns list of equipment records with:
        - equipment_name
        - battlegroup_stats (armor, penetration, points, BR)
        - count
        - experience_level
        """
        equipment_list = []

        nation = unit_data.get('nation', 'unknown')
        quarter = unit_data.get('quarter', 'unknown')
        experience = assign_experience_level(nation, quarter)

        # Process tanks
        if 'tanks' in unit_data:
            equipment_list.extend(
                self._process_tanks(unit_data['tanks'], nation, quarter, experience)
            )

        # Process artillery
        if 'field_artillery' in unit_data or 'artillery' in unit_data:
            artillery_section = unit_data.get('field_artillery') or unit_data.get('artillery')
            equipment_list.extend(
                self._process_artillery(artillery_section, experience)
            )

        # Process AT guns
        if 'anti_tank' in unit_data or 'anti_tank_guns' in unit_data:
            at_section = unit_data.get('anti_tank') or unit_data.get('anti_tank_guns')
            equipment_list.extend(
                self._process_at_guns(at_section, experience)
            )

        # Process vehicles
        for vehicle_type in ['halftracks', 'trucks', 'armored_cars', 'motorcycles']:
            if vehicle_type in unit_data:
                equipment_list.extend(
                    self._process_vehicles(unit_data[vehicle_type], vehicle_type, experience)
                )

        return equipment_list

    def _process_tanks(self, tanks_section: Dict, nation: str, quarter: str, experience: str) -> List[Dict]:
        """Process tank variants into BattleGroup format"""
        tank_list = []

        # Handle nested structure (heavy_tanks, medium_tanks, light_tanks)
        tank_categories = ['heavy_tanks', 'medium_tanks', 'light_tanks', 'command_tanks']

        for category in tank_categories:
            if category in tanks_section and 'variants' in tanks_section[category]:
                variants = tanks_section[category]['variants']

                for tank_name, tank_data in variants.items():
                    if not isinstance(tank_data, dict):
                        continue

                    count = tank_data.get('count', 0)
                    if count == 0:
                        continue

                    # Extract armor values
                    armor_front = tank_data.get('armor_front_mm', 30)
                    armor_side = tank_data.get('armor_side_mm', 20)
                    armor_rear = tank_data.get('armor_rear_mm', 20)

                    # Extract gun penetration
                    gun_pen_mm = self._extract_gun_penetration(tank_data)

                    # Determine special rules
                    special_rules = []
                    if 'radio' in str(tank_data).lower():
                        special_rules.append('radio')
                    if 'smoke' in str(tank_data).lower():
                        special_rules.append('smoke')

                    is_command = 'command' in category.lower() or 'command' in tank_name.lower()
                    if is_command:
                        special_rules.append('command')

                    # Calculate BattleGroup stats
                    armor_profile = convert_tank_armor(armor_front, armor_side, armor_rear)
                    penetration = convert_penetration_to_battlegroup(gun_pen_mm)
                    points = estimate_tank_points(armor_front, armor_side, armor_rear, gun_pen_mm, special_rules)
                    br = assign_tank_br(armor_front, gun_pen_mm, is_command)

                    tank_list.append({
                        'name': tank_name,
                        'count': count,
                        'type': 'tank',
                        'category': category.replace('_tanks', ''),
                        'battlegroup_stats': {
                            'armor': f"{armor_profile['front']}/{armor_profile['side']}/{armor_profile['rear']}",
                            'armor_category': get_armor_category(armor_profile['front']),
                            'penetration': penetration,
                            'points_each': points,
                            'points_total': points * count,
                            'br_each': br,
                            'br_total': br * count,
                            'experience': experience,
                            'special_rules': special_rules
                        },
                        'original_data': {
                            'armor_mm': f"{armor_front}/{armor_side}/{armor_rear}",
                            'gun_pen_mm': gun_pen_mm
                        }
                    })

        # Handle flat variants structure
        if 'variants' in tanks_section:
            variants = tanks_section['variants']
            for tank_name, tank_data in variants.items():
                if not isinstance(tank_data, dict):
                    continue

                count = tank_data.get('count', 0)
                if count == 0:
                    continue

                armor_front = tank_data.get('armor_front_mm', 30)
                armor_side = tank_data.get('armor_side_mm', 20)
                armor_rear = tank_data.get('armor_rear_mm', 20)
                gun_pen_mm = self._extract_gun_penetration(tank_data)

                special_rules = ['radio', 'smoke']
                is_command = 'command' in tank_name.lower()

                armor_profile = convert_tank_armor(armor_front, armor_side, armor_rear)
                penetration = convert_penetration_to_battlegroup(gun_pen_mm)
                points = estimate_tank_points(armor_front, armor_side, armor_rear, gun_pen_mm, special_rules)
                br = assign_tank_br(armor_front, gun_pen_mm, is_command)

                tank_list.append({
                    'name': tank_name,
                    'count': count,
                    'type': 'tank',
                    'category': 'medium',
                    'battlegroup_stats': {
                        'armor': f"{armor_profile['front']}/{armor_profile['side']}/{armor_profile['rear']}",
                        'armor_category': get_armor_category(armor_profile['front']),
                        'penetration': penetration,
                        'points_each': points,
                        'points_total': points * count,
                        'br_each': br,
                        'br_total': br * count,
                        'experience': experience,
                        'special_rules': special_rules
                    },
                    'original_data': {
                        'armor_mm': f"{armor_front}/{armor_side}/{armor_rear}",
                        'gun_pen_mm': gun_pen_mm
                    }
                })

        return tank_list

    def _process_artillery(self, artillery_section: Dict, experience: str) -> List[Dict]:
        """Process artillery/field guns into BattleGroup format"""
        artillery_list = []

        if 'variants' in artillery_section:
            variants = artillery_section['variants']

            for gun_name, gun_data in variants.items():
                if not isinstance(gun_data, dict):
                    continue

                count = gun_data.get('count', 0)
                if count == 0:
                    continue

                caliber = self._extract_caliber(gun_name, gun_data)
                gun_pen_mm = self._extract_gun_penetration(gun_data)

                # Determine HE size from caliber
                if caliber < 75:
                    he_size = 'very_light'
                elif caliber < 105:
                    he_size = 'light'
                elif caliber < 155:
                    he_size = 'medium'
                else:
                    he_size = 'heavy'

                points = estimate_gun_points(gun_pen_mm, he_size, 6, 'towed', experience)
                br = assign_gun_br(gun_pen_mm, 'howitzer', False)

                artillery_list.append({
                    'name': gun_name,
                    'count': count,
                    'type': 'artillery',
                    'battlegroup_stats': {
                        'penetration': convert_penetration_to_battlegroup(gun_pen_mm),
                        'he_size': he_size,
                        'points_each': points,
                        'points_total': points * count,
                        'br_each': br,
                        'br_total': br * count,
                        'experience': experience,
                        'mobility': 'towed'
                    },
                    'original_data': {
                        'caliber_mm': caliber,
                        'gun_pen_mm': gun_pen_mm
                    }
                })

        return artillery_list

    def _process_at_guns(self, at_section: Dict, experience: str) -> List[Dict]:
        """Process anti-tank guns into BattleGroup format"""
        at_list = []

        if 'variants' in at_section:
            variants = at_section['variants']

            for gun_name, gun_data in variants.items():
                if not isinstance(gun_data, dict):
                    continue

                count = gun_data.get('count', 0)
                if count == 0:
                    continue

                caliber = self._extract_caliber(gun_name, gun_data)
                gun_pen_mm = self._extract_gun_penetration(gun_data)

                # AT guns have light HE
                he_size = 'very_light' if caliber < 75 else 'light'

                points = estimate_gun_points(gun_pen_mm, he_size, 5, 'towed', experience)
                br = assign_gun_br(gun_pen_mm, 'at', False)

                at_list.append({
                    'name': gun_name,
                    'count': count,
                    'type': 'anti_tank',
                    'battlegroup_stats': {
                        'penetration': convert_penetration_to_battlegroup(gun_pen_mm),
                        'he_size': he_size,
                        'points_each': points,
                        'points_total': points * count,
                        'br_each': br,
                        'br_total': br * count,
                        'experience': experience,
                        'mobility': 'towed'
                    },
                    'original_data': {
                        'caliber_mm': caliber,
                        'gun_pen_mm': gun_pen_mm
                    }
                })

        return at_list

    def _process_vehicles(self, vehicle_section: Dict, vehicle_type: str, experience: str) -> List[Dict]:
        """Process support vehicles into BattleGroup format"""
        vehicle_list = []

        if 'variants' in vehicle_section:
            variants = vehicle_section['variants']

            for vehicle_name, vehicle_data in variants.items():
                if not isinstance(vehicle_data, dict):
                    continue

                count = vehicle_data.get('count', 0)
                if count == 0:
                    continue

                # Map our vehicle types to BattleGroup types
                bg_type_map = {
                    'halftracks': 'halftrack',
                    'trucks': 'truck',
                    'armored_cars': 'armored_car',
                    'motorcycles': 'motorcycle'
                }
                bg_type = bg_type_map.get(vehicle_type, 'truck')

                has_special_role = 'command' in vehicle_name.lower()

                points = estimate_vehicle_points(bg_type, 0, [])
                br = assign_vehicle_br(bg_type, has_special_role)

                vehicle_list.append({
                    'name': vehicle_name,
                    'count': count,
                    'type': vehicle_type,
                    'battlegroup_stats': {
                        'points_each': points,
                        'points_total': points * count,
                        'br_each': br,
                        'br_total': br * count,
                        'vehicle_type': bg_type,
                        'special_role': has_special_role
                    }
                })

        return vehicle_list

    def _extract_gun_penetration(self, item_data: Dict) -> float:
        """Extract gun penetration value from equipment data"""
        # Try various field names
        for field in ['penetration_mm', 'gun_penetration', 'pen_500m', 'penetration']:
            if field in item_data:
                value = item_data[field]
                # Handle both numeric and string values
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str):
                    # Try to extract number from string
                    import re
                    num_match = re.search(r'(\d+(?:\.\d+)?)', value)
                    if num_match:
                        return float(num_match.group(1))

        # Try to extract from gun name
        gun = item_data.get('gun', '')
        if '5cm' in gun or '50mm' in gun:
            return 60.0
        elif '7.5cm' in gun or '75mm' in gun:
            if 'L/24' in gun:
                return 40.0  # Short barrel
            else:
                return 90.0  # Long barrel
        elif '8.8cm' in gun or '88mm' in gun:
            return 130.0

        # If we have caliber, estimate from that
        caliber = self._extract_caliber('', item_data)
        if caliber > 0:
            return estimate_penetration_from_caliber(caliber, 'standard')

        return 50.0  # Default estimate

    def _extract_caliber(self, gun_name: str, gun_data: Dict) -> float:
        """Extract gun caliber from name or data"""
        import re

        # Try data field first
        if 'caliber' in gun_data:
            value = gun_data['caliber']
            # Handle both numeric and string values
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Extract number from string like '105mm'
                num_match = re.search(r'(\d+(?:\.\d+)?)', value)
                if num_match:
                    return float(num_match.group(1))

        # Parse from name (e.g., "105mm leFH 18" or "10.5cm leFH 18")
        cm_match = re.search(r'(\d+(?:\.\d+)?)cm', gun_name)
        if cm_match:
            return float(cm_match.group(1)) * 10  # Convert cm to mm

        mm_match = re.search(r'(\d+)mm', gun_name)
        if mm_match:
            return float(mm_match.group(1))

        return 75.0  # Default

    def generate_narrative(self, metadata: Dict, unit_data: Dict,
                          supply: Dict, environment: Dict, air_support: Optional[Dict]) -> Dict:
        """
        Generate BattleGroup scenario narrative

        Includes:
        - Historical situation
        - Force lists with points and BR
        - Deployment instructions
        - Victory conditions
        - Special rules
        """
        narrative = {
            'title': f"BattleGroup: {metadata['unit_designation']} - {metadata['quarter'].upper()}",
            'date': metadata['date'],
            'location': metadata['theater'],
            'nation': metadata['nation'],
            'scenario_size': 'Platoon',  # Default 500pts
            'recommended_points': 500
        }

        # Historical context
        if 'historical_context' in unit_data:
            historical = unit_data['historical_context']
            if isinstance(historical, dict):
                narrative['situation'] = historical.get('formation', 'North Africa Campaign engagement.')
            else:
                narrative['situation'] = str(historical)
        else:
            narrative['situation'] = f"{metadata['nation']} forces engaged in {metadata['theater']} during {metadata['quarter'].upper()}."

        # Deployment
        narrative['deployment'] = {
            'defender': f"{metadata['nation']} forces deploy first, within 18\" of table edge",
            'attacker': "Opponent deploys within 12\" of opposite edge",
            'terrain': environment.get('terrain_type', 'Desert - sparse cover, open sightlines')
        }

        # Victory conditions
        narrative['victory_conditions'] = {
            'primary': 'Break enemy Battlegroup Rating (BR)',
            'secondary': [
                'Hold 2 of 3 objectives',
                'Destroy enemy command unit',
                'Take fewer casualties than opponent'
            ]
        }

        # Special rules based on environment/supply
        special_rules = []

        if supply.get('fuel_days', 0) < 5:
            special_rules.append('Limited Fuel: Vehicles move at half speed after Turn 5')

        if 'desert' in environment.get('terrain_type', '').lower():
            special_rules.append('Desert Conditions: Visibility 48\" maximum, dust after vehicle movement')

        narrative['special_rules'] = special_rules

        return narrative

    def export_scenario(self, unit_file_path: Path) -> Dict:
        """
        Export BattleGroup scenario from unit JSON

        Creates:
        - force_list.json (BattleGroup force with points/BR)
        - scenario.md (narrative, objectives, special rules)
        """
        filename = unit_file_path.name
        print(f"\nExporting BattleGroup scenario: {filename}")

        # Load unit data
        unit_data = self.load_unit_json(unit_file_path)

        # Extract metadata
        metadata = self.extract_scenario_metadata(unit_data, filename)
        if not metadata:
            print(f"  [SKIP] Cannot extract metadata from {filename}")
            return None

        scenario_name = f"{metadata['nation']}_{metadata['quarter']}_{metadata['unit_designation'].replace(' ', '_')}"
        print(f"  Scenario name: {scenario_name}")

        # Extract enhanced data
        supply = self.extract_supply_states(unit_data)
        environment = self.extract_weather_environment(unit_data)
        air_support = self.extract_air_support(unit_data)

        # Convert equipment to BattleGroup format
        equipment_list = self.format_equipment_data(unit_data)
        print(f"  Equipment items: {len(equipment_list)}")

        # Calculate total points and BR
        total_points = sum(item['battlegroup_stats']['points_total'] for item in equipment_list if 'battlegroup_stats' in item)
        total_br = sum(item['battlegroup_stats']['br_total'] for item in equipment_list if 'battlegroup_stats' in item)

        print(f"  Total Points: {total_points}, Total BR: {total_br}")

        # Generate narrative
        narrative = self.generate_narrative(metadata, unit_data, supply, environment, air_support)

        # Create scenario directory
        scenario_dir = self.output_dir / scenario_name
        scenario_dir.mkdir(parents=True, exist_ok=True)

        # Write force list JSON
        force_list_file = scenario_dir / 'force_list.json'
        with open(force_list_file, 'w', encoding='utf-8') as f:
            json.dump({
                'battlegroup_name': metadata['unit_designation'],
                'nation': metadata['nation'],
                'quarter': metadata['quarter'],
                'total_points': total_points,
                'total_br': total_br,
                'equipment': equipment_list,
                'exported_at': datetime.now().isoformat(),
                'exporter_version': 'Phase 9B BattleGroup (October 2025)'
            }, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Wrote force list: {force_list_file.name}")

        # Write scenario markdown
        scenario_md_file = scenario_dir / 'scenario.md'
        self._write_scenario_md(scenario_md_file, narrative, metadata, equipment_list, total_points, total_br, supply, environment)
        print(f"  [OK] Wrote scenario: {scenario_md_file.name}")

        return {
            'scenario_name': scenario_name,
            'equipment_count': len(equipment_list),
            'total_points': total_points,
            'total_br': total_br,
            'scenario_dir': str(scenario_dir)
        }

    def _write_scenario_md(self, scenario_file: Path, narrative: Dict, metadata: Dict,
                          equipment_list: List[Dict], total_points: int, total_br: int,
                          supply: Dict, environment: Dict):
        """Write BattleGroup scenario markdown file"""
        with open(scenario_file, 'w', encoding='utf-8') as f:
            f.write(f"# {narrative['title']}\n\n")
            f.write(f"**Date**: {narrative['date']}\n")
            f.write(f"**Location**: {narrative['location']}\n")
            f.write(f"**Nation**: {narrative['nation'].title()}\n")
            f.write(f"**Scenario Size**: {narrative['scenario_size']} ({narrative['recommended_points']}pts)\n\n")

            f.write(f"## Historical Situation\n\n{narrative['situation']}\n\n")

            f.write(f"## Battlegroup Stats\n\n")
            f.write(f"- **Total Points**: {total_points}pts\n")
            f.write(f"- **Battle Rating**: {total_br}\n")
            f.write(f"- **Equipment Items**: {len(equipment_list)}\n\n")

            f.write(f"## Force List\n\n")

            # Group by type
            tanks = [e for e in equipment_list if e.get('type') == 'tank']
            artillery = [e for e in equipment_list if e.get('type') in ['artillery', 'anti_tank']]
            vehicles = [e for e in equipment_list if e.get('type') in ['halftracks', 'trucks', 'armored_cars', 'motorcycles']]

            if tanks:
                f.write(f"### Tanks ({len(tanks)} types)\n\n")
                for tank in tanks:
                    stats = tank['battlegroup_stats']
                    f.write(f"**{tank['name']}** (x{tank['count']})\n")
                    f.write(f"- Armor: {stats['armor']} ({stats['armor_category']})\n")
                    f.write(f"- Penetration: {stats['penetration']}\n")
                    f.write(f"- Points: {stats['points_each']}pts each ({stats['points_total']}pts total)\n")
                    f.write(f"- BR: {stats['br_each']} each ({stats['br_total']} total)\n")
                    f.write(f"- Experience: {stats['experience'].upper()}\n")
                    if stats.get('special_rules'):
                        f.write(f"- Special: {', '.join(stats['special_rules'])}\n")
                    f.write(f"\n")

            if artillery:
                f.write(f"### Guns ({len(artillery)} types)\n\n")
                for gun in artillery:
                    stats = gun['battlegroup_stats']
                    f.write(f"**{gun['name']}** (x{gun['count']})\n")
                    f.write(f"- Penetration: {stats['penetration']}\n")
                    f.write(f"- HE: {stats['he_size'].replace('_', ' ').title()}\n")
                    f.write(f"- Points: {stats['points_each']}pts each ({stats['points_total']}pts total)\n")
                    f.write(f"- BR: {stats['br_each']} each ({stats['br_total']} total)\n")
                    f.write(f"- Mobility: {stats['mobility'].title()}\n\n")

            if vehicles:
                f.write(f"### Support Vehicles ({len(vehicles)} types)\n\n")
                for vehicle in vehicles:
                    stats = vehicle['battlegroup_stats']
                    f.write(f"**{vehicle['name']}** (x{vehicle['count']}): {stats['points_total']}pts, BR {stats['br_total']}\n")

            f.write(f"\n## Deployment\n\n")
            f.write(f"**Defender**: {narrative['deployment']['defender']}\n\n")
            f.write(f"**Attacker**: {narrative['deployment']['attacker']}\n\n")
            f.write(f"**Terrain**: {narrative['deployment']['terrain']}\n\n")

            f.write(f"## Victory Conditions\n\n")
            f.write(f"**Primary**: {narrative['victory_conditions']['primary']}\n\n")
            f.write(f"**Secondary**:\n")
            for condition in narrative['victory_conditions']['secondary']:
                f.write(f"- {condition}\n")
            f.write(f"\n")

            if narrative.get('special_rules'):
                f.write(f"## Special Rules\n\n")
                for rule in narrative['special_rules']:
                    f.write(f"- {rule}\n")
                f.write(f"\n")

            f.write(f"## Supply & Environment\n\n")
            f.write(f"**Fuel**: {supply.get('fuel_days', 'Unknown')} days\n")
            f.write(f"**Ammunition**: {supply.get('ammunition_days', 'Unknown')} days\n")
            f.write(f"**Terrain**: {environment.get('terrain_type', 'Desert')}\n\n")

            f.write(f"---\n\n")
            f.write(f"*Generated by BattleGroup Exporter Phase 9B*\n")


def main():
    """Export all BattleGroup scenarios"""
    exporter = BattleGroupExporter()
    results = exporter.export_all_scenarios()

    print(f"\n[Phase 9B] BattleGroup export complete:")
    print(f"  - Scenarios exported: {results['exported']}")
    print(f"  - Scenarios skipped: {results['skipped']}")
    print(f"  - Errors: {results['errors']}")

    return results


if __name__ == '__main__':
    main()
