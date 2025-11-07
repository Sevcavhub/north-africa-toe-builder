import sqlite3

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

# Based on gun names and Crucible file structure:
# Canadian: 20mm (autocannon), 37mmL53, 75mmL40, 105mmL22
# German: 80mm, 120mm, 20mmL55, 37mmL43 (PaK36), 50mmL60 (PaK38), 75mmL24, 88mmL56 (Flak36)

canadian_ids = [47, 48, 49, 50]  # 20mm, 37mmL53, 75mmL40, 105mmL22
german_ids = [51, 52, 53, 54, 55, 56, 57]  # 80mm, 120mm, 20mmL55, PaK36, PaK38, 75mmL24, Flak36

# Update Canadian guns
for gun_id in canadian_ids:
    cursor.execute("UPDATE bg_reference_guns SET nation = 'canadian' WHERE id = ?", (gun_id,))
print(f"Updated {len(canadian_ids)} guns to nation='canadian'")

# Update German guns
for gun_id in german_ids:
    cursor.execute("UPDATE bg_reference_guns SET nation = 'german' WHERE id = ?", (gun_id,))
print(f"Updated {len(german_ids)} guns to nation='german'")

# Also update source_document
cursor.execute("UPDATE bg_reference_guns SET source_document = 'Battlegroup-Canadas-Crucible' WHERE id >= 47 AND id <= 57")

conn.commit()
conn.close()

print("\nFixed nation assignments")
print("Canadian: IDs 47-50 (4 guns)")
print("German: IDs 51-57 (7 guns)")
