-- ============================================================================
-- Phase 5.5 - Phase 1: Backward Compatibility VIEWs
-- ============================================================================
-- Date: November 3, 2025
-- Purpose: Allow 33 read-only scripts to continue working during migration
-- Strategy: Create VIEWs that mimic old table structure
--
-- Impact: 33 of 95 active scripts (35%) require ZERO changes during migration
--
-- Critical Dependency Chains:
--   - Phase 9B Equipment Datacard Generation (8-script chain)
--   - Phase 9A Scenario Export (5-script chain)
--   - Phase 6 Unit Enrichment Workflow
--
-- Safety: VIEWs will be phased out after script migration (Phase 5.5 Phase 5)
-- ============================================================================

-- ============================================================================
-- VIEW 1: equipment (WITW Baseline - 469 North Africa Items)
-- ============================================================================
-- Purpose: Compatibility with 33 read-only scripts accessing equipment table
-- Original Table: equipment (469 rows)
-- Expected Count: 469 rows (North Africa theater only)
-- ============================================================================

CREATE VIEW IF NOT EXISTS equipment_view AS
SELECT
    em.master_id as canonical_id,
    em.canonical_name as name,
    em.original_nation as nation,
    em.equipment_category as equipment_type,
    em.equipment_category as category,

    -- WITW Fields (extracted from historical_specs_json)
    json_extract(em.historical_specs_json, '$.witw_id') as witw_id,
    json_extract(em.historical_specs_json, '$.witw_name') as witw_name,
    json_extract(em.historical_specs_json, '$.witw_confidence') as witw_confidence,

    -- OnWar Match Fields
    CASE WHEN json_extract(em.historical_specs_json, '$.onwar_url') IS NOT NULL THEN 1 ELSE 0 END as onwar_matched,
    json_extract(em.historical_specs_json, '$.onwar_url') as onwar_url,

    -- WWIItanks Match Fields
    CASE WHEN json_extract(em.historical_specs_json, '$.wwiitanks_id') IS NOT NULL THEN 1 ELSE 0 END as wwiitanks_matched,
    json_extract(em.historical_specs_json, '$.wwiitanks_id') as wwiitanks_id,

    -- Match Quality
    CAST(em.confidence_score as INTEGER) as match_confidence,
    em.primary_source as match_method,

    -- Production Data
    json_extract(em.historical_specs_json, '$.production_start') as production_start,
    json_extract(em.historical_specs_json, '$.production_end') as production_end,
    json_extract(em.historical_specs_json, '$.production_quantity') as production_quantity,
    json_extract(em.historical_specs_json, '$.manufacturers') as manufacturers,
    json_extract(em.historical_specs_json, '$.formal_designation') as formal_designation,

    -- Physical Dimensions
    CAST(json_extract(em.historical_specs_json, '$.weight_tonnes') as REAL) as weight_tonnes,
    CAST(json_extract(em.historical_specs_json, '$.length_m') as REAL) as length_m,
    CAST(json_extract(em.historical_specs_json, '$.width_m') as REAL) as width_m,
    CAST(json_extract(em.historical_specs_json, '$.height_m') as REAL) as height_m,
    CAST(json_extract(em.historical_specs_json, '$.crew') as INTEGER) as crew,
    CAST(json_extract(em.historical_specs_json, '$.ground_clearance_m') as REAL) as ground_clearance_m,

    -- Armor Values
    CAST(json_extract(em.historical_specs_json, '$.armor_front_mm') as INTEGER) as armor_front_mm,
    CAST(json_extract(em.historical_specs_json, '$.armor_front_angle') as INTEGER) as armor_front_angle,
    CAST(json_extract(em.historical_specs_json, '$.armor_front_effective_mm') as INTEGER) as armor_front_effective_mm,
    CAST(json_extract(em.historical_specs_json, '$.armor_side_mm') as INTEGER) as armor_side_mm,
    CAST(json_extract(em.historical_specs_json, '$.armor_side_angle') as INTEGER) as armor_side_angle,
    CAST(json_extract(em.historical_specs_json, '$.armor_rear_mm') as INTEGER) as armor_rear_mm,
    CAST(json_extract(em.historical_specs_json, '$.armor_rear_angle') as INTEGER) as armor_rear_angle,
    CAST(json_extract(em.historical_specs_json, '$.armor_top_mm') as INTEGER) as armor_top_mm,
    CAST(json_extract(em.historical_specs_json, '$.armor_bottom_mm') as INTEGER) as armor_bottom_mm,
    CAST(json_extract(em.historical_specs_json, '$.turret_front_mm') as INTEGER) as turret_front_mm,
    CAST(json_extract(em.historical_specs_json, '$.turret_front_angle') as INTEGER) as turret_front_angle,
    CAST(json_extract(em.historical_specs_json, '$.turret_side_mm') as INTEGER) as turret_side_mm,
    CAST(json_extract(em.historical_specs_json, '$.turret_rear_mm') as INTEGER) as turret_rear_mm,
    CAST(json_extract(em.historical_specs_json, '$.turret_top_mm') as INTEGER) as turret_top_mm,

    -- Performance
    CAST(json_extract(em.historical_specs_json, '$.max_speed_kmh') as INTEGER) as max_speed_kmh,
    CAST(json_extract(em.historical_specs_json, '$.max_speed_road_kmh') as INTEGER) as max_speed_road_kmh,
    CAST(json_extract(em.historical_specs_json, '$.max_speed_offroad_kmh') as INTEGER) as max_speed_offroad_kmh,
    CAST(json_extract(em.historical_specs_json, '$.range_road_km') as INTEGER) as range_road_km,
    CAST(json_extract(em.historical_specs_json, '$.range_offroad_km') as INTEGER) as range_offroad_km,
    json_extract(em.historical_specs_json, '$.fuel_type') as fuel_type,
    CAST(json_extract(em.historical_specs_json, '$.fuel_capacity_l') as INTEGER) as fuel_capacity_l,
    json_extract(em.historical_specs_json, '$.engine_make') as engine_make,
    json_extract(em.historical_specs_json, '$.engine_model') as engine_model,
    CAST(json_extract(em.historical_specs_json, '$.engine_hp') as INTEGER) as engine_hp,
    CAST(json_extract(em.historical_specs_json, '$.power_weight_ratio') as REAL) as power_weight_ratio,

    -- Mobility
    CAST(json_extract(em.historical_specs_json, '$.gradient_capability_deg') as INTEGER) as gradient_capability_deg,
    CAST(json_extract(em.historical_specs_json, '$.fording_depth_m') as REAL) as fording_depth_m,
    CAST(json_extract(em.historical_specs_json, '$.trench_crossing_m') as REAL) as trench_crossing_m,
    CAST(json_extract(em.historical_specs_json, '$.vertical_obstacle_m') as REAL) as vertical_obstacle_m,
    CAST(json_extract(em.historical_specs_json, '$.turning_radius_m') as REAL) as turning_radius_m,
    json_extract(em.historical_specs_json, '$.radio_equipment') as radio_equipment,

    -- Operational Dates
    json_extract(em.historical_specs_json, '$.first_appearance') as first_appearance,
    json_extract(em.historical_specs_json, '$.last_appearance') as last_appearance,

    -- Metadata
    em.notes as notes,
    json_extract(em.historical_specs_json, '$.aliases') as aliases,
    em.created_at as created_at,
    em.updated_at as updated_at,
    'Phase_5_5_Migration' as created_by,
    'Phase_5_5_Migration' as updated_by

