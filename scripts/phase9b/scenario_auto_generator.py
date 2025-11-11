#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 9B Phase 2.2: Scenario Auto-Generator from BG Builder Army Lists

Generates complete BattleGroup scenarios from imported army lists with:
- Historical battlefield locations from Phase 6 data
- Terrain and weather appropriate to quarter/location
- Victory conditions based on force composition
- Deployment zones and special rules
- Integration with Phase 9B book structure

Author: North Africa TO&E Builder
Date: November 11, 2025
"""

import json
import sys
import io
import random
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
SCENARIOS_DIR = Path("D:/north-africa-toe-builder/data/output/bg_builder_scenarios")
OUTPUT_DIR = Path("D:/north-africa-toe-builder/books")

# Historical North Africa battlefield locations by quarter
BATTLEFIELD_LOCATIONS = {
    '1940q2': ['Bardia', 'Fort Capuzzo', 'Sollum', 'Halfaya Pass'],
    '1940q3': ['Sidi Barrani', 'Buq Buq', 'Maktila'],
    '1940q4': ['Sidi Barrani', 'Bardia', 'Tobruk', 'Beda Fomm'],
    '1941q1': ['Tobruk', 'Derna', 'Benghazi', 'El Agheila'],
    '1941q2': ['Halfaya Pass', 'Fort Capuzzo', 'Sidi Barrani', 'Sollum'],
    '1941q3': ['Tobruk Perimeter', 'Bardia', 'Halfaya Pass'],
    '1941q4': ['Sidi Rezegh', 'Bir el Gubi', 'Tobruk Relief Corridor', 'Point 175'],
    '1942q1': ['Gazala Line', 'Bir Hacheim', 'El Adem'],
    '1942q2': ['Gazala', 'Bir Hacheim', 'Knightsbridge Box', 'Tobruk'],
    '1942q3': ['El Alamein', 'Alam Halfa Ridge', 'Ruweisat Ridge', 'Miteirya Ridge'],
    '1942q4': ['El Alamein', 'Kidney Ridge', 'Tel el Aqqaqir', 'Rahman Track'],
    '1943q1': ['Mareth Line', 'Kasserine Pass', 'Medenine', 'Wadi Akarit'],
    '1943q2': ['Enfidaville', 'Tunis', 'Bizerte', 'Cape Bon']
}

# Terrain types by location characteristics
TERRAIN_TYPES = {
    'desert_open': ['Open desert with scattered rocks', 'Flat desert with good visibility', 'Sandy desert with dunes'],
    'desert_rough': ['Rocky desert with wadis', 'Broken ground with escarpments', 'Desert with ridge lines'],
    'coastal': ['Coastal plain', 'Mediterranean coastline', 'Coastal escarpment'],
    'urban': ['Town outskirts', 'Village ruins', 'Fortified position'],
    'fortified': ['Defensive box', 'Fortified line', 'Prepared positions']
}

# Weather conditions by quarter
WEATHER_CONDITIONS = {
    '1940q2': 'Hot and dry, excellent visibility',
    '1940q3': 'Extreme heat, dust storms possible',
    '1940q4': 'Cooler temperatures, occasional rain',
    '1941q1': 'Mild temperatures, clear skies',
    '1941q2': 'Hot and dry, sandstorms possible',
    '1941q3': 'Extreme heat, limited visibility from heat haze',
    '1941q4': 'Cooler, rainy season begins',
    '1942q1': 'Mild temperatures, clear visibility',
    '1942q2': 'Hot and dry, dust devils common',
    '1942q3': 'Extreme heat, limited water availability',
    '1942q4': 'Cooler temperatures, occasional rain',
    '1943q1': 'Rainy season, muddy conditions',
    '1943q2': 'Spring conditions, improving weather'
}

@dataclass
class ScenarioTemplate:
    """Template for auto-generated scenario."""
    title: str
    location: str
    date: str
    quarter: str
    terrain: str
    weather: str
    attacker: str
    defender: str
    attacker_objective: str
    defender_objective: str
    victory_conditions: List[str]
    deployment_notes: str
    special_rules: List[str]
    turn_limit: int
    recommended_table_size: str

class ScenarioAutoGenerator:
    """Auto-generate scenarios from BG Builder army lists."""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        self.conn.close()

    def load_imported_scenario(self, scenario_path: Path) -> Optional[Dict]:
        """Load scenario JSON from bg_builder_import."""
        try:
            with open(scenario_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def determine_force_role(self, force_data: Dict) -> str:
        """
        Determine if force is attacker or defender based on composition.

        High armor/mobile = attacker
        High infantry/artillery = defender
        """
        units = force_data.get('units', [])

        armor_count = 0
        infantry_count = 0

        for unit in units:
            name_lower = unit['name'].lower()
            if any(x in name_lower for x in ['panzer', 'tank', 'armour', 'armor', 'cruiser']):
                armor_count += unit['quantity']
            elif any(x in name_lower for x in ['infantry', 'rifle', 'regiment']):
                infantry_count += unit['quantity']

        return 'attacker' if armor_count > infantry_count else 'defender'

    def generate_victory_conditions(self, attacker_br: int, defender_br: int) -> List[str]:
        """Generate victory conditions based on force sizes."""
        conditions = []

        # BR-based objectives
        attacker_target = int(defender_br * 0.6)
        defender_target = int(attacker_br * 0.5)

        conditions.append(f"Attacker wins by breaking defender (inflicting {attacker_target}+ BR)")
        conditions.append(f"Defender wins by breaking attacker (inflicting {defender_target}+ BR)")
        conditions.append("Draw if neither side breaks by turn limit")

        return conditions

    def generate_deployment_zones(self, table_size: str) -> str:
        """Generate deployment zone description."""
        if '6x4' in table_size:
            return "Attacker deploys within 12\" of short table edge. Defender deploys within 18\" of opposite edge, with prepared positions."
        else:
            return "Attacker deploys within 18\" of long table edge. Defender deploys within 24\" of opposite edge."

    def select_special_rules(self, quarter: str, location: str) -> List[str]:
        """Select appropriate special rules for scenario."""
        rules = []

        # Heat rules for summer
        if quarter in ['1941q2', '1941q3', '1942q2', '1942q3']:
            rules.append("Heat Haze: Visibility limited to 48\" for ranged fire")
            rules.append("Water Supply: Units must be within 12\" of water source or vehicle by turn 6")

        # Dust/sandstorms
        if quarter in ['1941q2', '1942q2']:
            rules.append("Dust Storms: Roll D6 each turn, on 5-6 visibility reduced to 24\"")

        # Fortified positions
        if 'fortified' in location.lower() or 'box' in location.lower():
            rules.append("Prepared Positions: Defender has minefields and wire")
            rules.append("Defender may pre-place 3 minefield markers")

        return rules if rules else ["Standard BattleGroup rules apply"]

    def generate_scenario_from_imported(self, scenario_data: Dict) -> Dict:
        """
        Generate complete scenario from imported BG Builder data.

        Args:
            scenario_data: Imported scenario from bg_builder_import.py

        Returns:
            Complete scenario dictionary ready for book integration
        """
        quarter = scenario_data['date']
        nation = list(scenario_data['forces'].keys())[0]
        force_data = scenario_data['forces'][nation]

        # Select battlefield location
        locations = BATTLEFIELD_LOCATIONS.get(quarter, ['North Africa'])
        location = random.choice(locations)

        # Determine terrain
        if 'tobruk' in location.lower() or 'box' in location.lower():
            terrain_type = random.choice(TERRAIN_TYPES['fortified'])
        elif 'ridge' in location.lower() or 'escarpment' in location.lower():
            terrain_type = random.choice(TERRAIN_TYPES['desert_rough'])
        else:
            terrain_type = random.choice(TERRAIN_TYPES['desert_open'])

        # Weather
        weather = WEATHER_CONDITIONS.get(quarter, 'Clear and dry')

        # Determine roles
        role = self.determine_force_role(force_data)
        attacker_nation = nation if role == 'attacker' else 'british'  # Assume opposing force
        defender_nation = 'british' if role == 'attacker' else nation

        # Victory conditions
        br = force_data['battle_rating']
        opposing_br = int(br * 1.1)  # Slightly larger opposing force
        victory_conditions = self.generate_victory_conditions(br if role == 'attacker' else opposing_br,
                                                               opposing_br if role == 'attacker' else br)

        # Special rules
        special_rules = self.select_special_rules(quarter, location)

        # Table size based on force size
        points = force_data['total_points']
        if points < 500:
            table_size = '6x4 feet'
            turn_limit = 8
        elif points < 1000:
            table_size = '8x6 feet'
            turn_limit = 10
        else:
            table_size = '12x6 feet'
            turn_limit = 12

        # Build complete scenario
        complete_scenario = {
            'title': f"{scenario_data['title']} - {location}",
            'location': location,
            'date': quarter,
            'quarter': quarter,
            'terrain': terrain_type,
            'weather': weather,
            'table_size': table_size,
            'turn_limit': turn_limit,
            'attacker': attacker_nation.title(),
            'defender': defender_nation.title(),
            'forces': scenario_data['forces'],
            'historical_context': scenario_data.get('historical_context', {}),
            'objectives': {
                'attacker': f"Seize {location} and break defender morale",
                'defender': f"Hold {location} and repel attacker"
            },
            'victory_conditions': victory_conditions,
            'deployment': self.generate_deployment_zones(table_size),
            'special_rules': special_rules,
            'terrain_setup': self._generate_terrain_setup(terrain_type),
            'scenario_notes': f"Generated from BG Builder import: {scenario_data['metadata']['import_file']}",
            'metadata': scenario_data.get('metadata', {})
        }

        return complete_scenario

    def _generate_terrain_setup(self, terrain_type: str) -> List[str]:
        """Generate terrain placement suggestions."""
        terrain = []

        if 'desert' in terrain_type.lower():
            terrain.extend([
                "3-4 rocky outcrops (soft cover)",
                "2-3 low ridges or escarpments (hard cover)",
                "1-2 wadis or depressions (concealment)",
                "Scattered scrub bushes (light cover)"
            ])

        if 'fortified' in terrain_type.lower():
            terrain.extend([
                "Defensive trenches along defender edge",
                "Wire obstacles (6\" strips)",
                "3 minefield markers (pre-placed by defender)",
                "Sandbagged positions"
            ])

        if 'urban' in terrain_type.lower():
            terrain.extend([
                "2-3 ruined buildings (hard cover)",
                "Stone walls and rubble (soft cover)",
                "Roads connecting built-up areas"
            ])

        return terrain if terrain else ["Sparse desert terrain, 4-6 terrain pieces"]

    def generate_markdown_scenario(self, scenario: Dict) -> str:
        """Generate markdown formatted scenario for book integration."""
        md = f"""## {scenario['title']}

