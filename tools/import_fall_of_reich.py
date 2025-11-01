#!/usr/bin/env python3
"""
Import Fall of the Reich vehicles and guns with duplicate detection
"""

import json
import sqlite3
from pathlib import Path

# Paths
DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
VEHICLES_JSON = Path("D:/north-africa-toe-builder/data/output/battlegroup_fall_of_reich_vehicles.json")
GUNS_JSON = Path("D:/north-africa-toe-builder/data/output/battlegroup_fall_of_reich_guns.json")

def normalize_name(name):
    """Normalize name for comparison"""
    return name.lower().strip()

def check_duplicates(conn):
    """Get existing vehicles and guns for duplicate detection"""
    cursor = conn.cursor()

    # Get existing vehicles
    cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
    existing_vehicles = set((normalize_name(row[0]), row[1].lower()) for row in cursor.fetchall())

    # Get existing guns
    cursor.execute("SELECT name, nation FROM bg_reference_guns")
    existing_guns = set((normalize_name(row[0]), row[1].lower() if row[1] else 'unknown') for row in cursor.fetchall())

    return existing_vehicles, existing_guns

def import_vehicles(conn, vehicles_data, existing_vehicles):
    """Import vehicles with duplicate detection"""
    cursor = conn.cursor()
    imported = 0
    duplicates = 0

    for vehicle in vehicles_data:
        name_norm = normalize_name(vehicle['name'])
        nation = vehicle['nation'].lower()

        # Check for duplicate
        if (name_norm, nation) in existing_vehicles:
            duplicates += 1
            print(f"  SKIP (duplicate): {vehicle['name']} ({nation})")
            continue

        # Import new vehicle
        cursor.execute("""
            INSERT INTO bg_reference_vehicles
            (name, nation, source_file, extraction_confidence)
            VALUES (?, ?, ?, ?)
        """, (
            vehicle['name'],
            nation,
            vehicle['source_file'],
            'medium'  # OCR extraction
        ))
        imported += 1
        print(f"  [+] IMPORTED: {vehicle['name']} ({nation})")

    return imported, duplicates

def import_guns(conn, guns_data, existing_guns):
    """Import guns with duplicate detection"""
    cursor = conn.cursor()
    imported = 0
    duplicates = 0

    for gun in guns_data:
        name_norm = normalize_name(gun['name'])
        nation = gun.get('nation', 'unknown').lower()

        # Check for duplicate
        if (name_norm, nation) in existing_guns:
            duplicates += 1
            print(f"  SKIP (duplicate): {gun['name']} ({nation})")
            continue

        # Skip guns with unknown nation (can't determine from OCR)
        if nation == 'unknown' or not nation:
            print(f"  SKIP (unknown nation): {gun['name']} ({gun.get('caliber_mm')}mm)")
            continue

        # Import new gun
        cursor.execute("""
            INSERT INTO bg_reference_guns
            (name, nation, caliber_mm, source_file)
            VALUES (?, ?, ?, ?)
        """, (
            gun['name'],
            nation,
            gun.get('caliber_mm'),
            gun['source_file']
        ))
        imported += 1
        print(f"  [+] IMPORTED: {gun['name']} ({nation}, {gun.get('caliber_mm')}mm)")

    return imported, duplicates

def main():
    print("=" * 80)
    print("Fall of the Reich - Import with Duplicate Detection")
    print("=" * 80)

    # Load JSON data
    print("\n1. Loading extraction data...")
    with open(VEHICLES_JSON, 'r', encoding='utf-8') as f:
        vehicles_data = json.load(f)
    with open(GUNS_JSON, 'r', encoding='utf-8') as f:
        guns_data = json.load(f)

    print(f"   Vehicles extracted: {len(vehicles_data)}")
    print(f"   Guns extracted: {len(guns_data)}")

    # Connect to database
    print("\n2. Connecting to database...")
    conn = sqlite3.connect(DB_PATH)

    # Get existing data
    print("\n3. Checking for duplicates...")
    existing_vehicles, existing_guns = check_duplicates(conn)
    print(f"   Existing vehicles: {len(existing_vehicles)}")
    print(f"   Existing guns: {len(existing_guns)}")

    # Import vehicles
    print("\n4. Importing vehicles...")
    v_imported, v_duplicates = import_vehicles(conn, vehicles_data, existing_vehicles)

    # Import guns
    print("\n5. Importing guns...")
    g_imported, g_duplicates = import_guns(conn, guns_data, existing_guns)

    # Commit changes
    conn.commit()

    # Get final counts
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
    final_vehicles = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bg_reference_guns")
    final_guns = cursor.fetchone()[0]

    conn.close()

    # Summary
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"\nVEHICLES:")
    print(f"  Extracted: {len(vehicles_data)}")
    print(f"  Duplicates: {v_duplicates}")
    print(f"  Imported: {v_imported}")
    print(f"  Database: {len(existing_vehicles)} -> {final_vehicles} (+{v_imported})")

    print(f"\nGUNS:")
    print(f"  Extracted: {len(guns_data)}")
    print(f"  Duplicates: {g_duplicates}")
    print(f"  Imported: {g_imported}")
    print(f"  Database: {len(existing_guns)} -> {final_guns} (+{g_imported})")

    print(f"\nTOTAL ENTRIES: {final_vehicles + final_guns}")
    print("=" * 80)

if __name__ == "__main__":
    main()
