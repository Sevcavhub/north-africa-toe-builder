#!/usr/bin/env python3
"""
Unit File Inventory Audit
Generates comprehensive report of all unit JSON files in canonical location.
Compares against QA validation report to find discrepancies.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import os

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
UNITS_DIR = PROJECT_ROOT / 'data' / 'output' / 'units'
QA_REPORT = PROJECT_ROOT / 'data' / 'SCHEMA_VALIDATION_REPORT.json'
OUTPUT_REPORT = PROJECT_ROOT / 'REPORT_UNIT_FILE_INVENTORY.md'

def main():
    print("Unit File Inventory Audit")
    print("=" * 80)

    # Load QA report
    print(f"\nLoading QA validation report...")
    with open(QA_REPORT, 'r', encoding='utf-8') as f:
        qa_report = json.load(f)

    qa_files = set()
    for violation in qa_report.get('violations', []):
        qa_files.add(violation['file'])

    print(f"   QA report scanned: {qa_report['total']} files")
    print(f"   Violations recorded: {len(qa_files)} files")

    # Scan units directory
    print(f"\nScanning {UNITS_DIR}...")
    unit_files = list(UNITS_DIR.glob('*_toe.json'))
    print(f"   Found: {len(unit_files)} _toe.json files")

    # Process each file
    print(f"\nProcessing unit files...")
    units = []
    parse_errors = []

    for filepath in sorted(unit_files):
        try:
            stat = filepath.stat()
            created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            size_kb = stat.st_size / 1024

            # Parse JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            unit_info = {
                'filename': filepath.name,
                'nation': data.get('nation', 'unknown'),
                'quarter': data.get('quarter', 'unknown'),
                'unit_designation': data.get('unit_designation', 'Unknown'),
                'confidence': data.get('validation', {}).get('confidence', 0),
                'tier': data.get('validation', {}).get('tier', 'unknown'),
                'created': created,
                'modified': modified,
                'size_kb': size_kb,
                'in_qa_report': filepath.name in qa_files
            }
            units.append(unit_info)

        except json.JSONDecodeError as e:
            parse_errors.append({
                'filename': filepath.name,
                'error': str(e)
            })
        except Exception as e:
            parse_errors.append({
                'filename': filepath.name,
                'error': f'Unexpected error: {str(e)}'
            })

    print(f"   Successfully parsed: {len(units)} files")
    print(f"   Parse errors: {len(parse_errors)} files")

    # Find discrepancies
    not_in_qa = [u for u in units if not u['in_qa_report']]

    # Generate statistics
    by_nation = defaultdict(int)
    by_quarter = defaultdict(int)
    by_tier = defaultdict(int)
    confidence_ranges = {'0%': 0, '1-49%': 0, '50-74%': 0, '75-100%': 0}

    for unit in units:
        by_nation[unit['nation']] += 1
        by_quarter[unit['quarter']] += 1
        by_tier[unit['tier']] += 1

        conf = unit['confidence']
        if conf == 0:
            confidence_ranges['0%'] += 1
        elif conf < 50:
            confidence_ranges['1-49%'] += 1
        elif conf < 75:
            confidence_ranges['50-74%'] += 1
        else:
            confidence_ranges['75-100%'] += 1

    # Generate report
    print(f"\nGenerating report...")
    generate_report(units, parse_errors, not_in_qa, by_nation, by_quarter, by_tier, confidence_ranges, qa_report)

    print(f"\nReport generated: {OUTPUT_REPORT}")
    print(f"\nSummary:")
    print(f"   Total files: {len(units)}")
    print(f"   Parse errors: {len(parse_errors)}")
    print(f"   Missing from QA: {len(not_in_qa)}")
    print(f"   0% confidence: {confidence_ranges['0%']}")

def generate_report(units, parse_errors, not_in_qa, by_nation, by_quarter, by_tier, confidence_ranges, qa_report):
    """Generate markdown report"""

    report = []
    report.append('# Unit File Inventory Audit Report')
    report.append('')
    report.append(f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    report.append(f'**Location:** `{UNITS_DIR}`')
    report.append(f'**Total Files:** {len(units)}')
    report.append('')

    # Executive Summary
    report.append('## Executive Summary')
    report.append('')
    report.append(f'- **Unit JSON files found:** {len(units)}')
    report.append(f'- **QA report scanned:** {qa_report["total"]} files')
    report.append(f'- **Discrepancy:** {len(units) - qa_report["total"]} files difference')
    report.append(f'- **Parse errors:** {len(parse_errors)}')
    report.append(f'- **Files not in QA report:** {len(not_in_qa)}')
    report.append('')

    # Confidence Distribution
    report.append('## Confidence Distribution')
    report.append('')
    report.append('| Range | Count | Percentage |')
    report.append('|-------|-------|------------|')
    for range_name, count in confidence_ranges.items():
        pct = (count / len(units) * 100) if units else 0
        report.append(f'| {range_name} | {count} | {pct:.1f}% |')
    report.append('')

    # By Nation
    report.append('## Distribution by Nation')
    report.append('')
    report.append('| Nation | Count |')
    report.append('|--------|-------|')
    for nation in sorted(by_nation.keys()):
        report.append(f'| {nation.capitalize()} | {by_nation[nation]} |')
    report.append('')

    # By Tier
    report.append('## Distribution by Tier')
    report.append('')
    report.append('| Tier | Count |')
    report.append('|------|-------|')
    for tier in sorted(by_tier.keys(), key=str):
        report.append(f'| {tier} | {by_tier[tier]} |')
    report.append('')

    # Parse Errors
    if parse_errors:
        report.append('## Parse Errors (Malformed JSON)')
        report.append('')
        report.append('These files could not be parsed and may be corrupted:')
        report.append('')
        report.append('| Filename | Error |')
        report.append('|----------|-------|')
        for error in parse_errors:
            report.append(f'| {error["filename"]} | {error["error"][:100]} |')
        report.append('')

    # Files not in QA
    if not_in_qa:
        report.append('## Files Not in QA Validation Report')
        report.append('')
        report.append(f'These {len(not_in_qa)} files exist but were not scanned by QA validation:')
        report.append('')
        report.append('| Filename | Nation | Quarter | Confidence | Created |')
        report.append('|----------|--------|---------|------------|---------|')
        for unit in not_in_qa:
            report.append(f'| {unit["filename"]} | {unit["nation"]} | {unit["quarter"]} | {unit["confidence"]}% | {unit["created"]} |')
        report.append('')

    # Complete Inventory
    report.append('## Complete Unit Inventory')
    report.append('')
    report.append('| Filename | Nation | Quarter | Unit | Tier | Conf% | Size(KB) | Created |')
    report.append('|----------|--------|---------|------|------|-------|----------|---------|')

    for unit in sorted(units, key=lambda x: (x['quarter'], x['nation'], x['filename'])):
        designation = unit['unit_designation'][:40]  # Truncate long names
        report.append(f'| {unit["filename"]} | {unit["nation"]} | {unit["quarter"]} | {designation} | {unit["tier"]} | {unit["confidence"]} | {unit["size_kb"]:.1f} | {unit["created"]} |')

    report.append('')
    report.append('---')
    report.append(f'**Report Location:** `{OUTPUT_REPORT}`')
    report.append('')

    # Write report
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

if __name__ == '__main__':
    main()
