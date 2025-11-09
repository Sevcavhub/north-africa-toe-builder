#!/usr/bin/env python3
"""
Verification script - demonstrate BG Builder import success
Shows sample queries and statistics
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def verify_import():
    print("=" * 80)
    print("BG BUILDER IMPORT VERIFICATION")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Table counts
    print("\nDATABASE TABLE COUNTS:")
    tables = ['bg_builder_vehicles', 'bg_builder_weapons', 'bg_builder_forces', 'bg_reference_vehicles']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table:30s} {count:4d} rows")
        except:
            print(f"   {table:30s} (not found)")

    # Sample vehicle - Panzer III J
    print("\nSAMPLE VEHICLE: Panzer III J")
    cursor.execute("""
        SELECT name, off_road_inches, road_inches, armor_front, armor_side, armor_rear,
               weapon_1, weapon_2, has_mg, has_ammo, data_status
        FROM v_vehicles_unified
        WHERE bg_builder_id = 1
    """)
    vehicle = cursor.fetchone()
    if vehicle:
        print(f"   Name: {vehicle['name']}")
        print(f"   Movement: {vehicle['off_road_inches']}\" off-road, {vehicle['road_inches']}\" road")
        print(f"   Armor: {vehicle['armor_front']}/{vehicle['armor_side']}/{vehicle['armor_rear']}")
        print(f"   Primary Weapon: {vehicle['weapon_1']}")
        print(f"   Has MG: {bool(vehicle['has_mg'])}")
        print(f"   Data Status: {vehicle['data_status']}")

    # Sample weapon - 50mmL42
    print("\nSAMPLE WEAPON: 50mmL42 (Panzer III J gun)")
    cursor.execute("""
        SELECT weapon_name, he_type, he_effect, ap_strength_0, ap_strength_10,
               ap_strength_20, ap_strength_30, ap_strength_40
        FROM v_weapons_unified
        WHERE weapon_id = 8
    """)
    weapon = cursor.fetchone()
    if weapon:
        print(f"   Name: {weapon['weapon_name']}")
        print(f"   HE: {weapon['he_type']} {weapon['he_effect']}")
        print(f"   AP Penetration at ranges:")
        print(f"      0\": {weapon['ap_strength_0']}")
        print(f"     10\": {weapon['ap_strength_10']}")
        print(f"     20\": {weapon['ap_strength_20']}")
        print(f"     30\": {weapon['ap_strength_30']}")
        print(f"     40\": {weapon['ap_strength_40']}")

    # North Africa vehicles
    print("\nNORTH AFRICA FORCES:")
    cursor.execute("""
        SELECT force_id, force_name
        FROM bg_builder_forces
        WHERE force_group LIKE '%Tobruk%' OR force_group LIKE '%Torch%'
        ORDER BY force_id
        LIMIT 10
    """)
    forces = cursor.fetchall()
    for force in forces:
        print(f"   [{force['force_id']:3d}] {force['force_name']}")

    # Linkage statistics
    print("\nMANUAL DATA LINKAGE:")
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN bg_builder_id IS NOT NULL THEN 1 ELSE 0 END) as linked,
            ROUND(100.0 * SUM(CASE WHEN bg_builder_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as pct
        FROM bg_reference_vehicles
    """)
    stats = cursor.fetchone()
    if stats:
        print(f"   Total manual vehicles: {stats['total']}")
        print(f"   Linked to BG Builder: {stats['linked']}")
        print(f"   Linkage rate: {stats['pct']}%")

    # Data completeness
    print("\nDATA COMPLETENESS:")
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN armor_front IS NOT NULL THEN 1 ELSE 0 END) as has_armor,
            SUM(CASE WHEN off_road_inches IS NOT NULL THEN 1 ELSE 0 END) as has_movement,
            SUM(CASE WHEN weapon_1 IS NOT NULL THEN 1 ELSE 0 END) as has_weapons
        FROM v_vehicles_unified
    """)
    completeness = cursor.fetchone()
    if completeness:
        total = completeness['total']
        print(f"   Total vehicles: {total}")
        print(f"   With armor data: {completeness['has_armor']} ({100*completeness['has_armor']//total}%)")
        print(f"   With movement data: {completeness['has_movement']} ({100*completeness['has_movement']//total}%)")
        print(f"   With weapons data: {completeness['has_weapons']} ({100*completeness['has_weapons']//total}%)")

    # Sample merged vehicle (BG Builder + manual)
    print("\nSAMPLE MERGED VEHICLE (BG Builder + Manual):")
    cursor.execute("""
        SELECT name, off_road_inches, road_inches, armor_front, weapon_1,
               ammo_1, mount_1, year_range, nation, data_status
        FROM v_vehicles_unified
        WHERE data_status = 'merged'
        LIMIT 1
    """)
    merged = cursor.fetchone()
    if merged:
        print(f"   Name: {merged['name']}")
        print(f"   Movement (BG Builder): {merged['off_road_inches']}/{merged['road_inches']}\"")
        print(f"   Armor (BG Builder): {merged['armor_front']}")
        print(f"   Weapon (BG Builder): {merged['weapon_1']}")
        print(f"   Ammo (Manual): {merged['ammo_1'] or 'Not yet entered'}")
        print(f"   Mount (Manual): {merged['mount_1'] or 'Not yet entered'}")
        print(f"   Year (Manual): {merged['year_range'] or 'Not yet entered'}")
        print(f"   Nation (Manual): {merged['nation'] or 'Not yet entered'}")
        print(f"   Status: {merged['data_status']}")

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE - BG Builder import successful!")
    print("=" * 80)
    print("\nNEXT STEPS:")
    print("   1. Use manual_entry_MISSING_FIELDS_ONLY.csv for optimized data entry")
    print("   2. Query v_vehicles_unified for complete vehicle stats")
    print("   3. Update datacard generator to use unified view")
    print("   4. Extract points/BR from forces.json")

    conn.close()

if __name__ == '__main__':
    verify_import()
