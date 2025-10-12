import os
import glob
import json

# Find all 1941-Q2 unit files
units = glob.glob('data/output/*/units/*1941*q2*.json') + glob.glob('data/output/*/units/*1941*Q2*.json')
print(f'Total 1941-Q2 unit files found: {len(units)}')

# Group by nation
nations = {}
for u in units:
    basename = os.path.basename(u)
    nation = basename.split('_')[0]
    nations[nation] = nations.get(nation, 0) + 1

print(f'\nBy nation:')
for n, c in sorted(nations.items()):
    print(f'  {n}: {c} units')

# Get unique unit names (deduplicate across sessions)
unique_units = {}
for u in units:
    basename = os.path.basename(u)
    if basename not in unique_units:
        unique_units[basename] = u

print(f'\nUnique units (deduplicated): {len(unique_units)}')
print('\nUnit list:')
for unit in sorted(unique_units.keys()):
    print(f'  - {unit}')
