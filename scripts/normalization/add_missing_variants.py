"""Add display names as variants for masters without any variants."""
import sqlite3

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

# Find masters without variants
cursor.execute("""
    SELECT master_id, display_name
    FROM equipment_master_new
    WHERE master_id NOT IN (SELECT DISTINCT master_id FROM equipment_name_variants_new)
""")
masters = cursor.fetchall()

print(f"Found {len(masters)} masters without variants")
print()

for master_id, display_name in masters:
    # Check if this variant name already exists
    cursor.execute("""
        SELECT variant_name FROM equipment_name_variants_new
        WHERE variant_name = ?
    """, (display_name,))

    if cursor.fetchone():
        print(f"  Skipping master_id={master_id}: {display_name} (already exists)")
        # Use canonical_name instead
        cursor.execute("SELECT canonical_name FROM equipment_master_new WHERE master_id = ?", (master_id,))
        canonical_name = cursor.fetchone()[0]
        print(f"    Using canonical name instead: {canonical_name}")

        cursor.execute("""
            INSERT INTO equipment_name_variants_new
            (master_id, variant_name, variant_source, is_official)
            VALUES (?, ?, ?, ?)
        """, (master_id, canonical_name, 'manual', 1))
    else:
        print(f"  Adding variant for master_id={master_id}: {display_name}")
        cursor.execute("""
            INSERT INTO equipment_name_variants_new
            (master_id, variant_name, variant_source, is_official)
            VALUES (?, ?, ?, ?)
        """, (master_id, display_name, 'manual', 1))

conn.commit()

print()
print(f"[OK] Added {len(masters)} variants")
print()

# Verify coverage
cursor.execute("SELECT COUNT(DISTINCT master_id) FROM equipment_name_variants_new")
covered = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
total = cursor.fetchone()[0]

print(f"Coverage: {covered}/{total} ({100*covered/total:.1f}%)")
print()

conn.close()
