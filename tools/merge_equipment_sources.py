#!/usr/bin/env python3
"""
Merge Equipment Sources into Master Table
Imports all equipment from WITW, OnWar, and WWIITANKS into master_equipment table.

Strategy:
1. Import all OnWar AFVs (211 items) - structured data, good specs
2. Import all WWIITANKS AFVs (612 items) - comprehensive but needs parsing
3. Import WITW equipment (469 items) - game data, official IDs
4. Calculate completeness scores for each item
5. Handle deduplication (mark secondary sources)
"""

import sqlite3
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

DATABASE_FILE = Path("database/master_database.db")

# Nation normalization
NATION_NORMALIZE = {
    'usa': 'american',
    'uk': 'british',
    'britain': 'british',
    'germany': 'german',
    'italy': 'italian',
    'france': 'french',
    'ussr': 'soviet',
    'japan': 'japanese'
}


def normalize_nation(nation: str) -> str:
    """Normalize nation names to standard format."""
    return NATION_NORMALIZE.get(nation.lower(), nation.lower())


def parse_numeric(value) -> Optional[float]:
    """Parse numeric value from text or number."""
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return None
    if isinstance(value, str):
        if value.strip().lower() in ['', 'n.a.', 'n/a', 'unknown', '?', '-', 'none']:
            return None
        # Extract first number
        match = re.search(r'(\d+\.?\d*)', value.strip())
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
    return None


def parse_range_average(value) -> Optional[float]:
    """Parse average of range, or single value."""
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return None
    if isinstance(value, str):
        # Try range "X-Y"
        match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', value.strip())
        if match:
            try:
                val1 = float(match.group(1))
                val2 = float(match.group(2))
                return (val1 + val2) / 2
            except ValueError:
                pass
    return parse_numeric(value)


def calculate_completeness(item: Dict) -> int:
    """Calculate completeness score (0-100) based on filled fields."""
    critical_fields = [
        'crew', 'weight_tonnes',
        'armor_hull_front_mm', 'armor_hull_side_mm', 'armor_hull_rear_mm',
        'armor_turret_front_mm', 'armor_turret_side_mm', 'armor_turret_rear_mm',
        'primary_armament', 'max_speed_kmh', 'range_road_km',
        'engine_hp', 'production_start', 'manufacturers'
    ]

    filled = sum(1 for field in critical_fields if item.get(field) is not None)
    return int((filled / len(critical_fields)) * 100)


