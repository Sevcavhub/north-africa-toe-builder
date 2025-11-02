#!/usr/bin/env python3
"""
BattleGroup Random Scenario Generator (North Africa)

Generates random scenarios for quick play using D6×D6 terrain table
and scenario templates adapted for North Africa theater.

Based on BattleGroup Kursk/Torch scenario generation system.

Part of Phase 9B Step 5 Part 4A (Random Scenario Generator).

Author: North Africa TO&E Builder
Date: November 2, 2025
"""

import json
import random
import sqlite3
import sys
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class ScenarioType(Enum):
    """Scenario type classification."""
    MEETING_ENGAGEMENT = "Meeting Engagement"
    ATTACK_DEFENCE = "Attack/Defence"


class BattleSize(Enum):
    """Battle size determines reinforcement dice."""
    SQUAD_PLATOON = "Squad/Platoon"
    COMPANY = "Company"
    BATTALION = "Battalion"


class TableSize(Enum):
    """Standard table sizes."""
    SMALL = "4' × 4'"
    STANDARD = "6' × 4'"
    LARGE = "8' × 4'"
    VERY_LARGE = "8' × 6'"


@dataclass
class TerrainFeature:
    """A terrain feature from the terrain table."""
    name: str
    size: str
    description: str
    special_rules: str
    cover_type: Optional[str] = None  # "soft", "hard", "none"
    movement_penalty: Optional[str] = None  # "difficult", "dangerous", "impassable"


@dataclass
class WeatherCondition:
    """Weather conditions for the battle."""
    condition: str  # "clear" or "sandstorm"
    turn_starts: Optional[int] = None  # For Desert Dust Cloud
    effects: List[str] = field(default_factory=list)


@dataclass
class DeploymentZone:
    """Deployment zone description."""
    side: str  # "Attacker", "Defender", "Player 1", "Player 2"
    location: str  # "North table edge, 12\" deep"
    special_rules: List[str] = field(default_factory=list)


@dataclass
class ObjectivePlacement:
    """Objective placement rules."""
    count: int  # Usually D3+2
    first_objective: str  # Special placement for first objective
    spacing_rules: str  # "10\" from edges and other objectives"
    placed_by: str  # "Alternating" or "Defender first" etc.


@dataclass
class ReinforcementSchedule:
    """Reinforcement arrival schedule."""
    side: str
    starting_turn: int
    dice_per_turn: str  # "D6", "2D6", "3D6"
    special_rules: List[str] = field(default_factory=list)


@dataclass
class RandomScenario:
    """Complete random scenario."""
    number: int
    name: str
    scenario_type: ScenarioType
    battle_size: BattleSize
    table_size: TableSize

    # Situation
    situation_report: str
    tactical_context: str

    # Terrain
    terrain_features: List[TerrainFeature]
    terrain_notes: str

    # Weather
    weather: WeatherCondition

    # Victory
    victory_conditions: str

    # Deployment (step-by-step)
    deployment_steps: List[str]
    deployment_zones: List[DeploymentZone]

    # Objectives
    objectives: ObjectivePlacement

    # Forces
    attacker_points: int
    defender_points: int

    # Reinforcements
    reinforcements: List[ReinforcementSchedule]

    # Special rules
    special_rules: List[str]

    # ASCII map
    deployment_map: str

    # Metadata
    year: str  # "1942" or "1943"
    location_type: str  # "Desert" or "Tunisia"
    recommended_nations: List[str]


# ============================================================================
# NORTH AFRICA TERRAIN TABLE (D6×D6)
# ============================================================================

# Based on BattleGroup Torch book terrain generator
NORTH_AFRICA_TERRAIN_TABLE = {
    # Row 1: Hills and Elevation
    (1, 1): TerrainFeature(
        "Small Hill",
        "Up to 10\" square",
        "A low hill or rise in the desert. Provides elevated firing positions.",
        "Units on hill gain +1 to observation rolls. Vehicles treat as difficult terrain.",
        cover_type="none",
        movement_penalty="difficult"
    ),
    (1, 2): TerrainFeature(
        "Rocky Hill",
        "Up to 15\" square",
        "A hill with rocky outcrops and loose stones. Difficult to climb but excellent cover.",
        "Infantry gain soft cover. Vehicles treat as difficult terrain. May include rock outcrops.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (1, 3): TerrainFeature(
        "Sand Dune",
        "Up to 20\" square",
        "Large sand dune typical of desert erg (sand sea). Soft sand makes movement difficult.",
        "All units treat as difficult terrain. Provides soft cover for infantry.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (1, 4): TerrainFeature(
        "Jebel (Mountain)",
        "Up to 25\" square",
        "Rocky mountain or large hill feature. Dominates the battlefield.",
        "Steep slopes count as dangerous terrain. Top provides excellent observation (+2 to rolls).",
        cover_type="hard",
        movement_penalty="dangerous"
    ),
    (1, 5): TerrainFeature(
        "Ridge",
        "20\" long, 6\" wide",
        "Long ridge feature creating forward and reverse slopes.",
        "Units on reverse slope cannot be seen from forward slope. Ridge crest provides hull-down positions.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (1, 6): TerrainFeature(
        "Escarpment",
        "Table edge to 12\" deep",
        "Steep cliff face or escarpment. Major tactical feature.",
        "Impassable to vehicles. Infantry can climb (dangerous terrain). Artillery observers gain +1.",
        cover_type="hard",
        movement_penalty="impassable"
    ),

    # Row 2: Open Desert Features
    (2, 1): TerrainFeature(
        "Open Desert",
        "24\" × 24\" area",
        "Flat, open desert with excellent visibility. No cover.",
        "No special rules. Fast movement for all units.",
        cover_type="none",
        movement_penalty="none"
    ),
    (2, 2): TerrainFeature(
        "Rocky Desert",
        "20\" × 20\" area",
        "Desert floor scattered with rocks and stones.",
        "Vehicles treat as difficult terrain. Infantry move normally.",
        cover_type="none",
        movement_penalty="difficult"
    ),
    (2, 3): TerrainFeature(
        "Sand Sea (Erg)",
        "20\" × 20\" area",
        "Area of soft sand dunes and sandy desert.",
        "All units treat as difficult terrain. Vehicles risk bogging down (1 on movement die = immobilized).",
        cover_type="none",
        movement_penalty="difficult"
    ),
    (2, 4): TerrainFeature(
        "Salt Flat (Sabkha)",
        "15\" × 15\" area",
        "Dried salt lake bed. Treacherous for vehicles.",
        "Looks flat but is dangerous terrain for vehicles (risk of breakthrough). Infantry move normally.",
        cover_type="none",
        movement_penalty="dangerous"
    ),
    (2, 5): TerrainFeature(
        "Wadi (Dry)",
        "20\" long, 6\" wide",
        "Dry riverbed cutting through desert. Excellent cover and concealment.",
        "Infantry and vehicles in wadi gain hard cover. Counts as difficult terrain to enter/exit.",
        cover_type="hard",
        movement_penalty="difficult"
    ),
    (2, 6): TerrainFeature(
        "Depression",
        "15\" × 15\" area",
        "Natural depression in desert floor. Good concealment.",
        "Units in depression gain soft cover from direct fire. Difficult terrain for vehicles.",
        cover_type="soft",
        movement_penalty="difficult"
    ),

    # Row 3: Vegetation
    (3, 1): TerrainFeature(
        "Oasis",
        "10\" × 10\" area",
        "Small oasis with palm trees and water. Strategic objective.",
        "Counts as wood for cover (soft). Usually marks an objective. May include a well.",
        cover_type="soft",
        movement_penalty="none"
    ),
    (3, 2): TerrainFeature(
        "Palm Grove",
        "15\" × 15\" area",
        "Plantation of date palms. Common in cultivated areas.",
        "Infantry gain soft cover. Blocks line of sight beyond 5\". Difficult terrain for vehicles.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (3, 3): TerrainFeature(
        "Scrubland",
        "20\" × 20\" area",
        "Low scrub bushes and thistles. Sparse concealment.",
        "Infantry gain soft cover if stationary. Vehicles unaffected.",
        cover_type="soft",
        movement_penalty="none"
    ),
    (3, 4): TerrainFeature(
        "Wadi (Vegetated)",
        "20\" long, 8\" wide",
        "Seasonal watercourse with dense brush and trees.",
        "Infantry gain hard cover. Blocks LOS beyond 5\". Difficult terrain for all.",
        cover_type="hard",
        movement_penalty="difficult"
    ),
    (3, 5): TerrainFeature(
        "Heavy Scrub",
        "20\" square",
        "Dense scrub with thistles and tall grass.",
        "Infantry gain soft cover. Not cover for vehicles. Difficult terrain.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (3, 6): TerrainFeature(
        "Ancient Ruins",
        "12\" × 12\" area",
        "Crumbling Roman or Punic ruins. Archaeological site.",
        "Infantry gain hard cover. Impassable to vehicles. Excellent defensive position.",
        cover_type="hard",
        movement_penalty="impassable"
    ),

    # Row 4: Buildings and Settlements
    (4, 1): TerrainFeature(
        "Stone Building",
        "Single building",
        "Small stone structure, typical Arab architecture.",
        "Infantry gain hard cover. Impassable to vehicles unless destroyed.",
        cover_type="hard",
        movement_penalty="impassable"
    ),
    (4, 2): TerrainFeature(
        "Mud-Brick Village",
        "4-6 buildings, 20\" area",
        "Small North African village with adobe houses.",
        "Buildings provide hard cover. Narrow streets are difficult terrain for vehicles.",
        cover_type="hard",
        movement_penalty="difficult"
    ),
    (4, 3): TerrainFeature(
        "Fortified Position",
        "12\" × 12\" area",
        "Prepared defensive position with trenches and dugouts.",
        "Infantry gain hard cover with +1 to cover saves. Difficult terrain for vehicles.",
        cover_type="hard",
        movement_penalty="difficult"
    ),
    (4, 4): TerrainFeature(
        "Ancient Ruins (Large)",
        "20\" × 20\" area",
        "Extensive Roman/Carthaginian ruins. Forum, amphitheater, etc.",
        "Complex terrain. Infantry gain hard cover. Impassable to vehicles. May have open central area.",
        cover_type="hard",
        movement_penalty="impassable"
    ),
    (4, 5): TerrainFeature(
        "Farm Complex",
        "2-3 buildings with walls",
        "North African farm with adobe buildings and stone walls.",
        "Buildings provide hard cover. Walled fields provide soft cover. Difficult terrain.",
        cover_type="hard",
        movement_penalty="difficult"
    ),
    (4, 6): TerrainFeature(
        "Well/Cistern",
        "Single 3\" feature",
        "Stone well or water cistern. Vital water source.",
        "Counts as objective marker. No cover. May have low wall (soft cover within 2\").",
        cover_type="none",
        movement_penalty="none"
    ),

    # Row 5: Infrastructure
    (5, 1): TerrainFeature(
        "Track (Dirt)",
        "4\" wide, table length",
        "Unpaved desert track or caravan route.",
        "Vehicles on track ignore difficult terrain penalties. May become muddy (Tunisia).",
        cover_type="none",
        movement_penalty="none"
    ),
    (5, 2): TerrainFeature(
        "Paved Road",
        "6\" wide, table length",
        "Metalled road, often Italian-built.",
        "Fast movement for vehicles. Key strategic route. Often an objective.",
        cover_type="none",
        movement_penalty="none"
    ),
    (5, 3): TerrainFeature(
        "Railway Line",
        "Table length on embankment",
        "Single-track railway with embankment.",
        "Embankment provides soft cover. Crossing is difficult terrain. May have telegraph poles.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (5, 4): TerrainFeature(
        "Airfield",
        "30\" × 20\" area",
        "Desert airstrip with runway and dispersals.",
        "Open ground. May have buildings (hangars), fuel dumps, wrecked aircraft.",
        cover_type="none",
        movement_penalty="none"
    ),
    (5, 5): TerrainFeature(
        "Supply Dump",
        "10\" × 10\" area",
        "Fuel drums, ammunition boxes, supply crates.",
        "Soft cover for infantry. Explodes if hit by HE (6+ causes pinning within 10\").",
        cover_type="soft",
        movement_penalty="none"
    ),
    (5, 6): TerrainFeature(
        "Wrecked Vehicles",
        "Scatter 2D3 wrecks",
        "Destroyed tanks, trucks, and armored vehicles.",
        "Each wreck provides hard cover. Impassable to vehicles.",
        cover_type="hard",
        movement_penalty="impassable"
    ),

    # Row 6: Tunisia-Specific (also works for coastal areas)
    (6, 1): TerrainFeature(
        "Copse/Orchard",
        "10\" square",
        "Small stand of cork oaks, olives, or fruit trees.",
        "Infantry gain soft cover. Blocks LOS beyond 5\". Difficult terrain for vehicles.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (6, 2): TerrainFeature(
        "Woods",
        "20\" square",
        "Larger wooded area of Mediterranean trees.",
        "Infantry gain soft cover. Blocks LOS beyond 5\". Difficult terrain for vehicles.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (6, 3): TerrainFeature(
        "Crop Field",
        "20\" square with walls",
        "Wheat field, vineyard, or olive grove with stone walls.",
        "Infantry in field gain soft cover. Walls provide hard cover. Difficult terrain.",
        cover_type="soft",
        movement_penalty="difficult"
    ),
    (6, 4): TerrainFeature(
        "Cactus Patch",
        "20\" square",
        "Area of tall prickly pear cactus. North African hedgerows.",
        "Dangerous terrain for infantry. Impassable to vehicles. Good concealment.",
        cover_type="soft",
        movement_penalty="dangerous"
    ),
    (6, 5): TerrainFeature(
        "Rock Outcrop",
        "10\" square",
        "Large boulders and rock formations.",
        "Impassable to vehicles. Hard cover for infantry and guns. Excellent position.",
        cover_type="hard",
        movement_penalty="impassable"
    ),
    (6, 6): TerrainFeature(
        "Stream/Irrigation Ditch",
        "Table length, 3\" wide",
        "Fordable stream or irrigation canal.",
        "Difficult terrain for vehicles. May have vegetation along banks (soft cover).",
        cover_type="none",
        movement_penalty="difficult"
    ),
}


