#!/usr/bin/env python3
"""
Populate Corps/Army-level chapters with aggregated data from JSON files (v2)
Focuses on 77 units that have actual aggregated personnel/equipment data
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

def load_json(json_path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {json_path}: {e}")
        return None

def find_chapter_for_json(json_file: Path, chapters_dir: Path) -> Optional[Path]:
    """Find matching chapter file for a JSON file"""
    # Extract components from JSON filename
    # Format: [nation]_[quarter]_[unit]_toe.json
    stem = json_file.stem.replace('_toe', '')
    parts = stem.split('_')

    if len(parts) < 3:
        return None

    nation = parts[0]
    quarter = parts[1]
    unit_parts = parts[2:]

    # Try to find matching chapter
    # Format: chapter_[nation]_[quarter]_[unit].md

    # Try exact match first
    exact_name = f"chapter_{nation}_{quarter}_{'_'.join(unit_parts)}.md"
    exact_path = chapters_dir / exact_name
    if exact_path.exists():
        return exact_path

    # Try fuzzy matching
    pattern = f"chapter_{nation}_{quarter}_*.md"
    for chapter_file in chapters_dir.glob(pattern):
        chapter_unit = chapter_file.stem.replace(f'chapter_{nation}_{quarter}_', '')

        # Normalize both for comparison
        chapter_norm = chapter_unit.lower().replace('-', '_').replace("'", '').replace(' ', '_')
        json_norm = '_'.join(unit_parts).lower().replace('-', '_').replace("'", '').replace(' ', '_')

        # Check if they match or if one contains the other
        if chapter_norm == json_norm or chapter_norm in json_norm or json_norm in chapter_norm:
            return chapter_file

    return None

def create_personnel_summary(data: Dict[str, Any]) -> str:
    """Create personnel summary text"""
    total = data.get('total_personnel', 0)
    if total == 0:
        return ""

    officers = data.get('officers', 0)
    ncos = data.get('ncos', 0)
    enlisted = data.get('enlisted', 0)

    text = f"The formation comprised **{total:,} personnel** across all subordinate units and attached formations. "

    if officers > 0:
        text += f"This included {officers:,} officers ({officers*100//total if total > 0 else 0}%), "
        text += f"{ncos:,} NCOs ({ncos*100//total if total > 0 else 0}%), "
        text += f"and {enlisted:,} enlisted personnel ({enlisted*100//total if total > 0 else 0}%).\n\n"

    text += f"Personnel were distributed across divisional combat units, corps-level artillery and anti-tank battalions, "
    text += f"engineer regiments, signals units, supply and transport columns, medical services, and headquarters staff."

    return text

def create_equipment_summary(data: Dict[str, Any]) -> str:
    """Create equipment summary text"""
    lines = []

    # Tanks
    tanks_total = data.get('tanks', {}).get('total', {}).get('count', 0)
    if tanks_total > 0:
        lines.append(f"\n### Armored Fighting Vehicles\n")
        lines.append(f"**Total Tanks:** {tanks_total}")

        operational = data.get('tanks', {}).get('operational', {}).get('count', 0)
        if operational > 0:
            lines.append(f"- Operational: {operational} ({operational*100//tanks_total}%)")

        medium = data.get('tanks', {}).get('medium_tanks', {}).get('count', {}).get('total', 0)
        if medium > 0:
            lines.append(f"- Medium Tanks: {medium}")

        light = data.get('tanks', {}).get('light_tanks', {}).get('count', {}).get('total', 0)
        if light > 0:
            lines.append(f"- Light Tanks: {light}")

    # Artillery
    artillery_total = data.get('artillery_total', 0)
    if artillery_total > 0:
        lines.append(f"\n### Artillery\n")
        lines.append(f"**Total Artillery:** {artillery_total} guns")

        field = data.get('field_artillery', 0)
        if field > 0:
            lines.append(f"- Field Artillery: {field} pieces")

        at_guns = data.get('anti_tank', 0)
        if at_guns > 0:
            lines.append(f"- Anti-Tank Guns: {at_guns}")

        aa_guns = data.get('anti_aircraft', 0)
        if aa_guns > 0:
            lines.append(f"- Anti-Aircraft Guns: {aa_guns}")

    # Vehicles
    vehicles = data.get('ground_vehicles_total', 0)
    if vehicles > 0:
        lines.append(f"\n### Motor Transport\n")
        lines.append(f"**Total Motor Vehicles:** {vehicles:,}")
        lines.append(f"\nMajority were trucks for supply and troop transport, with specialized vehicles for artillery towing, "
                    f"signals equipment, engineering tools, and command vehicles.")

    return '\n'.join(lines)

def create_weapons_summary(data: Dict[str, Any]) -> str:
    """Create infantry weapons summary"""
    if 'top_3_infantry_weapons' not in data:
        return ""

    lines = []
    for rank, weapon_data in data['top_3_infantry_weapons'].items():
        weapon = weapon_data.get('weapon', '')
        count = weapon_data.get('count', 0)
        weapon_type = weapon_data.get('type', '')

        if count > 0 and 'unknown' not in weapon.lower():
            lines.append(f"\n### {weapon}")
            lines.append(f"- **Count:** {count:,}")
            lines.append(f"- **Type:** {weapon_type}")
            lines.append("")

    if lines:
        intro = "The formation's infantry units were equipped with:\n"
        return intro + '\n'.join(lines)

    return ""

def populate_chapter(chapter_path: Path, data: Dict[str, Any]) -> bool:
    """Populate chapter with aggregated data"""
    try:
        content = chapter_path.read_text(encoding='utf-8')
        original_content = content

        # 1. Replace total personnel section
        total_personnel = data.get('total_personnel', 0)
        if total_personnel > 0:
            personnel_summary = create_personnel_summary(data)

            # Find and replace the personnel section
            content = re.sub(
                r'(### Total Strength: )0( Personnel\n\n)\*\*\[MANUAL: Add 1-2 paragraphs[^\]]+\]\*\*',
                f'\\1{total_personnel:,}\\2{personnel_summary}',
                content
            )

            # Update officer count
            officers = data.get('officers', 0)
            if officers > 0:
                content = re.sub(
                    r'(### Officer Corps: )0( Officers \()0\.0(% of total\))',
                    f'\\1{officers:,}\\2{officers*100//total_personnel if total_personnel > 0 else 0}\\3',
                    content
                )

            # Update NCO count
            ncos = data.get('ncos', 0)
            if ncos > 0:
                content = re.sub(
                    r'(### Non-Commissioned Officers: )0( NCOs \()0\.0(% of total\))',
                    f'\\1{ncos:,}\\2{ncos*100//total_personnel if total_personnel > 0 else 0}\\3',
                    content
                )

            # Update enlisted count
            enlisted = data.get('enlisted', 0)
            if enlisted > 0:
                content = re.sub(
                    r'(### Enlisted Personnel: )0( \()0\.0(% of total\))',
                    f'\\1{enlisted:,}\\2{enlisted*100//total_personnel if total_personnel > 0 else 0}\\3',
                    content
                )

        # 2. Replace vehicles section
        vehicles = data.get('ground_vehicles_total', 0)
        if vehicles > 0:
            content = re.sub(
                r'(### Total Motor Vehicles: )0',
                f'\\1{vehicles:,}',
                content
            )

        # 3. Replace artillery section
        artillery = data.get('artillery_total', 0)
        if artillery > 0:
            content = re.sub(
                r'(### Total Artillery: )0( Guns)',
                f'\\1{artillery}\\2',
                content
            )

        # 4. Add equipment summary after Infantry Weapons section if data available
        equipment_summary = create_equipment_summary(data)
        if equipment_summary:
            # Find the Infantry Weapons section and add summary
            content = re.sub(
                r'(## 5\. Infantry Weapons\n\n)\*\*\[MANUAL: Add introductory paragraph[^\]]+\]\*\*',
                f'\\1Aggregated equipment across all subordinate formations:{equipment_summary}\n',
                content
            )

        # 5. Replace infantry weapons "Unknown" entries
        weapons_summary = create_weapons_summary(data)
        if weapons_summary:
            # Remove the "Unknown - subordinate divisions not extracted" sections
            content = re.sub(
                r'### Unknown - subordinate divisions not extracted\n- \*\*Count:\*\* 0\n- \*\*Type:\*\* Unknown\n\n\*\*\[MANUAL: Add specifications:[^\]]+\]\*\*\n\n\*\*\[MANUAL: Add 1-2 paragraphs[^\]]+\]\*\*\n\n',
                '',
                content,
                flags=re.DOTALL
            )

        # Write back if changed
        if content != original_content:
            chapter_path.write_text(content, encoding='utf-8')
            return True

        return False

    except Exception as e:
        print(f"Error populating {chapter_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    units_dir = Path('D:/north-africa-toe-builder/data/output/units')
    chapters_dir = Path('D:/north-africa-toe-builder/data/output/chapters')

    # Find all JSON files with corps/army-level data
    corps_jsons = []
    for json_file in units_dir.glob('*_toe.json'):
        data = load_json(json_file)
        if data and data.get('organization_level') in ['corps', 'army']:
            if data.get('total_personnel', 0) > 0:
                corps_jsons.append((json_file, data))

    print(f"Found {len(corps_jsons)} corps/army JSON files with aggregated data\n")

    # Process each JSON
    populated = 0
    skipped = 0

    for json_file, data in corps_jsons:
        chapter_path = find_chapter_for_json(json_file, chapters_dir)

        if not chapter_path:
            print(f"SKIP: No chapter found for {json_file.name}")
            skipped += 1
            continue

        if '[MANUAL:' not in chapter_path.read_text(encoding='utf-8'):
            print(f"SKIP: No MANUAL placeholders in {chapter_path.name}")
            skipped += 1
            continue

        if populate_chapter(chapter_path, data):
            unit_name = data.get('unit_designation', 'Unknown')
            personnel = data.get('total_personnel', 0)
            print(f"POPULATED: {chapter_path.name} ({unit_name}: {personnel:,} personnel)")
            populated += 1
        else:
            print(f"UNCHANGED: {chapter_path.name}")
            skipped += 1

    print(f"\n=== SUMMARY ===")
    print(f"Total JSON files with data: {len(corps_jsons)}")
    print(f"Chapters populated: {populated}")
    print(f"Skipped/Unchanged: {skipped}")

if __name__ == '__main__':
    main()
