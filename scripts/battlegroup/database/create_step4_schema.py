#!/usr/bin/env python3
"""
Phase 9B Step 4: Database Schema Creation and Lookup Table Population
Creates 8 new tables for BattleGroup stat generation and campaign tracking.
Populates lookup tables with conversion data from Steps 2-3.
"""

import sqlite3
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"
SCHEMA_PATH = project_root / "scripts" / "battlegroup" / "database" / "step4_schema.sql"


def create_schema():
    """Create Step 4 database schema."""

    print("Phase 9B Step 4: Database Schema Creation")
    print("=" * 70)
    print()

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Read and execute schema file
        print("Executing schema SQL...")
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()

        cursor.executescript(schema_sql)
        print("[OK] Schema created successfully")
        print()

        # Verify tables created
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'bg_%'
            OR name = 'equipment_battlegroup'
            ORDER BY name
        """)
        tables = cursor.fetchall()

        print(f"Created/verified {len(tables)} BattleGroup tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} rows")
        print()

        conn.commit()
        return conn

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return None


def populate_armor_conversion(conn):
    """Populate bg_armor_conversion table with armor thickness to letter mappings."""

    print("Populating bg_armor_conversion table...")
    cursor = conn.cursor()

    # Armor conversion data (reverse alphabetical: A = thickest, O = thinnest)
    armor_data = [
        # Super heavy armor
        (200, 999, 'A', 6, 'Super Heavy', 'King Tiger, Jagdtiger, Maus'),
        (180, 199, 'B', 7, 'Very Heavy', 'Tiger II (turret), Ferdinand'),
        (150, 179, 'C', 7, 'Very Heavy', 'Tiger I (front), Jagdpanther'),
        (120, 149, 'D', 8, 'Heavy+', 'Tiger I, IS-2, Churchill VII'),
        (100, 119, 'E', 8, 'Heavy', 'Panther (glacis), Churchill (front)'),

        # Medium-heavy armor
        (80, 99, 'F', 9, 'Medium-Heavy', 'Panther (turret), Sherman Jumbo'),
        (70, 79, 'G', 9, 'Medium-Heavy', 'Panzer IV Ausf H/J'),
        (60, 69, 'H', 10, 'Medium+', 'Sherman (75mm variants), T-34'),
        (50, 59, 'I', 10, 'Medium', 'Panzer IV Ausf F/G, Cromwell'),
        (45, 49, 'J', 11, 'Medium', 'Sherman M4A3, StuG III (late)'),

        # Medium-light armor
        (40, 44, 'K', 11, 'Medium-Light', 'Panzer IV Ausf E, early T-34'),
        (35, 39, 'L', 12, 'Light+', 'Panzer III late, M3 Lee/Grant'),
        (30, 34, 'M', 12, 'Light', 'Panzer III mid, early StuG, M3 Stuart'),
        (20, 29, 'N', 13, 'Very Light', 'Panzer II, Pz 38(t), armored cars'),
        (5, 19, 'O', 13, 'Very Light', 'Halftracks, light armored cars'),

        # Soft-skinned (no letter)
        (0, 4, 'Soft-Skinned', None, 'No Armor', 'Trucks, jeeps, towed guns')
    ]

    for mm_min, mm_max, letter, numeric, description, examples in armor_data:
        cursor.execute("""
            INSERT OR IGNORE INTO bg_armor_conversion
            (mm_min, mm_max, letter, numeric_value, description, typical_vehicles)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (mm_min, mm_max, letter, numeric, description, examples))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM bg_armor_conversion")
    count = cursor.fetchone()[0]
    print(f"  [OK] Populated {count} armor conversion entries")
    print()


