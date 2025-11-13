"""
Classify all scenarios by scale (Squad/Platoon/Company/Battalion)
and generate metadata JSON for use in web and MDBook templates.
"""

import re
import json
from pathlib import Path

# Project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
BOOKS_DIR = PROJECT_ROOT / "books"

# Battle directory mapping
BATTLES = {
    'battleaxe': {
        'name': 'Operation Battleaxe',
        'scenarios': list(range(1, 9))  # 1-8
    },
    'crusader': {
        'name': 'Operation Crusader',
        'scenarios': list(range(1, 13))  # 1-12
    },
    'gazala': {
        'name': 'Battle of Gazala',
        'scenarios': list(range(1, 16))  # 1-15
    },
    'first_alamein': {
        'name': 'First El Alamein',
        'scenarios': list(range(1, 11))  # 1-10
    }
}

def classify_scale(points):
    """
    Classify scenario scale based on points budget.

    Squad: <100 pts (small unit actions, 10-30 men)
    Platoon: 100-500 pts (platoon-level, 30-100 men)
    Company: 500-1500 pts (company-level, 100-300 men)
    Battalion: 1500+ pts (battalion+, 300+ men)
    """
    if points < 100:
        return "Squad"
    elif points < 500:
        return "Platoon"
    elif points < 1500:
        return "Company"
    else:
        return "Battalion"

def parse_scenario(scenario_file):
    """
    Parse scenario markdown file and extract metadata.

    Returns dict with:
    - title: Full scenario title
    - points: Dict of faction: points budget
    - scale: Calculated scale classification
    - nations: List of nations involved
    """
    with open(scenario_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title (first H1 line)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Unknown"

    # Extract all forces sections (handle multi-word faction names like "NEW ZEALAND" or "BRITISH (TOBRUK)")
    forces_pattern = r'###\s+([\w\s\(\)]+?)\s+FORCES.*?Points Budget.*?:\s*(\d+)'
    forces_matches = re.finditer(forces_pattern, content, re.DOTALL | re.IGNORECASE)

    points_by_faction = {}
    nations = set()

    for match in forces_matches:
        faction = match.group(1).upper()
        points = int(match.group(2))
        points_by_faction[faction] = points

        # Extract nation from forces section (handle multi-word nations like "New Zealand", "South African")
        nation_match = re.search(r'\*\*Nation\*\*:\s*([\w\s\(\)]+)', match.group(0), re.IGNORECASE)
        if nation_match:
            nation_name = nation_match.group(1).strip().lower()
            nations.add(nation_name)

    # Calculate scale based on total points (sum of all factions)
    total_points = sum(points_by_faction.values())
    scale = classify_scale(total_points)

    return {
        'title': title,
        'points': points_by_faction,
        'total_points': total_points,
        'scale': scale,
        'nations': sorted(list(nations))
    }

def main():
    """Parse all scenarios and generate scale metadata."""
    print("Classifying all 45 scenarios by scale...\n")

    all_scenarios = []
    stats = {
        'Squad': 0,
        'Platoon': 0,
        'Company': 0,
        'Battalion': 0
    }

    for battle_id, battle_info in BATTLES.items():
        print(f"\n{'='*60}")
        print(f"{battle_info['name']}")
        print(f"{'='*60}")

        for scenario_num in battle_info['scenarios']:
            scenario_file = BOOKS_DIR / battle_id / "book" / "src" / "scenarios" / f"scenario_{scenario_num:02d}.md"

            if not scenario_file.exists():
                print(f"  [MISSING] Scenario {scenario_num:02d}")
                continue

            try:
                metadata = parse_scenario(scenario_file)
                metadata['battle'] = battle_id
                metadata['battle_name'] = battle_info['name']
                metadata['scenario_number'] = scenario_num
                metadata['file_path'] = str(scenario_file.relative_to(PROJECT_ROOT))

                all_scenarios.append(metadata)
                stats[metadata['scale']] += 1

                # Print summary
                points_str = " + ".join([f"{faction}: {pts}" for faction, pts in metadata['points'].items()])
                print(f"  Scenario {scenario_num:02d}: {metadata['title'][:50]}")
                print(f"    Scale: {metadata['scale']:10s} | Total Points: {metadata['total_points']:4d} ({points_str})")
                print(f"    Nations: {', '.join(metadata['nations'])}")

            except Exception as e:
                print(f"  [ERROR] Scenario {scenario_num:02d}: {e}")

    # Print statistics
    print(f"\n{'='*60}")
    print("SCALE DISTRIBUTION")
    print(f"{'='*60}")
    for scale, count in stats.items():
        percentage = (count / len(all_scenarios)) * 100 if all_scenarios else 0
        print(f"{scale:10s}: {count:2d} scenarios ({percentage:5.1f}%)")
    print(f"{'='*60}")
    print(f"TOTAL: {len(all_scenarios)} scenarios")

    # Save metadata JSON
    output_file = SCRIPT_DIR / "scenario_metadata.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_scenarios, f, indent=2)

    print(f"\n[OK] Metadata saved to: {output_file.relative_to(PROJECT_ROOT)}")

    return all_scenarios, stats

if __name__ == '__main__':
    scenarios, stats = main()
