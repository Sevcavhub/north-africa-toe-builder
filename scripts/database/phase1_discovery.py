#!/usr/bin/env python3
"""
Phase 1: Discovery & Analysis (READ-ONLY)
Database Normalization Agent v2.0.0
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
OUTPUT_DIR = Path("D:/north-africa-toe-builder")

def get_db_connection():
    """Get read-only database connection"""
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

def list_all_tables(conn) -> List[str]:
    """Get all tables in database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    return [row[0] for row in cursor.fetchall()]

def get_table_info(conn, table_name: str) -> List[Dict]:
    """Get column information for a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    return [{
        'cid': col[0],
        'name': col[1],
        'type': col[2],
        'notnull': col[3],
        'default': col[4],
        'pk': col[5]
    } for col in columns]

def get_row_count(conn, table_name: str) -> int:
    """Get row count for a table"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    return cursor.fetchone()[0]

def main():
    """Main discovery function"""
    print("=" * 80)
    print("DATABASE NORMALIZATION - PHASE 1: DISCOVERY & ANALYSIS")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print(f"Mode: READ-ONLY")
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # Connect to database
    conn = get_db_connection()

    # List all tables
    tables = list_all_tables(conn)
    print(f"Total tables found: {len(tables)}")
    print()

    # Analyze each table
    table_info = {}
    total_records = 0

    for table in tables:
        row_count = get_row_count(conn, table)
        columns = get_table_info(conn, table)
        total_records += row_count

        table_info[table] = {
            'row_count': row_count,
            'column_count': len(columns),
            'columns': columns
        }

        print(f"Table: {table}")
        print(f"  Rows: {row_count:,}")
        print(f"  Columns: {len(columns)}")
        print()

    # Save database schema overview
    schema_overview = {
        'database': str(DB_PATH),
        'analyzed_at': datetime.now().isoformat(),
        'total_tables': len(tables),
        'total_records': total_records,
        'tables': table_info
    }

    output_file = OUTPUT_DIR / 'database_schema_overview.json'
    with open(output_file, 'w') as f:
        json.dump(schema_overview, f, indent=2)

    print(f"✓ Schema overview saved: {output_file}")
    print()
    print("=" * 80)
    print(f"Total records across all tables: {total_records:,}")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    main()
