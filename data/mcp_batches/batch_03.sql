BEGIN TRANSACTION;

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1940-Q4', '55ª Divisione di Fanteria "Savona"',
    'Auto-transportable Infantry Division', 'division',
    'Pietro Maggiani', 'Generale di Divisione',
    12169, 465, 2890, 8814,
    0, 0, 0, 0,
    36, 1937, 0,
    78, 3, 'TM E 30-420 Handbook on Italian Military Forces (August 1943) - Tier 1 primary source',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1940q4_savona_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1940-Q4', '102ª Divisione Motorizzata "Trento"',
    'Motorized Infantry Division (Autotrasportabile)', 'division',
    'Luigi Nuvoloni', 'Generale di Divisione',
    10500, 420, 1890, 8190,
    0, 0, 0, 0,
    60, 2845, 0,
    78, 3, 'Wikipedia: 102nd Motorised Division Trento (formation date, organization, commanders, deployment timeline)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1940q4_trento_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q1', '132ª Divisione Corazzata ''Ariete''',
    'Armored Division', 'division',
    'Generale di Divisione Ettore Baldassarre', 'Generale di Divisione (Major General)',
    6949, 236, 1200, 5513,
    163, 0, 46, 117,
    97, 1534, 0,
    78, 3, 'TM E 30-420 Handbook on Italian Military Forces 1943 (US War Department)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1941q1_ariete_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q1', '25ª Divisione di Fanteria ''Bologna''',
    'Divisione Autotrasportabile AS (Semi-Motorized Infantry Division, North Africa Type)', 'division',
    'Generale di Divisione Roberto Lerici', 'Generale di Divisione',
    10125, 410, 1098, 8617,
    38, 0, 0, 38,
    64, 468, 0,
    88, 3, 'Order-of-battle of the Italian Army, USA HQ G-2 (July 1943) - PRIMARY SOURCE',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1941q1_bologna_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q1', '27ª Divisione di Fanteria "Brescia"',
    'Divisione Autotrasportabile (Semi-Motorized Infantry Division)', 'division',
    'Brunetto Brunetti', 'Generale di Divisione',
    7595, 350, 1268, 5977,
    12, 0, 0, 12,
    48, 503, 0,
    87, 3, 'Order-of-battle of the Italian Army, USA HQ G-2 (July 1943) - PRIMARY SOURCE (95% confidence)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1941q1_brescia_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q1', '101st TRIESTE Division',
    'Semi-Motorized Infantry Division', 'division',
    'Not specified in source', 'Divisional General',
    11800, 485, 1890, 9425,
    0, 0, 0, 0,
    76, 1680, 0,
    87, 3, 'US Army G-2 Order of Battle of the Italian Army (July 1943) - Primary source pages 101-102',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1941q1_trieste_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q2', '132ª Divisione Corazzata ''Ariete''',
    'Armored Division', 'division',
    'Generale di Divisione Ettore Baldassarre', 'Generale di Divisione (Major General)',
    7458, 258, 1280, 5920,
    186, 0, 75, 111,
    106, 1687, 0,
    85, 3, 'TM E 30-420 Handbook on Italian Military Forces 1943 (US War Department) - PRIMARY SOURCE',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1941q2_ariete_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1941-Q2', '101ª Divisione motorizzata "Trieste"',
    'Motorized Infantry Division', 'division',
    'Unknown', 'Generale di Divisione',
    9500, 520, 1850, 7130,
    46, 0, 0, 46,
    84, 980, 0,
    78, 3, 'TM E 30-420 Handbook on Italian Military Forces (1943) - Primary source, pages discussing motorized division organization, artillery regiments, and equipment specifications',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1941q2_trieste_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1942-Q1', '133ª Divisione Corazzata ''Littorio''',
    'Armored Division', 'division',
    'Generale di Divisione Gervasio Bitossi', 'Generale di Divisione (Major General)',
    7842, 284, 1358, 6200,
    189, 0, 146, 43,
    108, 1687, 0,
    82, 3, 'Order-of-battle-of-the-Italian-Army-USA-HQ-G2-July-1943.txt (US Military Intelligence primary source, 95% confidence)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1942q1_littorio_division_toe.json'
);

INSERT OR IGNORE INTO units (
    nation, quarter, unit_designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    tanks_total, tanks_heavy, tanks_medium, tanks_light,
    artillery_total, ground_vehicles_total, aircraft_total,
    confidence_score, source_tier, primary_source, extraction_date, json_file_path
) VALUES (
    'italian', '1942-Q2', '133rd LITTORIO Armored Division',
    'Armored Division (Divisione Corazzata)', 'division',
    'Unknown', 'Major General',
    7400, 350, 940, 6110,
    152, 0, 112, 40,
    78, 2920, 0,
    85, 3, 'Order of Battle of the Italian Army, USA HQ G-2, July 1943 (Primary source, 95% confidence)',
    '2025-10-10', 'D:/north-africa-toe-builder/data/output/autonomous_1760155681040/units/italy_1942q2_littorio_division_toe.json'
);

COMMIT;