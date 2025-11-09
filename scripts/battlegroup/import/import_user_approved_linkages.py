#!/usr/bin/env python3
"""
Import user-approved manual linkages from CSV
- Handles "No match" decisions (skips, doesn't error)
- Imports only numeric bg_id values
- Generates detailed reports with user notes
- Creates no-match report for alternative sourcing
"""
import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
INPUT_CSV = Path(__file__).parent.parent.parent.parent / "manual_vehicle_linkage_review.csv"
IMPORT_LOG = Path(__file__).parent.parent.parent.parent / "linkage_import_log.txt"
NO_MATCH_REPORT = Path(__file__).parent.parent.parent.parent / "linkage_no_match_report.csv"

def import_approved_linkages():
    print("=" * 80)
    print("IMPORTING USER-APPROVED MANUAL LINKAGES")
    print("=" * 80)

    if not INPUT_CSV.exists():
        print(f"ERROR: CSV file not found: {INPUT_CSV}")
        return

    # Read CSV
    print(f"\nReading: {INPUT_CSV}")
    approved_linkages = []
    no_match_vehicles = []
    armor_update_vehicles = []
    skipped_rows = []

    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            manual_id = row['manual_id']
            manual_name = row['manual_name']
            approved_bg_id = row['APPROVED_bg_id'].strip()
            notes = row['NOTES'].strip()

            # Check for armor update action item
            if 'Update all armor stats to SS' in notes:
                armor_update_vehicles.append({
                    'manual_id': int(manual_id),
                    'manual_name': manual_name,
                    'notes': notes
                })

            # Handle different approval statuses
            if not approved_bg_id:
                skipped_rows.append({
                    'row': row_num,
                    'manual_id': manual_id,
                    'manual_name': manual_name,
                    'reason': 'Blank APPROVED_bg_id',
                    'notes': notes
                })
            elif approved_bg_id.lower() in ['no match', 'no match,']:
                no_match_vehicles.append({
                    'manual_id': manual_id,
                    'manual_name': manual_name,
                    'armor': row['manual_armor_f_s_r'],
                    'movement': row['manual_movement'],
                    'weapon1': row['manual_weapon1'],
                    'nation': row['manual_nation'],
                    'source': row['manual_source'],
                    'notes': notes,
                    'suggested_1': f"{row['SUGGESTED_bg_name_1']} (ID: {row['SUGGESTED_bg_id_1']}, {row['similarity_1']})"
                })
            else:
                try:
                    bg_id = int(approved_bg_id)
                    approved_linkages.append({
                        'manual_id': int(manual_id),
                        'manual_name': manual_name,
                        'bg_builder_id': bg_id,
                        'notes': notes
                    })
                except ValueError:
                    skipped_rows.append({
                        'row': row_num,
                        'manual_id': manual_id,
                        'manual_name': manual_name,
                        'reason': f'Invalid bg_id: {approved_bg_id}',
                        'notes': notes
                    })

    print(f"\nCategorization Results:")
    print(f"  Approved linkages: {len(approved_linkages)}")
    print(f"  'No match' decisions: {len(no_match_vehicles)}")
    print(f"  Armor update actions: {len(armor_update_vehicles)}")
    print(f"  Skipped rows: {len(skipped_rows)}")

    # Write no-match report
    print(f"\nGenerating no-match report: {NO_MATCH_REPORT}")
    with open(NO_MATCH_REPORT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'manual_id', 'manual_name', 'armor_f_s_r', 'movement', 'weapon1',
            'nation', 'source', 'notes', 'suggested_match'
        ])
        for vehicle in no_match_vehicles:
            writer.writerow([
                vehicle['manual_id'], vehicle['manual_name'], vehicle['armor'],
                vehicle['movement'], vehicle['weapon1'], vehicle['nation'],
                vehicle['source'], vehicle['notes'], vehicle['suggested_1']
            ])

    if not approved_linkages:
        print("\nNo approved linkages to import!")
        return

    # Connect to database
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Validate all approved linkages
    print("\nValidating approved linkages...")
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
            print(f"ERROR: BG Builder vehicle ID {bg_builder_id} not found (manual: {manual_result['name']})")
            invalid_count += 1
            continue

        valid_linkages.append({
            'manual_id': manual_id,
            'manual_name': manual_result['name'],
            'bg_builder_id': bg_builder_id,
            'bg_builder_name': bg_result['name'],
            'notes': linkage['notes']
        })

    print(f"Valid linkages: {len(valid_linkages)}")
    print(f"Invalid linkages: {invalid_count}")

    if not valid_linkages:
        print("\nNo valid linkages to import!")
        conn.close()
        return

    # Get current linkage state
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT CASE WHEN bg_builder_id IS NOT NULL THEN id END) as linked_before
        FROM bg_reference_vehicles
    """)
    stats_before = cursor.fetchone()

    # Apply linkages
    print("\nApplying linkages to database...")
    updated = 0

    log_lines = []
    log_lines.append("=" * 80)
    log_lines.append("LINKAGE IMPORT LOG")
    log_lines.append("=" * 80)
    log_lines.append(f"\nImport Date: {Path(__file__).stat().st_mtime}")
    log_lines.append(f"Total Vehicles Reviewed: {len(approved_linkages) + len(no_match_vehicles) + len(skipped_rows)}")
    log_lines.append(f"Approved Linkages: {len(valid_linkages)}")
    log_lines.append(f"'No Match' Decisions: {len(no_match_vehicles)}")
    log_lines.append(f"Skipped Rows: {len(skipped_rows)}")
    log_lines.append("\n" + "=" * 80)
    log_lines.append("APPROVED LINKAGES (APPLIED)")
    log_lines.append("=" * 80)

    for linkage in valid_linkages:
        # Get current linkage if exists
        cursor.execute("SELECT bg_builder_id FROM bg_reference_vehicles WHERE id = ?", (linkage['manual_id'],))
        current = cursor.fetchone()
        old_bg_id = current['bg_builder_id'] if current and current['bg_builder_id'] else None

        # Update linkage
        cursor.execute("""
            UPDATE bg_reference_vehicles
            SET bg_builder_id = ?
            WHERE id = ?
        """, (linkage['bg_builder_id'], linkage['manual_id']))

        log_msg = f"[{linkage['manual_id']:3d}] {linkage['manual_name']:40s} -> [{linkage['bg_builder_id']:3d}] {linkage['bg_builder_name']}"

        if old_bg_id and old_bg_id != linkage['bg_builder_id']:
            log_msg += f" (was: {old_bg_id})"

        print(f"  {log_msg}")
        log_lines.append(log_msg)

        if linkage['notes']:
            note_msg = f"       Note: {linkage['notes']}"
            print(note_msg)
            log_lines.append(note_msg)

        updated += 1

    # Commit changes
    conn.commit()

    # Get final statistics
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT CASE WHEN bg_builder_id IS NOT NULL THEN id END) as linked_after
        FROM bg_reference_vehicles
    """)
    stats_after = cursor.fetchone()

    conn.close()

    # Add statistics to log
    log_lines.append("\n" + "=" * 80)
    log_lines.append("STATISTICS")
    log_lines.append("=" * 80)
    log_lines.append(f"\nBefore Import:")
    log_lines.append(f"  Total manual vehicles: {stats_before['total']}")
    log_lines.append(f"  Linked to BG Builder: {stats_before['linked_before']}")
    log_lines.append(f"  Linkage rate: {stats_before['linked_before']/stats_before['total']*100:.1f}%")
    log_lines.append(f"\nAfter Import:")
    log_lines.append(f"  Total manual vehicles: {stats_after['total']}")
    log_lines.append(f"  Linked to BG Builder: {stats_after['linked_after']}")
    log_lines.append(f"  Linkage rate: {stats_after['linked_after']/stats_after['total']*100:.1f}%")
    log_lines.append(f"\nChange:")
    log_lines.append(f"  New linkages: +{stats_after['linked_after'] - stats_before['linked_before']}")
    log_lines.append(f"  Unlinked vehicles: {stats_after['total'] - stats_after['linked_after']}")

    # Add no-match summary
    log_lines.append("\n" + "=" * 80)
    log_lines.append("'NO MATCH' DECISIONS (NOT LINKED)")
    log_lines.append("=" * 80)
    log_lines.append(f"\nTotal: {len(no_match_vehicles)} vehicles")
    log_lines.append("\nBreakdown by category (based on notes):")

    # Categorize no-match vehicles
    categories = {
        'Variant issues': [],
        'Not in North Africa': [],
        'BG Builder dataset gaps': [],
        'Weapon data needed': [],
        'Other': []
    }

    for vehicle in no_match_vehicles:
        notes_lower = vehicle['notes'].lower()
        if 'same stats' in notes_lower or 'variant' in notes_lower:
            categories['Variant issues'].append(vehicle)
        elif 'not in africa' in notes_lower:
            categories['Not in North Africa'].append(vehicle)
        elif 'bg builder' in notes_lower or 'should match' in notes_lower or 'should be' in notes_lower:
            categories['BG Builder dataset gaps'].append(vehicle)
        elif 'need' in notes_lower and 'gun' in notes_lower:
            categories['Weapon data needed'].append(vehicle)
        else:
            categories['Other'].append(vehicle)

    for category, vehicles in categories.items():
        if vehicles:
            log_lines.append(f"\n{category}: {len(vehicles)}")
            for v in vehicles:
                manual_id_str = str(v['manual_id'])
                log_lines.append(f"  [{manual_id_str:>3s}] {v['manual_name']:40s} - {v['notes']}")

    # Write log file
    print(f"\nWriting import log: {IMPORT_LOG}")
    with open(IMPORT_LOG, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))

    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"\nUpdated: {updated} linkages")
    print(f"\nFinal Statistics:")
    print(f"  Total manual vehicles: {stats_after['total']}")
    print(f"  Linked to BG Builder: {stats_after['linked_after']}")
    print(f"  Linkage rate: {stats_after['linked_after']/stats_after['total']*100:.1f}%")
    print(f"  Unlinked vehicles: {stats_after['total'] - stats_after['linked_after']}")
    print(f"\nGenerated Reports:")
    print(f"  {IMPORT_LOG}")
    print(f"  {NO_MATCH_REPORT}")
    print(f"\nNext Steps:")
    print(f"  - Review {NO_MATCH_REPORT} for alternative data sourcing")
    print(f"  - {len(armor_update_vehicles)} vehicles need armor stats updated to 'SS'")

if __name__ == '__main__':
    import_approved_linkages()
