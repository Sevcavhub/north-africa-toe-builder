-- Architecture Fix: Add reference_gun_id Column
-- Enables linking artillery/guns to bg_reference_guns table
--
-- Background:
-- - 110 artillery items (23.5%) cannot use reference_vehicle_id
-- - bg_reference_guns has 57 guns with penetration data
-- - Expected gain: 50-70 items (10.7-14.9%)

BEGIN TRANSACTION;

-- Check current structure
PRAGMA table_info(equipment_battlegroup);

-- Add reference_gun_id column
ALTER TABLE equipment_battlegroup
ADD COLUMN reference_gun_id INTEGER;

-- Add reference_gun_match_confidence column
ALTER TABLE equipment_battlegroup
ADD COLUMN reference_gun_match_confidence INTEGER;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_equipment_battlegroup_reference_gun
ON equipment_battlegroup(reference_gun_id);

-- Log the schema change
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('ALTER TABLE', 'equipment_battlegroup', 'schema', 'NULL', 'reference_gun_id, reference_gun_match_confidence', 'Architecture fix for artillery linkage', datetime('now'));

-- Validate
SELECT COUNT(*) as records_affected FROM equipment_battlegroup;

COMMIT;

-- Verify new columns
PRAGMA table_info(equipment_battlegroup);

SELECT 'Architecture fix complete: reference_gun_id column added' as status;
