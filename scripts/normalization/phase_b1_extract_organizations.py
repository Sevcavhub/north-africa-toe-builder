"""
Phase B1: Extract Organizational Units from bg_reference_vehicles

Moves platoons, squads, teams, and headquarters to new bg_reference_organizations table.
Cleans bg_reference_vehicles to contain only actual equipment.
"""

import sqlite3


def identify_organizational_units(conn: sqlite3.Connection):
    """
    Identify all organizational unit entries in bg_reference_vehicles.

    Returns list of IDs to move.
    """
    cursor = conn.cursor()

    # Pattern matching for organizational units
    cursor.execute('''
        SELECT id, name, nation, vehicle_type
        FROM bg_reference_vehicles
        WHERE name LIKE '%platoon%'
           OR name LIKE '%company%'
           OR name LIKE '%squad%'
           OR name LIKE '%section%'
           OR name LIKE '%team%'
           OR name LIKE '%headquarters%'
           OR name LIKE '%forward aid post%'
           OR name LIKE '%forward observer%'
           OR name LIKE '%supply column%'
           OR name LIKE '%sniper%'
           OR name LIKE '%command post%'
           OR name LIKE '%battalion%'
           OR name LIKE '%regiment%'
        ORDER BY name
    ''')

    return cursor.fetchall()


def create_organizations_table(conn: sqlite3.Connection):
    """Create bg_reference_organizations table."""
    cursor = conn.cursor()

    # Check if table already exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='bg_reference_organizations'
    """)

    if cursor.fetchone():
        print("[INFO] Table bg_reference_organizations already exists")
        return False

    # Create new table with same structure as bg_reference_vehicles
    cursor.execute("""
        CREATE TABLE bg_reference_organizations AS
        SELECT * FROM bg_reference_vehicles WHERE 1=0
    """)

    return True


def move_organizations(conn: sqlite3.Connection, org_units, dry_run=True):
    """Move organizational units to new table."""
    cursor = conn.cursor()

    if not org_units:
        print("[OK] No organizational units to move")
        return

    print(f"Found {len(org_units)} organizational unit entries to move")
    print()

    # Group by name
    by_name = {}
    for id_, name, nation, vehicle_type in org_units:
        if name not in by_name:
            by_name[name] = []
        by_name[name].append((id_, nation, vehicle_type))

    print(f"Unique organizational unit names: {len(by_name)}")
    print()
    print("Sample organizational units (first 20):")
    for i, (name, entries) in enumerate(sorted(by_name.items())[:20]):
        print(f"  {i+1:2}. {name:50} : {len(entries):3} entries")

    if len(by_name) > 20:
        print(f"  ... and {len(by_name) - 20} more")

    if not dry_run:
        # Create table
        created = create_organizations_table(conn)
        if created:
            print()
            print("[OK] Created bg_reference_organizations table")

        # Move records
        print()
        print("Moving records...")

        org_ids = [id_ for id_, _, _, _ in org_units]
        placeholders = ','.join('?' * len(org_ids))

        # Copy to new table
        cursor.execute(f"""
            INSERT INTO bg_reference_organizations
            SELECT * FROM bg_reference_vehicles
            WHERE id IN ({placeholders})
        """, org_ids)

        moved_count = cursor.rowcount

        # Delete from bg_reference_vehicles
        cursor.execute(f"""
            DELETE FROM bg_reference_vehicles
            WHERE id IN ({placeholders})
        """, org_ids)

        deleted_count = cursor.rowcount

        conn.commit()

        print(f"[OK] Moved {moved_count} records to bg_reference_organizations")
        print(f"[OK] Deleted {deleted_count} records from bg_reference_vehicles")
        print()

        # Verify
        cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
        remaining = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bg_reference_organizations")
        org_count = cursor.fetchone()[0]

        print(f"Verification:")
        print(f"  bg_reference_vehicles:      {remaining} equipment items")
        print(f"  bg_reference_organizations: {org_count} organizational units")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract organizational units from bg_reference_vehicles")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')
    parser.add_argument('--execute', action='store_true', help='Apply changes (default: dry run)')

    args = parser.parse_args()

    conn = sqlite3.connect(args.db)

    print("=" * 100)
    print("PHASE B1: EXTRACT ORGANIZATIONAL UNITS")
    print("=" * 100)
    print()

    # Step 1: Identify organizational units
    org_units = identify_organizational_units(conn)

    # Step 2: Move to new table
    move_organizations(conn, org_units, dry_run=not args.execute)

    if not args.execute:
        print()
        print("DRY RUN - No changes applied. Run with --execute to apply changes.")
    else:
        print()
        print("[OK] Phase B1 complete - organizational units extracted")

    print()
    conn.close()


if __name__ == '__main__':
    main()
