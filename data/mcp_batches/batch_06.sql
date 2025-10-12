BEGIN TRANSACTION;

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1940-Q3', '7th Armoured Division',
    NULL, 'division',
    NULL, NULL,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0,
    0, 3, 'Unknown',
    '2025-10-12', 'D:/north-africa-toe-builder/data/output/autonomous_1760245551581/units/britain_1940q3_7th_armoured_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q1', '5th Indian Infantry Division',
    'Infantry Division', 'division',
    'Major-General Lewis Heath', 'Major-General',
    17000, 680, 2380, 13940,
    0, 0, 0, 0,
    120, 3260, 0,
    80, 3, 'Military Wiki: 5th Infantry Division (India) - Brigade composition, battalion assignments, commanders confirmed (Confidence: 80%)',
    '2025-10-11T16:15:00Z', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/britain_1941-q1_5th_indian_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q2', '1st South African Infantry Division',
    'Infantry Division (Commonwealth - South Africa)', 'division',
    'Brigadier-General George Edwin Brink', 'Brigadier-General (later Major-General)',
    18500, 740, 2590, 15170,
    0, 0, 0, 0,
    128, 3450, 0,
    72, 3, 'Wikipedia: 1st South African Infantry Division - Division history, commander, brigade composition (Confidence: 75%)',
    '2025-10-11T18:30:00Z', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/britain_1941-q2_1st_south_african_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1942-Q2', '9th Australian Division',
    'Infantry Division (Commonwealth - Australia)', 'division',
    'Lieutenant-General Leslie James Morshead', 'Lieutenant-General',
    16000, 900, 2400, 12700,
    40, 0, 25, 15,
    120, 1850, 0,
    82, 3, 'Australian War Memorial - 9th Division collection and unit histories',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/britain_1942-q2_9th_australian_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1942-Q4', '10th Armoured Division',
    'Armoured Division', 'division',
    'Major-General Alexander Hugh Gatehouse', 'Major-General',
    13235, 815, 2650, 9770,
    230, 0, 183, 47,
    96, 2850, 0,
    82, 3, 'Second Battle of El Alamein Order of Battle (Wikipedia)',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/britain_1942-q4_10th_armoured_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1942-Q4', '51st (Highland) Infantry Division',
    'Infantry Division', 'division',
    'Major-General Douglas Neil Wimberley', 'Major-General',
    16420, 720, 2850, 12850,
    0, 0, 0, 0,
    174, 2840, 0,
    78, 3, '51hd.co.uk - 51st Highland Division Official History Website',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/britain_1942-q4_51st_highland_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'french', '1943-Q1', '1re Division Française Libre (1st Free French Division)',
    'Motorized Infantry Division', 'division',
    'Général de Division Edgard de Larminat', 'Général de Division',
    15200, 720, 2280, 12200,
    52, 0, 28, 24,
    96, 1850, 0,
    72, 3, 'Web search: Chemins de mémoire - 1st Free French Division official history',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/france_1943-q1_1st_free_french_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1941-Q4', '15. Panzer-Division',
    'Panzer Division', 'division',
    'Generalmajor Walter Neumann-Silkow', 'Generalmajor',
    14500, 620, 2500, 11380,
    125, 0, 90, 35,
    148, 2150, 0,
    82, 3, 'Nafziger Collection - Weekly Overall Strengths of 15th Panzer Division, November 1941-February 1942',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/germany_1941-q4_15_panzer_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1942-Q1', '90. leichte Afrika-Division',
    'Light Infantry Division', 'division',
    'Generalmajor Richard Veith', 'Generalmajor',
    10800, 435, 1730, 8635,
    0, 0, 0, 0,
    78, 1920, 0,
    88, 1, 'Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 06 (Tier 1, 95% confidence)',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/germany_1942-q1_90_leichte_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'german', '1942-Q2', '21. Panzer-Division',
    'Panzer Division', 'division',
    'Generalmajor Georg von Bismarck', 'Generalmajor',
    13800, 580, 2350, 10870,
    142, 0, 110, 32,
    134, 2080, 0,
    85, 1, 'Georg Tessin - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS, Band 02 and 05',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760247716952/units/germany_1942-q2_21_panzer_division_toe.json'
);

COMMIT;