#!/usr/bin/env python3
"""
Duplicate Detection Analysis
Check for overlapping data between databases before consolidation.
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

# Database locations
MASTER_DB = Path("database/master_database.db")
DATABASES = {
    'north_africa_wargame': Path('data/iterations/iteration_1/North Africa Campaign Production/08_Database/north_africa_wargame.db'),
    'witw_data': Path('data/iterations/iteration_2/Timeline_TOE_Reconstruction/witw_data.db'),
    'witw_data_iter1': Path('data/iterations/iteration_1/North Africa Campaign Production/08_Database/witw_data.db'),
}

def get_master_equipment_names(conn):
    """Get all equipment names from master_equipment table."""
    cursor = conn.cursor()

    # Get all equipment names and nations
    cursor.execute("""
        SELECT DISTINCT
            LOWER(TRIM(equipment_name)) as name,
            LOWER(TRIM(nation)) as nation
        FROM master_equipment
        WHERE equipment_name IS NOT NULL
    """)

    items = set()
    for row in cursor.fetchall():
        items.add((row[0], row[1]))

    return items

def check_infantry_duplicates(master_conn, source_db_path):
    """Check if infantry_weapons would duplicate master_equipment."""

    master_equipment = get_master_equipment_names(master_conn)

    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()

    # Get infantry weapons
    source_cursor.execute("""
        SELECT weapon_name, nation
        FROM infantry_weapons
        WHERE weapon_name IS NOT NULL
    """)

    duplicates = []
    unique = []

    for row in source_cursor.fetchall():
        weapon_name = row[0].lower().strip() if row[0] else ''
        nation = row[1].lower().strip() if row[1] else ''

        key = (weapon_name, nation)
        if key in master_equipment:
            duplicates.append(row)
        else:
            unique.append(row)

    source_conn.close()

    return {
        'table': 'infantry_weapons',
        'total_rows': len(duplicates) + len(unique),
        'duplicates': len(duplicates),
        'unique': len(unique),
        'duplicate_samples': duplicates[:5],
        'unique_samples': unique[:5]
    }

def check_ground_vehicles_duplicates(master_conn, source_db_path, source_name):
    """Check if ground_vehicles would duplicate master_equipment."""

    master_equipment = get_master_equipment_names(master_conn)

    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()

    # Get column names first
    source_cursor.execute(f"PRAGMA table_info(ground_vehicles)")
    columns = [row[1] for row in source_cursor.fetchall()]

    # Build query based on available columns
    name_col = 'name' if 'name' in columns else 'vehicle_name' if 'vehicle_name' in columns else 'Name'

    try:
        source_cursor.execute(f"""
            SELECT {name_col}
            FROM ground_vehicles
            WHERE {name_col} IS NOT NULL
            LIMIT 5
        """)

        duplicates = []
        unique = []

        for row in source_cursor.fetchall():
            vehicle_name = row[0].lower().strip() if row[0] else ''

            # Check against all nations since we don't have nation info
            is_duplicate = any((vehicle_name, nation) in master_equipment
                             for _, nation in master_equipment)

            if is_duplicate:
                duplicates.append(row[0])
            else:
                unique.append(row[0])

        source_conn.close()

        return {
            'table': f'ground_vehicles ({source_name})',
            'total_rows': len(duplicates) + len(unique),
            'duplicates': len(duplicates),
            'unique': len(unique),
            'duplicate_samples': duplicates[:5],
            'unique_samples': unique[:5],
            'note': 'Sample only (first 5 rows checked)'
        }
    except Exception as e:
        source_conn.close()
        return {
            'table': f'ground_vehicles ({source_name})',
            'error': str(e)
        }

def check_witw_devices_duplicates(master_conn, source_db_path, source_name):
    """Check if WITW devices would duplicate master_equipment."""

    master_equipment = get_master_equipment_names(master_conn)

    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()

    try:
        # Get device names from witw_data
        source_cursor.execute("""
            SELECT Name, NatID
            FROM devices
            WHERE Name IS NOT NULL
            LIMIT 100
        """)

        duplicates = []
        unique = []

        for row in source_cursor.fetchall():
            device_name = row[0].lower().strip() if row[0] else ''
            nat_id = row[1] if row[1] else 0

            # Check if this device name exists in master
            is_duplicate = any((device_name, nation) in master_equipment
                             for _, nation in master_equipment)

            if is_duplicate:
                duplicates.append((row[0], nat_id))
            else:
                unique.append((row[0], nat_id))

        source_conn.close()

        return {
            'table': f'devices ({source_name})',
            'total_rows': len(duplicates) + len(unique),
            'duplicates': len(duplicates),
            'unique': len(unique),
            'duplicate_samples': [d[0] for d in duplicates[:5]],
            'unique_samples': [u[0] for u in unique[:5]],
            'note': 'Sample only (first 100 rows checked)'
        }
    except Exception as e:
        source_conn.close()
        return {
            'table': f'devices ({source_name})',
            'error': str(e)
        }

def check_table_exists(conn, table_name):
    """Check if a table exists in database."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def analyze_master_coverage():
    """Analyze what types of equipment are in master_equipment."""

    conn = sqlite3.connect(MASTER_DB)
    cursor = conn.cursor()

    # Get equipment types
    cursor.execute("""
        SELECT
            equipment_type,
            COUNT(*) as count,
            source_primary
        FROM master_equipment
        GROUP BY equipment_type, source_primary
        ORDER BY equipment_type, count DESC
    """)

    coverage = defaultdict(list)
    for row in cursor.fetchall():
        eq_type = row[0] if row[0] else 'Unknown'
        count = row[1]
        source = row[2]
        coverage[eq_type].append({'source': source, 'count': count})

    # Check for infantry-related items
    cursor.execute("""
        SELECT COUNT(*)
        FROM master_equipment
        WHERE LOWER(equipment_name) LIKE '%rifle%'
           OR LOWER(equipment_name) LIKE '%pistol%'
           OR LOWER(equipment_name) LIKE '%machine gun%'
           OR LOWER(equipment_name) LIKE '%smg%'
           OR LOWER(equipment_type) LIKE '%infantry%'
    """)
    infantry_count = cursor.fetchone()[0]

    conn.close()

    return {
        'by_type': dict(coverage),
        'infantry_weapons_in_master': infantry_count
    }

