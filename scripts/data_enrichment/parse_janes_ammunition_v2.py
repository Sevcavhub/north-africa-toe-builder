#!/usr/bin/env python3
"""
Parse Jane's WWII Tanks guide for ammunition capacity data - Version 2.

Strategy:
1. Get list of North Africa vehicles from database
2. Search Jane's guide for each vehicle name
3. Extract ammunition capacity from surrounding text
"""

import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

# File paths
DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
JANES_FILE = Path("D:/north-africa-toe-builder/Resource Documents/Janes-WorldWarIiTanksAndFightingVehicles-TheCompleteGuide-text-pdf.txt")
OUTPUT_FILE = Path("D:/north-africa-toe-builder/data/ammunition_capacity_janes_v2.json")

class JanesAmmoParserV2:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.janes_path = JANES_FILE
        self.janes_content = ""
        self.results = []

    def load_janes(self):
        """Load Jane's guide text file."""
        print(f"Loading {self.janes_path}...")
        with open(self.janes_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.janes_content = f.read()
        print(f"Loaded {len(self.janes_content):,} characters")

    def get_north_africa_vehicles(self) -> List[Dict]:
        """Get list of AFVs from database that need ammunition data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get vehicles that are tanks, tank destroyers, assault guns, or SPGs
        query = '''
        SELECT DISTINCT e.canonical_id, e.name, e.nation, e.equipment_type
        FROM equipment e
        WHERE e.equipment_type IN ('tank', 'tank_destroyer', 'assault_gun', 'self_propelled_gun')
        ORDER BY e.nation, e.name
        '''

        cursor.execute(query)
        vehicles = []
        for row in cursor.fetchall():
            vehicles.append({
                'equipment_id': row[0],
                'name': row[1],
                'nation': row[2],
                'type': row[3]
            })

        conn.close()
        print(f"Found {len(vehicles)} North Africa AFVs in database")
        return vehicles

    def extract_ammunition_for_vehicle(self, vehicle_name: str) -> Optional[Dict]:
        """
        Search for vehicle in Jane's guide and extract ammunition capacity.
        """
        # Normalize vehicle name for searching
        search_variants = self._generate_search_variants(vehicle_name)

        # Search for each variant
        for variant in search_variants:
            # Find the vehicle mention in text
            pattern = re.compile(r'\b' + re.escape(variant) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(self.janes_content))

            if not matches:
                continue

            # For each mention, search nearby text for ammunition data
            for match in matches:
                start_pos = match.start()
                end_pos = match.end()

                # Get context (500 chars before and after)
                context_start = max(0, start_pos - 500)
                context_end = min(len(self.janes_content), end_pos + 500)
                context = self.janes_content[context_start:context_end]

                # Search for ammunition patterns in context
                ammo_data = self._extract_ammo_from_context(context)

                if ammo_data:
                    return {
                        'vehicle_name': vehicle_name,
                        'search_variant': variant,
                        'ammunition_capacity': ammo_data['rounds'],
                        'context': ammo_data['context'],
                        'confidence': ammo_data['confidence']
                    }

        return None

    def _generate_search_variants(self, vehicle_name: str) -> List[str]:
        """
        Generate search variants for a vehicle name.

        Examples:
        - "M3 Stuart" -> ["M3 Stuart", "M3", "Stuart"]
        - "PzKw III" -> ["PzKw III", "Panzer III", "Pz.Kw. III", "PzKpfw III"]
        - "Sherman M4A1" -> ["Sherman M4A1", "M4A1", "M4A1 Sherman"]
        """
        variants = [vehicle_name]  # Original name

        # Common abbreviation expansions
        expansions = {
            'PzKw': ['Panzer', 'Pz.Kw.', 'PzKpfw', 'Pz.Kpfw.'],
            'SdKfz': ['Sd.Kfz.', 'SdKfz'],
        }

        for abbrev, expansions_list in expansions.items():
            if abbrev in vehicle_name:
                for expansion in expansions_list:
                    variants.append(vehicle_name.replace(abbrev, expansion))

        # Extract model numbers (M3, M4, etc.)
        model_match = re.search(r'\b(M\d+[A-Z]?\d*)\b', vehicle_name)
        if model_match:
            variants.append(model_match.group(1))

        # Extract common names
        common_names = ['Sherman', 'Stuart', 'Grant', 'Lee', 'Churchill', 'Crusader',
                       'Valentine', 'Matilda', 'Tiger', 'Panther', 'Panzer']
        for name in common_names:
            if name.lower() in vehicle_name.lower():
                variants.append(name)

        # Deduplicate while preserving order
        seen = set()
        unique_variants = []
        for v in variants:
            if v not in seen:
                seen.add(v)
                unique_variants.append(v)

        return unique_variants

    def _extract_ammo_from_context(self, context: str) -> Optional[Dict]:
        """
        Extract ammunition capacity from context text.

        Returns dict with rounds, context snippet, and confidence score.
        """
        # Ammunition patterns (ordered by confidence/specificity)
        patterns = [
            # High confidence - explicit main gun ammo
            (r'carried\s+(\d+)\s+rounds\s+for\s+the\s+main\s+gun', 100),
            (r'(\d+)\s+rounds\s+for\s+the\s+main\s+gun', 95),

            # Medium-high confidence - general stowage
            (r'ammunition\s+stowage\s+was\s+(\d+)\s+rounds', 90),
            (r'stowage\s+was\s+(\d+)\s+rounds', 85),
            (r'carried\s+(\d+)\s+rounds', 80),

            # Medium confidence - stowage range
            (r'stowage\s+ranged?\s+from\s+(\d+)\s+to\s+(\d+)\s+rounds', 75),

            # Medium-low confidence
            (r'stowage\s+comprised\s+(\d+)\s+rounds', 70),
            (r'(\d+)\s+rounds\s+were\s+carried', 65),

            # Lower confidence - generic rounds mention
            (r'(\d+)\s+rounds', 50),
        ]

        for pattern, confidence in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                # Extract rounds
                if len(match.groups()) == 2:  # Range pattern
                    rounds = int(match.group(2))  # Use upper end of range
                else:
                    rounds = int(match.group(1))

                # Validate reasonable range for tank ammunition
                if 10 <= rounds <= 300:
                    # Extract context snippet around match
                    match_start = max(0, match.start() - 50)
                    match_end = min(len(context), match.end() + 50)
                    snippet = context[match_start:match_end].strip()

                    return {
                        'rounds': rounds,
                        'context': snippet,
                        'confidence': confidence,
                        'pattern': pattern
                    }

        return None

    def process_all_vehicles(self):
        """Process all North Africa vehicles."""
        self.load_janes()
        vehicles = self.get_north_africa_vehicles()

        print(f"\nSearching Jane's guide for {len(vehicles)} vehicles...")
        print("-" * 80)

        found_count = 0
        not_found_count = 0

        for i, vehicle in enumerate(vehicles, 1):
            if i % 10 == 0:
                print(f"Processed {i}/{len(vehicles)} vehicles...")

            ammo_data = self.extract_ammunition_for_vehicle(vehicle['name'])

            if ammo_data:
                # Merge with vehicle data
                result = {**vehicle, **ammo_data}
                self.results.append(result)
                found_count += 1
            else:
                not_found_count += 1

        print(f"\n{'='*80}")
        print(f"RESULTS:")
        print(f"  Found ammunition data: {found_count} vehicles")
        print(f"  Not found: {not_found_count} vehicles")
        print(f"  Success rate: {100.0 * found_count / len(vehicles):.1f}%")

    def save_results(self):
        """Save results to JSON file."""
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        output = {
            'source': 'Janes WWII Tanks and Fighting Vehicles - The Complete Guide',
            'extraction_date': '2025-11-11',
            'extraction_method': 'Database-driven search with name variants',
            'total_vehicles_searched': len(self.results),
            'vehicles': self.results
        }

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        print(f"\nSaved results to {OUTPUT_FILE}")

    def print_summary(self):
        """Print summary of results."""
        if not self.results:
            print("\nNo results to display")
            return

        print(f"\n{'='*80}")
        print("SAMPLE RESULTS (first 20):")
        print(f"{'='*80}")

        for vehicle in self.results[:20]:
            print(f"\n{vehicle['name']} ({vehicle['nation']})")
            print(f"  Equipment ID: {vehicle['equipment_id']}")
            print(f"  Ammunition: {vehicle['ammunition_capacity']} rounds")
            print(f"  Confidence: {vehicle['confidence']}%")
            print(f"  Search variant: {vehicle['search_variant']}")
            print(f"  Context: {vehicle['context'][:100]}...")

        # Statistics
        if self.results:
            ammo_capacities = [v['ammunition_capacity'] for v in self.results]
            confidences = [v['confidence'] for v in self.results]

            print(f"\n{'='*80}")
            print("STATISTICS:")
            print(f"{'='*80}")
            print(f"Ammunition capacity:")
            print(f"  Min: {min(ammo_capacities)} rounds")
            print(f"  Max: {max(ammo_capacities)} rounds")
            print(f"  Average: {sum(ammo_capacities)/len(ammo_capacities):.1f} rounds")
            print(f"\nConfidence scores:")
            print(f"  Min: {min(confidences)}%")
            print(f"  Max: {max(confidences)}%")
            print(f"  Average: {sum(confidences)/len(confidences):.1f}%")

            # Confidence distribution
            high_conf = len([c for c in confidences if c >= 80])
            medium_conf = len([c for c in confidences if 60 <= c < 80])
            low_conf = len([c for c in confidences if c < 60])

            print(f"\nConfidence distribution:")
            print(f"  High (80-100%): {high_conf} vehicles")
            print(f"  Medium (60-79%): {medium_conf} vehicles")
            print(f"  Low (<60%): {low_conf} vehicles")

def main():
    parser = JanesAmmoParserV2()
    parser.process_all_vehicles()
    parser.save_results()
    parser.print_summary()

    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print(f"{'='*80}")
    print("1. Review ammunition_capacity_janes_v2.json for accuracy")
    print("2. Create import script to update database")
    print("3. Update equipment_battlegroup with ammunition data")
    print("4. Regenerate datacards with complete ammunition information")

if __name__ == '__main__':
    main()
