#!/usr/bin/env python3
"""
Penetration Converter - WWIITANKS mm to BattleGroup Pen values

Converts WWIITANKS penetration data (millimeters at various distances) to
BattleGroup abstract Penetration values (1-15+).

Based on BattleGroup research (sources/BATTLEGROUP_SCENARIO_GUIDE.md):
- Uses penetration at 500m as standard engagement range
- Converts to abstract Pen values 1-15+ for game balance
"""

def convert_penetration_to_battlegroup(pen_mm_500m: float) -> int:
    """
    Convert WWIITANKS penetration (mm @ 500m) to BattleGroup Pen value

    Args:
        pen_mm_500m: Penetration in millimeters at 500 meters

    Returns:
        BattleGroup Penetration value (1-15+, capped at 15)

    Conversion table:
        0-30mm   → Pen 1-2 (AT rifles, 20mm guns)
        31-50mm  → Pen 3-4 (37mm guns)
        51-70mm  → Pen 5-6 (50mm guns)
        71-90mm  → Pen 7-8 (75mm guns short barrel)
        91-110mm → Pen 9-10 (75mm guns long barrel, 76mm)
        111-130mm → Pen 11-12 (88mm guns, 17-pdr)
        131-150mm → Pen 13-14 (100mm+ guns)
        151+mm   → Pen 15+ (Heavy AT guns, 122mm+)
    """
    if pen_mm_500m <= 0:
        return 0

    if pen_mm_500m <= 30:
        return 1 if pen_mm_500m <= 15 else 2
    elif pen_mm_500m <= 50:
        return 3 if pen_mm_500m <= 40 else 4
    elif pen_mm_500m <= 70:
        return 5 if pen_mm_500m <= 60 else 6
    elif pen_mm_500m <= 90:
        return 7 if pen_mm_500m <= 80 else 8
    elif pen_mm_500m <= 110:
        return 9 if pen_mm_500m <= 100 else 10
    elif pen_mm_500m <= 130:
        return 11 if pen_mm_500m <= 120 else 12
    elif pen_mm_500m <= 150:
        return 13 if pen_mm_500m <= 140 else 14
    else:
        return 15  # Cap at 15 (superheavy AT guns)


def get_penetration_description(pen_value: int) -> str:
    """Get human-readable description of penetration value"""
    descriptions = {
        0: "No penetration capability",
        1: "Anti-tank rifle / Very light (20mm)",
        2: "Light anti-tank (20mm-25mm)",
        3: "37mm gun / Light AT",
        4: "37mm gun / Improved",
        5: "50mm gun / Medium AT",
        6: "50mm gun / Improved",
        7: "75mm gun / Short barrel",
        8: "75mm gun / Improved short",
        9: "75mm gun / Long barrel",
        10: "76mm gun / Heavy AT",
        11: "88mm gun / Very heavy AT",
        12: "88mm gun / Improved / 17-pdr",
        13: "100mm+ gun / Superheavy AT",
        14: "100mm+ gun / Improved",
        15: "122mm+ gun / Extreme AT (cap)"
    }
    return descriptions.get(pen_value, f"Unknown penetration value: {pen_value}")


def estimate_penetration_from_caliber(caliber_mm: float, gun_type: str = "standard") -> int:
    """
    Estimate BattleGroup penetration from caliber when WWIITANKS data unavailable

    Args:
        caliber_mm: Gun caliber in millimeters
        gun_type: Gun type ("at" = anti-tank, "howitzer" = HE, "standard" = mixed)

    Returns:
        Estimated BattleGroup Penetration value
    """
    if gun_type == "howitzer":
        # Howitzers have poor penetration (HE-focused)
        if caliber_mm < 75:
            return 1  # Very light HE
        elif caliber_mm < 105:
            return 2  # Light/Medium HE
        elif caliber_mm < 155:
            return 3  # Heavy HE
        else:
            return 4  # Very heavy HE

    elif gun_type == "at":
        # Anti-tank guns have good penetration for their caliber
        if caliber_mm < 40:
            return 2  # AT rifle / 20mm-37mm
        elif caliber_mm < 50:
            return 4  # 37mm-47mm AT
        elif caliber_mm < 60:
            return 6  # 50mm-57mm AT
        elif caliber_mm < 80:
            return 8  # 75mm AT
        elif caliber_mm < 95:
            return 10  # 88mm-90mm AT
        elif caliber_mm < 110:
            return 12  # 100mm AT
        else:
            return 14  # 122mm+ AT

    else:
        # Standard guns (tank guns, dual-purpose)
        if caliber_mm < 30:
            return 1
        elif caliber_mm < 50:
            return 3
        elif caliber_mm < 60:
            return 5
        elif caliber_mm < 80:
            return 7
        elif caliber_mm < 95:
            return 10
        elif caliber_mm < 110:
            return 12
        else:
            return 14


# Example usage and testing
if __name__ == '__main__':
    print("BattleGroup Penetration Converter - Test Cases\n")
    print("=" * 60)

    test_cases = [
        # (pen_mm_500m, gun_name)
        (61, "50mm KwK 38 L/42 (Panzer III Ausf F)"),
        (89, "75mm KwK 37 L/24 (Panzer IV Ausf D)"),
        (106, "75mm KwK 40 L/43 (Panzer IV Ausf F2)"),
        (138, "88mm KwK 36 L/56 (Tiger I)"),
        (165, "88mm PaK 43 L/71 (Nashorn)"),
        (48, "37mm PaK 36"),
        (78, "50mm PaK 38"),
        (30, "20mm KwK 30 (Panzer II)"),
        (120, "88mm FlaK 18/36 (Dual-purpose)"),
        (190, "128mm PaK 44 (Jagdtiger)")
    ]

    for pen_mm, gun_name in test_cases:
        pen_value = convert_penetration_to_battlegroup(pen_mm)
        description = get_penetration_description(pen_value)
        print(f"{gun_name}:")
        print(f"  WWIITANKS: {pen_mm}mm @ 500m")
        print(f"  BattleGroup: Pen {pen_value}")
        print(f"  Description: {description}")
        print()

    print("=" * 60)
    print("\nEstimation from caliber (when WWIITANKS data unavailable):\n")

    estimation_tests = [
        (37, "at", "37mm PaK 36"),
        (75, "howitzer", "75mm leFH 18"),
        (88, "at", "88mm PaK 43"),
        (105, "howitzer", "105mm leFH 18"),
        (122, "at", "122mm A-19")
    ]

    for caliber, gun_type, gun_name in estimation_tests:
        pen_est = estimate_penetration_from_caliber(caliber, gun_type)
        description = get_penetration_description(pen_est)
        print(f"{gun_name} ({caliber}mm {gun_type}):")
        print(f"  Estimated Pen: {pen_est}")
        print(f"  Description: {description}")
        print()
