#!/usr/bin/env python3
"""Generate simplified decision list for remaining 34 collisions."""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("database/master_database.db")
OUTPUT_FILE = Path("REMAINING_34_COLLISIONS_SIMPLIFIED.md")

def analyze_collision(witw_id, items):
    """Analyze collision and provide recommendation."""

    names = [item['name'] for item in items]
    categories = [item['category'] for item in items]
    ids = [item['id'] for item in items]

    # Check for naming convention patterns
    if len(items) == 2:
        name1 = names[0].lower()
        name2 = names[1].lower()

        # Churchill IV vs Churchill Mk IV pattern
        if 'churchill' in name1 and 'churchill' in name2:
            if ' mk ' in name1 or ' mk ' in name2:
                retained = next(item for item in items if ' Mk ' in item['name'])
                return {
                    'type': 'naming_convention',
                    'recommendation': 'A',
                    'retained': retained['id'],
                    'reason': 'British naming convention prefers "Mk"',
                    'confidence': 'HIGH'
                }

        # Valentine patterns
        if 'valentine' in name1 and 'valentine' in name2:
            # If one has "Mk" and other doesn't, prefer "Mk"
            if (' mk ' in name1.lower() and ' mk ' not in name2.lower()) or \
               (' mk ' in name2.lower() and ' mk ' not in name1.lower()):
                retained = next(item for item in items if ' Mk ' in item['name'] or ' mk ' in item['name'])
                return {
                    'type': 'naming_convention',
                    'recommendation': 'A',
                    'retained': retained['id'],
                    'reason': 'British naming convention prefers "Mk"',
                    'confidence': 'HIGH'
                }
            else:
                # Both have Mk or neither - might be different variants
                return {
                    'type': 'possible_variants',
                    'recommendation': 'B',
                    'reason': 'Different Valentine marks - keep separate if specs differ',
                    'confidence': 'MEDIUM',
                    'alternative': 'C (NULL all if unsure)'
                }

        # Crusader patterns
        if 'crusader' in name1 and 'crusader' in name2:
            # Similar to Valentine
            if (' mk ' in name1.lower() and ' mk ' not in name2.lower()) or \
               (' mk ' in name2.lower() and ' mk ' not in name1.lower()):
                retained = next(item for item in items if ' Mk ' in item['name'] or ' mk ' in item['name'])
                return {
                    'type': 'naming_convention',
                    'recommendation': 'A',
                    'retained': retained['id'],
                    'reason': 'British naming convention prefers "Mk"',
                    'confidence': 'HIGH'
                }
            else:
                return {
                    'type': 'possible_variants',
                    'recommendation': 'B',
                    'reason': 'Different Crusader marks with different armament',
                    'confidence': 'HIGH',
                    'note': 'Mk III has 6pdr vs Mk I/II 2pdr'
                }

        # Grant/Stuart patterns
        if ('grant' in name1 or 'stuart' in name1) and ('grant' in name2 or 'stuart' in name2):
            # Check if same base name
            base1 = 'grant' if 'grant' in name1 else 'stuart'
            base2 = 'grant' if 'grant' in name2 else 'stuart'
            if base1 == base2:
                # Prefer M3 designation over just name
                if 'm3' in name1 and 'm3' not in name2:
                    return {
                        'type': 'naming_convention',
                        'recommendation': 'A',
                        'retained': ids[0],
                        'reason': 'Prefer official M3 designation',
                        'confidence': 'HIGH'
                    }
                elif 'm3' in name2 and 'm3' not in name1:
                    return {
                        'type': 'naming_convention',
                        'recommendation': 'A',
                        'retained': ids[1],
                        'reason': 'Prefer official M3 designation',
                        'confidence': 'HIGH'
                    }

    # Check for variant series (3+ items, same base)
    if len(items) >= 3:
        # GMC CCKW variants
        if all('cckw' in name.lower() for name in names):
            return {
                'type': 'variant_series',
                'recommendation': 'B',
                'reason': 'GMC CCKW variants (different cargo capacities)',
                'confidence': 'MEDIUM',
                'note': 'Keep separate if cargo capacity matters for logistics modeling'
            }

        # Dodge WC variants
        if all('wc' in name.lower() and 'dodge' in name.lower() for name in names):
            return {
                'type': 'variant_series',
                'recommendation': 'B',
                'reason': 'Dodge WC variants (different models)',
                'confidence': 'MEDIUM'
            }

        # Morris variants
        if all('morris' in name.lower() for name in names):
            return {
                'type': 'variant_series',
                'recommendation': 'A',
                'reason': 'Retain most specific Morris variant',
                'confidence': 'MEDIUM',
                'suggested': next((item['id'] for item in items if 'quad' in item['name'].lower()), ids[0])
            }

    # Cross-nation collision
    unique_nations = set(id.split('_')[0] for id in ids)
    if len(unique_nations) > 1:
        return {
            'type': 'cross_nation',
            'recommendation': 'C',
            'reason': f'Cross-nation collision: {", ".join(unique_nations)}',
            'confidence': 'HIGH',
            'note': 'Likely incorrect ID assignment'
        }

    # Default - needs review
    return {
        'type': 'requires_review',
        'recommendation': 'D',
        'reason': 'Needs case-by-case review',
        'confidence': 'LOW'
    }

