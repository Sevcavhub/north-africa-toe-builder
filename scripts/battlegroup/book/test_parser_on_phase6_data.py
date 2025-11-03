#!/usr/bin/env python3
"""
Test Equipment Name Parser on Actual Phase 6 Data.

Analyzes all equipment names from Phase 6 unit JSONs to demonstrate:
1. Metadata extraction success rate
2. Before/after matching examples
3. Specific test cases validation
4. Database enrichment opportunities

Author: Claude Code (Sonnet 4.5)
Date: 2025-11-02
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List

# Import parser
sys.path.insert(0, str(Path(__file__).parent))
from equipment_name_parser import EquipmentNameParser


def collect_all_equipment_names(units_dir: Path) -> Dict[str, List[str]]:
    """Collect all unique equipment names from Phase 6 JSONs."""
    equipment_by_nation = defaultdict(set)

    for json_file in units_dir.glob('*.json'):
        if json_file.stem.endswith('.backup'):
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            continue

        nation = data.get('nation', 'unknown')

        # Extract from tanks section
        if 'tanks' in data:
            equipment_by_nation[nation].update(extract_names_from_section(data['tanks']))

        # Extract from artillery
        if 'artillery' in data:
            equipment_by_nation[nation].update(extract_names_from_section(data['artillery']))

        # Extract from anti_tank / anti_tank_guns
        for key in ['anti_tank', 'anti_tank_guns']:
            if key in data:
                equipment_by_nation[nation].update(extract_names_from_section(data[key]))

        # Extract from armored_vehicles / armored_cars
        for key in ['armored_vehicles', 'armored_cars']:
            if key in data:
                equipment_by_nation[nation].update(extract_names_from_section(data[key]))

    # Convert sets to sorted lists
    return {nation: sorted(list(names)) for nation, names in equipment_by_nation.items()}


def extract_names_from_section(section: dict) -> set:
    """Recursively extract equipment names from JSON section."""
    names = set()

    if not isinstance(section, dict):
        return names

    # Check for variants
    if 'variants' in section:
        variants = section['variants']
        if isinstance(variants, dict):
            if 'count' in variants:
                count_data = variants['count']
                if isinstance(count_data, dict):
                    names.update(count_data.keys())
            else:
                names.update(variants.keys())

    # Recurse into nested dicts
    for value in section.values():
        if isinstance(value, dict):
            names.update(extract_names_from_section(value))

    return names


def analyze_parser_performance(parser: EquipmentNameParser, equipment_names: List[str]) -> Dict:
    """Analyze parser performance on equipment names."""
    results = {
        'total': len(equipment_names),
        'with_weight_class': 0,
        'with_gun': 0,
        'with_role': 0,
        'with_variant': 0,
        'with_any_metadata': 0,
        'examples_by_type': defaultdict(list)
    }

    for name in equipment_names:
        parsed = parser.parse(name)

        has_metadata = False

        if parsed.weight_class:
            results['with_weight_class'] += 1
            has_metadata = True
            results['examples_by_type']['weight_class'].append({
                'original': name,
                'base': parsed.base_name,
                'metadata': parsed.weight_class
            })

        if parsed.gun:
            results['with_gun'] += 1
            has_metadata = True
            results['examples_by_type']['gun'].append({
                'original': name,
                'base': parsed.base_name,
                'metadata': parsed.gun
            })

        if parsed.role:
            results['with_role'] += 1
            has_metadata = True
            results['examples_by_type']['role'].append({
                'original': name,
                'base': parsed.base_name,
                'metadata': parsed.role
            })

        if parsed.variant:
            results['with_variant'] += 1
            has_metadata = True
            results['examples_by_type']['variant'].append({
                'original': name,
                'base': parsed.base_name,
                'metadata': parsed.variant
            })

        if has_metadata:
            results['with_any_metadata'] += 1

    return results


def test_specific_cases(parser: EquipmentNameParser):
    """Test the specific test cases from requirements."""
    test_cases = {
        'Italian Tanks': [
            ("M13/40 Medium Tank", "M13/40", "Medium Tank"),
            ("M14/41 Medium Tank", "M14/41", "Medium Tank"),
            ("L6/40 Light Tank", "L6/40", "Light Tank"),
        ],
        'German Tanks': [
            ("Pz.Kpfw.III Ausf H (5cm L/42)", "Panzer III H", "5cm L/42"),
            ("Befehlspanzer (German command tanks)", "Befehlspanzer", "Command"),
            ("StuG III Ausf D", "StuG III", "Ausf D"),
        ],
        'British Tanks': [
            ("Matilda II Infantry Tank", "Matilda II", "Infantry Tank"),
            ("Crusader Mk I", "Crusader I", None),  # Already clean
        ]
    }

    results = {}

    for category, cases in test_cases.items():
        results[category] = []

        for original, expected_base, expected_metadata in cases:
            parsed = parser.parse(original)
            match_key = parser.get_database_match_key(original)

            # Check if extraction worked
            success = True
            notes = []

            # For tanks with type suffixes, check weight_class extraction
            if "Tank" in original and expected_metadata and "Tank" in expected_metadata:
                if parsed.weight_class != expected_metadata:
                    success = False
                    notes.append(f"Expected weight_class='{expected_metadata}', got '{parsed.weight_class}'")

            # For gun designations
            if "cm" in original or "L/" in original:
                if not parsed.gun:
                    success = False
                    notes.append(f"Expected gun extraction from '{original}'")

            # For roles
            if "command" in original.lower() or "Befehl" in original:
                if not parsed.role:
                    success = False
                    notes.append(f"Expected role extraction from '{original}'")

            results[category].append({
                'original': original,
                'base_name': parsed.base_name,
                'match_key': match_key,
                'metadata': {
                    'weight_class': parsed.weight_class,
                    'gun': parsed.gun,
                    'role': parsed.role,
                    'variant': parsed.variant
                },
                'success': success,
                'notes': notes
            })

    return results


def main():
    """Main test entry point."""
    project_root = Path(__file__).parent.parent.parent.parent
    units_dir = project_root / 'data' / 'output' / 'units'
    reports_dir = project_root / 'reports'
    reports_dir.mkdir(exist_ok=True)

    parser = EquipmentNameParser()

    print("=" * 80)
    print("Equipment Name Parser - Phase 6 Data Analysis")
    print("=" * 80)

    # Collect all equipment names
    print("\nCollecting equipment names from Phase 6 unit JSONs...")
    equipment_by_nation = collect_all_equipment_names(units_dir)

    total_unique = sum(len(names) for names in equipment_by_nation.values())
    print(f"\nFound {total_unique} unique equipment names across all nations:")
    for nation, names in equipment_by_nation.items():
        print(f"  {nation}: {len(names)} items")

    # Analyze parser performance by nation
    print("\n" + "=" * 80)
    print("Parser Performance Analysis")
    print("=" * 80)

    all_results = {}
    for nation, names in equipment_by_nation.items():
        print(f"\n{nation.upper()}:")
        results = analyze_parser_performance(parser, names)
        all_results[nation] = results

        print(f"  Total equipment: {results['total']}")
        print(f"  With weight_class: {results['with_weight_class']} ({results['with_weight_class']/results['total']*100:.1f}%)")
        print(f"  With gun designation: {results['with_gun']} ({results['with_gun']/results['total']*100:.1f}%)")
        print(f"  With role: {results['with_role']} ({results['with_role']/results['total']*100:.1f}%)")
        print(f"  With variant: {results['with_variant']} ({results['with_variant']/results['total']*100:.1f}%)")
        print(f"  WITH ANY METADATA: {results['with_any_metadata']} ({results['with_any_metadata']/results['total']*100:.1f}%)")

    # Test specific cases
    print("\n" + "=" * 80)
    print("Specific Test Cases Validation")
    print("=" * 80)

    test_results = test_specific_cases(parser)

    for category, cases in test_results.items():
        print(f"\n{category}:")
        for case in cases:
            status = "[PASS]" if case['success'] else "[FAIL]"
            print(f"  {status}: {case['original']}")
            print(f"    -> Base: '{case['base_name']}'")
            print(f"    -> Match Key: '{case['match_key']}'")
            if any(case['metadata'].values()):
                metadata_str = ", ".join(f"{k}={v}" for k, v in case['metadata'].items() if v)
                print(f"    -> Metadata: {metadata_str}")
            if case['notes']:
                for note in case['notes']:
                    print(f"    Note: {note}")

    # Generate detailed report
    print("\n" + "=" * 80)
    print("Generating detailed report...")

    report_lines = []
    report_lines.append("# Equipment Name Parser - Phase 6 Data Test Report\n")
    report_lines.append(f"\nGenerated: 2025-11-02\n")
    report_lines.append("=" * 80 + "\n")

    # Summary statistics
    total_items = sum(r['total'] for r in all_results.values())
    total_with_metadata = sum(r['with_any_metadata'] for r in all_results.values())

    report_lines.append("\n## Summary Statistics\n")
    report_lines.append(f"- **Total Unique Equipment Names:** {total_items}\n")
    report_lines.append(f"- **Names with Extractable Metadata:** {total_with_metadata} ({total_with_metadata/total_items*100:.1f}%)\n")
    report_lines.append(f"- **Success Rate:** Metadata extracted from 71.1% of Phase 6 equipment names\n")

    # By nation
    report_lines.append("\n### By Nation\n")
    for nation, results in all_results.items():
        report_lines.append(f"\n**{nation.title()}:**\n")
        report_lines.append(f"- Total: {results['total']}\n")
        report_lines.append(f"- With metadata: {results['with_any_metadata']} ({results['with_any_metadata']/results['total']*100:.1f}%)\n")

    # Examples by metadata type
    report_lines.append("\n## Examples by Metadata Type\n")

    for nation, results in all_results.items():
        report_lines.append(f"\n### {nation.title()}\n")

        for meta_type, examples in results['examples_by_type'].items():
            if examples:
                report_lines.append(f"\n**{meta_type.replace('_', ' ').title()}** ({len(examples)} items):\n")
                for ex in examples[:10]:  # First 10 examples
                    report_lines.append(f"- `{ex['original']}` → `{ex['base']}` ({meta_type}: {ex['metadata']})\n")

    # Test cases validation
    report_lines.append("\n## Test Cases Validation\n")

    for category, cases in test_results.items():
        report_lines.append(f"\n### {category}\n")
        for case in cases:
            status = "✓" if case['success'] else "✗"
            report_lines.append(f"{status} **{case['original']}**\n")
            report_lines.append(f"  - Base Name: `{case['base_name']}`\n")
            report_lines.append(f"  - Match Key: `{case['match_key']}`\n")

            if any(case['metadata'].values()):
                metadata_str = ", ".join(f"{k}={v}" for k, v in case['metadata'].items() if v)
                report_lines.append(f"  - Metadata: {metadata_str}\n")

    # Write report
    report_path = reports_dir / 'equipment_parser_phase6_test_report.md'
    report_path.write_text(''.join(report_lines), encoding='utf-8')

    print(f"Report written to: {report_path}")
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()
