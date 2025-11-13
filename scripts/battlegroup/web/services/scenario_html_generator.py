#!/usr/bin/env python3
"""
Scenario HTML Generator

Generates printable HTML scenarios with embedded AFV datacards.
Combines scenario content from markdown files with V5.5 datacards.
"""

import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Template

# Import equipment resolver
try:
    # When running as a module (Flask app)
    from services.equipment_resolver import resolve_equipment_canonical_id, extract_equipment_from_scenario_forces
except ImportError:
    # When running standalone
    from equipment_resolver import resolve_equipment_canonical_id, extract_equipment_from_scenario_forces

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "database" / "master_database.db"
TEMPLATE_PATH = PROJECT_ROOT / "scripts" / "battlegroup" / "web" / "templates" / "scenario_printable.html"
BOOKS_PATH = PROJECT_ROOT / "books"


def classify_scenario_scale(total_points: int) -> str:
    """
    Classify scenario scale based on total points budget.

    Args:
        total_points: Combined points budget for all factions

    Returns:
        Scale classification (Squad, Platoon, Company, or Battalion)
    """
    if total_points < 100:
        return "Squad"
    elif total_points < 500:
        return "Platoon"
    elif total_points < 1500:
        return "Company"
    else:
        return "Battalion"


def parse_scenario_markdown(md_path: Path) -> Dict:
    """
    Parse scenario markdown file into structured data.

    Args:
        md_path: Path to scenario markdown file

    Returns:
        Dict with scenario data (title, forces, objectives, etc.)
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    scenario = {
        'title': '',
        'date': '',
        'location': '',
        'situation_description': '',
        'battle_description': '',
        'table_size': "6' × 4'",
        'terrain_features': [],
        'victory_type': 'mixed',
        'attacker_name': 'Attacker',
        'attacker_objective': '',
        'defender_name': 'Defender',
        'defender_objective': '',
        'attacker_deployment': '',
        'defender_deployment': '',
        'turn_limit': 8,
        'special_rules': [],
        'attacker_units': [],
        'attacker_points': 0,
        'attacker_br': 0,
        'defender_units': [],
        'defender_points': 0,
        'defender_br': 0,
    }

    # Extract title (first H1)
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        scenario['title'] = title_match.group(1).strip()

    # Extract date and location from SITUATION REPORT
    date_match = re.search(r'\*\*Date\*\*:\s*(.+)$', content, re.MULTILINE)
    if date_match:
        scenario['date'] = date_match.group(1).strip()

    location_match = re.search(r'\*\*Location\*\*:\s*(.+)$', content, re.MULTILINE)
    if location_match:
        scenario['location'] = location_match.group(1).strip()

    # Extract situation description (paragraph after location)
    situation_match = re.search(
        r'\*\*Location\*\*:.*?\n\n(.+?)\n\n',
        content,
        re.DOTALL
    )
    if situation_match:
        scenario['situation_description'] = situation_match.group(1).strip()

    # Extract battle description (THE BATTLE section)
    battle_match = re.search(
        r'## THE BATTLE\n(.+?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    if battle_match:
        scenario['battle_description'] = battle_match.group(1).strip()

    # Extract table size
    table_match = re.search(r'\*\*Table Size\*\*:\s*(.+)$', content, re.MULTILINE)
    if table_match:
        scenario['table_size'] = table_match.group(1).strip()

    # Extract terrain features
    terrain_section = re.search(
        r'\*\*Terrain\*\*:\n((?:- .+\n)+)',
        content
    )
    if terrain_section:
        terrain_text = terrain_section.group(1)
        scenario['terrain_features'] = [
            line.strip('- ').strip()
            for line in terrain_text.split('\n')
            if line.strip().startswith('-')
        ]

    # Extract objectives
    obj_type_match = re.search(r'\*\*Victory Type\*\*:\s*(.+)$', content, re.MULTILINE)
    if obj_type_match:
        scenario['victory_type'] = obj_type_match.group(1).strip()

    # Parse forces section to get attacker/defender names
    # Find all forces section titles
    forces_names = re.findall(r'### (.+?) FORCES', content, re.IGNORECASE)
    if len(forces_names) >= 1:
        scenario['attacker_name'] = forces_names[0].strip().title()
    if len(forces_names) >= 2:
        scenario['defender_name'] = forces_names[1].strip().title()

    # Extract objectives (using attacker/defender names if found)
    attacker_obj_pattern = rf'\*\*{re.escape(scenario["attacker_name"])} Victory\*\*:\s*(.+)$'
    attacker_obj_match = re.search(attacker_obj_pattern, content, re.MULTILINE | re.IGNORECASE)
    if attacker_obj_match:
        scenario['attacker_objective'] = attacker_obj_match.group(1).strip()

    defender_obj_pattern = rf'\*\*{re.escape(scenario["defender_name"])} Victory\*\*:\s*(.+)$'
    defender_obj_match = re.search(defender_obj_pattern, content, re.MULTILINE | re.IGNORECASE)
    if defender_obj_match:
        scenario['defender_objective'] = defender_obj_match.group(1).strip()

    # Extract deployment
    deployment_section = re.search(
        r'## DEPLOYMENT\n(.+?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    if deployment_section:
        deploy_text = deployment_section.group(1)
        attacker_deploy = re.search(rf'\*\*{re.escape(scenario["attacker_name"])}\*\*:\s*(.+)$', deploy_text, re.MULTILINE | re.IGNORECASE)
        if attacker_deploy:
            scenario['attacker_deployment'] = attacker_deploy.group(1).strip()

        defender_deploy = re.search(rf'\*\*{re.escape(scenario["defender_name"])}\*\*:\s*(.+)$', deploy_text, re.MULTILINE | re.IGNORECASE)
        if defender_deploy:
            scenario['defender_deployment'] = defender_deploy.group(1).strip()

    # Extract turn limit
    turn_match = re.search(r'\*\*Turn Limit\*\*:\s*(\d+)', content, re.MULTILINE)
    if turn_match:
        scenario['turn_limit'] = int(turn_match.group(1))

    # Extract special rules
    rules_match = re.search(
        r'## SPECIAL SCENARIO RULES\n((?:- .+\n?)+)',
        content
    )
    if rules_match:
        rules_text = rules_match.group(1)
        scenario['special_rules'] = [
            line.strip('- ').strip()
            for line in rules_text.split('\n')
            if line.strip().startswith('-')
        ]

    # Extract forces (stop at next ## or ### heading)
    forces_pattern = rf'### {re.escape(scenario["attacker_name"])} FORCES\n\*\*Nation\*\*:.*?\n\*\*Points Budget\*\*:\s*(\d+)\n\*\*Total Battle Rating\*\*:\s*(\d+)\n\n\*\*Units\*\*:\n((?:- .+\n?)+?)(?=\n###|\n##|\Z)'
    attacker_forces = re.search(forces_pattern, content, re.IGNORECASE | re.DOTALL)
    if attacker_forces:
        scenario['attacker_points'] = int(attacker_forces.group(1))
        scenario['attacker_br'] = int(attacker_forces.group(2))
        units_text = attacker_forces.group(3)
        scenario['attacker_units'] = [
            line.strip('- ').strip()
            for line in units_text.split('\n')
            if line.strip().startswith('-')
        ]

    forces_pattern = rf'### {re.escape(scenario["defender_name"])} FORCES\n\*\*Nation\*\*:.*?\n\*\*Points Budget\*\*:\s*(\d+)\n\*\*Total Battle Rating\*\*:\s*(\d+)\n\n\*\*Units\*\*:\n((?:- .+\n?)+?)(?=\n###|\n##|\Z)'
    defender_forces = re.search(forces_pattern, content, re.IGNORECASE | re.DOTALL)
    if defender_forces:
        scenario['defender_points'] = int(defender_forces.group(1))
        scenario['defender_br'] = int(defender_forces.group(2))
        units_text = defender_forces.group(3)
        scenario['defender_units'] = [
            line.strip('- ').strip()
            for line in units_text.split('\n')
            if line.strip().startswith('-')
        ]

    return scenario


def generate_simple_datacard_html(canonical_id: str) -> str:
    """
    Generate simplified datacard HTML for an AFV.

    This is a simplified version that shows basic stats.
    For production, we should integrate with generate_book_datacards_v5_5.py

    Args:
        canonical_id: Equipment canonical ID (e.g., "BRI_MATILDA_II")

    Returns:
        HTML string for datacard
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get equipment data
    # Join with bg_reference_vehicles for weapon data if available
    cursor.execute("""
        SELECT
            e.name, e.nation, e.category,
            COALESCE(bgv.armor_front, eb.armor_front) as armor_front,
            COALESCE(bgv.armor_side, eb.armor_side) as armor_side,
            COALESCE(bgv.armor_rear, eb.armor_rear) as armor_rear,
            COALESCE(bgv.off_road_inches, eb.off_road_movement) as off_road_movement,
            COALESCE(bgv.road_inches, eb.road_movement) as road_movement,
            eb.points_regular, eb.battle_rating_regular,
            bgv.weapon_1, bgv.weapon_2, bgv.weapon_3, bgv.weapon_4
        FROM equipment e
        JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
        LEFT JOIN bg_reference_vehicles bgv ON eb.reference_vehicle_id = bgv.id
        WHERE e.canonical_id = ?
    """, (canonical_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return f'<div class="datacard"><p>Datacard not available for {canonical_id}</p></div>'

    # Determine nation class
    nation_class = f"datacard-{row['nation']}"

    # Build datacard HTML
    html = f'''
    <div class="datacard {nation_class}">
        <div class="datacard-header">
            <div class="datacard-silhouette">
                <!-- Silhouette would go here -->
            </div>
            <div class="datacard-title-block">
                <div class="datacard-title">{row['name']}</div>
                <div class="datacard-subtitle">{row['nation'].title()} {row['category'].replace('_', ' ').title()}</div>
            </div>
        </div>

        <table class="datacard-armor">
            <tr>
                <th>Armor</th>
                <th>Front</th>
                <th>Side</th>
                <th>Rear</th>
            </tr>
            <tr>
                <td></td>
                <td>{row['armor_front'] or '-'}</td>
                <td>{row['armor_side'] or '-'}</td>
                <td>{row['armor_rear'] or '-'}</td>
            </tr>
        </table>

        <table class="datacard-movement">
            <tr>
                <th>Movement</th>
                <th>Off-Road</th>
                <th>Road</th>
            </tr>
            <tr>
                <td></td>
                <td>{row['off_road_movement'] or '-'}"</td>
                <td>{row['road_movement'] or '-'}"</td>
            </tr>
        </table>

        <table class="datacard-weapons">
            <tr>
                <th colspan="4">Armament</th>
            </tr>
'''

    # Add weapons
    for i in range(1, 5):
        weapon = row[f'weapon_{i}']
        if weapon:
            html += f'<tr><td colspan="4">{weapon}</td></tr>\n'

    html += f'''
        </table>

        <table class="datacard-points">
            <tr>
                <th>Points (Regular)</th>
                <th>BR</th>
            </tr>
            <tr>
                <td>{row['points_regular'] or '-'}</td>
                <td>{row['battle_rating_regular'] or '-'}</td>
            </tr>
        </table>
    </div>
    '''

    return html


def generate_printable_scenario_html(scenario_id: str, battle: str = "battleaxe") -> str:
    """
    Generate printable HTML for a scenario with embedded AFV datacards.

    Args:
        scenario_id: Scenario filename without extension (e.g., "scenario_01")
        battle: Battle name (e.g., "battleaxe", "crusader")

    Returns:
        Complete HTML string ready for printing
    """
    # Find scenario markdown file
    scenario_path = BOOKS_PATH / battle / "book" / "src" / "scenarios" / f"{scenario_id}.md"

    if not scenario_path.exists():
        return f"<html><body><h1>Scenario not found: {scenario_id}</h1></body></html>"

    # Parse scenario
    scenario_data = parse_scenario_markdown(scenario_path)

    # Calculate scenario scale
    total_points = scenario_data['attacker_points'] + scenario_data['defender_points']
    scenario_scale = classify_scenario_scale(total_points)

    # Extract AFVs from forces
    all_units_text = '\n'.join(scenario_data['attacker_units'] + scenario_data['defender_units'])
    afv_list = extract_equipment_from_scenario_forces(all_units_text)

    # Generate datacards for unique AFVs
    datacards_html = []
    seen_canonical_ids = set()

    for afv in afv_list:
        if afv['canonical_id'] not in seen_canonical_ids:
            datacard_html = generate_simple_datacard_html(afv['canonical_id'])
            datacards_html.append(datacard_html)
            seen_canonical_ids.add(afv['canonical_id'])

    # Load template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template_content = f.read()

    template = Template(template_content)

    # Render HTML
    html = template.render(
        scenario_title=scenario_data['title'],
        date=scenario_data['date'],
        location=scenario_data['location'],
        scenario_scale=scenario_scale,
        situation_description=scenario_data['situation_description'],
        battle_description=scenario_data['battle_description'],
        table_size=scenario_data['table_size'],
        terrain_features=scenario_data['terrain_features'],
        victory_type=scenario_data['victory_type'],
        attacker_name=scenario_data['attacker_name'],
        attacker_objective=scenario_data['attacker_objective'],
        defender_name=scenario_data['defender_name'],
        defender_objective=scenario_data['defender_objective'],
        attacker_deployment=scenario_data['attacker_deployment'],
        defender_deployment=scenario_data['defender_deployment'],
        turn_limit=scenario_data['turn_limit'],
        special_rules=scenario_data['special_rules'],
        attacker_units=scenario_data['attacker_units'],
        attacker_points=scenario_data['attacker_points'],
        attacker_br=scenario_data['attacker_br'],
        defender_units=scenario_data['defender_units'],
        defender_points=scenario_data['defender_points'],
        defender_br=scenario_data['defender_br'],
        datacards=datacards_html
    )

    return html


def test_generator():
    """Test the scenario HTML generator."""
    print("Testing Scenario HTML Generator\n")

    # Test with battleaxe scenario_01
    print("Generating printable HTML for: Dawn at Fort Capuzzo")
    html = generate_printable_scenario_html("scenario_01", "battleaxe")

    # Save to file for inspection
    output_path = PROJECT_ROOT / "test_scenario_printable.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[OK] Generated HTML: {output_path}")
    print(f"[OK] File size: {len(html)} bytes")
    print("\nOpen in browser to test printing:")
    print(f"  {output_path}")


if __name__ == "__main__":
    test_generator()
