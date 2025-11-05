-- Set aircraft movement to NULL (will display as "*" in BattleGroup datacards)
-- Aircraft don't have ground movement - they're air support only

UPDATE equipment_battlegroup
SET off_road_movement = NULL,
    road_movement = NULL,
    generation_method = 'aircraft_no_ground_movement',
    validation_notes = 'Aircraft have no ground movement (display as * in datacards)',
    generated_date = datetime('now')
WHERE equipment_id IN (
    SELECT canonical_id FROM equipment
    WHERE category IN ('aircraft', 'fighters', 'bombers', 'dive_bombers', 'reconnaissance')
);
