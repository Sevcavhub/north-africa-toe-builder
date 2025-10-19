#!/usr/bin/env python3
"""
Generate WITW Scenario Exports from Enriched Unit JSON Files

Purpose: Export WITW-format CSV with equipment IDs, battle context, and victory conditions

Input: Enriched unit JSON files (from enrich_units_with_database.py)
Output: WITW scenario CSV files (equipment IDs, counts, battle narratives, victory conditions)

This script is CRITICAL for:
- Phase 9 scenario generation
- Wargame scenario exports with historical accuracy
- Battle context (historical situation, date, location)
- Victory conditions (narrative description for each side)
- Supply states (fuel days, ammo days, water reserves)
- Weather/terrain conditions (operational context)
"""

import json
import csv
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ENRICHED_UNITS_DIR = PROJECT_ROOT / "data" / "output" / "units"  # Canonical location (Architecture v4.0)
SCENARIOS_DIR = PROJECT_ROOT / "data" / "output" / "scenarios"

def parse_quarter(quarter_str):
    """Parse quarter string (e.g., '1941q2') to date"""
    match = re.match(r'(\d{4})q(\d)', quarter_str.lower())
    if not match:
        return None

    year, quarter = match.groups()
    year = int(year)
    quarter = int(quarter)

    # Convert quarter to month (Q1=March, Q2=June, Q3=September, Q4=December)
    month_map = {1: 3, 2: 6, 3: 9, 4: 12}
    month = month_map.get(quarter, 6)

    return f"{year}-{month:02d}-01"

def extract_scenario_metadata(unit_data, filename):
    """Extract scenario metadata from unit JSON"""

    # Parse filename: nation_quarter_unit_designation_toe.json
    parts = filename.replace('_toe.json', '').split('_')

    if len(parts) < 3:
        return None

    nation = parts[0]
    quarter = parts[1]
    unit_designation = '_'.join(parts[2:])

    # Parse quarter to date
    scenario_date = parse_quarter(quarter) or f"{quarter}-01-01"

    metadata = {
        'nation': nation.title(),
        'quarter': quarter,
        'date': scenario_date,
        'unit_designation': unit_designation.replace('_', ' ').title(),
        'unit_type': 'Division' if 'division' in unit_designation.lower() else
                     'Corps' if 'corps' in unit_designation.lower() else
                     'Brigade' if 'brigade' in unit_designation.lower() else
                     'Regiment' if 'regiment' in unit_designation.lower() else
                     'Battalion',
        'theater': 'North Africa' if 'africa' in filename.lower() else 'Mediterranean'
    }

    # Extract commander if available
    if 'unit_designation' in unit_data:
        metadata['unit_name'] = unit_data['unit_designation']
    if 'commander' in unit_data:
        metadata['commander'] = unit_data['commander']

    return metadata

