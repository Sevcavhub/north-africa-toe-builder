#!/usr/bin/env python3
"""
Phase 5 Data Import
Imports OnWar and WWIITANKS source data into master_database.db.

Imports:
1. OnWar AFV data → afv_data table (structured, ready to use)
2. WWIITANKS AFV data → wwiitanks_afv_data table (raw, needs parsing)
3. WWIITANKS gun data → wwiitanks_gun_data table (raw, needs parsing)
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Source file paths
ONWAR_FILE = Path("data/output/afv_data/afv_complete_with_specs.json")
WWIITANKS_AFV_FILE = Path("data/output/afv_data/wwiitanks/all_afvs.json")
WWIITANKS_GUN_FILE = Path("data/output/afv_data/wwiitanks/all_guns_v2.json")

DATABASE_FILE = Path("database/master_database.db")


def import_onwar_data(conn) -> Dict[str, int]:
    """Import OnWar AFV data into afv_data table."""
    print("\n" + "=" * 70)
    print("IMPORTING ONWAR AFV DATA")
    print("=" * 70)

    print(f"\nReading: {ONWAR_FILE}")

    with open(ONWAR_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    print(f"Found {total} AFV records")

    cursor = conn.cursor()
    imported = 0
    failed = 0
    skipped = 0

    timestamp = datetime.now().isoformat()

    print("\nImporting records...")
    for i, item in enumerate(data, 1):
        if i % 50 == 0 or i == total:
            print(f"  Progress: {i}/{total} ({i/total*100:.1f}%)")

        try:
            # Check if already exists
            vehicle_name = item.get('vehicle_name', '')
            country = item.get('country', '')

            cursor.execute("SELECT id FROM afv_data WHERE vehicle_name = ? AND country = ?", (vehicle_name, country))
            if cursor.fetchone():
                skipped += 1
                continue

            # Insert record with all fields from JSON
            cursor.execute("""
                INSERT INTO afv_data (
                    country, vehicle_name, url, formal_designation, type,
                    crew, manufacturers, production_quantity, production_period,
                    length_hull, width, height, combat_weight, ground_clearance,
                    radio, primary_armament, secondary_armament, ammunition_carried,
                    traverse, elevation,
                    engine_make_model, engine_type_displacement, horsepower,
                    power_weight_ratio, fuel_type, fuel_capacity, speed, range, gearbox,
                    turning_radius, gradient, fording, vertical_obstacle,
                    trench_crossing, ground_pressure, track_width, track_ground_contact,
                    hull_front, hull_side, hull_rear, hull_top_bottom,
                    superstructure_front, superstructure_side, superstructure_rear, superstructure_top_bottom,
                    turret_front, turret_side, turret_rear, turret_top_bottom, mantlet,
                    source, scraped_date, imported_at, imported_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get('country', ''),
                item.get('vehicle_name', ''),
                item.get('url', ''),
                item.get('formal_designation', ''),
                item.get('type', ''),
                item.get('crew', ''),
                item.get('manufacturers', ''),
                item.get('production_quantity', ''),
                item.get('production_period', ''),
                item.get('length_hull', ''),
                item.get('width', ''),
                item.get('height', ''),
                item.get('combat_weight', ''),
                item.get('ground_clearance', ''),
                item.get('radio', ''),
                item.get('primary_armament', ''),
                item.get('secondary_armament', ''),
                item.get('ammunition_carried', ''),
                item.get('traverse', ''),
                item.get('elevation', ''),
                item.get('engine_make_model', ''),
                item.get('engine_type_displacement', ''),
                item.get('horsepower', ''),
                item.get('power_weight_ratio', ''),
                item.get('fuel_type', ''),
                item.get('fuel_capacity', ''),
                item.get('speed', ''),
                item.get('range', ''),
                item.get('gearbox', ''),
                item.get('turning_radius', ''),
                item.get('gradient', ''),
                item.get('fording', ''),
                item.get('vertical_obstacle', ''),
                item.get('trench_crossing', ''),
                item.get('ground_pressure', ''),
                item.get('track_width', ''),
                item.get('track_ground_contact', ''),
                item.get('hull_front', ''),
                item.get('hull_side', ''),
                item.get('hull_rear', ''),
                item.get('hull_top_bottom', ''),
                item.get('superstructure_front', ''),
                item.get('superstructure_side', ''),
                item.get('superstructure_rear', ''),
                item.get('superstructure_top_bottom', ''),
                item.get('turret_front', ''),
                item.get('turret_side', ''),
                item.get('turret_rear', ''),
                item.get('turret_top_bottom', ''),
                item.get('mantlet', ''),
                'onwar.com',
                None,  # scraped_date not in source data
                timestamp,
                'import_phase5_sources.py'
            ))
            imported += 1

        except Exception as e:
            print(f"\n  ERROR importing {item.get('vehicle_name', 'unknown')}: {e}")
            failed += 1

    conn.commit()

    print(f"\n[SUCCESS] OnWar import complete")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")

    return {"imported": imported, "failed": failed, "skipped": skipped}


