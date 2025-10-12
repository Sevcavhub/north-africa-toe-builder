-- Database Backfill SQL
-- Generated: 2025-10-12T14:05:26.992Z
-- Units to insert: 68

-- Unit 1: british 7th Armoured Division (1940-Q2)
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

-- Unit 2: british 50th (Northumbrian) Infantry Division (1941-Q2)
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

-- Unit 3: french 1re Brigade Française Libre (1942-Q2)
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

-- Unit 4: french Division de Marche du Maroc (1943-Q1)
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

-- Unit 5: german 5. leichte Division (1941-Q1)
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

-- Unit 6: german Deutsches Afrikakorps (DAK) (1941-Q2)
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

-- Unit 7: german 21. Panzer-Division (1941-Q3)
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

-- Unit 8: german 90. leichte Afrika-Division (1941-Q3)
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

-- Unit 9: british 4th Indian Infantry Division (1940-Q2)
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

-- Unit 10: italian 27a Divisione di Fanteria "Brescia" (1940-Q3)
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

-- Unit 11: italian 132ª Divisione Corazzata "Ariete" (1940-Q4)
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

-- Unit 12: italian 25ª Divisione di Fanteria 'Bologna' (1940-Q4)
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

-- Unit 13: italian 101ª Divisione motorizzata 'Trieste' (1941-Q1)
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

-- Unit 14: british 2nd New Zealand Division (1941-Q1)
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

-- Unit 15: american 1st Armored Division (1942-Q4)
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

-- Unit 16: american 1st Infantry Division (1942-Q4)
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

-- Unit 17: american II Corps (1943-Q1)
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

-- Unit 18: italian 17a Divisione di Fanteria "Pavia" (1940-Q3)
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

-- Unit 19: italian 132ª Divisione Corazzata 'Ariete' (1940-Q4)
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

-- Unit 20: italian 27a Divisione di Fanteria "Brescia" (1940-Q4)
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

-- Unit 21: italian 55ª Divisione di Fanteria "Savona" (1940-Q4)
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

-- Unit 22: italian 102ª Divisione Motorizzata "Trento" (1940-Q4)
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

-- Unit 23: italian 132ª Divisione Corazzata 'Ariete' (1941-Q1)
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

-- Unit 24: italian 25ª Divisione di Fanteria 'Bologna' (1941-Q1)
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

-- Unit 25: italian 27ª Divisione di Fanteria "Brescia" (1941-Q1)
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

-- Unit 26: italian 101st TRIESTE Division (1941-Q1)
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

-- Unit 27: italian 132ª Divisione Corazzata 'Ariete' (1941-Q2)
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

-- Unit 28: italian 101ª Divisione motorizzata "Trieste" (1941-Q2)
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

-- Unit 29: italian 133ª Divisione Corazzata 'Littorio' (1942-Q1)
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

-- Unit 30: italian 133rd LITTORIO Armored Division (1942-Q2)
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

-- Unit 31: italian 185ª Divisione Paracadutisti Folgore (1942-Q3)
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

-- Unit 32: italian 133a Divisione Corazzata LITTORIO (1942-Q3)
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

-- Unit 33: italian 185a Divisione Paracadutisti FOLGORE (1942-Q4)
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

-- Unit 34: italian 133a Divisione Corazzata Littorio (1942-Q4)
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

-- Unit 35: british 2nd New Zealand Division (1941-Q2)
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

-- Unit 36: british 4th Indian Infantry Division (1941-Q2)
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

-- Unit 37: british 50th (Northumbrian) Infantry Division (1941-Q2)
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

-- Unit 38: british 7th Armoured Division (1941-Q2)
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

-- Unit 39: british 9th Australian Division (1941-Q3)
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

-- Unit 40: british 1st Armoured Division (1941-Q4)
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

-- Unit 41: german 15. Panzer-Division (1941-Q2)
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

-- Unit 42: german 5. leichte Division (1941-Q2)
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

-- Unit 43: german 21. Panzer-Division (1941-Q3)
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

-- Unit 44: german 90. leichte Afrika-Division (1941-Q3)
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

-- Unit 45: unknown Unknown Unit (unknown)
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

-- Unit 46: italian 17ª Divisione di fanteria "Pavia" (1941-Q2)
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

-- Unit 47: italian 27ª Divisione di fanteria "Brescia" (1941-Q2)
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

-- Unit 48: italian 55ª Divisione motorizzata "Trento" (1941-Q2)
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

-- Unit 49: italian 60ª Divisione di fanteria "Sabratha" (1941-Q2)
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

-- Unit 50: british Western Desert Force (1940-Q2)
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

-- Unit 51: british 7th Armoured Division (1940-Q3)
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

-- Unit 52: british 5th Indian Infantry Division (1941-Q1)
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

-- Unit 53: british 1st South African Infantry Division (1941-Q2)
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

-- Unit 54: british 9th Australian Division (1942-Q2)
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

-- Unit 55: british 10th Armoured Division (1942-Q4)
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

-- Unit 56: british 51st (Highland) Infantry Division (1942-Q4)
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

-- Unit 57: french 1re Division Française Libre (1st Free French Division) (1943-Q1)
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

-- Unit 58: german 15. Panzer-Division (1941-Q4)
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

-- Unit 59: german 90. leichte Afrika-Division (1942-Q1)
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

-- Unit 60: german 21. Panzer-Division (1942-Q2)
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

-- Unit 61: german 164. leichte Afrika-Division (1942-Q3)
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

-- Unit 62: german Panzerarmee Afrika (1942-Q3)
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

-- Unit 63: italian 102ª Divisione Motorizzata "Trento" (1941-Q1)
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

-- Unit 64: italian 55ª Divisione di Fanteria "Savona" (1941-Q2)
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

-- Unit 65: italian 25th Infantry Division "Bologna" (1941-Q3)
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

-- Unit 66: italian 17ª Divisione di Fanteria "Pavia" (1941-Q3)
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

-- Unit 67: german 15. Panzer-Division (1941-Q2)
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

-- Unit 68: german Deutsches Afrikakorps (1941-Q2)
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