**Location:** {scenario['location']}
**Date:** {scenario['quarter']}
**Table Size:** {scenario['table_size']}
**Turn Limit:** {scenario['turn_limit']} turns

### Historical Context

{scenario.get('scenario_notes', 'Auto-generated scenario from BG Builder army list.')}

### Terrain

**Type:** {scenario['terrain']}
**Weather:** {scenario['weather']}

**Terrain Setup:**
"""

        for item in scenario['terrain_setup']:
            md += f"- {item}\n"

        md += f"""
### Forces

**Attacker:** {scenario['attacker']}
**Defender:** {scenario['defender']}

"""

        # Add force details
        for nation, force in scenario['forces'].items():
            md += f"**{nation.title()} Force ({force['force_name']})**\n"
            md += f"- Battle Rating: {force['battle_rating']}\n"
            md += f"- Total Points: {force['total_points']}\n\n"
            md += "Units:\n"
            for unit in force['units']:
                md += f"- {unit['quantity']}x {unit['name']} ({unit['cost_per_unit']} pts, BR {unit['br_per_unit']})\n"
            md += "\n"

        md += """### Objectives

"""
        md += f"**Attacker:** {scenario['objectives']['attacker']}\n"
        md += f"**Defender:** {scenario['objectives']['defender']}\n\n"

        md += """### Victory Conditions

