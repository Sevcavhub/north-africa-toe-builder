-- Migration: Add HE range columns and gun name variants table
-- Date: November 5, 2025
-- Purpose: Fix missing HE range data in bg_reference_guns and add alias support

-- ============================================================================
-- PART 1: Add HE Range Columns to bg_reference_guns
-- ============================================================================

-- Add 6 HE range columns to match AP range structure
ALTER TABLE bg_reference_guns ADD COLUMN he_0_10 INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN he_10_20 INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN he_20_30 INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN he_30_40 INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN he_40_50 INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN he_50_70 INTEGER DEFAULT NULL;

-- Add common_name column for primary alias (e.g., "2 pdr" instead of "Ordnance QF 2-pounder")
ALTER TABLE bg_reference_guns ADD COLUMN common_name TEXT DEFAULT NULL;

-- ============================================================================
-- PART 2: Create Gun Name Variants Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS gun_name_variants (
    variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gun_id INTEGER NOT NULL,
    variant_name TEXT NOT NULL UNIQUE,
    variant_source TEXT,  -- 'vehicle_weapon', 'datacard', 'manual', 'official'
    is_official BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gun_id) REFERENCES bg_reference_guns(id) ON DELETE CASCADE
);

-- Create index for fast lookups by variant name
CREATE INDEX IF NOT EXISTS idx_gun_variants_name ON gun_name_variants(variant_name);
CREATE INDEX IF NOT EXISTS idx_gun_variants_gun_id ON gun_name_variants(gun_id);

-- ============================================================================
-- PART 3: Populate Initial Variants (Optional - can be done via import script)
-- ============================================================================

-- Populate canonical names as official variants
INSERT INTO gun_name_variants (gun_id, variant_name, variant_source, is_official)
SELECT id, name, 'official', 1
FROM bg_reference_guns
WHERE name IS NOT NULL;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify HE range columns were added
SELECT sql FROM sqlite_master WHERE type='table' AND name='bg_reference_guns';

-- Verify gun_name_variants table exists
SELECT COUNT(*) as variant_count FROM gun_name_variants;

-- Show schema changes
PRAGMA table_info(bg_reference_guns);
