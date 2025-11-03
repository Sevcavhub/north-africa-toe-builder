#!/usr/bin/env python3
"""Phase 1: Auto-apply obvious collision resolutions."""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def categorize_collision(items):
    """Determine if collision is auto-resolvable."""

    categories = [item['category'] for item in items]
    names = [item['name'] for item in items]

    # Check for multi-category critical (aircraft + ground)
    unique_cats = set(categories)
    if len(unique_cats) > 1:
        ground_cats = {'tanks', 'anti_tank', 'anti_aircraft', 'field_artillery', 'trucks',
                      'halftracks', 'armored_cars', 'support_vehicles', 'light_tanks',
                      'main_tanks', 'medium_tanks', 'heavy_tanks'}
        air_cats = {'fighters', 'bombers', 'reconnaissance', 'aircraft'}

        has_ground = any(cat in ground_cats for cat in categories)
        has_air = any(cat in air_cats for cat in categories)

        if has_ground and has_air:
            return {
                'auto_resolve': True,
                'strategy': 'null_all_multi_category',
                'reason': 'Aircraft and ground equipment collision'
            }

    # Check for obvious duplicates (2 items, similar names)
    if len(items) == 2:
        name1_lower = names[0].lower().replace('-', '').replace(' ', '').replace('_', '')
        name2_lower = names[1].lower().replace('-', '').replace(' ', '').replace('_', '')

        # Strip common prefixes
        for prefix in ['gbr', 'ger', 'usa', 'ita']:
            name1_lower = name1_lower.replace(prefix, '', 1)
            name2_lower = name2_lower.replace(prefix, '', 1)

        # Check if one name contains the other
        if name1_lower in name2_lower or name2_lower in name1_lower:
            # Retain the fuller name
            retained_idx = 0 if len(names[0]) > len(names[1]) else 1

            return {
                'auto_resolve': True,
                'strategy': 'retain_fuller_name',
                'reason': 'Same item with different naming',
                'retained_item': items[retained_idx]['id']
            }

    return {'auto_resolve': False}

