#!/usr/bin/env python3
"""
BattleGroup Datacard Format Analyzer

Analyzes the structure of BattleGroup text files to identify patterns
for extraction. This helps design the regex patterns for datacard_scraper.py.

Usage:
    python scripts/battlegroup/scrapers/analyze_datacard_format.py
"""

import re
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESOURCE_DIR = PROJECT_ROOT / "Resource Documents" / "Battlegroup Game"


def analyze_file(file_path: Path):
    """Analyze a single datacard file for patterns"""
    print(f"\n{'='*70}")
    print(f"ANALYZING: {file_path.name}")
    print(f"{'='*70}")

    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')

    print(f"\nTotal lines: {len(lines)}")
    print(f"Total characters: {len(content)}")

    # Find vehicle name patterns
    vehicle_patterns = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Look for patterns like "M4 SHERMAN (A1, A2, A3) 1942-45"
        # All caps name with optional variants and year range
        if re.match(r'^[A-Z0-9\s\-]+(\([^)]+\))?\s*\d{4}(-\d{2,4})?', line):
            vehicle_patterns.append((i, line))

    print(f"\n[VEHICLES] Potential vehicle names found: {len(vehicle_patterns)}")
    if vehicle_patterns:
        print("\nFirst 10 examples:")
        for i, (line_num, text) in enumerate(vehicle_patterns[:10]):
            print(f"   Line {line_num}: {text}")

    # Find movement patterns
    movement_patterns = []
    for i, line in enumerate(lines):
        if re.search(r'(Off-Road|Road):\s*\d+', line, re.IGNORECASE):
            movement_patterns.append((i, line.strip()))

    print(f"\n[MOVEMENT] Movement patterns found: {len(movement_patterns)}")
    if movement_patterns:
        print("\nFirst 5 examples:")
        for i, (line_num, text) in enumerate(movement_patterns[:5]):
            print(f"   Line {line_num}: {text}")

    # Find armor patterns
    armor_patterns = []
    for i, line in enumerate(lines):
        if re.search(r'(Front|Side|Rear|Turret):\s*[A-O]', line, re.IGNORECASE):
            armor_patterns.append((i, line.strip()))

    print(f"\n[ARMOR] Armor patterns found: {len(armor_patterns)}")
    if armor_patterns:
        print("\nFirst 5 examples:")
        for i, (line_num, text) in enumerate(armor_patterns[:5]):
            print(f"   Line {line_num}: {text}")

    # Find weapon patterns
    weapon_patterns = []
    for i, line in enumerate(lines):
        # Look for caliber designations (75mm, 88mm, etc.)
        if re.search(r'\d+mm\s+L\d+', line, re.IGNORECASE):
            weapon_patterns.append((i, line.strip()))

    print(f"\n[WEAPONS] Weapon patterns found: {len(weapon_patterns)}")
    if weapon_patterns:
        print("\nFirst 10 examples:")
        for i, (line_num, text) in enumerate(weapon_patterns[:10]):
            print(f"   Line {line_num}: {text}")

    # Find HE/AP patterns
    he_ap_patterns = []
    for i, line in enumerate(lines):
        if re.search(r'(HE|AP):\s*[\d\-/+,\s]+', line, re.IGNORECASE):
            he_ap_patterns.append((i, line.strip()))

    print(f"\n[HE/AP] HE/AP patterns found: {len(he_ap_patterns)}")
    if he_ap_patterns:
        print("\nFirst 10 examples:")
        for i, (line_num, text) in enumerate(he_ap_patterns[:10]):
            print(f"   Line {line_num}: {text}")

    # Find section headers
    section_headers = []
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        # All caps lines that might be section headers
        if line_upper and line_upper == line.strip() and len(line.strip()) > 5:
            if not re.search(r'\d{4}', line):  # Exclude year ranges
                section_headers.append((i, line.strip()))

    print(f"\n[HEADERS] Potential section headers: {len(section_headers)}")
    if section_headers:
        # Get unique headers
        unique_headers = Counter([text for _, text in section_headers])
        print("\nMost common headers:")
        for header, count in unique_headers.most_common(20):
            print(f"   {header}: {count}")

    # Find points/BR patterns
    points_patterns = []
    for i, line in enumerate(lines):
        if re.search(r'(Points|BR|Battle\s*Rating):\s*\d+', line, re.IGNORECASE):
            points_patterns.append((i, line.strip()))

    print(f"\n[POINTS/BR] Points/BR patterns found: {len(points_patterns)}")
    if points_patterns:
        print("\nFirst 10 examples:")
        for i, (line_num, text) in enumerate(points_patterns[:10]):
            print(f"   Line {line_num}: {text}")

    # Sample a few complete vehicle profiles
    print(f"\n[SAMPLE PROFILES] SAMPLE VEHICLE PROFILES")
    print("="*70)

    if vehicle_patterns:
        # Get first 3 vehicle profiles (30 lines each)
        for i, (start_line, vehicle_name) in enumerate(vehicle_patterns[:3]):
            print(f"\n--- Profile {i+1}: {vehicle_name} (Line {start_line}) ---")
            end_line = min(start_line + 30, len(lines))
            for line_num in range(start_line, end_line):
                print(f"{line_num:4d} | {lines[line_num]}")
            print()


def main():
    """Analyze all datacard files"""
    files_to_analyze = [
        RESOURCE_DIR / "Battlegroup-Kursk.txt",
        RESOURCE_DIR / "Battlegroup-DataCards-British.txt",
        RESOURCE_DIR / "Avanti Italian Forces.txt",
    ]

    for file_path in files_to_analyze:
        if file_path.exists():
            analyze_file(file_path)
        else:
            print(f"\n⚠️  File not found: {file_path}")

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print("\nUse these patterns to design extraction regex in datacard_scraper.py")


if __name__ == "__main__":
    main()
