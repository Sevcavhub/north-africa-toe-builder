#!/usr/bin/env python3
"""
Generate integrated quarter overview chapters with full hierarchical forces structure.
"""

import json
from pathlib import Path
from datetime import datetime


def safe_int(value, default=0):
    """Safely extract integer from value."""
    if isinstance(value, int):
        return value
    elif isinstance(value, float):
        return int(value)
    elif isinstance(value, dict):
        for key in ['count', 'total', 'value']:
            if key in value:
                return safe_int(value[key], default)
        return default
    elif isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    return default


def load_json(filepath):
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def format_commander(command_data):
    """Format commander information."""
    if not command_data:
        return "Unknown"

    commander_data = command_data.get('commander', {})
    if isinstance(commander_data, str):
        return commander_data
    elif isinstance(commander_data, dict):
        name = commander_data.get('name', 'Unknown')
        rank = commander_data.get('rank', '')
        if rank:
            return f"{rank} {name}"
        return name
    return "Unknown"


def generate_forces_section(nation, quarter, data_dir):
    """Generate forces section for a nation and quarter."""

    # Find army-level units
    pattern = f"{nation}_{quarter}_*_toe.json"
    json_files = sorted(data_dir.glob(pattern))

    army_units = []
    for jf in json_files:
        unit_json = load_json(jf)
        if unit_json:
            org_level = unit_json.get('organization_level', '').lower()
            if org_level in ['army', 'theater', 'theater_scm']:
                army_units.append(unit_json)

    if not army_units:
        return ""

    nation_name = nation.capitalize()
    if nation == "british":
        nation_name = "British/Commonwealth"

    output = []
    output.append(f"\n### {nation_name} Forces\n")

    for unit_json in army_units:
        unit_name = unit_json.get('unit_designation', 'Unknown Unit')
        output.append(f"\n#### {unit_name}")

        # Commander
        command_data = unit_json.get('command', {})
        commander = format_commander(command_data)
        output.append(f"**Commander**: {commander}")

        # Strength
        total_personnel = safe_int(unit_json.get('total_personnel', 0))
        if total_personnel > 0:
            output.append(f"**Strength**: {total_personnel:,} personnel")

        # HQ location
        hq_location = command_data.get('headquarters_location', '')
        if hq_location:
            output.append(f"**Headquarters**: {hq_location}")

        output.append("")
        output.append("##### Aggregate Equipment Summary")

        # Personnel breakdown
        officers = safe_int(unit_json.get('officers', 0))
        ncos = safe_int(unit_json.get('ncos', 0))
        enlisted = safe_int(unit_json.get('enlisted', 0))
        if total_personnel > 0:
            output.append(f"- **Personnel**: {total_personnel:,} total ({officers:,} officers, {ncos:,} NCOs, {enlisted:,} enlisted)")

        # Tanks
        tanks_data = unit_json.get('tanks', {})
        total_tanks_raw = tanks_data.get('total', 0)
        total_tanks = safe_int(total_tanks_raw)

        if total_tanks > 0:
            operational_tanks = safe_int(tanks_data.get('operational', 0))
            tank_str = f"- **Tanks**: {total_tanks:,} total"
            if operational_tanks > 0 and operational_tanks != total_tanks:
                readiness = int((operational_tanks / total_tanks) * 100)
                tank_str += f" ({operational_tanks:,} operational, {readiness}% readiness)"
            output.append(tank_str)

            # Tank variants by category
            for category in ['medium_tanks', 'light_tanks', 'heavy_tanks']:
                if category in tanks_data:
                    cat_data = tanks_data[category]
                    if isinstance(cat_data, dict) and 'count' in cat_data:
                        count_data = cat_data['count']
                        if isinstance(count_data, dict):
                            variants = count_data.get('variants', {})
                            for variant_name, variant_info in variants.items():
                                if isinstance(variant_info, dict):
                                    count = safe_int(variant_info.get('count', 0))
                                    if count > 0:
                                        operational = safe_int(variant_info.get('operational', count))
                                        notes = variant_info.get('notes', '')
                                        variant_str = f"  - {variant_name}: {count:,}"
                                        if operational != count:
                                            variant_str += f" ({operational:,} operational)"
                                        if notes:
                                            variant_str += f" - {notes}"
                                        output.append(variant_str)

        # Artillery
        artillery_total = safe_int(unit_json.get('artillery_total', 0))
        if artillery_total > 0:
            output.append(f"- **Artillery**: {artillery_total:,} guns")

            # Field artillery
            field_art = unit_json.get('field_artillery', {})
            if field_art and isinstance(field_art, dict):
                if variants:
                    output.append("  - Field Artillery:")
                    for gun_name, gun_info in variants.items():
                        if isinstance(gun_info, dict):
                            count = safe_int(gun_info.get('count', 0))
                            if count > 0:
                                caliber = gun_info.get('caliber', '')
                                gun_str = f"    - {gun_name}: {count:,}"
                                if caliber:
                                    gun_str += f" ({caliber})"
                                output.append(gun_str)

            # Anti-tank
            anti_tank = unit_json.get('anti_tank', {})
            if anti_tank and isinstance(anti_tank, dict):
                variants = anti_tank.get('variants', {})
                if variants:
                    output.append("  - Anti-Tank:")
                    for gun_name, gun_info in variants.items():
                        if isinstance(gun_info, dict):
                            count = safe_int(gun_info.get('count', 0))
                            if count > 0:
                                caliber = gun_info.get('caliber', '')
                                gun_str = f"    - {gun_name}: {count:,}"
                                if caliber:
                                    gun_str += f" ({caliber})"
                                output.append(gun_str)

            # Anti-aircraft
            anti_aircraft = unit_json.get('anti_aircraft', {})
            if anti_aircraft and isinstance(anti_aircraft, dict):
                variants = anti_aircraft.get('variants', {})
                if variants:
                    output.append("  - Anti-Aircraft:")
                    for gun_name, gun_info in variants.items():
                        if isinstance(gun_info, dict):
                            count = safe_int(gun_info.get('count', 0))
                            if count > 0:
                                caliber = gun_info.get('caliber', '')
                                gun_str = f"    - {gun_name}: {count:,}"
                                if caliber:
                                    gun_str += f" ({caliber})"
                                output.append(gun_str)

        # Vehicles
        ground_vehicles = safe_int(unit_json.get('ground_vehicles_total', 0))
        if ground_vehicles > 0:
            output.append(f"- **Vehicles**: {ground_vehicles:,} total")

            halftracks_data = unit_json.get('halftracks', {})
            halftracks = safe_int(halftracks_data.get('total', 0) if isinstance(halftracks_data, dict) else halftracks_data)
            if halftracks > 0:
                output.append(f"  - Halftracks: {halftracks:,}")

            armored_cars_data = unit_json.get('armored_cars', {})
            armored_cars = safe_int(armored_cars_data.get('total', 0) if isinstance(armored_cars_data, dict) else armored_cars_data)
            if armored_cars > 0:
                output.append(f"  - Armored Cars: {armored_cars:,}")

            trucks_data = unit_json.get('trucks', {})
            trucks = safe_int(trucks_data.get('total', 0) if isinstance(trucks_data, dict) else trucks_data)
            if trucks > 0:
                output.append(f"  - Trucks: {trucks:,}")

            motorcycles_data = unit_json.get('motorcycles', {})
            motorcycles = safe_int(motorcycles_data.get('total', 0) if isinstance(motorcycles_data, dict) else motorcycles_data)
            if motorcycles > 0:
                output.append(f"  - Motorcycles: {motorcycles:,}")

            support_vehicles_data = unit_json.get('support_vehicles', {})
            support_vehicles = safe_int(support_vehicles_data.get('total', 0) if isinstance(support_vehicles_data, dict) else support_vehicles_data)
            if support_vehicles > 0:
                output.append(f"  - Support vehicles: {support_vehicles:,}")

        output.append("")

        # Subordinate units
        subordinate_units = unit_json.get('subordinate_units', [])
        if subordinate_units:
            output.append("##### Subordinate Units\n")

            for sub_unit in subordinate_units:
                if isinstance(sub_unit, dict):
                    sub_name = sub_unit.get('unit_designation', 'Unknown')
                    sub_type = sub_unit.get('unit_type', '')
                    sub_commander = sub_unit.get('commander', 'Unknown')
                    sub_strength = safe_int(sub_unit.get('strength', 0))
                    sub_composition = sub_unit.get('composition', '')
                    sub_equipment = sub_unit.get('equipment_summary', '')
                    sub_notes = sub_unit.get('notes', '')

                    output.append(f"###### {sub_name}")
                    if sub_commander:
                        output.append(f"**Commander**: {sub_commander}")
                    if sub_type:
                        output.append(f"**Type**: {sub_type}")
                    if sub_strength > 0:
                        output.append(f"**Strength**: {sub_strength:,} personnel")
                    if sub_composition:
                        output.append(f"**Composition**: {sub_composition}")
                    if sub_equipment:
                        output.append(f"**Equipment**: {sub_equipment}")
                    if sub_notes:
                        output.append(f"**Notes**: {sub_notes}")
                    output.append("")

        # Air Support
        air_support = unit_json.get('air_support', {})
        if air_support:
            output.append("##### Air Support Available\n")

            theater_air = air_support.get('theater_air_command', {})
            if theater_air:
                air_designation = theater_air.get('designation', '')
                air_commander = theater_air.get('commander', '')
                if air_designation:
                    output.append(f"**Theater Air Command**: {air_designation}")
                if air_commander and air_commander != 'Unknown':
                    output.append(f"**Commander**: {air_commander}")

            aggregate = air_support.get('aggregate_strength', {})
            if aggregate:
                total_aircraft = safe_int(aggregate.get('total_aircraft', 0))
                operational = safe_int(aggregate.get('operational_aircraft', 0))
                serviceability = safe_int(aggregate.get('serviceability_rate', 0))

                if total_aircraft > 0:
                    output.append(f"**Aggregate Strength**: {total_aircraft} aircraft ({operational} operational, {serviceability}% serviceability)")

            key_types = air_support.get('key_aircraft_types', [])
            if key_types:
                output.append(f"**Key Aircraft Types**: {', '.join(key_types)}")

            org_summary = air_support.get('organizational_summary', '')
            if org_summary:
                output.append(f"**Organization**: {org_summary}")

            integration_note = air_support.get('integration_note', '')
            if integration_note:
                output.append(f"\n*{integration_note}*")

            output.append("")

        # Weather & Logistics
        supply_logistics = unit_json.get('supply_logistics', {})
        weather_environment = unit_json.get('weather_environment', {})

        if supply_logistics or weather_environment:
            output.append("##### Weather & Logistics\n")

            if weather_environment:
                output.append("**Environmental Conditions**:")

                season = weather_environment.get('season_quarter', '')
                if season:
                    output.append(f"- **Season**: {season}")

                temp_range = weather_environment.get('temperature_range_c', {})
                if temp_range:
                    temp_min = safe_int(temp_range.get('min', 0))
                    temp_max = safe_int(temp_range.get('max', 0))
                    if temp_min > 0 or temp_max > 0:
                        output.append(f"- **Temperature**: {temp_min}-{temp_max}°C")

                terrain = weather_environment.get('terrain_type', '')
                if terrain:
                    output.append(f"- **Terrain**: {terrain[:200]}")

                daylight = weather_environment.get('daylight_hours', 0)
                if daylight > 0:
                    output.append(f"- **Daylight**: {daylight} hours average")

                output.append("")

            if supply_logistics:
                output.append("**Logistics Status**:")

                supply_status = supply_logistics.get('supply_status', '')
                if supply_status:
                    if len(supply_status) > 400:
                        supply_status = supply_status[:400] + "..."
                    output.append(f"- **Supply Situation**: {supply_status}")

                fuel_days = supply_logistics.get('fuel_reserves_days', 0)
                if fuel_days > 0:
                    output.append(f"- **Fuel Reserves**: {fuel_days} days")

                ammo_days = supply_logistics.get('ammunition_days', 0)
                if ammo_days > 0:
                    output.append(f"- **Ammunition**: {ammo_days} days stockpile")

                water = supply_logistics.get('water_liters_per_day', 0)
                if water > 0:
                    output.append(f"- **Water**: {water}L/man/day requirement")

                operational_radius = supply_logistics.get('operational_radius_km', 0)
                if operational_radius > 0:
                    output.append(f"- **Operational Radius**: {operational_radius}km")

                output.append("")

        output.append("---\n")

    return "\n".join(output)


