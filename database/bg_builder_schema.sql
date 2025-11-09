-- ============================================================================
-- BATTLEGROUP BUILDER IMPORT TABLES
-- Created: 2025-11-09
-- Source: https://osjones.github.io/BattlegroupBuilder/
-- Purpose: Official BattleGroup stats from 18 supplement books (601 vehicles, 241 weapons, 117 force lists)
-- ============================================================================

-- BG Builder Vehicles (601 entries)
CREATE TABLE IF NOT EXISTS bg_builder_vehicles (
    id INTEGER PRIMARY KEY,              -- Original BG Builder ID
    name TEXT NOT NULL,                  -- Vehicle name

    -- Movement (inches)
    movement_off_road INTEGER,           -- Off-road movement in inches
    movement_road INTEGER,               -- Road movement in inches

    -- Armor (A-O letter scale)
    armor_front TEXT,                    -- Front armor letter (A-O)
    armor_side TEXT,                     -- Side armor letter (A-O)
    armor_rear TEXT,                     -- Rear armor letter (A-O)

    -- Weapons (IDs cross-reference bg_builder_weapons)
    weapon_1_id INTEGER,                 -- Primary weapon ID
    weapon_2_id INTEGER,                 -- Secondary weapon ID
    weapon_3_id INTEGER,                 -- Additional weapon ID
    weapon_4_id INTEGER,                 -- Additional weapon ID

    -- Flags
    has_mg BOOLEAN,                      -- Has machine gun
    has_ammo BOOLEAN,                    -- Carries ammunition (boolean, not count)

    -- Special rules
    special_rules TEXT,                  -- Special rules string

    -- Soft-skinned vehicle fields
    hits INTEGER,                        -- Damage capacity
    capacity INTEGER,                    -- Transport capacity
    movement_special TEXT,               -- Movement type special rules

    -- Metadata
    restricted TEXT,                     -- Availability restrictions
    unique_flag BOOLEAN,                 -- One-per-army flag (renamed from 'unique' which is SQL keyword)

    -- Import provenance
    import_date TEXT DEFAULT CURRENT_TIMESTAMP,
    import_source TEXT DEFAULT 'bg_builder',

    FOREIGN KEY (weapon_1_id) REFERENCES bg_builder_weapons(weapon_id),
    FOREIGN KEY (weapon_2_id) REFERENCES bg_builder_weapons(weapon_id),
    FOREIGN KEY (weapon_3_id) REFERENCES bg_builder_weapons(weapon_id),
    FOREIGN KEY (weapon_4_id) REFERENCES bg_builder_weapons(weapon_id)
);

-- BG Builder Weapons (241 entries)
CREATE TABLE IF NOT EXISTS bg_builder_weapons (
    weapon_id INTEGER PRIMARY KEY,       -- Original BG Builder weapon ID
    weapon_name TEXT NOT NULL,           -- Weapon name (e.g., "50mmL42", "2 pdr")

    -- HE stats (if applicable)
    he_type TEXT,                        -- HE type: "HE", "HE [VL]", "HE [L]", "HE [M]", "HE [H]"
    he_effect TEXT,                      -- HE effect (e.g., "3/5+", "4/4+")
    he_strength_0 INTEGER,               -- HE strength at 0" range
    he_strength_10 INTEGER,              -- HE strength at 10" range
    he_strength_20 INTEGER,              -- HE strength at 20" range
    he_strength_30 INTEGER,              -- HE strength at 30" range
    he_strength_40 INTEGER,              -- HE strength at 40" range
    he_strength_50 INTEGER,              -- HE strength at 50" range

    -- AP stats (if applicable)
    ap_effect TEXT,                      -- AP effect (usually "-")
    ap_strength_0 INTEGER,               -- AP penetration at 0" range
    ap_strength_10 INTEGER,              -- AP penetration at 10" range
    ap_strength_20 INTEGER,              -- AP penetration at 20" range
    ap_strength_30 INTEGER,              -- AP penetration at 30" range
    ap_strength_40 INTEGER,              -- AP penetration at 40" range
    ap_strength_50 INTEGER,              -- AP penetration at 50" range

    -- Import provenance
    import_date TEXT DEFAULT CURRENT_TIMESTAMP,
    import_source TEXT DEFAULT 'bg_builder'
);

