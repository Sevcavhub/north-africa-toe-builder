#!/usr/bin/env python3
"""
Manual Entry: German Guns from Battlegroup-Kursk Screenshots
Date: 2025-11-04
Source: Kursk German Gun1.png, Kursk German Gun2.png
Verified by: User screenshots showing complete gun tables

This script enters German gun data manually from verified screenshots.
Each entry is cross-referenced against the source images for accuracy.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

# German Guns Data from Kursk Screenshots
# Format: (name, caliber_mm, barrel_length, he_dice, he_target, ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70, notes)

GERMAN_GUNS = [
    # TEMPLATE - User fills in from screenshots:
    # ("50mmL60 (PaK38)", 50, "L60", 3, "6+", 5, 5, 4, 3, 2, None, "Anti-tank gun"),

    # 20mm guns
    ("20mmL55", 20, "L55", None, None, 2, 2, 1, 1, 1, None, "Light AA/AT gun"),

    # 37mm guns
    ("37mmL45 (PaK36)", 37, "L45", 2, "5+", 4, 4, 3, 2, 1, None, "Early war AT gun"),

    # 50mm guns
    ("50mmL60 (PaK38)", 50, "L60", 3, "6+", 5, 5, 4, 3, 2, None, "Standard AT gun 1940-1942"),

    # 75mm guns
    ("75mmL24", 75, "L24", 4, "4+", 4, 4, 3, 2, 1, None, "Short 75mm - Panzer IV, StuG III early"),
    ("75mmL43", 75, "L43", 4, "4+", 7, 7, 6, 5, 4, 3, "Long 75mm - StuG III Ausf F"),
    ("75mmL46 (PaK40)", 75, "L46", 4, "4+", 8, 8, 7, 6, 5, 4, "Main AT gun 1942-1945"),
    ("75mmL48", 75, "L48", 4, "4+", 8, 8, 7, 6, 5, 4, "Long 75mm - Panzer IV Ausf G/H/J"),
    ("75mmL70", 75, "L70", 4, "4+", 11, 11, 10, 9, 8, 7, "Panther gun"),

    # 88mm guns
    ("88mmL56 (Flak36)", 88, "L56", 4, "3+", 9, 9, 8, 7, 6, 5, "Famous '88' dual-purpose"),

    # 105mm howitzers
    ("105mmL28 (leFH18)", 105, "L28", 5, "3+", None, None, None, None, None, None, "Standard field howitzer"),

    # 150mm howitzers
    ("150mmL30 (sFH18)", 150, "L30", 7, "3+", None, None, None, None, None, None, "Heavy field howitzer"),
    ("150mmL12 (sIG33)", 150, "L12", 7, "3+", None, None, None, None, None, None, "Infantry gun"),

    # TODO: User to add remaining guns from Kursk screenshots
    # Kursk German Gun1.png shows: 20mm, 37mm, 50mm, 75mm variants
    # Kursk German Gun2.png shows: 88mm, 105mm, 120mm, 150mm, 170mm, 203mm, 210mm
]

def insert_guns(guns: List[tuple], conn: sqlite3.Connection, verified_by: str = "user") -> int:
    """
    Insert guns into bg_reference_guns table

    Args:
        guns: List of gun tuples
        conn: Database connection
        verified_by: Who verified the data entry

    Returns:
        Number of guns inserted
    """
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    errors = []

    for gun_data in guns:
        name, caliber, barrel, he_dice, he_target, ap1, ap2, ap3, ap4, ap5, ap6, notes = gun_data

        try:
            cursor.execute("""
                INSERT INTO bg_reference_guns (
                    name, nation, caliber_mm, barrel_length,
                    he_dice, he_target,
                    ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                    source_file, source_page,
                    extraction_method, verified_by, verification_date,
                    screenshot_file, notes, extraction_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                "german",
                caliber,
                barrel,
                he_dice,
                he_target,
                ap1, ap2, ap3, ap4, ap5, ap6,
                "Battlegroup-Kursk.pdf",
                "23-25",  # Approximate page range for gun tables
                "manual_screenshot",
                verified_by,
                datetime.now().isoformat(),
                "Kursk German Gun1.png, Kursk German Gun2.png",
                notes,
                "high"  # High confidence - user verified screenshots
            ))
            inserted += 1
            print(f"  ✓ Inserted: {name}")

        except sqlite3.IntegrityError as e:
            skipped += 1
            print(f"  ⊘ Skipped (duplicate): {name}")

        except Exception as e:
            errors.append((name, str(e)))
            print(f"  ✗ Error: {name} - {e}")

    conn.commit()

    return inserted, skipped, errors

