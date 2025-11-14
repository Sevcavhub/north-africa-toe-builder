#!/usr/bin/env python3
"""
Equipment Name Resolver

Resolves human-readable equipment names from scenarios to canonical database IDs.
Includes AFVs, guns, artillery, aircraft, and infantry weapons.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict

# Database path (from scripts/battlegroup/web/services/ to root database/)
DB_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "database" / "master_database.db"

# Equipment categories to include in datacards (expanded from AFV-only)
DATACARD_CATEGORIES = [
    # Vehicles
    'tank', 'tanks', 'main_tanks', 'light_tanks',
    'tank_destroyer', 'tank_destroyers',
    'armored_car', 'armored_cars', 'armored_cars_reconnaissance',
    'self_propelled_gun',
    'armored_vehicles',

    # Artillery and Guns
    'artillery', 'field_artillery', 'towed_artillery',
    'anti_tank', 'anti_tank_guns',
    'anti_aircraft', 'anti_aircraft_guns',

    # Aircraft
    'aircraft', 'fighters', 'bombers', 'dive_bombers',

    # Support (for completeness - halftrucks etc)
    'reconnaissance',
]


def resolve_equipment_canonical_id(display_name: str) -> Optional[str]:
    """
    Resolve equipment display name to canonical ID.

    Args:
        display_name: Human-readable name (e.g., "Matilda II", "25-pdr", "Bf 109")

    Returns:
        canonical_id if found, None if not found or not in DATACARD_CATEGORIES

    Resolution Strategy:
        1. Exact match in equipment_name_aliases table
        2. Case-insensitive fuzzy match in equipment table (name or canonical_id)
        3. Filter by DATACARD_CATEGORIES (vehicles, guns, artillery, aircraft)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clean input
    display_name = display_name.strip()

    # Strategy 1: Lookup table (fastest, most accurate)
    try:
        cursor.execute("""
            SELECT canonical_id, category
            FROM equipment_name_aliases
            WHERE alias = ?
        """, (display_name,))

        result = cursor.fetchone()
        if result:
            canonical_id, category = result
            # Verify it's in our datacard categories
            if category in DATACARD_CATEGORIES:
                conn.close()
                return canonical_id
    except sqlite3.OperationalError:
        # Table doesn't exist - skip to next strategy
        pass

    # Strategy 2: Fuzzy match in equipment table
    # Try exact match first
    cursor.execute("""
        SELECT e.canonical_id, e.category
        FROM equipment e
        WHERE e.name = ? OR e.canonical_id = ?
    """, (display_name, display_name))

    result = cursor.fetchone()
    if result:
        canonical_id, category = result
        if category in DATACARD_CATEGORIES:
            conn.close()
            return canonical_id

    # Try case-insensitive partial match with category filter
    search_pattern = f"%{display_name}%"
    # Build placeholders for IN clause
    placeholders = ','.join(['?' for _ in DATACARD_CATEGORIES])

    cursor.execute(f"""
        SELECT e.canonical_id, e.category
        FROM equipment e
        WHERE (e.name LIKE ? OR e.canonical_id LIKE ?)
        AND e.category IN ({placeholders})
        LIMIT 1
    """, (search_pattern, search_pattern, *DATACARD_CATEGORIES))

    result = cursor.fetchone()
    if result:
        canonical_id, category = result
        conn.close()
        return canonical_id

    # Not found or not in datacard categories
    conn.close()
    return None