def populate_penetration_scale(conn):
    """Populate bg_penetration_scale table with caliber/barrel length to penetration mappings."""

    print("Populating bg_penetration_scale table...")
    cursor = conn.cursor()

    # Penetration scale data (common guns, values derived from Step 2 validation)
    pen_data = [
        # German guns
        (37, 'L/45', 38, 3, 3, 2, 1, 0, None, '3.7cm PaK36'),
        (50, 'L/42', 60, 5, 5, 4, 3, 2, None, '5cm KwK38 (Panzer III Ausf F-H)'),
        (50, 'L/60', 67, 6, 6, 5, 4, 3, None, '5cm KwK39 (Panzer III Ausf J-M)'),
        (75, 'L/24', 43, 4, 4, 3, 2, 1, None, '7.5cm KwK37 (Panzer IV Ausf A-F1)'),
        (75, 'L/43', 92, 7, 7, 6, 5, 4, None, '7.5cm KwK40 L/43 (Panzer IV Ausf F2-G)'),
        (75, 'L/48', 106, 8, 8, 7, 6, 5, None, '7.5cm KwK40 L/48 (Panzer IV Ausf H-J)'),
        (75, 'L/70', 138, 10, 10, 9, 8, 7, None, '7.5cm KwK42 (Panther)'),
        (88, 'L/56', 110, 9, 9, 8, 7, 6, 5, '8.8cm KwK36 (Tiger I)'),
        (88, 'L/71', 165, 12, 12, 11, 10, 9, 8, '8.8cm KwK43 (Tiger II, Jagdpanther)'),

        # British guns
        (40, 'L/52', 57, 5, 5, 4, 3, 2, None, '2-pdr (40mm)'),
        (57, 'L/43', 74, 6, 6, 5, 4, 3, None, '6-pdr Mk III (57mm)'),
        (57, 'L/50', 89, 7, 7, 6, 5, 4, None, '6-pdr Mk V (57mm)'),
        (76, 'L/55', 110, 9, 9, 8, 7, 6, 5, '17-pdr (76.2mm)'),
        (75, 'L/37', 60, 6, 6, 5, 4, 3, None, 'QF 75mm (Sherman)'),

        # American guns
        (37, 'L/50', 46, 4, 4, 3, 2, 1, None, '37mm M6 (M3/M5 Stuart)'),
        (75, 'L/37', 60, 6, 6, 5, 4, 3, None, '75mm M3 (M4 Sherman, M3 Grant)'),
        (75, 'L/40', 68, 6, 6, 5, 4, 3, None, '75mm M2/M3 (M4 Sherman)'),
        (76, 'L/52', 109, 9, 9, 8, 7, 6, None, '76mm M1 (M4A3E8, M18)'),

        # Soviet guns
        (45, 'L/46', 51, 5, 5, 4, 3, 2, None, '45mm 20-K (T-26, BT-7)'),
        (76, 'L/30', 55, 5, 5, 4, 3, 2, None, '76.2mm L-11 (early T-34, KV-1)'),
        (76, 'L/42', 69, 6, 6, 5, 4, 3, None, '76.2mm F-34 (T-34/76)'),
        (85, 'L/52', 111, 9, 9, 8, 7, 6, 5, '85mm D-5T (T-34/85, SU-85)'),

        # Italian guns
        (47, 'L/32', 40, 4, 4, 3, 2, 1, None, '47mm L/32 (L6/40, AB41)'),
        (47, 'L/40', 53, 5, 5, 4, 3, 2, None, '47mm L/40 (Semovente)')
    ]

    for caliber, barrel, pen_1000m, v0_10, v10_20, v20_30, v30_40, v40_50, v50_70, examples in pen_data:
        cursor.execute("""
            INSERT OR IGNORE INTO bg_penetration_scale
            (caliber_mm, barrel_length, penetration_1000m_mm,
             value_0_10, value_10_20, value_20_30, value_30_40, value_40_50, value_50_70,
             gun_examples)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (caliber, barrel, pen_1000m, v0_10, v10_20, v20_30, v30_40, v40_50, v50_70, examples))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM bg_penetration_scale")
    count = cursor.fetchone()[0]
    print(f"  [OK] Populated {count} penetration scale entries")
    print()


def populate_movement_values(conn):
    """Populate bg_movement_values table with type/weight to movement mappings."""

    print("Populating bg_movement_values table...")
    cursor = conn.cursor()

    # Movement data by type and weight
    movement_data = [
        ('light_tank', 0, 10, 14, 20, 'M3 Stuart, Panzer II, L6/40'),
        ('light_tank', 10, 15, 12, 18, 'Panzer 38(t), T-70'),

        ('medium_tank', 15, 25, 10, 16, 'Panzer III, M4 Sherman, T-34'),
        ('medium_tank', 25, 35, 8, 14, 'Panzer IV, Sherman Firefly'),
        ('medium_tank', 35, 50, 8, 12, 'Panther, Churchill'),

        ('heavy_tank', 50, 60, 6, 10, 'Tiger I, KV-1, Churchill VII'),
        ('heavy_tank', 60, 75, 6, 8, 'Tiger II, IS-2'),

        ('tank_destroyer', 0, 20, 14, 20, 'M18 Hellcat, Marder III'),
        ('tank_destroyer', 20, 40, 10, 14, 'StuG III, M10 Wolverine'),
        ('tank_destroyer', 40, 999, 8, 12, 'Jagdpanther, Ferdinand, Elefant'),

        ('assault_gun', 15, 30, 8, 12, 'StuG III, Semovente 75/18'),
        ('assault_gun', 30, 50, 6, 10, 'StuH 42, Brummbär'),

        ('halftrack', 0, 10, 12, 18, 'SdKfz 251, M3 halftrack'),
        ('halftrack', 10, 15, 10, 16, 'Heavy halftracks'),

        ('armored_car', 0, 10, 14, 24, 'SdKfz 222, Daimler, AB 41, M8 Greyhound'),
        ('armored_car', 10, 15, 12, 20, 'Heavy armored cars, SdKfz 234'),

        ('wheeled', 0, 5, 16, 28, 'Jeeps, Kübelwagen, light trucks'),
        ('wheeled', 5, 999, 12, 24, 'Medium trucks, heavy trucks'),

        ('tracked', 0, 10, 10, 14, 'Light tractors, carriers'),
        ('tracked', 10, 999, 8, 12, 'Heavy tractors')
    ]

    for vtype, wmin, wmax, offroad, road, examples in movement_data:
        cursor.execute("""
            INSERT OR IGNORE INTO bg_movement_values
            (vehicle_type, weight_min_tonnes, weight_max_tonnes,
             off_road, road, typical_vehicles)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (vtype, wmin, wmax, offroad, road, examples))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM bg_movement_values")
    count = cursor.fetchone()[0]
    print(f"  [OK] Populated {count} movement value entries")
    print()


