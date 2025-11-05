-- Create BG_Reference_ArmyList_Examples table for army list unit entries
-- Captures unit compositions, points costs, BR values, transport options, and special rules

CREATE TABLE IF NOT EXISTS BG_Reference_ArmyList_Examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_name TEXT NOT NULL,
    category TEXT,
    unit_composition TEXT,
    men_count INTEGER,
    points_cost INTEGER,
    br_rating TEXT,
    transport TEXT,
    special_rules TEXT,
    optional_upgrades TEXT,
    nation TEXT,
    source_supplement TEXT,
    source_image_location TEXT,
    extraction_method TEXT DEFAULT 'manual_screenshot',
    verified_by TEXT,
    verification_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unit_name, nation, source_supplement)
);

CREATE INDEX IF NOT EXISTS idx_armylist_nation ON BG_Reference_ArmyList_Examples(nation);
CREATE INDEX IF NOT EXISTS idx_armylist_category ON BG_Reference_ArmyList_Examples(category);
CREATE INDEX IF NOT EXISTS idx_armylist_source ON BG_Reference_ArmyList_Examples(source_supplement);
