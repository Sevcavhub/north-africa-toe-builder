#!/usr/bin/env python3
"""
Extract British/Commonwealth vehicle data from BattleGroup datacards.
Manually transcribed from visual inspection of PDF pages.
"""

import json

# Manually transcribed from the datacard images
vehicles = [
    # Page 1 - Early tanks and cruisers
    {
        'name': 'Vickers Mk IV',
        'year_range': '1940',
        'off_road_inches': 8,
        'road_inches': 12,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Turret', 'ammo': None}
        ]
    },
    {
        'name': 'Vickers Mk VI A/B',
        'year_range': '1940',
        'off_road_inches': 10,
        'road_inches': 14,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Turret', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Vickers Mk VI C',
        'year_range': '1940-42',
        'off_road_inches': 10,
        'road_inches': 14,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '15mm Besa', 'mount': 'Turret', 'ammo': 12},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Matilda I',
        'year_range': '1940',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': None,
        'armor_front': 'G',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Turret', 'ammo': None}
        ]
    },
    {
        'name': 'Matilda II',
        'year_range': '1940-42',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': None,
        'armor_front': 'E',
        'armor_side': 'H',
        'armor_rear': 'I',
        'weapons': [
            {'weapon': '2pdr', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Matilda II CS',
        'year_range': '1940-42',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': None,
        'armor_front': 'E',
        'armor_side': 'H',
        'armor_rear': 'I',
        'weapons': [
            {'weapon': '3" Howitzer', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'A9 Cruiser',
        'year_range': '1940',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'L',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '2pdr', 'mount': 'Turret', 'ammo': 8},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': '2x MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'A9 CS Cruiser',
        'year_range': '1940',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'L',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '3.7" Howitzer', 'mount': 'Turret', 'ammo': 6},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': '2x MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'A10 Cruiser',
        'year_range': '1940-41',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'K',
        'armor_side': 'M',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '2pdr', 'mount': 'Turret', 'ammo': 8},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'A13 Mk I Cruiser',
        'year_range': '1940-41',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': None,
        'armor_front': 'M',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '2pdr', 'mount': 'Turret', 'ammo': 8},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Valentine (Bridgelayer)',
        'year_range': '1941-45',
        'off_road_inches': 8,
        'road_inches': 12,
        'special_movement': 'Engineer',
        'armor_front': 'I',
        'armor_side': 'K',
        'armor_rear': 'L',
        'weapons': []
    },

    # Page 2 - More cruisers and heavy tanks
    {
        'name': 'M4 Sherman Crab',
        'year_range': '1944-45',
        'off_road_inches': 9,
        'road_inches': 14,
        'special_movement': 'Engineer',
        'armor_front': 'K',
        'armor_side': 'L',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '75mm L40', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'M4 Sherman Barv',
        'year_range': '1944-45',
        'off_road_inches': 9,
        'road_inches': 14,
        'special_movement': 'Amphib',
        'armor_front': 'K',
        'armor_side': 'L',
        'armor_rear': 'N',
        'weapons': []
    },
    {
        'name': 'Cromwell IV (w/6pdr)',
        'year_range': '1944',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': None,
        'armor_front': 'J',
        'armor_side': 'L',
        'armor_rear': 'M',
        'weapons': [
            {'weapon': '6pdr', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Cromwell I/II/III',
        'year_range': '1944',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': None,
        'armor_front': 'J',
        'armor_side': 'L',
        'armor_rear': 'M',
        'weapons': [
            {'weapon': '6pdr', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Challenger',
        'year_range': '1944-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'J',
        'armor_side': 'M',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '17pdr', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Cromwell VIII',
        'year_range': '1944-45',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': None,
        'armor_front': 'I',
        'armor_side': 'L',
        'armor_rear': 'M',
        'weapons': [
            {'weapon': '95mm', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'M10 Wolverine',
        'year_range': '1943-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'K',
        'armor_side': 'M',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '3" AA', 'mount': 'Turret', 'ammo': 8},
            {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
        ]
    },
    {
        'name': 'M10 Achilles',
        'year_range': '1944-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'K',
        'armor_side': 'M',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '17pdr', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
        ]
    },
    {
        'name': 'Archer',
        'year_range': '1944-45',
        'off_road_inches': 8,
        'road_inches': 12,
        'special_movement': None,
        'armor_front': 'M',
        'armor_side': 'N',
        'armor_rear': 'J',
        'weapons': [
            {'weapon': '17pdr', 'mount': 'Hull', 'ammo': 7}
        ]
    },
    {
        'name': 'M7 Priest',
        'year_range': '1942-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'L',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '105mm Howitzer', 'mount': 'Hull', 'ammo': 8},
            {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
        ]
    },
    {
        'name': 'Sexton',
        'year_range': '1943-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'L',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '25pdr', 'mount': 'Hull', 'ammo': 8}
        ]
    },
    {
        'name': 'Comet',
        'year_range': '1945',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': None,
        'armor_front': 'I',
        'armor_side': 'K',
        'armor_rear': 'L',
        'weapons': [
            {'weapon': '77mm HV', 'mount': 'Turret', 'ammo': 8},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
        ]
    },

    # Page 3 - Sherman variants
    {
        'name': 'M4 Sherman (A1, A2, A3)',
        'year_range': '1942-45',
        'off_road_inches': 9,
        'road_inches': 14,
        'special_movement': None,
        'armor_front': 'K',
        'armor_side': 'L',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '75mm L40', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'M4 Sherman Firefly',
        'year_range': '1944-45',
        'off_road_inches': 8,
        'road_inches': 12,
        'special_movement': None,
        'armor_front': 'K',
        'armor_side': 'L',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '17pdr', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'M4 Sherman Dozer',
        'year_range': '1944-45',
        'off_road_inches': 9,
        'road_inches': 14,
        'special_movement': 'Engineer',
        'armor_front': 'K',
        'armor_side': 'L',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '75mm L40', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'M4 Sherman 76',
        'year_range': '1944-45',
        'off_road_inches': 9,
        'road_inches': 14,
        'special_movement': None,
        'armor_front': 'K',
        'armor_side': 'L',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '76mm L53', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'Tetrarch',
        'year_range': '1944-45',
        'off_road_inches': 14,
        'road_inches': 20,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '2pdr', 'mount': 'Turret', 'ammo': 5},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Tetrarch CS',
        'year_range': '1944-45',
        'off_road_inches': 14,
        'road_inches': 20,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '3" Howitzer', 'mount': 'Turret', 'ammo': 5},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'M4 Sherman DD',
        'year_range': '1944-45',
        'off_road_inches': 9,
        'road_inches': 14,
        'special_movement': 'Amphib',
        'armor_front': 'K',
        'armor_side': 'L',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '75mm L40', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'M4 Sherman ARV',
        'year_range': '1944-45',
        'off_road_inches': 9,
        'road_inches': 14,
        'special_movement': 'Recover',
        'armor_front': 'K',
        'armor_side': 'L',
        'armor_rear': 'N',
        'weapons': []
    },

    # Page 4 - Cruisers and carriers
    {
        'name': 'Crusader I AA Mk I',
        'year_range': '1941-42',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': None,
        'armor_front': 'L',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '2x MG', 'mount': 'Turret', 'ammo': None}
        ]
    },
    {
        'name': 'Crusader I AA Mk II',
        'year_range': '1941-42',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': None,
        'armor_front': 'L',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '20mm', 'mount': 'Turret', 'ammo': 12}
        ]
    },
    {
        'name': 'Crusader I AA "Triple"',
        'year_range': '1941-42',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': None,
        'armor_front': 'L',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '3x 20mm', 'mount': 'Turret', 'ammo': 15}
        ]
    },
    {
        'name': 'Crusader Tractor',
        'year_range': '1941-45',
        'off_road_inches': 12,
        'road_inches': 18,
        'special_movement': 'Tow',
        'armor_front': 'L',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': []
    },
    {
        'name': 'Centaur Bulldozer',
        'year_range': '1944-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': 'Engineer',
        'armor_front': 'J',
        'armor_side': 'L',
        'armor_rear': 'M',
        'weapons': []
    },
    {
        'name': 'Bren Carrier',
        'year_range': '1940-45',
        'off_road_inches': 10,
        'road_inches': 14,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
        ]
    },
    {
        'name': 'Wasp',
        'year_range': '1942-45',
        'off_road_inches': 10,
        'road_inches': 14,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'Flamethrower', 'mount': 'Hull', 'ammo': 4}
        ]
    },
    {
        'name': 'Loyd Carrier',
        'year_range': '1940-45',
        'off_road_inches': 10,
        'road_inches': 14,
        'special_movement': 'Transport',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': []
    },
    {
        'name': 'Dorchester ACV',
        'year_range': '1941-45',
        'off_road_inches': 8,
        'road_inches': 12,
        'special_movement': 'Command',
        'armor_front': 'M',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': []
    },
    {
        'name': 'Guy Lizard ACV',
        'year_range': '1940-42',
        'off_road_inches': 8,
        'road_inches': 14,
        'special_movement': 'Command',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': []
    },
    {
        'name': 'LVT-IV Buffalo',
        'year_range': '1944-45',
        'off_road_inches': 8,
        'road_inches': 10,
        'special_movement': 'Amphib',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '75mm Howitzer', 'mount': 'Hull', 'ammo': 7}
        ]
    },
    {
        'name': 'LVT-IV Buffalo (A)',
        'year_range': '1944-45',
        'off_road_inches': 8,
        'road_inches': 10,
        'special_movement': 'Amphib',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '2x MG', 'mount': 'Turret', 'ammo': None}
        ]
    },

    # Page 5 - Armored cars and scouts
    {
        'name': 'AEC III',
        'year_range': '1943-45',
        'off_road_inches': 10,
        'road_inches': 24,
        'special_movement': 'Recce',
        'armor_front': 'K',
        'armor_side': 'N',
        'armor_rear': 'N',
        'weapons': [
            {'weapon': '75mm', 'mount': 'Turret', 'ammo': 8},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Daimler',
        'year_range': '1941-45',
        'off_road_inches': 8,
        'road_inches': 24,
        'special_movement': 'Recce',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '2pdr', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'M3 Scout Car',
        'year_range': '1941-45',
        'off_road_inches': 10,
        'road_inches': 24,
        'special_movement': 'Recce',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
        ]
    },
    {
        'name': 'M3 Greyhound',
        'year_range': '1943-45',
        'off_road_inches': 10,
        'road_inches': 24,
        'special_movement': 'Recce',
        'armor_front': 'M',
        'armor_side': 'N',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '37mm', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Daimler Dingo',
        'year_range': '1940-45',
        'off_road_inches': 10,
        'road_inches': 24,
        'special_movement': 'Recce',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
        ]
    },
    {
        'name': 'Humber Scout Car',
        'year_range': '1942-45',
        'off_road_inches': 10,
        'road_inches': 24,
        'special_movement': 'Recce',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
        ]
    },
    {
        'name': 'M3 Halftrack',
        'year_range': '1942-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': 'Transport',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
        ]
    },
    {
        'name': 'Humberley',
        'year_range': '1943-45',
        'off_road_inches': 10,
        'road_inches': 24,
        'special_movement': 'Recce',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '15mm Besa', 'mount': 'Turret', 'ammo': 12},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'M4 Ambulance',
        'year_range': '1943-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': 'Medic',
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': []
    },
    {
        'name': 'Guy Lizard Mk I',
        'year_range': '1940-42',
        'off_road_inches': 8,
        'road_inches': 14,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'O',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': 'MG', 'mount': 'Turret', 'ammo': None}
        ]
    },
    {
        'name': 'Staghound',
        'year_range': '1943-45',
        'off_road_inches': 8,
        'road_inches': 24,
        'special_movement': 'Recce',
        'armor_front': 'M',
        'armor_side': 'N',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '37mm', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
        ]
    },
    {
        'name': 'Staghound AA',
        'year_range': '1944',
        'off_road_inches': 8,
        'road_inches': 24,
        'special_movement': None,
        'armor_front': 'N',
        'armor_side': 'N',
        'armor_rear': 'O',
        'weapons': [
            {'weapon': '2x MG', 'mount': 'Turret', 'ammo': None}
        ]
    },

    # Page 6 - Churchill variants
    {
        'name': 'Churchill III',
        'year_range': '1942-43',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': None,
        'armor_front': 'F',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': [
            {'weapon': '6pdr', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
            {'weapon': '3" Howitzer', 'mount': 'Hull', 'ammo': 7}
        ]
    },
    {
        'name': 'Churchill V',
        'year_range': '1943-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': None,
        'armor_front': 'F',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': [
            {'weapon': '95mm', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Churchill VI',
        'year_range': '1943-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': None,
        'armor_front': 'F',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': [
            {'weapon': '75mm', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Churchill VII',
        'year_range': '1944-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': None,
        'armor_front': 'D',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': [
            {'weapon': '75mm', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Churchill VIII',
        'year_range': '1944-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': None,
        'armor_front': 'D',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': [
            {'weapon': '95mm', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Churchill AVRE',
        'year_range': '1944-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': 'Engineer',
        'armor_front': 'F',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': [
            {'weapon': '290mm Petard', 'mount': 'Turret', 'ammo': 3}
        ]
    },
    {
        'name': 'Churchill w/Goat II',
        'year_range': '1944-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': 'Engineer',
        'armor_front': 'F',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': [
            {'weapon': '6pdr', 'mount': 'Turret', 'ammo': 9},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Churchill ARK',
        'year_range': '1944-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': 'Engineer',
        'armor_front': 'F',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': []
    },
    {
        'name': 'Churchill ARV',
        'year_range': '1944-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': 'Recover',
        'armor_front': 'F',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': []
    },
    {
        'name': 'AVRE Bridgelayer',
        'year_range': '1944-45',
        'off_road_inches': 6,
        'road_inches': 10,
        'special_movement': 'Engineer',
        'armor_front': 'F',
        'armor_side': 'I',
        'armor_rear': 'K',
        'weapons': []
    },
    {
        'name': 'Centaur IV',
        'year_range': '1944-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'J',
        'armor_side': 'L',
        'armor_rear': 'M',
        'weapons': [
            {'weapon': '95mm', 'mount': 'Turret', 'ammo': 7},
            {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
        ]
    },
    {
        'name': 'Centaur AA',
        'year_range': '1944-45',
        'off_road_inches': 10,
        'road_inches': 16,
        'special_movement': None,
        'armor_front': 'J',
        'armor_side': 'L',
        'armor_rear': 'M',
        'weapons': [
            {'weapon': '2x 20mm', 'mount': 'Turret', 'ammo': 15}
        ]
    }
]

def main():
    output_path = r'D:\north-africa-toe-builder\data\output\battlegroup_british_vehicles.json'

    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vehicles, f, indent=2)

    print(f'Extracted {len(vehicles)} British/Commonwealth vehicles')
    print(f'Saved to {output_path}')

    # Summary by category
    tanks = [v for v in vehicles if any(x in v['name'].lower() for x in ['sherman', 'churchill', 'cromwell', 'crusader', 'matilda', 'valentine', 'comet', 'challenger', 'centaur', 'tetrarch', 'vickers'])]
    tank_destroyers = [v for v in vehicles if any(x in v['name'].lower() for x in ['wolverine', 'achilles', 'archer'])]
    spgs = [v for v in vehicles if any(x in v['name'].lower() for x in ['priest', 'sexton'])]
    armored_cars = [v for v in vehicles if any(x in v['name'].lower() for x in ['daimler', 'staghound', 'humber', 'aec', 'greyhound', 'scout', 'dingo', 'guy', 'lizard'])]
    carriers = [v for v in vehicles if any(x in v['name'].lower() for x in ['carrier', 'wasp', 'loyd', 'buffalo', 'halftrack', 'ambulance'])]

    print(f'\nBreakdown:')
    print(f'  Tanks: {len(tanks)}')
    print(f'  Tank Destroyers: {len(tank_destroyers)}')
    print(f'  SPGs: {len(spgs)}')
    print(f'  Armored Cars: {len(armored_cars)}')
    print(f'  Carriers/Transports: {len(carriers)}')

    # List all vehicles
    print(f'\nComplete vehicle list:')
    for v in vehicles:
        weapons_str = f"{len(v['weapons'])} weapons" if v['weapons'] else "unarmed"
        print(f"  - {v['name']} ({v['year_range']}) - {weapons_str}")

if __name__ == '__main__':
    main()
