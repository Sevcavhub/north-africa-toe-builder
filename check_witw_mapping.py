import sqlite3
import json

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

print('=== SAMPLE WITW NAMES IN DATABASE ===')
cursor.execute("""
SELECT canonical_id, name, nation, witw_id, witw_name
FROM equipment
WHERE witw_name IS NOT NULL AND witw_name != '' AND witw_name != 'NOT_IN_DATABASE'
ORDER BY nation, name
LIMIT 20
""")

print('Canonical ID         | Name                | Nation   | WITW ID | WITW Name')
print('-' * 110)
for row in cursor.fetchall():
    canonical_id, name, nation, witw_id, witw_name = row
    print(f'{canonical_id[:20]:20s} | {name[:20]:20s} | {nation:8s} | {str(witw_id):7s} | {witw_name}')

print()
print('=== CHECK WHAT PHASE 6 ACTUALLY USES ===')

# Read a sample Phase 6 JSON
phase6_file = 'data/output/units/american_1942q4_1st_armored_division_toe.json'
try:
    with open(phase6_file, 'r') as f:
        phase6_data = json.load(f)

    print(f'Sample from: {phase6_file}')
    print()
    print('Phase 6 uses these WITW identifiers:')

    # Extract M4 Sherman example
    if 'tanks' in phase6_data:
        tanks = phase6_data['tanks']
        if 'medium_tanks' in tanks and 'variants' in tanks['medium_tanks']:
            for variant_name, variant_data in tanks['medium_tanks']['variants'].items():
                witw_id = variant_data.get('witw_id', 'MISSING')
                count = variant_data.get('count', 0)
                print(f'  {variant_name:30s} -> witw_id: "{witw_id}" (count: {count})')

    print()
    print('Now checking if these WITW IDs exist in equipment table...')
    print()

    # Check each WITW ID
    if 'tanks' in phase6_data:
        tanks = phase6_data['tanks']
        for tank_type in ['medium_tanks', 'light_tanks', 'heavy_tanks']:
            if tank_type in tanks and 'variants' in tanks[tank_type]:
                for variant_name, variant_data in tanks[tank_type]['variants'].items():
                    witw_id = variant_data.get('witw_id', '')
                    if witw_id:
                        # Try exact match on witw_id (integer)
                        cursor.execute("SELECT canonical_id, name FROM equipment WHERE witw_id = ?", (witw_id,))
                        row = cursor.fetchone()
                        if row:
                            print(f'  [OK] "{witw_id}" found -> {row[0]} ({row[1]})')
                        else:
                            # Try witw_name string match
                            cursor.execute("SELECT canonical_id, name FROM equipment WHERE witw_name = ?", (witw_id,))
                            row = cursor.fetchone()
                            if row:
                                print(f'  [OK] "{witw_id}" found via witw_name -> {row[0]} ({row[1]})')
                            else:
                                # Try name fuzzy match
                                search_name = variant_name.replace('_', ' ').lower()
                                cursor.execute("SELECT canonical_id, name FROM equipment WHERE LOWER(name) LIKE ?", (f'%{search_name}%',))
                                row = cursor.fetchone()
                                if row:
                                    print(f'  [~]  "{witw_id}" NOT in database, but name match: {row[0]} ({row[1]})')
                                else:
                                    print(f'  [X]  "{witw_id}" NOT FOUND (variant: {variant_name})')

except FileNotFoundError:
    print(f'Could not find {phase6_file}')
except Exception as e:
    print(f'Error: {e}')

conn.close()
