#!/usr/bin/env python3
"""
BattleGroup Book Structure Generator

Generates complete battle books in multiple formats (MDBook, LaTeX/PDF, HTML)
from structured YAML definition and assembled content.

Usage:
    python book_structure_generator.py --battle battleaxe --format mdbook
    python book_structure_generator.py --battle kursk --format latex --output books/
    python book_structure_generator.py --config custom_structure.yaml --format all
"""

import argparse
import os
import sys
import json
import sqlite3
# import yaml  # Not used in current implementation
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def safe_print(text: str):
    """Print text with Windows console encoding safety"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to ASCII
        print(text.encode('ascii', 'replace').decode('ascii'))


@dataclass
class BookMetadata:
    """Metadata for a battle book"""
    title: str
    subtitle: str
    author: str
    version: str
    date: str
    battle_name: str
    operation: str
    date_range: str
    quarter: str
    location: str
    attacker_nation: str
    defender_nation: str
    scenario_count: int = 8


class ContentAssembler:
    """Assembles content from various sources into book sections"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def get_datacards(self, equipment_type: str, nations: List[str] = None) -> List[Dict]:
        """Get datacards for specified equipment type and nations"""
        if not self.conn:
            self.connect()

        query = """
        SELECT canonical_id, display_name, category, nation,
               armor_front, armor_side, armor_rear, armor_turret,
               off_road_movement, road_movement,
               he_dice, he_target,
               ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
               points_regular, points_inexperienced, points_veteran, points_elite,
               br_regular, br_inexperienced, br_veteran, br_elite,
               special_rules
        FROM equipment_battlegroup
        WHERE 1=1
        """

        params = []

        if equipment_type == "vehicle":
            query += " AND category IN ('Tank', 'AFV', 'Self-Propelled Gun', 'Armored Car', 'Halftrack', 'Truck')"
        elif equipment_type == "gun":
            query += " AND category IN ('Anti-Tank Gun', 'Artillery', 'Anti-Aircraft Gun', 'Infantry Gun')"
        elif equipment_type == "defence":
            query += " AND category = 'Defence'"
        elif equipment_type == "fire_support":
            query += " AND category = 'Fire Support'"

        if nations:
            placeholders = ','.join(['?' for _ in nations])
            query += f" AND nation IN ({placeholders})"
            params.extend(nations)

        query += " ORDER BY nation, display_name"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_special_rules(self, rule_ids: List[str] = None) -> List[Dict]:
        """Get special rules"""
        if not self.conn:
            self.connect()

        query = """
        SELECT rule_id, name, description, category, game_effect
        FROM bg_special_rules
        WHERE 1=1
        """

        params = []
        if rule_ids:
            placeholders = ','.join(['?' for _ in rule_ids])
            query += f" AND rule_id IN ({placeholders})"
            params.extend(rule_ids)

        query += " ORDER BY category, name"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_unit_data(self, nation: str, quarter: str) -> List[Dict]:
        """Get Phase 6 unit data for army lists"""
        # This will parse Phase 6 JSON files from data/output/units/
        unit_dir = project_root / "data" / "output" / "units"

        if not unit_dir.exists():
            return []

        units = []
        pattern = f"{nation}_{quarter}_*.json"

        for unit_file in unit_dir.glob(pattern):
            try:
                with open(unit_file, 'r', encoding='utf-8') as f:
                    unit_data = json.load(f)
                    units.append(unit_data)
            except Exception as e:
                print(f"Warning: Could not load {unit_file}: {e}")

        return units


