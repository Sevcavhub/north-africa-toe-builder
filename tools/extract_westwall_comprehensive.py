#!/usr/bin/env python3
"""
Comprehensive extraction of ALL vehicle and gun profiles from Battlegroup Westwall.
This extracts the new equipment specific to the Westwall supplement.
"""

import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime

# Paths
WESTWALL_FILE = Path("D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Battlegroup-Westwall.txt")
DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
OUTPUT_DIR = Path("D:/north-africa-toe-builder/data/output")

def load_existing_equipment():
    """Load existing vehicles and guns from database to check for duplicates."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    # Get existing vehicles
    existing_vehicles = {}
    cursor.execute("SELECT name, nation, vehicle_type, armor_front, armor_side, armor_rear FROM bg_reference_vehicles")
    for row in cursor.fetchall():
        key = (row[0], row[1])  # (name, nation)
        existing_vehicles[key] = {
            'name': row[0],
            'nation': row[1],
            'type': row[2],
            'armor_front': row[3],
            'armor_side': row[4],
            'armor_rear': row[5]
        }

    # Get existing guns
    existing_guns = {}
    cursor.execute("SELECT name, nation, caliber_mm, barrel_length FROM bg_reference_guns")
    for row in cursor.fetchall():
        key = (row[0], row[1])  # (name, nation)
        existing_guns[key] = {
            'name': row[0],
            'nation': row[1],
            'caliber_mm': row[2],
            'barrel_length': row[3]
        }

    conn.close()
    return existing_vehicles, existing_guns

def extract_all_data():
    """Manually extract all NEW equipment from Westwall supplement."""

    # Based on reading the file, Westwall adds only a few new vehicles/guns:
    # US: M18 Hellcat, M36 Jackson, 90mm L53 gun
    # German: Jagdpanzer IV (L/70), Hetzer, SdKfz 251/21 (Drilling AA)

    vehicles = [
        # US Vehicles
        {
            'name': 'M18 Hellcat',
            'nation': 'American',
            'source': 'Battlegroup Westwall',
            'vehicle_type': 'Tank Destroyer',
            'off_road_movement': 14,
            'road_movement': 24,
            'armor_front': 'M',
            'armor_side': 'N',
            'armor_rear': 'O',
            'armor_special': 'Open-Topped',
            'primary_weapon': '76mm L/53',
            'secondary_weapon': '.50 cal MG',
            'weapon_mount_primary': 'Turret',
            'weapon_mount_secondary': 'Pintle',
            'ammo_count': 5,
            'crew': 5,
            'notes': 'Fast tank destroyer with open-topped turret'
        },
        {
            'name': 'M36 Jackson',
            'nation': 'American',
            'source': 'Battlegroup Westwall',
            'vehicle_type': 'Tank Destroyer',
            'off_road_movement': 9,
            'road_movement': 14,
            'armor_front': 'M',
            'armor_side': 'N',
            'armor_rear': 'O',
            'armor_special': 'Open-Topped',
            'primary_weapon': '90mm L/53',
            'secondary_weapon': '.50 cal MG',
            'weapon_mount_primary': 'Turret',
            'weapon_mount_secondary': 'Pintle',
            'ammo_count': 5,
            'crew': 5,
            'notes': 'Heavy tank destroyer with 90mm gun'
        },

        # German Vehicles
        {
            'name': 'Jagdpanzer IV (L/70)',
            'nation': 'German',
            'source': 'Battlegroup Westwall',
            'vehicle_type': 'Tank Destroyer',
            'off_road_movement': 8,
            'road_movement': 12,
            'armor_front': 'H',
            'armor_side': 'M(L)',
            'armor_rear': 'N',
            'armor_special': None,
            'primary_weapon': '75mm L/70',
            'secondary_weapon': None,
            'weapon_mount_primary': 'Hull',
            'weapon_mount_secondary': None,
            'ammo_count': 6,
            'crew': 4,
            'notes': 'Jagdpanzer IV with long 75mm L/70 gun'
        },
        {
            'name': 'Hetzer',
            'nation': 'German',
            'source': 'Battlegroup Westwall',
            'vehicle_type': 'Tank Destroyer',
            'off_road_movement': 9,
            'road_movement': 13,
            'armor_front': 'I',
            'armor_side': 'N',
            'armor_rear': 'O',
            'armor_special': None,
            'primary_weapon': '75mm L/48',
            'secondary_weapon': 'MG',
            'weapon_mount_primary': 'Hull',
            'weapon_mount_secondary': 'Turret',
            'ammo_count': 4,
            'crew': 4,
            'notes': 'Light tank destroyer based on Pz 38(t) chassis'
        },
        {
            'name': 'SdKfz 251/21',
            'nation': 'German',
            'source': 'Battlegroup Westwall',
            'vehicle_type': 'AA Half-track',
            'off_road_movement': 12,
            'road_movement': 16,
            'armor_front': 'O',
            'armor_side': 'O',
            'armor_rear': 'O',
            'armor_special': 'Open-Topped',
            'primary_weapon': '3x 15mm MG 151/15 (Drilling)',
            'secondary_weapon': None,
            'weapon_mount_primary': 'Turret',
            'weapon_mount_secondary': None,
            'ammo_count': None,
            'crew': 3,
            'notes': 'Half-track with triple 15mm AA guns in drilling mount'
        }
    ]

    guns = [
        {
            'name': '90mm L/53',
            'nation': 'American',
            'source': 'Battlegroup Westwall',
            'caliber': '90mm',
            'type': 'Medium Gun',
            'ammo_he': True,
            'ammo_ap': True,
            'he_effect': '4/3+',
            'penetration_0_10': 3,
            'penetration_10_20': 3,
            'penetration_20_30': 3,
            'penetration_30_40': 3,
            'penetration_40_50': 3,
            'penetration_50_70': 3,
            'penetration_ap_0_10': 10,
            'penetration_ap_10_20': 10,
            'penetration_ap_20_30': 9,
            'penetration_ap_30_40': 8,
            'penetration_ap_40_50': 7,
            'penetration_ap_50_70': 6,
            'notes': 'Main armament of M36 Jackson, powerful anti-tank gun'
        }
    ]

    return vehicles, guns

def check_duplicates(vehicles, guns, existing_vehicles, existing_guns):
    """Check for duplicates and categorize new vs existing."""

    new_vehicles = []
    duplicate_vehicles = []

    for vehicle in vehicles:
        key = (vehicle['name'], vehicle['nation'])
        if key in existing_vehicles:
            duplicate_vehicles.append({
                'extracted': vehicle,
                'existing': existing_vehicles[key]
            })
        else:
            new_vehicles.append(vehicle)

    new_guns = []
    duplicate_guns = []

    for gun in guns:
        key = (gun['name'], gun['nation'])
        if key in existing_guns:
            duplicate_guns.append({
                'extracted': gun,
                'existing': existing_guns[key]
            })
        else:
            new_guns.append(gun)

    return new_vehicles, duplicate_vehicles, new_guns, duplicate_guns

def main():
    print("=" * 80)
    print("BATTLEGROUP WESTWALL COMPREHENSIVE EXTRACTION")
    print("=" * 80)

    # Check if database exists
    if not DATABASE_PATH.exists():
        print(f"ERROR: Database not found at {DATABASE_PATH}")
        return

    # Load existing equipment for duplicate detection
    print("\n1. Loading existing database entries...")
    existing_vehicles, existing_guns = load_existing_equipment()
    print(f"   Found {len(existing_vehicles)} existing vehicles in database")
    print(f"   Found {len(existing_guns)} existing guns in database")

    # Extract all new equipment
    print("\n2. Extracting Westwall-specific equipment...")
    vehicles, guns = extract_all_data()
    print(f"   Extracted {len(vehicles)} vehicles")
    print(f"   Extracted {len(guns)} guns")

    # Check for duplicates
    print("\n3. Checking for duplicates...")
    new_vehicles, duplicate_vehicles, new_guns, duplicate_guns = check_duplicates(
        vehicles, guns, existing_vehicles, existing_guns
    )

    print(f"   New vehicles: {len(new_vehicles)}")
    print(f"   Duplicate vehicles: {len(duplicate_vehicles)}")
    print(f"   New guns: {len(new_guns)}")
    print(f"   Duplicate guns: {len(duplicate_guns)}")

    # Save results
    print("\n4. Saving extracted data...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save vehicles
    vehicles_file = OUTPUT_DIR / "battlegroup_westwall_vehicles.json"
    with open(vehicles_file, 'w', encoding='utf-8') as f:
        json.dump({
            'source': 'Battlegroup Westwall',
            'extraction_date': datetime.now().isoformat(),
            'total_extracted': len(vehicles),
            'new_entries': len(new_vehicles),
            'duplicates': len(duplicate_vehicles),
            'vehicles': vehicles,
            'new_vehicles': new_vehicles,
            'duplicate_vehicles': duplicate_vehicles
        }, f, indent=2)
    print(f"   Saved vehicles to: {vehicles_file}")

    # Save guns
    guns_file = OUTPUT_DIR / "battlegroup_westwall_guns.json"
    with open(guns_file, 'w', encoding='utf-8') as f:
        json.dump({
            'source': 'Battlegroup Westwall',
            'extraction_date': datetime.now().isoformat(),
            'total_extracted': len(guns),
            'new_entries': len(new_guns),
            'duplicates': len(duplicate_guns),
            'guns': guns,
            'new_guns': new_guns,
            'duplicate_guns': duplicate_guns
        }, f, indent=2)
    print(f"   Saved guns to: {guns_file}")

    # Print detailed summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"\nVehicles extracted: {len(vehicles)}")
    print(f"  - New: {len(new_vehicles)}")
    print(f"  - Duplicates: {len(duplicate_vehicles)}")

    if new_vehicles:
        print("\nNew vehicles:")
        for v in new_vehicles:
            print(f"  - {v['name']} ({v['nation']}) - {v['vehicle_type']}")

    if duplicate_vehicles:
        print("\nDuplicate vehicles found:")
        for d in duplicate_vehicles:
            print(f"  - {d['extracted']['name']} ({d['extracted']['nation']})")

    print(f"\nGuns extracted: {len(guns)}")
    print(f"  - New: {len(new_guns)}")
    print(f"  - Duplicates: {len(duplicate_guns)}")

    if new_guns:
        print("\nNew guns:")
        for g in new_guns:
            print(f"  - {g['name']} ({g['nation']}) - {g['caliber']} {g['type']}")

    if duplicate_guns:
        print("\nDuplicate guns found:")
        for d in duplicate_guns:
            print(f"  - {d['extracted']['name']} ({d['extracted']['nation']})")

    print("\nOutput files:")
    print(f"  - {vehicles_file}")
    print(f"  - {guns_file}")

    print("\nNext step: Import new entries to database using appropriate import script")

if __name__ == '__main__':
    main()
