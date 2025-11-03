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
sys.path.insert(0, str(project_root / "scripts" / "battlegroup"))

# Import from generators
from historical_scenario_generator import (
    Scenario, SituationReport, BattlefieldSetup, BattleDescription,
    Objectives, ForceRoster, Deployment, AlternativeForces, TerrainFeature,
    ScenarioType, TableSize, VictoryType
)
from phase6_unit_parser import Phase6UnitParser

# Import BattleGroup point system and organization templates
from generate_platoon_templates import TACTICAL_TEMPLATES
from generate_company_templates import COMPANY_SUPPORT
from generate_battlegroup_army_lists import BattleGroupPoints

# Import force composition validator
from force_composition_validator import validate_force_composition, print_validation_report

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

        # Use official BattleGroup Points system (consistent with army lists)
        self.bg_points = BattleGroupPoints()

        # Note: Old hardcoded lookup tables removed - now using BattleGroupPoints
        # which provides consistent values across scenarios and army lists

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
        units = []
        total_points = 0
        total_br = 0

        # Parse force description for units
        # Pattern: "1 squadron Matilda II (7-9 tanks)"
        # Pattern: "2 companies 4th Indian infantry (160-200 men)"
        # Pattern: "4x 88mm FlaK 18/36 (hull-down)"
        # Pattern: "1 battery 25-pdr (4 guns)"

        # Try to extract unit entries
        unit_entries = self._parse_force_description(force_description)

        for entry in unit_entries:
            unit_name, count, equipment_type, notes = entry

            # Get points and BR using BattleGroupPoints system
            # For infantry, we need to convert from soldier count to platoon count
            if equipment_type == "infantry":
                # Convert soldiers to platoons based on nation
                template = TACTICAL_TEMPLATES.get(nation)
                if template:
                    platoon_size = template.platoon_size
                    platoon_count = max(1, count // platoon_size)

                    # Recalculate for proper platoon organization
                    unit_points = self._get_points(equipment_type, platoon_count, nation)
                    unit_br = self._get_br(equipment_type, platoon_count)

                    # Update unit entry to show platoons
                    unit_dict = {
                        "name": f"{unit_name.replace('Company', 'Platoons')}",
                        "type": "infantry_platoon",
                        "count": platoon_count,
                        "experience": experience,
                        "points": unit_points,
                        "br": unit_br,
                        "notes": f"{platoon_count} platoons ({count} men total)"
                    }
                else:
                    # Fallback if template not found
                    unit_points = self._get_points(equipment_type, 1, nation) * count
                    unit_br = self._get_br(equipment_type, count)
                    unit_dict = {
                        "name": unit_name,
                        "type": equipment_type,
                        "count": count,
                        "experience": experience,
                        "points": unit_points,
                        "br": unit_br,
                        "notes": notes
                    }
            else:
                # For non-infantry (tanks, guns, etc.)
                unit_points = self._get_points(equipment_type, count, nation)
                unit_br = self._get_br(equipment_type, count)

                unit_dict = {
                    "name": unit_name,
                    "type": equipment_type,
                    "count": count,
                    "experience": experience,
                    "points": unit_points,
                    "br": unit_br,
                    "notes": notes
                }

            total_points += unit_points
            total_br += unit_br
            units.append(unit_dict)

        # If no units parsed, create placeholder
        if not units:
            units.append({
                "name": "Mixed Force",
                "type": "combined_arms",
                "count": 1,
                "experience": experience,
                "points": points_budget,
                "br": points_budget // 20,
                "notes": force_description[:100] + "..."
            })
            total_points = points_budget
            total_br = points_budget // 20

        roster = ForceRoster(
            nation=nation,
            name=f"{nation.upper()} FORCES",
            battle_rating=total_br,
            points_budget=points_budget,
            units=units
        )

        return roster

    def _parse_force_description(self, description: str) -> List[Tuple[str, int, str, str]]:
        """
        Parse force description to extract unit entries

        Returns:
            List of (unit_name, count, equipment_type, notes) tuples
        """
        print(f"\n[PARSING] Force description: {description[:150]}...")

        entries = []
        unparsed_parts = []

        # Clean up description - remove modifiers like "+ fortifications"
        description = re.sub(r'\s*\+\s*fortifications?\s*', '', description, flags=re.IGNORECASE)

        # Split by commas or semicolons
        parts = re.split(r'[,;]\s*', description)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            parsed = False

            # Try various patterns (order matters - most specific first!)

            # Pattern 1: "1 squadron Matilda II (7-9 tanks)" or "2 squadrons Matilda II (14-16 tanks)"
            match = re.search(r'(\d+)\s*squadrons?\s+([^(]+)\((\d+)-(\d+)\s+tanks?\)', part, re.IGNORECASE)
            if match:
                squadron_count = int(match.group(1))
                tank_name = match.group(2).strip()
                tank_min = int(match.group(3))
                tank_max = int(match.group(4))
                tank_count = (tank_min + tank_max) // 2  # Average

                equipment_type = self._identify_equipment_type(tank_name)
                entries.append((tank_name, tank_count, equipment_type, f"{squadron_count} squadron"))
                print(f"[PARSE OK] Pattern 1 (Squadron): {tank_count}x {tank_name}")
                parsed = True
                continue

            # Pattern 2: "2 companies 4th Indian infantry (160-200 men)" or "1 company Italian infantry (80-100 men)"
            match = re.search(r'(\d+)\s*compan(?:y|ies)\s+([^(]*?)infantry\s*\((\d+)-(\d+)\s+men\)', part, re.IGNORECASE)
            if match:
                company_count = int(match.group(1))
                descriptor = match.group(2).strip()  # e.g., "4th Indian", "Italian", etc.
                men_min = int(match.group(3))
                men_max = int(match.group(4))
                men_count = (men_min + men_max) // 2

                # Extract nationality/description
                nationality = self._extract_nationality(descriptor)
                unit_name = f"{nationality}Infantry Company" if nationality else "Infantry Company"
                notes = f"{company_count} companies, {men_count} men"

                entries.append((unit_name, men_count, "infantry", notes))
                print(f"[PARSE OK] Pattern 2 (Infantry Company): {men_count} men ({company_count} companies)")
                parsed = True
                continue

            # Pattern 3: "1 platoon infantry (25-30 men)" or "1 platoon German infantry reinforcement (30 men)"
            match = re.search(r'(\d+)\s*platoon(?:s)?\s+([^(]*?)infantry(?:\s+([^(]+?))?\s*\((\d+)(?:-(\d+))?\s+men\)', part, re.IGNORECASE)
            if match:
                platoon_count = int(match.group(1))
                descriptor = match.group(2).strip() if match.group(2) else ""
                modifier = match.group(3).strip() if match.group(3) else ""  # e.g., "reinforcement"
                men_min = int(match.group(4))
                men_max = int(match.group(5)) if match.group(5) else men_min  # Handle single number like (30 men)
                men_count = (men_min + men_max) // 2

                # Extract nationality and reinforcement status
                nationality = self._extract_nationality(descriptor + " " + modifier)
                is_reinforcement = "reinforcement" in modifier.lower()

                unit_name = f"{nationality}Infantry Platoon" if nationality else "Infantry Platoon"
                if is_reinforcement:
                    unit_name += " (Reinforcement)"

                notes = f"{platoon_count} platoon, {men_count} men"

                entries.append((unit_name, men_count, "infantry", notes))
                print(f"[PARSE OK] Pattern 3 (Infantry Platoon): {men_count} men ({platoon_count} platoon)")
                parsed = True
                continue

            # Pattern 4: "1 battery 25-pdr (4 guns)" or "1 section 25-pdr (2 guns)"
            match = re.search(r'(\d+)\s*(?:battery|section)\s+([^(]+)\((\d+)\s+guns?\)', part, re.IGNORECASE)
            if match:
                battery_count = int(match.group(1))
                gun_name = match.group(2).strip()
                gun_count = int(match.group(3))

                equipment_type = self._identify_equipment_type(gun_name)
                entries.append((gun_name, gun_count, equipment_type, f"{battery_count} battery/section"))
                print(f"[PARSE OK] Pattern 4 (Artillery): {gun_count}x {gun_name}")
                parsed = True
                continue

            # Pattern 5: "4x 88mm FlaK 18/36" or "3x Panzer III" (generic equipment with explicit 'x')
            match = re.search(r'(\d+)x\s+([^(]+?)(?:\(|$)', part)
            if match:
                count = int(match.group(1))
                equipment_name = match.group(2).strip()
                equipment_type = self._identify_equipment_type(equipment_name)

                notes = ""
                if '(' in part:
                    notes_match = re.search(r'\(([^)]+)\)', part)
                    if notes_match:
                        notes = notes_match.group(1)

                entries.append((equipment_name, count, equipment_type, notes))
                print(f"[PARSE OK] Pattern 5 (Generic Equipment): {count}x {equipment_name}")
                parsed = True
                continue

            # Pattern 6: "2 companies (20-25 Panzer III, 6-8 Panzer II)" - complex multi-tank companies
            match = re.search(r'(\d+)\s*compan(?:y|ies)\s*\(([^)]+)\)', part, re.IGNORECASE)
            if match:
                company_count = int(match.group(1))
                tank_list = match.group(2)

                # Parse comma-separated tank entries
                tank_entries = tank_list.split(',')
                for tank_entry in tank_entries:
                    tank_entry = tank_entry.strip()

                    # Try to extract "20-25 Panzer III" pattern
                    tank_match = re.search(r'(\d+)-(\d+)\s+([^,]+)', tank_entry)
                    if tank_match:
                        min_count = int(tank_match.group(1))
                        max_count = int(tank_match.group(2))
                        tank_name = tank_match.group(3).strip()
                        avg_count = (min_count + max_count) // 2

                        equipment_type = self._identify_equipment_type(tank_name)
                        entries.append((
                            tank_name,
                            avg_count,
                            equipment_type,
                            f"{company_count} companies"
                        ))

                # If we successfully parsed tanks from company description, continue
                if any(tank_match for tank_entry in tank_entries
                       if re.search(r'(\d+)-(\d+)\s+([^,]+)', tank_entry.strip())):
                    print(f"[PARSE OK] Pattern 6 (Complex Company): {len(tank_entries)} tank types")
                    parsed = True
                    continue

            # Track unparsed parts
            if not parsed:
                unparsed_parts.append(part)

        # Log unparsed parts if any
        if unparsed_parts:
            print(f"[WARNING] Failed to parse {len(unparsed_parts)} part(s):")
            for unparsed in unparsed_parts:
                print(f"  - {unparsed}")

        print(f"[PARSING] Successfully parsed {len(entries)} unit entries\n")

        return entries

    def _extract_nationality(self, text: str) -> str:
        """Extract nationality from text descriptor"""
        text_lower = text.lower()

        # Check for nationality keywords
        if "german" in text_lower or "panzergrenadier" in text_lower:
            return "German "
        elif "italian" in text_lower:
            return "Italian "
        elif "british" in text_lower or "indian" in text_lower or "australian" in text_lower or "new zealand" in text_lower or "south african" in text_lower:
            return "British "
        elif "french" in text_lower or "free french" in text_lower:
            return "French "
        elif "american" in text_lower or "us " in text_lower:
            return "American "
        else:
            return ""

    def _identify_equipment_type(self, name: str) -> str:
        """Identify equipment type from name"""
        name_lower = name.lower()

        # Tanks
        if "matilda" in name_lower:
            return "matilda"
        elif "crusader" in name_lower:
            return "crusader"
        elif "panzer iii" in name_lower or "panzer 3" in name_lower or "pz iii" in name_lower or "pzkpfw iii" in name_lower:
            return "panzer_iii"
        elif "panzer iv" in name_lower or "panzer 4" in name_lower or "pz iv" in name_lower or "pzkpfw iv" in name_lower:
            return "panzer_iv"
        elif "panzer ii" in name_lower or "panzer 2" in name_lower or "pz ii" in name_lower:
            return "panzer_ii"
        elif "m13/40" in name_lower or "m13" in name_lower:
            return "m13_40"
        elif "stuart" in name_lower or "m3" in name_lower:
            return "m3_stuart"
        elif "grant" in name_lower or "m3 medium" in name_lower:
            return "m3_grant"
        elif "a9" in name_lower:
            return "a9"
        elif "a10" in name_lower:
            return "a10"
        elif "a13" in name_lower:
            return "a13"

        # Artillery
        elif "25" in name_lower and ("pdr" in name_lower or "pounder" in name_lower):
            return "25pdr"
        elif "88" in name_lower and "mm" in name_lower:
            return "88mm"
        elif "pak 38" in name_lower or "pak38" in name_lower:
            return "pak_38"
        elif "2" in name_lower and ("pdr" in name_lower or "pounder" in name_lower):
            return "2pdr"
        elif "6" in name_lower and ("pdr" in name_lower or "pounder" in name_lower):
            return "6pdr"
        elif "bofors" in name_lower:
            return "bofors"

        # Infantry
        elif any(word in name_lower for word in ["infantry", "soldier", "men", "platoon"]):
            return "infantry"
        elif "engineer" in name_lower:
            return "engineer"

        # Fallback based on keywords
        elif any(word in name_lower for word in ["tank", "panzer"]):
            return "tank_medium"
        elif any(word in name_lower for word in ["gun", "pdr", "mm", "artillery"]):
            return "artillery"
        else:
            return "unknown"

    def _get_points(self, equipment_type: str, count: int = 1, nation: str = "british") -> int:
        """
        Get points value for equipment type using BattleGroupPoints system

        Args:
            equipment_type: Equipment type identifier
            count: Number of units (for platoons/sections)
            nation: Nation code for infantry/company calculations
        """
        # Map equipment types to BattleGroupPoints attributes
        if equipment_type == "matilda":
            return self.bg_points.matilda_ii * count
        elif equipment_type == "crusader":
            return self.bg_points.crusader_ii * count
        elif equipment_type == "panzer_iii":
            return self.bg_points.panzer_iii_short * count
        elif equipment_type == "panzer_iv":
            return self.bg_points.panzer_iv_short * count
        elif equipment_type == "panzer_ii":
            return 65 * count  # Estimate for Panzer II
        elif equipment_type == "m13_40":
            return self.bg_points.m13_40 * count
        elif equipment_type == "m3_stuart":
            return self.bg_points.m3_stuart * count
        elif equipment_type == "m3_grant":
            return self.bg_points.m3_grant * count
        elif equipment_type == "25pdr":
            return self.bg_points.artillery_25pdr * count
        elif equipment_type == "88mm":
            return 95 * count  # 88mm FlaK (estimate, not in BattleGroupPoints)
        elif equipment_type == "pak_38":
            return self.bg_points.pak38_5cm * count
        elif equipment_type == "2pdr":
            return self.bg_points.at_gun_2pdr * count
        elif equipment_type == "6pdr":
            return self.bg_points.at_gun_6pdr * count
        elif equipment_type == "infantry":
            # Use platoon-level points based on nation
            if nation == "british":
                return self.bg_points.platoon_british * count
            elif nation == "german":
                return self.bg_points.platoon_german * count
            elif nation == "italian":
                return self.bg_points.platoon_italian * count
            elif nation == "american":
                return self.bg_points.platoon_american * count
            else:
                return 160 * count  # Default to British
        else:
            return 50 * count  # Default fallback

    def _get_br(self, equipment_type: str, count: int = 1) -> int:
        """
        Get BR value for equipment type

        BR calculation:
        - Tanks: 1-3 BR per vehicle (heavy = 3, medium = 2, light = 1)
        - Infantry: 1 BR per platoon
        - Artillery: 0-1 BR per gun
        """
        if equipment_type in ["matilda"]:
            return 3 * count  # Heavy tank
        elif equipment_type in ["crusader", "panzer_iii", "panzer_iv", "m13_40"]:
            return 2 * count  # Medium tank
        elif equipment_type in ["panzer_ii", "m3_stuart", "a9", "a10", "a13"]:
            return 1 * count  # Light tank
        elif equipment_type in ["88mm"]:
            return 2 * count  # Powerful AT gun
        elif equipment_type in ["25pdr", "pak_38", "2pdr", "6pdr", "bofors"]:
            return 1 * count  # Artillery piece
        elif equipment_type == "infantry":
            return 1 * count  # Per platoon
        elif equipment_type == "engineer":
            return 1 * count  # Per platoon
        else:
            return max(1, count // 3)  # Default: 1 BR per 3 units


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
        output_dir: Optional[Path] = None,
        per_book_index: Optional[int] = None
    ) -> Scenario:
        """
        Generate a complete scenario

        Args:
            battle: Battle name (battleaxe, crusader, gazala, first_alamein)
            scenario_num: Global scenario number (1-45)
            output_dir: Optional output directory override
            per_book_index: Per-book scenario index (1-N for each battle), for filename

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

        # Build force rosters from research data
        attacker_force_desc = research.forces.get(attacker_side, "")
        defender_force_desc = research.forces.get(defender_side, "")

        # Map attacker/defender to nations from Phase 6 units
        # nation_quarter is like {"british": "1941q2", "german": "1941q2"}
        # attacker_side is like "British" or "Axis"

        # Infer nation from side name
        attacker_nation_guess = "british" if "british" in attacker_side.lower() else "german"
        defender_nation_guess = "german" if "german" in defender_side.lower() or "axis" in defender_side.lower() else "italian"

        # Get quarter from nation_quarter dict (or use first available)
        available_quarters = list(nation_quarter.items())
        attacker_quarter = nation_quarter.get(attacker_nation_guess, available_quarters[0][1] if available_quarters else "1941q2")
        defender_quarter = nation_quarter.get(defender_nation_guess, available_quarters[1][1] if len(available_quarters) > 1 else "1941q2")

        attacker_nation = attacker_side.lower()  # Use actual side name
        defender_nation = defender_side.lower()

        attacker_roster = self.roster_builder.build_roster(
            nation=attacker_nation,
            quarter=attacker_quarter,
            force_description=attacker_force_desc,
            points_budget=points_budget,
            experience="veteran"  # Most North Africa units were experienced
        )

        # Validate attacker force composition
        attacker_year = int(attacker_quarter.split('q')[0])  # Extract year from "1941q2"
        attacker_validation = validate_force_composition(
            units=attacker_roster.units,
            points_budget=points_budget,
            year=attacker_year,
            historical_description=attacker_force_desc
        )
        if not attacker_validation.is_valid or attacker_validation.warnings:
            print_validation_report(attacker_validation, f"{attacker_side} Forces")

        defender_roster = self.roster_builder.build_roster(
            nation=defender_nation,
            quarter=defender_quarter,
            force_description=defender_force_desc,
            points_budget=points_budget,
            experience="veteran"
        )

        # Validate defender force composition
        defender_year = int(defender_quarter.split('q')[0])  # Extract year from "1941q2"
        defender_validation = validate_force_composition(
            units=defender_roster.units,
            points_budget=points_budget,
            year=defender_year,
            historical_description=defender_force_desc
        )
        if not defender_validation.is_valid or defender_validation.warnings:
            print_validation_report(defender_validation, f"{defender_side} Forces")

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

        # Use per-book index for filename if provided, otherwise use global scenario_num
        file_index = per_book_index if per_book_index is not None else scenario_num
        output_file = output_dir / f"scenario_{file_index:02d}.md"
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

        # Generate scenarios using per-book numbering (1-N for each battle)
        for idx, research_data in enumerate(scenarios, 1):
            self.generate_scenario(battle, research_data.scenario_number, per_book_index=idx)

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
