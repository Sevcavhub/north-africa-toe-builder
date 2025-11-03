#!/usr/bin/env python3
"""Apply all 34 remaining collision decisions."""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("database/master_database.db")

# User decisions
DECISIONS = {
    # High confidence - Cross-nation (NULL all)
    73: {'strategy': 'null_all', 'reason': 'Cross-nation collision (GER+ITA)'},
    91: {'strategy': 'null_all', 'reason': 'Cross-nation collision (GER+ITA)'},
    92: {'strategy': 'null_all', 'reason': 'Cross-nation collision (GER+ITA)'},
    180: {'strategy': 'null_all', 'reason': 'Cross-nation collision (GER+ITA)'},
    187: {'strategy': 'null_all', 'reason': 'Cross-nation collision (GER+ITA)'},

    # High confidence - British naming convention (retain Mk version)
    761: {'strategy': 'retain_one', 'retained': 'GBR_VALENTINE_MK_III', 'reason': 'British naming convention prefers Mk'},
    828: {'strategy': 'retain_one', 'retained': 'GBR_VALENTINE_MK_IX', 'reason': 'British naming convention prefers Mk'},
    2014: {'strategy': 'retain_one', 'retained': 'GBR_CRUSADER_MK_II', 'reason': 'British naming convention prefers Mk'},
    2044: {'strategy': 'retain_one', 'retained': 'GBR_CHURCHILL_MK_IV', 'reason': 'British naming convention prefers Mk'},

    # Medium confidence - User decisions
    100034: {'strategy': 'retain_one', 'retained': 'GBR_MORRIS_C8_QUAD', 'reason': 'User decision: Retain most specific Morris variant'},
    100041: {'strategy': 'keep_separate', 'reason': 'User decision: Keep GMC CCKW variants separate (different cargo capacities)'},
    100044: {'strategy': 'retain_merge_duplicate', 'retained': ['USA_DODGE_WC-52', 'USA_DODGE_WC-62'], 'reason': 'User decision: Keep WC-52 and WC-62 separate, merge duplicate WC62'},

    # Low confidence - NULL all (22 collisions)
    68: {'strategy': 'null_all', 'reason': 'Low confidence: 50mm vs 5.0cm naming'},
    84: {'strategy': 'null_all', 'reason': 'Low confidence: Panzer III Ausf G vs Command'},
    89: {'strategy': 'null_all', 'reason': 'Low confidence: Panzer IV Ausf E vs F2'},
    113: {'strategy': 'null_all', 'reason': 'Low confidence: Gladiator + Liberator collision'},
    131: {'strategy': 'null_all', 'reason': 'Low confidence: Matilda Mk II vs Grant Mk II'},
    159: {'strategy': 'null_all', 'reason': 'Low confidence: 4.5-inch Howitzer naming'},
    177: {'strategy': 'null_all', 'reason': 'Low confidence: L3/33 vs L3/35 variants'},
    179: {'strategy': 'null_all', 'reason': 'Low confidence: M11/39 + multiple Italian guns'},
    192: {'strategy': 'null_all', 'reason': 'Low confidence: 47mm Mod 37 vs 47mm AT'},
    205: {'strategy': 'null_all', 'reason': 'Low confidence: 100mm guns + Semovente'},
    231: {'strategy': 'null_all', 'reason': 'Low confidence: P-38G vs P-38H variants'},
    258: {'strategy': 'null_all', 'reason': 'Low confidence: 37mm M3 vs 57mm M1'},
    268: {'strategy': 'null_all', 'reason': 'Low confidence: M1 155mm vs M2A1 105mm'},
    271: {'strategy': 'null_all', 'reason': 'Low confidence: M1 57mm vs M3 37mm AT guns'},
    2003: {'strategy': 'null_all', 'reason': 'Low confidence: Stuart I variants'},
    2011: {'strategy': 'null_all', 'reason': 'Low confidence: A13 Mk II variants'},
    2024: {'strategy': 'null_all', 'reason': 'Low confidence: Grant M3 variants'},
    2059: {'strategy': 'null_all', 'reason': 'Low confidence: Daimler variants'},
    3098: {'strategy': 'null_all', 'reason': 'Low confidence: Light Tank Mk VI variants'},
    100021: {'strategy': 'null_all', 'reason': 'Low confidence: Ford F15 variants'},
    100024: {'strategy': 'null_all', 'reason': 'Low confidence: CMP Chevrolet variants'},
    100050: {'strategy': 'null_all', 'reason': 'Low confidence: Diamond T variants'},
}

