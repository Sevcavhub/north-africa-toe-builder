import json
import glob
import os

# Find all 1941-Q2 unit files
unit_files = glob.glob('data/output/*/units/*1941*q2*.json') + glob.glob('data/output/*/units/*1941*Q2*.json')

# Deduplicate by filename, keeping most recent
units_by_name = {}
for filepath in unit_files:
    basename = os.path.basename(filepath)
    normalized_name = basename.replace('1941-q2', '1941q2').replace('1941-Q2', '1941q2')
    mtime = os.path.getmtime(filepath)
    if normalized_name not in units_by_name or mtime > units_by_name[normalized_name]['mtime']:
        units_by_name[normalized_name] = {'path': filepath, 'mtime': mtime}

print(f"Scanning {len(units_by_name)} unique 1941-Q2 units for aircraft data...\n")

aircraft_found = []
units_with_aircraft = []
units_without_aircraft = []

for normalized_name, info in sorted(units_by_name.items()):
    filepath = info['path']

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            unit_data = json.load(f)

        unit_designation = unit_data.get('unit_designation', 'Unknown')
        nation = unit_data.get('nation', 'unknown')

        # Check for aircraft data
        aircraft_total = unit_data.get('aircraft_total', 0)

        # Check for aircraft equipment sections
        has_aircraft_sections = False
        aircraft_types = []

        if 'fighters' in unit_data:
            has_aircraft_sections = True
            if unit_data['fighters'].get('total', 0) > 0:
                for variant, details in unit_data['fighters'].get('variants', {}).items():
                    aircraft_types.append({
                        'type': variant,
                        'count': details.get('count', 0),
                        'role': 'fighter',
                        'witw_id': details.get('witw_id', None)
                    })

        if 'bombers' in unit_data:
            has_aircraft_sections = True
            if unit_data['bombers'].get('total', 0) > 0:
                for variant, details in unit_data['bombers'].get('variants', {}).items():
                    aircraft_types.append({
                        'type': variant,
                        'count': details.get('count', 0),
                        'role': 'bomber',
                        'witw_id': details.get('witw_id', None)
                    })

        if 'reconnaissance_aircraft' in unit_data:
            has_aircraft_sections = True
            if unit_data['reconnaissance_aircraft'].get('total', 0) > 0:
                for variant, details in unit_data['reconnaissance_aircraft'].get('variants', {}).items():
                    aircraft_types.append({
                        'type': variant,
                        'count': details.get('count', 0),
                        'role': 'reconnaissance',
                        'witw_id': details.get('witw_id', None)
                    })

        if 'transport_aircraft' in unit_data:
            has_aircraft_sections = True
            if unit_data['transport_aircraft'].get('total', 0) > 0:
                for variant, details in unit_data['transport_aircraft'].get('variants', {}).items():
                    aircraft_types.append({
                        'type': variant,
                        'count': details.get('count', 0),
                        'role': 'transport',
                        'witw_id': details.get('witw_id', None)
                    })

        if aircraft_total > 0 or has_aircraft_sections or aircraft_types:
            units_with_aircraft.append({
                'unit': unit_designation,
                'nation': nation,
                'file': os.path.basename(filepath),
                'aircraft_total': aircraft_total,
                'aircraft_types': aircraft_types
            })
            print(f"[AIRCRAFT] {nation.upper()} - {unit_designation}: {aircraft_total} total")
            for aircraft in aircraft_types:
                print(f"  - {aircraft['count']}x {aircraft['type']} ({aircraft['role']}) WITW: {aircraft['witw_id']}")
                aircraft_found.append({
                    'aircraft_type': aircraft['type'],
                    'nation': nation,
                    'unit': unit_designation,
                    'count': aircraft['count'],
                    'role': aircraft['role'],
                    'witw_id': aircraft['witw_id']
                })
        else:
            units_without_aircraft.append({
                'unit': unit_designation,
                'nation': nation,
                'file': os.path.basename(filepath)
            })

    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")

print(f"\n{'='*80}")
print("AIRCRAFT EXTRACTION SUMMARY")
print(f"{'='*80}\n")

print(f"Units with aircraft: {len(units_with_aircraft)}")
print(f"Units without aircraft: {len(units_without_aircraft)}")
print(f"Total aircraft types found: {len(aircraft_found)}")

if aircraft_found:
    print(f"\nAircraft inventory:")
    # Group by nation
    by_nation = {}
    for ac in aircraft_found:
        nation = ac['nation']
        if nation not in by_nation:
            by_nation[nation] = []
        by_nation[nation].append(ac)

    for nation, aircraft_list in sorted(by_nation.items()):
        print(f"\n  {nation.upper()}:")
        for ac in aircraft_list:
            print(f"    {ac['count']}x {ac['aircraft_type']} ({ac['role']}) - {ac['unit']}")

# Save results
output_data = {
    'quarter': '1941-Q2',
    'units_scanned': len(units_by_name),
    'units_with_aircraft': len(units_with_aircraft),
    'units_without_aircraft': len(units_without_aircraft),
    'aircraft_found': aircraft_found,
    'units_with_aircraft_detail': units_with_aircraft,
    'note': 'Most ground units have aircraft_total: 0 - aircraft were separate air force units, not organic to divisions'
}

output_file = 'data/output/1941-Q2_AIRCRAFT_EXTRACTION.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Results saved to: {output_file}")
