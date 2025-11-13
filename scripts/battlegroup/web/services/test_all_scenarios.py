#!/usr/bin/env python3
"""
Test All Scenarios - Validation Script

Tests all 45 scenarios across 4 battles to ensure:
1. Scenario files exist and are parseable
2. AFVs are extracted correctly
3. Equipment is resolved to canonical IDs
4. Datacards can be generated
5. HTML output is valid
"""

import sys
from pathlib import Path
from scenario_html_generator import generate_printable_scenario_html, parse_scenario_markdown
from equipment_resolver import extract_equipment_from_scenario_forces

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
BOOKS_PATH = PROJECT_ROOT / "books"

# Battle configurations (based on actual files)
BATTLES = {
    'battleaxe': {
        'name': 'Operation Battleaxe',
        'scenarios': 8  # scenario_01 to scenario_08
    },
    'crusader': {
        'name': 'Operation Crusader',
        'scenarios': 12  # scenario_01 to scenario_12
    },
    'gazala': {
        'name': 'Battle of Gazala',
        'scenarios': 12  # scenario_01 to scenario_12
    },
    'first_alamein': {
        'name': 'First Battle of El Alamein',
        'scenarios': 10  # scenario_01 to scenario_10
    }
}


def test_scenario(battle: str, scenario_id: str) -> dict:
    """
    Test a single scenario.

    Returns:
        dict with test results
    """
    result = {
        'battle': battle,
        'scenario_id': scenario_id,
        'exists': False,
        'parseable': False,
        'has_forces': False,
        'afvs_extracted': 0,
        'afvs_resolved': 0,
        'html_generated': False,
        'html_size': 0,
        'errors': []
    }

    scenario_path = BOOKS_PATH / battle / "book" / "src" / "scenarios" / f"{scenario_id}.md"

    # Test 1: File exists
    if not scenario_path.exists():
        result['errors'].append(f"File not found: {scenario_path}")
        return result

    result['exists'] = True

    try:
        # Test 2: Parse scenario markdown
        scenario_data = parse_scenario_markdown(scenario_path)
        result['parseable'] = True

        # Test 3: Check for forces
        if scenario_data['attacker_units'] or scenario_data['defender_units']:
            result['has_forces'] = True

            # Test 4: Extract AFVs
            all_units_text = '\n'.join(scenario_data['attacker_units'] + scenario_data['defender_units'])
            afv_list = extract_equipment_from_scenario_forces(all_units_text)
            result['afvs_extracted'] = len(afv_list)

            # Count resolved AFVs (those with canonical_id)
            result['afvs_resolved'] = sum(1 for afv in afv_list if afv.get('canonical_id'))

        # Test 5: Generate HTML
        html = generate_printable_scenario_html(scenario_id, battle)
        result['html_generated'] = True
        result['html_size'] = len(html)

        # Validate HTML has datacards
        if 'datacard' not in html.lower():
            result['errors'].append("No datacards found in HTML")

        # Validate HTML is reasonable size (should be > 5KB for a scenario with datacards)
        if result['html_size'] < 5000:
            result['errors'].append(f"HTML size suspiciously small: {result['html_size']} bytes")

    except Exception as e:
        result['errors'].append(f"Exception: {str(e)}")

    return result


def run_all_tests():
    """Run tests on all scenarios."""
    print("=" * 80)
    print("SCENARIO VALIDATION TEST SUITE")
    print("=" * 80)
    print()

    all_results = []
    total_scenarios = sum(battle['scenarios'] for battle in BATTLES.values())

    for battle_key, battle_info in BATTLES.items():
        print(f"\n{'=' * 80}")
        print(f"Testing: {battle_info['name']}")
        print(f"{'=' * 80}\n")

        for i in range(1, battle_info['scenarios'] + 1):
            scenario_id = f"scenario_{i:02d}"
            print(f"  Testing {scenario_id}... ", end='', flush=True)

            result = test_scenario(battle_key, scenario_id)
            all_results.append(result)

            if result['errors']:
                print(f"[FAIL]")
                for error in result['errors']:
                    print(f"    - {error}")
            else:
                print(f"[PASS] ({result['afvs_resolved']}/{result['afvs_extracted']} AFVs, {result['html_size']} bytes)")

    # Summary statistics
    print(f"\n\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")

    passed = sum(1 for r in all_results if not r['errors'])
    failed = sum(1 for r in all_results if r['errors'])

    print(f"Total Scenarios: {total_scenarios}")
    print(f"Passed: {passed} ({100*passed/total_scenarios:.1f}%)")
    print(f"Failed: {failed} ({100*failed/total_scenarios:.1f}%)")
    print()

    # AFV statistics
    total_afvs_extracted = sum(r['afvs_extracted'] for r in all_results)
    total_afvs_resolved = sum(r['afvs_resolved'] for r in all_results)

    print(f"AFVs Extracted: {total_afvs_extracted}")
    print(f"AFVs Resolved: {total_afvs_resolved} ({100*total_afvs_resolved/max(1,total_afvs_extracted):.1f}%)")
    print()

    # HTML generation stats
    html_generated = sum(1 for r in all_results if r['html_generated'])
    avg_html_size = sum(r['html_size'] for r in all_results) / max(1, len(all_results))

    print(f"HTML Generated: {html_generated}/{total_scenarios}")
    print(f"Average HTML Size: {avg_html_size:.0f} bytes")
    print()

    # Failures detail
    if failed > 0:
        print(f"\n{'=' * 80}")
        print("FAILURES DETAIL")
        print(f"{'=' * 80}\n")

        for result in all_results:
            if result['errors']:
                print(f"{result['battle']}/{result['scenario_id']}:")
                for error in result['errors']:
                    print(f"  - {error}")
                print()

    return passed == total_scenarios


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
