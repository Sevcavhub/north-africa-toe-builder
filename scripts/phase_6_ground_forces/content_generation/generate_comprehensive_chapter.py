#!/usr/bin/env python3
"""
Hybrid Chapter Template Generator

Generates comprehensive MDBook chapters from Phase 6 unit JSON files.
Auto-populates equipment/organization sections from data.
Creates structure for manual historical narrative sections.

Usage:
    python generate_comprehensive_chapter.py <unit_json_file>
    python generate_comprehensive_chapter.py --all  # Process all units
    python generate_comprehensive_chapter.py --stub-only  # Only expand stub chapters
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Paths
UNITS_DIR = PROJECT_ROOT / "data" / "output" / "units"
CHAPTERS_DIR = PROJECT_ROOT / "data" / "output" / "chapters"
DATABASE_PATH = PROJECT_ROOT / "database" / "master_database.db"


def load_unit_json(filepath: Path) -> Dict:
    """Load and parse unit JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_number(num: int) -> str:
    """Format number with comma separators."""
    return f"{num:,}"


def get_quarter_display(quarter: str) -> str:
    """Convert quarter code to display format (1941q3 -> 1941-Q3)."""
    if 'q' in quarter.lower():
        parts = quarter.lower().split('q')
        return f"{parts[0]}-Q{parts[1]}"
    return quarter


def get_echelon_title(echelon: str) -> str:
    """Convert echelon to title case."""
    return echelon.replace('_', ' ').title()


def get_nation_display(nation: str) -> str:
    """Convert nation code to display name."""
    nation_map = {
        'british': 'British',
        'german': 'German',
        'italian': 'Italian',
        'american': 'American',
        'french': 'French'
    }
    return nation_map.get(nation.lower(), nation.title())


def generate_chapter_title(unit_data: Dict) -> str:
    """Generate chapter title from unit data."""
    designation = unit_data.get('unit_designation', 'Unknown Unit')

    # Clean up designation if needed
    if 'division' in designation.lower() and 'divisione' not in designation.lower():
        # Already has 'Division' in name
        return designation
    elif unit_data.get('organization_level') == 'division':
        return f"{designation} Division"
    else:
        return designation


def generate_overview_section(unit_data: Dict) -> str:
    """Generate Overview section (requires manual enhancement)."""
    designation = unit_data.get('unit_designation', 'Unknown Unit')
    nation = get_nation_display(unit_data.get('nation', 'unknown'))
    quarter = unit_data.get('quarter', 'unknown')
    quarter_display = get_quarter_display(quarter)
    unit_type = unit_data.get('unit_type', 'Unknown')
    total_personnel = unit_data.get('total_personnel', 0)
    echelon = unit_data.get('organization_level', 'unknown')
    parent = unit_data.get('parent_formation', 'Unknown')

    overview = f"""## 1. Overview

**[MANUAL: Add 2-3 paragraphs of historical context about the {designation}]**

**[MANUAL: Describe the unit's role during {quarter_display}, formation history, and strategic importance]**

**[MANUAL: Add operational context - what major operations/battles occurred this quarter]**

**Key Statistics ({quarter_display}):**
- Total Strength: {format_number(total_personnel)} personnel
- Unit Type: {unit_type}
- Organization Level: {get_echelon_title(echelon)}
- Parent Formation: {parent}
"""

    # Add commander if available
    commander_name = unit_data.get('command', {}).get('commander', {}).get('name', 'Unknown')
    commander_rank = unit_data.get('command', {}).get('commander', {}).get('rank', 'Unknown')
    if commander_name != 'Unknown':
        overview += f"- Commander: {commander_rank} {commander_name}\n"

    # Add HQ location if available
    hq_location = unit_data.get('command', {}).get('headquarters_location', '')
    if hq_location:
        overview += f"- Headquarters Location: {hq_location}\n"

    # Add key equipment stats
    tanks_total = unit_data.get('tanks', {}).get('total', {}).get('count', 0)
    artillery_total = unit_data.get('artillery_total', 0)
    vehicles_total = unit_data.get('ground_vehicles_total', 0)

    if tanks_total > 0:
        overview += f"- Tanks: {tanks_total}\n"
    if artillery_total > 0:
        overview += f"- Artillery: {artillery_total} guns\n"
    if vehicles_total > 0:
        overview += f"- Motor Vehicles: {format_number(vehicles_total)}\n"

    return overview


