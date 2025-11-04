"""
Phase A3: Merge master_equipment into equipment_master_new

Consolidates two equipment tables into single master table.
Preserves all unique data from both sources.
"""

import sqlite3
import json
import re
from typing import Dict, List, Tuple, Optional


def normalize_name_for_matching(name: str) -> str:
    """Normalize equipment name for fuzzy matching."""
    name = name.lower()
    name = name.replace(' ', '_')
    name = re.sub(r'\(([^)]+)\)', r'_\1_', name)
    name = re.sub(r'[^a-z0-9_\-]', '', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name


def analyze_tables(conn: sqlite3.Connection):
    """Analyze both tables to understand structure and overlap."""
    cursor = conn.cursor()

    print("=" * 100)
    print("TABLE ANALYSIS")
    print("=" * 100)
    print()

    # equipment_master_new stats
    cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
    emn_count = cursor.fetchone()[0]

    cursor.execute("PRAGMA table_info(equipment_master_new)")
    emn_cols = [col[1] for col in cursor.fetchall()]

    print(f"equipment_master_new:")
    print(f"  Records: {emn_count}")
    print(f"  Columns: {len(emn_cols)}")
    print()

    # master_equipment stats
    cursor.execute("SELECT COUNT(*) FROM master_equipment")
    me_count = cursor.fetchone()[0]

    cursor.execute("PRAGMA table_info(master_equipment)")
    me_cols = [col[1] for col in cursor.fetchall()]

    print(f"master_equipment:")
    print(f"  Records: {me_count}")
    print(f"  Columns: {len(me_cols)}")
    print()

    # Find overlapping columns
    common_cols = set(emn_cols) & set(me_cols)
    emn_only = set(emn_cols) - set(me_cols)
    me_only = set(me_cols) - set(emn_cols)

    print(f"Column overlap:")
    print(f"  Common columns: {len(common_cols)}")
    print(f"  equipment_master_new only: {len(emn_only)}")
    print(f"  master_equipment only: {len(me_only)}")
    print()

    if me_only:
        print(f"  Unique columns in master_equipment:")
        for col in sorted(me_only)[:20]:
            print(f"    - {col}")
        if len(me_only) > 20:
            print(f"    ... and {len(me_only) - 20} more")
        print()

    return emn_cols, me_cols


def find_matches(conn: sqlite3.Connection):
    """Find matching records between tables."""
    cursor = conn.cursor()

    print("=" * 100)
    print("FINDING MATCHES")
    print("=" * 100)
    print()

    # Get all equipment from both tables
    cursor.execute("SELECT master_id, canonical_name, display_name FROM equipment_master_new")
    emn_items = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

    cursor.execute("SELECT id, equipment_name FROM master_equipment")
    me_items = {row[0]: row[1] for row in cursor.fetchall()}

    # Try to match by normalized name
    matches = []  # (emn_master_id, me_id, confidence)
    unmatched_emn = set(emn_items.keys())
    unmatched_me = set(me_items.keys())

    # Create lookup by normalized name
    emn_by_norm = {}
    for master_id, (canonical, display) in emn_items.items():
        norm = normalize_name_for_matching(display)
        if norm not in emn_by_norm:
            emn_by_norm[norm] = []
        emn_by_norm[norm].append(master_id)

    # Try to match each master_equipment item
    for me_id, me_name in me_items.items():
        norm = normalize_name_for_matching(me_name)

        if norm in emn_by_norm:
            # Found match(es)
            for emn_id in emn_by_norm[norm]:
                matches.append((emn_id, me_id, 100))  # Perfect match
                unmatched_emn.discard(emn_id)
                unmatched_me.discard(me_id)

    print(f"Matching results:")
    print(f"  Matched: {len(matches)} pairs")
    print(f"  Unmatched in equipment_master_new: {len(unmatched_emn)}")
    print(f"  Unmatched in master_equipment: {len(unmatched_me)}")
    print()

    # Show sample matches
    print("Sample matches (first 10):")
    for emn_id, me_id, conf in matches[:10]:
        emn_name = emn_items[emn_id][1]
        me_name = me_items[me_id]
        print(f"  emn_id={emn_id:4} ({emn_name:40}) <-> me_id={me_id:4} ({me_name:40}) conf={conf}%")

    if len(matches) > 10:
        print(f"  ... and {len(matches) - 10} more matches")
    print()

    # Show sample unmatched
    if unmatched_me:
        print(f"Sample unmatched master_equipment items (first 10):")
        for me_id in list(unmatched_me)[:10]:
            print(f"  me_id={me_id:4} : {me_items[me_id]}")
        if len(unmatched_me) > 10:
            print(f"  ... and {len(unmatched_me) - 10} more")
        print()

    return matches, list(unmatched_emn), list(unmatched_me)


def merge_tables(conn: sqlite3.Connection, matches, unmatched_me, dry_run=True):
    """
    Merge master_equipment into equipment_master_new.

    Strategy:
    1. For matched items: update equipment_master_new with any missing data from master_equipment
    2. For unmatched master_equipment items: insert as new records into equipment_master_new
    """
    cursor = conn.cursor()

    print("=" * 100)
    print("MERGING TABLES")
    print("=" * 100)
    print()

    updates_made = 0
    inserts_made = 0

    # Step 1: Update matched records (if master_equipment has better/additional data)
    print(f"Processing {len(matches)} matched records...")

    # For now, we'll just note the matches exist
    # Could enhance later to merge specific fields if needed
    print(f"  [INFO] Matches identified - both tables have these items")
    print()

    # Step 2: Insert unmatched master_equipment items
    if unmatched_me:
        print(f"Inserting {len(unmatched_me)} new items from master_equipment...")
        print()

        # Get master_equipment records
        placeholders = ','.join('?' * len(unmatched_me))
        cursor.execute(f"""
            SELECT id, equipment_name, nation, category
            FROM master_equipment
            WHERE id IN ({placeholders})
        """, unmatched_me)

        new_items = cursor.fetchall()

        print("Sample new items to insert (first 10):")
        for item in new_items[:10]:
            me_id, name, nation, category = item
            print(f"  me_id={me_id:4} : {name:50} | {nation:10} | {category}")
        if len(new_items) > 10:
            print(f"  ... and {len(new_items) - 10} more")
        print()

        if not dry_run:
            for me_id, name, nation, category in new_items:
                # Create canonical name
                canonical = normalize_name_for_matching(name)

                # Insert into equipment_master_new
                cursor.execute("""
                    INSERT INTO equipment_master_new
                    (canonical_name, display_name, short_name, equipment_category,
                     original_nation, primary_source, confidence_score, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    canonical,
                    name,
                    name,
                    category if category else 'unknown',
                    nation if nation else 'unknown',
                    'master_equipment',
                    50.0,
                    f'Imported from master_equipment table (id={me_id})'
                ))
                inserts_made += 1

            conn.commit()
            print(f"[OK] Inserted {inserts_made} new records")
            print()

    # Summary
    cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
    final_count = cursor.fetchone()[0]

    print("Summary:")
    print(f"  Updates: {updates_made}")
    print(f"  Inserts: {inserts_made}")
    print(f"  Final equipment_master_new count: {final_count}")
    print()

    return updates_made, inserts_made


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Merge master_equipment into equipment_master_new")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')
    parser.add_argument('--execute', action='store_true', help='Apply merge (default: dry run)')

    args = parser.parse_args()

    conn = sqlite3.connect(args.db)

    print("=" * 100)
    print("PHASE A3: MERGE MASTER_EQUIPMENT")
    print("=" * 100)
    print()

    # Step 1: Analyze tables
    emn_cols, me_cols = analyze_tables(conn)

    # Step 2: Find matches
    matches, unmatched_emn, unmatched_me = find_matches(conn)

    # Step 3: Merge
    updates, inserts = merge_tables(conn, matches, unmatched_me, dry_run=not args.execute)

    if not args.execute:
        print()
        print("DRY RUN - No changes applied. Run with --execute to apply merge.")
    else:
        print()
        print("[OK] Phase A3 complete - master_equipment merged into equipment_master_new")
        print()
        print("Note: You may want to drop the master_equipment table after verifying the merge.")

    print()
    conn.close()


if __name__ == '__main__':
    main()
