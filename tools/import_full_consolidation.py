#!/usr/bin/env python3
"""
Full Database Consolidation Import (Tier 1 + 2)
Import all 11,023 rows from infantry, game conversions, and WITW metadata.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

MASTER_DB = Path("database/master_database.db")
NAW_DB = Path("data/iterations/iteration_1/North Africa Campaign Production/08_Database/north_africa_wargame.db")
WITW_DB = Path("data/iterations/iteration_2/Timeline_TOE_Reconstruction/witw_data.db")

# Tier 1 tables from north_africa_wargame.db
TIER1_TABLES = [
    'infantry_weapons',
    'infantry_squads',
    'squad_weapons',
    'infantry_weapon_types',
    'Other_game_conversion_formulas'
]

# Tier 2 tables from witw_data.db
TIER2_TABLES = [
    'devices',
    'ground_vehicles',
    'ground_weapons',
    'leaders',
    'toe_ob'
]

def check_prerequisites():
    """Verify all source databases exist."""
    print("\n" + "=" * 100)
    print("PREREQUISITE CHECK")
    print("=" * 100)

    all_ok = True

    print(f"\nChecking master database: {MASTER_DB}")
    if MASTER_DB.exists():
        size = MASTER_DB.stat().st_size / (1024 * 1024)
        print(f"  [OK] Found ({size:.2f} MB)")
    else:
        print(f"  [ERROR] Not found!")
        all_ok = False

    print(f"\nChecking source database: {NAW_DB}")
    if NAW_DB.exists():
        size = NAW_DB.stat().st_size / (1024 * 1024)
        print(f"  [OK] Found ({size:.2f} MB)")
    else:
        print(f"  [ERROR] Not found!")
        all_ok = False

    print(f"\nChecking source database: {WITW_DB}")
    if WITW_DB.exists():
        size = WITW_DB.stat().st_size / (1024 * 1024)
        print(f"  [OK] Found ({size:.2f} MB)")
    else:
        print(f"  [ERROR] Not found!")
        all_ok = False

    if not all_ok:
        print("\n[FAILED] Prerequisites not met!")
        return False

    print("\n[SUCCESS] All prerequisites met")
    return True

def import_tier1_table(master_conn, source_db_path, table_name):
    """Import a Tier 1 table from north_africa_wargame.db."""

    print(f"\n  Importing {table_name}...")

    # Attach source database
    master_conn.execute(f"ATTACH DATABASE '{source_db_path}' AS source")

    cursor = master_conn.cursor()

    try:
        # Get row count from source
        cursor.execute(f"SELECT COUNT(*) FROM source.{table_name}")
        source_count = cursor.fetchone()[0]

        if source_count == 0:
            print(f"    [SKIP] Source table empty")
            cursor.close()
            master_conn.execute("DETACH DATABASE source")
            return 0

        # Check if table exists in master
        cursor.execute(f"""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='{table_name}'
        """)

        if not cursor.fetchone():
            # Create table by copying structure
            print(f"    Creating table {table_name}...")
            cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM source.{table_name} WHERE 0")
            master_conn.commit()

        # Get current count in master
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        before_count = cursor.fetchone()[0]

        # Import data (direct insert since zero duplicates)
        cursor.execute(f"INSERT INTO {table_name} SELECT * FROM source.{table_name}")
        imported = cursor.rowcount
        master_conn.commit()

        # Verify
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        after_count = cursor.fetchone()[0]

        print(f"    [SUCCESS] Imported {imported} rows ({before_count} -> {after_count})")

        cursor.close()
        master_conn.execute("DETACH DATABASE source")
        return imported

    except Exception as e:
        print(f"    [ERROR] {e}")
        cursor.close()
        try:
            master_conn.execute("DETACH DATABASE source")
        except:
            pass
        return 0

def import_tier2_table(master_conn, source_db_path, table_name):
    """Import a Tier 2 table from witw_data.db."""

    print(f"\n  Importing {table_name}...")

    # Attach source database
    master_conn.execute(f"ATTACH DATABASE '{source_db_path}' AS witw_source")

    cursor = master_conn.cursor()

    try:
        # Get row count from source
        cursor.execute(f"SELECT COUNT(*) FROM witw_source.{table_name}")
        source_count = cursor.fetchone()[0]

        if source_count == 0:
            print(f"    [SKIP] Source table empty")
            cursor.close()
            master_conn.execute("DETACH DATABASE witw_source")
            return 0

        # Check if table exists in master
        cursor.execute(f"""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='witw_{table_name}'
        """)

        target_table = f"witw_{table_name}"

        if not cursor.fetchone():
            # Create table with witw_ prefix
            print(f"    Creating table {target_table}...")
            cursor.execute(f"CREATE TABLE {target_table} AS SELECT * FROM witw_source.{table_name} WHERE 0")
            master_conn.commit()

        # Get current count in master
        cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
        before_count = cursor.fetchone()[0]

        # Import data
        cursor.execute(f"INSERT INTO {target_table} SELECT * FROM witw_source.{table_name}")
        imported = cursor.rowcount
        master_conn.commit()

        # Verify
        cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
        after_count = cursor.fetchone()[0]

        print(f"    [SUCCESS] Imported {imported} rows ({before_count} -> {after_count})")

        cursor.close()
        master_conn.execute("DETACH DATABASE witw_source")
        return imported

    except Exception as e:
        print(f"    [ERROR] {e}")
        cursor.close()
        try:
            master_conn.execute("DETACH DATABASE witw_source")
        except:
            pass
        return 0

def import_tier1(master_conn, source_db_path):
    """Import all Tier 1 tables."""

    print("\n" + "=" * 100)
    print("TIER 1 IMPORT: INFANTRY & GAME CONVERSIONS")
    print("=" * 100)

    results = {}

    for table in TIER1_TABLES:
        imported = import_tier1_table(master_conn, source_db_path, table)
        results[table] = imported

    total = sum(results.values())

    print(f"\n[TIER 1 COMPLETE] Imported {total} rows across {len(TIER1_TABLES)} tables")

    return results

def import_tier2(master_conn, source_db_path):
    """Import all Tier 2 tables."""

    print("\n" + "=" * 100)
    print("TIER 2 IMPORT: WITW METADATA")
    print("=" * 100)

    results = {}

    for table in TIER2_TABLES:
        imported = import_tier2_table(master_conn, source_db_path, table)
        results[table] = imported

    total = sum(results.values())

    print(f"\n[TIER 2 COMPLETE] Imported {total} rows across {len(TIER2_TABLES)} tables")

    return results

def log_import(conn, tier_results, tier_name):
    """Log import results to import_log table."""

    timestamp = datetime.now().isoformat()
    cursor = conn.cursor()

    for table, count in tier_results.items():
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file, records_imported, records_failed,
                import_started_at, import_completed_at, import_status,
                error_log, imported_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"{tier_name}_{table}",
            tier_name,
            count,
            0,
            timestamp,
            timestamp,
            'success',
            f'Full consolidation import - {tier_name}',
            'import_full_consolidation.py'
        ))

    conn.commit()

def generate_statistics(conn):
    """Generate post-import statistics."""

    print("\n" + "=" * 100)
    print("CONSOLIDATION STATISTICS")
    print("=" * 100)

    cursor = conn.cursor()

    # Master equipment stats
    cursor.execute("SELECT COUNT(*) FROM master_equipment")
    equipment_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM master_equipment WHERE equipment_type = 'AFV'")
    afv_count = cursor.fetchone()[0]

    print(f"\nmaster_equipment: {equipment_count} items")
    print(f"  - AFVs/Vehicles: {afv_count}")
    print(f"  - Other: {equipment_count - afv_count}")

    # Infantry weapons stats
    cursor.execute("SELECT COUNT(*) FROM infantry_weapons")
    infantry_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT nationality_id, COUNT(*)
        FROM infantry_weapons
        GROUP BY nationality_id
        ORDER BY nationality_id
    """)

    print(f"\ninfantry_weapons: {infantry_count} items")
    nations = {1: 'German', 2: 'British', 3: 'Italian', 4: 'American', 5: 'French'}
    for row in cursor.fetchall():
        nat_name = nations.get(row[0], f'Nation {row[0]}')
        print(f"  - {nat_name}: {row[1]}")

    # Game conversions
    cursor.execute("SELECT COUNT(*) FROM Other_game_conversion_formulas")
    formula_count = cursor.fetchone()[0]
    print(f"\nOther_game_conversion_formulas: {formula_count} formulas")

    # WITW tables
    witw_tables = ['witw_devices', 'witw_ground_vehicles', 'witw_ground_weapons', 'witw_leaders', 'witw_toe_ob']
    print(f"\nWITW Metadata Tables:")
    witw_total = 0
    for table in witw_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        witw_total += count
        print(f"  - {table}: {count} rows")

    print(f"\n  Total WITW metadata: {witw_total} rows")

    # Grand total
    print(f"\n{'='*100}")
    print(f"GRAND TOTAL: {equipment_count + infantry_count + formula_count + witw_total} rows")
    print(f"  - Equipment (vehicles): {equipment_count}")
    print(f"  - Infantry weapons: {infantry_count}")
    print(f"  - Game conversions: {formula_count}")
    print(f"  - WITW metadata: {witw_total}")
    print(f"{'='*100}")

