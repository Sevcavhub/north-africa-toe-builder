"""
Update SUMMARY.md files with actual scenario names and create Forces pages.

This script:
1. Extracts scenario names from scenario markdown files
2. Updates SUMMARY.md to show actual names instead of "Scenario 1"
3. Creates placeholder Forces/TO&E pages (to be populated later)
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BOOKS_PATH = PROJECT_ROOT / "books"

BATTLES = [
    'compass', 'sonnenblume', 'battleaxe', 'crusader',
    'gazala', 'tobruk', 'first_alamein', 'alam_halfa',
    'second_alamein', 'torch', 'tunisia', 'mareth'
]


def extract_scenario_title(scenario_path: Path) -> str:
    """Extract scenario title from markdown file."""
    with open(scenario_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        # Format: # 1. Dawn at Fort Capuzzo
        match = re.match(r'^#\s+(.+)$', first_line)
        if match:
            return match.group(1)
        return scenario_path.stem.replace('_', ' ').title()


def update_summary_md(battle: str):
    """Update SUMMARY.md with actual scenario names."""
    book_path = BOOKS_PATH / battle / "book"
    summary_path = book_path / "src" / "SUMMARY.md"
    scenarios_path = book_path / "src" / "scenarios"

    if not summary_path.exists():
        print(f"  [SKIP] {battle} - No SUMMARY.md")
        return False

    # Read current SUMMARY.md
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract scenario files and their titles
    scenario_files = sorted(scenarios_path.glob("scenario_*.md"))

    updated = False
    for scenario_file in scenario_files:
        scenario_num = scenario_file.stem.replace('scenario_', '')
        actual_title = extract_scenario_title(scenario_file)

        # Replace generic "Scenario X" with actual title
        # Try different spacing patterns
        patterns = [
            f'  - [Scenario {scenario_num}](./scenarios/{scenario_file.name})',
            f'- [Scenario {scenario_num}](./scenarios/{scenario_file.name})',
        ]

        replacement = f'  - [{actual_title}](./scenarios/{scenario_file.name})'

        for pattern in patterns:
            if pattern in content:
                content = content.replace(pattern, replacement)
                updated = True
                break

    if updated:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False


def create_forces_placeholder(battle: str):
    """Create placeholder Forces/TO&E pages."""
    book_path = BOOKS_PATH / battle / "book"
    army_lists_path = book_path / "src" / "army_lists"

    # Create directory if it doesn't exist
    army_lists_path.mkdir(parents=True, exist_ok=True)

    # Determine which nations are in this battle
    # For now, create all three - we'll populate based on actual data later
    nations = ['british', 'german', 'italian']

    created = []
    for nation in nations:
        nation_file = army_lists_path / f"{nation}.md"

        if not nation_file.exists():
            content = f"""# {nation.title()} Forces

## Organization

*This section will contain detailed Table of Organization & Equipment (TO&E) data for {nation.title()} forces in this battle.*

**Status**: TO&E extraction in progress. This page will be populated with:

- Corps and Division organization
- Regiment and Battalion breakdowns
- Company and Platoon compositions
- Equipment allocations by unit type
- Variant-level detail (e.g., Panzer III Ausf J vs Ausf L)

## Historical Units

*Historical units that fought in this battle will be listed here with their organizational hierarchy.*

## Equipment Summary

*Equipment used by {nation.title()} forces in this battle - see Equipment Datacards section for detailed stats.*

---

*Note: This content is generated from Phase 6 unit extraction data and will be populated in a future update.*
"""
            with open(nation_file, 'w', encoding='utf-8') as f:
                f.write(content)
            created.append(nation)

    return created


def process_battle(battle: str):
    """Process a single battle."""
    print(f"\n{battle.upper()}")
    print("=" * 60)

    # Update SUMMARY.md
    if update_summary_md(battle):
        print("  [OK] Updated SUMMARY.md with scenario names")
    else:
        print("  [SKIP] SUMMARY.md already updated or not found")

    # Create Forces placeholders
    created = create_forces_placeholder(battle)
    if created:
        print(f"  [OK] Created Forces pages: {', '.join(created)}")
    else:
        print("  [SKIP] Forces pages already exist")


def main():
    """Process all battles."""
    print("Updating MDBook SUMMARY.md and creating Forces pages")
    print("=" * 60)

    for battle in BATTLES:
        process_battle(battle)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Rebuild books: cd books/<battle>/book && mdbook build")
    print("2. Commit changes: git add -A && git commit")
    print("3. Push to GitHub: git push origin main")


if __name__ == "__main__":
    main()
