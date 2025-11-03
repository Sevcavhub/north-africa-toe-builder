#!/usr/bin/env python3
"""
Phase 3B Task 6: Orphaned Foreign Key Investigation

Investigate why ALL 953 unit_equipment records have NULL equipment_id.
Determine root cause and recommend fix strategy.

This is INVESTIGATION ONLY - no fixes will be applied.
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("database/master_database.db")

def examine_schema(cursor):
    """Step 1: Examine unit_equipment schema"""
    print("=" * 80)
    print("STEP 1: SCHEMA EXAMINATION")
    print("=" * 80)
    print()

    # Table structure
    cursor.execute("PRAGMA table_info(unit_equipment)")
    columns = cursor.fetchall()

    print("unit_equipment table structure:")
    for col in columns:
        col_id, name, dtype, notnull, default, pk = col
        pk_marker = " (PK)" if pk else ""
        null_marker = " NOT NULL" if notnull else ""
        default_marker = f" DEFAULT {default}" if default else ""
        print(f"  - {name}: {dtype}{pk_marker}{null_marker}{default_marker}")
    print()

    # Foreign keys
    cursor.execute("PRAGMA foreign_key_list(unit_equipment)")
    fks = cursor.fetchall()

    print("Foreign key constraints:")
    if fks:
        for fk in fks:
            fk_id, seq, table, from_col, to_col, on_update, on_delete, match = fk
            print(f"  - {from_col} -> {table}.{to_col}")
    else:
        print("  (No foreign key constraints found)")
    print()

    # Record count
    cursor.execute("SELECT COUNT(*) FROM unit_equipment")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM unit_equipment WHERE equipment_id IS NULL")
    null_count = cursor.fetchone()[0]

    print(f"Record counts:")
    print(f"  Total: {total}")
    print(f"  NULL equipment_id: {null_count} ({null_count/total*100:.1f}%)")
    print()

def examine_sample_records(cursor):
    """Step 2: Examine sample records"""
    print("=" * 80)
    print("STEP 2: SAMPLE RECORD EXAMINATION")
    print("=" * 80)
    print()

    cursor.execute("SELECT * FROM unit_equipment LIMIT 10")
    records = cursor.fetchall()

    if not records:
        print("No records found in unit_equipment table")
        return

    # Get column names
    col_names = [desc[0] for desc in cursor.description]

    print(f"Sample records (first 10 of {len(records)}):")
    print()

    for i, record in enumerate(records, 1):
        print(f"Record {i}:")
        for col_name, value in zip(col_names, record):
            print(f"  {col_name}: {value}")
        print()

def check_import_source(cursor):
    """Step 3: Check import log for unit_equipment"""
    print("=" * 80)
    print("STEP 3: IMPORT SOURCE CHECK")
    print("=" * 80)
    print()

    # Check if import_log table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='import_log'")
    if not cursor.fetchone():
        print("import_log table does not exist")
        print()
        return

    # Check import_log schema first
    cursor.execute("PRAGMA table_info(import_log)")
    import_cols = [col[1] for col in cursor.fetchall()]

    if 'table_name' in import_cols:
        cursor.execute("SELECT * FROM import_log WHERE table_name = 'unit_equipment'")
        import_records = cursor.fetchall()

        if import_records:
            col_names = [desc[0] for desc in cursor.description]
            print(f"Import log entries for unit_equipment: {len(import_records)}")
            print()
            for record in import_records:
                for col_name, value in zip(col_names, record):
                    print(f"  {col_name}: {value}")
                print()
        else:
            print("No import log entries found for unit_equipment")
            print()
    else:
        print(f"import_log columns: {', '.join(import_cols)}")
        print("(table_name column not found - checking all records)")
        cursor.execute("SELECT * FROM import_log LIMIT 5")
        import_records = cursor.fetchall()
        if import_records:
            col_names = [desc[0] for desc in cursor.description]
            print(f"\nSample import_log records:")
            for record in import_records[:3]:
                record_dict = dict(zip(col_names, record))
                print(f"  {record_dict}")
        print()

def cross_reference_units(cursor):
    """Step 4: Cross-reference with units table"""
    print("=" * 80)
    print("STEP 4: UNITS TABLE CROSS-REFERENCE")
    print("=" * 80)
    print()

    # Check if units table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='units'")
    if not cursor.fetchone():
        print("units table does not exist")
        print()
        return

    # First check units table schema
    cursor.execute("PRAGMA table_info(units)")
    units_cols = [col[1] for col in cursor.fetchall()]

    # Use designation instead of name
    name_col = 'designation' if 'designation' in units_cols else 'name'

    # Check unit_equipment references to units
    cursor.execute(f"""
        SELECT
            ue.unit_id,
            ue.equipment_id,
            ue.variant_name,
            u.{name_col} AS unit_name,
            u.nation AS unit_nation
        FROM unit_equipment ue
        LEFT JOIN units u ON ue.unit_id = u.unit_id
        LIMIT 10
    """)

    joined = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]

    print("unit_equipment joined with units (first 10):")
    print()

    cursor.execute("""
        SELECT COUNT(*)
        FROM unit_equipment ue
        LEFT JOIN units u ON ue.unit_id = u.unit_id
        WHERE u.unit_id IS NOT NULL
    """)
    total_valid = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM unit_equipment")
    total = cursor.fetchone()[0]

    print(f"Valid unit_id references: {total_valid}/{total} ({total_valid/total*100:.1f}%)")
    print()

    if joined:
        print("Sample joined records:")
        for record in joined[:5]:
            record_dict = dict(zip(col_names, record))
            print(f"  unit_id: {record_dict.get('unit_id')}")
            print(f"    unit_name: {record_dict.get('unit_name')}")
            print(f"    variant_name: {record_dict.get('variant_name')}")
            print(f"    equipment_id: {record_dict.get('equipment_id')}")
            print()
        print()

def analyze_witw_sources(cursor):
    """Step 5: Analyze WITW source tables"""
    print("=" * 80)
    print("STEP 5: WITW SOURCE TABLE ANALYSIS")
    print("=" * 80)
    print()

    # Check for WITW-related tables
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name LIKE '%witw%'
        ORDER BY name
    """)
    witw_tables = [row[0] for row in cursor.fetchall()]

    print(f"WITW-related tables: {len(witw_tables)}")
    for table in witw_tables:
        print(f"  - {table}")
    print()

    # Check witw_toe_ob if it exists
    if 'witw_toe_ob' in witw_tables:
        print("Examining witw_toe_ob table:")
        cursor.execute("PRAGMA table_info(witw_toe_ob)")
        cols = cursor.fetchall()
        print("  Columns:")
        for col in cols:
            print(f"    - {col[1]}: {col[2]}")

        cursor.execute("SELECT COUNT(*) FROM witw_toe_ob")
        count = cursor.fetchone()[0]
        print(f"  Record count: {count}")

        cursor.execute("SELECT * FROM witw_toe_ob LIMIT 5")
        sample = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        print("  Sample records:")
        for record in sample:
            record_dict = dict(zip(col_names, record))
            print(f"    {record_dict}")
        print()

