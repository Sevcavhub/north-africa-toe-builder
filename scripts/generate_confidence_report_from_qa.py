import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import os

# Read the QA validation report
with open('data/SCHEMA_VALIDATION_REPORT.json', 'r', encoding='utf-8') as f:
    qa_report = json.load(f)

low_confidence_units = []

# Extract units with confidence < 75% from violations
for violation in qa_report['violations']:
    for warning in violation.get('warnings', []):
        if 'Confidence score' in warning and '% is below' in warning:
            # Parse confidence from warning message
            conf_str = warning.split('Confidence score ')[1].split('%')[0]
            confidence = int(conf_str)

            if confidence < 75:
                file_path = Path(violation['path'])

                # Get file creation date
                stat = file_path.stat()
                created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')

                # Parse filename for nation, quarter
                filename = violation['file']
                parts = filename.replace('_toe.json', '').split('_')

                if len(parts) >= 2:
                    nation = parts[0]
                    quarter = parts[1]
                else:
                    nation = 'unknown'
                    quarter = 'unknown'

                # Try to read tier from actual file
                tier = 'unknown'
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        tier = str(data.get('validation', {}).get('tier', 'unknown'))
                except:
                    pass

                low_confidence_units.append({
                    'nation': nation,
                    'quarter': quarter,
                    'tier': tier,
                    'confidence': confidence,
                    'created': created,
                    'filename': filename
                })
                break  # Only count once per file

# Sort by quarter then nation
low_confidence_units.sort(key=lambda x: (x['quarter'], x['nation']))

# Generate markdown report
report = []
report.append('# Units with Confidence < 75% (from QA Validation)')
report.append('')
report.append(f'**Generated:** {datetime.now().strftime("%Y-%m-%d")}')
report.append(f'**Total Units:** {len(low_confidence_units)} of {qa_report["total"]} ({len(low_confidence_units)/qa_report["total"]*100:.1f}%)')
report.append('')

# Summary by quarter
by_quarter = defaultdict(int)
for unit in low_confidence_units:
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
for unit in low_confidence_units:
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
for unit in low_confidence_units:
    report.append(f'| {unit["nation"]} | {unit["quarter"]} | {unit["tier"]} | {unit["confidence"]} | {unit["created"]} | {unit["filename"]} |')
report.append('')

# Critical issues (0% confidence)
zero_conf = [u for u in low_confidence_units if u['confidence'] == 0]
report.append(f'## Critical Issues (0% Confidence)')
report.append('')
report.append(f'These {len(zero_conf)} units have **ZERO confidence** and require immediate attention:')
report.append('')
report.append('| Nation | Quarter | Tier | Filename |')
report.append('|--------|---------|------|----------|')
for unit in zero_conf:
    report.append(f'| {unit["nation"]} | {unit["quarter"]} | {unit["tier"]} | {unit["filename"]} |')
report.append('')

# Very low confidence (<50%)
very_low = [u for u in low_confidence_units if 0 < u['confidence'] < 50]
report.append(f'## Very Low Confidence (1-49%)')
report.append('')
report.append(f'These {len(very_low)} units have very low confidence:')
report.append('')
report.append('| Nation | Quarter | Tier | Conf% | Filename |')
report.append('|--------|---------|------|-------|----------|')
for unit in very_low:
    report.append(f'| {unit["nation"]} | {unit["quarter"]} | {unit["tier"]} | {unit["confidence"]} | {unit["filename"]} |')
report.append('')

report.append('---')
report.append('**Report Location:** `D:\\north-africa-toe-builder\\REPORT_LOW_CONFIDENCE_CORRECTED.md`')
report.append('')

# Write report
with open('REPORT_LOW_CONFIDENCE_CORRECTED.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f'Report generated: REPORT_LOW_CONFIDENCE_CORRECTED.md')
print(f'Total low-confidence units: {len(low_confidence_units)}/{qa_report["total"]} ({len(low_confidence_units)/qa_report["total"]*100:.1f}%)')
print(f'  - 0% confidence: {len(zero_conf)} units')
print(f'  - 1-49% confidence: {len(very_low)} units')
print(f'  - 50-74% confidence: {len(low_confidence_units) - len(zero_conf) - len(very_low)} units')
