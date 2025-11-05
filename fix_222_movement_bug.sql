-- Fix 4 vehicles with incorrect 222" movement placeholder value
-- Should be 8"/12" like similar armored cars and halftracks

UPDATE equipment_battlegroup
SET off_road_movement = 8,
    road_movement = 12,
    generation_method = 'corrected_placeholder_bug',
    validation_notes = 'Fixed placeholder bug: 222" → 8"/12" (standard halftrack/armored car movement)',
    generated_date = datetime('now')
WHERE equipment_id IN (
    'GER_SDKFZ_251',
    'GER_SDKFZ_10',
    'GER_SDKFZ_232_(FU)',
    'GER_SDKFZ_232_(8-RAD)'
);
