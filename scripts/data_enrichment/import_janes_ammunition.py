#!/usr/bin/env python3
"""
Import Jane's ammunition capacity data into database.

Creates a new table `ammunition_capacity_janes` with ammunition data
extracted from Jane's WWII Tanks guide.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

# File paths
DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
JANES_DATA = Path("D:/north-africa-toe-builder/data/ammunition_capacity_janes_v2.json")

class JanesAmmoImporter:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.janes_data_path = JANES_DATA
        self.conn = None

    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"Connected to {self.db_path}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def create_table(self):
        """Create ammunition_capacity_janes table if it doesn't exist."""
        cursor = self.conn.cursor()

        create_sql = '''
        CREATE TABLE IF NOT EXISTS ammunition_capacity_janes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id TEXT NOT NULL,
            vehicle_name TEXT NOT NULL,
            nation TEXT,
            equipment_type TEXT,
            ammunition_capacity INTEGER NOT NULL,
            search_variant TEXT,
            confidence INTEGER,
            context TEXT,
            source TEXT DEFAULT 'Janes WWII Tanks and Fighting Vehicles',
            extraction_date TEXT,
            imported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (equipment_id) REFERENCES equipment(canonical_id),
            UNIQUE(equipment_id)
        )
        '''

        cursor.execute(create_sql)
        self.conn.commit()
        print("Created ammunition_capacity_janes table")

    def load_janes_data(self) -> dict:
        """Load Jane's ammunition data from JSON file."""
        print(f"\nLoading {self.janes_data_path}...")
        with open(self.janes_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"Loaded {len(data['vehicles'])} vehicles from Jane's guide")
        return data

    def import_data(self, min_confidence: int = 80):
        """
        Import ammunition data with confidence >= min_confidence.

        Args:
            min_confidence: Minimum confidence score (0-100) to import
        """
        data = self.load_janes_data()
        cursor = self.conn.cursor()

        # Filter by confidence
        vehicles_to_import = [v for v in data['vehicles'] if v['confidence'] >= min_confidence]

        print(f"\nImporting {len(vehicles_to_import)} vehicles (confidence >= {min_confidence}%)...")
        print("-" * 80)

        imported = 0
        skipped = 0
        errors = 0

        for vehicle in vehicles_to_import:
            try:
                insert_sql = '''
                INSERT OR REPLACE INTO ammunition_capacity_janes
                (equipment_id, vehicle_name, nation, equipment_type, ammunition_capacity,
                 search_variant, confidence, context, source, extraction_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''

                cursor.execute(insert_sql, (
                    vehicle['equipment_id'],
                    vehicle['vehicle_name'],
                    vehicle['nation'],
                    vehicle['type'],
                    vehicle['ammunition_capacity'],
                    vehicle['search_variant'],
                    vehicle['confidence'],
                    vehicle['context'],
                    data['source'],
                    data['extraction_date']
                ))

                imported += 1

            except sqlite3.IntegrityError as e:
                skipped += 1
                print(f"Skipped {vehicle['vehicle_name']}: {e}")

            except Exception as e:
                errors += 1
                print(f"Error importing {vehicle['vehicle_name']}: {e}")

        self.conn.commit()

        print(f"\n{'='*80}")
        print(f"IMPORT SUMMARY:")
        print(f"{'='*80}")
        print(f"  Imported: {imported}")
        print(f"  Skipped: {skipped}")
        print(f"  Errors: {errors}")
        print(f"  Total: {imported + skipped + errors}")

    def verify_import(self):
        """Verify imported data."""
        cursor = self.conn.cursor()

        # Count total records
        cursor.execute('SELECT COUNT(*) FROM ammunition_capacity_janes')
        total = cursor.fetchone()[0]

        # Confidence distribution
        cursor.execute('''
        SELECT
            COUNT(CASE WHEN confidence >= 90 THEN 1 END) as high,
            COUNT(CASE WHEN confidence >= 80 AND confidence < 90 THEN 1 END) as medium,
            COUNT(CASE WHEN confidence < 80 THEN 1 END) as low
        FROM ammunition_capacity_janes
        ''')
        row = cursor.fetchone()

        print(f"\n{'='*80}")
        print(f"VERIFICATION:")
        print(f"{'='*80}")
        print(f"Total records in ammunition_capacity_janes: {total}")
        print(f"\nConfidence distribution:")
        print(f"  High (90-100%): {row[0]}")
        print(f"  Medium (80-89%): {row[1]}")
        print(f"  Low (<80%): {row[2]}")

        # Sample records
        cursor.execute('''
        SELECT vehicle_name, nation, ammunition_capacity, confidence
        FROM ammunition_capacity_janes
        ORDER BY confidence DESC, vehicle_name
        LIMIT 10
        ''')

        print(f"\nSample records (top 10 by confidence):")
        for row in cursor.fetchall():
            print(f"  {row[0]} ({row[1]}): {row[2]} rounds (confidence {row[3]}%)")

    def create_view(self):
        """
        Create view combining equipment_battlegroup with Jane's ammo data.
        """
        cursor = self.conn.cursor()

        view_sql = '''
        CREATE VIEW IF NOT EXISTS equipment_with_janes_ammo AS
        SELECT
            e.canonical_id,
            e.name,
            e.nation,
            e.equipment_type,
            eb.reference_vehicle_id,
            rv.ammo_1 as reference_ammo,
            ja.ammunition_capacity as janes_ammo,
            ja.confidence as janes_confidence,
            COALESCE(rv.ammo_1, ja.ammunition_capacity) as best_ammo_estimate
        FROM equipment e
        LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
        LEFT JOIN bg_reference_vehicles rv ON eb.reference_vehicle_id = rv.id
        LEFT JOIN ammunition_capacity_janes ja ON e.canonical_id = ja.equipment_id
        WHERE e.equipment_type IN ('tank', 'tank_destroyer', 'assault_gun', 'self_propelled_gun')
        '''

        cursor.execute(view_sql)
        self.conn.commit()
        print("\nCreated view: equipment_with_janes_ammo")

        # Test view
        cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN reference_ammo IS NOT NULL THEN 1 ELSE 0 END) as has_ref_ammo,
            SUM(CASE WHEN janes_ammo IS NOT NULL THEN 1 ELSE 0 END) as has_janes_ammo,
            SUM(CASE WHEN best_ammo_estimate IS NOT NULL THEN 1 ELSE 0 END) as has_any_ammo
        FROM equipment_with_janes_ammo
        ''')

        row = cursor.fetchone()
        print(f"\nView statistics:")
        print(f"  Total AFVs: {row[0]}")
        print(f"  With reference ammo: {row[1]} ({100.0*row[1]/row[0]:.1f}%)")
        print(f"  With Jane's ammo: {row[2]} ({100.0*row[2]/row[0]:.1f}%)")
        print(f"  With ANY ammo estimate: {row[3]} ({100.0*row[3]/row[0]:.1f}%)")
        print(f"  Coverage improvement: +{row[3] - row[1]} vehicles")

def main():
    importer = JanesAmmoImporter()
    importer.connect()

    try:
        # Create table
        importer.create_table()

        # Import high-confidence data (80%+)
        print("\n" + "="*80)
        print("IMPORTING HIGH CONFIDENCE DATA (80%+)")
        print("="*80)
        importer.import_data(min_confidence=80)

        # Verify import
        importer.verify_import()

        # Create view
        importer.create_view()

    finally:
        importer.close()

    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print(f"{'='*80}")
    print("1. Review imported data: SELECT * FROM ammunition_capacity_janes")
    print("2. Check coverage: SELECT * FROM equipment_with_janes_ammo WHERE best_ammo_estimate IS NULL")
    print("3. Update equipment_battlegroup or datacard generator to use Jane's ammo data")
    print("4. Regenerate datacards with improved ammunition coverage")
    print("\nFor low-confidence matches, consider:")
    print("- Manual review and correction")
    print("- Online sources (tanks-encyclopedia.com, militaryfactory.com)")
    print("- Additional PDF extraction from BattleGroup supplements")

if __name__ == '__main__':
    main()