def generate_equipment_csv(enriched_unit_data, scenario_name):
    """Generate WITW equipment CSV from enriched unit data"""

    equipment_rows = []

    # Equipment sections to export (handle both flat and nested structures)
    equipment_sections = [
        'tanks',
        'armored_cars',
        'artillery',
        'anti_tank_guns',
        'anti_aircraft_guns',
        'ground_vehicles',
        'aircraft',
        'halftracks',
        'trucks',
        'motorcycles'
    ]

    for section in equipment_sections:
        if section not in enriched_unit_data:
            continue

        section_data = enriched_unit_data[section]
        if not isinstance(section_data, dict):
            continue

        # Handle nested variant structure (Architecture v3.0+)
        if 'variants' in section_data:
            # Process variants subsection
            for equipment_name, equipment_info in section_data['variants'].items():
                if isinstance(equipment_info, dict):
                    count = equipment_info.get('count', 0)
                    operational = equipment_info.get('operational', count)

                    # Generate WITW ID from nation and equipment name
                    nation = enriched_unit_data.get('nation', 'unknown')
                    witw_id = f"{nation.upper()[:3]}_{equipment_name.upper().replace(' ', '_').replace('-', '_')}"

                    if count == 0:
                        continue

                    # Calculate operational readiness
                    readiness = int((operational / count * 100) if count > 0 else 100)

                    equipment_rows.append({
                        'equipment_id': witw_id,
                        'equipment_name': equipment_name,
                        'equipment_type': section,
                        'count': count,
                        'section': section,
                        'ready': operational,
                        'damaged': count - operational,
                        'operational_readiness': readiness
                    })

        # Handle tank subcategories (heavy_tanks, medium_tanks, light_tanks)
        elif 'heavy_tanks' in section_data or 'medium_tanks' in section_data or 'light_tanks' in section_data:
            for tank_category in ['heavy_tanks', 'medium_tanks', 'light_tanks']:
                if tank_category not in section_data:
                    continue

                tank_cat_data = section_data[tank_category]
                if 'variants' not in tank_cat_data:
                    continue

                for equipment_name, equipment_info in tank_cat_data['variants'].items():
                    if isinstance(equipment_info, dict):
                        count = equipment_info.get('count', 0)
                        operational = equipment_info.get('operational', count)

                        nation = enriched_unit_data.get('nation', 'unknown')
                        witw_id = f"{nation.upper()[:3]}_{equipment_name.upper().replace(' ', '_').replace('-', '_')}"

                        if count == 0:
                            continue

                        readiness = int((operational / count * 100) if count > 0 else 100)

                        equipment_rows.append({
                            'equipment_id': witw_id,
                            'equipment_name': equipment_name,
                            'equipment_type': 'tanks',
                            'count': count,
                            'section': 'tanks',
                            'ready': operational,
                            'damaged': count - operational,
                            'operational_readiness': readiness
                        })

        # Handle flat enriched structure (simple count or enriched object)
        else:
            for equipment_name, equipment_info in section_data.items():
                # Skip metadata fields
                if equipment_name in ['total', 'operational', 'readiness_percentage']:
                    continue

                # Extract count and WITW ID
                if isinstance(equipment_info, dict):
                    count = equipment_info.get('count', 0)
                    witw_id = equipment_info.get('witw_id', equipment_name)
                    specifications = equipment_info.get('specifications', {})
                else:
                    count = equipment_info
                    witw_id = equipment_name
                    specifications = {}

                if count == 0:
                    continue

                # Get equipment type
                eq_type = specifications.get('type', 'unknown') if specifications else 'unknown'

                # Create CSV row
                equipment_rows.append({
                    'equipment_id': witw_id,
                    'equipment_name': equipment_name,
                    'equipment_type': eq_type,
                    'count': count,
                    'section': section,
                    'ready': count,  # Assume all ready unless specified
                    'damaged': 0,
                    'operational_readiness': 100
                })

    return equipment_rows

def generate_scenario_narrative(metadata, unit_data):
    """Generate battle narrative and victory conditions"""

    # Default narrative template
    narrative = {
        'title': f"{metadata['unit_designation']} - {metadata['quarter'].upper()}",
        'date': metadata['date'],
        'location': metadata['theater'],
        'situation': f"{metadata['nation']} {metadata['unit_type']} deployed in {metadata['theater']} during {metadata['quarter'].upper()}.",
        'axis_objective': "Maintain defensive positions and inflict maximum casualties on Allied forces.",
        'allied_objective': "Advance and secure strategic objectives while minimizing casualties.",
        'weather': 'Clear',
        'terrain': 'Desert',
        'special_rules': 'None'
    }

    # Customize based on unit data if available
    if 'historical_context' in unit_data:
        narrative['situation'] = unit_data['historical_context']

    if 'mission' in unit_data:
        if metadata['nation'].lower() in ['german', 'italian']:
            narrative['axis_objective'] = unit_data['mission']
        else:
            narrative['allied_objective'] = unit_data['mission']

    return narrative

