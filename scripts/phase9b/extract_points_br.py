#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 9B Phase 1.2: Extract Points/BR from BG Builder forces.js

Parses bg_builder_forces.sections JSON to extract Points and BR values for vehicles.
Populates bg_builder_vehicle_costs table with veteran/regular/inexperienced/elite costs.

Author: North Africa TO&E Builder
Date: November 11, 2025
"""

import sqlite3
import sys
import io
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")

@dataclass
class VehicleCost:
    """Vehicle cost/BR data."""
    vehicle_id: int
    vehicle_name: str
    force_name: str
    cost_regular: int
    br_regular: int
    cost_veteran: Optional[int] = None
    cost_elite: Optional[int] = None
    cost_inexperienced: Optional[int] = None
    br_veteran: Optional[int] = None
    br_elite: Optional[int] = None
    br_inexperienced: Optional[int] = None
    restricted: bool = False
    unique: bool = False

class PointsBRExtractor:
    """Extract Points/BR from BG Builder forces."""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        self.conn.close()

    def create_costs_table(self):
        """Create bg_builder_vehicle_costs table if not exists."""
        cursor = self.conn.cursor()

        # Drop existing table to ensure clean schema
        cursor.execute('DROP TABLE IF EXISTS bg_builder_vehicle_costs')

        cursor.execute('''
            CREATE TABLE bg_builder_vehicle_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                vehicle_name TEXT,
                force_name TEXT,
                cost_regular INTEGER,
                cost_veteran INTEGER,
                cost_elite INTEGER,
                cost_inexperienced INTEGER,
                br_regular INTEGER,
                br_veteran INTEGER,
                br_elite INTEGER,
                br_inexperienced INTEGER,
                restricted BOOLEAN DEFAULT 0,
                unique_flag BOOLEAN DEFAULT 0,
                import_date TEXT,
                import_source TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES bg_builder_vehicles(id)
            )
        ''')

        self.conn.commit()
        print("✓ bg_builder_vehicle_costs table ready")

    def parse_sections(self, sections_json: str, force_name: str) -> List[VehicleCost]:
        """
        Parse sections JSON to extract vehicle costs.

        Args:
            sections_json: JSON string from bg_builder_forces.sections
            force_name: Name of the force (e.g., "German Panzer Division")

        Returns:
            List of VehicleCost objects
        """
        costs = []

        try:
            sections = json.loads(sections_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for {force_name}: {e}")
            return costs

        for section in sections:
            section_name = section.get('name', 'Unknown')
            entries = section.get('entries', [])

            for entry in entries:
                # Check if entry has vehicle reference
                vehicle_id = entry.get('v')
                if not vehicle_id:
                    continue

                # Handle single vehicle
                if isinstance(vehicle_id, int):
                    cost = self._parse_entry(entry, force_name)
                    if cost:
                        costs.append(cost)

                # Handle multiple vehicles (arrays)
                elif isinstance(vehicle_id, list):
                    # Skip for now - these are complex entries with multiple vehicles
                    pass

        return costs

    def _parse_entry(self, entry: Dict, force_name: str) -> Optional[VehicleCost]:
        """Parse a single entry to extract cost/BR."""
        vehicle_id = entry.get('v')
        if not vehicle_id or not isinstance(vehicle_id, int):
            return None

        # Get vehicle name from database
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM bg_builder_vehicles WHERE id = ?', (vehicle_id,))
        row = cursor.fetchone()
        if not row:
            return None

        vehicle_name = row['name']

        # Base cost and BR
        cost_regular = entry.get('cost', 0)
        br_regular = entry.get('br', 0)

        # Check for troop quality options
        cost_veteran = None
        cost_elite = None
        cost_inexperienced = None
        br_veteran = None
        br_elite = None
        br_inexperienced = None

        options = entry.get('options', [])
        for option in options:
            if option.get('name') == 'Troop Quality':
                choices = option.get('choices', [])
                for choice in choices:
                    text = choice.get('text', '').lower()
                    if 'veteran' in text:
                        cost_veteran = cost_regular
                        br_veteran = br_regular
                    elif 'elite' in text:
                        cost_elite = cost_regular + choice.get('cost', 0)
                        br_elite = br_regular + choice.get('br', 0)
                    elif 'inexperienced' in text:
                        cost_inexperienced = cost_regular + choice.get('cost', 0)
                        br_inexperienced = br_regular + choice.get('br', 0)

        # Flags
        restricted = entry.get('restricted', False) in [True, 'true', 'True']
        unique = entry.get('unique', False)

        return VehicleCost(
            vehicle_id=vehicle_id,
            vehicle_name=vehicle_name,
            force_name=force_name,
            cost_regular=cost_regular,
            br_regular=br_regular,
            cost_veteran=cost_veteran,
            cost_elite=cost_elite,
            cost_inexperienced=cost_inexperienced,
            br_veteran=br_veteran,
            br_elite=br_elite,
            br_inexperienced=br_inexperienced,
            restricted=restricted,
            unique=unique
        )

    def extract_all_costs(self) -> List[VehicleCost]:
        """Extract costs from all forces."""
        cursor = self.conn.cursor()

        cursor.execute('SELECT force_name, sections FROM bg_builder_forces')

        all_costs = []
        for row in cursor.fetchall():
            force_name = row['force_name']
            sections_json = row['sections']

            costs = self.parse_sections(sections_json, force_name)
            all_costs.extend(costs)

        print(f"✓ Extracted {len(all_costs)} vehicle cost entries from {cursor.rowcount} forces")
        return all_costs

    def import_costs(self, costs: List[VehicleCost]):
        """Import costs to database."""
        cursor = self.conn.cursor()

        # Clear existing data
        cursor.execute('DELETE FROM bg_builder_vehicle_costs')

        # Import new data
        for cost in costs:
            cursor.execute('''
                INSERT INTO bg_builder_vehicle_costs
                (vehicle_id, vehicle_name, force_name, cost_regular, cost_veteran, cost_elite,
                 cost_inexperienced, br_regular, br_veteran, br_elite, br_inexperienced,
                 restricted, unique_flag, import_date, import_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 'bg_builder_forces')
            ''', (
                cost.vehicle_id, cost.vehicle_name, cost.force_name,
                cost.cost_regular, cost.cost_veteran, cost.cost_elite, cost.cost_inexperienced,
                cost.br_regular, cost.br_veteran, cost.br_elite, cost.br_inexperienced,
                cost.restricted, cost.unique
            ))

        self.conn.commit()
        print(f"✓ Imported {len(costs)} cost entries")

    def generate_report(self):
        """Generate extraction report."""
        cursor = self.conn.cursor()

        print("\n" + "="*80)
        print("POINTS/BR EXTRACTION REPORT")
        print("="*80)

        # Total vehicles with costs
        cursor.execute('SELECT COUNT(DISTINCT vehicle_id) FROM bg_builder_vehicle_costs')
        unique_vehicles = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM bg_builder_vehicle_costs')
        total_entries = cursor.fetchone()[0]

        print(f"\nTotal unique vehicles: {unique_vehicles}")
        print(f"Total cost entries: {total_entries}")

        # Sample high-cost vehicles
        cursor.execute('''
            SELECT vehicle_name, cost_regular, cost_veteran, cost_elite, br_regular, force_name
            FROM bg_builder_vehicle_costs
            WHERE cost_regular IS NOT NULL
            ORDER BY cost_regular DESC
            LIMIT 10
        ''')

        print("\nSample high-cost vehicles (top 10):")
        for row in cursor.fetchall():
            veteran_str = f" / {row[2]}" if row[2] else ""
            elite_str = f" / {row[3]}" if row[3] else ""
            print(f"  {row[0]}: {row[1]}{veteran_str}{elite_str} pts, BR {row[4]} ({row[5]})")

        # Restricted vehicles
        cursor.execute('SELECT COUNT(*) FROM bg_builder_vehicle_costs WHERE restricted = 1')
        restricted_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM bg_builder_vehicle_costs WHERE unique_flag = 1')
        unique_count = cursor.fetchone()[0]

        print(f"\nSpecial vehicles:")
        print(f"  Restricted: {restricted_count}")
        print(f"  Unique: {unique_count}")

def main():
    """Main execution."""
    print("="*80)
    print("PHASE 9B PHASE 1.2: EXTRACT POINTS/BR FROM BG BUILDER")
    print("="*80)

    extractor = PointsBRExtractor()

    try:
        # Step 1: Create table
        print("\n[Step 1/3] Creating bg_builder_vehicle_costs table...")
        extractor.create_costs_table()

        # Step 2: Extract costs
        print("\n[Step 2/3] Extracting costs from bg_builder_forces...")
        costs = extractor.extract_all_costs()

        # Step 3: Import costs
        print("\n[Step 3/3] Importing costs to database...")
        extractor.import_costs(costs)

        # Report
        extractor.generate_report()

        print("\n" + "="*80)
        print("✅ EXTRACTION COMPLETE")
        print("="*80)
        print("\nNext steps:")
        print("1. Link vehicle costs to equipment_battlegroup")
        print("2. Update datacard generator to use Points/BR")
        print("3. Regenerate datacards with complete Points/BR values")

    finally:
        extractor.close()

if __name__ == '__main__':
    main()
