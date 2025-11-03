#!/usr/bin/env python3
"""
Phase 3B Task 5: Infer equipment_type from category

Rules-based UPDATE to populate equipment_type field based on category values.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def infer_equipment_type(cursor):
    """Infer equipment_type from category using mapping rules"""

    print("Inferring equipment_type from category...\n")

    # First, check current state
    cursor.execute("SELECT COUNT(*) FROM equipment WHERE equipment_type IS NULL")
    null_count_before = cursor.fetchone()[0]
    print(f"Equipment with NULL equipment_type: {null_count_before}\n")

    # Audit logging (before update)
    cursor.execute("""
        INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
        SELECT
            'equipment' AS table_name,
            canonical_id AS record_id,
            'equipment_type' AS field_name,
            'NULL' AS old_value,
            CASE
                WHEN category IN ('tanks', 'main_tanks', 'light_tanks', 'heavy_tanks', 'medium_tanks') THEN 'tank'
                WHEN category IN ('field_artillery', 'anti_tank', 'anti_aircraft', 'infantry_guns', 'self_propelled_guns') THEN 'artillery'
                WHEN category IN ('halftracks') THEN 'halftrack'
                WHEN category IN ('armored_cars', 'armored_cars_reconnaissance') THEN 'armored_car'
                WHEN category IN ('trucks', 'support_vehicles', 'command_vehicles', 'recovery_vehicles', 'transport_vehicles') THEN 'vehicle'
                WHEN category IN ('fighters', 'bombers', 'reconnaissance', 'fighter_bombers', 'dive_bombers', 'torpedo_bombers', 'maritime_patrol', 'aircraft') THEN 'aircraft'
                ELSE 'unknown'
            END AS new_value,
            'type_inference' AS change_type,
            'Inferred from category: ' || category AS change_reason
        FROM equipment
        WHERE equipment_type IS NULL
    """)

    audit_count = cursor.rowcount
    print(f"Audit records created: {audit_count}\n")

    # Update equipment_type
    cursor.execute("""
        UPDATE equipment
        SET equipment_type = CASE
            WHEN category IN ('tanks', 'main_tanks', 'light_tanks', 'heavy_tanks', 'medium_tanks') THEN 'tank'
            WHEN category IN ('field_artillery', 'anti_tank', 'anti_aircraft', 'infantry_guns', 'self_propelled_guns') THEN 'artillery'
            WHEN category IN ('halftracks') THEN 'halftrack'
            WHEN category IN ('armored_cars', 'armored_cars_reconnaissance') THEN 'armored_car'
            WHEN category IN ('trucks', 'support_vehicles', 'command_vehicles', 'recovery_vehicles', 'transport_vehicles') THEN 'vehicle'
            WHEN category IN ('fighters', 'bombers', 'reconnaissance', 'fighter_bombers', 'dive_bombers', 'torpedo_bombers', 'maritime_patrol', 'aircraft') THEN 'aircraft'
            ELSE 'unknown'
        END
        WHERE equipment_type IS NULL
    """)

    updated_count = cursor.rowcount
    print(f"Equipment records updated: {updated_count}\n")

    return updated_count

def validation_report(cursor):
    """Generate validation report"""
    print("=" * 80)
    print("\n=== Validation Report ===\n")

    # Check NULL count after
    cursor.execute("SELECT COUNT(*) FROM equipment WHERE equipment_type IS NULL")
    null_count = cursor.fetchone()[0]
    print(f"Equipment with NULL equipment_type: {null_count}\n")

    # Check distribution
    cursor.execute("""
        SELECT equipment_type, COUNT(*) AS count
        FROM equipment
        GROUP BY equipment_type
        ORDER BY count DESC
    """)

    print("Equipment type distribution:")
    total = 0
    for eq_type, count in cursor.fetchall():
        type_display = eq_type if eq_type else "NULL"
        print(f"  {type_display}: {count}")
        total += count
    print(f"  TOTAL: {total}\n")

    # Check for 'unknown' type
    cursor.execute("""
        SELECT canonical_id, name, category
        FROM equipment
        WHERE equipment_type = 'unknown'
    """)

    unknown = cursor.fetchall()
    if unknown:
        print(f"Equipment with 'unknown' type: {len(unknown)}")
        for eq_id, name, category in unknown[:20]:
            print(f"  - {eq_id}: {name} (category: {category})")
        print()

    # Total populated
    cursor.execute("SELECT COUNT(*) FROM equipment WHERE equipment_type IS NOT NULL")
    populated = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM equipment")
    total_eq = cursor.fetchone()[0]

    pct = (populated / total_eq * 100) if total_eq > 0 else 0
    print(f"Equipment type populated: {populated}/{total_eq} ({pct:.1f}%)")

    print("\n" + "=" * 80)

def main():
    """Execute Phase 3B Task 5: Infer equipment_type"""

    print("=" * 80)
    print("=== Phase 3B Task 5: Infer equipment_type from category ===")
    print("=" * 80)
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Infer equipment_type
        updated_count = infer_equipment_type(cursor)

        # Commit changes
        conn.commit()

        # Validation
        validation_report(cursor)

        print("\n=== Task 5 Complete ===")
        print(f"Total records updated: {updated_count}")
        print("Transaction committed successfully!\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return 1
    finally:
        conn.close()

    return 0

if __name__ == "__main__":
    exit(main())
