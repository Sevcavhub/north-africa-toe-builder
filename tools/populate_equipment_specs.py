#!/usr/bin/env python3
"""
Phase 4: Populate Equipment Specifications
Populates equipment table with specs from afv_data and wwiitanks_afv_data source tables.

Strategy:
1. For each equipment item (469 WITW baseline items)
2. Find matches in match_reviews table
3. Query source tables for specifications
4. Parse and normalize data (text → numeric)
5. Populate equipment table with hybrid data (WWIITANKS preferred, OnWar fallback)
"""

import sqlite3
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

DATABASE_FILE = Path("database/master_database.db")


def parse_numeric_value(text, default=None) -> Optional[float]:
    """Extract first numeric value from text string or return numeric value if already a number.

    Examples:
        "29-34mm @30°" → 29.0 (first value in range)
        "10 km/h max." → 10.0
        "n.a." → None
        "7000" → 7000.0
        7000 → 7000.0 (already a number)
    """
    # Handle already-numeric values
    if isinstance(text, (int, float)):
        return float(text)

    # Handle None
    if text is None:
        return default

    # Handle strings
    if isinstance(text, str):
        if text.strip().lower() in ['', 'n.a.', 'n/a', 'unknown', '?', '-', 'none']:
            return default

        # Try to find first number (integer or decimal)
        match = re.search(r'(\d+\.?\d*)', text.strip())
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return default

    return default


def parse_range_average(text, default=None) -> Optional[float]:
    """Extract average of numeric range from text or return numeric value if already a number.

    Examples:
        "29-34mm @30°" → 31.5 (average of 29 and 34)
        "10-15 km" → 12.5
        "7000" → 7000.0 (single value)
        7000 → 7000.0 (already a number)
    """
    # Handle already-numeric values
    if isinstance(text, (int, float)):
        return float(text)

    # Handle None
    if text is None:
        return default

    # Handle strings
    if isinstance(text, str):
        if text.strip().lower() in ['', 'n.a.', 'n/a', 'unknown', '?', '-', 'none']:
            return default

        # Try to find range "X-Y"
        match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', text.strip())
        if match:
            try:
                val1 = float(match.group(1))
                val2 = float(match.group(2))
                return (val1 + val2) / 2
            except ValueError:
                pass

    # Fallback to single value
    return parse_numeric_value(text, default)


def get_onwar_specs(conn, canonical_id: str) -> Optional[Dict]:
    """Query OnWar afv_data for equipment specifications."""
    cursor = conn.cursor()

    # Find OnWar match from equipment table
    cursor.execute("""
        SELECT onwar_url
        FROM equipment
        WHERE canonical_id = ? AND onwar_matched = 1
        LIMIT 1
    """, (canonical_id,))

    match = cursor.fetchone()
    if not match or not match[0]:
        return None

    onwar_url = match[0]

    # Query afv_data by URL
    cursor.execute("""
        SELECT country, vehicle_name, type, crew, combat_weight,
               hull_front, hull_side, hull_rear,
               turret_front, turret_side, turret_rear,
               speed, range, primary_armament
        FROM afv_data
        WHERE url = ?
        LIMIT 1
    """, (onwar_url,))

    row = cursor.fetchone()
    if not row:
        return None

    return {
        'source': 'onwar',
        'country': row[0],
        'vehicle_name': row[1],
        'type': row[2],
        'crew': parse_numeric_value(row[3]),
        'weight_tonnes': parse_numeric_value(row[4]),
        'armor_hull_front_mm': parse_range_average(row[5]),
        'armor_hull_side_mm': parse_range_average(row[6]),
        'armor_hull_rear_mm': parse_range_average(row[7]),
        'armor_turret_front_mm': parse_range_average(row[8]),
        'armor_turret_side_mm': parse_range_average(row[9]),
        'armor_turret_rear_mm': parse_range_average(row[10]),
        'max_speed_kmh': parse_numeric_value(row[11]),
        'range_road_km': parse_numeric_value(row[12]),
        'primary_armament': row[13]
    }


