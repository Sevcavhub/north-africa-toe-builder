#!/usr/bin/env python3
"""
Extract all Early German vehicles from BattleGroup datacards.
Extracted manually from rendered PDF images due to corrupted text extraction.
"""

import json
from pathlib import Path

vehicles = []

# ============= PAGE 1: TANKS =============

# Row 1
vehicles.append({
    'name': 'Panzer II F',
    'year_range': '1941-1943',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'N',
    'armor_rear': 'N',
    'weapons': [
        {'weapon': '20mmL55', 'mount': 'Turret', 'ammo': 12},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer II C',
    'year_range': '1939-1943',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '20mmL55', 'mount': 'Turret', 'ammo': 12},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer I',
    'year_range': '1936-1943',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'O',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'MG', 'mount': 'Turret', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Turret', 'ammo': None}
    ]
})

# Row 2
vehicles.append({
    'name': 'Panzer III D',
    'year_range': '1939-1940',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'N',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '37mmL45', 'mount': 'Turret', 'ammo': 16},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer III E',
    'year_range': '1939-1940',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'N',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '37mmL45', 'mount': 'Turret', 'ammo': 16},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer III F',
    'year_range': '1939-1941',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'N',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '37mmL45', 'mount': 'Turret', 'ammo': 16},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

# Row 3
vehicles.append({
    'name': 'Panzer 38(t)',
    'year_range': '1939-1942',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'N',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '37mmL45', 'mount': 'Turret', 'ammo': 14},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer III L',
    'year_range': '1942-1943',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'K',
    'armor_side': 'L',
    'armor_rear': 'M',
    'weapons': [
        {'weapon': '50mmL60', 'mount': 'Turret', 'ammo': 14},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Flammenpanzer II',
    'year_range': '1940-1942',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'Flamethrower', 'mount': 'Fixed', 'ammo': None}
    ]
})

