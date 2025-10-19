-- North Africa TO&E Master Database Schema
-- Version: 1.0.0
-- Created: 2025-10-18
-- Purpose: Unified equipment, guns, ammunition, and unit data for TO&E research

-- ============================================================================
-- EQUIPMENT MASTER TABLE
-- Baseline: WITW canonical equipment enhanced with OnWar + WWII Tanks UK data
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment (
    canonical_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    nation TEXT NOT NULL,
    equipment_type TEXT, -- tank, armored_car, halftrack, truck, gun, artillery
    category TEXT, -- tanks, halftracks, field_artillery, anti_tank_guns, etc.

    -- WITW integration for scenario export
    witw_id INTEGER,
    witw_name TEXT,
    witw_confidence INTEGER,

    -- Source provenance tracking
    onwar_matched INTEGER DEFAULT 0, -- Boolean: 1 if matched with OnWar data
    onwar_url TEXT,
    wwiitanks_matched INTEGER DEFAULT 0, -- Boolean: 1 if matched with WWII Tanks UK
    wwiitanks_id TEXT,
    match_confidence INTEGER, -- 0-100 confidence score of match
    match_method TEXT, -- exact, caliber_type, variant, manual

    -- Production data (primarily from OnWar)
    production_start TEXT, -- YYYY format
    production_end TEXT,
    production_quantity INTEGER,
    manufacturers TEXT,
    formal_designation TEXT,

    -- Physical specifications (merged from all sources)
    weight_tonnes REAL,
    length_m REAL,
    width_m REAL,
    height_m REAL,
    crew INTEGER,
    ground_clearance_m REAL,

    -- Armor protection (from WWII Tanks UK - most detailed)
    armor_front_mm INTEGER,
    armor_front_angle INTEGER, -- degrees from vertical
    armor_front_effective_mm INTEGER, -- calculated effective thickness
    armor_side_mm INTEGER,
    armor_side_angle INTEGER,
    armor_rear_mm INTEGER,
    armor_rear_angle INTEGER,
    armor_top_mm INTEGER,
    armor_bottom_mm INTEGER,

    -- Turret armor (if applicable)
    turret_front_mm INTEGER,
    turret_front_angle INTEGER,
    turret_side_mm INTEGER,
    turret_rear_mm INTEGER,
    turret_top_mm INTEGER,

    -- Performance specifications (merged sources)
    max_speed_kmh INTEGER,
    max_speed_road_kmh INTEGER,
    max_speed_offroad_kmh INTEGER,
    range_road_km INTEGER,
    range_offroad_km INTEGER,
    fuel_type TEXT, -- petrol, diesel
    fuel_capacity_l INTEGER,
    engine_make TEXT,
    engine_model TEXT,
    engine_hp INTEGER,
    power_weight_ratio REAL, -- HP per tonne

    -- Mobility
    gradient_capability_deg INTEGER,
    fording_depth_m REAL,
    trench_crossing_m REAL,
    vertical_obstacle_m REAL,
    turning_radius_m REAL,

    -- Radio/Communications
    radio_equipment TEXT,

    -- Metadata
    first_appearance TEXT, -- Quarter format: 1941-Q2
    last_appearance TEXT,
    notes TEXT,
    aliases TEXT, -- JSON array of alternate names

    -- Audit trail
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_equipment_nation ON equipment(nation);
CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(equipment_type);
CREATE INDEX IF NOT EXISTS idx_equipment_category ON equipment(category);
CREATE INDEX IF NOT EXISTS idx_equipment_witw ON equipment(witw_id);
CREATE INDEX IF NOT EXISTS idx_equipment_first_appearance ON equipment(first_appearance);

-- ============================================================================
-- GUNS MASTER TABLE
-- Source: WWII Tanks UK v2.1 enhanced gun scraper (342 guns)
-- ============================================================================

CREATE TABLE IF NOT EXISTS guns (
    gun_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    full_name TEXT,
    nation TEXT NOT NULL,

    -- Basic specifications
    caliber_mm INTEGER NOT NULL,
    barrel_length TEXT, -- Format: L/42, L/60, etc.
    rate_of_fire_rpm INTEGER,

    -- Production information
    manufactured_start INTEGER, -- Year
    manufactured_end INTEGER,

    -- Classification
    gun_type TEXT, -- anti_tank, tank_gun, field_gun, howitzer, anti_aircraft, machine_gun

    -- Source provenance
    wwiitanks_id TEXT UNIQUE,
    source_url TEXT,
    scraped_at TEXT,
    scraper_version TEXT,

    -- Historical context
    history TEXT,
    notes TEXT,

    -- Audit trail
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_guns_caliber ON guns(caliber_mm);
CREATE INDEX IF NOT EXISTS idx_guns_nation ON guns(nation);
CREATE INDEX IF NOT EXISTS idx_guns_type ON guns(gun_type);
CREATE INDEX IF NOT EXISTS idx_guns_wwiitanks ON guns(wwiitanks_id);

-- ============================================================================
-- AMMUNITION TABLE
-- Source: WWII Tanks UK v2.1 (ammunition arrays per gun)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ammunition (
    ammo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gun_id TEXT NOT NULL,

    name TEXT NOT NULL,
    type TEXT NOT NULL, -- AP, AP40, HE, HEAT, APCR, APDS, HVAP
    type_full TEXT,

    -- Ballistic specifications
    caliber_mm INTEGER,
    weight_kg REAL,
    muzzle_velocity_m_s INTEGER,
    explosive_kg REAL, -- For HE rounds

    -- Reference penetration (quoted from source)
    quoted_penetration TEXT,

    -- HE blast effects (from WWII Tanks UK)
    blast_kill_99pct_radius_m INTEGER,
    blast_kill_66pct_radius_m INTEGER,
    blast_kill_33pct_radius_m INTEGER,
    blast_armor_pen_1m_mm INTEGER, -- Blast penetration at 1m

    -- Metadata
    notes TEXT,

    FOREIGN KEY (gun_id) REFERENCES guns(gun_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ammunition_gun ON ammunition(gun_id);
CREATE INDEX IF NOT EXISTS idx_ammunition_type ON ammunition(type);
CREATE INDEX IF NOT EXISTS idx_ammunition_caliber ON ammunition(caliber_mm);

-- ============================================================================
-- PENETRATION DATA TABLE
-- Source: WWII Tanks UK v2.1 (8 range entries per ammunition type)
-- Enables AFV vs Gun effectiveness analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS penetration_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ammo_id INTEGER NOT NULL,

    range_m INTEGER NOT NULL,
    flight_time_s REAL,
    penetration_0deg_mm INTEGER, -- Penetration at 0° (perpendicular)
    penetration_30deg_mm INTEGER, -- Penetration at 30° angle
    hit_probability_pct INTEGER,

    FOREIGN KEY (ammo_id) REFERENCES ammunition(ammo_id) ON DELETE CASCADE,
    UNIQUE(ammo_id, range_m)
);

CREATE INDEX IF NOT EXISTS idx_penetration_ammo ON penetration_data(ammo_id);
CREATE INDEX IF NOT EXISTS idx_penetration_range ON penetration_data(range_m);

-- ============================================================================
-- EQUIPMENT-GUN RELATIONSHIPS
-- Links equipment (tanks, AFVs) to their mounted guns
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_guns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id TEXT NOT NULL,
    gun_id TEXT NOT NULL,

    mount_type TEXT, -- main, coaxial, hull, aa, bow
    mount_position TEXT, -- turret, hull, pintle, sponson
    ammunition_count INTEGER, -- Rounds carried

    notes TEXT,

    FOREIGN KEY (equipment_id) REFERENCES equipment(canonical_id) ON DELETE CASCADE,
    FOREIGN KEY (gun_id) REFERENCES guns(gun_id) ON DELETE CASCADE,
    UNIQUE(equipment_id, gun_id, mount_type)
);

CREATE INDEX IF NOT EXISTS idx_eq_guns_equipment ON equipment_guns(equipment_id);
CREATE INDEX IF NOT EXISTS idx_eq_guns_gun ON equipment_guns(gun_id);

-- ============================================================================
-- UNITS TABLE
-- Source: Existing unit JSON files (100+ units)
-- ============================================================================

CREATE TABLE IF NOT EXISTS units (
    unit_id TEXT PRIMARY KEY,
    nation TEXT NOT NULL,
    quarter TEXT NOT NULL, -- Format: 1941-Q2
    designation TEXT NOT NULL,
    unit_type TEXT, -- Panzer Division, Infantry Division, Armoured Brigade, etc.
    parent_formation TEXT,
    organization_level TEXT, -- theater, corps, division, regiment, battalion, company

    -- Command structure
    commander_name TEXT,
    commander_rank TEXT,
    commander_appointment_date TEXT,
    headquarters_location TEXT,
    parent_command TEXT,

    -- Personnel strength
    total_personnel INTEGER,
    officers INTEGER,
    ncos INTEGER,
    enlisted INTEGER,
    staff_officers INTEGER,
    staff_ncos INTEGER,
    staff_enlisted INTEGER,

    -- Operational status
    operational_status TEXT, -- full_strength, reduced, reinforcing, disbanded
    readiness_percentage REAL,

    -- Geographic context
    theater TEXT, -- north_africa, eastern_front, western_europe
    location TEXT,

    -- Source reference
    source_file TEXT, -- Original JSON filename
    schema_version TEXT,

    -- Audit trail
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_units_nation ON units(nation);
CREATE INDEX IF NOT EXISTS idx_units_quarter ON units(quarter);
CREATE INDEX IF NOT EXISTS idx_units_nation_quarter ON units(nation, quarter);
CREATE INDEX IF NOT EXISTS idx_units_type ON units(unit_type);
CREATE INDEX IF NOT EXISTS idx_units_org_level ON units(organization_level);

-- ============================================================================
-- UNIT EQUIPMENT TABLE
-- Tracks which equipment each unit has and in what quantities
-- ============================================================================

CREATE TABLE IF NOT EXISTS unit_equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id TEXT NOT NULL,
    equipment_id TEXT, -- NULL allowed until equipment matching is completed

    count INTEGER NOT NULL,
    operational INTEGER, -- How many are operational
    readiness_percentage REAL,

    variant_name TEXT, -- Specific variant (e.g., "Panzer III Ausf G")
    variant_notes TEXT,
    category TEXT, -- tanks, halftracks, trucks, artillery, etc.
    subcategory TEXT, -- heavy_tanks, medium_tanks, light_tanks, etc.

    -- Context from original JSON
    armament TEXT, -- Main gun designation
    armor_mm TEXT, -- Armor protection summary
    role TEXT, -- Primary role in unit

    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(canonical_id) ON DELETE SET NULL,
    UNIQUE(unit_id, variant_name)  -- Removed equipment_id from unique constraint since it can be NULL
);

CREATE INDEX IF NOT EXISTS idx_unit_eq_unit ON unit_equipment(unit_id);
CREATE INDEX IF NOT EXISTS idx_unit_eq_equipment ON unit_equipment(equipment_id);
CREATE INDEX IF NOT EXISTS idx_unit_eq_category ON unit_equipment(category);

-- ============================================================================
-- MATCH REVIEWS TABLE
-- Tracks manual review decisions for equipment matching
-- ============================================================================

CREATE TABLE IF NOT EXISTS match_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_id TEXT NOT NULL,

    -- WITW source
    witw_name TEXT,
    witw_id INTEGER,
    witw_type TEXT,

    -- OnWar match candidate
    onwar_name TEXT,
    onwar_url TEXT,
    onwar_confidence INTEGER,
    onwar_fields_count INTEGER,

    -- WWII Tanks UK match candidate
    wwiitanks_name TEXT,
    wwiitanks_id TEXT,
    wwiitanks_confidence INTEGER,
    wwiitanks_fields_count INTEGER,

    -- Review decision
    review_status TEXT NOT NULL, -- pending, approved, rejected, needs_research, skipped
    reviewer_notes TEXT,
    reviewed_at TEXT,
    reviewed_by TEXT,

    -- Match outcome
    final_match_method TEXT,
    final_confidence INTEGER,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reviews_status ON match_reviews(review_status);
CREATE INDEX IF NOT EXISTS idx_reviews_canonical ON match_reviews(canonical_id);

-- ============================================================================
-- DATA SOURCE TRACKING
-- Tracks which source files have been imported
-- ============================================================================

CREATE TABLE IF NOT EXISTS import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL, -- witw, onwar, wwiitanks_afv, wwiitanks_guns, units
    source_file TEXT NOT NULL,

    records_imported INTEGER,
    records_failed INTEGER,

    import_started_at TEXT,
    import_completed_at TEXT,
    import_status TEXT, -- success, failed, partial
    error_log TEXT,

    imported_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_import_source ON import_log(source_name);
CREATE INDEX IF NOT EXISTS idx_import_status ON import_log(import_status);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Complete equipment with all enhancements
CREATE VIEW IF NOT EXISTS v_equipment_full AS
SELECT
    e.*,
    COUNT(DISTINCT eg.gun_id) as guns_count,
    COUNT(DISTINCT ue.unit_id) as units_count,
    GROUP_CONCAT(DISTINCT g.name) as mounted_guns
FROM equipment e
LEFT JOIN equipment_guns eg ON e.canonical_id = eg.equipment_id
LEFT JOIN guns g ON eg.gun_id = g.gun_id
LEFT JOIN unit_equipment ue ON e.canonical_id = ue.equipment_id
GROUP BY e.canonical_id;

-- View: Units with equipment summary
CREATE VIEW IF NOT EXISTS v_units_with_equipment AS
SELECT
    u.*,
    COUNT(DISTINCT ue.equipment_id) as equipment_types,
    SUM(ue.count) as total_equipment_count,
    SUM(CASE WHEN ue.category = 'tanks' THEN ue.count ELSE 0 END) as tanks_count,
    SUM(CASE WHEN ue.category = 'halftracks' THEN ue.count ELSE 0 END) as halftracks_count,
    SUM(CASE WHEN ue.category = 'artillery' THEN ue.count ELSE 0 END) as artillery_count
FROM units u
LEFT JOIN unit_equipment ue ON u.unit_id = ue.unit_id
GROUP BY u.unit_id;

-- View: Guns with ammunition count
CREATE VIEW IF NOT EXISTS v_guns_with_ammo AS
SELECT
    g.*,
    COUNT(DISTINCT a.ammo_id) as ammo_types_count,
    COUNT(DISTINCT p.id) as penetration_data_points,
    COUNT(DISTINCT eg.equipment_id) as vehicles_count
FROM guns g
LEFT JOIN ammunition a ON g.gun_id = a.gun_id
LEFT JOIN penetration_data p ON a.ammo_id = p.ammo_id
LEFT JOIN equipment_guns eg ON g.gun_id = eg.gun_id
GROUP BY g.gun_id;

-- ============================================================================
-- DATABASE METADATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description)
VALUES ('1.0.0', 'Initial schema creation with equipment, guns, ammunition, penetration, units, and matching tables');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