class MDBookGenerator:
    """Generates MDBook format output"""

    def __init__(self, metadata: BookMetadata, content: ContentAssembler):
        self.metadata = metadata
        self.content = content

    def generate(self, output_dir: Path) -> bool:
        """Generate complete MDBook structure"""
        try:
            # Create directory structure
            src_dir = output_dir / "src"
            src_dir.mkdir(parents=True, exist_ok=True)

            # Generate SUMMARY.md
            self._generate_summary(src_dir)

            # Generate chapters
            self._generate_intro(src_dir)
            self._generate_chapter1(src_dir)
            self._generate_chapter2(src_dir)
            self._generate_chapter3(src_dir)
            self._generate_chapter4(src_dir)
            self._generate_chapter5(src_dir)
            self._generate_appendices(src_dir)

            # Generate book.toml
            self._generate_book_toml(output_dir)

            safe_print(f"[OK] MDBook structure generated in {output_dir}")
            return True

        except Exception as e:
            safe_print(f"[ERROR] Error generating MDBook: {e}")
            return False

    def _generate_summary(self, src_dir: Path):
        """Generate SUMMARY.md file"""
        template_path = project_root / "scripts" / "battlegroup" / "templates" / "mdbook_summary.txt"

        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Generate scenario list
        scenario_list = []
        for i in range(1, self.metadata.scenario_count + 1):
            scenario_list.append(f"- [Scenario {i}](./scenarios/scenario_{i}.md)")

        # Substitute placeholders
        content = template.format(
            attacker_nation_full=self._get_nation_full_name(self.metadata.attacker_nation),
            defender_nation_full=self._get_nation_full_name(self.metadata.defender_nation),
            attacker_nation=self.metadata.attacker_nation,
            defender_nation=self.metadata.defender_nation,
            vehicle_sections="",  # Can add sub-sections later
            gun_sections="",
            scenario_list="\n".join(scenario_list)
        )

        # Write SUMMARY.md
        with open(src_dir / "SUMMARY.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_intro(self, src_dir: Path):
        """Generate introduction page"""
        content = f"""# {self.metadata.title}

{self.metadata.subtitle}

**Battle**: {self.metadata.battle_name}
**Operation**: {self.metadata.operation}
**Dates**: {self.metadata.date_range}
**Location**: {self.metadata.location}

---

## About This Book

This book contains historically accurate scenarios, army lists, and equipment data for
{self.metadata.battle_name} using the BattleGroup wargaming rules.

All data is extracted from primary historical sources including divisional orders of battle,
war diaries, and field manuals. Equipment statistics are calculated using validated conversion
formulas that translate historical specifications into BattleGroup game mechanics.

## Contents

- **Historical Context**: Strategic situation and orders of battle
- **Equipment Reference**: Complete datacards for all vehicles, guns, and support
- **Army Lists**: Force organization and unit options for both sides
- **Scenarios**: {self.metadata.scenario_count} historical scenarios with deployment maps
- **Special Rules**: Theatre-specific rules for North Africa

## How to Use

Each scenario is designed to be playable as a standalone game or linked together in a
campaign. Force lists allow you to build custom armies within historical restrictions,
or use the pre-generated forces included with each scenario.

---

**Version**: {self.metadata.version}
**Generated**: {self.metadata.date}
**Author**: {self.metadata.author}
"""

        with open(src_dir / "intro.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_chapter1(self, src_dir: Path):
        """Generate Chapter 1: Historical Context"""
        chapter_dir = src_dir / "chapter1"
        chapter_dir.mkdir(exist_ok=True)

        # Historical Overview
        historical_content = f"""# Historical Overview

## {self.metadata.battle_name}

**Operation**: {self.metadata.operation}
**Dates**: {self.metadata.date_range}
**Theatre**: {self.metadata.location}

### Strategic Context

[Placeholder: Historical narrative about the strategic situation leading to this battle]

### Forces Involved

**{self._get_nation_full_name(self.metadata.attacker_nation)}**:
- [Placeholder: Major units and commanders]

**{self._get_nation_full_name(self.metadata.defender_nation)}**:
- [Placeholder: Major units and commanders]

### Battle Outcome

[Placeholder: Results and consequences of the battle]

---

*This section synthesizes information from multiple primary sources. See Appendix B for full bibliography.*
"""

        with open(chapter_dir / "historical_overview.md", 'w', encoding='utf-8') as f:
            f.write(historical_content)

        # Strategic Situation
        strategic_content = f"""# Strategic Situation

## Terrain

The terrain around {self.metadata.location} consists of:
- [Placeholder: Terrain description]

## Objectives

**{self._get_nation_full_name(self.metadata.attacker_nation)} Objectives**:
- [Placeholder: Attacker objectives]

**{self._get_nation_full_name(self.metadata.defender_nation)} Objectives**:
- [Placeholder: Defender objectives]

## Weather and Environment

- **Season**: [Placeholder]
- **Temperature**: [Placeholder]
- **Visibility**: [Placeholder]
"""

        with open(chapter_dir / "strategic_situation.md", 'w', encoding='utf-8') as f:
            f.write(strategic_content)

        # Orders of Battle
        oob_content = f"""# Orders of Battle

## {self._get_nation_full_name(self.metadata.attacker_nation)} Forces ({self.metadata.quarter})

[Placeholder: List of units from Phase 6 data]

## {self._get_nation_full_name(self.metadata.defender_nation)} Forces ({self.metadata.quarter})

[Placeholder: List of units from Phase 6 data]

---

*Note: These orders of battle represent the units available during {self.metadata.quarter}.
Equipment and organization changed over time - scenarios will specify which quarter's forces to use.*
"""

        with open(chapter_dir / "orders_of_battle.md", 'w', encoding='utf-8') as f:
            f.write(oob_content)

    def _generate_chapter2(self, src_dir: Path):
        """Generate Chapter 2: Equipment Reference"""
        chapter_dir = src_dir / "chapter2"
        chapter_dir.mkdir(exist_ok=True)

        # Vehicles
        vehicles_content = "# Vehicles\n\n"
        vehicles_content += "This section contains datacards for all vehicles used in this battle.\n\n"
        vehicles_content += "[Placeholder: Vehicle datacards will be generated here]\n\n"
        vehicles_content += "---\n\n"
        vehicles_content += "*Use the datacard_generator.py tool to generate specific vehicle datacards.*\n"

        with open(chapter_dir / "vehicles.md", 'w', encoding='utf-8') as f:
            f.write(vehicles_content)

        # Similar for guns, defences, fire_support...
        for equipment_type in ["guns", "defences", "fire_support"]:
            content = f"# {equipment_type.replace('_', ' ').title()}\n\n"
            content += f"[Placeholder: {equipment_type} datacards]\n"

            with open(chapter_dir / f"{equipment_type}.md", 'w', encoding='utf-8') as f:
                f.write(content)

    def _generate_chapter3(self, src_dir: Path):
        """Generate Chapter 3: Army Lists"""
        # Placeholder - will integrate with army_list_generator.py
        content = f"""# Army Lists

## {self._get_nation_full_name(self.metadata.attacker_nation)} Forces

[Placeholder: Force organization and unit options]

## {self._get_nation_full_name(self.metadata.defender_nation)} Forces

[Placeholder: Force organization and unit options]

---

*Army lists will be generated using the army_list_generator.py tool with Phase 6 unit data.*
"""

        army_file = src_dir / f"{self.metadata.attacker_nation}_forces.md"
        with open(army_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_chapter4(self, src_dir: Path):
        """Generate Chapter 4: Scenarios"""
        scenarios_dir = src_dir / "scenarios"
        scenarios_dir.mkdir(exist_ok=True)

        # Overview
        overview_content = """# Using These Scenarios

## Scenario Format

Each scenario is presented in a 2-page spread format:

**Page 1**:
- Historical situation
- Tactical objectives
- Terrain setup
- Deployment map

**Page 2**:
- Victory conditions
- Special rules
- Force compositions
- Alternative forces

## Linking Scenarios

Scenarios can be played individually or linked together in a campaign.
See Chapter 6 for campaign rules.

## Modifications

Feel free to modify scenarios for your collection, table size, or preferences.
The historical framework is provided as a starting point.
"""

        with open(scenarios_dir / "overview.md", 'w', encoding='utf-8') as f:
            f.write(overview_content)

        # Generate placeholder scenarios
        for i in range(1, self.metadata.scenario_count + 1):
            scenario_content = f"""# Scenario {i}: [Title]

**Date**: [Placeholder]
**Location**: [Placeholder]
**Battle Size**: [Squad/Platoon/Company/Battalion]

## Situation

[Placeholder: Historical situation]

## Forces

**Attacker**: [Points budget]
**Defender**: [Points budget]

## Victory Conditions

[Placeholder]

---

*This scenario will be generated using the historical_scenario_generator.py tool.*
"""

            with open(scenarios_dir / f"scenario_{i}.md", 'w', encoding='utf-8') as f:
                f.write(scenario_content)

    def _generate_chapter5(self, src_dir: Path):
        """Generate Chapter 5: Special Rules"""
        special_dir = src_dir / "special_rules"
        special_dir.mkdir(exist_ok=True)

        # Nation rules
        nations_content = """# Nation-Specific Rules

## British and Commonwealth Forces

[Placeholder: British special rules]

## German Forces

[Placeholder: German special rules]

## Italian Forces

[Placeholder: Italian special rules]

## American Forces

[Placeholder: American special rules]

## Free French Forces

[Placeholder: French special rules]
"""

        with open(special_dir / "nations.md", 'w', encoding='utf-8') as f:
            f.write(nations_content)

        # Terrain rules
        terrain_content = """# North Africa Terrain

## Desert Terrain Types

### Open Desert
- Flat, open sand with minimal cover
- No movement penalties for vehicles
- Infantry count as in the open

### Rocky Desert
- Scattered rocks and boulders
- Light cover for infantry
- Difficult terrain for vehicles

### Escarpment
- Steep cliffs and rock faces
- Impassable to vehicles
- Defensible positions

### Wadi
- Dry riverbeds with sandy bottoms
- Concealment for vehicles
- Dead ground from elevated positions

[Placeholder: Additional terrain types]

## Weather Effects

### Sandstorm (1 in 6 chance, 1942)
- Visibility reduced to 20"
- Aircraft grounded
- Vehicle movement penalties

### Desert Dust Cloud (Always turn 6+, 1942)
- Visibility reduced to 30"
- -1 to hit for shooting

[Placeholder: Additional weather]
"""

        with open(special_dir / "terrain.md", 'w', encoding='utf-8') as f:
            f.write(terrain_content)

        # Scenario rules
        scenarios_content = """# Scenario Special Rules

This section contains special rules that appear in the scenarios.

[Placeholder: Collected from all scenarios]
"""

        with open(special_dir / "scenarios.md", 'w', encoding='utf-8') as f:
            f.write(scenarios_content)

    def _generate_appendices(self, src_dir: Path):
        """Generate appendices"""
        # Appendix A: Quick Reference
        appendix_a = """# Appendix A: Quick Reference Tables

## Armor Penetration Scale

| AP Value | Penetration | Example Guns |
|----------|-------------|--------------|
| 1-2      | Very Light  | 20mm, rifle caliber |
| 3-5      | Light       | 37mm, 40mm, 50mm |
| 6-8      | Medium      | 75mm, 6-pdr |
| 9-11     | Heavy       | 88mm, 17-pdr |
| 12-15    | Very Heavy  | 122mm, large AT guns |

## Movement Rates

| Vehicle Type | Off-Road | Road |
|--------------|----------|------|
| Tracked (light) | 10" | 16" |
| Tracked (medium) | 8" | 12" |
| Tracked (heavy) | 6" | 10" |
| Wheeled | 8" | 16" |
| Half-tracked | 9" | 14" |

[Placeholder: Additional tables]
"""

        with open(src_dir / "appendix_a.md", 'w', encoding='utf-8') as f:
            f.write(appendix_a)

        # Appendix B: Historical Sources
        appendix_b = f"""# Appendix B: Historical Sources

## Primary Sources

[Placeholder: List of primary sources from Phase 6 provenance]

## Secondary Sources

[Placeholder: Books, articles, websites]

## Data Methodology

All unit compositions and equipment data are extracted from:
- War diaries and unit histories
- Field manuals and technical documents
- Post-war divisional histories

Equipment statistics are calculated using validated conversion formulas
with 90-100% accuracy against official BattleGroup reference data.

See PROJECT_SCOPE.md and PHASE_9B_SESSION_SUMMARY.md for complete
methodology documentation.
"""

        with open(src_dir / "appendix_b.md", 'w', encoding='utf-8') as f:
            f.write(appendix_b)

        # Appendix C: Force Roster Sheet
        appendix_c = """# Appendix C: Force Roster Sheet

```
═══════════════════════════════════════════════════════════════════
                    BATTLEGROUP FORCE ROSTER
═══════════════════════════════════════════════════════════════════

Nation: __________________    Battle: _________________________

Points Budget: __________     Battle Rating: __________


UNIT                           EXP    PTS    BR    NOTES
────────────────────────────────────────────────────────────────────
HQ SECTION:



INFANTRY:



ARMOR:



SUPPORT:



════════════════════════════════════════════════════════════════════
TOTAL POINTS: _________     TOTAL BR: _________
════════════════════════════════════════════════════════════════════
```

*Photocopy this page for your games.*
"""

        with open(src_dir / "appendix_c.md", 'w', encoding='utf-8') as f:
            f.write(appendix_c)

        # Index
        index_content = """# Index

[Auto-generated index will be inserted here]

---

*To generate a searchable index, use MDBook's search feature or build with --index flag.*
"""

        with open(src_dir / "index.md", 'w', encoding='utf-8') as f:
            f.write(index_content)

    def _generate_book_toml(self, output_dir: Path):
        """Generate book.toml configuration"""
        toml_content = f"""[book]
title = "{self.metadata.title}"
author = "{self.metadata.author}"
description = "{self.metadata.subtitle}"
language = "en"

[build]
build-dir = "book"

[output.html]
default-theme = "light"
preferred-dark-theme = "navy"
git-repository-url = "https://github.com/yourusername/north-africa-toe-builder"
edit-url-template = "https://github.com/yourusername/north-africa-toe-builder/edit/main/{{{{path}}}}"

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

[output.html.print]
enable = true
"""

        with open(output_dir / "book.toml", 'w', encoding='utf-8') as f:
            f.write(toml_content)

    def _get_nation_full_name(self, nation_code: str) -> str:
        """Convert nation code to full name"""
        names = {
            "german": "German",
            "british": "British & Commonwealth",
            "american": "American",
            "italian": "Italian",
            "french": "Free French"
        }
        return names.get(nation_code, nation_code.title())


class LaTeXGenerator:
    """Generates LaTeX format for print output"""

    def __init__(self, metadata: BookMetadata, content: ContentAssembler):
        self.metadata = metadata
        self.content = content

    def generate(self, output_dir: Path) -> bool:
        """Generate LaTeX document"""
        try:
            # For LaTeX, we'll generate the content directly rather than use the template
            # because the LaTeX syntax conflicts with Python's format() placeholders

            content = self._generate_latex_document()

            # Write main .tex file
            output_file = output_dir / f"{self.metadata.battle_name.lower().replace(' ', '_')}.tex"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            safe_print(f"[OK] LaTeX document generated: {output_file}")
            safe_print(f"   To compile: cd {output_dir} && pdflatex {output_file.name}")

            return True

        except Exception as e:
            safe_print(f"[ERROR] Error generating LaTeX: {e}")
            return False

    def _generate_latex_document(self) -> str:
        """Generate LaTeX document content"""
        title = self._escape_latex(self.metadata.title)
        subtitle = self._escape_latex(self.metadata.subtitle)
        author = self._escape_latex(self.metadata.author)
        battle_name = self._escape_latex(self.metadata.battle_name)
        date_range = self._escape_latex(self.metadata.date_range)

        latex = f"""% BattleGroup North Africa - {battle_name}
% LaTeX document for professional print output

\\documentclass[11pt,letterpaper,twoside]{{book}}

% Packages
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{libertine}}
\\usepackage[margin=0.75in]{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{longtable}}
\\usepackage{{booktabs}}
\\usepackage{{multicol}}
\\usepackage{{fancyhdr}}
\\usepackage{{titlesec}}
\\usepackage{{tocloft}}
\\usepackage{{enumitem}}
\\usepackage{{xcolor}}
\\usepackage{{tikz}}
\\usepackage{{mdframed}}
\\usepackage{{hyperref}}

% Color definitions (desert theme)
\\definecolor{{deserttan}}{{RGB}}{{210,180,140}}
\\definecolor{{desertsand}}{{RGB}}{{237,201,175}}
\\definecolor{{desertbrown}}{{RGB}}{{139,90,43}}

% Page style
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[LE,RO]{{\\thepage}}
\\fancyhead[RE]{{\\leftmark}}
\\fancyhead[LO]{{\\rightmark}}
\\renewcommand{{\\headrulewidth}}{{0.4pt}}

% Chapter/Section styling
\\titleformat{{\\chapter}}[display]
  {{\\normalfont\\huge\\bfseries\\color{{desertbrown}}}}
  {{\\chaptertitlename\\ \\thechapter}}{{20pt}}{{\\Huge}}

\\titleformat{{\\section}}
  {{\\normalfont\\Large\\bfseries\\color{{desertbrown}}}}
  {{\\thesection}}{{1em}}{{}}

% Hyperlink setup
\\hypersetup{{
  colorlinks=true,
  linkcolor=desertbrown,
  filecolor=desertbrown,
  urlcolor=desertbrown,
  pdftitle={{{title}}},
  pdfauthor={{{author}}}
}}

% Document metadata
\\title{{{title}}}
\\author{{{author}}}
\\date{{{self.metadata.date}}}

\\begin{{document}}

% Title page
\\begin{{titlepage}}
  \\centering
  \\vspace*{{2cm}}

  {{\\Huge\\bfseries {title}\\par}}
  \\vspace{{0.5cm}}
  {{\\Large {subtitle}\\par}}
  \\vspace{{2cm}}

  {{\\large {battle_name}\\par}}
  {{\\large {date_range}\\par}}
  \\vspace{{1cm}}

  \\vfill

  {{\\large {author}\\par}}
  {{\\large Version {self.metadata.version}\\par}}
  {{\\large {self.metadata.date}\\par}}
\\end{{titlepage}}

% Credits
\\chapter*{{Credits}}
\\addcontentsline{{toc}}{{chapter}}{{Credits}}

This book was generated from historical primary sources.

% Table of Contents
\\tableofcontents
\\clearpage

% Preface
\\chapter*{{Preface}}
\\addcontentsline{{toc}}{{chapter}}{{Preface}}

This book contains historically accurate scenarios and army lists for {battle_name}.
All data is extracted from primary sources and converted using validated formulas.

% Main content placeholder
\\chapter{{Historical Context}}

Placeholder for historical overview.

\\chapter{{Equipment Reference}}

Placeholder for equipment datacards.

\\chapter{{Army Lists}}

Placeholder for army lists.

\\chapter{{Scenarios}}

Placeholder for {self.metadata.scenario_count} historical scenarios.

\\chapter{{Special Rules}}

Placeholder for special rules.

% Appendices
\\appendix

\\chapter{{Quick Reference Tables}}

Placeholder for reference tables.

\\chapter{{Historical Sources}}

Placeholder for bibliography.

\\end{{document}}
"""
        return latex

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Generate BattleGroup battle books in multiple formats")

    parser.add_argument('--battle', required=True, help="Battle name (e.g., 'battleaxe', 'kursk')")
    parser.add_argument('--format', choices=['mdbook', 'latex', 'all'], default='mdbook',
                        help="Output format (default: mdbook)")
    parser.add_argument('--output', default='output/books', help="Output directory (default: output/books)")
    parser.add_argument('--config', help="Custom YAML structure file (optional)")
    parser.add_argument('--db', default='database/master_database.db', help="Database path")

    # Battle-specific metadata
    parser.add_argument('--operation', help="Operation name (e.g., 'Operation Battleaxe')")
    parser.add_argument('--dates', help="Date range (e.g., 'June 15-17, 1941')")
    parser.add_argument('--quarter', help="Quarter (e.g., '1941q2')")
    parser.add_argument('--location', help="Location (e.g., 'Halfaya Pass, Libya-Egypt Border')")
    parser.add_argument('--attacker', help="Attacker nation code (e.g., 'british')")
    parser.add_argument('--defender', help="Defender nation code (e.g., 'german')")
    parser.add_argument('--scenarios', type=int, default=8, help="Number of scenarios (default: 8)")

    args = parser.parse_args()

    # Create metadata
    metadata = BookMetadata(
        title=f"{args.battle.title()} - BattleGroup North Africa",
        subtitle="Historical Scenarios and Army Lists",
        author="Generated from Primary Sources",
        version="1.0",
        date=datetime.now().strftime("%B %Y"),
        battle_name=args.battle.title(),
        operation=args.operation or f"Operation {args.battle.title()}",
        date_range=args.dates or "[Date range TBD]",
        quarter=args.quarter or "1941q2",
        location=args.location or "[Location TBD]",
        attacker_nation=args.attacker or "british",
        defender_nation=args.defender or "german",
        scenario_count=args.scenarios
    )

    # Initialize content assembler
    db_path = project_root / args.db
    content = ContentAssembler(str(db_path))

    # Create output directory
    output_dir = Path(args.output) / args.battle
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_print(f"Generating book: {metadata.title}")
    safe_print(f"   Format: {args.format}")
    safe_print(f"   Output: {output_dir}")
    safe_print("")

    # Generate requested format(s)
    success = True

    if args.format in ['mdbook', 'all']:
        safe_print("Generating MDBook format...")
        mdbook_gen = MDBookGenerator(metadata, content)
        success = mdbook_gen.generate(output_dir) and success

    if args.format in ['latex', 'all']:
        safe_print("Generating LaTeX format...")
        latex_gen = LaTeXGenerator(metadata, content)
        success = latex_gen.generate(output_dir) and success

    # Cleanup
    content.close()

    if success:
        safe_print("")
        safe_print("[OK] Book generation complete!")
        safe_print("")
        safe_print("Next steps:")
        if args.format in ['mdbook', 'all']:
            safe_print(f"  1. cd {output_dir}")
            safe_print(f"  2. mdbook build")
            safe_print(f"  3. mdbook serve  (to preview)")
        if args.format in ['latex', 'all']:
            safe_print(f"  1. cd {output_dir}")
            safe_print(f"  2. pdflatex {args.battle}.tex")
        return 0
    else:
        safe_print("")
        safe_print("[ERROR] Book generation failed - see errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
