"""
QA Validation Suite for Phase 5.5 Database Normalization

Comprehensive validation to ensure all normalization phases completed successfully.
Tests data integrity, foreign key links, coverage, and data quality.
"""

import sqlite3
from typing import Dict, List, Tuple, Any


class ValidationResult:
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = True
        self.errors = []
        self.warnings = []
        self.info = []

    def add_error(self, message: str):
        self.passed = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_info(self, message: str):
        self.info.append(message)


class QAValidationSuite:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.results = []

    def run_all_tests(self):
        """Run complete QA validation suite."""
        print("=" * 100)
        print("QA VALIDATION SUITE - PHASE 5.5 DATABASE NORMALIZATION")
        print("=" * 100)
        print()

        # Test categories
        self.test_data_integrity()
        self.test_foreign_key_integrity()
        self.test_coverage_metrics()
        self.test_data_quality()
        self.test_database_views()
        self.test_no_data_loss()

        # Summary
        self.print_summary()

        return all(r.passed for r in self.results)

    def test_data_integrity(self):
        """Test 1: Data Integrity Checks."""
        print("=" * 100)
        print("TEST 1: DATA INTEGRITY")
        print("=" * 100)
        print()

        cursor = self.conn.cursor()

        # Test 1.1: No duplicate canonical names
        result = ValidationResult("1.1 No Duplicate Canonical Names")
        cursor.execute("""
            SELECT canonical_name, COUNT(*) as count
            FROM equipment_master_new
            GROUP BY canonical_name
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()

        if duplicates:
            result.add_error(f"Found {len(duplicates)} duplicate canonical names")
            for name, count in duplicates[:5]:
                result.add_error(f"  - '{name}': {count} occurrences")
        else:
            result.add_info("No duplicate canonical names found")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

        # Test 1.2: All critical fields populated
        result = ValidationResult("1.2 Critical Fields Populated")
        cursor.execute("""
            SELECT COUNT(*) FROM equipment_master_new
            WHERE canonical_name IS NULL OR canonical_name = ''
               OR display_name IS NULL OR display_name = ''
        """)
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            result.add_error(f"{null_count} records have NULL/empty canonical_name or display_name")
        else:
            result.add_info("All records have canonical_name and display_name populated")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

    def test_foreign_key_integrity(self):
        """Test 2: Foreign Key Integrity."""
        print("=" * 100)
        print("TEST 2: FOREIGN KEY INTEGRITY")
        print("=" * 100)
        print()

        cursor = self.conn.cursor()

        # Test 2.1: Equipment master_id links valid
        result = ValidationResult("2.1 Equipment master_id Links Valid")
        cursor.execute("""
            SELECT COUNT(*) FROM equipment
            WHERE master_id IS NOT NULL
              AND master_id NOT IN (SELECT master_id FROM equipment_master_new)
        """)
        invalid_links = cursor.fetchone()[0]

        if invalid_links > 0:
            result.add_error(f"{invalid_links} equipment records have invalid master_id")
        else:
            result.add_info("All equipment master_id links are valid")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

        # Test 2.2: Name variant master_id links valid
        result = ValidationResult("2.2 Name Variant master_id Links Valid")
        cursor.execute("""
            SELECT COUNT(*) FROM equipment_name_variants_new
            WHERE master_id NOT IN (SELECT master_id FROM equipment_master_new)
        """)
        invalid_links = cursor.fetchone()[0]

        if invalid_links > 0:
            result.add_error(f"{invalid_links} name variant records have invalid master_id")
        else:
            result.add_info("All name variant master_id links are valid")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

    def test_coverage_metrics(self):
        """Test 3: Coverage Metrics."""
        print("=" * 100)
        print("TEST 3: COVERAGE METRICS")
        print("=" * 100)
        print()

        cursor = self.conn.cursor()

        # Test 3.1: Equipment linkage
        result = ValidationResult("3.1 Equipment Table Linkage")
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN master_id IS NOT NULL THEN 1 ELSE 0 END) as linked
            FROM equipment
        """)
        total, linked = cursor.fetchone()
        pct = 100 * linked / total if total > 0 else 0

        if pct < 100:
            result.add_warning(f"Equipment linkage: {linked}/{total} ({pct:.1f}%) - expected 100%")
        else:
            result.add_info(f"Equipment linkage: {linked}/{total} ({pct:.1f}%)")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for warning in result.warnings:
            print(f"  [WARNING] {warning}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

        # Test 3.2: Name variant coverage
        result = ValidationResult("3.2 Name Variant Master Coverage")
        cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
        total_masters = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT master_id) FROM equipment_name_variants_new")
        masters_with_variants = cursor.fetchone()[0]

        coverage_pct = 100 * masters_with_variants / total_masters if total_masters > 0 else 0

        if coverage_pct < 100:
            result.add_error(f"Name variant coverage: {masters_with_variants}/{total_masters} ({coverage_pct:.1f}%) - expected 100%")
        else:
            result.add_info(f"Name variant coverage: {masters_with_variants}/{total_masters} ({coverage_pct:.1f}%)")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

        # Test 3.3: bg_reference linkage (informational)
        result = ValidationResult("3.3 BG Reference Linkage (Informational)")

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN master_id IS NOT NULL THEN 1 ELSE 0 END) as linked
            FROM bg_reference_vehicles
        """)
        total_vehicles, linked_vehicles = cursor.fetchone()
        pct_vehicles = 100 * linked_vehicles / total_vehicles if total_vehicles > 0 else 0

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN master_id IS NOT NULL THEN 1 ELSE 0 END) as linked
            FROM bg_reference_guns
        """)
        total_guns, linked_guns = cursor.fetchone()
        pct_guns = 100 * linked_guns / total_guns if total_guns > 0 else 0

        result.add_info(f"bg_reference_vehicles: {linked_vehicles}/{total_vehicles} ({pct_vehicles:.1f}%)")
        result.add_info(f"bg_reference_guns: {linked_guns}/{total_guns} ({pct_guns:.1f}%)")
        result.add_info("Note: Low linkage expected - requires fuzzy matching (Phase 9B work)")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for info in result.info:
            print(f"  [INFO] {info}")
        print()

    def test_data_quality(self):
        """Test 4: Data Quality Checks."""
        print("=" * 100)
        print("TEST 4: DATA QUALITY")
        print("=" * 100)
        print()

        cursor = self.conn.cursor()

        # Test 4.1: Canonical name format
        result = ValidationResult("4.1 Canonical Name Format")
        cursor.execute("""
            SELECT canonical_name FROM equipment_master_new
            WHERE canonical_name LIKE 'eq_%'
        """)
        bad_names = cursor.fetchall()

        if bad_names:
            result.add_error(f"Found {len(bad_names)} names with old 'eq_' prefix format")
            for name, in bad_names[:5]:
                result.add_error(f"  - {name}")
        else:
            result.add_info("All canonical names follow simple format (no eq_ prefix)")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

        # Test 4.2: Name variant sources valid
        result = ValidationResult("4.2 Name Variant Sources Valid")
        cursor.execute("""
            SELECT DISTINCT variant_source FROM equipment_name_variants_new
            WHERE variant_source NOT IN ('onwar', 'wwiitanks', 'bg_pdf', 'witw', 'manual')
        """)
        invalid_sources = cursor.fetchall()

        if invalid_sources:
            result.add_error(f"Found {len(invalid_sources)} invalid variant sources")
            for source, in invalid_sources:
                result.add_error(f"  - {source}")
        else:
            result.add_info("All variant sources are valid")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

    def test_database_views(self):
        """Test 5: Database Views."""
        print("=" * 100)
        print("TEST 5: DATABASE VIEWS")
        print("=" * 100)
        print()

        cursor = self.conn.cursor()

        views_to_test = [
            'v_equipment_complete',
            'v_equipment_by_nation',
            'v_name_variants'
        ]

        for view_name in views_to_test:
            result = ValidationResult(f"5.{views_to_test.index(view_name) + 1} View '{view_name}' Functional")

            try:
                cursor.execute(f"SELECT COUNT(*) FROM {view_name}")
                count = cursor.fetchone()[0]
                result.add_info(f"View returns {count} rows")
            except sqlite3.Error as e:
                result.add_error(f"View query failed: {e}")

            self.results.append(result)
            print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
            for error in result.errors:
                print(f"  [ERROR] {error}")
            for info in result.info:
                print(f"  [OK] {info}")
            print()

    def test_no_data_loss(self):
        """Test 6: No Data Loss."""
        print("=" * 100)
        print("TEST 6: NO DATA LOSS")
        print("=" * 100)
        print()

        cursor = self.conn.cursor()

        # Test 6.1: Equipment count maintained
        result = ValidationResult("6.1 Equipment Records Maintained")
        cursor.execute("SELECT COUNT(*) FROM equipment")
        equipment_count = cursor.fetchone()[0]

        expected_count = 469  # From Phase 5
        if equipment_count != expected_count:
            result.add_error(f"Equipment count mismatch: {equipment_count} (expected {expected_count})")
        else:
            result.add_info(f"Equipment count maintained: {equipment_count} records")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for error in result.errors:
            print(f"  [ERROR] {error}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

        # Test 6.2: Master table size reasonable
        result = ValidationResult("6.2 Master Table Size Reasonable")
        cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
        master_count = cursor.fetchone()[0]

        # Expected range: 1,100-1,200 (after de-duplication)
        if master_count < 1000 or master_count > 1500:
            result.add_warning(f"Master count outside expected range: {master_count} (expected 1,100-1,200)")
        else:
            result.add_info(f"Master table size: {master_count} unique items")

        self.results.append(result)
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.test_name}")
        for warning in result.warnings:
            print(f"  [WARNING] {warning}")
        for info in result.info:
            print(f"  [OK] {info}")
        print()

    def print_summary(self):
        """Print test summary."""
        print("=" * 100)
        print("VALIDATION SUMMARY")
        print("=" * 100)
        print()

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests

        total_errors = sum(len(r.errors) for r in self.results)
        total_warnings = sum(len(r.warnings) for r in self.results)

        print(f"Tests Run: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print()
        print(f"Total Errors: {total_errors}")
        print(f"Total Warnings: {total_warnings}")
        print()

        if failed_tests == 0 and total_errors == 0:
            print("[OK] All validation tests PASSED")
        elif failed_tests == 0 and total_warnings > 0:
            print("[OK] All tests passed with warnings")
        else:
            print("[FAIL] Validation failed - see errors above")

        print()

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="QA Validation Suite for Phase 5.5 Normalization")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')

    args = parser.parse_args()

    suite = QAValidationSuite(args.db)

    try:
        success = suite.run_all_tests()
        exit_code = 0 if success else 1
    finally:
        suite.close()

    exit(exit_code)


if __name__ == '__main__':
    main()