FROM equipment_master_new em
JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
WHERE etu.theater = 'north_africa';

-- ============================================================================
-- VIEW 2: equipment_battlegroup (BattleGroup Stats - 469 Items)
-- ============================================================================
-- Purpose: Compatibility with Phase 9B datacard generation scripts
-- Original Table: equipment_battlegroup (469 rows)
-- Expected Count: 469 rows (North Africa items with BattleGroup stats)
-- ============================================================================

CREATE VIEW IF NOT EXISTS equipment_battlegroup_view AS
SELECT
    eb.stat_id as equipment_id,
    em.canonical_name as name,

    -- Armor (Letter Scale)
    eb.armor_front,
    eb.armor_side,
    eb.armor_rear,
    NULL as armor_turret_front,  -- Not in new schema (derived from armor_front)
    NULL as armor_turret_side,   -- Not in new schema (derived from armor_side)
    NULL as armor_turret_rear,   -- Not in new schema (derived from armor_rear)

    -- Movement
    eb.movement_offroad as off_road_movement,
    eb.movement_road as road_movement,

    -- HE Weapon
    SUBSTR(eb.he_rating, 1, 1) as he_dice,       -- Extract "4" from "4/4+"
    SUBSTR(eb.he_rating, 3) as he_target,        -- Extract "4+" from "4/4+"
    eb.he_rating as he_format,

    -- AP Weapon (penetration scale)
    CASE
        WHEN CAST(eb.ap_rating as INTEGER) <= 2 THEN 0
        WHEN CAST(eb.ap_rating as INTEGER) BETWEEN 3 AND 4 THEN CAST(eb.ap_rating as INTEGER)
        ELSE CAST(eb.ap_rating as INTEGER)
    END as ap_0_10,

    CASE
        WHEN CAST(eb.ap_rating as INTEGER) <= 3 THEN 0
        ELSE CAST(eb.ap_rating as INTEGER) - 1
    END as ap_10_20,

    CASE
        WHEN CAST(eb.ap_rating as INTEGER) <= 4 THEN 0
        ELSE CAST(eb.ap_rating as INTEGER) - 2
    END as ap_20_30,

    CASE
        WHEN CAST(eb.ap_rating as INTEGER) <= 5 THEN 0
        ELSE CAST(eb.ap_rating as INTEGER) - 3
    END as ap_30_40,

    CASE
        WHEN CAST(eb.ap_rating as INTEGER) <= 6 THEN 0
        ELSE CAST(eb.ap_rating as INTEGER) - 4
    END as ap_40_50,

    CASE
        WHEN CAST(eb.ap_rating as INTEGER) <= 7 THEN 0
        ELSE CAST(eb.ap_rating as INTEGER) - 5
    END as ap_50_70,

    -- Points & BR
    eb.points as points_regular,
    eb.points as points_inexperienced,  -- Same for now
    eb.points as points_veteran,
    eb.points as points_elite,
    eb.battle_rating as battle_rating_regular,
    eb.battle_rating as battle_rating_inexperienced,
    eb.battle_rating as battle_rating_veteran,
    eb.battle_rating as battle_rating_elite,

    -- Special Rules
    eb.special_rules,

    -- Crew & Weapon Description
    CAST(json_extract(em.historical_specs_json, '$.crew') as INTEGER) as crew,
    eb.weapon_description,

    -- Metadata
    eb.generated_date,
    eb.conversion_method as generation_method,
    CAST(eb.conversion_confidence as INTEGER) as confidence_score,
    eb.notes as validation_notes,

    -- Reference Linkage (for backward compatibility)
    NULL as reference_vehicle_id,      -- Not directly stored in new schema
    eb.conversion_confidence as reference_match_confidence,
    NULL as reference_gun_id,
    eb.conversion_confidence as reference_gun_match_confidence

