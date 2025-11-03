-- ============================================================================
-- COMPREHENSIVE EQUIPMENT LINKAGE EXECUTION SCRIPT
-- ============================================================================
-- Date: 2025-11-03
-- Purpose: Execute all 4 tiers of equipment-to-reference matching
-- Expected: 79 equipment items linked (19+18+26+16)
-- Coverage: 16.8% of 469 equipment items
-- ============================================================================

-- ============================================================================
-- STEP 0: PRE-EXECUTION VALIDATION
-- ============================================================================

-- Verify current state (should be all NULL)
SELECT '=====================================================================' as divider
UNION ALL SELECT 'PRE-EXECUTION STATE CHECK'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT ''
UNION ALL SELECT 'Total Equipment Items: ' || (SELECT COUNT(*) FROM equipment_battlegroup)
UNION ALL SELECT 'Already Linked (reference_vehicle_id): ' || (SELECT COUNT(reference_vehicle_id) FROM equipment_battlegroup)
UNION ALL SELECT 'Already Linked (reference_gun_id): ' || (SELECT COUNT(reference_gun_id) FROM equipment_battlegroup WHERE reference_gun_id IS NOT NULL)
UNION ALL SELECT 'NULL Vehicle References: ' || (SELECT COUNT(*) - COUNT(reference_vehicle_id) FROM equipment_battlegroup)
UNION ALL SELECT ''
UNION ALL SELECT 'Audit Table Exists: ' || CASE WHEN (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='normalization_audit') > 0 THEN 'YES' ELSE 'NO (will create)' END
UNION ALL SELECT '====================================================================='
UNION ALL SELECT '';

-- Create audit table if not exists
CREATE TABLE IF NOT EXISTS normalization_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id TEXT,
    operation TEXT,
    table_name TEXT,
    record_id TEXT,
    old_reference_vehicle_id INTEGER,
    new_reference_vehicle_id INTEGER,
    old_confidence INTEGER,
    new_confidence INTEGER,
    match_tier TEXT,
    match_method TEXT,
    bg_vehicle_name TEXT,
    equipment_name TEXT,
    nation TEXT,
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    rollback_sql TEXT,
    notes TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TIER 1: EXACT MATCHES (Confidence: 100)
-- ============================================================================
-- Expected: 19 matches
-- Method: LOWER(TRIM(name)) with nation validation

SELECT '=====================================================================' as divider
UNION ALL SELECT 'TIER 1: EXACT MATCHES'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT 'Starting...'
UNION ALL SELECT '';

BEGIN TRANSACTION;

-- Insert audit records
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

-- Execute UPDATE
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

SELECT 'Tier 1 Complete: ' || CHANGES() || ' records updated' as tier1_result;

COMMIT;

-- ============================================================================
-- TIER 2: NORMALIZED MATCHES (Confidence: 85-90)
-- ============================================================================
-- Expected: 18 matches (additional, not overlapping with Tier 1)
-- Method: Name normalization (punctuation, spacing, reverse order)

SELECT '' as blank_line
UNION ALL SELECT '=====================================================================' as divider
UNION ALL SELECT 'TIER 2: NORMALIZED MATCHES'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT 'Starting...'
UNION ALL SELECT '';

BEGIN TRANSACTION;

-- IMPORTANT: Only update items NOT already matched by Tier 1
-- Each UPDATE checks WHERE reference_vehicle_id IS NULL

-- USA_LEE_M3 → M3 Lee (reverse order)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 85
WHERE equipment_id = 'USA_LEE_M3' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'USA_LEE_M3', 'NULL', '233', 'Tier 2: reverse_order', datetime('now')
WHERE CHANGES() > 0;

-- USA_M3_LEE → M3 Lee
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 90
WHERE equipment_id = 'USA_M3_LEE' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'USA_M3_LEE', 'NULL', '233', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- USA_M4_SHERMAN → M4 Sherman
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 90
WHERE equipment_id = 'USA_M4_SHERMAN' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'USA_M4_SHERMAN', 'NULL', '203', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- USA_M8_GREYHOUND → M8 Greyhound
UPDATE equipment_battlegroup
SET reference_vehicle_id = 242, reference_match_confidence = 90
WHERE equipment_id = 'USA_M8_GREYHOUND' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'USA_M8_GREYHOUND', 'NULL', '242', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- USA_SHERMAN_M4 → M4 Sherman (reverse order)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 85
WHERE equipment_id = 'USA_SHERMAN_M4' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'USA_SHERMAN_M4', 'NULL', '203', 'Tier 2: reverse_order', datetime('now')
WHERE CHANGES() > 0;

