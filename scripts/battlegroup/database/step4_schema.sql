-- ============================================================================
-- Phase 9B Step 4: Database Extensions Schema
-- Purpose: BattleGroup stat generation and campaign tracking
-- ============================================================================

-- ============================================================================
-- EQUIPMENT BATTLEGROUP TABLE
-- Generated BattleGroup stats for all 469 equipment items
-- Links to existing equipment table via canonical_id
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_battlegroup (
    equipment_id TEXT PRIMARY KEY,

    -- Armor protection (BattleGroup letter scale)
    armor_front TEXT,           -- Letter rating (A-O scale, reverse alphabetical)
    armor_side TEXT,
    armor_rear TEXT,
    armor_turret_front TEXT,
    armor_turret_side TEXT,
    armor_turret_rear TEXT,

    -- Movement (inches)
    off_road_movement INTEGER,  -- Off-road movement in inches
    road_movement INTEGER,      -- Road movement in inches

    -- HE effectiveness
    he_dice INTEGER,            -- Number of dice
    he_target TEXT,             -- Target number (e.g., "4+", "5+")
    he_format TEXT,             -- Combined format (e.g., "4/4+")

    -- Penetration values (1-15 scale across 6 range bands)
    ap_0_10 INTEGER,            -- Penetration at 0-10"
    ap_10_20 INTEGER,           -- Penetration at 10-20"
    ap_20_30 INTEGER,           -- Penetration at 20-30"
    ap_30_40 INTEGER,           -- Penetration at 30-40"
    ap_40_50 INTEGER,           -- Penetration at 40-50"
    ap_50_70 INTEGER,           -- Penetration at 50-70" (only for 88mm+ guns)

    -- Points and Battle Rating
    points_regular INTEGER,     -- Points cost for Regular experience
    points_inexperienced INTEGER, -- Points cost for Inexperienced (0.85x)
    points_veteran INTEGER,     -- Points cost for Veteran (1.10x)
    points_elite INTEGER,       -- Points cost for Elite (1.20x)
    battle_rating_regular INTEGER, -- BR for Regular
    battle_rating_inexperienced INTEGER, -- BR for Inexperienced (-1)
    battle_rating_veteran INTEGER, -- BR for Veteran (+0-1)
    battle_rating_elite INTEGER,   -- BR for Elite (+1)

    -- Special rules and notes
    special_rules TEXT,         -- JSON array of special rules
    crew INTEGER,               -- Crew size
    weapon_description TEXT,    -- Main weapon description

    -- Generation metadata
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generation_method TEXT,     -- Which converters used (lookup/formula/hybrid)
    confidence_score INTEGER,   -- 0-100 confidence in generated stats
    validation_notes TEXT,      -- Any discrepancies or warnings

    -- Source references (for validation)
    reference_vehicle_id INTEGER, -- FK to bg_reference_vehicles if matched
    reference_match_confidence INTEGER, -- Confidence of reference match

    FOREIGN KEY (equipment_id) REFERENCES equipment(canonical_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_equipbg_front_armor ON equipment_battlegroup(armor_front);
CREATE INDEX IF NOT EXISTS idx_equipbg_points ON equipment_battlegroup(points_regular);
CREATE INDEX IF NOT EXISTS idx_equipbg_br ON equipment_battlegroup(battle_rating_regular);
CREATE INDEX IF NOT EXISTS idx_equipbg_confidence ON equipment_battlegroup(confidence_score);

-- ============================================================================
-- ARMOR CONVERSION LOOKUP TABLE
-- MM thickness to BattleGroup letter scale
-- ============================================================================

CREATE TABLE IF NOT EXISTS bg_armor_conversion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mm_min INTEGER NOT NULL,     -- Minimum armor thickness in mm
    mm_max INTEGER NOT NULL,     -- Maximum armor thickness in mm
    letter TEXT NOT NULL,        -- BattleGroup letter (A-O)
    numeric_value INTEGER,       -- Alternative numeric scale (6-12)
    description TEXT,
    typical_vehicles TEXT,       -- Example vehicles with this armor
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_armor_conv_mm ON bg_armor_conversion(mm_min, mm_max);
CREATE INDEX IF NOT EXISTS idx_armor_conv_letter ON bg_armor_conversion(letter);

-- ============================================================================
-- PENETRATION SCALE LOOKUP TABLE
-- Caliber and barrel length to penetration scale values
-- ============================================================================

CREATE TABLE IF NOT EXISTS bg_penetration_scale (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caliber_mm INTEGER NOT NULL,
    barrel_length TEXT,          -- Format: L/42, L/56, L/70, etc.
    penetration_1000m_mm INTEGER, -- Historical penetration at 1000m

    -- BattleGroup scale values (1-15)
    value_0_10 INTEGER,          -- Penetration value at 0-10"
    value_10_20 INTEGER,         -- Penetration value at 10-20"
    value_20_30 INTEGER,         -- Penetration value at 20-30"
    value_30_40 INTEGER,         -- Penetration value at 30-40"
    value_40_50 INTEGER,         -- Penetration value at 40-50"
    value_50_70 INTEGER,         -- Penetration value at 50-70"

    gun_examples TEXT,           -- Example guns (e.g., "7.5cm KwK40, 75mm M3")
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_pen_scale_caliber ON bg_penetration_scale(caliber_mm);
CREATE INDEX IF NOT EXISTS idx_pen_scale_barrel ON bg_penetration_scale(barrel_length);

-- ============================================================================
-- MOVEMENT VALUES LOOKUP TABLE
-- Vehicle type and weight to movement values
-- ============================================================================

CREATE TABLE IF NOT EXISTS bg_movement_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_type TEXT NOT NULL,  -- light_tank, medium_tank, heavy_tank, halftrack, wheeled, etc.
    weight_min_tonnes REAL,      -- Minimum weight in tonnes
    weight_max_tonnes REAL,      -- Maximum weight in tonnes
    off_road INTEGER NOT NULL,   -- Off-road movement in inches
    road INTEGER NOT NULL,       -- Road movement in inches

    typical_vehicles TEXT,       -- Example vehicles
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_movement_type ON bg_movement_values(vehicle_type);
CREATE INDEX IF NOT EXISTS idx_movement_weight ON bg_movement_values(weight_min_tonnes, weight_max_tonnes);

-- ============================================================================
-- HE EFFECTIVENESS LOOKUP TABLE
-- Caliber to HE dice and target number
-- ============================================================================

CREATE TABLE IF NOT EXISTS bg_he_effectiveness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caliber_min_mm INTEGER NOT NULL,
    caliber_max_mm INTEGER NOT NULL,
    dice INTEGER NOT NULL,       -- Number of HE dice
    target TEXT NOT NULL,        -- Target number (e.g., "4+", "5+")
    format TEXT NOT NULL,        -- Combined format (e.g., "4/4+")

    gun_examples TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_he_caliber ON bg_he_effectiveness(caliber_min_mm, caliber_max_mm);

-- ============================================================================
-- SPECIAL RULES TABLE
-- BattleGroup game mechanics and special rules
-- ============================================================================

CREATE TABLE IF NOT EXISTS bg_special_rules (
    rule_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,               -- movement, firepower, morale, command, defensive
    description TEXT NOT NULL,
    mechanical_effect TEXT,      -- Specific game effect

    -- Restrictions
    nation_specific TEXT,        -- NULL or nation code (german, british, italian, american, french)
    era_restriction TEXT,        -- NULL or date range (e.g., "1943-01:1945-05")
    unit_type_restriction TEXT,  -- NULL or unit types (e.g., "tank, armored_car")

    -- Source reference
    source_book TEXT,            -- BattleGroup rulebook reference
    source_page TEXT,

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_special_rules_category ON bg_special_rules(category);
CREATE INDEX IF NOT EXISTS idx_special_rules_nation ON bg_special_rules(nation_specific);

-- ============================================================================
-- CAMPAIGN UNITS TABLE
-- Tracks unit evolution quarter-by-quarter
-- Links to Phase 6 extracted units (402 ground + 23 air)
-- ============================================================================

CREATE TABLE IF NOT EXISTS bg_campaign_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id TEXT NOT NULL,       -- FK to units table
    quarter TEXT NOT NULL,       -- Format: 1941q2

    -- BattleGroup stats for this quarter
    points_cost INTEGER,         -- Total force points
    battle_rating INTEGER,       -- Total force BR
    force_composition TEXT,      -- JSON: equipment breakdown

    -- Equipment changes from previous quarter
    equipment_added TEXT,        -- JSON: new equipment types
    equipment_removed TEXT,      -- JSON: removed equipment types
    equipment_upgraded TEXT,     -- JSON: variant upgrades

    -- Operational status
    status TEXT,                 -- active, disbanded, reformed, reinforcing
    readiness_percentage REAL,
    personnel_strength INTEGER,

    -- Historical context
    location TEXT,
    engagements TEXT,            -- JSON: battles participated in this quarter

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE,
    UNIQUE(unit_id, quarter)
);

CREATE INDEX IF NOT EXISTS idx_campaign_units_unit ON bg_campaign_units(unit_id);
CREATE INDEX IF NOT EXISTS idx_campaign_units_quarter ON bg_campaign_units(quarter);
CREATE INDEX IF NOT EXISTS idx_campaign_units_status ON bg_campaign_units(status);

-- ============================================================================
-- CAMPAIGN PROGRESSION TABLE
-- Tracks campaign timeline and linked scenarios
-- ============================================================================

CREATE TABLE IF NOT EXISTS bg_campaign_progression (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    theater TEXT NOT NULL,      -- north_africa, eastern_front, western_europe

    start_quarter TEXT NOT NULL, -- Format: 1940q4
    end_quarter TEXT NOT NULL,   -- Format: 1943q2

    -- Campaign structure
    battles TEXT,                -- JSON: array of battle names
    scenarios TEXT,              -- JSON: array of scenario IDs
    participants TEXT,           -- JSON: array of unit_ids

    -- Campaign rules
    attrition_rules TEXT,        -- JSON: campaign-specific attrition
    reinforcement_schedule TEXT, -- JSON: when/how units are reinforced
    victory_conditions TEXT,     -- JSON: campaign victory conditions

    -- Status tracking
    current_quarter TEXT,        -- Current quarter in campaign
    status TEXT,                 -- planning, active, completed, abandoned

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_campaign_theater ON bg_campaign_progression(theater);
CREATE INDEX IF NOT EXISTS idx_campaign_status ON bg_campaign_progression(status);

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

INSERT OR IGNORE INTO schema_version (version, description)
VALUES ('1.1.0', 'Phase 9B Step 4: BattleGroup stat generation and campaign tracking tables');

-- ============================================================================
-- END OF STEP 4 SCHEMA
-- ============================================================================
