#!/usr/bin/env python3
"""
Process user's final manual linkage decisions
- Add 3 missing vehicles to bg_builder_vehicles
- Apply 24 linkages to bg_reference_vehicles
- Delete 1 invalid entry (CMP)
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def process_final_linkages():
    print("=" * 80)
    print("PROCESSING FINAL MANUAL LINKAGE DECISIONS")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    cursor = conn.cursor()

    # Step 1: Add missing vehicles to bg_builder_vehicles
    print("\nStep 1: Adding missing vehicles to bg_builder_vehicles...")

    new_vehicles = [
        {
            'id': 600,
            'name': 'Centaur Bulldozer',
            'armor_front': 'K',
            'armor_side': 'L',
            'armor_rear': 'M',
            'movement_off_road': 9,
            'movement_road': 14,
            'weapon_1_id': None,
            'notes': 'Was not in Africa'
        },
        {
            'id': 601,
            'name': '20mm Flak Truck',
            'armor_front': 'SS',
            'armor_side': 'SS',
            'armor_rear': 'SS',
            'movement_off_road': 6,
            'movement_road': 24,
            'weapon_1_id': None,  # Would need to find 20mmL55 weapon_id
            'notes': 'German improvised AA truck, Tobruk'
        },
        {
            'id': 602,
            'name': '37mm Flak Truck',
            'armor_front': 'SS',
            'armor_side': 'SS',
            'armor_rear': 'SS',
            'movement_off_road': 6,
            'movement_road': 24,
            'weapon_1_id': None,  # Would need to find 37mmL98 weapon_id
            'notes': 'German improvised AA truck, Tobruk'
        }
    ]

    for vehicle in new_vehicles:
        cursor.execute("""
            INSERT INTO bg_builder_vehicles
            (id, name, armor_front, armor_side, armor_rear,
             movement_off_road, movement_road, weapon_1_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vehicle['id'],
            vehicle['name'],
            vehicle['armor_front'],
            vehicle['armor_side'],
            vehicle['armor_rear'],
            vehicle['movement_off_road'],
            vehicle['movement_road'],
            vehicle['weapon_1_id']
        ))
        print(f"  Added: [{vehicle['id']}] {vehicle['name']} - {vehicle['notes']}")

    # Step 2: Apply linkages
    print("\nStep 2: Applying linkages...")

    linkages = [
        (241, 418, "Churchill II"),
        (152, 88, "Churchill IV"),
        (17, 319, "Humber Light Recce Vehicle II"),
        (2, 100, "M4A1 Sherman"),
        (123, 100, "M4A2 Sherman"),
        (124, 100, "M4A3 Sherman"),
        (3, 100, "M4 Sherman"),
        (211, 7, "Panzer IV E"),
        (127, 106, "M4 Sherman DD"),
        (230, 344, "Marmon-Herrington II A (20mm)"),
        (231, 345, "Marmon-Herrington II A (37mm)"),
        (143, 577, "M3 Scout Car"),
        (101, 587, "A10"),
        (135, 600, "Centaur Bulldozer"),
        (15, 83, "M5 Ambulance"),
        (6, 136, "Dingo Scout Car"),
        (132, 130, "Crusader AA MkII (2x 20mm)"),
        (133, 233, "Crusader AA MkII (3x 20mm)"),
        (121, 83, "M5 Recce"),
        (103, 321, "A13 MkII"),
        (220, 601, "20mm Flak Truck"),
        (221, 602, "37mm Flak Truck"),
        (99, 332, "A9"),
        (189, 316, "Van")
    ]

    for manual_id, bg_id, name in linkages:
        cursor.execute("""
            UPDATE bg_reference_vehicles
            SET bg_builder_id = ?
            WHERE id = ?
        """, (bg_id, manual_id))
        print(f"  [{manual_id:3d}] {name:45s} -> [{bg_id:3d}]")

    # Step 3: Delete invalid entry
    print("\nStep 3: Deleting invalid entry...")
    cursor.execute("DELETE FROM bg_reference_vehicles WHERE id = 11")
    print(f"  Deleted: [11] CMP (data entry error)")

    # Commit changes
    conn.commit()

    # Get final statistics
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT CASE WHEN bg_builder_id IS NOT NULL THEN id END) as linked
        FROM bg_reference_vehicles
    """)
    stats = cursor.fetchone()
    total = stats[0]
    linked = stats[1]

    conn.close()

    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"\nNew bg_builder vehicles added: 3")
    print(f"Linkages applied: 24")
    print(f"Vehicles deleted: 1 (CMP)")
    print(f"\nFinal Statistics:")
    print(f"  Total manual vehicles: {total}")
    print(f"  Linked to BG Builder: {linked}")
    print(f"  Linkage rate: {linked/total*100:.1f}%")
    print(f"  Unlinked: {total - linked}")

if __name__ == '__main__':
    process_final_linkages()