def roll_terrain(num_pieces: int = 3) -> List[TerrainFeature]:
    """
    Roll on the North Africa terrain table.

    Args:
        num_pieces: Number of terrain pieces to generate (default D3+1 = 3 average)

    Returns:
        List of terrain features
    """
    terrain = []
    for _ in range(num_pieces):
        d6_1 = random.randint(1, 6)
        d6_2 = random.randint(1, 6)
        terrain.append(NORTH_AFRICA_TERRAIN_TABLE[(d6_1, d6_2)])
    return terrain


# ============================================================================
# WEATHER SYSTEM
# ============================================================================

def roll_weather_1942() -> WeatherCondition:
    """
    Roll for weather in 1942 desert battles.
    Includes Desert Dust Cloud system.
    """
    # Roll for sandstorm (1 in 6)
    if random.randint(1, 6) == 1:
        return WeatherCondition(
            condition="sandstorm",
            effects=[
                "All aircraft grounded (Air Attack counters automatically fail)",
                "Visibility reduced to 20\"",
                "All observation tests at -1",
                "Movement penalties for all units"
            ]
        )

    # Roll for Desert Dust Cloud (how many turns until dust affects spotting)
    dust_turn = random.randint(2, 12)  # 2D6
    return WeatherCondition(
        condition="clear",
        turn_starts=dust_turn,
        effects=[
            f"Desert Dust Cloud begins on turn {dust_turn}",
            f"From turn {dust_turn}: -1 to observation tests",
            f"From turn {dust_turn}: Maximum weapon range 40\"",
            f"From turn {dust_turn}: Maximum artillery spotter range 40\""
        ]
    )


def roll_weather_1943() -> WeatherCondition:
    """
    Roll for weather in 1943 Tunisia battles.
    No Desert Dust Cloud (replaced by mud and rain).
    """
    # Roll for bad weather (1 in 6)
    if random.randint(1, 6) == 1:
        return WeatherCondition(
            condition="rain",
            effects=[
                "All aircraft grounded (Air Attack counters automatically fail)",
                "All off-road terrain counts as difficult",
                "Tracks become muddy (difficult terrain)",
                "Visibility normal (rain, not dust)"
            ]
        )

    return WeatherCondition(
        condition="clear",
        effects=["Clear weather. No special effects."]
    )


# ============================================================================
# SCENARIO TEMPLATES
# ============================================================================

