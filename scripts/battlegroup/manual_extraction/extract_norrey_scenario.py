#!/usr/bin/env python3
"""
Extract Pre-built Norrey Scenario from Canada's Crucible supplement
Populates BG_Scenario_Army_Lists, BG_Scenario_Forces, and BG_Scenario_Units tables
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Pre-built Norrey Scenario Army List .png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Pre-built Norrey Scenario...')
    print()

    # Step 1: Insert scenario
    cursor.execute('''
    INSERT INTO BG_Scenario_Army_Lists (
        scenario_name, scenario_size, source_supplement, source_image_location
    ) VALUES (?, ?, ?, ?)
    ''', (
        'First Assault on Norrey',
        None,
        'Battlegroup-Canadas-Crucible',
        SCREENSHOT_FILE
    ))
    scenario_id = cursor.lastrowid
    print(f'  [OK] Inserted scenario: First Assault on Norrey (ID: {scenario_id})')

    # Step 2: Insert Canadian Forces
    cursor.execute('''
    INSERT INTO BG_Scenario_Forces (
        scenario_id, force_name, side, nation, br_total, officers_count, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        scenario_id,
        'Canadian Forces',
        'Allied',
        'canadian',
        20,
        2,  # including senior officer
        'Defensive force with artillery support'
    ))
    canadian_force_id = cursor.lastrowid
    print(f'  [OK] Inserted Canadian Forces (ID: {canadian_force_id})')

    # Step 3: Insert German Forces
    cursor.execute('''
    INSERT INTO BG_Scenario_Forces (
        scenario_id, force_name, side, nation, br_total, officers_count, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        scenario_id,
        'German Forces',
        'Axis',
        'german',
        53,
        3,  # including senior officer
        'Armoured Panzer Grenadiers with half-track support'
    ))
    german_force_id = cursor.lastrowid
    print(f'  [OK] Inserted German Forces (ID: {german_force_id})')

    # Step 4: Insert Canadian Units
    canadian_units = [
        {'unit_designation': 'Forward HQ', 'quantity': 3, 'modifiers': '3 men'},
        {'unit_designation': 'Comms relay team'},
        {'unit_designation': 'Infantry Platoon'},
        {'unit_designation': 'Combat Medic'},
        {'unit_designation': 'Vickers HMG and loader team', 'equipment_name': 'Vickers HMG'},
        {'unit_designation': 'Sniper with spotter'},
        {'unit_designation': 'Artillery Observer Team', 'quantity': 2, 'modifiers': '2 men', 'deployment_notes': 'Any of the above can fire on 4+ in foxholes'},
        {'unit_designation': 'Pre-Registered Target Points', 'quantity': 2},
        {'unit_designation': 'Battery of 2 105mm L25 guns', 'equipment_name': '105mm L25', 'quantity': 2, 'deployment_notes': 'off-table'},
        {'unit_designation': 'Battery of 1 105mm L25 gun', 'equipment_name': '105mm L25', 'quantity': 1, 'deployment_notes': 'off-table'},
        {'unit_designation': 'Minefields', 'quantity': 2},
    ]

    for unit in canadian_units:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (
            force_id, unit_designation, quantity, equipment_name,
            modifiers, deployment_notes
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            canadian_force_id,
            unit.get('unit_designation'),
            unit.get('quantity'),
            unit.get('equipment_name'),
            unit.get('modifiers'),
            unit.get('deployment_notes')
        ))

    print(f'  [OK] Inserted {len(canadian_units)} Canadian units')

    # Step 5: Insert German Units
    german_units = [
        {'unit_designation': 'Forward HQ', 'quantity': 3, 'modifiers': '3 men in SdKfz 251/3', 'equipment_name': 'SdKfz 251/3'},
        {'unit_designation': 'Armoured Panzer Grenadier Platoon', 'modifiers': '(veterans) they must have the game abandoned from their half-tracks. Each now 5 men in Team is upgraded to an MG42', 'special_equipment': 'upgraded to an MG42, 5 SdKfz 251/1s'},
        {'unit_designation': 'SdKfz 251/10', 'equipment_name': 'SdKfz 251/10', 'quantity': 1},
        {'unit_designation': 'SdKfz 251/1', 'equipment_name': 'SdKfz 251/1', 'quantity': 1},
        {'unit_designation': 'Armoured Panzer Grenadier Platoon #2', 'modifiers': '(veterans) they must have the game abandoned from their half-tracks. Each now 5 men in Team is upgraded to an MG42', 'special_equipment': 'upgraded to an MG42'},
        {'unit_designation': 'SdKfz 251/10 #2', 'equipment_name': 'SdKfz 251/10', 'quantity': 1},
        {'unit_designation': 'SdKfz 251/1s', 'equipment_name': 'SdKfz 251/1', 'quantity': 3},
        {'unit_designation': 'SdKfz 251/9s', 'equipment_name': 'SdKfz 251/9', 'quantity': 2},
        {'unit_designation': 'Battery of 2 80mm mortars', 'equipment_name': '80mm mortar', 'quantity': 2, 'deployment_notes': 'off-table'},
    ]

    for unit in german_units:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (
            force_id, unit_designation, quantity, equipment_name,
            modifiers, special_equipment, deployment_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            german_force_id,
            unit.get('unit_designation'),
            unit.get('quantity'),
            unit.get('equipment_name'),
            unit.get('modifiers'),
            unit.get('special_equipment'),
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
