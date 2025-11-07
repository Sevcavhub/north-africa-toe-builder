import sqlite3

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

cursor.execute('SELECT id, name, nation, caliber_mm, he_dice, he_target, source_file FROM bg_reference_guns ORDER BY id')

print('ID  | Name                           | Nation     | Cal | HE | Target | Source')
print('-' * 120)
for row in cursor.fetchall():
    gun_id, name, nation, caliber, he_dice, he_target, source_file = row
    print(f'{gun_id:3d} | {name:30s} | {nation or "None":10s} | {str(caliber) or "None":3s} | {str(he_dice) or "None":2s} | {he_target or "None":6s} | {(source_file or "None")[:35]}')

conn.close()
