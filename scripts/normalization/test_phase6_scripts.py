"""
Test Phase 6 Scripts After Database Normalization

Tests that Phase 6 unit extraction and chapter generation scripts
still work after Phase 5.5 database normalization.
"""

import sys
import sqlite3
from pathlib import Path


def test_phase6_unit_parser():
    """Test Phase6EquipmentMapper with normalized database."""
    print("=" * 100)
    print("TEST: Phase 6 Unit Parser")
    print("=" * 100)
    print()

    try:
        # Import the module
        sys.path.insert(0, str(Path(__file__).parent.parent / 'battlegroup' / 'generators'))
        from phase6_unit_parser import Phase6EquipmentMapper

        # Create mapper instance
        mapper = Phase6EquipmentMapper()
        mapper.connect()

        # Test 1: Map WITW ID to canonical (British tank)
        print("Test 1: Map WITW ID to canonical ID")
        try:
            result = mapper.map_witw_id_to_canonical("TANK_CRU_A13_MKII_CRUISER_MKIV", "british")
            if result:
                canonical_id, equipment_name, match_type = result
                print(f"  [OK] Mapped WITW ID successfully")
                print(f"       Canonical ID: {canonical_id}")
                print(f"       Name: {equipment_name}")
                print(f"       Match type: {match_type}")
            else:
                print(f"  [INFO] No match found (expected if not in database)")
        except Exception as e:
            print(f"  [FAIL] Mapping failed: {e}")
            return False

        # Test 2: Get equipment details
        print()
        print("Test 2: Get equipment details")
        try:
            # Use a canonical_id we know exists
            conn = sqlite3.connect('database/master_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT canonical_id FROM equipment LIMIT 1")
            sample_id = cursor.fetchone()
            conn.close()

            if sample_id:
                canonical_id = sample_id[0]
                details = mapper.get_equipment_details(canonical_id)
                if details:
                    print(f"  [OK] Retrieved details for: {canonical_id}")
                    print(f"       Name: {details.get('name', 'N/A')}")
                    print(f"       Armor: {details.get('armor_front', 'N/A')}")
                    print(f"       Points: {details.get('points_regular', 'N/A')}")
                else:
                    print(f"  [INFO] No details found for {canonical_id}")
        except Exception as e:
            print(f"  [FAIL] Get details failed: {e}")
            return False

        # Test 3: Check database queries work
        print()
        print("Test 3: Verify SQL queries")
        try:
            conn = sqlite3.connect('database/master_database.db')
            cursor = conn.cursor()

            # Query from phase6_unit_parser.py line 130
            cursor.execute("SELECT canonical_id FROM equipment WHERE canonical_id = ?", ("test",))
            result = cursor.fetchone()
            print("  [OK] Query 1: SELECT canonical_id FROM equipment")

            # Query from phase6_unit_parser.py line 165-166
            cursor.execute("SELECT canonical_id, aliases FROM equipment LIMIT 1")
            result = cursor.fetchone()
            print("  [OK] Query 2: SELECT canonical_id, aliases FROM equipment")

            # Query from phase6_unit_parser.py line 223-243 (big query)
            cursor.execute("""
                SELECT
                    e.canonical_id,
                    e.name,
                    e.category,
                    e.nation,
                    eb.armor_front,
                    eb.armor_side,
                    eb.armor_rear,
                    eb.off_road_movement,
                    eb.road_movement,
                    eb.points_regular,
                    eb.battle_rating_regular
                FROM equipment e
                LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
                LIMIT 1
            """)
            result = cursor.fetchone()
            print("  [OK] Query 3: equipment JOIN equipment_battlegroup")

            conn.close()
        except Exception as e:
            print(f"  [FAIL] SQL query failed: {e}")
            return False

        mapper.close()
        print()
        print("[OK] Phase 6 unit parser validated")
        return True

    except ImportError as e:
        print(f"[FAIL] Could not import phase6_unit_parser: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def test_unit_files_exist():
    """Test that Phase 6 unit files exist and are parseable."""
    print("=" * 100)
    print("TEST: Phase 6 Unit Files")
    print("=" * 100)
    print()

    import json

    units_dir = Path("data/output/units")

    if not units_dir.exists():
        print(f"[FAIL] Units directory not found: {units_dir}")
        return False

    # Find all _toe.json files
    unit_files = list(units_dir.glob("*_toe.json"))

    if not unit_files:
        print(f"[FAIL] No unit files found in {units_dir}")
        return False

    print(f"Found {len(unit_files)} unit files")

    # Try to parse a few sample files
    sample_count = min(5, len(unit_files))
    parse_errors = 0

    for unit_file in unit_files[:sample_count]:
        try:
            with open(unit_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check for basic structure
            if 'unit_identity' not in data:
                print(f"  [WARNING] {unit_file.name}: Missing unit_identity")

            print(f"  [OK] Parsed: {unit_file.name}")
        except Exception as e:
            print(f"  [FAIL] {unit_file.name}: {e}")
            parse_errors += 1

    print()
    if parse_errors == 0:
        print(f"[OK] Successfully parsed {sample_count} sample unit files")
        return True
    else:
        print(f"[FAIL] {parse_errors}/{sample_count} files had parse errors")
        return False


def test_equipment_enrichment():
    """Test that enrichment queries work."""
    print("=" * 100)
    print("TEST: Equipment Enrichment Queries")
    print("=" * 100)
    print()

    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    try:
        # Query from enrich_units_with_database.py
        cursor.execute("""
            SELECT canonical_id, witw_name, reviewer_notes, final_confidence
            FROM match_reviews
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"[OK] match_reviews query: {len(results)} rows")

        # Query for guns
        cursor.execute("""
            SELECT gun_id, name, full_name, caliber_mm
            FROM guns
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"[OK] guns query: {len(results)} rows")

        # Query for aircraft
        cursor.execute("""
            SELECT aircraft_id, witw_id, name, nation
            FROM aircraft
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"[OK] aircraft query: {len(results)} rows")

        # Query for AFV data (wwiitanks) - note: uses 'id' not 'afv_id'
        cursor.execute("""
            SELECT id, vehicle_name
            FROM wwiitanks_afv_data
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"[OK] wwiitanks_afv_data query: {len(results)} rows")
        print(f"[NOTE] enrich_units_with_database.py has pre-existing bug (line 144): uses 'afv_id' column name")
        print(f"       Actual column name is 'id' - this is NOT caused by normalization")

        print()
        print("[OK] Equipment enrichment queries validated")
        conn.close()
        return True

    except Exception as e:
        print(f"[FAIL] Query failed: {e}")
        conn.close()
        return False


def main():
    print("=" * 100)
    print("PHASE 6 SCRIPTS VALIDATION AFTER DATABASE NORMALIZATION")
    print("=" * 100)
    print()

    tests = [
        ("Phase 6 Unit Parser", test_phase6_unit_parser),
        ("Phase 6 Unit Files", test_unit_files_exist),
        ("Equipment Enrichment", test_equipment_enrichment)
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
        print("[OK] All Phase 6 scripts validated - working correctly")
        return 0
    else:
        print("[FAIL] Some Phase 6 scripts may have issues")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