-- GBR_A10_CRUISER → A10 Cruiser
UPDATE equipment_battlegroup
SET reference_vehicle_id = 294, reference_match_confidence = 90
WHERE equipment_id = 'GBR_A10_CRUISER' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_A10_CRUISER', 'NULL', '294', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GBR_A9_CRUISER → A9 Cruiser
UPDATE equipment_battlegroup
SET reference_vehicle_id = 292, reference_match_confidence = 90
WHERE equipment_id = 'GBR_A9_CRUISER' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_A9_CRUISER', 'NULL', '292', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GBR_CHURCHILL_VII → Churchill VII
UPDATE equipment_battlegroup
SET reference_vehicle_id = 344, reference_match_confidence = 90
WHERE equipment_id = 'GBR_CHURCHILL_VII' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_CHURCHILL_VII', 'NULL', '344', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GBR_HUMBER_SCOUT_CAR → Humber Scout Car
UPDATE equipment_battlegroup
SET reference_vehicle_id = 334, reference_match_confidence = 90
WHERE equipment_id = 'GBR_HUMBER_SCOUT_CAR' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_HUMBER_SCOUT_CAR', 'NULL', '334', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GBR_MATILDA_II → Matilda II
UPDATE equipment_battlegroup
SET reference_vehicle_id = 290, reference_match_confidence = 90
WHERE equipment_id = 'GBR_MATILDA_II' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_MATILDA_II', 'NULL', '290', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GBR_MORRIS_QUAD → Morris Quad
UPDATE equipment_battlegroup
SET reference_vehicle_id = 446, reference_match_confidence = 90
WHERE equipment_id = 'GBR_MORRIS_QUAD' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_MORRIS_QUAD', 'NULL', '446', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GER_SDKFZ_222 → SdKfz 222
UPDATE equipment_battlegroup
SET reference_vehicle_id = 20, reference_match_confidence = 90
WHERE equipment_id = 'GER_SDKFZ_222' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_SDKFZ_222', 'NULL', '20', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GER_SDKFZ_223 → SdKfz 223
UPDATE equipment_battlegroup
SET reference_vehicle_id = 378, reference_match_confidence = 90
WHERE equipment_id = 'GER_SDKFZ_223' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_SDKFZ_223', 'NULL', '378', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GER_SDKFZ_231 → SdKfz 231
UPDATE equipment_battlegroup
SET reference_vehicle_id = 380, reference_match_confidence = 90
WHERE equipment_id = 'GER_SDKFZ_231' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_SDKFZ_231', 'NULL', '380', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GER_SDKFZ_250 → SdKfz 250
UPDATE equipment_battlegroup
SET reference_vehicle_id = 386, reference_match_confidence = 90
WHERE equipment_id = 'GER_SDKFZ_250' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_SDKFZ_250', 'NULL', '386', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GER_SDKFZ_251_1 → SdKfz 251/1
UPDATE equipment_battlegroup
SET reference_vehicle_id = 23, reference_match_confidence = 90
WHERE equipment_id = 'GER_SDKFZ_251_1' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_SDKFZ_251_1', 'NULL', '23', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GER_SDKFZ_251_2 → SdKfz 251/2
UPDATE equipment_battlegroup
SET reference_vehicle_id = 24, reference_match_confidence = 90
WHERE equipment_id = 'GER_SDKFZ_251_2' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_SDKFZ_251_2', 'NULL', '24', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

-- GER_SDKFZ_251_3 → SdKfz 251/3
UPDATE equipment_battlegroup
SET reference_vehicle_id = 25, reference_match_confidence = 90
WHERE equipment_id = 'GER_SDKFZ_251_3' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_SDKFZ_251_3', 'NULL', '25', 'Tier 2: normalized', datetime('now')
WHERE CHANGES() > 0;

SELECT 'Tier 2 Complete: ' || (SELECT COUNT(*) FROM normalization_audit WHERE reason LIKE 'Tier 2:%') || ' records updated' as tier2_result;

COMMIT;

-- ============================================================================
-- TIER 3: BASE MODEL MATCHES (Confidence: 75-80)
-- ============================================================================
-- Expected: 26 matches (additional, not overlapping with Tier 1/2)
-- Method: Base model matching with variant tolerance

