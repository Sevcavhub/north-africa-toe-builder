#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 9B Phase 1.2b: Link vehicle costs to equipment_battlegroup

Links bg_builder_vehicle_costs to equipment_battlegroup via bg_builder_vehicle_id.
Populates points_regular, points_veteran, points_elite, br_regular, br_veteran.

Author: North Africa TO&E Builder
Date: November 11, 2025
"""

import sqlite3
import sys
import io
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")

def main():
    """Link vehicle costs to equipment_battlegroup."""
    print("="*80)
    print("PHASE 9B PHASE 1.2B: LINK COSTS TO EQUIPMENT")
    print("="*80)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Step 1: Add columns if not exist
    print("\n[Step 1/2] Adding Points/BR columns to equipment_battlegroup...")
    cursor.execute('PRAGMA table_info(equipment_battlegroup)')
    cols = [col[1] for col in cursor.fetchall()]

    columns_to_add = [
        'points_regular INTEGER',
        'points_veteran INTEGER',
        'points_elite INTEGER',
        'br_regular INTEGER',
        'br_veteran INTEGER'
    ]

    for col_def in columns_to_add:
        col_name = col_def.split()[0]
        if col_name not in cols:
            cursor.execute(f'ALTER TABLE equipment_battlegroup ADD COLUMN {col_def}')
            print(f"  Added {col_name}")

    conn.commit()
    print("✓ Columns ready")

    # Step 2: Link costs
    print("\n[Step 2/2] Linking costs via bg_builder_vehicle_id...")
    cursor.execute('''
        UPDATE equipment_battlegroup
        SET points_regular = (
            SELECT CAST(AVG(cost_regular) AS INTEGER)
            FROM bg_builder_vehicle_costs
            WHERE bg_builder_vehicle_costs.vehicle_id = equipment_battlegroup.bg_builder_vehicle_id
        ),
        points_veteran = (
            SELECT CAST(AVG(cost_veteran) AS INTEGER)
            FROM bg_builder_vehicle_costs
            WHERE bg_builder_vehicle_costs.vehicle_id = equipment_battlegroup.bg_builder_vehicle_id
        ),
        points_elite = (
            SELECT CAST(AVG(cost_elite) AS INTEGER)
            FROM bg_builder_vehicle_costs
            WHERE bg_builder_vehicle_costs.vehicle_id = equipment_battlegroup.bg_builder_vehicle_id
        ),
        br_regular = (
            SELECT CAST(AVG(br_regular) AS INTEGER)
            FROM bg_builder_vehicle_costs
            WHERE bg_builder_vehicle_costs.vehicle_id = equipment_battlegroup.bg_builder_vehicle_id
        ),
        br_veteran = (
            SELECT CAST(AVG(br_veteran) AS INTEGER)
            FROM bg_builder_vehicle_costs
            WHERE bg_builder_vehicle_costs.vehicle_id = equipment_battlegroup.bg_builder_vehicle_id
        )
        WHERE bg_builder_vehicle_id IS NOT NULL
    ''')

    updated = cursor.rowcount
    conn.commit()
    print(f"✓ Updated {updated} equipment items")

    # Report
    print("\n" + "="*80)
    print("LINKAGE REPORT")
    print("="*80)

    cursor.execute('SELECT COUNT(*) FROM equipment_battlegroup WHERE points_regular IS NOT NULL')
    count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM equipment_battlegroup')
    total = cursor.fetchone()[0]
    print(f"\nEquipment with Points/BR: {count}/{total} ({100.0*count/total:.1f}%)")

    # Sample
    cursor.execute('''
        SELECT e.name, eb.points_regular, eb.points_veteran, eb.br_regular, e.nation
        FROM equipment_battlegroup eb
        JOIN equipment e ON eb.equipment_id = e.canonical_id
        WHERE eb.points_regular IS NOT NULL
        ORDER BY eb.points_regular DESC
        LIMIT 10
    ''')

    print("\nSample high-cost equipment (top 10):")
    for row in cursor.fetchall():
        vet_str = f" / {row[2]}" if row[2] else ""
        print(f"  {row[0]}: {row[1]}{vet_str} pts, BR {row[3]} ({row[4]})")

    conn.close()

    print("\n" + "="*80)
    print("✅ LINKAGE COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
