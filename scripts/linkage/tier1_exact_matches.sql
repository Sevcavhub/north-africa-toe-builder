-- ============================================================================
-- DATABASE LINKAGE: Tier 1 Exact Matches
-- ============================================================================
-- Date: 2025-11-03
-- Purpose: Populate equipment_battlegroup.reference_vehicle_id for exact matches
-- Method: LOWER(TRIM(name)) matching with nation validation
-- Expected: 19 records updated
-- Confidence: 100 (perfect match)
-- ============================================================================

-- ============================================================================
-- STEP 1: Create Audit Table (if not exists)
-- ============================================================================

CREATE TABLE IF NOT EXISTS normalization_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_reference_vehicle_id INTEGER,
    new_reference_vehicle_id INTEGER,
    old_confidence INTEGER,
    new_confidence INTEGER,
    match_tier TEXT,
    match_method TEXT,
    bg_vehicle_name TEXT,
    equipment_name TEXT,
    nation TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    rollback_sql TEXT,
    notes TEXT
);

-- ============================================================================
-- STEP 2: Verify Current State
-- ============================================================================

-- Expected: 469 NULL references
SELECT
    COUNT(*) as total_records,
    COUNT(reference_vehicle_id) as populated,
    COUNT(*) - COUNT(reference_vehicle_id) as null_refs
FROM equipment_battlegroup;

-- ============================================================================
-- STEP 3: Preview Tier 1 Matches
-- ============================================================================

-- Show all matches that will be updated
SELECT
    e.canonical_id,
    e.name as equipment_name,
    e.nation,
    e.category,
    MIN(brv.id) as selected_bg_id,
    MIN(brv.name) as bg_vehicle_name,
    COUNT(brv.id) as variant_count,
    GROUP_CONCAT(brv.id, ', ') as all_variant_ids
FROM equipment e
JOIN bg_reference_vehicles brv
    ON LOWER(TRIM(e.name)) = LOWER(TRIM(brv.name))
    AND e.nation = brv.nation
GROUP BY e.canonical_id, e.name, e.nation, e.category
ORDER BY e.nation, e.name;

-- Expected output: 19 rows

-- ============================================================================
-- STEP 4: Execute Tier 1 Updates with Audit Trail
-- ============================================================================

BEGIN TRANSACTION;

