"""
Phase A1: De-duplicate equipment_master_new

Merges duplicate equipment records (956 duplicates in 465 collision groups).
Chooses best record from each group based on:
1. Highest confidence_score
2. Most complete historical_specs_json
3. Primary_source preference (witw > wwiitanks > onwar)
"""

import sqlite3
import json
import re
from typing import Dict, List, Tuple, Optional


def normalize_display_name(display_name: str) -> str:
    """
    Normalize display name to detect duplicates.

    Same logic as phase_a1_simplify_canonical_names.py
    """
    name = display_name.lower()
    name = name.replace(' ', '_')
    name = re.sub(r'\(([^)]+)\)', r'_\1_', name)
    name = re.sub(r'[^a-z0-9_\-]', '', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name


def calculate_completeness(record: Tuple) -> float:
    """
    Calculate completeness score for a record.

    record: (master_id, canonical_name, display_name, short_name, category,
             subcategory, nation, historical_specs_json, primary_source,
             confidence_score, created_at, updated_at, notes)
    """
    master_id, canonical_name, display_name, short_name, category, subcategory, \
        nation, specs_json, primary_source, confidence, created_at, updated_at, notes = record

    score = 0.0

    # Confidence score (0-100)
    if confidence:
        score += confidence * 0.4  # 40% weight

    # Historical specs JSON completeness
    if specs_json:
        try:
            specs = json.loads(specs_json)
            if isinstance(specs, dict):
                # Count fields with non-null, non-empty values
                field_count = sum(1 for v in specs.values() if v not in (None, '', [], {}))
                score += min(field_count * 2, 30)  # 30% weight (cap at 30)
        except:
            pass

    # Primary source quality (30% weight)
    source_weights = {
        'witw': 30,
        'wwiitanks': 25,
        'onwar': 20,
        'bg_reference': 15,
    }
    score += source_weights.get(primary_source, 10)

    return score


def find_duplicate_groups(conn: sqlite3.Connection) -> Dict[str, List[Tuple]]:
    """
    Find all duplicate groups in equipment_master_new.

    Returns: {normalized_name: [records...]}
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT master_id, canonical_name, display_name, short_name,
               equipment_category, equipment_subcategory, original_nation,
               historical_specs_json, primary_source, confidence_score,
               created_at, updated_at, notes
        FROM equipment_master_new
        ORDER BY master_id
    """)

    # Group by normalized display name
    groups = {}
    for record in cursor.fetchall():
        display_name = record[2]
        normalized = normalize_display_name(display_name)

        if normalized not in groups:
            groups[normalized] = []
        groups[normalized].append(record)

    # Filter to only duplicates (2+ records)
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}

    return duplicates


def choose_best_record(records: List[Tuple]) -> Tuple:
    """
    Choose the best record from a duplicate group.

    Criteria:
    1. Highest completeness score
    2. If tie, prefer witw > wwiitanks > onwar source
    3. If still tie, prefer lowest master_id (original)
    """
    scored = [(calculate_completeness(r), r) for r in records]
    scored.sort(key=lambda x: (-x[0], x[1][8], x[1][0]))  # score desc, source, master_id asc

    return scored[0][1]


def merge_historical_specs(winner_specs: str, loser_specs_list: List[str]) -> str:
    """
    Merge historical_specs_json from multiple records.

    Winner's values take precedence, but fill in gaps from losers.
    """
    try:
        winner = json.loads(winner_specs) if winner_specs else {}
    except:
        winner = {}

    if not isinstance(winner, dict):
        winner = {}

    # Merge in data from losers (only if winner missing field)
    for loser_specs in loser_specs_list:
        try:
            loser = json.loads(loser_specs) if loser_specs else {}
            if isinstance(loser, dict):
                for key, value in loser.items():
                    # Only add if winner doesn't have this key or has null/empty value
                    if key not in winner or winner[key] in (None, '', [], {}):
                        if value not in (None, '', [], {}):
                            winner[key] = value
        except:
            continue

    return json.dumps(winner, indent=2)


