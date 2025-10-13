#!/usr/bin/env python3
"""
Regenerate MDBook chapters following MDBOOK_CHAPTER_TEMPLATE.md v2.0

This script reads unit JSON files and generates complete, compliant MDBook chapters
with all 16 required sections and detailed variant specifications.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Define the units to regenerate
UNITS = [
    "britain_1940q2_7th_armoured_division",
    "france_1942q2_1st_free_french_division",
    "france_1943q1_division_marche_maroc",
    "germany_1941q1_5_leichte_division",
    "germany_1941q2_deutsches_afrikakorps"
]

BASE_DIR = Path("D:/north-africa-toe-builder")
UNITS_DIR = BASE_DIR / "data/output/autonomous_1760133539236/units"
CHAPTERS_DIR = BASE_DIR / "data/output/autonomous_1760133539236/chapters"

def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_readiness(operational, total):
    """Calculate readiness percentage."""
    if total == 0:
        return "N/A"
    return f"{(operational / total * 100):.1f}%"

def generate_tank_section(data):
    """Generate the Armoured Strength section with variant details."""
    tanks = data.get("tanks", {})
    total = tanks.get("total", 0)
    operational = tanks.get("operational", total)

    section = f"""## Armoured Strength

### Summary

"""

    # Add narrative about tank strength
    if total == 0:
        section += "This formation operated without organic tank units.\n\n"
        return section

    section += f"The formation operated {total} tanks with {operational} operational ({calculate_readiness(operational, total)} readiness).\n\n"

    # Table
    section += """| Category | Total | Operational | Readiness |
