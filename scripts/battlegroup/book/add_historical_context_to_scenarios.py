"""
Add Historical Context to MDBook Scenarios

Updates all 45 scenario markdown files with historical context linking equipment
to Phase 6 units. Inserts a new subsection after the Forces section.
"""

import re
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "services"))

from equipment_resolver import extract_equipment_from_scenario_forces
from historical_context_service import get_historical_context, format_historical_context_paragraph

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BOOKS_PATH = PROJECT_ROOT / "books"

# Battle to quarter mapping
BATTLE_QUARTERS = {
    'compass': '1940q4',
    'sonnenblume': '1941q1',
    'battleaxe': '1941q2',
    'crusader': '1941q4',
    'gazala': '1942q2',
    'tobruk': '1942q2',
    'first_alamein': '1942q3',
    'alam_halfa': '1942q3',
    'second_alamein': '1942q4',
    'torch': '1942q4',
    'tunisia': '1943q1',
    'mareth': '1943q1',
}


def extract_scenario_data(content: str):
    """Extract nations and units from scenario markdown."""
    data = {'nations': [], 'units_text': ''}

    # Extract nations
    nation_matches = re.findall(r'\*\*Nation\*\*:\s*([\w\s\(\)]+)', content, re.IGNORECASE)
    for nation in nation_matches:
        data['nations'].append(nation.strip().lower())

    # Extract all unit lists
    units_sections = re.findall(r'\*\*Units\*\*:\n((?:- .+\n?)+)', content)
    if units_sections:
        data['units_text'] = '\n'.join(units_sections)

    return data


def add_historical_context_to_scenario(scenario_path: Path, battle: str) -> bool:
    """
    Add historical context section to a scenario file.

    Args:
        scenario_path: Path to scenario markdown file
        battle: Battle name for quarter lookup

    Returns:
        True if updated, False if already has context or couldn't add
    """
    with open(scenario_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has historical context
    if '### Historical Context' in content or '## Historical Context' in content:
        return False

    # Extract scenario data
    scenario_data = extract_scenario_data(content)

    if not scenario_data['nations'] or not scenario_data['units_text']:
        print(f"  [SKIP] {scenario_path.name} - Missing nations or units")
        return False

    # Get quarter for this battle
    quarter = BATTLE_QUARTERS.get(battle.lower())
    if not quarter:
        print(f"  [SKIP] {scenario_path.name} - Unknown battle: {battle}")
        return False

    # Extract equipment
    equipment_list = extract_equipment_from_scenario_forces(scenario_data['units_text'])

    if not equipment_list:
        print(f"  [SKIP] {scenario_path.name} - No equipment extracted")
        return False

    # Get historical context
    equipment_names = [e['display_name'] for e in equipment_list]
    context = get_historical_context(equipment_names, quarter, scenario_data['nations'])

    if not context:
        print(f"  [SKIP] {scenario_path.name} - No historical context found")
        return False

    # Format context paragraph
    context_text = format_historical_context_paragraph(context)

    # Build historical context section
    historical_section = f"""
### Historical Context

{context_text}

"""

    # Find insertion point (after the second ### heading in FORCES section)
    # Pattern: Find the end of the second "### {NATION} FORCES" section
    forces_sections = list(re.finditer(r'### .+ FORCES\n', content))

    if len(forces_sections) < 2:
        print(f"  [SKIP] {scenario_path.name} - Couldn't find both force sections")
        return False

    # Find the end of the second forces section (before next ## or end of file)
    second_forces_start = forces_sections[1].end()
    next_section = re.search(r'\n##\s+', content[second_forces_start:])

    if next_section:
        insertion_point = second_forces_start + next_section.start()
    else:
        insertion_point = len(content)

    # Insert historical context
    updated_content = (
        content[:insertion_point] +
        "\n" + historical_section +
        content[insertion_point:]
    )

    # Write updated content
    with open(scenario_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    return True


def process_battle(battle_name: str) -> tuple:
    """
    Process all scenarios for a battle.

    Returns:
        (updated_count, skipped_count, total_count)
    """
    battle_path = BOOKS_PATH / battle_name / "book" / "src" / "scenarios"

    if not battle_path.exists():
        print(f"[SKIP] Battle not found: {battle_name}")
        return (0, 0, 0)

    scenario_files = sorted(battle_path.glob("scenario_*.md"))

    if not scenario_files:
        print(f"[SKIP] No scenarios found in: {battle_name}")
        return (0, 0, 0)

    updated = 0
    skipped = 0

    print(f"\n{battle_name.upper()} ({len(scenario_files)} scenarios)")
    print("=" * 60)

    for scenario_path in scenario_files:
        if add_historical_context_to_scenario(scenario_path, battle_name):
            print(f"  [UPDATED] {scenario_path.name}")
            updated += 1
        else:
            skipped += 1

    return (updated, skipped, len(scenario_files))


def main():
    """Process all 12 battles and update scenarios."""
    print("Adding Historical Context to MDBook Scenarios")
    print("=" * 60)

    battles = [
        'compass', 'sonnenblume', 'battleaxe', 'crusader',
        'gazala', 'tobruk', 'first_alamein', 'alam_halfa',
        'second_alamein', 'torch', 'tunisia', 'mareth'
    ]

    total_updated = 0
    total_skipped = 0
    total_scenarios = 0

    for battle in battles:
        updated, skipped, total = process_battle(battle)
        total_updated += updated
        total_skipped += skipped
        total_scenarios += total

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Updated: {total_updated}")
    print(f"Skipped: {total_skipped}")
    print("=" * 60)


if __name__ == "__main__":
    main()
