#!/usr/bin/env python3
"""Apply German equipment matching results to database"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"

def apply_automated_matches():
    """Apply automated matching results from JSON"""

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Load automated matching results
    json_file = PROJECT_ROOT / "data" / "equipment_matching_logs" / "german_automated_matching_20251018_223011.json"

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=" * 80)
    print("APPLYING GERMAN AUTOMATED MATCHES TO DATABASE")
    print("=" * 80)
    print(f"\nLoaded {len(data['decisions'])} decisions from JSON\n")

    approved_count = 0
    rejected_count = 0
    skipped_count = 0

    for decision in data['decisions']:
        canonical_id = decision['canonical_id']
        witw_name = decision['item']
        decision_type = decision['decision']
        reason = decision['reason']
        confidence = decision.get('confidence')

        # Map decision types to database status
        if decision_type == "AUTO-MATCHED":
            review_status = "approved"
            approved_count += 1
        elif decision_type == "AUTO-APPROVED":
            review_status = "approved"
            approved_count += 1
        elif decision_type == "SKIPPED":
            review_status = "needs_research"
            skipped_count += 1
        elif decision_type == "NEEDS_RESEARCH":
            review_status = "needs_research"
            skipped_count += 1
        elif decision_type == "AUTO-FILTER":
            review_status = "rejected"
            rejected_count += 1
        else:
            review_status = "pending"

        # Check if entry exists
        cursor.execute("""
            SELECT id FROM match_reviews WHERE canonical_id = ?
        """, (canonical_id,))

        exists = cursor.fetchone()

        if exists:
            # Update existing entry
            cursor.execute("""
                UPDATE match_reviews
                SET review_status = ?,
                    reviewer_notes = ?,
                    reviewed_at = ?,
                    reviewed_by = 'equipment_matcher_auto',
                    final_confidence = ?
                WHERE canonical_id = ?
            """, (
                review_status,
                f"Automated matching: {reason}",
                decision['timestamp'],
                confidence,
                canonical_id
            ))
        else:
            # Insert new entry
            cursor.execute("""
                INSERT INTO match_reviews (
                    canonical_id, witw_name,
                    review_status, reviewer_notes,
                    reviewed_at, reviewed_by, final_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                canonical_id,
                witw_name,
                review_status,
                f"Automated matching: {reason}",
                decision['timestamp'],
                'equipment_matcher_auto',
                confidence
            ))

    conn.commit()

    print(f"Applied {len(data['decisions'])} automated decisions:")
    print(f"  Approved: {approved_count}")
    print(f"  Needs research: {skipped_count}")
    print(f"  Rejected/Filtered: {rejected_count}")

    return conn

