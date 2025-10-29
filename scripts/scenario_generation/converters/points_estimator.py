#!/usr/bin/env python3
"""
Points Cost Estimator - Calculate BattleGroup points from vehicle/unit stats

Estimates BattleGroup points costs using documented formulas from research.
Since we don't have official North Africa supplement, we reverse-engineer
using relative power calculations.

Based on: sources/BATTLEGROUP_SCENARIO_GUIDE.md (lines 335-377)
"""

from typing import Dict, List, Optional
from armor_converter import convert_armor_to_battlegroup, get_armor_category
from penetration_converter import convert_penetration_to_battlegroup


def estimate_tank_points(front_armor_mm: float, side_armor_mm: float, rear_armor_mm: float,
                         gun_penetration_mm: float, special_rules: List[str] = None) -> int:
    """
    Estimate BattleGroup points for a tank

    Formula from guide:
        Tank Points = Base + Armor Bonus + Gun Bonus + Special Rules

        Base = 80pts (light tank) to 200pts (heavy tank)

        Armor Bonus (based on front armor):
          - Front armor 1-4: +0pts
          - Front armor 5-7: +20pts
          - Front armor 8-10: +40pts
          - Front armor 11-13: +60pts
          - Front armor 14-16: +100pts

        Gun Bonus (based on penetration):
          - Penetration 1-4: +0pts
          - Penetration 5-7: +20pts
          - Penetration 8-10: +40pts
          - Penetration 11-13: +60pts
          - Penetration 14+: +80pts

        Special Rules: +10-50pts each
          - Radio: +10pts
          - Smoke: +5pts
          - Fast: +15pts
          - Stabilized gun: +20pts

    Args:
        front_armor_mm: Front armor in mm
        side_armor_mm: Side armor in mm
        rear_armor_mm: Rear armor in mm
        gun_penetration_mm: Gun penetration at 500m in mm
        special_rules: List of special rule names

    Returns:
        Estimated points cost
    """
    if special_rules is None:
        special_rules = []

    # Convert to BattleGroup values
    front_armor = convert_armor_to_battlegroup(front_armor_mm)
    gun_pen = convert_penetration_to_battlegroup(gun_penetration_mm)

    # Determine base cost from armor category
    category = get_armor_category(front_armor)
    if category == "Light":
        base = 80
    elif category == "Medium":
        base = 120
    elif category == "Heavy":
        base = 180
    else:  # Superheavy
        base = 250

    # Armor bonus
    if front_armor <= 4:
        armor_bonus = 0
    elif front_armor <= 7:
        armor_bonus = 20
    elif front_armor <= 10:
        armor_bonus = 40
    elif front_armor <= 13:
        armor_bonus = 60
    else:
        armor_bonus = 100

    # Gun bonus
    if gun_pen <= 4:
        gun_bonus = 0
    elif gun_pen <= 7:
        gun_bonus = 20
    elif gun_pen <= 10:
        gun_bonus = 40
    elif gun_pen <= 13:
        gun_bonus = 60
    else:
        gun_bonus = 80

    # Special rules bonus
    special_rules_points = {
        'radio': 10,
        'smoke': 5,
        'fast': 15,
        'stabilized': 20,
        'amphibious': 10,
        'command': 15,
        'veteran_crew': 10
    }

    special_bonus = 0
    for rule in special_rules:
        special_bonus += special_rules_points.get(rule.lower(), 0)

    total = base + armor_bonus + gun_bonus + special_bonus
    return total


