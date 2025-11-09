#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restore bg_reference_vehicles from backup"""

import sys
import io
import sqlite3

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("RESTORING FROM BACKUP")
print("=" * 100)

# Check current state
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
current_count = cursor.fetchone()[0]
print(f"\nCurrent records in bg_reference_vehicles: {current_count}")

# Check backup
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles_backup_20251107_222611")
backup_count = cursor.fetchone()[0]
print(f"Records in backup: {backup_count}")

# Drop current table and restore
print("\nDropping current table...")
cursor.execute("DROP TABLE IF EXISTS bg_reference_vehicles")
conn.commit()

print("Renaming backup to bg_reference_vehicles...")
cursor.execute("ALTER TABLE bg_reference_vehicles_backup_20251107_222611 RENAME TO bg_reference_vehicles")
conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
final_count = cursor.fetchone()[0]

print(f"\n✅ RESTORE COMPLETE")
print(f"   Records restored: {final_count}")

conn.close()
