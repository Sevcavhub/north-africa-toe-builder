#!/usr/bin/env python3
"""
Audit Scraped Canadian and German Data

Compare scraped data from Crucible PDF against British manual entry standards.

Checks:
1. Canadian vehicles (64 vehicles)
2. Canadian guns (26 guns)
3. German vehicles (if any)
4. German guns (16 guns)

Standards from British manual entry:
- Armor values (front, side, rear, top)
- Movement values (slow/fast)
- Weapons field populated
- Points cost, Battle Rating
- Special rules
- HE/AP range data (guns)
- ROF field (guns)
- Caliber_mm (guns)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def audit_vehicles(cursor, nation):
    """Audit vehicle data completeness."""
    print(f"\n{'='*80}")
    print(f"{nation.upper()} VEHICLES AUDIT")
    print(f"{'='*80}\n")

    # Count total
    cursor.execute(f"SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation LIKE '%{nation}%'")
    total = cursor.fetchone()[0]
    print(f"[*] Total {nation} vehicles: {total}\n")

    # Check critical fields (using actual column names)
    checks = {
        'armor_front': 'Armor front',
        'armor_side': 'Armor side',
        'armor_rear': 'Armor rear',
        'off_road_inches': 'Movement (off-road)',
        'road_inches': 'Movement (road)',
        'weapons': 'Weapons',
        'vehicle_type': 'Vehicle type'
    }

    for field, label in checks.items():
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM bg_reference_vehicles
            WHERE nation LIKE '%{nation}%' AND {field} IS NULL
        """)
        missing = cursor.fetchone()[0]
        pct = (total - missing) / total * 100 if total > 0 else 0
        status = "+" if missing == 0 else "!" if missing < total * 0.1 else "X"
        print(f"  [{status}] {label:20s}: {total - missing:3d}/{total} ({pct:5.1f}%) - {missing} missing")

    # Check special rules
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM bg_reference_vehicles
        WHERE nation LIKE '%{nation}%' AND special_movement IS NOT NULL
    """)
    with_special = cursor.fetchone()[0]
    print(f"\n  [i] Special rules populated: {with_special}/{total}")

    # Sample vehicles with missing data
    cursor.execute(f"""
        SELECT name, armor_front, armor_side, off_road_inches, road_inches, weapons, vehicle_type
        FROM bg_reference_vehicles
        WHERE nation LIKE '%{nation}%'
          AND (armor_front IS NULL
           OR armor_side IS NULL
           OR off_road_inches IS NULL
           OR weapons IS NULL
           OR vehicle_type IS NULL)
        LIMIT 10
    """)

    missing_data = cursor.fetchall()
    if missing_data:
        print(f"\n  [!] Sample vehicles with missing data:")
        for row in missing_data:
            issues = []
            if row[1] is None or row[1] == 'None': issues.append("armor")
            if row[3] is None: issues.append("movement")
            if row[5] is None or row[5] == 'None': issues.append("weapons")
            if row[6] is None: issues.append("vehicle_type")
            print(f"      {row[0]:35s} - Missing: {', '.join(issues)}")

def audit_guns(cursor, nation):
    """Audit gun data completeness."""
    print(f"\n{'='*80}")
    print(f"{nation.upper()} GUNS AUDIT")
    print(f"{'='*80}\n")

    # Count total
    cursor.execute(f"SELECT COUNT(*) FROM bg_reference_guns WHERE nation LIKE '%{nation}%'")
    total = cursor.fetchone()[0]
    print(f"[*] Total {nation} guns: {total}\n")

    # Check critical fields
    checks = {
        'caliber_mm': 'Caliber (mm)',
        'he_dice': 'HE dice',
        'he_target': 'HE target',
        'he_0_10': 'HE 0-10"',
        'he_10_20': 'HE 10-20"',
        'ap_0_10': 'AP 0-10"',
        'ap_10_20': 'AP 10-20"',
        'rof': 'Rate of Fire',
        'he_shell_classification': 'HE shell class'
    }

    for field, label in checks.items():
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM bg_reference_guns
            WHERE nation LIKE '%{nation}%' AND {field} IS NULL
        """)
        missing = cursor.fetchone()[0]
        pct = (total - missing) / total * 100 if total > 0 else 0
        status = "+" if missing == 0 else "!" if missing < total * 0.3 else "X"
        print(f"  [{status}] {label:20s}: {total - missing:3d}/{total} ({pct:5.1f}%) - {missing} missing")

    # Check HE vs AP coverage
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM bg_reference_guns
        WHERE nation LIKE '%{nation}%'
          AND (he_dice IS NOT NULL OR he_0_10 IS NOT NULL)
    """)
    with_he = cursor.fetchone()[0]

    cursor.execute(f"""
        SELECT COUNT(*)
        FROM bg_reference_guns
        WHERE nation LIKE '%{nation}%'
          AND ap_0_10 IS NOT NULL
    """)
    with_ap = cursor.fetchone()[0]

    print(f"\n  [i] Guns with HE data: {with_he}/{total} ({with_he/total*100:.1f}%)")
    print(f"  [i] Guns with AP data: {with_ap}/{total} ({with_ap/total*100:.1f}%)")

    # Sample guns with missing data
    cursor.execute(f"""
        SELECT name, caliber_mm, he_dice, he_0_10, ap_0_10, rof, he_shell_classification
        FROM bg_reference_guns
        WHERE nation LIKE '%{nation}%'
        ORDER BY name
    """)

    all_guns = cursor.fetchall()
    print(f"\n  [*] All {nation} guns:")
    for row in all_guns:
        issues = []
        if row[1] is None: issues.append("caliber")
        if row[2] is None and row[3] is None: issues.append("HE")
        if row[4] is None: issues.append("AP")
        if row[5] is None: issues.append("ROF")
        if row[6] is None: issues.append("HE_class")

        status = "+" if not issues else "!"
        issue_str = f" - Missing: {', '.join(issues)}" if issues else ""
        print(f"      [{status}] {row[0]:35s}{issue_str}")

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*80)
    print("SCRAPED DATA AUDIT REPORT")
    print("Comparing Canadian/German data vs British manual entry standards")
    print("="*80)

    # Audit Canadian data
    audit_vehicles(cursor, 'canadian')
    audit_guns(cursor, 'canadian')

    # Audit German data
    audit_vehicles(cursor, 'german')
    audit_guns(cursor, 'german')

    # Summary comparison
    print(f"\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}\n")

    # Compare against British standards
    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation LIKE '%british%'")
    british_vehicles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE nation LIKE '%british%'")
    british_guns = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation LIKE '%canadian%'")
    canadian_vehicles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE nation LIKE '%canadian%'")
    canadian_guns = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation LIKE '%german%'")
    german_vehicles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE nation LIKE '%german%'")
    german_guns = cursor.fetchone()[0]

    print("Nation Totals:")
    print(f"  British:  {british_vehicles:3d} vehicles, {british_guns:2d} guns (MANUAL ENTRY - baseline)")
    print(f"  Canadian: {canadian_vehicles:3d} vehicles, {canadian_guns:2d} guns (SCRAPED - needs review)")
    print(f"  German:   {german_vehicles:3d} vehicles, {german_guns:2d} guns (SCRAPED - needs review)")

    print("\nKey Differences to Investigate:")
    print("  1. British has ROF data (manual entry), Canadian/German may be missing")
    print("  2. British has HE shell classification, Canadian/German may be missing")
    print("  3. British has all HE range bands (he_0_10 through he_50_70)")
    print("  4. British has import_date metadata")
    print("  5. Verify special cases: Flamethrowers, Bombs, Rockets handled correctly")

    conn.close()

if __name__ == '__main__':
    main()