def determine_root_cause(cursor):
    """Step 6: Root cause analysis and recommendations"""
    print("=" * 80)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 80)
    print()

    # Gather key metrics
    cursor.execute("SELECT COUNT(*) FROM unit_equipment WHERE equipment_id IS NULL")
    null_equipment = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM unit_equipment")
    total_ue = cursor.fetchone()[0]

    # Check if units table exists and has valid references
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='units'")
    units_exists = cursor.fetchone() is not None

    valid_unit_refs = 0
    if units_exists:
        cursor.execute("""
            SELECT COUNT(*)
            FROM unit_equipment ue
            INNER JOIN units u ON ue.unit_id = u.unit_id
        """)
        valid_unit_refs = cursor.fetchone()[0]

    # Check for any other fields that might identify equipment
    cursor.execute("PRAGMA table_info(unit_equipment)")
    columns = [col[1] for col in cursor.fetchall()]

    # Check variant_name population
    cursor.execute("SELECT COUNT(*) FROM unit_equipment WHERE variant_name IS NOT NULL")
    variant_populated = cursor.fetchone()[0]

    # Sample variant names
    cursor.execute("SELECT DISTINCT variant_name FROM unit_equipment WHERE variant_name IS NOT NULL LIMIT 10")
    sample_variants = [row[0] for row in cursor.fetchall()]

    print("KEY FINDINGS:")
    print()
    print(f"1. Total unit_equipment records: {total_ue}")
    print(f"2. Records with NULL equipment_id: {null_equipment} (100%)")
    print(f"3. Records with variant_name populated: {variant_populated} ({variant_populated/total_ue*100:.1f}%)" if total_ue > 0 else "3. No records")
    print(f"4. Valid unit_id references: {valid_unit_refs} ({valid_unit_refs/total_ue*100:.1f}%)" if total_ue > 0 else "4. No valid unit_id references")
    print(f"5. unit_equipment columns: {', '.join(columns)}")
    print()
    print(f"6. Sample variant_name values:")
    for variant in sample_variants[:5]:
        print(f"   - {variant}")
    print()

    # Determine most likely cause
    print("PROBABLE ROOT CAUSE:")
    print()

    if variant_populated > 0 and variant_populated == total_ue:
        print("RESULT: Outcome E: ARCHITECTURAL DESIGN - variant_name USED INSTEAD OF equipment_id")
        print()
        print("ANALYSIS:")
        print("  - ALL records have variant_name populated (100%)")
        print("  - variant_name identifies equipment (e.g., 'SdKfz 222', 'Opel Blitz')")
        print("  - equipment_id FK is OPTIONAL, not REQUIRED")
        print("  - This is a valid design choice, not a bug")
        print()
        print("IMPLICATIONS:")
        print("  - unit_equipment uses string-based equipment identification")
        print("  - equipment table uses canonical_id (e.g., 'GER_SDKFZ_222')")
        print("  - Linkage requires name matching (like Task 3: Name Variants)")
        print()
        print("RECOMMENDED ACTION:")
        print("  1. Create mapping: variant_name -> equipment.canonical_id")
        print("  2. Populate equipment_id using variant_name matching")
        print("  3. Similar to Phase 3B Task 3 (name variant mapping)")
        print("  4. Estimated time: 2-3 hours")
        print()
        print("ALTERNATIVE:")
        print("  - Leave as-is if variant_name is sufficient for queries")
        print("  - Document that equipment_id is optional")
        print("  - Use variant_name for equipment identification")
        print("  - No normalization work needed")
    elif null_equipment == total_ue and total_ue > 0:
        if valid_unit_refs > 0:
            print("RESULT: Outcome A: IMPORT BUG")
            print("  - equipment_id should have been populated during import")
            print("  - unit_id references are valid, suggesting partial import")
            print("  - equipment_id field was not mapped correctly")
            print()
            print("RECOMMENDED FIX:")
            print("  1. Identify source data for equipment assignments")
            print("  2. Write re-import script to populate equipment_id")
            print("  3. Estimated time: 2-3 hours")
        else:
            print("RESULT: Outcome D: TABLE IS LEGACY/UNUSED")
            print("  - No valid unit_id references")
            print("  - All equipment_id are NULL")
            print("  - Table appears to be deprecated or never populated")
            print()
            print("RECOMMENDED ACTION:")
            print("  1. Document as unused table")
            print("  2. Exclude from future normalization work")
            print("  3. Consider dropping table or marking as deprecated")
            print("  4. Estimated time: 30 minutes (documentation only)")
    else:
        print("RESULT: Outcome C: MISSING SOURCE DATA")
        print("  - WITW data may not include unit→equipment linkages")
        print("  - Would require manual data entry or historical sources")
        print()
        print("RECOMMENDED ACTION:")
        print("  - OUT OF SCOPE for Phase 3")
        print("  - Document as future work")
        print("  - Estimated time: Days-weeks (manual research)")

    print()

def main():
    """Execute Phase 3B Task 6: Orphaned FK Investigation"""

    print("=" * 80)
    print("=== Phase 3B Task 6: Orphaned Foreign Key Investigation ===")
    print("=" * 80)
    print()
    print("OBJECTIVE: Investigate why ALL 953 unit_equipment records have NULL equipment_id")
    print("SCOPE: Investigation only - no fixes will be applied")
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Step 1: Schema examination
        examine_schema(cursor)

        # Step 2: Sample records
        examine_sample_records(cursor)

        # Step 3: Import source
        check_import_source(cursor)

        # Step 4: Cross-reference units
        cross_reference_units(cursor)

        # Step 5: WITW sources
        analyze_witw_sources(cursor)

        # Step 6: Root cause determination
        determine_root_cause(cursor)

        print("=" * 80)
        print("=== Task 6 Investigation Complete ===")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Review findings above")
        print("  2. Determine if fix is in-scope for Phase 3 or defer")
        print("  3. Document decision in orphaned_fk_analysis.md")
        print()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()

    return 0

if __name__ == "__main__":
    exit(main())
