#!/usr/bin/env python3
"""
Extract Surrounded at La Ferme Scenario from Canada's Crucible supplement
Populates BG_Scenario_Army_Lists, BG_Scenario_Forces, and BG_Scenario_Units tables
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Army Lists/Pre-built Surrounded Scenario Army List .png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Extracting Surrounded at La Ferme Scenario...')
    print()

    # Step 1: Insert scenario
    cursor.execute('''
    INSERT INTO BG_Scenario_Army_Lists (
        scenario_name, scenario_size, source_supplement, source_image_location
    ) VALUES (?, ?, ?, ?)
    ''', (
        'Surrounded at La Ferme',
        None,
        'Battlegroup-Canadas-Crucible',
        SCREENSHOT_FILE
    ))
    scenario_id = cursor.lastrowid
    print(f'  [OK] Inserted scenario: Surrounded at La Ferme (ID: {scenario_id})')

    # Step 2: Insert Canadian Forces (Farm Fortress - Defenders)
    cursor.execute('''
    INSERT INTO BG_Scenario_Forces (
        scenario_id, force_name, side, nation, br_total, officers_count, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        scenario_id,
        'Canadian Forces',
        'Allied',
        'canadian',
        22,
        2,  # including senior officer Cephas Brown
        'Farm Fortress - very sturdily constructed fortifications of thick stone'
    ))
    canadian_force_id = cursor.lastrowid
    print(f'  [OK] Inserted Canadian Forces (ID: {canadian_force_id})')

    # Step 3: Insert German Forces (Attackers)
    cursor.execute('''
    INSERT INTO BG_Scenario_Forces (
        scenario_id, force_name, side, nation, br_total, officers_count, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        scenario_id,
        'German Forces',
        'Axis',
        'german',
        15,
        1,
        'Panther Platoon assault force'
    ))
    german_force_id = cursor.lastrowid
    print(f'  [OK] Inserted German Forces (ID: {german_force_id})')

    # Step 4: Insert Canadian Units
    canadian_units = [
        {'unit_designation': 'Forward HQ', 'quantity': 2, 'modifiers': '2 men (Cephas Brown, senior officer)', 'officer_count': 1, 'deployment_notes': 'may start dug-in to foxholes'},
        {'unit_designation': 'Infantry Platoon', 'modifiers': '3 sections', 'deployment_notes': 'may start dug-in to foxholes'},
        {'unit_designation': 'Ad hoc AT team', 'quantity': 2, 'special_equipment': 'anti-tank grenades', 'deployment_notes': 'may start dug-in to foxholes'},
        {'unit_designation': 'Ad hoc AT team', 'quantity': 2, 'special_equipment': 'anti-tank grenades', 'deployment_notes': 'may start dug-in to foxholes'},
        {'unit_designation': 'Vickers HMG team', 'equipment_name': 'Vickers HMG', 'deployment_notes': 'may start dug-in to foxholes'},
        {'unit_designation': '6pdr anti-tank gun', 'equipment_name': '6pdr', 'quantity': 2, 'special_equipment': 'loader teams, Loyd carrier tows', 'deployment_notes': 'in anti-tank gun dug-outs'},
        {'unit_designation': 'Minefield', 'quantity': 1, 'deployment_notes': 'must be placed on the track to the farm\'s gate'},
    ]

    for unit in canadian_units:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (
            force_id, unit_designation, quantity, equipment_name,
            modifiers, special_equipment, officer_count, deployment_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            canadian_force_id,
            unit.get('unit_designation'),
            unit.get('quantity'),
            unit.get('equipment_name'),
            unit.get('modifiers'),
            unit.get('special_equipment'),
            unit.get('officer_count', 0),
            unit.get('deployment_notes')
        ))

    print(f'  [OK] Inserted {len(canadian_units)} Canadian units')

    # Step 5: Insert German Units
    german_units = [
        {'unit_designation': 'Panther Platoon', 'equipment_name': 'Panther', 'quantity': 5, 'officer_count': 1, 'modifiers': '1 officer'},
    ]

    for unit in german_units:
        cursor.execute('''
        INSERT INTO BG_Scenario_Units (
            force_id, unit_designation, quantity, equipment_name,
            modifiers, officer_count
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            german_force_id,
            unit.get('unit_designation'),
            unit.get('quantity'),
            unit.get('equipment_name'),
            unit.get('modifiers'),
            unit.get('officer_count', 0)
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
