"""
Generate Forces/TO&E pages from Phase 6 unit JSONs.

This script:
1. Loads Phase 6 unit JSONs (402 unit-quarters)
2. Filters by battle quarter and nation
3. Extracts organizational hierarchy and equipment
4. Generates Forces pages showing actual TO&E data (NOT placeholders)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
UNITS_PATH = PROJECT_ROOT / "data" / "output" / "units"
BOOKS_PATH = PROJECT_ROOT / "books"

# Map battles to quarters
BATTLE_QUARTERS = {
    'compass': ['1940q4'],
    'sonnenblume': ['1941q1'],
    'battleaxe': ['1941q2'],
    'crusader': ['1941q4'],
    'gazala': ['1942q2'],
    'tobruk': ['1942q2'],
    'first_alamein': ['1942q3'],
    'alam_halfa': ['1942q3'],
    'second_alamein': ['1942q4'],
    'torch': ['1942q4'],
    'tunisia': ['1943q1'],
    'mareth': ['1943q1'],
}

# Map nations to canonical names
NATION_MAPPING = {
    'british': ['british', 'commonwealth'],
    'german': ['german'],
    'italian': ['italian'],
    'american': ['american'],
    'french': ['french'],
}


def load_units_for_battle(battle: str, nation: str) -> List[Dict]:
    """Load all Phase 6 units matching battle quarter and nation."""
    quarters = BATTLE_QUARTERS.get(battle, [])
    if not quarters:
        return []

    units = []
    nation_variants = NATION_MAPPING.get(nation, [nation])

    for unit_file in UNITS_PATH.glob("*.json"):
        # Parse filename: american_1942q4_1st_armored_division_toe.json
        parts = unit_file.stem.split('_')
        if len(parts) < 3:
            continue

        file_nation = parts[0]
        file_quarter = parts[1]

        # Check if matches
        if file_nation in nation_variants and file_quarter in quarters:
            with open(unit_file, 'r', encoding='utf-8') as f:
                try:
                    unit_data = json.load(f)
                    units.append(unit_data)
                except json.JSONDecodeError:
                    print(f"  [WARNING] Failed to parse {unit_file.name}")

    return units


def format_equipment_variants(variants_dict, category: str = "equipment") -> str:
    """Format equipment variants as markdown list."""
    if not variants_dict:
        return "_None documented_\n"

    output = []

    # Handle list format
    if isinstance(variants_dict, list):
        for item in variants_dict:
            if isinstance(item, dict):
                name = item.get('name') or item.get('type') or 'Unknown'
                count = item.get('count') or item.get('quantity', 0)
                notes = item.get('notes', '')

                line = f"- **{name}**: {count} total"
                if notes:
                    line += f" - _{notes}_"
                output.append(line)
        return '\n'.join(output) + '\n'

    # Handle dict format
    for name, data in variants_dict.items():
        if isinstance(data, dict):
            count = data.get('count', 0)
            operational = data.get('operational', count)
            notes = data.get('notes', '')

            line = f"- **{name}**: {count} total"
            if operational != count:
                line += f" ({operational} operational)"
            if notes:
                line += f" - _{notes}_"
            output.append(line)
        else:
            output.append(f"- **{name}**: {data}")

    return '\n'.join(output) + '\n'


def format_subordinate_units(subordinates) -> str:
    """Format subordinate units as markdown."""
    if not subordinates:
        return "_None documented_\n"

    output = []
    for unit in subordinates:
        # Handle string format (just unit names)
        if isinstance(unit, str):
            output.append(f"- {unit}")
            continue

        # Handle dict format (full unit data)
        if isinstance(unit, dict):
            designation = unit.get('unit_designation', 'Unknown')
            unit_type = unit.get('unit_type', '').replace('_', ' ').title()
            commander = unit.get('commander', 'Unknown')
            strength = unit.get('strength', 0)
            composition = unit.get('composition', '')

            output.append(f"### {designation}")
            output.append(f"- **Type**: {unit_type}")
            output.append(f"- **Commander**: {commander}")
            if isinstance(strength, int) and strength > 0:
                output.append(f"- **Strength**: {strength:,} personnel")
            elif strength:
                output.append(f"- **Strength**: {strength}")
            if composition:
                output.append(f"- **Composition**: {composition}")
            output.append("")

    return '\n'.join(output)


def generate_forces_page(units: List[Dict], nation: str, battle: str) -> str:
    """Generate Forces page markdown from Phase 6 unit data."""

    if not units:
        return f"""# {nation.title()} Forces