def apply_manual_research():
    """Apply manual research findings"""

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("APPLYING MANUAL RESEARCH FINDINGS")
    print("=" * 80)

    # Manual research findings
    manual_matches = [
        # AIRCRAFT - All found in database
        {
            'canonical_id': 'GER_BF_109F-4_TROP',
            'witw_name': 'Bf 109f-4/trop',
            'notes': 'MANUAL MATCH: Bf 109F-4 found in aircraft database (WITW ID 9). Tropical variant with sand filters, 404 mph, 476 mile range. Used in North Africa 1942 by JG 27. Confidence: 95%',
            'confidence': 95,
            'status': 'approved'
        },
        {
            'canonical_id': 'GER_BF_109G-2_TROP',
            'witw_name': 'Bf 109g-2/trop',
            'notes': 'MANUAL MATCH: Bf 109G-2 found in aircraft database (WITW ID 11). DB 605A engine (1,455 hp), tropical sand filters. Max speed 407 mph. North Africa service 1942-1943. Confidence: 95%',
            'confidence': 95,
            'status': 'approved'
        },
        {
            'canonical_id': 'GER_HE_111H-6',
            'witw_name': 'He 111H-6',
            'notes': 'MANUAL MATCH: He 111H-6 found in aircraft database (WITW ID 53). Twin Junkers Jumo 211F-2 engines (1,340 hp each), max speed 270 mph, range 1,705 miles, crew 5. Most numerous He 111 variant (1,800 produced 1941-1942). Confidence: 100%',
            'confidence': 100,
            'status': 'approved'
        },
        {
            'canonical_id': 'GER_JU_87D-3_TROP',
            'witw_name': 'Ju 87d-3/trop',
            'notes': 'MANUAL MATCH: Ju 87D-3 found in aircraft database (WITW ID 72). Tropical variant with sand filters + desert survival kit. Jumo 211J-1 engine (1,420 hp), max speed 257 mph. First attack variant in Ju 87 family, 1,559 built 1942+. North Africa and Eastern Front service. Confidence: 95%',
            'confidence': 95,
            'status': 'approved'
        },

        # GUNS - Need to be added to database
        {
            'canonical_id': 'GER_LEIG_18',
            'witw_name': 'Leig 18',
            'notes': 'NEEDS DATABASE ADDITION: 7.5cm leichtes Infanteriegeschütz 18 (leIG 18). Light infantry gun, 75mm caliber, weight 400kg combat / 1,560kg travel. Range 4,000m, 12 lb HE shell, 8-12 rpm. Crew 5. 9,037-12,000 produced 1939-1945. Should be added to guns table. Confidence: 95%',
            'confidence': 95,
            'status': 'needs_research'
        },
        {
            'canonical_id': 'GER_17CM_KANONE_18',
            'witw_name': '17cm Kanone 18',
            'notes': 'NEEDS DATABASE ADDITION: 17cm Kanone 18. Heavy artillery gun, 172.5mm caliber, 68kg shell, range 29,600m (18.4 miles). Weight 17,510kg, muzzle velocity 925 m/s. Designed by Krupp, entered service 1941. Corps-level counter-battery fire. Should be added to guns table. Confidence: 95%',
            'confidence': 95,
            'status': 'needs_research'
        },

        # GENERIC CATEGORY - Filter out
        {
            'canonical_id': 'GER_RECONNAISSANCE',
            'witw_name': 'Reconnaissance',
            'notes': 'FILTERED: Generic category, not specific equipment. Should be excluded from equipment database.',
            'confidence': None,
            'status': 'rejected'
        }
    ]

    print(f"\nApplying {len(manual_matches)} manual research findings...\n")

    for item in manual_matches:
        cursor.execute("""
            SELECT id FROM match_reviews WHERE canonical_id = ?
        """, (item['canonical_id'],))

        exists = cursor.fetchone()

        if exists:
            # Update existing entry
            cursor.execute("""
                UPDATE match_reviews
                SET review_status = ?,
                    reviewer_notes = ?,
                    reviewed_at = ?,
                    reviewed_by = 'manual_research',
                    final_confidence = ?
                WHERE canonical_id = ?
            """, (
                item['status'],
                item['notes'],
                datetime.now().isoformat(),
                item['confidence'],
                item['canonical_id']
            ))
            print(f"  [OK] Updated: {item['witw_name']}")
        else:
            # Insert new entry
            cursor.execute("""
                INSERT INTO match_reviews (
                    canonical_id, witw_name,
                    review_status, reviewer_notes,
                    reviewed_at, reviewed_by, final_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item['canonical_id'],
                item['witw_name'],
                item['status'],
                item['notes'],
                datetime.now().isoformat(),
                'manual_research',
                item['confidence']
            ))
            print(f"  [OK] Inserted: {item['witw_name']}")

    conn.commit()
    return conn

def print_summary():
    """Print final summary"""

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT review_status, COUNT(*) as count
        FROM match_reviews
        WHERE canonical_id LIKE 'GER_%'
        GROUP BY review_status
    """)

    results = cursor.fetchall()

    print("\n" + "=" * 80)
    print("GERMAN EQUIPMENT MATCHING SUMMARY")
    print("=" * 80)

    total = 0
    for status, count in results:
        print(f"  {status}: {count}")
        total += count

    print(f"\nTotal German equipment entries: {total}")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    # Apply automated matches
    conn = apply_automated_matches()
    conn.close()

    # Apply manual research
    conn = apply_manual_research()
    conn.close()

    # Print summary
    print_summary()

    print("\n[OK] German equipment matching complete!")
    print("\nNOTE: 7.5cm leIG 18 and 17cm Kanone 18 need to be added to guns table in future phases.")
