#!/usr/bin/env python3
"""
Execute BG Builder schema to create new tables in master_database.db
"""
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCHEMA_PATH = Path(__file__).parent.parent.parent.parent / "database" / "bg_builder_schema.sql"

def execute_schema():
    print("Executing BG Builder Schema")
    print("=" * 80)

    # Read schema file
    print(f"\nReading schema: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Connect to database with retries
    print(f"Connecting to database: {DB_PATH}")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            break
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                print(f"   Database locked, retrying in 2 seconds... (attempt {attempt+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"   ERROR: Could not connect after {max_retries} attempts")
                raise

    # Execute schema
    print("\nExecuting SQL...")
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print("   Schema executed successfully")
    except Exception as e:
        print(f"   ERROR: {e}")
        conn.rollback()
        raise

    # Verify tables created
    print("\nVerifying tables created...")
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name LIKE 'bg_builder%'
        ORDER BY name
    """)
    tables = cursor.fetchall()

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   {table[0]:40s} ({count} rows)")

    # Check if view created
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='view' AND name = 'v_vehicles_unified'
    """)
    if cursor.fetchone():
        print(f"   {'v_vehicles_unified (view)':40s}")

    conn.close()

    print("\n" + "=" * 80)
    print("SCHEMA EXECUTION COMPLETE")
    print("=" * 80)
    print("\nCreated tables:")
    print("   - bg_builder_vehicles")
    print("   - bg_builder_weapons")
    print("   - bg_builder_forces")
    print("   - bg_builder_vehicle_costs")
    print("   - v_vehicles_unified (view)")

if __name__ == '__main__':
    execute_schema()
