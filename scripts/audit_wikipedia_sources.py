#!/usr/bin/env python3
"""
Wikipedia Source Analysis
Analyzes all units with Wikipedia references to determine pattern and timeline.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
UNITS_DIR = PROJECT_ROOT / 'data' / 'output' / 'units'
OUTPUT_REPORT = PROJECT_ROOT / 'REPORT_WIKIPEDIA_ANALYSIS.md'

# Critical date: Wikipedia prohibition added to agents
PROHIBITION_DATE = datetime(2025, 10, 18, 0, 0, 0)

WIKIPEDIA_PATTERNS = [
    'wikipedia.org',
    'wikipedia.com',
    'wikia',
    'fandom',
    'wiki/',
    'wikipedia'
]

def contains_wikipedia(text):
    """Check if text contains Wikipedia reference"""
    if not text or not isinstance(text, str):
        return False
    text_lower = text.lower()
    return any(pattern in text_lower for pattern in WIKIPEDIA_PATTERNS)

def extract_wikipedia_urls(sources):
    """Extract all Wikipedia URLs from source list"""
    urls = []
    if not sources:
        return urls

    if isinstance(sources, str):
        if contains_wikipedia(sources):
            urls.append(sources)
    elif isinstance(sources, list):
        for source in sources:
            if isinstance(source, str) and contains_wikipedia(source):
                urls.append(source)

    return urls

def main():
    print("Wikipedia Source Analysis")
    print("=" * 80)

    print(f"\nScanning {UNITS_DIR}...")
    unit_files = list(UNITS_DIR.glob('*_toe.json'))
    print(f"   Found: {len(unit_files)} unit files")

    # Analyze each file
    print(f"\nAnalyzing Wikipedia sources...")

    wikipedia_units = []
    total_wiki_refs = 0

    for filepath in unit_files:
        try:
            stat = filepath.stat()
            created = datetime.fromtimestamp(stat.st_ctime)
            modified = datetime.fromtimestamp(stat.st_mtime)

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check for Wikipedia in sources
            sources = data.get('validation', {}).get('source', [])
            wiki_urls = extract_wikipedia_urls(sources)

            if wiki_urls:
                total_wiki_refs += len(wiki_urls)

                wikipedia_units.append({
                    'filename': filepath.name,
                    'nation': data.get('nation', 'unknown'),
                    'quarter': data.get('quarter', 'unknown'),
                    'unit_designation': data.get('unit_designation', 'Unknown'),
                    'confidence': data.get('validation', {}).get('confidence', 0),
                    'tier': data.get('validation', {}).get('tier', 'unknown'),
                    'created': created,
                    'modified': modified,
                    'wikipedia_urls': wiki_urls,
                    'wiki_count': len(wiki_urls),
                    'after_prohibition': created > PROHIBITION_DATE
                })

        except Exception as e:
            print(f"   WARNING: Error processing {filepath.name}: {e}")

    print(f"   Units with Wikipedia: {len(wikipedia_units)}")
    print(f"   Total Wikipedia references: {total_wiki_refs}")

    # Analyze timeline
    pre_prohibition = [u for u in wikipedia_units if not u['after_prohibition']]
    post_prohibition = [u for u in wikipedia_units if u['after_prohibition']]

    print(f"\nTimeline Analysis:")
    print(f"   Before Oct 18 prohibition: {len(pre_prohibition)} units")
    print(f"   After Oct 18 prohibition: {len(post_prohibition)} units")

    # Analyze by nation
    by_nation = defaultdict(int)
    by_quarter = defaultdict(int)
    by_tier = defaultdict(int)

    for unit in wikipedia_units:
        by_nation[unit['nation']] += 1
        by_quarter[unit['quarter']] += 1
        by_tier[unit['tier']] += 1

    # Generate report
    print(f"\nGenerating report...")
    generate_report(
        wikipedia_units,
        pre_prohibition,
        post_prohibition,
        by_nation,
        by_quarter,
        by_tier,
        total_wiki_refs
    )

    print(f"\nReport generated: {OUTPUT_REPORT}")

def generate_report(all_units, pre, post, by_nation, by_quarter, by_tier, total_refs):
    """Generate markdown report"""

    report = []
    report.append('# Wikipedia Source Analysis Report')
    report.append('')
    report.append(f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    report.append(f'**Prohibition Date:** {PROHIBITION_DATE.strftime("%Y-%m-%d")} (Wikipedia blocking added to agents)')
    report.append('')

    # Executive Summary
    report.append('## Executive Summary')
    report.append('')
    report.append(f'- **Units with Wikipedia sources:** {len(all_units)}')
    report.append(f'- **Total Wikipedia references:** {total_refs}')
    report.append(f'- **Before prohibition:** {len(pre)} units ({len(pre)/len(all_units)*100:.1f}% of violations)')
    report.append(f'- **After prohibition:** {len(post)} units ({len(post)/len(all_units)*100:.1f}% of violations)')
    report.append('')

    if post:
        report.append(f'⚠️ **CRITICAL**: {len(post)} units created AFTER Wikipedia prohibition still contain Wikipedia sources!')
        report.append('')

    # Timeline analysis
    report.append('## Timeline Analysis')
    report.append('')

    # Group by month
    by_month = defaultdict(lambda: {'pre': 0, 'post': 0})
    for unit in all_units:
        month_key = unit['created'].strftime('%Y-%m')
        if unit['after_prohibition']:
            by_month[month_key]['post'] += 1
        else:
            by_month[month_key]['pre'] += 1

    report.append('| Month | Pre-Prohibition | Post-Prohibition | Total |')
    report.append('|-------|-----------------|------------------|-------|')
    for month in sorted(by_month.keys()):
        pre_count = by_month[month]['pre']
        post_count = by_month[month]['post']
        total = pre_count + post_count
        marker = ' ⚠️' if post_count > 0 and month >= '2025-10' else ''
        report.append(f'| {month} | {pre_count} | {post_count} | {total}{marker} |')
    report.append('')

    # By Nation
    report.append('## Distribution by Nation')
    report.append('')
    report.append('| Nation | Count | Percentage |')
    report.append('|--------|-------|------------|')
    for nation in sorted(by_nation.keys()):
        count = by_nation[nation]
        pct = (count / len(all_units) * 100) if all_units else 0
        report.append(f'| {nation.capitalize()} | {count} | {pct:.1f}% |')
    report.append('')

    # By Quarter
    report.append('## Distribution by Quarter')
    report.append('')
    report.append('| Quarter | Count |')
    report.append('|---------|-------|')
    for quarter in sorted(by_quarter.keys()):
        report.append(f'| {quarter} | {by_quarter[quarter]} |')
    report.append('')

    # Post-prohibition violations (CRITICAL)
    if post:
        report.append('## ⚠️ CRITICAL: Post-Prohibition Violations')
        report.append('')
        report.append(f'These {len(post)} units were created AFTER Oct 18 Wikipedia prohibition but still contain Wikipedia:')
        report.append('')
        report.append('| Filename | Nation | Quarter | Created | Wiki URLs |')
        report.append('|----------|--------|---------|---------|-----------|')

        for unit in sorted(post, key=lambda x: x['created'], reverse=True):
            created = unit['created'].strftime('%Y-%m-%d %H:%M')
            wiki_list = ', '.join(url[:50] + '...' if len(url) > 50 else url for url in unit['wikipedia_urls'][:2])
            if unit['wiki_count'] > 2:
                wiki_list += f' (+{unit["wiki_count"] - 2} more)'
            report.append(f'| {unit["filename"]} | {unit["nation"]} | {unit["quarter"]} | {created} | {wiki_list} |')

        report.append('')
        report.append('**Action Required:** Re-extract these units using proper Tier 1/2 sources.')
        report.append('')

    # Complete list
    report.append('## Complete List of Wikipedia Violations')
    report.append('')
    report.append('| Filename | Nation | Quarter | Tier | Conf% | Created | Wiki Count | Status |')
    report.append('|----------|--------|---------|------|-------|---------|------------|--------|')

    for unit in sorted(all_units, key=lambda x: x['created'], reverse=True):
        created = unit['created'].strftime('%Y-%m-%d')
        status = '⚠️ POST-OCT18' if unit['after_prohibition'] else 'Pre-Oct18'
        report.append(f'| {unit["filename"]} | {unit["nation"]} | {unit["quarter"]} | {unit["tier"]} | {unit["confidence"]} | {created} | {unit["wiki_count"]} | {status} |')

    report.append('')

    # Recommendations
    report.append('## Recommendations')
    report.append('')

    if post:
        report.append(f'### 🚨 Immediate Action (Priority 1)')
        report.append(f'Re-extract {len(post)} units created after Oct 18 prohibition:')
        report.append('')
        for unit in sorted(post, key=lambda x: x['created'], reverse=True):
            report.append(f'- `{unit["filename"]}` ({unit["created"].strftime("%Y-%m-%d")})')
        report.append('')

    if pre:
        report.append(f'### ⏳ Backlog (Priority 2)')
        report.append(f'Re-extract {len(pre)} older units with Wikipedia (created before Oct 18):')
        report.append('')
        report.append('Group by nation for efficient batch processing:')
        pre_by_nation = defaultdict(list)
        for unit in pre:
            pre_by_nation[unit['nation']].append(unit)

        for nation in sorted(pre_by_nation.keys()):
            units = pre_by_nation[nation]
            report.append(f'- **{nation.capitalize()}**: {len(units)} units')

        report.append('')

    report.append('### 🔧 Workflow Fix Required')
    report.append('')
    report.append('Wikipedia violations persisting after Oct 18 suggest:')
    report.append('1. Agents may not be loading updated `agent_catalog.json`')
    report.append('2. Extraction workflow may not enforce Wikipedia validation')
    report.append('3. Session/checkpoint scripts may not block Wikipedia sources')
    report.append('')
    report.append('Verify agent catalog is being used and validation is enforced at runtime.')
    report.append('')

    report.append('---')
    report.append(f'**Report Location:** `{OUTPUT_REPORT}`')
    report.append('')

    # Write report
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

if __name__ == '__main__':
    main()
