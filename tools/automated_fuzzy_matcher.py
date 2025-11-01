#!/usr/bin/env python3
"""
Automated Fuzzy Name Matcher
Links equipment items to OnWar and WWIITANKS source data using fuzzy string matching.

Strategy:
1. For each unmatched equipment item
2. Find best fuzzy match in afv_data (OnWar) and wwiitanks_afv_data (WWIITANKS)
3. Filter by nation to avoid cross-matches
4. Auto-approve high confidence (95%+), flag rest for manual review
5. Update equipment table with matches
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional
import json

DATABASE_FILE = Path("database/master_database.db")

# Nation mappings (equipment table → source tables)
NATION_MAP = {
    'american': ['usa'],
    'british': ['uk', 'britain'],
    'german': ['germany'],
    'italian': ['italy'],
    'french': ['france']
}


def normalize_name(name: str) -> str:
    """Normalize equipment name for matching."""
    return name.lower().strip().replace('-', ' ').replace('_', ' ')


def fuzzy_match_score(str1: str, str2: str) -> float:
    """Calculate fuzzy match score (0-100) between two strings."""
    return SequenceMatcher(None, normalize_name(str1), normalize_name(str2)).ratio() * 100


def find_best_onwar_match(conn, equipment_name: str, nation: str) -> Optional[Dict]:
    """Find best OnWar AFV match for equipment item."""
    cursor = conn.cursor()

    # Get source nations for this equipment nation
    source_nations = NATION_MAP.get(nation, [nation])

    # Query all AFVs from matching nations
    placeholders = ','.join(['?' for _ in source_nations])
    cursor.execute(f"""
        SELECT vehicle_name, country, url, type
        FROM afv_data
        WHERE country IN ({placeholders})
    """, source_nations)

    afvs = cursor.fetchall()

    if not afvs:
        return None

    # Find best match
    best_match = None
    best_score = 0

    for vehicle_name, country, url, vehicle_type in afvs:
        score = fuzzy_match_score(equipment_name, vehicle_name)

        if score > best_score:
            best_score = score
            best_match = {
                'vehicle_name': vehicle_name,
                'country': country,
                'url': url,
                'type': vehicle_type,
                'confidence': round(best_score, 1)
            }

    return best_match


def find_best_wwiitanks_match(conn, equipment_name: str, nation: str) -> Optional[Dict]:
    """Find best WWIITANKS AFV match for equipment item."""
    cursor = conn.cursor()

    # Get source nations for this equipment nation
    source_nations = NATION_MAP.get(nation, [nation])

    # Query all AFVs from matching nations
    placeholders = ','.join(['?' for _ in source_nations])
    cursor.execute(f"""
        SELECT vehicle_name, country, wwiitanks_id, has_armour_details
        FROM wwiitanks_afv_data
        WHERE country IN ({placeholders})
    """, source_nations)

    afvs = cursor.fetchall()

    if not afvs:
        return None

    # Find best match
    best_match = None
    best_score = 0

    for vehicle_name, country, wwiitanks_id, has_armour in afvs:
        score = fuzzy_match_score(equipment_name, vehicle_name)

        if score > best_score:
            best_score = score
            best_match = {
                'vehicle_name': vehicle_name,
                'country': country,
                'wwiitanks_id': wwiitanks_id,
                'has_armour': bool(has_armour),
                'confidence': round(best_score, 1)
            }

    return best_match


def automated_matching(conn, auto_approve_threshold: float = 95.0, min_threshold: float = 70.0):
    """Perform automated fuzzy matching for all unmatched equipment."""

    print("\n" + "=" * 70)
    print("AUTOMATED FUZZY NAME MATCHING")
    print("=" * 70)

    cursor = conn.cursor()

    # Get unmatched equipment items
    cursor.execute("""
        SELECT canonical_id, name, nation
        FROM equipment
        WHERE (onwar_matched IS NULL OR onwar_matched = 0)
          AND (wwiitanks_matched IS NULL OR wwiitanks_matched = 0)
        ORDER BY nation, name
    """)

    unmatched = cursor.fetchall()

    print(f"\nFound {len(unmatched)} unmatched equipment items")
    print(f"Auto-approve threshold: {auto_approve_threshold}%")
    print(f"Minimum match threshold: {min_threshold}%")

    auto_approved = 0
    manual_review = 0
    no_match = 0

    matches_log = []

    print("\nProcessing equipment...")

    for i, (canonical_id, name, nation) in enumerate(unmatched, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(unmatched)} ({i/len(unmatched)*100:.1f}%)")

        # Find best matches
        onwar_match = find_best_onwar_match(conn, name, nation)
        wwiitanks_match = find_best_wwiitanks_match(conn, name, nation)

        # Choose best match (prefer OnWar if similar confidence)
        best_match = None
        source = None

        if onwar_match and wwiitanks_match:
            # Prefer OnWar if confidence within 5% (OnWar has structured data)
            if onwar_match['confidence'] >= wwiitanks_match['confidence'] - 5:
                best_match = onwar_match
                source = 'onwar'
            else:
                best_match = wwiitanks_match
                source = 'wwiitanks'
        elif onwar_match:
            best_match = onwar_match
            source = 'onwar'
        elif wwiitanks_match:
            best_match = wwiitanks_match
            source = 'wwiitanks'

        if not best_match or best_match['confidence'] < min_threshold:
            no_match += 1
            matches_log.append({
                'canonical_id': canonical_id,
                'name': name,
                'nation': nation,
                'status': 'NO_MATCH',
                'reason': 'No match above minimum threshold'
            })
            continue

        # Auto-approve or flag for review
        if best_match['confidence'] >= auto_approve_threshold:
            status = 'AUTO_APPROVED'
            auto_approved += 1

            # Update equipment table
            timestamp = datetime.now().isoformat()

            if source == 'onwar':
                cursor.execute("""
                    UPDATE equipment SET
                        onwar_matched = 1,
                        onwar_url = ?,
                        match_confidence = ?,
                        match_method = 'automated_fuzzy_matcher',
                        updated_at = ?,
                        updated_by = ?
                    WHERE canonical_id = ?
                """, (best_match['url'], int(best_match['confidence']), timestamp, 'automated_fuzzy_matcher.py', canonical_id))
            else:  # wwiitanks
                cursor.execute("""
                    UPDATE equipment SET
                        wwiitanks_matched = 1,
                        wwiitanks_id = ?,
                        match_confidence = ?,
                        match_method = 'automated_fuzzy_matcher',
                        updated_at = ?,
                        updated_by = ?
                    WHERE canonical_id = ?
                """, (best_match['wwiitanks_id'], int(best_match['confidence']), timestamp, 'automated_fuzzy_matcher.py', canonical_id))
        else:
            status = 'MANUAL_REVIEW'
            manual_review += 1

        matches_log.append({
            'canonical_id': canonical_id,
            'name': name,
            'nation': nation,
            'status': status,
            'source': source,
            'matched_name': best_match['vehicle_name'],
            'confidence': best_match['confidence'],
            'match_data': best_match
        })

    conn.commit()

    print(f"\n[SUCCESS] Automated matching complete")
    print(f"  Auto-approved (>={auto_approve_threshold}%): {auto_approved}")
    print(f"  Manual review ({min_threshold}%-{auto_approve_threshold}%): {manual_review}")
    print(f"  No match (<{min_threshold}%): {no_match}")

    # Save matches log
    log_file = Path("data/equipment_matching_logs") / f"automated_fuzzy_matching_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'auto_approve_threshold': auto_approve_threshold,
            'min_threshold': min_threshold,
            'statistics': {
                'total': len(unmatched),
                'auto_approved': auto_approved,
                'manual_review': manual_review,
                'no_match': no_match
            },
            'matches': matches_log
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  Match log saved: {log_file}")

    return {
        'auto_approved': auto_approved,
        'manual_review': manual_review,
        'no_match': no_match,
        'matches_log': matches_log
    }


def generate_manual_review_report(matches_log: List[Dict]):
    """Generate report for items needing manual review."""

    manual_items = [m for m in matches_log if m['status'] == 'MANUAL_REVIEW']

    if not manual_items:
        return

    print("\n" + "=" * 70)
    print("MANUAL REVIEW NEEDED")
    print("=" * 70)

    print(f"\n{len(manual_items)} items need manual review (70-95% confidence):\n")

    for item in manual_items[:20]:  # Show first 20
        print(f"  {item['name']:35s} ({item['nation']})")
        print(f"    → Matched: {item['matched_name']} ({item['confidence']}% confidence, {item['source']})")
        print()

    if len(manual_items) > 20:
        print(f"  ...and {len(manual_items) - 20} more items")

    print("\nReview file: Check latest automated_fuzzy_matching_*.json in data/equipment_matching_logs/")


def verify_matches(conn):
    """Verify equipment table matches after automated matching."""

    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM equipment WHERE onwar_matched = 1")
    onwar_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM equipment WHERE wwiitanks_matched = 1")
    wwiitanks_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM equipment WHERE onwar_matched = 1 OR wwiitanks_matched = 1")
    total_matched = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM equipment")
    total_equipment = cursor.fetchone()[0]

    print(f"\nEquipment Matching Status:")
    print(f"  Total equipment: {total_equipment}")
    print(f"  OnWar matched: {onwar_count} ({onwar_count/total_equipment*100:.1f}%)")
    print(f"  WWIITANKS matched: {wwiitanks_count} ({wwiitanks_count/total_equipment*100:.1f}%)")
    print(f"  Either matched: {total_matched} ({total_matched/total_equipment*100:.1f}%)")
    print(f"  Unmatched: {total_equipment - total_matched} ({(total_equipment - total_matched)/total_equipment*100:.1f}%)")

    # Sample matches
    print("\nSample auto-approved matches:")
    cursor.execute("""
        SELECT name, nation, onwar_url, wwiitanks_id, match_confidence
        FROM equipment
        WHERE match_method = 'automated_fuzzy_matcher'
        LIMIT 15
    """)

    for row in cursor.fetchall():
        source = "OnWar" if row[2] else "WWIITANKS"
        print(f"  {row[0]:35s} ({row[1]}) → {source} ({row[4]}%)")


def main():
    """Main execution function."""

    print("=" * 70)
    print("AUTOMATED FUZZY NAME MATCHING")
    print("=" * 70)

    # Check database exists
    if not DATABASE_FILE.exists():
        print(f"ERROR: Database file not found: {DATABASE_FILE}")
        sys.exit(1)

    # Connect to database
    print(f"\nConnecting to: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)

    try:
        # Perform automated matching
        results = automated_matching(conn, auto_approve_threshold=95.0, min_threshold=70.0)

        # Generate manual review report
        generate_manual_review_report(results['matches_log'])

        # Verify matches
        verify_matches(conn)

        # Log to import_log
        timestamp = datetime.now().isoformat()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file, records_imported, records_failed,
                import_started_at, import_completed_at, import_status,
                error_log, imported_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'automated_fuzzy_matching',
            'afv_data + wwiitanks_afv_data',
            results['auto_approved'],
            results['no_match'],
            timestamp,
            timestamp,
            'success',
            f"Auto-approved: {results['auto_approved']}, Manual review: {results['manual_review']}, No match: {results['no_match']}",
            'automated_fuzzy_matcher.py'
        ))
        conn.commit()

        print("\n" + "=" * 70)
        print("AUTOMATED MATCHING COMPLETE")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Review manual_review items if desired (70-95% confidence)")
        print("  2. Run populate_equipment_specs.py to populate specifications")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