FROM equipment_stats_battlegroup eb
JOIN equipment_master_new em ON eb.master_id = em.master_id
JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
WHERE etu.theater = 'north_africa';

-- ============================================================================
-- VIEW 3: afv_data (OnWar AFV Database - ~250 Vehicles)
-- ============================================================================
-- Purpose: Compatibility with Phase 6 unit enrichment scripts
-- Original Table: afv_data (211 rows)
-- Expected Count: 200-250 rows (vehicles only)
-- ============================================================================

CREATE VIEW IF NOT EXISTS afv_data_view AS
SELECT
    em.master_id as id,
    em.original_nation as country,
    em.canonical_name as vehicle_name,
    json_extract(em.historical_specs_json, '$.onwar_url') as url,
    json_extract(em.historical_specs_json, '$.formal_designation') as formal_designation,
    em.equipment_subcategory as type,
    CAST(json_extract(em.historical_specs_json, '$.crew') as INTEGER) as crew,
    json_extract(em.historical_specs_json, '$.manufacturers') as manufacturers,
    json_extract(em.historical_specs_json, '$.production_quantity') as production_quantity,
    json_extract(em.historical_specs_json, '$.production_start') || '-' || json_extract(em.historical_specs_json, '$.production_end') as production_period,
    CAST(json_extract(em.historical_specs_json, '$.length_m') as REAL) as length_hull,
    CAST(json_extract(em.historical_specs_json, '$.width_m') as REAL) as width,
    CAST(json_extract(em.historical_specs_json, '$.height_m') as REAL) as height,
    CAST(json_extract(em.historical_specs_json, '$.weight_tonnes') as REAL) as combat_weight,
    CAST(json_extract(em.historical_specs_json, '$.ground_clearance_m') as REAL) as ground_clearance,
    json_extract(em.historical_specs_json, '$.radio_equipment') as radio,
    json_extract(em.historical_specs_json, '$.primary_armament') as primary_armament,
    json_extract(em.historical_specs_json, '$.secondary_armament') as secondary_armament,
    json_extract(em.historical_specs_json, '$.ammunition_carried') as ammunition_carried,
    json_extract(em.historical_specs_json, '$.traverse') as traverse,
    json_extract(em.historical_specs_json, '$.elevation') as elevation,
    json_extract(em.historical_specs_json, '$.engine_make') as engine_make_model,
    json_extract(em.historical_specs_json, '$.engine_type') as engine_type_displacement,
    CAST(json_extract(em.historical_specs_json, '$.engine_hp') as INTEGER) as horsepower,
    CAST(json_extract(em.historical_specs_json, '$.power_weight_ratio') as REAL) as power_weight_ratio,
    json_extract(em.historical_specs_json, '$.fuel_type') as fuel_type,
    CAST(json_extract(em.historical_specs_json, '$.fuel_capacity_l') as INTEGER) as fuel_capacity,
    CAST(json_extract(em.historical_specs_json, '$.max_speed_kmh') as INTEGER) as speed,
    CAST(json_extract(em.historical_specs_json, '$.range_road_km') as INTEGER) as range,
    json_extract(em.historical_specs_json, '$.gearbox') as gearbox,
    CAST(json_extract(em.historical_specs_json, '$.turning_radius_m') as REAL) as turning_radius,
    CAST(json_extract(em.historical_specs_json, '$.gradient_capability_deg') as INTEGER) as gradient,
    CAST(json_extract(em.historical_specs_json, '$.fording_depth_m') as REAL) as fording,
    CAST(json_extract(em.historical_specs_json, '$.vertical_obstacle_m') as REAL) as vertical_obstacle,
    CAST(json_extract(em.historical_specs_json, '$.trench_crossing_m') as REAL) as trench_crossing,
    json_extract(em.historical_specs_json, '$.ground_pressure') as ground_pressure,
    json_extract(em.historical_specs_json, '$.track_width') as track_width,
    json_extract(em.historical_specs_json, '$.track_ground_contact') as track_ground_contact,
    CAST(json_extract(em.historical_specs_json, '$.armor_front_mm') as INTEGER) as hull_front,
    CAST(json_extract(em.historical_specs_json, '$.armor_side_mm') as INTEGER) as hull_side,
    CAST(json_extract(em.historical_specs_json, '$.armor_rear_mm') as INTEGER) as hull_rear,
    CAST(json_extract(em.historical_specs_json, '$.armor_top_mm') as INTEGER) as hull_top_bottom,
    NULL as superstructure_front,
    NULL as superstructure_side,
    NULL as superstructure_rear,
    NULL as superstructure_top_bottom,
    CAST(json_extract(em.historical_specs_json, '$.turret_front_mm') as INTEGER) as turret_front,
    CAST(json_extract(em.historical_specs_json, '$.turret_side_mm') as INTEGER) as turret_side,
    CAST(json_extract(em.historical_specs_json, '$.turret_rear_mm') as INTEGER) as turret_rear,
    CAST(json_extract(em.historical_specs_json, '$.turret_top_mm') as INTEGER) as turret_top_bottom,
    NULL as mantlet,
    em.primary_source as source,
    em.created_at as scraped_date,
    em.created_at as imported_at,
    'Phase_5_5_Migration' as imported_by

