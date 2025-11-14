"""
Populate empty Forces pages with placeholder content explaining they're in development.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BOOKS_PATH = PROJECT_ROOT / "books"

BATTLES = [
    'compass', 'sonnenblume', 'battleaxe', 'crusader',
    'gazala', 'tobruk', 'first_alamein', 'alam_halfa',
    'second_alamein', 'torch', 'tunisia', 'mareth'
]

PLACEHOLDER_TEMPLATE = """# {nation_title} Forces

## Organization

*This section will contain detailed Table of Organization & Equipment (TO&E) data for {nation_title} forces in this battle.*

**Status**: TO&E extraction script in development. This page will be populated with:

- Corps and Division organization
- Regiment and Battalion breakdowns
- Company and Platoon compositions
- Equipment allocations by unit type
- Variant-level detail (specific tank/gun models used)

## Historical Units

*Historical units that fought in this battle will be listed here with their organizational hierarchy extracted from Phase 6 unit data.*

**Source Data**: Phase 6 unit JSONs contain 402 unit-quarters of organization data across all North Africa battles.

## Equipment Summary

*Equipment used by {nation_title} forces in this battle - see Equipment Datacards section for detailed statistics.*

---

**Development Note**: This content will be auto-generated from Phase 6 unit extraction data (402 unit JSONs in `data/output/units/`). The extraction script (`generate_forces_pages.py`) is planned for Phase 9B completion.

**Current Priority**: Medium - Will be implemented after:
1. Equipment datacards are finalized
2. All 45 scenarios are validated
3. Special rules sections are complete

**Data Available**: The raw data exists in Phase 6 JSONs. Example units for this quarter are ready for extraction.
"""


def populate_forces_page(nation_file: Path, nation: str):
    """Populate a single Forces page if it's empty."""
    with open(nation_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file is effectively empty (just title and maybe whitespace)
    if len(content.strip()) < 50:  # Less than 50 chars = basically empty
        nation_title = nation.title()
        new_content = PLACEHOLDER_TEMPLATE.format(
            nation_title=nation_title,
            nation=nation
        )

        with open(nation_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    return False


def process_battle(battle: str):
    """Process Forces pages for one battle."""
    army_lists_path = BOOKS_PATH / battle / "book" / "src" / "army_lists"

    if not army_lists_path.exists():
        return 0

    updated = 0
    for nation_file in army_lists_path.glob("*.md"):
        nation = nation_file.stem  # british, german, italian
        if populate_forces_page(nation_file, nation):
            updated += 1

    return updated


def main():
    """Populate all empty Forces pages."""
    print("Populating Empty Forces Pages")
    print("=" * 60)

    total_updated = 0

    for battle in BATTLES:
        updated = process_battle(battle)
        if updated > 0:
            print(f"{battle:20} - Updated {updated} pages")
            total_updated += updated

    print("=" * 60)
    print(f"Total pages updated: {total_updated}")
    print("\nNext: Rebuild books and push to GitHub")


if __name__ == "__main__":
    main()
