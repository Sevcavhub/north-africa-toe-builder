#!/usr/bin/env python3
"""Apply Italian equipment matching results to database"""

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
    json_file = PROJECT_ROOT / "data" / "equipment_matching_logs" / "italian_automated_matching_20251018_223424.json"

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=" * 80)
    print("APPLYING ITALIAN AUTOMATED MATCHES TO DATABASE")
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
            'canonical_id': 'ITA_RO37_LINCE',
            'witw_name': 'Ro37 Lince',
            'notes': 'MANUAL MATCH: Ro.37bis found in aircraft database (WITW ID 179). Two-seat reconnaissance biplane. Engine: Piaggio Stella P.IX R.C.40 (600 hp). Max speed 187 mph (300 km/h), range 750 miles. Crew 2. Armed with 3× 7.7mm MGs + 397 lb bombs. Operational on all fronts except Russia/English Channel. Confidence: 95%',
            'confidence': 95,
            'status': 'approved'
        },
        {
            'canonical_id': 'ITA_CR42_FALCO',
            'witw_name': 'Cr42 Falco',
            'notes': 'MANUAL MATCH: CR.42 Falco found in aircraft database (WITW ID 149). Last biplane fighter. Fiat 870hp radial, max speed 272 mph, range 481 miles. Crew 1. Armed with 2× 12.7mm MGs + 440 lb bombs. CR.42AS variant for North Africa (sand filters, ground attack role). 1,784 produced. Exceptional maneuverability but outclassed by monoplanes. Confidence: 100%',
            'confidence': 100,
            'status': 'approved'
        },
        {
            'canonical_id': 'ITA_SM79_SPARVIERO',
            'witw_name': 'Sm79 Sparviero',
            'notes': 'MANUAL MATCH: SM.79 Sparviero found in aircraft database (WITW ID 166). Three-engine torpedo bomber. Max speed 270 mph, range 1,180 miles. Bomb load 2,760 lb or 2 torpedoes. SM.79 AS variant for North Africa (sand filters, extended radiators). One of finest torpedo bombers of war - sank 86 Allied ships (708,000 tons). Confidence: 100%',
            'confidence': 100,
            'status': 'approved'
        },
        {
            'canonical_id': 'ITA_SM81_PIPISTRELLO',
            'witw_name': 'Sm81 Pipistrello',
            'notes': 'MANUAL MATCH: SM.81 Pipistrello found in aircraft database (WITW ID 167). Three-engine bomber/transport. 3× Piaggio P.X engines (670 hp each). Max speed 216 mph (335 km/h), range 1,500 km combat. Crew 6. Armed with 6× 7.7mm MGs + 2,000 kg bombs. Obsolete by 1940 but effective night bomber in North Africa. 535 produced, 300 in service 1940. Confidence: 100%',
            'confidence': 100,
            'status': 'approved'
        },

        # GUNS - Need to be added to database
        {
            'canonical_id': 'ITA_OBICE_DA_100_17',
            'witw_name': 'Obice DA 100/17',
            'notes': 'NEEDS DATABASE ADDITION: Obice da 100/17 Modello 14/16 (Italian designation for captured Škoda 10 cm M. 14/16 howitzer). Caliber 100mm, weight 1,417kg, range 8,180m (upgraded to 9km with new projectile 1932). Rate of fire 10 rpm, elevation -8° to +48°, traverse 5°21′. Mountain gun variant (can break down into 3 parts for mule transport). 1,222 captured WWI + 1,472 war reparations. Should be added to guns table. Confidence: 95%',
            'confidence': 95,
            'status': 'needs_research'
        },
        {
            'canonical_id': 'ITA_OBICE_DA_149_13',
            'witw_name': 'Obice DA 149/13',
            'notes': 'NEEDS DATABASE ADDITION: Obice da 149/13 (Italian designation for captured Škoda 15 cm schwere Feldhaubitze M 14/16). Caliber 149.1mm, shell weight 41kg, range M 14: 6,900m / M 14/16: 8,760m. Weight M 14: 2,344kg / M 14/16: 2,765kg. Muzzle velocity M 14: 300 m/s / M 14/16: 336 m/s. Rate of fire 1-2 rpm, elevation -5° to +43° (M 14) / +70° (M 14/16). 490 on hand 1939. Should be added to guns table. Confidence: 95%',
            'confidence': 95,
            'status': 'needs_research'
        },

        # GENERIC CATEGORY - Filter out
        {
            'canonical_id': 'ITA_RECONNAISSANCE',
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
        WHERE canonical_id LIKE 'ITA_%'
        GROUP BY review_status
    """)

    results = cursor.fetchall()

    print("\n" + "=" * 80)
    print("ITALIAN EQUIPMENT MATCHING SUMMARY")
    print("=" * 80)

    total = 0
    for status, count in results:
        print(f"  {status}: {count}")
        total += count

    print(f"\nTotal Italian equipment entries: {total}")
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

    print("\n[OK] Italian equipment matching complete!")
    print("\nNOTE: Obice da 100/17 and Obice da 149/13 need to be added to guns table in future phases.")
