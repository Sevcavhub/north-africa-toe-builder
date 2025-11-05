-- Manual artillery movement updates for 6 items with known calibers

-- 1. 10.5cm Lefh 18 → 105mm → Heavy gun (105mm+) → 0"/0"
UPDATE equipment_battlegroup
SET off_road_movement = 0,
    road_movement = 0,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 105mm (leFH 18 light field howitzer) | Heavy gun (105mm) - cannot manhandle, requires tow vehicle',
    generated_date = datetime('now')
WHERE equipment_id = 'GER_10.5CM_LEFH_18';

-- 6. Sfh 18 15cm → 150mm → Heavy gun (105mm+) → 0"/0"
UPDATE equipment_battlegroup
SET off_road_movement = 0,
    road_movement = 0,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 150mm (sFH 18 heavy field howitzer) | Heavy gun (150mm) - cannot manhandle, requires tow vehicle',
    generated_date = datetime('now')
WHERE equipment_id = 'GER_SFH_18_15CM';

-- 13. Boys Anti-tank Rifle → 13.97mm (.55 cal) → Very light gun (<50mm) → 3"/3"
UPDATE equipment_battlegroup
SET off_road_movement = 3,
    road_movement = 3,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 13.97mm (.55 caliber anti-tank rifle) | Very light gun (13.97mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'GBR_BOYS_ANTI-TANK_RIFLE';

-- 15. Cannone DA 20/65 → 20mm → Very light gun (<50mm) → 3"/3"
UPDATE equipment_battlegroup
SET off_road_movement = 3,
    road_movement = 3,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 20mm (Cannone DA 20/65 - 20mm caliber, 65 calibers long) | Very light gun (20mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'ITA_CANNONE_DA_20_65';

-- 16. Cannone DA 47/32 → 47mm → Very light gun (<50mm) → 3"/3"
UPDATE equipment_battlegroup
SET off_road_movement = 3,
    road_movement = 3,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 47mm (Cannone DA 47/32 - 47mm caliber, 32 calibers long) | Very light gun (47mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'ITA_CANNONE_DA_47_32';

-- 17. Cannone DA 75/46 → 75mm → Light gun (50-75mm) → 2"/2"
UPDATE equipment_battlegroup
SET off_road_movement = 2,
    road_movement = 2,
    generation_method = 'caliber_based_gun_rules_manual',
    validation_notes = 'Manual caliber extraction: 75mm (Cannone DA 75/46 - 75mm caliber, 46 calibers long) | Light gun (75mm) manhandled',
    generated_date = datetime('now')
WHERE equipment_id = 'ITA_CANNONE_DA_75_46';