def apply_null_all(cursor, witw_id, items):
    """NULL all witw_ids for a collision."""

    canonical_ids = [item['id'] for item in items]

    # Audit logging
    for item in items:
        cursor.execute("""
            INSERT INTO normalization_audit
            (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('equipment', item['id'], 'witw_id', str(witw_id), 'NULL',
              'collision_fix_auto', 'Phase 1 auto-resolve: Aircraft+ground collision'))

    # Resolution logging
    cursor.execute("""
        INSERT INTO witw_collision_resolutions
        (witw_id, collision_count, resolution_strategy, retained_canonical_id,
         nulled_canonical_ids, escalated, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (witw_id, len(items), 'auto_null_all_multi_category', None,
          ','.join(canonical_ids), 0, 'Phase 1: NULL all (aircraft+ground)'))

    # NULL all witw_ids
    cursor.execute("""
        UPDATE equipment
        SET witw_id = NULL, witw_name = NULL
        WHERE witw_id = ?
    """, (witw_id,))

    return len(items)

def apply_retain_fuller(cursor, witw_id, items, retained_id):
    """Retain one item (fuller name), NULL others."""

    nulled_ids = [item['id'] for item in items if item['id'] != retained_id]
    retained_name = next(item['name'] for item in items if item['id'] == retained_id)

    # Audit logging for nulled items
    for item in items:
        if item['id'] != retained_id:
            cursor.execute("""
                INSERT INTO normalization_audit
                (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('equipment', item['id'], 'witw_id', str(witw_id), 'NULL',
                  'collision_fix_auto', f'Phase 1 auto-resolve: Retained fuller name ({retained_name})'))

    # Resolution logging
    cursor.execute("""
        INSERT INTO witw_collision_resolutions
        (witw_id, collision_count, resolution_strategy, retained_canonical_id,
         nulled_canonical_ids, escalated, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (witw_id, len(items), 'auto_retain_fuller_name', retained_id,
          ','.join(nulled_ids), 0, f'Phase 1: Retained {retained_name}'))

    # NULL others
    cursor.execute("""
        UPDATE equipment
        SET witw_id = NULL, witw_name = NULL
        WHERE witw_id = ? AND canonical_id != ?
    """, (witw_id, retained_id))

    return len(nulled_ids)

def main():
    """Auto-apply Phase 1 collision resolutions."""

    print("=== Phase 1: Auto-Apply Obvious Collisions ===\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all numeric WITW ID collisions
    cursor.execute("""
        SELECT
            CAST(witw_id AS INTEGER) as witw_id_num,
            COUNT(*) as collision_count,
            json_group_array(
                json_object('id', canonical_id, 'name', name, 'category', category)
            ) as items_json
        FROM equipment
        WHERE witw_id IS NOT NULL
          AND witw_id != 'NOT_IN_DATABASE'
          AND CAST(witw_id AS INTEGER) > 0
        GROUP BY CAST(witw_id AS INTEGER)
        HAVING COUNT(*) > 1
        ORDER BY CAST(witw_id AS INTEGER)
    """)

    collisions = cursor.fetchall()

    print(f"Analyzing {len(collisions)} total collisions...")
    print()

    auto_resolvable = []

    for row in collisions:
        witw_id = row['witw_id_num']
        items = json.loads(row['items_json'])

        category_info = categorize_collision(items)

        if category_info['auto_resolve']:
            auto_resolvable.append({
                'witw_id': witw_id,
                'items': items,
                'info': category_info
            })

    print(f"Found {len(auto_resolvable)} auto-resolvable collisions\n")

    if not auto_resolvable:
        print("No auto-resolvable collisions found!")
        return 0

    # Show what will be done
    print("Preview of changes:")
    print("-" * 80)

    null_all_count = 0
    retain_fuller_count = 0

    for collision in auto_resolvable:
        witw_id = collision['witw_id']
        items = collision['items']
        info = collision['info']

        print(f"\nWITW ID {witw_id}: {len(items)} items")
        for item in items:
            print(f"  - {item['id']}: {item['name']} ({item['category']})")

        if info['strategy'] == 'null_all_multi_category':
            print(f"  -> Strategy: NULL all ({info['reason']})")
            null_all_count += 1
        elif info['strategy'] == 'retain_fuller_name':
            print(f"  -> Strategy: Retain {info['retained_item']} ({info['reason']})")
            retain_fuller_count += 1

    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  NULL all (multi-category): {null_all_count} collisions")
    print(f"  Retain fuller name: {retain_fuller_count} collisions")
    print(f"  Total: {len(auto_resolvable)} collisions")
    print()

    # Prompt for confirmation
    response = input("Apply these changes? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("Cancelled by user.")
        return 1

    print("\nApplying changes...")

    try:
        total_items_modified = 0

        for collision in auto_resolvable:
            witw_id = collision['witw_id']
            items = collision['items']
            info = collision['info']

            if info['strategy'] == 'null_all_multi_category':
                modified = apply_null_all(cursor, witw_id, items)
                print(f"  WITW ID {witw_id}: NULL'd {modified} items")
                total_items_modified += modified

            elif info['strategy'] == 'retain_fuller_name':
                modified = apply_retain_fuller(cursor, witw_id, items, info['retained_item'])
                print(f"  WITW ID {witw_id}: Retained {info['retained_item']}, NULL'd {modified} others")
                total_items_modified += modified

        conn.commit()

        print(f"\n=== Phase 1 Complete ===")
        print(f"Resolved: {len(auto_resolvable)} collisions")
        print(f"Modified: {total_items_modified} equipment items")
        print(f"Transaction committed successfully!")

        # Check remaining collisions
        cursor.execute("""
            SELECT COUNT(DISTINCT witw_id) as collision_count
            FROM (
                SELECT witw_id, COUNT(*) as cnt
                FROM equipment
                WHERE witw_id IS NOT NULL
                  AND witw_id != 'NOT_IN_DATABASE'
                  AND CAST(witw_id AS INTEGER) > 0
                GROUP BY witw_id
                HAVING COUNT(*) > 1
            )
        """)

        remaining = cursor.fetchone()['collision_count']
        print(f"\nRemaining collisions: {remaining}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return 1
    finally:
        conn.close()

    return 0

if __name__ == "__main__":
    exit(main())