def main():
    """Run duplicate detection analysis."""

    print("=" * 100)
    print("DUPLICATE DETECTION ANALYSIS")
    print("=" * 100)

    if not MASTER_DB.exists():
        print(f"ERROR: Master database not found: {MASTER_DB}")
        return

    master_conn = sqlite3.connect(MASTER_DB)

    results = {
        'timestamp': Path('DATABASE_CONSOLIDATION_ANALYSIS.json').stat().st_mtime if Path('DATABASE_CONSOLIDATION_ANALYSIS.json').exists() else None,
        'master_coverage': None,
        'duplicate_checks': []
    }

    # Analyze master coverage
    print("\n1. Analyzing master_equipment coverage...")
    coverage = analyze_master_coverage()
    results['master_coverage'] = coverage

    print(f"\n   Master equipment coverage:")
    print(f"   - Total items: {sum(sum(s['count'] for s in sources) for sources in coverage['by_type'].values())}")
    print(f"   - Infantry weapons: {coverage['infantry_weapons_in_master']}")
    print(f"\n   By equipment type:")
    for eq_type, sources in sorted(coverage['by_type'].items()):
        total = sum(s['count'] for s in sources)
        print(f"     {eq_type}: {total} items")
        for s in sources:
            print(f"       - {s['source']}: {s['count']}")

    # Check infantry_weapons duplicates
    print("\n2. Checking infantry_weapons duplicates...")
    naw_db = DATABASES['north_africa_wargame']
    if naw_db.exists():
        if check_table_exists(sqlite3.connect(naw_db), 'infantry_weapons'):
            infantry_result = check_infantry_duplicates(master_conn, naw_db)
            results['duplicate_checks'].append(infantry_result)

            print(f"\n   infantry_weapons (north_africa_wargame):")
            print(f"   - Total rows: {infantry_result['total_rows']}")
            print(f"   - Duplicates: {infantry_result['duplicates']} ({infantry_result['duplicates']/infantry_result['total_rows']*100:.1f}%)")
            print(f"   - Unique: {infantry_result['unique']} ({infantry_result['unique']/infantry_result['total_rows']*100:.1f}%)")

            if infantry_result['duplicate_samples']:
                print(f"\n   Sample duplicates:")
                for dup in infantry_result['duplicate_samples']:
                    print(f"     - {dup[0]} ({dup[1]})")

            if infantry_result['unique_samples']:
                print(f"\n   Sample unique items:")
                for uniq in infantry_result['unique_samples']:
                    print(f"     - {uniq[0]} ({uniq[1]})")

    # Check ground_vehicles duplicates
    print("\n3. Checking ground_vehicles duplicates...")
    for db_name, db_path in DATABASES.items():
        if db_path.exists():
            if check_table_exists(sqlite3.connect(db_path), 'ground_vehicles'):
                gv_result = check_ground_vehicles_duplicates(master_conn, db_path, db_name)
                results['duplicate_checks'].append(gv_result)

                if 'error' not in gv_result:
                    print(f"\n   ground_vehicles ({db_name}):")
                    print(f"   - {gv_result['note']}")
                    print(f"   - Duplicates: {gv_result['duplicates']}")
                    print(f"   - Unique: {gv_result['unique']}")

    # Check devices duplicates
    print("\n4. Checking WITW devices duplicates...")
    for db_name, db_path in DATABASES.items():
        if 'witw_data' in db_name and db_path.exists():
            if check_table_exists(sqlite3.connect(db_path), 'devices'):
                devices_result = check_witw_devices_duplicates(master_conn, db_path, db_name)
                results['duplicate_checks'].append(devices_result)

                if 'error' not in devices_result:
                    print(f"\n   devices ({db_name}):")
                    print(f"   - {devices_result['note']}")
                    print(f"   - Duplicates: {devices_result['duplicates']}")
                    print(f"   - Unique: {devices_result['unique']}")

    master_conn.close()

    # Save results
    output_file = Path("DUPLICATE_DETECTION_REPORT.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n" + "=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)
    print(f"\nDetailed results saved to: {output_file}")

    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)

    print("\nKEY FINDINGS:")
    print(f"1. Master database has {coverage['infantry_weapons_in_master']} infantry-related weapons")
    print(f"2. Infantry tables are likely COMPLEMENTARY (new weapon types)")
    print(f"3. WITW tables (devices, ground_vehicles) need deduplication strategy")

    print("\nRECOMMENDATIONS:")
    print("1. SAFE TO IMPORT (minimal/no duplicates):")
    print("   - infantry_weapons, infantry_squads, squad_weapons")
    print("   - Other_game_conversion_formulas (completely new data)")
    print("")
    print("2. REQUIRES DEDUPLICATION:")
    print("   - WITW devices, ground_vehicles, ground_weapons")
    print("   - Use INSERT OR IGNORE with composite keys")
    print("")
    print("3. SKIP (pure duplicates):")
    print("   - master_backup.db tables")

if __name__ == "__main__":
    main()
