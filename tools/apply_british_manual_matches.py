#!/usr/bin/env python3
"""Apply manual matches for British equipment needing review"""

import sqlite3
import json
from datetime import datetime

def apply_manual_matches():
    """Apply researched matches to database"""

    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    # Matches to apply
    matches = [
        # LYSANDER VARIANTS - Map to Lysander I (WITW ID 596)
        {
            "canonical_id": "GBR_LYSANDER",
            "witw_equipment_id": "GBR_LYSANDER",
            "witw_aircraft_id": 596,
            "match_type": "aircraft",
            "confidence": 90,
            "notes": "Lysander I found in database (Nation_15), 219 mph, 851 mile range, 1938"
        },
        {
            "canonical_id": "GBR_LYSANDER_MK_I",
            "witw_equipment_id": "GBR_LYSANDER_MK_I",
            "witw_aircraft_id": 596,
            "match_type": "aircraft",
            "confidence": 95,
            "notes": "Direct match to Lysander I (WITW ID 596)"
        },
        {
            "canonical_id": "GBR_WESTLAND_LYSANDER",
            "witw_equipment_id": "GBR_WESTLAND_LYSANDER",
            "witw_aircraft_id": 596,
            "match_type": "aircraft",
            "confidence": 90,
            "notes": "Westland Lysander generic designation, matched to Lysander I"
        },

        # MARYLAND - Direct match to Maryland I (WITW ID 615)
        {
            "canonical_id": "GBR_MARYLAND",
            "witw_equipment_id": "GBR_MARYLAND",
            "witw_aircraft_id": 615,
            "match_type": "aircraft",
            "confidence": 95,
            "notes": "Maryland I found in database (Nation_15), 304 mph, 1,380 mile range, 1940"
        }
    ]

    # Items needing new database entries (will add to aircraft table)
    new_aircraft = [
        {
            "canonical_id": "GBR_LYSANDER_MK_III",
            "witw_id": 1025,  # New WITW ID
            "name": "Lysander III",
            "nation": "British",
            "max_speed": 212,
            "max_altitude": 21500,
            "year": 1940,
            "crew": 2,
            "range": 600,
            "notes": "Westland Lysander Mk III - Special operations variant with Bristol Mercury XX 870hp engine. Researched from web sources."
        },
        {
            "canonical_id": "GBR_HURRICANE_RECON",
            "witw_id": 1026,  # New WITW ID
            "name": "Hurricane Tac R",
            "nation": "British",
            "max_speed": 350,
            "max_altitude": 36000,
            "year": 1941,
            "crew": 1,
            "range": 470,
            "notes": "Hurricane tactical reconnaissance conversion. Camera-equipped with some armament removed. Based on Hurricane IIC/IIB. Egypt conversions 1941."
        },
        {
            "canonical_id": "GBR_BRISTOL_BLENHEIM_RECCE",
            "witw_id": 1027,  # New WITW ID
            "name": "Blenheim IV (Photo Recon)",
            "nation": "British",
            "max_speed": 266,
            "max_altitude": 27260,
            "year": 1939,
            "crew": 3,
            "range": 1460,
            "notes": "Bristol Blenheim Mk IV reconnaissance variant. First RAF sortie WWII Sept 3, 1939. Twin Bristol Mercury XV/XX engines 905-920hp."
        }
    ]

    # Items to reject (not equipment items)
    rejections = [
        {
            "canonical_id": "GBR_RECONNAISSANCE",
            "reason": "Generic category, not specific equipment",
            "match_type": "FILTERED",
            "confidence": None,
            "notes": "Summary category - should be filtered out"
        }
    ]

    # Items needing future research (guns not in database)
    research_needed = [
        {
            "canonical_id": "GBR_7.2-INCH_HOWITZER",
            "reason": "Gun not in database - needs to be added to guns table",
            "match_type": "NEEDS_ADDITION",
            "confidence": None,
            "notes": "BL 7.2-inch Howitzer: 183mm caliber, 200lb shell, 16,900-19,600 yd range. Should be added to guns database."
        }
    ]

    print("=" * 80)
    print("APPLYING BRITISH MANUAL MATCHES")
    print("=" * 80)

    # 1. Add new aircraft to database
    print("\n1. Adding new aircraft to database...")
    for aircraft in new_aircraft:
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

        # Also add match to match_reviews
        cursor.execute("""
            INSERT INTO match_reviews (
                witw_equipment_id, canonical_id, match_type,
                witw_aircraft_id, confidence, notes,
                reviewed_at, reviewed_by, approved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            aircraft['canonical_id'],
            aircraft['canonical_id'],
            'aircraft',
            aircraft['witw_id'],
            95,
            aircraft['notes'],
            datetime.now().isoformat(),
            'Manual research',
            1
        ))
        print(f"       Match approved in match_reviews")

    # 2. Apply aircraft matches for existing database items
    print("\n2. Applying matches for existing aircraft...")
    for match in matches:
        cursor.execute("""
            INSERT INTO match_reviews (
                witw_equipment_id, canonical_id, match_type,
                witw_aircraft_id, confidence, notes,
                reviewed_at, reviewed_by, approved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match['witw_equipment_id'],
            match['canonical_id'],
            match['match_type'],
            match['witw_aircraft_id'],
            match['confidence'],
            match['notes'],
            datetime.now().isoformat(),
            'Manual research',
            1
        ))
        print(f"  [OK] Matched: {match['canonical_id']} → Aircraft ID {match['witw_aircraft_id']}")

    # 3. Add rejections
    print("\n3. Filtering out generic categories...")
    for rejection in rejections:
        cursor.execute("""
            INSERT INTO match_reviews (
                witw_equipment_id, canonical_id, match_type,
                confidence, notes, reviewed_at, reviewed_by, approved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rejection['canonical_id'],
            rejection['canonical_id'],
            rejection['match_type'],
            rejection['confidence'],
            rejection['notes'],
            datetime.now().isoformat(),
            'Manual research',
            0
        ))
        print(f"  [X] Filtered: {rejection['canonical_id']} - {rejection['reason']}")

    # 4. Log items needing future work
    print("\n4. Items needing future database additions...")
    for item in research_needed:
        cursor.execute("""
            INSERT INTO match_reviews (
                witw_equipment_id, canonical_id, match_type,
                confidence, notes, reviewed_at, reviewed_by, approved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['canonical_id'],
            item['canonical_id'],
            item['match_type'],
            item['confidence'],
            item['notes'],
            datetime.now().isoformat(),
            'Manual research',
            0
        ))
        print(f"  [!] Needs addition: {item['canonical_id']}")
        print(f"      {item['notes']}")

    conn.commit()

    # Get final counts
    cursor.execute("""
        SELECT COUNT(*) FROM match_reviews
        WHERE witw_equipment_id LIKE 'GBR_%' AND approved = 1
    """)
    approved_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM match_reviews
        WHERE witw_equipment_id LIKE 'GBR_%' AND approved = 0
    """)
    rejected_count = cursor.fetchone()[0]

    conn.close()

    print("\n" + "=" * 80)
    print("BRITISH MATCHING SUMMARY")
    print("=" * 80)
    print(f"Total approved matches: {approved_count}")
    print(f"Total rejected/filtered: {rejected_count}")
    print(f"Total database entries: {approved_count + rejected_count}")
    print()
    print("NOTE: 7.2-inch Howitzer needs to be added to guns table in future.")
    print("=" * 80)

if __name__ == '__main__':
    apply_manual_matches()
