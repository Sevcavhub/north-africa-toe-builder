#!/usr/bin/env python3
"""
Validate British Guns Import

Checks:
1. All 24 guns present (20 new + 3 multi-nation + 1 flamethrower edge case)
2. Critical fields populated (name, caliber_mm, nation)
3. HE/AP data completeness
4. ROF field populated where applicable
5. gun_name_variants created correctly
6. Special cases handled (Littlejohn, Flamethrower D6)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*80)
    print("BRITISH GUNS IMPORT VALIDATION REPORT")
    print("="*80)
    print()

    # 1. Count British guns
    cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE nation LIKE '%british%'")
    british_count = cursor.fetchone()[0]
    print(f"[*] British guns in database: {british_count}")
    print(f"    Expected: 23 (20 British-only + 3 multi-nation)")
    print()

    # 2. Check for NULL critical fields
    cursor.execute("""
        SELECT name
        FROM bg_reference_guns
        WHERE nation LIKE '%british%'
          AND (name IS NULL OR caliber_mm IS NULL)
    """)
    missing_critical = cursor.fetchall()
    if missing_critical:
        print("[!] WARNING: Guns missing critical fields:")
        for row in missing_critical:
            print(f"    - {row[0]}")
    else:
        print("[+] All guns have critical fields (name, caliber_mm)")
    print()

    # 3. Check HE/AP data completeness
    cursor.execute("""
        SELECT name, caliber_mm, he_dice, ap_0_10
        FROM bg_reference_guns
        WHERE nation LIKE '%british%'
          AND he_dice IS NULL
          AND he_0_10 IS NULL
          AND ap_0_10 IS NULL
    """)
    no_weapon_data = cursor.fetchall()
    if no_weapon_data:
        print("[!] WARNING: Guns with NO HE or AP data:")
        for row in no_weapon_data:
            print(f"    - {row[0]} (caliber: {row[1]})")
    else:
        print("[+] All guns have HE or AP data")
    print()

    # 4. Check ROF field population
    cursor.execute("""
        SELECT COUNT(*)
        FROM bg_reference_guns
        WHERE nation LIKE '%british%' AND rof IS NOT NULL
    """)
    rof_count = cursor.fetchone()[0]
    print(f"[*] Guns with ROF populated: {rof_count} of {british_count}")
    print()

    # 5. Check special cases
    print("[*] Checking special cases:")

    # Littlejohn Adaptor
    cursor.execute("""
        SELECT name, ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50
        FROM bg_reference_guns
        WHERE name LIKE '%Littlejohn%'
    """)
    littlejohn = cursor.fetchone()
    if littlejohn:
        print(f"    [+] Littlejohn Adaptor: {littlejohn[0]}")
        print(f"        AP values: {littlejohn[1]}, {littlejohn[2]}, {littlejohn[3]}, {littlejohn[4]}, {littlejohn[5]}")
    else:
        print("    [!] Littlejohn Adaptor: NOT FOUND")

    # Flamethrower (D6 variable damage)
    cursor.execute("""
        SELECT name, he_0_10, he_dice, caliber_mm
        FROM bg_reference_guns
        WHERE name LIKE '%Flamethrower%'
    """)
    flamethrower = cursor.fetchone()
    if flamethrower:
        print(f"    [+] Flamethrower: {flamethrower[0]}")
        print(f"        HE 0-10: {flamethrower[1]}, HE dice: {flamethrower[2]}, Caliber: {flamethrower[3]}")
    else:
        print("    [!] Flamethrower: NOT FOUND")

    # Boys AT Rifle
    cursor.execute("""
        SELECT name, caliber_mm, ap_0_10, ap_10_20
        FROM bg_reference_guns
        WHERE name LIKE '%Boys%'
    """)
    boys = cursor.fetchone()
    if boys:
        print(f"    [+] Boys AT Rifle: {boys[0]}")
        print(f"        Caliber: {boys[1]}mm, AP: {boys[2]}, {boys[3]}")
    else:
        print("    [!] Boys AT Rifle: NOT FOUND")

    # Bombs (should have HE only, no AP)
    cursor.execute("""
        SELECT name, he_0_10, ap_0_10
        FROM bg_reference_guns
        WHERE name LIKE '%bomb%'
    """)
    bombs = cursor.fetchall()
    print(f"    [+] Bombs found: {len(bombs)}")
    for bomb in bombs:
        print(f"        {bomb[0]}: HE={bomb[1]}, AP={bomb[2]}")

    print()

    # 6. Check gun_name_variants
    cursor.execute("""
        SELECT COUNT(DISTINCT g.id)
        FROM bg_reference_guns g
        JOIN gun_name_variants v ON g.id = v.gun_id
        WHERE g.nation LIKE '%british%'
    """)
    guns_with_variants = cursor.fetchone()[0]
    print(f"[*] British guns with name variants: {guns_with_variants} of {british_count}")

    # Show sample variants
    cursor.execute("""
        SELECT g.name, GROUP_CONCAT(v.variant_name, ', ') as variants
        FROM bg_reference_guns g
        JOIN gun_name_variants v ON g.id = v.gun_id
        WHERE g.nation LIKE '%british%'
        GROUP BY g.id
        ORDER BY g.id DESC
        LIMIT 8
    """)
    print()
    print("Sample gun name variants:")
    for row in cursor.fetchall():
        print(f"  {row[0]:30s} -> {row[1]}")
    print()

    # 7. Multi-nation guns (Canadian + British)
    cursor.execute("""
        SELECT name, nation
        FROM bg_reference_guns
        WHERE nation LIKE '%,%'
        ORDER BY name
    """)
    multi_nation = cursor.fetchall()
    print(f"[*] Multi-nation guns: {len(multi_nation)}")
    for row in multi_nation:
        print(f"    {row[0]:30s} -> {row[1]}")
    print()

    # 8. Import metadata
    cursor.execute("""
        SELECT COUNT(*)
        FROM bg_reference_guns
        WHERE nation LIKE '%british%' AND import_date IS NOT NULL
    """)
    with_import_date = cursor.fetchone()[0]
    print(f"[*] Guns with import_date metadata: {with_import_date} of {british_count}")
    print()

    # 9. Final summary
    print("="*80)
    print("VALIDATION SUMMARY")
    print("="*80)

    issues = []
    if british_count != 23:
        issues.append(f"Gun count mismatch: {british_count} (expected 23)")
    if missing_critical:
        issues.append(f"{len(missing_critical)} guns missing critical fields")
    if no_weapon_data:
        issues.append(f"{len(no_weapon_data)} guns have no HE/AP data")

    if issues:
        print("[!] ISSUES FOUND:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("[+] ALL VALIDATIONS PASSED")

    print()
    print(f"Total guns in database: {cursor.execute('SELECT COUNT(*) FROM bg_reference_guns').fetchone()[0]}")
    print(f"Total gun name variants: {cursor.execute('SELECT COUNT(*) FROM gun_name_variants').fetchone()[0]}")

    conn.close()

if __name__ == '__main__':
    main()