def get_wwiitanks_specs(conn, canonical_id: str) -> Optional[Dict]:
    """Query WWIITANKS wwiitanks_afv_data for equipment specifications."""
    cursor = conn.cursor()

    # Find WWIITANKS match from equipment table
    cursor.execute("""
        SELECT wwiitanks_id
        FROM equipment
        WHERE canonical_id = ? AND wwiitanks_matched = 1
        LIMIT 1
    """, (canonical_id,))

    match = cursor.fetchone()
    if not match or not match[0]:
        return None

    wwiitanks_id = match[0]

    # Query wwiitanks_afv_data by ID
    # Note: WWIITANKS data is stored as raw JSON in text fields
    # For now, we can only return basic info since parsing isn't implemented yet
    cursor.execute("""
        SELECT country, vehicle_name, weight_tonnes, crew,
               armor_hull_front_mm, armor_hull_side_mm, armor_hull_rear_mm,
               armor_turret_front_mm, armor_turret_side_mm, armor_turret_rear_mm,
               speed_kmh, range_km
        FROM wwiitanks_afv_data
        WHERE wwiitanks_id = ?
        LIMIT 1
    """, (wwiitanks_id,))

    row = cursor.fetchone()
    if not row:
        return None

    return {
        'source': 'wwiitanks',
        'country': row[0],
        'vehicle_name': row[1],
        'weight_tonnes': row[2],
        'crew': row[3],
        'armor_hull_front_mm': row[4],
        'armor_hull_side_mm': row[5],
        'armor_hull_rear_mm': row[6],
        'armor_turret_front_mm': row[7],
        'armor_turret_side_mm': row[8],
        'armor_turret_rear_mm': row[9],
        'speed_kmh': row[10],
        'range_km': row[11]
    }


def merge_specs(onwar_specs: Optional[Dict], wwiitanks_specs: Optional[Dict]) -> Dict:
    """Merge specifications from both sources (WWIITANKS preferred, OnWar fallback)."""

    merged = {
        'crew': None,
        'weight_tonnes': None,
        'armor_front_mm': None,
        'armor_side_mm': None,
        'armor_rear_mm': None,
        'turret_front_mm': None,
        'turret_side_mm': None,
        'turret_rear_mm': None,
        'max_speed_kmh': None,
        'range_road_km': None,
        'spec_source': 'none',
        'spec_confidence': 'none'
    }

    # If we have WWIITANKS data, use it (preferred)
    if wwiitanks_specs:
        merged.update({
            'crew': wwiitanks_specs.get('crew'),
            'weight_tonnes': wwiitanks_specs.get('weight_tonnes'),
            'armor_front_mm': wwiitanks_specs.get('armor_hull_front_mm'),
            'armor_side_mm': wwiitanks_specs.get('armor_hull_side_mm'),
            'armor_rear_mm': wwiitanks_specs.get('armor_hull_rear_mm'),
            'turret_front_mm': wwiitanks_specs.get('armor_turret_front_mm'),
            'turret_side_mm': wwiitanks_specs.get('armor_turret_side_mm'),
            'turret_rear_mm': wwiitanks_specs.get('armor_turret_rear_mm'),
            'max_speed_kmh': wwiitanks_specs.get('speed_kmh'),
            'range_road_km': wwiitanks_specs.get('range_km'),
            'spec_source': 'wwiitanks',
            'spec_confidence': 'high'
        })

    # Fill gaps with OnWar data
    if onwar_specs:
        for field in ['crew', 'weight_tonnes', 'armor_front_mm', 'armor_side_mm',
                      'armor_rear_mm', 'turret_front_mm', 'turret_side_mm',
                      'turret_rear_mm', 'max_speed_kmh', 'range_road_km']:

            if merged[field] is None:
                onwar_field = field
                if field.startswith('armor_'):
                    onwar_field = f'armor_hull_{field[6:]}' if 'turret' not in field else f'armor_{field[7:]}'

                merged[field] = onwar_specs.get(onwar_field)

                if merged['spec_source'] == 'none' and merged[field] is not None:
                    merged['spec_source'] = 'onwar'
                    merged['spec_confidence'] = 'medium'
                elif merged['spec_source'] == 'wwiitanks' and merged[field] is not None:
                    merged['spec_source'] = 'hybrid'
                    merged['spec_confidence'] = 'high'

    return merged


