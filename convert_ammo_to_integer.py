#!/usr/bin/env python3
"""
Convert ammo_1, ammo_2, ammo_3, ammo_4 columns to INTEGER in bg_reference_vehicles
SQLite requires recreating the table to change column types
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "master_database.db"

conn = sqlite3.connect(DB_PATH, timeout=60)
cursor = conn.cursor()

print("=" * 80)
print("CONVERTING AMMO COLUMNS TO INTEGER")
print("=" * 80)

# Step 1: Check current data
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE ammo_1 IS NOT NULL OR ammo_2 IS NOT NULL OR ammo_3 IS NOT NULL OR ammo_4 IS NOT NULL")
ammo_count = cursor.fetchone()[0]
print(f"\n{ammo_count} vehicles have ammo data")

# Step 2: Create new table with INTEGER ammo columns
print("\nCreating new table structure...")
cursor.execute("""
    CREATE TABLE bg_reference_vehicles_new (
        id INTEGER PRIMARY KEY,
        name TEXT,
        off_road_inches INTEGER,
        road_inches INTEGER,
        special_movement TEXT,
        armor_front TEXT,
        armor_side TEXT,
        armor_rear TEXT,
        weapon_1 TEXT,
        weapon_2 TEXT,
        weapon_3 TEXT,
        weapon_4 TEXT,
        mount_1 TEXT,
        mount_2 TEXT,
        mount_3 TEXT,
        mount_4 TEXT,
        ammo_1 INTEGER,
        ammo_2 INTEGER,
        ammo_3 INTEGER,
        ammo_4 INTEGER,
        armor_modifier TEXT,
        armor_side_schurzen TEXT,
        ss_hits INTEGER,
        ss_transport_capacity INTEGER,
        ss_special TEXT,
        year_range TEXT,
        vehicle_type TEXT,
        nation TEXT,
        dc_meta TEXT,
        source_file TEXT,
        source_document TEXT,
        source_battle TEXT,
        extraction_method TEXT,
        screenshot_file TEXT,
        bg_builder_id INTEGER
    )
""")

# Step 3: Copy data with CAST for ammo columns
print("Copying data with integer conversion...")
cursor.execute("""
    INSERT INTO bg_reference_vehicles_new
    SELECT
        id, name, off_road_inches, road_inches, special_movement,
        armor_front, armor_side, armor_rear,
        weapon_1, weapon_2, weapon_3, weapon_4,
        mount_1, mount_2, mount_3, mount_4,
        CAST(ammo_1 AS INTEGER),
        CAST(ammo_2 AS INTEGER),
        CAST(ammo_3 AS INTEGER),
        CAST(ammo_4 AS INTEGER),
        armor_modifier, armor_side_schurzen,
        ss_hits, ss_transport_capacity, ss_special,
        year_range, vehicle_type, nation,
        dc_meta, source_file, source_document, source_battle,
        extraction_method, screenshot_file, bg_builder_id
    FROM bg_reference_vehicles
""")

# Step 4: Drop dependent views
print("Dropping dependent views...")
cursor.execute("DROP VIEW IF EXISTS v_vehicles_unified")

# Step 5: Drop old table and rename new
print("Replacing old table...")
cursor.execute("DROP TABLE bg_reference_vehicles")
cursor.execute("ALTER TABLE bg_reference_vehicles_new RENAME TO bg_reference_vehicles")

# Step 6: Recreate view
print("Recreating v_vehicles_unified view...")
cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_vehicles_unified AS
    SELECT * FROM bg_reference_vehicles
""")

conn.commit()

# Step 5: Verify
cursor.execute("PRAGMA table_info(bg_reference_vehicles)")
cols = cursor.fetchall()
ammo_cols = [c for c in cols if 'ammo' in c[1]]
print("\nNew ammo column types:")
for c in ammo_cols:
    print(f"  {c[1]}: {c[2]}")

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
total = cursor.fetchone()[0]
print(f"\nTotal vehicles: {total}")

cursor.execute("SELECT id, name, ammo_1, ammo_2 FROM bg_reference_vehicles WHERE ammo_1 IS NOT NULL LIMIT 5")
print("\nSample ammo values:")
for row in cursor.fetchall():
    print(f"  [{row[0]}] {row[1]}: ammo_1={row[2]} (type: {type(row[2]).__name__})")

conn.close()

print("\nConversion complete!")
