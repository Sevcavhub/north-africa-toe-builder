#!/usr/bin/env python3
"""
Battle Rating (BR) Assigner - Determine unit importance for BattleGroup

Assigns Battle Rating values (0-5) based on unit type, role, and importance.
BR represents how important a unit is to the battlegroup - when you lose units,
you draw counters equal to their BR. When total counters >= your total BR, you lose.

Based on: sources/BATTLEGROUP_SCENARIO_GUIDE.md (lines 379-427)
"""

from typing import Dict, Optional
from armor_converter import get_armor_category


def assign_infantry_br(unit_size: int, role: str, is_command: bool = False) -> int:
    """
    Assign Battle Rating for infantry units

    Args:
        unit_size: Number of men (squad typically 8-12, platoon 30-40)
        role: 'rifle', 'assault', 'support', 'recon', 'engineer', 'command'
        is_command: Whether this is a command/HQ unit

    Returns:
        BR value (0-5)

    Guide rules:
      - Regular squad: BR 1-2
      - Veteran squad: BR 2
      - Elite squad: BR 2-3
      - Command squad: BR 3
    """
    if is_command or role == 'command':
        return 3 if unit_size < 20 else 4

    if role == 'recon':
        return 1  # Expendable scouts

    if role in ['assault', 'engineer']:
        return 2 if unit_size < 15 else 3  # Specialized units more valuable

    # Standard infantry
    if unit_size < 10:
        return 1  # Small squad
    elif unit_size < 20:
        return 2  # Full squad
    elif unit_size < 40:
        return 3  # Platoon
    else:
        return 4  # Company


def assign_tank_br(front_armor_mm: float, gun_penetration_mm: float,
                   is_command: bool = False, vehicle_role: str = 'standard') -> int:
    """
    Assign Battle Rating for tanks

    Args:
        front_armor_mm: Front armor in mm
        gun_penetration_mm: Gun penetration at 500m
        is_command: Whether this is a command tank
        vehicle_role: 'light', 'medium', 'heavy', 'command', 'recon'

    Returns:
        BR value (2-5)

    Guide rules:
      - Light tanks/armored cars: BR 2-3
      - Medium tanks: BR 3-4
      - Heavy tanks: BR 4-5
      - Command vehicles: BR 4-5
    """
    from armor_converter import convert_armor_to_battlegroup

    if is_command or vehicle_role == 'command':
        return 5  # Command tanks are vital

    front_armor = convert_armor_to_battlegroup(front_armor_mm)
    category = get_armor_category(front_armor)

    if category == "Light" or vehicle_role == 'recon':
        return 2 if front_armor <= 3 else 3

    elif category == "Medium":
        return 3 if front_armor <= 6 else 4

    elif category == "Heavy":
        return 4 if front_armor <= 10 else 5

    else:  # Superheavy
        return 5


def assign_gun_br(gun_penetration_mm: float, gun_type: str,
                  is_self_propelled: bool = False) -> int:
    """
    Assign Battle Rating for guns (AT guns, artillery)

    Args:
        gun_penetration_mm: Penetration at 500m
        gun_type: 'at' (anti-tank), 'howitzer', 'aa' (anti-aircraft), 'field'
        is_self_propelled: Whether gun is on SPG chassis

    Returns:
        BR value (0-5)

    Guide rules:
      - Light AT guns (37mm-50mm): BR 2-3
      - Medium AT guns (57mm-75mm): BR 3-4
      - Heavy AT guns (88mm, 17-pdr): BR 4-5
      - Artillery (off-table): BR 0 (don't count)
      - Artillery (on-table): BR 3-4
    """
    from penetration_converter import convert_penetration_to_battlegroup

    if gun_type == 'off_table':
        return 0  # Off-table artillery doesn't count for BR

    gun_pen = convert_penetration_to_battlegroup(gun_penetration_mm)

    # Self-propelled guns are more valuable (mobility)
    sp_bonus = 1 if is_self_propelled else 0

    if gun_type == 'at':
        if gun_pen <= 4:
            return 2 + sp_bonus  # Light AT
        elif gun_pen <= 7:
            return 3 + sp_bonus  # Medium AT
        elif gun_pen <= 10:
            return 4 + sp_bonus  # Heavy AT
        else:
            return 5  # Very heavy AT (cap at 5)

    elif gun_type in ['howitzer', 'field']:
        return 3 + sp_bonus  # On-table artillery

    elif gun_type == 'aa':
        return 2 + sp_bonus  # AA guns

    else:
        return 3  # Default


