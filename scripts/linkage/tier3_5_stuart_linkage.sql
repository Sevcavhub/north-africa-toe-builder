-- Stuart Tank Linkage (Tier 3.5 - Manual)
-- Generated for Phase 9B weapon data fix
-- Links Stuart variants to bg_reference_vehicles

BEGIN TRANSACTION;

-- Stuart I (M3 Light) -> M3A1 Stuart (ID 101)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 101, reference_match_confidence = 85
WHERE equipment_id = 'GBR_STUART_I_M3_LIGHT' AND reference_vehicle_id IS NULL;

-- M3 Stuart I -> M3A1 Stuart (ID 101)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 101, reference_match_confidence = 90
WHERE equipment_id = 'GBR_M3_STUART_I' AND reference_vehicle_id IS NULL;

-- M3A1 Stuart III -> M3A1 Stuart (ID 101)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 101, reference_match_confidence = 100
WHERE equipment_id = 'GBR_M3A1_STUART_III' AND reference_vehicle_id IS NULL;

-- Stuart M3 -> M3A1 Stuart (ID 101)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 101, reference_match_confidence = 90
WHERE equipment_id = 'GBR_STUART_M3' AND reference_vehicle_id IS NULL;

-- Honey Stuart M3a1 -> M3A1 Stuart (ID 101)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 101, reference_match_confidence = 95
WHERE equipment_id = 'GBR_HONEY_STUART_M3A1' AND reference_vehicle_id IS NULL;

-- Stuart V -> M5 Stuart (ID 216)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 216, reference_match_confidence = 90
WHERE equipment_id = 'GBR_STUART_V' AND reference_vehicle_id IS NULL;

-- Stuart VI -> M5 Stuart (ID 216)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 216, reference_match_confidence = 85
WHERE equipment_id = 'GBR_STUART_VI' AND reference_vehicle_id IS NULL;

-- M3 Stuart (USA) -> M3A1 Stuart (ID 101)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 101, reference_match_confidence = 90
WHERE equipment_id = 'USA_M3_STUART' AND reference_vehicle_id IS NULL;

-- M3A1 Stuart (USA) -> M3A1 Stuart (ID 101)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 101, reference_match_confidence = 100
WHERE equipment_id = 'USA_M3A1_STUART' AND reference_vehicle_id IS NULL;

-- M3 Stuart (French) -> M3A1 Stuart (ID 101)
UPDATE equipment_battlegroup
SET reference_vehicle_id = 101, reference_match_confidence = 90
WHERE equipment_id = 'FRA_M3_STUART' AND reference_vehicle_id IS NULL;

COMMIT;

-- Verification
SELECT equipment_id, reference_vehicle_id, reference_match_confidence
FROM equipment_battlegroup
WHERE equipment_id LIKE '%STUART%' OR equipment_id LIKE '%M3%LIGHT%';