"""
        for condition in scenario['victory_conditions']:
            md += f"- {condition}\n"

        md += f"""
### Deployment

{scenario['deployment']}

### Special Rules

"""
        for rule in scenario['special_rules']:
            md += f"- {rule}\n"

        return md

    def generate_all_scenarios(self) -> List[Dict]:
        """Generate scenarios from all imported army lists."""
        if not SCENARIOS_DIR.exists():
            print(f"No scenarios directory found: {SCENARIOS_DIR}")
            return []

        scenario_files = list(SCENARIOS_DIR.glob('*.json'))
        print(f"Found {len(scenario_files)} imported scenarios")

        generated = []

        for scenario_file in scenario_files:
            print(f"\nProcessing: {scenario_file.name}")

            # Load imported scenario
            imported = self.load_imported_scenario(scenario_file)
            if not imported:
                continue

            # Generate complete scenario
            complete = self.generate_scenario_from_imported(imported)
            generated.append(complete)

            # Save to output
            output_file = scenario_file.parent / f"complete_{scenario_file.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(complete, f, indent=2)

            print(f"  Generated: {complete['title']}")
            print(f"  Location: {complete['location']}")
            print(f"  Table: {complete['table_size']}, {complete['turn_limit']} turns")

        return generated

def main():
    """Main execution."""
    print("="*80)
    print("PHASE 9B PHASE 2.2: SCENARIO AUTO-GENERATOR")
    print("="*80)

    generator = ScenarioAutoGenerator()

    try:
        scenarios = generator.generate_all_scenarios()

        if scenarios:
            print(f"\n✓ Generated {len(scenarios)} complete scenarios")

            # Generate markdown versions
            print("\nGenerating markdown scenarios...")
            for scenario in scenarios:
                md_content = generator.generate_markdown_scenario(scenario)

                # Save markdown
                md_file = SCENARIOS_DIR / f"{scenario['title'].replace(' ', '_').lower()}.md"
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                print(f"  {md_file.name}")

            print(f"\n✓ Saved markdown scenarios to: {SCENARIOS_DIR}")
        else:
            print("\nNo imported scenarios found.")
            print("Run bg_builder_import.py first to import army lists.")

        print("\n" + "="*80)
        print("✅ GENERATION COMPLETE")
        print("="*80)

    finally:
        generator.close()

if __name__ == '__main__':
    main()
