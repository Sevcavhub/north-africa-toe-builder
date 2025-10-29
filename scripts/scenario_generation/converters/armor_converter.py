#!/usr/bin/env python3
"""
Armor Converter - WWIITANKS mm to BattleGroup Armor values

Converts WWIITANKS armor data (millimeters) to BattleGroup abstract Armor values (1-16).

Based on BattleGroup research (sources/BATTLEGROUP_SCENARIO_GUIDE.md):
- Converts mm armor thickness to abstract Armor values 1-16
- Higher values = better protection
- Considers front, side, rear separately
"""

def convert_armor_to_battlegroup(armor_mm: float) -> int:
    """
    Convert WWIITANKS armor (mm) to BattleGroup Armor value

    Args:
        armor_mm: Armor thickness in millimeters

    Returns:
        BattleGroup Armor value (1-16)

    Conversion table:
        0-20mm   → Armor 1-2 (Light armor, armored cars)
        21-30mm  → Armor 3-4 (Light tanks)
        31-50mm  → Armor 5-6 (Medium tanks early)
        51-70mm  → Armor 7-8 (Medium tanks mid)
        71-90mm  → Armor 9-10 (Medium/Heavy tanks)
        91-120mm → Armor 11-12 (Heavy tanks)
        121-150mm → Armor 13-14 (Very heavy tanks)
        151+mm   → Armor 15-16 (Superheavy tanks - rare)
    """
    if armor_mm <= 0:
        return 0

    if armor_mm <= 20:
        return 1 if armor_mm <= 10 else 2
    elif armor_mm <= 30:
        return 3 if armor_mm <= 25 else 4
    elif armor_mm <= 50:
        return 5 if armor_mm <= 40 else 6
    elif armor_mm <= 70:
        return 7 if armor_mm <= 60 else 8
    elif armor_mm <= 90:
        return 9 if armor_mm <= 80 else 10
    elif armor_mm <= 120:
        return 11 if armor_mm <= 105 else 12
    elif armor_mm <= 150:
        return 13 if armor_mm <= 135 else 14
    else:
        return 15 if armor_mm <= 180 else 16  # Cap at 16


def get_armor_description(armor_value: int) -> str:
    """Get human-readable description of armor value"""
    descriptions = {
        0: "No armor (open-topped, soft-skinned)",
        1: "Very light armor (armored car, thin plate)",
        2: "Light armor (armored car, light tank)",
        3: "Light tank armor (early)",
        4: "Light tank armor (improved)",
        5: "Medium tank armor (early)",
        6: "Medium tank armor (standard)",
        7: "Medium tank armor (improved)",
        8: "Medium tank armor (heavy)",
        9: "Heavy tank armor (early)",
        10: "Heavy tank armor (standard)",
        11: "Heavy tank armor (improved)",
        12: "Very heavy tank armor",
        13: "Superheavy tank armor (early)",
        14: "Superheavy tank armor (standard)",
        15: "Superheavy tank armor (improved)",
        16: "Superheavy tank armor (maximum)"
    }
    return descriptions.get(armor_value, f"Unknown armor value: {armor_value}")


def convert_tank_armor(front_mm: float, side_mm: float, rear_mm: float) -> dict:
    """
    Convert complete tank armor profile to BattleGroup values

    Args:
        front_mm: Front armor thickness in mm
        side_mm: Side armor thickness in mm
        rear_mm: Rear armor thickness in mm

    Returns:
        Dict with 'front', 'side', 'rear' BattleGroup Armor values
    """
    return {
        'front': convert_armor_to_battlegroup(front_mm),
        'side': convert_armor_to_battlegroup(side_mm),
        'rear': convert_armor_to_battlegroup(rear_mm),
        'front_mm': front_mm,
        'side_mm': side_mm,
        'rear_mm': rear_mm
    }


def get_armor_category(front_armor: int) -> str:
    """
    Get vehicle category based on front armor value

    Returns: "Light", "Medium", "Heavy", "Superheavy"
    """
    if front_armor <= 4:
        return "Light"
    elif front_armor <= 8:
        return "Medium"
    elif front_armor <= 12:
        return "Heavy"
    else:
        return "Superheavy"


# Example usage and testing
if __name__ == '__main__':
    print("BattleGroup Armor Converter - Test Cases\n")
    print("=" * 70)

    test_cases = [
        # (front_mm, side_mm, rear_mm, vehicle_name)
        (30, 14, 14, "Panzer II Ausf F"),
        (30, 30, 30, "Panzer III Ausf F"),
        (50, 30, 20, "Panzer III Ausf H"),
        (30, 20, 20, "Panzer IV Ausf D"),
        (50, 30, 20, "Panzer IV Ausf F2"),
        (78, 60, 25, "Matilda II"),
        (50, 30, 30, "M3 Grant"),
        (51, 38, 38, "M4 Sherman"),
        (100, 80, 80, "Tiger I"),
        (150, 80, 80, "Tiger II"),
        (13, 13, 13, "SdKfz 222 (Armored Car)"),
        (10, 10, 10, "Universal Carrier")
    ]

    for front_mm, side_mm, rear_mm, vehicle_name in test_cases:
        armor_profile = convert_tank_armor(front_mm, side_mm, rear_mm)
        category = get_armor_category(armor_profile['front'])

        print(f"{vehicle_name}:")
        print(f"  WWIITANKS: Front {front_mm}mm / Side {side_mm}mm / Rear {rear_mm}mm")
        print(f"  BattleGroup: Front {armor_profile['front']} / Side {armor_profile['side']} / Rear {armor_profile['rear']}")
        print(f"  Category: {category}")
        print(f"  Front Description: {get_armor_description(armor_profile['front'])}")
        print()

    print("=" * 70)
    print("\nArmor Value Summary:\n")

    armor_ranges = [
        (1, 2, "Light armor (armored cars, thin plate)"),
        (3, 4, "Light tanks (early WWII)"),
        (5, 6, "Medium tanks (early/mid)"),
        (7, 8, "Medium tanks (improved)"),
        (9, 10, "Heavy tanks (early/standard)"),
        (11, 12, "Heavy tanks (improved/very heavy)"),
        (13, 14, "Superheavy tanks (King Tiger, IS-2)"),
        (15, 16, "Superheavy tanks (maximum protection)")
    ]

    for min_val, max_val, description in armor_ranges:
        print(f"Armor {min_val}-{max_val}: {description}")