def assign_vehicle_br(vehicle_type: str, has_special_role: bool = False) -> int:
    """
    Assign Battle Rating for support vehicles

    Args:
        vehicle_type: 'truck', 'halftrack', 'carrier', 'motorcycle', 'command', 'supply'
        has_special_role: Command post, medic, observer, etc.

    Returns:
        BR value (0-3)

    Guide rules:
      - Supply trucks: BR 0-1
      - Command post: BR 3-4
      - Medics: BR 2
      - Observers: BR 1-2
    """
    if has_special_role:
        if vehicle_type == 'command':
            return 4  # Command post vital
        elif vehicle_type == 'observer':
            return 2  # Observers valuable
        elif vehicle_type == 'medic':
            return 2  # Medics valuable
        else:
            return 1

    if vehicle_type in ['truck', 'supply']:
        return 0  # Unimportant logistics

    if vehicle_type == 'motorcycle':
        return 1  # Recon/dispatch

    if vehicle_type in ['halftrack', 'carrier']:
        return 1  # Transport

    return 1  # Default support vehicle


def assign_experience_level(nation: str, quarter: str, unit_quality: Optional[str] = None) -> str:
    """
    Assign experience level based on nation, quarter, and historical context

    Args:
        nation: 'german', 'italian', 'british', 'american', 'french'
        quarter: '1941q2' format
        unit_quality: Optional override ('inexperienced', 'regular', 'veteran', 'elite')

    Returns:
        Experience level ('i', 'r', 'v', 'e')

    Guide rules (North Africa):
      German:
        - 1940-1941: Veteran/Elite (v/e)
        - 1942-1943: Veteran (v)
        - 1943 Late: Regular/Veteran (r/v)

      Italian:
        - 1940-1941: Regular/Inexperienced (r/i)
        - 1942-1943: Regular (r)

      British:
        - 1940-1941: Regular (r)
        - 1941-1942 (Desert Rats): Veteran/Elite (v/e)
        - 1943: Veteran (v)

      American:
        - 1942-1943 Early: Inexperienced (i)
        - 1943 Late: Regular/Veteran (r/v)
    """
    if unit_quality:
        quality_map = {
            'inexperienced': 'i',
            'regular': 'r',
            'veteran': 'v',
            'elite': 'e'
        }
        return quality_map.get(unit_quality.lower(), 'r')

    # Parse quarter to get year
    try:
        year = int(quarter[:4])
        q = int(quarter[5])
    except:
        year = 1942
        q = 2

    nation = nation.lower()

    if nation == 'german':
        if year <= 1941:
            return 'v'  # Veteran (early war, France veterans)
        elif year == 1942:
            return 'v'  # Still veteran
        else:  # 1943
            return 'r' if q >= 3 else 'v'  # Declining quality late war

    elif nation == 'italian':
        if year <= 1941:
            return 'r' if q >= 3 else 'i'  # Mixed quality early
        else:
            return 'r'  # Regular by 1942

    elif nation == 'british':
        if year == 1940:
            return 'r'  # Regular (evacuated from France)
        elif year == 1941:
            return 'v' if q >= 3 else 'r'  # Desert Rats forming
        else:  # 1942-1943
            return 'v'  # Veteran Desert Rats

    elif nation == 'american':
        if year == 1942:
            return 'i'  # Inexperienced (first combat)
        elif year == 1943 and q <= 2:
            return 'r'  # Regular (learning fast)
        else:
            return 'v'  # Veteran by late 1943

    elif nation == 'french':
        return 'v'  # Free French were motivated volunteers

    return 'r'  # Default: Regular


def calculate_force_br(unit_list: list) -> Dict:
    """
    Calculate total Battlegroup BR from unit list

    Args:
        unit_list: List of dicts with 'br' values

    Returns:
        Dict with total_br, unit_count, average_br
    """
    total_br = sum(unit.get('br', 0) for unit in unit_list)
    unit_count = len([u for u in unit_list if u.get('br', 0) > 0])
    average_br = total_br / unit_count if unit_count > 0 else 0

    return {
        'total_br': total_br,
        'unit_count': unit_count,
        'average_br': round(average_br, 1)
    }


