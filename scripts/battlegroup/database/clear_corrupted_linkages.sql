-- Clear Corrupted Equipment Linkages
-- Date: 2025-11-04
-- Reason: HE/AP values populated from corrupted reference data (70-100% missing values)
-- Impact: ~99 of 191 items (52%) have potentially incorrect weapon stats

-- =============================================================================
-- Step 1: Identify affected equipment
-- =============================================================================

-- Show equipment with HE/AP values that will be cleared
SELECT 'Equipment items with HE/AP values to be cleared:' as message
UNION ALL
SELECT '  Total items with HE/AP: ' || COUNT(*)
FROM equipment_battlegroup
WHERE he_value IS NOT NULL OR ap_0_10 IS NOT NULL;

-- Show specific examples of corrupted data
SELECT ''
UNION ALL
SELECT 'Examples of corrupted entries (transport with artillery guns):'
UNION ALL
SELECT '  Item 468: ' || (SELECT name FROM equipment WHERE id = 468) ||
       ' - HE: ' || (SELECT he_value FROM equipment_battlegroup WHERE equipment_id = 468) ||
       ', AP: ' || (SELECT ap_0_10 FROM equipment_battlegroup WHERE equipment_id = 468)
FROM equipment_battlegroup WHERE equipment_id = 468 LIMIT 1;

-- =============================================================================
-- Step 2: Clear HE/AP values populated from corrupted reference data
-- =============================================================================

-- Clear ALL HE/AP values (will repopulate after manual extraction)
UPDATE equipment_battlegroup
SET
    he_value = NULL,
    ap_0_10 = NULL,
    ap_10_20 = NULL,
    ap_20_30 = NULL,
    ap_30_40 = NULL,
    ap_40_50 = NULL,
    ap_50_70 = NULL,
    reference_gun_id = NULL
WHERE
    -- Clear anything with HE/AP values
    he_value IS NOT NULL
    OR ap_0_10 IS NOT NULL
    OR ap_10_20 IS NOT NULL
    OR ap_20_30 IS NOT NULL
    OR ap_30_40 IS NOT NULL
    OR ap_40_50 IS NOT NULL
    OR ap_50_70 IS NOT NULL
    OR reference_gun_id IS NOT NULL;

-- =============================================================================
-- Step 3: Clear vehicle linkages (will re-link after manual extraction)
-- =============================================================================

UPDATE equipment_battlegroup
SET reference_vehicle_id = NULL
WHERE reference_vehicle_id IS NOT NULL;

-- =============================================================================
-- Step 4: Record cleanup in audit log
-- =============================================================================

INSERT INTO extraction_audit (table_name, action, notes, user_name)
VALUES
    ('equipment_battlegroup', 'cleared_he_ap_values',
     'Cleared HE/AP values populated from corrupted bg_reference_guns (70-100% missing data)',
     'claude_code'),
    ('equipment_battlegroup', 'cleared_reference_gun_linkages',
     'Cleared reference_gun_id linkages to corrupted data',
     'claude_code'),
    ('equipment_battlegroup', 'cleared_reference_vehicle_linkages',
     'Cleared reference_vehicle_id linkages - will re-link after manual extraction',
     'claude_code');

-- =============================================================================
-- Step 5: Verification
-- =============================================================================

-- Show cleanup results
SELECT ''
UNION ALL
SELECT 'Cleanup complete:' as message
UNION ALL
SELECT '  Items with HE/AP after cleanup: ' || COUNT(*)
FROM equipment_battlegroup
WHERE he_value IS NOT NULL OR ap_0_10 IS NOT NULL
UNION ALL
SELECT '  Items with reference_gun_id after cleanup: ' || COUNT(*)
FROM equipment_battlegroup
WHERE reference_gun_id IS NOT NULL
UNION ALL
SELECT '  Items with reference_vehicle_id after cleanup: ' || COUNT(*)
FROM equipment_battlegroup
WHERE reference_vehicle_id IS NOT NULL
UNION ALL
SELECT ''
UNION ALL
SELECT 'Status: Ready for fresh HE/AP population after manual extraction';
