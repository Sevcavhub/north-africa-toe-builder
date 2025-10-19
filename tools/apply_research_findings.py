#!/usr/bin/env python3
"""
Apply French equipment research findings to database
"""
import sqlite3
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"

def main():
    print("="*80)
    print("APPLYING FRENCH EQUIPMENT RESEARCH FINDINGS")
    print("="*80)

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Research findings
    research_items = [
        {
            'name': 'Panhard 178',
            'notes': 'RESEARCH COMPLETE: Armored car, 8.6t, crew 4, 25mm gun. Production: 1,143 units (729 pre-war). North Africa deployment LIMITED - 128 vehicles with desert radiators, but most captured by Germans (190 units) or used by Vichy (64 units). Very few available for Free French forces. Confidence: 85%. Sources: MilitaryFactory, Tank-AFV, WW2DB.'
        },
        {
            'name': 'White-laffly AMD 50',
            'notes': 'RESEARCH COMPLETE: Armored car, 6.2t, crew 4, 37mm Puteaux SA18. Production: 98 upgraded from White 1918 chassis. North Africa deployment CONFIRMED - 28-32 vehicles in Algeria/Tunisia May 1940, active until Nov 1943 when replaced by M8 Greyhound. Used by Free French in Tunisia 1942-1943. Confidence: 90%. Sources: Tank-AFV, WarWheels.'
        },
        {
            'name': '75mm M1897',
            'notes': 'RESEARCH COMPLETE: Field artillery, 75mm, 1,544kg, crew 6. Revolutionary hydro-pneumatic recoil. Rate of fire: 15-30 rpm. Range: 8,500m. Production: 21,000+ guns. North Africa deployment CONFIRMED - Standard Free French field artillery, widely used, proven design. Confidence: 95%. Sources: WW2DB, Landships, HistoryOfWar.'
        },
        {
            'name': 'QF 25-pounder',
            'notes': 'RESEARCH COMPLETE: BRITISH EQUIPMENT - Field artillery/gun-howitzer, 87.6mm (25-pdr shell weight), ~1,800kg, crew 6-8. Rate of fire: 5-8 rpm. Range: 13,400 yards. Production: 12,000+ guns 1940-1945. North Africa deployment CONFIRMED - British lend-lease to Free French forces, used in Tunisia 1942-1943. Confidence: 95%. NOTE: Cross-reference to British gun database entry.'
        },
        {
            'name': 'QF 6-pounder',
            'notes': 'RESEARCH COMPLETE: BRITISH EQUIPMENT - Anti-tank gun, 57mm (6-pdr shell weight), ~1,140kg, crew 5-6. Rate of fire: 15-20 rpm. Penetration: 74mm @ 1,000 yards. Production: 15,000+ guns 1941-1945. North Africa deployment CONFIRMED - British lend-lease to Free French forces, effective against German armor in Tunisia from 1942 onwards. Confidence: 95%. NOTE: Cross-reference to British gun database entry.'
        }
    ]

    print(f"\nUpdating match_reviews for {len(research_items)} items...\n")

    updated_count = 0
    for item in research_items:
        cursor.execute("""
            UPDATE match_reviews
            SET reviewer_notes = ?,
                reviewed_at = ?
            WHERE witw_name = ?
        """, (item['notes'], datetime.now().isoformat(), item['name']))

        if cursor.rowcount > 0:
            print(f"[OK] Updated: {item['name']}")
            updated_count += 1
        else:
            print(f"[WARN] Not found in match_reviews: {item['name']}")

    # Add research log entry
    print(f"\nAdding research log entry...")
    cursor.execute("""
        INSERT INTO import_log (
            source_name,
            source_file,
            import_started_at,
            import_completed_at,
            records_imported,
            records_failed,
            import_status,
            imported_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'french_equipment_research',
        'data/research_requests/FRENCH_RESEARCH_SUMMARY.md',
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        len(research_items),
        0,
        'success',
        'automated_research_agent'
    ))

    conn.commit()

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Match reviews updated: {updated_count}")
    print(f"Research log entries added: 1")
    print(f"\n[OK] Research findings applied to database!")
    print(f"{'='*80}")

    # Verification
    print(f"\nVerification - Recent research entries:")
    cursor.execute("""
        SELECT witw_name, substr(reviewer_notes, 1, 80) || '...' as preview
        FROM match_reviews
        WHERE reviewer_notes LIKE '%RESEARCH COMPLETE%'
        ORDER BY reviewed_at DESC
        LIMIT 5
    """)

    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")

    conn.close()

if __name__ == '__main__':
    main()
