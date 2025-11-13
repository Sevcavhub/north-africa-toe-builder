#!/usr/bin/env python3
"""
Equipment Name Resolver

Resolves human-readable equipment names from scenarios to canonical database IDs.
Filters by AFV categories (tanks, tank_destroyers, armored_cars).
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict

# Database path (from scripts/battlegroup/web/services/ to root database/)
DB_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "database" / "master_database.db"

# AFV categories to include in scenarios
AFV_CATEGORIES = ['tank', 'tank_destroyer', 'armored_car', 'self_propelled_gun']


def resolve_equipment_canonical_id(display_name: str) -> Optional[str]:
    """
    Resolve equipment display name to canonical ID.

    Args:
        display_name: Human-readable name (e.g., "Matilda II", "Panzer IV")

    Returns:
        canonical_id if found, None if not found or not an AFV

    Resolution Strategy:
        1. Exact match in equipment_name_aliases table
        2. Case-insensitive fuzzy match in equipment table (name or canonical_id)
        3. Filter by AFV categories only
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clean input
    display_name = display_name.strip()

    # Strategy 1: Lookup table (fastest, most accurate)
    cursor.execute("""
        SELECT canonical_id, category
        FROM equipment_name_aliases
        WHERE alias = ?
    """, (display_name,))

    result = cursor.fetchone()
    if result:
        canonical_id, category = result
        # Verify it's an AFV
        if category in AFV_CATEGORIES:
            conn.close()
            return canonical_id

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
        if category in AFV_CATEGORIES:
            conn.close()
            return canonical_id

    # Try case-insensitive partial match
    search_pattern = f"%{display_name}%"
    cursor.execute("""
        SELECT e.canonical_id, e.category
        FROM equipment e
        WHERE (e.name LIKE ? OR e.canonical_id LIKE ?)
        AND e.category IN (?, ?, ?, ?)
        LIMIT 1
    """, (search_pattern, search_pattern, *AFV_CATEGORIES))

    result = cursor.fetchone()
    if result:
        canonical_id, category = result
        conn.close()
        return canonical_id

    # Not found or not an AFV
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

        # Only include AFVs (canonical_id will be None for non-AFVs)
        if canonical_id:
            equipment_list.append({
                'display_name': display_name,
                'count': count,
                'experience': experience,
                'canonical_id': canonical_id
            })

    return equipment_list


def get_afv_list_from_scenario(scenario_dict: dict) -> List[Dict[str, str]]:
    """
    Extract AFV list from scenario dictionary.

    Args:
        scenario_dict: Scenario with 'forces_attacker' and 'forces_defender' keys

    Returns:
        List of unique AFVs with canonical IDs
    """
    afvs = []

    # Extract from attacker forces
    if 'forces_attacker' in scenario_dict and 'units' in scenario_dict['forces_attacker']:
        for unit in scenario_dict['forces_attacker']['units']:
            unit_text = f"- {unit.get('count', 1)}x {unit.get('name', '')} ({unit.get('experience', 'regular')})"
            afvs.extend(extract_equipment_from_scenario_forces(unit_text))

    # Extract from defender forces
    if 'forces_defender' in scenario_dict and 'units' in scenario_dict['forces_defender']:
        for unit in scenario_dict['forces_defender']['units']:
            unit_text = f"- {unit.get('count', 1)}x {unit.get('name', '')} ({unit.get('experience', 'regular')})"
            afvs.extend(extract_equipment_from_scenario_forces(unit_text))

    # Deduplicate by canonical_id
    unique_afvs = {}
    for afv in afvs:
        if afv['canonical_id'] not in unique_afvs:
            unique_afvs[afv['canonical_id']] = afv

    return list(unique_afvs.values())


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
