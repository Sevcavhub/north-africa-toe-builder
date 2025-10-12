BEGIN TRANSACTION;

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1940-Q2', '7th Armoured Division',
    'Armoured Division', 'division',
    'Major-General Sir Michael O''Moore Creagh', 'Major-General',
    10000, 580, 1850, 7570,
    228, 0, 69, 159,
    180, 2538, 0,
    85, 1, 'Local JSON files: british_organization.json, british_scm.json (1940-Q2)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/britain_1940q2_7th_armoured_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q2', '50th (Northumbrian) Infantry Division',
    'Infantry Division', 'division',
    'Major-General William Horatio Crawford Ramsden', 'Major-General',
    17298, 920, 2850, 13528,
    0, 0, 0, 0,
    168, 4166, 0,
    82, 3, 'unithistories.com - 50th Northumbrian Division deployment records',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/britain_1941q2_50th_infantry_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'french', '1942-Q2', '1re Brigade Française Libre',
    'Free French Infantry Brigade', 'brigade',
    'Général de brigade Marie-Pierre Koenig', 'Général de brigade',
    3850, 285, 715, 2850,
    0, 0, 0, 0,
    104, 125, 0,
    82, 3, 'National WWII Museum - Forgotten Fights: The Free French at Bir Hacheim',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/france_1942q2_1st_free_french_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'french', '1943-Q1', 'Division de Marche du Maroc',
    'Colonial Infantry Division (Moroccan)', 'division',
    'Général de Division Maurice Mathenet', 'Général de Division',
    12500, 520, 1875, 10105,
    24, 0, 12, 12,
    72, 380, 0,
    78, 3, 'British Military History - Tunisia 1942-1943 French Divisions',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/france_1943q1_division_marche_maroc_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1941-Q1', '5. leichte Division',
    'leichte Division (Light Division)', 'division',
    'Generalmajor Johannes Streich', 'Generalmajor',
    12000, 850, 2150, 9000,
    155, 0, 78, 77,
    120, 1393, 0,
    80, 1, 'Tessin Band 02, 04, 05 - Organizational structure and unit history',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/germany_1941q1_5_leichte_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1941-Q2', 'Deutsches Afrikakorps (DAK)',
    'Panzer Corps', 'corps',
    'Generalleutnant Erwin Rommel', 'Generalleutnant',
    31160, 2100, 5560, 23500,
    320, 0, 170, 150,
    186, 2866, 0,
    85, 3, '1941-Q2_Enhanced_COMPREHENSIVE_v4.json (german_scm.json and german_organization.json)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/germany_1941q2_deutsches_afrikakorps_toe.json'
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
    'Armored Division', 'Division',
    'Johann von Ravenstein', 'Generalmajor',
    0, 0, 0, 0,
    110, 0, 75, 35,
    0, 0, 0,
    70, 1, 'Tessin Band 02 - Organizational structure and redesignation details',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/germany_1941q3_21_panzer_division_toe.json'
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
    85, 1, 'Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 06 (Tier 1, 95% confidence)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/germany_1941q3_90_leichte_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1940-Q2', '4th Indian Infantry Division',
    'Infantry Division (Indian Army)', 'division',
    'Major-General Noel Beresford-Peirse', 'Major-General',
    15000, 680, 1820, 12500,
    0, 0, 0, 0,
    96, 945, 0,
    85, 3, 'MDBook 1940-Q2 Complete',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/india_1940q2_4th_indian_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1940-Q3', '27a Divisione di Fanteria "Brescia"',
    'Autotrasportabile Infantry Division', 'division',
    'Giuseppe Cremascoli', 'Generale di Divisione',
    7450, 342, 1240, 5868,
    12, 0, 0, 12,
    48, 487, 0,
    78, 3, 'TM-E 30-420 Handbook on Italian Military Forces (August 1943)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/italy_1940q3_brescia_division_toe.json'
);

COMMIT;