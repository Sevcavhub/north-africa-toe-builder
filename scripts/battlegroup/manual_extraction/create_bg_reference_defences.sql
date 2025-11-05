-- Create BG_Reference_Defences table for defensive fortifications
-- Captures defensive structures, obstacles, and fortifications with points/BR costs

CREATE TABLE IF NOT EXISTS BG_Reference_Defences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    points_cost INTEGER,
    br_rating INTEGER,
    nation TEXT,
    special_rules TEXT,
    terrain_type TEXT,
    source_supplement TEXT,
    source_image_location TEXT,
    extraction_method TEXT DEFAULT 'manual_screenshot',
    verified_by TEXT,
    verification_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, nation, source_supplement)
);

CREATE INDEX IF NOT EXISTS idx_defences_nation ON BG_Reference_Defences(nation);
CREATE INDEX IF NOT EXISTS idx_defences_source ON BG_Reference_Defences(source_supplement);