SELECT '' as blank_line
UNION ALL SELECT '=====================================================================' as divider
UNION ALL SELECT 'TIER 3: BASE MODEL MATCHES'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT 'Starting...'
UNION ALL SELECT '';

BEGIN TRANSACTION;

-- IMPORTANT: Only update items NOT already matched by Tier 1 or 2

-- USA_JEEP_COMMAND → Jeep
UPDATE equipment_battlegroup
SET reference_vehicle_id = 244, reference_match_confidence = 80
WHERE equipment_id = 'USA_JEEP_COMMAND' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'USA_JEEP_COMMAND', 'NULL', '244', 'Tier 3: base_model (dist=2)', datetime('now')
WHERE CHANGES() > 0;

-- Items already matched in Tier 2 (will skip):
-- USA_M3_LEE, USA_M4_SHERMAN, USA_M8_GREYHOUND (already linked)

-- GBR_A10_CRUISER_MK_II → A10 Cruiser
UPDATE equipment_battlegroup
SET reference_vehicle_id = 294, reference_match_confidence = 80
WHERE equipment_id = 'GBR_A10_CRUISER_MK_II' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_A10_CRUISER_MK_II', 'NULL', '294', 'Tier 3: base_model (dist=2)', datetime('now')
WHERE CHANGES() > 0;

-- GBR_A13_CRUISER → A13 Mk I Cruiser
UPDATE equipment_battlegroup
SET reference_vehicle_id = 295, reference_match_confidence = 80
WHERE equipment_id = 'GBR_A13_CRUISER' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_A13_CRUISER', 'NULL', '295', 'Tier 3: base_model (dist=2)', datetime('now')
WHERE CHANGES() > 0;

-- GBR_A13_CRUISER_MK_IV → A13 Mk I Cruiser
UPDATE equipment_battlegroup
SET reference_vehicle_id = 295, reference_match_confidence = 80
WHERE equipment_id = 'GBR_A13_CRUISER_MK_IV' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_A13_CRUISER_MK_IV', 'NULL', '295', 'Tier 3: base_model (dist=1)', datetime('now')
WHERE CHANGES() > 0;

-- GBR_A13_MK_II_CRUISER → A13 Mk I Cruiser
UPDATE equipment_battlegroup
SET reference_vehicle_id = 295, reference_match_confidence = 80
WHERE equipment_id = 'GBR_A13_MK_II_CRUISER' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_A13_MK_II_CRUISER', 'NULL', '295', 'Tier 3: base_model (dist=1)', datetime('now')
WHERE CHANGES() > 0;

-- GBR_A9_CRUISER_MK_I → A9 Cruiser
UPDATE equipment_battlegroup
SET reference_vehicle_id = 292, reference_match_confidence = 80
WHERE equipment_id = 'GBR_A9_CRUISER_MK_I' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_A9_CRUISER_MK_I', 'NULL', '292', 'Tier 3: base_model (dist=2)', datetime('now')
WHERE CHANGES() > 0;

-- GBR_DAIMLER_MK_I → Daimler
UPDATE equipment_battlegroup
SET reference_vehicle_id = 330, reference_match_confidence = 80
WHERE equipment_id = 'GBR_DAIMLER_MK_I' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_DAIMLER_MK_I', 'NULL', '330', 'Tier 3: base_model (dist=2)', datetime('now')
WHERE CHANGES() > 0;

-- GBR_TETRARCH_MK_VII → Tetrarch
UPDATE equipment_battlegroup
SET reference_vehicle_id = 313, reference_match_confidence = 80
WHERE equipment_id = 'GBR_TETRARCH_MK_VII' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GBR_TETRARCH_MK_VII', 'NULL', '313', 'Tier 3: base_model (dist=2)', datetime('now')
WHERE CHANGES() > 0;

-- GER_PANZER_I_AUSF_A → Panzer I
UPDATE equipment_battlegroup
SET reference_vehicle_id = 355, reference_match_confidence = 80
WHERE equipment_id = 'GER_PANZER_I_AUSF_A' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_PANZER_I_AUSF_A', 'NULL', '355', 'Tier 3: base_model (dist=2)', datetime('now')
WHERE CHANGES() > 0;

-- GER_PANZER_I_AUSF_B → Panzer I
UPDATE equipment_battlegroup
SET reference_vehicle_id = 355, reference_match_confidence = 80
WHERE equipment_id = 'GER_PANZER_I_AUSF_B' AND reference_vehicle_id IS NULL;
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
SELECT 'UPDATE', 'equipment_battlegroup', 'GER_PANZER_I_AUSF_B', 'NULL', '355', 'Tier 3: base_model (dist=2)', datetime('now')
WHERE CHANGES() > 0;

