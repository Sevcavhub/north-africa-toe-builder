"""
Special Rules Service

Filters BattleGroup special rules by nation and equipment for scenario-specific display.
Queries bg_special_rules table and filters based on equipment in the scenario.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Set

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "database" / "master_database.db"


def get_special_rules_for_equipment(canonical_ids: List[str]) -> List[Dict]:
    """
    Get special rules for specific equipment items.

    Args:
        canonical_ids: List of equipment canonical IDs

    Returns:
        List of special rule dictionaries with rule_name and description
    """
    if not canonical_ids:
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query special rules linked to equipment
    placeholders = ','.join('?' * len(canonical_ids))
    query = f"""
        SELECT DISTINCT r.name, r.description, r.mechanical_effect, r.category
        FROM bg_special_rules r
        JOIN equipment_special_rules esr ON r.rule_id = esr.rule_id
        WHERE esr.equipment_id IN ({placeholders})
        ORDER BY r.name
    """

    cursor.execute(query, canonical_ids)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            'rule_name': row['name'],
            'description': row['description'],
            'mechanical_effect': row['mechanical_effect'],
            'category': row['category']
        }
        for row in rows
    ]


def get_special_rules_for_nations(nations: List[str]) -> List[Dict]:
    """
    Get national-level special rules.

    Args:
        nations: List of nation names (e.g., ['british', 'german'])

    Returns:
        List of special rule dictionaries with rule_name and description
    """
    if not nations:
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Normalize nation names
    nations_normalized = [n.lower().strip() for n in nations]

    # Query national special rules
    placeholders = ','.join('?' * len(nations_normalized))
    query = f"""
        SELECT DISTINCT r.name, r.description, r.mechanical_effect, r.category, r.nation_specific
        FROM bg_special_rules r
        JOIN equipment_special_rules esr ON r.rule_id = esr.rule_id
        JOIN equipment e ON esr.equipment_id = e.canonical_id
        WHERE e.nation IN ({placeholders})
        AND (r.nation_specific IN ({placeholders}) OR r.nation_specific IS NULL)
        ORDER BY r.name
    """

    # Combine nations list twice for the two placeholders
    params = nations_normalized + nations_normalized

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            'rule_name': row['name'],
            'description': row['description'],
            'mechanical_effect': row['mechanical_effect'],
            'category': row['category'],
            'nation_specific': row['nation_specific']
        }
        for row in rows
    ]


def get_scenario_special_rules(canonical_ids: List[str], nations: List[str]) -> Dict[str, List[Dict]]:
    """
    Get all special rules relevant to a scenario.

    Args:
        canonical_ids: List of equipment canonical IDs in scenario
        nations: List of nations in scenario

    Returns:
        Dict with 'equipment_rules' and 'national_rules' lists
    """
    equipment_rules = get_special_rules_for_equipment(canonical_ids)
    national_rules = get_special_rules_for_nations(nations)

    # Remove duplicates (rules that appear in both lists)
    equipment_rule_names = {r['rule_name'] for r in equipment_rules}
    national_rules_filtered = [
        r for r in national_rules
        if r['rule_name'] not in equipment_rule_names
    ]

    return {
        'equipment_rules': equipment_rules,
        'national_rules': national_rules_filtered,
        'all_rules': equipment_rules + national_rules_filtered
    }


def format_special_rules_section(rules: List[Dict]) -> str:
    """
    Format special rules as HTML for scenario display.

    Args:
        rules: List of special rule dictionaries

    Returns:
        HTML string with formatted rules
    """
    if not rules:
        return ""

    html = '<div class="special-rules-reference">\n'
    html += '<h3>Relevant Special Rules</h3>\n'
    html += '<ul>\n'

    for rule in rules:
        html += f'<li><strong>{rule["rule_name"]}</strong>: {rule["description"]}</li>\n'

    html += '</ul>\n'
    html += '</div>\n'

    return html


def test_service():
    """Test the special rules service."""
    print("Testing Special Rules Service\n")

    # Test with some British equipment
    test_equipment = ['GBR_MATILDA_II', 'GBR_CRUSADER_I', 'GBR_25_PDR']
    test_nations = ['british']

    print(f"Test Equipment: {test_equipment}")
    print(f"Test Nations: {test_nations}\n")

    rules = get_scenario_special_rules(test_equipment, test_nations)

    print(f"Equipment Rules: {len(rules['equipment_rules'])}")
    for rule in rules['equipment_rules'][:5]:
        print(f"  - {rule['rule_name']}")

    print(f"\nNational Rules: {len(rules['national_rules'])}")
    for rule in rules['national_rules'][:5]:
        print(f"  - {rule['rule_name']}")

    print(f"\nTotal Unique Rules: {len(rules['all_rules'])}")


if __name__ == "__main__":
    test_service()
