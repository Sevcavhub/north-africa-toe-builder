-- ============================================================================
-- Phase 5.5 - Phase 1: Multi-Game Equipment Database Schema
-- ============================================================================
-- Date: November 3, 2025
-- Purpose: Replace 8x duplicated equipment tables with normalized architecture
-- Design: Game-agnostic core + game-specific stat tables
--
-- Problem Solved:
--   - 6 equipment tables with ~4,669 rows representing ~500-600 unique items
--   - Sherman tank: ~50 entries, Panzer IV: ~95 entries across tables
--   - Multi-game requirements: BattleGroup, Achtung Panzer, Flames of War
--
-- Architecture:
--   1. equipment_master: Single source of truth for equipment identity
--   2. equipment_name_variants: Solve naming hell (Sherman/M4/M4 Medium Tank)
--   3. equipment_theater_usage: Many-to-many theater assignments
--   4. equipment_nation_usage: Handle lend-lease, captured equipment
--   5. equipment_stats_battlegroup: BattleGroup game stats (Phase 9B)
--   6. equipment_stats_achtung_panzer: Achtung Panzer stats (Phase 9C)
--   7. equipment_stats_flames_of_war: Flames of War stats (Phase 9D)
--   8. normalization_audit: Migration audit trail
-- ============================================================================

