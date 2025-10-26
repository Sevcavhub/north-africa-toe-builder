#!/usr/bin/env python3
"""
Chapter Matching Audit
Compares unit JSON files with chapter markdown files to find orphans and duplicates.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
UNITS_DIR = PROJECT_ROOT / 'data' / 'output' / 'units'
CHAPTERS_DIR = PROJECT_ROOT / 'data' / 'output' / 'chapters'
OUTPUT_REPORT = PROJECT_ROOT / 'REPORT_CHAPTER_MATCHING.md'

def extract_unit_key(filename):
    """Extract nation_quarter_unit key from filename"""
    # Remove extensions
    name = filename.replace('_toe.json', '').replace('chapter_', '').replace('.md', '')
    return name

def main():
    print("Chapter Matching Audit")
    print("=" * 80)

    # Scan unit files
    print(f"\nScanning unit files in {UNITS_DIR}...")
    unit_files = list(UNITS_DIR.glob('*_toe.json'))
    print(f"   Found: {len(unit_files)} unit JSON files")

    # Scan chapter files
    print(f"\nScanning chapter files in {CHAPTERS_DIR}...")
    chapter_files = list(CHAPTERS_DIR.glob('chapter_*.md'))
    print(f"   Found: {len(chapter_files)} chapter files")

    # Build mappings
    print(f"\nBuilding filename mappings...")

    units_map = {}
    for filepath in unit_files:
        key = extract_unit_key(filepath.name)
        stat = filepath.stat()
        units_map[key] = {
            'filename': filepath.name,
            'path': filepath,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'size': stat.st_size
        }

    chapters_map = defaultdict(list)  # Use list to catch duplicates
    for filepath in chapter_files:
        key = extract_unit_key(filepath.name)
        stat = filepath.stat()
        chapters_map[key].append({
            'filename': filepath.name,
            'path': filepath,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'size': stat.st_size
        })

    print(f"   Unique unit keys: {len(units_map)}")
    print(f"   Unique chapter keys: {len(chapters_map)}")

    # Find matches and mismatches
    print(f"\nAnalyzing matches...")

    matched_pairs = []
    units_without_chapters = []
    chapters_without_units = []
    duplicate_chapters = []

    # Check each unit for matching chapter
    for key, unit_info in units_map.items():
        if key in chapters_map:
            chapters = chapters_map[key]
            if len(chapters) == 1:
                matched_pairs.append({
                    'key': key,
                    'unit': unit_info,
                    'chapter': chapters[0]
                })
            else:
                # Multiple chapters for same unit
                duplicate_chapters.append({
                    'key': key,
                    'unit': unit_info,
                    'chapters': chapters,
                    'count': len(chapters)
                })
        else:
            units_without_chapters.append({
                'key': key,
                'unit': unit_info
            })

    # Check for orphan chapters (no corresponding unit)
    for key, chapters in chapters_map.items():
        if key not in units_map:
            for chapter in chapters:
                chapters_without_units.append({
                    'key': key,
                    'chapter': chapter
                })

    print(f"   Matched pairs (1:1): {len(matched_pairs)}")
    print(f"   Units without chapters: {len(units_without_chapters)}")
    print(f"   Chapters without units: {len(chapters_without_units)}")
    print(f"   Duplicate chapters: {len(duplicate_chapters)}")

    # Calculate discrepancy
    total_chapter_files = sum(len(chs) for chs in chapters_map.values())
    expected_chapters = len(units_map)
    excess_chapters = total_chapter_files - expected_chapters

    print(f"\nDiscrepancy Analysis:")
    print(f"   Expected chapters (1 per unit): {expected_chapters}")
    print(f"   Actual chapter files: {total_chapter_files}")
    print(f"   Excess chapters: {excess_chapters}")

    # Generate report
    print(f"\nGenerating report...")
    generate_report(
        matched_pairs,
        units_without_chapters,
        chapters_without_units,
        duplicate_chapters,
        len(unit_files),
        total_chapter_files,
        excess_chapters
    )

    print(f"\nReport generated: {OUTPUT_REPORT}")

def generate_report(matched, no_chapter, no_unit, duplicates, total_units, total_chapters, excess):
    """Generate markdown report"""

    report = []
    report.append('# Chapter Matching Audit Report')
    report.append('')
    report.append(f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    report.append(f'**Units Directory:** `{UNITS_DIR}`')
    report.append(f'**Chapters Directory:** `{CHAPTERS_DIR}`')
    report.append('')

    # Executive Summary
    report.append('## Executive Summary')
    report.append('')
    report.append(f'- **Unit JSON files:** {total_units}')
    report.append(f'- **Chapter files:** {total_chapters}')
    report.append(f'- **Expected (1:1 mapping):** {total_units} chapters')
    report.append(f'- **Excess chapters:** {excess}')
    report.append('')
    report.append(f'- **Matched pairs (1:1):** {len(matched)}')
    report.append(f'- **Units without chapters:** {len(no_chapter)}')
    report.append(f'- **Orphan chapters (no unit):** {len(no_unit)}')
    report.append(f'- **Units with duplicate chapters:** {len(duplicates)}')
    report.append('')

    # Status breakdown
    report.append('## Status Breakdown')
    report.append('')

    good = len(matched)
    missing_chapters = len(no_chapter)
    orphans = len(no_unit)
    dupes_count = sum(d['count'] - 1 for d in duplicates)  # Extra chapters beyond first

    total_checked = total_units
    pct_good = (good / total_checked * 100) if total_checked > 0 else 0
    pct_missing = (missing_chapters / total_checked * 100) if total_checked > 0 else 0

    report.append('| Status | Count | Percentage |')
    report.append('|--------|-------|------------|')
    report.append(f'| ✅ Perfect match (1:1) | {good} | {pct_good:.1f}% |')
    report.append(f'| ⚠️ Unit missing chapter | {missing_chapters} | {pct_missing:.1f}% |')
    report.append(f'| ❌ Orphan chapters | {orphans} | - |')
    report.append(f'| 📑 Duplicate chapters (extras) | {dupes_count} | - |')
    report.append('')

    # Units without chapters
    if no_chapter:
        report.append('## ⚠️ Units Without Chapters')
        report.append('')
        report.append(f'These {len(no_chapter)} units are missing their chapter files:')
        report.append('')
        report.append('| Key | Unit Filename | Created |')
        report.append('|-----|---------------|---------|')
        for item in sorted(no_chapter, key=lambda x: x['key']):
            report.append(f'| {item["key"]} | {item["unit"]["filename"]} | {item["unit"]["created"].strftime("%Y-%m-%d")} |')
        report.append('')

    # Orphan chapters
    if no_unit:
        report.append('## ❌ Orphan Chapters (No Corresponding Unit)')
        report.append('')
        report.append(f'These {len(no_unit)} chapters have no matching unit JSON:')
        report.append('')
        report.append('| Key | Chapter Filename | Created | Size (KB) |')
        report.append('|-----|------------------|---------|-----------|')
        for item in sorted(no_unit, key=lambda x: x['key']):
            size_kb = item['chapter']['size'] / 1024
            report.append(f'| {item["key"]} | {item["chapter"]["filename"]} | {item["chapter"]["created"].strftime("%Y-%m-%d %H:%M")} | {size_kb:.1f} |')
        report.append('')
        report.append('**Recommendation:** Delete these orphan chapters or create corresponding unit JSONs.')
        report.append('')

    # Duplicate chapters
    if duplicates:
        report.append('## 📑 Units with Duplicate Chapters')
        report.append('')
        report.append(f'These {len(duplicates)} units have multiple chapter files:')
        report.append('')

        for item in sorted(duplicates, key=lambda x: x['count'], reverse=True):
            report.append(f'### {item["key"]} ({item["count"]} chapters)')
            report.append('')
            report.append('| Chapter Filename | Created | Modified | Size (KB) |')
            report.append('|------------------|---------|----------|-----------|')

            for chapter in sorted(item['chapters'], key=lambda x: x['created']):
                size_kb = chapter['size'] / 1024
                created = chapter['created'].strftime("%Y-%m-%d %H:%M:%S")
                modified = chapter['modified'].strftime("%Y-%m-%d %H:%M:%S")
                report.append(f'| {chapter["filename"]} | {created} | {modified} | {size_kb:.1f} |')

            report.append('')
            report.append(f'**Recommendation:** Keep most recent, delete {item["count"] - 1} older versions.')
            report.append('')

    # Cleanup recommendations
    report.append('## Cleanup Recommendations')
    report.append('')

    if excess > 0:
        report.append(f'**Total cleanup needed:** {excess} excess chapter files')
        report.append('')

    if no_unit:
        report.append(f'1. **Delete {len(no_unit)} orphan chapters** (no corresponding unit)')

    if duplicates:
        dupes_to_delete = sum(d['count'] - 1 for d in duplicates)
        report.append(f'2. **Delete {dupes_to_delete} duplicate chapters** (keep most recent per unit)')

    if no_chapter:
        report.append(f'3. **Generate {len(no_chapter)} missing chapters** for units without chapters')

    report.append('')
    report.append('After cleanup, should have exactly 1:1 mapping: **{} units = {} chapters**'.format(total_units, total_units))
    report.append('')

    report.append('---')
    report.append(f'**Report Location:** `{OUTPUT_REPORT}`')
    report.append('')

    # Write report
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

if __name__ == '__main__':
    main()
