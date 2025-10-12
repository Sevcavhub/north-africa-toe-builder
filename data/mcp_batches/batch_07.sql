BEGIN TRANSACTION;

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1942-Q3', '164. leichte Afrika-Division',
    'Light Division', 'division',
    'Generalleutnant Carl-Hans Lungershausen', 'Generalleutnant',
    9200, 420, 1380, 7400,
    0, 0, 0, 0,
    68, 1450, 0,
    78, 1, 'Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS, Band 07, pages 140-141',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/germany_1942-q3_164_leichte_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1942-Q3', 'Panzerarmee Afrika',
    'Panzer Army (Theater-Level Command)', 'theater',
    'Generalfeldmarschall Erwin Rommel', 'Generalfeldmarschall',
    96000, 4200, 18600, 73200,
    320, 0, 285, 35,
    465, 12500, 0,
    78, 1, 'Georg Tessin - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS, Band 14 (Panzerarmee Afrika section)',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/germany_1942-q3_panzerarmee_afrika_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q1', '102ª Divisione Motorizzata "Trento"',
    'Motorized Infantry Division (Divisione fanteria motorizzata)', 'division',
    'Luigi Nuvoloni', 'Generale di Divisione',
    10850, 435, 1950, 8465,
    0, 0, 0, 0,
    60, 2915, 0,
    82, 3, 'US Army TM E 30-420 ''Handbook on Italian Military Forces'' (August 1943) - motorized division organization, equipment',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/italy_1941-q1_trento_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q2', '55ª Divisione di Fanteria "Savona"',
    'Auto-transportable Infantry Division (Combat Degraded)', 'division',
    'Pietro Maggiani', 'Generale di Divisione',
    8423, 356, 2045, 6022,
    0, 0, 0, 0,
    0, 1156, 0,
    83, 3, 'Order of Battle of the Italian Army - USA HQ G-2 (July 1943) - Tier 1 primary intelligence source',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/italy_1941-q2_savona_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q3', '25th Infantry Division "Bologna"',
    'Semi-Motorized Infantry Division', 'division',
    'Generale di Divisione Alessandro Gloria', 'Major General',
    11500, 425, 1850, 9225,
    0, 0, 0, 0,
    72, 1450, 0,
    72, 3, 'Order of Battle of the Italian Army - USA HQ G2 July 1943',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/italy_1941-q3_bologna_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q3', '17ª Divisione di Fanteria "Pavia"',
    'Semi-Motorized Infantry Division', 'division',
    'Antonio FRANCESCHINI', 'Generale di Divisione',
    10420, 492, 1880, 8048,
    0, 0, 0, 0,
    90, 438, 0,
    81, 3, 'TM-E 30-420 Handbook on Italian Military Forces (August 1943) - Italian semi-motorized division organization',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/italy_1941-q3_pavia_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1941-Q2', '15. Panzer-Division',
    'Panzer Division', 'division',
    'Generalmajor Walter Neumann-Silkow', 'Generalmajor',
    12850, 485, 1890, 10475,
    155, 0, 109, 46,
    146, 2850, 0,
    65, 3, 'Osprey Men-at-Arms #53: Rommel''s Desert Army (Tier 2, 75% confidence)',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_20251012_065701/units/germany_1941-Q2_15_panzer_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1941-Q2', 'Deutsches Afrikakorps',
    'Panzer Corps', 'corps',
    'Generalleutnant Erwin Rommel', 'Generalleutnant',
    28500, 1250, 4850, 22400,
    305, 0, 95, 210,
    156, 3850, 0,
    78, 3, 'Osprey Men-At-Arms #53 ''Rommel''s Desert Army'' (1976)',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_20251012_065751/units/germany_1941-Q2_deutsches_afrikakorps_toe.json'
);

COMMIT;