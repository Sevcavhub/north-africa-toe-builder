#!/usr/bin/env python3
"""
Import soft-skinned vehicles from BattleGroup datacards
Using existing schema without modifications
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")

# Soft-skinned vehicle data transcribed from images
BRITISH_SOFT_SKINNED = [
    {"name": "Motorcycle", "off_road": 6, "road": 24, "hits": 1, "transport": 1, "special": None},
    {"name": "Jeep", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": None},
    {"name": "Bedford MWD", "off_road": 6, "road": 24, "hits": 2, "transport": 8, "special": None},
    {"name": "Bedford OXD", "off_road": 6, "road": 24, "hits": 3, "transport": 12, "special": None},
    {"name": "Bedford OYD", "off_road": 6, "road": 24, "hits": 3, "transport": 14, "special": None},
    {"name": "Bedford QLT/QLD", "off_road": 6, "road": 24, "hits": 3, "transport": 22, "special": None},
    {"name": "Leyland Hippo", "off_road": 6, "road": 24, "hits": 4, "transport": 32, "special": None},
    {"name": "AEC Matador", "off_road": 6, "road": 24, "hits": 4, "transport": "1 gun", "special": None},
    {"name": "Morris Quad", "off_road": 8, "road": 24, "hits": 3, "transport": "1 gun", "special": None},
    {"name": "Scammel Pioneer", "off_road": 6, "road": 24, "hits": 4, "transport": "1 vehicle", "special": "recovery"},
    {"name": "M1 Wrecker", "off_road": 6, "road": 24, "hits": 4, "transport": "1 vehicle", "special": "recovery"},
    {"name": "1/4 tonne amphibian", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": "amphibious"},
    {"name": "Austin K2 ambulance", "off_road": 6, "road": 24, "hits": 2, "transport": "-", "special": "medic"},
    {"name": "DUKW", "off_road": 6, "road": 24, "hits": 3, "transport": 25, "special": "amphibious"},
]

GERMAN_SOFT_SKINNED = [
    {"name": "Motorcycle", "off_road": 6, "road": 24, "hits": 1, "transport": 1, "special": None},
    {"name": "Motorcycle and sidecar", "off_road": 6, "road": 24, "hits": 1, "transport": 2, "special": None},
    {"name": "Kettenkrad", "off_road": 14, "road": 22, "hits": 1, "transport": 2, "special": None},
    {"name": "Staff car", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": None},
    {"name": "Kubelwagen", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": None},
    {"name": "Schwimmwagen", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": "amphibious"},
    {"name": "Steyr/Horch Medium Car", "off_road": 6, "road": 24, "hits": 2, "transport": 5, "special": None},
    {"name": "Krupp Protze", "off_road": 6, "road": 24, "hits": 2, "transport": 8, "special": None},
    {"name": "Opel Blitz (medium truck)", "off_road": 6, "road": 24, "hits": 3, "transport": 12, "special": None},
    {"name": "Opel Maultier", "off_road": 12, "road": 16, "hits": 3, "transport": 12, "special": None},
    {"name": "RSO", "off_road": 9, "road": 12, "hits": 3, "transport": 10, "special": None},
    {"name": "Heavy Truck", "off_road": 6, "road": 24, "hits": 4, "transport": 24, "special": None},
    {"name": "Horse and limber", "off_road": 4, "road": 6, "hits": 2, "transport": "1 gun", "special": None},
    {"name": "Horse and wagon", "off_road": 4, "road": 6, "hits": 2, "transport": "10-20", "special": None},
    {"name": "3 tonne SdKfz 11", "off_road": 12, "road": 16, "hits": 3, "transport": 8, "special": None},
    {"name": "5 tonne SdKfz 6", "off_road": 12, "road": 16, "hits": 3, "transport": 10, "special": None},
    {"name": "8 tonne SdKfz 7", "off_road": 12, "road": 16, "hits": 4, "transport": 12, "special": None},
    {"name": "12 tonne SdKfz 8", "off_road": 12, "road": 16, "hits": 4, "transport": 15, "special": None},
    {"name": "18 tonne SdKfz 9 'Famo'", "off_road": 12, "road": 16, "hits": 5, "transport": "-", "special": "repair"},
]

SOVIET_SOFT_SKINNED = [
    {"name": "Motorcycle", "off_road": 6, "road": 24, "hits": 1, "transport": 1, "special": None},
    {"name": "Motorcycle and sidecar", "off_road": 6, "road": 24, "hits": 1, "transport": 2, "special": None},
    {"name": "Gaz 67B Jeep", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": None},
    {"name": "Staff car", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": None},
    {"name": "Civilian car", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": None},
    {"name": "Civilian medium truck", "off_road": 6, "road": 24, "hits": 2, "transport": 10, "special": None},
    {"name": "Gaz AA Truck", "off_road": 6, "road": 24, "hits": 2, "transport": 10, "special": None},
    {"name": "Zis-5V Truck", "off_road": 6, "road": 24, "hits": 3, "transport": 12, "special": None},
    {"name": "Gaz AAA Truck", "off_road": 12, "road": 16, "hits": 3, "transport": 12, "special": None},
    {"name": "Zis-42M Truck", "off_road": 12, "road": 16, "hits": 3, "transport": 15, "special": None},
    {"name": "2.5 tonne truck", "off_road": 6, "road": 24, "hits": 4, "transport": 20, "special": None},
    {"name": "Yag-10/12 heavy truck", "off_road": 6, "road": 24, "hits": 3, "transport": "-", "special": "medic"},
    {"name": "Gaz-55 ambulance", "off_road": 6, "road": 24, "hits": 2, "transport": "-", "special": "medic"},
    {"name": "Komsomollet tractor", "off_road": 12, "road": 16, "hits": 1, "transport": "1 light gun", "special": None},
    {"name": "Komintarn tractor", "off_road": 12, "road": 16, "hits": 3, "transport": "1 medium gun", "special": None},
    {"name": "Voroshilovets tractor", "off_road": 12, "road": 16, "hits": 5, "transport": "1 heavy gun", "special": None},
    {"name": "Horse drawn wagon", "off_road": 4, "road": 6, "hits": 2, "transport": "10-20", "special": None},
    {"name": "Limber", "off_road": 4, "road": 6, "hits": 2, "transport": "1 gun", "special": None},
]

AMERICAN_SOFT_SKINNED = [
    {"name": "Motorcycle", "off_road": 6, "road": 24, "hits": 1, "transport": 1, "special": None},
    {"name": "Jeep", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": None},
    {"name": "3/4 tonne truck 'Beep'", "off_road": 6, "road": 24, "hits": 2, "transport": 5, "special": None},
    {"name": "1 1/2 tonne truck", "off_road": 6, "road": 24, "hits": 3, "transport": 12, "special": None},
    {"name": "2 1/2 tonne truck", "off_road": 6, "road": 24, "hits": 2, "transport": 20, "special": None},
    {"name": "4 tonne truck", "off_road": 6, "road": 24, "hits": 3, "transport": 28, "special": None},
    {"name": "6 tonne truck", "off_road": 6, "road": 24, "hits": 4, "transport": 36, "special": None},
    {"name": "M29 Water Weasel", "off_road": 12, "road": 18, "hits": 2, "transport": 4, "special": "amphibious"},
    {"name": "M4 High Speed Tractor", "off_road": 10, "road": 15, "hits": 3, "transport": "-", "special": "medium gun tow"},
    {"name": "M5 High Speed Tractor", "off_road": 10, "road": 15, "hits": 4, "transport": "-", "special": "heavy gun tow"},
    {"name": "M1 Wrecker", "off_road": 6, "road": 24, "hits": 4, "transport": 1, "special": "recovery"},
    {"name": "1/4 tonne amphibian", "off_road": 6, "road": 24, "hits": 2, "transport": 3, "special": "amphibious"},
    {"name": "Dodge ambulance", "off_road": 6, "road": 24, "hits": 2, "transport": "-", "special": "medic"},
    {"name": "DUKW", "off_road": 6, "road": 24, "hits": 3, "transport": 25, "special": "amphibious"},
]

def classify_vehicle_type(name):
    """Determine vehicle type from name"""
    name_lower = name.lower()
    if "motorcycle" in name_lower:
        return "motorcycle"
    elif "jeep" in name_lower:
        return "jeep"
    elif "truck" in name_lower or "bedford" in name_lower or "opel" in name_lower or "gaz" in name_lower or "zis" in name_lower:
        return "truck"
    elif "tractor" in name_lower:
        return "tractor"
    elif "ambulance" in name_lower:
        return "ambulance"
    elif "wrecker" in name_lower or "pioneer" in name_lower:
        return "recovery_vehicle"
    elif "horse" in name_lower or "limber" in name_lower:
        return "horse_drawn"
    elif "dukw" in name_lower or "amphibian" in name_lower or "weasel" in name_lower:
        return "amphibious_vehicle"
    elif "car" in name_lower or "kubelwagen" in name_lower or "schwimmwagen" in name_lower:
        return "car"
    elif "kettenkrad" in name_lower:
        return "halftrack_motorcycle"
    elif "rso" in name_lower:
        return "tracked_tractor"
    else:
        return "soft_skinned"

def build_special_rules(hits, transport, special):
    """Build special_rules string from soft-skinned vehicle data"""
    rules = []

    # Always include hits
    rules.append(f"Hits: {hits}")

    # Add transport capacity
    if transport and transport != "-":
        if isinstance(transport, int):
            rules.append(f"Transport: {transport}")
        else:
            rules.append(f"Transport: {transport}")

    # Add special characteristics
    if special:
        rules.append(special.capitalize())

    return "; ".join(rules)

def import_soft_skinned(conn, vehicles, nation):
    """Import soft-skinned vehicles for a nation"""
    cursor = conn.cursor()
    imported = 0
    skipped = 0

    for vehicle in vehicles:
        # Check for duplicate
        cursor.execute("""
            SELECT COUNT(*) FROM bg_reference_vehicles
            WHERE name = ? AND nation = ?
        """, (vehicle['name'], nation))

        if cursor.fetchone()[0] > 0:
            print(f"  SKIP (duplicate): {vehicle['name']}")
            skipped += 1
            continue

        # Build special_rules string
        special_rules = build_special_rules(
            vehicle['hits'],
            vehicle['transport'],
            vehicle['special']
        )

        # Determine vehicle type
        vehicle_type = classify_vehicle_type(vehicle['name'])

        # Insert vehicle
        cursor.execute("""
            INSERT INTO bg_reference_vehicles
            (name, nation, vehicle_type, off_road_inches, road_inches,
             armor_front, special_rules, source_file, extraction_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vehicle['name'],
            nation,
            vehicle_type,
            vehicle['off_road'],
            vehicle['road'],
            'Soft-Skinned',  # Mark as soft-skinned in armor field
            special_rules,
            'BattleGroup Soft-Skinned Vehicle Cards',
            'high'
        ))

        imported += 1
        print(f"  [+] {vehicle['name']} - {special_rules}")

    return imported, skipped

