-- Add armor_side_schurzen field for vehicles with side skirts
-- When present, side armor displays as: "base(schurzen)" e.g., "N(M)"
-- When NULL, displays as just base armor: "N"

ALTER TABLE bg_reference_vehicles
ADD COLUMN armor_side_schurzen TEXT DEFAULT NULL;

-- Verify the column was added
SELECT
    name,
    armor_front,
    armor_side,
    armor_side_schurzen,
    armor_rear,
    armor_modifier
FROM bg_reference_vehicles
WHERE armor_modifier IS NOT NULL OR armor_side_schurzen IS NOT NULL
LIMIT 5;
