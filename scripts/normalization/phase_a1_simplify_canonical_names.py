"""
Phase A1: Simplify Canonical Names in equipment_master_new

Converts verbose canonical names (eq_FRA_75MM_M1897_75mm_m1897) to simple format (75mm_m1897).
Each variant gets unique name based on display_name.

Strategy:
- Use display_name as base
- Convert to lowercase
- Replace spaces with underscores
- Remove special characters (keep alphanumeric, underscore, hyphen)
- Ensure uniqueness (append _v2, _v3 if collision)
"""

import sqlite3
import re
from typing import Dict, List, Tuple


def normalize_name(display_name: str) -> str:
    """
    Convert display name to canonical name format.

    Examples:
        "75mm M1897" -> "75mm_m1897"
        "M3 Stuart" -> "m3_stuart"
        "Stuart I (M3 Light)" -> "stuart_i_m3_light"
        "QF 25-pounder" -> "qf_25_pounder"
    """
    # Convert to lowercase
    name = display_name.lower()

    # Replace spaces with underscores
    name = name.replace(' ', '_')

    # Remove parentheses content and replace with underscores
    name = re.sub(r'\(([^)]+)\)', r'_\1_', name)

    # Remove special characters except alphanumeric, underscore, hyphen
    name = re.sub(r'[^a-z0-9_\-]', '', name)

    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)

    # Remove leading/trailing underscores
    name = name.strip('_')

    return name


def check_collisions(conn: sqlite3.Connection) -> Dict[str, List[Tuple[int, str, str]]]:
    """
    Check for canonical name collisions after normalization.

    Returns dict of {proposed_canonical_name: [(master_id, old_canonical, display_name), ...]}
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT master_id, canonical_name, display_name
        FROM equipment_master_new
        ORDER BY master_id
    """)

    # Build mapping of proposed names to records
    name_map: Dict[str, List[Tuple[int, str, str]]] = {}

    for master_id, old_canonical, display_name in cursor.fetchall():
        proposed = normalize_name(display_name)
        if proposed not in name_map:
            name_map[proposed] = []
        name_map[proposed].append((master_id, old_canonical, display_name))

    # Filter to only collisions (more than 1 record with same proposed name)
    collisions = {k: v for k, v in name_map.items() if len(v) > 1}

    return collisions


def resolve_collisions(collisions: Dict[str, List[Tuple[int, str, str]]]) -> Dict[int, str]:
    """
    Resolve canonical name collisions by appending suffixes.

    Returns dict of {master_id: final_canonical_name}
    """
    resolution = {}

    for base_name, records in collisions.items():
        # First record keeps base name
        resolution[records[0][0]] = base_name

        # Subsequent records get _v2, _v3, etc.
        for i, (master_id, old_canonical, display_name) in enumerate(records[1:], start=2):
            resolution[master_id] = f"{base_name}_v{i}"
            print(f"  COLLISION: '{display_name}' -> {base_name}_v{i} (master_id={master_id})")

    return resolution


def simplify_canonical_names(db_path: str, dry_run: bool = True):
    """
    Simplify all canonical names in equipment_master_new.

    Args:
        db_path: Path to SQLite database
        dry_run: If True, show changes but don't commit
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("PHASE A1: SIMPLIFY CANONICAL NAMES")
    print("=" * 80)
    print()

    # Get current record count
    cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
    total_records = cursor.fetchone()[0]
    print(f"Total records: {total_records}")
    print()

    # Check for collisions
    print("Checking for canonical name collisions...")
    collisions = check_collisions(conn)

    if collisions:
        print(f"Found {len(collisions)} collision groups affecting {sum(len(v) for v in collisions.values())} records:")
        print()
        for base_name, records in sorted(collisions.items()):
            print(f"  '{base_name}' -> {len(records)} records:")
            for master_id, old_canonical, display_name in records:
                print(f"    - master_id={master_id}: {display_name}")
        print()

        # Resolve collisions
        print("Resolving collisions...")
        collision_resolutions = resolve_collisions(collisions)
        print()
    else:
        print("No collisions detected.")
        collision_resolutions = {}
        print()

    # Generate all new canonical names
    cursor.execute("SELECT master_id, canonical_name, display_name FROM equipment_master_new ORDER BY master_id")
    updates = []

    for master_id, old_canonical, display_name in cursor.fetchall():
        if master_id in collision_resolutions:
            # Use collision-resolved name
            new_canonical = collision_resolutions[master_id]
        else:
            # Use normalized display name
            new_canonical = normalize_name(display_name)

        if new_canonical != old_canonical:
            updates.append((new_canonical, master_id, old_canonical, display_name))

    print(f"Changes to apply: {len(updates)} of {total_records} records")
    print()

    # Show sample changes
    print("Sample changes (first 20):")
    print("-" * 80)
    for new_canonical, master_id, old_canonical, display_name in updates[:20]:
        print(f"  {master_id:4}: {display_name:35} ")
        print(f"        OLD: {old_canonical}")
        print(f"        NEW: {new_canonical}")
        print()

    if len(updates) > 20:
        print(f"  ... and {len(updates) - 20} more changes")
        print()

    # Apply updates
    if not dry_run:
        print("Applying updates...")
        cursor.executemany(
            "UPDATE equipment_master_new SET canonical_name = ? WHERE master_id = ?",
            [(new_canonical, master_id) for new_canonical, master_id, _, _ in updates]
        )
        conn.commit()
        print(f"[OK] Updated {len(updates)} records")
        print()

        # Verify no duplicates
        cursor.execute("""
            SELECT canonical_name, COUNT(*) as count
            FROM equipment_master_new
            GROUP BY canonical_name
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()

        if duplicates:
            print(f"[WARNING] {len(duplicates)} duplicate canonical names found after update:")
            for name, count in duplicates:
                print(f"  - {name}: {count} records")
        else:
            print("[OK] No duplicate canonical names - all unique")
        print()
    else:
        print("DRY RUN - No changes applied. Run with --execute to apply changes.")
        print()

    conn.close()

    return len(updates)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simplify canonical names in equipment_master_new")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')
    parser.add_argument('--execute', action='store_true', help='Apply changes (default: dry run)')

    args = parser.parse_args()

    simplify_canonical_names(args.db, dry_run=not args.execute)


if __name__ == '__main__':
    main()
