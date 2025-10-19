#!/usr/bin/env python3
"""
Units Import Script
Imports unit TO&E data from JSON files into SQLite database

Usage:
    python tools/import_units.py
    python tools/import_units.py --nation german  # Import specific nation only
    python tools/import_units.py --quarter 1941-Q2  # Import specific quarter only
"""

import sqlite3
import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"
UNITS_DIR = PROJECT_ROOT / "data" / "output" / "units"

class UnitsImporter:
    def __init__(self, nation_filter=None, quarter_filter=None):
        self.nation_filter = nation_filter
        self.quarter_filter = quarter_filter
        self.conn = None
        self.unit_files = []

        # Statistics
        self.total_units = 0
        self.imported_units = 0
        self.skipped_units = 0
        self.error_units = 0

        self.total_equipment_items = 0
        self.imported_equipment_items = 0

    def connect_database(self):
        """Connect to SQLite database"""
        if not DATABASE_FILE.exists():
            print(f"[ERROR] Database not found: {DATABASE_FILE}")
            print("       Run: python tools/init_database.py")
            sys.exit(1)

        self.conn = sqlite3.connect(DATABASE_FILE)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        print(f"[OK] Connected to database: {DATABASE_FILE}")

    def load_unit_files(self):
        """Load all unit JSON files"""
        if not UNITS_DIR.exists():
            print(f"[ERROR] Units directory not found: {UNITS_DIR}")
            sys.exit(1)

        # Find all unit JSON files
        all_files = list(UNITS_DIR.glob("*_toe.json"))

        for file_path in all_files:
            # Parse filename to extract nation and quarter
            # Format: {nation}_{quarter}_{designation}_toe.json
            filename = file_path.stem
            parts = filename.split('_')

            if len(parts) < 3:
                continue

            file_nation = parts[0].lower()
            file_quarter = parts[1].upper()

            # Normalize quarter format: 1941q2 -> 1941-Q2
            if 'q' in file_quarter.lower():
                year_quarter = file_quarter.split('Q')
                if len(year_quarter) == 2:
                    file_quarter = f"{year_quarter[0]}-Q{year_quarter[1]}"

            # Filter by nation
            if self.nation_filter and file_nation != self.nation_filter:
                continue

            # Filter by quarter
            if self.quarter_filter and file_quarter != self.quarter_filter:
                continue

            self.unit_files.append(file_path)

        self.total_units = len(self.unit_files)

        filter_desc = []
        if self.nation_filter:
            filter_desc.append(f"{self.nation_filter.title()}")
        if self.quarter_filter:
            filter_desc.append(f"{self.quarter_filter}")

        if filter_desc:
            print(f"[OK] Loaded {self.total_units} unit files ({' '.join(filter_desc)})")
        else:
            print(f"[OK] Loaded {self.total_units} total unit files")

    def generate_unit_id(self, unit_data):
        """Generate unique unit ID"""
        nation = unit_data.get('nation', '').lower()
        quarter = unit_data.get('quarter', '').replace('-', '').lower()
        designation = unit_data.get('unit_designation', '')

        # Sanitize designation for ID
        designation_id = re.sub(r'[^\w\s-]', '', designation.lower())
        designation_id = re.sub(r'[\s-]+', '_', designation_id)

        return f"{nation}_{quarter}_{designation_id}"

    def import_unit(self, file_path):
        """Import single unit with equipment"""
        try:
            # Load JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                unit_data = json.load(f)

            # Generate unit ID
            unit_id = self.generate_unit_id(unit_data)

            # Basic unit fields
            nation = unit_data.get('nation')
            quarter = unit_data.get('quarter')
            designation = unit_data.get('unit_designation')
            unit_type = unit_data.get('unit_type')
            parent_formation = unit_data.get('parent_formation')
            organization_level = unit_data.get('organization_level')

            # Command structure
            command = unit_data.get('command', {})
            commander_info = command.get('commander', {})
            commander_name = commander_info.get('name')
            commander_rank = commander_info.get('rank')
            commander_appointment_date = commander_info.get('appointment_date')

            headquarters_location = command.get('headquarters_location')
            parent_command = command.get('parent_command')

            staff = command.get('staff_strength', {})
            staff_officers = staff.get('officers')
            staff_ncos = staff.get('ncos')
            staff_enlisted = staff.get('enlisted')

            # Personnel
            total_personnel = unit_data.get('total_personnel')
            officers = unit_data.get('officers')
            ncos = unit_data.get('ncos')
            enlisted = unit_data.get('enlisted')

            # Operational status
            operational_status = unit_data.get('operational_status')
            readiness_percentage = unit_data.get('readiness_percentage')

            # Geographic context
            theater = unit_data.get('theater', 'north_africa')
            location = unit_data.get('location')

            # Source reference
            source_file = file_path.name
            schema_version = unit_data.get('schema_version')

            # Insert unit
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO units (
                    unit_id, nation, quarter, designation, unit_type,
                    parent_formation, organization_level,
                    commander_name, commander_rank, commander_appointment_date,
                    headquarters_location, parent_command,
                    staff_officers, staff_ncos, staff_enlisted,
                    total_personnel, officers, ncos, enlisted,
                    operational_status, readiness_percentage,
                    theater, location,
                    source_file, schema_version,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                unit_id, nation, quarter, designation, unit_type,
                parent_formation, organization_level,
                commander_name, commander_rank, commander_appointment_date,
                headquarters_location, parent_command,
                staff_officers, staff_ncos, staff_enlisted,
                total_personnel, officers, ncos, enlisted,
                operational_status, readiness_percentage,
                theater, location,
                source_file, schema_version,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))

            self.imported_units += 1

            # Import equipment
            equipment_count = self.import_unit_equipment(unit_id, unit_data)
            self.total_equipment_items += equipment_count

            self.conn.commit()
            return True

        except Exception as e:
            print(f"[ERROR] Failed to import {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
            self.error_units += 1
            self.conn.rollback()
            return False

    def import_unit_equipment(self, unit_id, unit_data):
        """Import all equipment for a unit"""
        cursor = self.conn.cursor()
        equipment_count = 0

        # Import tanks
        tanks = unit_data.get('tanks', {})
        equipment_count += self.import_equipment_category(
            cursor, unit_id, tanks, 'tanks', 'heavy_tanks'
        )
        equipment_count += self.import_equipment_category(
            cursor, unit_id, tanks, 'tanks', 'medium_tanks'
        )
        equipment_count += self.import_equipment_category(
            cursor, unit_id, tanks, 'tanks', 'light_tanks'
        )

        # Import halftracks
        halftracks = unit_data.get('halftracks', {})
        equipment_count += self.import_equipment_category(
            cursor, unit_id, halftracks, 'halftracks'
        )

        # Import armored cars
        armored_cars = unit_data.get('armored_cars', {})
        equipment_count += self.import_equipment_category(
            cursor, unit_id, armored_cars, 'armored_cars'
        )

        # Import trucks
        trucks = unit_data.get('trucks', {})
        equipment_count += self.import_equipment_category(
            cursor, unit_id, trucks, 'trucks'
        )

        # Import artillery
        artillery = unit_data.get('artillery', {})
        if artillery:
            for arty_type in ['field_artillery', 'anti_tank_guns', 'anti_aircraft_guns']:
                arty_category = artillery.get(arty_type, {})
                equipment_count += self.import_equipment_category(
                    cursor, unit_id, arty_category, 'artillery', arty_type
                )

        self.imported_equipment_items += equipment_count
        return equipment_count

    def import_equipment_category(self, cursor, unit_id, category_data, category, subcategory=None):
        """Import equipment from a specific category"""
        if not category_data:
            return 0

        count = 0
        variants = category_data.get('variants', {})

        for variant_name, variant_info in variants.items():
            # Get equipment count
            item_count = variant_info.get('count', 0)
            if item_count == 0:
                continue

            # Get operational count
            operational = variant_info.get('operational')

            # Calculate readiness percentage
            readiness_pct = None
            if operational is not None and item_count > 0:
                readiness_pct = round((operational / item_count) * 100, 1)

            # Get variant details
            armament = variant_info.get('armament')
            armor_mm = variant_info.get('armor_mm')
            role = variant_info.get('role')
            variant_notes = variant_info.get('notes')

            # Determine equipment_id (will be NULL if not matched yet)
            equipment_id = None  # TODO: Match to equipment table in future

            # Insert unit_equipment record
            cursor.execute("""
                INSERT OR REPLACE INTO unit_equipment (
                    unit_id, equipment_id,
                    count, operational, readiness_percentage,
                    variant_name, variant_notes,
                    category, subcategory,
                    armament, armor_mm, role
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                unit_id, equipment_id,
                item_count, operational, readiness_pct,
                variant_name, variant_notes,
                category, subcategory,
                armament, armor_mm, role
            ))

            count += 1

        return count

    def import_all(self):
        """Import all units"""
        print(f"\n{'='*80}")
        print(f"Units Import")
        print(f"{'='*80}")
        print(f"Total units to import: {self.total_units}\n")

        # Log import start
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file,
                import_started_at, import_status, imported_by
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            'units',
            str(UNITS_DIR),
            datetime.now().isoformat(),
            'in_progress',
            'units_importer'
        ))
        import_log_id = cursor.lastrowid
        self.conn.commit()

        # Import each unit
        for idx, file_path in enumerate(self.unit_files, 1):
            # Check if already imported
            unit_name = file_path.stem.replace('_toe', '')

            cursor.execute("""
                SELECT unit_id FROM units
                WHERE source_file = ?
            """, (file_path.name,))

            existing = cursor.fetchone()
            if existing:
                print(f"[SKIP] #{idx}/{self.total_units} {unit_name} - already imported")
                self.skipped_units += 1
                continue

            # Import unit
            success = self.import_unit(file_path)

            if success:
                print(f"[OK] #{idx}/{self.total_units} {unit_name}")

        # Update import log
        cursor.execute("""
            UPDATE import_log
            SET records_imported = ?,
                records_failed = ?,
                import_completed_at = ?,
                import_status = ?
            WHERE id = ?
        """, (
            self.imported_units,
            self.error_units,
            datetime.now().isoformat(),
            'success' if self.error_units == 0 else 'partial',
            import_log_id
        ))
        self.conn.commit()

        # Final statistics
        print(f"\n{'='*80}")
        print(f"Import Complete")
        print(f"{'='*80}")
        print(f"Units:")
        print(f"  Total: {self.total_units}")
        print(f"  Imported: {self.imported_units}")
        print(f"  Skipped (already imported): {self.skipped_units}")
        print(f"  Errors: {self.error_units}")
        print(f"\nEquipment items: {self.imported_equipment_items}")

        if self.error_units > 0:
            print(f"\n[WARN] {self.error_units} units failed to import")
        else:
            print(f"\n[OK] All units imported successfully")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Import unit TO&E data from JSON files'
    )
    parser.add_argument(
        '--nation',
        choices=['british', 'german', 'italian', 'american', 'french'],
        help='Import only specific nation'
    )
    parser.add_argument(
        '--quarter',
        help='Import only specific quarter (e.g., 1941-Q2)'
    )

    args = parser.parse_args()

    try:
        importer = UnitsImporter(nation_filter=args.nation, quarter_filter=args.quarter)
        importer.connect_database()
        importer.load_unit_files()
        importer.import_all()
        importer.close()

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n[INFO] Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
