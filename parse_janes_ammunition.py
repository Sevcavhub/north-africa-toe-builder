#!/usr/bin/env python3
"""
Parse Jane's WWII Tanks Guide for Ammunition Capacity Data

Extracts ammunition/rounds carried for each vehicle mentioned in the guide.

Strategy:
1. Read entire text file
2. Search for patterns: "X rounds", "carried X", "stowed X"
3. Extract context around ammunition mentions (vehicle names)
4. Create structured ammunition capacity data

Output: CSV with columns: vehicle_name, ammunition_count, source_context
"""

import re
from pathlib import Path
import csv

JANES_PATH = Path("Resource Documents/Janes-WorldWarIiTanksAndFightingVehicles-TheCompleteGuide-text-pdf.txt")


def extract_ammunition_data(text):
    """Extract ammunition capacity data from Jane's guide text."""

    ammunition_data = []

    # Pattern 1: "X rounds" with optional context
    pattern1 = re.compile(r'(\d+)\s+rounds', re.IGNORECASE)

    # Pattern 2: "carried X" / "stowed X" / "provided X"
    pattern2 = re.compile(r'(carried|stowed|provided)\s+(\d+)', re.IGNORECASE)

    # Pattern 3: "with X rounds"
    pattern3 = re.compile(r'with\s+(\d+)\s+rounds', re.IGNORECASE)

    # Pattern 4: "(X rounds)"
    pattern4 = re.compile(r'\((\d+)\s+rounds\)', re.IGNORECASE)

    # Split into lines for context extraction
    lines = text.split('\n')

    for i, line in enumerate(lines):
        # Look for ammunition mentions
        matches = []

        # Check all patterns
        matches.extend(pattern1.findall(line))
        matches.extend([m[1] for m in pattern2.findall(line)])
        matches.extend(pattern3.findall(line))
        matches.extend(pattern4.findall(line))

        if matches:
            # Get context (current line + previous 3 lines + next 2 lines)
            start = max(0, i - 3)
            end = min(len(lines), i + 3)
            context_lines = lines[start:end]
            context = ' '.join(context_lines).strip()

            # Clean up context (remove excessive whitespace)
            context = re.sub(r'\s+', ' ', context)

            for ammo_count in matches:
                ammunition_data.append({
                    'ammunition_count': ammo_count,
                    'line_number': i + 1,
                    'context': context[:300]  # Limit context to 300 chars
                })

    return ammunition_data


def identify_vehicle_names(context):
    """
    Try to identify vehicle name from context.

    Common patterns:
    - Tank names before "with X rounds"
    - Names in parentheses like "Matilda II"
    - German PzKw designations
    - British cruiser/infantry tank names
    - American M3/M4 designations
    """

    # Common vehicle name patterns (North Africa relevant)
    vehicle_patterns = [
        # British
        r'Matilda\s*I{1,3}?',
        r'Valentine\s*[IVX]+',
        r'Crusader\s*[IVX]+',
        r'Cruiser\s*[IVX]+',
        r'Churchill\s*[IVX]+',
        r'Stuart\s*[IVX]*',
        r'M3\s*Stuart',
        r'M3A1\s*Stuart',
        r'M5\s*Stuart',
        r'Grant',
        r'Lee',
        r'M3\s*Lee',
        r'M3\s*Grant',
        r'Sherman\s*[IVX]*',
        r'M4\s*Sherman',
        r'M4A1\s*Sherman',

        # German
        r'Panzer\s*I{1,4}\s*[A-Z]?',
        r'PzKw\s*I{1,4}\s*[A-Z]?',
        r'Panther',
        r'Tiger\s*I?',
        r'SdKfz\s*\d+',

        # Italian
        r'M\d{2}/\d{2}',  # M11/39, M13/40, M14/41
        r'L3/\d{2}',      # L3/35
        r'L6/\d{2}',      # L6/40
        r'CV-\d{2}',      # CV-33, CV-35

        # Generic
        r'\d+pdr',  # 2pdr, 6pdr, etc.
        r'\d+mm',   # Caliber mentions
    ]

    matches = []
    for pattern in vehicle_patterns:
        found = re.findall(pattern, context, re.IGNORECASE)
        matches.extend(found)

    return matches


def main():
    """Main execution."""

    print("=" * 80)
    print("JANE'S WWII TANKS AMMUNITION CAPACITY EXTRACTION")
    print("=" * 80)

    # Read Jane's guide
    if not JANES_PATH.exists():
        print(f"\nERROR: File not found: {JANES_PATH}")
        return

    print(f"\nReading: {JANES_PATH.name}")
    with open(JANES_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    print(f"File size: {len(text):,} characters")

    # Extract ammunition data
    print("\nExtracting ammunition data...")
    ammo_data = extract_ammunition_data(text)

    print(f"Found {len(ammo_data)} ammunition mentions\n")

    # Try to identify vehicles
    print("Identifying vehicle names...")
    for entry in ammo_data:
        vehicles = identify_vehicle_names(entry['context'])
        entry['potential_vehicles'] = vehicles

    # Filter to entries with vehicle names
    with_vehicles = [e for e in ammo_data if e['potential_vehicles']]

    print(f"  {len(with_vehicles)} mentions with potential vehicle matches")
    print(f"  {len(ammo_data) - len(with_vehicles)} mentions without vehicle context\n")

    # Save to CSV
    output_file = "janes_ammunition_extraction.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ammunition_count', 'line_number', 'potential_vehicles', 'context'])

        for entry in with_vehicles:
            vehicles_str = ', '.join(entry['potential_vehicles'])
            writer.writerow([
                entry['ammunition_count'],
                entry['line_number'],
                vehicles_str,
                entry['context']
            ])

    print(f"Saved: {output_file}")

    # Show sample
    print(f"\nSample extractions (first 20 with vehicle names):\n")
    print(f"{'Ammo':>5} | {'Line':>5} | {'Vehicles':30} | Context")
    print("-" * 120)

    for entry in with_vehicles[:20]:
        vehicles_str = ', '.join(entry['potential_vehicles'][:2])  # Limit to 2 vehicles
        context_short = entry['context'][:70]
        print(f"{entry['ammunition_count']:>5} | {entry['line_number']:>5} | "
              f"{vehicles_str[:30]:30} | {context_short}")

    print(f"\n... ({len(with_vehicles) - 20} more entries in CSV)")

    # Statistics
    print(f"\n" + "=" * 80)
    print("EXTRACTION STATISTICS")
    print("=" * 80)

    ammo_counts = [int(e['ammunition_count']) for e in with_vehicles]

    if ammo_counts:
        print(f"\nAmmunition capacity range:")
        print(f"  Minimum: {min(ammo_counts)} rounds")
        print(f"  Maximum: {max(ammo_counts)} rounds")
        print(f"  Average: {sum(ammo_counts) / len(ammo_counts):.1f} rounds")

        # Most common ammo counts
        from collections import Counter
        common_counts = Counter(ammo_counts).most_common(10)

        print(f"\nMost common ammunition capacities:")
        for count, freq in common_counts:
            print(f"  {count:>4} rounds: {freq:>3} mentions")

    print(f"\n" + "=" * 80)
    print("Next steps:")
    print("  1. Review CSV file: janes_ammunition_extraction.csv")
    print("  2. Manually verify vehicle-ammunition mappings")
    print("  3. Import verified data to database")
    print("=" * 80)


if __name__ == "__main__":
    main()