-- First, insert audit records for rollback capability
INSERT INTO normalization_audit (
    equipment_id,
    operation,
    old_reference_vehicle_id,
    new_reference_vehicle_id,
    old_confidence,
    new_confidence,
    match_tier,
    match_method,
    bg_vehicle_name,
    equipment_name,
    nation,
    rollback_sql,
    notes
)
SELECT
    e.canonical_id,
    'UPDATE_TIER1',
    eb.reference_vehicle_id,
    MIN(brv.id),
    eb.reference_match_confidence,
    100,
    'Tier 1',
    'exact_match_case_insensitive',
    MIN(brv.name),
    e.name,
    e.nation,
    'UPDATE equipment_battlegroup SET reference_vehicle_id = NULL, reference_match_confidence = NULL WHERE equipment_id = ''' || e.canonical_id || ''';',
    CASE
        WHEN COUNT(brv.id) > 1 THEN 'MULTIPLE_VARIANTS: Using MIN(id) = ' || MIN(brv.id) || ' from [' || GROUP_CONCAT(brv.id, ', ') || ']'
        ELSE 'SINGLE_MATCH'
    END
FROM equipment e
JOIN bg_reference_vehicles brv
    ON LOWER(TRIM(e.name)) = LOWER(TRIM(brv.name))
    AND e.nation = brv.nation
JOIN equipment_battlegroup eb
    ON eb.equipment_id = e.canonical_id
GROUP BY e.canonical_id, e.name, e.nation, eb.reference_vehicle_id, eb.reference_match_confidence;

-- Verify audit insert count (should be 19)
SELECT '>>> Audit records created: ' || CHANGES() as audit_count;

-- Now execute the actual UPDATE
UPDATE equipment_battlegroup
SET
    reference_vehicle_id = (
        SELECT MIN(brv.id)
        FROM equipment e
        JOIN bg_reference_vehicles brv
            ON LOWER(TRIM(e.name)) = LOWER(TRIM(brv.name))
            AND e.nation = brv.nation
        WHERE e.canonical_id = equipment_battlegroup.equipment_id
    ),
    reference_match_confidence = 100
WHERE equipment_id IN (
    SELECT e.canonical_id
    FROM equipment e
    JOIN bg_reference_vehicles brv
        ON LOWER(TRIM(e.name)) = LOWER(TRIM(brv.name))
        AND e.nation = brv.nation
);

-- Verify update count (should be 19)
SELECT '>>> Equipment records updated: ' || CHANGES() as update_count;

-- ============================================================================
-- STEP 5: Validation
-- ============================================================================

-- Check updated records
SELECT
    eb.equipment_id,
    e.name as equipment_name,
    e.nation,
    eb.reference_vehicle_id,
    brv.name as bg_vehicle_name,
    eb.reference_match_confidence
FROM equipment_battlegroup eb
JOIN equipment e ON eb.equipment_id = e.canonical_id
LEFT JOIN bg_reference_vehicles brv ON eb.reference_vehicle_id = brv.id
WHERE eb.reference_match_confidence = 100
ORDER BY e.nation, e.name;

-- Expected: 19 rows with reference_vehicle_id populated

-- Verify counts
SELECT
    'VALIDATION' as check_type,
    COUNT(*) as total_equipment,
    COUNT(reference_vehicle_id) as populated_refs,
    COUNT(*) - COUNT(reference_vehicle_id) as null_refs,
    ROUND(CAST(COUNT(reference_vehicle_id) AS FLOAT) / COUNT(*) * 100, 2) || '%' as percent_populated
FROM equipment_battlegroup;

-- Expected: 19 populated (4.1%), 450 NULL (95.9%)

-- ============================================================================
-- STEP 6: Commit or Rollback
-- ============================================================================

-- If validation passes, COMMIT:
COMMIT;

-- If validation fails, ROLLBACK:
-- ROLLBACK;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed later)
-- ============================================================================

-- To rollback Tier 1 changes:
--
-- BEGIN TRANSACTION;
--
-- UPDATE equipment_battlegroup
-- SET
--     reference_vehicle_id = NULL,
--     reference_match_confidence = NULL
-- WHERE equipment_id IN (
--     SELECT equipment_id
--     FROM normalization_audit
--     WHERE match_tier = 'Tier 1' AND operation = 'UPDATE_TIER1'
-- );
--
-- DELETE FROM normalization_audit
-- WHERE match_tier = 'Tier 1' AND operation = 'UPDATE_TIER1';
--
-- COMMIT;

-- ============================================================================
-- SUMMARY REPORT
-- ============================================================================

SELECT '=====================================================================' as divider
UNION ALL SELECT 'TIER 1 EXACT MATCH LINKAGE - EXECUTION SUMMARY'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT ''
UNION ALL SELECT 'Execution Date: ' || datetime('now')
UNION ALL SELECT 'Match Tier: Tier 1 (Exact Match)'
UNION ALL SELECT 'Match Method: LOWER(TRIM(name)) with nation validation'
UNION ALL SELECT 'Confidence Score: 100'
UNION ALL SELECT ''
UNION ALL SELECT 'Records Updated: ' || (SELECT COUNT(*) FROM normalization_audit WHERE match_tier = 'Tier 1' AND operation = 'UPDATE_TIER1')
UNION ALL SELECT 'Audit Records: ' || (SELECT COUNT(*) FROM normalization_audit WHERE match_tier = 'Tier 1')
UNION ALL SELECT ''
UNION ALL SELECT 'Coverage:'
UNION ALL SELECT '  Total Equipment: 469'
UNION ALL SELECT '  Populated References: ' || (SELECT COUNT(reference_vehicle_id) FROM equipment_battlegroup)
UNION ALL SELECT '  NULL References: ' || (SELECT COUNT(*) - COUNT(reference_vehicle_id) FROM equipment_battlegroup)
UNION ALL SELECT '  Percent Populated: ' || (SELECT ROUND(CAST(COUNT(reference_vehicle_id) AS FLOAT) / COUNT(*) * 100, 2) || '%' FROM equipment_battlegroup)
UNION ALL SELECT ''
UNION ALL SELECT 'By Nation:'
UNION ALL SELECT '  American: ' || (SELECT COUNT(*) FROM equipment_battlegroup eb JOIN equipment e ON eb.equipment_id = e.canonical_id WHERE e.nation = 'american' AND eb.reference_match_confidence = 100)
UNION ALL SELECT '  British: ' || (SELECT COUNT(*) FROM equipment_battlegroup eb JOIN equipment e ON eb.equipment_id = e.canonical_id WHERE e.nation = 'british' AND eb.reference_match_confidence = 100)
UNION ALL SELECT '  German: ' || (SELECT COUNT(*) FROM equipment_battlegroup eb JOIN equipment e ON eb.equipment_id = e.canonical_id WHERE e.nation = 'german' AND eb.reference_match_confidence = 100)
UNION ALL SELECT ''
UNION ALL SELECT 'Priority Test Cases:'
UNION ALL SELECT '  GBR_MATILDA_II: ' || CASE WHEN (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'GBR_MATILDA_II') IS NOT NULL THEN 'LINKED (id: ' || (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'GBR_MATILDA_II') || ')' ELSE 'NOT LINKED' END
UNION ALL SELECT '  USA_M4_SHERMAN: ' || CASE WHEN (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'USA_M4_SHERMAN') IS NOT NULL THEN 'LINKED (id: ' || (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'USA_M4_SHERMAN') || ')' ELSE 'NOT LINKED' END
UNION ALL SELECT '  GER_PANZER_III_AUSF_F: ' || CASE WHEN (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'GER_PANZER_III_AUSF_F') IS NOT NULL THEN 'LINKED (id: ' || (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'GER_PANZER_III_AUSF_F') || ')' ELSE 'NOT IN TIER 1 (needs normalization)' END
UNION ALL SELECT '  GBR_25_POUNDER: BLOCKED (artillery, no ref_gun_id column)'
UNION ALL SELECT ''
UNION ALL SELECT 'Multiple Variants Handled:'
UNION ALL SELECT '  ' || (SELECT COUNT(*) FROM normalization_audit WHERE match_tier = 'Tier 1' AND notes LIKE 'MULTIPLE_VARIANTS%') || ' equipment items had multiple BG variants (used MIN(id) strategy)'
UNION ALL SELECT ''
UNION ALL SELECT 'Next Steps:'
UNION ALL SELECT '  - Review Tier 2 normalization candidates'
UNION ALL SELECT '  - Develop Python normalization script'
UNION ALL SELECT '  - Address architecture issue (add reference_gun_id)'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT '';