def populate_he_effectiveness(conn):
    """Populate bg_he_effectiveness table with caliber to HE effect mappings."""

    print("Populating bg_he_effectiveness table...")
    cursor = conn.cursor()

    # HE effectiveness data (derived from Step 2 HE calculator validation)
    he_data = [
        (20, 37, 2, '6+', '2/6+', '20mm cannons, small AT rifles'),
        (37, 49, 2, '5+', '2/5+', '37mm guns, 40mm 2-pdr'),
        (50, 74, 3, '5+', '3/5+', '50mm KwK38/39, 57mm 6-pdr'),
        (75, 87, 4, '4+', '4/4+', '75mm guns (Sherman, Panzer IV, StuG)'),
        (88, 104, 4, '3+', '4/3+', '88mm FlaK/KwK36'),
        (105, 119, 5, '3+', '5/3+', '105mm howitzers'),
        (120, 149, 6, '3+', '6/3+', '120-149mm howitzers'),
        (150, 179, 6, '2+', '6/2+', '150-179mm artillery'),
        (180, 999, 8, '2+', '8/2+', '180mm+ heavy artillery')
    ]

    for cal_min, cal_max, dice, target, format_str, examples in he_data:
        cursor.execute("""
            INSERT OR IGNORE INTO bg_he_effectiveness
            (caliber_min_mm, caliber_max_mm, dice, target, format, gun_examples)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cal_min, cal_max, dice, target, format_str, examples))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM bg_he_effectiveness")
    count = cursor.fetchone()[0]
    print(f"  [OK] Populated {count} HE effectiveness entries")
    print()


def populate_special_rules(conn):
    """Populate bg_special_rules table with common BattleGroup special rules."""

    print("Populating bg_special_rules table...")
    cursor = conn.cursor()

    # Common special rules
    rules_data = [
        ('smoke_dischargers', 'Smoke Dischargers', 'defensive',
         'Vehicle can deploy smoke to obscure itself',
         'Once per game, create smoke screen (blocks LOS)', None, None, None,
         'BattleGroup Core Rules', '45'),

        ('command_tank', 'Command Tank', 'command',
         'Enhanced radio equipment for command and control',
         '+6" command radius', None, None, 'tank',
         'BattleGroup Core Rules', '52'),

        ('slow_traverse', 'Slow Traverse', 'firepower',
         'Fixed or limited-traverse gun mount',
         '-1 to hit if vehicle moved', None, None, 'tank,tank_destroyer',
         'BattleGroup Core Rules', '48'),

        ('unreliable', 'Unreliable', 'movement',
         'Prone to mechanical breakdown',
         'On first move, roll D6: 1 = breakdown', None, None, None,
         'BattleGroup Core Rules', '51'),

        ('fast', 'Fast', 'movement',
         'Exceptional speed and maneuverability',
         '+2" to all movement', None, None, None,
         'BattleGroup Core Rules', '47'),

        ('amphibious', 'Amphibious', 'movement',
         'Can traverse water obstacles',
         'Ignore water terrain for movement', None, None, None,
         'BattleGroup Core Rules', '46'),

        ('awkward_layout', 'Awkward Layout', 'firepower',
         'Poor internal ergonomics',
         '-1 to shooting if crew quality Regular or worse', None, None, None,
         'BattleGroup Core Rules', '46'),

        ('gyro_stabilizer', 'Gyro-Stabilized Gun', 'firepower',
         'Stabilized gun mount for firing on the move',
         'No penalty for shooting on the move at half speed or less', 'american,british', '1943-01:1945-05', 'tank',
         'BattleGroup Core Rules', '48')
    ]

    for rule_id, name, category, description, effect, nation, era, unit_type, source_book, source_page in rules_data:
        cursor.execute("""
            INSERT OR IGNORE INTO bg_special_rules
            (rule_id, name, category, description, mechanical_effect,
             nation_specific, era_restriction, unit_type_restriction,
             source_book, source_page)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rule_id, name, category, description, effect, nation, era, unit_type, source_book, source_page))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM bg_special_rules")
    count = cursor.fetchone()[0]
    print(f"  [OK] Populated {count} special rule entries")
    print()


