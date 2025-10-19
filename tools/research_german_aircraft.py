#!/usr/bin/env python3
"""Research German aircraft in database"""

import sqlite3

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

aircraft_to_search = [
    "Bf 109f-4/trop",
    "Bf 109g-2/trop",
    "He 111H-6",
    "Ju 87d-3/trop"
]

print("Searching for German aircraft in database...\n")

for aircraft_name in aircraft_to_search:
    search_term = aircraft_name.lower()

    # Try various search patterns
    patterns = [
        f"%{search_term}%",
        f"%109f%4%",
        f"%109g%2%",
        f"%he 111%h%6%",
        f"%111h%6%",
        f"%ju 87%d%3%",
        f"%87d%3%"
    ]

    found = False
    for pattern in patterns:
        cursor.execute("""
            SELECT aircraft_id, witw_id, name, nation, max_speed, range, year
            FROM aircraft
            WHERE LOWER(name) LIKE ?
        """, (pattern,))

        results = cursor.fetchall()

        if results:
            print(f"\n{aircraft_name}:")
            for row in results:
                aircraft_id, witw_id, name, nation, max_speed, range_val, year = row
                print(f"  WITW ID: {witw_id}")
                print(f"  Name: {name}")
                print(f"  Nation: {nation}")
                print(f"  Speed: {max_speed} mph")
                print(f"  Range: {range_val} miles")
                print(f"  Year: {year}")
            found = True
            break

    if not found:
        print(f"\n{aircraft_name}: NOT FOUND")

conn.close()
