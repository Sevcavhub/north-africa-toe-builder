-- Add armor_modifier field to bg_reference_vehicles table
-- This field captures armor characteristics that display below armor values
-- Examples: "Open-Topped", "Schürzen", etc.
-- NULL/empty = no special armor characteristic (normal closed-top vehicle)

ALTER TABLE bg_reference_vehicles
ADD COLUMN armor_modifier TEXT DEFAULT NULL;

-- Verify the column was added
SELECT
    name,
    armor_front,
    armor_side,
    armor_rear,
    armor_modifier,
    weapons
FROM bg_reference_vehicles
LIMIT 3;
