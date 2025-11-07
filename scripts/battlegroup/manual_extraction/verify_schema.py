import sqlite3

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(bg_reference_guns)')
columns = cursor.fetchall()

print(f'[+] bg_reference_guns has {len(columns)} columns')
print('\nLast 10 columns:')
for col in columns[-10:]:
    print(f'  {col[1]:25s} {col[2]}')

conn.close()
