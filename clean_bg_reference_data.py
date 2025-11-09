#!/usr/bin/env python3
"""
Data Cleaning Script for bg_reference_vehicles

Fixes:
1. Remove quote marks (") from off_road_inches and road_inches fields
2. Remove spaces in weapon caliber designations (e.g., "75mmL 24" -> "75mmL24")
3. Standardize weapon name formatting to match bg_reference_guns

Usage:
    python clean_bg_reference_data.py --dry-run    # Preview changes
    python clean_bg_reference_data.py              # Apply changes
"""

import sqlite3
import re
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "database" / "master_database.db"


def clean_movement_inches(conn, dry_run=False):
    """Remove quote marks from movement inch fields."""
    cur = conn.cursor()

    # Find records with quotes
    cur.execute('''
        SELECT id, name, off_road_inches, road_inches
        FROM bg_reference_vehicles
        WHERE off_road_inches LIKE '%"%' OR road_inches LIKE '%"%'
    ''')

    rows = cur.fetchall()
    print(f"\n{'='*80}")
    print("CLEANING MOVEMENT INCH FIELDS (Remove Quotes)")
    print(f"{'='*80}\n")
    print(f"Found {len(rows)} records with quote marks\n")

    if not rows:
        print("No changes needed.")
        return

    changes = []
    for row in rows:
        record_id, name, off_road, road = row

        # Remove quotes
        off_road_clean = off_road.replace('"', '') if off_road else off_road
        road_clean = road.replace('"', '') if road else road

        if off_road != off_road_clean or road != road_clean:
            changes.append({
                'id': record_id,
                'name': name,
                'old_off_road': off_road,
                'new_off_road': off_road_clean,
                'old_road': road,
                'new_road': road_clean
            })

    # Display changes
    print(f"ID  | Name                          | Off-Road         | Road")
    print(f"{'-'*80}")
    for change in changes:
        print(f"{change['id']:3} | {change['name'][:30]:30} | "
              f"{change['old_off_road']:7} -> {change['new_off_road']:7} | "
              f"{change['old_road']:7} -> {change['new_road']:7}")

    # Apply changes
    if not dry_run:
        for change in changes:
            cur.execute('''
                UPDATE bg_reference_vehicles
                SET off_road_inches = ?, road_inches = ?
                WHERE id = ?
            ''', (change['new_off_road'], change['new_road'], change['id']))

        conn.commit()
        print(f"\nOK - Updated {len(changes)} records")
    else:
        print(f"\n[DRY-RUN] Would update {len(changes)} records")


def clean_weapon_calibers(conn, dry_run=False):
    """Remove spaces in weapon caliber designations."""
    cur = conn.cursor()

    # Find records with spaces in calibers (e.g., "75mmL 24")
    cur.execute('''
        SELECT id, name, weapon_1, weapon_2, weapon_3, weapon_4
        FROM bg_reference_vehicles
        WHERE weapon_1 LIKE '%mmL %' OR weapon_2 LIKE '%mmL %'
           OR weapon_3 LIKE '%mmL %' OR weapon_4 LIKE '%mmL %'
    ''')

    rows = cur.fetchall()
    print(f"\n{'='*80}")
    print("CLEANING WEAPON CALIBER SPACES (e.g., '75mmL 24' -> '75mmL24')")
    print(f"{'='*80}\n")
    print(f"Found {len(rows)} records with spaces in weapon calibers\n")

    if not rows:
        print("No changes needed.")
        return

    changes = []
    for row in rows:
        record_id, name, w1, w2, w3, w4 = row

        # Clean weapon fields
        def clean_caliber(weapon):
            if not weapon:
                return weapon
            # Remove space between "mmL" and number (e.g., "75mmL 24" -> "75mmL24")
            return re.sub(r'(\d+mmL)\s+(\d+)', r'\1\2', weapon)

        w1_clean = clean_caliber(w1)
        w2_clean = clean_caliber(w2)
        w3_clean = clean_caliber(w3)
        w4_clean = clean_caliber(w4)

        if w1 != w1_clean or w2 != w2_clean or w3 != w3_clean or w4 != w4_clean:
            changes.append({
                'id': record_id,
                'name': name,
                'weapons': [
                    (w1, w1_clean, 'weapon_1'),
                    (w2, w2_clean, 'weapon_2'),
                    (w3, w3_clean, 'weapon_3'),
                    (w4, w4_clean, 'weapon_4')
                ]
            })

    # Display changes
    print(f"ID  | Name                          | Field    | Old -> New")
    print(f"{'-'*80}")
    for change in changes:
        for old, new, field in change['weapons']:
            if old != new:
                print(f"{change['id']:3} | {change['name'][:30]:30} | {field:8} | "
                      f"{repr(old)} -> {repr(new)}")

    # Apply changes
    if not dry_run:
        for change in changes:
            updates = {}
            for old, new, field in change['weapons']:
                if old != new:
                    updates[field] = new

            if updates:
                set_clause = ', '.join(f"{field} = ?" for field in updates.keys())
                values = list(updates.values()) + [change['id']]

                cur.execute(f'''
                    UPDATE bg_reference_vehicles
                    SET {set_clause}
                    WHERE id = ?
                ''', values)

        conn.commit()
        print(f"\nOK - Updated {len(changes)} records")
    else:
        print(f"\n[DRY-RUN] Would update {len(changes)} records")


