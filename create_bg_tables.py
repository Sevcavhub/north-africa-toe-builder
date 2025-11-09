#!/usr/bin/env python3
import sqlite3
import time

# Wait a moment for any locks to clear
time.sleep(2)

conn = sqlite3.connect('database/master_database.db', timeout=60)
cursor = conn.cursor()

print("Creating bg_builder_vehicles table...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS bg_builder_vehicles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    movement_off_road INTEGER,
    movement_road INTEGER,
    armor_front TEXT,
    armor_side TEXT,
    armor_rear TEXT,
    weapon_1_id INTEGER,
    weapon_2_id INTEGER,
    weapon_3_id INTEGER,
    weapon_4_id INTEGER,
    has_mg BOOLEAN,
    has_ammo BOOLEAN,
    special_rules TEXT,
    hits INTEGER,
    capacity INTEGER,
    movement_special TEXT,
    restricted TEXT,
    unique_flag BOOLEAN,
    import_date TEXT DEFAULT CURRENT_TIMESTAMP,
    import_source TEXT DEFAULT 'bg_builder'
)
''')
print("Created bg_builder_vehicles")

print("Creating bg_builder_weapons table...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS bg_builder_weapons (
    weapon_id INTEGER PRIMARY KEY,
    weapon_name TEXT NOT NULL,
    he_type TEXT,
    he_effect TEXT,
    he_strength_0 INTEGER,
    he_strength_10 INTEGER,
    he_strength_20 INTEGER,
    he_strength_30 INTEGER,
    he_strength_40 INTEGER,
    he_strength_50 INTEGER,
    ap_effect TEXT,
    ap_strength_0 INTEGER,
    ap_strength_10 INTEGER,
    ap_strength_20 INTEGER,
    ap_strength_30 INTEGER,
    ap_strength_40 INTEGER,
    ap_strength_50 INTEGER,
    import_date TEXT DEFAULT CURRENT_TIMESTAMP,
    import_source TEXT DEFAULT 'bg_builder'
)
''')
print("Created bg_builder_weapons")

print("Creating bg_builder_forces table...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS bg_builder_forces (
    force_id INTEGER PRIMARY KEY,
    force_group TEXT NOT NULL,
    force_name TEXT NOT NULL,
    infantry_tiers TEXT,
    sections TEXT,
    import_date TEXT DEFAULT CURRENT_TIMESTAMP,
    import_source TEXT DEFAULT 'bg_builder'
)
''')
print("Created bg_builder_forces")

print("Creating bg_builder_vehicle_costs table...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS bg_builder_vehicle_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    force_id INTEGER NOT NULL,
    role TEXT,
    points_base INTEGER,
    points_regular INTEGER,
    points_veteran INTEGER,
    battle_rating INTEGER,
    unique_in_force BOOLEAN,
    officer_vehicle BOOLEAN,
    FOREIGN KEY (vehicle_id) REFERENCES bg_builder_vehicles(id),
    FOREIGN KEY (force_id) REFERENCES bg_builder_forces(force_id)
)
''')
print("Created bg_builder_vehicle_costs")

print("Creating indexes...")
cursor.execute('CREATE INDEX IF NOT EXISTS idx_bg_builder_vehicles_name ON bg_builder_vehicles(name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_bg_builder_weapons_name ON bg_builder_weapons(weapon_name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_bg_builder_forces_group ON bg_builder_forces(force_group)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_bg_builder_costs_vehicle ON bg_builder_vehicle_costs(vehicle_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_bg_builder_costs_force ON bg_builder_vehicle_costs(force_id)')
print("Created indexes")

conn.commit()
conn.close()

print("\nAll tables created successfully!")
