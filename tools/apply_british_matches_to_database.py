#!/usr/bin/env python3
"""Apply British equipment matching results to database"""

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
    json_file = PROJECT_ROOT / "data" / "equipment_matching_logs" / "british_automated_matching_20251018_221940.json"

    with open(json_file, 'r') as f:
        data = json.load(f)

    print("=" * 80)
    print("APPLYING BRITISH AUTOMATED MATCHES TO DATABASE")
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
        elif decision_type == "FILTERED":
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
        {
            'canonical_id': 'GBR_LYSANDER',
            'witw_name': 'Lysander',
            'notes': 'MANUAL MATCH: Lysander I found in aircraft database (WITW ID 596, Nation_15). Specs: 219 mph, 851 mile range, 1938. Confidence: 90%',
            'confidence': 90,
            'status': 'approved'
        },
        {
            'canonical_id': 'GBR_LYSANDER_MK_I',
            'witw_name': 'Lysander Mk I',
            'notes': 'MANUAL MATCH: Direct match to Lysander I (WITW ID 596). Confidence: 95%',
            'confidence': 95,
            'status': 'approved'
        },
        {
            'canonical_id': 'GBR_WESTLAND_LYSANDER',
            'witw_name': 'Westland Lysander',
            'notes': 'MANUAL MATCH: Lysander I (WITW ID 596). Generic designation. Confidence: 90%',
            'confidence': 90,
            'status': 'approved'
        },
        {
            'canonical_id': 'GBR_LYSANDER_MK_III',
            'witw_name': 'Lysander Mk III',
            'notes': 'MANUAL RESEARCH: Added to aircraft database (WITW ID 1025). Bristol Mercury XX 870hp, 212 mph @ 5,000 ft, 600 mile range, 21,500 ft ceiling, crew 2. Special operations variant. Confidence: 95%',
            'confidence': 95,
            'status': 'approved'
        },
        {
            'canonical_id': 'GBR_MARYLAND',
            'witw_name': 'Maryland',
            'notes': 'MANUAL MATCH: Maryland I found in aircraft database (WITW ID 615, Nation_15). Specs: 304 mph, 1,380 mile range, 1940. Confidence: 95%',
            'confidence': 95,
            'status': 'approved'
        },
        {
            'canonical_id': 'GBR_HURRICANE_RECON',
            'witw_name': 'Hurricane Recon',
            'notes': 'MANUAL RESEARCH: Added to aircraft database (WITW ID 1026). Tactical reconnaissance conversion based on Hurricane IIC/IIB with camera equipment. Some armament removed. Egypt conversions 1941, max speed 350 mph. Confidence: 90%',
            'confidence': 90,
            'status': 'approved'
        },
        {
            'canonical_id': 'GBR_BRISTOL_BLENHEIM_RECCE',
            'witw_name': 'Bristol Blenheim (recce)',
            'notes': 'MANUAL RESEARCH: Added to aircraft database (WITW ID 1027). Blenheim IV reconnaissance variant with twin Bristol Mercury XV/XX engines 905-920hp. First RAF sortie WWII Sept 3, 1939. Max speed 266 mph, range 1,460 miles. Confidence: 95%',
            'confidence': 95,
            'status': 'approved'
        },
        {
            'canonical_id': 'GBR_RECONNAISSANCE',
            'witw_name': 'Reconnaissance',
            'notes': 'FILTERED: Generic category, not specific equipment. Should be excluded from equipment database.',
            'confidence': None,
            'status': 'rejected'
        },
        {
            'canonical_id': 'GBR_7.2-INCH_HOWITZER',
            'witw_name': '7.2-inch Howitzer',
            'notes': 'NEEDS ADDITION TO DATABASE: BL 7.2-inch Howitzer, 183mm caliber, 200lb shell, range 16,900-19,600 yd, muzzle velocity 1,700 fps. Should be added to guns table in future. Confidence: 90%',
            'confidence': 90,
            'status': 'needs_research'
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

    # Also add new aircraft to aircraft table
    new_aircraft = [
        {
            'witw_id': 1025,
            'name': 'Lysander III',
            'nation': 'British',
            'max_speed': 212,
            'max_altitude': 21500,
            'year': 1940,
            'crew': 2,
            'range': 600
        },
        {
            'witw_id': 1026,
            'name': 'Hurricane Tac R',
            'nation': 'British',
            'max_speed': 350,
            'max_altitude': 36000,
            'year': 1941,
            'crew': 1,
            'range': 470
        },
        {
            'witw_id': 1027,
            'name': 'Blenheim IV (Photo Recon)',
            'nation': 'British',
            'max_speed': 266,
            'max_altitude': 27260,
            'year': 1939,
            'crew': 3,
            'range': 1460
        }
    ]

    print("\nAdding new aircraft to aircraft table...")
    for aircraft in new_aircraft:
        # Check if already exists
        cursor.execute("""
            SELECT aircraft_id FROM aircraft WHERE witw_id = ?
        """, (aircraft['witw_id'],))

        if cursor.fetchone():
            print(f"  [SKIP] {aircraft['name']} already exists")
        else:
            cursor.execute("""
                INSERT INTO aircraft (witw_id, name, nation, max_speed, max_altitude, year, crew, range, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aircraft['witw_id'],
                aircraft['name'],
                aircraft['nation'],
                aircraft['max_speed'],
                aircraft['max_altitude'],
                aircraft['year'],
                aircraft['crew'],
                aircraft['range'],
                'Manual research - web sources'
            ))
            print(f"  [OK] Added: {aircraft['name']} (WITW ID {aircraft['witw_id']})")

    conn.commit()
    return conn

def print_summary():
    """Print final summary"""

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT review_status, COUNT(*) as count
        FROM match_reviews
        WHERE canonical_id LIKE 'GBR_%'
        GROUP BY review_status
    """)

    results = cursor.fetchall()

    print("\n" + "=" * 80)
    print("BRITISH EQUIPMENT MATCHING SUMMARY")
    print("=" * 80)

    total = 0
    for status, count in results:
        print(f"  {status}: {count}")
        total += count

    print(f"\nTotal British equipment entries: {total}")
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

    print("\n[OK] British equipment matching complete!")
    print("\nNOTE: 7.2-inch Howitzer needs to be added to guns table in future phases.")
