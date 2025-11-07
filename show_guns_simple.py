import sqlite3

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

print("\nCANADIAN GUNS:")
print("-"*80)
cursor.execute('SELECT id, name, caliber_mm FROM bg_reference_guns WHERE nation="canadian" ORDER BY id')
for row in cursor.fetchall():
    cal = str(row[2]) if row[2] else "?"
    print(f"ID {row[0]:3d}: {row[1]:30s} {cal:>4s}mm")

print("\n\nGERMAN GUNS:")
print("-"*80)
cursor.execute('SELECT id, name, caliber_mm FROM bg_reference_guns WHERE nation="german" ORDER BY id')
for row in cursor.fetchall():
    cal = str(row[2]) if row[2] else "?"
    print(f"ID {row[0]:3d}: {row[1]:30s} {cal:>4s}mm")

print("\n\nBRITISH GUNS:")
print("-"*80)
cursor.execute('SELECT id, name, caliber_mm FROM bg_reference_guns WHERE nation="british" ORDER BY id')
for row in cursor.fetchall():
    cal = str(row[2]) if row[2] else "?"
    print(f"ID {row[0]:3d}: {row[1]:30s} {cal:>4s}mm")

conn.close()
