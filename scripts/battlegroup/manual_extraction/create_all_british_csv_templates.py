"""
Create CSV templates for ALL 8 pages of British DataCards
User fills in blank fields, then we import to database
"""

import csv

output_dir = 'D:/north-africa-toe-builder'

# All vehicles across all 8 pages (extracted from OCR)
all_vehicles = [
    # PAGE 1
    {'name': 'Vickers IV', 'page': 1},
    {'name': 'Vickers VI A-B', 'page': 1},
    {'name': 'Vickers VI C', 'page': 1},
    {'name': 'Matilda I', 'page': 1},
    {'name': 'Matilda II', 'page': 1},
    {'name': 'Matilda II CS', 'page': 1},
    {'name': 'A9', 'page': 1},
    {'name': 'A9 CS', 'page': 1},
    {'name': 'A10', 'page': 1},
    {'name': 'A13', 'page': 1},
    {'name': 'A13 MkII', 'page': 1},
    {'name': 'Valentine Bridgelayer', 'page': 1},

    # PAGE 2
    {'name': 'M4 Sherman Crab', 'page': 2},
    {'name': 'M4 Sherman BARV', 'page': 2},
    {'name': 'Cromwell (IV or V)', 'page': 2},
    {'name': 'Cromwell HQ', 'page': 2},
    {'name': 'Cromwell ARV', 'page': 2},
    {'name': 'Challenger', 'page': 2},
    {'name': 'M10 Wolverine', 'page': 2},
    {'name': 'M10 Achilles', 'page': 2},
    {'name': 'Archer', 'page': 2},
    {'name': 'M7 Priest', 'page': 2},
    {'name': 'Sexton', 'page': 2},
    {'name': 'Comet', 'page': 2},

    # PAGE 3
    {'name': 'M5 Stuart (A1, A2, A3)', 'page': 3},
    {'name': 'M5 Recce', 'page': 3},
    {'name': 'M24 Chaffee', 'page': 3},
    {'name': 'M4 Sherman (A1, A2, A3)', 'page': 3},
    {'name': 'M4 Sherman (76mm)', 'page': 3},
    {'name': 'M4 Sherman Firefly', 'page': 3},
    {'name': 'M4 Sherman Dozer', 'page': 3},
    {'name': 'M4 Sherman DD', 'page': 3},
    {'name': 'Sherman ARV', 'page': 3},
    {'name': 'Tetrarch', 'page': 3},
    {'name': 'Tetrarch CS', 'page': 3},

    # PAGE 4
    {'name': 'Crusader AA MkI', 'page': 4},
    {'name': 'Crusader AA MkII (2x 20mm)', 'page': 4},
    {'name': 'Crusader AA MkII (3x 20mm)', 'page': 4},
    {'name': 'Crusader Tractor', 'page': 4},
    {'name': 'Centaur Bulldozer', 'page': 4},
    {'name': 'Bren Carrier', 'page': 4},
    {'name': 'Wasp', 'page': 4},
    {'name': 'Loyd Carrier', 'page': 4},
    {'name': 'Dorchester ACV', 'page': 4},
    {'name': 'Guy Lizard ACV', 'page': 4},
    {'name': 'LVT IV (20mm)', 'page': 4},
    {'name': 'LVT IV (MG)', 'page': 4},

    # PAGE 5
    {'name': 'AEC III', 'page': 5},
    {'name': 'Daimler', 'page': 5},
    {'name': 'M3 Scout Car', 'page': 5},
    {'name': 'M8 Greyhound', 'page': 5},
    {'name': 'Dingo', 'page': 5},
    {'name': 'Humber Scout Car', 'page': 5},
    {'name': 'M5 (also M9)', 'page': 5},
    {'name': 'Humber IV', 'page': 5},
    {'name': 'M5 Ambulance', 'page': 5},
    {'name': 'Guy Mk1', 'page': 5},
    {'name': 'Staghound', 'page': 5},
    {'name': 'Staghound AA', 'page': 5},

    # PAGE 6
    {'name': 'Churchill III', 'page': 6},
    {'name': 'Churchill V', 'page': 6},
    {'name': 'Churchill VI', 'page': 6},
    {'name': 'Churchill VII', 'page': 6},
    {'name': 'Churchill VIII', 'page': 6},
    {'name': 'Churchill AVRE (280mm)', 'page': 6},
    {'name': 'Churchill Crocodile', 'page': 6},
    {'name': 'Churchill Ark', 'page': 6},
    {'name': 'Churchill ARV', 'page': 6},
    {'name': 'Churchill AVRE Bridge', 'page': 6},
    {'name': 'Centaur IV', 'page': 6},
    {'name': 'Centaur AA', 'page': 6},

    # PAGE 7
    {'name': 'Humber Light Recce', 'page': 7},
    {'name': 'Morris CS9', 'page': 7},
    {'name': 'RAM Kangaroo', 'page': 7},
    {'name': 'Sherman Kangaroo', 'page': 7},
    {'name': 'Armoured Bulldozer', 'page': 7},

    # PAGE 8
    {'name': 'M3 Honey (A1, A2, A3)', 'page': 8},
]