def export_scenario(enriched_unit_file):
    """Export a single scenario from enriched unit file"""

    filename = enriched_unit_file.name
    print(f"\nExporting scenario: {filename}")

    # Read enriched unit data
    with open(enriched_unit_file, 'r', encoding='utf-8') as f:
        unit_data = json.load(f)

    # Extract metadata
    metadata = extract_scenario_metadata(unit_data, filename)
    if not metadata:
        print(f"  [SKIP] Cannot extract metadata from {filename}")
        return None

    scenario_name = f"{metadata['nation']}_{metadata['quarter']}_{metadata['unit_designation'].replace(' ', '_')}"
    print(f"  Scenario name: {scenario_name}")

    # Generate equipment CSV
    equipment_csv = generate_equipment_csv(unit_data, scenario_name)
    print(f"  Equipment items: {len(equipment_csv)}")

    # Generate narrative
    narrative = generate_scenario_narrative(metadata, unit_data)

    # Create scenario directory
    scenario_dir = SCENARIOS_DIR / scenario_name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    # Write equipment CSV
    equipment_csv_file = scenario_dir / 'equipment.csv'
    with open(equipment_csv_file, 'w', newline='', encoding='utf-8') as f:
        if equipment_csv:
            fieldnames = ['equipment_id', 'equipment_name', 'equipment_type', 'count',
                         'section', 'ready', 'damaged', 'operational_readiness']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(equipment_csv)
    print(f"  [OK] Wrote equipment CSV: {equipment_csv_file.name}")

    # Write scenario metadata
    metadata_file = scenario_dir / 'scenario_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': metadata,
            'narrative': narrative,
            'exported_at': datetime.now().isoformat(),
            'source_file': filename
        }, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Wrote scenario metadata: {metadata_file.name}")

    # Write README with battle context
    readme_file = scenario_dir / 'README.md'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(f"# {narrative['title']}\n\n")
        f.write(f"**Date**: {narrative['date']}\n\n")
        f.write(f"**Location**: {narrative['location']}\n\n")
        f.write(f"## Situation\n\n{narrative['situation']}\n\n")
        f.write(f"## Axis Objective\n\n{narrative['axis_objective']}\n\n")
        f.write(f"## Allied Objective\n\n{narrative['allied_objective']}\n\n")
        f.write(f"## Conditions\n\n")
        f.write(f"- **Weather**: {narrative['weather']}\n")
        f.write(f"- **Terrain**: {narrative['terrain']}\n")
        f.write(f"- **Special Rules**: {narrative['special_rules']}\n\n")
        f.write(f"## Equipment\n\n")
        f.write(f"Total equipment items: {len(equipment_csv)}\n\n")
        f.write(f"See `equipment.csv` for complete equipment list.\n")
    print(f"  [OK] Wrote README: {readme_file.name}")

    return {
        'scenario_name': scenario_name,
        'equipment_count': len(equipment_csv),
        'scenario_dir': str(scenario_dir)
    }

def export_all_scenarios():
    """Export scenarios from all enriched unit files"""

    print('=' * 80)
    print('GENERATING WITW SCENARIO EXPORTS')
    print('=' * 80)
    print(f'\nInput directory: {ENRICHED_UNITS_DIR}')
    print(f'Output directory: {SCENARIOS_DIR}\n')

    # Ensure scenarios directory exists
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)

    # Get all enriched unit files
    enriched_files = list(ENRICHED_UNITS_DIR.glob('*_toe.json'))
    print(f'Found {len(enriched_files)} enriched unit files\n')

    exported = 0
    skipped = 0
    errors = 0

    results = []

    for enriched_file in enriched_files:
        try:
            result = export_scenario(enriched_file)
            if result:
                results.append(result)
                exported += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  [ERROR] Failed to export {enriched_file.name}: {e}")
            errors += 1

    print('\n' + '=' * 80)
    print('SCENARIO EXPORT SUMMARY')
    print('=' * 80)
    print(f'Scenarios exported: {exported}')
    print(f'Scenarios skipped: {skipped}')
    print(f'Errors: {errors}')
    print(f'\n[OK] Scenario export complete!')
    print(f'\nScenarios saved to: {SCENARIOS_DIR}')
    print('=' * 80)

    return {'exported': exported, 'skipped': skipped, 'errors': errors, 'results': results}

if __name__ == '__main__':
    export_all_scenarios()