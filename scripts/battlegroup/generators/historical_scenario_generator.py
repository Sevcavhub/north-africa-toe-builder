#!/usr/bin/env python3
"""
BattleGroup Scenario Generator

Generates complete playable scenarios following the BattleGroup format.
Based on the Kursk book scenario structure (2-page format).

Part of Phase 9B Step 5 (Generator Enhancement).

Author: North Africa TO&E Builder
Date: November 2, 2025
"""

import json
import sqlite3
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class ScenarioType(Enum):
    """Scenario type/template."""
    ASSAULT = "assault"
    DEFENSE = "defense"
    MEETING_ENGAGEMENT = "meeting_engagement"
    BREAKTHROUGH = "breakthrough"
    ENCIRCLEMENT = "encirclement"
    HOLD_THE_LINE = "hold_the_line"
    COUNTERATTACK = "counterattack"

class TableSize(Enum):
    """Standard table sizes."""
    SMALL = "4' × 4'"  # 500 points
    STANDARD = "6' × 4'"  # 750-1000 points
    LARGE = "8' × 4'"  # 1250-1500 points
    VERY_LARGE = "8' × 6'"  # 2000+ points

class VictoryType(Enum):
    """Victory condition types."""
    OBJECTIVE = "objective"  # Control objectives
    BREAK_THE_ENEMY = "break_the_enemy"  # Reach BR limit
    BREAKTHROUGH = "breakthrough"  # Exit units off table
    HOLD_GROUND = "hold_ground"  # Defend area
    MIXED = "mixed"  # Combination

@dataclass
class TerrainFeature:
    """A terrain feature on the battlefield."""
    type: str  # "hill", "woods", "building", "road", etc.
    placement: str  # Description of where to place it
    special_rules: Optional[str] = None

@dataclass
class SituationReport:
    """Historical context for the scenario."""
    date: str  # "June 30th-July 2nd, 1943"
    location: str  # "Komsomolets Kolkhoz, Russia"
    context: str  # Multi-paragraph historical background
    strategic_situation: str  # Current strategic situation

@dataclass
class BattlefieldSetup:
    """Table setup and terrain."""
    table_size: str  # "6' × 4'"
    terrain: List[TerrainFeature]
    special_rules: List[str]

@dataclass
class BattleDescription:
    """Tactical situation for the battle."""
    description: str  # Detailed tactical situation
    attacker: str  # "The Germans"
    defender: str  # "The Russians"
    attacker_objective: str
    defender_objective: str

@dataclass
class Objectives:
    """Victory conditions."""
    type: VictoryType
    attacker_victory: str
    defender_victory: str
    draw_conditions: Optional[str] = None

@dataclass
class ForceRoster:
    """Force roster for one side."""
    nation: str
    name: str  # "GERMAN FORCES"
    battle_rating: int
    points_budget: int
    units: List[Dict]  # List of unit dicts from force_roster_builder

@dataclass
class Deployment:
    """Deployment zones and setup."""
    attacker_zone: str  # "South table edge, 12\" deep"
    defender_zone: str  # "North table edge, 18\" deep"
    turn_order: str  # "Attacker goes first" or "Roll off"
    reinforcements: Optional[str] = None

@dataclass
class AlternativeForces:
    """Alternative force suggestions."""
    description: str
    suggestions: List[str]