# All unique guns (deduplicated across pages)
all_guns = [
    {'name': '15mm Besa', 'caliber_mm': 15},
    {'name': '2 pdr', 'caliber_mm': 40},
    {'name': '3in Howitzer', 'caliber_mm': 76},
    {'name': '6 pdr', 'caliber_mm': 57},
    {'name': '17 pdr', 'caliber_mm': 76},
    {'name': '75mmL40', 'caliber_mm': 75},
    {'name': '76mmL53', 'caliber_mm': 76},
    {'name': '77mmL50', 'caliber_mm': 77},
    {'name': '95mmL20', 'caliber_mm': 95},
    {'name': '105mmL22', 'caliber_mm': 105},
    {'name': '25 pdr', 'caliber_mm': 87},
    {'name': '37mmL53', 'caliber_mm': 37},
    {'name': '40mmL60', 'caliber_mm': 40},
    {'name': '20mm Oerlikon', 'caliber_mm': 20},
    {'name': '280mm Petard', 'caliber_mm': 280},
]

# Aircraft from page 7
all_aircraft = [
    {'aircraft_name': 'Typhoon', 'role': 'Fighter-Bomber', 'hits': 4, 'weaponry_full': '4 x 20mm cannons, 8 x 60 lbs rockets or 2 x large bomb or 4x medium bombs'},
    {'aircraft_name': 'Spitfire MkIX', 'role': 'Fighter', 'hits': 3, 'weaponry_full': '2 x 20mm cannons, 2 x small bombs'},
    {'aircraft_name': 'Tempest', 'role': 'Fighter-Bomber', 'hits': 4, 'weaponry_full': '4 x 20mm cannons, 2 x medium bombs'},
    {'aircraft_name': 'Hurricane MkI', 'role': 'Fighter-Bomber', 'hits': '', 'weaponry_full': '2 x large bombs or 4x small bombs'},
    {'aircraft_name': 'Blenheim MkIV', 'role': 'Light Bomber', 'hits': 4, 'weaponry_full': '3x MG (low and slow)'},
    {'aircraft_name': 'Fairey Battle', 'role': 'Fighter-Bomber', 'hits': 3, 'weaponry_full': '2x MGs, 4 x small bombs'},
]

def create_all_csvs():
    print('Creating CSV templates for all British DataCards...')
    print('='*80)

    # Create VEHICLES CSV
    vehicle_fields = ['name', 'nation', 'vehicle_type', 'off_road_inches', 'road_inches', 'special_movement',
                      'armor_front', 'armor_side', 'armor_rear', 'weapons',
                      'points_cost', 'battle_rating', 'special_rules', 'page_number']

    with open(f'{output_dir}/british_datacards_ALL_VEHICLES.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=vehicle_fields)
        writer.writeheader()
        for v in all_vehicles:
            writer.writerow({
                'name': v['name'],
                'nation': 'british',
                'vehicle_type': '',
                'off_road_inches': '',
                'road_inches': '',
                'special_movement': '',
                'armor_front': '',
                'armor_side': '',
                'armor_rear': '',
                'weapons': '',
                'points_cost': '',
                'battle_rating': '',
                'special_rules': '',
                'page_number': v['page']
            })

    print(f'Created: british_datacards_ALL_VEHICLES.csv ({len(all_vehicles)} vehicles)')

    # Create GUNS CSV
    gun_fields = ['name', 'nation', 'caliber_mm', 'he_dice', 'he_target',
                  'ap_0_10', 'ap_10_20', 'ap_20_30', 'ap_30_40', 'ap_40_50', 'ap_50_70']

    with open(f'{output_dir}/british_datacards_ALL_GUNS.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=gun_fields)
        writer.writeheader()
        for g in all_guns:
            writer.writerow({
                'name': g['name'],
                'nation': 'british',
                'caliber_mm': g['caliber_mm'],
                'he_dice': '',
                'he_target': '',
                'ap_0_10': '',
                'ap_10_20': '',
                'ap_20_30': '',
                'ap_30_40': '',
                'ap_40_50': '',
                'ap_50_70': ''
            })

    print(f'Created: british_datacards_ALL_GUNS.csv ({len(all_guns)} guns)')

    # Create AIRCRAFT CSV
    aircraft_fields = ['aircraft_name', 'nation', 'role', 'hits', 'weaponry_full',
                       'cannon_count', 'cannon_caliber', 'rockets', 'bombs',
                       'machine_guns', 'special_notes']

    with open(f'{output_dir}/british_datacards_ALL_AIRCRAFT.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=aircraft_fields)
        writer.writeheader()
        for a in all_aircraft:
            writer.writerow({
                'aircraft_name': a['aircraft_name'],
                'nation': 'british',
                'role': a['role'],
                'hits': a['hits'],
                'weaponry_full': a['weaponry_full'],
                'cannon_count': '',
                'cannon_caliber': '',
                'rockets': '',
                'bombs': '',
                'machine_guns': '',
                'special_notes': ''
            })

    print(f'Created: british_datacards_ALL_AIRCRAFT.csv ({len(all_aircraft)} aircraft)')

    print('\n' + '='*80)
    print('CSV TEMPLATES CREATED SUCCESSFULLY!')
    print('='*80)
    print(f'\nTotal to extract:')
    print(f'  Vehicles: {len(all_vehicles)}')
    print(f'  Guns: {len(all_guns)}')
    print(f'  Aircraft: {len(all_aircraft)}')
    print('\nPlease fill in all blank fields using the PDF/OCR files as reference.')
    print('OCR text files are available: british_datacard_page1-8_OCR.txt')

if __name__ == '__main__':
    create_all_csvs()
