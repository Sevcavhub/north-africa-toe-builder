import sqlite3
import json

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

# Check equipment table structure and sample data
print('=== MASTER EQUIPMENT TABLE: equipment ===')
print('Primary Key: canonical_id')
print()

# Check if aliases field is populated
cursor.execute("""
SELECT canonical_id, name, nation, aliases, witw_id, witw_name
FROM equipment
WHERE aliases IS NOT NULL AND aliases != '[]' AND aliases != ''
LIMIT 10
""")

print('Sample equipment with aliases populated:')
print('ID                  | Name                | Nation   | Aliases                       | WITW ID')
print('-' * 100)
for row in cursor.fetchall():
    canonical_id, name, nation, aliases, witw_id, witw_name = row
    try:
        aliases_list = json.loads(aliases) if aliases else []
        aliases_str = ', '.join(aliases_list[:3])
        if len(aliases_list) > 3:
            aliases_str += f' (+{len(aliases_list)-3} more)'
    except:
        aliases_str = str(aliases)[:30]
    witw_str = str(witw_id) if witw_id else 'None'
    print(f'{canonical_id[:20]:20s} | {name[:20]:20s} | {nation:8s} | {aliases_str[:30]:30s} | {witw_str}')

print()
print('=== ALIAS COVERAGE STATS ===')

# Check how many have aliases
cursor.execute("""
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN aliases IS NOT NULL AND aliases != '[]' AND aliases != '' THEN 1 ELSE 0 END) as with_aliases,
    SUM(CASE WHEN witw_id IS NOT NULL THEN 1 ELSE 0 END) as with_witw
FROM equipment
""")

total, with_aliases, with_witw = cursor.fetchone()
print(f'Total equipment items: {total}')
print(f'Items with aliases: {with_aliases} ({with_aliases/total*100:.1f}%)')
print(f'Items with WITW mapping: {with_witw} ({with_witw/total*100:.1f}%)')

print()
print('=== CHECK PHASE 6 WITW IDS ===')

# Check some common Phase 6 WITW IDs
phase6_ids = ['M4_SHERMAN', 'M3_LEE', 'M3_GRANT', 'M3_STUART', 'M5_STUART',
              'PANZER_III', 'PANZER_IV', 'TIGER_I', 'VALENTINE_II', 'CRUSADER_III']

print('Checking if common Phase 6 WITW IDs are in database:')
for witw_id in phase6_ids:
    cursor.execute("SELECT canonical_id, name, witw_name FROM equipment WHERE witw_name = ?", (witw_id,))
    row = cursor.fetchone()
    if row:
        print(f'  [OK] {witw_id:20s} -> {row[0]} ({row[1]})')
    else:
        # Try case-insensitive
        cursor.execute("SELECT canonical_id, name, witw_name FROM equipment WHERE LOWER(witw_name) = LOWER(?)", (witw_id,))
        row = cursor.fetchone()
        if row:
            print(f'  [~]  {witw_id:20s} -> {row[0]} ({row[1]}) [case mismatch]')
        else:
            print(f'  [X]  {witw_id:20s} NOT FOUND')

conn.close()
