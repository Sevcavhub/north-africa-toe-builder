-- ============================================================================
-- UNIFIED VIEW: v_vehicles_unified
-- Combines BG Builder (primary for armor/movement/weapons) + manual data (supplementary)
-- ============================================================================

DROP VIEW IF EXISTS v_vehicles_unified;

CREATE VIEW v_vehicles_unified AS
SELECT
    -- Primary ID from BG Builder
    bgb.id as bg_builder_id,
    bgb.name,

    -- Movement from BG Builder (PRIMARY)
    bgb.movement_off_road as off_road_inches,
    bgb.movement_road as road_inches,
    bgb.movement_special as special_movement,

    -- Armor from BG Builder (PRIMARY)
    bgb.armor_front,
    bgb.armor_side,
    bgb.armor_rear,

    -- Weapons from BG Builder (PRIMARY) - resolved to names
    w1.weapon_name as weapon_1,
    w2.weapon_name as weapon_2,
    w3.weapon_name as weapon_3,
    w4.weapon_name as weapon_4,

    -- Weapon IDs from BG Builder (for cross-reference)
    bgb.weapon_1_id,
    bgb.weapon_2_id,
    bgb.weapon_3_id,
    bgb.weapon_4_id,

    -- Ammunition counts from MANUAL (if available)
    manual.ammo_1,
    manual.ammo_2,
    manual.ammo_3,
    manual.ammo_4,

    -- Weapon mounts from MANUAL (if available)
    manual.mount_1,
    manual.mount_2,
    manual.mount_3,
    manual.mount_4,

    -- Metadata from MANUAL (if available)
    COALESCE(manual.year_range, '') as year_range,
    COALESCE(manual.vehicle_type, '') as vehicle_type,
    COALESCE(manual.nation, '') as nation,

    -- Special rules from BG Builder (PRIMARY)
    bgb.special_rules,

    -- Armor modifiers from MANUAL (if available)
    manual.armor_modifier,
    manual.armor_side_schurzen,

    -- Soft-skin fields from BG Builder (PRIMARY)
    bgb.hits as ss_hits,
    bgb.capacity as ss_transport_capacity,

    -- Flags from BG Builder
    bgb.has_mg,
    bgb.has_ammo,

    -- Source provenance
    'bg_builder' as primary_source,
    CASE
        WHEN manual.id IS NOT NULL THEN 'merged'
        ELSE 'bg_builder_only'
    END as data_status,
    manual.id as manual_id,
    manual.bg_builder_id as manual_link_id

FROM bg_builder_vehicles bgb
LEFT JOIN bg_builder_weapons w1 ON bgb.weapon_1_id = w1.weapon_id
LEFT JOIN bg_builder_weapons w2 ON bgb.weapon_2_id = w2.weapon_id
LEFT JOIN bg_builder_weapons w3 ON bgb.weapon_3_id = w3.weapon_id
LEFT JOIN bg_builder_weapons w4 ON bgb.weapon_4_id = w4.weapon_id
LEFT JOIN bg_reference_vehicles manual ON bgb.id = manual.bg_builder_id;

-- ============================================================================
-- UNIFIED WEAPONS VIEW
-- ============================================================================

DROP VIEW IF EXISTS v_weapons_unified;

CREATE VIEW v_weapons_unified AS
SELECT
    weapon_id,
    weapon_name,

    -- HE stats
    he_type,
    he_effect,
    he_strength_0,
    he_strength_10,
    he_strength_20,
    he_strength_30,
    he_strength_40,
    he_strength_50,

    -- AP stats
    ap_effect,
    ap_strength_0,
    ap_strength_10,
    ap_strength_20,
    ap_strength_30,
    ap_strength_40,
    ap_strength_50,

    -- Metadata
    'bg_builder' as source

FROM bg_builder_weapons;

-- ============================================================================
-- END OF UNIFIED VIEWS
-- ============================================================================