def generate_command_section(unit_data: Dict) -> str:
    """Generate Command Structure section."""
    command_data = unit_data.get('command', {})
    commander = command_data.get('commander', {})
    chief_of_staff = command_data.get('chief_of_staff', {})
    hq_location = command_data.get('headquarters_location', 'Unknown')
    staff_strength = command_data.get('staff_strength', {})

    commander_name = commander.get('name', 'Unknown')
    commander_rank = commander.get('rank', 'Unknown')
    appointment_date = commander.get('appointment_date', 'unknown')
    previous_service = commander.get('previous_service', 'unknown')

    section = f"""## 2. Command Structure

### Division Commander

"""

    if commander_name == 'Unknown':
        section += f"""The division commander during this period is not identified in available source documents. The position would have been held by an officer of **{commander_rank}** rank.

**[MANUAL: Add commander biography if name can be identified through additional research]**
"""
    else:
        section += f"""**{commander_rank} {commander_name}**"""
        if appointment_date != 'unknown':
            section += f" assumed command on {appointment_date}"
        section += ".\n\n"

        if previous_service != 'unknown':
            section += f"Previous service: {previous_service}\n\n"

        section += "**[MANUAL: Add 1-2 paragraphs about commander's background, command style, and performance]**\n"

    # Division Staff
    section += f"""
### Division Staff

The division headquarters staff comprised approximately {staff_strength.get('officers', 0) + staff_strength.get('ncos', 0) + staff_strength.get('enlisted', 0)} personnel:
"""

    if staff_strength.get('officers'):
        section += f"- **Officers:** {staff_strength['officers']} (operations, intelligence, logistics, signals)\n"
    if staff_strength.get('ncos'):
        section += f"- **NCOs:** {staff_strength['ncos']} (section chiefs, administrative staff)\n"
    if staff_strength.get('enlisted'):
        section += f"- **Enlisted:** {staff_strength['enlisted']} (clerks, drivers, guards, support)\n"

    # Chief of Staff
    cos_name = chief_of_staff.get('name', 'Unknown')
    cos_rank = chief_of_staff.get('rank', 'Unknown')

    section += f"""
### Chief of Staff

"""
    if cos_name == 'Unknown':
        section += f"The **Chief of Staff** position was typically held by a {cos_rank} who coordinated all divisional operations.\n"
    else:
        section += f"**{cos_rank} {cos_name}** served as Chief of Staff, coordinating all divisional operations.\n"

    # Headquarters Location
    section += f"""
### Headquarters Location

Division headquarters was established at: {hq_location}

**[MANUAL: Add details about headquarters mobility, facilities, and operational context]**
"""

    return section


def generate_personnel_section(unit_data: Dict) -> str:
    """Generate Personnel Strength section."""
    total = unit_data.get('total_personnel', 0)
    officers = unit_data.get('officers', 0)
    ncos = unit_data.get('ncos', 0)
    enlisted = unit_data.get('enlisted', 0)

    officers_pct = (officers / total * 100) if total > 0 else 0
    ncos_pct = (ncos / total * 100) if total > 0 else 0
    enlisted_pct = (enlisted / total * 100) if total > 0 else 0

    section = f"""## 3. Personnel Strength

### Total Strength: {format_number(total)} Personnel

**[MANUAL: Add 1-2 paragraphs about overall strength, comparing to establishment, explaining any understrength/overstrength]**

### Officer Corps: {format_number(officers)} Officers ({officers_pct:.1f}% of total)

The division's officer corps included:
- Division staff and headquarters officers
- Regiment and battalion commanders
- Company and platoon leaders
- Technical specialists

**[MANUAL: Add details about officer quality, training, and leadership capabilities]**

### Non-Commissioned Officers: {format_number(ncos)} NCOs ({ncos_pct:.1f}% of total)

NCOs provided critical small unit leadership:
- Squad and section leaders
- Weapon crew chiefs
- Technical specialists
- Administrative and supply NCOs

**[MANUAL: Add details about NCO experience and role]**

### Enlisted Personnel: {format_number(enlisted)} ({enlisted_pct:.1f}% of total)

The bulk of the division consisted of enlisted soldiers:
- Infantry riflemen
- Machine gun and weapon crews
- Artillery crews
- Drivers and mechanics
- Engineers and pioneers
- Supply and administrative personnel

### Personnel Quality

**[MANUAL: Add 2-3 paragraphs about:]**
- Combat experience level (veteran vs. newly-arrived)
- Morale status
- Training emphasis
- Replacement situation
- Known strengths/weaknesses
"""

    return section