def apply_null_all(cursor, witw_id, reason):
    """NULL all witw_ids for a collision."""

    # Get items
    cursor.execute("""
        SELECT canonical_id, name FROM equipment WHERE witw_id = ?
    """, (witw_id,))
    items = cursor.fetchall()

    if not items:
        return 0

    canonical_ids = [item['canonical_id'] for item in items]

    # Audit logging
    for item in items:
        cursor.execute("""
            INSERT INTO normalization_audit
            (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('equipment', item['canonical_id'], 'witw_id', str(witw_id), 'NULL',
              'collision_fix_final', reason))

    # Resolution logging
    cursor.execute("""
        INSERT INTO witw_collision_resolutions
        (witw_id, collision_count, resolution_strategy, retained_canonical_id,
         nulled_canonical_ids, escalated, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (witw_id, len(items), 'null_all', None, ','.join(canonical_ids), 1, reason))

    # NULL all
    cursor.execute("UPDATE equipment SET witw_id = NULL, witw_name = NULL WHERE witw_id = ?", (witw_id,))

    return len(items)

def apply_retain_one(cursor, witw_id, retained_id, reason):
    """Retain one item, NULL others."""

    # Get items
    cursor.execute("""
        SELECT canonical_id, name FROM equipment WHERE witw_id = ?
    """, (witw_id,))
    items = cursor.fetchall()

    if not items:
        return 0

    nulled_ids = [item['canonical_id'] for item in items if item['canonical_id'] != retained_id]

    # Audit logging for nulled items
    for item in items:
        if item['canonical_id'] != retained_id:
            cursor.execute("""
                INSERT INTO normalization_audit
                (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('equipment', item['canonical_id'], 'witw_id', str(witw_id), 'NULL',
                  'collision_fix_final', f'{reason} (retained {retained_id})'))

    # Resolution logging
    cursor.execute("""
        INSERT INTO witw_collision_resolutions
        (witw_id, collision_count, resolution_strategy, retained_canonical_id,
         nulled_canonical_ids, escalated, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (witw_id, len(items), 'retain_one', retained_id, ','.join(nulled_ids), 1, reason))

    # NULL others
    cursor.execute("""
        UPDATE equipment SET witw_id = NULL, witw_name = NULL
        WHERE witw_id = ? AND canonical_id != ?
    """, (witw_id, retained_id))

    return len(nulled_ids)

def apply_keep_separate(cursor, witw_id, reason):
    """Keep all separate (NULL all witw_ids)."""
    return apply_null_all(cursor, witw_id, f'{reason} (keep separate)')

def apply_retain_merge_duplicate(cursor, witw_id, retained_ids, reason):
    """Retain multiple items, NULL duplicates."""

    # Get items
    cursor.execute("""
        SELECT canonical_id, name FROM equipment WHERE witw_id = ?
    """, (witw_id,))
    items = cursor.fetchall()

    if not items:
        return 0

    nulled_ids = [item['canonical_id'] for item in items if item['canonical_id'] not in retained_ids]

    # Audit logging
    for item in items:
        if item['canonical_id'] not in retained_ids:
            cursor.execute("""
                INSERT INTO normalization_audit
                (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('equipment', item['canonical_id'], 'witw_id', str(witw_id), 'NULL',
                  'collision_fix_final', f'{reason} (retained {", ".join(retained_ids)})'))

    # Resolution logging
    cursor.execute("""
        INSERT INTO witw_collision_resolutions
        (witw_id, collision_count, resolution_strategy, retained_canonical_id,
         nulled_canonical_ids, escalated, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (witw_id, len(items), 'keep_separate_merge_duplicates', ','.join(retained_ids),
          ','.join(nulled_ids), 1, reason))

    # NULL others
    placeholders = ','.join('?' * len(retained_ids))
    cursor.execute(f"""
        UPDATE equipment SET witw_id = NULL, witw_name = NULL
        WHERE witw_id = ? AND canonical_id NOT IN ({placeholders})
    """, (witw_id, *retained_ids))

    return len(nulled_ids)

def main():
    """Apply all 34 remaining collision decisions."""

    print("=== Applying All 34 Remaining Collision Decisions ===\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    total_modified = 0
    null_all_count = 0
    retain_one_count = 0
    keep_separate_count = 0

    try:
        for witw_id, decision in sorted(DECISIONS.items()):
            strategy = decision['strategy']
            reason = decision['reason']

            print(f"WITW ID {witw_id}: {strategy}")

            if strategy == 'null_all':
                modified = apply_null_all(cursor, witw_id, reason)
                null_all_count += 1

            elif strategy == 'retain_one':
                retained = decision['retained']
                modified = apply_retain_one(cursor, witw_id, retained, reason)
                retain_one_count += 1
                print(f"  Retained: {retained}")

            elif strategy == 'keep_separate':
                modified = apply_keep_separate(cursor, witw_id, reason)
                keep_separate_count += 1
                print(f"  Kept all separate (NULL'd witw_ids)")

            elif strategy == 'retain_merge_duplicate':
                retained_list = decision['retained']
                modified = apply_retain_merge_duplicate(cursor, witw_id, retained_list, reason)
                keep_separate_count += 1
                print(f"  Retained: {', '.join(retained_list)}")

            total_modified += modified
            print(f"  Modified: {modified} items\n")

        conn.commit()

        print("=" * 80)
        print(f"\n=== All 34 Collisions Resolved ===")
        print(f"Strategies applied:")
        print(f"  NULL all: {null_all_count}")
        print(f"  Retain one: {retain_one_count}")
        print(f"  Keep separate: {keep_separate_count}")
        print(f"Total items modified: {total_modified}")
        print(f"Transaction committed successfully!\n")

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
        print(f"Remaining collisions: {remaining}")

        if remaining == 0:
            print("\nSUCCESS: All WITW ID collisions resolved!")

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
