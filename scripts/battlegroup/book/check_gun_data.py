#!/usr/bin/env python3
"""Check gun data availability for datacards."""

import sqlite3
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
DATABASE_PATH = project_root / "database" / "master_database.db"

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Check equipment_guns table
cursor.execute('SELECT COUNT(*) FROM equipment_guns')
print(f'equipment_guns entries: {cursor.fetchone()[0]}')

# Sample gun linkages
cursor.execute("""
    SELECT e.name, g.name, eg.mount_type
    FROM equipment e
    JOIN equipment_guns eg ON e.canonical_id = eg.equipment_id
    JOIN guns g ON eg.gun_id = g.gun_id
    LIMIT 10
""")
print('\nSample gun linkages:')
for row in cursor.fetchall():
    print(f'  {row[0]} -> {row[1]} ({row[2]})')

# Check tanks without gun linkages
cursor.execute("""
    SELECT e.name, e.equipment_type
    FROM equipment e
    WHERE (e.name LIKE '%tank%' OR e.name LIKE '%panzer%')
    AND e.canonical_id NOT IN (SELECT equipment_id FROM equipment_guns)
    LIMIT 10
""")
print('\nTanks without gun linkages:')
for row in cursor.fetchall():
    print(f'  {row[0]} ({row[1]})')

# Check if we have gun data in equipment table itself
cursor.execute("""
    SELECT name, formal_designation
    FROM equipment
    WHERE name LIKE '%Matilda%' OR name LIKE '%Pak 38%'
    LIMIT 5
""")
print('\nEquipment formal designations (may have gun info):')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
