#!/usr/bin/env python3
"""Generate NEW user decision matrix based on actual 48 collisions."""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("database/master_database.db")
OUTPUT_FILE = Path("WITW_COLLISION_USER_DECISIONS_ACTUAL.md")

def categorize_collision(items):
    """Determine collision category and recommend strategy."""

    categories = [item['category'] for item in items]
    names = [item['name'] for item in items]
    ids = [item['id'] for item in items]

    # Check if multi-category (different equipment types)
    unique_cats = set(categories)

    # Multi-category collision (e.g., aircraft + ground equipment)
    if len(unique_cats) > 1:
        # Check for obvious mismatches
        ground_cats = {'tanks', 'anti_tank', 'anti_aircraft', 'field_artillery', 'trucks', 'halftracks', 'armored_cars'}
        air_cats = {'fighters', 'bombers', 'reconnaissance', 'aircraft'}

        has_ground = any(cat in ground_cats for cat in categories)
        has_air = any(cat in air_cats for cat in categories)

        if has_ground and has_air:
            return {
                'type': 'multi_category_critical',
                'recommendation': 'C',
                'reason': 'Aircraft and ground equipment collision - NULL all (Phase 5 re-match)',
                'auto_resolve': True
            }
        else:
            return {
                'type': 'multi_category',
                'recommendation': 'D',
                'reason': 'Different equipment categories - requires review',
                'auto_resolve': False
            }

    # Check for obvious duplicates (same item, different naming)
    if len(items) == 2:
        name1_lower = names[0].lower().replace('-', '').replace(' ', '')
        name2_lower = names[1].lower().replace('-', '').replace(' ', '')

        # Strip out common prefixes
        for prefix in ['gbr_', 'ger_', 'usa_', 'ita_']:
            name1_lower = name1_lower.replace(prefix, '')
            name2_lower = name2_lower.replace(prefix, '')

        # Check similarity
        if name1_lower in name2_lower or name2_lower in name1_lower:
            # Determine which to keep (prefer fuller name)
            if len(names[0]) > len(names[1]):
                retained_idx = 0
            else:
                retained_idx = 1

            return {
                'type': 'obvious_duplicate',
                'recommendation': 'A',
                'reason': f'Same item, different naming - retain fuller name',
                'auto_resolve': True,
                'retained_item': items[retained_idx]['id']
            }

    # Check for variant series (e.g., GMC CCKW-352, CCKW-353, CCKW-354)
    if len(items) >= 2:
        # Extract base names
        base_names = []
        for name in names:
            # Remove variant suffixes
            base = name.split(' ')[0].split('-')[0]
            base_names.append(base.lower())

        # If all have same base, it's a variant series
        if len(set(base_names)) == 1:
            return {
                'type': 'variant_series',
                'recommendation': 'D',
                'reason': 'Variant series - may need to keep separate or choose generic',
                'auto_resolve': False
            }

    # Default: needs manual review
    return {
        'type': 'requires_review',
        'recommendation': 'D',
        'reason': 'Requires manual review to determine correct item',
        'auto_resolve': False
    }

def generate_decision_text(witw_id, items, category_info):
    """Generate decision text for markdown."""

    lines = []
    lines.append(f"## Decision #{len(lines)+1}: WITW ID {witw_id}")
    lines.append("")
    lines.append(f"**Collision Type**: {category_info['type'].replace('_', ' ').title()}")
    lines.append(f"**Item Count**: {len(items)}")
    lines.append("")
    lines.append("**Colliding Items**:")
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. **{item['id']}** - {item['name']} ({item['category']})")
    lines.append("")

    # Analysis
    lines.append("**Analysis**:")
    lines.append(category_info['reason'])
    lines.append("")

    # Options
    lines.append("**Options**:")

    if category_info['type'] == 'multi_category_critical':
        lines.append("- **A**: Retain one item (specify which)")
        lines.append("- **B**: Keep all separate (NULL all witw_ids)")
        lines.append("- **C**: NULL all (too ambiguous, Phase 5 re-match) [RECOMMENDED]")
        lines.append("- **D**: Research WITW database for correct assignment")
    elif category_info['type'] == 'obvious_duplicate':
        lines.append(f"- **A**: Retain {category_info.get('retained_item', items[0]['id'])} (fuller/more precise name) [RECOMMENDED]")
        lines.append("- **B**: Retain other item")
        lines.append("- **C**: NULL all")
    elif category_info['type'] == 'variant_series':
        lines.append("- **A**: Retain most generic variant")
        lines.append("- **B**: Keep all separate (NULL all witw_ids)")
        lines.append("- **C**: NULL all (Phase 5 re-match)")
        lines.append("- **D**: Retain most common variant [RECOMMENDED]")
    else:
        lines.append("- **A**: Retain first item")
        lines.append("- **B**: Keep all separate")
        lines.append("- **C**: NULL all")
        lines.append("- **D**: Research needed")

    lines.append("")
    lines.append(f"**Recommendation**: Option {category_info['recommendation']}")
    lines.append("")
    lines.append("**User Decision**: _________________")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)

def main():
    """Generate new user decision matrix."""

    print("=== Generating NEW User Decision Matrix ===\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all numeric WITW ID collisions
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
        ORDER BY COUNT(*) DESC, CAST(witw_id AS INTEGER)
    """)

    collisions = cursor.fetchall()
    conn.close()

    print(f"Found {len(collisions)} collisions\n")

    # Generate markdown
    output_lines = []
    output_lines.append("# WITW ID Collision User Decision Matrix (ACTUAL DATA)")
    output_lines.append("")
    output_lines.append(f"**Generated**: 2025-11-02")
    output_lines.append(f"**Total Collisions**: {len(collisions)}")
    output_lines.append(f"**Database**: `master_database.db` (current state)")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Instructions")
    output_lines.append("")
    output_lines.append("For each collision below, review the analysis and select an option (A, B, C, or D).")
    output_lines.append("Write your decision in the **User Decision** field.")
    output_lines.append("")
    output_lines.append("**Decision Format**: Letter (A/B/C/D) + optional notes")
    output_lines.append("")
    output_lines.append("**Auto-resolve Available**: Collisions marked with [RECOMMENDED] can be auto-applied if you approve.")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")

    auto_resolve_count = 0
    manual_count = 0

    for row in collisions:
        witw_id = row['witw_id_num']
        items = json.loads(row['items_json'])

        # Categorize collision
        category_info = categorize_collision(items)

        if category_info['auto_resolve']:
            auto_resolve_count += 1
        else:
            manual_count += 1

        # Generate decision text
        decision_text = generate_decision_text(witw_id, items, category_info)
        output_lines.append(decision_text)

    # Summary at end
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Summary")
    output_lines.append("")
    output_lines.append(f"**Total Collisions**: {len(collisions)}")
    output_lines.append(f"**Auto-resolvable**: {auto_resolve_count} (with user approval)")
    output_lines.append(f"**Require Manual Review**: {manual_count}")
    output_lines.append("")
    output_lines.append("**Recommendation**: Review auto-resolvable decisions first, then focus on manual review cases.")
    output_lines.append("")

    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))

    print(f"Generated: {OUTPUT_FILE}")
    print(f"Total: {len(collisions)} collisions")
    print(f"Auto-resolvable: {auto_resolve_count}")
    print(f"Manual review: {manual_count}")

if __name__ == "__main__":
    main()
