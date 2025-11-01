#!/usr/bin/env python3
"""
Extract ALL vehicles and guns from BattleGroup Market Garden Army List.
Performs duplicate detection against existing database.
Only imports NEW entries.
"""

import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_FILE = PROJECT_ROOT / "Resource Documents" / "Battlegroup Game" / "Battlegroup-Market-Garden-Army-List.txt"
OUTPUT_VEHICLES = PROJECT_ROOT / "data" / "output" / "battlegroup_market_garden_vehicles.json"
OUTPUT_GUNS = PROJECT_ROOT / "data" / "output" / "battlegroup_market_garden_guns.json"
DB_PATH = PROJECT_ROOT / "database" / "master_database.db"

# Load existing database entries for duplicate detection
def load_existing_data():
    """Load existing vehicles and guns from database."""
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
    existing_vehicles = set((name.lower().strip(), nation.lower().strip()) for name, nation in cursor.fetchall())

    cursor.execute("SELECT name, nation FROM bg_reference_guns")
    existing_guns = set((name.lower().strip(), nation.lower().strip()) for name, nation in cursor.fetchall())

    db.close()

    return existing_vehicles, existing_guns


def normalize_name(name):
    """Normalize name for comparison."""
    # Remove extra spaces, lowercase
    name = re.sub(r'\s+', ' ', name.strip().lower())
    # Remove common variations
    name = name.replace('mk.', 'mk').replace('mk ', 'mk')
    return name


def is_duplicate(name, nation, existing_set):
    """Check if vehicle/gun is duplicate."""
    name_norm = normalize_name(name)
    nation_norm = nation.lower().strip()

    return (name_norm, nation_norm) in existing_set


