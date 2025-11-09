#!/usr/bin/env python3
"""
Import approved manual linkages from CSV back to database
- Reads manual_vehicle_linkage_review.csv
- Updates bg_reference_vehicles.bg_builder_id based on APPROVED_bg_id column
- Validates linkages before applying
"""
import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
INPUT_CSV = Path(__file__).parent.parent.parent.parent / "manual_vehicle_linkage_review.csv"

def import_approved_linkages():
    print("Importing Approved Manual Linkages")
    print("=" * 80)

    if not INPUT_CSV.exists():
        print(f"ERROR: CSV file not found: {INPUT_CSV}")
        print("Run create_manual_linkage_interface.py first!")
        return

    # Read CSV
    print(f"Reading: {INPUT_CSV}")
    approved_linkages = []

    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            manual_id = row['manual_id']
            approved_bg_id = row['APPROVED_bg_id'].strip()
            notes = row['NOTES'].strip()

            if approved_bg_id:
                try:
                    approved_linkages.append({
                        'manual_id': int(manual_id),
                        'bg_builder_id': int(approved_bg_id),
                        'notes': notes
                    })
                except ValueError:
                    print(f"WARNING: Invalid bg_id for manual_id {manual_id}: '{approved_bg_id}'")

    print(f"Found {len(approved_linkages)} approved linkages")

    if not approved_linkages:
        print("\nNo approved linkages found in CSV!")
        print("Make sure you filled in the APPROVED_bg_id column.")
        return

    # Connect to database
    conn = sqlite3.connect(DB_PATH, timeout=60)
    cursor = conn.cursor()

    # Validate all approved linkages first
    print("\nValidating linkages...")
    valid_linkages = []
    invalid_count = 0

    for linkage in approved_linkages:
        manual_id = linkage['manual_id']
        bg_builder_id = linkage['bg_builder_id']

        # Check manual vehicle exists
        cursor.execute("SELECT name FROM bg_reference_vehicles WHERE id = ?", (manual_id,))
        manual_result = cursor.fetchone()
        if not manual_result:
            print(f"ERROR: Manual vehicle ID {manual_id} not found")
            invalid_count += 1
            continue

        # Check BG Builder vehicle exists
        cursor.execute("SELECT name FROM bg_builder_vehicles WHERE id = ?", (bg_builder_id,))
        bg_result = cursor.fetchone()
        if not bg_result:
            print(f"ERROR: BG Builder vehicle ID {bg_builder_id} not found (manual: {manual_result[0]})")
            invalid_count += 1
            continue

        valid_linkages.append({
            'manual_id': manual_id,
            'manual_name': manual_result[0],
            'bg_builder_id': bg_builder_id,
            'bg_builder_name': bg_result[0],
            'notes': linkage['notes']
        })

    print(f"Valid linkages: {len(valid_linkages)}")
    print(f"Invalid linkages: {invalid_count}")

    if not valid_linkages:
        print("\nNo valid linkages to import!")
        conn.close()
        return

    # Apply linkages
    print("\nApplying linkages to database...")
    updated = 0

    for linkage in valid_linkages:
        cursor.execute("""
            UPDATE bg_reference_vehicles
            SET bg_builder_id = ?
            WHERE id = ?
        """, (linkage['bg_builder_id'], linkage['manual_id']))

        print(f"  [{linkage['manual_id']:3d}] {linkage['manual_name']:40s} → [{linkage['bg_builder_id']:3d}] {linkage['bg_builder_name']}")
        if linkage['notes']:
            print(f"       Note: {linkage['notes']}")

        updated += 1

    # Commit changes
    conn.commit()

    # Show statistics
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT CASE WHEN bg_builder_id IS NOT NULL THEN id END) as linked
        FROM bg_reference_vehicles
    """)
    stats = cursor.fetchone()
    total = stats[0]
    linked = stats[1]
    linkage_rate = (linked / total * 100) if total > 0 else 0

    conn.close()

    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"\nUpdated: {updated} linkages")
    print(f"\nFinal Statistics:")
    print(f"  Total manual vehicles: {total}")
    print(f"  Linked to BG Builder: {linked}")
    print(f"  Linkage rate: {linkage_rate:.1f}%")
    print(f"  Unlinked vehicles: {total - linked}")

if __name__ == '__main__':
    import_approved_linkages()
