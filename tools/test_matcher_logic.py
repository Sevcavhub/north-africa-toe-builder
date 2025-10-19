#!/usr/bin/env python3
"""
Test equipment matcher logic
Verify name normalization, matching algorithms work correctly
"""

import re
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
WITW_FILE = PROJECT_ROOT / "data" / "iterations" / "iteration_2" / "Timeline_TOE_Reconstruction" / "OUTPUT" / "v5_development" / "canonical_equipment_master_with_witw_ALL_NATIONS.json"
ONWAR_FILE = PROJECT_ROOT / "data" / "output" / "afv_data" / "afv_complete_with_specs.json"

def normalize_name(name):
    """Normalize equipment name for matching (from matcher)"""
    if not name:
        return ""

    name = name.lower()

    # Special handling for model numbers: convert "h-39" or "h 39" to "h39"
    # This handles variants like: H-39/H39, R-35/R35, S-35/S35, etc.
    name = re.sub(r'([a-z])[\s\-](\d+)', r'\1\2', name)

    # Remove all remaining punctuation (including hyphens)
    name = re.sub(r'[.,/\-]', ' ', name)

    # Collapse multiple spaces
    name = ' '.join(name.split())
    return name

def find_afv_matches_test(witw_name, onwar_data):
    """Test AFV matching logic"""
    witw_name_norm = normalize_name(witw_name)

    matches = []

    for onwar_item in onwar_data:
        onwar_name = onwar_item.get('vehicle_name', '')
        onwar_name_norm = normalize_name(onwar_name)

        # Exact match
        if witw_name_norm == onwar_name_norm:
            score = 100
            match_type = "exact"
        # Partial match
        elif witw_name_norm in onwar_name_norm or onwar_name_norm in witw_name_norm:
            score = 85
            match_type = "partial"
        else:
            # Word-based matching
            witw_words = set(witw_name_norm.split())
            onwar_words = set(onwar_name_norm.split())
            common = len(witw_words & onwar_words)
            if common >= 2:
                score = 70
                match_type = f"word_match ({common} common words)"
            else:
                continue

        matches.append({
            'onwar_name': onwar_name,
            'onwar_name_norm': onwar_name_norm,
            'country': onwar_item.get('country'),
            'score': score,
            'match_type': match_type
        })

    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches

def main():
    print("="*80)
    print("EQUIPMENT MATCHER LOGIC TEST")
    print("="*80)

    # Load WITW data
    print("\n[1] Loading WITW data...")
    with open(WITW_FILE, 'r', encoding='utf-8') as f:
        witw_data = json.load(f)

    # Get French equipment
    french_equipment = []
    for canonical_id, item in witw_data.get('equipment', {}).items():
        nation = item.get('nation', '').lower()
        if 'french' in nation or nation == 'french':
            item['canonical_id'] = canonical_id
            french_equipment.append(item)

    print(f"[OK] Loaded {len(french_equipment)} French equipment items")

    # Load OnWar data
    print("\n[2] Loading OnWar AFV data...")
    with open(ONWAR_FILE, 'r', encoding='utf-8') as f:
        onwar_data = json.load(f)

    print(f"[OK] Loaded {len(onwar_data)} OnWar AFV entries (all nations)")

    # Test cases
    print("\n" + "="*80)
    print("TEST CASES")
    print("="*80)

    test_cases = [
        "Hotchkiss H39",
        "Renault R35",
        "Somua S35",
        "Char B1 bis",
        "Laffly W15 TCC"
    ]

    for test_name in test_cases:
        print(f"\n{'='*80}")
        print(f"Testing: {test_name}")
        print(f"{'='*80}")

        # Normalize
        normalized = normalize_name(test_name)
        print(f"Normalized: '{test_name}' -> '{normalized}'")

        # Find matches
        matches = find_afv_matches_test(test_name, onwar_data)

        if matches:
            print(f"\nFound {len(matches)} potential matches:")
            for idx, match in enumerate(matches[:5], 1):
                print(f"\n  Match #{idx}:")
                print(f"    OnWar Name: {match['onwar_name']}")
                print(f"    Normalized: {match['onwar_name_norm']}")
                print(f"    Country: {match['country']}")
                print(f"    Score: {match['score']}%")
                print(f"    Type: {match['match_type']}")
        else:
            print(f"\n  [X] NO MATCHES FOUND")

    # Summary: Check all French equipment
    print("\n" + "="*80)
    print("FULL FRENCH EQUIPMENT SCAN")
    print("="*80)

    no_matches = []
    low_confidence = []
    good_matches = []

    for item in french_equipment:
        name = item.get('canonical_name', '')
        matches = find_afv_matches_test(name, onwar_data)

        if not matches:
            no_matches.append(name)
        elif matches[0]['score'] < 85:
            low_confidence.append((name, matches[0]['score']))
        else:
            good_matches.append(name)

    print(f"\nResults:")
    print(f"  [OK] Good matches (>=85%): {len(good_matches)} items")
    print(f"  [WARN] Low confidence (<85%): {len(low_confidence)} items")
    print(f"  [NONE] No matches: {len(no_matches)} items")

    if low_confidence:
        print(f"\nLow confidence matches:")
        for name, score in low_confidence[:10]:
            print(f"  - {name} ({score}%)")

    if no_matches:
        print(f"\nNo matches found:")
        for name in no_matches[:15]:
            print(f"  - {name}")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
