"""
Validation Script: Test Existing Scripts After Database Normalization

Tests that critical Phase 9B scripts still work after Phase 5.5 schema changes.
"""

import sqlite3
import sys
from pathlib import Path


def test_database_structure():
    """Test 1: Verify database structure is as expected."""
    print("=" * 100)
    print("TEST 1: DATABASE STRUCTURE")
    print("=" * 100)
    print()

    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    # Check critical tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    expected_tables = [
        'equipment',
        'equipment_battlegroup',
        'equipment_master_new',
        'equipment_name_variants_new',
        'bg_reference_vehicles',
        'bg_reference_guns',
        'bg_reference_organizations',
        'bg_special_rules',
        'equipment_special_rules'
    ]

    missing = []
    for table in expected_tables:
        if table not in tables:
            missing.append(table)

    if missing:
        print(f"[FAIL] Missing tables: {missing}")
        return False
    else:
        print(f"[OK] All {len(expected_tables)} critical tables present")

    # Check equipment table has master_id column
    cursor.execute("PRAGMA table_info(equipment)")
    equipment_cols = [col[1] for col in cursor.fetchall()]

    if 'master_id' not in equipment_cols:
        print("[FAIL] equipment table missing master_id column")
        return False
    else:
        print("[OK] equipment table has master_id column")

    # Check equipment_battlegroup table structure
    cursor.execute("PRAGMA table_info(equipment_battlegroup)")
    eb_cols = [col[1] for col in cursor.fetchall()]

    required_eb_cols = ['equipment_id', 'armor_front', 'armor_side', 'armor_rear',
                        'off_road_movement', 'road_movement',
                        'points_regular', 'points_veteran',
                        'battle_rating_regular', 'battle_rating_veteran',
                        'reference_vehicle_id', 'reference_gun_id']
    missing_cols = [col for col in required_eb_cols if col not in eb_cols]

    if missing_cols:
        print(f"[FAIL] equipment_battlegroup missing columns: {missing_cols}")
        return False
    else:
        print("[OK] equipment_battlegroup has all required columns")

    print()
    conn.close()
    return True


