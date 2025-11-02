#!/usr/bin/env python3
"""
BattleGroup Book Structure Setup
Creates complete directory structure for all 4 battle books

Phase 9B Step 6 Part 2: Directory Structure Setup
"""

import os
import json
import sys
from pathlib import Path

# Windows-safe print function
def safe_print(text):
    """Print text with ASCII fallback for Windows console"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace Unicode characters with ASCII equivalents
        text = text.replace('✓', 'OK').replace('✅', '[DONE]').replace('⏸️', '[PAUSE]').replace('🎯', '[TARGET]')
        print(text.encode('ascii', 'replace').decode('ascii'))

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BOOKS_DIR = PROJECT_ROOT / "books"

# Book definitions
BOOKS = {
    "battleaxe": {
        "title": "Operation Battleaxe",
        "subtitle": "June 1941 - The 88mm Surprise",
        "quarter": "1941-Q2",
        "scenario_count": 8,
        "description": "British offensive to relieve Tobruk meets devastating German 88mm anti-tank guns"
    },
    "crusader": {
        "title": "Operation Crusader",
        "subtitle": "November-December 1941 - The Largest Desert Battle",
        "quarter": "1941-Q4",
        "scenario_count": 12,
        "description": "Massive British offensive to relieve Tobruk featuring Totensonntag tank battle"
    },
    "gazala": {
        "title": "The Battle of Gazala",
        "subtitle": "May-June 1942 - Rommel's Masterpiece",
        "quarter": "1942-Q2",
        "scenario_count": 15,
        "description": "Rommel's left-hook maneuver, Free French at Bir Hacheim, fall of Tobruk"
    },
    "first_alamein": {
        "title": "First Battle of El Alamein",
        "subtitle": "July 1942 - The Defensive Stalemate",
        "quarter": "1942-Q3",
        "scenario_count": 10,
        "description": "Rommel's offensive finally halted, Commonwealth defensive masterpiece"
    }
}

def create_directory_structure():
    """Create complete directory structure for all books"""
    safe_print("=" * 70)
    safe_print("BattleGroup Book Structure Setup")
    safe_print("Phase 9B Step 6 Part 2: Directory Structure")
    safe_print("=" * 70)
    safe_print("")

    # Create books root directory
    BOOKS_DIR.mkdir(exist_ok=True)
    safe_print(f"OK Created books root: {BOOKS_DIR}")
    safe_print("")

    total_dirs = 0
    total_files = 0

    for book_key, book_info in BOOKS.items():
        safe_print(f"Setting up: {book_info['title']}")
        safe_print(f"  Scenarios: {book_info['scenario_count']}")
        safe_print("")

        book_root = BOOKS_DIR / book_key
        book_root.mkdir(exist_ok=True)

        # Create main directories
        directories = [
            # MDBook structure
            book_root / "book" / "src" / "scenarios",
            book_root / "book" / "src" / "army_lists",
            book_root / "book" / "src" / "datacards" / "vehicles",
            book_root / "book" / "src" / "datacards" / "guns",
            book_root / "book" / "src" / "special_rules",
            book_root / "book" / "src" / "appendices",
            book_root / "book" / "src" / "chapter1",
            book_root / "book" / "src" / "chapter2",

            # LaTeX structure
            book_root / "latex",

            # Images
            book_root / "images" / "battles",
            book_root / "images" / "miniatures",
            book_root / "images" / "maps",
            book_root / "images" / "diagrams",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            total_dirs += 1

        # Create book.toml (MDBook config)
        book_toml = book_root / "book" / "book.toml"
        if not book_toml.exists():
            create_book_toml(book_toml, book_info)
            total_files += 1
            safe_print(f"  OK Created book.toml")

        # Create SUMMARY.md (table of contents template)
        summary_md = book_root / "book" / "src" / "SUMMARY.md"
        if not summary_md.exists():
            create_summary_md(summary_md, book_info)
            total_files += 1
            safe_print(f"  OK Created SUMMARY.md template")

        # Create introduction template
        intro_md = book_root / "book" / "src" / "intro.md"
        if not intro_md.exists():
            create_intro_md(intro_md, book_info)
            total_files += 1
            safe_print(f"  OK Created intro.md template")

        # Create chapter templates
        for chapter_num in [1, 2]:
            chapter_dir = book_root / "book" / "src" / f"chapter{chapter_num}"
            create_chapter_templates(chapter_dir, chapter_num, book_info)
            total_files += 3  # Each chapter has 3 templates
        safe_print(f"  OK Created chapter templates")

        # Create scenario placeholders
        create_scenario_placeholders(
            book_root / "book" / "src" / "scenarios",
            book_info['scenario_count']
        )
        total_files += book_info['scenario_count']
        safe_print(f"  OK Created {book_info['scenario_count']} scenario placeholders")

        # Create special rules templates
        create_special_rules_templates(book_root / "book" / "src" / "special_rules")
        total_files += 3
        safe_print(f"  OK Created special rules templates")

        # Create appendices templates
        create_appendices_templates(book_root / "book" / "src" / "appendices")
        total_files += 3
        safe_print(f"  OK Created appendices templates")

        # Create README for images
        create_images_readme(book_root / "images")
        total_files += 1
        safe_print(f"  OK Created images README")

        # Create LaTeX template
        latex_main = book_root / "latex" / f"{book_key}.tex"
        if not latex_main.exists():
            create_latex_template(latex_main, book_info)
            total_files += 1
            safe_print(f"  OK Created LaTeX template")

        safe_print("")

    safe_print("=" * 70)
    safe_print(f"[DONE] Setup Complete!")
    safe_print(f"   Total directories created: {total_dirs}")
    safe_print(f"   Total files created: {total_files}")
    safe_print(f"   Books ready for content generation")
    safe_print("=" * 70)

def create_book_toml(filepath: Path, book_info: dict):
    """Create MDBook configuration file"""
    content = f'''[book]
title = "{book_info['title']}"
description = "{book_info['description']}"
authors = ["North Africa TO&E Builder", "Claude Code"]
language = "en"
multilingual = false
src = "src"

[build]
build-dir = "book"
create-missing = true

[output.html]
default-theme = "rust"
preferred-dark-theme = "navy"
git-repository-url = ""
git-repository-icon = "fa-github"

[output.html.print]
enable = true

[output.html.fold]
enable = true
level = 1

[output.html.search]
enable = true
limit-results = 30
teaser-word-count = 30
use-boolean-and = true
boost-title = 2
boost-hierarchy = 1
boost-paragraph = 1
expand = true
heading-split-level = 3
copy-js = true

[preprocessor.index]
enable = true

[preprocessor.links]
enable = true
'''
    filepath.write_text(content, encoding='utf-8')

def create_summary_md(filepath: Path, book_info: dict):
    """Create table of contents template"""
    content = f'''# {book_info['title']}

[Introduction](./intro.md)

# Historical Context

- [Strategic Situation](./chapter1/strategic_situation.md)
- [Historical Overview](./chapter1/historical_overview.md)
- [Orders of Battle](./chapter1/orders_of_battle.md)

# Scenarios

- [Scenarios Overview](./scenarios/overview.md)
'''

    # Add scenario links
    for i in range(1, book_info['scenario_count'] + 1):
        content += f'  - [Scenario {i}](./scenarios/scenario_{i:02d}.md)\n'

    content += '''
# Forces

- [British Forces](./army_lists/british.md)
- [German Forces](./army_lists/german.md)
'''

    # Add Italian/French forces based on book
    if book_info['quarter'] >= "1941-Q2":
        content += '- [Italian Forces](./army_lists/italian.md)\n'
    if "gazala" in str(filepath):
        content += '- [Free French Forces](./army_lists/french.md)\n'

    content += '''
# Equipment Datacards

- [Vehicles](./chapter2/vehicles.md)
- [Guns](./chapter2/guns.md)
- [Defensive Structures](./chapter2/defences.md)
- [Fire Support](./chapter2/fire_support.md)

# Special Rules

- [Terrain Rules](./special_rules/terrain.md)
- [Scenario Special Rules](./special_rules/scenarios.md)
- [National Special Rules](./special_rules/nations.md)

# Appendices

- [Appendix A: Quick Reference](./appendices/appendix_a.md)
- [Appendix B: Designer's Notes](./appendices/appendix_b.md)
- [Appendix C: Historical Sources](./appendices/appendix_c.md)
'''
    filepath.write_text(content, encoding='utf-8')

def create_intro_md(filepath: Path, book_info: dict):
    """Create introduction template"""
    content = f'''# {book_info['title']}

## {book_info['subtitle']}

{book_info['description']}

---

## About This Book

This book contains {book_info['scenario_count']} historical scenarios for BattleGroup WW2, covering the {book_info['title']} in North Africa ({book_info['quarter']}).

Each scenario includes:
- Historical background and context
- Detailed force rosters with exact equipment
- Terrain setup and deployment
- Victory conditions and special rules
- Designer's notes

## How to Use This Book

1. **Choose a Scenario**: Browse the scenarios section
2. **Read Historical Context**: Understand the battle background
3. **Build Forces**: Use the army lists and datacards
4. **Set Up Terrain**: Follow the terrain maps
5. **Play**: Use BattleGroup rules with scenario special rules

## Force Organization

All forces are based on historical Table of Organization & Equipment (TO&E) data extracted from primary sources including unit war diaries, official histories, and divisional records.

Equipment statistics use the BattleGroup game system values calculated from historical specifications.

---

**Period Covered**: {book_info['quarter']}

**Scenarios**: {book_info['scenario_count']} complete scenarios

**Nations**: British/Commonwealth, German, Italian forces

**Scale**: Patrol to battalion level (400-1500 points)

---

*Generated with Claude Code - North Africa TO&E Builder*
*Phase 9B: BattleGroup Book Generation System*
'''
    filepath.write_text(content, encoding='utf-8')

def create_chapter_templates(chapter_dir: Path, chapter_num: int, book_info: dict):
    """Create chapter template files"""

    if chapter_num == 1:
        # Strategic Situation
        (chapter_dir / "strategic_situation.md").write_text(f'''# Strategic Situation - {book_info['quarter']}

## North Africa Theater

[Strategic overview of North Africa theater in {book_info['quarter']}]

## Axis Forces

[Overview of German and Italian forces in theater]

## British/Commonwealth Forces

[Overview of British and Commonwealth forces in theater]

## Strategic Context

[Why this battle was fought, strategic objectives both sides]
''', encoding='utf-8')

        # Historical Overview
        (chapter_dir / "historical_overview.md").write_text(f'''# Historical Overview: {book_info['title']}

## The Battle

[Detailed historical narrative of the battle]

## Timeline

[Key dates and events]

## Outcome

[Battle results and strategic impact]

## Lessons Learned

[Tactical and operational lessons from the battle]
''', encoding='utf-8')

        # Orders of Battle
        (chapter_dir / "orders_of_battle.md").write_text(f'''# Orders of Battle - {book_info['title']}

## British/Commonwealth Forces

[List of British divisions, brigades, and major units]

## German Forces

[List of German divisions and major units]

## Italian Forces

[List of Italian divisions and major units]
''', encoding='utf-8')

    elif chapter_num == 2:
        # Equipment datacards chapter
        (chapter_dir / "vehicles.md").write_text('''# Vehicle Datacards

[Vehicle datacards will be generated here using datacard_generator.py]

Equipment statistics from equipment_battlegroup database.
''', encoding='utf-8')

        (chapter_dir / "guns.md").write_text('''# Gun Datacards

[Gun datacards will be generated here using datacard_generator.py]

Equipment statistics from equipment_battlegroup and bg_reference_guns databases.
''', encoding='utf-8')

        (chapter_dir / "defences.md").write_text('''# Defensive Structures

[Defensive structure datacards will be generated here]
''', encoding='utf-8')

def create_scenario_placeholders(scenarios_dir: Path, count: int):
    """Create scenario placeholder files"""

    # Overview file
    (scenarios_dir / "overview.md").write_text(f'''# Scenarios Overview

This book contains {count} scenarios covering the battle.

Each scenario includes:
- **Historical Context**: What happened and why
- **Forces**: Exact unit composition from Phase 6 TO&E data
- **Terrain**: Detailed setup with maps
- **Objectives**: Victory conditions for both sides
- **Special Rules**: Scenario-specific rules
- **Historical Outcome**: What actually happened

## Scenario List

[Scenario summaries will be added here]

## Difficulty Ratings

- ⭐ Beginner-friendly
- ⭐⭐ Intermediate
- ⭐⭐⭐ Advanced
- ⭐⭐⭐⭐ Expert (large/complex scenarios)

## Time Estimates

- Patrol/Company (400-800 pts): 2-3 hours
- Battalion (800-1200 pts): 3-4 hours
- Battalion+ (1200-1800 pts): 4-5 hours
- Multi-battalion (1800+ pts): 5-6 hours
''', encoding='utf-8')

    # Individual scenario placeholders
    for i in range(1, count + 1):
        scenario_file = scenarios_dir / f"scenario_{i:02d}.md"
        scenario_file.write_text(f'''# Scenario {i}: [Title TBD]

**Date**: [TBD]
**Location**: [TBD]
**Scale**: [TBD]

## Historical Context

[Historical background will be added from scenario_research.md]

## Forces

### Attacker
[Force roster will be generated from Phase 6 units]

### Defender
[Force roster will be generated from Phase 6 units]

## Terrain Setup

[Terrain map and setup instructions]

## Deployment

[Deployment zones and rules]

## Objectives

[Victory conditions for both sides]

## Special Rules

[Scenario-specific special rules]

## Historical Outcome

[What actually happened in history]

## Designer's Notes

[Balancing notes, suggestions, variants]

---

*Scenario {i} of {count}*
''', encoding='utf-8')

def create_special_rules_templates(rules_dir: Path):
    """Create special rules template files"""

    (rules_dir / "terrain.md").write_text('''# Terrain Special Rules

## Desert Terrain

### Open Desert
- Movement: No penalty for vehicles
- Cover: None
- Line of Sight: Unlimited (dust and haze may apply)

### Rocky Ground
- Movement: -2" for vehicles
- Cover: Soft cover for infantry
- Line of Sight: Blocks LOS at ground level

### Escarpment/Ridge
- Movement: Impassable for vehicles except at designated passes
- Cover: Hard cover for units on reverse slope
- Line of Sight: Blocks LOS, units on crest visible

### Wadi (Dry Riverbed)
- Movement: -4" for vehicles crossing, movement along wadi normal
- Cover: Hard cover for units in wadi
- Line of Sight: Blocks LOS to units in wadi from ground level

### Sand Dunes
- Movement: -4" for vehicles, infantry -2"
- Cover: Soft cover
- Line of Sight: Blocks LOS, crest provides observation

## Environmental Effects

### Dust and Haze
- Long range (30"+) shooting: -1 to hit
- Affects observation for artillery

### Desert Storm
- Visibility reduced to 20"
- All shooting: -1 to hit
- Movement: -2" all units

### Heat
- Water supply considerations (scenario-specific)
- Affects vehicle reliability (scenario-specific)
''', encoding='utf-8')

    (rules_dir / "scenarios.md").write_text('''# Scenario Special Rules

## Common Special Rules

### Night Fighting
- Visibility limited to 12" first turn, increases +6" per turn
- Shooting beyond visibility range impossible
- Close combat likely

### Minefield
- Movement through: Test for each unit
- Failed test: Unit stops, takes casualties
- Engineer teams can clear lanes

### Fortified Position
- Defenders in prepared positions: +1 cover
- May include trenches, dugouts, barbed wire
- Barbed wire: Reduces movement by half

### Hull-Down Positions
- Tanks in prepared positions: +1 armor save
- Requires preparation time or pre-existing positions

### Air Support
- Stuka dive bombers (Axis)
- Hurricane/Kittyhawk fighter-bombers (British)
- Arrival on random turn, random target selection

### Artillery Barrage
- Pre-game bombardment: Affects defender morale
- Off-board artillery: Available as fire support
- Ammunition limits may apply

### Supply Issues
- Limited ammunition (scenario-specific)
- Fuel shortages (scenario-specific)
- Water shortages (scenario-specific)
''', encoding='utf-8')

    (rules_dir / "nations.md").write_text('''# National Special Rules

## British/Commonwealth

### British
- Steady Under Fire: Morale re-rolls
- Tea Break: Rally phase bonus (when appropriate)

### Australian
- Aggressive Infantry: Bonus in close combat
- Night Fighting: Expertise in night operations

### New Zealand
- Combined Arms: Infantry-tank cooperation bonus
- Determined: Bonus morale for objectives

### Indian
- Mountain Fighters: Bonus in rough terrain
- Disciplined: Rally bonus

### South African
- Defensive Experts: Bonus in defensive positions
- Motorized: Movement bonus for motorized units

## German

### Wehrmacht
- Tactical Excellence: First shot bonus
- Stormtroopers: Assault bonus
- Combined Arms Doctrine: Tank-infantry coordination

### Afrika Korps Veterans
- Desert Fighters: Expertise in desert warfare
- Aggressive Tactics: Counterattack bonus

## Italian

### Regio Esercito
- Defensive: Bonus when defending prepared positions
- Artillery Support: Good artillery coordination

### Bersaglieri
- Fast Moving: Movement bonus
- Aggressive: Bonus in assault

## Free French

### 1st Free French Brigade
- Determined Defenders: Morale bonus when defending
- Foreign Legion: Elite troops, combat bonuses
- Desert Adapted: Expertise in desert warfare
''', encoding='utf-8')

def create_appendices_templates(appendices_dir: Path):
    """Create appendices template files"""

    (appendices_dir / "appendix_a.md").write_text('''# Appendix A: Quick Reference

## BattleGroup Core Rules Summary

[Quick reference tables for BattleGroup rules]

## Weapon Ranges

[Table of common weapon ranges]

## Armor Penetration Scale

[Reference for armor penetration values]

## Movement Rates

[Table of movement rates by vehicle type]

## Special Rules Index

[Alphabetical index of all special rules used in scenarios]
''', encoding='utf-8')

    (appendices_dir / "appendix_b.md").write_text('''# Appendix B: Designer's Notes

## Historical Accuracy vs Game Balance

[Discussion of how historical accuracy balanced with playability]

## Force Construction

[Notes on how forces were constructed from Phase 6 TO&E data]

## Points Values

[Discussion of points calculation methodology]

## Scenario Design Philosophy

[Approach to creating balanced, historical scenarios]

## Variant Rules

[Optional rules for different play styles]

## Campaign System

[Rules for linking scenarios into campaigns]
''', encoding='utf-8')

    (appendices_dir / "appendix_c.md").write_text('''# Appendix C: Historical Sources

## Primary Sources

[List of war diaries, official histories used]

## Secondary Sources

[List of historical books referenced]

## Unit Records

[Sources for unit TO&E data]

## Equipment Specifications

[Sources for equipment data]

## Recommended Reading

[Further reading on North Africa campaign]

## Online Resources

[Links to historical archives, databases]
''', encoding='utf-8')

def create_images_readme(images_dir: Path):
    """Create README for images directory"""
    content = '''# Images Directory

## Structure

- **battles/** - Historical photographs from the battle
- **miniatures/** - Painted miniature photography for scenarios
- **maps/** - Deployment maps and terrain diagrams
- **diagrams/** - Special diagrams (unit organization, etc.)

## Image Sources

### Historical Photos
- Imperial War Museum (IWM) - Public domain
- National Archives - Public domain
- Library of Congress - Public domain
- Australian War Memorial - Public domain

### Miniatures Photos
- To be added: Photography of painted miniatures
- Scale: 15mm recommended
- Terrain: Desert boards

### Maps
- Generated from scenario terrain setups
- Deployment zone diagrams
- Objective locations

## Image Naming Convention

Format: `{type}_{scenario_number}_{description}.{ext}`

Examples:
- `battle_01_fort_capuzzo.jpg` - Historical photo, scenario 1
- `mini_01_deployment.jpg` - Miniatures photo, scenario 1 deployment
- `map_01_terrain.png` - Terrain map, scenario 1
- `diagram_forces_british.png` - Force organization diagram

## Copyright

All images must be public domain or properly licensed.
Historical photos: Use only public domain sources.
Miniatures: Original photography only.
'''
    (images_dir / "README.md").write_text(content, encoding='utf-8')

def create_latex_template(filepath: Path, book_info: dict):
    """Create LaTeX template for PDF generation"""
    content = f'''\\documentclass[11pt,letterpaper,twoside]{{book}}

% Packages
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
\\usepackage{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{fancyhdr}}
\\usepackage{{titlesec}}
\\usepackage{{tocloft}}
\\usepackage{{hyperref}}
\\usepackage{{xcolor}}

% Page geometry
\\geometry{{
    letterpaper,
    left=1in,
    right=1in,
    top=1in,
    bottom=1in,
    headheight=14pt
}}

% Colors (desert theme)
\\definecolor{{deserttan}}{{RGB}}{{210, 180, 140}}
\\definecolor{{desertsand}}{{RGB}}{{237, 201, 175}}
\\definecolor{{darktan}}{{RGB}}{{139, 115, 85}}

% Headers and footers
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[LE,RO]{{\\thepage}}
\\fancyhead[RE]{{{book_info['title']}}}
\\fancyhead[LO]{{\\leftmark}}

% Title formatting
\\titleformat{{\\chapter}}[display]
  {{\\normalfont\\huge\\bfseries\\color{{darktan}}}}{{\\chaptertitlename\\ \\thechapter}}{{20pt}}{{\\Huge}}

% Hyperlinks
\\hypersetup{{
    colorlinks=true,
    linkcolor=darktan,
    filecolor=darktan,
    urlcolor=darktan,
    pdftitle={{{book_info['title']}}},
    pdfauthor={{North Africa TOE Builder}},
}}

% Document
\\begin{{document}}

% Title page
\\begin{{titlepage}}
    \\centering
    \\vspace*{{2cm}}
    {{\\Huge\\bfseries {book_info['title']}\\par}}
    \\vspace{{1cm}}
    {{\\Large {book_info['subtitle']}\\par}}
    \\vspace{{2cm}}
    {{\\Large BattleGroup North Africa\\par}}
    {{\\large Historical Scenarios for Miniature Wargaming\\par}}
    \\vfill
    {{\\large Generated with Claude Code\\par}}
    {{\\large North Africa TO&E Builder\\par}}
    \\vspace{{1cm}}
\\end{{titlepage}}

% Table of contents
\\tableofcontents

% Include chapters
% (Chapters will be generated from markdown and converted to LaTeX)

\\chapter{{Introduction}}
% Include intro.tex

\\chapter{{Historical Context}}
% Include chapter1 sections

\\chapter{{Scenarios}}
% Include all scenario files

\\chapter{{Forces}}
% Include army lists

\\chapter{{Equipment}}
% Include datacards

\\chapter{{Special Rules}}
% Include special rules

\\appendix
\\chapter{{Quick Reference}}
% Include appendix A

\\chapter{{Designer's Notes}}
% Include appendix B

\\chapter{{Historical Sources}}
% Include appendix C

\\end{{document}}
'''
    filepath.write_text(content, encoding='utf-8')

if __name__ == "__main__":
    create_directory_structure()
