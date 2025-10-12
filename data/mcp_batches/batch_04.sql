BEGIN TRANSACTION;

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1942-Q3', '185ª Divisione Paracadutisti Folgore',
    'Paratrooper Division (Elite Infantry)', 'division',
    'Generale di Brigata Enrico Frattini', 'Brigadier General',
    5200, 310, 780, 4110,
    0, 0, 0, 0,
    44, 45, 0,
    78, 3, 'TM E 30-420 Italian Military Forces (1943) - Parachute division organization',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1942q3_folgore_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1942-Q3', '133a Divisione Corazzata LITTORIO',
    'Armored Division', 'division',
    'Unknown', 'Generale di Divisione',
    7800, 380, 920, 6500,
    133, 0, 110, 23,
    104, 1850, 0,
    80, 3, 'Order of Battle of the Italian Army, USA HQ G-2, July 1943 (Primary Source - US Military Intelligence)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1942q3_littorio_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1942-Q4', '185a Divisione Paracadutisti FOLGORE',
    'Parachute Division', 'division',
    'Unknown', 'Brigadier General',
    5200, 320, 780, 4100,
    0, 0, 0, 0,
    60, 280, 0,
    82, 3, 'Order of Battle of the Italian Army, USA HQ G2, July 1943 (Primary Source)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1942q4_folgore_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1942-Q4', '133a Divisione Corazzata Littorio',
    'Armored Division', 'division',
    'Unknown', 'Generale di Divisione',
    6800, 380, 920, 5500,
    82, 0, 58, 24,
    86, 1840, 0,
    85, 3, 'Order of Battle of the Italian Army, USA War Department Military Intelligence Service, July 1943 (Primary source, 95% confidence)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1942q4_littorio_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q2', '2nd New Zealand Division',
    'Infantry Division (Commonwealth)', 'division',
    'Major-General Bernard Cyril Freyberg', 'Major-General',
    20000, 920, 2850, 16230,
    0, 0, 0, 0,
    156, 2800, 0,
    82, 3, 'British Army List April 1941 (Primary source)',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/britain_1941q2_2nd_new_zealand_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q2', '4th Indian Infantry Division',
    'Infantry Division', 'division',
    'Major-General Frank Walter Messervy', 'Major-General',
    17000, 680, 2380, 13940,
    0, 0, 0, 0,
    120, 3260, 0,
    75, 3, 'British Army Lists April 1941 (armylistapr1941grea) - Commanders and officer rosters verified',
    '2025-10-11T15:45:00Z', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/britain_1941q2_4th_indian_division_toe.json'
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
    'Major-General William Ramsden', 'Major-General',
    17298, 692, 2594, 14012,
    0, 0, 0, 0,
    168, 4166, 0,
    88, 3, 'British Military Forces and Equipment Database (verified division strength 17,298)',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/britain_1941q2_50th_infantry_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q2', '7th Armoured Division',
    'Armoured Division', 'division',
    'Major-General Michael O''Moore Creagh', 'Major-General',
    14964, 598, 2245, 12121,
    190, 100, 90, 0,
    112, 4628, 0,
    82, 3, 'British Army Lists April 1941 (armylistapr1941grea) - Officer rosters verified',
    '2025-10-11T14:30:00Z', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/britain_1941q2_7th_armoured_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q3', '9th Australian Division',
    'Infantry Division', 'division',
    'Leslie James Morshead', 'Major-General',
    14000, 700, 2800, 10500,
    0, 0, 0, 0,
    120, 1240, 0,
    82, 3, 'Australian War Memorial Official Histories',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/britain_1941q3_9th_australian_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q4', '1st Armoured Division',
    'Armoured Division', 'division',
    'Major-General Herbert Lumsden', 'Major-General',
    14200, 780, 2840, 10580,
    184, 0, 124, 60,
    72, 1850, 0,
    78, 3, 'British Army Lists October-December 1941',
    '2025-10-11', 'D:/north-africa-toe-builder/data/output/autonomous_1760203201365/units/britain_1941q4_1st_armoured_division_toe.json'
);

COMMIT;