@dataclass
class Scenario:
    """Complete BattleGroup scenario."""
    number: int
    title: str
    name: str
    situation_report: SituationReport
    battlefield: BattlefieldSetup
    battle: BattleDescription
    objectives: Objectives
    forces_attacker: ForceRoster
    forces_defender: ForceRoster
    deployment: Deployment
    special_scenario_rules: List[str]
    turn_limit: Optional[int]
    alternative_forces: AlternativeForces

    def to_dict(self) -> Dict:
        """Convert to dictionary with enum handling."""
        def convert_value(obj):
            if isinstance(obj, Enum):
                return obj.value
            return obj

        return asdict(self, dict_factory=lambda x: {k: convert_value(v) for k, v in x})

    def to_json(self, filepath: Path):
        """Export to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"[JSON] Scenario JSON saved to: {filepath}")

    def to_markdown(self, filepath: Path):
        """Export to Markdown (2-page format for MDBook)."""
        md = []

        # Page 1 Header
        md.append(f"# {self.number}. {self.name}\n")

        # Situation Report
        md.append("## SITUATION REPORT\n")
        md.append(f"**Date**: {self.situation_report.date}\n")
        md.append(f"**Location**: {self.situation_report.location}\n")
        md.append(f"\n{self.situation_report.context}\n")
        md.append(f"\n{self.situation_report.strategic_situation}\n")

        # The Battle
        md.append("## THE BATTLE\n")
        md.append(f"{self.battle.description}\n")
        md.append(f"\n**{self.battle.attacker} Objective**: {self.battle.attacker_objective}\n")
        md.append(f"\n**{self.battle.defender} Objective**: {self.battle.defender_objective}\n")

        # The Battlefield
        md.append("## THE BATTLEFIELD\n")
        md.append(f"**Table Size**: {self.battlefield.table_size}\n")

        if self.battlefield.terrain:
            md.append("\n**Terrain**:\n")
            for terrain in self.battlefield.terrain:
                md.append(f"- **{terrain.type}**: {terrain.placement}")
                if terrain.special_rules:
                    md.append(f" ({terrain.special_rules})")
                md.append("\n")

        if self.battlefield.special_rules:
            md.append("\n**Special Battlefield Rules**:\n")
            for rule in self.battlefield.special_rules:
                md.append(f"- {rule}\n")

        # Page break
        md.append("\n---\n\n")

        # Page 2 - Objectives
        md.append("## OBJECTIVES\n")
        md.append(f"**Victory Type**: {self.objectives.type.value}\n\n")
        md.append(f"**{self.battle.attacker} Victory**: {self.objectives.attacker_victory}\n\n")
        md.append(f"**{self.battle.defender} Victory**: {self.objectives.defender_victory}\n")

        if self.objectives.draw_conditions:
            md.append(f"\n**Draw**: {self.objectives.draw_conditions}\n")

        # Deployment
        md.append("\n## DEPLOYMENT\n")
        md.append(f"**{self.battle.attacker}**: {self.deployment.attacker_zone}\n\n")
        md.append(f"**{self.battle.defender}**: {self.deployment.defender_zone}\n\n")
        md.append(f"**Turn Order**: {self.deployment.turn_order}\n")

        if self.deployment.reinforcements:
            md.append(f"\n**Reinforcements**: {self.deployment.reinforcements}\n")

        # Special Scenario Rules
        if self.special_scenario_rules:
            md.append("\n## SPECIAL SCENARIO RULES\n")
            for rule in self.special_scenario_rules:
                md.append(f"- {rule}\n")

        # Turn Limit
        if self.turn_limit:
            md.append(f"\n**Turn Limit**: {self.turn_limit} turns\n")

        # Force Rosters
        md.append("\n## FORCES\n")
        md.append(f"\n### {self.forces_attacker.name}\n")
        md.append(f"**Nation**: {self.forces_attacker.nation.title()}\n")
        md.append(f"**Points Budget**: {self.forces_attacker.points_budget}\n")
        md.append(f"**Total Battle Rating**: {self.forces_attacker.battle_rating}\n\n")

        if self.forces_attacker.units:
            md.append("**Units**:\n")
            for unit in self.forces_attacker.units:
                # Format: "- 8x Matilda II (veteran) - 1160 pts, BR: 6 [1 squadron]"
                count = unit.get('count', 1)
                name = unit.get('name', 'Unknown')
                exp = unit.get('experience', '')
                pts = unit.get('points', 0)
                br = unit.get('br', 0)
                notes = unit.get('notes', '')

                md.append(f"- {count}x {name}")
                if exp:
                    md.append(f" ({exp})")
                if pts > 0:
                    md.append(f" - {pts} pts")
                if br > 0:
                    md.append(f", BR: {br}")
                if notes:
                    md.append(f" [{notes}]")
                md.append("\n")

        md.append(f"\n### {self.forces_defender.name}\n")
        md.append(f"**Nation**: {self.forces_defender.nation.title()}\n")
        md.append(f"**Points Budget**: {self.forces_defender.points_budget}\n")
        md.append(f"**Total Battle Rating**: {self.forces_defender.battle_rating}\n\n")

        if self.forces_defender.units:
            md.append("**Units**:\n")
            for unit in self.forces_defender.units:
                # Format: "- 4x 88mm FlaK 18/36 (veteran) - 380 pts, BR: 2 [hull-down]"
                count = unit.get('count', 1)
                name = unit.get('name', 'Unknown')
                exp = unit.get('experience', '')
                pts = unit.get('points', 0)
                br = unit.get('br', 0)
                notes = unit.get('notes', '')

                md.append(f"- {count}x {name}")
                if exp:
                    md.append(f" ({exp})")
                if pts > 0:
                    md.append(f" - {pts} pts")
                if br > 0:
                    md.append(f", BR: {br}")
                if notes:
                    md.append(f" [{notes}]")
                md.append("\n")

        # Alternative Forces
        md.append("\n## ALTERNATIVE FORCES\n")
        md.append(f"{self.alternative_forces.description}\n\n")
        if self.alternative_forces.suggestions:
            for suggestion in self.alternative_forces.suggestions:
                md.append(f"- {suggestion}\n")

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(md))

        print(f"[MARKDOWN] Scenario Markdown saved to: {filepath}")

    def to_text(self) -> str:
        """Export to formatted text (for printing/display)."""
        lines = []

        # Title
        lines.append("=" * 80)
        lines.append(f"{self.number}. {self.name}".center(80))
        lines.append("=" * 80)
        lines.append("")

        # Situation Report
        lines.append("SITUATION REPORT")
        lines.append("-" * 80)
        lines.append(f"Date: {self.situation_report.date}")
        lines.append(f"Location: {self.situation_report.location}")
        lines.append("")
        lines.append(self.situation_report.context)
        lines.append("")
        lines.append(self.situation_report.strategic_situation)
        lines.append("")

        # The Battle
        lines.append("THE BATTLE")
        lines.append("-" * 80)
        lines.append(self.battle.description)
        lines.append("")
        lines.append(f"{self.battle.attacker} Objective: {self.battle.attacker_objective}")
        lines.append(f"{self.battle.defender} Objective: {self.battle.defender_objective}")
        lines.append("")

        # The Battlefield
        lines.append("THE BATTLEFIELD")
        lines.append("-" * 80)
        lines.append(f"Table Size: {self.battlefield.table_size}")
        lines.append("")

        if self.battlefield.terrain:
            lines.append("Terrain:")
            for terrain in self.battlefield.terrain:
                rule_text = f" ({terrain.special_rules})" if terrain.special_rules else ""
                lines.append(f"  - {terrain.type}: {terrain.placement}{rule_text}")
            lines.append("")

        if self.battlefield.special_rules:
            lines.append("Special Battlefield Rules:")
            for rule in self.battlefield.special_rules:
                lines.append(f"  - {rule}")
            lines.append("")

        # Page 2
        lines.append("=" * 80)
        lines.append("PAGE 2")
        lines.append("=" * 80)
        lines.append("")

        # Objectives
        lines.append("OBJECTIVES")
        lines.append("-" * 80)
        lines.append(f"Victory Type: {self.objectives.type.value}")
        lines.append("")
        lines.append(f"{self.battle.attacker} Victory: {self.objectives.attacker_victory}")
        lines.append(f"{self.battle.defender} Victory: {self.objectives.defender_victory}")
        if self.objectives.draw_conditions:
            lines.append(f"Draw: {self.objectives.draw_conditions}")
        lines.append("")

        # Deployment
        lines.append("DEPLOYMENT")
        lines.append("-" * 80)
        lines.append(f"{self.battle.attacker}: {self.deployment.attacker_zone}")
        lines.append(f"{self.battle.defender}: {self.deployment.defender_zone}")
        lines.append(f"Turn Order: {self.deployment.turn_order}")
        if self.deployment.reinforcements:
            lines.append(f"Reinforcements: {self.deployment.reinforcements}")
        lines.append("")

        # Special Rules
        if self.special_scenario_rules:
            lines.append("SPECIAL SCENARIO RULES")
            lines.append("-" * 80)
            for rule in self.special_scenario_rules:
                lines.append(f"  - {rule}")
            lines.append("")

        # Turn Limit
        if self.turn_limit:
            lines.append(f"TURN LIMIT: {self.turn_limit} turns")
            lines.append("")

        # Forces
        lines.append("FORCES")
        lines.append("=" * 80)

        # Attacker
        lines.append(f"\n{self.forces_attacker.name}")
        lines.append("-" * 40)
        lines.append(f"Nation: {self.forces_attacker.nation.title()}")
        lines.append(f"Points Budget: {self.forces_attacker.points_budget}")
        lines.append(f"Total Battle Rating: {self.forces_attacker.battle_rating}")
        lines.append("")

        if self.forces_attacker.units:
            lines.append("Units:")
            for unit in self.forces_attacker.units:
                name = unit.get('name', 'Unknown')
                exp = unit.get('experience', '')
                pts = unit.get('points', 0)
                br = unit.get('br', 0)
                lines.append(f"  - {name} ({exp}) - {pts} pts, BR: {br}")
        lines.append("")

        # Defender
        lines.append(f"{self.forces_defender.name}")
        lines.append("-" * 40)
        lines.append(f"Nation: {self.forces_defender.nation.title()}")
        lines.append(f"Points Budget: {self.forces_defender.points_budget}")
        lines.append(f"Total Battle Rating: {self.forces_defender.battle_rating}")
        lines.append("")

        if self.forces_defender.units:
            lines.append("Units:")
            for unit in self.forces_defender.units:
                name = unit.get('name', 'Unknown')
                exp = unit.get('experience', '')
                pts = unit.get('points', 0)
                br = unit.get('br', 0)
                lines.append(f"  - {name} ({exp}) - {pts} pts, BR: {br}")
        lines.append("")

        # Alternative Forces
        lines.append("ALTERNATIVE FORCES")
        lines.append("-" * 80)
        lines.append(self.alternative_forces.description)
        if self.alternative_forces.suggestions:
            lines.append("")
            for suggestion in self.alternative_forces.suggestions:
                lines.append(f"  - {suggestion}")
        lines.append("")

        return '\n'.join(lines)


class ScenarioGenerator:
    """Generates complete BattleGroup scenarios."""

    def __init__(self, db_path: str = "database/master_database.db"):
        """Initialize generator with database connection."""
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

    def create_scenario(
        self,
        number: int,
        name: str,
        scenario_type: ScenarioType,
        date: str,
        location: str,
        context: str,
        strategic_situation: str,
        attacker_nation: str,
        defender_nation: str,
        attacker_points: int,
        defender_points: int,
        table_size: TableSize = TableSize.STANDARD,
        turn_limit: Optional[int] = None
    ) -> Scenario:
        """
        Create a scenario from parameters.

        This is the main entry point - you provide the historical details,
        and it generates the complete scenario structure.
        """
        # Create situation report
        situation = SituationReport(
            date=date,
            location=location,
            context=context,
            strategic_situation=strategic_situation
        )

        # Generate terrain based on scenario type
        terrain, battlefield_rules = self._generate_terrain(scenario_type, table_size)

        battlefield = BattlefieldSetup(
            table_size=table_size.value,
            terrain=terrain,
            special_rules=battlefield_rules
        )

        # Generate battle description and objectives
        battle_desc = self._generate_battle_description(
            scenario_type, attacker_nation, defender_nation
        )

        objectives = self._generate_objectives(scenario_type)

        # Generate deployment
        deployment = self._generate_deployment(scenario_type, table_size)

        # Create placeholder force rosters
        # (In real usage, these would be loaded from force_roster_builder)
        forces_attacker = ForceRoster(
            nation=attacker_nation,
            name=f"{attacker_nation.upper()} FORCES",
            battle_rating=0,  # Calculate from units
            points_budget=attacker_points,
            units=[]  # Would be populated from roster builder
        )

        forces_defender = ForceRoster(
            nation=defender_nation,
            name=f"{defender_nation.upper()} FORCES",
            battle_rating=0,
            points_budget=defender_points,
            units=[]
        )

        # Generate special scenario rules
        special_rules = self._generate_special_scenario_rules(scenario_type)

        # Generate alternative forces suggestions
        alt_forces = self._generate_alternative_forces(
            attacker_nation, defender_nation, date
        )

        # Create complete scenario
        scenario = Scenario(
            number=number,
            title=f"{number}. {name}",
            name=name,
            situation_report=situation,
            battlefield=battlefield,
            battle=battle_desc,
            objectives=objectives,
            forces_attacker=forces_attacker,
            forces_defender=forces_defender,
            deployment=deployment,
            special_scenario_rules=special_rules,
            turn_limit=turn_limit,
            alternative_forces=alt_forces
        )

        return scenario

    def _generate_terrain(
        self, scenario_type: ScenarioType, table_size: TableSize
    ) -> Tuple[List[TerrainFeature], List[str]]:
        """Generate terrain features based on scenario type."""
        terrain = []
        rules = []

        if scenario_type == ScenarioType.ASSAULT:
            terrain = [
                TerrainFeature(
                    "Objective Building",
                    "Center of table",
                    "Hard cover, counts as objective"
                ),
                TerrainFeature(
                    "Woods",
                    "Two woods on flanks, 8\" diameter",
                    "Soft cover, difficult terrain"
                ),
                TerrainFeature(
                    "Hill",
                    "Defender's table edge, 12\" from edge",
                    "Elevated position, good fields of fire"
                ),
            ]
            rules = [
                "Defender may place up to 3 additional terrain pieces (trenches, obstacles, etc.)",
                "Buildings provide hard cover",
            ]

        elif scenario_type == ScenarioType.MEETING_ENGAGEMENT:
            terrain = [
                TerrainFeature(
                    "Crossroads",
                    "Center of table",
                    "Counts as objective"
                ),
                TerrainFeature(
                    "Woods",
                    "Scatter 3-4 woods randomly",
                    "Soft cover"
                ),
                TerrainFeature(
                    "Road",
                    "Bisects table from edge to edge",
                    "Fast movement for vehicles"
                ),
            ]
            rules = [
                "Both sides set up terrain alternately",
                "No terrain within 6\" of table center",
            ]

        elif scenario_type == ScenarioType.DEFENSE:
            terrain = [
                TerrainFeature(
                    "Defensive Line",
                    "Across defender's deployment zone",
                    "Trenches, barbed wire, obstacles"
                ),
                TerrainFeature(
                    "Buildings",
                    "2-3 buildings in defensive zone",
                    "Hard cover, fortified"
                ),
                TerrainFeature(
                    "Approach Terrain",
                    "Attacker's side - open with some cover",
                    "Scattered woods, shell craters"
                ),
            ]
            rules = [
                "Defender deploys first, may fortify positions",
                "Attacker has initiative on turn 1",
            ]

        else:  # Default/breakthrough
            terrain = [
                TerrainFeature(
                    "Mixed Terrain",
                    "Scatter terrain across table",
                    "Mix of woods, buildings, hills"
                ),
            ]
            rules = ["Players agree on terrain placement"]

        return terrain, rules

    def _generate_battle_description(
        self, scenario_type: ScenarioType, attacker: str, defender: str
    ) -> BattleDescription:
        """Generate battle description based on scenario type."""
        attacker_title = f"The {attacker.title()}s"
        defender_title = f"The {defender.title()}s"

        if scenario_type == ScenarioType.ASSAULT:
            description = (
                f"{attacker_title} are launching an assault to capture key objectives. "
                f"{defender_title} must hold their positions and repel the attack."
            )
            attacker_obj = "Capture the primary objective and break the enemy's will to fight"
            defender_obj = "Hold the objective and inflict sufficient casualties to stop the assault"

        elif scenario_type == ScenarioType.MEETING_ENGAGEMENT:
            description = (
                f"Both forces are converging on the same objective. "
                f"Neither side has had time to prepare positions."
            )
            attacker_obj = "Seize the objective before the enemy"
            defender_obj = "Seize the objective before the enemy"

        elif scenario_type == ScenarioType.DEFENSE:
            description = (
                f"{defender_title} have prepared defensive positions. "
                f"{attacker_title} must break through the defenses."
            )
            attacker_obj = "Break through the defensive line"
            defender_obj = "Hold the defensive line and repel the attack"

        else:  # BREAKTHROUGH
            description = (
                f"{attacker_title} must breakthrough the enemy lines. "
                f"{defender_title} must prevent the breakthrough."
            )
            attacker_obj = "Exit at least 50% of forces off the opposite table edge"
            defender_obj = "Prevent the enemy breakthrough"

        return BattleDescription(
            description=description,
            attacker=attacker_title,
            defender=defender_title,
            attacker_objective=attacker_obj,
            defender_objective=defender_obj
        )

    def _generate_objectives(self, scenario_type: ScenarioType) -> Objectives:
        """Generate victory conditions based on scenario type."""
        if scenario_type == ScenarioType.ASSAULT:
            return Objectives(
                type=VictoryType.MIXED,
                attacker_victory=(
                    "Control the primary objective at game end AND "
                    "have not reached your Battle Rating limit"
                ),
                defender_victory=(
                    "Control the primary objective at game end OR "
                    "force the attacker to reach their Battle Rating limit"
                ),
                draw_conditions="Any other result"
            )

        elif scenario_type == ScenarioType.MEETING_ENGAGEMENT:
            return Objectives(
                type=VictoryType.OBJECTIVE,
                attacker_victory="Control the objective at game end",
                defender_victory="Control the objective at game end",
                draw_conditions="No one controls the objective (contested)"
            )

        elif scenario_type == ScenarioType.DEFENSE:
            return Objectives(
                type=VictoryType.HOLD_GROUND,
                attacker_victory=(
                    "Break through the defensive line (control 2+ objectives in defender's zone)"
                ),
                defender_victory=(
                    "Hold the defensive line AND force attacker to reach BR limit"
                ),
                draw_conditions="Attacker breaks through but reaches BR limit"
            )

        else:  # BREAKTHROUGH
            return Objectives(
                type=VictoryType.BREAKTHROUGH,
                attacker_victory="Exit 50%+ of starting force off opposite edge",
                defender_victory="Prevent the breakthrough AND inflict heavy casualties",
                draw_conditions="Attacker exits 25-49% of force"
            )

    def _generate_deployment(
        self, scenario_type: ScenarioType, table_size: TableSize
    ) -> Deployment:
        """Generate deployment zones based on scenario type."""
        if scenario_type == ScenarioType.ASSAULT:
            return Deployment(
                attacker_zone="Attacker's table edge, up to 12\" onto table",
                defender_zone="Defender's table edge, up to 18\" onto table (prepared positions)",
                turn_order="Attacker has initiative and goes first"
            )

        elif scenario_type == ScenarioType.MEETING_ENGAGEMENT:
            return Deployment(
                attacker_zone="South table edge, up to 12\" onto table",
                defender_zone="North table edge, up to 12\" onto table",
                turn_order="Roll off for initiative each turn"
            )

        elif scenario_type == ScenarioType.DEFENSE:
            return Deployment(
                attacker_zone="Attacker's table edge, up to 6\" onto table",
                defender_zone="Defender's table edge, up to 24\" onto table (fortified)",
                turn_order="Attacker goes first",
                reinforcements="Defender may receive reinforcements on turns 3+"
            )

        else:  # BREAKTHROUGH
            return Deployment(
                attacker_zone="Attacker's short edge, up to 12\" onto table",
                defender_zone="Center of table, blocking positions",
                turn_order="Attacker goes first"
            )

    def _generate_special_scenario_rules(self, scenario_type: ScenarioType) -> List[str]:
        """Generate special rules based on scenario type."""
        rules = []

        if scenario_type == ScenarioType.ASSAULT:
            rules = [
                "Prepared Positions: Defender's units in cover at start gain +1 to pinning tests",
                "Assault Doctrine: Attacker's units within 12\" of objective gain +1 to assault moves",
            ]

        elif scenario_type == ScenarioType.DEFENSE:
            rules = [
                "Fortified Positions: Defender may place fortifications (trenches, wire, mines)",
                "Artillery Support: Defender receives bonus artillery mission on turn 1",
            ]

        elif scenario_type == ScenarioType.BREAKTHROUGH:
            rules = [
                "Breakthrough Attempt: Attacker must exit 50%+ of force",
                "Reinforcements: Defender receives reinforcements on turn 3+ (roll)",
            ]

        return rules

    def _generate_alternative_forces(
        self, attacker: str, defender: str, date: str
    ) -> AlternativeForces:
        """Generate alternative force suggestions."""
        description = (
            "This scenario uses historical forces for the battle, "
            "but players can choose alternative forces from their own model "
            "collections. To fit this scenario choose any battlegroup from the "
            f"{attacker.title()} and {defender.title()} army lists."
        )

        suggestions = [
            f"Use forces from the same time period ({date})",
            "Adjust points budgets proportionally for different scales",
            "Swap nations but keep force structure similar",
        ]

        return AlternativeForces(
            description=description,
            suggestions=suggestions
        )


def main():
    """CLI interface for scenario generator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="BattleGroup Scenario Generator (Phase 9B Step 5 Part 4)"
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Generate a demo scenario (Operation Battleaxe assault)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output/scenarios',
        help='Output directory for scenarios'
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = ScenarioGenerator()

    if args.demo:
        # Generate demo scenario
        print("[DEMO] Generating demo scenario: Operation Battleaxe Assault\n")

        scenario = generator.create_scenario(
            number=1,
            name="HALFAYA PASS ASSAULT",
            scenario_type=ScenarioType.ASSAULT,
            date="June 15-17, 1941",
            location="Halfaya Pass, Libya-Egypt Border",
            context=(
                "Operation Battleaxe was a British offensive to relieve Tobruk and "
                "push back Rommel's forces. The attack on Halfaya Pass was crucial "
                "to opening the coastal route. German forces had fortified the pass "
                "with 88mm guns and created strong defensive positions."
            ),
            strategic_situation=(
                "The British need to break through the Axis defenses at Halfaya Pass "
                "to advance along the coast road toward Tobruk. German forces under "
                "Generalmajor Bach have created a formidable defensive position with "
                "interlocking fields of fire."
            ),
            attacker_nation="british",
            defender_nation="german",
            attacker_points=750,
            defender_points=600,  # Defender gets fewer points but prepared positions
            table_size=TableSize.STANDARD,
            turn_limit=8
        )

        # Export in all formats
        scenario.to_json(output_dir / "battleaxe_assault.json")
        scenario.to_markdown(output_dir / "battleaxe_assault.md")

        # Print to console
        print(scenario.to_text())

        print(f"\n[SUCCESS] Demo scenario generated in {output_dir}/")

    else:
        print("Use --demo to generate a demonstration scenario")
        print("Or import ScenarioGenerator class for programmatic use")


if __name__ == '__main__':
    main()