def generate_organization_section(unit_data: Dict) -> str:
    """Generate Organization section with subordinate units."""
    subordinate_units = unit_data.get('subordinate_units', [])

    section = f"""## 4. Organization

**[MANUAL: Add 1-2 paragraphs describing overall organizational structure and doctrine]**

### Primary Subordinate Units

"""

    for idx, unit in enumerate(subordinate_units, 1):
        designation = unit.get('unit_designation', 'Unknown Unit')
        unit_type = unit.get('unit_type', 'Unknown')
        strength = unit.get('strength', 0)
        commander = unit.get('commander', 'Unknown')

        section += f"""**{idx}. {designation}**
- Type: {unit_type}
- Strength: {format_number(strength)} personnel
"""

        if commander != 'Unknown':
            section += f"- Commander: {commander}\n"

        # Add composition if available
        composition = unit.get('composition', '')
        if composition:
            if isinstance(composition, list):
                section += f"- Composition:\n"
                for comp in composition:
                    section += f"  - {comp}\n"
            else:
                section += f"- Composition: {composition}\n"

        # Add components if available
        components = unit.get('components', [])
        if components:
            section += "- Components:\n"
            for comp in components:
                section += f"  - {comp}\n"

        # Add notes if available
        notes = unit.get('notes', '')
        if notes:
            section += f"- Note: {notes}\n"

        section += "\n"

    if not subordinate_units:
        section += "**[MANUAL: List subordinate units with type, strength, commander, and composition]**\n"

    section += """
### Organizational Assessment

**[MANUAL: Add assessment of organizational strengths, gaps, and combat effectiveness]**
"""

    return section


def generate_weapons_section(unit_data: Dict) -> str:
    """Generate Infantry Weapons section."""
    top_3 = unit_data.get('top_3_infantry_weapons', {})

    section = f"""## 5. Infantry Weapons

**[MANUAL: Add introductory paragraph about unit's infantry weapons doctrine and supply]**

"""

    if top_3:
        for key in ['1', '2', '3']:
            weapon_data = top_3.get(key, {})
            if weapon_data:
                weapon = weapon_data.get('weapon', 'Unknown')
                count = weapon_data.get('count', 0)
                weapon_type = weapon_data.get('type', 'unknown')

                section += f"""### {weapon}
- **Count:** {format_number(count)}
- **Type:** {weapon_type.replace('_', ' ').title()}

**[MANUAL: Add specifications:]**
- Caliber
- Action type
- Magazine/feed system
- Effective range
- Rate of fire
- Weight
- Muzzle velocity

**[MANUAL: Add 1-2 paragraphs about weapon's performance, reliability, and tactical employment]**

"""
    else:
        section += "**[MANUAL: Add rifle, machine gun, and other infantry weapons with specifications and counts]**\n"

    return section


