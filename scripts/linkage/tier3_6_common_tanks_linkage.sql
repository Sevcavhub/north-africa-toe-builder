-- Common Tanks Linkage (Tier 3.6 - Manual)
-- Generated for Phase 9B weapon data fix
-- Links common tanks including lend-lease equipment (cross-nation matching)

BEGIN TRANSACTION;

-- ============================================================================
-- AMERICAN SHERMAN VARIANTS (Lend-Lease to British)
-- ============================================================================

-- Sherman M4 (British) -> M4 Sherman (ID 203, American)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 90
WHERE equipment_id = 'GBR_SHERMAN_M4' AND reference_vehicle_id IS NULL;

-- Sherman M4A1 (British) -> M4 Sherman (ID 203, American - closest match)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 85
WHERE equipment_id = 'GBR_SHERMAN_M4A1' AND reference_vehicle_id IS NULL;

-- Sherman I (M4) (British) -> M4 Sherman (ID 203)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 90
WHERE equipment_id = 'GBR_SHERMAN_I_M4' AND reference_vehicle_id IS NULL;

-- Sherman II (M4A1) (British) -> M4 Sherman (ID 203)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 85
WHERE equipment_id = 'GBR_SHERMAN_II_M4A1' AND reference_vehicle_id IS NULL;

-- Sherman III (M4A4) (British) -> M4 Sherman (ID 203)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 85
WHERE equipment_id = 'GBR_SHERMAN_III_M4A4' AND reference_vehicle_id IS NULL;

-- M4 Sherman (USA) -> M4 Sherman (ID 203)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 100
WHERE equipment_id = 'USA_M4_SHERMAN' AND reference_vehicle_id IS NULL;

-- M4A1 Sherman (USA) -> M4 Sherman (ID 203)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 90
WHERE equipment_id = 'USA_M4A1_SHERMAN' AND reference_vehicle_id IS NULL;

-- Sherman M4A1 (USA) -> M4 Sherman (ID 203)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 203, reference_match_confidence = 90
WHERE equipment_id = 'USA_SHERMAN_M4A1' AND reference_vehicle_id IS NULL;

-- ============================================================================
-- GRANT / LEE VARIANTS (Lend-Lease to British)
-- ============================================================================

-- Grant M3 (British) -> M3 Lee (ID 233, American)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 90
WHERE equipment_id = 'GBR_GRANT_M3' AND reference_vehicle_id IS NULL;

-- M3 Grant (British) -> M3 Lee (ID 233)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 90
WHERE equipment_id = 'GBR_M3_GRANT' AND reference_vehicle_id IS NULL;

-- Grant M3 Lee (British) -> M3 Lee (ID 233)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 90
WHERE equipment_id = 'GBR_GRANT_M3_LEE' AND reference_vehicle_id IS NULL;

-- Grant Mk I (British) -> M3 Lee (ID 233)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 85
WHERE equipment_id = 'GBR_GRANT_MK_I' AND reference_vehicle_id IS NULL;

-- Grant Mk II (British) -> M3 Lee (ID 233)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 85
WHERE equipment_id = 'GBR_GRANT_MK_II' AND reference_vehicle_id IS NULL;

-- M3 Lee/Grant (USA) -> M3 Lee (ID 233)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 100
WHERE equipment_id = 'USA_M3_LEE_GRANT' AND reference_vehicle_id IS NULL;

-- M3A1 Lee (USA) -> M3 Lee (ID 233)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 233, reference_match_confidence = 95
WHERE equipment_id = 'USA_M3A1_LEE' AND reference_vehicle_id IS NULL;

-- ============================================================================
-- BRITISH CRUSADER VARIANTS
-- ============================================================================

-- Crusader I -> Crusader (ID 298)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 298, reference_match_confidence = 90
WHERE equipment_id = 'GBR_CRUSADER_I' AND reference_vehicle_id IS NULL;

-- Crusader II -> Crusader (ID 298)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 298, reference_match_confidence = 90
WHERE equipment_id = 'GBR_CRUSADER_II' AND reference_vehicle_id IS NULL;

-- Crusader III -> Crusader III (ID 299)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 299, reference_match_confidence = 100
WHERE equipment_id = 'GBR_CRUSADER_III' AND reference_vehicle_id IS NULL;

-- A15 Crusader Mk I -> Crusader (ID 298)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 298, reference_match_confidence = 90
WHERE equipment_id = 'GBR_A15_CRUSADER_MK_I' AND reference_vehicle_id IS NULL;

-- Crusader Mk I -> Crusader (ID 298)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 298, reference_match_confidence = 90
WHERE equipment_id = 'GBR_CRUSADER_MK_I' AND reference_vehicle_id IS NULL;

-- Crusader Mk II -> Crusader (ID 298)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 298, reference_match_confidence = 90
WHERE equipment_id = 'GBR_CRUSADER_MK_II' AND reference_vehicle_id IS NULL;

-- Crusader Mk III -> Crusader III (ID 299)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 299, reference_match_confidence = 100
WHERE equipment_id = 'GBR_CRUSADER_MK_III' AND reference_vehicle_id IS NULL;

-- ============================================================================
-- BRITISH MATILDA VARIANTS
-- ============================================================================

-- Matilda Mk II -> Matilda II (ID 290)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 290, reference_match_confidence = 100
WHERE equipment_id = 'GBR_MATILDA_MK_II' AND reference_vehicle_id IS NULL;

-- A12 Matilda II -> Matilda II (ID 290)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 290, reference_match_confidence = 100
WHERE equipment_id = 'GBR_A12_MATILDA_II' AND reference_vehicle_id IS NULL;