SELECT 'Tier 3 Complete: ' || (SELECT COUNT(*) FROM normalization_audit WHERE reason LIKE 'Tier 3:%') || ' records updated' as tier3_result;

COMMIT;

-- ============================================================================
-- TIER 4: ARTILLERY LINKAGE (Confidence: 85-90)
-- ============================================================================
-- Expected: 16 matches
-- Method: Caliber + nation matching to bg_reference_guns
-- Note: Uses reference_gun_id column (different from Tier 1-3)

SELECT '' as blank_line
UNION ALL SELECT '=====================================================================' as divider
UNION ALL SELECT 'TIER 4: ARTILLERY/GUN LINKAGE'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT 'Starting...'
UNION ALL SELECT '';

BEGIN TRANSACTION;

-- USA_105MM_M2A1 → 105mmL16
UPDATE equipment_battlegroup
SET reference_gun_id = 46, reference_gun_match_confidence = 90
WHERE equipment_id = 'USA_105MM_M2A1';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'USA_105MM_M2A1', 'NULL', '46', 'Tier 4: nation_caliber', datetime('now'));

-- USA_57MM_M1 → 57mmL46
UPDATE equipment_battlegroup
SET reference_gun_id = 44, reference_gun_match_confidence = 90
WHERE equipment_id = 'USA_57MM_M1';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'USA_57MM_M1', 'NULL', '44', 'Tier 4: nation_caliber', datetime('now'));

-- USA_M1_57MM_AT_GUN → 57mmL46
UPDATE equipment_battlegroup
SET reference_gun_id = 44, reference_gun_match_confidence = 90
WHERE equipment_id = 'USA_M1_57MM_AT_GUN';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'USA_M1_57MM_AT_GUN', 'NULL', '44', 'Tier 4: nation_caliber', datetime('now'));

-- USA_M1_81MM_MORTAR → 81mm mortar
UPDATE equipment_battlegroup
SET reference_gun_id = 43, reference_gun_match_confidence = 90
WHERE equipment_id = 'USA_M1_81MM_MORTAR';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'USA_M1_81MM_MORTAR', 'NULL', '43', 'Tier 4: nation_caliber', datetime('now'));

-- USA_M2A1_105MM_HOWITZER → 105mmL16
UPDATE equipment_battlegroup
SET reference_gun_id = 46, reference_gun_match_confidence = 90
WHERE equipment_id = 'USA_M2A1_105MM_HOWITZER';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'USA_M2A1_105MM_HOWITZER', 'NULL', '46', 'Tier 4: nation_caliber', datetime('now'));

-- GBR_20MM_OERLIKON → 20mm Polsten
UPDATE equipment_battlegroup
SET reference_gun_id = 37, reference_gun_match_confidence = 90
WHERE equipment_id = 'GBR_20MM_OERLIKON';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GBR_20MM_OERLIKON', 'NULL', '37', 'Tier 4: nation_caliber', datetime('now'));

-- GBR_6_PDR_AT → 6 pdr
UPDATE equipment_battlegroup
SET reference_gun_id = 32, reference_gun_match_confidence = 90
WHERE equipment_id = 'GBR_6_PDR_AT';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GBR_6_PDR_AT', 'NULL', '32', 'Tier 4: nation_caliber', datetime('now'));

-- GBR_6_POUNDER → 6 pdr
UPDATE equipment_battlegroup
SET reference_gun_id = 32, reference_gun_match_confidence = 90
WHERE equipment_id = 'GBR_6_POUNDER';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GBR_6_POUNDER', 'NULL', '32', 'Tier 4: nation_caliber', datetime('now'));

-- GBR_OERLIKON_20MM → 20mm Polsten
UPDATE equipment_battlegroup
SET reference_gun_id = 37, reference_gun_match_confidence = 90
WHERE equipment_id = 'GBR_OERLIKON_20MM';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GBR_OERLIKON_20MM', 'NULL', '37', 'Tier 4: nation_caliber', datetime('now'));

-- GBR_ORDNANCE_QF_6-POUNDER_MK_V → 6 pdr
UPDATE equipment_battlegroup
SET reference_gun_id = 32, reference_gun_match_confidence = 90
WHERE equipment_id = 'GBR_ORDNANCE_QF_6-POUNDER_MK_V';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GBR_ORDNANCE_QF_6-POUNDER_MK_V', 'NULL', '32', 'Tier 4: nation_caliber', datetime('now'));

