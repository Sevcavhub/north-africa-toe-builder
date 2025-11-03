#!/usr/bin/env python3
"""Phase 3A Batch 2 & 3: Resolve WITW ID collisions using user decisions."""

import sqlite3
import re
from pathlib import Path

DB_PATH = Path("database/master_database.db")
DECISIONS_FILE = Path("WITW_COLLISION_USER_DECISIONS.md")

# Parse user decisions from file
def parse_user_decisions():
    """Extract user decisions from the markdown file."""

    with open(DECISIONS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    decisions = {}

    # Pattern to match escalation sections
    escalation_pattern = r'## Escalation (\d+).*?WITW ID (\d+).*?\*\*User Decision\*\*: ([A-D]) - (.+?)(?=\n\n---|\Z)'

    matches = re.findall(escalation_pattern, content, re.DOTALL)

    for escalation_num, witw_id, decision_letter, decision_text in matches:
        decisions[int(witw_id)] = {
            'escalation': int(escalation_num),
            'decision': decision_letter,
            'text': decision_text.strip()
        }

    return decisions

def get_collision_info(cursor, witw_id):
    """Get all equipment items with this WITW ID."""
    cursor.execute("""
        SELECT canonical_id, name, category, witw_name
        FROM equipment
        WHERE witw_id = ?
        ORDER BY canonical_id
    """, (witw_id,))
    return cursor.fetchall()

def apply_decision_keep_separate(cursor, witw_id, items):
    """Decision D/B for keeping variants separate - NULL all witw_ids."""

    canonical_ids = [item['canonical_id'] for item in items]

    print(f"  Strategy: Keep all separate (NULL all {len(items)} items)")

    # Audit logging
    for item in items:
        cursor.execute("""
            INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('equipment', item['canonical_id'], 'witw_id', str(witw_id), 'NULL', 'collision_fix',
              f'User decision: Keep separate - variants have significant differences'))

    # Resolution logging
    cursor.execute("""
        INSERT INTO witw_collision_resolutions (witw_id, collision_count, resolution_strategy, retained_canonical_id, nulled_canonical_ids, escalated, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (witw_id, len(items), 'keep_separate', None, ','.join(canonical_ids), 1, 'Keep all separate'))

    # NULL all witw_ids
    cursor.execute("""
        UPDATE equipment
        SET witw_id = NULL, witw_name = NULL
        WHERE witw_id = ?
    """, (witw_id,))

    return len(items)

def apply_decision_null_all(cursor, witw_id, items):
    """Decision C - NULL all due to ambiguity."""

    canonical_ids = [item['canonical_id'] for item in items]

    print(f"  Strategy: NULL all (too ambiguous, {len(items)} items)")

    # Audit logging
    for item in items:
        cursor.execute("""
            INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('equipment', item['canonical_id'], 'witw_id', str(witw_id), 'NULL', 'collision_fix',
              f'User decision: NULL all - too ambiguous to determine correct item'))

    # Resolution logging
    cursor.execute("""
        INSERT INTO witw_collision_resolutions (witw_id, collision_count, resolution_strategy, retained_canonical_id, nulled_canonical_ids, escalated, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (witw_id, len(items), 'null_all_ambiguous', None, ','.join(canonical_ids), 1, 'NULL all - too ambiguous'))

    # NULL all witw_ids
    cursor.execute("""
        UPDATE equipment
        SET witw_id = NULL, witw_name = NULL
        WHERE witw_id = ?
    """, (witw_id,))

    return len(items)

def apply_decision_retain_one(cursor, witw_id, items, decision_text):
    """Decision A - Retain one item, NULL others."""

    # Parse which item to retain from decision text
    # Extract equipment name from decision text
    # Examples:
    #   "Retain SdKfz 251/1"
    #   "Retain FIAT 626 (all Variants)"
    #   "Retain Flak 36 8.8cm"
    #   "Retain Bedford MW"

    retained_item = None

    # Try to match canonical_id or name
    for item in items:
        item_name = item['name'].lower()
        canonical_lower = item['canonical_id'].lower()
        decision_lower = decision_text.lower()

        # Check for explicit matches in decision text
        if 'sdkfz 251' in decision_lower and '251' in item_name:
            if 'halftrack' in item['category'].lower() or 'halftrack' in item_name:
                retained_item = item
                break
        elif 'fiat 626' in decision_lower and '626' in item_name:
            if 'all variants' in item_name.lower() or 'all_variants' in canonical_lower:
                retained_item = item
                break
        elif 'flak 36' in decision_lower and 'flak_36' in canonical_lower:
            retained_item = item
            break
        elif 'bedford mw' in decision_lower and 'bedford_mw' in canonical_lower:
            if 'bedford_mw_15cwt' not in canonical_lower and 'bedford_mw_mwd' not in canonical_lower:
                retained_item = item
                break
        elif 'dodge wc series' in decision_lower and 'wc_series' in canonical_lower:
            retained_item = item
            break
        elif 'm3 halftrack' in decision_lower and 'm3_halftrack' == canonical_lower:
            retained_item = item
            break
        elif 'panzer i' in decision_lower and not 'ausf' in decision_lower:
            if 'panzer_i' == canonical_lower.replace('ger_', ''):
                retained_item = item
                break
        elif 'panzer ii' in decision_lower and not 'ausf' in decision_lower:
            if 'panzer_ii' == canonical_lower.replace('ger_', ''):
                retained_item = item
                break
        elif 'panzer iv' in decision_lower and not 'ausf' in decision_lower and not '_d' in canonical_lower and not '_e' in canonical_lower:
            if 'panzer_iv' == canonical_lower.replace('ger_', ''):
                retained_item = item
                break
        elif 'stug iii' in decision_lower and not 'ausf' in decision_lower:
            if 'stug_iii' == canonical_lower.replace('ger_', ''):
                retained_item = item
                break
        elif 'a9 cruiser mk i' in decision_lower and 'a9_cruiser_mk_i' in canonical_lower:
            retained_item = item
            break
        elif 'a10 cruiser mk ii' in decision_lower and 'a10_cruiser_mk_ii' in canonical_lower:
            retained_item = item
            break
        elif 'a13 mk ii cruiser mk iv' in decision_lower and 'a13_mk_ii_cruiser_mk_iv' in canonical_lower:
            retained_item = item
            break
        elif 'a12 matilda ii' in decision_lower and 'a12_matilda_ii' in canonical_lower:
            retained_item = item
            break
        elif 'churchill mk iv' in decision_lower and 'churchill_mk_iv' in canonical_lower:
            retained_item = item
            break

    if not retained_item:
        print(f"  WARNING: Could not identify retained item from decision: {decision_text}")
        print(f"  Available items: {[i['canonical_id'] for i in items]}")
        # Fallback: keep first item
        retained_item = items[0]
        print(f"  Fallback: Retaining first item: {retained_item['canonical_id']}")

    print(f"  Strategy: Retain {retained_item['canonical_id']}, NULL {len(items)-1} others")

    canonical_ids = [item['canonical_id'] for item in items]
    nulled_ids = [item['canonical_id'] for item in items if item['canonical_id'] != retained_item['canonical_id']]

    # Audit logging for nulled items only
    for item in items:
        if item['canonical_id'] != retained_item['canonical_id']:
            cursor.execute("""
                INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('equipment', item['canonical_id'], 'witw_id', str(witw_id), 'NULL', 'collision_fix',
                  f'User decision: Retain {retained_item["name"]}, NULL this variant'))

    # Resolution logging
    cursor.execute("""
        INSERT INTO witw_collision_resolutions (witw_id, collision_count, resolution_strategy, retained_canonical_id, nulled_canonical_ids, escalated, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (witw_id, len(items), 'retain_one', retained_item['canonical_id'], ','.join(nulled_ids), 1, decision_text))

    # NULL all except retained
    cursor.execute("""
        UPDATE equipment
        SET witw_id = NULL, witw_name = NULL
        WHERE witw_id = ? AND canonical_id != ?
    """, (witw_id, retained_item['canonical_id']))

    return len(nulled_ids)

def main():
    """Process all WITW ID collisions using user decisions."""

    print("=== Phase 3A Batch 2 & 3: WITW ID Collision Resolution ===\n")

    # Parse decisions
    print("Parsing user decisions...")
    decisions = parse_user_decisions()
    print(f"Found {len(decisions)} user decisions\n")

    if len(decisions) != 23:
        print(f"WARNING: Expected 23 decisions, found {len(decisions)}")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Process each decision
    total_fixed = 0
    total_nulled = 0

    try:
        for witw_id, decision_info in sorted(decisions.items()):
            print(f"Processing WITW ID {witw_id} (Escalation #{decision_info['escalation']}):")
            print(f"  Decision: {decision_info['decision']} - {decision_info['text'][:60]}...")

            # Get colliding items
            items = get_collision_info(cursor, witw_id)

            if not items:
                print(f"  WARNING: No items found with WITW ID {witw_id}")
                continue

            print(f"  Found {len(items)} colliding items:")
            for item in items:
                print(f"    - {item['canonical_id']}: {item['name']} ({item['category']})")

            # Apply decision strategy
            if decision_info['decision'] in ['D', 'B'] and 'keep' in decision_info['text'].lower() and 'separate' in decision_info['text'].lower():
                nulled = apply_decision_keep_separate(cursor, witw_id, items)
                total_nulled += nulled
            elif decision_info['decision'] == 'C' or 'null all' in decision_info['text'].lower():
                nulled = apply_decision_null_all(cursor, witw_id, items)
                total_nulled += nulled
            elif decision_info['decision'] in ['A', 'B']:
                nulled = apply_decision_retain_one(cursor, witw_id, items, decision_info['text'])
                total_nulled += nulled
            else:
                print(f"  WARNING: Unknown decision strategy: {decision_info['decision']}")

            total_fixed += 1
            print()

        # Commit transaction
        conn.commit()
        print(f"\n=== Collision Resolution Complete ===")
        print(f"Processed: {total_fixed} WITW ID collisions")
        print(f"Total equipment items modified: {total_nulled}")
        print(f"Transaction committed successfully!\n")

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
