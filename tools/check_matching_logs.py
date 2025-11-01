#!/usr/bin/env python3
import json
import glob

files = glob.glob('data/equipment_matching_logs/*automated_matching*.json')
print('Matching log statistics:\n')

total_approved = 0
for f in sorted(files):
    data = json.load(open(f))
    stats = data.get('statistics', {})
    nation = data.get('nation', 'unknown')
    print(f'{nation:10s}: {stats.get("approved", 0):3d} approved / {stats.get("total_items", 0):3d} total')
    total_approved += stats.get('approved', 0)

print(f'\nTotal approved matches across all nations: {total_approved}')
