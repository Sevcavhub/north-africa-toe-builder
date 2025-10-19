#!/usr/bin/env python3
"""
WITW Baseline Import Script
Imports canonical WITW equipment data as baseline records into equipment table

Usage:
    python tools/import_witw_baseline.py
    python tools/import_witw_baseline.py --nation british  # Import specific nation only
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"
WITW_FILE = PROJECT_ROOT / "data" / "iterations" / "iteration_2" / "Timeline_TOE_Reconstruction" / "OUTPUT" / "v5_development" / "canonical_equipment_master_with_witw_ALL_NATIONS.json"

class WITWImporter:
    def __init__(self, nation_filter=None):
        self.nation_filter = nation_filter
        self.conn = None
        self.witw_data = []

        # Statistics
        self.total_items = 0
        self.imported_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def connect_database(self):
        """Connect to SQLite database"""
        if not DATABASE_FILE.exists():
            print(f"[ERROR] Database not found: {DATABASE_FILE}")
            print("       Run: python tools/init_database.py")
            sys.exit(1)

        self.conn = sqlite3.connect(DATABASE_FILE)
        print(f"[OK] Connected to database: {DATABASE_FILE}")

    def load_witw_data(self):
        """Load WITW canonical equipment data"""
        if not WITW_FILE.exists():
            print(f"[ERROR] WITW file not found: {WITW_FILE}")
            sys.exit(1)

        with open(WITW_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract all equipment items from the nested structure
        all_equipment = data.get('equipment', {})

        for canonical_id, item in all_equipment.items():
            # Get nation
            item_nation = item.get('nation', '').lower()

            # Normalize British variants
            if 'british' in item_nation or 'commonwealth' in item_nation:
                item_nation = 'british'

            # Filter by nation if specified
            if self.nation_filter and item_nation != self.nation_filter:
                continue

            # Add canonical_id to item
            item['canonical_id'] = canonical_id
            item['nation'] = item_nation

            self.witw_data.append(item)

        self.total_items = len(self.witw_data)

        if self.nation_filter:
            print(f"[OK] Loaded {self.total_items} {self.nation_filter.title()} items from WITW")
        else:
            print(f"[OK] Loaded {self.total_items} total items from WITW")

    def import_equipment(self, item):
        """Import single equipment item as baseline record"""
        try:
            canonical_id = item.get('canonical_id')
            name = item.get('canonical_name', item.get('name'))
            nation = item.get('nation')
            equipment_type = item.get('type')
            category = item.get('category')

            # WITW specific fields
            witw_id = item.get('witw_id')
            witw_name = item.get('witw_name')
            witw_confidence = 100  # Baseline data is 100% confidence

            # First appearance (from WITW)
            first_appearance = item.get('first_appearance')

            # Aliases (store as JSON string)
            aliases = item.get('aliases')
            if aliases and isinstance(aliases, list):
                aliases = json.dumps(aliases)

            # Basic specs if available in WITW
            crew = item.get('crew')
            weight_tonnes = item.get('weight_tonnes')

            # Insert baseline record
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO equipment (
                    canonical_id, name, nation, equipment_type, category,
                    witw_id, witw_name, witw_confidence,
                    crew, weight_tonnes,
                    first_appearance, aliases,
                    created_at, updated_at, created_by, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                canonical_id, name, nation, equipment_type, category,
                witw_id, witw_name, witw_confidence,
                crew, weight_tonnes,
                first_appearance, aliases,
                datetime.now().isoformat(), datetime.now().isoformat(),
                'witw_importer', 'witw_importer'
            ))

            self.conn.commit()
            self.imported_count += 1

            return True

        except Exception as e:
            print(f"[ERROR] Failed to import {item.get('canonical_id')}: {e}")
            self.error_count += 1
            return False

    def import_all(self):
        """Import all WITW items as baseline"""
        print(f"\n{'='*80}")
        print(f"WITW Baseline Import")
        print(f"{'='*80}")
        print(f"Total items to import: {self.total_items}\n")

        # Log import start
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file,
                import_started_at, import_status, imported_by
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            'witw_baseline',
            str(WITW_FILE),
            datetime.now().isoformat(),
            'in_progress',
            'witw_importer'
        ))
        import_log_id = cursor.lastrowid
        self.conn.commit()

        # Import each item
        for idx, item in enumerate(self.witw_data, 1):
            try:
                canonical_id = item.get('canonical_id', '')
                name = item.get('canonical_name', item.get('name', ''))

                # Make ASCII-safe for printing
                safe_id = canonical_id.encode('ascii', 'replace').decode('ascii')
                safe_name = name.encode('ascii', 'replace').decode('ascii')

                # Check if already imported
                cursor.execute("""
                    SELECT canonical_id FROM equipment
                    WHERE canonical_id = ? AND witw_id IS NOT NULL
                """, (canonical_id,))

                existing = cursor.fetchone()
                if existing:
                    print(f"[SKIP] #{idx}/{self.total_items} {safe_id} - already imported")
                    self.skipped_count += 1
                    continue

                # Import item
                success = self.import_equipment(item)

                if success:
                    print(f"[OK] #{idx}/{self.total_items} {safe_id} - {safe_name}")

            except Exception as e:
                # Handle encoding or other errors
                print(f"[ERROR] #{idx}/{self.total_items} - {str(e)}")
                self.error_count += 1
                continue

        # Update import log
        cursor.execute("""
            UPDATE import_log
            SET records_imported = ?,
                records_failed = ?,
                import_completed_at = ?,
                import_status = ?
            WHERE id = ?
        """, (
            self.imported_count,
            self.error_count,
            datetime.now().isoformat(),
            'success' if self.error_count == 0 else 'partial',
            import_log_id
        ))
        self.conn.commit()

        # Final statistics
        print(f"\n{'='*80}")
        print(f"Import Complete")
        print(f"{'='*80}")
        print(f"Total items: {self.total_items}")
        print(f"  Imported: {self.imported_count}")
        print(f"  Skipped (already imported): {self.skipped_count}")
        print(f"  Errors: {self.error_count}")

        if self.error_count > 0:
            print(f"\n[WARN] {self.error_count} items failed to import")
        else:
            print(f"\n[OK] All items imported successfully")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Import WITW baseline equipment data'
    )
    parser.add_argument(
        '--nation',
        choices=['british', 'german', 'italian', 'american', 'french'],
        help='Import only specific nation'
    )

    args = parser.parse_args()

    try:
        importer = WITWImporter(nation_filter=args.nation)
        importer.connect_database()
        importer.load_witw_data()
        importer.import_all()
        importer.close()

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n[INFO] Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
