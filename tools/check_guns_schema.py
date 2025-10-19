#!/usr/bin/env python3
"""Check guns table schema"""

import sqlite3

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(guns)")
columns = cursor.fetchall()

print("Guns table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check for 7.2-inch (183mm) guns
cursor.execute("""
    SELECT gun_id, name, caliber_mm
    FROM guns
    WHERE caliber_mm BETWEEN 180 AND 185
""")

results = cursor.fetchall()
print(f"\nGuns with caliber 180-185mm:")
for row in results:
    print(f"  ID: {row[0]}, Name: {row[1]}, Caliber: {row[2]}mm")

conn.close()