# Row 4
vehicles.append({
    'name': 'Panzer IV D',
    'year_range': '1939-1941',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '75mmL24', 'mount': 'Turret', 'ammo': 8},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer IV C',
    'year_range': '1938-1941',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '75mmL24', 'mount': 'Turret', 'ammo': 8},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer IV E',
    'year_range': '1940-1943',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'L',
    'armor_side': 'N',
    'armor_rear': 'N',
    'weapons': [
        {'weapon': '75mmL24', 'mount': 'Turret', 'ammo': 8},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

print(f'Page 1: {len(vehicles)} vehicles')

# ============= PAGE 2: MORE TANKS & ASSAULT GUNS =============

# Row 1
vehicles.append({
    'name': 'Panzer III G',
    'year_range': '1940-1941',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'L',
    'armor_side': 'M',
    'armor_rear': 'N',
    'weapons': [
        {'weapon': '50mmL42', 'mount': 'Turret', 'ammo': 14},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer IV F1/F2',
    'year_range': '1942-1943',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'L',
    'armor_side': 'N',
    'armor_rear': 'N',
    'weapons': [
        {'weapon': '75mmL24', 'mount': 'Turret', 'ammo': 8},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer III H',
    'year_range': '1940-1941',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'L',
    'armor_side': 'M',
    'armor_rear': 'N',
    'weapons': [
        {'weapon': '50mmL42', 'mount': 'Turret', 'ammo': 14},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

# Row 2
vehicles.append({
    'name': 'SdKfz 251/10',
    'year_range': '1939-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '37mmL45', 'mount': 'Pintle', 'ammo': 12}
    ]
})

vehicles.append({
    'name': 'Panzer III J',
    'year_range': '1941-1943',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'K',
    'armor_side': 'L',
    'armor_rear': 'M',
    'weapons': [
        {'weapon': '50mmL60', 'mount': 'Turret', 'ammo': 14},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panzer II M',
    'year_range': '1942-1943',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'L',
    'armor_side': 'M',
    'armor_rear': 'N',
    'weapons': [
        {'weapon': '20mmL55', 'mount': 'Turret', 'ammo': 12},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

# Row 3
vehicles.append({
    'name': 'Panzer 38(t) n.A.',
    'year_range': '1942-1943',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'K',
    'armor_side': 'L',
    'armor_rear': 'M',
    'weapons': [
        {'weapon': '37mmL45', 'mount': 'Turret', 'ammo': 14},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'StuG III A-E',
    'year_range': '1940-1942',
    'off_road_inches': 8,
    'road_inches': 12,
    'special_movement': None,
    'armor_front': 'K',
    'armor_side': 'M',
    'armor_rear': 'N',
    'weapons': [
        {'weapon': '75mmL24', 'mount': 'Fixed', 'ammo': 8}
    ]
})

vehicles.append({
    'name': 'Panzerjager I',
    'year_range': '1940-1943',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '47mmL43', 'mount': 'Fixed', 'ammo': 10}
    ]
})

# Row 4
vehicles.append({
    'name': 'SIG 33 auf Panzer I',
    'year_range': '1940-1942',
    'off_road_inches': 10,
    'road_inches': 14,
    'special_movement': None,
    'armor_front': 'O',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '150mmL11', 'mount': 'Fixed', 'ammo': 4}
    ]
})

vehicles.append({
    'name': 'Bunkerflak',
    'year_range': '1940-1945',
    'off_road_inches': None,
    'road_inches': None,
    'special_movement': 'Static',
    'armor_front': 'K',
    'armor_side': 'K',
    'armor_rear': 'K',
    'weapons': [
        {'weapon': '37mmL60', 'mount': 'AA', 'ammo': 12}
    ]
})

vehicles.append({
    'name': 'Munitions Carrier',
    'year_range': '1939-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': None,
    'armor_side': None,
    'armor_rear': None,
    'weapons': []
})

print(f'Page 2: {len(vehicles) - 12} vehicles (total: {len(vehicles)})')

# ============= PAGE 3: ARMORED CARS & HALFTRACKS =============

# Row 1
vehicles.append({
    'name': 'SdKfz 222',
    'year_range': '1938-1945',
    'off_road_inches': 10,
    'road_inches': 28,
    'special_movement': None,
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '20mmL55', 'mount': 'Turret', 'ammo': 10},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'SdKfz 223',
    'year_range': '1935-1945',
    'off_road_inches': 10,
    'road_inches': 28,
    'special_movement': None,
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'SdKfz 231 (6-rad)',
    'year_range': '1932-1942',
    'off_road_inches': 8,
    'road_inches': 24,
    'special_movement': None,
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '20mmL55', 'mount': 'Turret', 'ammo': 10},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

# Row 2
vehicles.append({
    'name': 'SdKfz 231',
    'year_range': '1937-1945',
    'off_road_inches': 10,
    'road_inches': 28,
    'special_movement': None,
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '20mmL55', 'mount': 'Turret', 'ammo': 10},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'Panhard 178',
    'year_range': '1940-1945',
    'off_road_inches': 10,
    'road_inches': 28,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'N',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '25mmL72', 'mount': 'Turret', 'ammo': 10},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'SdKfz 221',
    'year_range': '1935-1945',
    'off_road_inches': 10,
    'road_inches': 28,
    'special_movement': None,
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'MG', 'mount': 'Turret', 'ammo': None}
    ]
})

# Row 3
vehicles.append({
    'name': 'ADGz',
    'year_range': '1937-1944',
    'off_road_inches': 8,
    'road_inches': 24,
    'special_movement': None,
    'armor_front': 'M',
    'armor_side': 'N',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '20mmL55', 'mount': 'Turret', 'ammo': 10},
        {'weapon': 'MG', 'mount': 'Co-axial', 'ammo': None},
        {'weapon': 'MG', 'mount': 'Hull', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'RSO',
    'year_range': '1942-1945',
    'off_road_inches': 6,
    'road_inches': 14,
    'special_movement': 'Tracked',
    'armor_front': None,
    'armor_side': None,
    'armor_rear': None,
    'weapons': []
})

vehicles.append({
    'name': 'RSO/4',
    'year_range': '1943-1945',
    'off_road_inches': 6,
    'road_inches': 14,
    'special_movement': 'Tracked',
    'armor_front': None,
    'armor_side': None,
    'armor_rear': None,
    'weapons': []
})

# Row 4
vehicles.append({
    'name': 'SdKfz 250',
    'year_range': '1941-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'SdKfz 250/1',
    'year_range': '1941-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'SdKfz 251/1',
    'year_range': '1939-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
    ]
})

print(f'Page 3: {len(vehicles) - 24} vehicles (total: {len(vehicles)})')

# ============= PAGE 4: MORE HALFTRACKS (skip aircraft) =============

# Row 1
vehicles.append({
    'name': 'SdKfz 251/9',
    'year_range': '1942-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '75mmL24', 'mount': 'Fixed', 'ammo': 6}
    ]
})

