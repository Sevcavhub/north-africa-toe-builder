#!/usr/bin/env python3
"""
Export CSV template for manual entry - ONLY MISSING FIELDS.
Uses BG Builder data as base, user fills in: ammo counts, weapon mounts, metadata.
"""
import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
OUTPUT_CSV = Path(__file__).parent.parent.parent.parent / "manual_entry_MISSING_FIELDS_ONLY.csv"

def export_template():
    print("Exporting Optimized Manual Entry Template")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all BG Builder vehicles with weapon names resolved
    cursor.execute("""
        SELECT
            bgb.id,
            bgb.name,
            bgb.movement_off_road,
            bgb.movement_road,
            bgb.armor_front,
            bgb.armor_side,
            bgb.armor_rear,
            w1.weapon_name as weapon_1,
            w2.weapon_name as weapon_2,
            w3.weapon_name as weapon_3,
            w4.weapon_name as weapon_4,
            bgb.special_rules,
            bgb.has_mg,
            bgb.has_ammo
        FROM bg_builder_vehicles bgb
        LEFT JOIN bg_builder_weapons w1 ON bgb.weapon_1_id = w1.weapon_id
        LEFT JOIN bg_builder_weapons w2 ON bgb.weapon_2_id = w2.weapon_id
        LEFT JOIN bg_builder_weapons w3 ON bgb.weapon_3_id = w3.weapon_id
        LEFT JOIN bg_builder_weapons w4 ON bgb.weapon_4_id = w4.weapon_id
        ORDER BY bgb.name
    """)

    vehicles = cursor.fetchall()

    # Write CSV with ONLY fields user needs to fill
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'id', 'name',
            # READ-ONLY REFERENCE (from BG Builder)
            'movement_REF', 'armor_REF', 'weapons_REF', 'special_rules_REF',
            # FILL THESE FIELDS (missing from BG Builder)
            'ammo_1', 'ammo_2', 'ammo_3', 'ammo_4',
            'mount_1', 'mount_2', 'mount_3', 'mount_4',
            'year_range', 'vehicle_type', 'nation',
            'armor_modifier', 'armor_side_schurzen',
            'notes'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for v in vehicles:
            # Build reference strings
            movement_ref = f"{v['movement_off_road']}/{v['movement_road']}" if v['movement_off_road'] else ""
            armor_ref = f"{v['armor_front'] or ''}/{v['armor_side'] or ''}/{v['armor_rear'] or ''}"
            weapons = [v['weapon_1'], v['weapon_2'], v['weapon_3'], v['weapon_4']]
            weapons_ref = ", ".join([w for w in weapons if w])

            writer.writerow({
                'id': v['id'],
                'name': v['name'],
                # Reference data (user can see but doesn't edit)
                'movement_REF': movement_ref,
                'armor_REF': armor_ref,
                'weapons_REF': weapons_ref,
                'special_rules_REF': v['special_rules'] or '',
                # Empty fields for user to fill
                'ammo_1': '',
                'ammo_2': '',
                'ammo_3': '',
                'ammo_4': '',
                'mount_1': '',
                'mount_2': '',
                'mount_3': '',
                'mount_4': '',
                'year_range': '',
                'vehicle_type': '',
                'nation': '',
                'armor_modifier': '',
                'armor_side_schurzen': '',
                'notes': ''
            })

    print(f"\nExported {len(vehicles)} vehicles to {OUTPUT_CSV}")
    print("\nCSV Structure:")
    print("   READ-ONLY columns (suffix _REF): Already filled from BG Builder")
    print("      - movement_REF: Off-road/Road movement in inches")
    print("      - armor_REF: Front/Side/Rear armor letters")
    print("      - weapons_REF: Weapon names from BG Builder")
    print("      - special_rules_REF: Special rules")
    print("\n   FILL THESE columns: Missing data you need to enter")
    print("      - ammo_1-4: Ammunition round counts")
    print("      - mount_1-4: Weapon mount types (turret, hull, coax, AA)")
    print("      - year_range: Production/service years")
    print("      - vehicle_type: Classification (Light Tank, Medium Tank, etc.)")
    print("      - nation: Country (German, British, Italian, American, French)")
    print("      - armor_modifier: Additional armor (Applique, Concrete, etc.)")
    print("      - armor_side_schurzen: Side skirt armor value")
    print("      - notes: Any additional notes")

    print(f"\nManual entry effort: ~10 fields vs. 25+ fields (60% reduction)")
    print(f"\nArmor/movement/weapons already complete from BG Builder!")

    conn.close()

if __name__ == '__main__':
    export_template()