def generate_vehicles_section(unit_data: Dict) -> str:
    """Generate Vehicles and Transport section."""
    trucks = unit_data.get('trucks', {})
    motorcycles = unit_data.get('motorcycles', {})
    armored_cars = unit_data.get('armored_cars', {})
    halftracks = unit_data.get('halftracks', {})
    support_vehicles = unit_data.get('support_vehicles', {})

    total_vehicles = unit_data.get('ground_vehicles_total', 0)

    section = f"""## 6. Motor Vehicles and Transport

### Total Motor Vehicles: {format_number(total_vehicles)}

**[MANUAL: Add paragraph about unit's motorization level and mobility capabilities]**

"""

    # Trucks
    truck_total = trucks.get('total', 0)
    if truck_total > 0:
        section += f"""### Trucks: {format_number(truck_total)} Total

"""
        truck_variants = trucks.get('variants', {})
        for truck_name, truck_data in truck_variants.items():
            if isinstance(truck_data, dict):
                count = truck_data.get('count', 0)
                capacity = truck_data.get('capacity', 'unknown')
                section += f"""#### {truck_name}
- **Count:** {format_number(count)}
- **Capacity:** {capacity}

**[MANUAL: Add specifications and usage]**

"""

    # Motorcycles
    motorcycle_total = motorcycles.get('total', 0)
    if motorcycle_total > 0:
        section += f"""### Motorcycles: {format_number(motorcycle_total)} Total

"""
        moto_variants = motorcycles.get('variants', {})
        for moto_name, moto_data in moto_variants.items():
            if isinstance(moto_data, dict):
                count = moto_data.get('count', 0)
                section += f"""#### {moto_name}
- **Count:** {format_number(count)}

**[MANUAL: Add specifications and usage]**

"""

    # Armored Cars
    if armored_cars.get('total', {}).get('count', 0) > 0:
        section += f"""### Armored Cars: {armored_cars['total']['count']} Total

**[MANUAL: Add armored car variants with specifications and tactical employment]**

"""

    # Support Vehicles
    support_total = support_vehicles.get('total', 0)
    if support_total > 0:
        section += f"""### Support Vehicles: {format_number(support_total)} Total

"""
        support_variants = support_vehicles.get('variants', {})
        for vehicle_name, vehicle_data in support_variants.items():
            if isinstance(vehicle_data, dict):
                count = vehicle_data.get('count', 0)
                vehicle_type = vehicle_data.get('type', 'unknown')
                section += f"""#### {vehicle_name}
- **Count:** {format_number(count)}
- **Type:** {vehicle_type.replace('_', ' ').title()}

"""

    section += """
### Transport Challenges

**[MANUAL: Add section about desert operating challenges, maintenance, fuel consumption, etc.]**
"""

    return section


def generate_artillery_section(unit_data: Dict) -> str:
    """Generate Artillery section."""
    artillery_total = unit_data.get('artillery_total', 0)
    field_artillery = unit_data.get('field_artillery', {})
    anti_tank = unit_data.get('anti_tank', {}) or unit_data.get('anti_tank_artillery', {})
    anti_aircraft = unit_data.get('anti_aircraft', {}) or unit_data.get('anti_aircraft_artillery', {})
    mortars = unit_data.get('mortars', {})

    section = f"""## 7. Artillery

### Total Artillery: {artillery_total} Guns

**[MANUAL: Add paragraph about artillery organization and doctrine]**

"""

    # Field Artillery
    if field_artillery.get('total', 0) > 0:
        section += f"""### Field Artillery: {field_artillery['total']} Guns

"""
        field_variants = field_artillery.get('variants', {})
        for gun_name, gun_data in field_variants.items():
            if isinstance(gun_data, dict):
                count = gun_data.get('count', 0)
                caliber = gun_data.get('caliber', 'unknown')
                section += f"""#### {gun_name}
- **Count:** {count}
- **Caliber:** {caliber}

**[MANUAL: Add specifications:]**
- Range
- Shell weight
- Rate of fire
- Muzzle velocity
- Weight
- Crew size

**[MANUAL: Add tactical employment paragraph]**

"""

    # Anti-Tank
    if anti_tank.get('total', 0) > 0:
        section += f"""### Anti-Tank Artillery: {anti_tank['total']} Guns

"""
        at_variants = anti_tank.get('variants', {})
        for gun_name, gun_data in at_variants.items():
            if isinstance(gun_data, dict):
                count = gun_data.get('count', 0)
                caliber = gun_data.get('caliber', 'unknown')
                section += f"""#### {gun_name}
- **Count:** {count}
- **Caliber:** {caliber}

**[MANUAL: Add specifications and anti-armor effectiveness]**

"""

    # Anti-Aircraft
    if anti_aircraft.get('total', 0) > 0:
        section += f"""### Anti-Aircraft Artillery: {anti_aircraft['total']} Guns

"""
        aa_variants = anti_aircraft.get('variants', {})
        for gun_name, gun_data in aa_variants.items():
            if isinstance(gun_data, dict):
                count = gun_data.get('count', 0)
                caliber = gun_data.get('caliber', 'unknown')
                section += f"""#### {gun_name}
- **Count:** {count}
- **Caliber:** {caliber}

**[MANUAL: Add specifications and air defense employment]**

"""

    # Mortars
    if mortars.get('total', {}).get('count', 0) > 0:
        section += f"""### Mortars: {mortars['total']['count']} Total

**[MANUAL: Add mortar types, specifications, and employment]**

"""

    return section


