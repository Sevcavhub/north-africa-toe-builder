#!/usr/bin/env python3
"""
Phase 9B Step 3: Database Schema Enhancement
Adds provenance tracking fields and creates new tables for defences and fire support.
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"


def enhance_schema():
    """Enhance database schema for Phase 9B Step 3 extraction work."""

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("Phase 9B Step 3: Database Schema Enhancement")
    print("=" * 60)
    print()

    # Track changes
    changes_made = []

    try:
        # ================================================================
        # PART 1: Extend bg_reference_vehicles table
        # ================================================================
        print("Part 1: Extending bg_reference_vehicles table...")

        vehicle_columns = [
            ("source_battle", "TEXT", "Battle/engagement context (e.g., 'Kursk', 'Normandy')"),
            ("source_date", "TEXT", "Battle date (e.g., '1943-07', '1944-06')"),
            ("unit_experience", "TEXT", "Experience level (Regular/Veteran/Inexperienced/Elite)"),
            ("source_document", "TEXT", "Source document name"),
            ("extraction_notes", "TEXT", "Parser warnings, variant details, etc.")
        ]

        for col_name, col_type, description in vehicle_columns:
            try:
                cursor.execute(f"ALTER TABLE bg_reference_vehicles ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column: {col_name} - {description}")
                changes_made.append(f"bg_reference_vehicles.{col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  [SKIP] Column already exists: {col_name}")
                else:
                    raise

        print()

        # ================================================================
        # PART 2: Extend bg_reference_guns table
        # ================================================================
        print("Part 2: Extending bg_reference_guns table...")

        gun_columns = [
            ("source_battle", "TEXT", "Battle/engagement context"),
            ("source_date", "TEXT", "Battle date"),
            ("unit_experience", "TEXT", "Experience level"),
            ("source_document", "TEXT", "Source document name"),
            ("extraction_notes", "TEXT", "Parser warnings, variant details, etc.")
        ]

        for col_name, col_type, description in gun_columns:
            try:
                cursor.execute(f"ALTER TABLE bg_reference_guns ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column: {col_name} - {description}")
                changes_made.append(f"bg_reference_guns.{col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  [SKIP] Column already exists: {col_name}")
                else:
                    raise

        print()

        # ================================================================
        # PART 3: Create bg_reference_defences table
        # ================================================================
        print("Part 3: Creating bg_reference_defences table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bg_reference_defences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                defence_type TEXT,  -- 'fortification', 'obstacle', 'minefield', 'trench', 'building', etc.
                class_rating TEXT,  -- For pillboxes (Class 1, 2, 3, 4, 5)
                description TEXT,
                points_cost INTEGER,
                battle_rating INTEGER,
                special_rules TEXT,
                source_battle TEXT,
                source_date TEXT,
                source_document TEXT,
                source_page TEXT,
                extraction_confidence TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, source_document, class_rating)
            )
        """)

        print("  [OK] Created bg_reference_defences table")
        print("    - Tracks defensive structures (fortifications, obstacles, minefields, pillboxes)")
        print("    - Includes class ratings for pillboxes (Class 1-5)")
        print("    - Estimated 200+ entries from 7 documents")
        changes_made.append("bg_reference_defences table")
        print()

        # ================================================================
        # PART 4: Create bg_reference_fire_support table
        # ================================================================
        print("Part 4: Creating bg_reference_fire_support table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bg_reference_fire_support (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                support_type TEXT,  -- 'off-table-artillery', 'air-strike', 'timed-barrage', 'counter-battery', etc.
                priority_level TEXT,  -- '1st (3+)', '2nd (4+)', '3rd (5+)', or NULL for timed missions
                fire_mission_type TEXT,  -- 'regimental', 'divisional', 'corps', 'army', etc.
                battery_composition TEXT,  -- What guns are firing (e.g., '4x 25-pdr', '2x 5.5" guns')
                description TEXT,
                points_cost INTEGER,
                battle_rating INTEGER,
                special_rules TEXT,
                source_battle TEXT,
                source_date TEXT,
                source_document TEXT,
                source_page TEXT,
                extraction_confidence TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, source_document, priority_level)
            )
        """)

        print("  [OK] Created bg_reference_fire_support table")
        print("    - Tracks off-board artillery and air support")
        print("    - Includes priority levels (1st/2nd/3rd target priority)")
        print("    - Includes timed barrages, counter-battery, air strikes")
        print("    - Estimated 150+ entries from 7 documents")
        changes_made.append("bg_reference_fire_support table")
        print()

        # ================================================================
        # PART 5: Create bg_extraction_log table
        # ================================================================
        print("Part 5: Creating bg_extraction_log tracking table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bg_extraction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_name TEXT NOT NULL,
                source_battle TEXT,
                source_date TEXT,
                total_entries INTEGER,
                vehicles_extracted INTEGER,
                guns_extracted INTEGER,
                infantry_extracted INTEGER,
                defences_extracted INTEGER,
                fire_support_extracted INTEGER,
                status TEXT,
                extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                UNIQUE(document_name)
            )
        """)

        print("  [OK] Created bg_extraction_log table")
        print("    - Tracks extraction progress for 7 documents")
        print("    - Records counts by category (vehicles/guns/defences/fire support)")
        print("    - Maintains extraction status and provenance")
        changes_made.append("bg_extraction_log table")
        print()

        # ================================================================
        # COMMIT CHANGES
        # ================================================================
        conn.commit()

        print("=" * 60)
        print("[SUCCESS] Schema enhancement COMPLETE!")
        print()
        print(f"Total changes made: {len(changes_made)}")
        for i, change in enumerate(changes_made, 1):
            print(f"  {i}. {change}")
        print()

        # ================================================================
        # VERIFICATION: Check table counts
        # ================================================================
        print("=" * 60)
        print("Verification: Current database state")
        print()

        cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
        vehicle_count = cursor.fetchone()[0]
        print(f"  bg_reference_vehicles: {vehicle_count} entries")

        cursor.execute("SELECT COUNT(*) FROM bg_reference_guns")
        gun_count = cursor.fetchone()[0]
        print(f"  bg_reference_guns: {gun_count} entries")

        cursor.execute("SELECT COUNT(*) FROM bg_reference_defences")
        defence_count = cursor.fetchone()[0]
        print(f"  bg_reference_defences: {defence_count} entries (NEW)")

        cursor.execute("SELECT COUNT(*) FROM bg_reference_fire_support")
        fire_support_count = cursor.fetchone()[0]
        print(f"  bg_reference_fire_support: {fire_support_count} entries (NEW)")

        cursor.execute("SELECT COUNT(*) FROM bg_extraction_log")
        log_count = cursor.fetchone()[0]
        print(f"  bg_extraction_log: {log_count} entries (NEW)")
        print()

        print("=" * 60)
        print("[SUCCESS] Database ready for Phase 9B Step 3 extraction work!")
        print()

        return True

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


def show_schema():
    """Display the enhanced schema for verification."""

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print()
    print("=" * 60)
    print("Enhanced Schema Verification")
    print("=" * 60)
    print()

    tables = [
        "bg_reference_vehicles",
        "bg_reference_guns",
        "bg_reference_defences",
        "bg_reference_fire_support",
        "bg_extraction_log"
    ]

    for table in tables:
        print(f"\n{table}:")
        print("-" * 60)
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            col_id, name, type_, not_null, default, pk = col
            print(f"  {name:<30} {type_:<15} {'NOT NULL' if not_null else ''}")

    conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 3: Database Schema Enhancement"
    )
    parser.add_argument(
        "--show-schema",
        action="store_true",
        help="Show enhanced schema after changes"
    )

    args = parser.parse_args()

    # Enhance schema
    success = enhance_schema()

    # Show schema if requested
    if args.show_schema and success:
        show_schema()

    sys.exit(0 if success else 1)
