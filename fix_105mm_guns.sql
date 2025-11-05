-- Fix 105mm American guns that were incorrectly classified as "medium" (1"/1")
-- Should be "heavy" (0"/0") per BattleGroup rules

-- 105mm M2A1 → 0"/0" (heavy gun, cannot manhandle)
UPDATE equipment_battlegroup
SET off_road_movement = 0,
    road_movement = 0,
    generation_method = 'caliber_based_gun_rules_corrected',
    validation_notes = 'Corrected: 105mm (M2A1 howitzer) | Heavy gun (105mm) - cannot manhandle, requires tow vehicle',
    generated_date = datetime('now')
WHERE equipment_id IN (
    SELECT canonical_id FROM equipment
    WHERE name = '105mm M2A1' OR name = 'M2A1 105mm Howitzer'
);
