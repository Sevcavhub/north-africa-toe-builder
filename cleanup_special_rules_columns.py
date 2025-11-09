#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Delete special_rules and special_rules_temp columns"""

import sys
import io
import sqlite3
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"D:\north-africa-toe-builder\database\master_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("CLEANUP: Remove special_rules and special_rules_temp columns")
print("=" * 100)

# Step 1: Verify data has been migrated
print("\n📋 Verifying data migration...")

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE special_rules IS NOT NULL")
old_rules_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE special_rules_temp IS NOT NULL AND special_rules_temp != ''")
temp_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE ss_special IS NOT NULL OR dc_meta IS NOT NULL")
new_data_count = cursor.fetchone()[0]

print(f"   special_rules (old): {old_rules_count} records with data")
print(f"   special_rules_temp: {temp_count} records with data")
print(f"   ss_special + dc_meta (new): {new_data_count} records with data")

if temp_count > 0:
    print("\n⚠️  WARNING: special_rules_temp still has unparsed data!")
    cursor.execute("SELECT id, name, special_rules_temp FROM bg_reference_vehicles WHERE special_rules_temp IS NOT NULL AND special_rules_temp != ''")
    for row in cursor.fetchall():
        print(f"   ID {row[0]}: {row[1]} | {row[2]}")

    response = input("\nContinue anyway? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Aborted.")
        conn.close()
        sys.exit(0)

# Step 2: Backup
backup_table = f"bg_reference_vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"\n💾 Creating backup: {backup_table}")
cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM bg_reference_vehicles")
conn.commit()
print(f"   ✅ Backup created")

# Step 3: SQLite doesn't support DROP COLUMN directly, need to recreate table
print("\n🔧 Recreating table without special_rules columns...")

# Get current schema
cursor.execute("PRAGMA table_info(bg_reference_vehicles)")
columns = cursor.fetchall()

# Filter out special_rules and special_rules_temp
new_columns = []
for col in columns:
    col_name = col[1]
    if col_name not in ['special_rules', 'special_rules_temp']:
        col_type = col[2]
        new_columns.append(f"{col_name} {col_type}")

# Create new table
create_sql = f"CREATE TABLE bg_reference_vehicles_new ({', '.join(new_columns)})"
print(f"\n   Creating new table schema...")
cursor.execute(create_sql)

# Copy data (excluding special_rules columns)
column_names = [col[1] for col in columns if col[1] not in ['special_rules', 'special_rules_temp']]
copy_sql = f"""
    INSERT INTO bg_reference_vehicles_new ({', '.join(column_names)})
    SELECT {', '.join(column_names)}
    FROM bg_reference_vehicles
"""
print(f"   Copying data...")
cursor.execute(copy_sql)

# Drop old table and rename new one
print(f"   Replacing old table...")
cursor.execute("DROP TABLE bg_reference_vehicles")
cursor.execute("ALTER TABLE bg_reference_vehicles_new RENAME TO bg_reference_vehicles")

conn.commit()

# Step 4: Verify
print("\n✅ Verifying cleanup...")
cursor.execute("PRAGMA table_info(bg_reference_vehicles)")
final_columns = cursor.fetchall()

print(f"   Columns remaining: {len(final_columns)}")
print(f"\n   Column list:")
for col in final_columns:
    print(f"      {col[0]:2d}. {col[1]:30s} {col[2]}")

cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles")
final_count = cursor.fetchone()[0]

print(f"\n   Total records: {final_count}")

# Check that special_rules columns are gone
has_special_rules = any(col[1] == 'special_rules' for col in final_columns)
has_special_rules_temp = any(col[1] == 'special_rules_temp' for col in final_columns)

if has_special_rules or has_special_rules_temp:
    print("\n❌ ERROR: Columns still exist!")
else:
    print("\n✅ Columns successfully removed!")

conn.close()

print("\n" + "=" * 100)
print(f"Backup table: {backup_table}")
print("=" * 100)