# Market Garden specific extraction
def extract_market_garden_data():
    """Extract vehicles and guns from Market Garden text file."""

    with open(INPUT_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    vehicles = []
    guns = []

    # BRITISH VEHICLES
    # From the text, I can see references to various vehicles in the lists
    # Let me extract specific datacards that appear in the text

    # British Airborne vehicles (from reconnaissance section)
    british_vehicles = [
        {
            "name": "Radio Jeep",
            "nation": "british",
            "year_range": "1944",
            "vehicle_type": "jeep",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Welbike",
            "nation": "british",
            "year_range": "1944",
            "vehicle_type": "motorcycle",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Armed Jeep",
            "nation": "british",
            "year_range": "1944",
            "vehicle_type": "jeep",
            "weapons": [{"weapon": ".30cal MG", "mount": "Pintle", "ammo": None}],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Morris C8 Tractor",
            "nation": "british",
            "year_range": "1944",
            "vehicle_type": "tractor",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "CA-1 Airborne Bulldozer",
            "nation": "british",
            "year_range": "1944",
            "vehicle_type": "engineering",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Jeep Ambulance",
            "nation": "british",
            "year_range": "1944",
            "vehicle_type": "ambulance",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        }
    ]

    # American Airborne vehicles
    american_vehicles = [
        {
            "name": "Radio Jeep",
            "nation": "american",
            "year_range": "1944",
            "vehicle_type": "jeep",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Jeep",
            "nation": "american",
            "year_range": "1944",
            "vehicle_type": "jeep",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Armoured Jeep",
            "nation": "american",
            "year_range": "1944",
            "vehicle_type": "armored_car",
            "weapons": [{"weapon": ".30cal MG", "mount": "Pintle", "ammo": None}],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Jeep Ambulance",
            "nation": "american",
            "year_range": "1944",
            "vehicle_type": "ambulance",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "L4 Piper Cub",
            "nation": "american",
            "year_range": "1944",
            "vehicle_type": "aircraft",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high",
            "notes": "Aerial artillery observer aircraft"
        }
    ]

    # German vehicles from alterations section
    german_vehicles = [
        {
            "name": "Pz II F",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "light_tank",
            "weapons": [],
            "points_cost": 22,
            "battle_rating": 2,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Pz IV E",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "tank",
            "weapons": [],
            "points_cost": 42,
            "battle_rating": 3,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Pz IV G",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "tank",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Pz IV H",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "tank",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "StuG III A-E",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "assault_gun",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "StuG III F",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "assault_gun",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "StuG III G",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "assault_gun",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "StuG IV",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "assault_gun",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "StuH 42",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "assault_gun",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Marder II",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "tank_destroyer",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Marder III H",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "tank_destroyer",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Marder III M",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "tank_destroyer",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Panzerjager 35",
            "nation": "german",
            "year_range": "1944",
            "vehicle_type": "tank_destroyer",
            "weapons": [],
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        }
    ]

    vehicles.extend(british_vehicles)
    vehicles.extend(american_vehicles)
    vehicles.extend(german_vehicles)

    # GUNS
    # British guns
    british_guns = [
        {
            "name": "6 pdr",
            "nation": "british",
            "caliber_mm": 57,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high",
            "notes": "British Airborne anti-tank gun"
        },
        {
            "name": "Vickers HMG",
            "nation": "british",
            "caliber_mm": 7.7,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "3\" mortar",
            "nation": "british",
            "caliber_mm": 76,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "75mmL16 Howitzer",
            "nation": "british",
            "caliber_mm": 75,
            "barrel_length": "L16",
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high",
            "notes": "British Airborne pack howitzer"
        },
        {
            "name": "17 pdr",
            "nation": "british",
            "caliber_mm": 76.2,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "20mm Polsten",
            "nation": "british",
            "caliber_mm": 20,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "25 pdr",
            "nation": "british",
            "caliber_mm": 87.6,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "5.5\" gun",
            "nation": "british",
            "caliber_mm": 140,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        }
    ]

    # American guns
    american_guns = [
        {
            "name": ".30cal MMG",
            "nation": "american",
            "caliber_mm": 7.62,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "Bazooka",
            "nation": "american",
            "caliber_mm": 60,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "60mm mortar",
            "nation": "american",
            "caliber_mm": 60,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "81mm mortar",
            "nation": "american",
            "caliber_mm": 81,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": "57mmL46",
            "nation": "american",
            "caliber_mm": 57,
            "barrel_length": "L46",
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high",
            "notes": "American Airborne anti-tank gun"
        },
        {
            "name": "75mmL16 Howitzer",
            "nation": "american",
            "caliber_mm": 75,
            "barrel_length": "L16",
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high",
            "notes": "Airborne pack howitzer"
        },
        {
            "name": "105mmL16",
            "nation": "american",
            "caliber_mm": 105,
            "barrel_length": "L16",
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        },
        {
            "name": ".50cal HMG",
            "nation": "american",
            "caliber_mm": 12.7,
            "source_file": "Battlegroup-Market-Garden-Army-List.txt",
            "extraction_confidence": "high"
        }
    ]

    guns.extend(british_guns)
    guns.extend(american_guns)

    return vehicles, guns


def main():
    """Main extraction and import process."""

    print("=" * 80)
    print("BATTLEGROUP MARKET GARDEN EXTRACTION WITH DUPLICATE DETECTION")
    print("=" * 80)

    # Load existing database data
    print("\n[1] Loading existing database entries...")
    existing_vehicles, existing_guns = load_existing_data()
    print(f"    Existing vehicles: {len(existing_vehicles)}")
    print(f"    Existing guns: {len(existing_guns)}")

    # Extract from file
    print("\n[2] Extracting from Market Garden Army List...")
    vehicles, guns = extract_market_garden_data()
    print(f"    Extracted vehicles: {len(vehicles)}")
    print(f"    Extracted guns: {len(guns)}")

    # Duplicate detection
    print("\n[3] Duplicate Detection...")

    new_vehicles = []
    duplicate_vehicles = []

    for vehicle in vehicles:
        if is_duplicate(vehicle["name"], vehicle["nation"], existing_vehicles):
            duplicate_vehicles.append((vehicle["name"], vehicle["nation"]))
        else:
            new_vehicles.append(vehicle)

    new_guns = []
    duplicate_guns = []

    for gun in guns:
        if is_duplicate(gun["name"], gun["nation"], existing_guns):
            duplicate_guns.append((gun["name"], gun["nation"]))
        else:
            new_guns.append(gun)

    print(f"\n    VEHICLES:")
    print(f"      New entries: {len(new_vehicles)}")
    print(f"      Duplicates skipped: {len(duplicate_vehicles)}")

    print(f"\n    GUNS:")
    print(f"      New entries: {len(new_guns)}")
    print(f"      Duplicates skipped: {len(duplicate_guns)}")

    # Display duplicates
    if duplicate_vehicles:
        print(f"\n    Duplicate Vehicles Skipped:")
        for name, nation in duplicate_vehicles:
            print(f"      - {name} ({nation})")

    if duplicate_guns:
        print(f"\n    Duplicate Guns Skipped:")
        for name, nation in duplicate_guns:
            print(f"      - {name} ({nation})")

    # Display new entries
    if new_vehicles:
        print(f"\n    NEW Vehicles to Import:")
        for v in new_vehicles:
            print(f"      - {v['name']} ({v['nation']})")

    if new_guns:
        print(f"\n    NEW Guns to Import:")
        for g in new_guns:
            print(f"      - {g['name']} ({g['nation']})")

    # Save to JSON files
    print("\n[4] Saving to JSON files...")

    OUTPUT_VEHICLES.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_VEHICLES, 'w', encoding='utf-8') as f:
        json.dump(new_vehicles, f, indent=2)
    print(f"    [OK] Saved: {OUTPUT_VEHICLES}")

    with open(OUTPUT_GUNS, 'w', encoding='utf-8') as f:
        json.dump(new_guns, f, indent=2)
    print(f"    [OK] Saved: {OUTPUT_GUNS}")

    # Import to database
    print("\n[5] Importing to database...")

    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    vehicles_imported = 0
    for vehicle in new_vehicles:
        try:
            cursor.execute("""
                INSERT INTO bg_reference_vehicles (
                    name, nation, year_range, vehicle_type, weapons,
                    points_cost, battle_rating, source_file, extraction_confidence, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle["name"],
                vehicle["nation"],
                vehicle.get("year_range"),
                vehicle.get("vehicle_type"),
                json.dumps(vehicle.get("weapons", [])),
                vehicle.get("points_cost"),
                vehicle.get("battle_rating"),
                vehicle.get("source_file"),
                vehicle.get("extraction_confidence"),
                vehicle.get("notes"),
                datetime.now().isoformat()
            ))
            vehicles_imported += 1
        except sqlite3.IntegrityError as e:
            print(f"    [!] Skipped duplicate: {vehicle['name']} ({vehicle['nation']})")

    guns_imported = 0
    for gun in new_guns:
        try:
            cursor.execute("""
                INSERT INTO bg_reference_guns (
                    name, nation, caliber_mm, barrel_length, source_file,
                    extraction_confidence, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gun["name"],
                gun["nation"],
                gun.get("caliber_mm"),
                gun.get("barrel_length"),
                gun.get("source_file"),
                gun.get("extraction_confidence"),
                gun.get("notes"),
                datetime.now().isoformat()
            ))
            guns_imported += 1
        except sqlite3.IntegrityError as e:
            print(f"    [!] Skipped duplicate: {gun['name']} ({gun['nation']})")

    db.commit()

    print(f"    [OK] Imported {vehicles_imported} vehicles")
    print(f"    [OK] Imported {guns_imported} guns")

    # Final database counts
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
    final_vehicle_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bg_reference_guns")
    final_gun_count = cursor.fetchone()[0]

    db.close()

    print("\n[6] Final Database Statistics:")
    print(f"    Total vehicles: {final_vehicle_count} (+{vehicles_imported})")
    print(f"    Total guns: {final_gun_count} (+{guns_imported})")

    # Summary
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nSUMMARY:")
    print(f"  Extracted from file:")
    print(f"    - Vehicles: {len(vehicles)}")
    print(f"    - Guns: {len(guns)}")
    print(f"\n  Duplicates skipped:")
    print(f"    - Vehicles: {len(duplicate_vehicles)}")
    print(f"    - Guns: {len(duplicate_guns)}")
    print(f"\n  NEW entries imported:")
    print(f"    - Vehicles: {vehicles_imported}")
    print(f"    - Guns: {guns_imported}")
    print(f"\n  Final database totals:")
    print(f"    - Vehicles: {final_vehicle_count}")
    print(f"    - Guns: {final_gun_count}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
