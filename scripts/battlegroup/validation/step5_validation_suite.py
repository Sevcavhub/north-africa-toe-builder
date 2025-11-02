#!/usr/bin/env python3
"""
Phase 9B Step 5: Comprehensive Validation Suite
Tests all generators built in Step 5 for correctness and integration.

Components tested:
- Part 1: Datacard Generator (vehicles, guns, defences, fire support)
- Part 2: Special Rules Database (coverage, linkages)
- Part 3: Force Roster Builder (validation, composition)
- Part 4: Scenario Generators (random & historical)
- Part 5: Book Structure Generator (MDBook, LaTeX)
- Part 6: Army List Generator (Phase 6 integration)

Usage:
    python step5_validation_suite.py --all
    python step5_validation_suite.py --component datacard
    python step5_validation_suite.py --component scenario --verbose
"""

import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"
OUTPUT_DIR = project_root / "data" / "output" / "battlegroup"
VALIDATION_OUTPUT = project_root / "validation_reports"


class ValidationResult:
    """Stores validation test results"""
    def __init__(self, component: str, test_name: str):
        self.component = component
        self.test_name = test_name
        self.passed = True
        self.errors = []
        self.warnings = []
        self.info = []
        self.duration = 0.0

    def add_error(self, message: str):
        """Add error (causes test to fail)"""
        self.passed = False
        self.errors.append(message)

    def add_warning(self, message: str):
        """Add warning (doesn't cause failure)"""
        self.warnings.append(message)

    def add_info(self, message: str):
        """Add informational message"""
        self.info.append(message)

    def __str__(self):
        status = "[PASS]" if self.passed else "[FAIL]"
        lines = [f"{status} - {self.component}: {self.test_name}"]

        if self.errors:
            lines.append(f"  Errors ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"    [X] {error}")

        if self.warnings:
            lines.append(f"  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"    [!] {warning}")

        if self.info:
            lines.append(f"  Info:")
            for info in self.info:
                lines.append(f"    [i] {info}")

        return "\n".join(lines)


class Step5ValidationSuite:
    """Main validation suite for all Step 5 components"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[ValidationResult] = []
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'conn'):
            self.conn.close()

    # ===================================================================
    # PART 1: DATACARD GENERATOR VALIDATION
    # ===================================================================

    def validate_datacard_generator(self) -> List[ValidationResult]:
        """Validate datacard generator functionality"""
        results = []

        # Test 1: Check datacard templates exist
        result = ValidationResult("Part 1: Datacard Generator", "Template Files Exist")
        template_dir = project_root / "scripts" / "battlegroup" / "templates"

        required_templates = [
            "datacard_vehicle.txt",
            "datacard_gun.txt",
            "datacard_defence.txt",
            "datacard_fire_support.txt"
        ]

        for template in required_templates:
            template_path = template_dir / template
            if not template_path.exists():
                result.add_error(f"Missing template: {template}")
            else:
                result.add_info(f"Found: {template}")

        results.append(result)

        # Test 2: Validate datacard generator can be imported
        result = ValidationResult("Part 1: Datacard Generator", "Module Import")
        try:
            from scripts.battlegroup.generators.datacard_generator import DatacardGenerator
            result.add_info("Successfully imported DatacardGenerator")

            # Test instantiation
            generator = DatacardGenerator()
            result.add_info("Successfully instantiated DatacardGenerator")

        except Exception as e:
            result.add_error(f"Import/instantiation failed: {str(e)}")

        results.append(result)

        # Test 3: Test vehicle datacard generation
        result = ValidationResult("Part 1: Datacard Generator", "Vehicle Datacard Generation")
        try:
            from scripts.battlegroup.generators.datacard_generator import DatacardGenerator
            generator = DatacardGenerator()

            # Test with M4 Sherman
            datacard = generator.format_vehicle_datacard("M4 Sherman", "american", "regular")

            if "M4 Sherman" in datacard or "M4" in datacard:
                result.add_info("Vehicle name appears in datacard")
            else:
                result.add_warning("Vehicle name not found in datacard")

            if "pts" in datacard and "BR" in datacard:
                result.add_info("Points and BR found in datacard")
            else:
                result.add_error("Missing points or BR in datacard")

        except Exception as e:
            result.add_error(f"Vehicle datacard generation failed: {str(e)}")

        results.append(result)

        # Test 4: Test gun datacard generation
        result = ValidationResult("Part 1: Datacard Generator", "Gun Datacard Generation")
        try:
            from scripts.battlegroup.generators.datacard_generator import DatacardGenerator
            generator = DatacardGenerator()

            # Test with PaK 38
            datacard = generator.format_gun_datacard("50mm Pak 38", "german", "regular")

            if "PAK" in datacard.upper() or "PaK" in datacard:
                result.add_info("Gun name appears in datacard")
            else:
                result.add_warning("Gun name not found in datacard")

            if "AP" in datacard and "HE" in datacard:
                result.add_info("AP and HE data found")
            else:
                result.add_warning("Missing AP or HE data")

        except Exception as e:
            result.add_error(f"Gun datacard generation failed: {str(e)}")

        results.append(result)

        return results

    # ===================================================================
    # PART 2: SPECIAL RULES DATABASE VALIDATION
    # ===================================================================

    def validate_special_rules_database(self) -> List[ValidationResult]:
        """Validate special rules database coverage and linkages"""
        results = []

        # Test 1: Check special rules table exists
        result = ValidationResult("Part 2: Special Rules Database", "Table Structure")
        try:
            cursor = self.conn.execute("""
                SELECT COUNT(*) as count FROM special_rules
            """)
            count = cursor.fetchone()['count']

            if count >= 50:
                result.add_info(f"Found {count} special rules (target: 50+)")
            else:
                result.add_warning(f"Only {count} special rules (target: 50+)")

        except Exception as e:
            result.add_error(f"Special rules table query failed: {str(e)}")

        results.append(result)

        # Test 2: Check equipment_special_rules junction table
        result = ValidationResult("Part 2: Special Rules Database", "Equipment Linkages")
        try:
            cursor = self.conn.execute("""
                SELECT COUNT(*) as count FROM equipment_special_rules
            """)
            linkage_count = cursor.fetchone()['count']

            if linkage_count >= 1500:
                result.add_info(f"Found {linkage_count} equipment-rule linkages (target: 1500+)")
            else:
                result.add_warning(f"Only {linkage_count} linkages (target: 1500+)")

            # Check coverage
            cursor = self.conn.execute("""
                SELECT
                    COUNT(DISTINCT equipment_id) as equipment_with_rules,
                    (SELECT COUNT(*) FROM equipment) as total_equipment
                FROM equipment_special_rules
            """)
            row = cursor.fetchone()
            coverage = (row['equipment_with_rules'] / row['total_equipment']) * 100

            if coverage >= 80:
                result.add_info(f"Equipment coverage: {coverage:.1f}% (target: 80%+)")
            else:
                result.add_error(f"Low equipment coverage: {coverage:.1f}% (target: 80%+)")

        except Exception as e:
            result.add_error(f"Linkage validation failed: {str(e)}")

        results.append(result)

        return results

    # ===================================================================
    # PART 3: FORCE ROSTER BUILDER VALIDATION
    # ===================================================================

    def validate_force_roster_builder(self) -> List[ValidationResult]:
        """Validate force roster builder functionality"""
        results = []

        # Test 1: Module import
        result = ValidationResult("Part 3: Force Roster Builder", "Module Import")
        try:
            from scripts.battlegroup.generators.force_roster_builder_v2 import ForceRosterBuilder
            result.add_info("Successfully imported ForceRosterBuilder")

            builder = ForceRosterBuilder("german", "kursk")
            result.add_info("Successfully instantiated ForceRosterBuilder")

        except Exception as e:
            result.add_error(f"Import/instantiation failed: {str(e)}")

        results.append(result)

        # Test 2: Validation logic
        result = ValidationResult("Part 3: Force Roster Builder", "Composition Validation")
        try:
            from scripts.battlegroup.generators.force_roster_builder_v2 import ForceRoster

            # Create empty roster (should fail HQ requirement)
            roster = ForceRoster("german", "test", 500)
            issues = roster.validate()

            if any("HQ" in issue for issue in issues):
                result.add_info("Correctly detects missing HQ unit")
            else:
                result.add_error("Failed to detect missing HQ unit")

        except Exception as e:
            result.add_error(f"Validation logic test failed: {str(e)}")

        results.append(result)

        return results

    # ===================================================================
    # PART 4: SCENARIO GENERATOR VALIDATION
    # ===================================================================

    def validate_scenario_generators(self) -> List[ValidationResult]:
        """Validate random and historical scenario generators"""
        results = []

        # Test 1: Random scenario generator import
        result = ValidationResult("Part 4: Scenario Generators", "Random Scenario Generator Import")
        try:
            from scripts.battlegroup.generators.random_scenario_generator import RandomScenarioGenerator
            result.add_info("Successfully imported RandomScenarioGenerator")

            generator = RandomScenarioGenerator()
            result.add_info("Successfully instantiated RandomScenarioGenerator")

        except Exception as e:
            result.add_error(f"Import/instantiation failed: {str(e)}")

        results.append(result)

        # Test 2: Historical scenario generator import
        result = ValidationResult("Part 4: Scenario Generators", "Historical Scenario Generator Import")
        try:
            from scripts.battlegroup.generators.historical_scenario_generator import HistoricalScenarioGenerator
            result.add_info("Successfully imported HistoricalScenarioGenerator")

            generator = HistoricalScenarioGenerator()
            result.add_info("Successfully instantiated HistoricalScenarioGenerator")

        except Exception as e:
            result.add_error(f"Import/instantiation failed: {str(e)}")

        results.append(result)

        # Test 3: Scenario template count
        result = ValidationResult("Part 4: Scenario Generators", "Random Scenario Templates")
        try:
            from scripts.battlegroup.generators.random_scenario_generator import RandomScenarioGenerator
            generator = RandomScenarioGenerator()

            template_count = len(generator.SCENARIO_TEMPLATES)

            if template_count >= 12:
                result.add_info(f"Found {template_count} scenario templates (target: 12)")
            else:
                result.add_error(f"Only {template_count} templates (target: 12)")

        except Exception as e:
            result.add_error(f"Template count check failed: {str(e)}")

        results.append(result)

        return results

    # ===================================================================
    # PART 5: BOOK STRUCTURE GENERATOR VALIDATION
    # ===================================================================

    def validate_book_structure_generator(self) -> List[ValidationResult]:
        """Validate book structure generator for MDBook and LaTeX"""
        results = []

        # Test 1: Module import
        result = ValidationResult("Part 5: Book Structure Generator", "Module Import")
        try:
            from scripts.battlegroup.generators.book_structure_generator import BookStructureGenerator
            result.add_info("Successfully imported BookStructureGenerator")

            generator = BookStructureGenerator(
                battle="test",
                operation="Test Operation",
                dates="Jan 1-5, 1942",
                quarter="1942q1",
                location="Test Location",
                attacker="british",
                defender="german"
            )
            result.add_info("Successfully instantiated BookStructureGenerator")

        except Exception as e:
            result.add_error(f"Import/instantiation failed: {str(e)}")

        results.append(result)

        # Test 2: Check templates exist
        result = ValidationResult("Part 5: Book Structure Generator", "Template Files")
        template_dir = project_root / "scripts" / "battlegroup" / "templates"

        required_templates = [
            "book_structure.yaml",
            "mdbook_summary.txt",
            "book_print.tex"
        ]

        for template in required_templates:
            template_path = template_dir / template
            if not template_path.exists():
                result.add_error(f"Missing template: {template}")
            else:
                result.add_info(f"Found: {template}")

        results.append(result)

        return results

    # ===================================================================
    # PART 6: ARMY LIST GENERATOR VALIDATION
    # ===================================================================

    def validate_army_list_generator(self) -> List[ValidationResult]:
        """Validate army list generator with Phase 6 integration"""
        results = []

        # Test 1: Module import
        result = ValidationResult("Part 6: Army List Generator", "Module Import")
        try:
            from scripts.battlegroup.generators.army_list_generator import ArmyListGenerator
            result.add_info("Successfully imported ArmyListGenerator")

            generator = ArmyListGenerator()
            result.add_info("Successfully instantiated ArmyListGenerator")

        except Exception as e:
            result.add_error(f"Import/instantiation failed: {str(e)}")

        results.append(result)

        # Test 2: Phase6UnitParser integration
        result = ValidationResult("Part 6: Army List Generator", "Phase6UnitParser Integration")
        try:
            from scripts.battlegroup.generators.phase6_unit_parser import Phase6UnitParser
            parser = Phase6UnitParser()
            result.add_info("Successfully imported Phase6UnitParser")

            # Check if we can get units
            units = parser.get_units_for_quarter("american", "1942q4")
            if units:
                result.add_info(f"Found {len(units)} American 1942q4 units")
            else:
                result.add_warning("No units found for American 1942q4")

        except Exception as e:
            result.add_error(f"Phase6UnitParser integration failed: {str(e)}")

        results.append(result)

        # Test 3: Force organization categories
        result = ValidationResult("Part 6: Army List Generator", "Force Organization Categories")
        try:
            from scripts.battlegroup.generators.army_list_generator import ArmyListGenerator
            generator = ArmyListGenerator()

            expected_categories = ['HQ', 'INFANTRY', 'ARMOR', 'ARTILLERY', 'ANTI-TANK',
                                 'ANTI-AIRCRAFT', 'RECONNAISSANCE', 'SUPPORT']

            for category in expected_categories:
                if category in str(generator.CATEGORY_MAPPINGS.values()):
                    result.add_info(f"Found category: {category}")
                else:
                    result.add_warning(f"Missing category mapping: {category}")

        except Exception as e:
            result.add_error(f"Category validation failed: {str(e)}")

        results.append(result)

        return results

    # ===================================================================
    # MAIN VALIDATION ORCHESTRATION
    # ===================================================================

    def run_all_validations(self) -> Dict[str, List[ValidationResult]]:
        """Run all validation tests"""
        all_results = {}

        print("=" * 80)
        print("PHASE 9B STEP 5 - COMPREHENSIVE VALIDATION SUITE")
        print("=" * 80)
        print()

        # Part 1: Datacard Generator
        print("[*] Validating Part 1: Datacard Generator...")
        all_results['Part 1'] = self.validate_datacard_generator()
        print()

        # Part 2: Special Rules Database
        print("[*] Validating Part 2: Special Rules Database...")
        all_results['Part 2'] = self.validate_special_rules_database()
        print()

        # Part 3: Force Roster Builder
        print("[*] Validating Part 3: Force Roster Builder...")
        all_results['Part 3'] = self.validate_force_roster_builder()
        print()

        # Part 4: Scenario Generators
        print("[*] Validating Part 4: Scenario Generators...")
        all_results['Part 4'] = self.validate_scenario_generators()
        print()

        # Part 5: Book Structure Generator
        print("[*] Validating Part 5: Book Structure Generator...")
        all_results['Part 5'] = self.validate_book_structure_generator()
        print()

        # Part 6: Army List Generator
        print("[*] Validating Part 6: Army List Generator...")
        all_results['Part 6'] = self.validate_army_list_generator()
        print()

        return all_results

    def generate_report(self, all_results: Dict[str, List[ValidationResult]]) -> str:
        """Generate validation report"""
        lines = []
        lines.append("=" * 80)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        total_tests = 0
        total_passed = 0
        total_errors = 0
        total_warnings = 0

        for component, results in all_results.items():
            lines.append(f"\n{component}")
            lines.append("-" * 80)

            for result in results:
                total_tests += 1
                if result.passed:
                    total_passed += 1
                total_errors += len(result.errors)
                total_warnings += len(result.warnings)

                lines.append(str(result))
                lines.append("")

        # Summary
        lines.append("=" * 80)
        lines.append("SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Total Tests: {total_tests}")
        lines.append(f"Passed: {total_passed} ({(total_passed/total_tests*100):.1f}%)")
        lines.append(f"Failed: {total_tests - total_passed}")
        lines.append(f"Total Errors: {total_errors}")
        lines.append(f"Total Warnings: {total_warnings}")
        lines.append("")

        if total_passed == total_tests:
            lines.append("[OK] ALL TESTS PASSED")
        else:
            lines.append("[FAIL] SOME TESTS FAILED")

        return "\n".join(lines)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 5: Comprehensive Validation Suite"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all validation tests"
    )
    parser.add_argument(
        "--component",
        choices=['datacard', 'special_rules', 'roster', 'scenario', 'book', 'army_list'],
        help="Run validation for specific component"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output report file path"
    )

    args = parser.parse_args()

    suite = Step5ValidationSuite(verbose=args.verbose)

    if args.all or not args.component:
        # Run all validations
        all_results = suite.run_all_validations()
        report = suite.generate_report(all_results)
    else:
        # Run specific component validation
        print(f"Running validation for: {args.component}")
        all_results = {}

        if args.component == 'datacard':
            all_results['Part 1'] = suite.validate_datacard_generator()
        elif args.component == 'special_rules':
            all_results['Part 2'] = suite.validate_special_rules_database()
        elif args.component == 'roster':
            all_results['Part 3'] = suite.validate_force_roster_builder()
        elif args.component == 'scenario':
            all_results['Part 4'] = suite.validate_scenario_generators()
        elif args.component == 'book':
            all_results['Part 5'] = suite.validate_book_structure_generator()
        elif args.component == 'army_list':
            all_results['Part 6'] = suite.validate_army_list_generator()

        report = suite.generate_report(all_results)

    # Print report
    print(report)

    # Save report if output path specified
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n[OK] Report saved to: {args.output}")
    else:
        # Default output path
        VALIDATION_OUTPUT.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_output = VALIDATION_OUTPUT / f"step5_validation_{timestamp}.txt"
        with open(default_output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n[OK] Report saved to: {default_output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