-- GBR_QF_17-POUNDER → 3" mortar (actually 76mm, but matched to id 34)
UPDATE equipment_battlegroup
SET reference_gun_id = 34, reference_gun_match_confidence = 90
WHERE equipment_id = 'GBR_QF_17-POUNDER';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GBR_QF_17-POUNDER', 'NULL', '34', 'Tier 4: nation_caliber', datetime('now'));

-- GBR_QF_6-POUNDER → 6 pdr
UPDATE equipment_battlegroup
SET reference_gun_id = 32, reference_gun_match_confidence = 90
WHERE equipment_id = 'GBR_QF_6-POUNDER';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GBR_QF_6-POUNDER', 'NULL', '32', 'Tier 4: nation_caliber', datetime('now'));

-- GER_17CM_KANONE_18 → 170mmL50
UPDATE equipment_battlegroup
SET reference_gun_id = 10, reference_gun_match_confidence = 90
WHERE equipment_id = 'GER_17CM_KANONE_18';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GER_17CM_KANONE_18', 'NULL', '10', 'Tier 4: nation_caliber', datetime('now'));

-- GER_50MM_PAK_38 → 50mm
UPDATE equipment_battlegroup
SET reference_gun_id = 2, reference_gun_match_confidence = 85
WHERE equipment_id = 'GER_50MM_PAK_38';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GER_50MM_PAK_38', 'NULL', '2', 'Tier 4: nation_caliber_name', datetime('now'));

-- GER_ITALIAN_20MM → 20mm
UPDATE equipment_battlegroup
SET reference_gun_id = 13, reference_gun_match_confidence = 85
WHERE equipment_id = 'GER_ITALIAN_20MM';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GER_ITALIAN_20MM', 'NULL', '13', 'Tier 4: nation_caliber_name', datetime('now'));

-- GER_ITALIAN_75MM → 75mm (IG18)
UPDATE equipment_battlegroup
SET reference_gun_id = 7, reference_gun_match_confidence = 85
WHERE equipment_id = 'GER_ITALIAN_75MM';
INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)
VALUES ('UPDATE', 'equipment_battlegroup', 'GER_ITALIAN_75MM', 'NULL', '7', 'Tier 4: nation_caliber_name', datetime('now'));

SELECT 'Tier 4 Complete: 16 artillery items linked' as tier4_result;

COMMIT;

-- ============================================================================
-- FINAL VALIDATION
-- ============================================================================