def deduplicate_equipment_master_new(db_path: str, dry_run: bool = True):
    """
    De-duplicate equipment_master_new table.

    Args:
        db_path: Path to SQLite database
        dry_run: If True, show changes but don't commit
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 100)
    print("PHASE A1: DE-DUPLICATE EQUIPMENT_MASTER_NEW")
    print("=" * 100)
    print()

    # Get current record count
    cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
    total_before = cursor.fetchone()[0]
    print(f"Records before de-duplication: {total_before}")
    print()

    # Find duplicate groups
    print("Finding duplicate groups...")
    duplicate_groups = find_duplicate_groups(conn)

    total_duplicates = sum(len(records) for records in duplicate_groups.values())
    records_to_delete = sum(len(records) - 1 for records in duplicate_groups.values())

    print(f"Found {len(duplicate_groups)} duplicate groups")
    print(f"Total duplicate records: {total_duplicates}")
    print(f"Records to delete: {records_to_delete}")
    print(f"Records after de-duplication: {total_before - records_to_delete}")
    print()

    # Show sample duplicate groups
    print("Sample duplicate groups (first 10):")
    print("-" * 100)
    for i, (normalized_name, records) in enumerate(list(duplicate_groups.items())[:10]):
        print(f"\n{i+1}. '{normalized_name}' -> {len(records)} records:")
        for record in records:
            master_id, canonical, display, short, cat, subcat, nation, specs, source, conf, _, _, _ = record
            completeness = calculate_completeness(record)
            specs_fields = 0
            if specs:
                try:
                    specs_obj = json.loads(specs)
                    if isinstance(specs_obj, dict):
                        specs_fields = len([v for v in specs_obj.values() if v not in (None, '', [], {})])
                except:
                    pass
            print(f"    master_id={master_id:4} | {display:40} | conf={conf:.1f} | source={source:12} | "
                  f"specs_fields={specs_fields:2} | completeness={completeness:.1f}")

        # Show winner
        winner = choose_best_record(records)
        winner_id = winner[0]
        print(f"    ==> WINNER: master_id={winner_id}")

    if len(duplicate_groups) > 10:
        print(f"\n... and {len(duplicate_groups) - 10} more duplicate groups")
    print()

    # Process de-duplication
    if not dry_run:
        print("Processing de-duplication...")

        updates_made = 0
        deletes_made = 0

        for normalized_name, records in duplicate_groups.items():
            # Choose best record
            winner = choose_best_record(records)
            winner_id = winner[0]
            winner_specs = winner[7]

            # Get loser records
            losers = [r for r in records if r[0] != winner_id]
            loser_ids = [r[0] for r in losers]
            loser_specs = [r[7] for r in losers]

            # Merge historical specs
            merged_specs = merge_historical_specs(winner_specs, loser_specs)

            # Update winner with merged specs
            cursor.execute("""
                UPDATE equipment_master_new
                SET historical_specs_json = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE master_id = ?
            """, (merged_specs, winner_id))
            updates_made += 1

            # Delete losers
            placeholders = ','.join('?' * len(loser_ids))
            cursor.execute(f"""
                DELETE FROM equipment_master_new
                WHERE master_id IN ({placeholders})
            """, loser_ids)
            deletes_made += len(loser_ids)

        conn.commit()

        print(f"[OK] Updated {updates_made} winner records with merged data")
        print(f"[OK] Deleted {deletes_made} duplicate records")
        print()

        # Verify final count
        cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
        total_after = cursor.fetchone()[0]
        print(f"Records after de-duplication: {total_after}")
        print(f"Reduction: {total_before - total_after} records ({100 * (total_before - total_after) / total_before:.1f}%)")
        print()

        # Check for remaining duplicates
        remaining_duplicates = find_duplicate_groups(conn)
        if remaining_duplicates:
            print(f"[WARNING] {len(remaining_duplicates)} duplicate groups still exist")
            print("First 5 remaining duplicates:")
            for name, records in list(remaining_duplicates.items())[:5]:
                print(f"  - {name}: {len(records)} records")
        else:
            print("[OK] No duplicate display names remaining - all unique")
        print()
    else:
        print("DRY RUN - No changes applied. Run with --execute to apply de-duplication.")
        print()

    conn.close()

    return len(duplicate_groups), records_to_delete


def main():
    import argparse

    parser = argparse.ArgumentParser(description="De-duplicate equipment_master_new table")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')
    parser.add_argument('--execute', action='store_true', help='Apply de-duplication (default: dry run)')

    args = parser.parse_args()

    deduplicate_equipment_master_new(args.db, dry_run=not args.execute)


if __name__ == '__main__':
    main()
