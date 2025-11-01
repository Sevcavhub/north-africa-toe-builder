#!/usr/bin/env python3
"""
Import BattleGroup vehicles from PDF extractions into master_database.db

Normalizes different JSON schemas from subagents and imports into bg_reference_vehicles table.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "database" / "master_database.db"

def normalize_us_vehicle(vehicle: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize US vehicle schema"""
    return {
        'name': vehicle['name'],
        'nation': 'american',
        'year_range': vehicle.get('year_range'),
        'vehicle_type': classify_vehicle(vehicle['name']),
        'off_road_inches': vehicle.get('off_road_inches'),
        'road_inches': vehicle.get('road_inches'),
        'special_movement': vehicle.get('special_movement'),
        'armor_front': vehicle.get('armor_front'),
        'armor_side': vehicle.get('armor_side'),
        'armor_rear': vehicle.get('armor_rear'),
        'weapons': json.dumps(vehicle.get('weapons', [])) if vehicle.get('weapons') else None,
        'source_file': 'Battlegroup-DataCards-US.pdf',
        'extraction_confidence': 'high'
    }

def normalize_soviet_vehicle(vehicle: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Soviet vehicle schema (uses nested movement/armor objects)"""
    movement = vehicle.get('movement', {})
    armor = vehicle.get('armor', {})

    return {
        'name': vehicle.get('vehicle_name') or vehicle.get('name'),
        'nation': 'soviet',
        'year_range': vehicle.get('year_range'),
        'vehicle_type': classify_vehicle(vehicle.get('vehicle_name') or vehicle.get('name')),
        'off_road_inches': parse_inches(movement.get('off_road')),
        'road_inches': parse_inches(movement.get('road')),
        'special_movement': movement.get('special'),
        'armor_front': armor.get('front'),
        'armor_side': armor.get('side'),
        'armor_rear': armor.get('rear'),
        'weapons': json.dumps(vehicle.get('weapons', [])) if vehicle.get('weapons') else None,
        'source_file': 'Battlegroup-DataCards-Soviets.pdf',
        'extraction_confidence': 'high'
    }

def normalize_french_vehicle(vehicle: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize French vehicle schema (uses nested movement/armor objects)"""
    movement = vehicle.get('movement', {})
    armor = vehicle.get('armor', {})

    # Determine nation from metadata or default to french
    nation = vehicle.get('nation', 'french')

    return {
        'name': vehicle.get('name'),
        'nation': nation,
        'year_range': vehicle.get('year') if vehicle.get('year') else None,
        'vehicle_type': classify_vehicle(vehicle.get('name')),
        'off_road_inches': movement.get('off_road') if isinstance(movement.get('off_road'), int) else None,
        'road_inches': movement.get('road') if isinstance(movement.get('road'), int) else None,
        'special_movement': movement.get('special'),
        'armor_front': armor.get('front') if armor.get('front') != '0' else None,
        'armor_side': armor.get('side') if armor.get('side') != '0' else None,
        'armor_rear': armor.get('rear') if armor.get('rear') != '0' else None,
        'weapons': json.dumps(vehicle.get('weapons', [])) if vehicle.get('weapons') else None,
        'source_file': 'Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf',
        'extraction_confidence': 'high'
    }

def parse_inches(value: Any) -> int:
    """Parse inches from string like '12"' or integer"""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.replace('"', '').strip())
    return None

def classify_vehicle(name: str) -> str:
    """Classify vehicle type from name"""
    if not name:
        return 'unknown'

    name_lower = name.lower()

    if 'stuart' in name_lower or 'ba-64' in name_lower or 't-60' in name_lower or 't-70' in name_lower:
        return 'light_tank'
    elif 'sherman' in name_lower or 't-34' in name_lower or 't-28' in name_lower or 'pzkpfw' in name_lower:
        return 'tank'
    elif 'kv-' in name_lower or 'is-2' in name_lower or 't-35' in name_lower or 'pershing' in name_lower:
        return 'heavy_tank'
    elif 'su-' in name_lower or 'isu-' in name_lower or 'm10' in name_lower or 'm36' in name_lower:
        return 'tank_destroyer'
    elif 'ba-10' in name_lower or 'm8' in name_lower or 'm20' in name_lower or 'greyhound' in name_lower:
        return 'armored_car'
    elif 'half' in name_lower or 'm2' in name_lower or 'm3' in name_lower or 'm15' in name_lower or 'm16' in name_lower:
        return 'halftrack'
    elif 'truck' in name_lower or 'gaz' in name_lower or 'zis' in name_lower or 'gmc' in name_lower or 'dodge' in name_lower or 'tatra' in name_lower:
        return 'truck'
    elif 'jeep' in name_lower:
        return 'jeep'
    elif 'priest' in name_lower or 'scott' in name_lower:
        return 'self_propelled_artillery'
    else:
        return 'unknown'

