import sqlite3

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

# Check match_reviews table schema
print('=== MATCH_REVIEWS TABLE SCHEMA ===')
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='match_reviews'")
schema = cursor.fetchone()
if schema:
    print(schema[0])
else:
    print('ERROR: match_reviews table not found!')
    exit(1)

print()
print('=== SAMPLE MATCH_REVIEWS ENTRIES ===')
cursor.execute("""
SELECT canonical_id, witw_name, witw_id, onwar_name, wwiitanks_name, review_status, final_confidence
FROM match_reviews
LIMIT 20
""")

print('Canonical ID        | WITW Name           | WITW ID | OnWar Name         | WWIITanks Name     | Status    | Conf')
print('-' * 140)
for row in cursor.fetchall():
    canonical_id, witw_name, witw_id, onwar_name, wwiitanks_name, status, confidence = row
    print(f'{str(canonical_id)[:20]:20s} | {str(witw_name)[:20]:20s} | {str(witw_id):7s} | {str(onwar_name)[:18]:18s} | {str(wwiitanks_name)[:18]:18s} | {str(status):9s} | {str(confidence):4s}')

print()
print('=== CHECK IF PHASE 6 WITW IDS ARE IN MATCH_REVIEWS ===')

# Check some Phase 6 WITW names
phase6_names = ['M4 Sherman', 'M3 Lee', 'M3 Grant', 'M3 Stuart', 'M5 Stuart',
                'Panzer III', 'Panzer IV', 'Tiger I', 'Valentine II', 'Crusader III']

print('Checking if Phase 6 equipment names are in match_reviews:')
for name in phase6_names:
    cursor.execute("""
    SELECT canonical_id, witw_name, witw_id
    FROM match_reviews
    WHERE witw_name LIKE ?
    """, (f'%{name}%',))

    rows = cursor.fetchall()
    if rows:
        print(f'  [OK] "{name}" found: {len(rows)} matches')
        for row in rows[:3]:  # Show first 3
            print(f'       -> {row[0]} (WITW: {row[1]}, ID: {row[2]})')
    else:
        print(f'  [X]  "{name}" NOT FOUND in match_reviews')

print()
print('=== STATISTICS ===')
cursor.execute("SELECT COUNT(*) FROM match_reviews")
total = cursor.fetchone()[0]
print(f'Total match_reviews entries: {total}')

cursor.execute("SELECT COUNT(DISTINCT canonical_id) FROM match_reviews")
unique_canonical = cursor.fetchone()[0]
print(f'Unique canonical IDs: {unique_canonical}')

cursor.execute("SELECT COUNT(*) FROM match_reviews WHERE wwiitanks_name IS NOT NULL")
afv_matches = cursor.fetchone()[0]
print(f'Matched to wwiitanks: {afv_matches}')

cursor.execute("SELECT COUNT(*) FROM match_reviews WHERE onwar_name IS NOT NULL")
onwar_matches = cursor.fetchone()[0]
print(f'Matched to onwar: {onwar_matches}')

cursor.execute("SELECT COUNT(*) FROM match_reviews WHERE review_status = 'approved'")
approved = cursor.fetchone()[0]
print(f'Review status approved: {approved}')

conn.close()