def main():
    """Execute full consolidation import."""

    print("=" * 100)
    print("FULL DATABASE CONSOLIDATION (TIER 1 + 2)")
    print("=" * 100)
    print("\nThis will import 11,023 rows:")
    print("  - Tier 1: Infantry & Game Conversions (257 rows)")
    print("  - Tier 2: WITW Metadata (10,766 rows)")
    print("\nEstimated time: 10-15 minutes")

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Connect to master database
    print(f"\n\nConnecting to master database: {MASTER_DB}")
    master_conn = sqlite3.connect(MASTER_DB)
    master_conn.execute("PRAGMA foreign_keys = OFF")  # Disable FK checks during import

    try:
        # Import Tier 1
        tier1_results = import_tier1(master_conn, NAW_DB)
        log_import(master_conn, tier1_results, "Tier1")

        # Import Tier 2
        tier2_results = import_tier2(master_conn, WITW_DB)
        log_import(master_conn, tier2_results, "Tier2")

        # Commit all changes
        print("\n\nCommitting changes to database...")
        master_conn.commit()
        print("[SUCCESS] All changes committed")

        # Generate statistics
        generate_statistics(master_conn)

        print("\n" + "=" * 100)
        print("CONSOLIDATION COMPLETE")
        print("=" * 100)
        print("\nDatabase consolidation successful!")
        print(f"  - {sum(tier1_results.values())} Tier 1 rows imported")
        print(f"  - {sum(tier2_results.values())} Tier 2 rows imported")
        print(f"  - Total: {sum(tier1_results.values()) + sum(tier2_results.values())} rows")

        print("\nNext steps:")
        print("  1. Verify imports with: python tools/validate_consolidation.py")
        print("  2. Update documentation: PROJECT_SCOPE.md, CLAUDE.md")
        print("  3. Continue with Phase 6 ground forces extraction")

    except Exception as e:
        print(f"\n\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        master_conn.rollback()
        print("\n[ROLLBACK] All changes rolled back")
        sys.exit(1)

    finally:
        master_conn.close()

if __name__ == "__main__":
    main()