|----------|-------|-------------|-----------|
"""
    section += f"| **All Tanks** | **{total}** | **{operational}** | **{calculate_readiness(operational, total)}** |\n"

    # Medium tanks
    medium = tanks.get("medium_tanks", {})
    if medium.get("total", 0) > 0:
        m_total = medium["total"]
        m_variants = medium.get("variants", {})
        m_operational = sum(v.get("operational", v.get("count", 0)) for v in m_variants.values())

        section += f"| **Medium Tanks** | **{m_total}** | **{m_operational}** | **{calculate_readiness(m_operational, m_total)}** |\n"

        for variant_name, variant_data in m_variants.items():
            v_count = variant_data.get("count", 0)
            v_op = variant_data.get("operational", v_count)
            section += f"| ↳ {variant_name} | {v_count} | {v_op} | {calculate_readiness(v_op, v_count)} |\n"

    # Light tanks
    light = tanks.get("light_tanks", {})
    if light.get("total", 0) > 0:
        l_total = light["total"]
        l_variants = light.get("variants", {})
        l_operational = sum(v.get("operational", v.get("count", 0)) for v in l_variants.values())

        section += f"| **Light Tanks** | **{l_total}** | **{l_operational}** | **{calculate_readiness(l_operational, l_total)}** |\n"

        for variant_name, variant_data in l_variants.items():
            v_count = variant_data.get("count", 0)
            v_op = variant_data.get("operational", v_count)
            section += f"| ↳ {variant_name} | {v_count} | {v_op} | {calculate_readiness(v_op, v_count)} |\n"

    # Heavy tanks
    heavy = tanks.get("heavy_tanks", {})
    h_total = heavy.get("total", 0)
    section += f"| **Heavy Tanks** | **{h_total}** | **0** | **N/A** |\n"

    section += "\n"

    # Now add variant detail sections
    section += "### Tank Variant Details\n\n"

    # Medium tank details
    if medium.get("total", 0) > 0:
        for variant_name, variant_data in medium.get("variants", {}).items():
            section += generate_tank_variant_detail(variant_name, variant_data)

    # Light tank details
    if light.get("total", 0) > 0:
        for variant_name, variant_data in light.get("variants", {}).items():
            section += generate_tank_variant_detail(variant_name, variant_data)

    return section

def generate_tank_variant_detail(name, data):
    """Generate detailed specifications for a tank variant."""
    count = data.get("count", 0)
    specs = data.get("specifications", {})

    detail = f"### {name} - {count} tanks\n\n"
    detail += "**Specifications**:\n"

    # Common fields
    if "gun" in specs or "gun" in data:
        gun = specs.get("gun", data.get("gun", "Unknown"))
        detail += f"- **Gun**: {gun}\n"

    if "armament" in specs or "armament" in data:
        arm = specs.get("armament", data.get("armament", "Unknown"))
        detail += f"- **Armament**: {arm}\n"

    if "armor_front" in specs or "armor_front_mm" in data:
        armor = specs.get("armor_front", data.get("armor_front_mm", "Unknown"))
        detail += f"- **Armor**: {armor}mm maximum\n"

    if "crew" in specs or "crew" in data:
        crew = specs.get("crew", data.get("crew", "Unknown"))
        detail += f"- **Crew**: {crew}\n"

    if "speed" in specs:
        speed = specs["speed"]
        detail += f"- **Speed**: {speed}\n"

    # Notes
    notes = data.get("notes", "")
    if notes:
        detail += f"\n**Combat Performance**: {notes}\n\n"
    else:
        detail += "\n**Combat Performance**: Standard variant for this period.\n\n"

    detail += "---\n\n"

    return detail

def generate_chapter(unit_name):
    """Generate a complete MDBook chapter for a unit."""
    print(f"Generating chapter for {unit_name}...")

    # Load JSON
    json_file = UNITS_DIR / f"{unit_name}_toe.json"
    data = load_json(json_file)

    # Extract key data
    designation = data.get("unit_designation", "Unknown Unit")
    nation = data.get("nation", "unknown").title()
    quarter = data.get("quarter", "Unknown")
    unit_type = data.get("unit_type", "")

    # Start building chapter
    chapter = f"# {designation}\n\n"
    chapter += f"**{nation} Forces • {quarter} • North Africa**\n\n"
    chapter += "---\n\n"

    # Section 2: Overview
    chapter += "## Division Overview\n\n"
    hist = data.get("historical_context", {})
    chapter += f"{hist.get('formation_history', 'Unit formation history not available.')}\n\n"
    chapter += f"{hist.get('operational_status', '')}\n\n"

    # Section 3: Command
    chapter += generate_command_section(data)

    # Section 4: Personnel
    chapter += generate_personnel_section(data)

    # Section 5: Armoured Strength
    chapter += generate_tank_section(data)

    # Section 6: Artillery
    chapter += generate_artillery_section(data)

    # Section 7: Armored Cars
    chapter += generate_armored_cars_section(data)

    # Section 8: Infantry Weapons
    chapter += generate_infantry_weapons_section(data)

    # Section 9: Transport & Vehicles
    chapter += generate_transport_section(data)

    # Section 10: Organizational Structure
    chapter += generate_org_structure_section(data)

    # Section 11: Supply Status
    chapter += generate_supply_section(data)

    # Section 12: Tactical Doctrine
    chapter += generate_doctrine_section(data)

    # Section 13: Critical Equipment Shortages
    chapter += generate_shortages_section(data)

    # Section 14: Historical Context
    chapter += generate_historical_section(data)

    # Section 15: Wargaming Data
    chapter += generate_wargaming_section(data)

    # Section 16: Data Quality & Known Gaps
    chapter += generate_data_quality_section(data)

    # Section 17: Conclusion
    chapter += generate_conclusion_section(data)

    # Write to file
    output_file = CHAPTERS_DIR / f"chapter_{unit_name}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(chapter)

    print(f"  + Chapter written to {output_file}")
    return output_file

def generate_command_section(data):
    """Generate command section."""
    cmd = data.get("command", {})
    commander = cmd.get("commander", {})

    section = "## Command\n\n"
    section += f"**Divisional Commander**: {commander.get('name', 'Unknown')}\n"
    section += f"**Rank**: {commander.get('rank', 'Unknown')}\n"
    section += f"**Appointed**: {commander.get('appointment_date', 'Unknown')}\n"

    if "previous_service" in commander:
        section += f"**Service**: {commander['previous_service']}\n"

    section += f"\n**Headquarters**: {cmd.get('headquarters_location', 'Unknown')}\n"
    section += f"**Parent Formation**: {data.get('parent_formation', 'Unknown')}\n\n"

    staff = cmd.get("staff_strength", {})
    total_staff = staff.get("officers", 0) + staff.get("ncos", 0) + staff.get("enlisted", 0)
    section += f"**Division Staff**: {total_staff} personnel\n"
    section += f"- Officers: {staff.get('officers', 0)}\n"
    section += f"- NCOs: {staff.get('ncos', 0)}\n"
    section += f"- Enlisted: {staff.get('enlisted', 0)}\n\n"

    return section

def generate_personnel_section(data):
    """Generate personnel strength section."""
    total = data.get("total_personnel", 0)
    officers = data.get("officers", 0)
    ncos = data.get("ncos", 0)
    enlisted = data.get("enlisted", 0)

    section = "## Personnel Strength\n\n"
    section += "| Category | Count | Percentage |\n"
    section += "|----------|-------|------------|\n"
    section += f"| **Total Personnel** | **{total:,}** | 100% |\n"

    if total > 0:
        section += f"| Officers | {officers:,} | {(officers/total*100):.1f}% |\n"
        section += f"| NCOs | {ncos:,} | {(ncos/total*100):.1f}% |\n"
        section += f"| Other Ranks | {enlisted:,} | {(enlisted/total*100):.1f}% |\n"

    section += "\n"
    return section

def generate_artillery_section(data):
    """Generate artillery section with variant details."""
    section = "## Artillery Strength\n\n"

    total_arty = data.get("artillery_total", 0)
    if total_arty == 0:
        section += "No organic artillery units assigned to this formation.\n\n"
        return section

    section += "| Type | Total | Operational | Caliber |\n"
    section += "|------|-------|-------------|---------||\n"

    # Field artillery
    field = data.get("field_artillery", {})
    if field.get("total", 0) > 0:
        section += f"| **Field Artillery** | **{field['total']}** | **{field['total']}** | - |\n"
        for var_name, var_data in field.get("variants", {}).items():
            count = var_data.get("count", 0)
            caliber = var_data.get("caliber", "Unknown")
            section += f"| ↳ {var_name} | {count} | {var_data.get('operational', count)} | {caliber} |\n"

    # Anti-tank
    at = data.get("anti_tank", {})
    if at.get("total", 0) > 0:
        section += f"| **Anti-Tank** | **{at['total']}** | **{at['total']}** | - |\n"
        for var_name, var_data in at.get("variants", {}).items():
            count = var_data.get("count", 0)
            caliber = var_data.get("caliber", "Unknown")
            section += f"| ↳ {var_name} | {count} | {var_data.get('operational', count)} | {caliber} |\n"

    # Anti-aircraft
    aa = data.get("anti_aircraft", {})
    if aa.get("total", 0) > 0:
        section += f"| **Anti-Aircraft** | **{aa['total']}** | **{aa['total']}** | - |\n"
        for var_name, var_data in aa.get("variants", {}).items():
            count = var_data.get("count", 0)
            caliber = var_data.get("caliber", "Unknown")
            section += f"| ↳ {var_name} | {count} | {var_data.get('operational', count)} | {caliber} |\n"

    section += f"| **Total Artillery** | **{total_arty}** | **{total_arty}** | - |\n\n"

    # Add variant details
    section += "### Artillery Variant Details\n\n"

    for var_name, var_data in field.get("variants", {}).items():
        section += generate_artillery_variant_detail(var_name, var_data)

    for var_name, var_data in at.get("variants", {}).items():
        section += generate_artillery_variant_detail(var_name, var_data)

    for var_name, var_data in aa.get("variants", {}).items():
        section += generate_artillery_variant_detail(var_name, var_data)

    return section

def generate_artillery_variant_detail(name, data):
    """Generate artillery variant detail section."""
    count = data.get("count", 0)

    detail = f"### {name} - {count} guns\n\n"
    detail += "**Specifications**:\n"
    detail += f"- **Caliber**: {data.get('caliber', 'Unknown')}\n"

    if "range_km" in data:
        detail += f"- **Range**: {data['range_km']} km\n"

    if "penetration_mm" in data:
        detail += f"- **Penetration**: {data['penetration_mm']}mm\n"

    if "rate_of_fire" in data:
        detail += f"- **Rate of Fire**: {data['rate_of_fire']}\n"

    notes = data.get("notes", "")
    if notes:
        detail += f"\n**Combat Performance**: {notes}\n\n"

    detail += "---\n\n"
    return detail

def generate_armored_cars_section(data):
    """Generate armored cars section."""
    section = "## Armoured Cars\n\n"

    ac = data.get("armored_cars", {})
    total = ac.get("total", 0)

    if total == 0:
        section += "No armoured cars assigned to this formation.\n\n"
        return section

    section += "| Type | Count | Role | Unit |\n"
    section += "|------|-------|------|------|\n"
    section += f"| **Total Armoured Cars** | **{total}** | - | - |\n"

    for var_name, var_data in ac.get("variants", {}).items():
        count = var_data.get("count", 0)
        role = var_data.get("role", "Reconnaissance")
        section += f"| ↳ {var_name} | {count} | {role} | - |\n"

    section += "\n### Armoured Car Variant Details\n\n"

    for var_name, var_data in ac.get("variants", {}).items():
        count = var_data.get("count", 0)
        detail = f"### {var_name} - {count} vehicles\n\n"
        detail += "**Armament**:\n"
        detail += f"- {var_data.get('armament', 'Unknown')}\n\n"

        specs = var_data.get("specifications", {})
        if "armor" in specs:
            detail += f"**Armor**: {specs['armor']}\n"
        if "crew" in specs:
            detail += f"**Crew**: {specs['crew']}\n"

        notes = var_data.get("notes", "")
        if notes:
            detail += f"\n**Combat Record**: {notes}\n\n"

        detail += "---\n\n"
        section += detail

    return section

def generate_infantry_weapons_section(data):
    """Generate infantry weapons section."""
    section = "## Infantry Weapons\n\n"

    top3 = data.get("top_3_infantry_weapons", {})
    if not top3:
        section += "Infantry weapons data not available.\n\n"
        return section

    section += "**Top 3 Infantry Weapons:**\n\n"

    for rank in ["1", "2", "3"]:
        if rank in top3:
            weapon_data = top3[rank]
            weapon = weapon_data.get("weapon", "Unknown")
            count = weapon_data.get("count", 0)
            wtype = weapon_data.get("type", "")

            section += f"### {rank}. {weapon} - {count:,} units\n\n"
            section += f"**Type**: {wtype}\n\n"

            notes = weapon_data.get("note", weapon_data.get("notes", ""))
            if notes:
                section += f"{notes}\n\n"

            section += "---\n\n"

    return section

def generate_transport_section(data):
    """Generate transport & vehicles section."""
    section = "## Transport & Vehicles\n\n"

    total_vehicles = data.get("ground_vehicles_total", 0)
    tanks_total = data.get("tanks", {}).get("total", 0)
    ac_total = data.get("armored_cars", {}).get("total", 0)

    # Calculate non-tank/non-AC vehicles
    transport_total = total_vehicles - tanks_total - ac_total

    if transport_total <= 0:
        section += "Transport vehicle data not available.\n\n"
        return section

    section += f"**Note**: This section covers trucks, motorcycles, and support vehicles. Tanks (Section 5) and Armoured Cars (Section 7) are documented separately.\n\n"

    section += "| Category | Count | Percentage |\n"
    section += "|----------|-------|------------|\n"
    section += f"| **Total Vehicles** | **{transport_total:,}** | 100% |\n"

    # Trucks
    trucks = data.get("trucks", {})
    if trucks.get("total", 0) > 0:
        t_total = trucks["total"]
        section += f"| **Trucks** | **{t_total}** | {(t_total/transport_total*100):.1f}% |\n"
        for var_name, var_data in trucks.get("variants", {}).items():
            count = var_data.get("count", 0)
            capacity = var_data.get("capacity", "")
            section += f"| ↳ {var_name} | {count} | {capacity} |\n"

    # Motorcycles
    motorcycles = data.get("motorcycles", {})
    if motorcycles.get("total", 0) > 0:
        m_total = motorcycles["total"]
        section += f"| **Motorcycles** | **{m_total}** | {(m_total/transport_total*100):.1f}% |\n"
        for var_name, var_data in motorcycles.get("variants", {}).items():
            count = var_data.get("count", 0)
            vtype = var_data.get("type", "")
            section += f"| ↳ {var_name} | {count} | {vtype} |\n"

    # Support vehicles
    support = data.get("support_vehicles", {})
    if support.get("total", 0) > 0:
        s_total = support["total"]
        section += f"| **Support Vehicles** | **{s_total}** | {(s_total/transport_total*100):.1f}% |\n"
        for var_name, var_data in support.get("variants", {}).items():
            count = var_data.get("count", 0)
            vtype = var_data.get("type", "")
            section += f"| ↳ {var_name} | {count} | {vtype} |\n"

    section += "\n"
    return section

def generate_org_structure_section(data):
    """Generate organizational structure section."""
    section = "## Organizational Structure\n\n"

    sub_units = data.get("subordinate_units", [])
    if not sub_units:
        section += "Subordinate unit details not available.\n\n"
        return section

    for i, unit in enumerate(sub_units, 1):
        section += f"### {i}. {unit.get('unit_designation', 'Unknown Unit')}\n\n"
        section += f"**Commander**: {unit.get('commander', 'Unknown')}\n"
        section += f"**Strength**: {unit.get('strength', 0):,} personnel\n"
        section += f"**Type**: {unit.get('unit_type', 'Unknown')}\n\n"

        if "composition" in unit:
            section += f"**Composition**: {unit['composition']}\n\n"

        if "note" in unit or "notes" in unit:
            section += f"**Notes**: {unit.get('note', unit.get('notes', ''))}\n\n"

    return section

def generate_supply_section(data):
    """Generate supply status section."""
    section = "## Supply Status\n\n"

    supply = data.get("supply_status", {})
    if not supply:
        section += "Supply status data not available.\n\n"
        return section

    section += "| Resource | Days of Supply | Status |\n"
    section += "|----------|----------------|--------|\n"
    section += f"| **Fuel** | {supply.get('fuel_days', 'Unknown')} | - |\n"
    section += f"| **Ammunition** | {supply.get('ammunition_days', 'Unknown')} | - |\n"
    section += f"| **Food** | {supply.get('food_days', 'Unknown')} | - |\n"
    section += f"| **Water** | {supply.get('water_liters_per_day', 'Unknown')} L/day | - |\n\n"

    if "operational_radius" in supply:
        section += f"**Operational Radius**: {supply['operational_radius']}\n"

    if "assessment" in supply:
        section += f"**Assessment**: {supply['assessment']}\n\n"

    if "notes" in supply:
        section += f"{supply['notes']}\n\n"

    return section

def generate_doctrine_section(data):
    """Generate tactical doctrine section."""
    section = "## Tactical Doctrine & Capabilities\n\n"

    doctrine = data.get("tactical_doctrine", {})
    if not doctrine:
        section += "Tactical doctrine data not available.\n\n"
        return section

    section += f"**Role**: {doctrine.get('role', 'Unknown')}\n\n"

    if "special_capabilities" in doctrine:
        section += "**Special Capabilities**:\n"
        for cap in doctrine["special_capabilities"]:
            section += f"- {cap}\n"
        section += "\n"

    if "tactical_innovations" in doctrine:
        section += "**Tactical Innovations**:\n"
        for innov in doctrine["tactical_innovations"]:
            section += f"- {innov}\n"
        section += "\n"

    if "known_issues" in doctrine:
        section += "**Known Issues**:\n"
        for issue in doctrine["known_issues"]:
            section += f"- {issue}\n"
        section += "\n"

    if "desert_adaptations" in doctrine:
        section += f"**Desert Adaptations**: {doctrine['desert_adaptations']}\n\n"

    return section

def generate_shortages_section(data):
    """Generate critical equipment shortages section."""
    section = "## Critical Equipment Shortages\n\n"

    doctrine = data.get("tactical_doctrine", {})
    issues = doctrine.get("known_issues", [])

    if not issues:
        section += "No critical equipment shortages documented for this period.\n\n"
        return section

    section += "### Priority 1: Critical Shortages (Mission-Limiting)\n\n"

    # Extract shortage-related issues
    shortage_issues = [issue for issue in issues if any(word in issue.lower() for word in ['shortage', 'lack', 'limited', 'inadequate'])]

    if shortage_issues:
        for issue in shortage_issues[:2]:  # Top 2 as Priority 1
            section += f"- {issue}\n"
        section += "\n"

    if len(shortage_issues) > 2:
        section += "### Priority 2: Important Shortages (Capability-Reducing)\n\n"
        for issue in shortage_issues[2:]:
            section += f"- {issue}\n"
        section += "\n"

    section += "**Overall Assessment**: Equipment shortages limited operational capability during this quarter. Units adapted through tactical innovation and aggressive use of available resources.\n\n"

    return section

def generate_historical_section(data):
    """Generate historical context section."""
    section = "## Historical Context\n\n"

    hist = data.get("historical_context", {})
    if not hist:
        section += "Historical context data not available.\n\n"
        return section

    if "formation_history" in hist:
        section += f"### Formation History\n\n{hist['formation_history']}\n\n"

    if "operational_status" in hist:
        section += f"### Operational Status\n\n{hist['operational_status']}\n\n"

    if "quarter_events" in hist:
        section += "### Key Events\n\n"
        for event in hist["quarter_events"]:
            section += f"- {event}\n"
        section += "\n"

    if "commonwealth_forces" in hist:
        section += f"### Commonwealth Forces\n\n{hist['commonwealth_forces']}\n\n"

    return section

def generate_wargaming_section(data):
    """Generate wargaming data section."""
    section = "## Wargaming Data\n\n"

    wg = data.get("wargaming_data", {})
    if not wg:
        section += "Wargaming data not available.\n\n"
        return section

    section += f"**Morale Rating**: {wg.get('morale_rating', 'Unknown')}/10\n"
    section += f"**Experience Level**: {wg.get('experience_level', 'Unknown')}\n\n"

    if "special_rules" in wg:
        section += "**Special Rules**:\n"
        for rule in wg["special_rules"]:
            section += f"- {rule}\n"
        section += "\n"

    if "scenario_suitability" in wg:
        section += "**Suitable Scenarios**:\n"
        for scenario in wg["scenario_suitability"]:
            section += f"- {scenario}\n"
        section += "\n"

    if "historical_engagements" in wg:
        section += "**Historical Engagements**:\n"
        for engagement in wg["historical_engagements"]:
            section += f"- {engagement}\n"
        section += "\n"

    return section

def generate_data_quality_section(data):
    """Generate data quality & known gaps section."""
    section = "## Data Quality & Known Gaps\n\n"

    validation = data.get("validation", {})
    if not validation:
        section += "Data quality information not available.\n\n"
        return section

    confidence = validation.get("confidence", 0)
    conf_level = "High" if confidence >= 80 else "Medium" if confidence >= 70 else "Acceptable"

    section += f"**Confidence Score**: {confidence}% ({conf_level} confidence)\n\n"

    section += "### Data Sources\n\n"
    sources = validation.get("source", [])
    if isinstance(sources, list):
        section += "This unit's TO&E was compiled from:\n"
        for source in sources:
            section += f"- {source}\n"
        section += "\n"

    section += "### Known Data Gaps\n\n"
    gaps = validation.get("known_gaps", [])
    if gaps:
        section += "The following information could not be confirmed from available sources:\n\n"
        for gap in gaps:
            section += f"- {gap}\n"
        section += "\n"
    else:
        section += "No significant data gaps identified.\n\n"

    return section

def generate_conclusion_section(data):
    """Generate conclusion section."""
    section = "## Conclusion\n\n"

    unit_designation = data.get("unit_designation", "This formation")
    nation = data.get("nation", "").title()
    quarter = data.get("quarter", "this period")

    section += f"{unit_designation} represents a significant {nation} formation during {quarter}. "
    section += "This TO&E provides a comprehensive snapshot of the unit's organization, equipment, and capabilities during this period.\n\n"

    # Add assessment
    total_personnel = data.get("total_personnel", 0)
    tanks_total = data.get("tanks", {}).get("total", 0)
    artillery_total = data.get("artillery_total", 0)

    section += f"With {total_personnel:,} personnel, {tanks_total} tanks, and {artillery_total} artillery pieces, "
    section += "the formation demonstrated the organizational structure and combat power typical of its type and period.\n\n"

    section += "---\n\n"

    # Footer
    validation = data.get("validation", {})
    confidence = validation.get("confidence", 0)

    section += "**Data Source**: Autonomous TO&E Extraction System\n"
    section += f"**Confidence**: {confidence}%\n"
    section += "**Schema**: unified_toe_schema.json v1.0.0\n"
    section += f"**Extraction Date**: {validation.get('last_updated', datetime.now().strftime('%Y-%m-%d'))}\n\n"

    section += "---\n\n"

    # Subordinate units references
    sub_units = data.get("subordinate_units", [])
    if sub_units:
        section += "*For detailed equipment specifications and subordinate unit TO&E files, see:*\n"
        for unit in sub_units:
            ref_file = unit.get("reference_file")
            if ref_file:
                section += f"- `{ref_file}`\n"
        section += "\n"

    return section

def main():
    """Main execution function."""
    print("MDBook Chapter Regeneration Script")
    print("=" * 60)
    print(f"Units to process: {len(UNITS)}")
    print()

    generated = []

    for unit_name in UNITS:
        try:
            output_file = generate_chapter(unit_name)
            generated.append((unit_name, output_file, True))
        except Exception as e:
            print(f"  X Error generating {unit_name}: {e}")
            generated.append((unit_name, None, False))

    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    success_count = sum(1 for _, _, success in generated if success)
    print(f"Successfully generated: {success_count}/{len(UNITS)}")
    print()

    for unit_name, output_file, success in generated:
        if success:
            print(f"+ {unit_name}")
            print(f"  -> {output_file}")
        else:
            print(f"X {unit_name} - FAILED")

    print()
    print("=" * 60)
    print("Generation complete!")

if __name__ == "__main__":
    main()