class RandomScenarioGenerator:
    """Generates random scenarios for North Africa battles."""

    def __init__(self, db_path: str = "database/master_database.db"):
        """Initialize with optional database connection."""
        self.db_path = Path(db_path)
        if self.db_path.exists():
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
        else:
            self.conn = None

    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def generate_scenario(
        self,
        scenario_name: str,
        battle_size: BattleSize = BattleSize.COMPANY,
        table_size: TableSize = TableSize.STANDARD,
        year: str = "1942",
        attacker_points: int = 750,
        defender_points: int = 750
    ) -> RandomScenario:
        """
        Generate a random scenario by name.

        Available scenarios:
        - "desert_patrol_clash"
        - "oasis_counter_attack"
        - "desert_flanking"
        - "wadi_crossing"
        - "escarpment_defense"
        - "pass_assault"
        - "convoy_ambush"
        - "airfield_assault"
        - "fortified_box"
        - "coastal_road"
        - "desert_breakthrough"
        - "rearguard"
        """
        # Map scenario names to generator methods
        generators = {
            "desert_patrol_clash": self._generate_desert_patrol_clash,
            "oasis_counter_attack": self._generate_oasis_counter_attack,
            "desert_flanking": self._generate_desert_flanking,
            "wadi_crossing": self._generate_wadi_crossing,
            "escarpment_defense": self._generate_escarpment_defense,
            "pass_assault": self._generate_pass_assault,
            "convoy_ambush": self._generate_convoy_ambush,
            "airfield_assault": self._generate_airfield_assault,
            "fortified_box": self._generate_fortified_box,
            "coastal_road": self._generate_coastal_road,
            "desert_breakthrough": self._generate_desert_breakthrough,
            "rearguard": self._generate_rearguard,
        }

        if scenario_name not in generators:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        return generators[scenario_name](
            battle_size=battle_size,
            table_size=table_size,
            year=year,
            attacker_points=attacker_points,
            defender_points=defender_points
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _calculate_scout_modifier(self, scout_count: int) -> str:
        """Calculate initiative modifier from scout units."""
        if scout_count == 0:
            return "No scout bonus"
        return f"+{scout_count} to initiative rolls"

    def _determine_deployment_priority(self, attacker_scouts: int, defender_scouts: int) -> str:
        """Determine who deploys first based on scout count."""
        if attacker_scouts > defender_scouts:
            return "Attacker deploys first (more scouts)"
        elif defender_scouts > attacker_scouts:
            return "Defender deploys first (more scouts)"
        else:
            return "Roll off for deployment priority"

    def _calculate_ambush_units(self, scout_count: int) -> str:
        """Calculate how many units can ambush fire."""
        if scout_count >= 5:
            return "D6 units may ambush fire"
        elif scout_count >= 3:
            return "D3 units may ambush fire"
        elif scout_count >= 1:
            return "1 unit may ambush fire"
        else:
            return "No ambush fire available"

    def _generate_objective_placement(self, scenario_type: str) -> ObjectivePlacement:
        """Generate objective placement rules for scenario."""
        count = random.randint(1, 3) + 2  # D3+2 = 3-5 objectives

        first_placement = {
            "meeting": "Center of table",
            "assault": "Defender's half of table",
            "defense": "Defender's deployment zone",
            "breakthrough": "Along center line",
            "flank": "Either flank, 12\" from edge"
        }

        return ObjectivePlacement(
            count=count,
            first_objective=first_placement.get(scenario_type, "Center of table"),
            spacing_rules="All objectives must be 10\" from table edges and other objectives",
            placed_by="Defender places first, then alternating"
        )

    def _generate_reinforcement_schedule(
        self, side: str, battle_size: BattleSize, starting_turn: int = 3
    ) -> ReinforcementSchedule:
        """Generate reinforcement schedule based on battle size."""
        dice_map = {
            BattleSize.SQUAD_PLATOON: "D6",
            BattleSize.COMPANY: "2D6",
            BattleSize.BATTALION: "3D6"
        }

        return ReinforcementSchedule(
            side=side,
            starting_turn=starting_turn,
            dice_per_turn=dice_map[battle_size],
            special_rules=[
                f"Roll {dice_map[battle_size]} at start of turn {starting_turn}+",
                "On a 4+, reinforcements arrive from reserve edge",
                "Maximum 1/3 of force may arrive per turn"
            ]
        )

    def _generate_deployment_map(
        self,
        scenario_name: str,
        table_size: TableSize,
        attacker_zone: str,
        defender_zone: str,
        objectives_count: int
    ) -> str:
        """Generate ASCII deployment map for scenario."""

        # Determine table dimensions in characters
        if table_size == TableSize.STANDARD:
            width, height = 60, 40
            size_label = "6' x 4'"
        elif table_size == TableSize.SMALL:
            width, height = 40, 40
            size_label = "4' x 4'"
        elif table_size == TableSize.LARGE:
            width, height = 80, 40
            size_label = "8' x 4'"
        else:
            width, height = 80, 60
            size_label = "8' x 6'"

        lines = []
        lines.append(f"DEPLOYMENT MAP: {scenario_name}")
        lines.append(f"Table Size: {size_label}")
        lines.append("")
        lines.append("+" + "-" * width + "+")

        # Add objective markers (O)
        mid_height = height // 2
        for i in range(height):
            if i == 0:
                # North edge (usually defender)
                line = "|" + "=" * width + "|  NORTH (Defender)"
            elif i == height - 1:
                # South edge (usually attacker)
                line = "|" + "=" * width + "|  SOUTH (Attacker)"
            elif i == mid_height:
                # Center line with objectives
                obj_spacing = width // (objectives_count + 1)
                center_line = " " * width
                center_list = list(center_line)
                for obj_num in range(objectives_count):
                    pos = obj_spacing * (obj_num + 1)
                    if pos < width:
                        center_list[pos] = "O"
                line = "|" + "".join(center_list) + "|  Objectives"
            elif i < height // 3:
                # Defender deployment zone
                line = "|" + " " * width + "|  Defender Zone"
            elif i > (2 * height) // 3:
                # Attacker deployment zone
                line = "|" + " " * width + "|  Attacker Zone"
            else:
                # No man's land
                line = "|" + " " * width + "|"

            lines.append(line)

        lines.append("+" + "-" * width + "+")
        lines.append("")
        lines.append("Legend: O = Objective, = = Deployment Zone Edge")

        return "\n".join(lines)

    def _format_markdown_2_page(self, scenario: RandomScenario) -> str:
        """Format scenario as 2-page markdown output."""
        lines = []

        # ====================================================================
        # PAGE 1
        # ====================================================================
        lines.append(f"# {scenario.number}. {scenario.name}")
        lines.append("")

        # Metadata
        lines.append("**Scenario Metadata**")
        lines.append(f"- **Battle Size**: {scenario.battle_size.value}")
        lines.append(f"- **Table Size**: {scenario.table_size.value}")
        lines.append(f"- **Year**: {scenario.year}")
        lines.append(f"- **Location Type**: {scenario.location_type}")
        lines.append(f"- **Recommended Nations**: {', '.join(scenario.recommended_nations)}")
        lines.append("")

        # Situation Report
        lines.append("## SITUATION REPORT")
        lines.append("")
        lines.append(scenario.situation_report)
        lines.append("")

        # Tactical Context
        lines.append("## TACTICAL SITUATION")
        lines.append("")
        lines.append(scenario.tactical_context)
        lines.append("")

        # Terrain Setup
        lines.append("## THE BATTLEFIELD")
        lines.append("")
        lines.append(f"**Table Size**: {scenario.table_size.value}")
        lines.append("")
        lines.append("**Terrain Features** (rolled on North Africa Terrain Table):")
        lines.append("")
        for i, terrain in enumerate(scenario.terrain_features, 1):
            lines.append(f"{i}. **{terrain.name}** ({terrain.size})")
            lines.append(f"   - {terrain.description}")
            lines.append(f"   - *Special Rules*: {terrain.special_rules}")
            if terrain.cover_type:
                lines.append(f"   - *Cover*: {terrain.cover_type.title()}")
            if terrain.movement_penalty:
                lines.append(f"   - *Movement*: {terrain.movement_penalty.title()}")
            lines.append("")

        if scenario.terrain_notes:
            lines.append(f"**Terrain Notes**: {scenario.terrain_notes}")
            lines.append("")

        # Weather
        lines.append("## WEATHER CONDITIONS")
        lines.append("")
        lines.append(f"**Condition**: {scenario.weather.condition.title()}")
        lines.append("")
        if scenario.weather.effects:
            lines.append("**Effects**:")
            for effect in scenario.weather.effects:
                lines.append(f"- {effect}")
            lines.append("")

        # Deployment Map
        lines.append("## DEPLOYMENT MAP")
        lines.append("")
        lines.append("```")
        lines.append(scenario.deployment_map)
        lines.append("```")
        lines.append("")

        # Page break
        lines.append("---")
        lines.append("")
        lines.append("<!-- PAGE 2 -->")
        lines.append("")

        # ====================================================================
        # PAGE 2
        # ====================================================================

        # Victory Conditions
        lines.append("## VICTORY CONDITIONS")
        lines.append("")
        lines.append(scenario.victory_conditions)
        lines.append("")

        # Objectives
        lines.append("## OBJECTIVES")
        lines.append("")
        lines.append(f"**Number of Objectives**: {scenario.objectives.count}")
        lines.append(f"**First Objective Placement**: {scenario.objectives.first_objective}")
        lines.append(f"**Spacing Rules**: {scenario.objectives.spacing_rules}")
        lines.append(f"**Placed By**: {scenario.objectives.placed_by}")
        lines.append("")

        # Deployment Procedure
        lines.append("## DEPLOYMENT PROCEDURE")
        lines.append("")
        for i, step in enumerate(scenario.deployment_steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

        lines.append("**Deployment Zones**:")
        for zone in scenario.deployment_zones:
            lines.append(f"- **{zone.side}**: {zone.location}")
            if zone.special_rules:
                for rule in zone.special_rules:
                    lines.append(f"  - {rule}")
        lines.append("")

        # Special Scenario Rules
        if scenario.special_rules:
            lines.append("## SPECIAL SCENARIO RULES")
            lines.append("")
            for rule in scenario.special_rules:
                lines.append(f"- {rule}")
            lines.append("")

        # Forces
        lines.append("## FORCES")
        lines.append("")
        lines.append(f"**Attacker**: {scenario.attacker_points} points")
        lines.append(f"**Defender**: {scenario.defender_points} points")
        lines.append("")
        lines.append("*Use the Force Roster Builder to create specific forces within these budgets.*")
        lines.append("")

        # Reinforcements
        if scenario.reinforcements:
            lines.append("## REINFORCEMENTS")
            lines.append("")
            for reinf in scenario.reinforcements:
                lines.append(f"**{reinf.side}**:")
                lines.append(f"- Starting Turn: {reinf.starting_turn}")
                lines.append(f"- Dice per Turn: {reinf.dice_per_turn}")
                if reinf.special_rules:
                    lines.append("- Special Rules:")
                    for rule in reinf.special_rules:
                        lines.append(f"  - {rule}")
                lines.append("")

        # Image Placeholders
        lines.append("## IMAGES")
        lines.append("")
        lines.append(f"![Historical Photo](images/{scenario.name.lower().replace(' ', '_')}_historical.jpg)")
        lines.append("")
        lines.append(f"![Miniatures Setup](images/{scenario.name.lower().replace(' ', '_')}_setup.jpg)")
        lines.append("")

        # Alternative Forces
        lines.append("## ALTERNATIVE FORCES")
        lines.append("")
        lines.append("This scenario uses generic point budgets suitable for any nations fighting in North Africa.")
        lines.append("")
        lines.append("**Suggested Matchups**:")
        for nation in scenario.recommended_nations:
            lines.append(f"- {nation.title()} forces")
        lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # SCENARIO GENERATION METHODS (12 TEMPLATES)
    # ========================================================================

    def _generate_desert_patrol_clash(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 1: Desert Patrol Clash (Meeting Engagement)
        Adapted from Kursk "Clash of Reconnaissance"
        """

        # Roll terrain and weather
        terrain = roll_terrain(num_pieces=random.randint(2, 4))  # D3+1
        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        # Generate objectives
        objectives = self._generate_objective_placement("meeting")

        # Deployment
        deployment_zones = [
            DeploymentZone(
                side="Player 1",
                location="South table edge, 12\" deep",
                special_rules=["May deploy scouts up to 18\" onto table"]
            ),
            DeploymentZone(
                side="Player 2",
                location="North table edge, 12\" deep",
                special_rules=["May deploy scouts up to 18\" onto table"]
            )
        ]

        deployment_steps = [
            "Both players count their scout/recce units",
            "Player with MOST scouts chooses table edge (tie = roll off)",
            "Player with MOST scouts deploys first",
            "Both players place scouts first, then remaining units alternately",
            "Roll for initiative each turn (scouts give +1 per scout unit)"
        ]

        # Reinforcements (none for meeting engagement)
        reinforcements = []

        # Special rules
        special_rules = [
            "**Scout Advantage**: +1 to initiative per scout unit",
            "**Ambush Fire**: Side with most scouts may have D3 units ambush fire",
            "**Mobile Warfare**: All vehicles move at full speed on roads/tracks",
            "**Meeting Engagement**: No prepared positions or fortifications"
        ]

        # Victory conditions
        victory = (
            "**Major Victory**: Control 3+ objectives at game end AND have not reached BR limit.\n\n"
            "**Minor Victory**: Control 2+ objectives at game end OR force enemy to BR limit.\n\n"
            "**Draw**: Equal objectives controlled or both sides reach BR limit."
        )

        # ASCII map
        deployment_map = self._generate_deployment_map(
            "Desert Patrol Clash",
            table_size,
            "South 12\"",
            "North 12\"",
            objectives.count
        )

        return RandomScenario(
            number=1,
            name="DESERT PATROL CLASH",
            scenario_type=ScenarioType.MEETING_ENGAGEMENT,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "Reconnaissance patrols from both sides have unexpectedly encountered each other "
                "in the desert. Neither side has had time to prepare positions. The side that can "
                "seize the key terrain features and establish control will gain valuable intelligence "
                "and tactical advantage."
            ),
            tactical_context=(
                "This is a fast-moving encounter battle. Scout units are critical for gaining "
                "initiative and choosing favorable positions. Rapid deployment and aggressive "
                "movement to objectives will determine the victor."
            ),
            terrain_features=terrain,
            terrain_notes="Light terrain typical of desert patrol routes",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=attacker_points,
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_oasis_counter_attack(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 2: Oasis Counter-Attack
        Defender holds oasis, attacker must capture it, defender counter-attacks
        """

        # Ensure oasis terrain is included
        terrain = [
            TerrainFeature(
                "Oasis",
                "Center of table (PRIMARY OBJECTIVE)",
                "Strategic water source with palm trees",
                "Counts as soft cover. This is the primary objective.",
                cover_type="soft",
                movement_penalty="none"
            )
        ]
        # Add random terrain
        terrain.extend(roll_terrain(num_pieces=random.randint(2, 3)))

        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=1,  # Just the oasis
            first_objective="The Oasis in table center",
            spacing_rules="Single objective scenario",
            placed_by="Scenario-defined (Oasis is the objective)"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker",
                location="South table edge, 12\" deep",
                special_rules=["Attacks first", "No prepared positions"]
            ),
            DeploymentZone(
                side="Defender",
                location="Within 12\" of the Oasis",
                special_rules=[
                    "Deploys first",
                    "May fortify Oasis (light cover becomes hard cover)",
                    "Receives reinforcements turn 3+ for counter-attack"
                ]
            )
        ]

        deployment_steps = [
            "Place Oasis in table center (primary objective)",
            "Defender deploys ALL units within 12\" of Oasis",
            "Attacker deploys in deployment zone",
            "Defender keeps 1/3 of force off table as counter-attack reserve",
            "Game begins - Attacker has first turn"
        ]

        # Defender gets reinforcements for counter-attack
        reinforcements = [
            self._generate_reinforcement_schedule("Defender", battle_size, starting_turn=3)
        ]

        special_rules = [
            "**Hold the Oasis**: Unit within 6\" of Oasis center controls it",
            "**Water Source**: Oasis provides soft cover and blocks LOS beyond 5\"",
            "**Counter-Attack**: Defender's reserves arrive turn 3+ from any table edge",
            "**Asymmetric Forces**: Defender has fewer points but prepared positions"
        ]

        victory = (
            "**Attacker Victory**: Control the Oasis at game end AND defender reaches BR limit.\n\n"
            "**Defender Victory**: Control the Oasis at game end OR attacker reaches BR limit before capturing it.\n\n"
            "**Draw**: Oasis contested at game end."
        )

        deployment_map = self._generate_deployment_map(
            "Oasis Counter-Attack",
            table_size,
            "South 12\"",
            "Within 12\" of Center Oasis",
            1
        )

        return RandomScenario(
            number=2,
            name="OASIS COUNTER-ATTACK",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "A vital oasis has been occupied by enemy forces. Your mission is to attack and "
                "capture this critical water source. However, intelligence suggests the enemy has "
                "reserves nearby and will launch a counter-attack once your assault is underway."
            ),
            tactical_context=(
                "The attacker must move quickly to seize the Oasis before defender reinforcements "
                "arrive. The defender must hold long enough for reserves to arrive and then launch "
                "a decisive counter-attack to retake the position."
            ),
            terrain_features=terrain,
            terrain_notes="Oasis is the focal point, with approach terrain providing limited cover",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=attacker_points,
            defender_points=int(defender_points * 0.8),  # Defender gets 80% points but reinforcements
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_desert_flanking(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 3: Desert Flanking Maneuver
        Attacker attempts flanking move, portion of force arrives from flank
        """

        terrain = roll_terrain(num_pieces=random.randint(3, 5))
        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = self._generate_objective_placement("assault")

        deployment_zones = [
            DeploymentZone(
                side="Attacker (Main Force)",
                location="South table edge, 12\" deep",
                special_rules=["2/3 of force deploys here", "Attacks first"]
            ),
            DeploymentZone(
                side="Attacker (Flanking Force)",
                location="East or West table edge (attacker chooses)",
                special_rules=[
                    "1/3 of force (must include at least 1 scout/recce unit)",
                    "Arrives turn 2+ on roll of 4+ (automatic turn 4)"
                ]
            ),
            DeploymentZone(
                side="Defender",
                location="North half of table, 18\" deep",
                special_rules=["Deploys first", "May prepare positions"]
            )
        ]

        deployment_steps = [
            "Defender places all objectives in their half",
            "Defender deploys entire force",
            "Attacker deploys 2/3 of force in main deployment zone",
            "Attacker designates 1/3 of force as flanking force (must include scout)",
            "Attacker chooses which flank (East or West) for flanking force",
            "Flanking force arrives turn 2+ on 4+ (automatic turn 4)",
            "Attacker has first turn"
        ]

        reinforcements = [
            ReinforcementSchedule(
                side="Attacker (Flanking Force)",
                starting_turn=2,
                dice_per_turn="D6",
                special_rules=[
                    "Roll D6 at start of turn 2+",
                    "4+ = Flanking force arrives",
                    "Automatic arrival on turn 4 if not yet arrived",
                    "Arrives from designated flank edge"
                ]
            )
        ]

        special_rules = [
            "**Flanking Force**: Attacker divides force 2/3 main, 1/3 flank (must include scout)",
            "**Flank Arrival**: Roll D6 turn 2+, 4+ arrives (automatic turn 4)",
            "**Scout Requirement**: Flanking force must include at least 1 recce/scout unit",
            "**Flank Choice**: Attacker chooses East or West flank secretly before deployment"
        ]

        victory = (
            "**Attacker Victory**: Control 2+ objectives in defender's deployment zone at game end.\n\n"
            "**Defender Victory**: Prevent attacker from controlling objectives AND inflict heavy casualties.\n\n"
            "**Draw**: Attacker controls 1 objective or forces are too depleted to continue."
        )

        deployment_map = self._generate_deployment_map(
            "Desert Flanking Maneuver",
            table_size,
            "South 12\" (Main) + East/West Edge (Flank)",
            "North 18\"",
            objectives.count
        )

        return RandomScenario(
            number=3,
            name="DESERT FLANKING MANEUVER",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "Enemy forces have established a defensive position. Rather than assault directly, "
                "your command has ordered a flanking maneuver through the desert. Your main force "
                "will fix the enemy in place while a mobile flanking column strikes from the side."
            ),
            tactical_context=(
                "Timing is critical. The main force must pressure the defender without being destroyed, "
                "while the flanking force must arrive quickly enough to exploit the tactical advantage. "
                "Defenders must watch both the front and flanks."
            ),
            terrain_features=terrain,
            terrain_notes="Open terrain favors flanking maneuver but provides limited cover",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=attacker_points,
            defender_points=int(defender_points * 0.85),  # Slight advantage to attacker
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_wadi_crossing(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 4: Wadi Crossing
        Attacker must cross wadi, defender defends far side
        """

        # Ensure wadi terrain
        terrain = [
            TerrainFeature(
                "Wadi (Dry)",
                "Runs across center of table (East-West), 6\" wide",
                "Deep dry riverbed providing excellent cover but difficult to cross",
                "Infantry and vehicles in wadi gain hard cover. Difficult terrain to enter/exit.",
                cover_type="hard",
                movement_penalty="difficult"
            )
        ]
        terrain.extend(roll_terrain(num_pieces=random.randint(2, 3)))

        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=random.randint(2, 4),  # D3+1
            first_objective="North side of wadi (defender's side)",
            spacing_rules="All objectives on defender's side of wadi, 10\" spacing",
            placed_by="Defender places all objectives on their side of wadi"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker",
                location="South of wadi, 12\" deep",
                special_rules=["Must cross wadi to reach objectives", "Attacks first"]
            ),
            DeploymentZone(
                side="Defender",
                location="North of wadi, 18\" deep",
                special_rules=[
                    "Deploys first",
                    "May place obstacles at wadi crossing points",
                    "Prepared positions on objectives"
                ]
            )
        ]

        deployment_steps = [
            "Place wadi running East-West across table center (6\" wide)",
            "Defender places 2-4 objectives on their side of wadi",
            "Defender deploys entire force north of wadi",
            "Defender may place obstacles (wire, mines) at up to 3 crossing points",
            "Attacker deploys south of wadi",
            "Attacker has first turn"
        ]

        reinforcements = []

        special_rules = [
            "**Wadi Crossing**: Entering/exiting wadi counts as difficult terrain",
            "**Hard Cover**: Units in the wadi gain hard cover from direct fire",
            "**Crossing Points**: Defender may obstruct up to 3 crossing points with wire/mines",
            "**Prepared Defense**: Defender's units on objectives start dug in (+1 cover save)"
        ]

        victory = (
            "**Attacker Victory**: Control 2+ objectives on north side of wadi at game end.\n\n"
            "**Defender Victory**: Attacker controls 0-1 objectives OR attacker reaches BR limit.\n\n"
            "**Draw**: Attacker controls exactly 1 objective but has not broken through."
        )

        deployment_map = self._generate_deployment_map(
            "Wadi Crossing",
            table_size,
            "South of Wadi (12\")",
            "North of Wadi (18\")",
            objectives.count
        )

        return RandomScenario(
            number=4,
            name="WADI CROSSING",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "A major wadi cuts across your line of advance. Enemy forces have fortified the "
                "far side and positioned themselves to massacre any forces attempting to cross. "
                "You must force a crossing and establish a bridgehead on the far side."
            ),
            tactical_context=(
                "The wadi provides excellent cover but slows movement. Attacker must use smoke, "
                "suppression fire, and speed to minimize exposure. Defender must prevent any "
                "foothold from being established on the far bank."
            ),
            terrain_features=terrain,
            terrain_notes="Wadi dominates the battlefield as a major linear obstacle",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=int(attacker_points * 1.2),  # Attacker needs advantage for assault
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_escarpment_defense(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 5: Escarpment Defense
        Defender holds high ground (escarpment), attacker must take it
        """

        # Ensure escarpment/ridge terrain
        terrain = [
            TerrainFeature(
                "Escarpment/Ridge",
                "North table edge to 18\" deep",
                "Major cliff or steep ridge providing elevated positions and observation",
                "Impassable to vehicles except at designated passes. Infantry can climb (dangerous terrain). +2 observation.",
                cover_type="hard",
                movement_penalty="impassable"
            )
        ]
        terrain.extend(roll_terrain(num_pieces=random.randint(1, 3)))

        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=3,
            first_objective="Top of escarpment (defender's position)",
            spacing_rules="Objectives on top of escarpment/ridge line",
            placed_by="Scenario-defined (along escarpment)"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker",
                location="South table edge, 12\" deep (below escarpment)",
                special_rules=["Attacks uphill", "No prepared positions"]
            ),
            DeploymentZone(
                side="Defender",
                location="On/behind escarpment, north 18\" of table",
                special_rules=[
                    "Elevated positions (+2 observation)",
                    "Hull-down positions available",
                    "Prepared defensive works"
                ]
            )
        ]

        deployment_steps = [
            "Place escarpment/ridge across north side of table",
            "Place 3 objectives along the escarpment ridgeline",
            "Defender deploys on/behind escarpment",
            "Defender may place defensive works (trenches, wire, gun pits)",
            "Attacker deploys below escarpment",
            "Attacker has first turn but faces uphill assault"
        ]

        reinforcements = []

        special_rules = [
            "**High Ground**: Defender has +2 observation from escarpment positions",
            "**Hull Down**: Vehicles on escarpment may take hull-down positions (-1 to hit)",
            "**Difficult Assault**: Climbing escarpment is dangerous terrain for infantry",
            "**Impassable**: Vehicles cannot climb except at designated passes/routes",
            "**Defensive Works**: Defender may fortify positions before game"
        ]

        victory = (
            "**Attacker Victory**: Control 2+ objectives on the escarpment at game end.\n\n"
            "**Defender Victory**: Hold 2+ objectives OR attacker reaches BR limit before taking objectives.\n\n"
            "**Draw**: Equal objectives controlled or attacker controls 1 objective."
        )

        deployment_map = self._generate_deployment_map(
            "Escarpment Defense",
            table_size,
            "South 12\" (Below Escarpment)",
            "North 18\" (On Escarpment)",
            3
        )

        return RandomScenario(
            number=5,
            name="ESCARPMENT DEFENSE",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "Enemy forces have occupied a commanding escarpment that dominates the surrounding "
                "desert. From these heights, they can observe and engage our forces at long range. "
                "The escarpment must be taken to continue the advance."
            ),
            tactical_context=(
                "The defender has every advantage: height, observation, prepared positions, and the "
                "attacker must climb under fire. Success requires overwhelming firepower, smoke screens, "
                "and determination. Classic examples: Halfaya Pass, Alam Halfa ridge."
            ),
            terrain_features=terrain,
            terrain_notes="Escarpment dominates battlefield; attacker must find routes up",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=int(attacker_points * 1.3),  # Attacker needs significant advantage
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_pass_assault(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 6: Pass Assault
        Narrow pass/defile defended by enemy forces (Halfaya, Kasserine)
        """

        # Mountain pass terrain
        terrain = [
            TerrainFeature(
                "Mountain Pass",
                "Runs North-South through table center, 12\" wide",
                "Narrow defile between impassable rocky hills/mountains",
                "Only vehicles can use the pass road. Infantry can climb hills (dangerous terrain).",
                cover_type="none",
                movement_penalty="none"
            ),
            TerrainFeature(
                "Rocky Hills (East Side)",
                "East side of pass, impassable to vehicles",
                "Steep rocky terrain flanking the pass",
                "Impassable to vehicles. Dangerous terrain for infantry. Provides hard cover and +1 observation.",
                cover_type="hard",
                movement_penalty="impassable"
            ),
            TerrainFeature(
                "Rocky Hills (West Side)",
                "West side of pass, impassable to vehicles",
                "Steep rocky terrain flanking the pass",
                "Impassable to vehicles. Dangerous terrain for infantry. Provides hard cover and +1 observation.",
                cover_type="hard",
                movement_penalty="impassable"
            )
        ]

        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=3,
            first_objective="North exit of pass (defender's side)",
            spacing_rules="Objectives along the pass road and flanking heights",
            placed_by="Scenario-defined (1 in pass, 1 on each flank height)"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker",
                location="South table edge (entering pass)",
                special_rules=["Funneled into narrow pass", "Vehicles must use road"]
            ),
            DeploymentZone(
                side="Defender",
                location="North half of pass and flanking heights",
                special_rules=[
                    "Fortified pass exit",
                    "AT guns positioned to cover pass",
                    "Infantry on flanking heights"
                ]
            )
        ]

        deployment_steps = [
            "Place mountain pass running N-S through table center (12\" wide)",
            "Place impassable rocky hills on both sides of pass",
            "Place 3 objectives: 1 at north pass exit, 1 on each flank height",
            "Defender deploys in north half with prepared positions",
            "Defender places obstacles/mines in pass (up to 3 locations)",
            "Attacker deploys at south end entering pass",
            "Attacker has first turn"
        ]

        reinforcements = []

        special_rules = [
            "**Narrow Frontage**: Only 2-3 vehicles abreast can move through pass",
            "**Flanking Heights**: Infantry can climb hills but vehicles cannot",
            "**Prepared Defense**: Defender has fortified pass exit and heights",
            "**Observation**: Units on heights get +1 observation and can spot into pass",
            "**Bottleneck**: Destroyed vehicles block the pass (difficult terrain)"
        ]

        victory = (
            "**Attacker Victory**: Control north exit of pass (main objective) at game end.\n\n"
            "**Defender Victory**: Hold pass exit OR attacker reaches BR limit in the killing zone.\n\n"
            "**Draw**: Attacker controls 1-2 flank objectives but not pass exit."
        )

        deployment_map = self._generate_deployment_map(
            "Pass Assault",
            table_size,
            "South End of Pass",
            "North End of Pass + Heights",
            3
        )

        return RandomScenario(
            number=6,
            name="PASS ASSAULT",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "A vital mountain pass blocks your advance. The enemy has fortified the exit with "
                "anti-tank guns and positioned infantry on the commanding heights. To continue the "
                "offensive, the pass must be taken. Historical examples: Halfaya Pass, Kasserine Pass."
            ),
            tactical_context=(
                "This is one of the most difficult assaults in warfare: a frontal attack through a "
                "narrow defile against prepared defenses. The attacker must either force through with "
                "overwhelming firepower or infiltrate infantry up the heights to outflank the defenses."
            ),
            terrain_features=terrain,
            terrain_notes="Mountain pass creates a deadly funnel for attacking forces",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=int(attacker_points * 1.4),  # Attacker needs major advantage
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_convoy_ambush(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 7: Supply Convoy Ambush (NEW Africa-specific)
        Attacker ambushes supply convoy, defender must protect convoy
        """

        # Road terrain
        terrain = [
            TerrainFeature(
                "Desert Road/Track",
                "Runs East-West across table center",
                "Main supply route for the convoy",
                "Fast movement for vehicles. Convoy must stay on road.",
                cover_type="none",
                movement_penalty="none"
            )
        ]
        terrain.extend(roll_terrain(num_pieces=random.randint(2, 4)))

        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        # Convoy trucks are objectives
        objectives = ObjectivePlacement(
            count=random.randint(2, 4),  # D3+1 = 3-4 convoy trucks
            first_objective="Convoy trucks (defender controlled)",
            spacing_rules="Trucks start on road in defender's deployment zone",
            placed_by="Defender places convoy trucks on road"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker (Ambush Force)",
                location="Hidden deployment within 18\" of road (excluding defender zone)",
                special_rules=[
                    "Deploy hidden (reveal when moving or firing)",
                    "May deploy after seeing convoy positions",
                    "First turn surprise (+1 to hit)"
                ]
            ),
            DeploymentZone(
                side="Defender (Convoy)",
                location="West table edge moving East along road",
                special_rules=[
                    "Convoy trucks must be on road",
                    "Escorts deploy within 6\" of trucks",
                    "Convoy moves first turn toward East edge"
                ]
            )
        ]

        deployment_steps = [
            "Place road running E-W across table",
            "Defender places 3-4 convoy trucks on road at West edge",
            "Defender deploys escort forces within 6\" of convoy",
            "Attacker places hidden deployment markers (reveal when acting)",
            "Convoy begins moving East on turn 1",
            "Ambush is sprung when attacker reveals or defender spots them"
        ]

        reinforcements = []

        special_rules = [
            "**Convoy Movement**: Trucks move 12\" per turn along road toward East edge",
            "**Hidden Deployment**: Attacker deploys hidden, reveals when moving/firing",
            "**Surprise**: First turn of ambush, attacker gets +1 to hit",
            "**Truck Vulnerability**: Convoy trucks have Armor 0, destroyed on any penetrating hit",
            "**Escape**: Trucks that exit East edge are saved (count as objectives held)",
            "**Escort**: Defender must keep escorts within 12\" of convoy or trucks stop"
        ]

        victory = (
            "**Attacker Victory**: Destroy or capture 2+ convoy trucks before they escape.\n\n"
            "**Defender Victory**: Get 2+ trucks off East edge OR destroy ambush force.\n\n"
            "**Draw**: Equal trucks destroyed/escaped, or convoy halted."
        )

        deployment_map = self._generate_deployment_map(
            "Supply Convoy Ambush",
            table_size,
            "Hidden within 18\" of Road",
            "West Edge (Convoy)",
            objectives.count
        )

        return RandomScenario(
            number=7,
            name="SUPPLY CONVOY AMBUSH",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "Intelligence reports an enemy supply convoy moving along the desert road. This is "
                "an opportunity to strike a critical blow against enemy logistics. Your forces have "
                "positioned for an ambush. Destroy or capture the convoy trucks before they escape."
            ),
            tactical_context=(
                "The ambusher must strike fast and hard before escorts can react. The convoy must "
                "keep moving - stopping means destruction. Classic desert warfare: fast raids on "
                "vulnerable supply lines."
            ),
            terrain_features=terrain,
            terrain_notes="Open terrain with limited cover near the road",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=int(attacker_points * 0.8),  # Ambusher gets fewer points but surprise
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_airfield_assault(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 8: Airfield Assault (NEW Africa-specific)
        Attacker raids enemy airfield to destroy aircraft/facilities
        """

        # Airfield terrain
        terrain = [
            TerrainFeature(
                "Desert Airstrip",
                "Center of table, 30\" × 20\" area",
                "Cleared runway with fuel dumps and aircraft dispersals",
                "Open ground. Aircraft and fuel dumps are objectives/targets.",
                cover_type="none",
                movement_penalty="none"
            ),
            TerrainFeature(
                "Hangar/Control Tower",
                "North side of runway",
                "Small buildings for airfield operations",
                "Hard cover. May be fortified by defender.",
                cover_type="hard",
                movement_penalty="impassable"
            ),
            TerrainFeature(
                "Fuel Dump",
                "East side of runway",
                "Stacked fuel drums (target)",
                "Soft cover. Explodes if destroyed (pinning within 10\").",
                cover_type="soft",
                movement_penalty="none"
            ),
            TerrainFeature(
                "Aircraft Dispersals",
                "Scatter 3-4 around runway",
                "Parked aircraft (targets)",
                "Destroying aircraft is attacker objective.",
                cover_type="none",
                movement_penalty="none"
            )
        ]

        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=5,
            first_objective="Destroy/capture airfield facilities",
            spacing_rules="3-4 aircraft + fuel dump + control tower = 5 objectives",
            placed_by="Scenario-defined (airfield facilities)"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker (Raiding Force)",
                location="South table edge, 12\" deep",
                special_rules=[
                    "Fast moving raid force",
                    "Must destroy aircraft and facilities",
                    "May need to withdraw before reinforcements arrive"
                ]
            ),
            DeploymentZone(
                side="Defender (Airfield Garrison)",
                location="Within 12\" of runway/buildings",
                special_rules=[
                    "Light garrison forces (50% of attacker points)",
                    "Reinforcements arrive turn 3+ (main base nearby)",
                    "May fortify control tower"
                ]
            )
        ]

        deployment_steps = [
            "Place airfield runway in table center",
            "Place 3-4 aircraft at dispersals around runway",
            "Place fuel dump, hangar, control tower",
            "Defender deploys light garrison (50% points) within 12\" of runway",
            "Attacker deploys entire force in deployment zone",
            "Attacker gets first turn (surprise raid)"
        ]

        # Defender gets reinforcements (base reaction force)
        reinforcements = [
            self._generate_reinforcement_schedule("Defender", battle_size, starting_turn=3)
        ]
        reinforcements[0].special_rules.append("Reinforcements are base reaction force arriving from North edge")

        special_rules = [
            "**Aircraft Targets**: Each aircraft destroyed = 1 objective. Armor 0, any hit destroys.",
            "**Fuel Dump**: Explodes on destruction (all units within 10\" must pass pinning test)",
            "**Control Tower**: Capturing control tower = 1 objective (must have unit in base)",
            "**Time Limit**: Attacker must withdraw by turn 6 or face overwhelming reinforcements",
            "**Surprise Raid**: Attacker gets +1 to hit on turn 1 only",
            "**Light Garrison**: Defender starts with 50% points, reinforcements 50% arrive turn 3+"
        ]

        victory = (
            "**Attacker Major Victory**: Destroy 3+ aircraft AND fuel dump AND withdraw by turn 6.\n\n"
            "**Attacker Minor Victory**: Destroy 2+ aircraft or fuel dump AND withdraw.\n\n"
            "**Defender Victory**: Prevent destruction of aircraft OR trap attacker (don't let them withdraw).\n\n"
            "**Draw**: Heavy damage but both sides depleted."
        )

        deployment_map = self._generate_deployment_map(
            "Airfield Assault",
            table_size,
            "South 12\"",
            "Within 12\" of Runway",
            5
        )

        return RandomScenario(
            number=8,
            name="AIRFIELD ASSAULT",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "An enemy airfield lies lightly defended. A bold raid could destroy aircraft on the "
                "ground and cripple enemy air operations. Your forces must strike fast, destroy as "
                "much as possible, and withdraw before enemy reinforcements arrive from the main base."
            ),
            tactical_context=(
                "This is a raid, not an occupation. Speed is essential. Destroy high-value targets "
                "(aircraft, fuel) quickly and get out. Don't get bogged down or you'll be trapped "
                "when reinforcements arrive."
            ),
            terrain_features=terrain,
            terrain_notes="Open airfield with parked aircraft and fuel as primary targets",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=attacker_points,
            defender_points=int(defender_points * 0.5),  # Split 50/50 garrison and reinforcements
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_fortified_box(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 9: Fortified Box Defense (NEW Africa-specific)
        Defender holds fortified "box" position (Gazala, Tobruk style)
        """

        # Fortified box terrain
        terrain = [
            TerrainFeature(
                "Perimeter Defenses",
                "18\" × 18\" square in table center",
                "Minefields, barbed wire, defensive positions forming a box",
                "Minefield (dangerous terrain). Wire (difficult terrain). Trenches (hard cover).",
                cover_type="hard",
                movement_penalty="dangerous"
            ),
            TerrainFeature(
                "Command Post",
                "Center of box",
                "Fortified HQ bunker",
                "Hard cover with +1 cover save. Primary objective.",
                cover_type="hard",
                movement_penalty="impassable"
            ),
            TerrainFeature(
                "Supply Dump",
                "Inside box (East side)",
                "Ammunition and supply cache",
                "Objective. Explodes if hit.",
                cover_type="soft",
                movement_penalty="none"
            ),
            TerrainFeature(
                "Gun Positions",
                "Corners of box (4 positions)",
                "Dug-in AT gun positions",
                "Hard cover, prepared fields of fire.",
                cover_type="hard",
                movement_penalty="difficult"
            )
        ]

        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=3,
            first_objective="Command Post (center of box)",
            spacing_rules="Command post + 2 corner gun positions = 3 objectives",
            placed_by="Scenario-defined (fortified box positions)"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker",
                location="All table edges except within 12\" of box",
                special_rules=[
                    "May choose which edge(s) to attack from",
                    "Must breach perimeter to reach objectives",
                    "Heavy losses expected"
                ]
            ),
            DeploymentZone(
                side="Defender",
                location="Within the fortified box (18\" × 18\")",
                special_rules=[
                    "All units start dug-in (+1 cover save)",
                    "Minefields and wire on perimeter",
                    "Prepared fields of fire (re-roll missed AT shots turn 1-2)"
                ]
            )
        ]

        deployment_steps = [
            "Place 18\" × 18\" fortified box in table center",
            "Place minefields and wire around perimeter",
            "Place command post in center, gun positions at corners",
            "Defender deploys all units inside box (dug in)",
            "Attacker chooses which table edge(s) to attack from",
            "Attacker deploys and attacks first"
        ]

        reinforcements = []

        special_rules = [
            "**Fortified Box**: Defender's units start dug-in (+1 cover save)",
            "**Minefields**: D6 per unit entering, 6 = immobilized vehicle or pinned infantry",
            "**Barbed Wire**: Difficult terrain, infantry may cut (requires turn in contact)",
            "**Prepared Defense**: Defender re-rolls missed AT shots turns 1-2",
            "**All-Around Defense**: Defender can face any direction without penalty",
            "**Breakthrough Required**: Attacker must breach perimeter and reach objectives"
        ]

        victory = (
            "**Attacker Victory**: Capture command post AND 1+ gun position.\n\n"
            "**Defender Victory**: Hold command post OR attacker reaches BR limit.\n\n"
            "**Draw**: Attacker breaches perimeter but cannot take command post."
        )

        deployment_map = self._generate_deployment_map(
            "Fortified Box Defense",
            table_size,
            "Any Edge (Attacker Choice)",
            "Inside 18\" × 18\" Box",
            3
        )

        return RandomScenario(
            number=9,
            name="FORTIFIED BOX DEFENSE",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "Enemy forces have created a fortified 'box' position with all-around defenses. "
                "This strongpoint blocks our advance and must be reduced. The position is heavily "
                "mined and wired, with prepared gun positions covering all approaches. "
                "Historical examples: Gazala boxes, Tobruk perimeter strongpoints."
            ),
            tactical_context=(
                "Breaking a fortified box requires overwhelming force, careful breaching of minefields, "
                "and accepting heavy casualties. The defender has prepared fields of fire and can "
                "engage from all sides. Artillery and engineer support are essential."
            ),
            terrain_features=terrain,
            terrain_notes="Central fortified box with mines, wire, and dug-in positions",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=int(attacker_points * 1.5),  # Attacker needs overwhelming advantage
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_coastal_road(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 10: Coastal Road Defense (NEW Africa-specific)
        Fight along Via Balbia coastal road
        """

        # Coastal terrain
        terrain = [
            TerrainFeature(
                "Via Balbia (Coastal Road)",
                "Runs East-West along North table edge (6\" from edge)",
                "Paved coastal road, key strategic route",
                "Fast movement. Controlling road is key objective.",
                cover_type="none",
                movement_penalty="none"
            ),
            TerrainFeature(
                "Mediterranean Sea",
                "North table edge (off-board)",
                "Sea prevents outflanking from north",
                "Impassable. May have naval gunfire support (optional).",
                cover_type="none",
                movement_penalty="impassable"
            ),
            TerrainFeature(
                "Coastal Village",
                "On road, center of table",
                "Small coastal settlement (2-3 buildings)",
                "Hard cover. Primary objective.",
                cover_type="hard",
                movement_penalty="difficult"
            )
        ]
        terrain.extend(roll_terrain(num_pieces=random.randint(1, 2)))

        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=3,
            first_objective="Coastal village on road",
            spacing_rules="Village + 2 road sections (East/West of village)",
            placed_by="Scenario-defined (along coastal road)"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker",
                location="West table edge, advancing East along coast",
                special_rules=[
                    "Funneled between sea and desert",
                    "Limited flanking room",
                    "Advancing along road"
                ]
            ),
            DeploymentZone(
                side="Defender",
                location="East half of table, defending road",
                special_rules=[
                    "Blocking positions along road",
                    "May fortify village",
                    "Must prevent attacker breakthrough"
                ]
            )
        ]

        deployment_steps = [
            "Place coastal road E-W along North edge (6\" from edge)",
            "Place village in table center on road",
            "Place 2 additional objectives (road sections E/W of village)",
            "Defender deploys in East half, may fortify village",
            "Attacker deploys in West edge area",
            "Attacker moves first (advancing along coast)"
        ]

        reinforcements = []

        special_rules = [
            "**Coastal Advance**: Sea prevents flanking from north",
            "**Road Control**: Controlling road sections is vital for supply/retreat",
            "**Bottleneck**: Limited room to deploy forces (narrow frontage)",
            "**Naval Gunfire** (Optional): Defender may call 1 naval bombardment (D6 turns delay)",
            "**Urban Combat**: Village fighting uses special street fighting rules"
        ]

        victory = (
            "**Attacker Victory**: Control village AND 1+ additional road section.\n\n"
            "**Defender Victory**: Hold village OR force attacker to reach BR limit.\n\n"
            "**Draw**: Village contested or road sections split equally."
        )

        deployment_map = self._generate_deployment_map(
            "Coastal Road Defense",
            table_size,
            "West Edge (Advancing East)",
            "East Half (Defending Road)",
            3
        )

        return RandomScenario(
            number=10,
            name="COASTAL ROAD DEFENSE",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "The Via Balbia coastal road is the lifeline of forces in North Africa. Control of "
                "this road means control of logistics and reinforcement. Enemy forces are defending "
                "a coastal village that blocks our advance. The sea prevents flanking - we must "
                "attack directly along the narrow coastal strip."
            ),
            tactical_context=(
                "Limited maneuver room makes this a grinding frontal battle. The defender has a "
                "narrow front to defend. The attacker cannot outflank. Artillery and direct assault "
                "are the only options. Historical examples: fighting along Via Balbia throughout "
                "the North African campaign."
            ),
            terrain_features=terrain,
            terrain_notes="Coastal road with sea to north, limiting maneuver",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=int(attacker_points * 1.2),  # Attacker needs some advantage for frontal assault
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Coastal" if year == "1942" else "Tunisia Coastal",
            recommended_nations=["british", "italian", "german", "american"]
        )

    def _generate_desert_breakthrough(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 11: Desert Breakthrough
        Attacker must break through enemy lines and exit opposite edge
        """

        terrain = roll_terrain(num_pieces=random.randint(3, 5))
        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=2,
            first_objective="Center of table (breach point)",
            spacing_rules="2 breach points in defender's line",
            placed_by="Defender places 2 blocking positions"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker",
                location="South table edge, 12\" deep",
                special_rules=[
                    "Must exit 50%+ force off North edge",
                    "Fast mobile forces preferred",
                    "Overwhelming local superiority needed"
                ]
            ),
            DeploymentZone(
                side="Defender",
                location="Center of table (East-West line)",
                special_rules=[
                    "Blocking positions across table center",
                    "Must prevent breakthrough",
                    "May prepare defensive positions"
                ]
            )
        ]

        deployment_steps = [
            "Defender sets up defensive line across table center (E-W)",
            "Defender places 2 blocking position objectives",
            "Attacker deploys at South edge",
            "Attacker must break through and exit North edge with 50%+ force",
            "Attacker moves first"
        ]

        reinforcements = [
            self._generate_reinforcement_schedule("Defender", battle_size, starting_turn=2)
        ]
        reinforcements[0].special_rules.append("Defender reinforcements arrive from North edge (behind attacker if breakthrough succeeds)")

        special_rules = [
            "**Breakthrough Objective**: Attacker must exit 50%+ force off North edge",
            "**Exit Points**: Calculate based on starting force points value",
            "**Blocking Force**: Defender forms thin line across table center",
            "**Mobile Warfare**: Fast vehicles and recce crucial for breakthrough",
            "**Pursuit**: If attacker breaks through, defender reinforcements pursue from North"
        ]

        victory = (
            "**Attacker Major Victory**: Exit 75%+ of force off North edge.\n\n"
            "**Attacker Minor Victory**: Exit 50-74% of force off North edge.\n\n"
            "**Defender Victory**: Prevent breakthrough (attacker exits <50%).\n\n"
            "**Draw**: Attacker achieves breakthrough but loses 50%+ force doing so."
        )

        deployment_map = self._generate_deployment_map(
            "Desert Breakthrough",
            table_size,
            "South 12\"",
            "Center Line (E-W Blocking)",
            2
        )

        return RandomScenario(
            number=11,
            name="DESERT BREAKTHROUGH",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "Enemy forces have established a thin defensive line across our line of advance. "
                "Rather than reduce each position methodically, Command has ordered a breakthrough "
                "operation. Concentrate overwhelming force at one or two points, smash through, "
                "and race for the rear areas before enemy reserves can react."
            ),
            tactical_context=(
                "This is mobile warfare at its finest. Find the weak point, concentrate force, "
                "break through decisively, and keep moving. Don't get bogged down. The defender "
                "must delay and channel the attacker until reinforcements arrive."
            ),
            terrain_features=terrain,
            terrain_notes="Open terrain favoring mobile operations",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=int(attacker_points * 1.3),  # Attacker needs advantage for breakthrough
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )

    def _generate_rearguard(
        self,
        battle_size: BattleSize,
        table_size: TableSize,
        year: str,
        attacker_points: int,
        defender_points: int
    ) -> RandomScenario:
        """
        Scenario 12: Rearguard Action
        Defender conducting fighting retreat, must delay attacker
        """

        terrain = roll_terrain(num_pieces=random.randint(3, 5))
        weather = roll_weather_1942() if year == "1942" else roll_weather_1943()

        objectives = ObjectivePlacement(
            count=3,
            first_objective="Defender's withdrawal route (North edge)",
            spacing_rules="3 delay positions across table",
            placed_by="Defender places 3 successive delay positions"
        )

        deployment_zones = [
            DeploymentZone(
                side="Attacker",
                location="South table edge, 12\" deep",
                special_rules=[
                    "Pursuing retreating enemy",
                    "Must prevent enemy escape",
                    "Aggressive advance required"
                ]
            ),
            DeploymentZone(
                side="Defender (Rearguard)",
                location="Center and North areas (successive positions)",
                special_rules=[
                    "Must delay attacker",
                    "Can withdraw units that break contact",
                    "Victory = time delay, not holding ground"
                ]
            )
        ]

        deployment_steps = [
            "Defender places 3 successive delay positions (South, Center, North)",
            "Defender deploys 1/3 force at each position",
            "Attacker deploys at South edge",
            "Defender may withdraw units that break contact (move to next position)",
            "Game has 8 turn limit - defender wins by surviving",
            "Attacker moves first (pursuing)"
        ]

        reinforcements = []

        special_rules = [
            "**Fighting Withdrawal**: Defender may withdraw units to next position if not in contact",
            "**Successive Positions**: Defender has 3 prepared positions to fall back through",
            "**Time Limit**: 8 turns - defender wins by exiting units off North edge",
            "**Exit Points**: Defender scores points for units exited off North edge",
            "**Pursuit**: Attacker must press hard to prevent organized withdrawal",
            "**Prepared Positions**: Each defender position starts with defensive prep"
        ]

        victory = (
            "**Defender Major Victory**: Exit 75%+ of force off North edge by turn 8.\n\n"
            "**Defender Minor Victory**: Exit 50-74% of force off North edge.\n\n"
            "**Attacker Victory**: Prevent defender escape (defender exits <50%).\n\n"
            "**Draw**: Defender escapes but suffers 50%+ casualties."
        )

        deployment_map = self._generate_deployment_map(
            "Rearguard Action",
            table_size,
            "South 12\" (Pursuing)",
            "3 Successive Positions (S/C/N)",
            3
        )

        return RandomScenario(
            number=12,
            name="REARGUARD ACTION",
            scenario_type=ScenarioType.ATTACK_DEFENCE,
            battle_size=battle_size,
            table_size=table_size,
            situation_report=(
                "The main force is withdrawing and your rearguard must buy them time. Enemy forces "
                "are pursuing aggressively. Your mission: establish successive delay positions, "
                "inflict casualties, slow the pursuit, and extract your forces intact. Every hour "
                "of delay is a success."
            ),
            tactical_context=(
                "This is one of the most difficult missions: fighting while retreating. The rearguard "
                "must trade space for time without being decisively engaged. Position, delay, inflict "
                "casualties, disengage, fall back, repeat. The pursuer must press hard before the "
                "rearguard can organize the next position."
            ),
            terrain_features=terrain,
            terrain_notes="Mix of terrain providing successive defensive positions",
            weather=weather,
            victory_conditions=victory,
            deployment_steps=deployment_steps,
            deployment_zones=deployment_zones,
            objectives=objectives,
            attacker_points=int(attacker_points * 1.2),  # Attacker has advantage in pursuit
            defender_points=defender_points,
            reinforcements=reinforcements,
            special_rules=special_rules,
            deployment_map=deployment_map,
            year=year,
            location_type="Open Desert" if year == "1942" else "Tunisia",
            recommended_nations=["british", "german", "italian", "american"]
        )


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="BattleGroup Random Scenario Generator (North Africa)"
    )
    parser.add_argument(
        '--scenario',
        type=str,
        required=True,
        choices=[
            "desert_patrol_clash", "oasis_counter_attack", "desert_flanking",
            "wadi_crossing", "escarpment_defense", "pass_assault",
            "convoy_ambush", "airfield_assault", "fortified_box",
            "coastal_road", "desert_breakthrough", "rearguard"
        ],
        help='Scenario type to generate'
    )
    parser.add_argument('--year', type=str, default="1942", choices=["1942", "1943"])
    parser.add_argument('--size', type=str, default="company",
                       choices=["squad", "company", "battalion"])
    parser.add_argument('--points-attacker', type=int, default=750)
    parser.add_argument('--points-defender', type=int, default=750)
    parser.add_argument('--output', type=str, default='output/scenarios')

    args = parser.parse_args()

    # Map size string to enum
    size_map = {
        "squad": BattleSize.SQUAD_PLATOON,
        "company": BattleSize.COMPANY,
        "battalion": BattleSize.BATTALION
    }

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate scenario
    generator = RandomScenarioGenerator()
    scenario = generator.generate_scenario(
        scenario_name=args.scenario,
        battle_size=size_map[args.size],
        year=args.year,
        attacker_points=args.points_attacker,
        defender_points=args.points_defender
    )

    print(f"[SUCCESS] Generated scenario: {scenario.name}")
    print(f"   Type: {scenario.scenario_type.value}")
    print(f"   Battle Size: {scenario.battle_size.value}")
    print(f"   Table Size: {scenario.table_size.value}")
    print(f"   Year: {scenario.year}")
    print()

    # Export to markdown (2-page format)
    scenario_filename = f"{args.scenario}_{args.year}_{args.size}.md"
    markdown_path = output_dir / scenario_filename
    markdown_content = generator._format_markdown_2_page(scenario)
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    print(f"[MARKDOWN] Saved to: {markdown_path}")

    # Also export to JSON for programmatic use
    json_filename = f"{args.scenario}_{args.year}_{args.size}.json"
    json_path = output_dir / json_filename
    import json
    scenario_dict = {
        'number': scenario.number,
        'name': scenario.name,
        'scenario_type': scenario.scenario_type.value,
        'battle_size': scenario.battle_size.value,
        'table_size': scenario.table_size.value,
        'year': scenario.year,
        'location_type': scenario.location_type,
        'recommended_nations': scenario.recommended_nations,
        'situation_report': scenario.situation_report,
        'tactical_context': scenario.tactical_context,
        'terrain_features': [
            {
                'name': t.name,
                'size': t.size,
                'description': t.description,
                'special_rules': t.special_rules,
                'cover_type': t.cover_type,
                'movement_penalty': t.movement_penalty
            }
            for t in scenario.terrain_features
        ],
        'terrain_notes': scenario.terrain_notes,
        'weather': {
            'condition': scenario.weather.condition,
            'turn_starts': scenario.weather.turn_starts,
            'effects': scenario.weather.effects
        },
        'victory_conditions': scenario.victory_conditions,
        'deployment_steps': scenario.deployment_steps,
        'deployment_zones': [
            {
                'side': z.side,
                'location': z.location,
                'special_rules': z.special_rules
            }
            for z in scenario.deployment_zones
        ],
        'objectives': {
            'count': scenario.objectives.count,
            'first_objective': scenario.objectives.first_objective,
            'spacing_rules': scenario.objectives.spacing_rules,
            'placed_by': scenario.objectives.placed_by
        },
        'attacker_points': scenario.attacker_points,
        'defender_points': scenario.defender_points,
        'reinforcements': [
            {
                'side': r.side,
                'starting_turn': r.starting_turn,
                'dice_per_turn': r.dice_per_turn,
                'special_rules': r.special_rules
            }
            for r in scenario.reinforcements
        ],
        'special_rules': scenario.special_rules,
        'deployment_map': scenario.deployment_map
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(scenario_dict, f, indent=2, ensure_ascii=False)
    print(f"[JSON] Saved to: {json_path}")
    print()
    print("[COMPLETE] Scenario generation complete!")


if __name__ == '__main__':
    main()
