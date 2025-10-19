#!/usr/bin/env python3
"""Check match_reviews table schema"""

import sqlite3

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(match_reviews)")
columns = cursor.fetchall()

print("match_reviews table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
