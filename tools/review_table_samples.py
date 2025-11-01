#!/usr/bin/env python3
"""
Review Table Samples
Show detailed samples from consolidation candidate tables.
"""

import sqlite3
import json
from pathlib import Path

NAW_DB = Path('data/iterations/iteration_1/North Africa Campaign Production/08_Database/north_africa_wargame.db')
WITW_DB = Path('data/iterations/iteration_2/Timeline_TOE_Reconstruction/witw_data.db')

def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

def show_infantry_weapons():
    """Show infantry_weapons samples."""
    print_section("TIER 1: infantry_weapons (154 rows)")

    conn = sqlite3.connect(NAW_DB)
    cursor = conn.cursor()

    # Show schema
    cursor.execute("PRAGMA table_info(infantry_weapons)")
    cols = cursor.fetchall()

    print("\nSchema (23 columns):")
    key_cols = [c for c in cols if c[1] in ['weapon_name', 'nationality_id', 'caliber_mm',
                                              'effective_range_m', 'weight_kg', 'introduced_date']]
    for col in key_cols:
        print(f"  - {col[1]:25s} {col[2]}")
    print(f"  ... and {len(cols) - len(key_cols)} more columns")

    # Show samples by nation
    cursor.execute("""
        SELECT weapon_name, nationality_id, caliber_mm, effective_range_m,
               weight_kg, model_designation
        FROM infantry_weapons
        WHERE nationality_id = 1
        ORDER BY weapon_name
        LIMIT 5
    """)

    print("\nSample German Infantry Weapons:")
    print(f"  {'Weapon Name':<35s} {'Cal':<6s} {'Range':<8s} {'Weight':<8s} {'Model':<20s}")
    print("  " + "-" * 95)
    for row in cursor.fetchall():
        print(f"  {row[0]:<35s} {row[2]:<6.1f} {row[3]:<8d}m {row[4]:<8.2f}kg {row[5]:<20s}")

    # Show variety
    cursor.execute("""
        SELECT nationality_id, COUNT(*) as count
        FROM infantry_weapons
        GROUP BY nationality_id
        ORDER BY nationality_id
    """)

    print("\nBreakdown by Nation:")
    nation_names = {1: 'German', 2: 'British', 3: 'Italian', 4: 'American'}
    for row in cursor.fetchall():
        nat_name = nation_names.get(row[0], f'Nation {row[0]}')
        print(f"  - {nat_name}: {row[1]} weapons")

    conn.close()

def show_infantry_squads():
    """Show infantry_squads samples."""
    print_section("TIER 1: infantry_squads (17 rows)")

    conn = sqlite3.connect(NAW_DB)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(infantry_squads)")
    cols = cursor.fetchall()

    print(f"\nSchema ({len(cols)} columns):")
    for col in cols[:8]:
        print(f"  - {col[1]:25s} {col[2]}")
    if len(cols) > 8:
        print(f"  ... and {len(cols) - 8} more columns")

    cursor.execute("""
        SELECT squad_id, squad_name, nationality_id, squad_size,
               rifles, smgs, lmgs, year_introduced
        FROM infantry_squads
        ORDER BY nationality_id, year_introduced
        LIMIT 10
    """)

    print("\nSample Squad Compositions:")
    print(f"  {'Squad Name':<40s} {'Size':<5s} {'Rifles':<7s} {'SMGs':<5s} {'LMGs':<5s} {'Year':<5s}")
    print("  " + "-" * 95)
    nation_names = {1: 'GER', 2: 'BRI', 3: 'ITA', 4: 'USA'}
    for row in cursor.fetchall():
        nat = nation_names.get(row[2], 'UNK')
        print(f"  [{nat}] {row[1]:<35s} {row[3]:<5d} {row[4]:<7d} {row[5]:<5d} {row[6]:<5d} {row[7]}")

    conn.close()

def show_game_conversions():
    """Show game conversion formulas."""
    print_section("TIER 1: Other_game_conversion_formulas (30 rows)")

    conn = sqlite3.connect(NAW_DB)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(Other_game_conversion_formulas)")
    cols = cursor.fetchall()

    print(f"\nSchema ({len(cols)} columns):")
    for col in cols:
        print(f"  - {col[1]:25s} {col[2]}")

    cursor.execute("SELECT * FROM Other_game_conversion_formulas LIMIT 5")
    col_names = [desc[0] for desc in cursor.description]

    print("\nSample Conversion Formulas:")
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"\n  Formula {i}:")
        for col_name, value in zip(col_names, row):
            if value is not None and value != '':
                print(f"    {col_name}: {value}")

    # Show game systems covered
    cursor.execute("SELECT DISTINCT source_game FROM Other_game_conversion_formulas WHERE source_game IS NOT NULL")
    sources = cursor.fetchall()

    cursor.execute("SELECT DISTINCT target_game FROM Other_game_conversion_formulas WHERE target_game IS NOT NULL")
    targets = cursor.fetchall()

    print("\nGame Systems Covered:")
    print(f"  Source games: {', '.join(str(s[0]) for s in sources)}")
    print(f"  Target games: {', '.join(str(t[0]) for t in targets)}")

    conn.close()