def generate_supply_section(unit_data: Dict) -> str:
    """Generate Supply and Logistics section."""
    supply_data = unit_data.get('supply_logistics', {})

    fuel = supply_data.get('fuel_supply', '')
    ammo = supply_data.get('ammunition_supply', '')
    water = supply_data.get('water_supply', '')
    op_radius = supply_data.get('operational_radius', '') or supply_data.get('operational_radius_km', 0)
    supply_status = supply_data.get('supply_status', '')

    # Additional fields
    fuel_reserves = supply_data.get('fuel_reserves_days', 0)
    ammo_reserves = supply_data.get('ammunition_days', 0)
    water_liters = supply_data.get('water_liters_per_day', 0)

    section = f"""## 8. Supply and Logistics

### Supply Status

{supply_status if supply_status else '**[MANUAL: Add overall supply status assessment]**'}

### Fuel Supply

"""

    if fuel_reserves > 0:
        section += f"**Fuel Reserves:** {fuel_reserves} days\n\n"

    section += f"""{fuel if fuel else '**[MANUAL: Add fuel supply details, daily consumption, sources, constraints]**'}

### Ammunition Supply

"""

    if ammo_reserves > 0:
        section += f"**Ammunition Reserves:** {ammo_reserves} days\n\n"

    section += f"""{ammo if ammo else '**[MANUAL: Add ammunition supply details, types, resupply, shortages]**'}

### Water Supply

"""

    if water_liters > 0:
        section += f"**Daily Requirement:** {water_liters} liters per day\n\n"

    section += f"""{water if water else '**[MANUAL: Add water supply details, transport, rationing, sources]**'}

### Operational Radius

"""

    if isinstance(op_radius, (int, float)) and op_radius > 0:
        section += f"**Estimated:** {op_radius} km from supply dumps\n\n"
    elif op_radius:
        section += f"{op_radius}\n\n"
    else:
        section += "**[MANUAL: Add operational radius estimate with limiting factors]**\n\n"

    section += """
### Supply Chain Vulnerabilities

**[MANUAL: Add section about supply chain risks, interdiction, priorities, and challenges]**
"""

    return section


def generate_environment_section(unit_data: Dict) -> str:
    """Generate Weather and Environment section."""
    weather_data = unit_data.get('weather_environment', {})
    quarter = unit_data.get('quarter', 'unknown')

    terrain = weather_data.get('terrain_type', '')
    temp_range = weather_data.get('temperature_range', '') or weather_data.get('temperature_range_c', {})
    seasonal = weather_data.get('seasonal_impacts', '')
    challenges = weather_data.get('environmental_challenges', '')
    weather_notes = weather_data.get('weather_notes', '')

    # Additional fields
    season = weather_data.get('season_quarter', '')
    storm_freq = weather_data.get('storm_frequency_days', 0)
    daylight = weather_data.get('daylight_hours', 0)

    section = f"""## 9. Weather and Environment

### Climate ({get_quarter_display(quarter)})

"""

    if season:
        section += f"**Season:** {season}\n\n"

    if isinstance(temp_range, dict):
        temp_min = temp_range.get('min', 0)
        temp_max = temp_range.get('max', 0)
        if temp_min or temp_max:
            section += f"**Temperature Range:** {temp_min}-{temp_max}°C\n\n"
    elif temp_range:
        section += f"{temp_range}\n\n"

    if daylight > 0:
        section += f"**Daylight Hours:** {daylight} hours\n\n"

    if storm_freq > 0:
        section += f"**Storm Frequency:** Approximately {storm_freq} days per month\n\n"

    section += """**[MANUAL: Add detailed climate description for this quarter]**

### Terrain

"""

    section += f"""{terrain if terrain else '**[MANUAL: Add terrain description]**'}

### Weather Challenges

"""

    if seasonal:
        section += f"{seasonal}\n\n"

    section += """**[MANUAL: Add weather impact on operations]**

### Environmental Challenges

"""

    section += f"""{challenges if challenges else '**[MANUAL: Add environmental challenges - dust, heat, navigation, disease, etc.]**'}

"""

    if weather_notes:
        section += f"""### Weather Notes

{weather_notes}
"""

    return section


