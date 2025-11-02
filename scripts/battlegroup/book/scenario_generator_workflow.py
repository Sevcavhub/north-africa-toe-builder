#!/usr/bin/env python3
"""
BattleGroup Book Scenario Generation Workflow

Orchestrates the complete workflow for generating historical scenarios:
1. Research Phase - Parse scenario_research.md for historical data
2. Unit Selection - Query Phase 6 unit JSONs
3. Force Roster Generation - Build force rosters with equipment
4. Terrain Setup - Create battlefield terrain features
5. Scenario Assembly - Construct complete Scenario objects
6. Integration - Save to book directories

Part of Phase 9B Step 6 (Book Generation).

Usage:
    # Generate single scenario
    python scenario_generator_workflow.py --battle battleaxe --scenario 1

    # Generate all scenarios for a battle
    python scenario_generator_workflow.py --battle battleaxe --all

    # Generate all 45 scenarios
    python scenario_generator_workflow.py --all-battles

Author: North Africa TO&E Builder
Date: November 2, 2025
"""

import json
import sqlite3
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add project directories to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "battlegroup" / "generators"))

# Import from generators
from historical_scenario_generator import (
    Scenario, SituationReport, BattlefieldSetup, BattleDescription,
    Objectives, ForceRoster, Deployment, AlternativeForces, TerrainFeature,
    ScenarioType, TableSize, VictoryType
)
from phase6_unit_parser import Phase6UnitParser

# Paths
DATABASE_PATH = project_root / "database" / "master_database.db"
RESEARCH_DOC = project_root / "books" / "scenario_research.md"
BOOKS_DIR = project_root / "books"
UNITS_DIR = project_root / "data" / "output" / "units"


@dataclass
class ScenarioResearchData:
    """Parsed scenario research data"""
    scenario_number: int
    title: str
    date: str
    location: str
    scale: str
    points: str  # e.g., "600-800 points"
    historical_engagement: str
    forces: Dict[str, str]  # {"British": "...", "Axis": "..."}
    terrain: str
    objectives: Dict[str, str]  # {"British": "...", "Axis": "..."}
    special_rules: List[str]
    historical_outcome: str
    phase6_units: List[str]  # e.g., ["british_1941q2_7th_armoured_division_toe.json"]