def test_equipment_queries():
    """Test 2: Verify common equipment queries still work."""
    print("=" * 100)
    print("TEST 2: EQUIPMENT QUERIES")
    print("=" * 100)
    print()

    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    # Query 1: Get equipment with BattleGroup stats
    try:
        cursor.execute("""
            SELECT e.canonical_id, e.name, eb.armor_front, eb.off_road_movement,
                   eb.points_regular, eb.battle_rating_regular
            FROM equipment e
            LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"[OK] Equipment + BattleGroup stats query: {len(results)} rows")
    except Exception as e:
        print(f"[FAIL] Equipment + BattleGroup stats query failed: {e}")
        return False

    # Query 2: Get equipment with master linkage
    try:
        cursor.execute("""
            SELECT e.canonical_id, e.name, e.master_id, emn.canonical_name, emn.display_name
            FROM equipment e
            LEFT JOIN equipment_master_new emn ON e.master_id = emn.master_id
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"[OK] Equipment + Master linkage query: {len(results)} rows")

        # Check linkage percentage
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN master_id IS NOT NULL THEN 1 ELSE 0 END) as linked
            FROM equipment
        """)
        total, linked = cursor.fetchone()
        pct = 100 * linked / total if total > 0 else 0
        print(f"[OK] Equipment linkage: {linked}/{total} ({pct:.1f}%)")

    except Exception as e:
        print(f"[FAIL] Equipment + Master linkage query failed: {e}")
        return False

    # Query 3: Get bg_reference_vehicles with master linkage
    try:
        cursor.execute("""
            SELECT brv.id, brv.name, brv.master_id, emn.canonical_name
            FROM bg_reference_vehicles brv
            LEFT JOIN equipment_master_new emn ON brv.master_id = emn.master_id
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"[OK] bg_reference_vehicles + Master linkage query: {len(results)} rows")

    except Exception as e:
        print(f"[FAIL] bg_reference_vehicles + Master linkage query failed: {e}")
        return False

    # Query 4: Get equipment special rules
    try:
        cursor.execute("""
            SELECT e.name, sr.name, sr.description
            FROM equipment e
            JOIN equipment_special_rules esr ON e.canonical_id = esr.equipment_id
            JOIN bg_special_rules sr ON esr.rule_id = sr.rule_id
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"[OK] Equipment special rules query: {len(results)} rows")

    except Exception as e:
        print(f"[FAIL] Equipment special rules query failed: {e}")
        return False

    print()
    conn.close()
    return True


def test_name_variant_system():
    """Test 3: Verify name variant system works."""
    print("=" * 100)
    print("TEST 3: NAME VARIANT SYSTEM")
    print("=" * 100)
    print()

    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    # Check variant coverage
    cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
    total_masters = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT master_id) FROM equipment_name_variants_new")
    masters_with_variants = cursor.fetchone()[0]

    coverage_pct = 100 * masters_with_variants / total_masters if total_masters > 0 else 0

    if coverage_pct < 100:
        print(f"[FAIL] Name variant coverage: {masters_with_variants}/{total_masters} ({coverage_pct:.1f}%)")
        return False
    else:
        print(f"[OK] Name variant coverage: {masters_with_variants}/{total_masters} ({coverage_pct:.1f}%)")

    # Check variant lookup works
    try:
        cursor.execute("""
            SELECT emn.canonical_name, emn.display_name, COUNT(env.variant_id) as variant_count
            FROM equipment_master_new emn
            LEFT JOIN equipment_name_variants_new env ON emn.master_id = env.master_id
            GROUP BY emn.master_id
            ORDER BY variant_count DESC
            LIMIT 10
        """)
        results = cursor.fetchall()
        print(f"[OK] Name variant lookup query: {len(results)} top items")

        # Show top 3 with most variants
        for canonical, display, count in results[:3]:
            print(f"  - {display} ({canonical}): {count} variants")

    except Exception as e:
        print(f"[FAIL] Name variant lookup failed: {e}")
        return False

    print()
    conn.close()
    return True


def test_database_views():
    """Test 4: Verify database views work."""
    print("=" * 100)
    print("TEST 4: DATABASE VIEWS")
    print("=" * 100)
    print()

    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    views = [
        'v_equipment_complete',
        'v_equipment_by_nation',
        'v_name_variants'
    ]

    for view in views:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {view}")
            count = cursor.fetchone()[0]
            print(f"[OK] View '{view}': {count} rows")
        except Exception as e:
            print(f"[FAIL] View '{view}' failed: {e}")
            return False

    print()
    conn.close()
    return True


def test_canonical_name_format():
    """Test 5: Verify canonical names follow new format."""
    print("=" * 100)
    print("TEST 5: CANONICAL NAME FORMAT")
    print("=" * 100)
    print()

    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    # Check for old eq_ prefix
    cursor.execute("""
        SELECT COUNT(*) FROM equipment_master_new
        WHERE canonical_name LIKE 'eq_%'
    """)
    old_format_count = cursor.fetchone()[0]

    if old_format_count > 0:
        print(f"[FAIL] Found {old_format_count} items with old 'eq_' prefix")
        return False
    else:
        print("[OK] No items with old 'eq_' prefix")

    # Show sample canonical names
    cursor.execute("""
        SELECT canonical_name, display_name
        FROM equipment_master_new
        LIMIT 10
    """)
    samples = cursor.fetchall()

    print()
    print("Sample canonical names (new format):")
    for canonical, display in samples[:5]:
        print(f"  - {canonical} ({display})")

    print()
    conn.close()
    return True


def main():
    print("=" * 100)
    print("VALIDATION: EXISTING SCRIPTS AFTER DATABASE NORMALIZATION")
    print("=" * 100)
    print()

    tests = [
        ("Database Structure", test_database_structure),
        ("Equipment Queries", test_equipment_queries),
        ("Name Variant System", test_name_variant_system),
        ("Database Views", test_database_views),
        ("Canonical Name Format", test_canonical_name_format)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print()

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print()
    print(f"Tests: {len(results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print()

    if failed == 0:
        print("[OK] All validation tests passed - existing scripts should work")
        return 0
    else:
        print("[FAIL] Some validation tests failed - scripts may be broken")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