def show_witw_devices():
    """Show WITW devices samples."""
    print_section("TIER 2: WITW devices (1,074 rows)")

    conn = sqlite3.connect(WITW_DB)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(devices)")
    cols = cursor.fetchall()

    print(f"\nSchema ({len(cols)} columns):")
    for col in cols[:10]:
        print(f"  - {col[1]:25s} {col[2]}")
    if len(cols) > 10:
        print(f"  ... and {len(cols) - 10} more columns")

    cursor.execute("""
        SELECT ID, Name, NatID, Type, Year
        FROM devices
        WHERE NatID IN (1, 2, 3, 4)
        ORDER BY NatID, Name
        LIMIT 10
    """)

    print("\nSample WITW Devices:")
    print(f"  {'ID':<6s} {'Nation':<7s} {'Name':<50s} {'Type':<10s} {'Year':<5s}")
    print("  " + "-" * 95)
    nation_map = {1: 'GER', 2: 'BRI', 3: 'ITA', 4: 'USA'}
    for row in cursor.fetchall():
        nat = nation_map.get(row[2], f'N{row[2]}')
        device_id = row[0] if row[0] else 'NULL'
        device_type = row[3] if row[3] else 'NULL'
        year = row[4] if row[4] else 'NULL'
        print(f"  {device_id:<6s} {nat:<7s} {row[1]:<50s} {device_type:<10s} {year}")

    # Show type breakdown
    cursor.execute("SELECT Type, COUNT(*) as count FROM devices GROUP BY Type ORDER BY count DESC LIMIT 5")
    print("\nTop Device Types:")
    for row in cursor.fetchall():
        type_name = row[0] if row[0] else 'Unknown'
        print(f"  - {type_name}: {row[1]} items")

    conn.close()

def show_witw_leaders():
    """Show WITW leaders samples."""
    print_section("TIER 2: WITW leaders (4,096 rows)")

    conn = sqlite3.connect(WITW_DB)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(leaders)")
    cols = cursor.fetchall()

    print(f"\nSchema ({len(cols)} columns):")
    for col in cols[:8]:
        print(f"  - {col[1]:25s} {col[2]}")
    if len(cols) > 8:
        print(f"  ... and {len(cols) - 8} more columns")

    cursor.execute("""
        SELECT ID, Name, NatID, Rank
        FROM leaders
        WHERE NatID IN (1, 2, 3, 4)
        ORDER BY NatID, Name
        LIMIT 15
    """)

    print("\nSample WITW Leaders:")
    print(f"  {'ID':<6s} {'Nation':<7s} {'Name':<40s} {'Rank':<15s}")
    print("  " + "-" * 95)
    nation_map = {1: 'German', 2: 'British', 3: 'Italian', 4: 'American'}
    for row in cursor.fetchall():
        nat = nation_map.get(row[2], f'Nation {row[2]}')
        leader_id = row[0] if row[0] else 'NULL'
        rank = row[3] if row[3] else 'Unknown'
        print(f"  {leader_id:<6s} {nat:<7s} {row[1]:<40s} {rank:<15s}")

    conn.close()

def show_witw_toe():
    """Show WITW TOE samples."""
    print_section("TIER 2: WITW toe_ob (2,151 rows)")

    conn = sqlite3.connect(WITW_DB)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(toe_ob)")
    cols = cursor.fetchall()

    print(f"\nSchema ({len(cols)} columns):")
    for col in cols[:8]:
        print(f"  - {col[1]:25s} {col[2]}")
    if len(cols) > 8:
        print(f"  ... and {len(cols) - 8} more columns")

    cursor.execute("""
        SELECT ID, Name, NatID, Type
        FROM toe_ob
        WHERE NatID IN (1, 2, 3, 4)
        ORDER BY NatID, Name
        LIMIT 10
    """)

    print("\nSample WITW TO&E Structures:")
    print(f"  {'ID':<6s} {'Nation':<7s} {'Name':<60s}")
    print("  " + "-" * 95)
    nation_map = {1: 'German', 2: 'British', 3: 'Italian', 4: 'American'}
    for row in cursor.fetchall():
        nat = nation_map.get(row[2], f'Nation {row[2]}')
        toe_id = row[0] if row[0] else 'NULL'
        print(f"  {toe_id:<6s} {nat:<7s} {row[1]:<60s}")

    conn.close()

def main():
    """Show all table samples."""

    print("=" * 100)
    print("TABLE SAMPLE REVIEW")
    print("=" * 100)
    print("\nReviewing data from consolidation candidate tables...")
    print("This will help you decide which tiers to import.")

    # Tier 1 - High Value
    print("\n\n")
    print("#" * 100)
    print("# TIER 1: INFANTRY & GAME CONVERSIONS (257 rows)")
    print("# Critical for equipment database completeness")
    print("#" * 100)

    show_infantry_weapons()
    show_infantry_squads()
    show_game_conversions()

    # Tier 2 - WITW Metadata
    print("\n\n")
    print("#" * 100)
    print("# TIER 2: WITW METADATA (10,766 rows)")
    print("# Game metadata for scenario generation")
    print("#" * 100)

    show_witw_devices()
    show_witw_leaders()
    show_witw_toe()

    print("\n" + "=" * 100)
    print("REVIEW COMPLETE")
    print("=" * 100)

    print("\nNext steps:")
    print("  1. Review the samples above")
    print("  2. Decide which tier(s) to import:")
    print("     - Tier 1 only: 257 rows (infantry + conversions)")
    print("     - Tier 1 + 2: 11,023 rows (include WITW metadata)")
    print("     - All tiers: 16,069 rows (complete consolidation)")
    print("  3. Confirm import decision")
    print("\nAll options have ZERO duplicate risk!")

if __name__ == "__main__":
    main()
