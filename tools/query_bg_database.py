#!/usr/bin/env python3
"""Query BattleGroup database for existing vehicles and guns."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "master_database.db"

def main():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    # Get vehicle count
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
    v_count = cursor.fetchone()[0]

    # Get gun count
    cursor.execute("SELECT COUNT(*) FROM bg_reference_guns")
    g_count = cursor.fetchone()[0]

    # Get vehicles by nation
    cursor.execute("""
        SELECT nation, COUNT(*)
        FROM bg_reference_vehicles
        GROUP BY nation
        ORDER BY COUNT(*) DESC
    """)
    nations = cursor.fetchall()

    print(f"Database Statistics:")
    print(f"  Vehicles: {v_count}")
    print(f"  Guns: {g_count}")
    print(f"\nVehicles by Nation:")
    for nation, count in nations:
        print(f"  {nation}: {count}")

    # Get all vehicle names and nations for duplicate checking
    cursor.execute("SELECT name, nation FROM bg_reference_vehicles ORDER BY nation, name")
    vehicles = cursor.fetchall()

    print(f"\n=== ALL VEHICLES ({len(vehicles)}) ===")
    for name, nation in vehicles:
        print(f"{name}|{nation}")

    # Get all gun names and nations
    cursor.execute("SELECT name, nation FROM bg_reference_guns ORDER BY nation, name")
    guns = cursor.fetchall()

    print(f"\n=== ALL GUNS ({len(guns)}) ===")
    for name, nation in guns:
        print(f"{name}|{nation}")

    db.close()

if __name__ == "__main__":
    main()
