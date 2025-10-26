import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

units_dir = Path('data/output/units')
wikipedia_units = []

for json_file in units_dir.glob('*_toe.json'):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check for Wikipedia in sources
        sources = data.get('validation', {}).get('source', [])
        if isinstance(sources, list):
            has_wikipedia = any('wikipedia' in str(s).lower() for s in sources)
        else:
            has_wikipedia = 'wikipedia' in str(sources).lower()

        if has_wikipedia:
            stat = json_file.stat()
            created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')

            wikipedia_units.append({
                'nation': data.get('nation', 'unknown'),
                'quarter': data.get('quarter', 'unknown'),
                'tier': str(data.get('validation', {}).get('tier', 'unknown')),
                'confidence': data.get('validation', {}).get('confidence', 0),
                'created': created,
                'filename': json_file.name
            })
    except Exception as e:
        continue

# Sort by quarter then nation
wikipedia_units.sort(key=lambda x: (x['quarter'], x['nation']))

# Generate markdown report
report = []
report.append('# Units with Wikipedia References')
report.append('')
report.append(f'**Generated:** {datetime.now().strftime("%Y-%m-%d")}')
report.append(f'**Total Units:** {len(wikipedia_units)} of 407 ({len(wikipedia_units)/407*100:.1f}%)')
report.append('')

# Summary by quarter
by_quarter = defaultdict(int)
for unit in wikipedia_units:
    by_quarter[unit['quarter']] += 1

report.append('## Summary by Quarter')
report.append('')
report.append('| Quarter | Count |')
report.append('|---------|-------|')
for quarter in sorted(by_quarter.keys()):
    report.append(f'| {quarter} | {by_quarter[quarter]} |')
report.append('')

# Summary by nation
by_nation = defaultdict(lambda: {'count': 0, 'total_conf': 0})
for unit in wikipedia_units:
    by_nation[unit['nation']]['count'] += 1
    by_nation[unit['nation']]['total_conf'] += unit['confidence']

report.append('## Summary by Nation')
report.append('')
report.append('| Nation | Count | Avg Confidence |')
report.append('|--------|-------|----------------|')
for nation in sorted(by_nation.keys()):
    count = by_nation[nation]['count']
    avg_conf = by_nation[nation]['total_conf'] / count if count > 0 else 0
    report.append(f'| {nation.capitalize()} | {count} | {avg_conf:.1f}% |')
report.append('')

# Complete list
report.append('## Complete List')
report.append('')
report.append('| Nation | Quarter | Tier | Conf% | Created | Filename |')
report.append('|--------|---------|------|-------|---------|----------|')
for unit in wikipedia_units:
    report.append(f'| {unit["nation"]} | {unit["quarter"]} | {unit["tier"]} | {unit["confidence"]} | {unit["created"]} | {unit["filename"]} |')
report.append('')

report.append('---')
report.append('**Report Location:** `D:\\north-africa-toe-builder\\REPORT_WIKIPEDIA_UNITS.md`')
report.append('')

# Write report
with open('REPORT_WIKIPEDIA_UNITS.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print('Report generated: REPORT_WIKIPEDIA_UNITS.md')
print(f'Total units with Wikipedia references: {len(wikipedia_units)}/407 ({len(wikipedia_units)/407*100:.1f}%)')