def extract_equipment_from_scenario_forces(forces_text: str) -> List[Dict[str, str]]:
    """
    Parse equipment names from scenario forces section.

    Args:
        forces_text: Forces section text (e.g., "- 8x Matilda II (veteran) - 400 pts")

    Returns:
        List of dicts with keys: display_name, count, experience, canonical_id

    Example:
        Input: "- 8x Matilda II (veteran) - 400 pts, BR: 2"
        Output: [{"display_name": "Matilda II", "count": 8, "experience": "veteran",
                  "canonical_id": "BRI_MATILDA_II"}]

        Also matches guns, aircraft, etc.:
        "- 2x 25-pdr (veteran) - 100 pts" -> {"display_name": "25-pdr", ...}
        "- 3x Bf 109E (regular) - 150 pts" -> {"display_name": "Bf 109E", ...}
    """
    import re

    # Regex pattern: 8x Matilda II (veteran) - 400 pts
    # Groups: count, name, experience
    # Note: Leading dash removed since scenario parsing strips it
    pattern = r'(\d+)x\s+([^(]+?)\s*\((\w+)\)\s*-'

    equipment_list = []
    for match in re.finditer(pattern, forces_text):
        count = int(match.group(1))
        display_name = match.group(2).strip()
        experience = match.group(3).strip()

        # Resolve to canonical ID
        canonical_id = resolve_equipment_canonical_id(display_name)

        # Only include equipment in DATACARD_CATEGORIES (vehicles, guns, artillery, aircraft)
        # Infantry platoons, generic units, etc. will return None and be skipped
        if canonical_id:
            equipment_list.append({
                'display_name': display_name,
                'count': count,
                'experience': experience,
                'canonical_id': canonical_id
            })

    return equipment_list


def get_equipment_list_from_scenario(scenario_dict: dict) -> List[Dict[str, str]]:
    """
    Extract equipment list from scenario dictionary.

    Args:
        scenario_dict: Scenario with 'forces_attacker' and 'forces_defender' keys

    Returns:
        List of unique equipment items (vehicles, guns, aircraft) with canonical IDs
    """
    equipment = []

    # Extract from attacker forces
    if 'forces_attacker' in scenario_dict and 'units' in scenario_dict['forces_attacker']:
        for unit in scenario_dict['forces_attacker']['units']:
            unit_text = f"- {unit.get('count', 1)}x {unit.get('name', '')} ({unit.get('experience', 'regular')})"
            equipment.extend(extract_equipment_from_scenario_forces(unit_text))

    # Extract from defender forces
    if 'forces_defender' in scenario_dict and 'units' in scenario_dict['forces_defender']:
        for unit in scenario_dict['forces_defender']['units']:
            unit_text = f"- {unit.get('count', 1)}x {unit.get('name', '')} ({unit.get('experience', 'regular')})"
            equipment.extend(extract_equipment_from_scenario_forces(unit_text))

    # Deduplicate by canonical_id
    unique_equipment = {}
    for item in equipment:
        if item['canonical_id'] not in unique_equipment:
            unique_equipment[item['canonical_id']] = item

    return list(unique_equipment.values())


# Legacy function name for backwards compatibility
def get_afv_list_from_scenario(scenario_dict: dict) -> List[Dict[str, str]]:
    """
    Legacy function - use get_equipment_list_from_scenario() instead.

    This function is maintained for backwards compatibility but now returns
    all equipment types (vehicles, guns, aircraft), not just AFVs.
    """
    return get_equipment_list_from_scenario(scenario_dict)


def test_resolver():
    """Test the equipment resolver with common scenario equipment."""
    print("Testing Equipment Resolver\n")

    test_cases = [
        "Matilda II",
        "Panzer IV",
        "Crusader",
        "M3 Stuart",
        "25-pdr",  # Should return None (gun, not AFV)
        "Infantry Platoon",  # Should return None (infantry)
        "StuG III",
        "Sherman",
    ]

    for name in test_cases:
        result = resolve_equipment_canonical_id(name)
        status = "[AFV]" if result else "[NOT AFV]"
        print(f"{status} {name:25s} -> {result or 'None'}")

    print("\nTesting scenario forces parsing:")
    test_forces = """
    - 8x Matilda II (veteran) - 400 pts, BR: 2
    - 1x Infantry Platoon (veteran) - 160 pts, BR: 1
    - 2x 25-pdr (veteran) - 100 pts, BR: 1
    - 3x Panzer IV (regular) - 300 pts, BR: 3
    """

    equipment = extract_equipment_from_scenario_forces(test_forces)
    print(f"Found {len(equipment)} AFVs:")
    for item in equipment:
        print(f"  {item['count']}x {item['display_name']} ({item['experience']}) -> {item['canonical_id']}")


if __name__ == "__main__":
    test_resolver()