class ScenarioResearchParser:
    """Parses scenario_research.md to extract scenario data"""

    def __init__(self, research_file: Path = RESEARCH_DOC):
        self.research_file = research_file
        self.scenarios_by_battle = {
            "battleaxe": [],
            "crusader": [],
            "gazala": [],
            "first_alamein": []
        }

    def parse(self):
        """Parse the research document"""
        print(f"[RESEARCH] Parsing {self.research_file}")

        with open(self.research_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse each battle book section
        self._parse_battleaxe(content)
        self._parse_crusader(content)
        self._parse_gazala(content)
        self._parse_first_alamein(content)

        return self.scenarios_by_battle

    def _parse_battleaxe(self, content: str):
        """Parse Operation Battleaxe scenarios (8 scenarios)"""
        # Extract Battleaxe section
        pattern = r'## 📖 Book 1: Operation Battleaxe.*?(?=## 📖 Book 2:|$)'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print("[WARNING] Could not find Battleaxe section")
            return

        section = match.group(0)
        scenarios = self._extract_scenarios(section, "battleaxe")
        self.scenarios_by_battle["battleaxe"] = scenarios
        print(f"[RESEARCH] Found {len(scenarios)} Battleaxe scenarios")

    def _parse_crusader(self, content: str):
        """Parse Operation Crusader scenarios (12 scenarios)"""
        pattern = r'## 📖 Book 2: Operation Crusader.*?(?=## 📖 Book 3:|$)'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print("[WARNING] Could not find Crusader section")
            return

        section = match.group(0)
        scenarios = self._extract_scenarios(section, "crusader")
        self.scenarios_by_battle["crusader"] = scenarios
        print(f"[RESEARCH] Found {len(scenarios)} Crusader scenarios")

    def _parse_gazala(self, content: str):
        """Parse Gazala scenarios (15 scenarios)"""
        pattern = r'## 📖 Book 3: Gazala.*?(?=## 📖 Book 4:|$)'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print("[WARNING] Could not find Gazala section")
            return

        section = match.group(0)
        scenarios = self._extract_scenarios(section, "gazala")
        self.scenarios_by_battle["gazala"] = scenarios
        print(f"[RESEARCH] Found {len(scenarios)} Gazala scenarios")

    def _parse_first_alamein(self, content: str):
        """Parse First El Alamein scenarios (10 scenarios)"""
        pattern = r'## 📖 Book 4: First El Alamein.*?(?=$)'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print("[WARNING] Could not find First Alamein section")
            return

        section = match.group(0)
        scenarios = self._extract_scenarios(section, "first_alamein")
        self.scenarios_by_battle["first_alamein"] = scenarios
        print(f"[RESEARCH] Found {len(scenarios)} First Alamein scenarios")

    def _extract_scenarios(self, section: str, battle: str) -> List[ScenarioResearchData]:
        """Extract individual scenarios from a battle section"""
        scenarios = []

        # Find all scenario headers (### Scenario N: "Title")
        scenario_pattern = r'### Scenario (\d+): "([^"]+)".*?(?=### Scenario \d+:|## 📖|$)'
        matches = re.finditer(scenario_pattern, section, re.DOTALL)

        for match in matches:
            scenario_num = int(match.group(1))
            title = match.group(2)
            scenario_text = match.group(0)

            # Extract fields
            scenario = ScenarioResearchData(
                scenario_number=scenario_num,
                title=title,
                date=self._extract_field(scenario_text, r'\*\*Date\*\*: (.+)'),
                location=self._extract_field(scenario_text, r'\*\*Location\*\*: (.+)'),
                scale=self._extract_field(scenario_text, r'\*\*Scale\*\*: (.+)'),
                points=self._extract_field(scenario_text, r'\*\*Scale\*\*: [^(]+\(([^)]+)\)'),
                historical_engagement=self._extract_section(scenario_text, r'\*\*Historical Engagement\*\*:\n(.+?)(?=\n\*\*|$)'),
                forces=self._extract_forces(scenario_text),
                terrain=self._extract_field(scenario_text, r'\*\*Terrain\*\*: (.+)'),
                objectives=self._extract_objectives(scenario_text),
                special_rules=self._extract_special_rules(scenario_text),
                historical_outcome=self._extract_field(scenario_text, r'\*\*Historical Outcome\*\*: (.+)'),
                phase6_units=self._extract_phase6_units(scenario_text)
            )

            scenarios.append(scenario)
            print(f"  [{battle.upper()}] Scenario {scenario_num}: {title}")

        return scenarios

    def _extract_field(self, text: str, pattern: str) -> str:
        """Extract a single field using regex"""
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def _extract_section(self, text: str, pattern: str) -> str:
        """Extract a multi-line section"""
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_forces(self, text: str) -> Dict[str, str]:
        """Extract force descriptions"""
        forces = {}

        # Look for force listings like "- **British**: 1 squadron..."
        force_pattern = r'- \*\*([^:]+)\*\*: (.+?)(?=\n- \*\*|\n\n|\*\*Terrain|$)'
        matches = re.finditer(force_pattern, text, re.DOTALL)

        for match in matches:
            side = match.group(1).strip()
            description = match.group(2).strip()
            forces[side] = description

        return forces

    def _extract_objectives(self, text: str) -> Dict[str, str]:
        """Extract objectives for each side"""
        objectives = {}

        # Look for objectives section
        obj_section = re.search(r'\*\*Objectives\*\*:(.*?)(?=\n\*\*|$)', text, re.DOTALL)
        if not obj_section:
            return objectives

        obj_text = obj_section.group(1)

        # Extract individual objectives
        obj_pattern = r'- ([^:]+): (.+?)(?=\n- |\n\n|$)'
        matches = re.finditer(obj_pattern, obj_text, re.DOTALL)

        for match in matches:
            side = match.group(1).strip()
            objective = match.group(2).strip()
            objectives[side] = objective

        return objectives

    def _extract_special_rules(self, text: str) -> List[str]:
        """Extract special rules list"""
        rules = []

        # Look for special rules section
        rules_section = re.search(r'\*\*Special Rules\*\*:(.*?)(?=\n\*\*|$)', text, re.DOTALL)
        if not rules_section:
            return rules

        rules_text = rules_section.group(1)

        # Extract list items
        rule_pattern = r'- (.+?)(?=\n- |\n\n|$)'
        matches = re.finditer(rule_pattern, rules_text, re.DOTALL)

        for match in matches:
            rule = match.group(1).strip()
            rules.append(rule)

        return rules

    def _extract_phase6_units(self, text: str) -> List[str]:
        """Extract Phase 6 unit file references"""
        units = []

        # Look for Phase 6 Units section
        units_section = re.search(r'\*\*Phase 6 Units\*\*:(.*?)(?=\n###|\n---|\n## |$)', text, re.DOTALL)
        if not units_section:
            return units

        units_text = units_section.group(1)

        # Extract unit filenames
        unit_pattern = r'- (.+?\.json)'
        matches = re.finditer(unit_pattern, units_text)

        for match in matches:
            unit_file = match.group(1).strip()
            units.append(unit_file)

        return units


class ForceRosterBuilder:
    """Builds force rosters from Phase 6 unit data"""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.parser = Phase6UnitParser()

    def build_roster(
        self,
        nation: str,
        quarter: str,
        force_description: str,
        points_budget: int,
        experience: str = "regular"
    ) -> ForceRoster:
        """
        Build a force roster from description

        Args:
            nation: Nation code (e.g., "british")
            quarter: Quarter code (e.g., "1941q2")
            force_description: Text description of force (from research doc)
            points_budget: Points budget for the force
            experience: Unit experience level

        Returns:
            ForceRoster object
        """
        # For now, create a simple roster structure
        # In future iterations, this will parse force_description and query equipment

        units = []
        estimated_br = points_budget // 20  # Rough estimate: 20 pts per BR

        # Parse force description to extract unit types
        # This is a simplified version - full implementation would use Phase 6 data

        roster = ForceRoster(
            nation=nation,
            name=f"{nation.upper()} FORCES",
            battle_rating=estimated_br,
            points_budget=points_budget,
            units=units
        )

        return roster


class ScenarioWorkflow:
    """Main workflow orchestrator"""

    def __init__(self):
        self.research_parser = ScenarioResearchParser()
        self.roster_builder = ForceRosterBuilder()
        self.scenarios_data = {}

    def initialize(self):
        """Initialize workflow by parsing research document"""
        print("[WORKFLOW] Initializing scenario generation workflow...")
        self.scenarios_data = self.research_parser.parse()

        total = sum(len(scenarios) for scenarios in self.scenarios_data.values())
        print(f"[WORKFLOW] Loaded {total} scenarios across 4 battles")

    def generate_scenario(
        self,
        battle: str,
        scenario_num: int,
        output_dir: Optional[Path] = None
    ) -> Scenario:
        """
        Generate a complete scenario

        Args:
            battle: Battle name (battleaxe, crusader, gazala, first_alamein)
            scenario_num: Scenario number (1-based)
            output_dir: Optional output directory override

        Returns:
            Complete Scenario object
        """
        print(f"\n[GENERATE] {battle.upper()} Scenario {scenario_num}")

        # Get research data
        scenarios = self.scenarios_data.get(battle, [])
        research = next((s for s in scenarios if s.scenario_number == scenario_num), None)

        if not research:
            raise ValueError(f"Scenario {scenario_num} not found for battle {battle}")

        # Extract points budget
        points_match = re.search(r'(\d+)-(\d+)', research.points)
        if points_match:
            points_min = int(points_match.group(1))
            points_max = int(points_match.group(2))
            points_budget = (points_min + points_max) // 2
        else:
            points_budget = 750  # Default

        # Determine nations and quarters from Phase 6 units
        nation_quarter = self._extract_nation_quarter(research.phase6_units)

        # Build force rosters
        attacker_side = list(research.forces.keys())[0] if research.forces else "British"
        defender_side = list(research.forces.keys())[1] if len(research.forces) > 1 else "Axis"

        # Create situation report
        situation = SituationReport(
            date=research.date,
            location=research.location,
            context=research.historical_engagement,
            strategic_situation=f"Part of {battle.replace('_', ' ').title()} operation."
        )

        # Create battlefield setup
        terrain_features = self._parse_terrain(research.terrain)
        battlefield = BattlefieldSetup(
            table_size=self._determine_table_size(points_budget),
            terrain=terrain_features,
            special_rules=research.special_rules
        )

        # Create battle description
        battle_desc = BattleDescription(
            description=research.historical_engagement,
            attacker=attacker_side,
            defender=defender_side,
            attacker_objective=research.objectives.get(attacker_side, ""),
            defender_objective=research.objectives.get(defender_side, "")
        )

        # Create objectives
        objectives = Objectives(
            type=VictoryType.MIXED,
            attacker_victory=research.objectives.get(attacker_side, ""),
            defender_victory=research.objectives.get(defender_side, ""),
            draw_conditions="Neither side achieves their objectives"
        )

        # Build force rosters (simplified for now)
        attacker_roster = ForceRoster(
            nation=attacker_side.lower(),
            name=f"{attacker_side.upper()} FORCES",
            battle_rating=points_budget // 20,
            points_budget=points_budget,
            units=[]
        )

        defender_roster = ForceRoster(
            nation=defender_side.lower(),
            name=f"{defender_side.upper()} FORCES",
            battle_rating=points_budget // 20,
            points_budget=points_budget,
            units=[]
        )

        # Create deployment
        deployment = Deployment(
            attacker_zone=f"{attacker_side} deploy within 12\" of south table edge",
            defender_zone=f"{defender_side} deploy within 12\" of north table edge",
            turn_order="Roll off for initiative",
            reinforcements=None
        )

        # Create alternative forces
        alternatives = AlternativeForces(
            description="This scenario can be adapted for other battles or periods.",
            suggestions=[
                "Use units from adjacent quarters for force variation",
                "Adjust points budget for smaller/larger engagements"
            ]
        )

        # Assemble complete scenario
        scenario = Scenario(
            number=scenario_num,
            title=research.title,
            name=research.title,
            situation_report=situation,
            battlefield=battlefield,
            battle=battle_desc,
            objectives=objectives,
            forces_attacker=attacker_roster,
            forces_defender=defender_roster,
            deployment=deployment,
            special_scenario_rules=research.special_rules,
            turn_limit=8,  # Default
            alternative_forces=alternatives
        )

        # Save to output directory
        if output_dir is None:
            output_dir = BOOKS_DIR / battle / "book" / "src" / "scenarios"

        output_file = output_dir / f"scenario_{scenario_num:02d}.md"
        scenario.to_markdown(output_file)

        print(f"[SUCCESS] Generated {output_file}")

        return scenario

    def _extract_nation_quarter(self, phase6_units: List[str]) -> Dict[str, str]:
        """Extract nation and quarter from Phase 6 unit filenames"""
        nation_quarter = {}

        for unit_file in phase6_units:
            # Parse filename: british_1941q2_7th_armoured_division_toe.json
            parts = unit_file.replace('_toe.json', '').split('_')
            if len(parts) >= 2:
                nation = parts[0]
                quarter = parts[1]
                nation_quarter[nation] = quarter

        return nation_quarter

    def _determine_table_size(self, points: int) -> str:
        """Determine table size based on points"""
        if points < 600:
            return "4' × 4'"
        elif points < 1000:
            return "6' × 4'"
        elif points < 1500:
            return "8' × 4'"
        else:
            return "8' × 6'"

    def _parse_terrain(self, terrain_desc: str) -> List[TerrainFeature]:
        """Parse terrain description into TerrainFeature objects"""
        features = []

        # Simple parsing for now - split by comma or semicolon
        parts = re.split(r'[,;]', terrain_desc)

        for part in parts:
            part = part.strip()
            if part:
                features.append(TerrainFeature(
                    type="terrain",
                    placement=part,
                    special_rules=None
                ))

        return features

    def generate_battle(self, battle: str):
        """Generate all scenarios for a battle"""
        print(f"\n{'='*80}")
        print(f"Generating all scenarios for {battle.upper()}")
        print(f"{'='*80}\n")

        scenarios = self.scenarios_data.get(battle, [])

        for research_data in scenarios:
            self.generate_scenario(battle, research_data.scenario_number)

        print(f"\n[COMPLETE] Generated {len(scenarios)} scenarios for {battle}")

    def generate_all_battles(self):
        """Generate all 45 scenarios"""
        print(f"\n{'='*80}")
        print("Generating ALL 45 scenarios across 4 battles")
        print(f"{'='*80}\n")

        for battle in ["battleaxe", "crusader", "gazala", "first_alamein"]:
            self.generate_battle(battle)

        total = sum(len(scenarios) for scenarios in self.scenarios_data.values())
        print(f"\n{'='*80}")
        print(f"[COMPLETE] Generated {total} scenarios total")
        print(f"{'='*80}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate BattleGroup historical scenarios")
    parser.add_argument("--battle", choices=["battleaxe", "crusader", "gazala", "first_alamein"],
                       help="Battle to generate scenarios for")
    parser.add_argument("--scenario", type=int, help="Specific scenario number to generate")
    parser.add_argument("--all", action="store_true", help="Generate all scenarios for specified battle")
    parser.add_argument("--all-battles", action="store_true", help="Generate all 45 scenarios")

    args = parser.parse_args()

    # Initialize workflow
    workflow = ScenarioWorkflow()
    workflow.initialize()

    # Execute based on arguments
    if args.all_battles:
        workflow.generate_all_battles()
    elif args.battle:
        if args.scenario:
            workflow.generate_scenario(args.battle, args.scenario)
        elif args.all:
            workflow.generate_battle(args.battle)
        else:
            print("Error: Specify --scenario N or --all")
            sys.exit(1)
    else:
        print("Error: Specify --battle or --all-battles")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
