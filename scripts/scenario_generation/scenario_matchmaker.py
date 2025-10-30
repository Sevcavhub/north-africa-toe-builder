#!/usr/bin/env python3
"""
Phase 9 Scenario Matchmaker

Purpose: Generate balanced Axis vs Allied scenarios with complete Phase 9 structure
- Pairs forces by quarter, points, and experience
- Creates canonical battle_scenarios/ folder structure
- Generates 7 JSON files per PROJECT_SCOPE.md

Output Structure:
battle_scenarios/
  ├── {quarter}_{axis_unit}_vs_{allied_unit}_{size}/
  │   ├── oob_ground.json        # Both forces with TO&E tables
  │   ├── supply_state.json      # Fuel/ammo/water for both sides
  │   ├── weather.json           # Temperature, terrain, season
  │   ├── map_data.json          # Terrain features, deployment zones
  │   ├── victory_conditions.json # Objectives, scoring
  │   ├── oob_air.json           # Placeholder (Phase 8)
  │   └── air_support.json       # Placeholder (Phase 8)
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
from collections import defaultdict

# Add parent directories to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

# Import BattleGroup slicer for force generation
from battlegroup_scenario_slicer import BattleGroupScenarioSlicer


class ScenarioMatchmaker:
    """
    Intelligent matchmaking for balanced Axis vs Allied scenarios
    """

    # Scenario size configs (from BattleGroup but universally applicable)
    SCENARIO_SIZES = ['squad', 'platoon', 'company', 'battalion']

    POINTS_TARGETS = {
        'squad': 250,
        'platoon': 500,
        'company': 1000,
        'battalion': 1500
    }

    # Nation alignments
    AXIS_NATIONS = ['german', 'italian']
    ALLIED_NATIONS = ['british', 'american', 'french']

    # Experience level equivalents for matching
    EXPERIENCE_TIERS = {
        'elite': 4,
        'veteran': 3,
        'regular': 2,
        'inexperienced': 1
    }

    def __init__(self, project_root: Path = None):
        """Initialize matchmaker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.units_dir = project_root / 'data' / 'output' / 'units'
        self.output_dir = project_root / 'data' / 'output' / 'battle_scenarios'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.slicer = BattleGroupScenarioSlicer()

        # Cache of available forces by quarter
        self.forces_by_quarter = defaultdict(lambda: {'axis': [], 'allied': []})

    def scan_available_forces(self) -> Dict:
        """
        Scan all unit JSONs to build database of available forces

        Returns dict: {quarter: {axis: [...], allied: [...]}}
        """
        print("\n[Phase 9] Scanning available forces...")

        unit_files = sorted(self.units_dir.glob('*_toe.json'))

        scanned = 0
        skipped = 0

        for unit_file in unit_files:
            try:
                with open(unit_file, 'r', encoding='utf-8') as f:
                    unit_data = json.load(f)

                # Extract metadata
                nation = unit_data.get('nation', 'unknown')
                quarter = unit_data.get('quarter', 'unknown')
                unit_name = unit_data.get('unit_name', unit_file.stem)

                if nation == 'unknown' or quarter == 'unknown':
                    skipped += 1
                    continue

                # Check if unit has equipment data
                has_equipment = False
                for section in ['tanks', 'field_artillery', 'anti_tank', 'artillery']:
                    if section in unit_data and unit_data[section]:
                        has_equipment = True
                        break

                if not has_equipment:
                    skipped += 1
                    continue

                # Classify as Axis or Allied
                alignment = 'axis' if nation in self.AXIS_NATIONS else 'allied'

                # Store force info
                force_info = {
                    'file_path': str(unit_file),
                    'nation': nation,
                    'quarter': quarter,
                    'unit_name': unit_name,
                    'unit_data': unit_data,
                    'experience': self._extract_experience(unit_data, nation, quarter)
                }

                self.forces_by_quarter[quarter][alignment].append(force_info)
                scanned += 1

            except Exception as e:
                print(f"  [ERROR] Failed to scan {unit_file.name}: {e}")
                skipped += 1

        print(f"  Scanned: {scanned} units")
        print(f"  Skipped: {skipped} units (no equipment or metadata)")
        print(f"  Quarters with forces: {len(self.forces_by_quarter)}")

        return self.forces_by_quarter

    def _extract_experience(self, unit_data: Dict, nation: str, quarter: str) -> str:
        """Extract or estimate experience level"""
        # Check if experience is explicitly in unit data
        if 'experience_level' in unit_data:
            return unit_data['experience_level']

        # Estimate based on nation and quarter
        # Germans: veteran until 1943, then regular
        if nation == 'german':
            if quarter < '1943q1':
                return 'veteran'
            else:
                return 'regular'

        # British: regular early, veteran mid-war
        elif nation == 'british':
            if '1941q3' <= quarter <= '1942q4':
                return 'veteran'
            else:
                return 'regular'

        # Americans: inexperienced 1942q4, regular after
        elif nation == 'american':
            if quarter == '1942q4':
                return 'inexperienced'
            else:
                return 'regular'

        # Italians: regular
        elif nation == 'italian':
            return 'regular'

        return 'regular'  # Default

    def generate_matchups(self, max_per_quarter: int = 10) -> List[Dict]:
        """
        Generate balanced Axis vs Allied matchups

        Args:
            max_per_quarter: Maximum scenarios per quarter (prevents explosion)

        Returns:
            List of matchup dicts with axis_force, allied_force, scenario_size
        """
        print("\n[Phase 9] Generating matchups...")

        matchups = []

        for quarter in sorted(self.forces_by_quarter.keys()):
            quarter_data = self.forces_by_quarter[quarter]
            axis_forces = quarter_data['axis']
            allied_forces = quarter_data['allied']

            if not axis_forces or not allied_forces:
                print(f"  [SKIP] {quarter}: Missing {'Axis' if not axis_forces else 'Allied'} forces")
                continue

            print(f"\n  {quarter}: {len(axis_forces)} Axis, {len(allied_forces)} Allied")

            # Generate matchups for each scenario size
            quarter_matchups = []

            for scenario_size in self.SCENARIO_SIZES:
                # Try to pair each Axis force with best Allied match
                for axis_force in axis_forces:
                    best_match = self._find_best_match(
                        axis_force,
                        allied_forces,
                        scenario_size
                    )

                    if best_match:
                        matchup = {
                            'quarter': quarter,
                            'scenario_size': scenario_size,
                            'axis_force': axis_force,
                            'allied_force': best_match,
                            'points_target': self.POINTS_TARGETS[scenario_size]
                        }
                        quarter_matchups.append(matchup)

                # Limit matchups per quarter per size
                if len(quarter_matchups) > max_per_quarter:
                    quarter_matchups = quarter_matchups[:max_per_quarter]

            matchups.extend(quarter_matchups)
            print(f"    Generated {len(quarter_matchups)} matchups")

        print(f"\n  Total matchups: {len(matchups)}")
        return matchups

    def _find_best_match(self, axis_force: Dict, allied_forces: List[Dict],
                         scenario_size: str) -> Optional[Dict]:
        """
        Find best Allied force to match against Axis force

        Scoring based on:
        - Experience similarity (prefer veteran vs veteran)
        - Force type similarity (armor vs armor, infantry vs infantry)
        - Historical plausibility
        """
        best_match = None
        best_score = -1

        axis_exp_tier = self.EXPERIENCE_TIERS.get(axis_force['experience'], 2)

        for allied_force in allied_forces:
            allied_exp_tier = self.EXPERIENCE_TIERS.get(allied_force['experience'], 2)

            score = 100  # Base score

            # Experience matching (±1 tier is acceptable)
            exp_diff = abs(axis_exp_tier - allied_exp_tier)
            if exp_diff == 0:
                score += 30  # Perfect match
            elif exp_diff == 1:
                score += 15  # Close match
            else:
                score -= 20  # Poor match

            # Force type matching (check if both have tanks, etc.)
            axis_has_tanks = 'tank' in axis_force['unit_name'].lower() or \
                           'panzer' in axis_force['unit_name'].lower() or \
                           'armour' in axis_force['unit_name'].lower()

            allied_has_tanks = 'tank' in allied_force['unit_name'].lower() or \
                             'panzer' in allied_force['unit_name'].lower() or \
                             'armour' in allied_force['unit_name'].lower()

            if axis_has_tanks == allied_has_tanks:
                score += 20  # Similar force composition

            # Historical plausibility (prefer British vs German/Italian, American vs German in 1943)
            if axis_force['nation'] == 'german' and allied_force['nation'] == 'british':
                score += 10
            elif axis_force['nation'] == 'italian' and allied_force['nation'] == 'british':
                score += 10
            elif axis_force['nation'] == 'german' and allied_force['nation'] == 'american' and \
                 axis_force['quarter'] >= '1942q4':
                score += 10

            if score > best_score:
                best_score = score
                best_match = allied_force

        return best_match

    def generate_scenario(self, matchup: Dict) -> Optional[str]:
        """
        Generate complete Phase 9 scenario with all 7 JSON files

        Returns scenario directory path if successful
        """
        try:
            # Create scenario directory
            scenario_name = self._generate_scenario_name(matchup)
            scenario_dir = self.output_dir / scenario_name
            scenario_dir.mkdir(parents=True, exist_ok=True)

            # Generate each required file
            self._generate_oob_ground(matchup, scenario_dir)
            self._generate_supply_state(matchup, scenario_dir)
            self._generate_weather(matchup, scenario_dir)
            self._generate_map_data(matchup, scenario_dir)
            self._generate_victory_conditions(matchup, scenario_dir)
            self._generate_air_placeholders(matchup, scenario_dir)

            return str(scenario_dir)

        except Exception as e:
            print(f"    [ERROR] {scenario_name}: {e}")
            return None

    def _generate_scenario_name(self, matchup: Dict) -> str:
        """Generate scenario directory name"""
        quarter = matchup['quarter']
        size = matchup['scenario_size']

        axis_name = matchup['axis_force']['unit_name'].lower().replace(' ', '_')[:30]
        allied_name = matchup['allied_force']['unit_name'].lower().replace(' ', '_')[:30]

        return f"{quarter}_{axis_name}_vs_{allied_name}_{size}"

    def _generate_oob_ground(self, matchup: Dict, scenario_dir: Path):
        """Generate oob_ground.json with both forces and TO&E tables"""
        # This will use data from the unit JSONs directly
        axis_unit = matchup['axis_force']['unit_data']
        allied_unit = matchup['allied_force']['unit_data']

        oob = {
            'scenario_name': scenario_dir.name,
            'quarter': matchup['quarter'],
            'scenario_size': matchup['scenario_size'],
            'points_target': matchup['points_target'],
            'generated_at': datetime.now().isoformat(),

            'axis_force': {
                'nation': matchup['axis_force']['nation'],
                'unit_name': matchup['axis_force']['unit_name'],
                'experience': matchup['axis_force']['experience'],
                'toe': self._extract_toe_table(axis_unit),
                'equipment_summary': self._extract_equipment_summary(axis_unit)
            },

            'allied_force': {
                'nation': matchup['allied_force']['nation'],
                'unit_name': matchup['allied_force']['unit_name'],
                'experience': matchup['allied_force']['experience'],
                'toe': self._extract_toe_table(allied_unit),
                'equipment_summary': self._extract_equipment_summary(allied_unit)
            }
        }

        output_file = scenario_dir / 'oob_ground.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(oob, f, indent=2, ensure_ascii=False)

    def _extract_toe_table(self, unit_data: Dict) -> Dict:
        """Extract TO&E table from unit JSON"""
        toe = {
            'tanks': {},
            'artillery': {},
            'anti_tank': {},
            'infantry': {},
            'vehicles': {}
        }

        # Extract tanks
        if 'tanks' in unit_data and isinstance(unit_data['tanks'], dict):
            if 'variants' in unit_data['tanks']:
                for tank_name, tank_data in unit_data['tanks']['variants'].items():
                    if isinstance(tank_data, dict):
                        toe['tanks'][tank_name] = {
                            'count': tank_data.get('count', 0),
                            'type': tank_data.get('type', 'unknown'),
                            'gun': tank_data.get('gun', 'unknown')
                        }

        # Extract artillery
        for section in ['field_artillery', 'artillery']:
            if section in unit_data and isinstance(unit_data[section], dict):
                if 'variants' in unit_data[section]:
                    for gun_name, gun_data in unit_data[section]['variants'].items():
                        if isinstance(gun_data, dict):
                            toe['artillery'][gun_name] = {
                                'count': gun_data.get('count', 0),
                                'caliber': gun_data.get('caliber', 'unknown')
                            }

        # Extract AT guns
        if 'anti_tank' in unit_data and isinstance(unit_data['anti_tank'], dict):
            if 'variants' in unit_data['anti_tank']:
                for gun_name, gun_data in unit_data['anti_tank']['variants'].items():
                    if isinstance(gun_data, dict):
                        toe['anti_tank'][gun_name] = {
                            'count': gun_data.get('count', 0),
                            'caliber': gun_data.get('caliber', 'unknown')
                        }

        # Extract infantry (if available)
        if 'infantry' in unit_data:
            toe['infantry'] = unit_data['infantry']

        return toe

    def _extract_equipment_summary(self, unit_data: Dict) -> Dict:
        """Extract equipment summary counts"""
        summary = {
            'total_tanks': 0,
            'total_artillery': 0,
            'total_at_guns': 0,
            'total_personnel': unit_data.get('total_personnel', 0) or 0
        }

        # Count tanks
        if 'tanks' in unit_data:
            if isinstance(unit_data['tanks'], dict):
                summary['total_tanks'] = unit_data['tanks'].get('total', 0) or 0

        # Count artillery
        for section in ['field_artillery', 'artillery']:
            if section in unit_data and isinstance(unit_data[section], dict):
                total = unit_data[section].get('total', 0)
                summary['total_artillery'] += total if total is not None else 0

        # Count AT guns
        if 'anti_tank' in unit_data and isinstance(unit_data['anti_tank'], dict):
            summary['total_at_guns'] = unit_data['anti_tank'].get('total', 0) or 0

        return summary

    def _generate_supply_state(self, matchup: Dict, scenario_dir: Path):
        """Generate supply_state.json"""
        axis_unit = matchup['axis_force']['unit_data']
        allied_unit = matchup['allied_force']['unit_data']

        supply_state = {
            'quarter': matchup['quarter'],

            'axis_supply': self._extract_supply_data(axis_unit, matchup['axis_force']['nation']),
            'allied_supply': self._extract_supply_data(allied_unit, matchup['allied_force']['nation'])
        }

        output_file = scenario_dir / 'supply_state.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(supply_state, f, indent=2, ensure_ascii=False)

    def _extract_supply_data(self, unit_data: Dict, nation: str) -> Dict:
        """Extract supply logistics from unit JSON"""
        supply_logistics = unit_data.get('supply_logistics', {})

        return {
            'fuel_days': supply_logistics.get('fuel_days', 7),
            'ammunition_days': supply_logistics.get('ammunition_days', 7),
            'water_days': supply_logistics.get('water_days', 7),
            'operational_radius_km': supply_logistics.get('operational_radius_km', 200),
            'supply_status': supply_logistics.get('supply_status', 'adequate'),
            'notes': supply_logistics.get('notes', 'Standard operational supply levels')
        }

    def _generate_weather(self, matchup: Dict, scenario_dir: Path):
        """Generate weather.json"""
        # Extract from unit data if available
        axis_unit = matchup['axis_force']['unit_data']
        weather_env = axis_unit.get('weather_environment', {})

        quarter = matchup['quarter']
        season = self._determine_season(quarter)

        weather = {
            'quarter': quarter,
            'season': season,
            'terrain_type': weather_env.get('terrain_type', 'Desert - sparse cover, open sightlines'),
            'temperature_range_celsius': weather_env.get('temperature_range_celsius', [25, 45]),
            'seasonal_impacts': weather_env.get('seasonal_impacts', [
                'Extreme heat during day',
                'Dust storms reduce visibility',
                'Clear skies favor air operations'
            ]),
            'environmental_challenges': weather_env.get('environmental_challenges', [
                'Water scarcity',
                'Engine overheating',
                'Sand damage to equipment'
            ]),
            'visibility_km': 10,
            'precipitation': 'none',
            'wind_speed_kph': 15
        }

        output_file = scenario_dir / 'weather.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(weather, f, indent=2, ensure_ascii=False)

    def _determine_season(self, quarter: str) -> str:
        """Determine season from quarter"""
        q = quarter.split('q')[1] if 'q' in quarter else '1'
        seasons = {'1': 'Winter', '2': 'Spring', '3': 'Summer', '4': 'Autumn'}
        return seasons.get(q, 'Summer')

    def _generate_map_data(self, matchup: Dict, scenario_dir: Path):
        """Generate map_data.json"""
        size = matchup['scenario_size']

        # Table sizes based on scenario size
        table_sizes = {
            'squad': {'width_cm': 120, 'length_cm': 120},  # 4'x4'
            'platoon': {'width_cm': 120, 'length_cm': 180},  # 4'x6'
            'company': {'width_cm': 180, 'length_cm': 240},  # 6'x8'
            'battalion': {'width_cm': 240, 'length_cm': 360}  # 8'x12'
        }

        map_data = {
            'scenario_size': size,
            'table_dimensions': table_sizes.get(size, table_sizes['platoon']),
            'terrain_features': [
                {'type': 'hill', 'position': 'center', 'elevation_m': 50},
                {'type': 'wadi', 'position': 'left_flank', 'depth_m': 3},
                {'type': 'rocky_outcrop', 'position': 'right_flank', 'size': 'small'},
                {'type': 'sparse_vegetation', 'coverage': '10%'}
            ],
            'deployment_zones': {
                'axis': {
                    'edge': 'north',
                    'depth_cm': 30,
                    'description': 'Axis forces deploy within 30cm of north table edge'
                },
                'allied': {
                    'edge': 'south',
                    'depth_cm': 30,
                    'description': 'Allied forces deploy within 30cm of south table edge'
                }
            },
            'objectives': [
                {'type': 'capture_point', 'location': 'center_hill', 'points': 3},
                {'type': 'capture_point', 'location': 'left_wadi', 'points': 2},
                {'type': 'capture_point', 'location': 'right_outcrop', 'points': 2}
            ]
        }

        output_file = scenario_dir / 'map_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)

    def _generate_victory_conditions(self, matchup: Dict, scenario_dir: Path):
        """Generate victory_conditions.json"""
        victory = {
            'scenario_type': 'meeting_engagement',
            'primary_victory': {
                'type': 'break_enemy_force',
                'description': 'Force enemy to withdraw by exceeding their break point',
                'scoring': 'First side to exceed break point loses'
            },
            'secondary_objectives': [
                {
                    'type': 'capture_objectives',
                    'description': 'Control 2 of 3 objectives at game end',
                    'points': 3
                },
                {
                    'type': 'destroy_enemy_command',
                    'description': 'Destroy or route enemy command unit',
                    'points': 2
                },
                {
                    'type': 'minimize_casualties',
                    'description': 'Take fewer casualties than opponent',
                    'points': 1
                }
            ],
            'turn_limit': self._determine_turn_limit(matchup['scenario_size']),
            'sudden_death': 'Game ends immediately when one side breaks',
            'draw_conditions': 'Both sides break simultaneously or neither breaks by turn limit'
        }

        output_file = scenario_dir / 'victory_conditions.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(victory, f, indent=2, ensure_ascii=False)

    def _determine_turn_limit(self, size: str) -> int:
        """Determine turn limit based on scenario size"""
        limits = {
            'squad': 6,
            'platoon': 8,
            'company': 10,
            'battalion': 12
        }
        return limits.get(size, 8)

    def _generate_air_placeholders(self, matchup: Dict, scenario_dir: Path):
        """Generate placeholder files for Phase 8 (Air Forces)"""
        # oob_air.json placeholder
        oob_air = {
            'status': 'Phase 8 not yet implemented',
            'note': 'Air order of battle will be populated after Phase 8 air forces integration',
            'quarter': matchup['quarter'],
            'axis_air': {
                'available': False,
                'units': []
            },
            'allied_air': {
                'available': False,
                'units': []
            }
        }

        output_file = scenario_dir / 'oob_air.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(oob_air, f, indent=2, ensure_ascii=False)

        # air_support.json placeholder
        air_support = {
            'status': 'Phase 8 not yet implemented',
            'note': 'Air support data (sortie rates, aircraft availability) will be populated after Phase 8',
            'quarter': matchup['quarter'],
            'axis_sortie_rate': 0,
            'allied_sortie_rate': 0
        }

        output_file = scenario_dir / 'air_support.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(air_support, f, indent=2, ensure_ascii=False)


