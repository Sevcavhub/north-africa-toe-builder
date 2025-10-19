#!/usr/bin/env python3
"""Research British equipment items needing manual review"""

import sqlite3
import json

def research_items():
    """Research the 9 British items needing review"""

    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    items_to_research = [
        ("Lysander", "aircraft"),
        ("Lysander Mk I", "aircraft"),
        ("Lysander Mk III", "aircraft"),
        ("Westland Lysander", "aircraft"),
        ("Hurricane Recon", "aircraft"),
        ("Bristol Blenheim (recce)", "aircraft"),
        ("Reconnaissance", "aircraft"),
        ("Maryland", "aircraft"),
        ("7.2-inch Howitzer", "gun")
    ]

    print("=" * 80)
    print("BRITISH EQUIPMENT RESEARCH")
    print("=" * 80)
    print()

    for item_name, item_type in items_to_research:
        print(f"\n{'=' * 80}")
        print(f"ITEM: {item_name} (Type: {item_type})")
        print('=' * 80)

        if item_type == "aircraft":
            # Search aircraft database
            search_term = item_name.lower()

            # Try exact match first
            cursor.execute("""
                SELECT aircraft_id, witw_id, name, nation, max_speed, max_altitude, year, crew, range
                FROM aircraft
                WHERE LOWER(name) LIKE ?
            """, (f"%{search_term}%",))

            results = cursor.fetchall()

            if results:
                print(f"\nFound {len(results)} aircraft matches:")
                for row in results:
                    aircraft_id, witw_id, name, nation, max_speed, max_altitude, year, crew, range_miles = row
                    print(f"\n  WITW ID: {witw_id}")
                    print(f"  Name: {name}")
                    print(f"  Nation: {nation}")
                    print(f"  Speed: {max_speed} mph")
                    print(f"  Altitude: {max_altitude} ft")
                    print(f"  Year: {year}")
                    print(f"  Crew: {crew}")
                    print(f"  Range: {range_miles} miles")
            else:
                print(f"\n  [X] No aircraft found in database")
                print(f"  Status: NEEDS WEB RESEARCH")

        elif item_type == "gun":
            # For 7.2-inch Howitzer, convert to mm (183mm)
            caliber_mm = int(7.2 * 25.4)  # 183mm

            print(f"\n  Caliber: {caliber_mm}mm (7.2 inches)")

            # Search by caliber
            cursor.execute("""
                SELECT gun_id, name, caliber_mm, penetration_100m, penetration_500m
                FROM guns
                WHERE caliber_mm BETWEEN ? AND ?
            """, (caliber_mm - 2, caliber_mm + 2))

            results = cursor.fetchall()

            if results:
                print(f"\n  Found {len(results)} gun matches by caliber:")
                for row in results:
                    gun_id, name, caliber, pen_100, pen_500 = row
                    print(f"\n    Gun ID: {gun_id}")
                    print(f"    Name: {name}")
                    print(f"    Caliber: {caliber}mm")
                    print(f"    Penetration: {pen_100}mm @ 100m, {pen_500}mm @ 500m")
            else:
                print(f"\n  [X] No guns found with {caliber_mm}mm caliber")
                print(f"  Status: NEEDS WEB RESEARCH")

    conn.close()

    print("\n" + "=" * 80)
    print("RESEARCH COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    research_items()