-- ============================================================================
-- Table 1: equipment_master (Game-Agnostic Core)
-- ============================================================================
-- Purpose: Single source of truth for equipment identity and historical specs
-- Expected Count: 1,400-1,700 items (after deduplication)
-- Source Authority: equipment (469) + master_equipment (1,230) + unique items
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_master_new (
    master_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identity Fields (REQUIRED)
    canonical_name TEXT NOT NULL UNIQUE,  -- Authority: Sherman M4A1 (75mm)
    display_name TEXT NOT NULL,           -- User-friendly: M4A1 Sherman
    short_name TEXT,                       -- Abbreviated: M4A1

    -- Classification (REQUIRED)
    equipment_category TEXT NOT NULL CHECK(equipment_category IN (
        'tank',
        'armored_car',
        'self_propelled_gun',
        'vehicle',
        'gun',
        'artillery',
        'anti_tank_gun',
        'anti_aircraft_gun',
        'mortar',
        'aircraft',
        'infantry_weapon',
        'other'
    )),
    equipment_subcategory TEXT,            -- medium_tank, light_tank, howitzer, etc.

    -- Origin (REQUIRED)
    original_nation TEXT NOT NULL CHECK(original_nation IN (
        'german',
        'british',
        'italian',
        'american',
        'french',
        'soviet',
        'japanese',
        'commonwealth',
        'other'
    )),

    -- Historical Specifications (JSON for extensibility)
    -- Stores ALL real-world specs from multiple sources without ALTER TABLE
    -- Example: {
    --   "witw_id": "usa_m4a1_sherman",
    --   "onwar_url": "https://onwar.com/tanks/usa/...",
    --   "wwiitanks_id": "456",
    --   "production_years": "1942-1945",
    --   "weight_tons": 30.3,
    --   "crew": 5,
    --   "armor_hull_front_mm": 51,
    --   "armor_hull_side_mm": 38,
    --   "main_gun": "75mm M3",
    --   "engine_hp": 400,
    --   "speed_road_kmh": 38,
    --   "range_road_km": 193
    -- }
    historical_specs_json TEXT,            -- JSON object with all historical data

    -- Provenance
    primary_source TEXT CHECK(primary_source IN (
        'witw',           -- War in the West game baseline
        'onwar',          -- OnWar.com AFV database
        'wwiitanks',      -- WWIItanks.com database
        'bg_pdf',         -- BattleGroup rulebook PDF
        'tessin',         -- Tessin Verbaende orders of battle
        'jane',           -- Jane's Fighting Vehicles
        'manual',         -- Manually curated
        'other'
    )),

    -- Quality Metrics
    confidence_score REAL DEFAULT 0.0 CHECK(confidence_score >= 0 AND confidence_score <= 100),

    -- Audit Fields
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_equipment_master_category ON equipment_master_new(equipment_category);
CREATE INDEX IF NOT EXISTS idx_equipment_master_nation ON equipment_master_new(original_nation);
CREATE INDEX IF NOT EXISTS idx_equipment_master_canonical ON equipment_master_new(canonical_name);
CREATE INDEX IF NOT EXISTS idx_equipment_master_display ON equipment_master_new(display_name);

-- ============================================================================
-- Table 2: equipment_name_variants_new (Solve Naming Hell)
-- ============================================================================
-- Purpose: Map 2,000+ name variations to canonical equipment
-- Example: "Sherman", "M4", "M4 Medium Tank", "M4A1" → master_id 123
-- Expected Count: 2,000-3,000 variants (populated in Phase 2)
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_name_variants_new (
    variant_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign Key to equipment_master
    master_id INTEGER NOT NULL,

    -- Variant Name (UNIQUE across all variants)
    variant_name TEXT NOT NULL UNIQUE,

    -- Provenance
    variant_source TEXT CHECK(variant_source IN (
        'onwar',          -- OnWar database name
        'wwiitanks',      -- WWIItanks database name
        'bg_pdf',         -- BattleGroup rulebook name
        'tessin',         -- Tessin orders of battle name
        'jane',           -- Jane's book name
        'witw',           -- WITW game name
        'programmatic',   -- Generated via rules (Pz.Kpfw. → Panzer)
        'manual',         -- Manually curated
        'other'
    )),

    -- Flags
    is_official BOOLEAN DEFAULT 0,  -- 1 = official designation from Jane's/manuals

    -- Audit
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key Constraint
    FOREIGN KEY (master_id) REFERENCES equipment_master_new(master_id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_name_variants_master ON equipment_name_variants_new(master_id);
CREATE INDEX IF NOT EXISTS idx_name_variants_name ON equipment_name_variants_new(variant_name);
CREATE INDEX IF NOT EXISTS idx_name_variants_source ON equipment_name_variants_new(variant_source);

-- ============================================================================
-- Table 3: equipment_theater_usage (Many-to-Many Theater Assignments)
-- ============================================================================
-- Purpose: Track which equipment was used in which theaters and when
-- Example: Sherman M4A1 used in north_africa (1942-Q2 to 1943-Q1)
-- Expected Count: 469 North Africa + ~1,000 future theaters
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_theater_usage (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign Key to equipment_master
    master_id INTEGER NOT NULL,

    -- Theater Assignment (REQUIRED)
    theater TEXT NOT NULL CHECK(theater IN (
        'north_africa',
        'eastern_front',
        'western_europe',
        'italy',
        'pacific',
        'balkans',
        'middle_east',
        'other'
    )),

    -- Date Range (ISO 8601: YYYY-QN format)
    date_from TEXT,  -- Example: "1942-Q2"
    date_to TEXT,    -- Example: "1943-Q1"

    -- Notes
    usage_notes TEXT,

    -- Audit
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key Constraint
    FOREIGN KEY (master_id) REFERENCES equipment_master_new(master_id) ON DELETE CASCADE,

    -- Unique Constraint: One theater per equipment (with date ranges)
    UNIQUE(master_id, theater)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_theater_usage_master ON equipment_theater_usage(master_id);
CREATE INDEX IF NOT EXISTS idx_theater_usage_theater ON equipment_theater_usage(theater);

-- ============================================================================
-- Table 4: equipment_nation_usage (Handle Lend-Lease, Captured Equipment)
-- ============================================================================
-- Purpose: Track which nations used which equipment (original, lend-lease, captured)
-- Example: Sherman M4A1 → original: american, lend_lease: british (in north_africa)
-- Expected Count: 500-1,000 nation usage records
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_nation_usage (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign Key to equipment_master
    master_id INTEGER NOT NULL,

    -- Nation Using Equipment (REQUIRED)
    nation TEXT NOT NULL CHECK(nation IN (
        'german',
        'british',
        'italian',
        'american',
        'french',
        'soviet',
        'japanese',
        'commonwealth',
        'other'
    )),

    -- Usage Type (REQUIRED)
    usage_type TEXT NOT NULL CHECK(usage_type IN (
        'original',       -- Nation that designed/manufactured it
        'lend_lease',     -- Received via lend-lease
        'captured',       -- Captured from enemy
        'licensed',       -- Licensed production
        'other'
    )),

    -- Context
    theater TEXT,        -- Where this nation used it (north_africa, etc.)
    date_from TEXT,      -- ISO 8601: YYYY-QN
    date_to TEXT,
    source_nation TEXT,  -- For lend_lease/captured: original owner nation

    -- Notes
    usage_notes TEXT,

    -- Audit
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key Constraint
    FOREIGN KEY (master_id) REFERENCES equipment_master_new(master_id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_nation_usage_master ON equipment_nation_usage(master_id);
CREATE INDEX IF NOT EXISTS idx_nation_usage_nation ON equipment_nation_usage(nation);
CREATE INDEX IF NOT EXISTS idx_nation_usage_type ON equipment_nation_usage(usage_type);

-- ============================================================================
-- Table 5: equipment_stats_battlegroup (BattleGroup Game System Stats)
-- ============================================================================
-- Purpose: BattleGroup-specific stats for Phase 9B book generation
-- Expected Count: 469 North Africa items (100% coverage required for publication)
-- Source: bg_reference_vehicles (954) + bg_reference_guns (57) + conversion formulas
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_stats_battlegroup (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign Key to equipment_master (ONE-TO-ONE relationship)
    master_id INTEGER NOT NULL UNIQUE,

    -- Armor (Letter Scale: A-O)
    armor_front TEXT CHECK(armor_front IN (
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', NULL
    )),
    armor_side TEXT CHECK(armor_side IN (
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', NULL
    )),
    armor_rear TEXT CHECK(armor_rear IN (
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', NULL
    )),

    -- Movement (Inches)
    movement_offroad INTEGER CHECK(movement_offroad >= 0 AND movement_offroad <= 50),
    movement_road INTEGER CHECK(movement_road >= 0 AND movement_road <= 100),

    -- Weapons (BattleGroup Format)
    he_rating TEXT,     -- Example: "4/4+" (HE dice/to-hit)
    ap_rating TEXT,     -- Example: "6" (penetration value)
    weapon_description TEXT,  -- Full weapon stats string

    -- Points & Battle Rating
    points INTEGER CHECK(points >= 0),              -- Regular experience points cost
    battle_rating INTEGER CHECK(battle_rating >= 0), -- BR value

    -- Special Rules (Comma-Separated)
    special_rules TEXT,  -- Example: "Slow, Unreliable"

    -- Provenance & Quality
    conversion_confidence REAL CHECK(conversion_confidence >= 0 AND conversion_confidence <= 100),
    conversion_method TEXT CHECK(conversion_method IN (
        'scraped_from_pdf',      -- Directly from BattleGroup rulebook PDF
        'formula_derived',       -- Calculated via conversion formulas
        'interpolated',          -- Estimated from similar vehicles
        'manual',                -- Manually researched/curated
        'other'
    )),

    -- Audit
    generated_date TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    -- Foreign Key Constraint
    FOREIGN KEY (master_id) REFERENCES equipment_master_new(master_id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_stats_bg_master ON equipment_stats_battlegroup(master_id);
CREATE INDEX IF NOT EXISTS idx_stats_bg_points ON equipment_stats_battlegroup(points);
CREATE INDEX IF NOT EXISTS idx_stats_bg_br ON equipment_stats_battlegroup(battle_rating);

-- ============================================================================
-- Table 6: equipment_stats_achtung_panzer (Achtung Panzer Game System Stats)
-- ============================================================================
-- Purpose: Achtung Panzer-specific stats for Phase 9C (future)
-- Expected Count: 469+ items (Phase 9C implementation)
-- Key Difference: Separate turret/engine/track armor, burning rating
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_stats_achtung_panzer (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign Key to equipment_master (ONE-TO-ONE relationship)
    master_id INTEGER NOT NULL UNIQUE,

    -- Hull Armor (Millimeters)
    hull_armor_thick INTEGER,      -- Thickness rating
    hull_armor_assault INTEGER,    -- Assault rating
    hull_armor_front INTEGER,
    hull_armor_side INTEGER,

    -- Turret Armor (NEW for Achtung Panzer)
    turret_armor_front INTEGER,
    turret_armor_side INTEGER,

    -- Component Armor (NEW for Achtung Panzer)
    engine_armor INTEGER,          -- Engine protection rating
    track_armor INTEGER,           -- Track/suspension rating

    -- Flammability (NEW for Achtung Panzer)
    burning INTEGER,               -- Burning/flammability rating

    -- Crew Calibre (Subdivided by weapon type)
    crew_calibre_high INTEGER,
    crew_calibre_medium INTEGER,
    crew_calibre_low INTEGER,
    crew_calibre_main_gun TEXT,    -- Main gun calibre designation

    -- Movement
    speed INTEGER,                 -- Speed rating
    vehicle_class TEXT,            -- Vehicle classification

    -- Date
    date TEXT,                     -- Introduction date

    -- Provenance
    conversion_confidence REAL CHECK(conversion_confidence >= 0 AND conversion_confidence <= 100),

    -- Audit
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    -- Foreign Key Constraint
    FOREIGN KEY (master_id) REFERENCES equipment_master_new(master_id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_stats_ap_master ON equipment_stats_achtung_panzer(master_id);

-- ============================================================================
-- Table 7: equipment_stats_flames_of_war (Flames of War Game System Stats)
-- ============================================================================
-- Purpose: Flames of War-specific stats for Phase 9D (future)
-- Expected Count: 469+ items (Phase 9D implementation)
-- Note: Fields TBD based on FoW rulebook analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment_stats_flames_of_war (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign Key to equipment_master (ONE-TO-ONE relationship)
    master_id INTEGER NOT NULL UNIQUE,

    -- Placeholder fields (TBD in Phase 9D)
    -- Will be defined after FoW rulebook analysis
    fow_stats_json TEXT,           -- JSON object with FoW stats

    -- Provenance
    conversion_confidence REAL CHECK(conversion_confidence >= 0 AND conversion_confidence <= 100),

    -- Audit
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    -- Foreign Key Constraint
    FOREIGN KEY (master_id) REFERENCES equipment_master_new(master_id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_stats_fow_master ON equipment_stats_flames_of_war(master_id);

-- ============================================================================
-- Table 8: normalization_audit_new (Migration Audit Trail)
-- ============================================================================
-- Purpose: Track all migration operations for Phase 5.5 normalization
-- Expected Count: 1,000-2,000 audit records (every INSERT/UPDATE/MERGE logged)
-- Critical: MANDATORY for zero data loss guarantee
-- ============================================================================

CREATE TABLE IF NOT EXISTS normalization_audit_new (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Operation Details
    phase TEXT NOT NULL,           -- "Phase 5.5 Phase 1", "Phase 5.5 Phase 2", etc.
    operation TEXT NOT NULL,       -- "CREATE_TABLE", "INSERT", "UPDATE", "MERGE", "DEDUPLICATE"
    table_name TEXT NOT NULL,      -- Which table was affected

    -- Record Affected
    record_id INTEGER,             -- master_id or variant_id affected
    canonical_name TEXT,           -- Equipment name (for reference)

    -- SQL Executed
    sql_executed TEXT,             -- Full SQL statement (for reproducibility)

    -- Before/After Counts
    before_count INTEGER,
    after_count INTEGER,

    -- Reason & Notes
    reason TEXT NOT NULL,          -- Why this operation was performed
    notes TEXT,                    -- Additional context

    -- Audit
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    performed_by TEXT DEFAULT 'Phase_5_5_Migration_Script'
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_audit_phase ON normalization_audit_new(phase);
CREATE INDEX IF NOT EXISTS idx_audit_operation ON normalization_audit_new(operation);
CREATE INDEX IF NOT EXISTS idx_audit_table ON normalization_audit_new(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON normalization_audit_new(timestamp);

-- ============================================================================
-- Schema Version Tracking
-- ============================================================================

INSERT OR REPLACE INTO schema_version (version, description, applied_at)
VALUES ('4.0.0', 'Phase 5.5 Phase 1: Multi-game equipment database normalization', CURRENT_TIMESTAMP);

-- ============================================================================
-- End of Schema DDL
-- ============================================================================
-- Next Steps:
--   1. Create backward compatibility VIEWs (migration_views.sql)
--   2. Write migration script (create_equipment_master.js)
--   3. Test migration in DRY-RUN mode
--   4. Execute migration
--   5. Validate results
-- ============================================================================
