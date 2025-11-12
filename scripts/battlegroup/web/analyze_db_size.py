#!/usr/bin/env python3
"""Analyze database table sizes for web deployment optimization."""

import sqlite3
from pathlib import Path

db_path = Path("database/master_database.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in cursor.fetchall()]

# Get row count for each table
print(f"{'Table Name':<50} {'Row Count':>10}")
print("=" * 65)

table_data = []
total_rows = 0

for table in tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = cursor.fetchone()[0]
        total_rows += count
        if count > 0:  # Only show non-empty tables
            table_data.append((table, count))
    except Exception as e:
        print(f"{table:<50} ERROR: {e}")

# Sort by row count descending
table_data.sort(key=lambda x: x[1], reverse=True)

for table, count in table_data:
    print(f"{table:<50} {count:>10,}")

print("=" * 65)
print(f"{'TOTAL':<50} {total_rows:>10,}")

# Get database file size
db_size_bytes = db_path.stat().st_size
db_size_mb = db_size_bytes / (1024 * 1024)
print(f"\nDatabase file size: {db_size_mb:.2f} MB ({db_size_bytes:,} bytes)")

conn.close()

# Categorize tables
print("\n" + "=" * 65)
print("TABLE CATEGORIZATION FOR WEB DEPLOYMENT")
print("=" * 65)

web_essential = [
    "equipment", "equipment_battlegroup", "bg_reference_vehicles",
    "bg_reference_guns", "bg_special_rules", "guns", "wwiitanks_afv_data",
    "wwiitanks_gun_data", "penetration_data", "ammunition"
]

web_optional = [
    "units", "unit_equipment", "afv_data", "bg_armor_conversion",
    "bg_penetration_scale", "bg_movement_values", "bg_he_effectiveness"
]

can_exclude = [
    # Backup tables
    table for table in tables if 'backup' in table.lower()
] + [
    # Archive tables
    table for table in tables if 'archive' in table.lower()
] + [
    # WITW tables (other game system)
    table for table in tables if table.startswith('witw_')
] + [
    # Other game conversions
    "equipment_stats_achtung_panzer", "equipment_stats_flames_of_war",
    "Other_game_conversion_formulas",
    # Build/extraction metadata
    "extraction_audit", "extraction_log", "import_log", "bg_extraction_log",
    "match_reviews", "normalization_audit", "normalization_audit_new",
    # Reference/example data
    "BG_Reference_Aircraft", "BG_Reference_ArmyList_Examples",
    "BG_Reference_Defences", "BG_Sample_maps",
    # Scenario builder tables (different from web search)
    "BG_Scenario_Army_Lists", "BG_Scenario_Fire_Support", "BG_Scenario_Forces",
    "BG_Scenario_Reinforcement_Groups", "BG_Scenario_Reinforcement_Units",
    "BG_Scenario_Units",
    # Campaign system (Phase 10)
    "bg_campaign_progression", "bg_campaign_units",
    # Builder-specific tables
    "bg_builder_forces", "bg_builder_vehicle_costs", "bg_builder_vehicles",
    "bg_builder_weapons",
    # Infantry (if not needed for web)
    "infantry_squads", "infantry_weapon_types", "infantry_weapons", "squad_weapons",
    # Equipment variants/mapping (use simplified lookup)
    "equipment_name_variants", "equipment_name_variants_new",
    "gun_name_variants", "bg_gun_name_conversion", "bg_weapon_name_lookup",
    # Master equipment (use equipment table instead)
    "master_equipment", "equipment_master_new",
    # Utility tables
    "sqlite_sequence", "schema_version"
]

print("\nESSENTIAL for web (equipment search/display):")
for table in web_essential:
    if table in [t[0] for t in table_data]:
        count = next((c for t, c in table_data if t == table), 0)
        print(f"  ✓ {table:<45} {count:>10,}")

print("\nOPTIONAL (may improve functionality):")
for table in web_optional:
    if table in [t[0] for t in table_data]:
        count = next((c for t, c in table_data if t == table), 0)
        print(f"  ? {table:<45} {count:>10,}")

print("\nCAN EXCLUDE (reduce size):")
excluded_count = 0
for table in can_exclude:
    if table in [t[0] for t in table_data]:
        count = next((c for t, c in table_data if t == table), 0)
        excluded_count += 1
        if count > 0:
            print(f"  ✗ {table:<45} {count:>10,}")

print(f"\nTotal tables that can be excluded: {excluded_count}")
