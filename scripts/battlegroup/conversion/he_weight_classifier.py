#!/usr/bin/env python3
"""
HE Shell Weight Classifier for BattleGroup

Classifies HE shell weight based on caliber:
- Light: 20-49mm (small AT guns, light tank guns)
- Medium: 50-104mm (tank guns, medium artillery)
- Heavy: 105mm+ (howitzers, heavy artillery)

This is separate from HE effectiveness (dice/target notation).
"""

def classify_he_weight(caliber_mm: int) -> str:
    """
    Classify HE shell weight based on caliber.

    Args:
        caliber_mm: Gun caliber in millimeters

    Returns:
        str: 'Light', 'Medium', 'Heavy', or '-' if no HE capability

    Examples:
        >>> classify_he_weight(37)
        'Light'
        >>> classify_he_weight(75)
        'Medium'
        >>> classify_he_weight(105)
        'Heavy'
    """
    if caliber_mm is None:
        return '-'

    if caliber_mm < 20:
        # Very small calibers typically don't have HE (machine guns, etc.)
        return '-'
    elif caliber_mm <= 49:
        # Small AT guns, light tank guns
        # Examples: 37mm M6, 40mm 2-pdr, 45mm 20-K, 47mm
        return 'Light'
    elif caliber_mm <= 104:
        # Medium tank guns, medium artillery
        # Examples: 50mm KwK, 75mm Sherman/Panzer IV, 76mm, 88mm FlaK
        return 'Medium'
    else:
        # Heavy howitzers and artillery
        # Examples: 105mm, 120mm, 150mm, 155mm
        return 'Heavy'


def get_he_weight_and_effectiveness(caliber_mm: int, gun_name: str = None) -> dict:
    """
    Get both HE shell weight class and effectiveness notation.

    Args:
        caliber_mm: Gun caliber in millimeters
        gun_name: Optional gun name for special cases

    Returns:
        dict: {
            'he_weight': str ('Light', 'Medium', 'Heavy', or '-'),
            'he_effectiveness': str ('2/5+', '4/4+', etc.),
            'caliber_mm': int
        }
    """
    # Import HE calculator for effectiveness
    try:
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        from scripts.battlegroup.conversion.he_calculator import calculate_he_effect

        he_result = calculate_he_effect(caliber_mm=caliber_mm, gun_name=gun_name)
        he_effectiveness = he_result.get('format', '-')
    except:
        he_effectiveness = '-'

    return {
        'he_weight': classify_he_weight(caliber_mm),
        'he_effectiveness': he_effectiveness,
        'caliber_mm': caliber_mm
    }


if __name__ == '__main__':
    # Test cases
    test_calibers = [
        (37, '37mm M6'),
        (40, '2-pdr'),
        (50, '50mm KwK38'),
        (75, '75mm Sherman'),
        (88, '88mm FlaK'),
        (105, '105mm howitzer'),
        (150, '150mm artillery')
    ]

    print('HE Shell Weight Classification Tests')
    print('=' * 60)
    print(f"{'Caliber':<15} {'Weight':<10} {'Effectiveness':<15} {'Gun'}")
    print('-' * 60)

    for caliber, gun_name in test_calibers:
        result = get_he_weight_and_effectiveness(caliber, gun_name)
        print(f"{caliber}mm{'':<11} {result['he_weight']:<10} {result['he_effectiveness']:<15} {gun_name}")
