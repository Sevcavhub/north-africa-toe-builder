import sqlite3

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

# Get IDs to delete
cursor.execute("SELECT id FROM bg_reference_guns WHERE nation LIKE '%canadian%' OR nation LIKE '%german%'")
gun_ids = [row[0] for row in cursor.fetchall()]

print(f"Found {len(gun_ids)} guns to delete: IDs {min(gun_ids)}-{max(gun_ids)}")

# Delete variants first (foreign key constraint)
if gun_ids:
    placeholders = ','.join(['?'] * len(gun_ids))
    cursor.execute(f"DELETE FROM gun_name_variants WHERE gun_id IN ({placeholders})", gun_ids)
    variants_deleted = cursor.rowcount
    print(f"Deleted {variants_deleted} variants from gun_name_variants")

# Delete guns
cursor.execute("DELETE FROM bg_reference_guns WHERE nation LIKE '%canadian%' OR nation LIKE '%german%'")
guns_deleted = cursor.rowcount
print(f"Deleted {guns_deleted} guns from bg_reference_guns")

conn.commit()
conn.close()

print("\nReady to re-scrape from Crucible text file")