def show_summary(conn):
    """Display summary of created schema."""

    print("=" * 70)
    print("Step 4 Schema Creation COMPLETE!")
    print("=" * 70)
    print()

    cursor = conn.cursor()

    # Count all BattleGroup tables
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND (name LIKE 'bg_%' OR name = 'equipment_battlegroup')
        ORDER BY name
    """)
    tables = cursor.fetchall()

    print(f"Total BattleGroup tables: {len(tables)}")
    print()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]

        # Get column count
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        print(f"{table_name}:")
        print(f"  Rows: {count}")
        print(f"  Columns: {len(columns)}")
        print()

    print("=" * 70)
    print("Next Steps:")
    print("  1. Build equipment enrichment pipeline")
    print("  2. Enrich all 469 equipment items with BattleGroup stats")
    print("  3. Implement generator tools (army lists, datacards, rosters)")
    print("  4. Build campaign tracker")
    print("=" * 70)
    print()


def main():
    """Main execution function."""

    # Create schema
    conn = create_schema()
    if not conn:
        print("[FAILED] Schema creation failed")
        return False

    # Populate lookup tables
    print("Populating lookup tables with conversion data...")
    print()

    populate_armor_conversion(conn)
    populate_penetration_scale(conn)
    populate_movement_values(conn)
    populate_he_effectiveness(conn)
    populate_special_rules(conn)

    # Show summary
    show_summary(conn)

    conn.close()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
