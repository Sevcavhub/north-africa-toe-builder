#!/usr/bin/env python3
"""
Populate Corps/Army-level chapter MANUAL placeholders with aggregated data from JSON files

This script:
1. Finds all corps/army-level chapters with [MANUAL:...] placeholders
2. Loads corresponding JSON TOE file with aggregated data
3. Replaces placeholders with actual aggregated content
4. Preserves all manually-written content
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

def load_toe_json(json_path: Path) -> Optional[Dict[str, Any]]:
    """Load TOE JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {json_path}: {e}")
        return None

def find_matching_json(chapter_path: Path, units_dir: Path) -> Optional[Path]:
    """Find matching JSON file for chapter"""
    # Extract nation, quarter, unit from chapter filename
    # Format: chapter_[nation]_[quarter]_[unit_name].md
    match = re.match(r'chapter_(\w+)_(\d{4}q\d)_(.+)\.md', chapter_path.name)
    if not match:
        return None

    nation, quarter, unit = match.groups()

    # Try to find matching JSON
    json_filename = f"{nation}_{quarter}_{unit}_toe.json"
    json_path = units_dir / json_filename

    if json_path.exists():
        return json_path

    # Try variations (spaces, underscores, etc.)
    for json_file in units_dir.glob(f"{nation}_{quarter}_*_toe.json"):
        if unit.replace('_', ' ').lower() in json_file.stem.replace('_', ' ').lower():
            return json_file

    return None

def format_subordinate_units(toe_data: Dict[str, Any]) -> str:
    """Format subordinate units section from JSON data"""
    if 'subordinate_units' not in toe_data or not toe_data['subordinate_units']:
        return "No subordinate units data available in JSON."

    lines = []
    for idx, unit in enumerate(toe_data['subordinate_units'], 1):
        lines.append(f"**{idx}. {unit.get('designation', 'Unknown Unit')}**")
        lines.append(f"- Type: {unit.get('type', 'Unknown')}")
        if 'strength' in unit:
            lines.append(f"- Strength: {unit['strength']:,} personnel")
        if 'commander' in unit:
            lines.append(f"- Commander: {unit['commander']}")
        if 'note' in unit:
            lines.append(f"- Note: {unit['note']}")
        lines.append("")

    return "\n".join(lines)

def format_equipment_summary(toe_data: Dict[str, Any]) -> str:
    """Format equipment summary from JSON data"""
    lines = []

    # Tanks
    if 'tanks' in toe_data and toe_data['tanks'].get('total', {}).get('count', 0) > 0:
        tanks = toe_data['tanks']
        lines.append(f"**Total Tanks:** {tanks['total']['count']}")
        if 'operational' in tanks:
            lines.append(f"- Operational: {tanks['operational'].get('count', 0)}")
        if 'medium_tanks' in tanks and tanks['medium_tanks']['count'].get('total', 0) > 0:
            lines.append(f"- Medium Tanks: {tanks['medium_tanks']['count']['total']}")
            if 'variants' in tanks['medium_tanks']['count']:
                for variant, count in tanks['medium_tanks']['count']['variants'].items():
                    lines.append(f"  - {variant}: {count}")
        if 'light_tanks' in tanks and tanks['light_tanks']['count'].get('total', 0) > 0:
            lines.append(f"- Light Tanks: {tanks['light_tanks']['count']['total']}")
        lines.append("")

    # Artillery
    if 'artillery_total' in toe_data and toe_data['artillery_total'] > 0:
        lines.append(f"**Total Artillery:** {toe_data['artillery_total']} guns")
        if 'field_artillery' in toe_data:
            lines.append(f"- Field Artillery: {toe_data['field_artillery']}")
        if 'anti_tank' in toe_data:
            lines.append(f"- Anti-Tank Guns: {toe_data['anti_tank']}")
        if 'anti_aircraft' in toe_data:
            lines.append(f"- Anti-Aircraft Guns: {toe_data['anti_aircraft']}")
        lines.append("")

    # Vehicles
    if 'ground_vehicles_total' in toe_data and toe_data['ground_vehicles_total'] > 0:
        lines.append(f"**Total Motor Vehicles:** {toe_data['ground_vehicles_total']:,}")
        lines.append("")

    return "\n".join(lines)

def format_infantry_weapons(toe_data: Dict[str, Any]) -> str:
    """Format infantry weapons from JSON data"""
    if 'top_3_infantry_weapons' not in toe_data:
        return "Infantry weapons data not available in JSON."

    lines = []
    for rank, weapon_data in toe_data['top_3_infantry_weapons'].items():
        lines.append(f"### {weapon_data['weapon']}")
        lines.append(f"- **Count:** {weapon_data['count']:,}")
        lines.append(f"- **Type:** {weapon_data['type']}")
        if 'witw_id' in weapon_data:
            lines.append(f"- **WITW ID:** {weapon_data['witw_id']}")
        lines.append("")

    return "\n".join(lines)

