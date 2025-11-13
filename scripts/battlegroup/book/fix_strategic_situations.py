#!/usr/bin/env python3
"""
Fix Strategic Situation Content - Historical Accuracy Correction

This script:
1. Loads historical reference data for each battle
2. Generates corrected strategic situation content
3. Validates content with historical expert agent
4. Applies corrections to book files

Run with --validate-only to check without writing
Run with --apply to write corrections
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # Go up 3 levels from scripts/battlegroup/book
BOOKS_PATH = PROJECT_ROOT / "books"
REFERENCE_PATH = SCRIPT_DIR / "historical_accuracy_reference.json"


def load_historical_reference() -> Dict:
    """Load historical reference data."""
    with open(REFERENCE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_strategic_situation(battle_key: str, battle_data: Dict) -> str:
    """
    Generate historically accurate strategic situation content.

    Args:
        battle_key: Battle identifier (e.g., 'compass')
        battle_data: Historical reference data for the battle

    Returns:
        Markdown content for strategic situation
    """

    # Determine quarter display format
    quarter = battle_data['quarter']
    year = quarter[:4]
    q = quarter[5:]
    quarter_display = f"{year}-Q{q.upper()}"

    # Build combatants list
    allies = ", ".join(battle_data['combatants']['allies'])
    axis = ", ".join(battle_data['combatants']['axis'])

    # German forces note
    german_note = ""
    if battle_data['german_forces_present']:
        german_units = ", ".join(battle_data['key_german_units'])
        german_note = f"\n\n**German Forces**: {german_units}"
    else:
        german_note = "\n\n**No German forces present in this battle** - Germans did not arrive in North Africa until Operation Sonnenblume (February 1941)."

    content = f"""# Strategic Situation - {quarter_display}

## North Africa Theater

**{battle_data['name']}**
**Dates**: {battle_data['dates']}
**Combatants**: {allies} vs {axis}

## Historical Context

{battle_data['strategic_context']}

## Key Forces

### Allied Forces
{chr(10).join(f"- {unit}" for unit in battle_data['key_british_units'])}
{german_note}

### Axis Forces

**Italian Forces**:
{chr(10).join(f"- {unit}" for unit in battle_data['key_italian_units'])}
"""

    # Add German section if present
    if battle_data['german_forces_present']:
        content += f"""
**German Forces**:
{chr(10).join(f"- {unit}" for unit in battle_data['key_german_units'])}
"""

    # Add key locations
    content += f"""
## Key Locations and Objectives

{chr(10).join(f"- {loc}" for loc in battle_data['key_locations'])}

## Outcome

{battle_data['outcome']}
"""

    # Add notes if present
    if 'notes' in battle_data:
        content += f"""
## Historical Notes

{battle_data['notes']}
"""

    return content


def validate_content_historical_accuracy(battle_key: str, content: str, reference_data: Dict) -> Dict:
    """
    Validate strategic situation content for historical accuracy.

    This is a placeholder - will be replaced by expert agent validation.

    Returns:
        dict with 'valid': bool, 'errors': list, 'warnings': list
    """
    battle_data = reference_data['battles'][battle_key]
    errors = []
    warnings = []

    # Check 1: German forces mentioned when not present
    if not battle_data['german_forces_present']:
        if any(term in content.lower() for term in ['rommel', 'afrika korps', 'panzer division', '88mm']):
            errors.append(f"Content mentions German forces but Germans not present in {battle_data['name']}")

    # Check 2: Tobruk siege mentioned when not applicable
    tobruk_siege_battles = ['tobruk', 'battleaxe', 'crusader']
    if battle_key not in tobruk_siege_battles:
        if 'tobruk siege' in content.lower() or 'besieged port of tobruk' in content.lower():
            errors.append(f"Content mentions Tobruk siege but not applicable to {battle_data['name']}")

    # Check 3: Correct quarter mentioned
    quarter_display = content.split('\n')[0]  # First line "# Strategic Situation - 1941-Q2"
    expected_quarter = battle_data['quarter']
    year = expected_quarter[:4]
    q = expected_quarter[5:]
    expected_display = f"{year}-Q{q.upper()}"

    if expected_display not in quarter_display:
        errors.append(f"Quarter mismatch: header shows {quarter_display} but should be {expected_display}")

    # Check 4: Dates mentioned
    if battle_data['dates'] not in content:
        warnings.append(f"Dates '{battle_data['dates']}' not found in content")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def main():
    """Main execution function."""
    print("=" * 80)
    print("STRATEGIC SITUATION HISTORICAL ACCURACY CORRECTION")
    print("=" * 80)
    print()

    # Check mode
    validate_only = '--validate-only' in sys.argv
    apply_fixes = '--apply' in sys.argv

    if not validate_only and not apply_fixes:
        print("Usage:")
        print("  python fix_strategic_situations.py --validate-only  # Check without writing")
        print("  python fix_strategic_situations.py --apply          # Write corrections")
        return

    # Load reference data
    print("Loading historical reference data...")
    reference = load_historical_reference()
    battles = reference['battles']
    print(f"Loaded data for {len(battles)} battles\n")

    # Process each battle
    results = {}

    for battle_key, battle_data in battles.items():
        print(f"\n{'=' * 80}")
        print(f"Processing: {battle_data['name']}")
        print(f"{'=' * 80}")

        # Generate corrected content
        print(f"Generating corrected content for {battle_key}...")
        new_content = generate_strategic_situation(battle_key, battle_data)

        # Validate content
        print(f"Validating historical accuracy...")
        validation = validate_content_historical_accuracy(battle_key, new_content, reference)

        results[battle_key] = {
            'name': battle_data['name'],
            'valid': validation['valid'],
            'errors': validation['errors'],
            'warnings': validation['warnings'],
            'content': new_content
        }

        # Report validation results
        if validation['valid']:
            print(f"[PASS] Historical accuracy validated")
        else:
            print(f"[FAIL] Historical accuracy errors found:")
            for error in validation['errors']:
                print(f"  - {error}")

        if validation['warnings']:
            print(f"[WARN] Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")

        # Apply fixes if requested
        if apply_fixes and validation['valid']:
            target_file = BOOKS_PATH / battle_key / "book" / "src" / "chapter1" / "strategic_situation.md"
            if target_file.exists():
                print(f"Writing corrected content to {target_file}...")
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"[OK] File updated")
            else:
                print(f"[SKIP] Target file not found: {target_file}")

    # Summary
    print(f"\n\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")

    total = len(results)
    valid = sum(1 for r in results.values() if r['valid'])
    invalid = total - valid

    print(f"Total battles: {total}")
    print(f"Valid: {valid} ({100*valid/total:.1f}%)")
    print(f"Invalid: {invalid} ({100*invalid/total:.1f}%)")

    if invalid > 0:
        print(f"\n{'=' * 80}")
        print("FAILURES")
        print(f"{'=' * 80}\n")
        for battle_key, result in results.items():
            if not result['valid']:
                print(f"\n{result['name']} ({battle_key}):")
                for error in result['errors']:
                    print(f"  - {error}")

    if apply_fixes:
        print(f"\n[OK] Corrections applied to {valid} battle books")
    else:
        print(f"\n[INFO] Validation only - no files modified")
        print(f"[INFO] Run with --apply to write corrections")

    return 0 if invalid == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
