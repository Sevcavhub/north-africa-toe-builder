#!/usr/bin/env python3
"""
BattleGroup Scenario Validation Suite

Validates scenario structure, content, and cross-references across all 4 battle books.

Part of Phase 9B Step 6 (Book Generation) - Part 9.

Usage:
    python validate_scenarios.py                # Validate all books
    python validate_scenarios.py --book battleaxe   # Validate specific book
    python validate_scenarios.py --verbose          # Show detailed output

Author: North Africa TO&E Builder
Date: November 2, 2025
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

BOOKS_DIR = project_root / "books"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    message: str
    severity: str = "error"  # "error", "warning", "info"


class ScenarioValidator:
    """Validates scenario markdown files"""

    REQUIRED_SECTIONS = [
        "SITUATION REPORT",
        "THE BATTLE",
        "THE BATTLEFIELD",
        "OBJECTIVES",
        "DEPLOYMENT",
        "FORCES"
    ]

    REQUIRED_FIELDS = {
        "SITUATION REPORT": ["Date", "Location"],
        "OBJECTIVES": ["Victory Type"],
        "DEPLOYMENT": ["Turn Order"],
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[ValidationResult] = []

    def validate_scenario_file(self, filepath: Path) -> List[ValidationResult]:
        """Validate a single scenario file"""
        results = []

        # Check file exists and is readable
        if not filepath.exists():
            results.append(ValidationResult(
                False,
                f"File not found: {filepath}",
                "error"
            ))
            return results

        # Read content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            results.append(ValidationResult(
                False,
                f"Could not read file {filepath}: {e}",
                "error"
            ))
            return results

        # Validate structure
        results.extend(self._validate_sections(content, filepath))
        results.extend(self._validate_fields(content, filepath))
        results.extend(self._validate_format(content, filepath))

        return results

    def _validate_sections(self, content: str, filepath: Path) -> List[ValidationResult]:
        """Check all required sections are present"""
        results = []

        for section in self.REQUIRED_SECTIONS:
            pattern = f"## {section}"
            if pattern not in content:
                results.append(ValidationResult(
                    False,
                    f"{filepath.name}: Missing section '{section}'",
                    "error"
                ))
            else:
                if self.verbose:
                    results.append(ValidationResult(
                        True,
                        f"{filepath.name}: Found section '{section}'",
                        "info"
                    ))

        return results

    def _validate_fields(self, content: str, filepath: Path) -> List[ValidationResult]:
        """Check required fields are present"""
        results = []

        for section, fields in self.REQUIRED_FIELDS.items():
            section_pattern = f"## {section}.*?(?=## |$)"
            section_match = re.search(section_pattern, content, re.DOTALL)

            if section_match:
                section_content = section_match.group(0)

                for field in fields:
                    field_pattern = f"\\*\\*{field}\\*\\*:"
                    if not re.search(field_pattern, section_content):
                        results.append(ValidationResult(
                            False,
                            f"{filepath.name}: Missing field '{field}' in section '{section}'",
                            "warning"
                        ))
                    elif self.verbose:
                        results.append(ValidationResult(
                            True,
                            f"{filepath.name}: Found field '{field}'",
                            "info"
                        ))

        return results

    def _validate_format(self, content: str, filepath: Path) -> List[ValidationResult]:
        """Validate markdown formatting"""
        results = []

        # Check for title (H1)
        if not content.startswith("#"):
            results.append(ValidationResult(
                False,
                f"{filepath.name}: Missing H1 title",
                "warning"
            ))

        # Check for page break
        if "\n---\n" not in content:
            results.append(ValidationResult(
                False,
                f"{filepath.name}: Missing page break (---)",
                "warning"
            ))

        # Check minimum length (should be ~70+ lines for 2-page format)
        line_count = len(content.split('\n'))
        if line_count < 50:
            results.append(ValidationResult(
                False,
                f"{filepath.name}: Content too short ({line_count} lines, expected 50+)",
                "warning"
            ))
        elif self.verbose:
            results.append(ValidationResult(
                True,
                f"{filepath.name}: Content length OK ({line_count} lines)",
                "info"
            ))

        return results


class BookValidator:
    """Validates entire book structure"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.scenario_validator = ScenarioValidator(verbose)

    def validate_book(self, book_name: str) -> Tuple[int, int, List[ValidationResult]]:
        """
        Validate a complete book

        Returns:
            (passed_count, total_count, results)
        """
        book_dir = BOOKS_DIR / book_name / "book"
        scenarios_dir = book_dir / "src" / "scenarios"

        all_results = []

        # Check book structure exists
        if not book_dir.exists():
            all_results.append(ValidationResult(
                False,
                f"Book directory not found: {book_dir}",
                "error"
            ))
            return 0, 0, all_results

        if not scenarios_dir.exists():
            all_results.append(ValidationResult(
                False,
                f"Scenarios directory not found: {scenarios_dir}",
                "error"
            ))
            return 0, 0, all_results

        # Validate book.toml
        book_toml = book_dir / "book.toml"
        if not book_toml.exists():
            all_results.append(ValidationResult(
                False,
                f"Missing book.toml: {book_toml}",
                "error"
            ))
        else:
            all_results.append(ValidationResult(
                True,
                f"Found book.toml",
                "info"
            ))

        # Validate SUMMARY.md
        summary_md = book_dir / "src" / "SUMMARY.md"
        if not summary_md.exists():
            all_results.append(ValidationResult(
                False,
                f"Missing SUMMARY.md: {summary_md}",
                "error"
            ))
        else:
            all_results.append(ValidationResult(
                True,
                f"Found SUMMARY.md",
                "info"
            ))

        # Validate all scenario files
        scenario_files = sorted(scenarios_dir.glob("scenario_*.md"))

        if not scenario_files:
            all_results.append(ValidationResult(
                False,
                f"No scenario files found in {scenarios_dir}",
                "error"
            ))
            return 0, 0, all_results

        for scenario_file in scenario_files:
            results = self.scenario_validator.validate_scenario_file(scenario_file)
            all_results.extend(results)

        # Count results
        passed = sum(1 for r in all_results if r.passed)
        total = len(all_results)

        return passed, total, all_results