def estimate_infantry_points(squad_size: int, experience: str, special_rules: List[str] = None) -> int:
    """
    Estimate BattleGroup points for infantry squad

    Args:
        squad_size: Number of men in squad (typically 8-12)
        experience: 'inexperienced', 'regular', 'veteran', 'elite'
        special_rules: List of special rule names

    Returns:
        Estimated points cost

    Base costs:
      - Inexperienced: 3pts/man
      - Regular: 4pts/man
      - Veteran: 5pts/man
      - Elite: 6pts/man

    Special rules:
      - Anti-tank grenades: +5pts
      - Flamethrower: +20pts
      - Panzerfaust: +10pts
      - Engineer: +10pts
      - Assault: +15pts
    """
    if special_rules is None:
        special_rules = []

    # Base cost per man
    cost_per_man = {
        'inexperienced': 3,
        'regular': 4,
        'veteran': 5,
        'elite': 6
    }

    base = squad_size * cost_per_man.get(experience.lower(), 4)

    # Special rules
    special_rules_points = {
        'anti_tank_grenades': 5,
        'flamethrower': 20,
        'panzerfaust': 10,
        'engineer': 10,
        'assault': 15,
        'commando': 20
    }

    special_bonus = 0
    for rule in special_rules:
        special_bonus += special_rules_points.get(rule.lower(), 0)

    return base + special_bonus


def estimate_gun_points(gun_penetration_mm: float, he_size: str, crew_size: int,
                       mobility: str = 'towed', experience: str = 'regular') -> int:
    """
    Estimate BattleGroup points for artillery/AT gun

    Args:
        gun_penetration_mm: Penetration at 500m in mm
        he_size: HE effectiveness ('very_light', 'light', 'medium', 'heavy')
        crew_size: Number of crew (typically 4-10)
        mobility: 'towed', 'self_propelled', 'static'
        experience: 'inexperienced', 'regular', 'veteran', 'elite'

    Returns:
        Estimated points cost

    Base costs:
      - Light AT gun (Pen 1-4): 40pts
      - Medium AT gun (Pen 5-7): 60pts
      - Heavy AT gun (Pen 8-10): 80pts
      - Very heavy AT gun (Pen 11+): 100-150pts

    HE bonus:
      - Very light: +0pts
      - Light: +10pts
      - Medium: +20pts
      - Heavy: +30pts

    Mobility:
      - Towed: +0pts
      - Self-propelled: +40pts
      - Static (dug-in): -10pts

    Experience:
      - Inexperienced: -5pts
      - Regular: +0pts
      - Veteran: +10pts
      - Elite: +15pts
    """
    gun_pen = convert_penetration_to_battlegroup(gun_penetration_mm)

    # Base cost by penetration
    if gun_pen <= 4:
        base = 40
    elif gun_pen <= 7:
        base = 60
    elif gun_pen <= 10:
        base = 80
    elif gun_pen <= 13:
        base = 120
    else:
        base = 150

    # HE bonus
    he_bonus = {
        'very_light': 0,
        'light': 10,
        'medium': 20,
        'heavy': 30
    }
    he_points = he_bonus.get(he_size.lower(), 0)

    # Mobility bonus/penalty
    mobility_bonus = {
        'towed': 0,
        'self_propelled': 40,
        'static': -10
    }
    mobility_points = mobility_bonus.get(mobility.lower(), 0)

    # Experience modifier
    experience_bonus = {
        'inexperienced': -5,
        'regular': 0,
        'veteran': 10,
        'elite': 15
    }
    exp_points = experience_bonus.get(experience.lower(), 0)

    return base + he_points + mobility_points + exp_points


def estimate_vehicle_points(vehicle_type: str, armor_mm: float = 0,
                           special_rules: List[str] = None) -> int:
    """
    Estimate points for support vehicles (trucks, carriers, etc.)

    Args:
        vehicle_type: 'truck', 'halftrack', 'carrier', 'armored_car', 'command'
        armor_mm: Armor thickness (if any)
        special_rules: List of special rules

    Returns:
        Estimated points cost
    """
    if special_rules is None:
        special_rules = []

    base_costs = {
        'truck': 10,
        'halftrack': 30,
        'carrier': 25,
        'armored_car': 40,
        'command': 50,
        'supply': 5,
        'motorcycle': 8
    }

    base = base_costs.get(vehicle_type.lower(), 20)

    # Armor bonus (light vehicles)
    if armor_mm > 10:
        base += 10

    # Special rules
    special_rules_points = {
        'transport': 5,
        'fast': 10,
        'radio': 5,
        'command': 15
    }

    special_bonus = 0
    for rule in special_rules:
        special_bonus += special_rules_points.get(rule.lower(), 0)

    return base + special_bonus


