#!/usr/bin/env python3
"""
BattleGroup Scenario Force Parser v2.0

Enhanced parser with comprehensive validation rules inspired by WargamingDataCleaner.
Fixes critical parsing failures found during scenario regeneration.

Author: North Africa TO&E Builder
Date: November 3, 2025
Version: 2.0.0
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# ============================================================================
# VALIDATION RULES - Strict patterns with no fuzzy matching
# ============================================================================

VALIDATION_RULES = {
    # ==== SQUADRONS ====
    'squadron_with_count': {
        'pattern': r'(\d+)\s*squadrons?\s+([^(]+?)\s*\((\d+)-(\d+)\s+tanks?\)',
        'examples': ['1 squadron Matilda II (7-9 tanks)', '2 squadrons Crusader (14-16 tanks)'],
        'description': 'Squadron with explicit tank count range'
    },
    'squadron_with_types': {
        'pattern': r'(\d+)\s*squadrons?\s+\((\d+)-(\d+)\s+tanks?:\s*([^)]+)\)',
        'examples': ['3 squadrons (30-35 tanks: Crusader, Honey Stuart)', '2 squadrons (20-25 tanks: Crusader I, A9/A10)'],
        'description': 'Squadron with mixed tank types listed'
    },
    'squadron_range': {
        'pattern': r'(\d+)-(\d+)\s*squadrons?\s+(?:tanks?\s+)?\((\d+)-(\d+)\s+([^)]+)\)',
        'examples': ['2-3 squadrons (24-30 tanks: Grant, Crusader)', '3-4 squadrons mixed tanks (35-45 tanks: Crusader, Honey Stuart)'],
        'description': 'Squadron with range count (2-3 squadrons) and tank types'
    },
    'squadron_simple_tanks': {
        'pattern': r'(\d+)\s*squadrons?\s+\((\d+)-(\d+)\s+([^)]+?)\s+tanks?\)',
        'examples': ['4 squadrons (40-45 Crusader tanks)', '2 squadrons (20-24 Valentine/Grant)'],
        'description': 'Squadron with tank range and type (tanks keyword)'
    },
    'squadron_no_detail': {
        'pattern': r'(\d+)\s*squadrons?\s+([^(,;]+?)(?:\s+tanks?)?(?=,|;|$)',
        'examples': ['1 squadron Valentine tanks', '2 squadrons tanks', '1 squadron armored cars'],
        'description': 'Squadron without parenthetical details (default 12 vehicles)'
    },
    'company_infantry': {
        'pattern': r'(\d+)\s*compan(?:y|ies)\s+([^(]*?)(?:infantry|motorized infantry)\s*\((\d+)-(\d+)\s+men\)',
        'examples': ['1 company Italian infantry (80-100 men)', '2 companies 4th Indian infantry (160-200 men)', '1 company motorized infantry (80-100 men)'],
        'description': 'Infantry company with manpower range'
    },
    'company_motorized_no_count': {
        'pattern': r'(\d+)\s*compan(?:y|ies)\s+motorized\s+infantry(?!\s*\()',
        'examples': ['1 company motorized infantry'],
        'description': 'Motorized infantry company without explicit manpower (default to 90 men/3 platoons)'
    },
    'company_tanks': {
        'pattern': r'(\d+)\s*compan(?:y|ies)\s+([^(]+?)\s*\((\d+)-(\d+)\s+tanks?\)',
        'examples': ['2 companies Panzer III (20-24 tanks)', '1 company M13/40 (10-12 tanks)'],
        'description': 'Tank company with vehicle count range'
    },
    'platoon_infantry': {
        'pattern': r'(\d+)\s*platoons?\s+([^(]*?)(?:infantry|Panzergrenadiers?|Bersaglieri)\s*(?:\(([^)]*?)\))?\s*\((\d+)(?:-(\d+))?\s+men\)',
        'examples': ['1 platoon infantry (25-30 men)', '2 platoons Panzergrenadiers (60-70 men)', '1 platoon German infantry reinforcement (30 men)'],
        'description': 'Infantry platoon with manpower'
    },
    'company_panzergrenadiers': {
        'pattern': r'(\d+)\s*compan(?:y|ies)\s+(Panzergrenadiers?)\s*\((\d+)-(\d+)\s+men\)',
        'examples': ['2 companies Panzergrenadiers (160-180 men)'],
        'description': 'Panzergrenadier companies with manpower'
    },
    'battalion_infantry': {
        'pattern': r'(\d+)\s*battalions?\s+([^(]+?)\s*\((\d+)-(\d+)\s+men\)',
        'examples': ['1 battalion Bersaglieri (300-350 men)', '2 battalions New Zealand infantry (600-700 men)'],
        'description': 'Infantry battalion with manpower range'
    },
    'battalion_no_count': {
        'pattern': r'(\d+)\s*battalions?\s+([\w\s]+?(?:infantry|Bersaglieri|Panzergrenadiers?|motorized))(?!\s*\()',
        'examples': ['1 battalion motorized infantry', '2 battalions infantry', '1 battalion King\'s Royal Rifles (motorized infantry)'],
        'description': 'Battalion without explicit men count (default 400 men/13 platoons)'
    },
    'battery_with_count': {
        'pattern': r'(\d+)\s*(?:battery|batteries|section)\s+([^(]+?)\s*\((\d+)\s+guns?\)',
        'examples': ['1 battery 25-pdr (4 guns)', '2 batteries 47mm AT guns (12 guns)'],
        'description': 'Artillery battery/section with gun count'
    },
    'battery_no_count': {
        'pattern': r'(\d+)\s*(?:battery|batteries)\s+([^,;]+?)(?=,|;|$)',
        'examples': ['1 battery 25-pdr', '2 batteries artillery'],
        'description': 'Artillery battery without explicit count (default to 4 guns per battery)'
    },
    'equipment_explicit': {
        'pattern': r'(\d+)x\s+([^(,;]+?)(?:\s*\([^)]*\))?(?=,|;|$)',
        'examples': ['2x 47mm Cannone da 47/32 AT guns', '4x 88mm FlaK 18/36', '2x Breda M37 heavy MG'],
        'description': 'Explicit equipment count with x notation'
    },
    'platoon_tanks': {
        'pattern': r'(\d+)\s*platoons?\s+([^(]+?)\s*\((\d+)-(\d+)\s+tanks?\)',
        'examples': ['1 platoon Panzer III (4-5 tanks)'],
        'description': 'Tank platoon with vehicle count'
    },
    'company_tanks_no_paren': {
        'pattern': r'(\d+)\s*compan(?:y|ies)\s+([A-Z][\w/]+?)\s+(\d+)-(\d+)(?:\s+tanks?)?',
        'examples': ['1 company Panzer III/IV 10-12 tanks', '2 companies M13/40 16-18'],
        'description': 'Tank company without parentheses'
    },
    'company_infantry_no_count': {
        'pattern': r'(\d+)\s*compan(?:y|ies)\s+(German|Italian|British|[\w\s]+?)\s+infantry(?!\s*\()',
        'examples': ['1 company German infantry', '1 company Italian infantry'],
        'description': 'Infantry company without men count (default 90 men/3 platoons)'
    },
    'informal_tank_range_named': {
        'pattern': r'(\d+)-(\d+)\s+([A-Z][\w\s/]+?)\s*(?:tanks?)?(?=,|;|$|\))',
        'examples': ['4-5 Matilda II tanks', '6-8 Panzer II', '2-3 Crusader'],
        'description': 'Informal tank range with specific tank name'
    },
    'informal_tank_range_generic': {
        'pattern': r'(\d+)-(\d+)\s+tanks?(?=,|;|$|\))',
        'examples': ['2-3 tanks', '6-8 tanks'],
        'description': 'Informal tank range without specific type (generic tanks)'
    },
    'informal_gun_range': {
        'pattern': r'(\d+)-(\d+)\s+(AT\s+guns?)',
        'examples': ['2-3 AT guns'],
        'description': 'Informal AT gun range'
    },
    'platoon_infantry_no_count': {
        'pattern': r'(\d+)\s*platoons?\s+([\w\s]*?)infantry(?!\s*\()',
        'examples': ['2 platoons infantry', '1 platoon German infantry'],
        'description': 'Infantry platoon without men count (default 30 men)'
    },
    'platoon_special': {
        'pattern': r'(\d+)\s*platoons?\s+(motorcycle troops|motorized infantry)(?!\s*\()',
        'examples': ['1 platoon motorcycle troops', '1 platoon motorized infantry'],
        'description': 'Special platoon without men count (default 30 men)'
    },
    'armored_cars': {
        'pattern': r'(\d+)\s*squadrons?\s+armored\s+cars',
        'examples': ['1 squadron armored cars'],
        'description': 'Armored car squadron (default 12 vehicles)'
    },
    'carriers': {
        'pattern': r'(\d+(?:-\d+)?)\s+(?:Bren\s+)?carriers?',
        'examples': ['3 Bren carriers', '2-3 carriers'],
        'description': 'Carrier vehicles (Bren carriers)'
    }
}


# ============================================================================
# NAMING STANDARDIZATION - Canonical forms for equipment
# ============================================================================

EQUIPMENT_NAMING_STANDARDS = {
    'tanks': {
        'panzer_iii': ['Panzer III', 'Pz III', 'PzKpfw III', 'Pz.Kpfw. III'],
        'panzer_iv': ['Panzer IV', 'Pz IV', 'PzKpfw IV', 'Pz.Kpfw. IV'],
        'matilda': ['Matilda II', 'Matilda Mk II', 'Infantry Tank Mk II'],
        'crusader': ['Crusader', 'Crusader I', 'Cruiser Mk VI'],
        'm13_40': ['M13/40', 'M.13/40', 'Carro Armato M13/40'],
    },
    'artillery': {
        '25pdr': ['25-pdr', '25-pounder', '25 pdr', 'QF 25-pdr'],
        '47mm_italian': ['47mm Cannone da 47/32', '47/32', 'Cannone da 47/32'],
        '88mm': ['88mm FlaK 18', '88mm FlaK 36', '8.8cm FlaK 18/36'],
        'pak_38': ['50mm PaK 38', '50mm PAK 38', '5cm PaK 38'],
        'pak_40': ['75mm PAK 40', '75mm PaK 40', '7.5cm PaK 40'],
    }
}


# ============================================================================
# INFANTRY ORGANIZATION STANDARDS
# ============================================================================

INFANTRY_STANDARDS = {
    'men_per_platoon': {
        'german': 30,
        'british': 30,
        'italian': 30,
        'american': 40,
        'default': 30
    },
    'platoons_per_company': {
        'default': 3
    },
    'companies_per_battalion': {
        'default': 3
    }
}


@dataclass
class ParsedUnit:
    """Structured representation of a parsed unit"""
    unit_name: str
    count: int
    unit_type: str  # infantry_platoon, tank, artillery, support
    equipment_type: str  # From _identify_equipment_type
    notes: str
    raw_description: str
    confidence: float  # 0.0-1.0 confidence in parse


@dataclass
class ValidationIssue:
    """Represents a validation issue found during parsing"""
    severity: str  # 'error', 'warning', 'info'
    line: int
    field: str
    issue: str
    suggestion: Optional[str] = None


class ScenarioForceParserV2:
    """Enhanced force parser with comprehensive validation"""

    def __init__(self):
        self.issues: List[ValidationIssue] = []
        self.parsed_units: List[ParsedUnit] = []

    def parse_force_description(self, description: str, nation: str = "unknown") -> List[ParsedUnit]:
        """
        Parse force description using strict validation rules

        Args:
            description: Force description string from scenario research
            nation: Nation for infantry standards (german, british, italian, american)

        Returns:
            List of ParsedUnit objects
        """
        self.issues = []
        self.parsed_units = []

        print(f"\n[PARSER V2] Parsing: {description[:150]}...")

        # Clean description
        cleaned = self._preprocess_description(description)

        # Split into parts
        parts = re.split(r'[,;]\s*', cleaned)

        for part_idx, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue

            parsed = self._parse_single_part(part, part_idx, nation)
            if parsed:
                self.parsed_units.append(parsed)
            else:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    line=part_idx,
                    field='force_description',
                    issue=f"Failed to parse: {part}",
                    suggestion="Check against VALIDATION_RULES patterns"
                ))

        # Print results
        print(f"[PARSER V2] Parsed {len(self.parsed_units)} units")
        if self.issues:
            print(f"[PARSER V2] {len(self.issues)} parsing issues (see validation report)")

        return self.parsed_units

    def _preprocess_description(self, description: str) -> str:
        """Clean and standardize description text"""
        cleaned = description

        # Strip complex prefixes (Mixed force, Kampfgruppe, etc.) but keep the content
        prefix_patterns = [
            r'^\s*(Mixed|Pursuit|Rearguard|Screening|Defensive|Assault|Exploitation|Converging|Trapped|Encirclement|Breakout|Final|Lead elements?|Probing|Defensive?|Withdrawing|Patrol|Garrison)\s+(force|forces?|elements?|units?|line|attack|screen|garrison)\s*\(',
            r'^\s*Kampfgruppe\s*\(',
        ]
        for pattern in prefix_patterns:
            match = re.match(pattern, cleaned, re.IGNORECASE)
            if match:
                # Remove prefix including the opening paren, then re-add it
                cleaned = cleaned[match.end():]
                break

        # Remove trailing contextual modifiers
        trailing_modifiers = [
            r',?\s*(withdrawing|limited ammunition|hasty defenses|fortifications?|defensive positions?|hull-down|concealed|minefields?|artillery support|prepared assault|coordinated attack|unprepared for attack|attacking from \w+|covering [\w\s]+|reduced strength|various support units|desperate defense|integrated defense|advancing rapidly|conducting withdrawal|attempting to [\w\s]+|testing [\w\s]+|supply trucks?|heavy artillery|Stuka [\w\s]+|engineer support|supply column|artillery barrage support|artillery preparation)$'
        ]
        for pattern in trailing_modifiers:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Remove explicit "+fortifications" style modifiers
        cleaned = re.sub(r'\s*\+\s*fortifications?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*\+\s*defensive\s+positions?\s*', '', cleaned, flags=re.IGNORECASE)

        # Standardize spacing
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()

    def _parse_single_part(self, part: str, part_idx: int, nation: str) -> Optional[ParsedUnit]:
        """Parse a single force description component using validation rules"""

        # Try each validation rule pattern
        for rule_name, rule_def in VALIDATION_RULES.items():
            pattern = rule_def['pattern']
            match = re.search(pattern, part, re.IGNORECASE)

            if match:
                return self._extract_unit_from_match(match, rule_name, part, nation)

        # No pattern matched
        return None

    def _extract_unit_from_match(self, match, rule_name: str, raw: str, nation: str) -> ParsedUnit:
        """Extract ParsedUnit from regex match based on rule type"""

        if rule_name == 'squadron_with_count':
            squadron_count = int(match.group(1))
            tank_name = match.group(2).strip()
            tank_min = int(match.group(3))
            tank_max = int(match.group(4))
            tank_count = (tank_min + tank_max) // 2

            equipment_type = self._identify_equipment_type(tank_name)

            return ParsedUnit(
                unit_name=tank_name,
                count=tank_count,
                unit_type='tank',
                equipment_type=equipment_type,
                notes=f"{squadron_count} squadron",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'squadron_with_types':
            squadron_count = int(match.group(1))
            tank_min = int(match.group(2))
            tank_max = int(match.group(3))
            tank_types = match.group(4)
            tank_count = (tank_min + tank_max) // 2

            # For mixed squadrons, use first type as primary
            primary_type = tank_types.split(',')[0].strip()

            equipment_type = self._identify_equipment_type(primary_type)

            return ParsedUnit(
                unit_name=f"Mixed Squadron ({tank_types})",
                count=tank_count,
                unit_type='tank',
                equipment_type=equipment_type,
                notes=f"{squadron_count} squadron, mixed types",
                raw_description=raw,
                confidence=0.9  # Slightly lower confidence for mixed types
            )

        elif rule_name == 'company_infantry':
            company_count = int(match.group(1))
            descriptor = match.group(2).strip()
            men_min = int(match.group(3))
            men_max = int(match.group(4))
            men_count = (men_min + men_max) // 2

            # Convert to platoons using standards
            men_per_platoon = INFANTRY_STANDARDS['men_per_platoon'].get(nation, 30)
            platoon_count = men_count // men_per_platoon

            nationality = self._extract_nationality(descriptor)
            unit_name = f"{nationality}Infantry Company"

            return ParsedUnit(
                unit_name=unit_name,
                count=platoon_count,  # Return as platoon count for validator
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{company_count} companies, {men_count} men",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'company_tanks':
            company_count = int(match.group(1))
            tank_name = match.group(2).strip()
            tank_min = int(match.group(3))
            tank_max = int(match.group(4))
            tank_count = (tank_min + tank_max) // 2

            equipment_type = self._identify_equipment_type(tank_name)

            return ParsedUnit(
                unit_name=tank_name,
                count=tank_count,
                unit_type='tank',
                equipment_type=equipment_type,
                notes=f"{company_count} companies",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'platoon_infantry':
            platoon_count = int(match.group(1))
            descriptor = match.group(2).strip() if match.group(2) else ""
            modifier = match.group(3).strip() if match.group(3) else ""
            men_min = int(match.group(4))
            men_max = int(match.group(5)) if match.group(5) else men_min
            men_count = (men_min + men_max) // 2

            nationality = self._extract_nationality(descriptor + " " + modifier)
            is_reinforcement = "reinforcement" in modifier.lower()

            unit_name = f"{nationality}Infantry Platoon"
            if is_reinforcement:
                unit_name += " (Reinforcement)"

            return ParsedUnit(
                unit_name=unit_name,
                count=platoon_count,  # Platoon count, not men count!
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{platoon_count} platoon, {men_count} men",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'battalion_infantry':
            battalion_count = int(match.group(1))
            descriptor = match.group(2).strip()
            men_min = int(match.group(3))
            men_max = int(match.group(4))
            men_count = (men_min + men_max) // 2

            # Convert battalion to platoons
            men_per_platoon = INFANTRY_STANDARDS['men_per_platoon'].get(nation, 30)
            platoon_count = men_count // men_per_platoon

            nationality = self._extract_nationality(descriptor)

            return ParsedUnit(
                unit_name=f"{nationality}Infantry Battalion",
                count=platoon_count,  # Convert to platoon count
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{battalion_count} battalion, {men_count} men (~{platoon_count} platoons)",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'battery_with_count':
            battery_count = int(match.group(1))
            gun_name = match.group(2).strip()
            gun_count = int(match.group(3))

            equipment_type = self._identify_equipment_type(gun_name)

            return ParsedUnit(
                unit_name=gun_name,
                count=gun_count,
                unit_type='artillery',
                equipment_type=equipment_type,
                notes=f"{battery_count} battery/section",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'battery_no_count':
            battery_count = int(match.group(1))
            gun_name = match.group(2).strip()

            # Default: 4 guns per battery
            gun_count = battery_count * 4

            equipment_type = self._identify_equipment_type(gun_name)

            return ParsedUnit(
                unit_name=gun_name,
                count=gun_count,
                unit_type='artillery',
                equipment_type=equipment_type,
                notes=f"{battery_count} battery (4 guns per battery assumed)",
                raw_description=raw,
                confidence=0.8  # Lower confidence when assuming count
            )

        elif rule_name == 'equipment_explicit':
            count = int(match.group(1))
            equipment_name = match.group(2).strip()

            equipment_type = self._identify_equipment_type(equipment_name)

            return ParsedUnit(
                unit_name=equipment_name,
                count=count,
                unit_type='support',
                equipment_type=equipment_type,
                notes="",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'company_motorized_no_count':
            company_count = int(match.group(1))

            # Default: 90 men per company = 3 platoons
            platoon_count = company_count * 3
            men_count = company_count * 90

            return ParsedUnit(
                unit_name="Motorized Infantry Company",
                count=platoon_count,
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{company_count} companies, ~{men_count} men (assumed)",
                raw_description=raw,
                confidence=0.7  # Lower confidence when assuming counts
            )

        elif rule_name == 'company_panzergrenadiers':
            company_count = int(match.group(1))
            unit_type = match.group(2)
            men_min = int(match.group(3))
            men_max = int(match.group(4))
            men_count = (men_min + men_max) // 2

            # Convert to platoons
            men_per_platoon = INFANTRY_STANDARDS['men_per_platoon'].get('german', 30)
            platoon_count = men_count // men_per_platoon

            return ParsedUnit(
                unit_name=f"German Panzergrenadier Company",
                count=platoon_count,
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{company_count} companies, {men_count} men",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'platoon_tanks':
            platoon_count = int(match.group(1))
            tank_name = match.group(2).strip()
            tank_min = int(match.group(3))
            tank_max = int(match.group(4))
            tank_count = (tank_min + tank_max) // 2

            equipment_type = self._identify_equipment_type(tank_name)

            return ParsedUnit(
                unit_name=tank_name,
                count=tank_count,
                unit_type='tank',
                equipment_type=equipment_type,
                notes=f"{platoon_count} platoon",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'squadron_range':
            squadron_min = int(match.group(1))
            squadron_max = int(match.group(2))
            tank_min = int(match.group(3))
            tank_max = int(match.group(4))
            tank_types = match.group(5).strip()

            squadron_count = (squadron_min + squadron_max) // 2
            tank_count = (tank_min + tank_max) // 2

            primary_type = tank_types.split(',')[0].strip()
            equipment_type = self._identify_equipment_type(primary_type)

            return ParsedUnit(
                unit_name=f"Mixed Squadron ({tank_types})",
                count=tank_count,
                unit_type='tank',
                equipment_type=equipment_type,
                notes=f"{squadron_count} squadrons, mixed types",
                raw_description=raw,
                confidence=0.9
            )

        elif rule_name == 'squadron_simple_tanks':
            squadron_count = int(match.group(1))
            tank_min = int(match.group(2))
            tank_max = int(match.group(3))
            tank_types = match.group(4).strip()

            tank_count = (tank_min + tank_max) // 2
            equipment_type = self._identify_equipment_type(tank_types)

            return ParsedUnit(
                unit_name=tank_types,
                count=tank_count,
                unit_type='tank',
                equipment_type=equipment_type,
                notes=f"{squadron_count} squadron",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'squadron_no_detail':
            squadron_count = int(match.group(1))
            vehicle_type = match.group(2).strip()

            # Default 12 vehicles per squadron
            vehicle_count = squadron_count * 12

            equipment_type = self._identify_equipment_type(vehicle_type)

            return ParsedUnit(
                unit_name=vehicle_type,
                count=vehicle_count,
                unit_type='tank' if 'tank' in vehicle_type.lower() else 'support',
                equipment_type=equipment_type,
                notes=f"{squadron_count} squadron (~12/squadron assumed)",
                raw_description=raw,
                confidence=0.7
            )

        elif rule_name == 'battalion_no_count':
            battalion_count = int(match.group(1))
            descriptor = match.group(2).strip()

            # Default: 400 men per battalion = ~13 platoons
            men_count = battalion_count * 400
            men_per_platoon = INFANTRY_STANDARDS['men_per_platoon'].get(nation, 30)
            platoon_count = men_count // men_per_platoon

            nationality = self._extract_nationality(descriptor)

            return ParsedUnit(
                unit_name=f"{nationality}Infantry Battalion",
                count=platoon_count,
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{battalion_count} battalion, ~{men_count} men (assumed, ~{platoon_count} platoons)",
                raw_description=raw,
                confidence=0.7
            )

        elif rule_name == 'company_tanks_no_paren':
            company_count = int(match.group(1))
            tank_name = match.group(2).strip()
            tank_min = int(match.group(3))
            tank_max = int(match.group(4))
            tank_count = (tank_min + tank_max) // 2

            equipment_type = self._identify_equipment_type(tank_name)

            return ParsedUnit(
                unit_name=tank_name,
                count=tank_count,
                unit_type='tank',
                equipment_type=equipment_type,
                notes=f"{company_count} companies",
                raw_description=raw,
                confidence=1.0
            )

        elif rule_name == 'company_infantry_no_count':
            company_count = int(match.group(1))
            descriptor = match.group(2).strip()

            # Default: 90 men per company = 3 platoons
            men_count = company_count * 90
            men_per_platoon = INFANTRY_STANDARDS['men_per_platoon'].get(nation, 30)
            platoon_count = men_count // men_per_platoon

            nationality = self._extract_nationality(descriptor)

            return ParsedUnit(
                unit_name=f"{nationality}Infantry Company",
                count=platoon_count,
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{company_count} companies, ~{men_count} men (assumed)",
                raw_description=raw,
                confidence=0.7
            )

        elif rule_name == 'informal_tank_range_named':
            tank_min = int(match.group(1))
            tank_max = int(match.group(2))
            tank_name = match.group(3).strip()
            tank_count = (tank_min + tank_max) // 2

            equipment_type = self._identify_equipment_type(tank_name)

            return ParsedUnit(
                unit_name=tank_name,
                count=tank_count,
                unit_type='tank',
                equipment_type=equipment_type,
                notes="Informal range",
                raw_description=raw,
                confidence=0.8
            )

        elif rule_name == 'informal_tank_range_generic':
            tank_min = int(match.group(1))
            tank_max = int(match.group(2))
            tank_count = (tank_min + tank_max) // 2

            return ParsedUnit(
                unit_name="Tanks (mixed types)",
                count=tank_count,
                unit_type='tank',
                equipment_type='tank',
                notes="Informal range, type unspecified",
                raw_description=raw,
                confidence=0.6  # Lower confidence for generic tanks
            )

        elif rule_name == 'informal_gun_range':
            gun_min = int(match.group(1))
            gun_max = int(match.group(2))
            gun_type = match.group(3).strip()
            gun_count = (gun_min + gun_max) // 2

            return ParsedUnit(
                unit_name=gun_type,
                count=gun_count,
                unit_type='artillery',
                equipment_type='at_gun',
                notes="Informal range",
                raw_description=raw,
                confidence=0.8
            )

        elif rule_name == 'platoon_infantry_no_count':
            platoon_count = int(match.group(1))
            descriptor = match.group(2).strip()

            nationality = self._extract_nationality(descriptor)

            return ParsedUnit(
                unit_name=f"{nationality}Infantry Platoon",
                count=platoon_count,
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{platoon_count} platoon, ~30 men/platoon (assumed)",
                raw_description=raw,
                confidence=0.7
            )

        elif rule_name == 'platoon_special':
            platoon_count = int(match.group(1))
            unit_type_desc = match.group(2).strip()

            # Default 30 men per platoon = 1 platoon
            return ParsedUnit(
                unit_name=unit_type_desc.title(),
                count=platoon_count,
                unit_type='infantry_platoon',
                equipment_type='infantry',
                notes=f"{platoon_count} platoon, ~30 men (assumed)",
                raw_description=raw,
                confidence=0.7
            )

        elif rule_name == 'armored_cars':
            squadron_count = int(match.group(1))
            vehicle_count = squadron_count * 12  # Default 12 per squadron

            return ParsedUnit(
                unit_name="Armored Cars",
                count=vehicle_count,
                unit_type='support',
                equipment_type='support_weapon',
                notes=f"{squadron_count} squadron",
                raw_description=raw,
                confidence=0.7
            )

        elif rule_name == 'carriers':
            carrier_str = match.group(1)

            # Handle range or single number
            if '-' in carrier_str:
                parts = carrier_str.split('-')
                carrier_count = (int(parts[0]) + int(parts[1])) // 2
            else:
                carrier_count = int(carrier_str)

            return ParsedUnit(
                unit_name="Bren Carriers",
                count=carrier_count,
                unit_type='support',
                equipment_type='support_weapon',
                notes="Carrier section",
                raw_description=raw,
                confidence=0.9
            )

        # Shouldn't reach here if pattern matched
        return None

    def _identify_equipment_type(self, name: str) -> str:
        """Categorize equipment by type for points calculation"""
        name_lower = name.lower()

        # Tanks
        if any(word in name_lower for word in ['panzer', 'tank', 'matilda', 'crusader', 'stuart', 'm13', 'valentine', 'grant', 'sherman']):
            return 'tank'

        # AT guns
        if any(word in name_lower for word in ['pak', 'at gun', '47mm', '50mm', '75mm', '2-pdr', '6-pdr', 'cannone']):
            return 'at_gun'

        # Artillery
        if any(word in name_lower for word in ['artillery', 'pdr', 'mm', 'howitzer', 'lefh', 'sfh']):
            return 'artillery'

        # AA guns
        if any(word in name_lower for word in ['flak', 'aa', 'bofors']):
            return 'aa_gun'

        # Infantry weapons
        if any(word in name_lower for word in ['mg', 'machine gun', 'mortar', 'breda']):
            return 'support_weapon'

        return 'unknown'

    def _extract_nationality(self, text: str) -> str:
        """Extract nationality prefix from text"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['german', 'panzergrenadier']):
            return "German "
        elif "italian" in text_lower or "bersaglieri" in text_lower:
            return "Italian "
        elif any(word in text_lower for word in ['british', 'indian', 'australian', 'new zealand', 'south african']):
            return "British "
        elif "french" in text_lower or "free french" in text_lower:
            return "French "
        elif "american" in text_lower or "us " in text_lower:
            return "American "

        return ""

    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("=" * 80)
        report.append("SCENARIO FORCE PARSER V2 - VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")

        report.append(f"Parsed Units: {len(self.parsed_units)}")
        report.append(f"Issues Found: {len(self.issues)}")
        report.append("")

        if self.parsed_units:
            report.append("SUCCESSFULLY PARSED UNITS:")
            for idx, unit in enumerate(self.parsed_units, 1):
                report.append(f"{idx}. {unit.unit_name} ({unit.count}x) - Type: {unit.unit_type}")
                report.append(f"   Confidence: {unit.confidence*100:.0f}% | Notes: {unit.notes}")
            report.append("")

        if self.issues:
            errors = [i for i in self.issues if i.severity == 'error']
            warnings = [i for i in self.issues if i.severity == 'warning']

            if errors:
                report.append(f"ERRORS ({len(errors)}):")
                for issue in errors:
                    report.append(f"  Line {issue.line}: {issue.issue}")
                    if issue.suggestion:
                        report.append(f"    -> Suggestion: {issue.suggestion}")
                report.append("")

            if warnings:
                report.append(f"WARNINGS ({len(warnings)}):")
                for issue in warnings:
                    report.append(f"  Line {issue.line}: {issue.issue}")
                    if issue.suggestion:
                        report.append(f"    -> Suggestion: {issue.suggestion}")
                report.append("")

        report.append("=" * 80)
        return "\n".join(report)


# ============================================================================
# CLI Interface for Testing
# ============================================================================

def main():
    """Test the parser with example force descriptions"""
    parser = ScenarioForceParserV2()

    test_cases = [
        ("1 squadron Matilda II (7-9 tanks), 1 platoon infantry (25-30 men), 1 section 25-pdr (2 guns)", "british"),
        ("3 squadrons (30-35 tanks: Crusader, Honey Stuart), 1 company motorized infantry, 1 battery 25-pdr", "british"),
        ("2 companies Panzer III (20-24 tanks), 2 companies Panzergrenadiers (160-180 men), 1 battery 105mm artillery (4 guns)", "german"),
        ("1 company Italian infantry (80-100 men), 2x 47mm Cannone da 47/32 AT guns, 2x Breda M37 heavy MG", "italian"),
        ("1 battalion Bersaglieri (300-350 men), 1 battery 47mm AT guns (4-6 guns)", "italian"),
    ]

    for description, nation in test_cases:
        print("\n" + "="*80)
        print(f"TEST: {description}")
        print(f"Nation: {nation}")
        print("="*80)

        units = parser.parse_force_description(description, nation)
        print(parser.generate_validation_report())


if __name__ == "__main__":
    main()
