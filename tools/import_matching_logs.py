#!/usr/bin/env python3
"""
Import Equipment Matching Logs into Database
Reads approved matches from JSON log files and updates equipment table.
"""

import json
import glob
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DATABASE_FILE = Path("database/master_database.db")
MATCHING_LOGS_DIR = Path("data/equipment_matching_logs")


def get_latest_log_per_nation():
    """Get the most recent matching log for each nation."""
    files = glob.glob(str(MATCHING_LOGS_DIR / "*_automated_matching_*.json"))

    # Group by nation
    by_nation = {}
    for f in files:
        data = json.load(open(f))
        nation = data.get('nation', 'unknown')

        # Use timestamp to find latest
        timestamp = data.get('timestamp', '')

        if nation not in by_nation or timestamp > by_nation[nation]['timestamp']:
            by_nation[nation] = {'file': f, 'timestamp': timestamp, 'data': data}

    return by_nation


def parse_match_from_reason(reason: str):
    """Extract match name from reason string.

    Examples:
        "AFV match: PzKpfw I Ausf. A (95%)" → "PzKpfw I Ausf. A"
        "Gun match: 8 cm 29M Anti Aircraft (score: 85%)" → "8 cm 29M Anti Aircraft"
        "AFV match: None (85%)" → None
    """
    if not reason or 'None' in reason:
        return None

    # Try AFV match pattern
    if 'AFV match:' in reason:
        parts = reason.split('AFV match:')[1].strip()
        # Remove confidence percentage
        match_name = parts.rsplit('(', 1)[0].strip()
        return match_name if match_name and match_name != 'None' else None

    # Try Gun match pattern
    if 'Gun match:' in reason:
        parts = reason.split('Gun match:')[1].strip()
        # Remove "(score: XX%)"
        match_name = parts.rsplit('(score:', 1)[0].strip() if '(score:' in parts else parts.rsplit('(', 1)[0].strip()
        return match_name if match_name and match_name != 'None' else None

    return None


def import_matches(conn):
    """Import approved matches from JSON logs into equipment table."""

    print("\n" + "=" * 70)
    print("IMPORTING EQUIPMENT MATCHING LOGS")
    print("=" * 70)

    # Get latest log per nation
    logs = get_latest_log_per_nation()

    print(f"\nFound matching logs for {len(logs)} nations:")
    for nation, info in logs.items():
        stats = info['data'].get('statistics', {})
        print(f"  {nation:10s}: {stats.get('approved', 0)} approved (from {Path(info['file']).name})")

    cursor = conn.cursor()

    total_updated = 0
    total_skipped = 0
    total_failed = 0

    for nation, info in logs.items():
        data = info['data']
        decisions = data.get('decisions', [])

        print(f"\nProcessing {nation} equipment ({len(decisions)} items)...")

        for decision in decisions:
            canonical_id = decision.get('canonical_id')
            item_name = decision.get('item')
            decision_status = decision.get('decision')
            reason = decision.get('reason', '')
            confidence = decision.get('confidence', 0)

            # Only process approved/auto-matched items
            if decision_status not in ['AUTO-APPROVED', 'AUTO-MATCHED', 'APPROVED']:
                total_skipped += 1
                continue

            try:
                # Check if equipment exists
                cursor.execute("SELECT canonical_id FROM equipment WHERE canonical_id = ?", (canonical_id,))
                if not cursor.fetchone():
                    print(f"  WARNING: Equipment not found in database: {canonical_id}")
                    total_skipped += 1
                    continue

                # Parse match from reason
                match_name = parse_match_from_reason(reason)

                if not match_name:
                    # AUTO-APPROVED soft-skin vehicles have no match data
                    total_skipped += 1
                    continue

                # Determine if it's OnWar or WWIITANKS match
                # (For now, we'll check if match exists in our source tables)
                cursor.execute("SELECT vehicle_name, url FROM afv_data WHERE vehicle_name LIKE ?", (f"%{match_name}%",))
                onwar_match = cursor.fetchone()

                cursor.execute("SELECT vehicle_name, wwiitanks_id FROM wwiitanks_afv_data WHERE vehicle_name LIKE ?", (f"%{match_name}%",))
                wwiitanks_match = cursor.fetchone()

                # Update equipment table
                if onwar_match:
                    cursor.execute("""
                        UPDATE equipment SET
                            onwar_matched = 1,
                            onwar_url = ?,
                            match_confidence = ?,
                            match_method = 'automated_matching_log',
                            updated_at = ?,
                            updated_by = ?
                        WHERE canonical_id = ?
                    """, (onwar_match[1], confidence, datetime.now().isoformat(), 'import_matching_logs.py', canonical_id))
                    total_updated += 1

                elif wwiitanks_match:
                    cursor.execute("""
                        UPDATE equipment SET
                            wwiitanks_matched = 1,
                            wwiitanks_id = ?,
                            match_confidence = ?,
                            match_method = 'automated_matching_log',
                            updated_at = ?,
                            updated_by = ?
                        WHERE canonical_id = ?
                    """, (wwiitanks_match[1], confidence, datetime.now().isoformat(), 'import_matching_logs.py', canonical_id))
                    total_updated += 1

                else:
                    # Match name in log but not found in source tables
                    # This could be guns or other equipment types
                    total_skipped += 1

            except Exception as e:
                print(f"  ERROR processing {canonical_id}: {e}")
                total_failed += 1

    conn.commit()

    print(f"\n[SUCCESS] Import complete")
    print(f"  Updated: {total_updated}")
    print(f"  Skipped: {total_skipped}")
    print(f"  Failed: {total_failed}")

    return {"updated": total_updated, "skipped": total_skipped, "failed": total_failed}


