-- Migration 4: Add ROF, weapon_category, and metadata columns to bg_reference_guns
-- Date: 2025-11-06
-- Purpose: Support British guns import with full schema

-- Add ROF (Rate of Fire) column
ALTER TABLE bg_reference_guns ADD COLUMN rof INTEGER DEFAULT NULL;

-- Add weapon category classification columns
ALTER TABLE bg_reference_guns ADD COLUMN weapon_category TEXT DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN category_confidence INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN gun_role TEXT DEFAULT NULL;

-- Add range and special rules columns
ALTER TABLE bg_reference_guns ADD COLUMN max_range_inches INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN special_rules TEXT DEFAULT NULL;

-- Add metadata columns for provenance tracking
ALTER TABLE bg_reference_guns ADD COLUMN import_date TEXT DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN import_source TEXT DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN validation_notes TEXT DEFAULT NULL;
