#!/usr/bin/env python3
"""
Populate Complete Black Sabbath Scenario
Company-level example showing full scenario replication capability
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get the force IDs
    cursor.execute('SELECT id FROM BG_Scenario_Forces WHERE force_name = "Canadian Forces"')
    canadian_force_id = cursor.fetchone()[0]

    cursor.execute('SELECT id FROM BG_Scenario_Forces WHERE force_name = "German Forces"')
    german_force_id = cursor.fetchone()[0]

    print('Populating complete Black Sabbath scenario...')
    print()

    # ============================================================================
    # CANADIAN FORCES - REINFORCEMENTS
    # ============================================================================

    print('Adding Canadian Reinforcements...')

    canadian_reinforcements = [
        # Turn 10 Reinforcements
        ('Reinforcement', 10, 'arriving via eastern table edge', 'Sherman Troop (Turn 10)', 'Tank Troop', 3, 'M4 Sherman', None, 0, None, None, None, None, None),
        ('Reinforcement', 10, 'arriving via eastern table edge', 'Firefly (Turn 10)', 'Tank', 1, 'Sherman Firefly', None, 1, None, None, None, None, None),
        ('Reinforcement', 10, 'arriving via eastern table edge', 'Infantry Section (Turn 10)', 'Infantry Section', 1, 'Infantry', None, 0, None, 'as tank riders', None, None, None),

        # Turn 11 Reinforcements
        ('Reinforcement', 11, 'arriving via eastern table edge', 'Sherman Troop (Turn 11)', 'Tank Troop', 3, 'M4 Sherman', None, 1, None, None, None, None, None),
        ('Reinforcement', 11, 'arriving via eastern table edge', 'Infantry Platoon HQ (Turn 11)', 'Infantry HQ', 1, 'Infantry', None, 0, None, 'as tank riders', None, None, None),

        # Turn 12 Reinforcements
        ('Reinforcement', 12, 'arriving via eastern table edge', 'Sherman Troop (Turn 12)', 'Tank Troop', 3, 'M4 Sherman', None, 0, None, None, None, None, None),
        ('Reinforcement', 12, 'arriving via eastern table edge', 'Firefly (Turn 12)', 'Tank', 1, 'Sherman Firefly', None, 0, None, None, None, None, None),
        ('Reinforcement', 12, 'arriving via eastern table edge', 'Senior Officer (Turn 12)', 'Senior Officer', 1, 'M4 Sherman', None, 1, None, None, None, 'as M4 Sherman', None),
    ]

    for unit in canadian_reinforcements:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (force_id, unit_type, arrival_turn, arrival_condition, unit_designation, unit_role, quantity, equipment_name, equipment_variant, officer_count, br_value, modifiers, special_equipment, deployment_notes, upgrade_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (canadian_force_id,) + unit)

    print(f'  Added {len(canadian_reinforcements)} Canadian reinforcement units')

    # ============================================================================
    # GERMAN FORCES - ALL MAIN UNITS
    # ============================================================================

    print('Adding German Main Force...')

    german_main_units = [
        # Command
        ('Main', None, None, 'Senior Officer', 'Force HQ', 3, 'Infantry', None, 1, None, None, None, 'must deploy in Chateau Mesnil', None),
        ('Main', None, None, 'Senior NCO Team 1', 'NCO Team', 2, 'Infantry', None, 0, None, None, None, None, None),
        ('Main', None, None, 'Senior NCO Team 2', 'NCO Team', 2, 'Infantry', None, 0, None, None, None, None, None),

        # Anti-Tank Guns
        ('Main', None, None, 'PaK40 Battery', 'Anti-Tank Gun', 2, 'PaK40', '75mm', 0, None, 'with loader teams', None, 'in anti-tank gun pits', None),

        # Assault Pioneer Platoon
        ('Main', None, None, 'Assault Pioneer PHQ', 'Platoon HQ', 5, 'Infantry', None, 0, None, None, None, 'in foxholes', None),
        ('Main', None, None, 'Assault Pioneer Squad 1', 'Assault Pioneers', 1, 'Infantry Squad', None, 0, None, '1 Panzerfaust, 3 Panzerschrecke', 'MG42', 'in foxholes', 'upgraded with MG42s'),
        ('Main', None, None, 'Assault Pioneer Squad 2', 'Assault Pioneers', 1, 'Infantry Squad', None, 0, None, '1 Panzerfaust, 3 Panzerschrecke', 'MG42', 'in foxholes', 'upgraded with MG42s'),
        ('Main', None, None, 'Assault Pioneer Squad 3', 'Assault Pioneers', 1, 'Infantry Squad', None, 0, None, '1 Panzerfaust, 3 Panzerschrecke', 'MG42', 'in foxholes', 'upgraded with MG42s'),

        # Mainline Infantry
        ('Main', None, None, 'Mainline Infantry Squad 1', 'Infantry Squad', 1, 'Infantry Squad', None, 0, None, '1 Panzerfaust, AT grenades', 'MG42', 'in foxholes', 'upgraded with MG42s'),
        ('Main', None, None, 'Mainline Infantry Squad 2', 'Infantry Squad', 1, 'Infantry Squad', None, 0, None, '1 Panzerfaust, AT grenades', 'MG42', 'in foxholes', 'upgraded with MG42s'),

        # Additional Assault Pioneer
        ('Main', None, None, 'Additional Assault Pioneer Squad', 'Assault Pioneers', 1, 'Infantry Squad', None, 0, None, '1 Panzerfaust, AT grenades', 'MG42', 'in foxholes', 'upgraded with MG42s'),

        # Turn 5 Mandatory Reinforcement
        ('Reinforcement', 5, 'anywhere on western table edge', 'Panzer IV Platoon (Turn 5)', 'Tank Platoon', 3, 'Panzer IV', 'Ausf H', 1, None, None, None, None, None),
    ]

    for unit in german_main_units:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (force_id, unit_type, arrival_turn, arrival_condition, unit_designation, unit_role, quantity, equipment_name, equipment_variant, officer_count, br_value, modifiers, special_equipment, deployment_notes, upgrade_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (german_force_id,) + unit)

    print(f'  Added {len(german_main_units)} German main force units')

    # ============================================================================
    # GERMAN FIRE SUPPORT
    # ============================================================================

    print('Adding German Fire Support...')

    german_fire_support = [
        ('Sniper', 'Sniper and Spotter', 1, None, 1, 'Pre-Registered Fire Points'),
        ('Smoke', 'Smoke Points', None, None, 1, 'Pre-Registered'),
        ('Counter Battery', 'Counter Battery Missions', None, 3, None, None),
        ('Mortar', '80mm Mortar', 2, None, None, 'off-table'),
        ('Artillery', '150mm Gun', 2, None, None, 'off-table'),
    ]

    for fs in german_fire_support:
        cursor.execute('''
        INSERT INTO BG_Scenario_Fire_Support (force_id, support_type, equipment_name, quantity, fire_missions, pre_registered_points, deployment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (german_force_id,) + fs)

    print(f'  Added {len(german_fire_support)} German fire support assets')

    # ============================================================================
    # GERMAN OPTIONAL REINFORCEMENTS
    # ============================================================================

    print('Adding German Optional Reinforcements...')

    german_optional_reinforcements = [
        ('Optional', 12, 'within 30" of north-west corner near Le Mesnil Chateau', 'Panzer IV Platoon (Turn 12)', 'Tank Platoon', 3, 'Panzer IV', 'Ausf H', 1, None, None, None, None, None),
        ('Optional', 13, 'within 30" of north-west corner near Le Mesnil Chateau', 'Panzer IV Platoon (Turn 13)', 'Tank Platoon', 3, 'Panzer IV', 'Ausf H', 1, None, None, None, None, None),
    ]

    for unit in german_optional_reinforcements:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (force_id, unit_type, arrival_turn, arrival_condition, unit_designation, unit_role, quantity, equipment_name, equipment_variant, officer_count, br_value, modifiers, special_equipment, deployment_notes, upgrade_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (german_force_id,) + unit)

    print(f'  Added {len(german_optional_reinforcements)} German optional reinforcement units')

    conn.commit()

    # ============================================================================
    # VERIFICATION QUERY
    # ============================================================================

    print()
    print('='*80)
    print('BLACK SABBATH SCENARIO - COMPLETE')
    print('='*80)
    print()

    # Canadian Force Summary
    print('CANADIAN FORCES:')
    cursor.execute('''
    SELECT unit_type, COUNT(*), SUM(officer_count)
    FROM BG_Scenario_Units
    WHERE force_id = ?
    GROUP BY unit_type
    ''', (canadian_force_id,))

    for row in cursor.fetchall():
        unit_type, count, officers = row
        officers = officers if officers else 0
        print(f'  {unit_type}: {count} units, {officers} officers')

    cursor.execute('''
    SELECT COUNT(*) FROM BG_Scenario_Fire_Support WHERE force_id = ?
    ''', (canadian_force_id,))
    print(f'  Fire Support: {cursor.fetchone()[0]} assets')

    print()

    # German Force Summary
    print('GERMAN FORCES:')
    cursor.execute('''
    SELECT unit_type, COUNT(*), SUM(officer_count)
    FROM BG_Scenario_Units
    WHERE force_id = ?
    GROUP BY unit_type
    ''', (german_force_id,))

    for row in cursor.fetchall():
        unit_type, count, officers = row
        officers = officers if officers else 0
        print(f'  {unit_type}: {count} units, {officers} officers')

    cursor.execute('''
    SELECT COUNT(*) FROM BG_Scenario_Fire_Support WHERE force_id = ?
    ''', (german_force_id,))
    print(f'  Fire Support: {cursor.fetchone()[0]} assets')

    print()
    print('='*80)
    print('REPLICATION EXAMPLE - Canadian Turn 10 Force Composition:')
    print('='*80)

    cursor.execute('''
    SELECT
        u.unit_designation,
        u.quantity,
        u.equipment_name,
        u.equipment_variant,
        u.officer_count,
        u.unit_type,
        u.arrival_turn
    FROM BG_Scenario_Units u
    WHERE u.force_id = ?
      AND (u.unit_type = 'Main' OR (u.unit_type = 'Reinforcement' AND u.arrival_turn <= 10))
    ORDER BY u.unit_type, u.arrival_turn, u.id
    ''', (canadian_force_id,))

    print()
    print('Main Force + Reinforcements (Turn 0-10):')
    for row in cursor.fetchall():
        designation, qty, equip, variant, officers, unit_type, turn = row
        turn_str = f'(Turn {turn})' if turn else ''
        officer_str = f', {officers} Officer' if officers else ''
        variant_str = f' {variant}' if variant else ''
        print(f'  {designation}: {qty}x {equip}{variant_str}{officer_str} {turn_str}')

    conn.close()

if __name__ == "__main__":
    main()
