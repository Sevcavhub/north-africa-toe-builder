BEGIN TRANSACTION;

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1940-Q4', '132ª Divisione Corazzata "Ariete"',
    'Armored Division', 'division',
    'Generale di Divisione Ettore Baldassarre', 'Generale di Divisione',
    7500, 350, 1200, 5950,
    111, 0, 37, 74,
    60, 520, 0,
    72, 3, 'Wikipedia: 132nd Armored Division Ariete (organization structure, commanders, battalion details)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/italy_1940q4_ariete_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1940-Q4', '25ª Divisione di Fanteria ''Bologna''',
    'Divisione Autotrasportabile AS (Auto-transportable Infantry Division, North Africa Type)', 'division',
    'Generale di Divisione Roberto Lerici', 'Generale di Divisione',
    10978, 445, 1203, 9330,
    46, 0, 0, 46,
    68, 545, 0,
    82, 3, 'TME 30-420: Handbook on the Italian Military Forces (1943) - US War Department',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/italy_1940q4_bologna_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q1', '101ª Divisione motorizzata ''Trieste''',
    'Motorized Infantry Division', 'division',
    'Generale di Divisione Francesco La Ferla', 'Generale di Divisione',
    10000, 420, 1680, 7900,
    0, 0, 0, 0,
    84, 1842, 0,
    78, 3, 'TM E 30-420 ''Handbook on Italian Military Forces'' (1943) - Primary source',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/italy_1941q1_trieste_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'british', '1941-Q1', '2nd New Zealand Division',
    'Commonwealth Infantry Division', 'division',
    'Lieutenant-General Bernard Freyberg', 'Lieutenant-General',
    17500, 875, 2625, 14000,
    0, 0, 0, 0,
    120, 2200, 0,
    78, 3, 'Web search: 2nd New Zealand Division organization 1941',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/newzealand_1941q1_2nd_nz_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'american', '1942-Q4', '1st Armored Division',
    'Heavy Armored Division', 'division',
    'Orlando Ward', 'Major General',
    14630, 585, 2195, 11850,
    390, 0, 232, 158,
    102, 2654, 0,
    77, 3, '1st Armored Division (United States) - Wikipedia (75% confidence)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/usa_1942q4_1st_armored_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'american', '1942-Q4', '1st Infantry Division',
    'Infantry Division', 'division',
    'Major General Terry de la Mesa Allen', 'Major General',
    14253, 856, 2134, 11263,
    0, 0, 0, 0,
    75, 2012, 0,
    85, 3, 'FM 7-20: Infantry Battalion (1942) - US War Department',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/usa_1942q4_1st_infantry_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'american', '1943-Q1', 'II Corps',
    'Army Corps', 'corps',
    'Major General Lloyd Fredendall', 'Major General',
    95000, 4750, 14250, 76000,
    390, 0, 320, 70,
    420, 23218, 0,
    80, 3, '1943-Q1_Enhanced_COMPREHENSIVE_v4.json - US forces data',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760133539236/units/usa_1943q1_ii_corps_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1940-Q3', '17a Divisione di Fanteria "Pavia"',
    'Autotrasportabile Infantry Division', 'division',
    'Pietro Zaglio', 'Generale di Divisione',
    7500, 345, 1250, 5905,
    12, 0, 0, 12,
    48, 492, 0,
    80, 3, 'TM-E 30-420 Handbook on Italian Military Forces (August 1943) - Paragraph 68 (autotrasportabile regiment)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1940q3_pavia_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1940-Q4', '132ª Divisione Corazzata ''Ariete''',
    'Armored Division', 'division',
    'Generale di Divisione Ettore Baldassarre', 'Generale di Divisione (Major General)',
    6124, 198, 1015, 4911,
    140, 0, 37, 103,
    72, 1187, 0,
    87, 3, 'Order of Battle of the Italian Army, US HQ G2, July 1943 (Primary Source - US War Department)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1940q4_ariete_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1940-Q4', '27a Divisione di Fanteria "Brescia"',
    'Autotrasportabile Infantry Division', 'division',
    'Giuseppe Cremascoli', 'Generale di Divisione',
    7520, 345, 1255, 5920,
    12, 0, 0, 12,
    48, 495, 0,
    82, 3, 'TM-E 30-420 Handbook on Italian Military Forces (August 1943) - Section 51, 54, Figure 5',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1940q4_brescia_division_toe.json'
);

COMMIT;