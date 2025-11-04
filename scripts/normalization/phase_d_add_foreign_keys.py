"""
Phase D: Add Foreign Keys & Integration

Adds master_id foreign keys to equipment and bg_reference_vehicles tables.
Populates links by matching names to equipment_master_new.
Creates database views for common queries.
"""

import sqlite3
import re
from typing import Dict, Tuple


def normalize_name(name: str) -> str:
    """Normalize name for matching."""
    name = name.lower()
    name = name.replace(' ', '_')
    name = re.sub(r'\(([^)]+)\)', r'_\1_', name)
    name = re.sub(r'[^a-z0-9_\-]', '', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name


def add_master_id_columns(conn: sqlite3.Connection, dry_run=True):
    """Add master_id columns to tables."""
    cursor = conn.cursor()

    print("=" * 100)
    print("STEP 1: ADD MASTER_ID COLUMNS")
    print("=" * 100)
    print()

    tables_to_update = ['equipment', 'bg_reference_vehicles', 'bg_reference_guns']

    for table in tables_to_update:
        # Check if column already exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]

        if 'master_id' in columns:
            print(f"  {table}: master_id column already exists")
        else:
            print(f"  {table}: adding master_id column")
            if not dry_run:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN master_id INTEGER")

    if not dry_run:
        conn.commit()
        print()
        print("[OK] Columns added")
    print()


def populate_equipment_links(conn: sqlite3.Connection, dry_run=True):
    """Populate master_id in equipment table."""
    cursor = conn.cursor()

    print("=" * 100)
    print("STEP 2: POPULATE EQUIPMENT TABLE LINKS")
    print("=" * 100)
    print()

    # Get equipment records
    cursor.execute("SELECT canonical_id, name FROM equipment")
    equipment_items = cursor.fetchall()

    # Get masters lookup
    cursor.execute("SELECT master_id, canonical_name, display_name FROM equipment_master_new")
    masters = {}
    for master_id, canonical, display in cursor.fetchall():
        norm = normalize_name(canonical)
        masters[norm] = master_id

    # Match equipment to masters
    matches = []
    unmatched = []

    for canonical_id, name in equipment_items:
        norm = normalize_name(name)
        if norm in masters:
            matches.append((masters[norm], canonical_id))
        else:
            unmatched.append((canonical_id, name))

    print(f"Equipment table ({len(equipment_items)} records):")
    print(f"  Matched: {len(matches)}")
    print(f"  Unmatched: {len(unmatched)}")
    print()

    if unmatched:
        print("Sample unmatched (first 5):")
        for canonical_id, name in unmatched[:5]:
            print(f"  {canonical_id:40} : {name}")
        print()

    if not dry_run and matches:
        for master_id, canonical_id in matches:
            cursor.execute("""
                UPDATE equipment
                SET master_id = ?
                WHERE canonical_id = ?
            """, (master_id, canonical_id))

        conn.commit()
        print(f"[OK] Updated {len(matches)} equipment records with master_id")
        print()

    return len(matches), len(unmatched)


def populate_bg_reference_links(conn: sqlite3.Connection, dry_run=True):
    """Populate master_id in bg_reference_vehicles and bg_reference_guns."""
    cursor = conn.cursor()

    print("=" * 100)
    print("STEP 3: POPULATE BG_REFERENCE TABLE LINKS")
    print("=" * 100)
    print()

    # Get masters lookup
    cursor.execute("SELECT master_id, canonical_name, display_name FROM equipment_master_new")
    masters = {}
    for master_id, canonical, display in cursor.fetchall():
        norm = normalize_name(display)
        masters[norm] = master_id

    # Process bg_reference_vehicles
    cursor.execute("SELECT id, name FROM bg_reference_vehicles")
    bg_vehicles = cursor.fetchall()

    vehicle_matches = []
    vehicle_unmatched = []

    for id_, name in bg_vehicles:
        norm = normalize_name(name)
        if norm in masters:
            vehicle_matches.append((masters[norm], id_))
        else:
            vehicle_unmatched.append((id_, name))

    print(f"bg_reference_vehicles ({len(bg_vehicles)} records):")
    print(f"  Matched: {len(vehicle_matches)}")
    print(f"  Unmatched: {len(vehicle_unmatched)}")
    print()

    if not dry_run and vehicle_matches:
        for master_id, id_ in vehicle_matches:
            cursor.execute("""
                UPDATE bg_reference_vehicles
                SET master_id = ?
                WHERE id = ?
            """, (master_id, id_))

        conn.commit()
        print(f"[OK] Updated {len(vehicle_matches)} bg_reference_vehicles records")
        print()

    # Process bg_reference_guns
    cursor.execute("SELECT id, name FROM bg_reference_guns")
    bg_guns = cursor.fetchall()

    gun_matches = []
    gun_unmatched = []

    for id_, name in bg_guns:
        norm = normalize_name(name)
        if norm in masters:
            gun_matches.append((masters[norm], id_))
        else:
            gun_unmatched.append((id_, name))

    print(f"bg_reference_guns ({len(bg_guns)} records):")
    print(f"  Matched: {len(gun_matches)}")
    print(f"  Unmatched: {len(gun_unmatched)}")
    print()

    if not dry_run and gun_matches:
        for master_id, id_ in gun_matches:
            cursor.execute("""
                UPDATE bg_reference_guns
                SET master_id = ?
                WHERE id = ?
            """, (master_id, id_))

        conn.commit()
        print(f"[OK] Updated {len(gun_matches)} bg_reference_guns records")
        print()

    return (len(vehicle_matches), len(vehicle_unmatched), len(gun_matches), len(gun_unmatched))


def create_views(conn: sqlite3.Connection, dry_run=True):
    """Create convenience views for common queries."""
    cursor = conn.cursor()

    print("=" * 100)
    print("STEP 4: CREATE DATABASE VIEWS")
    print("=" * 100)
    print()

    views = {
        'v_equipment_complete': """
            CREATE VIEW IF NOT EXISTS v_equipment_complete AS
            SELECT
                emn.master_id,
                emn.canonical_name,
                emn.display_name,
                emn.equipment_category,
                emn.original_nation,
                emn.armor_front_mm,
                emn.armor_side_mm,
                emn.armor_rear_mm,
                emn.weight_tonnes,
                emn.crew,
                emn.max_speed_kmh,
                emn.production_start,
                emn.production_end,
                emn.production_quantity,
                eq.canonical_id as witw_canonical_id,
                eq.witw_id,
                COUNT(DISTINCT env.variant_id) as variant_count
            FROM equipment_master_new emn
            LEFT JOIN equipment eq ON emn.master_id = eq.master_id
            LEFT JOIN equipment_name_variants_new env ON emn.master_id = env.master_id
            GROUP BY emn.master_id
        """,

        'v_equipment_by_nation': """
            CREATE VIEW IF NOT EXISTS v_equipment_by_nation AS
            SELECT
                original_nation as nation,
                equipment_category as category,
                COUNT(*) as count,
                GROUP_CONCAT(display_name, ', ') as items
            FROM equipment_master_new
            GROUP BY original_nation, equipment_category
            ORDER BY original_nation, equipment_category
        """,

        'v_name_variants': """
            CREATE VIEW IF NOT EXISTS v_name_variants AS
            SELECT
                emn.master_id,
                emn.canonical_name,
                emn.display_name,
                env.variant_name,
                env.variant_source,
                env.is_official
            FROM equipment_master_new emn
            JOIN equipment_name_variants_new env ON emn.master_id = env.master_id
            ORDER BY emn.master_id, env.variant_name
        """
    }

    print(f"Creating {len(views)} database views:")
    for view_name in views.keys():
        print(f"  - {view_name}")

    if not dry_run:
        for view_name, view_sql in views.items():
            cursor.execute(view_sql)

        conn.commit()
        print()
        print(f"[OK] Created {len(views)} views")
    print()


def verify_integration(conn: sqlite3.Connection):
    """Verify foreign key links are working."""
    cursor = conn.cursor()

    print("=" * 100)
    print("VERIFICATION")
    print("=" * 100)
    print()

    # Check equipment linkage
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN master_id IS NOT NULL THEN 1 ELSE 0 END) as linked,
            SUM(CASE WHEN master_id IS NULL THEN 1 ELSE 0 END) as unlinked
        FROM equipment
    """)
    eq_total, eq_linked, eq_unlinked = cursor.fetchone()
    eq_pct = 100 * eq_linked / eq_total if eq_total > 0 else 0

    print(f"equipment table:")
    print(f"  Total: {eq_total}")
    print(f"  Linked: {eq_linked} ({eq_pct:.1f}%)")
    print(f"  Unlinked: {eq_unlinked}")
    print()

    # Check bg_reference_vehicles linkage
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN master_id IS NOT NULL THEN 1 ELSE 0 END) as linked,
            SUM(CASE WHEN master_id IS NULL THEN 1 ELSE 0 END) as unlinked
        FROM bg_reference_vehicles
    """)
    bg_total, bg_linked, bg_unlinked = cursor.fetchone()
    bg_pct = 100 * bg_linked / bg_total if bg_total > 0 else 0

    print(f"bg_reference_vehicles table:")
    print(f"  Total: {bg_total}")
    print(f"  Linked: {bg_linked} ({bg_pct:.1f}%)")
    print(f"  Unlinked: {bg_unlinked}")
    print()

    # Check bg_reference_guns linkage
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN master_id IS NOT NULL THEN 1 ELSE 0 END) as linked,
            SUM(CASE WHEN master_id IS NULL THEN 1 ELSE 0 END) as unlinked
        FROM bg_reference_guns
    """)
    gun_total, gun_linked, gun_unlinked = cursor.fetchone()
    gun_pct = 100 * gun_linked / gun_total if gun_total > 0 else 0

    print(f"bg_reference_guns table:")
    print(f"  Total: {gun_total}")
    print(f"  Linked: {gun_linked} ({gun_pct:.1f}%)")
    print(f"  Unlinked: {gun_unlinked}")
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Add foreign keys and integrate tables")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')
    parser.add_argument('--execute', action='store_true', help='Apply changes (default: dry run)')

    args = parser.parse_args()

    conn = sqlite3.connect(args.db)

    print("=" * 100)
    print("PHASE D: INTEGRATION & FOREIGN KEYS")
    print("=" * 100)
    print()

    # Step 1: Add columns
    add_master_id_columns(conn, dry_run=not args.execute)

    # Step 2: Populate equipment links
    populate_equipment_links(conn, dry_run=not args.execute)

    # Step 3: Populate bg_reference links
    populate_bg_reference_links(conn, dry_run=not args.execute)

    # Step 4: Create views
    create_views(conn, dry_run=not args.execute)

    # Verification
    if not args.execute:
        print()
        print("DRY RUN - No changes applied. Run with --execute to apply integration.")
    else:
        verify_integration(conn)
        print()
        print("[OK] Phase D complete - foreign keys added and populated")

    print()
    conn.close()


if __name__ == '__main__':
    main()