def main():
    print("=" * 80)
    print("Importing BattleGroup Soft-Skinned Vehicles")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)

    # Get initial count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
    initial_count = cursor.fetchone()[0]

    total_imported = 0
    total_skipped = 0

    # Import British
    print("\n1. British Soft-Skinned Vehicles...")
    imported, skipped = import_soft_skinned(conn, BRITISH_SOFT_SKINNED, 'british')
    total_imported += imported
    total_skipped += skipped

    # Import German
    print("\n2. German Soft-Skinned Vehicles...")
    imported, skipped = import_soft_skinned(conn, GERMAN_SOFT_SKINNED, 'german')
    total_imported += imported
    total_skipped += skipped

    # Import Soviet
    print("\n3. Soviet Soft-Skinned Vehicles...")
    imported, skipped = import_soft_skinned(conn, SOVIET_SOFT_SKINNED, 'soviet')
    total_imported += imported
    total_skipped += skipped

    # Import American
    print("\n4. American Soft-Skinned Vehicles...")
    imported, skipped = import_soft_skinned(conn, AMERICAN_SOFT_SKINNED, 'american')
    total_imported += imported
    total_skipped += skipped

    # Commit
    conn.commit()

    # Get final count
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
    final_count = cursor.fetchone()[0]

    # Get breakdown
    cursor.execute("""
        SELECT nation, COUNT(*)
        FROM bg_reference_vehicles
        WHERE armor_front = 'Soft-Skinned'
        GROUP BY nation
        ORDER BY nation
    """)
    nation_breakdown = cursor.fetchall()

    conn.close()

    # Summary
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"\nTotal soft-skinned vehicles imported: {total_imported}")
    print(f"Duplicates skipped: {total_skipped}")
    print(f"\nDatabase: {initial_count} -> {final_count} (+{total_imported})")

    print(f"\nSoft-skinned vehicles by nation:")
    for nation, count in nation_breakdown:
        print(f"  {nation}: {count}")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