# Example usage and testing
if __name__ == '__main__':
    print("BattleGroup Battle Rating Assigner - Test Cases\n")
    print("=" * 70)

    print("\n### INFANTRY ###\n")

    infantry_tests = [
        (10, 'rifle', False, "Regular Infantry Squad"),
        (10, 'assault', False, "Panzergrenadier Squad"),
        (5, 'recon', False, "Scout Team"),
        (8, 'command', True, "Platoon HQ"),
        (30, 'rifle', False, "Infantry Platoon"),
    ]

    for size, role, cmd, name in infantry_tests:
        br = assign_infantry_br(size, role, cmd)
        print(f"{name}: BR {br}")
        print(f"  Size: {size} men, Role: {role}, Command: {cmd}")
        print()

    print("=" * 70)
    print("\n### TANKS ###\n")

    tank_tests = [
        (30, 61, False, 'light', "Panzer II Ausf F"),
        (30, 61, False, 'medium', "Panzer III Ausf F"),
        (78, 48, False, 'heavy', "Matilda II"),
        (100, 138, False, 'heavy', "Tiger I"),
        (30, 61, True, 'command', "Panzer III (Command)"),
    ]

    for front, pen, cmd, role, name in tank_tests:
        br = assign_tank_br(front, pen, cmd, role)
        print(f"{name}: BR {br}")
        print(f"  Armor: {front}mm, Pen: {pen}mm, Command: {cmd}, Role: {role}")
        print()

    print("=" * 70)
    print("\n### GUNS ###\n")

    gun_tests = [
        (48, 'at', False, "37mm PaK 36"),
        (78, 'at', False, "50mm PaK 38"),
        (138, 'at', False, "88mm FlaK 18/36"),
        (106, 'at', True, "Marder III (SPG)"),
        (50, 'howitzer', False, "75mm leFH 18"),
        (0, 'off_table', False, "25-pdr Battery (off-table)"),
    ]

    for pen, gtype, sp, name in gun_tests:
        br = assign_gun_br(pen, gtype, sp)
        print(f"{name}: BR {br}")
        print(f"  Pen: {pen}mm, Type: {gtype}, SP: {sp}")
        print()

    print("=" * 70)
    print("\n### VEHICLES ###\n")

    vehicle_tests = [
        ('truck', False, "Opel Blitz"),
        ('halftrack', False, "SdKfz 251"),
        ('command', True, "Command Halftrack"),
        ('observer', True, "Artillery Observer"),
        ('motorcycle', False, "BMW R75"),
    ]

    for vtype, special, name in vehicle_tests:
        br = assign_vehicle_br(vtype, special)
        print(f"{name}: BR {br}")
        print(f"  Type: {vtype}, Special Role: {special}")
        print()

    print("=" * 70)
    print("\n### EXPERIENCE LEVELS ###\n")

    experience_tests = [
        ('german', '1941q2', None, "German 1941-Q2"),
        ('german', '1943q3', None, "German 1943-Q3"),
        ('italian', '1941q1', None, "Italian 1941-Q1"),
        ('italian', '1942q3', None, "Italian 1942-Q3"),
        ('british', '1940q4', None, "British 1940-Q4"),
        ('british', '1942q2', None, "British 1942-Q2 (Desert Rats)"),
        ('american', '1942q4', None, "American 1942-Q4 (Torch)"),
        ('american', '1943q2', None, "American 1943-Q2 (Tunisia)"),
    ]

    for nation, quarter, quality, name in experience_tests:
        exp = assign_experience_level(nation, quarter, quality)
        exp_name = {'i': 'Inexperienced', 'r': 'Regular', 'v': 'Veteran', 'e': 'Elite'}
        print(f"{name}: {exp_name[exp]} ({exp})")
        print()

    print("=" * 70)
    print("\n### FORCE BR CALCULATION ###\n")

    example_force = [
        {'name': 'Panzer III x3', 'br': 4},
        {'name': 'Panzer II x2', 'br': 3},
        {'name': 'Infantry Squad x2', 'br': 2},
        {'name': 'PaK 38', 'br': 3},
        {'name': '88mm FlaK', 'br': 5},
        {'name': 'Command Halftrack', 'br': 4},
        {'name': 'Trucks x2', 'br': 0},
    ]

    force_stats = calculate_force_br(example_force)
    print(f"Example German Battlegroup:")
    for unit in example_force:
        if unit['br'] > 0:
            print(f"  {unit['name']}: BR {unit['br']}")
    print()
    print(f"Total BR: {force_stats['total_br']}")
    print(f"Units (BR > 0): {force_stats['unit_count']}")
    print(f"Average BR: {force_stats['average_br']}")
    print()
    print(f"This battlegroup breaks when {force_stats['total_br']} counters drawn.")