# Example usage and testing
if __name__ == '__main__':
    print("BattleGroup Points Estimator - Test Cases\n")
    print("=" * 70)

    print("\n### TANKS ###\n")

    tank_tests = [
        # (front, side, rear, pen, special, name)
        (30, 30, 30, 61, ['radio', 'smoke'], "Panzer III Ausf F"),
        (30, 20, 20, 89, ['radio', 'smoke'], "Panzer IV Ausf D"),
        (50, 30, 20, 106, ['radio', 'smoke'], "Panzer IV Ausf F2"),
        (78, 60, 25, 48, ['radio'], "Matilda II"),
        (50, 30, 30, 75, ['radio', 'stabilized'], "M3 Grant"),
        (100, 80, 80, 138, ['radio', 'smoke'], "Tiger I"),
    ]

    for front, side, rear, pen, special, name in tank_tests:
        points = estimate_tank_points(front, side, rear, pen, special)
        print(f"{name}: {points}pts")
        print(f"  Armor: F{front}/S{side}/R{rear}mm, Pen: {pen}mm @ 500m")
        print(f"  Special: {', '.join(special) if special else 'None'}")
        print()

    print("=" * 70)
    print("\n### INFANTRY ###\n")

    infantry_tests = [
        (10, 'regular', [], "German Infantry Squad"),
        (10, 'veteran', ['assault'], "German Panzergrenadier Squad"),
        (10, 'inexperienced', [], "Italian Infantry Squad"),
        (8, 'veteran', ['assault', 'engineer'], "British Commando Section"),
        (12, 'inexperienced', [], "American Infantry Squad (1942)"),
    ]

    for size, exp, special, name in infantry_tests:
        points = estimate_infantry_points(size, exp, special)
        print(f"{name}: {points}pts")
        print(f"  Size: {size} men, Experience: {exp}")
        print(f"  Special: {', '.join(special) if special else 'None'}")
        print()

    print("=" * 70)
    print("\n### GUNS ###\n")

    gun_tests = [
        (48, 'light', 5, 'towed', 'regular', "37mm PaK 36"),
        (78, 'medium', 5, 'towed', 'veteran', "50mm PaK 38"),
        (138, 'heavy', 10, 'towed', 'veteran', "88mm FlaK 18/36"),
        (106, 'heavy', 8, 'self_propelled', 'veteran', "Marder III"),
    ]

    for pen, he, crew, mobility, exp, name in gun_tests:
        points = estimate_gun_points(pen, he, crew, mobility, exp)
        print(f"{name}: {points}pts")
        print(f"  Pen: {pen}mm @ 500m, HE: {he}, Crew: {crew}")
        print(f"  Mobility: {mobility}, Experience: {exp}")
        print()

    print("=" * 70)
    print("\n### VEHICLES ###\n")

    vehicle_tests = [
        ('truck', 0, [], "Opel Blitz 3-ton"),
        ('halftrack', 10, ['transport'], "SdKfz 251"),
        ('carrier', 10, ['fast'], "Universal Carrier"),
        ('armored_car', 13, ['fast', 'radio'], "SdKfz 222"),
        ('command', 10, ['radio', 'command'], "Command Halftrack"),
    ]

    for vtype, armor, special, name in vehicle_tests:
        points = estimate_vehicle_points(vtype, armor, special)
        print(f"{name}: {points}pts")
        print(f"  Type: {vtype}, Armor: {armor}mm")
        print(f"  Special: {', '.join(special) if special else 'None'}")
        print()
