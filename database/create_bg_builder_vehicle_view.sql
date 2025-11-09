-- Create view showing BG Builder vehicles with weapon names resolved
-- Useful for finding matches for unlinked manual vehicles

CREATE VIEW IF NOT EXISTS v_bg_builder_vehicles_detailed AS
SELECT
    bgb.id,
    bgb.name,
    bgb.movement_off_road,
    bgb.movement_road,
    bgb.movement_special,
    bgb.armor_front,
    bgb.armor_side,
    bgb.armor_rear,

    -- Resolve weapon names from IDs
    w1.weapon_name as weapon_1,
    w2.weapon_name as weapon_2,
    w3.weapon_name as weapon_3,
    w4.weapon_name as weapon_4,

    -- Weapon IDs (for reference)
    bgb.weapon_1_id,
    bgb.weapon_2_id,
    bgb.weapon_3_id,
    bgb.weapon_4_id,

    -- Other useful fields
    bgb.special_rules,
    bgb.hits,
    bgb.capacity,
    bgb.has_mg,
    bgb.has_ammo,

    -- Flags for filtering
    CASE
        WHEN bgb.armor_front IN ('O', 'SS') THEN 'soft_skin'
        WHEN bgb.armor_front IN ('A', 'B', 'C', 'D', 'E') THEN 'heavy'
        WHEN bgb.armor_front IN ('F', 'G', 'H', 'I', 'J') THEN 'medium'
        WHEN bgb.armor_front IN ('K', 'L', 'M', 'N') THEN 'light'
        ELSE 'unknown'
    END as armor_class

FROM bg_builder_vehicles bgb
LEFT JOIN bg_builder_weapons w1 ON bgb.weapon_1_id = w1.weapon_id
LEFT JOIN bg_builder_weapons w2 ON bgb.weapon_2_id = w2.weapon_id
LEFT JOIN bg_builder_weapons w3 ON bgb.weapon_3_id = w3.weapon_id
LEFT JOIN bg_builder_weapons w4 ON bgb.weapon_4_id = w4.weapon_id;