def import_wwiitanks_afv_data(conn) -> Dict[str, int]:
    """Import WWIITANKS AFV data into wwiitanks_afv_data table."""
    print("\n" + "=" * 70)
    print("IMPORTING WWIITANKS AFV DATA")
    print("=" * 70)

    print(f"\nReading: {WWIITANKS_AFV_FILE}")

    with open(WWIITANKS_AFV_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    print(f"Found {total} AFV records")

    cursor = conn.cursor()
    imported = 0
    failed = 0
    skipped = 0

    timestamp = datetime.now().isoformat()

    print("\nImporting records...")
    print("  Note: Storing raw data - parsing will happen in next phase")

    for i, item in enumerate(data, 1):
        if i % 100 == 0 or i == total:
            print(f"  Progress: {i}/{total} ({i/total*100:.1f}%)")

        try:
            # Check if already exists
            wwiitanks_id = item.get('wwiitanks_id', '')

            cursor.execute("SELECT id FROM wwiitanks_afv_data WHERE wwiitanks_id = ?", (wwiitanks_id,))
            if cursor.fetchone():
                skipped += 1
                continue

            # Store raw data as JSON text (will be parsed later)
            indicators = item.get('indicators', {})

            cursor.execute("""
                INSERT INTO wwiitanks_afv_data (
                    wwiitanks_id, country, vehicle_name, full_name,
                    source, source_url, scraped_at, scraper_version,
                    has_photo, has_scale_illustration, has_vehicle_history,
                    has_weapon_details, has_armour_details,
                    general_details, specifications, armour_details,
                    weapon_details, vehicle_history,
                    imported_at, imported_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get('wwiitanks_id', ''),
                item.get('country', ''),
                item.get('vehicle_name', ''),
                item.get('full_name', ''),
                item.get('source', 'wwiitanks.co.uk'),
                item.get('source_url', ''),
                item.get('scraped_at', ''),
                item.get('scraper_version', ''),
                1 if indicators.get('hasPhoto') else 0,
                1 if indicators.get('hasScaleIllustration') else 0,
                1 if indicators.get('hasVehicleHistory') else 0,
                1 if indicators.get('hasWeaponDetails') else 0,
                1 if indicators.get('hasArmourDetails') else 0,
                json.dumps(item.get('general_details', {})),
                json.dumps(item.get('specifications', {})),
                json.dumps(item.get('armour_details', {})),
                json.dumps(item.get('weapon_details', {})),
                json.dumps(item.get('vehicle_history', {})),
                timestamp,
                'import_phase5_sources.py'
            ))
            imported += 1

        except Exception as e:
            print(f"\n  ERROR importing {item.get('vehicle_name', 'unknown')}: {e}")
            failed += 1

    conn.commit()

    print(f"\n[SUCCESS] WWIITANKS AFV import complete")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")

    return {"imported": imported, "failed": failed, "skipped": skipped}


def import_wwiitanks_gun_data(conn) -> Dict[str, int]:
    """Import WWIITANKS gun data into wwiitanks_gun_data table."""
    print("\n" + "=" * 70)
    print("IMPORTING WWIITANKS GUN DATA")
    print("=" * 70)

    print(f"\nReading: {WWIITANKS_GUN_FILE}")

    with open(WWIITANKS_GUN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    print(f"Found {total} gun records")

    cursor = conn.cursor()
    imported = 0
    failed = 0
    skipped = 0

    timestamp = datetime.now().isoformat()

    print("\nImporting records...")
    print("  Note: Storing raw data - parsing will happen in next phase")

    for i, item in enumerate(data, 1):
        if i % 100 == 0 or i == total:
            print(f"  Progress: {i}/{total} ({i/total*100:.1f}%)")

        try:
            # Check if already exists
            wwiitanks_id = item.get('wwiitanks_id', '')

            cursor.execute("SELECT id FROM wwiitanks_gun_data WHERE wwiitanks_id = ?", (wwiitanks_id,))
            if cursor.fetchone():
                skipped += 1
                continue

            # Store raw data
            basic_specs = item.get('basic_specs', {})

            cursor.execute("""
                INSERT INTO wwiitanks_gun_data (
                    wwiitanks_id, country, gun_name, full_name,
                    source, source_url, scraped_at, scraper_version,
                    manufactured, calibre, length, rate_of_fire,
                    ammunition, vehicles_using_gun,
                    imported_at, imported_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get('wwiitanks_id', ''),
                item.get('country', ''),
                item.get('gun_name', ''),
                item.get('full_name', ''),
                item.get('source', 'wwiitanks.co.uk'),
                item.get('source_url', ''),
                item.get('scraped_at', ''),
                item.get('scraper_version', ''),
                basic_specs.get('manufactured', ''),
                basic_specs.get('calibre', ''),
                basic_specs.get('length', ''),
                basic_specs.get('rate_of_fire', ''),
                json.dumps(item.get('ammunition', [])),
                json.dumps(item.get('vehicles_using_gun', [])),
                timestamp,
                'import_phase5_sources.py'
            ))
            imported += 1

        except Exception as e:
            print(f"\n  ERROR importing {item.get('gun_name', 'unknown')}: {e}")
            failed += 1

    conn.commit()

    print(f"\n[SUCCESS] WWIITANKS gun import complete")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")

    return {"imported": imported, "failed": failed, "skipped": skipped}


def log_import(conn, source_name: str, source_file: str, results: Dict[str, int]):
    """Log import results to import_log table."""
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()

    status = 'success' if results['failed'] == 0 else 'partial_success'
    error_log = f"Failed: {results['failed']}, Skipped: {results['skipped']}" if results['failed'] > 0 or results['skipped'] > 0 else None

    cursor.execute("""
        INSERT INTO import_log (
            source_name, source_file, records_imported, records_failed,
            import_started_at, import_completed_at, import_status,
            error_log, imported_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source_name,
        str(source_file),
        results['imported'],
        results['failed'],
        timestamp,
        timestamp,
        status,
        error_log,
        'import_phase5_sources.py'
    ))

    conn.commit()


def main():
    """Main execution function."""
    print("=" * 70)
    print("PHASE 5 DATA IMPORT")
    print("=" * 70)

    # Check files exist
    for filepath in [ONWAR_FILE, WWIITANKS_AFV_FILE, WWIITANKS_GUN_FILE]:
        if not filepath.exists():
            print(f"ERROR: Source file not found: {filepath}")
            sys.exit(1)

    # Check database exists
    if not DATABASE_FILE.exists():
        print(f"ERROR: Database file not found: {DATABASE_FILE}")
        sys.exit(1)

    # Connect to database
    print(f"\nConnecting to: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)

    try:
        # Import OnWar data
        onwar_results = import_onwar_data(conn)
        log_import(conn, 'onwar_afv', ONWAR_FILE, onwar_results)

        # Import WWIITANKS AFV data
        wwiitanks_afv_results = import_wwiitanks_afv_data(conn)
        log_import(conn, 'wwiitanks_afv', WWIITANKS_AFV_FILE, wwiitanks_afv_results)

        # Import WWIITANKS gun data
        wwiitanks_gun_results = import_wwiitanks_gun_data(conn)
        log_import(conn, 'wwiitanks_gun', WWIITANKS_GUN_FILE, wwiitanks_gun_results)

        # Final summary
        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print(f"\nOnWar AFV: {onwar_results['imported']} imported")
        print(f"WWIITANKS AFV: {wwiitanks_afv_results['imported']} imported")
        print(f"WWIITANKS Gun: {wwiitanks_gun_results['imported']} imported")
        print(f"\nTotal: {onwar_results['imported'] + wwiitanks_afv_results['imported'] + wwiitanks_gun_results['imported']} records")

        print("\nNext steps:")
        print("  1. Parse WWIITANKS raw data (future enhancement)")
        print("  2. Populate equipment table specs (Phase 4)")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
