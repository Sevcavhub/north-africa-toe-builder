#!/usr/bin/env python3
"""
Extract scenario titles from all battle books and generate JavaScript mapping.
"""

import json
from pathlib import Path

# Battles to process
BATTLES = ['battleaxe', 'crusader', 'gazala', 'first_alamein']

def extract_scenario_title(scenario_file):
    """Extract title from scenario markdown file."""
    with open(scenario_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        # Remove markdown heading prefix
        if first_line.startswith('#'):
            return first_line.lstrip('#').strip()
        return first_line

def main():
    """Extract all scenario titles and generate JavaScript mapping."""
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    books_dir = project_root / "books"

    scenario_mapping = {}

    for battle in BATTLES:
        scenarios_dir = books_dir / battle / "book" / "src" / "scenarios"

        if not scenarios_dir.exists():
            print(f"[WARNING] Scenarios directory not found: {scenarios_dir}")
            continue

        # Find all scenario files
        scenario_files = sorted(scenarios_dir.glob("scenario_*.md"))

        battle_scenarios = []
        for scenario_file in scenario_files:
            scenario_id = scenario_file.stem  # e.g., "scenario_01"
            title = extract_scenario_title(scenario_file)
            battle_scenarios.append({
                'id': scenario_id,
                'title': title
            })

        scenario_mapping[battle] = battle_scenarios
        print(f"{battle}: {len(battle_scenarios)} scenarios")

    # Generate JavaScript object
    print("\n" + "=" * 80)
    print("JAVASCRIPT SCENARIO MAPPING")
    print("=" * 80)
    print()
    print("const BATTLE_SCENARIOS = {")
    for battle, scenarios in scenario_mapping.items():
        print(f"    '{battle}': [")
        for scenario in scenarios:
            print(f"        {{ id: '{scenario['id']}', title: '{scenario['title']}' }},")
        print("    ],")
    print("};")
    print()

    # Also output as JSON for reference
    output_file = Path(__file__).parent / "scenario_mapping.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scenario_mapping, f, indent=2)

    print(f"JSON mapping saved to: {output_file}")

if __name__ == '__main__':
    main()
