#!/usr/bin/env python3
"""
Add "Open-Topped" special rule to vehicles that historically had open fighting compartments
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")

def main():
    print("=" * 80)
    print("Adding 'Open-Topped' Special Rule to BattleGroup Vehicles")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get current state
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE special_rules IS NOT NULL AND special_rules != ''")
    before_count = cursor.fetchone()[0]
    print(f"\nVehicles with special_rules before: {before_count}")

    updated_count = 0

    # American open-topped vehicles
    print("\n1. Updating American open-topped vehicles...")
    american_open_topped = [
        'M10 Wolverine',
        'M36 Jackson',
        'M7 Priest'
    ]

    for vehicle in american_open_topped:
        cursor.execute("""
            UPDATE bg_reference_vehicles
            SET special_rules = 'Open-Topped'
            WHERE name = ? AND nation = 'american'
        """, (vehicle,))
        count = cursor.rowcount
        updated_count += count
        if count > 0:
            print(f"   [+] {vehicle}: {count} entries")

    # British open-topped vehicles
    print("\n2. Updating British open-topped vehicles...")
    british_open_topped = [
        'M10 Wolverine',
        'M10 Achilles',
        'M7 Priest',
        'Sexton'
    ]

    for vehicle in british_open_topped:
        cursor.execute("""
            UPDATE bg_reference_vehicles
            SET special_rules = 'Open-Topped'
            WHERE name = ? AND nation = 'british'
        """, (vehicle,))
        count = cursor.rowcount
        updated_count += count
        if count > 0:
            print(f"   [+] {vehicle}: {count} entries")

    # German tank destroyers
    print("\n3. Updating German tank destroyers...")
    german_td_open_topped = [
        'Marder II',
        'Marder III H',
        'Marder III M',
        'Nashorn',
        'Panzerjager I',
        'Panzerjager 35'
    ]

    for vehicle in german_td_open_topped:
        cursor.execute("""
            UPDATE bg_reference_vehicles
            SET special_rules = 'Open-Topped'
            WHERE name = ? AND nation = 'german'
        """, (vehicle,))
        count = cursor.rowcount
        updated_count += count
        if count > 0:
            print(f"   [+] {vehicle}: {count} entries")

    # German SPGs
    print("\n4. Updating German self-propelled guns...")
    german_spg_open_topped = [
        'Wespe',
        'Hummel',
        'Grille H',
        'Grille K'
    ]

    for vehicle in german_spg_open_topped:
        cursor.execute("""
            UPDATE bg_reference_vehicles
            SET special_rules = 'Open-Topped'
            WHERE name = ? AND nation = 'german'
        """, (vehicle,))
        count = cursor.rowcount
        updated_count += count
        if count > 0:
            print(f"   [+] {vehicle}: {count} entries")

    # German halftracks (SdKfz 250 series)
    print("\n5. Updating German SdKfz 250 series halftracks...")
    cursor.execute("""
        UPDATE bg_reference_vehicles
        SET special_rules = 'Open-Topped'
        WHERE name LIKE 'SdKfz 250%' AND nation = 'german'
    """)
    count = cursor.rowcount
    updated_count += count
    print(f"   [+] SdKfz 250 series: {count} entries")

    # German halftracks (SdKfz 251 series)
    print("\n6. Updating German SdKfz 251 series halftracks...")
    cursor.execute("""
        UPDATE bg_reference_vehicles
        SET special_rules = 'Open-Topped'
        WHERE name LIKE 'SdKfz 251%' AND nation = 'german'
    """)
    count = cursor.rowcount
    updated_count += count
    print(f"   [+] SdKfz 251 series: {count} entries")

    # Captured Soviet vehicles (SU-76M used by Germans)
    print("\n7. Updating captured Soviet vehicles...")
    cursor.execute("""
        UPDATE bg_reference_vehicles
        SET special_rules = 'Open-Topped'
        WHERE name = 'SU-76M' AND nation = 'german'
    """)
    count = cursor.rowcount
    updated_count += count
    if count > 0:
        print(f"   [+] SU-76M (captured): {count} entries")

    # Soviet open-topped vehicles
    print("\n8. Updating Soviet open-topped vehicles...")
    cursor.execute("""
        UPDATE bg_reference_vehicles
        SET special_rules = 'Open-Topped'
        WHERE name = 'SU-76' AND nation = 'soviet'
    """)
    count = cursor.rowcount
    updated_count += count
    if count > 0:
        print(f"   [+] SU-76: {count} entries")

    # Commit changes
    conn.commit()

    # Get final state
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE special_rules IS NOT NULL AND special_rules != ''")
    after_count = cursor.fetchone()[0]

    # Get breakdown by nation
    cursor.execute("""
        SELECT nation, COUNT(*)
        FROM bg_reference_vehicles
        WHERE special_rules = 'Open-Topped'
        GROUP BY nation
        ORDER BY COUNT(*) DESC
    """)
    nation_breakdown = cursor.fetchall()

    conn.close()

    # Summary
    print("\n" + "=" * 80)
    print("UPDATE SUMMARY")
    print("=" * 80)
    print(f"\nTotal vehicles updated: {updated_count}")
    print(f"Vehicles with special_rules: {before_count} -> {after_count}")

    print(f"\nOpen-Topped vehicles by nation:")
    for nation, count in nation_breakdown:
        print(f"  {nation}: {count}")

    print("\n" + "=" * 80)
    print("COMPLETE - All open-topped vehicles updated")
    print("=" * 80)

if __name__ == "__main__":
    main()
