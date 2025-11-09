#!/usr/bin/env python3
"""
Update soft-skin vehicle armor stats to 'SS' (Soft-Skin designation)
- Processes vehicles flagged with "Update all armor stats to SS" in linkage review
- Updates armor_front, armor_side, armor_rear to 'SS'
- Creates audit log of changes
"""
import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
INPUT_CSV = Path(__file__).parent.parent.parent.parent / "manual_vehicle_linkage_review.csv"
ARMOR_LOG = Path(__file__).parent.parent.parent.parent / "armor_update_log.txt"

def update_softskin_armor():
    print("=" * 80)
    print("UPDATING SOFT-SKIN VEHICLE ARMOR STATS")
    print("=" * 80)

    # Read CSV to find vehicles needing armor updates
    print(f"\nScanning: {INPUT_CSV}")
    armor_update_vehicles = []

    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            manual_id = row['manual_id']
            manual_name = row['manual_name']
            notes = row['NOTES'].strip()

            if 'Update all armor stats to SS' in notes:
                armor_update_vehicles.append({
                    'manual_id': int(manual_id),
                    'manual_name': manual_name,
                    'current_armor': row['manual_armor_f_s_r']
                })

    print(f"Found {len(armor_update_vehicles)} vehicles needing armor updates")

    if not armor_update_vehicles:
        print("\nNo vehicles need armor updates!")
        return

    # Connect to database
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Process updates
    print("\nUpdating armor values to 'SS'...")
    log_lines = []
    log_lines.append("=" * 80)
    log_lines.append("SOFT-SKIN ARMOR UPDATE LOG")
    log_lines.append("=" * 80)
    log_lines.append(f"\nTotal vehicles updated: {len(armor_update_vehicles)}")
    log_lines.append("\n" + "=" * 80)
    log_lines.append("ARMOR UPDATES")
    log_lines.append("=" * 80)
    log_lines.append("\nFormat: [ID] Vehicle Name (Nation) - Before -> After\n")

    updated = 0

    for vehicle in armor_update_vehicles:
        manual_id = vehicle['manual_id']

        # Get current armor values
        cursor.execute("""
            SELECT name, nation, armor_front, armor_side, armor_rear
            FROM bg_reference_vehicles
            WHERE id = ?
        """, (manual_id,))
        result = cursor.fetchone()

        if not result:
            print(f"WARNING: Vehicle ID {manual_id} not found")
            continue

        before = f"{result['armor_front'] or '?'}/{result['armor_side'] or '?'}/{result['armor_rear'] or '?'}"

        # Update armor to 'SS'
        cursor.execute("""
            UPDATE bg_reference_vehicles
            SET armor_front = 'SS',
                armor_side = 'SS',
                armor_rear = 'SS'
            WHERE id = ?
        """, (manual_id,))

        after = "SS/SS/SS"
        nation = result['nation'] or 'unknown'

        log_msg = f"[{manual_id:3d}] {result['name']:40s} ({nation:10s}) - {before:15s} -> {after}"
        print(f"  {log_msg}")
        log_lines.append(log_msg)

        updated += 1

    # Commit changes
    conn.commit()

    # Get statistics
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN armor_front = 'SS' AND armor_side = 'SS' AND armor_rear = 'SS' THEN 1 ELSE 0 END) as softskin_count
        FROM bg_reference_vehicles
    """)
    stats = cursor.fetchone()

    conn.close()

    # Add statistics to log
    log_lines.append("\n" + "=" * 80)
    log_lines.append("STATISTICS")
    log_lines.append("=" * 80)
    log_lines.append(f"\nVehicles updated to SS: {updated}")
    log_lines.append(f"Total soft-skin vehicles in database: {stats['softskin_count']}")
    log_lines.append(f"Total vehicles: {stats['total']}")
    log_lines.append(f"Soft-skin percentage: {stats['softskin_count']/stats['total']*100:.1f}%")

    # Write log file
    print(f"\nWriting armor update log: {ARMOR_LOG}")
    with open(ARMOR_LOG, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))

    print("\n" + "=" * 80)
    print("ARMOR UPDATE COMPLETE")
    print("=" * 80)
    print(f"\nUpdated: {updated} vehicles")
    print(f"Total soft-skin vehicles: {stats['softskin_count']}")
    print(f"\nGenerated Log:")
    print(f"  {ARMOR_LOG}")

if __name__ == '__main__':
    update_softskin_armor()
