#!/usr/bin/env python3
"""
Phase 3C: BattleGroup Duplicate Analysis

Analyze 154 duplicate groups in bg_reference_vehicles table and categorize them
into generic units, import artifacts, nation-specific variants, or stat variants.

This is ANALYSIS ONLY - no data modifications.
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

DB_PATH = Path("database/master_database.db")

def find_duplicates(cursor):
    """Find all duplicate name groups in bg_reference_vehicles"""
    print("=" * 80)
    print("STEP 1: FINDING DUPLICATES")
    print("=" * 80)
    print()

    cursor.execute("""
        SELECT
            LOWER(name) AS name_lower,
            COUNT(*) AS duplicate_count,
            GROUP_CONCAT(DISTINCT nation) AS nations
        FROM bg_reference_vehicles
        GROUP BY LOWER(name)
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC
    """)

    duplicates = cursor.fetchall()
    print(f"Found {len(duplicates)} duplicate name groups")
    print()

    print("Top 10 most duplicated:")
    for name, count, nations in duplicates[:10]:
        print(f"  {name}: {count} copies (nations: {nations})")
    print()

    return duplicates

def categorize_duplicate(cursor, name):
    """Categorize a duplicate group into one of 4 categories"""

    cursor.execute("""
        SELECT
            name,
            nation,
            battle_rating,
            points_cost,
            armor_front,
            armor_side,
            armor_rear,
            weapons,
            vehicle_type,
            off_road_inches,
            road_inches,
            special_rules,
            notes
        FROM bg_reference_vehicles
        WHERE LOWER(name) = LOWER(?)
        ORDER BY nation
    """, (name,))

    records = cursor.fetchall()

    if len(records) < 2:
        return None

    # Convert to dicts for easier comparison
    col_names = [desc[0] for desc in cursor.description]
    records_dicts = [dict(zip(col_names, rec)) for rec in records]

    # Extract comparison fields (excluding name and nation)
    comparison_fields = ['battle_rating', 'points_cost', 'armor_front', 'armor_side',
                         'armor_rear', 'weapons', 'vehicle_type', 'off_road_inches',
                         'road_inches', 'special_rules']

    # Get unique combinations of comparison fields
    unique_stats = set()
    for rec in records_dicts:
        stat_tuple = tuple(rec.get(field) for field in comparison_fields)
        unique_stats.add(stat_tuple)

    # Get nations
    nations = set(rec['nation'] for rec in records_dicts)

    # Categorization logic
    if len(unique_stats) == 1:
        # All stats identical
        if len(nations) > 1:
            # Multiple nations, same stats = Generic unit
            return {
                'category': 'generic_units',
                'reason': 'Same stats across multiple nations',
                'action': 'keep_duplicates',
                'nations': list(nations),
                'count': len(records)
            }
        else:
            # Same nation, same stats = Import artifact
            return {
                'category': 'import_artifacts',
                'reason': 'Exact duplicate (same nation, same stats)',
                'action': 'merge_duplicates',
                'nations': list(nations),
                'count': len(records),
                'keep_count': 1,
                'delete_count': len(records) - 1
            }
    else:
        # Different stats
        if len(nations) > 1:
            # Different nations, different stats = Nation-specific variant
            return {
                'category': 'nation_specific',
                'reason': 'Same name, different stats per nation',
                'action': 'rename_with_nation',
                'nations': list(nations),
                'count': len(records),
                'stat_variants': len(unique_stats)
            }
        else:
            # Same nation, different stats = Stat variant (requires review)
            return {
                'category': 'stat_variants',
                'reason': 'Same name and nation, but different stats (unclear why)',
                'action': 'user_review',
                'nations': list(nations),
                'count': len(records),
                'stat_variants': len(unique_stats)
            }

def analyze_all_duplicates(cursor, duplicates):
    """Analyze and categorize all duplicate groups"""
    print("=" * 80)
    print("STEP 2: CATEGORIZING DUPLICATES")
    print("=" * 80)
    print()

    categories = {
        'generic_units': [],
        'import_artifacts': [],
        'nation_specific': [],
        'stat_variants': []
    }

    for name_lower, count, nations in duplicates:
        categorization = categorize_duplicate(cursor, name_lower)
        if categorization:
            category = categorization['category']
            categories[category].append({
                'name': name_lower,
                **categorization
            })

    # Summary
    print("Categorization Results:")
    print(f"  Generic units (keep all): {len(categories['generic_units'])}")
    print(f"  Import artifacts (merge): {len(categories['import_artifacts'])}")
    print(f"  Nation-specific variants (rename): {len(categories['nation_specific'])}")
    print(f"  Stat variants (review needed): {len(categories['stat_variants'])}")
    print()

    return categories

def generate_report(categories):
    """Generate detailed categorization report"""
    print("=" * 80)
    print("DETAILED CATEGORIZATION REPORT")
    print("=" * 80)
    print()

    # Category 1: Generic Units
    print("=" * 80)
    print(f"CATEGORY 1: GENERIC UNITS ({len(categories['generic_units'])})")
    print("=" * 80)
    print()
    print("DESCRIPTION:")
    print("  Same equipment used across multiple nations with identical stats.")
    print("  Examples: Sniper, Supply Column, Forward Headquarters, Combat Medic")
    print()
    print("ACTION: KEEP ALL DUPLICATES (intentional cross-nation use)")
    print()

    if categories['generic_units']:
        print("Examples:")
        for item in categories['generic_units'][:10]:
            print(f"  - {item['name']}: {item['count']} copies across {len(item['nations'])} nations")
        if len(categories['generic_units']) > 10:
            print(f"  ... and {len(categories['generic_units']) - 10} more")
    print()

    # Category 2: Import Artifacts
    print("=" * 80)
    print(f"CATEGORY 2: IMPORT ARTIFACTS ({len(categories['import_artifacts'])})")
    print("=" * 80)
    print()
    print("DESCRIPTION:")
    print("  Exact duplicates (same name, same nation, same stats)")
    print("  Likely result of data import running multiple times")
    print()
    print("ACTION: MERGE DUPLICATES (delete extras, keep one)")
    print()

    if categories['import_artifacts']:
        total_deletions = sum(item.get('delete_count', 0) for item in categories['import_artifacts'])
        print(f"Total records to delete: {total_deletions}")
        print()
        print("Examples:")
        for item in categories['import_artifacts'][:10]:
            print(f"  - {item['name']}: {item['count']} copies -> DELETE {item['delete_count']}")
        if len(categories['import_artifacts']) > 10:
            print(f"  ... and {len(categories['import_artifacts']) - 10} more")
    print()

    # Category 3: Nation-Specific
    print("=" * 80)
    print(f"CATEGORY 3: NATION-SPECIFIC VARIANTS ({len(categories['nation_specific'])})")
    print("=" * 80)
    print()
    print("DESCRIPTION:")
    print("  Same name but different stats for different nations")
    print("  Example: 'Sherman' might have different specs for US vs British lend-lease")
    print()
    print("ACTION: RENAME WITH NATION CODE (for clarity)")
    print()

    if categories['nation_specific']:
        print("Examples:")
        for item in categories['nation_specific'][:10]:
            print(f"  - {item['name']}: {item['count']} nations, {item['stat_variants']} stat variants")
            print(f"    Nations: {', '.join(item['nations'])}")
        if len(categories['nation_specific']) > 10:
            print(f"  ... and {len(categories['nation_specific']) - 10} more")
    print()

    # Category 4: Stat Variants
    print("=" * 80)
    print(f"CATEGORY 4: STAT VARIANTS (REVIEW NEEDED) ({len(categories['stat_variants'])})")
    print("=" * 80)
    print()
    print("DESCRIPTION:")
    print("  Same name AND same nation, but different stats")
    print("  Unclear why these differ - may be variants, upgrades, or data errors")
    print()
    print("ACTION: USER REVIEW REQUIRED")
    print()

    if categories['stat_variants']:
        print("Requires manual review:")
        for item in categories['stat_variants'][:20]:
            print(f"  - {item['name']}: {item['count']} variants (nation: {item['nations'][0] if item['nations'] else 'unknown'})")
        if len(categories['stat_variants']) > 20:
            print(f"  ... and {len(categories['stat_variants']) - 20} more")
    print()

def generate_json_output(categories):
    """Generate JSON output file"""
    output = {
        "analysis_date": "2025-11-02",
        "total_duplicate_groups": sum(len(cat) for cat in categories.values()),
        "categories": {
            "generic_units": {
                "count": len(categories['generic_units']),
                "action": "keep_duplicates",
                "description": "Same equipment across multiple nations with identical stats",
                "items": categories['generic_units'][:50]  # Limit to first 50 for readability
            },
            "import_artifacts": {
                "count": len(categories['import_artifacts']),
                "action": "merge_duplicates",
                "description": "Exact duplicates (same name, nation, stats) - import errors",
                "records_to_delete": sum(item.get('delete_count', 0) for item in categories['import_artifacts']),
                "items": categories['import_artifacts'][:50]
            },
            "nation_specific": {
                "count": len(categories['nation_specific']),
                "action": "rename_with_nation_code",
                "description": "Same name, different stats per nation",
                "items": categories['nation_specific'][:50]
            },
            "stat_variants": {
                "count": len(categories['stat_variants']),
                "action": "user_review",
                "description": "Same name and nation, different stats (unclear why)",
                "requires_review": True,
                "items": categories['stat_variants']
            }
        }
    }

    output_path = Path("bg_duplicate_resolution.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"JSON output saved to: {output_path}")
    return output_path

def main():
    """Execute Phase 3C: BattleGroup Duplicate Analysis"""

    print("=" * 80)
    print("=== Phase 3C: BattleGroup Duplicate Analysis ===")
    print("=" * 80)
    print()
    print("OBJECTIVE: Categorize 154 duplicate name groups in bg_reference_vehicles")
    print("SCOPE: Analysis only - no data modifications")
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Step 1: Find duplicates
        duplicates = find_duplicates(cursor)

        # Step 2: Categorize
        categories = analyze_all_duplicates(cursor, duplicates)

        # Step 3: Generate report
        generate_report(categories)

        # Step 4: Generate JSON
        json_path = generate_json_output(categories)

        print()
        print("=" * 80)
        print("=== Task 7 / Phase 3C Complete ===")
        print("=" * 80)
        print()
        print(f"Total duplicate groups analyzed: {len(duplicates)}")
        print(f"Categorization complete")
        print(f"JSON output: {json_path}")
        print()
        print("NEXT STEPS:")
        print("  1. Review bg_duplicate_resolution.json")
        print("  2. Decide if cleanup is in-scope for Phase 3 or defer")
        print("  3. If in-scope: Implement merge/rename scripts")
        print("  4. If deferred: Document for future phase")
        print()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()

    return 0

if __name__ == "__main__":
    exit(main())
