#!/usr/bin/env python3
"""
Test script to integrate forces structure into 1942Q2 quarter overview.
This is a simplified test version to validate the approach before running on all quarters.
"""

import json
from pathlib import Path


def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    # Paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "output" / "units"
    book_dir = project_root / "north_africa_campaign_book" / "src" / "quarter_overviews"

    quarter = "1942q2"

    # Load existing narrative
    narrative_file = book_dir / f"{quarter}.md"
    with open(narrative_file, 'r', encoding='utf-8') as f:
        existing_narrative = f.read()

    print(f"Loaded existing narrative: {len(existing_narrative)} chars")

    # Find Phase 6 JSONs for this quarter
    json_files = sorted(data_dir.glob(f"*_{quarter}_*_toe.json"))
    print(f"\nFound {len(json_files)} JSON files for {quarter}:")
    for jf in json_files:
        print(f"  - {jf.name}")

    # Load German Panzerarmee Afrika (army-level)
    german_army_file = data_dir / f"german_{quarter}_panzerarmee_afrika_toe.json"
    if german_army_file.exists():
        german_army = load_json(german_army_file)
        print(f"\nLoaded German Panzerarmee Afrika:")
        print(f"  Commander: {german_army.get('command', {}).get('commander', {}).get('name', 'Unknown')}")
        print(f"  Personnel: {german_army.get('total_personnel', 0):,}")
        print(f"  Tanks: {german_army.get('tanks', {}).get('total', {}).get('count', 0)}")

    # Simple forces section generation
    forces_section = []
    forces_section.append("\n---\n")
    forces_section.append("\n## Forces Structure\n")
    forces_section.append("\n### German Forces\n")
    forces_section.append("\n#### Panzerarmee Afrika\n")

    commander_data = german_army.get('command', {}).get('commander', {})
    if isinstance(commander_data, dict):
        commander_name = commander_data.get('name', 'Unknown')
        forces_section.append(f"**Commander**: {commander_name}\n")

    total_personnel = german_army.get('total_personnel', 0)
    forces_section.append(f"**Strength**: {total_personnel:,} personnel\n")

    forces_section.append("\n##### Aggregate Equipment Summary\n")

    # Tanks
    tanks_data = german_army.get('tanks', {})
    total_tanks = tanks_data.get('total', {})
    if isinstance(total_tanks, dict):
        tank_count = total_tanks.get('count', 0)
    else:
        tank_count = total_tanks

    if tank_count > 0:
        forces_section.append(f"- **Tanks**: {tank_count:,} total\n")

    # Artillery
    artillery_total = german_army.get('artillery_total', 0)
    if artillery_total > 0:
        forces_section.append(f"- **Artillery**: {artillery_total:,} guns\n")

    # Vehicles
    ground_vehicles = german_army.get('ground_vehicles_total', 0)
    if ground_vehicles > 0:
        forces_section.append(f"- **Vehicles**: {ground_vehicles:,} total\n")

    forces_section.append("\n")
    forces_section.append("*(Full hierarchical breakdown with corps/divisions to be added)*\n")
    forces_section.append("\n---\n")

    forces_content = "".join(forces_section)

    # Find insertion point after "## Strategic Situation"
    strategic_pos = existing_narrative.find("## Strategic Situation")
    if strategic_pos != -1:
        # Find next section (## Major Battles or next ##)
        next_section_pos = existing_narrative.find("\n##", strategic_pos + 22)
        if next_section_pos != -1:
            # Insert forces section
            integrated = existing_narrative[:next_section_pos] + "\n" + forces_content + existing_narrative[next_section_pos:]

            # Write output
            output_file = book_dir / f"{quarter}_integrated_test.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(integrated)

            print(f"\n[OK] Integrated test file written: {output_file}")
            print(f"     Original size: {len(existing_narrative)} chars")
            print(f"     Integrated size: {len(integrated)} chars")
            print(f"     Forces section: {len(forces_content)} chars")
        else:
            print("[ERROR] Could not find next section after Strategic Situation")
    else:
        print("[ERROR] Could not find Strategic Situation section")


if __name__ == "__main__":
    main()