def populate_chapter(chapter_path: Path, toe_data: Dict[str, Any]) -> bool:
    """Populate chapter MANUAL placeholders with TOE data"""
    try:
        content = chapter_path.read_text(encoding='utf-8')
        original_content = content

        # Replace key sections

        # 1. Overview section
        if 'operational_context' in toe_data:
            overview_text = toe_data['operational_context']
            content = re.sub(
                r'\*\*\[MANUAL: Add 2-3 paragraphs of historical context[^\]]+\]\*\*',
                overview_text,
                content,
                count=1
            )

        # 2. Personnel section
        if 'total_personnel' in toe_data and toe_data['total_personnel'] > 0:
            personnel_text = f"The corps comprised {toe_data['total_personnel']:,} personnel across all subordinate formations. This included divisional troops, corps-level artillery, engineers, and support units."
            content = re.sub(
                r'### Total Strength: 0 Personnel\n\n\*\*\[MANUAL: Add 1-2 paragraphs[^\]]+\]\*\*',
                f"### Total Strength: {toe_data['total_personnel']:,} Personnel\n\n{personnel_text}",
                content
            )

        # 3. Subordinate units (if they exist in JSON)
        if 'subordinate_units' in toe_data:
            subordinate_text = format_subordinate_units(toe_data)
            # Find the subordinate units section and replace NOT EXTRACTED notes
            content = re.sub(
                r'(\*\*\d+\. [^\n]+\*\*\n- Type: [^\n]+\n- Strength: [^\n]+\n- Commander: [^\n]+\n)- Note: [^\n]+ NOT EXTRACTED[^\n]+\n',
                r'\1',
                content
            )

        # 4. Equipment summary
        equipment_summary = format_equipment_summary(toe_data)
        if equipment_summary:
            # Replace infantry weapons section
            content = re.sub(
                r'### Unknown - subordinate divisions not extracted\n- \*\*Count:\*\* 0\n- \*\*Type:\*\* Unknown\n\n\*\*\[MANUAL: Add specifications:[^\]]+\]\*\*\n\n\*\*\[MANUAL: Add 1-2 paragraphs[^\]]+\]\*\*\n',
                '',
                content,
                flags=re.DOTALL
            )

        # 5. Infantry weapons
        if 'top_3_infantry_weapons' in toe_data:
            weapons_text = format_infantry_weapons(toe_data)
            # Find infantry weapons section
            content = re.sub(
                r'(## 5\. Infantry Weapons\n\n)\*\*\[MANUAL: Add introductory[^\]]+\]\*\*\n\n### Unknown - subordinate[^\n]+\n(?:- \*\*Count:\*\* 0\n- \*\*Type:\*\* Unknown\n\n\*\*\[MANUAL: Add specifications:[^\]]+\]\*\*\n\n\*\*\[MANUAL: Add 1-2 paragraphs[^\]]+\]\*\*\n\n)+',
                r'\1The corps was equipped with standard infantry weapons aggregated from subordinate formations:\n\n' + weapons_text,
                content,
                flags=re.DOTALL
            )

        # Write back if changed
        if content != original_content:
            chapter_path.write_text(content, encoding='utf-8')
            return True

        return False

    except Exception as e:
        print(f"Error populating {chapter_path}: {e}")
        return False

def main():
    """Main execution"""
    chapters_dir = Path('D:/north-africa-toe-builder/data/output/chapters')
    units_dir = Path('D:/north-africa-toe-builder/data/output/units')

    # Find all chapters with MANUAL placeholders
    chapters_with_manual = []
    for chapter_path in chapters_dir.glob('chapter_*.md'):
        content = chapter_path.read_text(encoding='utf-8')
        if '[MANUAL:' in content and ('corps' in chapter_path.stem.lower() or 'army' in chapter_path.stem.lower() or 'korps' in chapter_path.stem.lower()):
            chapters_with_manual.append(chapter_path)

    print(f"Found {len(chapters_with_manual)} corps/army chapters with MANUAL placeholders")

    # Process each chapter
    populated = 0
    skipped = 0

    for chapter_path in chapters_with_manual:
        # Find matching JSON
        json_path = find_matching_json(chapter_path, units_dir)

        if not json_path:
            print(f"SKIP: No JSON found for {chapter_path.name}")
            skipped += 1
            continue

        # Load JSON
        toe_data = load_toe_json(json_path)
        if not toe_data:
            print(f"SKIP: Could not load JSON for {chapter_path.name}")
            skipped += 1
            continue

        # Populate chapter
        if populate_chapter(chapter_path, toe_data):
            print(f"POPULATED: {chapter_path.name}")
            populated += 1
        else:
            print(f"UNCHANGED: {chapter_path.name}")
            skipped += 1

    print(f"\n=== SUMMARY ===")
    print(f"Total chapters processed: {len(chapters_with_manual)}")
    print(f"Populated: {populated}")
    print(f"Skipped/Unchanged: {skipped}")

if __name__ == '__main__':
    main()