def integrate_quarter(quarter, data_dir, book_dir):
    """Integrate forces structure into quarter overview."""

    print(f"[*] Processing {quarter.upper()}...")

    # Load existing narrative
    narrative_file = book_dir / f"{quarter}.md"
    if not narrative_file.exists():
        print(f"  [SKIP] No narrative file found")
        return False

    with open(narrative_file, 'r', encoding='utf-8') as f:
        existing_narrative = f.read()

    # Generate forces sections
    forces_sections = ["\n---\n", "\n## Forces Structure\n"]

    for nation in ["german", "italian", "british", "american", "french"]:
        nation_forces = generate_forces_section(nation, quarter, data_dir)
        if nation_forces:
            forces_sections.append(nation_forces)

    forces_content = "".join(forces_sections)

    # Find insertion point
    strategic_pos = existing_narrative.find("## Strategic Situation")
    if strategic_pos == -1:
        print(f"  [ERROR] Could not find Strategic Situation section")
        return False

    next_section_pos = existing_narrative.find("\n##", strategic_pos + 22)
    if next_section_pos == -1:
        print(f"  [ERROR] Could not find next section")
        return False

    # Insert forces section
    integrated = existing_narrative[:next_section_pos] + "\n" + forces_content + existing_narrative[next_section_pos:]

    # Backup original
    backup_file = book_dir / f"{quarter}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(existing_narrative)

    # Write integrated version
    with open(narrative_file, 'w', encoding='utf-8') as f:
        f.write(integrated)

    print(f"  [OK] Integrated ({len(integrated)} chars, +{len(forces_content)} forces)")

    return True


def main():
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "output" / "units"
    book_dir = project_root / "north_africa_campaign_book" / "src" / "quarter_overviews"

    quarters = [
        "1940q2", "1940q3", "1940q4",
        "1941q1", "1941q2", "1941q3", "1941q4",
        "1942q1", "1942q2", "1942q3", "1942q4",
        "1943q1", "1943q2"
    ]

    print("\n" + "="*80)
    print("INTEGRATED QUARTER OVERVIEW GENERATOR")
    print("="*80)
    print(f"\nProcessing {len(quarters)} quarters...")

    success_count = 0
    for quarter in quarters:
        if integrate_quarter(quarter, data_dir, book_dir):
            success_count += 1

    print("\n" + "="*80)
    print(f"[OK] COMPLETE: {success_count}/{len(quarters)} quarters integrated")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
