#!/usr/bin/env python3
"""
Create Master Equipment Table
Merges WITW, OnWar, and WWIITANKS equipment into a single comprehensive master table.

Strategy:
1. Create master_equipment table with all specification fields
2. Import all OnWar AFVs (211 items)
3. Import all WWIITANKS AFVs (612 items)
4. Import WITW equipment (469 items)
5. Handle deduplication intelligently (prefer most complete data)
6. Track source provenance for each item
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DATABASE_FILE = Path("database/master_database.db")

# Master equipment table schema
CREATE_MASTER_EQUIPMENT_TABLE = """
CREATE TABLE IF NOT EXISTS master_equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identity
    equipment_name TEXT NOT NULL,
    nation TEXT NOT NULL,
    equipment_type TEXT,
    equipment_category TEXT,

    -- Source tracking
    source_primary TEXT NOT NULL,  -- 'onwar', 'wwiitanks', 'witw'
    source_secondary TEXT,          -- If item appears in multiple sources
    onwar_url TEXT,
    wwiitanks_id TEXT,
    witw_canonical_id TEXT,
    witw_id INTEGER,

    -- Production & History
    production_start TEXT,
    production_end TEXT,
    production_quantity TEXT,
    manufacturers TEXT,
    formal_designation TEXT,
    operational_date TEXT,

    -- Physical Characteristics
    weight_tonnes REAL,
    length_m REAL,
    width_m REAL,
    height_m REAL,
    crew INTEGER,
    ground_clearance_m REAL,

    -- Armor Values (hull)
    armor_hull_front_mm REAL,
    armor_hull_front_angle INTEGER,
    armor_hull_side_mm REAL,
    armor_hull_side_angle INTEGER,
    armor_hull_rear_mm REAL,
    armor_hull_rear_angle INTEGER,
    armor_hull_top_mm REAL,
    armor_hull_bottom_mm REAL,

    -- Armor Values (superstructure)
    armor_superstructure_front_mm REAL,
    armor_superstructure_side_mm REAL,
    armor_superstructure_rear_mm REAL,
    armor_superstructure_top_mm REAL,

    -- Armor Values (turret)
    armor_turret_front_mm REAL,
    armor_turret_front_angle INTEGER,
    armor_turret_side_mm REAL,
    armor_turret_rear_mm REAL,
    armor_turret_top_mm REAL,
    armor_mantlet_mm REAL,

    -- Armament
    primary_armament TEXT,
    primary_gun_caliber_mm INTEGER,
    secondary_armament TEXT,
    ammunition_carried TEXT,

    -- Engine & Performance
    engine_make TEXT,
    engine_model TEXT,
    engine_type TEXT,
    engine_hp INTEGER,
    power_weight_ratio REAL,
    fuel_type TEXT,
    fuel_capacity_l INTEGER,

    -- Mobility
    max_speed_kmh INTEGER,
    max_speed_road_kmh INTEGER,
    max_speed_offroad_kmh INTEGER,
    range_road_km INTEGER,
    range_offroad_km INTEGER,

    -- Mobility Characteristics
    gradient_capability_deg INTEGER,
    fording_depth_m REAL,
    trench_crossing_m REAL,
    vertical_obstacle_m REAL,
    turning_radius_m REAL,
    ground_pressure REAL,

    -- Equipment
    radio_equipment TEXT,
    traverse TEXT,
    elevation TEXT,

    -- Data Quality
    completeness_score INTEGER,  -- 0-100 based on filled fields
    specification_quality TEXT,   -- 'high', 'medium', 'low'

    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT,
    created_by TEXT DEFAULT 'create_master_equipment_table.py',
    notes TEXT,

    -- Constraints
    UNIQUE(equipment_name, nation, source_primary)
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_master_equipment_name ON master_equipment(equipment_name);",
    "CREATE INDEX IF NOT EXISTS idx_master_equipment_nation ON master_equipment(nation);",
    "CREATE INDEX IF NOT EXISTS idx_master_equipment_type ON master_equipment(equipment_type);",
    "CREATE INDEX IF NOT EXISTS idx_master_equipment_source ON master_equipment(source_primary);",
    "CREATE INDEX IF NOT EXISTS idx_master_equipment_witw_id ON master_equipment(witw_canonical_id);",
    "CREATE INDEX IF NOT EXISTS idx_master_equipment_completeness ON master_equipment(completeness_score);",
]


