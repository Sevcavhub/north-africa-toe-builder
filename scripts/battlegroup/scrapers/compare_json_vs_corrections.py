#!/usr/bin/env python3
"""
Compare new parser JSON results vs. user corrections.
"""

import csv
import json
from pathlib import Path

JSON_PATH = Path(__file__).parent.parent.parent.parent / "table_gun_extraction_results.json"
CSV_PATH = Path(__file__).parent.parent.parent.parent / "canadian_guns_review.csv"

def compare_canadian_guns():
    """Compare new parser results vs user corrections"""

    # Read user corrections
    corrected_guns = {}
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            corrected_guns[row['name']] = row

    # Read parser results
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        parser_data = json.load(f)

    parser_guns = {gun['name']: gun for gun in parser_data.get('canadian', [])}

    print("="*120)
    print("NEW PARSER vs CORRECTIONS COMPARISON - CANADIAN GUNS")
    print("="*120)
    print(f"\nUser corrected: {len(corrected_guns)} guns")
    print(f"Parser extracted: {len(parser_guns)} guns")
    print(f"Missing from parser: {len(corrected_guns) - len(parser_guns)} guns\n")

    # Show missing guns
    missing_guns = set(corrected_guns.keys()) - set(parser_guns.keys())
    if missing_guns:
        print(f"MISSING GUNS ({len(missing_guns)}):")
        print("-"*120)
        for gun in sorted(missing_guns):
            row = corrected_guns[gun]
            he_str = f"{row['he_dice']}D6/{row['he_target']}" if row['he_dice'] else "No HE"
            print(f"  - {gun:30s} | {row['caliber_mm']:>4s}mm | HE:{he_str:12s}")
        print()

    # Compare extracted guns
    print(f"EXTRACTED GUNS COMPARISON ({len(parser_guns)}):")
    print("-"*120)

    exact_matches = 0
    partial_matches = 0

    for gun_name in sorted(parser_guns.keys()):
        if gun_name not in corrected_guns:
            print(f"\n[!] {gun_name}: In parser but NOT in corrections")
            continue

        parsed = parser_guns[gun_name]
        corrected = corrected_guns[gun_name]

        errors = []

        # Compare caliber
        if str(parsed.get('caliber_mm') or '') != str(corrected['caliber_mm'] or ''):
            errors.append(f"Caliber: {parsed.get('caliber_mm')} vs {corrected['caliber_mm']}")

        # Compare HE dice/target
        if str(parsed.get('he_dice') or '') != str(corrected['he_dice'] or ''):
            errors.append(f"HE dice: {parsed.get('he_dice')} vs {corrected['he_dice']}")

        if str(parsed.get('he_target') or '') != str(corrected['he_target'] or ''):
            errors.append(f"HE target: {parsed.get('he_target')} vs {corrected['he_target']}")

        # Compare HE ranges
        he_fields = ['he_0_10', 'he_10_20', 'he_20_30', 'he_30_40', 'he_40_50', 'he_50_70']
        parsed_he_ranges = [str(parsed.get(f) or '') for f in he_fields]
        corrected_he_ranges = [str(corrected[f] or '') for f in he_fields]

        if parsed_he_ranges != corrected_he_ranges:
            errors.append(f"HE ranges: {'/'.join(parsed_he_ranges)} vs {'/'.join(corrected_he_ranges)}")

        # Compare AP ranges
        ap_fields = ['ap_0_10', 'ap_10_20', 'ap_20_30', 'ap_30_40', 'ap_40_50', 'ap_50_70']
        parsed_ap_ranges = [str(parsed.get(f) or '') for f in ap_fields]
        corrected_ap_ranges = [str(corrected[f] or '') for f in ap_fields]

        if parsed_ap_ranges != corrected_ap_ranges:
            errors.append(f"AP ranges: {'/'.join(parsed_ap_ranges)} vs {'/'.join(corrected_ap_ranges)}")

        # Show results
        if errors:
            print(f"\n[X] {gun_name}")
            for error in errors:
                print(f"    - {error}")
            partial_matches += 1
        else:
            print(f"[OK] {gun_name}")
            exact_matches += 1

    # Summary statistics
    print("\n" + "="*120)
    print("SUMMARY")
    print("="*120)
    print(f"Guns in corrections:  {len(corrected_guns)}")
    print(f"Guns parsed:          {len(parser_guns)}")
    print(f"Missing from parser:  {len(missing_guns)} ({len(missing_guns)/len(corrected_guns)*100:.1f}%)")
    print(f"Exact matches:        {exact_matches} ({exact_matches/len(corrected_guns)*100:.1f}%)")
    print(f"Partial matches:      {partial_matches} ({partial_matches/len(corrected_guns)*100:.1f}%)")
    print(f"Total extracted:      {len(parser_guns)} ({len(parser_guns)/len(corrected_guns)*100:.1f}%)")

if __name__ == '__main__':
    compare_canadian_guns()
