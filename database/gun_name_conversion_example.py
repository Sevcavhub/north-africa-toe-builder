#!/usr/bin/env python3
"""
Example code for integrating bg_gun_name_conversion table
into the datacard generator.

This shows how to convert full weapon names to abbreviated
datacard display names.
"""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / 'master_database.db'


def get_weapon_display_name(weapon_name: str, conn: sqlite3.Connection = None) -> str:
    """
    Convert full weapon name to abbreviated datacard display name.

    Args:
        weapon_name: Full weapon name from bg_builder_weapons
        conn: Optional database connection (creates new one if None)

    Returns:
        Abbreviated display name, or original name if no conversion exists

    Examples:
        >>> get_weapon_display_name('75mmL46 (PaK40)')
        '(PaK40)'

        >>> get_weapon_display_name('17 pdr')
        '17 pdr'

        >>> get_weapon_display_name('Panzerfaust')
        'Pzerfst'
    """
    should_close = False
    if conn is None:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT datacard_name
            FROM bg_gun_name_conversion
            WHERE weapon_name = ?
        ''', (weapon_name,))

        result = cursor.fetchone()
        return result['datacard_name'] if result else weapon_name

    finally:
        if should_close:
            conn.close()


def get_weapon_display_names_batch(weapon_names: list, conn: sqlite3.Connection = None) -> dict:
    """
    Convert multiple weapon names in a single query (more efficient).

    Args:
        weapon_names: List of full weapon names
        conn: Optional database connection

    Returns:
        Dictionary mapping full names to display names

    Example:
        >>> weapons = ['75mmL46 (PaK40)', '2 x MGs', 'Panzerfaust']
        >>> get_weapon_display_names_batch(weapons)
        {'75mmL46 (PaK40)': '(PaK40)', '2 x MGs': '2 x MGs', 'Panzerfaust': 'Pzerfst'}
    """
    if not weapon_names:
        return {}

    should_close = False
    if conn is None:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        should_close = True

    try:
        cursor = conn.cursor()

        # Filter out None/empty values
        valid_names = [w for w in weapon_names if w]
        if not valid_names:
            return {}

        # Build query with placeholders
        placeholders = ','.join('?' * len(valid_names))
        cursor.execute(f'''
            SELECT weapon_name, datacard_name
            FROM bg_gun_name_conversion
            WHERE weapon_name IN ({placeholders})
        ''', valid_names)

        # Create mapping
        conversion_map = {row['weapon_name']: row['datacard_name'] for row in cursor.fetchall()}

        # Fill in any missing conversions with original names
        for name in valid_names:
            if name not in conversion_map:
                conversion_map[name] = name

        return conversion_map

    finally:
        if should_close:
            conn.close()


def get_vehicle_weapons_abbreviated(vehicle_data: dict, conn: sqlite3.Connection = None) -> dict:
    """
    Convert all weapon names in a vehicle record to abbreviated forms.

    Args:
        vehicle_data: Vehicle dictionary with weapon fields (main_gun, weapon_1, etc.)
        conn: Optional database connection

    Returns:
        Dictionary with original and abbreviated weapon names

    Example:
        >>> vehicle = {'main_gun': '75mmL46 (PaK40)', 'weapon_2': '2 x MGs'}
        >>> get_vehicle_weapons_abbreviated(vehicle)
        {
            'main_gun': '75mmL46 (PaK40)',
            'main_gun_display': '(PaK40)',
            'weapon_2': '2 x MGs',
            'weapon_2_display': '2 x MGs'
        }
    """
    weapon_fields = ['main_gun', 'weapon_1', 'weapon_2', 'weapon_3', 'weapon_4',
                     'coaxial_mg', 'hull_mg', 'aa_mg', 'bow_mg']

    # Collect all weapon names
    weapon_names = []
    field_mapping = {}

    for field in weapon_fields:
        value = vehicle_data.get(field)
        if value and value not in ['None', '-', '']:
            weapon_names.append(value)
            field_mapping[value] = field

    if not weapon_names:
        return vehicle_data

    # Get conversions in batch
    conversions = get_weapon_display_names_batch(weapon_names, conn)

    # Add display fields to vehicle data
    result = vehicle_data.copy()
    for weapon_name, field in field_mapping.items():
        result[f'{field}_display'] = conversions.get(weapon_name, weapon_name)

    return result


# Integration example for generate_book_datacards.py
def example_datacard_integration():
    """
    Example showing how to integrate into the datacard generator.

    This would be added to the DatacardGenerator class in generate_book_datacards.py
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Example: Get vehicle with weapons
    cursor.execute("""
        SELECT
            v.vehicle_name,
            v.main_gun,
            v.coaxial_mg,
            v.hull_mg,
            v.aa_mg
        FROM bg_builder_vehicles v
        WHERE v.vehicle_id = 1
    """)

    vehicle = dict(cursor.fetchone())

    # Convert weapons to display names
    vehicle_with_display = get_vehicle_weapons_abbreviated(vehicle, conn)

    print(f"Vehicle: {vehicle_with_display['vehicle_name']}")
    print(f"Main Gun: {vehicle_with_display['main_gun']} → {vehicle_with_display.get('main_gun_display', '-')}")
    print(f"Coax MG: {vehicle_with_display['coaxial_mg']} → {vehicle_with_display.get('coaxial_mg_display', '-')}")

    conn.close()

    # In the datacard template, use:
    # <td>{vehicle_with_display.get('main_gun_display', vehicle_with_display['main_gun'])}</td>


# Suggested modification for generate_book_datacards.py
INTEGRATION_INSTRUCTIONS = """
To integrate bg_gun_name_conversion into generate_book_datacards.py:

1. Add import at top of file:
   from database.gun_name_conversion_example import get_weapon_display_name

2. In the generate_datacard_html() method, after getting main_gun (around line 426):

   # Get abbreviated weapon name for display
   main_gun_display = get_weapon_display_name(main_gun, self.conn) if main_gun else '-'

3. Update weapon table generation (lines 799, 810) to use main_gun_display:

   <tr>
   <td>{main_gun_display}</td>  # Instead of {main_gun}
   <td>HE</td>
   ...

   <tr>
   <td>{main_gun_display}</td>  # Instead of {main_gun}
   <td>AP</td>
   ...

4. Similarly for secondary weapons in armament rows (around line 510):

   secondary_display = get_weapon_display_name(weapon_name, self.conn)
   secondary.append({
       'name': weapon_name,
       'display_name': secondary_display,  # Add this
       'mount_type': mount or 'Unknown',
       'ammunition_count': ammo
   })

5. Update armament_rows_html generation (around line 700) to use display_name:

   <td>{weapon['display_name']}</td>  # Instead of {weapon['name']}

This ensures all weapon names in datacards use the abbreviated format
while preserving full names in the database.
"""


if __name__ == '__main__':
    import sys
    import io

    # Force UTF-8 output on Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Test the conversion
    print("Testing bg_gun_name_conversion integration\n")
    print("="*60)

    test_weapons = [
        '75mmL46 (PaK40)',
        '17 pdr',
        '2 x MGs',
        'Panzerfaust',
        '88mmL56 (FlaK36)',
        'Boys AT-rifle',
        '150mmL12 (sIG33)'
    ]

    print("Single conversions:")
    for weapon in test_weapons:
        display = get_weapon_display_name(weapon)
        print(f"  {weapon:30} -> {display}")

    print("\n" + "="*60)
    print("Batch conversion:")
    batch_result = get_weapon_display_names_batch(test_weapons)
    for weapon, display in batch_result.items():
        print(f"  {weapon:30} -> {display}")

    print("\n" + "="*60)
    print(INTEGRATION_INSTRUCTIONS)