FROM equipment_master_new em
WHERE em.equipment_category IN ('tank', 'armored_car', 'self_propelled_gun', 'vehicle');

-- ============================================================================
-- VIEW 4: guns (Gun Database - ~350 Guns)
-- ============================================================================
-- Purpose: Compatibility with gun-related scripts
-- Original Table: guns (348 rows)
-- Expected Count: 300-400 rows (guns only)
-- ============================================================================

CREATE VIEW IF NOT EXISTS guns_view AS
SELECT
    em.master_id as gun_id,
    em.canonical_name as name,
    em.display_name as full_name,
    em.original_nation as nation,
    CAST(json_extract(em.historical_specs_json, '$.caliber_mm') as INTEGER) as caliber_mm,
    CAST(json_extract(em.historical_specs_json, '$.barrel_length_calibers') as REAL) as barrel_length,
    CAST(json_extract(em.historical_specs_json, '$.rate_of_fire_rpm') as INTEGER) as rate_of_fire_rpm,
    json_extract(em.historical_specs_json, '$.production_start') as manufactured_start,
    json_extract(em.historical_specs_json, '$.production_end') as manufactured_end,
    em.equipment_subcategory as gun_type,
    json_extract(em.historical_specs_json, '$.wwiitanks_id') as wwiitanks_id,
    json_extract(em.historical_specs_json, '$.wwiitanks_url') as source_url,
    em.created_at as scraped_at,
    'Phase_5_5_Migration' as scraper_version,
    json_extract(em.historical_specs_json, '$.history') as history,
    em.notes as notes,
    em.created_at as created_at,
    em.updated_at as updated_at