def create_master_table(conn):
    """Create master_equipment table."""

    print("\n" + "=" * 70)
    print("CREATING MASTER EQUIPMENT TABLE")
    print("=" * 70)

    cursor = conn.cursor()

    print("\nCreating master_equipment table...")
    cursor.execute(CREATE_MASTER_EQUIPMENT_TABLE)
    print("  [CREATED] master_equipment")

    print("\nCreating indexes...")
    for i, index_sql in enumerate(CREATE_INDEXES, 1):
        cursor.execute(index_sql)
        index_name = index_sql.split("INDEX IF NOT EXISTS ")[1].split(" ON")[0]
        print(f"  [{i}/{len(CREATE_INDEXES)}] {index_name}")

    conn.commit()
    print("\n[SUCCESS] Master equipment table created")


def verify_schema(conn):
    """Verify master_equipment table was created successfully."""

    print("\n" + "=" * 70)
    print("VERIFYING SCHEMA")
    print("=" * 70)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(master_equipment)")
    columns = cursor.fetchall()

    print(f"\nmaster_equipment: {len(columns)} columns")

    # Show column categories
    categories = {
        'Identity': ['id', 'equipment_name', 'nation', 'equipment_type', 'equipment_category'],
        'Source Tracking': ['source_primary', 'source_secondary', 'onwar_url', 'wwiitanks_id', 'witw_canonical_id', 'witw_id'],
        'Physical': ['weight_tonnes', 'length_m', 'width_m', 'height_m', 'crew'],
        'Armor': [c[1] for c in columns if 'armor' in c[1]],
        'Armament': [c[1] for c in columns if 'armament' in c[1] or 'gun' in c[1] or 'ammunition' in c[1]],
        'Performance': [c[1] for c in columns if 'speed' in c[1] or 'range' in c[1] or 'engine' in c[1]],
        'Metadata': ['created_at', 'updated_at', 'created_by', 'completeness_score', 'specification_quality']
    }

    for category, fields in categories.items():
        matching = [c for c in columns if c[1] in fields]
        print(f"\n{category} ({len(matching)} fields):")
        for col in matching[:5]:
            print(f"  - {col[1]:30s} {col[2]}")
        if len(matching) > 5:
            print(f"  ... and {len(matching) - 5} more fields")

    print("\n[SUCCESS] Schema verification complete")


def main():
    """Main execution function."""

    print("=" * 70)
    print("CREATE MASTER EQUIPMENT TABLE")
    print("=" * 70)

    # Check database exists
    if not DATABASE_FILE.exists():
        print(f"ERROR: Database file not found: {DATABASE_FILE}")
        sys.exit(1)

    # Connect to database
    print(f"\nConnecting to: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)

    try:
        # Check if table already exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='master_equipment'")
        if cursor.fetchone():
            print("\nWARNING: master_equipment table already exists")
            response = input("Drop and recreate? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                print("\nDropping existing master_equipment table...")
                cursor.execute("DROP TABLE master_equipment")
                conn.commit()
            else:
                print("\nKeeping existing table. Exiting.")
                return

        # Create master table
        create_master_table(conn)

        # Verify schema
        verify_schema(conn)

        # Log creation
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file, records_imported, records_failed,
                import_started_at, import_completed_at, import_status,
                error_log, imported_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'master_equipment_schema',
            'N/A',
            0,
            0,
            timestamp,
            timestamp,
            'success',
            'Created master_equipment table structure',
            'create_master_equipment_table.py'
        ))
        conn.commit()

        print("\n" + "=" * 70)
        print("TABLE CREATION COMPLETE")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run merge_equipment_sources.py to populate master table")
        print("  2. Create WITW cross-reference linkages")
        print("  3. Validate and generate reports")

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