def main():
    """Generate Phase 9 battle scenarios"""
    print("\n" + "="*80)
    print("Phase 9 Scenario Matchmaker")
    print("="*80)

    matchmaker = ScenarioMatchmaker()

    # Step 1: Scan available forces
    matchmaker.scan_available_forces()

    # Step 2: Generate matchups
    matchups = matchmaker.generate_matchups(max_per_quarter=5)  # Limit for initial test

    if not matchups:
        print("\n[ERROR] No matchups generated. Check available forces.")
        return

    # Step 3: Generate scenarios
    print(f"\n[Phase 9] Generating {len(matchups)} scenarios...")

    results = {
        'generated': 0,
        'failed': 0,
        'scenarios': []
    }

    for matchup in matchups:
        scenario_name = matchmaker._generate_scenario_name(matchup)
        print(f"\n  Generating: {scenario_name}")

        scenario_dir = matchmaker.generate_scenario(matchup)

        if scenario_dir:
            results['generated'] += 1
            results['scenarios'].append(scenario_dir)
            print(f"    [OK] Created {scenario_dir}")
        else:
            results['failed'] += 1

    # Summary
    print(f"\n{'='*80}")
    print(f"Phase 9 Scenario Generation Complete")
    print(f"{'='*80}")
    print(f"  Scenarios generated: {results['generated']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Output directory: data/output/battle_scenarios/")
    print(f"{'='*80}\n")

    return results


if __name__ == '__main__':
    main()
