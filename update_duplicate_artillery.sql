-- Update remaining 11 duplicate artillery items with correct movement values

-- DUPLICATES: Flak 36 8.8cm (reverse order) → 88mm → Medium gun → 1"/1"
UPDATE equipment_battlegroup
SET off_road_movement = 1,
    road_movement = 1,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 88mm (8.8cm Flak 36 - duplicate entry) | Medium gun (88mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GER_FLAK_36_8.8CM';

-- DUPLICATES: Lefh 18 10.5cm (reverse order) → 105mm → Heavy gun → 0"/0"
UPDATE equipment_battlegroup
SET off_road_movement = 0,
    road_movement = 0,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 105mm (10.5cm leFH 18 - duplicate entry) | Heavy gun (105mm) - cannot manhandle, requires tow vehicle',
    generated_date = datetime('now')
WHERE equipment_id = 'GER_LEFH_18_10.5CM';

-- DUPLICATES: Pak 38 5.0cm (reverse order) → 50mm → Light gun → 2"/2"
UPDATE equipment_battlegroup
SET off_road_movement = 2,
    road_movement = 2,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 50mm (5.0cm Pak 38 - duplicate entry) | Light gun (50mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GER_PAK_38_5.0CM';

-- DUPLICATES: Pak 40 7.5cm (reverse order) → 75mm → Light gun → 2"/2"
UPDATE equipment_battlegroup
SET off_road_movement = 2,
    road_movement = 2,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 75mm (7.5cm Pak 40 - duplicate entry) | Light gun (75mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GER_PAK_40_7.5CM';

-- DUPLICATES: 3.7cm Pak 36 (already has caliber at start, just missing update) → 37mm → Very light → 3"/3"
UPDATE equipment_battlegroup
SET off_road_movement = 3,
    road_movement = 3,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 37mm (3.7cm Pak 36) | Very light gun (37mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GER_3.7CM_PAK_36';

-- DUPLICATES: 2 Pdr AT → 40mm (2-pounder) → Very light → 3"/3"
UPDATE equipment_battlegroup
SET off_road_movement = 3,
    road_movement = 3,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 40mm (2-pdr = 40mm) | Very light gun (40mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GBR_2_PDR_AT';

-- DUPLICATES: 4 5 Howitzer (missing punctuation) → 114.3mm (4.5-inch) → Heavy → 0"/0"
UPDATE equipment_battlegroup
SET off_road_movement = 0,
    road_movement = 0,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 114.3mm (4.5-inch howitzer, formatting issue) | Heavy gun (114.3mm) - cannot manhandle, requires tow vehicle',
    generated_date = datetime('now')
WHERE equipment_id = 'GBR_4_5_HOWITZER';

-- DUPLICATES: 18-pounder (AT Adapted) → 83.8mm → Medium → 1"/1"
UPDATE equipment_battlegroup
SET off_road_movement = 1,
    road_movement = 1,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 83.8mm (18-pounder = 83.8mm) | Medium gun (83.8mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GBR_18-POUNDER_AT_ADAPTED';

-- DUPLICATES: 60-pounder Heavy Gun → 127mm → Heavy → 0"/0"
UPDATE equipment_battlegroup
SET off_road_movement = 0,
    road_movement = 0,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 127mm (60-pounder = 127mm) | Heavy gun (127mm) - cannot manhandle, requires tow vehicle',
    generated_date = datetime('now')
WHERE equipment_id = 'GBR_60-POUNDER_HEAVY_GUN';

-- DUPLICATES: Ordnance QF 18-pounder → 83.8mm → Medium → 1"/1"
UPDATE equipment_battlegroup
SET off_road_movement = 1,
    road_movement = 1,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 83.8mm (Ordnance QF 18-pounder = 83.8mm) | Medium gun (83.8mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GBR_ORDNANCE_QF_18-POUNDER';

-- DUPLICATES: Boys Anti-tank Rifle .55 → 13.97mm → Very light → 3"/3"
UPDATE equipment_battlegroup
SET off_road_movement = 3,
    road_movement = 3,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 13.97mm (.55 caliber anti-tank rifle - duplicate entry) | Very light gun (13.97mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GBR_BOYS_ANTI-TANK_RIFLE_.55';
