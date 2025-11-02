#!/usr/bin/env python3
"""
Quick Validation - Test that all Step 5 components can be imported and have core functionality
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 80)
    print("QUICK VALIDATION - STEP 5 COMPONENTS")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    # Part 1: Datacard Generator
    try:
        from scripts.battlegroup.generators.datacard_generator import DatacardGenerator
        generator = DatacardGenerator()
        print("[PASS] Part 1: Datacard Generator")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Part 1: Datacard Generator - {e}")
        failed += 1

    # Part 2: Special Rules Database (check table exists)
    try:
        import sqlite3
        conn = sqlite3.connect(project_root / "database" / "master_database.db")
        cursor = conn.execute("SELECT COUNT(*) FROM bg_special_rules")
        count = cursor.fetchone()[0]
        cursor2 = conn.execute("SELECT COUNT(*) FROM equipment_special_rules")
        linkages = cursor2.fetchone()[0]
        conn.close()
        print(f"[PASS] Part 2: Special Rules Database - {count} rules, {linkages} linkages")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Part 2: Special Rules Database - {e}")
        failed += 1

    # Part 3: Force Roster Builder
    try:
        from scripts.battlegroup.generators.force_roster_builder_v2 import ForceRosterBuilder
        print("[PASS] Part 3: Force Roster Builder")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Part 3: Force Roster Builder - {e}")
        failed += 1

    # Part 4A: Random Scenario Generator
    try:
        from scripts.battlegroup.generators.random_scenario_generator import RandomScenarioGenerator
        generator = RandomScenarioGenerator()
        print("[PASS] Part 4A: Random Scenario Generator")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Part 4A: Random Scenario Generator - {e}")
        failed += 1

    # Part 4B: Historical Scenario Builder (check file exists)
    try:
        historical_file = project_root / "scripts" / "battlegroup" / "generators" / "historical_scenario_generator.py"
        if historical_file.exists():
            print("[PASS] Part 4B: Historical Scenario Generator file exists")
            passed += 1
        else:
            print("[FAIL] Part 4B: Historical Scenario Generator file not found")
            failed += 1
    except Exception as e:
        print(f"[FAIL] Part 4B: Historical Scenario Generator - {e}")
        failed += 1

    # Part 5: Book Structure Generator (check file exists)
    try:
        book_file = project_root / "scripts" / "battlegroup" / "generators" / "book_structure_generator.py"
        if book_file.exists():
            print("[PASS] Part 5: Book Structure Generator file exists")
            passed += 1
        else:
            print("[FAIL] Part 5: Book Structure Generator file not found")
            failed += 1
    except Exception as e:
        print(f"[FAIL] Part 5: Book Structure Generator - {e}")
        failed += 1

    # Part 6: Army List Generator
    try:
        from scripts.battlegroup.generators.army_list_generator import ArmyListGenerator
        generator = ArmyListGenerator()
        print("[PASS] Part 6: Army List Generator")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Part 6: Army List Generator - {e}")
        failed += 1

    # Part 6: Phase6UnitParser
    try:
        from scripts.battlegroup.generators.phase6_unit_parser import Phase6UnitParser
        parser = Phase6UnitParser()
        units = parser.get_units_for_quarter("american", "1942q4")
        print(f"[PASS] Part 6: Phase6UnitParser - found {len(units)} units")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Part 6: Phase6UnitParser - {e}")
        failed += 1

    print()
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 80)

    if failed == 0:
        print("[OK] ALL COMPONENTS OPERATIONAL")
        return 0
    else:
        print("[FAIL] SOME COMPONENTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