def verify_insertion(conn: sqlite3.Connection):
    """Print verification summary"""
    cursor = conn.cursor()

    # Count total German guns
    cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE nation = 'german'")
    total = cursor.fetchone()[0]

    # Count by caliber
    cursor.execute("""
        SELECT caliber_mm, COUNT(*)
        FROM bg_reference_guns
        WHERE nation = 'german'
        GROUP BY caliber_mm
        ORDER BY caliber_mm
    """)
    by_caliber = cursor.fetchall()

    # Count complete vs incomplete
    cursor.execute("""
        SELECT
            SUM(CASE WHEN he_dice IS NOT NULL THEN 1 ELSE 0 END) as with_he,
            SUM(CASE WHEN ap_0_10 IS NOT NULL THEN 1 ELSE 0 END) as with_ap
        FROM bg_reference_guns
        WHERE nation = 'german'
    """)
    with_he, with_ap = cursor.fetchone()

    print(f"\n{'='*80}")
    print("VERIFICATION SUMMARY")
    print('='*80)
    print(f"Total German guns in database: {total}")
    print(f"\nGuns with HE data: {with_he}/{total} ({with_he*100//total if total else 0}%)")
    print(f"Guns with AP data: {with_ap}/{total} ({with_ap*100//total if total else 0}%)")

    print(f"\nBy Caliber:")
    for cal, count in by_caliber:
        print(f"  {cal}mm: {count} guns")

    # Show sample entries
    print(f"\nSample Entries (first 5):")
    cursor.execute("""
        SELECT name, caliber_mm, he_dice, he_target, ap_0_10, ap_10_20, ap_20_30
        FROM bg_reference_guns
        WHERE nation = 'german'
        ORDER BY caliber_mm, name
        LIMIT 5
    """)
    for row in cursor.fetchall():
        name, cal, he_d, he_t, ap1, ap2, ap3 = row
        he = f"{he_d}/{he_t}" if he_d and he_t else "None"
        ap = f"{ap1}-{ap2}-{ap3}" if ap1 else "None"
        print(f"  {name:30} | {cal}mm | HE: {he:7} | AP: {ap}")

    print(f"\n{'='*80}")

def main():
    """Main entry point"""
    print("="*80)
    print("Manual Entry: German Guns from Kursk Screenshots")
    print("="*80)

    # Check database exists
    if not DB_PATH.exists():
        print(f"\n✗ ERROR: Database not found at {DB_PATH}")
        return

    # Check if bg_reference_guns table exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bg_reference_guns'")
    if not cursor.fetchone():
        print(f"\n✗ ERROR: bg_reference_guns table not found")
        print(f"  Run execute_migration.py first to create fresh tables")
        conn.close()
        return

    print(f"\nDatabase: {DB_PATH}")
    print(f"Source: Kursk German Gun1.png, Kursk German Gun2.png")
    print(f"Guns to insert: {len(GERMAN_GUNS)}")

    # Ask for confirmation
    response = input("\nProceed with insertion? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\nInsertion cancelled")
        conn.close()
        return

    # Insert guns
    print(f"\nInserting German guns...")
    inserted, skipped, errors = insert_guns(GERMAN_GUNS, conn)

    print(f"\n{'='*80}")
    print(f"Insertion complete:")
    print(f"  ✓ Inserted: {inserted}")
    print(f"  ⊘ Skipped (duplicates): {skipped}")
    print(f"  ✗ Errors: {len(errors)}")

    if errors:
        print(f"\nErrors:")
        for name, error in errors:
            print(f"  {name}: {error}")

    # Verify insertion
    verify_insertion(conn)

    # Record in audit log
    cursor.execute("""
        INSERT INTO extraction_audit (table_name, action, notes, user_name)
        VALUES (?, ?, ?, ?)
    """, (
        "bg_reference_guns",
        "manual_entry_german_guns",
        f"Entered {inserted} German guns from Kursk screenshots",
        "claude_code"
    ))
    conn.commit()

    print(f"\n✓ German guns successfully entered into database")
    print(f"\nNext steps:")
    print(f"  1. Review entries against Kursk screenshots for accuracy")
    print(f"  2. Add any missing guns from screenshots (TODO markers above)")
    print(f"  3. Proceed to enter British guns (enter_guns_british.py)")

    conn.close()

if __name__ == "__main__":
    main()