def generate_combat_history_section(unit_data: Dict) -> str:
    """Generate Combat History section."""
    combat_history = unit_data.get('combat_history', {})
    major_engagements = combat_history.get('major_engagements', [])
    effectiveness = combat_history.get('combat_effectiveness', '')

    section = f"""## 10. Combat History

### Formation and Deployment

**[MANUAL: Add 2-3 paragraphs about unit formation, when/where raised, deployment to theater]**

"""

    if major_engagements:
        section += "### Major Engagements\n\n"
        for engagement in major_engagements:
            name = engagement.get('name', 'Unknown Battle')
            date = engagement.get('date', 'unknown date')
            location = engagement.get('location', 'unknown location')
            role = engagement.get('role', '')
            outcome = engagement.get('outcome', '')

            section += f"""**{name}**
- **Date:** {date}
- **Location:** {location}
"""
            if role:
                section += f"- **Role:** {role}\n"
            if outcome:
                section += f"- **Outcome:** {outcome}\n"

            section += "\n**[MANUAL: Add 2-3 paragraphs describing the battle and unit's performance]**\n\n"
    else:
        section += """### Major Engagements

**[MANUAL: List and describe major battles, operations, and engagements]**

"""

    section += """### Combat Effectiveness Assessment

"""

    if effectiveness:
        section += f"{effectiveness}\n\n"

    section += """**[MANUAL: Add assessment of strengths, weaknesses, and overall combat performance]**
"""

    return section


def generate_tactical_doctrine_section(unit_data: Dict) -> str:
    """Generate Tactical Doctrine section."""
    tactical_data = unit_data.get('tactical_doctrine', {})

    role = tactical_data.get('role', '')
    capabilities = tactical_data.get('special_capabilities', [])
    innovations = tactical_data.get('tactical_innovations', [])
    issues = tactical_data.get('known_issues', [])
    adaptations = tactical_data.get('desert_adaptations', '')

    section = f"""## 11. Tactical Doctrine and Capabilities

### Doctrinal Role

"""

    if role:
        section += f"{role}\n\n"
    else:
        section += "**[MANUAL: Add 1-2 paragraphs about unit's doctrinal role and mission]**\n\n"

    if capabilities:
        section += "### Special Capabilities\n\n"
        for cap in capabilities:
            section += f"- {cap}\n"
        section += "\n"

    if innovations:
        section += "### Tactical Innovations\n\n"
        for innov in innovations:
            section += f"- {innov}\n"
        section += "\n"

    section += """### Combined Arms Integration

**[MANUAL: Add section about infantry-tank-artillery cooperation, air support, engineer support]**

"""

    if issues:
        section += "### Known Issues and Limitations\n\n"
        for issue in issues:
            section += f"- {issue}\n"
        section += "\n"

    if adaptations:
        section += f"""### Desert Adaptations

{adaptations}
"""

    return section


def generate_wargaming_section(unit_data: Dict) -> str:
    """Generate Wargaming Data section."""
    wargaming_data = unit_data.get('wargaming_data', {})

    scenarios = wargaming_data.get('scenario_suitability', [])
    morale = wargaming_data.get('morale_rating', 0)
    experience = wargaming_data.get('experience_level', 'Unknown')
    special_rules = wargaming_data.get('special_rules', [])
    engagements = wargaming_data.get('historical_engagements', [])

    section = f"""## 12. Wargaming and Scenario Data

### Morale and Experience

"""

    if morale > 0:
        section += f"**Morale Rating:** {morale}/10\n\n"

    if experience and experience != 'Unknown':
        section += f"**Experience Level:** {experience}\n\n"

    section += "**[MANUAL: Add paragraph explaining morale factors and experience level]**\n\n"

    if scenarios:
        section += "### Scenario Suitability\n\n"
        section += "This unit is well-suited for:\n"
        for scenario in scenarios:
            section += f"- {scenario}\n"
        section += "\n"

    if special_rules:
        section += "### Special Rules (Wargaming)\n\n"
        for rule in special_rules:
            section += f"- {rule}\n"
        section += "\n"

    if engagements:
        section += "### Historical Engagements (This Quarter)\n\n"
        for engagement in engagements:
            section += f"- {engagement}\n"
        section += "\n"

    section += """### Force Composition for Scenarios

**[MANUAL: Add typical force breakdowns for wargaming scenarios]**
"""

    return section


