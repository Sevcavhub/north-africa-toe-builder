-- Create Fresh BattleGroup Reference Tables for Manual Extraction
-- Date: 2025-11-04
-- Method: Manual screenshot extraction with audit trail

-- =============================================================================
-- bg_reference_guns - Gun/Artillery Reference Data
-- =============================================================================
CREATE TABLE bg_reference_guns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Gun Identification
    name TEXT NOT NULL,
    nation TEXT NOT NULL,
    caliber_mm INTEGER,
    barrel_length TEXT,

    -- HE (High Explosive) Stats
    he_dice INTEGER,
    he_target TEXT,  -- e.g., "3+", "4+", "5+", "6+"

    -- AP (Armor Penetration) Stats by Range Band
    ap_0_10 INTEGER,   -- 0-10" range
    ap_10_20 INTEGER,  -- 10-20" range
    ap_20_30 INTEGER,  -- 20-30" range
    ap_30_40 INTEGER,  -- 30-40" range
    ap_40_50 INTEGER,  -- 40-50" range
    ap_50_70 INTEGER,  -- 50-70" range (long guns only)

    -- Game Stats
    points_cost INTEGER,
    battle_rating INTEGER,

    -- Source Provenance
    source_file TEXT,              -- e.g., "Battlegroup-Kursk.pdf"
    source_page TEXT,              -- Page number(s)
    extraction_confidence TEXT,    -- 'high', 'medium', 'low'
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Optional Theater/Experience Context
    source_battle TEXT,            -- e.g., "Kursk", "Torch", "Overlord"
    source_date TEXT,              -- Date/year of source
    unit_experience TEXT,          -- e.g., "Regular", "Veteran", "Elite"
    source_document TEXT,          -- Full document name
    extraction_notes TEXT,

    -- Master linkage (if needed for deduplication)
    master_id INTEGER,

    -- Manual Extraction Audit Fields (NEW)
    extraction_method TEXT DEFAULT 'manual_screenshot',
    verified_by TEXT,              -- Who verified the entry
    verification_date TIMESTAMP,   -- When verified
    screenshot_file TEXT,          -- Reference screenshot filename

    UNIQUE(name, nation, source_file)
);

CREATE INDEX idx_guns_nation ON bg_reference_guns(nation);
CREATE INDEX idx_guns_caliber ON bg_reference_guns(caliber_mm);
CREATE INDEX idx_guns_extraction_method ON bg_reference_guns(extraction_method);

-- =============================================================================
-- bg_reference_vehicles - Vehicle/Equipment Reference Data
-- =============================================================================
CREATE TABLE bg_reference_vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Vehicle Identification
    name TEXT NOT NULL,
    nation TEXT NOT NULL,
    year_range TEXT,               -- e.g., "1941-1943"
    vehicle_type TEXT,             -- e.g., "Medium Tank", "Heavy Tank", "SPG"

    -- Movement Stats
    off_road_inches INTEGER,
    road_inches INTEGER,
    special_movement TEXT,         -- e.g., "Tracked", "Wheeled", "Half-tracked", "HVSS"

    -- Armor Values (letter scale A-O)
    armor_front TEXT,
    armor_side TEXT,
    armor_rear TEXT,

    -- Armament
    weapons TEXT,                  -- e.g., "75mmL40, MG, MG"

    -- Game Stats
    points_cost INTEGER,
    battle_rating INTEGER,
    special_rules TEXT,

    -- Source Provenance
    source_file TEXT,
    source_page TEXT,
    extraction_confidence TEXT,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Optional Theater/Experience Context
    source_battle TEXT,
    source_date TEXT,
    unit_experience TEXT,
    source_document TEXT,
    extraction_notes TEXT,

    -- Master linkage
    master_id INTEGER,

    -- Manual Extraction Audit Fields (NEW)
    extraction_method TEXT DEFAULT 'manual_screenshot',
    verified_by TEXT,
    verification_date TIMESTAMP,
    screenshot_file TEXT,

    UNIQUE(name, nation, year_range, source_file)
);

CREATE INDEX idx_vehicles_nation ON bg_reference_vehicles(nation);
CREATE INDEX idx_vehicles_type ON bg_reference_vehicles(vehicle_type);
CREATE INDEX idx_vehicles_year ON bg_reference_vehicles(year_range);
CREATE INDEX idx_vehicles_extraction_method ON bg_reference_vehicles(extraction_method);

-- =============================================================================
-- Record table creation in audit log
-- =============================================================================
INSERT INTO extraction_audit (table_name, action, notes, user_name)
VALUES
    ('bg_reference_guns', 'created_fresh_table',
     'New table created with manual extraction audit fields',
     'claude_code'),
    ('bg_reference_vehicles', 'created_fresh_table',
     'New table created with manual extraction audit fields',
     'claude_code');

-- Print summary
SELECT 'Fresh tables created successfully:' as message
UNION ALL
SELECT '  bg_reference_guns (0 rows)'
UNION ALL
SELECT '  bg_reference_vehicles (0 rows)'
UNION ALL
SELECT ''
UNION ALL
SELECT 'New audit columns added:'
UNION ALL
SELECT '  - extraction_method (default: manual_screenshot)'
UNION ALL
SELECT '  - verified_by (who verified entry)'
UNION ALL
SELECT '  - verification_date (when verified)'
UNION ALL
SELECT '  - screenshot_file (reference screenshot)'
UNION ALL
SELECT ''
UNION ALL
SELECT 'Ready for manual data entry.';