## Organization

_No {nation.title()} forces documented for this battle._

---

**Note**: This battle did not involve {nation.title()} forces based on historical records.
"""

    # Sort by organization level (army > corps > division)
    org_priority = {'army': 0, 'corps': 1, 'division': 2, 'brigade': 3, 'regiment': 4}
    units.sort(key=lambda u: org_priority.get(u.get('organization_level', 'division'), 5))

    output = [f"# {nation.title()} Forces\n"]

    # Overview section
    output.append("## Organization Overview\n")
    output.append(f"**Battle**: {battle.replace('_', ' ').title()}")
    output.append(f"**Nation**: {nation.title()}")
    output.append(f"**Units Documented**: {len(units)}\n")

    # List major units
    output.append("### Major Units\n")
    for unit in units:
        designation = unit.get('unit_designation', 'Unknown Unit')
        org_level = unit.get('organization_level', 'division').replace('_', ' ').title()
        parent = unit.get('parent_formation', 'Independent')
        personnel = unit.get('total_personnel', 0)

        output.append(f"- **{designation}** ({org_level})")
        output.append(f"  - Parent Formation: {parent}")
        output.append(f"  - Personnel: {personnel:,}")

    output.append("\n---\n")

    # Detailed unit sections
    for unit in units:
        designation = unit.get('unit_designation', 'Unknown Unit')
        output.append(f"## {designation}\n")

        # Command section
        command = unit.get('command', {})
        if command:
            commander_data = command.get('commander', {})

            # Handle commander as string or dict
            if isinstance(commander_data, str):
                output.append(f"**Commander**: {commander_data}\n")
            elif isinstance(commander_data, dict):
                commander_name = commander_data.get('name', 'Unknown')
                commander_rank = commander_data.get('rank', '')
                output.append(f"**Commander**: {commander_rank} {commander_name}\n")

        # Personnel
        total_personnel = unit.get('total_personnel', 0)
        officers = unit.get('officers', 0)
        ncos = unit.get('ncos', 0)
        enlisted = unit.get('enlisted', 0)

        output.append("### Personnel Strength\n")
        output.append(f"- **Total**: {total_personnel:,}")
        output.append(f"- **Officers**: {officers:,}")
        output.append(f"- **NCOs**: {ncos:,}")
        output.append(f"- **Enlisted**: {enlisted:,}\n")

        # Tanks
        tanks = unit.get('tanks', {})
        if tanks and isinstance(tanks, dict):
            # Handle total being either dict with count or direct integer
            tank_total_data = tanks.get('total', {})
            if isinstance(tank_total_data, dict):
                tank_total = tank_total_data.get('count', 0)
            elif isinstance(tank_total_data, int):
                tank_total = tank_total_data
            else:
                tank_total = 0

            if tank_total > 0:
                output.append("### Tanks\n")
                output.append(f"**Total**: {tank_total}\n")

                # Heavy tanks
                heavy = tanks.get('heavy_tanks', {}).get('count', {})
                if isinstance(heavy, dict) and heavy.get('variants'):
                    output.append("#### Heavy Tanks\n")
                    output.append(format_equipment_variants(heavy['variants']))

                # Medium tanks
                medium = tanks.get('medium_tanks', {}).get('count', {})
                if isinstance(medium, dict) and medium.get('variants'):
                    output.append("#### Medium Tanks\n")
                    output.append(format_equipment_variants(medium['variants']))

                # Light tanks
                light = tanks.get('light_tanks', {}).get('count', {})
                if isinstance(light, dict) and light.get('variants'):
                    output.append("#### Light Tanks\n")
                    output.append(format_equipment_variants(light['variants']))

        # Armored cars
        armored_cars = unit.get('armored_cars', {})
        if armored_cars and isinstance(armored_cars, dict):
            # Handle total being either dict with count or direct integer
            ac_total_data = armored_cars.get('total', {})
            if isinstance(ac_total_data, dict):
                ac_total = ac_total_data.get('count', 0)
            elif isinstance(ac_total_data, int):
                ac_total = ac_total_data
            else:
                ac_total = 0

            if ac_total > 0:
                output.append("### Armoured Cars\n")
                output.append(f"**Total**: {ac_total}\n")

                variants = armored_cars.get('variants', {}).get('count', {})
                if variants:
                    output.append(format_equipment_variants(variants, 'armored_cars'))

        # Artillery
        artillery_total = unit.get('artillery_total', 0)
        if isinstance(artillery_total, dict):
            artillery_total = artillery_total.get('count', 0)
        if artillery_total > 0:
            output.append("### Artillery\n")
            output.append(f"**Total Guns**: {artillery_total}\n")

            # Field artillery
            field_art = unit.get('field_artillery', {})
            if isinstance(field_art, dict) and field_art.get('variants'):
                output.append("#### Field Artillery\n")
                output.append(format_equipment_variants(field_art['variants'], 'field_artillery'))

            # Anti-tank
            at_guns = unit.get('anti_tank', {})
            if isinstance(at_guns, dict) and at_guns.get('variants'):
                output.append("#### Anti-Tank Guns\n")
                output.append(format_equipment_variants(at_guns['variants'], 'anti_tank'))

            # Anti-aircraft
            aa_guns = unit.get('anti_aircraft', {})
            if isinstance(aa_guns, dict) and aa_guns.get('variants'):
                output.append("#### Anti-Aircraft Guns\n")
                output.append(format_equipment_variants(aa_guns['variants'], 'anti_aircraft'))

        # Infantry weapons (top 3)
        inf_weapons = unit.get('top_3_infantry_weapons', {})
        if inf_weapons:
            output.append("### Infantry Weapons (Primary)\n")

            # Handle list format
            if isinstance(inf_weapons, list):
                for weapon_data in inf_weapons[:3]:
                    weapon_name = weapon_data.get('weapon') or weapon_data.get('weapon_type', 'Unknown')
                    weapon_count = weapon_data.get('count') or weapon_data.get('quantity') or weapon_data.get('quantity_authorized', 0)
                    weapon_type = weapon_data.get('type', '').replace('_', ' ').title()
                    output.append(f"- **{weapon_name}**: {weapon_count:,} ({weapon_type})")
            # Handle dict format
            elif isinstance(inf_weapons, dict):
                for i in range(1, 4):
                    weapon_data = inf_weapons.get(str(i))
                    if weapon_data:
                        weapon_name = weapon_data.get('weapon', 'Unknown')
                        weapon_count = weapon_data.get('count', 0)
                        weapon_type = weapon_data.get('type', '').replace('_', ' ').title()
                        output.append(f"- **{weapon_name}**: {weapon_count:,} ({weapon_type})")
            output.append("")

        # Subordinate units
        subordinates = unit.get('subordinate_units', [])
        if subordinates:
            output.append("### Subordinate Units\n")
            output.append(format_subordinate_units(subordinates))

        output.append("---\n")

    # Footer
    output.append("\n**Data Source**: Phase 6 Unit Extraction (402 unit-quarters)")
    output.append(f"**Units Documented**: {len(units)} for {battle.replace('_', ' ').title()}\n")

    return '\n'.join(output)


def process_battle(battle: str):
    """Process Forces pages for one battle."""
    print(f"\n{battle.upper()}")
    print("=" * 60)

    army_lists_path = BOOKS_PATH / battle / "book" / "src" / "army_lists"
    army_lists_path.mkdir(parents=True, exist_ok=True)

    for nation in ['british', 'german', 'italian', 'american', 'french']:
        nation_file = army_lists_path / f"{nation}.md"

        # Load Phase 6 units
        units = load_units_for_battle(battle, nation)

        # Generate Forces page
        content = generate_forces_page(units, nation, battle)

        # Write to file
        with open(nation_file, 'w', encoding='utf-8') as f:
            f.write(content)

        if units:
            print(f"  [OK] {nation:10} - {len(units)} units")
        else:
            print(f"  [SKIP] {nation:10} - No units (not in this battle)")


def main():
    """Generate Forces pages for all 12 battles."""
    print("Generating Forces/TO&E Pages from Phase 6 Unit Data")
    print("=" * 60)
    print("\nData Source: 402 unit JSONs in data/output/units/")
    print("Target: 12 battles × 5 nations = 60 Forces pages\n")

    battles = list(BATTLE_QUARTERS.keys())

    for battle in battles:
        process_battle(battle)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update SUMMARY.md files with scenario names")
    print("2. Rebuild books: cd books/<battle>/book && mdbook build")
    print("3. Verify Forces pages show actual TO&E data")


if __name__ == "__main__":
    main()
