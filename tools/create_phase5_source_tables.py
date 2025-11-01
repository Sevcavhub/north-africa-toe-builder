#!/usr/bin/env python3
"""
Phase 5 Database Schema Creation
Creates source tables for OnWar and WWIITANKS data in master_database.db.

Creates:
- afv_data (OnWar AFV specifications)
- wwiitanks_afv_data (WWIITANKS AFV specifications)
- wwiitanks_gun_data (WWIITANKS gun specifications - if needed)
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DATABASE_FILE = Path("database/master_database.db")

# SQL for creating source tables
CREATE_AFV_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS afv_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identity
    country TEXT NOT NULL,
    vehicle_name TEXT NOT NULL,
    url TEXT,
    formal_designation TEXT,
    type TEXT,

    -- Crew & Production
    crew INTEGER,
    manufacturers TEXT,
    production_quantity TEXT,
    production_period TEXT,

    -- Physical Dimensions
    length_hull TEXT,
    width TEXT,
    height TEXT,
    combat_weight TEXT,
    ground_clearance TEXT,

    -- Armament
    radio TEXT,
    primary_armament TEXT,
    secondary_armament TEXT,
    ammunition_carried TEXT,
    traverse TEXT,
    elevation TEXT,

    -- Engine & Performance
    engine_make_model TEXT,
    engine_type_displacement TEXT,
    horsepower TEXT,
    power_weight_ratio TEXT,
    fuel_type TEXT,
    fuel_capacity TEXT,
    speed TEXT,
    range TEXT,
    gearbox TEXT,

    -- Mobility
    turning_radius TEXT,
    gradient TEXT,
    fording TEXT,
    vertical_obstacle TEXT,
    trench_crossing TEXT,
    ground_pressure TEXT,
    track_width TEXT,
    track_ground_contact TEXT,

    -- Armor Values (hull)
    hull_front TEXT,
    hull_side TEXT,
    hull_rear TEXT,
    hull_top_bottom TEXT,

    -- Armor Values (superstructure)
    superstructure_front TEXT,
    superstructure_side TEXT,
    superstructure_rear TEXT,
    superstructure_top_bottom TEXT,

    -- Armor Values (turret)
    turret_front TEXT,
    turret_side TEXT,
    turret_rear TEXT,
    turret_top_bottom TEXT,
    mantlet TEXT,

    -- Metadata
    source TEXT DEFAULT 'onwar.com',
    scraped_date TEXT,
    imported_at TEXT NOT NULL,
    imported_by TEXT DEFAULT 'phase5_import',

    UNIQUE(vehicle_name, country)
);
"""

CREATE_WWIITANKS_AFV_TABLE = """
CREATE TABLE IF NOT EXISTS wwiitanks_afv_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identity
    wwiitanks_id TEXT UNIQUE NOT NULL,
    country TEXT NOT NULL,
    vehicle_name TEXT NOT NULL,
    full_name TEXT,

    -- Source metadata
    source TEXT DEFAULT 'wwiitanks.co.uk',
    source_url TEXT,
    scraped_at TEXT,
    scraper_version TEXT,

    -- Data indicators (booleans stored as integers: 0=false, 1=true)
    has_photo INTEGER DEFAULT 0,
    has_scale_illustration INTEGER DEFAULT 0,
    has_vehicle_history INTEGER DEFAULT 0,
    has_weapon_details INTEGER DEFAULT 0,
    has_armour_details INTEGER DEFAULT 0,

    -- Raw extracted data (stored as JSON text for complex structures)
    general_details TEXT,
    specifications TEXT,
    armour_details TEXT,
    weapon_details TEXT,
    vehicle_history TEXT,

    -- Parsed fields (populated during Phase 3)
    operational_date TEXT,
    quantity_produced INTEGER,
    weight_tonnes REAL,
    crew INTEGER,

    -- Parsed armor (populated during Phase 3)
    armor_hull_front_mm REAL,
    armor_hull_side_mm REAL,
    armor_hull_rear_mm REAL,
    armor_turret_front_mm REAL,
    armor_turret_side_mm REAL,
    armor_turret_rear_mm REAL,

    -- Parsed mobility (populated during Phase 3)
    speed_kmh REAL,
    range_km REAL,

    -- Parsed weapons (populated during Phase 3)
    main_gun_caliber_mm INTEGER,
    main_gun_name TEXT,

    -- Import metadata
    imported_at TEXT NOT NULL,
    imported_by TEXT DEFAULT 'phase5_import',
    parsed_at TEXT,

    UNIQUE(wwiitanks_id)
);
"""

CREATE_WWIITANKS_GUN_TABLE = """
CREATE TABLE IF NOT EXISTS wwiitanks_gun_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identity
    wwiitanks_id TEXT UNIQUE NOT NULL,
    country TEXT NOT NULL,
    gun_name TEXT NOT NULL,
    full_name TEXT,

    -- Source metadata
    source TEXT DEFAULT 'wwiitanks.co.uk',
    source_url TEXT,
    scraped_at TEXT,
    scraper_version TEXT,

    -- Basic specifications (as scraped)
    manufactured TEXT,
    calibre TEXT,
    length TEXT,
    rate_of_fire TEXT,

    -- Ammunition data (stored as JSON text)
    ammunition TEXT,

    -- Vehicles using this gun (stored as JSON text)
    vehicles_using_gun TEXT,

    -- Parsed fields (populated during Phase 3)
    caliber_mm INTEGER,
    manufactured_start INTEGER,
    manufactured_end INTEGER,
    barrel_length_calibers REAL,

    -- Import metadata
    imported_at TEXT NOT NULL,
    imported_by TEXT DEFAULT 'phase5_import',
    parsed_at TEXT,

    UNIQUE(wwiitanks_id)
);
"""