def generate_data_quality_section(unit_data: Dict) -> str:
    """Generate Data Quality and Sources section."""
    validation = unit_data.get('validation', {})

    sources = validation.get('source', [])
    if isinstance(sources, str):
        sources = [sources]

    confidence = validation.get('confidence', 0) or validation.get('source_confidence', 0)
    tier = validation.get('tier', 0) or validation.get('data_tier', 'unknown')
    status = validation.get('status', '') or validation.get('data_tier', '')
    last_updated = validation.get('last_updated', '') or validation.get('extraction_date', '')
    validated_by = validation.get('validated_by', '') or validation.get('extracted_by', '')

    gaps = validation.get('required_field_gaps', []) or validation.get('known_gaps', [])
    gap_doc = validation.get('gap_documentation', {})

    completeness = validation.get('data_completeness', 0)

    section = f"""## 13. Data Quality and Sources

### Source Documentation

"""

    if sources:
        section += "This TO&E is based on:\n\n"
        for source in sources:
            section += f"- {source}\n"
        section += "\n"

    if last_updated:
        section += f"**Last Updated:** {last_updated}\n\n"

    if validated_by:
        section += f"**Validated By:** {validated_by}\n\n"

    section += """### Confidence Assessment

"""

    if confidence > 0:
        section += f"**Overall Confidence:** {confidence}%"
        if tier:
            tier_str = f"Tier {tier}" if isinstance(tier, int) else tier
            section += f" ({tier_str})"
        section += "\n\n"

    if completeness > 0:
        section += f"**Data Completeness:** {completeness}%\n\n"

    section += """**[MANUAL: Add confidence breakdown by category - High/Medium/Low confidence areas]**

### Required Field Gaps

"""

    if gaps:
        section += "Missing information:\n"
        for gap in gaps:
            section += f"- {gap}\n"
        section += "\n"

    if gap_doc:
        section += "### Gap Documentation\n\n"
        for field, doc_data in gap_doc.items():
            if isinstance(doc_data, dict):
                section += f"**{field}:**\n"
                for key, value in doc_data.items():
                    section += f"- {key}: {value}\n"
                section += "\n"

    section += """### Data Tier Rationale

**[MANUAL: Add explanation of tier assignment and data quality factors]**
"""

    return section


def generate_historical_significance_section(unit_data: Dict) -> str:
    """Generate Historical Significance section."""
    return """## 14. Historical Significance

### Strategic Importance

**[MANUAL: Add 2-3 paragraphs about unit's strategic role in theater]**

### Operational Lessons

**[MANUAL: Add lessons learned from this unit's operations]**

### Legacy

**[MANUAL: Add information about unit's post-war legacy, memorials, historical assessment]**

---

*[MANUAL: Add concluding paragraph summarizing the unit's significance]*

**Generated from Phase 6 TO&E Data | [MANUAL: Add sources] | Confidence: [%] | Tier [#]**
"""


def generate_chapter(unit_data: Dict, output_path: Path) -> None:
    """Generate complete chapter markdown file."""

    nation = get_nation_display(unit_data.get('nation', 'unknown'))
    quarter = get_quarter_display(unit_data.get('quarter', 'unknown'))
    echelon = get_echelon_title(unit_data.get('organization_level', 'unknown'))
    title = generate_chapter_title(unit_data)

    # Build chapter content
    content = f"""# {title}

**Nation:** {nation}
**Quarter:** {quarter}
**Organization Level:** {echelon}

"""

    # Add all sections
    content += generate_overview_section(unit_data)
    content += "\n"
    content += generate_command_section(unit_data)
    content += "\n"
    content += generate_personnel_section(unit_data)
    content += "\n"
    content += generate_organization_section(unit_data)
    content += "\n"
    content += generate_weapons_section(unit_data)
    content += "\n"
    content += generate_vehicles_section(unit_data)
    content += "\n"
    content += generate_artillery_section(unit_data)
    content += "\n"
    content += generate_supply_section(unit_data)
    content += "\n"
    content += generate_environment_section(unit_data)
    content += "\n"
    content += generate_combat_history_section(unit_data)
    content += "\n"
    content += generate_tactical_doctrine_section(unit_data)
    content += "\n"
    content += generate_wargaming_section(unit_data)
    content += "\n"
    content += generate_data_quality_section(unit_data)
    content += "\n"
    content += generate_historical_significance_section(unit_data)

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] Generated: {output_path.name}")