FROM equipment_master_new em
WHERE em.equipment_category IN ('gun', 'artillery', 'anti_tank_gun', 'anti_aircraft_gun', 'mortar');

-- ============================================================================
-- Audit: Log VIEW Creation
-- ============================================================================

INSERT INTO normalization_audit_new (phase, operation, table_name, reason, notes, timestamp)
VALUES
    ('Phase 5.5 Phase 1', 'CREATE_VIEW', 'equipment_view', 'Backward compatibility for 33 read-only scripts', '469 North Africa items', CURRENT_TIMESTAMP),
    ('Phase 5.5 Phase 1', 'CREATE_VIEW', 'equipment_battlegroup_view', 'Backward compatibility for Phase 9B datacard generation', '469 items with BattleGroup stats', CURRENT_TIMESTAMP),
    ('Phase 5.5 Phase 1', 'CREATE_VIEW', 'afv_data_view', 'Backward compatibility for Phase 6 unit enrichment', '200-250 vehicles', CURRENT_TIMESTAMP),
    ('Phase 5.5 Phase 1', 'CREATE_VIEW', 'guns_view', 'Backward compatibility for gun-related scripts', '300-400 guns', CURRENT_TIMESTAMP);

-- ============================================================================
-- End of Backward Compatibility VIEWs
-- ============================================================================
-- Impact: 33 of 95 active scripts (35%) work without modification
-- Strategy: Phase out VIEWs after script migration (Phase 5.5 Phase 5)
-- ============================================================================