def main():
    """Generate simplified decision list."""

    print("=== Generating Simplified Decision List ===\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get remaining collisions
    cursor.execute("""
        SELECT
            CAST(witw_id AS INTEGER) as witw_id_num,
            COUNT(*) as collision_count,
            json_group_array(
                json_object('id', canonical_id, 'name', name, 'category', category)
            ) as items_json
        FROM equipment
        WHERE witw_id IS NOT NULL
          AND witw_id != 'NOT_IN_DATABASE'
          AND CAST(witw_id AS INTEGER) > 0
        GROUP BY CAST(witw_id AS INTEGER)
        HAVING COUNT(*) > 1
        ORDER BY CAST(witw_id AS INTEGER)
    """)

    collisions = cursor.fetchall()
    conn.close()

    print(f"Found {len(collisions)} remaining collisions\n")

    # Generate markdown
    lines = []
    lines.append("# Remaining 34 Collisions - Simplified Decision List")
    lines.append("")
    lines.append("**Generated**: 2025-11-02")
    lines.append(f"**Total**: {len(collisions)} collisions")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Quick Instructions")
    lines.append("")
    lines.append("For each collision, either:")
    lines.append("- **Accept recommendation** (most are high confidence)")
    lines.append("- **Change decision** (write A/B/C/D in User Decision field)")
    lines.append("- **Skip for now** (leave blank, we'll handle later)")
    lines.append("")
    lines.append("**Decision Key**:")
    lines.append("- **A**: Retain one item (specified)")
    lines.append("- **B**: Keep all separate (NULL all witw_ids)")
    lines.append("- **C**: NULL all (too ambiguous)")
    lines.append("- **D**: Research needed")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Categorize by type
    high_confidence = []
    medium_confidence = []
    low_confidence = []

    for row in collisions:
        witw_id = row['witw_id_num']
        items = json.loads(row['items_json'])
        analysis = analyze_collision(witw_id, items)

        collision_data = {
            'witw_id': witw_id,
            'items': items,
            'analysis': analysis
        }

        if analysis['confidence'] == 'HIGH':
            high_confidence.append(collision_data)
        elif analysis['confidence'] == 'MEDIUM':
            medium_confidence.append(collision_data)
        else:
            low_confidence.append(collision_data)

    # Output by confidence level
    lines.append(f"## High Confidence Recommendations ({len(high_confidence)} collisions)")
    lines.append("")
    lines.append("These have clear recommendations you can approve quickly.")
    lines.append("")

    for idx, collision in enumerate(high_confidence, 1):
        lines.append(f"### {idx}. WITW ID {collision['witw_id']}")
        lines.append("")
        for item in collision['items']:
            lines.append(f"- {item['id']}: {item['name']} ({item['category']})")
        lines.append("")
        analysis = collision['analysis']
        lines.append(f"**Type**: {analysis['type'].replace('_', ' ').title()}")
        lines.append(f"**Recommendation**: {analysis['recommendation']} - {analysis['reason']}")
        if 'retained' in analysis:
            lines.append(f"**Action**: Retain `{analysis['retained']}`, NULL others")
        elif 'suggested' in analysis:
            lines.append(f"**Action**: Retain `{analysis['suggested']}`, NULL others")
        elif analysis['recommendation'] == 'B':
            lines.append("**Action**: Keep all separate (NULL all witw_ids)")
        elif analysis['recommendation'] == 'C':
            lines.append("**Action**: NULL all (Phase 5 re-match)")
        if 'note' in analysis:
            lines.append(f"**Note**: {analysis['note']}")
        lines.append("")
        lines.append(f"**User Decision**: {analysis['recommendation']} (accept recommendation)")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(f"## Medium Confidence ({len(medium_confidence)} collisions)")
    lines.append("")
    lines.append("These need your judgment on whether variants should be separate.")
    lines.append("")

    for idx, collision in enumerate(medium_confidence, 1):
        lines.append(f"### {idx}. WITW ID {collision['witw_id']}")
        lines.append("")
        for item in collision['items']:
            lines.append(f"- {item['id']}: {item['name']} ({item['category']})")
        lines.append("")
        analysis = collision['analysis']
        lines.append(f"**Type**: {analysis['type'].replace('_', ' ').title()}")
        lines.append(f"**Recommendation**: {analysis['recommendation']} - {analysis['reason']}")
        if 'alternative' in analysis:
            lines.append(f"**Alternative**: {analysis['alternative']}")
        if 'note' in analysis:
            lines.append(f"**Note**: {analysis['note']}")
        lines.append("")
        lines.append(f"**User Decision**: _________")
        lines.append("")
        lines.append("---")
        lines.append("")

    if low_confidence:
        lines.append(f"## Low Confidence / Needs Research ({len(low_confidence)} collisions)")
        lines.append("")
        lines.append("These need investigation or can be deferred.")
        lines.append("")

        for idx, collision in enumerate(low_confidence, 1):
            lines.append(f"### {idx}. WITW ID {collision['witw_id']}")
            lines.append("")
            for item in collision['items']:
                lines.append(f"- {item['id']}: {item['name']} ({item['category']})")
            lines.append("")
            lines.append(f"**Recommendation**: NULL all or defer to Phase 5")
            lines.append("")
            lines.append("**User Decision**: C (NULL all)")
            lines.append("")
            lines.append("---")
            lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **High Confidence**: {len(high_confidence)} (can auto-apply)")
    lines.append(f"- **Medium Confidence**: {len(medium_confidence)} (need quick review)")
    lines.append(f"- **Low Confidence**: {len(low_confidence)} (recommend NULL all)")
    lines.append("")
    lines.append("**Estimated review time**: 15-25 minutes")
    lines.append("")

    # Write file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Generated: {OUTPUT_FILE}")
    print(f"High confidence: {len(high_confidence)}")
    print(f"Medium confidence: {len(medium_confidence)}")
    print(f"Low confidence: {len(low_confidence)}")

if __name__ == "__main__":
    main()
