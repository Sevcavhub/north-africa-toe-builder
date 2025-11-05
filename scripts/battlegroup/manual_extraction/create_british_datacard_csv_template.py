"""
Create CSV template for British DataCards extraction
Populates what can be read from OCR, user fills in the rest
"""

import csv

# Based on OCR from page 1 of Battlegroup-DataCards-British.pdf
vehicles_page1 = [
    # Row 1
    {'vehicle_name': 'Vickers IV', 'nation': 'british', 'vehicle_type': 'Light Tank',
     'armor_front': '', 'armor_side': '', 'armor_rear': '',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '12', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': '', 'gun_name': 'MG', 'gun_type': 'MG',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    {'vehicle_name': 'Vickers VI A-B', 'nation': 'british', 'vehicle_type': 'Light Tank',
     'armor_front': '', 'armor_side': '', 'armor_rear': '',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '12', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': '', 'gun_name': 'MG', 'gun_type': 'MG',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    {'vehicle_name': 'Vickers VI C', 'nation': 'british', 'vehicle_type': 'Light Tank',
     'armor_front': '', 'armor_side': '', 'armor_rear': '',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '12', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': '', 'gun_name': '15mm Besa', 'gun_type': 'AT Gun',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    # Row 2
    {'vehicle_name': 'Matilda I', 'nation': 'british', 'vehicle_type': 'Infantry Tank',
     'armor_front': 'K', 'armor_side': 'K', 'armor_rear': 'L',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '4', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': '', 'gun_name': 'MG', 'gun_type': 'MG',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    {'vehicle_name': 'Matilda II', 'nation': 'british', 'vehicle_type': 'Infantry Tank',
     'armor_front': 'J', 'armor_side': 'K', 'armor_rear': 'L',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '8', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': '', 'gun_name': '2 pdr', 'gun_type': 'AT Gun',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    {'vehicle_name': 'Matilda II CS', 'nation': 'british', 'vehicle_type': 'Infantry Tank',
     'armor_front': 'J', 'armor_side': 'K', 'armor_rear': 'L',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '8', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': '', 'gun_name': '3in Howitzer', 'gun_type': 'Howitzer',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    # Row 3
    {'vehicle_name': 'A9', 'nation': 'british', 'vehicle_type': 'Cruiser Tank',
     'armor_front': 'N', 'armor_side': '', 'armor_rear': '',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '12', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': 'Unreliable', 'gun_name': '2 pdr', 'gun_type': 'AT Gun',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    {'vehicle_name': 'A9 CS', 'nation': 'british', 'vehicle_type': 'Cruiser Tank',
     'armor_front': 'N', 'armor_side': '', 'armor_rear': '',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '12', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': 'Unreliable', 'gun_name': '3in Howitzer', 'gun_type': 'Howitzer',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    {'vehicle_name': 'A10', 'nation': 'british', 'vehicle_type': 'Cruiser Tank',
     'armor_front': 'M', 'armor_side': 'N', 'armor_rear': '',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '8', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': 'Unreliable', 'gun_name': '2 pdr', 'gun_type': 'AT Gun',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    # Row 4
    {'vehicle_name': 'A13', 'nation': 'british', 'vehicle_type': 'Cruiser Tank',
     'armor_front': 'M', 'armor_side': 'N', 'armor_rear': '',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '15', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': '', 'gun_name': '2 pdr', 'gun_type': 'AT Gun',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    {'vehicle_name': 'A13 MkII', 'nation': 'british', 'vehicle_type': 'Cruiser Tank',
     'armor_front': 'L', 'armor_side': 'M', 'armor_rear': '',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '15', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': '', 'gun_name': '2 pdr', 'gun_type': 'AT Gun',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},

    {'vehicle_name': 'Valentine Bridgelayer', 'nation': 'british', 'vehicle_type': 'Engineering Vehicle',
     'armor_front': 'K', 'armor_side': 'K', 'armor_rear': 'L',
     'armor_turret_front': '', 'armor_turret_side': '', 'armor_turret_rear': '',
     'movement': '8', 'crew': '', 'points': '', 'battle_rating': '',
     'vehicle_special_rules': 'Bridge', 'gun_name': '', 'gun_type': '',
     'he_0_20': '', 'he_20_30': '', 'he_30_40': '', 'he_40_50': '', 'he_50_60': '',
     'ap_0_20': '', 'ap_20_30': '', 'ap_30_40': '', 'ap_40_50': '', 'ap_50_60': ''},
]

# CSV field names matching database schema
fieldnames = [
    'vehicle_name', 'nation', 'vehicle_type',
    'armor_front', 'armor_side', 'armor_rear',
    'armor_turret_front', 'armor_turret_side', 'armor_turret_rear',
    'movement', 'crew', 'points', 'battle_rating', 'vehicle_special_rules',
    'gun_name', 'gun_type',
    'he_0_20', 'he_20_30', 'he_30_40', 'he_40_50', 'he_50_60',
    'ap_0_20', 'ap_20_30', 'ap_30_40', 'ap_40_50', 'ap_50_60'
]

def create_csv_template():
    """Create CSV template with OCR-extracted data"""

    csv_path = r'D:\north-africa-toe-builder\british_datacards_page1_TEMPLATE.csv'

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(vehicles_page1)

    print(f'✓ Created CSV template: {csv_path}')
    print(f'✓ Extracted {len(vehicles_page1)} vehicles from page 1')
    print('\nPlease fill in the blank fields in the CSV file:')
    print('  - armor_turret_front, armor_turret_side, armor_turret_rear')
    print('  - crew, points, battle_rating')
    print('  - HE/AP penetration values (he_0_20 through ap_50_60)')
    print('  - Complete any missing armor values')
    print('  - Add/verify special rules')
    print('\nRange bands in BattleGroup:')
    print('  0-20" = 0-20 inches')
    print('  20-30" = 20-30 inches')
    print('  30-40" = 30-40 inches')
    print('  40-50" = 40-50 inches')
    print('  50-60" = 50-60 inches (shown as 50-70" in some tables)')

if __name__ == '__main__':
    create_csv_template()