# Indexes for efficient querying
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_afv_data_country ON afv_data(country);",
    "CREATE INDEX IF NOT EXISTS idx_afv_data_vehicle_name ON afv_data(vehicle_name);",
    "CREATE INDEX IF NOT EXISTS idx_afv_data_type ON afv_data(type);",

    "CREATE INDEX IF NOT EXISTS idx_wwiitanks_afv_country ON wwiitanks_afv_data(country);",
    "CREATE INDEX IF NOT EXISTS idx_wwiitanks_afv_vehicle_name ON wwiitanks_afv_data(vehicle_name);",
    "CREATE INDEX IF NOT EXISTS idx_wwiitanks_afv_has_armour ON wwiitanks_afv_data(has_armour_details);",

    "CREATE INDEX IF NOT EXISTS idx_wwiitanks_gun_country ON wwiitanks_gun_data(country);",
    "CREATE INDEX IF NOT EXISTS idx_wwiitanks_gun_name ON wwiitanks_gun_data(gun_name);",
    "CREATE INDEX IF NOT EXISTS idx_wwiitanks_gun_caliber ON wwiitanks_gun_data(caliber_mm);",
]


def check_database_exists():
    """Check if database file exists."""
    if not DATABASE_FILE.exists():
        print(f"ERROR: Database file not found: {DATABASE_FILE}")
        print("Expected location: database/master_database.db")
        sys.exit(1)


def check_existing_tables(conn):
    """Check which source tables already exist."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('afv_data', 'wwiitanks_afv_data', 'wwiitanks_gun_data')")
    existing = [row[0] for row in cursor.fetchall()]
    return existing


def create_tables(conn):
    """Create source tables in database."""
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("Creating source tables...")
    print("=" * 70)

    # Create afv_data table
    print("\n1. Creating afv_data table (OnWar AFV specifications)...")
    cursor.execute(CREATE_AFV_DATA_TABLE)
    print("   [CREATED] afv_data")

    # Create wwiitanks_afv_data table
    print("\n2. Creating wwiitanks_afv_data table (WWIITANKS AFV specifications)...")
    cursor.execute(CREATE_WWIITANKS_AFV_TABLE)
    print("   [CREATED] wwiitanks_afv_data")

    # Create wwiitanks_gun_data table
    print("\n3. Creating wwiitanks_gun_data table (WWIITANKS gun specifications)...")
    cursor.execute(CREATE_WWIITANKS_GUN_TABLE)
    print("   [CREATED] wwiitanks_gun_data")

    # Create indexes
    print("\n4. Creating indexes for efficient querying...")
    for i, index_sql in enumerate(CREATE_INDEXES, 1):
        cursor.execute(index_sql)
        index_name = index_sql.split("INDEX IF NOT EXISTS ")[1].split(" ON")[0]
        print(f"   [{i}/{len(CREATE_INDEXES)}] {index_name}")

    conn.commit()
    print("\n[SUCCESS] All tables and indexes created")


def verify_schema(conn):
    """Verify tables were created successfully."""
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("Verifying schema...")
    print("=" * 70)

    tables_to_check = ['afv_data', 'wwiitanks_afv_data', 'wwiitanks_gun_data']

    for table in tables_to_check:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"\n{table}: {len(columns)} columns")

        # Show first few columns
        for col in columns[:5]:
            print(f"  - {col[1]:30s} {col[2]}")
        if len(columns) > 5:
            print(f"  ... and {len(columns) - 5} more columns")

    print("\n[SUCCESS] Schema verification complete")


def log_import_metadata(conn):
    """Log schema creation in import_log table."""
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()

    for table in ['afv_data', 'wwiitanks_afv_data', 'wwiitanks_gun_data']:
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file, records_imported, records_failed,
                import_started_at, import_completed_at, import_status,
                error_log, imported_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            table,
            'N/A',
            0,
            0,
            timestamp,
            timestamp,
            'schema_created',
            f'Created {table} table structure',
            'create_phase5_source_tables.py'
        ))

    conn.commit()
    print("\n[SUCCESS] Import log updated")


def main():
    """Main execution function."""
    print("=" * 70)
    print("PHASE 5 DATABASE SCHEMA CREATION")
    print("=" * 70)

    # Check database exists
    check_database_exists()

    # Connect to database
    print(f"\nConnecting to: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)

    try:
        # Check existing tables
        existing = check_existing_tables(conn)
        if existing:
            print(f"\nWARNING: Found existing source tables: {', '.join(existing)}")
            print("These tables will NOT be dropped. Using CREATE IF NOT EXISTS.")

        # Create tables
        create_tables(conn)

        # Verify schema
        verify_schema(conn)

        # Log in import_log
        log_import_metadata(conn)

        print("\n" + "=" * 70)
        print("SCHEMA CREATION COMPLETE")
        print("=" * 70)
        print("\nNext step: Run import scripts (Phase 3)")
        print("  - tools/import_phase5_sources.py")

    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