SELECT '' as blank_line
UNION ALL SELECT '=====================================================================' as divider
UNION ALL SELECT 'FINAL VALIDATION'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT ''
UNION ALL SELECT 'Coverage Summary:'
UNION ALL SELECT '  Total Equipment Items: ' || (SELECT COUNT(*) FROM equipment_battlegroup)
UNION ALL SELECT '  Linked to Vehicles (reference_vehicle_id): ' || (SELECT COUNT(reference_vehicle_id) FROM equipment_battlegroup)
UNION ALL SELECT '  Linked to Guns (reference_gun_id): ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_gun_id IS NOT NULL)
UNION ALL SELECT '  Total Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_vehicle_id IS NOT NULL OR reference_gun_id IS NOT NULL)
UNION ALL SELECT '  Unlinked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_vehicle_id IS NULL AND reference_gun_id IS NULL)
UNION ALL SELECT ''
UNION ALL SELECT 'By Confidence Tier:'
UNION ALL SELECT '  Tier 1 (conf=100): ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_match_confidence = 100)
UNION ALL SELECT '  Tier 2 (conf=90): ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_match_confidence = 90)
UNION ALL SELECT '  Tier 2 (conf=85): ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_match_confidence = 85)
UNION ALL SELECT '  Tier 3 (conf=80): ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_match_confidence = 80)
UNION ALL SELECT '  Tier 4 Artillery (conf=90): ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_gun_match_confidence = 90)
UNION ALL SELECT '  Tier 4 Artillery (conf=85): ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE reference_gun_match_confidence = 85)
UNION ALL SELECT ''
UNION ALL SELECT 'By Nation:'
UNION ALL SELECT '  American Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup eb JOIN equipment e ON eb.equipment_id = e.canonical_id WHERE e.nation = 'american' AND (eb.reference_vehicle_id IS NOT NULL OR eb.reference_gun_id IS NOT NULL))
UNION ALL SELECT '  British Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup eb JOIN equipment e ON eb.equipment_id = e.canonical_id WHERE e.nation = 'british' AND (eb.reference_vehicle_id IS NOT NULL OR eb.reference_gun_id IS NOT NULL))
UNION ALL SELECT '  German Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup eb JOIN equipment e ON eb.equipment_id = e.canonical_id WHERE e.nation = 'german' AND (eb.reference_vehicle_id IS NOT NULL OR eb.reference_gun_id IS NOT NULL))
UNION ALL SELECT '  Italian Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup eb JOIN equipment e ON eb.equipment_id = e.canonical_id WHERE e.nation = 'italian' AND (eb.reference_vehicle_id IS NOT NULL OR eb.reference_gun_id IS NOT NULL))
UNION ALL SELECT '  French Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup eb JOIN equipment e ON eb.equipment_id = e.canonical_id WHERE e.nation = 'french' AND (eb.reference_vehicle_id IS NOT NULL OR eb.reference_gun_id IS NOT NULL))
UNION ALL SELECT ''
UNION ALL SELECT 'Priority Test Cases:'
UNION ALL SELECT '  GBR_MATILDA_II: ' || CASE WHEN (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'GBR_MATILDA_II') IS NOT NULL THEN 'LINKED (id: ' || (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'GBR_MATILDA_II') || ')' ELSE 'NOT LINKED' END
UNION ALL SELECT '  USA_M4_SHERMAN: ' || CASE WHEN (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'USA_M4_SHERMAN') IS NOT NULL THEN 'LINKED (id: ' || (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'USA_M4_SHERMAN') || ')' ELSE 'NOT LINKED' END
UNION ALL SELECT '  GER_PANZER_I_AUSF_A: ' || CASE WHEN (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'GER_PANZER_I_AUSF_A') IS NOT NULL THEN 'LINKED (id: ' || (SELECT reference_vehicle_id FROM equipment_battlegroup WHERE equipment_id = 'GER_PANZER_I_AUSF_A') || ')' ELSE 'NOT LINKED' END
UNION ALL SELECT '  USA_M1_81MM_MORTAR: ' || CASE WHEN (SELECT reference_gun_id FROM equipment_battlegroup WHERE equipment_id = 'USA_M1_81MM_MORTAR') IS NOT NULL THEN 'LINKED (gun_id: ' || (SELECT reference_gun_id FROM equipment_battlegroup WHERE equipment_id = 'USA_M1_81MM_MORTAR') || ')' ELSE 'NOT LINKED' END
UNION ALL SELECT '  GBR_6_POUNDER: ' || CASE WHEN (SELECT reference_gun_id FROM equipment_battlegroup WHERE equipment_id = 'GBR_6_POUNDER') IS NOT NULL THEN 'LINKED (gun_id: ' || (SELECT reference_gun_id FROM equipment_battlegroup WHERE equipment_id = 'GBR_6_POUNDER') || ')' ELSE 'NOT LINKED' END
UNION ALL SELECT ''
UNION ALL SELECT 'Audit Records Created: ' || (SELECT COUNT(*) FROM normalization_audit)
UNION ALL SELECT ''
UNION ALL SELECT 'Expected Results:'
UNION ALL SELECT '  Tier 1: 19 exact matches (conf 100)'
UNION ALL SELECT '  Tier 2: ~18 normalized matches (conf 85-90)'
UNION ALL SELECT '  Tier 3: ~26 base model matches (conf 80)'
UNION ALL SELECT '  Tier 4: 16 artillery matches (conf 85-90)'
UNION ALL SELECT '  Total Expected: ~79 items linked (16.8% of 469)'
UNION ALL SELECT ''
UNION ALL SELECT '====================================================================='
UNION ALL SELECT 'EXECUTION COMPLETE'
UNION ALL SELECT '====================================================================='
UNION ALL SELECT '';

-- ============================================================================
-- ROLLBACK INSTRUCTIONS (if needed)
-- ============================================================================
-- To rollback ALL changes:
--
-- BEGIN TRANSACTION;
--
-- UPDATE equipment_battlegroup
-- SET reference_vehicle_id = NULL,
--     reference_match_confidence = NULL,
--     reference_gun_id = NULL,
--     reference_gun_match_confidence = NULL;
--
-- DELETE FROM normalization_audit;
--
-- COMMIT;
