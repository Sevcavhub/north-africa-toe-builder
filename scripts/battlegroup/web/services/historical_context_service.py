"""
Historical Context Service

Links scenarios to Phase 6 unit data to provide historical context for forces.
Maps equipment names → canonical IDs → Phase 6 units → organizational context.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
UNITS_DIR = PROJECT_ROOT / "data" / "output" / "units"

# Quarter mapping (scenario quarter → Phase 6 quarter format)
QUARTER_MAP = {
    '1940-Q4': '1940q4', '1940q4': '1940q4',
    '1941-Q1': '1941q1', '1941q1': '1941q1',
    '1941-Q2': '1941q2', '1941q2': '1941q2',
    '1941-Q3': '1941q3', '1941q3': '1941q3',
    '1941-Q4': '1941q4', '1941q4': '1941q4',
    '1942-Q1': '1942q1', '1942q1': '1942q1',
    '1942-Q2': '1942q2', '1942q2': '1942q2',
    '1942-Q3': '1942q3', '1942q3': '1942q3',
    '1942-Q4': '1942q4', '1942q4': '1942q4',
    '1943-Q1': '1943q1', '1943q1': '1943q1',
}

# Nation mapping (scenario nation → Phase 6 nation format)
NATION_MAP = {
    'british': 'british',
    'german': 'german',
    'italian': 'italian',
    'american': 'american',
    'french': 'french',
    'axis': ['german', 'italian'],  # Axis can be either
    'allied': ['british', 'american', 'french'],  # Allied can be any
    'new zealand': 'british',  # Commonwealth treated as British
    'australian': 'british',
    'south african': 'british',
    'indian': 'british',
    'british (tobruk)': 'british',
}


def normalize_quarter(quarter: str) -> str:
    """
    Normalize quarter format to lowercase no-hyphen format.

    Args:
        quarter: Quarter string (e.g., "1941-Q2", "1941q2")

    Returns:
        Normalized quarter (e.g., "1941q2")
    """
    return QUARTER_MAP.get(quarter, quarter.lower().replace('-', ''))


def normalize_nation(nation: str) -> List[str]:
    """
    Normalize nation name to Phase 6 format.

    Args:
        nation: Nation name from scenario

    Returns:
        List of nation names (usually 1, but Axis/Allied can be multiple)
    """
    nation_lower = nation.lower().strip()
    mapped = NATION_MAP.get(nation_lower, [nation_lower])

    if isinstance(mapped, str):
        return [mapped]
    return mapped


def load_phase6_units(quarter: str, nation: str) -> List[Dict]:
    """
    Load all Phase 6 units for a given quarter and nation.

    Args:
        quarter: Normalized quarter (e.g., "1941q2")
        nation: Normalized nation (e.g., "german")

    Returns:
        List of unit data dictionaries
    """
    units = []

    # Pattern: {nation}_{quarter}_*.json
    pattern = f"{nation}_{quarter}_*.json"

    for unit_file in UNITS_DIR.glob(pattern):
        try:
            with open(unit_file, 'r', encoding='utf-8') as f:
                unit_data = json.load(f)
                units.append(unit_data)
        except Exception as e:
            print(f"Warning: Failed to load {unit_file.name}: {e}")

    return units


def find_matching_units(equipment_names: List[str], quarter: str, nations: List[str]) -> List[Dict]:
    """
    Find Phase 6 units that contain the specified equipment.

    Args:
        equipment_names: List of equipment display names from scenario
        quarter: Normalized quarter
        nations: List of normalized nation names

    Returns:
        List of matching units with equipment overlap scores
    """
    matching_units = []

    for nation in nations:
        units = load_phase6_units(quarter, nation)

        for unit in units:
            # Check if unit has any of the equipment
            unit_equipment = extract_unit_equipment(unit)

            # Calculate overlap score
            overlap = calculate_equipment_overlap(equipment_names, unit_equipment)

            if overlap['score'] > 0:
                matching_units.append({
                    'unit_designation': unit.get('unit_designation', 'Unknown'),
                    'parent_formation': unit.get('parent_formation', ''),
                    'operational_context': unit.get('operational_context', ''),
                    'nation': unit.get('nation', nation),
                    'quarter': quarter,
                    'overlap_score': overlap['score'],
                    'matched_equipment': overlap['matched_items'],
                    'total_equipment': len(unit_equipment)
                })

    # Sort by overlap score (highest first)
    matching_units.sort(key=lambda x: x['overlap_score'], reverse=True)

    return matching_units


def extract_unit_equipment(unit: Dict) -> List[str]:
    """
    Extract all equipment names from a Phase 6 unit.

    Args:
        unit: Phase 6 unit data dictionary

    Returns:
        List of equipment names (normalized)
    """
    equipment = []

    # Tanks - iterate through tank categories (heavy_tanks, medium_tanks, etc.)
    if 'tanks' in unit and isinstance(unit['tanks'], dict):
        for category_key, category_data in unit['tanks'].items():
            if isinstance(category_data, dict) and 'count' in category_data:
                # Check if count is a dict with variants
                if isinstance(category_data['count'], dict):
                    if 'variants' in category_data['count']:
                        # New format: count.variants.{variant_name}
                        equipment.extend(category_data['count']['variants'].keys())
                    else:
                        # Alternative format: count.{variant_name} directly
                        for key in category_data['count'].keys():
                            if key not in ['total', 'operational'] and isinstance(category_data['count'][key], dict):
                                equipment.append(key)

    # Artillery - iterate through artillery types
    if 'artillery' in unit:
        for artillery_key, artillery_data in unit['artillery'].items():
            if isinstance(artillery_data, dict) and 'equipment' in artillery_data:
                for gun_name in artillery_data['equipment'].keys():
                    if gun_name not in ['total', 'witw_id']:
                        equipment.append(gun_name)

    # Normalize names (lowercase, remove special chars)
    return [normalize_equipment_name(name) for name in equipment]


def normalize_equipment_name(name: str) -> str:
    """
    Normalize equipment name for fuzzy matching.

    Args:
        name: Equipment name

    Returns:
        Normalized name (lowercase, alphanumeric only)
    """
    # Remove special characters, keep alphanumeric and spaces
    normalized = re.sub(r'[^a-z0-9\s]', '', name.lower())
    # Collapse multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def calculate_equipment_overlap(scenario_equipment: List[str], unit_equipment: List[str]) -> Dict:
    """
    Calculate equipment overlap between scenario and unit.

    Args:
        scenario_equipment: Equipment names from scenario
        unit_equipment: Equipment names from Phase 6 unit

    Returns:
        Dict with 'score' and 'matched_items'
    """
    # Normalize both lists
    scenario_norm = [normalize_equipment_name(e) for e in scenario_equipment]
    unit_norm = [normalize_equipment_name(e) for e in unit_equipment]

    # Find matches (fuzzy matching - check if any part of name matches)
    matched = []
    for s_eq in scenario_norm:
        for u_eq in unit_norm:
            # Check if either name contains the other (handles variants)
            if s_eq in u_eq or u_eq in s_eq:
                matched.append((s_eq, u_eq))
                break

    return {
        'score': len(matched),
        'matched_items': matched
    }


def get_historical_context(equipment_list: List[str], quarter: str, nations: List[str]) -> Optional[Dict]:
    """
    Get historical context for scenario forces.

    Args:
        equipment_list: List of equipment display names from scenario
        quarter: Quarter string (e.g., "1941-Q2")
        nations: List of nation names from scenario

    Returns:
        Dict with historical context or None if no matches found
    """
    # Normalize inputs
    quarter_norm = normalize_quarter(quarter)
    nations_norm = []
    for nation in nations:
        nations_norm.extend(normalize_nation(nation))
    nations_norm = list(set(nations_norm))  # Remove duplicates

    # Find matching units
    matching_units = find_matching_units(equipment_list, quarter_norm, nations_norm)

    if not matching_units:
        return None

    # Get best match (highest overlap score)
    best_match = matching_units[0]

    return {
        'unit_designation': best_match['unit_designation'],
        'parent_formation': best_match['parent_formation'],
        'operational_context': best_match['operational_context'],
        'nation': best_match['nation'],
        'confidence': min(100, (best_match['overlap_score'] / len(equipment_list)) * 100),
        'matched_equipment_count': best_match['overlap_score'],
        'total_scenario_equipment': len(equipment_list),
        'all_matches': matching_units[:3]  # Top 3 matches
    }


def format_historical_context_paragraph(context: Dict) -> str:
    """
    Format historical context as a paragraph for inclusion in scenarios.

    Args:
        context: Historical context dict from get_historical_context()

    Returns:
        Formatted paragraph string
    """
    if not context:
        return ""

    unit = context['unit_designation']
    parent = context['parent_formation']
    op_context = context['operational_context']

    # Build paragraph
    parts = [f"These forces represent elements of **{unit}**"]

    if parent:
        parts.append(f" ({parent})")

    parts.append(".")

    if op_context:
        parts.append(f" {op_context}.")

    # Add confidence note if low
    if context['confidence'] < 50:
        parts.append(f" *Note: Equipment match confidence: {context['confidence']:.0f}%*")

    return "".join(parts)


def test_service():
    """Test the historical context service."""
    print("Testing Historical Context Service\n")

    # Test case: Battleaxe scenario with German forces
    equipment = ["Panzer III", "Panzer IV", "88mm FlaK"]
    quarter = "1941-Q2"
    nations = ["german"]

    print(f"Test: Finding units for equipment: {equipment}")
    print(f"Quarter: {quarter}")
    print(f"Nations: {nations}\n")

    context = get_historical_context(equipment, quarter, nations)

    if context:
        print("Historical Context Found:")
        print(f"  Unit: {context['unit_designation']}")
        print(f"  Parent: {context['parent_formation']}")
        print(f"  Context: {context['operational_context']}")
        print(f"  Confidence: {context['confidence']:.1f}%")
        print(f"  Matched: {context['matched_equipment_count']}/{context['total_scenario_equipment']} items")
        print(f"\nFormatted Paragraph:")
        print(f"  {format_historical_context_paragraph(context)}")
    else:
        print("No matching units found")


if __name__ == "__main__":
    test_service()
