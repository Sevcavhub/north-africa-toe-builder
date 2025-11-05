#!/usr/bin/env python3
"""
Extract Black Sabbath 1st Hussars Scenario from Canada's Crucible supplement
Populates BG_Scenario_Army_Lists, BG_Scenario_Forces, and BG_Scenario_Units tables
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Black Sabath 1st Hussars Scenario Army Lists for Company level game.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Black Sabbath 1st Hussars Scenario...')
    print()

    # Step 1: Insert scenario
    cursor.execute('''
    INSERT INTO BG_Scenario_Army_Lists (
        scenario_name, scenario_size, source_supplement, source_image_location
    ) VALUES (?, ?, ?, ?)
    ''', (
        'Black Sabbath - 1st Hussars Attack',
        'Company',
        'Battlegroup-Canadas-Crucible',
        SCREENSHOT_FILE
    ))
    scenario_id = cursor.lastrowid
    print(f'  [OK] Inserted scenario: Black Sabbath - 1st Hussars Attack (ID: {scenario_id})')

    # Step 2: Insert Canadian Forces
    cursor.execute('''
    INSERT INTO BG_Scenario_Forces (
        scenario_id, force_name, side, nation, br_total, officers_count, extra_br, extra_officers, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        scenario_id,
        'Canadian Forces',
        'Allied',
        'canadian',
        35,
        3,  # including senior officer
        35,  # Extra BR from reinforcements
        4,   # Extra Officers from reinforcements
        'B Squadron, 1st Hussars + D Company, Queen\'s Own Rifles of Canada'
    ))
    canadian_force_id = cursor.lastrowid
    print(f'  [OK] Inserted Canadian Forces (ID: {canadian_force_id})')

    # Step 3: Insert German Forces
    cursor.execute('''
    INSERT INTO BG_Scenario_Forces (
        scenario_id, force_name, side, nation, br_total, officers_count, extra_br, extra_officers, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        scenario_id,
        'German Forces',
        'Axis',
        'german',
        39,
        3,  # including senior officer
        49,  # Extra BR from reinforcements
        2,   # Extra Officers from reinforcements
        'Mixed infantry and armor defensive force'
    ))
    german_force_id = cursor.lastrowid
    print(f'  [OK] Inserted German Forces (ID: {german_force_id})')

    # Step 4: Insert Canadian Units
    canadian_units = [
        # B Squadron, 1st Hussars (under strength)
        {'unit_designation': 'Forward HQ', 'equipment_name': 'Sherman', 'equipment_variant': 'Firefly', 'officer_count': 1, 'deployment_notes': 'with Officer'},
        {'unit_designation': '1st Troop', 'equipment_name': 'Sherman', 'quantity': 3, 'equipment_variant': 'M4', 'officer_count': 1, 'deployment_notes': 'with Officer'},
        {'unit_designation': '2nd Troop', 'equipment_name': 'Sherman', 'quantity': 3, 'equipment_variant': 'M4', 'officer_count': 1, 'deployment_notes': 'with Officer'},
        {'unit_designation': '3rd Troop', 'equipment_name': 'Sherman', 'quantity': 3, 'equipment_variant': 'M4', 'officer_count': 1, 'deployment_notes': 'with Officer'},

        # D Company, Queen's Own Rifles of Canada
        {'unit_designation': 'Infantry Platoon', 'unit_role': 'on foot', 'deployment_notes': 'may start as tank riders'},
        {'unit_designation': 'Infantry Platoon', 'unit_role': 'on foot', 'deployment_notes': 'may start as tank riders'},
        {'unit_designation': 'Battery of 3" mortars', 'equipment_name': '3" mortar', 'deployment_notes': 'off-table'},

        # Optional Reinforcements
        {'unit_designation': 'Sherman Troop', 'equipment_name': 'Sherman', 'quantity': 3, 'equipment_variant': 'Firefly', 'officer_count': 1, 'arrival_turn': 10, 'arrival_condition': 'Optional Reinforcement'},
        {'unit_designation': 'Infantry Section', 'unit_role': 'as tank riders', 'arrival_turn': 10, 'arrival_condition': 'Optional Reinforcement'},
        {'unit_designation': 'Sherman Troop', 'equipment_name': 'Sherman', 'quantity': 3, 'officer_count': 1, 'arrival_turn': 11, 'arrival_condition': 'Optional Reinforcement'},
        {'unit_designation': 'Infantry Section HQ', 'unit_role': 'as tank riders', 'arrival_turn': 11, 'arrival_condition': 'Optional Reinforcement'},
        {'unit_designation': 'Sherman Troop', 'equipment_name': 'Sherman', 'quantity': 3, 'equipment_variant': 'Firefly', 'officer_count': 1, 'arrival_turn': 12, 'arrival_condition': 'Optional Reinforcement'},
        {'unit_designation': 'Infantry Section', 'unit_role': 'as tank riders', 'arrival_turn': 12, 'arrival_condition': 'Optional Reinforcement'},
        {'unit_designation': 'Senior Officer', 'equipment_name': 'M4 Sherman', 'arrival_turn': 12, 'arrival_condition': 'Optional Reinforcement'},
    ]

    for unit in canadian_units:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (
            force_id, unit_designation, unit_role, quantity, equipment_name,
            equipment_variant, officer_count, arrival_turn, arrival_condition, deployment_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            canadian_force_id,
            unit.get('unit_designation'),
            unit.get('unit_role'),
            unit.get('quantity'),
            unit.get('equipment_name'),
            unit.get('equipment_variant'),
            unit.get('officer_count', 0),
            unit.get('arrival_turn'),
            unit.get('arrival_condition'),
            unit.get('deployment_notes')
        ))

    print(f'  [OK] Inserted {len(canadian_units)} Canadian units')

    # Step 5: Insert German Units
    german_units = [
        # Initial Forces
        {'unit_designation': 'Senior Officer', 'quantity': 1, 'modifiers': '+ 2 men', 'deployment_notes': 'these must deploy in Chateau Mesnil'},
        {'unit_designation': 'MG squad', 'quantity': 1, 'modifiers': '+ 2 men', 'special_equipment': 'with Panzerfaust and AT grenades, 1 anti-tank mine'},
        {'unit_designation': 'Assault Pioneer Platoon', 'modifiers': 'PHQ of 5 men, 3 Pioneers squads each with 1 Panzerfaust and 3 Demolition charges, all upgraded with MG42s, sworn'},
        {'unit_designation': '1st Platoon Command Squad', 'modifiers': 'with 1 Panzerfaust and AT grenades, upgraded with MG42s (on foxholes) - sworn'},
        {'unit_designation': 'Additional Assault Squad', 'modifiers': 'with 1 Panzerfaust and AT grenades, upgraded with MG42s (no foxholes)'},
        {'unit_designation': 'Sniper and spotter', 'quantity': 1},
        {'unit_designation': '3 Pre-Registered Fire Points', 'quantity': 3},
        {'unit_designation': 'Battery of 3 80mm mortars', 'equipment_name': '80mm mortar', 'quantity': 3, 'deployment_notes': 'off-table'},
        {'unit_designation': 'Battery of 2 150mm guns', 'equipment_name': '150mm gun', 'quantity': 2, 'deployment_notes': 'off-table'},

        # Optional Reinforcements Turn 5
        {'unit_designation': 'Panzer IV Platoon', 'equipment_name': 'Panzer IV', 'equipment_variant': 'Hs', 'quantity': 3, 'officer_count': 1, 'arrival_turn': 5, 'arrival_condition': 'arriving on Turn 5, anywhere on western table edge'},

        # Optional Reinforcements Turn 12
        {'unit_designation': 'Panzer IV Platoon', 'equipment_name': 'Panzer IV', 'equipment_variant': 'Hs', 'quantity': 3, 'officer_count': 1, 'arrival_turn': 12, 'arrival_condition': 'within 30" of north-west corner near Le Mesnil Chateau'},

        # Optional Reinforcements Turn 13
        {'unit_designation': 'Panzer IV Platoon', 'equipment_name': 'Panzer IV', 'equipment_variant': 'Hs', 'quantity': 3, 'officer_count': 1, 'arrival_turn': 13, 'arrival_condition': 'within 30" of north-west corner near Le Mesnil Chateau'},
    ]

    for unit in german_units:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (
            force_id, unit_designation, unit_role, quantity, equipment_name,
            equipment_variant, officer_count, modifiers, special_equipment,
            arrival_turn, arrival_condition, deployment_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            german_force_id,
            unit.get('unit_designation'),
            unit.get('unit_role'),
            unit.get('quantity'),
            unit.get('equipment_name'),
            unit.get('equipment_variant'),
            unit.get('officer_count', 0),
            unit.get('modifiers'),
            unit.get('special_equipment'),
            unit.get('arrival_turn'),
            unit.get('arrival_condition'),
            unit.get('deployment_notes')
        ))

    print(f'  [OK] Inserted {len(german_units)} German units')

    conn.commit()

    # Verification
    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print()

    cursor.execute('SELECT COUNT(*) FROM BG_Scenario_Army_Lists')
    scenario_count = cursor.fetchone()[0]
    print(f'Total scenarios in database: {scenario_count}')

    cursor.execute('SELECT COUNT(*) FROM BG_Scenario_Forces WHERE scenario_id = ?', (scenario_id,))
    force_count = cursor.fetchone()[0]
    print(f'Forces for this scenario: {force_count}')

    cursor.execute('SELECT COUNT(*) FROM BG_Scenario_Units WHERE force_id IN (?, ?)', (canadian_force_id, german_force_id))
    unit_count = cursor.fetchone()[0]
    print(f'Total units for this scenario: {unit_count}')

    conn.close()

if __name__ == "__main__":
    main()