-- BG Builder Force Lists (117 entries)
CREATE TABLE IF NOT EXISTS bg_builder_forces (
    force_id INTEGER PRIMARY KEY,        -- Original BG Builder force ID
    force_group TEXT NOT NULL,           -- Book/supplement (e.g., "Battlegroup Kursk", "Battlegroup Tobruk")
    force_name TEXT NOT NULL,            -- Force name (e.g., "German Panzer Division", "British Armoured Brigade")

    -- Force composition (JSON structure)
    infantry_tiers TEXT,                 -- JSON: Infantry tier structure
    sections TEXT,                       -- JSON: Force sections with units

    -- Import provenance
    import_date TEXT DEFAULT CURRENT_TIMESTAMP,
    import_source TEXT DEFAULT 'bg_builder'
);

-- BG Builder Vehicle Costs (extracted from forces.js)
-- Links vehicles to their points/BR values in specific force contexts
CREATE TABLE IF NOT EXISTS bg_builder_vehicle_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,        -- BG Builder vehicle ID
    force_id INTEGER NOT NULL,          -- Force list ID
    role TEXT,                          -- Unit role (e.g., "Forward Headquarters", "Panzer Platoon")

    -- Cost data
    points_base INTEGER,                -- Base points cost
    points_regular INTEGER,             -- Regular points (if different)
    points_veteran INTEGER,             -- Veteran points (if different)
    battle_rating INTEGER,              -- Battle Rating (BR)

    -- Context
    unique_in_force BOOLEAN,            -- One-per-force restriction
    officer_vehicle BOOLEAN,            -- Command vehicle flag

    FOREIGN KEY (vehicle_id) REFERENCES bg_builder_vehicles(id),
    FOREIGN KEY (force_id) REFERENCES bg_builder_forces(force_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bg_builder_vehicles_name ON bg_builder_vehicles(name);
CREATE INDEX IF NOT EXISTS idx_bg_builder_weapons_name ON bg_builder_weapons(weapon_name);
CREATE INDEX IF NOT EXISTS idx_bg_builder_forces_group ON bg_builder_forces(force_group);
CREATE INDEX IF NOT EXISTS idx_bg_builder_costs_vehicle ON bg_builder_vehicle_costs(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_bg_builder_costs_force ON bg_builder_vehicle_costs(force_id);

-- ============================================================================
-- UNIFIED VIEW: Combines BG Builder (primary) + manual bg_reference_vehicles (supplementary)
-- ============================================================================

CREATE VIEW IF NOT EXISTS v_vehicles_unified AS
SELECT
    -- Primary ID from BG Builder
    bgb.id as bg_builder_id,
    bgb.name,

    -- Movement from BG Builder (PRIMARY)
    bgb.movement_off_road as off_road_inches,
    bgb.movement_road as road_inches,
    bgb.movement_special as special_movement,

    -- Armor from BG Builder (PRIMARY)
    bgb.armor_front,
    bgb.armor_side,
    bgb.armor_rear,

    -- Weapons from BG Builder (PRIMARY)
    w1.weapon_name as weapon_1,
    w2.weapon_name as weapon_2,
    w3.weapon_name as weapon_3,
    w4.weapon_name as weapon_4,

    -- Ammunition counts from MANUAL (if available)
    manual.ammo_1,
    manual.ammo_2,
    manual.ammo_3,
    manual.ammo_4,

    -- Weapon mounts from MANUAL (if available)
    manual.mount_1,
    manual.mount_2,
    manual.mount_3,
    manual.mount_4,

    -- Metadata from MANUAL (if available)
    COALESCE(manual.year_range, '') as year_range,
    COALESCE(manual.vehicle_type, '') as vehicle_type,
    COALESCE(manual.nation, '') as nation,

    -- Special rules from BG Builder (PRIMARY)
    bgb.special_rules,

    -- Armor modifiers from MANUAL (if available)
    manual.armor_modifier,
    manual.armor_side_schurzen,

    -- Soft-skin from BG Builder (PRIMARY)
    bgb.hits as ss_hits,
    bgb.capacity as ss_transport_capacity,

    -- Source provenance
    'bg_builder' as primary_source,
    CASE WHEN manual.id IS NOT NULL THEN 'merged' ELSE 'bg_builder_only' END as data_status,
    manual.id as manual_id

FROM bg_builder_vehicles bgb
LEFT JOIN bg_builder_weapons w1 ON bgb.weapon_1_id = w1.weapon_id
LEFT JOIN bg_builder_weapons w2 ON bgb.weapon_2_id = w2.weapon_id
LEFT JOIN bg_builder_weapons w3 ON bgb.weapon_3_id = w3.weapon_id
LEFT JOIN bg_builder_weapons w4 ON bgb.weapon_4_id = w4.weapon_id
LEFT JOIN bg_reference_vehicles manual ON bgb.id = manual.bg_builder_id;

-- ============================================================================
-- END OF BG BUILDER SCHEMA
-- ============================================================================
