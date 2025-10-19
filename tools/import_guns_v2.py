#!/usr/bin/env python3
"""
Guns v2.1 Import Script
Imports WWII Tanks UK gun data with ammunition and penetration tables

Usage:
    python tools/import_guns_v2.py
    python tools/import_guns_v2.py --nation british  # Import specific nation only
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
GUNS_FILE = PROJECT_ROOT / "data" / "output" / "afv_data" / "wwiitanks" / "all_guns_v2.json"

class GunsImporter:
    def __init__(self, nation_filter=None):
        self.nation_filter = nation_filter
        self.conn = None
        self.guns_data = []

        # Statistics
        self.total_guns = 0
        self.imported_guns = 0
        self.skipped_guns = 0
        self.error_guns = 0

        self.total_ammo = 0
        self.imported_ammo = 0

        self.total_penetration = 0
        self.imported_penetration = 0

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

    def load_guns_data(self):
        """Load guns v2.1 data"""
        if not GUNS_FILE.exists():
            print(f"[ERROR] Guns file not found: {GUNS_FILE}")
            sys.exit(1)

        with open(GUNS_FILE, 'r', encoding='utf-8') as f:
            guns = json.load(f)

        for gun in guns:
            # Get nation from country field
            gun_country = gun.get('country', '').lower()

            # Normalize to canonical nation names
            if 'britain' in gun_country:
                gun_nation = 'british'
            elif 'germany' in gun_country:
                gun_nation = 'german'
            elif 'italy' in gun_country or 'italian' in gun_country:
                gun_nation = 'italian'
            elif 'usa' in gun_country or 'america' in gun_country:
                gun_nation = 'american'
            elif 'france' in gun_country or 'french' in gun_country:
                gun_nation = 'french'
            else:
                gun_nation = gun_country

            # Filter by nation if specified
            if self.nation_filter and gun_nation != self.nation_filter:
                continue

            gun['nation'] = gun_nation
            self.guns_data.append(gun)

        self.total_guns = len(self.guns_data)

        if self.nation_filter:
            print(f"[OK] Loaded {self.total_guns} {self.nation_filter.title()} guns from WWII Tanks UK v2.1")
        else:
            print(f"[OK] Loaded {self.total_guns} total guns from WWII Tanks UK v2.1")

    def import_gun(self, gun):
        """Import single gun with ammunition and penetration data"""
        try:
            # Generate gun_id
            nation = gun.get('nation')
            wwiitanks_id = gun.get('wwiitanks_id', '')
            gun_id = f"{nation}_{wwiitanks_id}"

            # Basic gun fields
            name = gun.get('gun_name')
            full_name = gun.get('full_name')

            # Extract from basic_specs object
            basic_specs = gun.get('basic_specs', {})

            # Parse caliber from "47mm" format
            caliber_str = basic_specs.get('calibre', '')
            caliber_mm = None
            if caliber_str:
                cal_match = re.findall(r'\d+', caliber_str)
                if cal_match:
                    caliber_mm = int(cal_match[0])

            barrel_length = basic_specs.get('length')

            # Parse rate of fire from "12 rpm" format
            rof_str = basic_specs.get('rate_of_fire', '')
            rate_of_fire = None
            if rof_str:
                rof_match = re.findall(r'\d+', rof_str)
                if rof_match:
                    rate_of_fire = int(rof_match[0])

            # Parse manufactured from "1934 - 1945" format
            manuf_str = basic_specs.get('manufactured', '')
            manufactured_start = None
            manufactured_end = None
            if manuf_str:
                years = re.findall(r'\d{4}', manuf_str)
                if len(years) >= 1:
                    manufactured_start = int(years[0])
                if len(years) >= 2:
                    manufactured_end = int(years[1])

            gun_type = None  # Not in v2 format
            source_url = gun.get('source_url')
            history = None  # Not in v2 format

            scraper_version = gun.get('scraper_version')
            scraped_at = gun.get('scraped_at')

            # Insert gun
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO guns (
                    gun_id, name, full_name, nation,
                    caliber_mm, barrel_length, rate_of_fire_rpm,
                    manufactured_start, manufactured_end,
                    gun_type, wwiitanks_id, source_url,
                    history, scraped_at, scraper_version,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gun_id, name, full_name, nation,
                caliber_mm, barrel_length, rate_of_fire,
                manufactured_start, manufactured_end,
                gun_type, wwiitanks_id, source_url,
                history, scraped_at, scraper_version,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))

            self.imported_guns += 1

            # Import ammunition
            ammunition = gun.get('ammunition', [])
            self.total_ammo += len(ammunition)

            for ammo in ammunition:
                ammo_name = ammo.get('name')
                ammo_type = ammo.get('type')
                ammo_type_full = ammo.get('type_full')

                # Extract from specs object
                specs = ammo.get('specs', {})

                # Parse caliber from "20mm" format
                caliber_str = specs.get('calibre', '')
                caliber = None
                if caliber_str:
                    cal_match = re.findall(r'\d+', caliber_str)
                    if cal_match:
                        caliber = int(cal_match[0])

                weight_kg = specs.get('weight_kg')
                muzzle_velocity = specs.get('muzzle_velocity_m_s')

                # HE specific fields from specs
                explosive_kg = specs.get('explosive_kg')

                quoted_pen = ammo.get('quoted_penetration')

                # HE blast effects (not in v2 format)
                blast_99 = None
                blast_66 = None
                blast_33 = None
                blast_armor_1m = None

                cursor.execute("""
                    INSERT INTO ammunition (
                        gun_id, name, type, type_full,
                        caliber_mm, weight_kg, muzzle_velocity_m_s, explosive_kg,
                        quoted_penetration,
                        blast_kill_99pct_radius_m, blast_kill_66pct_radius_m,
                        blast_kill_33pct_radius_m, blast_armor_pen_1m_mm
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    gun_id, ammo_name, ammo_type, ammo_type_full,
                    caliber, weight_kg, muzzle_velocity, explosive_kg,
                    quoted_pen,
                    blast_99, blast_66, blast_33, blast_armor_1m
                ))

                ammo_id = cursor.lastrowid
                self.imported_ammo += 1

                # Import penetration data
                penetration_table = ammo.get('penetration_table', [])
                self.total_penetration += len(penetration_table)

                for pen in penetration_table:
                    range_m = pen.get('range_m')
                    flight_time = pen.get('flight_time_s')
                    pen_0deg = pen.get('penetration_0deg_mm')
                    pen_30deg = pen.get('penetration_30deg_mm')
                    hit_prob = pen.get('hit_probability_pct')

                    cursor.execute("""
                        INSERT INTO penetration_data (
                            ammo_id, range_m, flight_time_s,
                            penetration_0deg_mm, penetration_30deg_mm,
                            hit_probability_pct
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        ammo_id, range_m, flight_time,
                        pen_0deg, pen_30deg, hit_prob
                    ))

                    self.imported_penetration += 1

            self.conn.commit()
            return True

        except Exception as e:
            print(f"[ERROR] Failed to import gun {gun.get('gun_name')}: {e}")
            self.error_guns += 1
            self.conn.rollback()
            return False

    def import_all(self):
        """Import all guns with ammunition and penetration data"""
        print(f"\n{'='*80}")
        print(f"Guns v2.1 Import")
        print(f"{'='*80}")
        print(f"Total guns to import: {self.total_guns}\n")

        # Log import start
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO import_log (
                source_name, source_file,
                import_started_at, import_status, imported_by
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            'wwiitanks_guns_v2.1',
            str(GUNS_FILE),
            datetime.now().isoformat(),
            'in_progress',
            'guns_importer'
        ))
        import_log_id = cursor.lastrowid
        self.conn.commit()

        # Import each gun
        for idx, gun in enumerate(self.guns_data, 1):
            gun_id = gun.get('wwiitanks_id')
            gun_name = gun.get('gun_name')

            # Check if already imported
            cursor.execute("""
                SELECT gun_id FROM guns
                WHERE wwiitanks_id = ?
            """, (gun_id,))

            existing = cursor.fetchone()
            if existing:
                print(f"[SKIP] #{idx}/{self.total_guns} {gun_name} - already imported")
                self.skipped_guns += 1
                continue

            # Import gun
            success = self.import_gun(gun)

            if success:
                ammo_count = len(gun.get('ammunition', []))
                print(f"[OK] #{idx}/{self.total_guns} {gun_name} ({ammo_count} ammo types)")

        # Update import log
        cursor.execute("""
            UPDATE import_log
            SET records_imported = ?,
                records_failed = ?,
                import_completed_at = ?,
                import_status = ?
            WHERE id = ?
        """, (
            self.imported_guns,
            self.error_guns,
            datetime.now().isoformat(),
            'success' if self.error_guns == 0 else 'partial',
            import_log_id
        ))
        self.conn.commit()

        # Final statistics
        print(f"\n{'='*80}")
        print(f"Import Complete")
        print(f"{'='*80}")
        print(f"Guns:")
        print(f"  Total: {self.total_guns}")
        print(f"  Imported: {self.imported_guns}")
        print(f"  Skipped (already imported): {self.skipped_guns}")
        print(f"  Errors: {self.error_guns}")
        print(f"\nAmmunition types: {self.imported_ammo}")
        print(f"Penetration data points: {self.imported_penetration}")

        if self.error_guns > 0:
            print(f"\n[WARN] {self.error_guns} guns failed to import")
        else:
            print(f"\n[OK] All guns imported successfully")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Import WWII Tanks UK guns v2.1 data'
    )
    parser.add_argument(
        '--nation',
        choices=['british', 'german', 'italian', 'american', 'french'],
        help='Import only specific nation'
    )

    args = parser.parse_args()

    try:
        importer = GunsImporter(nation_filter=args.nation)
        importer.connect_database()
        importer.load_guns_data()
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
