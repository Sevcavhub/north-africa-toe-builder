#!/usr/bin/env python3
"""
Parse Jane's WWII Tanks guide for ammunition capacity data.

Extracts ammunition/shell counts for vehicles and stores them for database import.
Searches for patterns like:
- "carried 39 rounds"
- "ammunition stowage was 87 rounds"
- "stowage comprised 79 rounds of 75mm"
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# File paths
JANES_FILE = Path("D:/north-africa-toe-builder/Resource Documents/Janes-WorldWarIiTanksAndFightingVehicles-TheCompleteGuide-text-pdf.txt")
OUTPUT_FILE = Path("D:/north-africa-toe-builder/data/ammunition_capacity_janes.json")

class JanesAmmoParser:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.vehicles = []  # List of extracted vehicle ammunition data

    def load_file(self):
        """Load the Jane's guide text file."""
        print(f"Loading {self.file_path}...")
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.content = f.read()
        print(f"Loaded {len(self.content):,} characters")

    def find_vehicle_sections(self) -> List[Tuple[str, str]]:
        """
        Find vehicle sections in the text.
        Jane's guide typically has vehicle names as headers.
        """
        # Common tank/vehicle name patterns
        vehicle_patterns = [
            r'\n([A-Z][A-Za-z0-9\s\-]+(?:Tank|Panzer|Sherman|Churchill|Crusader|Valentine|Stuart|Grant|Lee|Matilda|Tiger|Panther))',
            r'\n(Pz\.?Kw\.?\s*[IVX]+[A-Za-z]*)',
            r'\n(SdKfz\s*\d+)',
            r'\n(M\d+[A-Za-z]*\s+(?:Tank|Medium|Light|Heavy))',
        ]

        sections = []
        lines = self.content.split('\n')

        current_vehicle = None
        current_text = []

        for i, line in enumerate(lines):
            # Check if line looks like a vehicle header
            is_header = False
            for pattern in vehicle_patterns:
                match = re.match(pattern, '\n' + line)
                if match:
                    # Save previous section
                    if current_vehicle and current_text:
                        sections.append((current_vehicle, '\n'.join(current_text)))

                    current_vehicle = match.group(1).strip()
                    current_text = []
                    is_header = True
                    break

            if not is_header and current_vehicle:
                current_text.append(line)

        # Save last section
        if current_vehicle and current_text:
            sections.append((current_vehicle, '\n'.join(current_text)))

        return sections

    def extract_ammunition_data(self) -> List[Dict]:
        """
        Extract ammunition capacity data from the text.

        Patterns to match:
        - "carried 39 rounds"
        - "stowage was 87 rounds"
        - "stowage comprised 79 rounds of 75mm"
        - "ammunition stowage to 28 rounds"
        """
        ammunition_data = []

        # Ammunition capacity patterns
        patterns = [
            # "carried X rounds"
            r'carried\s+(\d+)\s+rounds',
            # "stowage was X rounds"
            r'stowage\s+was\s+(\d+)\s+rounds',
            # "stowage comprised X rounds"
            r'stowage\s+comprised\s+(\d+)\s+rounds',
            # "ammunition stowage X rounds"
            r'ammunition\s+stowage\s+(\d+)\s+rounds',
            # "X rounds were carried"
            r'(\d+)\s+rounds\s+were\s+carried',
            # "stowage ranged from X to Y rounds"
            r'stowage\s+ranged\s+from\s+(\d+)\s+to\s+(\d+)\s+rounds',
            # More specific: "carried X rounds for the main gun"
            r'carried\s+(\d+)\s+rounds\s+for\s+the\s+main\s+gun',
        ]

        lines = self.content.split('\n')

        # Context window for vehicle identification
        context_lines = 10  # Look back N lines for vehicle name

        for i, line in enumerate(lines):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Extract round count
                    if len(match.groups()) == 2:  # Range pattern
                        rounds_min = int(match.group(1))
                        rounds_max = int(match.group(2))
                        rounds = f"{rounds_min}-{rounds_max}"
                    else:
                        rounds = int(match.group(1))

                    # Try to find vehicle name in context
                    vehicle_name = self._find_vehicle_in_context(lines, i, context_lines)

                    # Extract full context sentence
                    context = line.strip()

                    ammunition_data.append({
                        'line_number': i + 1,
                        'vehicle_name': vehicle_name,
                        'rounds': rounds,
                        'context': context,
                        'pattern_matched': pattern
                    })

        return ammunition_data

    def _find_vehicle_in_context(self, lines: List[str], current_line: int, context_lines: int) -> Optional[str]:
        """
        Look backwards from current line to find vehicle name.
        """
        # Look backwards for vehicle name patterns
        vehicle_patterns = [
            r'^([A-Z][A-Za-z0-9\s\-]+(?:Tank|Panzer|Sherman|Churchill|Crusader|Valentine|Stuart|Grant|Lee|Matilda|Tiger|Panther))',
            r'^(Pz\.?Kw\.?\s*[IVX]+[A-Za-z]*)',
            r'^(SdKfz\s*\d+)',
            r'^(M\d+[A-Za-z]*(?:\s+Tank|\s+Medium|\s+Light|\s+Heavy)?)',
        ]

        for i in range(max(0, current_line - context_lines), current_line):
            line = lines[i].strip()
            for pattern in vehicle_patterns:
                match = re.match(pattern, line)
                if match:
                    return match.group(1).strip()

        return "Unknown"

    def parse(self) -> List[Dict]:
        """Main parsing method."""
        self.load_file()
        print("\nExtracting ammunition data...")

        ammunition_data = self.extract_ammunition_data()

        print(f"\nFound {len(ammunition_data)} ammunition references")

        # Deduplicate and organize by vehicle
        vehicle_ammo = {}
        for entry in ammunition_data:
            vehicle = entry['vehicle_name']
            if vehicle not in vehicle_ammo:
                vehicle_ammo[vehicle] = []
            vehicle_ammo[vehicle].append(entry)

        print(f"Organized into {len(vehicle_ammo)} unique vehicles")

        # Convert to structured output
        self.vehicles = []
        for vehicle_name, entries in vehicle_ammo.items():
            # Use the most common/highest round count
            round_counts = [e['rounds'] for e in entries if isinstance(e['rounds'], int)]
            if round_counts:
                avg_rounds = sum(round_counts) / len(round_counts)
                max_rounds = max(round_counts)

                self.vehicles.append({
                    'vehicle_name': vehicle_name,
                    'ammunition_capacity': max_rounds,  # Use max as most likely full capacity
                    'average_capacity': round(avg_rounds),
                    'references_found': len(entries),
                    'contexts': [e['context'] for e in entries[:3]]  # First 3 contexts
                })

        # Sort by vehicle name
        self.vehicles.sort(key=lambda x: x['vehicle_name'])

        return self.vehicles

    def save_results(self):
        """Save parsed ammunition data to JSON file."""
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        output = {
            'source': 'Janes WWII Tanks and Fighting Vehicles - The Complete Guide',
            'extraction_date': '2025-11-11',
            'total_vehicles': len(self.vehicles),
            'vehicles': self.vehicles
        }

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        print(f"\nSaved results to {OUTPUT_FILE}")
        print(f"Total vehicles with ammunition data: {len(self.vehicles)}")

    def print_summary(self):
        """Print summary of extracted data."""
        print("\n" + "="*80)
        print("AMMUNITION CAPACITY EXTRACTION SUMMARY")
        print("="*80)

        print(f"\nTotal vehicles found: {len(self.vehicles)}")

        # Show sample entries
        print("\nSample entries (first 20):")
        print("-" * 80)
        for vehicle in self.vehicles[:20]:
            print(f"\n{vehicle['vehicle_name']}")
            print(f"  Ammunition: {vehicle['ammunition_capacity']} rounds")
            print(f"  Average: {vehicle['average_capacity']} rounds")
            print(f"  References: {vehicle['references_found']}")
            if vehicle['contexts']:
                print(f"  Context: {vehicle['contexts'][0][:100]}...")

        # Statistics
        capacities = [v['ammunition_capacity'] for v in self.vehicles]
        if capacities:
            print(f"\nStatistics:")
            print(f"  Min capacity: {min(capacities)} rounds")
            print(f"  Max capacity: {max(capacities)} rounds")
            print(f"  Average capacity: {sum(capacities)/len(capacities):.1f} rounds")

def main():
    parser = JanesAmmoParser(JANES_FILE)
    vehicles = parser.parse()
    parser.save_results()
    parser.print_summary()

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review ammunition_capacity_janes.json for accuracy")
    print("2. Create import script to load data into database")
    print("3. Match Jane's vehicle names to database equipment names")
    print("4. Update equipment_battlegroup with ammunition data")
    print("5. Regenerate datacards with complete ammunition information")

if __name__ == '__main__':
    main()