-- ============================================================================
-- BRITISH VALENTINE VARIANTS
-- ============================================================================

-- Valentine I -> Valentine (ID 308)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 308, reference_match_confidence = 90
WHERE equipment_id = 'GBR_VALENTINE_I' AND reference_vehicle_id IS NULL;

-- Valentine II -> Valentine (ID 308)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 308, reference_match_confidence = 90
WHERE equipment_id = 'GBR_VALENTINE_II' AND reference_vehicle_id IS NULL;

-- ============================================================================
-- BRITISH CHURCHILL VARIANTS
-- ============================================================================

-- Churchill IV -> Churchill III (ID 342, closest match)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 342, reference_match_confidence = 85
WHERE equipment_id = 'GBR_CHURCHILL_IV' AND reference_vehicle_id IS NULL;

-- Churchill Mk IV -> Churchill III (ID 342)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 342, reference_match_confidence = 85
WHERE equipment_id = 'GBR_CHURCHILL_MK_IV' AND reference_vehicle_id IS NULL;

-- ============================================================================
-- BRITISH LIGHT TANKS
-- ============================================================================

-- Light Mk VI -> Light Mk VI (ID 287)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 287, reference_match_confidence = 100
WHERE equipment_id = 'GBR_LIGHT_MK_VI' AND reference_vehicle_id IS NULL;

-- Light Tank Mk VI -> Light Mk VI (ID 287)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 287, reference_match_confidence = 100
WHERE equipment_id = 'GBR_LIGHT_TANK_MK_VI' AND reference_vehicle_id IS NULL;

-- Light Tank Mk6 -> Light Mk VI (ID 287)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 287, reference_match_confidence = 100
WHERE equipment_id = 'GBR_LIGHT_TANK_MK6' AND reference_vehicle_id IS NULL;

-- Light Tank Mk6b -> Light Mk VI (ID 287)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 287, reference_match_confidence = 95
WHERE equipment_id = 'GBR_LIGHT_TANK_MK6B' AND reference_vehicle_id IS NULL;

-- Light Tank Mk6c -> Light Mk VI (ID 287)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 287, reference_match_confidence = 95
WHERE equipment_id = 'GBR_LIGHT_TANK_MK6C' AND reference_vehicle_id IS NULL;

-- ============================================================================
-- BRITISH CRUISER TANKS (A9, A10, A13)
-- ============================================================================

-- A9 -> A9 Cruiser (ID 292)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 292, reference_match_confidence = 100
WHERE equipment_id = 'GBR_A9' AND reference_vehicle_id IS NULL;

-- A10 -> A10 Cruiser (ID 294)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 294, reference_match_confidence = 100
WHERE equipment_id = 'GBR_A10' AND reference_vehicle_id IS NULL;

-- A13 Cruiser Mk1 -> A13 Mk I Cruiser (ID 295)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 295, reference_match_confidence = 90
WHERE equipment_id = 'GBR_A13_CRUISER_MK1' AND reference_vehicle_id IS NULL;

-- A13 Cruiser Mk2 -> A13 Mk I Cruiser (ID 295)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 295, reference_match_confidence = 85
WHERE equipment_id = 'GBR_A13_CRUISER_MK2' AND reference_vehicle_id IS NULL;

-- A13 Cruiser Mk3 -> A13 Mk I Cruiser (ID 295)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 295, reference_match_confidence = 85
WHERE equipment_id = 'GBR_A13_CRUISER_MK3' AND reference_vehicle_id IS NULL;

-- A13 Mk II -> A13 Mk I Cruiser (ID 295)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 295, reference_match_confidence = 90
WHERE equipment_id = 'GBR_A13_MK_II' AND reference_vehicle_id IS NULL;

-- A13 Mk II (cruiser Mk IV) -> A13 Mk I Cruiser (ID 295)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 295, reference_match_confidence = 90
WHERE equipment_id = 'GBR_A13_MK_II_CRUISER_MK_IV' AND reference_vehicle_id IS NULL;

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT '============================================================================' as divider
UNION ALL SELECT 'VERIFICATION: Common Tanks Linkage'
UNION ALL SELECT '============================================================================'
UNION ALL SELECT ''
UNION ALL SELECT 'Sherman Variants Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE equipment_id LIKE '%SHERMAN%' AND reference_vehicle_id IS NOT NULL)
UNION ALL SELECT 'Grant/Lee Variants Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE (equipment_id LIKE '%GRANT%' OR equipment_id LIKE '%LEE%') AND reference_vehicle_id IS NOT NULL)
UNION ALL SELECT 'Crusader Variants Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE equipment_id LIKE '%CRUSADER%' AND reference_vehicle_id IS NOT NULL)
UNION ALL SELECT 'Matilda Variants Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE equipment_id LIKE '%MATILDA%' AND reference_vehicle_id IS NOT NULL)
UNION ALL SELECT 'Valentine Variants Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE equipment_id LIKE '%VALENTINE%' AND reference_vehicle_id IS NOT NULL)
UNION ALL SELECT 'Churchill Variants Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE equipment_id LIKE '%CHURCHILL%' AND reference_vehicle_id IS NOT NULL)
UNION ALL SELECT 'Light Tank Variants Linked: ' || (SELECT COUNT(*) FROM equipment_battlegroup WHERE equipment_id LIKE '%LIGHT%TANK%' AND reference_vehicle_id IS NOT NULL)
UNION ALL SELECT ''
UNION ALL SELECT '============================================================================';
