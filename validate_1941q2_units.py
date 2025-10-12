import os
import glob
import json
from datetime import datetime

# Load schema
with open('schemas/unified_toe_schema.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Find all 1941-Q2 unit files
unit_files = glob.glob('data/output/*/units/*1941*q2*.json') + glob.glob('data/output/*/units/*1941*Q2*.json')

# Deduplicate by filename, keeping most recent
units_by_name = {}
for filepath in unit_files:
    basename = os.path.basename(filepath)
    # Normalize name (handle both q2 and Q2)
    normalized_name = basename.replace('1941-q2', '1941q2').replace('1941-Q2', '1941q2')

    # Get modification time
    mtime = os.path.getmtime(filepath)

    if normalized_name not in units_by_name or mtime > units_by_name[normalized_name]['mtime']:
        units_by_name[normalized_name] = {
            'path': filepath,
            'original_name': basename,
            'mtime': mtime
        }

print(f"Found {len(units_by_name)} unique 1941-Q2 units\n")

# Validate each unit
results = []
for normalized_name, info in sorted(units_by_name.items()):
    filepath = info['path']
    basename = info['original_name']

    print(f"Validating: {basename}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            unit_data = json.load(f)

        # Basic validation checks
        checks = {
            'valid_json': True,
            'has_nation': 'nation' in unit_data,
            'has_quarter': 'quarter' in unit_data,
            'has_designation': 'unit_designation' in unit_data,
            'has_personnel': 'total_personnel' in unit_data,
            'has_equipment': any(key in unit_data for key in ['tanks', 'artillery_total', 'ground_vehicles_total']),
            'has_validation': 'validation' in unit_data,
            'file_size': os.path.getsize(filepath)
        }

        # Get metadata
        nation = unit_data.get('nation', 'unknown')
        designation = unit_data.get('unit_designation', 'unknown')
        unit_type = unit_data.get('unit_type', 'unknown')
        quarter = unit_data.get('quarter', 'unknown')

        # Check confidence score
        validation = unit_data.get('validation', {})
        confidence = validation.get('confidence', 0)

        result = {
            'file': basename,
            'path': filepath,
            'nation': nation,
            'quarter': quarter,
            'designation': designation,
            'type': unit_type,
            'confidence': confidence,
            'size_kb': round(checks['file_size'] / 1024, 1),
            'checks': checks,
            'status': 'VALID' if all([checks['has_nation'], checks['has_quarter'], checks['has_designation'], checks['has_personnel'], checks['has_equipment']]) else 'ISSUES'
        }

        results.append(result)
        print(f"  [OK] {nation.upper()} - {designation} ({confidence}% confidence, {result['size_kb']}KB)")

    except json.JSONDecodeError as e:
        result = {
            'file': basename,
            'path': filepath,
            'status': 'INVALID_JSON',
            'error': str(e)
        }
        results.append(result)
        print(f"  [ERROR] JSON ERROR: {e}")
    except Exception as e:
        result = {
            'file': basename,
            'path': filepath,
            'status': 'ERROR',
            'error': str(e)
        }
        results.append(result)
        print(f"  [ERROR] {e}")

# Generate summary
print(f"\n{'='*80}")
print("VALIDATION SUMMARY")
print(f"{'='*80}\n")

valid_units = [r for r in results if r.get('status') == 'VALID']
issue_units = [r for r in results if r.get('status') != 'VALID']

print(f"Total units: {len(results)}")
print(f"Valid units: {len(valid_units)}")
print(f"Units with issues: {len(issue_units)}")

if valid_units:
    print(f"\nBy nation:")
    nations = {}
    for r in valid_units:
        nation = r['nation']
        nations[nation] = nations.get(nation, 0) + 1
    for nation, count in sorted(nations.items()):
        print(f"  {nation}: {count} units")

    print(f"\nConfidence scores:")
    confidences = [r['confidence'] for r in valid_units if 'confidence' in r]
    if confidences:
        print(f"  Average: {sum(confidences) / len(confidences):.1f}%")
        print(f"  Range: {min(confidences)}% - {max(confidences)}%")
        print(f"  Below 80%: {len([c for c in confidences if c < 80])}")

# Save results
output_file = 'data/output/1941-Q2_VALIDATION_RESULTS.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'total_units': len(results),
        'valid_units': len(valid_units),
        'issue_units': len(issue_units),
        'units': results
    }, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Results saved to: {output_file}")
