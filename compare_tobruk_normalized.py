#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Tobruk British Comparison - Normalized Text Analysis

Compares content after normalizing whitespace and formatting differences
"""

import sys
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import re
from pathlib import Path
from difflib import SequenceMatcher

def load_json(filename):
    """Load JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_text(text):
    """
    Normalize text for comparison by:
    - Removing page markers
    - Collapsing multiple spaces/newlines
    - Converting to lowercase
    - Removing special formatting characters
    """
    # Remove page markers
    text = re.sub(r'={50,}\nPAGE \d+\n={50,}', '', text)

    # Remove underscores used as separators
    text = re.sub(r'_{10,}', '', text)

    # Collapse multiple newlines to single space
    text = re.sub(r'\n+', ' ', text)

    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Convert to lowercase for case-insensitive comparison
    text = text.lower()

    # Remove BOM and special characters
    text = text.replace('\ufeff', '')

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def extract_vehicle_names(text):
    """Extract vehicle/weapon names from text"""
    # Common patterns for vehicle/weapon names
    patterns = [
        r'Vickers\s+\w+(?:\s+[A-Z0-9-]+)?',
        r'M\d+\s+["\']?\w+["\']?',
        r'Matilda\s+\w+(?:\s+\w+)?',
        r'Valentine\s+\w+',
        r'Crusader\s+\w+',
        r'A\d+\s+\w+',
        r'\d+\s*pdr',
        r'\d+mm[^a-zA-Z]'
    ]

    names = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        names.extend(matches)

    return sorted(set(names))

def extract_numeric_stats(text):
    """Extract numeric statistics (armor values, movement, etc.)"""
    # Match patterns like: 12" 18", armor letters O N K, etc.
    stats = {
        'movement_values': re.findall(r'\d+["\']\s*\d+["\']', text),
        'armor_letters': re.findall(r'\b[I-O]\b', text),  # BattleGroup armor scale
        'calibers': re.findall(r'\d+mm', text, re.IGNORECASE),
        'pdr_guns': re.findall(r'\d+\s*pdr', text, re.IGNORECASE)
    }

    return stats

def main():
    print("="*70)
    print("Enhanced Tobruk British Comparison - Normalized Analysis")
    print("="*70)

    # Load JSON data
    print("\n📂 Loading extracted data...")
    ocr_data = load_json('tobruk_british_ocr_600dpi.json')
    txt_data = load_json('tobruk_british_existing_text.json')

    ocr_text = ocr_data['full_text']
    txt_text = txt_data['full_text']

    print(f"✅ OCR text: {len(ocr_text):,} chars")
    print(f"✅ Existing text: {len(txt_text):,} chars")

    # Normalize both texts
    print("\n🔄 Normalizing text (removing formatting differences)...")
    ocr_normalized = normalize_text(ocr_text)
    txt_normalized = normalize_text(txt_text)

    print(f"✅ OCR normalized: {len(ocr_normalized):,} chars")
    print(f"✅ Existing normalized: {len(txt_normalized):,} chars")

    # Calculate normalized similarity
    print("\n📊 Calculating content similarity (format-independent)...")
    matcher = SequenceMatcher(None, txt_normalized, ocr_normalized)
    normalized_similarity = matcher.ratio() * 100

    print(f"\n✅ Normalized Similarity: {normalized_similarity:.2f}%")

    # Extract and compare structured data
    print("\n🔍 Extracting structured data...")

    # Vehicle names
    ocr_vehicles = extract_vehicle_names(ocr_text)
    txt_vehicles = extract_vehicle_names(txt_text)

    print(f"\n📋 Vehicle/Weapon Names Found:")
    print(f"   OCR: {len(ocr_vehicles)} items")
    print(f"   Text: {len(txt_vehicles)} items")

    common_vehicles = set(ocr_vehicles) & set(txt_vehicles)
    ocr_only = set(ocr_vehicles) - set(txt_vehicles)
    txt_only = set(txt_vehicles) - set(ocr_vehicles)

    print(f"\n   Common: {len(common_vehicles)} items")
    if ocr_only:
        print(f"   OCR only: {len(ocr_only)} items - {list(ocr_only)[:5]}")
    if txt_only:
        print(f"   Text only: {len(txt_only)} items - {list(txt_only)[:5]}")

    # Numeric stats
    ocr_stats = extract_numeric_stats(ocr_text)
    txt_stats = extract_numeric_stats(txt_text)

    print(f"\n📊 Numeric Statistics:")
    for key in ocr_stats:
        ocr_count = len(ocr_stats[key])
        txt_count = len(txt_stats[key])
        print(f"   {key}: OCR={ocr_count}, Text={txt_count}")

    # Final assessment
    print(f"\n{'='*70}")
    print("FINAL ASSESSMENT")
    print(f"{'='*70}")

    print(f"\n📏 Raw Comparison:")
    print(f"   Similarity: 31.77% (line-by-line, format-sensitive)")

    print(f"\n📏 Normalized Comparison:")
    print(f"   Similarity: {normalized_similarity:.2f}% (content-only, format-independent)")

    if normalized_similarity >= 90:
        print(f"\n✅ VERDICT: Content match is EXCELLENT (≥90%)")
        print(f"   Differences are primarily formatting/line breaks")
    elif normalized_similarity >= 75:
        print(f"\n⚠️  VERDICT: Content match is GOOD (≥75%)")
        print(f"   Some content differences exist beyond formatting")
    else:
        print(f"\n❌ VERDICT: Significant content differences (<75%)")
        print(f"   OCR may have errors or documents differ substantially")

    # Save detailed report
    report = {
        'raw_similarity': 31.77,
        'normalized_similarity': normalized_similarity,
        'ocr_chars_raw': len(ocr_text),
        'txt_chars_raw': len(txt_text),
        'ocr_chars_normalized': len(ocr_normalized),
        'txt_chars_normalized': len(txt_normalized),
        'vehicles_ocr': ocr_vehicles,
        'vehicles_txt': txt_vehicles,
        'vehicles_common': list(common_vehicles),
        'vehicles_ocr_only': list(ocr_only),
        'vehicles_txt_only': list(txt_only),
        'stats_ocr': ocr_stats,
        'stats_txt': txt_stats
    }

    with open('tobruk_british_normalized_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved: tobruk_british_normalized_analysis.json")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    main()