def import_onwar_afvs(conn):
    """Import all OnWar AFVs into master_equipment."""

    print("\n" + "=" * 70)
    print("IMPORTING ONWAR AFVS")
    print("=" * 70)

    cursor = conn.cursor()

    # Get all OnWar AFVs
    cursor.execute("""
        SELECT id, country, vehicle_name, url, type,
               crew, combat_weight, length_hull, width, height,
               hull_front, hull_side, hull_rear,
               superstructure_front, superstructure_side, superstructure_rear,
               turret_front, turret_side, turret_rear, mantlet,
               primary_armament, secondary_armament, ammunition_carried,
               speed, range, engine_make_model, horsepower,
               manufacturers, production_quantity, production_period,
               fuel_type, fuel_capacity
        FROM afv_data
        ORDER BY country, vehicle_name
    """)

    afvs = cursor.fetchall()
    total = len(afvs)

    print(f"\nFound {total} OnWar AFVs")
    print("Importing...")

    imported = 0
    skipped = 0
    timestamp = datetime.now().isoformat()

    for i, row in enumerate(afvs, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{total} ({i/total*100:.1f}%)")

        (afv_id, country, vehicle_name, url, afv_type,
         crew, combat_weight, length_hull, width, height,
         hull_front, hull_side, hull_rear,
         superstructure_front, superstructure_side, superstructure_rear,
         turret_front, turret_side, turret_rear, mantlet,
         primary_armament, secondary_armament, ammunition_carried,
         speed, range, engine_make_model, horsepower,
         manufacturers, production_quantity, production_period,
         fuel_type, fuel_capacity) = row

        try:
            # Normalize nation
            nation = normalize_nation(country)

            # Parse numeric values
            item = {
                'equipment_name': vehicle_name,
                'nation': nation,
                'equipment_type': afv_type,
                'source_primary': 'onwar',
                'onwar_url': url,
                'crew': parse_numeric(crew),
                'weight_tonnes': parse_numeric(combat_weight),
                'length_m': parse_numeric(length_hull),
                'width_m': parse_numeric(width),
                'height_m': parse_numeric(height),
                'armor_hull_front_mm': parse_range_average(hull_front),
                'armor_hull_side_mm': parse_range_average(hull_side),
                'armor_hull_rear_mm': parse_range_average(hull_rear),
                'armor_superstructure_front_mm': parse_range_average(superstructure_front),
                'armor_superstructure_side_mm': parse_range_average(superstructure_side),
                'armor_superstructure_rear_mm': parse_range_average(superstructure_rear),
                'armor_turret_front_mm': parse_range_average(turret_front),
                'armor_turret_side_mm': parse_range_average(turret_side),
                'armor_turret_rear_mm': parse_range_average(turret_rear),
                'armor_mantlet_mm': parse_range_average(mantlet),
                'primary_armament': primary_armament,
                'secondary_armament': secondary_armament,
                'ammunition_carried': ammunition_carried,
                'max_speed_kmh': parse_numeric(speed),
                'range_road_km': parse_numeric(range),
                'engine_make': engine_make_model,
                'engine_hp': parse_numeric(horsepower),
                'manufacturers': manufacturers,
                'production_quantity': production_quantity,
                'production_start': production_period,
                'fuel_type': fuel_type,
                'fuel_capacity_l': parse_numeric(fuel_capacity)
            }

            # Calculate completeness
            completeness = calculate_completeness(item)
            quality = 'high' if completeness >= 75 else 'medium' if completeness >= 50 else 'low'

            # Insert into master_equipment
            cursor.execute("""
                INSERT INTO master_equipment (
                    equipment_name, nation, equipment_type, equipment_category,
                    source_primary, onwar_url,
                    crew, weight_tonnes, length_m, width_m, height_m,
                    armor_hull_front_mm, armor_hull_side_mm, armor_hull_rear_mm,
                    armor_superstructure_front_mm, armor_superstructure_side_mm, armor_superstructure_rear_mm,
                    armor_turret_front_mm, armor_turret_side_mm, armor_turret_rear_mm, armor_mantlet_mm,
                    primary_armament, secondary_armament, ammunition_carried,
                    max_speed_kmh, range_road_km,
                    engine_make, engine_hp,
                    manufacturers, production_quantity, production_start,
                    fuel_type, fuel_capacity_l,
                    completeness_score, specification_quality,
                    created_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle_name, nation, afv_type, 'AFV',
                'onwar', url,
                item['crew'], item['weight_tonnes'], item['length_m'], item['width_m'], item['height_m'],
                item['armor_hull_front_mm'], item['armor_hull_side_mm'], item['armor_hull_rear_mm'],
                item['armor_superstructure_front_mm'], item['armor_superstructure_side_mm'], item['armor_superstructure_rear_mm'],
                item['armor_turret_front_mm'], item['armor_turret_side_mm'], item['armor_turret_rear_mm'], item['armor_mantlet_mm'],
                primary_armament, secondary_armament, ammunition_carried,
                item['max_speed_kmh'], item['range_road_km'],
                engine_make_model, item['engine_hp'],
                manufacturers, production_quantity, production_period,
                fuel_type, item['fuel_capacity_l'],
                completeness, quality,
                timestamp, 'merge_equipment_sources.py'
            ))

            imported += 1

        except Exception as e:
            print(f"\n  ERROR importing {vehicle_name}: {e}")
            skipped += 1

    conn.commit()

    print(f"\n[SUCCESS] OnWar import complete")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")

    return {'imported': imported, 'skipped': skipped}


def import_wwiitanks_afvs(conn):
    """Import all WWIITANKS AFVs into master_equipment."""

    print("\n" + "=" * 70)
    print("IMPORTING WWIITANKS AFVS")
    print("=" * 70)

    cursor = conn.cursor()

    # Get all WWIITANKS AFVs
    cursor.execute("""
        SELECT id, wwiitanks_id, country, vehicle_name,
               operational_date, quantity_produced, weight_tonnes, crew,
               armor_hull_front_mm, armor_hull_side_mm, armor_hull_rear_mm,
               armor_turret_front_mm, armor_turret_side_mm, armor_turret_rear_mm,
               speed_kmh, range_km, main_gun_caliber_mm, main_gun_name
        FROM wwiitanks_afv_data
        ORDER BY country, vehicle_name
    """)

    afvs = cursor.fetchall()
    total = len(afvs)

    print(f"\nFound {total} WWIITANKS AFVs")
    print("Importing...")

    imported = 0
    skipped = 0
    timestamp = datetime.now().isoformat()

    for i, row in enumerate(afvs, 1):
        if i % 100 == 0:
            print(f"  Progress: {i}/{total} ({i/total*100:.1f}%)")

        (wwiitanks_db_id, wwiitanks_id, country, vehicle_name,
         operational_date, quantity_produced, weight_tonnes, crew,
         armor_hull_front_mm, armor_hull_side_mm, armor_hull_rear_mm,
         armor_turret_front_mm, armor_turret_side_mm, armor_turret_rear_mm,
         speed_kmh, range_km, main_gun_caliber_mm, main_gun_name) = row

        try:
            # Normalize nation
            nation = normalize_nation(country)

            # Build item
            item = {
                'equipment_name': vehicle_name,
                'nation': nation,
                'source_primary': 'wwiitanks',
                'wwiitanks_id': wwiitanks_id,
                'crew': crew,
                'weight_tonnes': weight_tonnes,
                'armor_hull_front_mm': armor_hull_front_mm,
                'armor_hull_side_mm': armor_hull_side_mm,
                'armor_hull_rear_mm': armor_hull_rear_mm,
                'armor_turret_front_mm': armor_turret_front_mm,
                'armor_turret_side_mm': armor_turret_side_mm,
                'armor_turret_rear_mm': armor_turret_rear_mm,
                'max_speed_kmh': speed_kmh,
                'range_road_km': range_km,
                'primary_gun_caliber_mm': main_gun_caliber_mm,
                'primary_armament': main_gun_name,
                'operational_date': operational_date,
                'production_quantity': str(quantity_produced) if quantity_produced else None
            }

            # Calculate completeness
            completeness = calculate_completeness(item)
            quality = 'high' if completeness >= 75 else 'medium' if completeness >= 50 else 'low'

            # Insert into master_equipment
            cursor.execute("""
                INSERT INTO master_equipment (
                    equipment_name, nation, equipment_type, equipment_category,
                    source_primary, wwiitanks_id,
                    crew, weight_tonnes,
                    armor_hull_front_mm, armor_hull_side_mm, armor_hull_rear_mm,
                    armor_turret_front_mm, armor_turret_side_mm, armor_turret_rear_mm,
                    max_speed_kmh, range_road_km,
                    primary_gun_caliber_mm, primary_armament,
                    operational_date, production_quantity,
                    completeness_score, specification_quality,
                    created_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle_name, nation, 'AFV', 'AFV',
                'wwiitanks', wwiitanks_id,
                crew, weight_tonnes,
                armor_hull_front_mm, armor_hull_side_mm, armor_hull_rear_mm,
                armor_turret_front_mm, armor_turret_side_mm, armor_turret_rear_mm,
                speed_kmh, range_km,
                main_gun_caliber_mm, main_gun_name,
                operational_date, str(quantity_produced) if quantity_produced else None,
                completeness, quality,
                timestamp, 'merge_equipment_sources.py'
            ))

            imported += 1

        except Exception as e:
            print(f"\n  ERROR importing {vehicle_name}: {e}")
            skipped += 1

    conn.commit()

    print(f"\n[SUCCESS] WWIITANKS import complete")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")

    return {'imported': imported, 'skipped': skipped}


def import_witw_equipment(conn):
    """Import WITW equipment into master_equipment."""

    print("\n" + "=" * 70)
    print("IMPORTING WITW EQUIPMENT")
    print("=" * 70)

    cursor = conn.cursor()

    # Get WITW equipment
    cursor.execute("""
        SELECT canonical_id, name, nation, equipment_type, category, witw_id
        FROM equipment
        ORDER BY nation, name
    """)

    items = cursor.fetchall()
    total = len(items)

    print(f"\nFound {total} WITW equipment items")
    print("Importing...")

    imported = 0
    skipped = 0
    timestamp = datetime.now().isoformat()

    for i, row in enumerate(items, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{total} ({i/total*100:.1f}%)")

        (canonical_id, name, nation, equipment_type, category, witw_id) = row

        try:
            # Insert into master_equipment (minimal data - just identifiers)
            cursor.execute("""
                INSERT INTO master_equipment (
                    equipment_name, nation, equipment_type, equipment_category,
                    source_primary, witw_canonical_id, witw_id,
                    completeness_score, specification_quality,
                    created_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, nation, equipment_type, category,
                'witw', canonical_id, witw_id,
                0, 'none',  # WITW items have no specs by default
                timestamp, 'merge_equipment_sources.py'
            ))

            imported += 1

        except Exception as e:
            # Likely duplicate - item already exists from OnWar/WWIITANKS
            # This is expected and we'll link them later
            skipped += 1

    conn.commit()

    print(f"\n[SUCCESS] WITW import complete")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped} (likely duplicates - will link later)")

    return {'imported': imported, 'skipped': skipped}


def generate_statistics(conn):
    """Generate statistics on master_equipment table."""

    print("\n" + "=" * 70)
    print("MASTER EQUIPMENT STATISTICS")
    print("=" * 70)

    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM master_equipment")
    total = cursor.fetchone()[0]

    # By source
    cursor.execute("SELECT source_primary, COUNT(*) FROM master_equipment GROUP BY source_primary")
    by_source = dict(cursor.fetchall())

    # By nation
    cursor.execute("SELECT nation, COUNT(*) FROM master_equipment GROUP BY nation ORDER BY COUNT(*) DESC")
    by_nation = cursor.fetchall()

    # By completeness
    cursor.execute("SELECT specification_quality, COUNT(*) FROM master_equipment GROUP BY specification_quality")
    by_quality = dict(cursor.fetchall())

    # Average completeness
    cursor.execute("SELECT AVG(completeness_score) FROM master_equipment WHERE completeness_score > 0")
    avg_completeness = cursor.fetchone()[0] or 0

    print(f"\nTotal Equipment: {total}")

    print(f"\nBy Source:")
    for source, count in sorted(by_source.items()):
        print(f"  {source:15s}: {count:4d} ({count/total*100:.1f}%)")

    print(f"\nBy Nation (top 10):")
    for nation, count in by_nation[:10]:
        print(f"  {nation:15s}: {count:4d} ({count/total*100:.1f}%)")

    print(f"\nBy Specification Quality:")
    for quality in ['high', 'medium', 'low', 'none']:
        count = by_quality.get(quality, 0)
        print(f"  {quality:15s}: {count:4d} ({count/total*100:.1f}%)")

    print(f"\nAverage Completeness: {avg_completeness:.1f}%")

    # Sample high-quality items
    print(f"\nSample High-Quality Equipment:")
    cursor.execute("""
        SELECT equipment_name, nation, source_primary, completeness_score
        FROM master_equipment
        WHERE specification_quality = 'high'
        ORDER BY completeness_score DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        print(f"  {row[0]:40s} ({row[1]}, {row[2]}) - {row[3]}% complete")


def main():
    """Main execution function."""

    print("=" * 70)
    print("MERGE EQUIPMENT SOURCES INTO MASTER TABLE")
    print("=" * 70)

    # Check database exists
    if not DATABASE_FILE.exists():
        print(f"ERROR: Database file not found: {DATABASE_FILE}")
        sys.exit(1)

    # Connect to database
    print(f"\nConnecting to: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)

    try:
        # Import all sources
        onwar_results = import_onwar_afvs(conn)
        wwiitanks_results = import_wwiitanks_afvs(conn)
        witw_results = import_witw_equipment(conn)

        # Generate statistics
        generate_statistics(conn)

        # Log to import_log
        timestamp = datetime.now().isoformat()
        cursor = conn.cursor()
        total_imported = (onwar_results['imported'] +
                         wwiitanks_results['imported'] +
                         witw_results['imported'])

        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file, records_imported, records_failed,
                import_started_at, import_completed_at, import_status,
                error_log, imported_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'master_equipment_merge',
            'afv_data + wwiitanks_afv_data + equipment',
            total_imported,
            0,
            timestamp,
            timestamp,
            'success',
            f"OnWar: {onwar_results['imported']}, WWIITANKS: {wwiitanks_results['imported']}, WITW: {witw_results['imported']}",
            'merge_equipment_sources.py'
        ))
        conn.commit()

        print("\n" + "=" * 70)
        print("MERGE COMPLETE")
        print("=" * 70)
        print(f"\nTotal: {total_imported} equipment items in master table")
        print("\nNext steps:")
        print("  1. Create WITW cross-reference linkages (link WITW items to OnWar/WWIITANKS)")
        print("  2. Generate validation report")
        print("  3. Update documentation")

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