def populate_equipment_table(conn):
    """Populate equipment table specifications from source tables."""

    print("\n" + "=" * 70)
    print("POPULATING EQUIPMENT TABLE SPECIFICATIONS")
    print("=" * 70)

    cursor = conn.cursor()

    # Get all equipment items
    cursor.execute("SELECT canonical_id, name, nation FROM equipment ORDER BY nation, name")
    equipment_items = cursor.fetchall()

    total = len(equipment_items)
    print(f"\nFound {total} equipment items to process")

    populated = 0
    partial = 0
    failed = 0
    timestamp = datetime.now().isoformat()

    print("\nProcessing equipment items...")

    for i, (canonical_id, name, nation) in enumerate(equipment_items, 1):
        if i % 50 == 0 or i == total:
            print(f"  Progress: {i}/{total} ({i/total*100:.1f}%) - Populated: {populated}, Partial: {partial}, Failed: {failed}")

        try:
            # Get specifications from sources
            onwar_specs = get_onwar_specs(conn, canonical_id)
            wwiitanks_specs = get_wwiitanks_specs(conn, canonical_id)

            # Merge specifications
            merged = merge_specs(onwar_specs, wwiitanks_specs)

            # Count how many specs we got
            spec_count = sum(1 for v in [merged['crew'], merged['weight_tonnes'],
                                          merged['armor_front_mm'], merged['armor_side_mm'],
                                          merged['max_speed_kmh'], merged['range_road_km']] if v is not None)

            if spec_count == 0:
                failed += 1
                continue
            elif spec_count < 4:
                partial += 1
            else:
                populated += 1

            # Update equipment table
            cursor.execute("""
                UPDATE equipment SET
                    crew = ?,
                    weight_tonnes = ?,
                    armor_front_mm = ?,
                    armor_side_mm = ?,
                    armor_rear_mm = ?,
                    turret_front_mm = ?,
                    turret_side_mm = ?,
                    turret_rear_mm = ?,
                    max_speed_kmh = ?,
                    range_road_km = ?,
                    updated_at = ?,
                    updated_by = ?
                WHERE canonical_id = ?
            """, (
                int(merged['crew']) if merged['crew'] else None,
                merged['weight_tonnes'],
                int(merged['armor_front_mm']) if merged['armor_front_mm'] else None,
                int(merged['armor_side_mm']) if merged['armor_side_mm'] else None,
                int(merged['armor_rear_mm']) if merged['armor_rear_mm'] else None,
                int(merged['turret_front_mm']) if merged['turret_front_mm'] else None,
                int(merged['turret_side_mm']) if merged['turret_side_mm'] else None,
                int(merged['turret_rear_mm']) if merged['turret_rear_mm'] else None,
                int(merged['max_speed_kmh']) if merged['max_speed_kmh'] else None,
                int(merged['range_road_km']) if merged['range_road_km'] else None,
                timestamp,
                'populate_equipment_specs.py',
                canonical_id
            ))

        except Exception as e:
            print(f"\n  ERROR processing {name} ({nation}): {e}")
            failed += 1

    conn.commit()

    print(f"\n[SUCCESS] Equipment table population complete")
    print(f"  Fully populated: {populated} ({populated/total*100:.1f}%)")
    print(f"  Partially populated: {partial} ({partial/total*100:.1f}%)")
    print(f"  No specs found: {failed} ({failed/total*100:.1f}%)")

    return {"populated": populated, "partial": partial, "failed": failed, "total": total}


def generate_statistics(conn):
    """Generate statistics on equipment table population."""

    print("\n" + "=" * 70)
    print("EQUIPMENT TABLE STATISTICS")
    print("=" * 70)

    cursor = conn.cursor()

    # Count non-null values for critical fields
    fields = ['crew', 'weight_tonnes', 'armor_front_mm', 'armor_side_mm',
              'turret_front_mm', 'max_speed_kmh', 'range_road_km']

    print("\nField Population Rates:")
    for field in fields:
        cursor.execute(f"SELECT COUNT(*) FROM equipment WHERE {field} IS NOT NULL")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM equipment")
        total = cursor.fetchone()[0]
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {field:25s}: {pct:5.1f}% ({count}/{total})")

    # Sample data
    print("\nSample Populated Equipment:")
    cursor.execute("""
        SELECT name, nation, armor_front_mm, max_speed_kmh, crew
        FROM equipment
        WHERE armor_front_mm IS NOT NULL
        LIMIT 5
    """)

    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]}): armor={row[2]}mm, speed={row[3]}km/h, crew={row[4]}")


def main():
    """Main execution function."""

    print("=" * 70)
    print("PHASE 4: EQUIPMENT SPECIFICATION POPULATION")
    print("=" * 70)

    # Check database exists
    if not DATABASE_FILE.exists():
        print(f"ERROR: Database file not found: {DATABASE_FILE}")
        sys.exit(1)

    # Connect to database
    print(f"\nConnecting to: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)

    try:
        # Populate equipment table
        results = populate_equipment_table(conn)

        # Generate statistics
        generate_statistics(conn)

        # Log to import_log
        timestamp = datetime.now().isoformat()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file, records_imported, records_failed,
                import_started_at, import_completed_at, import_status,
                error_log, imported_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'equipment_specs_population',
            'afv_data + wwiitanks_afv_data',
            results['populated'] + results['partial'],
            results['failed'],
            timestamp,
            timestamp,
            'success',
            f"Populated: {results['populated']}, Partial: {results['partial']}, Failed: {results['failed']}",
            'populate_equipment_specs.py'
        ))
        conn.commit()

        print("\n" + "=" * 70)
        print("PHASE 4 COMPLETE")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Parse WWIITANKS raw data for additional specs (future enhancement)")
        print("  2. Create equipment-gun linkages (Phase 5)")
        print("  3. Validate and test (Phase 6)")

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
