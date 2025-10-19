#!/usr/bin/env python3
"""Quick database statistics"""
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"

conn = sqlite3.connect(DATABASE_FILE)
c = conn.cursor()

print("="*60)
print("DATABASE STATISTICS")
print("="*60)

# Equipment by nation
c.execute("SELECT nation, COUNT(*) FROM equipment GROUP BY nation ORDER BY nation")
print("\nEquipment by Nation:")
for row in c.fetchall():
    print(f"  {row[0]:12s}: {row[1]:3d} items")

c.execute("SELECT COUNT(*) FROM equipment")
print(f"  {'TOTAL':12s}: {c.fetchone()[0]:3d} items")

# Other counts
print(f"\n{'='*60}")
c.execute("SELECT COUNT(*) FROM guns")
print(f"Guns:              {c.fetchone()[0]:3d}")

c.execute("SELECT COUNT(*) FROM ammunition")
print(f"Ammunition types:  {c.fetchone()[0]:3d}")

c.execute("SELECT COUNT(*) FROM penetration_data")
print(f"Penetration data:  {c.fetchone()[0]:,}")

c.execute("SELECT COUNT(*) FROM units")
print(f"Units:             {c.fetchone()[0]:3d}")

c.execute("SELECT COUNT(*) FROM unit_equipment")
print(f"Unit equipment:    {c.fetchone()[0]:,}")

print(f"{'='*60}")

conn.close()