vehicles.append({
    'name': 'SdKfz 251/1 (early)',
    'year_range': '1939-1942',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'O',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
    ]
})

vehicles.append({
    'name': 'SdKfz 251/4',
    'year_range': '1941-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': []
})

# Row 2
vehicles.append({
    'name': 'SdKfz 251/10 (early)',
    'year_range': '1939-1942',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'O',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': '37mmL45', 'mount': 'Pintle', 'ammo': 12}
    ]
})

vehicles.append({
    'name': 'SdKfz 251/7',
    'year_range': '1941-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': []
})

vehicles.append({
    'name': 'SdKfz 251/8',
    'year_range': '1941-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': []
})

# Row 3
vehicles.append({
    'name': 'SdKfz 251 (late)',
    'year_range': '1943-1945',
    'off_road_inches': 8,
    'road_inches': 18,
    'special_movement': 'Halftrack',
    'armor_front': 'N',
    'armor_side': 'O',
    'armor_rear': 'O',
    'weapons': [
        {'weapon': 'MG', 'mount': 'Pintle', 'ammo': None}
    ]
})

# Note: Skipping aircraft (Bf 109 E, Bf 109 C, HS-126, JU-87 D, Fieseler Storch) as they are not ground vehicles

print(f'Page 4: {len(vehicles) - 36} vehicles (total: {len(vehicles)})')

# ============= SAVE =============

output_path = Path('data/output/battlegroup_early_german_vehicles.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(vehicles, f, indent=2, ensure_ascii=False)

print(f'\n=== EXTRACTION COMPLETE ===')
print(f'Total vehicles extracted: {len(vehicles)}')
print(f'Saved to: {output_path}')

# Summary
print('\nVehicles by category:')
tanks = [v for v in vehicles if v['name'].startswith('Panzer') and 'SdKfz' not in v['name'] and 'StuG' not in v['name'] and 'jager' not in v['name']]
assault_guns = [v for v in vehicles if 'StuG' in v['name'] or 'jager' in v['name'] or 'SIG' in v['name']]
armored_cars = [v for v in vehicles if 'SdKfz 22' in v['name'] or 'ADGz' in v['name'] or 'Panhard' in v['name']]
halftracks = [v for v in vehicles if 'SdKfz 25' in v['name'] or 'Halftrack' in str(v.get('special_movement'))]
other = [v for v in vehicles if v not in tanks and v not in assault_guns and v not in armored_cars and v not in halftracks]

print(f'  Tanks: {len(tanks)}')
print(f'  Assault Guns/TDs: {len(assault_guns)}')
print(f'  Armored Cars: {len(armored_cars)}')
print(f'  Halftracks: {len(halftracks)}')
print(f'  Other: {len(other)}')

# Print all vehicle names
print('\nAll vehicles:')
for i, v in enumerate(vehicles, 1):
    print(f'{i:2d}. {v["name"]:25s} ({v["year_range"]:15s}) Movement: {v["off_road_inches"]}/{v["road_inches"]}')