def verify_import(conn):
    """Verify equipment table now has matches."""

    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM equipment WHERE onwar_matched = 1")
    onwar_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM equipment WHERE wwiitanks_matched = 1")
    wwiitanks_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM equipment WHERE onwar_matched = 1 OR wwiitanks_matched = 1")
    total_matched = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM equipment")
    total_equipment = cursor.fetchone()[0]

    print(f"\nEquipment Matching Status:")
    print(f"  Total equipment: {total_equipment}")
    print(f"  OnWar matched: {onwar_count} ({onwar_count/total_equipment*100:.1f}%)")
    print(f"  WWIITANKS matched: {wwiitanks_count} ({wwiitanks_count/total_equipment*100:.1f}%)")
    print(f"  Either matched: {total_matched} ({total_matched/total_equipment*100:.1f}%)")

    # Sample matches
    print("\nSample matched equipment:")
    cursor.execute("""
        SELECT name, nation, onwar_url, wwiitanks_id
        FROM equipment
        WHERE (onwar_matched = 1 OR wwiitanks_matched = 1)
        LIMIT 10
    """)

    for row in cursor.fetchall():
        onwar = "Y" if row[2] else "N"
        wwiitanks = "Y" if row[3] else "N"
        print(f"  - {row[0]:35s} ({row[1]}): onwar={onwar}, wwiitanks={wwiitanks}")


def main():
    """Main execution function."""

    print("=" * 70)
    print("IMPORT EQUIPMENT MATCHING LOGS TO DATABASE")
    print("=" * 70)

    # Check database exists
    if not DATABASE_FILE.exists():
        print(f"ERROR: Database file not found: {DATABASE_FILE}")
        sys.exit(1)

    # Check matching logs exist
    if not MATCHING_LOGS_DIR.exists():
        print(f"ERROR: Matching logs directory not found: {MATCHING_LOGS_DIR}")
        sys.exit(1)

    # Connect to database
    print(f"\nConnecting to: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)

    try:
        # Import matches
        results = import_matches(conn)

        # Verify import
        verify_import(conn)

        # Log to import_log
        timestamp = datetime.now().isoformat()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file, records_imported, records_failed,
                import_started_at, import_completed_at, import_status,
                error_log, imported_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'equipment_matching_logs',
            'data/equipment_matching_logs/*_automated_matching_*.json',
            results['updated'],
            results['failed'],
            timestamp,
            timestamp,
            'success',
            f"Updated: {results['updated']}, Skipped: {results['skipped']}, Failed: {results['failed']}",
            'import_matching_logs.py'
        ))
        conn.commit()

        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print("\nNext step: Re-run populate_equipment_specs.py to populate specifications")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
