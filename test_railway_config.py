#!/usr/bin/env python3
"""Test railway_config.py path resolution"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts" / "battlegroup" / "web"))

from railway_config import RailwayConfig

print("Railway Config Test")
print("=" * 70)
print(f"PROJECT_ROOT: {RailwayConfig.PROJECT_ROOT}")
print(f"DATABASE_PATH: {RailwayConfig.DATABASE_PATH}")
print(f"Database exists: {Path(RailwayConfig.DATABASE_PATH).exists()}")

if Path(RailwayConfig.DATABASE_PATH).exists():
    print("\nSUCCESS: Database path is correct!")

    # Test database access
    import sqlite3
    conn = sqlite3.connect(RailwayConfig.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bg_builder_vehicles")
    count = cursor.fetchone()[0]
    print(f"bg_builder_vehicles table has {count} rows")
    conn.close()
else:
    print("\nFAIL: Database not found at expected path")
    print(f"Expected: {RailwayConfig.DATABASE_PATH}")

    # Try to find it
    possible_paths = [
        Path("database/master_database.db"),
        Path("database/web_database.db"),
        Path("scripts/battlegroup/web/database/web_database.db")
    ]

    print("\nChecking possible locations:")
    for p in possible_paths:
        print(f"  {p}: {'EXISTS' if p.exists() else 'NOT FOUND'}")
