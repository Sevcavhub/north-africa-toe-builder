"""
Add scale classification to all MDBook scenario files.

Adds "**Scale**: {scale}-level engagement" line to the SITUATION REPORT section
of all 45 scenarios across the 4 battle books.
"""

import json
import re
from pathlib import Path

# Project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
METADATA_PATH = PROJECT_ROOT / "scripts" / "battlegroup" / "web" / "scenario_metadata.json"

def add_scale_to_scenario(scenario_file: Path, scale: str) -> bool:
    """
    Add scale classification to scenario markdown file.

    Args:
        scenario_file: Path to scenario markdown file
        scale: Scale classification (Squad, Platoon, Company, Battalion)

    Returns:
        True if file was modified, False if scale already present
    """
    with open(scenario_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if scale already present
    if re.search(r'\*\*Scale\*\*:', content):
        return False

    # Find the location line and add scale after it
    # Pattern: **Location**: ... \n\n situation_description
    # Insert: **Location**: ... \n**Scale**: {scale}-level engagement\n\n situation_description
    pattern = r'(\*\*Location\*\*:\s*.+?\n)(\n)'
    replacement = rf'\1**Scale**: {scale}-level engagement\n\2'

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(scenario_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True

    return False


def main():
    """Add scale classification to all scenarios."""
    print("Adding scale classification to all MDBook scenarios...\n")

    # Load scenario metadata
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    # Track statistics
    stats = {
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }

    for scenario in scenarios:
        battle = scenario['battle']
        scenario_num = scenario['scenario_number']
        scale = scenario['scale']
        title = scenario['title']

        scenario_file = PROJECT_ROOT / "books" / battle / "book" / "src" / "scenarios" / f"scenario_{scenario_num:02d}.md"

        if not scenario_file.exists():
            print(f"  [ERROR] File not found: {scenario_file.name}")
            stats['errors'] += 1
            continue

        try:
            if add_scale_to_scenario(scenario_file, scale):
                print(f"  [UPDATED] {title[:60]}")
                print(f"    Scale: {scale} | File: {scenario_file.name}")
                stats['updated'] += 1
            else:
                print(f"  [SKIP] {title[:60]} (scale already present)")
                stats['skipped'] += 1

        except Exception as e:
            print(f"  [ERROR] {title[:60]}: {e}")
            stats['errors'] += 1

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Updated:  {stats['updated']:2d} scenarios")
    print(f"Skipped:  {stats['skipped']:2d} scenarios (already had scale)")
    print(f"Errors:   {stats['errors']:2d} scenarios")
    print(f"Total:    {len(scenarios):2d} scenarios")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
