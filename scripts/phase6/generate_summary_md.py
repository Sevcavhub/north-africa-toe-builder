#!/usr/bin/env python3
"""
Generate SUMMARY.md for North Africa Campaign Book with forces hierarchy.
"""

from pathlib import Path
from collections import defaultdict
import re


def natural_sort_key(s):
    """Natural sort key for alphanumeric strings."""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', str(s))]


def generate_summary():
    """Generate SUMMARY.md with forces hierarchy."""

    forces_dir = Path("D:/north-africa-toe-builder/north_africa_campaign_book/src/forces")
    output_file = Path("D:/north-africa-toe-builder/north_africa_campaign_book/src/SUMMARY.md")

    # Scan all markdown files and organize by nation/echelon/quarter
    structure = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for nation_dir in sorted(forces_dir.iterdir()):
        if not nation_dir.is_dir() or nation_dir.name in ['.', 'README.md']:
            continue

        nation = nation_dir.name

        for echelon_dir in sorted(nation_dir.iterdir()):
            if not echelon_dir.is_dir():
                continue

            echelon = echelon_dir.name

            for md_file in sorted(echelon_dir.glob('*.md'), key=lambda p: natural_sort_key(p.stem)):
                # Extract quarter from filename (e.g., 1942q2_xxx.md)
                filename = md_file.stem
                parts = filename.split('_', 1)
                if len(parts) == 2:
                    quarter, unit_slug = parts
                    # Clean up unit name
                    unit_name = unit_slug.replace('_', ' ').title()
                    rel_path = md_file.relative_to(forces_dir.parent)
                    structure[nation][echelon][quarter].append((unit_name, rel_path))

    # Generate SUMMARY.md content
    lines = []
    lines.append("# North Africa Campaign 1940-1943\n")
    lines.append("[Introduction](./intro.md)\n")
    lines.append("# Strategic Overview\n")

    # Add quarter overviews
    quarters = [
        ('1940q2', '1940-Q2: Italy Enters War'),
        ('1940q3', '1940-Q3: Italian Invasion of Egypt'),
        ('1940q4', '1940-Q4: Operation Compass'),
        ('1941q1', '1941-Q1: Beda Fomm and German Arrival'),
        ('1941q2', '1941-Q2: Operation Battleaxe'),
        ('1941q3', '1941-Q3: Tobruk Siege and Desert Stalemate'),
        ('1941q4', '1941-Q4: Operation Crusader'),
        ('1942q1', '1942-Q1: Rommel\'s Counter-Offensive'),
        ('1942q2', '1942-Q2: Battle of Gazala and Fall of Tobruk'),
        ('1942q3', '1942-Q3: First El Alamein and Alam el Halfa'),
        ('1942q4', '1942-Q4: Second El Alamein and Operation Torch'),
        ('1943q1', '1943-Q1: Tunisia Campaign - Kasserine and Mareth'),
        ('1943q2', '1943-Q2: Final Victory - Axis Surrender in Tunisia'),
    ]

    for q_id, q_title in quarters:
        lines.append(f"- [{q_title}](./quarter_overviews/{q_id}.md)\n")

    # Add forces hierarchy
    lines.append("\n# Forces Organization\n")
    lines.append("- [Forces Overview](./forces/README.md)\n")

    nation_display = {
        'british': 'British and Commonwealth Forces',
        'german': 'German Forces',
        'italian': 'Italian Forces',
        'american': 'American Forces',
        'french': 'French Forces'
    }

    for nation in ['british', 'german', 'italian', 'american', 'french']:
        if nation not in structure:
            continue

        lines.append(f"\n## {nation_display[nation]}\n\n")

        # Just write all units as a flat list (MDBook doesn't support H3 in SUMMARY)
        all_units = []
        for echelon in ['armies', 'corps', 'divisions']:
            if echelon in structure[nation]:
                for quarter in sorted(structure[nation][echelon].keys()):
                    all_units.extend(structure[nation][echelon][quarter])

        # Write all units
        for unit_name, rel_path in all_units:
            # Convert path to use forward slashes for MDBook
            path_str = str(rel_path).replace('\\', '/')
            lines.append(f"- [{unit_name}](./{path_str})\n")

    # Add appendices section
    lines.append("\n# Appendices\n\n")
    lines.append("- [Methodology](./appendices/methodology.md)\n")
    lines.append("- [Bibliography](./appendices/bibliography.md)\n")
    lines.append("- [Glossary](./appendices/glossary.md)\n")
    lines.append("- [Abbreviations](./appendices/abbreviations.md)\n")

    # Write file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"Generated SUMMARY.md with {len(lines)} lines")
    print(f"Nations: {len(structure)}")
    for nation in structure:
        total = sum(len(files) for echelon in structure[nation].values() for files in echelon.values())
        print(f"  {nation}: {total} units")


if __name__ == '__main__':
    generate_summary()
