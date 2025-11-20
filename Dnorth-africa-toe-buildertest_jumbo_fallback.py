#!/usr/bin/env python3
"""Debug Sherman Jumbo weapon lookup - trace fallback path"""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path("database/master_database.db")

conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get Sherman Jumbo
cursor.execute("SELECT id, name FROM bg_builder_vehicles WHERE name = 'M4A3E2 Sherman Jumbo'")
vehicle_row = cursor.fetchone()
vehicle_id = vehicle_row['id']

print(f"Vehicle: {vehicle_row['name']}")
print(f"Vehicle ID: {vehicle_id}")
print("="*70)

# Check bg_reference_vehicles
cursor.execute("SELECT weapon_1 FROM bg_reference_vehicles WHERE bg_builder_id = ?", (vehicle_id,))
ref_row = cursor.fetchone()
if ref_row:
    print(f"\n✓ Found in bg_reference_vehicles:")
    print(f"  weapon_1: {ref_row['weapon_1']}")
    print("  → Will use manual extraction path (NOT fallback)")
else:
    print(f"\n✗ NOT in bg_reference_vehicles")
    print("  → Will use FALLBACK path")

# FALLBACK PATH: Get weapon IDs from bg_builder_vehicles
cursor.execute("SELECT weapon_1_id, weapon_2_id, weapon_3_id, weapon_4_id FROM bg_builder_vehicles WHERE id = ?", (vehicle_id,))
builder_row = cursor.fetchone()

print(f"\n{'='*70}")
print("FALLBACK: bg_builder_vehicles weapons:")
print(f"{'='*70}")

fallback_weapon_id = None
for i in range(1, 5):
    weapon_id = builder_row[f'weapon_{i}_id']
    if weapon_id:
        cursor.execute("SELECT weapon_name FROM bg_builder_weapons WHERE weapon_id = ?", (weapon_id,))
        weapon_row = cursor.fetchone()
        if weapon_row:
            weapon_name = weapon_row['weapon_name']
            print(f"  weapon_{i}_id: {weapon_id}")
            print(f"    name: {weapon_name}")

            # Check if this is a MG (should skip)
            if weapon_name.upper() in ['MG', 'MMG', 'HMG', 'LMG']:
                print(f"    → SKIP (Machine Gun)")
            else:
                print(f"    → MAIN GUN FOUND")
                if not fallback_weapon_id:
                    fallback_weapon_id = weapon_id
                    print(f"    → Setting fallback_weapon_id = {weapon_id}")

print(f"\n{'='*70}")
print(f"FALLBACK RESULT: fallback_weapon_id = {fallback_weapon_id}")
print(f"{'='*70}")

# Now test the HE/AP data lookup
if fallback_weapon_id:
    print(f"\nQuerying bg_builder_weapons for weapon_id {fallback_weapon_id}:")
    cursor.execute("""
        SELECT weapon_name, he_type, he_effect,
               he_strength_0, he_strength_10, he_strength_20,
               he_strength_30, he_strength_40, he_strength_50,
               ap_effect, ap_strength_0, ap_strength_10, ap_strength_20,
               ap_strength_30, ap_strength_40, ap_strength_50
        FROM bg_builder_weapons
        WHERE weapon_id = ?
    """, (fallback_weapon_id,))
    bg_weapon_he_ap_data = cursor.fetchone()

    if bg_weapon_he_ap_data:
        print("  ✓ bg_weapon_he_ap_data FOUND:")
        print(f"    weapon_name: {bg_weapon_he_ap_data['weapon_name']}")
        print(f"    he_type: {bg_weapon_he_ap_data['he_type']}")
        print(f"    he_effect: {bg_weapon_he_ap_data['he_effect']}")
        print(f"    ap_strength_0: {bg_weapon_he_ap_data['ap_strength_0']}")
        print(f"    ap_strength_10: {bg_weapon_he_ap_data['ap_strength_10']}")
        print(f"    ap_strength_20: {bg_weapon_he_ap_data['ap_strength_20']}")

        # Simulate the code that populates ap_vals
        ap_vals = [
            str(bg_weapon_he_ap_data['ap_strength_0']) if bg_weapon_he_ap_data['ap_strength_0'] is not None else '-',
            str(bg_weapon_he_ap_data['ap_strength_10']) if bg_weapon_he_ap_data['ap_strength_10'] is not None else '-',
            str(bg_weapon_he_ap_data['ap_strength_20']) if bg_weapon_he_ap_data['ap_strength_20'] is not None else '-',
            str(bg_weapon_he_ap_data['ap_strength_30']) if bg_weapon_he_ap_data['ap_strength_30'] is not None else '-',
            str(bg_weapon_he_ap_data['ap_strength_40']) if bg_weapon_he_ap_data['ap_strength_40'] is not None else '-',
            str(bg_weapon_he_ap_data['ap_strength_50']) if bg_weapon_he_ap_data['ap_strength_50'] is not None else '-'
        ]
        print(f"\n  AP VALUES: {'/'.join(ap_vals)}")

        # Extract HE weight
        import re
        he_type = bg_weapon_he_ap_data['he_type'] or ''
        if he_type and '[' in he_type and ']' in he_type:
            match = re.search(r'\[([^\]]+)\]', he_type)
            he_weight = match.group(1) if match else he_type
        else:
            he_weight = he_type if he_type else '-'

        he_effectiveness = bg_weapon_he_ap_data['he_effect'] if bg_weapon_he_ap_data['he_effect'] else '-'

        print(f"  HE WEIGHT: {he_weight}")
        print(f"  HE EFFECTIVENESS: {he_effectiveness}")
    else:
        print("  ✗ bg_weapon_he_ap_data is NULL")

conn.close()

print(f"\n{'='*70}")
print("CONCLUSION:")
print(f"{'='*70}")
if not ref_row:
    print("✓ Sherman Jumbo will use FALLBACK path")
    if fallback_weapon_id:
        print(f"✓ fallback_weapon_id = {fallback_weapon_id}")
        if bg_weapon_he_ap_data:
            print("✓ bg_weapon_he_ap_data has HE/AP values")
            print("\n→ TABLE 2 SHOULD BE GENERATED")
            print("→ If Table 2 is missing, the problem is in the table generation logic (line 936+)")
        else:
            print("✗ bg_weapon_he_ap_data is None")
            print("\n→ TABLE 2 WILL NOT BE GENERATED")
    else:
        print("✗ fallback_weapon_id is None (no main gun found)")
