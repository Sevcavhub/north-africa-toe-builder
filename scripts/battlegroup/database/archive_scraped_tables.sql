-- Archive Scraped BattleGroup Reference Tables
-- Date: 2025-11-04
-- Reason: Scraped data has 70-100% missing values, needs manual extraction
-- This preserves the original scraper output for historical reference

-- Archive guns table
ALTER TABLE bg_reference_guns RENAME TO bg_reference_guns_scraped_archive;

-- Archive vehicles table
ALTER TABLE bg_reference_vehicles RENAME TO bg_reference_vehicles_scraped_archive;

-- Create audit table to track extraction actions
CREATE TABLE IF NOT EXISTS extraction_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    user_name TEXT
);

-- Record archive actions
INSERT INTO extraction_audit (table_name, action, notes, user_name)
VALUES
    ('bg_reference_guns', 'archived_to_bg_reference_guns_scraped_archive',
     'Scraped data archived due to 70% missing AP (German), 100% missing HE/AP (American/British/Soviet)',
     'claude_code'),
    ('bg_reference_vehicles', 'archived_to_bg_reference_vehicles_scraped_archive',
     'Scraped data archived - starting fresh with manual screenshot extraction',
     'claude_code');

-- Print summary
SELECT 'Archive complete. Tables renamed:' as message
UNION ALL
SELECT '  bg_reference_guns -> bg_reference_guns_scraped_archive'
UNION ALL
SELECT '  bg_reference_vehicles -> bg_reference_vehicles_scraped_archive'
UNION ALL
SELECT ''
UNION ALL
SELECT 'Audit records created in extraction_audit table';