def get_chapter_filename(unit_data: Dict) -> str:
    """Generate chapter filename from unit data."""
    nation = unit_data.get('nation', 'unknown').lower()
    quarter = unit_data.get('quarter', 'unknown').lower()
    designation = unit_data.get('unit_designation', 'unknown_unit')

    # Clean designation for filename
    designation_clean = designation.lower()
    designation_clean = designation_clean.replace(' ', '_')
    designation_clean = designation_clean.replace("'", '')
    designation_clean = designation_clean.replace('"', '')
    designation_clean = designation_clean.replace('/', '_')
    designation_clean = designation_clean.replace('(', '')
    designation_clean = designation_clean.replace(')', '')

    return f"chapter_{nation}_{quarter}_{designation_clean}.md"


def is_stub_chapter(chapter_path: Path) -> bool:
    """Check if an existing chapter is a stub (<50 lines)."""
    if not chapter_path.exists():
        return False

    with open(chapter_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    return len(lines) < 50


def process_unit_file(unit_file: Path, overwrite: bool = False, stub_only: bool = False) -> bool:
    """Process a single unit JSON file and generate chapter."""
    try:
        # Load unit data
        unit_data = load_unit_json(unit_file)

        # Generate output filename
        chapter_filename = get_chapter_filename(unit_data)
        output_path = CHAPTERS_DIR / chapter_filename

        # Check if file exists and if we should skip
        if output_path.exists():
            if stub_only:
                # Only process if it's a stub
                if not is_stub_chapter(output_path):
                    print(f"[SKIP] Not a stub: {chapter_filename}")
                    return False
            elif not overwrite:
                print(f"[SKIP] Exists: {chapter_filename}")
                return False

        # Generate chapter
        generate_chapter(unit_data, output_path)
        return True

    except Exception as e:
        print(f"[ERROR] Processing {unit_file.name}: {e}")
        return False


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate comprehensive MDBook chapters from unit JSONs')
    parser.add_argument('unit_file', nargs='?', help='Specific unit JSON file to process')
    parser.add_argument('--all', action='store_true', help='Process all unit JSON files')
    parser.add_argument('--stub-only', action='store_true', help='Only process stub chapters (<50 lines)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing chapters')
    parser.add_argument('--list-stubs', action='store_true', help='List all stub chapters')

    args = parser.parse_args()

    # Ensure chapters directory exists
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    # List stubs mode
    if args.list_stubs:
        print("Finding stub chapters (<50 lines)...\n")
        stubs = []
        for chapter_file in sorted(CHAPTERS_DIR.glob("chapter_*.md")):
            if is_stub_chapter(chapter_file):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    line_count = len(f.readlines())
                stubs.append((chapter_file.name, line_count))

        print(f"Found {len(stubs)} stub chapters:\n")
        for name, lines in stubs:
            print(f"  {name} ({lines} lines)")

        return

    # Process all units mode
    if args.all or args.stub_only:
        print(f"Processing {'stub ' if args.stub_only else ''}chapters from {UNITS_DIR}\n")

        unit_files = sorted(UNITS_DIR.glob("*_toe.json"))
        processed = 0
        skipped = 0

        for unit_file in unit_files:
            if process_unit_file(unit_file, args.overwrite, args.stub_only):
                processed += 1
            else:
                skipped += 1

        print(f"\n{'='*60}")
        print(f"Processed: {processed} chapters")
        print(f"Skipped: {skipped} chapters")
        print(f"Total: {len(unit_files)} unit files")

        return

    # Process single unit mode
    if args.unit_file:
        unit_path = Path(args.unit_file)
        if not unit_path.exists():
            # Try in units directory
            unit_path = UNITS_DIR / args.unit_file
            if not unit_path.exists():
                print(f"✗ Error: Unit file not found: {args.unit_file}")
                return

        process_unit_file(unit_path, args.overwrite, args.stub_only)
        return

    # No arguments - show usage
    parser.print_help()


if __name__ == '__main__':
    main()