def import_vehicles(conn: sqlite3.Connection, vehicles: List[Dict[str, Any]]) -> int:
    """Import normalized vehicles into database"""
    inserted = 0

    for vehicle in vehicles:
        try:
            conn.execute("""
                INSERT INTO bg_reference_vehicles (
                    name, nation, year_range, vehicle_type,
                    off_road_inches, road_inches, special_movement,
                    armor_front, armor_side, armor_rear,
                    weapons, source_file, extraction_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle['name'],
                vehicle['nation'],
                vehicle['year_range'],
                vehicle['vehicle_type'],
                vehicle['off_road_inches'],
                vehicle['road_inches'],
                vehicle['special_movement'],
                vehicle['armor_front'],
                vehicle['armor_side'],
                vehicle['armor_rear'],
                vehicle['weapons'],
                vehicle['source_file'],
                vehicle['extraction_confidence']
            ))
            inserted += 1
        except sqlite3.IntegrityError as e:
            print(f"[SKIP] Duplicate vehicle: {vehicle['name']} ({e})")
        except Exception as e:
            print(f"[ERROR] Failed to insert {vehicle.get('name')}: {e}")

    return inserted

def main():
    """Import all PDF-extracted vehicles into database"""
    print("="*70)
    print("IMPORTING BATTLEGROUP PDF EXTRACTIONS")
    print("="*70)

    conn = sqlite3.connect(DB_PATH)

    # Import US vehicles
    print("\n[1/3] Importing US vehicles...")
    us_file = PROJECT_ROOT / "data" / "output" / "battlegroup_us_vehicles.json"
    if us_file.exists():
        us_data = json.loads(us_file.read_text())
        us_normalized = [normalize_us_vehicle(v) for v in us_data]
        us_count = import_vehicles(conn, us_normalized)
        print(f"   [OK] Imported {us_count}/{len(us_data)} US vehicles")
    else:
        print(f"   [WARN] File not found: {us_file}")

    # Import Soviet vehicles
    print("\n[2/3] Importing Soviet vehicles...")
    soviet_file = PROJECT_ROOT / "data" / "output" / "battlegroup_soviet_vehicles.json"
    if soviet_file.exists():
        soviet_data = json.loads(soviet_file.read_text())
        soviet_normalized = [normalize_soviet_vehicle(v) for v in soviet_data]
        soviet_count = import_vehicles(conn, soviet_normalized)
        print(f"   [OK] Imported {soviet_count}/{len(soviet_data)} Soviet vehicles")
    else:
        print(f"   [WARN] File not found: {soviet_file}")

    # Import French vehicles
    print("\n[3/3] Importing French/Polish/Romanian/Hungarian vehicles...")
    french_file = PROJECT_ROOT / "data" / "output" / "battlegroup_french_polish_romanian_hungarian_vehicles.json"
    if french_file.exists():
        french_data = json.loads(french_file.read_text())
        french_normalized = [normalize_french_vehicle(v) for v in french_data]
        french_count = import_vehicles(conn, french_normalized)
        print(f"   [OK] Imported {french_count}/{len(french_data)} French/Allied vehicles")
    else:
        print(f"   [WARN] File not found: {french_file}")

    conn.commit()

    # Show final statistics
    print("\n" + "="*70)
    print("FINAL DATABASE STATISTICS")
    print("="*70)

    cursor = conn.execute("SELECT nation, COUNT(*) FROM bg_reference_vehicles GROUP BY nation ORDER BY nation")
    for nation, count in cursor.fetchall():
        print(f"   {nation.capitalize()}: {count} vehicles")

    total = conn.execute("SELECT COUNT(*) FROM bg_reference_vehicles").fetchone()[0]
    print(f"\n   TOTAL: {total} vehicles")

    conn.close()
    print("\n[OK] Import complete!")
    print("="*70)

if __name__ == "__main__":
    main()
