"""
Phase A2: Add Explicit Columns to equipment_master_new

Adds ~32 key specification columns from equipment table structure.
Populates from historical_specs_json where available.
Keeps JSON as backup for flexibility.
"""

import sqlite3
import json
from typing import Dict, Any, Optional


# Define columns to add (from equipment table)
COLUMNS_TO_ADD = [
    # Production data
    ('production_start', 'TEXT'),
    ('production_end', 'TEXT'),
    ('production_quantity', 'INTEGER'),
    ('manufacturers', 'TEXT'),
    ('formal_designation', 'TEXT'),

    # Armor specifications
    ('armor_front_mm', 'INTEGER'),
    ('armor_front_angle', 'INTEGER'),
    ('armor_front_effective_mm', 'INTEGER'),
    ('armor_side_mm', 'INTEGER'),
    ('armor_side_angle', 'INTEGER'),
    ('armor_rear_mm', 'INTEGER'),
    ('armor_rear_angle', 'INTEGER'),
    ('armor_top_mm', 'INTEGER'),
    ('armor_bottom_mm', 'INTEGER'),

    # Physical dimensions
    ('weight_tonnes', 'REAL'),
    ('length_m', 'REAL'),
    ('width_m', 'REAL'),
    ('height_m', 'REAL'),
    ('ground_clearance_m', 'REAL'),
    ('power_weight_ratio', 'REAL'),

    # Crew
    ('crew', 'INTEGER'),

    # Performance
    ('max_speed_kmh', 'INTEGER'),
    ('max_speed_road_kmh', 'INTEGER'),
    ('max_speed_offroad_kmh', 'INTEGER'),
    ('range_road_km', 'INTEGER'),
    ('range_offroad_km', 'INTEGER'),
    ('fuel_type', 'TEXT'),
    ('fuel_capacity_l', 'INTEGER'),
    ('engine_make', 'TEXT'),
    ('engine_model', 'TEXT'),
    ('engine_hp', 'INTEGER'),
    ('gradient_capability_deg', 'INTEGER'),
    ('trench_crossing_m', 'REAL'),
]


def check_existing_columns(conn: sqlite3.Connection) -> set:
    """Get set of existing column names in equipment_master_new."""
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(equipment_master_new)')
    return {col[1] for col in cursor.fetchall()}


def add_columns(conn: sqlite3.Connection, dry_run: bool = True):
    """Add new columns to equipment_master_new table."""
    cursor = conn.cursor()

    existing = check_existing_columns(conn)
    to_add = [(name, type_) for name, type_ in COLUMNS_TO_ADD if name not in existing]

    if not to_add:
        print("[OK] All columns already exist - no changes needed")
        return 0

    print(f"Adding {len(to_add)} new columns to equipment_master_new:")
    print()

    for col_name, col_type in to_add:
        print(f"  + {col_name:35} {col_type}")

        if not dry_run:
            try:
                cursor.execute(f"ALTER TABLE equipment_master_new ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"    [ERROR] {e}")

    if not dry_run:
        conn.commit()
        print()
        print(f"[OK] Added {len(to_add)} columns")

    return len(to_add)


def populate_from_json(conn: sqlite3.Connection, dry_run: bool = True):
    """
    Populate new columns from historical_specs_json.

    Parses JSON and extracts values for each column.
    """
    cursor = conn.cursor()

    print()
    print("=" * 100)
    print("POPULATING COLUMNS FROM historical_specs_json")
    print("=" * 100)
    print()

    # Get all records with historical_specs_json
    cursor.execute("""
        SELECT master_id, canonical_name, display_name, historical_specs_json
        FROM equipment_master_new
        WHERE historical_specs_json IS NOT NULL
        ORDER BY master_id
    """)

    records = cursor.fetchall()
    print(f"Records with historical_specs_json: {len(records)}")
    print()

    updates = []
    errors = []

    for master_id, canonical_name, display_name, specs_json in records:
        try:
            specs = json.loads(specs_json)
            if not isinstance(specs, dict):
                continue

            # Extract values for each column
            values = {}
            for col_name, col_type in COLUMNS_TO_ADD:
                if col_name in specs:
                    value = specs[col_name]

                    # Type conversion
                    if value in (None, '', 'null', 'NULL'):
                        value = None
                    elif col_type == 'INTEGER' and value is not None:
                        try:
                            value = int(float(value))  # Handle "12.0" strings
                        except:
                            value = None
                    elif col_type == 'REAL' and value is not None:
                        try:
                            value = float(value)
                        except:
                            value = None

                    values[col_name] = value

            if values:
                updates.append((master_id, values))

        except json.JSONDecodeError as e:
            errors.append((master_id, display_name, str(e)))

    print(f"Records to update: {len(updates)}")
    print(f"JSON parse errors: {len(errors)}")
    print()

    if errors:
        print("Sample JSON errors (first 5):")
        for master_id, display_name, error in errors[:5]:
            print(f"  master_id={master_id} ({display_name}): {error}")
        print()

    # Show sample updates
    if updates:
        print("Sample updates (first 3 records):")
        for master_id, values in updates[:3]:
            print(f"  master_id={master_id}:")
            for col_name, value in list(values.items())[:10]:
                print(f"    {col_name:30} = {value}")
            if len(values) > 10:
                print(f"    ... and {len(values) - 10} more fields")
            print()

    # Apply updates
    if not dry_run:
        print("Applying updates...")
        updated_count = 0

        for master_id, values in updates:
            if not values:
                continue

            # Build UPDATE statement
            set_clauses = [f"{col_name} = ?" for col_name in values.keys()]
            sql = f"""
                UPDATE equipment_master_new
                SET {', '.join(set_clauses)}
                WHERE master_id = ?
            """

            params = list(values.values()) + [master_id]
            cursor.execute(sql, params)
            updated_count += 1

        conn.commit()
        print(f"[OK] Updated {updated_count} records")
        print()

        # Verify population
        print("Verification:")
        for col_name, col_type in COLUMNS_TO_ADD[:5]:  # Check first 5 columns
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM equipment_master_new
                WHERE {col_name} IS NOT NULL
            """)
            count = cursor.fetchone()[0]
            pct = 100 * count / len(records) if records else 0
            print(f"  {col_name:35} : {count:4} / {len(records)} ({pct:.1f}%)")
        print()

    return len(updates)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Add explicit columns to equipment_master_new")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')
    parser.add_argument('--execute', action='store_true', help='Apply changes (default: dry run)')

    args = parser.parse_args()

    conn = sqlite3.connect(args.db)

    print("=" * 100)
    print("PHASE A2: ADD EXPLICIT COLUMNS TO EQUIPMENT_MASTER_NEW")
    print("=" * 100)
    print()

    # Step 1: Add columns
    columns_added = add_columns(conn, dry_run=not args.execute)

    # Step 2: Populate from JSON
    if columns_added > 0 or not args.execute:  # Always show population plan in dry-run
        records_updated = populate_from_json(conn, dry_run=not args.execute)

    if not args.execute:
        print()
        print("DRY RUN - No changes applied. Run with --execute to apply changes.")
        print()
    else:
        print()
        print("[OK] Phase A2 complete - explicit columns added and populated")
        print()

    conn.close()


if __name__ == '__main__':
    main()
