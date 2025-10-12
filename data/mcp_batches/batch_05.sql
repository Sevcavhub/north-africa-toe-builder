BEGIN TRANSACTION;

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
    15000, 600, 2400, 11000,
    146, 0, 126, 20,
    136, 2080, 0,
    78, 1, 'Tessin - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS im Zweiten Weltkrieg 1939-1945, Volume 6',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/germany_1941q2_15_panzer_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1941-Q2', '5. leichte Division',
    'Light Division (Motorized-Mechanized)', 'division',
    'Generalmajor Johann von Ravenstein', 'Generalmajor',
    10750, 485, 1820, 8445,
    142, 0, 107, 35,
    86, 2450, 0,
    82, 1, 'Georg Tessin - Verbände und Truppen der deutschen Wehrmacht 1939-1945, Band 2',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/germany_1941q2_5_leichte_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1941-Q3', '21. Panzer-Division',
    'Panzer Division', 'division',
    'Johann von Ravenstein', 'Generalmajor',
    9500, 485, 1425, 7590,
    120, 0, 80, 40,
    82, 2840, 0,
    78, 3, 'Historical research report - comprehensive analysis of 21. Panzer-Division redesignation',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/germany_1941q3_21_panzer_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1941-Q3', '90. leichte Afrika-Division',
    'Light Infantry Division', 'division',
    'Generalmajor Max Sümmermann', 'Generalmajor',
    10500, 420, 1680, 8400,
    0, 0, 0, 0,
    72, 1850, 0,
    87, 1, 'Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 06 (Tier 1, 95% confidence)',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/germany_1941q3_90_leichte_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'unknown', 'unknown', 'Unknown Unit',
    NULL, NULL,
    NULL, NULL,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0,
    0, 3, 'Unknown',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/italy_1941q2_132_ariete_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q2', '17ª Divisione di fanteria "Pavia"',
    'infantry_division', NULL,
    NULL, NULL,
    10864, 510, 1950, 8404,
    0, 0, 0, 0,
    0, 0, 0,
    0, 3, 'Unknown',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/italy_1941q2_17_pavia_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q2', '27ª Divisione di fanteria "Brescia"',
    'infantry_division', NULL,
    NULL, NULL,
    12169, 425, 1340, 10404,
    0, 0, 0, 0,
    0, 0, 0,
    0, 3, 'Unknown',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/italy_1941q2_27_brescia_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q2', '55ª Divisione motorizzata "Trento"',
    'motorized_division', NULL,
    NULL, NULL,
    9500, 380, 1140, 7980,
    0, 0, 0, 0,
    0, 0, 0,
    0, 3, 'Unknown',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/italy_1941q2_55_trento_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q2', '60ª Divisione di fanteria "Sabratha"',
    'infantry_division', 'division',
    NULL, NULL,
    7850, 275, 890, 6685,
    0, 0, 0, 0,
    28, 920, 0,
    0, 3, 'Unknown',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/italy_1941q2_sabratha_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1940-Q2', 'Western Desert Force',
    'Corps', 'corps',
    'Major-General Richard Nugent O''Connor', 'Major-General',
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0,
    0, 3, 'Unknown',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_1760245551581/units/britain_1940q2_western_desert_force_toe.json'
);

COMMIT;