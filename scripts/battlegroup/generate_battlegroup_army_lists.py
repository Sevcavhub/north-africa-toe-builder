#!/usr/bin/env python3
"""
BattleGroup Army List Generator - Creates playable 400-600 point army lists

This script:
1. Reads platoon and company templates
2. Calculates BattleGroup points for each unit
3. Generates balanced army lists (400/500/600 points)
4. Applies historical constraints by battle/quarter
5. Creates markdown army lists for each battle

Author: Claude Code (Sonnet 4.5)
Date: 2025-11-02
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class BattleGroupPoints:
    """BattleGroup points values for units and weapons."""

    # Infantry
    rifle_section_british: int = 40  # 10 men, 1 Bren, 7 rifles
    rifle_section_german: int = 60   # 10 men, 2 MG34/42
    rifle_section_italian: int = 35  # 10 men, 2 Breda (binary)
    rifle_section_american: int = 50  # 12 men, BAR

    # Platoons (calculated from sections + HQ)
    platoon_british: int = 160  # 3 sections + HQ + 2" mortar
    platoon_german: int = 310   # 3 squads + AT rifle + 2x PaK guns
    platoon_italian: int = 120  # 2 sections (binary)
    platoon_american: int = 180  # 3 squads + 60mm mortar

    # Company (calculated from platoons + support)
    company_british: int = 560  # 3 platoons + HQ + 2x 2-pdr
    company_german: int = 980   # 3 platoons + HQ + 2x MMG + mortars
    company_italian: int = 390  # 3 platoons + HQ + 2x MMG

    # Support Weapons
    at_gun_2pdr: int = 40
    at_gun_6pdr: int = 55
    pak38_5cm: int = 45
    pak36r_76mm: int = 65
    italian_47_32: int = 35

    # Machine Guns
    vickers_mmg: int = 30
    mg34_42_mmg: int = 35
    breda_37_mmg: int = 25

    # Mortars
    mortar_2inch: int = 15
    mortar_3inch: int = 35
    mortar_8cm: int = 40
    mortar_81mm: int = 40

    # Artillery (off-table)
    artillery_25pdr: int = 60
    artillery_105mm: int = 70
    artillery_149mm: int = 90

    # Vehicles
    bren_carrier: int = 20
    sdkfz_251: int = 35
    truck_transport: int = 10

    # Tanks (per tank)
    matilda_ii: int = 145
    crusader: int = 95
    stuart_m3: int = 75
    panzer_iii: int = 110
    panzer_iv: int = 130
    m13_40: int = 85
    m14_41: int = 90

    # Battle Rating modifiers
    br_veteran: float = 1.2
    br_regular: float = 1.0
    br_inexperienced: float = 0.8


class ArmyListGenerator:
    """Generates BattleGroup army lists from templates."""

    def __init__(self, platoons_dir: Path, companies_dir: Path, output_dir: Path):
        self.platoons_dir = platoons_dir
        self.companies_dir = companies_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.points = BattleGroupPoints()
        self.stats = {
            'lists_generated': 0,
            'errors': []
        }

    def calculate_platoon_points(self, platoon_data: dict) -> int:
        """Calculate BattleGroup points for a platoon."""
        nation = platoon_data['nation']

        # Base points by nation
        points_map = {
            'british': self.points.platoon_british,
            'german': self.points.platoon_german,
            'italian': self.points.platoon_italian,
            'american': self.points.platoon_american,
            'french': self.points.platoon_british  # Free French use British org
        }

        return points_map.get(nation, 150)

    def calculate_company_points(self, company_data: dict) -> int:
        """Calculate BattleGroup points for a company."""
        nation = company_data['nation']

        points_map = {
            'british': self.points.company_british,
            'german': self.points.company_german,
            'italian': self.points.company_italian,
            'american': 600,  # Estimated
            'french': self.points.company_british
        }

        return points_map.get(nation, 500)

    def find_templates_by_nation_quarter(self, nation: str, quarter: str) -> Dict[str, List[Path]]:
        """Find all platoon and company templates for a nation/quarter."""
        templates = {
            'platoons': [],
            'companies': []
        }

        # Find platoons
        platoon_pattern = f"{nation}_{quarter}_*_platoon*_toe.json"
        templates['platoons'] = list(self.platoons_dir.glob(platoon_pattern))

        # Find companies
        company_pattern = f"{nation}_{quarter}_*_company*_toe.json"
        templates['companies'] = list(self.companies_dir.glob(company_pattern))

        return templates

    def generate_army_list(self, nation: str, quarter: str, points_target: int, battle_name: str) -> dict:
        """Generate a balanced army list for specified points."""

        templates = self.find_templates_by_nation_quarter(nation, quarter)

        if not templates['platoons'] and not templates['companies']:
            return None

        # Strategy: Build list from platoons
        army_list = {
            'battle': battle_name,
            'nation': nation,
            'quarter': quarter,
            'points_target': points_target,
            'points_actual': 0,
            'core_units': [],
            'support_weapons': [],
            'special_rules': []
        }

        # Add platoons until we reach points target
        points_used = 0
        platoon_count = 0

        for platoon_file in templates['platoons'][:6]:  # Max 6 platoons (2 companies)
            with open(platoon_file, encoding='utf-8') as f:
                platoon_data = json.load(f)

            platoon_points = self.calculate_platoon_points(platoon_data)

            if points_used + platoon_points <= points_target + 50:  # Allow 50 point buffer
                army_list['core_units'].append({
                    'type': 'Rifle Platoon',
                    'designation': platoon_data['unit_designation'].split(' - ')[-1],  # Just "Platoon 1"
                    'personnel': platoon_data['total_personnel'],
                    'sections': platoon_data['tactical_organization']['sections'],
                    'points': platoon_points,
                    'equipment': platoon_data['equipment_summary']
                })
                points_used += platoon_points
                platoon_count += 1

                if points_used >= points_target - 100:
                    break

        # Add support weapons to fill remaining points
        remaining_points = points_target - points_used

        if nation == 'british':
            # Add AT guns
            if remaining_points >= self.points.at_gun_2pdr:
                num_at_guns = min(2, remaining_points // self.points.at_gun_2pdr)
                army_list['support_weapons'].append({
                    'type': 'QF 2-pounder AT Gun',
                    'count': num_at_guns,
                    'points': num_at_guns * self.points.at_gun_2pdr
                })
                points_used += num_at_guns * self.points.at_gun_2pdr
                remaining_points -= num_at_guns * self.points.at_gun_2pdr

            # Add artillery
            if remaining_points >= self.points.artillery_25pdr:
                army_list['support_weapons'].append({
                    'type': '25-pdr Field Artillery (off-table)',
                    'count': 1,
                    'points': self.points.artillery_25pdr
                })
                points_used += self.points.artillery_25pdr

        elif nation == 'german':
            # German platoons already have AT guns
            # Add artillery or extra MMG
            if remaining_points >= self.points.mg34_42_mmg:
                num_mmg = min(2, remaining_points // self.points.mg34_42_mmg)
                army_list['support_weapons'].append({
                    'type': 'MG34/42 MMG Team',
                    'count': num_mmg,
                    'points': num_mmg * self.points.mg34_42_mmg
                })
                points_used += num_mmg * self.points.mg34_42_mmg

        elif nation == 'italian':
            # Add AT guns (regiment level)
            if remaining_points >= self.points.italian_47_32:
                num_at_guns = min(2, remaining_points // self.points.italian_47_32)
                army_list['support_weapons'].append({
                    'type': '47/32 AT Gun',
                    'count': num_at_guns,
                    'points': num_at_guns * self.points.italian_47_32
                })
                points_used += num_at_guns * self.points.italian_47_32

        army_list['points_actual'] = points_used

        # Add special rules by nation
        if nation == 'british':
            army_list['special_rules'] = [
                'Desert Rats: +1 morale in defensive positions',
                'Reconnaissance Excellence: +1 to spotting rolls',
                'Limited AT capability: Only 2-pdr available in 1941'
            ]
        elif nation == 'german':
            army_list['special_rules'] = [
                'Tactical Flexibility: May regroup after failed order',
                '88mm Effectiveness: Dual-purpose AA/AT',
                'Stutzpunkt Organization: All-round defense'
            ]
        elif nation == 'italian':
            army_list['special_rules'] = [
                'Variable Morale: Roll 2d6 for morale, use lowest',
                'Binary System: Squads specialized fire/maneuver',
                'Limited Equipment: Poor AT capability'
            ]

        return army_list

    def generate_markdown_army_list(self, army_list: dict) -> str:
        """Generate markdown formatted army list."""

        lines = []
        lines.append(f"# {army_list['battle']} - {army_list['nation'].capitalize()} Army List")
        lines.append(f"\n**Quarter**: {army_list['quarter']}")
        lines.append(f"**Points**: {army_list['points_actual']}/{army_list['points_target']}\n")

        lines.append("## Core Infantry Units\n")
        for unit in army_list['core_units']:
            lines.append(f"### {unit['designation']}")
            lines.append(f"- **Personnel**: {unit['personnel']} men")
            lines.append(f"- **Sections**: {unit['sections']}")
            lines.append(f"- **Equipment**:")
            eq = unit['equipment']
            lines.append(f"  - {eq['rifles']}x {eq['rifle_type']}")
            lines.append(f"  - {eq['lmg']}x {eq['lmg_type']}")
            if eq.get('mortars', 0) > 0:
                lines.append(f"  - {eq['mortars']}x Mortar")
            if eq.get('at_guns', 0) > 0:
                lines.append(f"  - {eq['at_guns']}x AT Gun")
            lines.append(f"- **BattleGroup Points**: {unit['points']}\n")

        if army_list['support_weapons']:
            lines.append("## Support Weapons\n")
            for weapon in army_list['support_weapons']:
                lines.append(f"- **{weapon['count']}x {weapon['type']}** - {weapon['points']} points")
            lines.append("")

        if army_list['special_rules']:
            lines.append("## Special Rules\n")
            for rule in army_list['special_rules']:
                lines.append(f"- {rule}")
            lines.append("")

        lines.append("## Force Summary\n")
        total_personnel = sum(u['personnel'] for u in army_list['core_units'])
        lines.append(f"- **Total Personnel**: {total_personnel}")
        lines.append(f"- **Platoons**: {len(army_list['core_units'])}")
        lines.append(f"- **Total Points**: {army_list['points_actual']}")

        return '\n'.join(lines)

    def generate_lists_for_battle(self, battle_name: str, nations_quarters: List[Tuple[str, str]], points: List[int]):
        """Generate army lists for a specific battle."""

        battle_dir = self.output_dir / battle_name.lower().replace(' ', '_')
        battle_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nGenerating lists for: {battle_name}")

        for nation, quarter in nations_quarters:
            for point_value in points:
                army_list = self.generate_army_list(nation, quarter, point_value, battle_name)

                if not army_list:
                    print(f"  WARNING: No templates found for {nation} {quarter}")
                    continue

                # Generate markdown
                markdown = self.generate_markdown_army_list(army_list)

                # Save file
                filename = f"{nation}_{point_value}pts.md"
                filepath = battle_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown)

                self.stats['lists_generated'] += 1
                print(f"  Generated: {nation.capitalize()} {point_value}pts ({army_list['points_actual']} actual)")

    def run(self):
        """Main execution - generate lists for all battles."""
        print("=" * 80)
        print("BattleGroup Army List Generator v1.0")
        print("=" * 80)
        print(f"Platoons directory: {self.platoons_dir}")
        print(f"Companies directory: {self.companies_dir}")
        print(f"Output directory: {self.output_dir}")
        print("=" * 80)

        # Define battles and available forces
        # For now, use the Czechoslovak battalion we have
        battles = [
            {
                'name': 'Syria-Lebanon Campaign',
                'nations_quarters': [
                    ('british', '1941q3'),  # Czechoslovak battalion
                    ('british', '1941q4'),
                ],
                'points': [400, 500, 600]
            }
        ]

        for battle in battles:
            self.generate_lists_for_battle(
                battle['name'],
                battle['nations_quarters'],
                battle['points']
            )

        # Print summary
        print("\n" + "=" * 80)
        print("GENERATION COMPLETE")
        print("=" * 80)
        print(f"Army lists generated: {self.stats['lists_generated']}")

        if self.stats['errors']:
            print(f"\nErrors: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print("\nNo errors!")

        print(f"\nOutput saved to: {self.output_dir}")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    platoons_dir = project_root / 'data' / 'output' / 'platoons'
    companies_dir = project_root / 'data' / 'output' / 'companies'
    output_dir = project_root / 'books' / 'army_lists_tactical'

    generator = ArmyListGenerator(platoons_dir, companies_dir, output_dir)
    generator.run()


if __name__ == '__main__':
    main()
