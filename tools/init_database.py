#!/usr/bin/env python3
"""
Database Initialization Script
Creates the master SQLite database with complete schema

Usage:
    python tools/init_database.py
    python tools/init_database.py --fresh  # Drop existing database and recreate
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_FILE = DATABASE_DIR / "master_database.db"
SCHEMA_FILE = DATABASE_DIR / "schema.sql"

def create_database_directory():
    """Ensure database directory exists"""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Database directory: {DATABASE_DIR}")

def load_schema():
    """Load SQL schema from file"""
    if not SCHEMA_FILE.exists():
        print(f"[ERROR] Schema file not found: {SCHEMA_FILE}")
        sys.exit(1)

    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    print(f"[OK] Loaded schema: {SCHEMA_FILE}")
    return schema_sql

def initialize_database(fresh=False):
    """
    Initialize the database with schema

    Args:
        fresh: If True, delete existing database and create new one
    """
    # Handle fresh start
    if fresh and DATABASE_FILE.exists():
        print(f"[WARN] Removing existing database: {DATABASE_FILE}")
        DATABASE_FILE.unlink()

    # Check if database already exists
    db_exists = DATABASE_FILE.exists()

    # Create database directory
    create_database_directory()

    # Load schema
    schema_sql = load_schema()

    # Connect to database
    if db_exists:
        print(f"[OK] Connecting to existing database: {DATABASE_FILE}")
    else:
        print(f"[NEW] Creating new database: {DATABASE_FILE}")

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Execute schema
        print("[...] Executing schema...")
        cursor.executescript(schema_sql)
        conn.commit()
        print("[OK] Schema applied successfully")

        # Validate tables were created
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        tables = cursor.fetchall()

        print(f"\n[OK] Created {len(tables)} tables:")
        for (table_name,) in tables:
            # Count rows in each table
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name:30s} ({count:,} rows)")

        # Validate views
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='view'
            ORDER BY name
        """)
        views = cursor.fetchall()

        if views:
            print(f"\n[OK] Created {len(views)} views:")
            for (view_name,) in views:
                print(f"  - {view_name}")

        # Validate indexes
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        index_count = cursor.fetchone()[0]
        print(f"\n[OK] Created {index_count} indexes")

        # Get schema version
        cursor.execute("SELECT version, description FROM schema_version ORDER BY applied_at DESC LIMIT 1")
        version_info = cursor.fetchone()
        if version_info:
            version, description = version_info
            print(f"\n[OK] Schema version: {version}")
            print(f"  Description: {description}")

        # Database file size
        db_size = DATABASE_FILE.stat().st_size
        size_kb = db_size / 1024
        print(f"\n[OK] Database size: {size_kb:.2f} KB")

        print(f"\n{'='*60}")
        print(f"DATABASE READY: {DATABASE_FILE}")
        print(f"{'='*60}")

        return True

    except sqlite3.Error as e:
        print(f"\n[ERROR] Error creating database: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def validate_database():
    """Run validation checks on existing database"""
    if not DATABASE_FILE.exists():
        print(f"[ERROR] Database not found: {DATABASE_FILE}")
        return False

    print(f"Validating database: {DATABASE_FILE}\n")

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Check schema version
        cursor.execute("SELECT version, applied_at FROM schema_version ORDER BY applied_at DESC LIMIT 1")
        version_info = cursor.fetchone()
        if version_info:
            version, applied_at = version_info
            print(f"[OK] Schema version: {version} (applied {applied_at})")
        else:
            print("[WARN] No schema version found")

        # Check table counts
        expected_tables = [
            'equipment', 'guns', 'ammunition', 'penetration_data',
            'equipment_guns', 'units', 'unit_equipment',
            'match_reviews', 'import_log', 'schema_version'
        ]

        print(f"\n[OK] Checking {len(expected_tables)} core tables:")
        all_valid = True
        for table in expected_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  [OK] {table:30s} {count:,} rows")
            except sqlite3.Error as e:
                print(f"  [ERROR] {table:30s} ERROR: {e}")
                all_valid = False

        # Check foreign key constraints
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        if fk_enabled:
            print(f"\n[OK] Foreign key constraints: ENABLED")
        else:
            print(f"\n[WARN] Foreign key constraints: DISABLED")
            print("   Enable with: PRAGMA foreign_keys = ON;")

        # Check indexes
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        index_count = cursor.fetchone()[0]
        print(f"[OK] Indexes: {index_count}")

        # Database integrity check
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        if integrity == 'ok':
            print(f"[OK] Integrity check: OK")
        else:
            print(f"[ERROR] Integrity check: {integrity}")
            all_valid = False

        return all_valid

    except sqlite3.Error as e:
        print(f"\n[ERROR] Validation error: {e}")
        return False

    finally:
        conn.close()

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Initialize North Africa TO&E master database'
    )
    parser.add_argument(
        '--fresh',
        action='store_true',
        help='Delete existing database and create fresh'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate existing database without modifying'
    )

    args = parser.parse_args()

    print("="*60)
    print("North Africa TO&E Database Initialization")
    print("="*60)
    print()

    if args.validate:
        # Validation mode
        success = validate_database()
        sys.exit(0 if success else 1)
    else:
        # Initialization mode
        success = initialize_database(fresh=args.fresh)
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
