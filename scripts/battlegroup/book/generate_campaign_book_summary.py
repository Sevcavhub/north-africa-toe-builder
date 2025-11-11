#!/usr/bin/env python3
"""
Generate comprehensive SUMMARY.md for North Africa Campaign Book
Links all 688 ground forces chapters organized by nation and quarter
"""

from pathlib import Path
import re

def extract_quarter_unit(filename):
    """Extract quarter and unit name from chapter filename"""
    # Format: chapter_[nation]_[quarter]_[unit_name].md
    match = re.match(r'chapter_(\w+)_(\d{4}q\d)_(.+)\.md', filename)
    if match:
        nation, quarter, unit = match.groups()
        # Clean unit name: replace underscores with spaces, title case
        unit_display = unit.replace('_', ' ').title()
        return nation, quarter, unit_display
    return None, None, None

def generate_summary():
    """Generate SUMMARY.md with all chapters properly linked"""

    chapters_dir = Path('D:/north-africa-toe-builder/data/output/chapters')
    chapters = sorted(chapters_dir.glob('chapter_*.md'))

    # Group chapters by nation, then by quarter
    by_nation = {
        'british': {},
        'german': {},
        'italian': {},
        'american': {},
        'french': {}
    }

    for ch in chapters:
        nation, quarter, unit = extract_quarter_unit(ch.name)
        if nation and quarter and unit:
            if quarter not in by_nation[nation]:
                by_nation[nation][quarter] = []
            by_nation[nation][quarter].append({
                'filename': ch.name,
                'unit': unit,
                'quarter': quarter
            })

    # Build SUMMARY.md content
    lines = []
    lines.append("# North Africa Campaign 1940-1943\n")
    lines.append("\n")
    lines.append("[Introduction](./intro.md)\n")
    lines.append("\n")

    # Strategic Overview section
    lines.append("# Strategic Overview\n")
    lines.append("\n")

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
        ('1943q2', '1943-Q2: Final Victory - Axis Surrender in Tunisia')
    ]

    for qtr, title in quarters:
        lines.append(f"- [{title}](./quarter_overviews/{qtr}.md)\n")
    lines.append("\n")

    # Ground Forces sections by nation
    nation_titles = {
        'british': 'British and Commonwealth Forces',
        'german': 'German Forces',
        'italian': 'Italian Forces',
        'american': 'American Forces',
        'french': 'French Forces'
    }

    for nation in ['british', 'german', 'italian', 'american', 'french']:
        if not by_nation[nation]:
            continue

        lines.append(f"# {nation_titles[nation]}\n")
        lines.append("\n")

        # Sort quarters chronologically
        sorted_quarters = sorted(by_nation[nation].keys())

        for quarter in sorted_quarters:
            units = sorted(by_nation[nation][quarter], key=lambda x: x['unit'])

            if units:
                # Quarter header
                quarter_display = quarter.replace('q', '-Q').upper()
                lines.append(f"## {quarter_display}\n")
                lines.append("\n")

                # List all units for this quarter
                for unit_data in units:
                    rel_path = f"./chapters/{unit_data['filename']}"
                    lines.append(f"- [{unit_data['unit']}]({rel_path})\n")
                lines.append("\n")

    # Appendices section
    lines.append("---\n")
    lines.append("\n")
    lines.append("[Methodology](./appendices/methodology.md)\n")
    lines.append("[Bibliography](./appendices/bibliography.md)\n")
    lines.append("[Glossary](./appendices/glossary.md)\n")
    lines.append("[Abbreviations](./appendices/abbreviations.md)\n")

    # Write SUMMARY.md
    summary_path = Path('D:/north-africa-toe-builder/north_africa_campaign_book/src/SUMMARY.md')
    summary_path.write_text(''.join(lines), encoding='utf-8')

    print(f"Generated SUMMARY.md with {len(chapters)} chapters")
    print(f"British/Commonwealth: {len([c for q in by_nation['british'].values() for c in q])} chapters")
    print(f"German: {len([c for q in by_nation['german'].values() for c in q])} chapters")
    print(f"Italian: {len([c for q in by_nation['italian'].values() for c in q])} chapters")
    print(f"American: {len([c for q in by_nation['american'].values() for c in q])} chapters")
    print(f"French: {len([c for q in by_nation['french'].values() for c in q])} chapters")

if __name__ == '__main__':
    generate_summary()