def validate_all_books(verbose: bool = False) -> Dict[str, Tuple[int, int, List[ValidationResult]]]:
    """Validate all 4 books"""
    books = ["battleaxe", "crusader", "gazala", "first_alamein"]
    validator = BookValidator(verbose)

    results = {}
    for book in books:
        print(f"\n{'='*80}")
        print(f"Validating {book.upper()}")
        print(f"{'='*80}")

        passed, total, book_results = validator.validate_book(book)
        results[book] = (passed, total, book_results)

        # Print summary
        errors = [r for r in book_results if not r.passed and r.severity == "error"]
        warnings = [r for r in book_results if not r.passed and r.severity == "warning"]

        print(f"\nResults: {passed}/{total} checks passed")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")

        if errors and not verbose:
            print("\nErrors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  [ERROR] {error.message}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")

        if warnings and not verbose:
            print("\nWarnings:")
            for warning in warnings[:5]:  # Show first 5 warnings
                print(f"  [WARN] {warning.message}")
            if len(warnings) > 5:
                print(f"  ... and {len(warnings) - 5} more warnings")

    return results


def print_overall_summary(results: Dict[str, Tuple[int, int, List[ValidationResult]]]):
    """Print overall validation summary"""
    print(f"\n{'='*80}")
    print("OVERALL VALIDATION SUMMARY")
    print(f"{'='*80}\n")

    total_passed = 0
    total_checks = 0
    total_errors = 0
    total_warnings = 0

    for book, (passed, total, book_results) in results.items():
        total_passed += passed
        total_checks += total

        errors = sum(1 for r in book_results if not r.passed and r.severity == "error")
        warnings = sum(1 for r in book_results if not r.passed and r.severity == "warning")

        total_errors += errors
        total_warnings += warnings

        status = "PASS" if errors == 0 else "FAIL"
        print(f"{book.ljust(15)}: {status} ({passed}/{total} checks, {errors} errors, {warnings} warnings)")

    print(f"\n{'='*80}")
    print(f"Total: {total_passed}/{total_checks} checks passed")
    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")

    if total_errors == 0:
        print("\n[SUCCESS] ALL BOOKS PASSED VALIDATION!")
    else:
        print(f"\n[FAILED] VALIDATION FAILED ({total_errors} errors)")

    print(f"{'='*80}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate BattleGroup scenario books")
    parser.add_argument("--book", choices=["battleaxe", "crusader", "gazala", "first_alamein"],
                       help="Validate specific book only")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show all validation checks (including passed)")

    args = parser.parse_args()

    if args.book:
        # Validate single book
        validator = BookValidator(args.verbose)
        passed, total, book_results = validator.validate_book(args.book)

        errors = [r for r in book_results if not r.passed and r.severity == "error"]
        warnings = [r for r in book_results if not r.passed and r.severity == "warning"]

        print(f"\nResults: {passed}/{total} checks passed")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")

        if args.verbose:
            print("\nAll Results:")
            for result in book_results:
                icon = "[PASS]" if result.passed else ("[ERROR]" if result.severity == "error" else "[WARN]")
                print(f"  {icon} {result.message}")

        sys.exit(0 if len(errors) == 0 else 1)
    else:
        # Validate all books
        results = validate_all_books(args.verbose)
        print_overall_summary(results)

        # Exit code based on errors
        total_errors = sum(
            sum(1 for r in book_results if not r.passed and r.severity == "error")
            for _, _, book_results in results.values()
        )
        sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
