-- Convenience view for datacard generation
-- Joins bg_builder_weapons with bg_gun_name_conversion
-- Provides both full and abbreviated weapon names in single query

CREATE VIEW IF NOT EXISTS vw_weapon_display AS
SELECT
    w.weapon_id,
    w.weapon_name AS full_name,
    COALESCE(c.datacard_name, w.weapon_name) AS display_name,
    w.he_type,
    w.he_effect,
    w.he_strength_0,
    w.he_strength_10,
    w.he_strength_20,
    w.he_strength_30,
    w.he_strength_40,
    w.he_strength_50,
    w.ap_effect,
    w.ap_strength_0,
    w.ap_strength_10,
    w.ap_strength_20,
    w.ap_strength_30,
    w.ap_strength_40,
    w.ap_strength_50,
    w.import_date,
    w.import_source,
    c.conversion_id,
    c.notes AS conversion_notes
FROM bg_builder_weapons w
LEFT JOIN bg_gun_name_conversion c ON w.weapon_name = c.weapon_name;

-- Example usage:
-- SELECT full_name, display_name, he_effect, ap_strength_0
-- FROM vw_weapon_display
-- WHERE full_name = '75mmL46 (PaK40)';
-- Returns: full_name='75mmL46 (PaK40)', display_name='(PaK40)', ...

-- For vehicle datacards:
-- SELECT
--     v.vehicle_name,
--     vw.display_name AS main_gun_display,
--     vw.he_effect,
--     vw.ap_strength_0
-- FROM bg_builder_vehicles v
-- LEFT JOIN vw_weapon_display vw ON v.main_gun = vw.full_name
-- WHERE v.vehicle_id = 1;
