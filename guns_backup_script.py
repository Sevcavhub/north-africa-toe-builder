import sqlite3
import json

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

# Backup all Canadian and German guns
cursor.execute("SELECT * FROM bg_reference_guns WHERE nation LIKE '%canadian%' OR nation LIKE '%german%'")
rows = cursor.fetchall()

# Get column names
cursor.execute("PRAGMA table_info(bg_reference_guns)")
columns = [col[1] for col in cursor.fetchall()]

backup = []
for row in rows:
    gun_dict = dict(zip(columns, row))
    backup.append(gun_dict)

with open('D:/north-africa-toe-builder/guns_backup_before_rescrape.json', 'w') as f:
    json.dump(backup, f, indent=2)

print(f"Backed up {len(backup)} guns to guns_backup_before_rescrape.json")
print(f"Canadian guns: {len([g for g in backup if 'canadian' in g['nation']])}")
print(f"German guns: {len([g for g in backup if 'german' in g['nation']])}")

conn.close()
