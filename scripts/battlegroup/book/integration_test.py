#!/usr/bin/env python3
"""
BattleGroup Book Integration Testing

End-to-end integration tests for the complete book generation workflow.

Tests:
1. MDBook builds for all 4 books
2. Scenario validation
3. File structure verification
4. Cross-reference checking

Part of Phase 9B Step 6 (Book Generation) - Part 10.

Usage:
    python integration_test.py          # Run all tests
    python integration_test.py --quick  # Skip MDBook builds

Author: North Africa TO&E Builder
Date: November 2, 2025
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Import validation from Part 9
from validate_scenarios import validate_all_books

BOOKS_DIR = project_root / "books"


class IntegrationTester:
    """End-to-end integration testing"""

    BOOKS = ["battleaxe", "crusader", "gazala", "first_alamein"]
    EXPECTED_SCENARIOS = {
        "battleaxe": 8,
        "crusader": 12,
        "gazala": 15,
        "first_alamein": 10
    }

    def __init__(self, skip_builds: bool = False):
        self.skip_builds = skip_builds
        self.results = []

    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("="*80)
        print("BATTLEGROUP BOOK GENERATION - INTEGRATION TESTS")
        print("="*80)
        print()

        all_passed = True

        # Test 1: File Structure
        print("[TEST 1] Verifying file structure...")
        if self.test_file_structure():
            print("[PASS] File structure verification passed\n")
        else:
            print("[FAIL] File structure verification failed\n")
            all_passed = False

        # Test 2: Scenario Counts
        print("[TEST 2] Verifying scenario counts...")
        if self.test_scenario_counts():
            print("[PASS] Scenario count verification passed\n")
        else:
            print("[FAIL] Scenario count verification failed\n")
            all_passed = False

        # Test 3: MDBook Builds (optional)
        if not self.skip_builds:
            print("[TEST 3] Testing MDBook builds...")
            if self.test_mdbook_builds():
                print("[PASS] All MDBook builds successful\n")
            else:
                print("[FAIL] MDBook builds failed\n")
                all_passed = False
        else:
            print("[TEST 3] Skipped MDBook builds (--quick mode)\n")

        # Test 4: Scenario Validation
        print("[TEST 4] Running scenario validation...")
        if self.test_scenario_validation():
            print("[PASS] All scenarios passed validation\n")
        else:
            print("[FAIL] Scenario validation failed\n")
            all_passed = False

        # Test 5: Build Output Verification
        if not self.skip_builds:
            print("[TEST 5] Verifying MDBook build outputs...")
            if self.test_build_outputs():
                print("[PASS] All build outputs verified\n")
            else:
                print("[FAIL] Build output verification failed\n")
                all_passed = False
        else:
            print("[TEST 5] Skipped build output verification (--quick mode)\n")

        # Print summary
        print("="*80)
        if all_passed:
            print("[SUCCESS] ALL INTEGRATION TESTS PASSED!")
        else:
            print("[FAILED] SOME INTEGRATION TESTS FAILED")
        print("="*80)
        print()

        return all_passed

    def test_file_structure(self) -> bool:
        """Test that all required directories and files exist"""
        errors = []

        for book in self.BOOKS:
            book_dir = BOOKS_DIR / book / "book"

            # Check book directory
            if not book_dir.exists():
                errors.append(f"Missing book directory: {book_dir}")
                continue

            # Check book.toml
            if not (book_dir / "book.toml").exists():
                errors.append(f"Missing book.toml for {book}")

            # Check SUMMARY.md
            if not (book_dir / "src" / "SUMMARY.md").exists():
                errors.append(f"Missing SUMMARY.md for {book}")

            # Check scenarios directory
            scenarios_dir = book_dir / "src" / "scenarios"
            if not scenarios_dir.exists():
                errors.append(f"Missing scenarios directory for {book}")

        if errors:
            for error in errors:
                print(f"  [ERROR] {error}")
            return False

        print(f"  Verified structure for {len(self.BOOKS)} books")
        return True

    def test_scenario_counts(self) -> bool:
        """Test that correct number of scenarios exist for each book"""
        errors = []

        for book, expected_count in self.EXPECTED_SCENARIOS.items():
            scenarios_dir = BOOKS_DIR / book / "book" / "src" / "scenarios"
            scenario_files = list(scenarios_dir.glob("scenario_*.md"))
            actual_count = len(scenario_files)

            if actual_count != expected_count:
                errors.append(f"{book}: expected {expected_count} scenarios, found {actual_count}")
            else:
                print(f"  {book}: {actual_count} scenarios [OK]")

        if errors:
            for error in errors:
                print(f"  [ERROR] {error}")
            return False

        total_expected = sum(self.EXPECTED_SCENARIOS.values())
        print(f"  Total: {total_expected} scenarios across 4 books")
        return True

    def test_mdbook_builds(self) -> bool:
        """Test that MDBook builds succeed for all books"""
        errors = []

        for book in self.BOOKS:
            book_dir = BOOKS_DIR / book / "book"
            print(f"  Building {book}...", end=" ")

            try:
                result = subprocess.run(
                    ["mdbook", "build"],
                    cwd=str(book_dir),
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    errors.append(f"{book}: build failed with code {result.returncode}")
                    print("[FAIL]")
                else:
                    print("[OK]")

            except subprocess.TimeoutExpired:
                errors.append(f"{book}: build timed out")
                print("[TIMEOUT]")
            except Exception as e:
                errors.append(f"{book}: {e}")
                print("[ERROR]")

        if errors:
            for error in errors:
                print(f"  [ERROR] {error}")
            return False

        return True

    def test_scenario_validation(self) -> bool:
        """Run scenario validation suite"""
        print("  Running validation suite...")

        # Import and run validation
        results = validate_all_books(verbose=False)

        # Check for errors
        total_errors = sum(
            sum(1 for r in book_results if not r.passed and r.severity == "error")
            for _, _, book_results in results.values()
        )

        if total_errors > 0:
            print(f"  [ERROR] {total_errors} validation errors found")
            return False

        print(f"  All {len(self.BOOKS)} books validated successfully")
        return True

    def test_build_outputs(self) -> bool:
        """Verify that MDBook build outputs exist"""
        errors = []

        for book in self.BOOKS:
            output_dir = BOOKS_DIR / book / "book" / "book"

            # Check output directory exists
            if not output_dir.exists():
                errors.append(f"{book}: output directory not found")
                continue

            # Check index.html exists
            if not (output_dir / "index.html").exists():
                errors.append(f"{book}: index.html not found")

            # Check scenario HTML files
            scenarios_dir = output_dir / "scenarios"
            if scenarios_dir.exists():
                html_files = list(scenarios_dir.glob("*.html"))
                expected_count = self.EXPECTED_SCENARIOS[book]

                if len(html_files) < expected_count:
                    errors.append(f"{book}: expected {expected_count}+ HTML files, found {len(html_files)}")
                else:
                    print(f"  {book}: {len(html_files)} HTML files generated [OK]")
            else:
                print(f"  {book}: scenarios directory not in output [OK - may be in other location]")

        if errors:
            for error in errors:
                print(f"  [ERROR] {error}")
            return False

        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run integration tests for BattleGroup books")
    parser.add_argument("--quick", action="store_true",
                       help="Skip time-consuming tests (MDBook builds)")

    args = parser.parse_args()

    tester = IntegrationTester(skip_builds=args.quick)
    passed = tester.run_all_tests()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