def verify_weapon_linkage(conn):
    """Verify weapon names match bg_reference_guns table."""
    cur = conn.cursor()

    print(f"\n{'='*80}")
    print("WEAPON LINKAGE VERIFICATION")
    print(f"{'='*80}\n")

    # Get all unique weapon names from bg_reference_vehicles
    cur.execute('''
        SELECT DISTINCT weapon_1 FROM bg_reference_vehicles WHERE weapon_1 IS NOT NULL
        UNION
        SELECT DISTINCT weapon_2 FROM bg_reference_vehicles WHERE weapon_2 IS NOT NULL
        UNION
        SELECT DISTINCT weapon_3 FROM bg_reference_vehicles WHERE weapon_3 IS NOT NULL
        UNION
        SELECT DISTINCT weapon_4 FROM bg_reference_vehicles WHERE weapon_4 IS NOT NULL
        ORDER BY 1
    ''')

    vehicle_weapons = [row[0] for row in cur.fetchall()]

    # Get all gun names from bg_reference_guns
    cur.execute('SELECT name FROM bg_reference_guns')
    reference_guns = set(row[0] for row in cur.fetchall())

    # Find weapons that don't match
    unmatched = []
    for weapon in vehicle_weapons:
        # Skip non-gun weapons
        if any(skip in weapon.upper() for skip in ['MG', 'MACHINE GUN', 'MORTAR', 'FLAMETHROWER']):
            continue

        if weapon not in reference_guns:
            unmatched.append(weapon)

    print(f"Total unique weapons in vehicles: {len(vehicle_weapons)}")
    print(f"Total guns in reference: {len(reference_guns)}")
    print(f"Unmatched weapons (need gun data): {len(unmatched)}\n")

    if unmatched:
        print("Weapons without matching gun data:")
        for weapon in sorted(unmatched):
            print(f"  - {weapon}")
    else:
        print("OK - All weapons have matching gun data!")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean data quality issues in bg_reference_vehicles"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database"
    )

    args = parser.parse_args()

    conn = sqlite3.connect(DATABASE_PATH)

    try:
        # Run cleaning operations
        clean_movement_inches(conn, dry_run=args.dry_run)
        clean_weapon_calibers(conn, dry_run=args.dry_run)
        verify_weapon_linkage(conn)

        if not args.dry_run:
            print(f"\n{'='*80}")
            print("DATA CLEANING COMPLETE")
            print(f"{'='*80}\n")
        else:
            print(f"\n{'='*80}")
            print("[DRY-RUN] No changes applied - run without --dry-run to apply")
            print(f"{'='*80}\n")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
