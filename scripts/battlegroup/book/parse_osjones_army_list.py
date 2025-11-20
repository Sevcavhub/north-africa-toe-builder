#!/usr/bin/env python3
"""
Parse OSJones BattleGroup Builder print output and extract vehicle/gun names (V6.1).

V6.1 changes (November 2025):
- Use V6.1 datacard generator with weapon fallback support
- Better coverage for vehicles not manually extracted (e.g., Sherman Jumbo, rare variants)

This script parses the formatted text output from OSJones Builder print page
and extracts the equipment names that have datacards (vehicles, guns, SPGs).

Filters out:
- Infantry units (squads, teams)
- Defences (off-table artillery, emplacements)
- Generic transports (unless specified with vehicle in unit name)
- Support elements (loaders, dispatch riders)

Usage:
    python parse_osjones_army_list.py --input army_list.txt --output equipment_list.txt
    python parse_osjones_army_list.py --input army_list.txt --generate-datacards datacards/
"""

import re
import sys
from pathlib import Path
from typing import List, Set, Dict, Tuple

# Import the V6.1 datacard generator with weapon fallback
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.battlegroup.book.generate_datacards_from_army_list_v6 import ArmyListDatacardGenerator


class OSJonesArmyListParser:
    """Parse OSJones Builder print output."""

    def __init__(self):
        self.equipment_names = set()
        self.vehicle_stats = {}  # Store parsed vehicle stats from table
        self.weapon_stats = {}   # Store parsed weapon stats from table

    def parse_army_list(self, text: str) -> Dict[str, any]:
        """
        Parse OSJones army list text and extract equipment.

        Returns:
            Dictionary with:
            - force_name: Army name
            - points_total: Total points
            - br_total: Total BR
            - units: List of unit entries
            - equipment: Set of equipment names (vehicles/guns for datacards)
        """
        lines = text.split('\n')

        result = {
            'force_name': '',
            'points_total': 0,
            'br_total': 0,
            'units': [],
            'equipment': set(),
            'vehicle_stats': {},
            'weapon_stats': {}
        }

        # Parse header (force name, points, BR)
        if lines:
            result['force_name'] = lines[0].strip()

        # Parse total points/BR (e.g., "496 / 31br")
        for line in lines[:10]:
            match = re.search(r'(\d+)\s*/\s*(\d+)br', line, re.IGNORECASE)
            if match:
                result['points_total'] = int(match.group(1))
                result['br_total'] = int(match.group(2))
                break

        # Parse unit sections and extract equipment
        current_unit = None
        in_stats_table = False

        for i, line in enumerate(lines):
            line = line.strip()

            # Detect stat table section (starts with "Move    Armour    Weapon")
            if 'Move' in line and 'Armour' in line and 'Weapon' in line:
                in_stats_table = True
                continue

            # Detect weapon performance table (starts with weapon name and ranges)
            # Also exit stat table when encountering section-level equipment (pure text, no stats)
            if re.match(r'^[\w\d.]+\s+0"-10"', line):
                in_stats_table = False
                continue  # Skip weapon performance table rows entirely

            # Parse vehicle stat table rows
            if in_stats_table and line and not line.startswith('ID:H:A:'):
                vehicle_stat = self.parse_vehicle_stat_row(line)
                if vehicle_stat:
                    result['vehicle_stats'][vehicle_stat['name']] = vehicle_stat
                    result['equipment'].add(vehicle_stat['name'])
                continue

            # Parse unit entries (e.g., "Panzer II Platoon")
            if line and not line.startswith('ID:H:A:'):
                # Unit header with points/BR (e.g., "65/6BR")
                match = re.match(r'(\d+)/(\d+)BR', line)
                if match:
                    if current_unit:
                        result['units'].append(current_unit)
                    current_unit = {
                        'points': int(match.group(1)),
                        'br': int(match.group(2)),
                        'equipment': []
                    }
                    continue

                # Unit name (next line after points/BR)
                if current_unit and 'name' not in current_unit:
                    current_unit['name'] = line
                    # Also extract equipment from unit name line
                    # (e.g., "76.2mmL51 Gun, 3-man loader team, Medium Truck")
                    equipment = self.extract_equipment_from_unit_line(line)
                    if equipment:
                        current_unit['equipment'].extend(equipment)
                        result['equipment'].update(equipment)
                    continue

                # Equipment in unit (e.g., "3 Panzer II/Fs", "2 Panzer III G")
                if current_unit and line:
                    equipment = self.extract_equipment_from_unit_line(line)
                    if equipment:
                        current_unit['equipment'].extend(equipment)
                        result['equipment'].update(equipment)

        # Add last unit
        if current_unit:
            result['units'].append(current_unit)

        return result

    def parse_vehicle_stat_row(self, line: str) -> Dict:
        """
        Parse vehicle stat table row.

        Format: "Panzer II F    8   /   12    N / O / O    20mmL55"
        Returns: {'name': 'Panzer II F', 'movement': '8/12', 'armor': 'N/O/O', 'weapon': '20mmL55'}
        """
        # Find the movement column (starts with digit, possibly with spaces before)
        # Movement pattern: one or more digits, possibly followed by spaces and "/"
        movement_match = re.search(r'\s+(\d+)\s*(?:/|$)', line)
        if not movement_match:
            return None

        # Vehicle name is everything before the movement column
        movement_start = movement_match.start()
        vehicle_name = line[:movement_start].strip()

        # Parse the rest using the movement match position
        rest_of_line = line[movement_start:].strip()
        parts = re.split(r'\s{2,}', rest_of_line)
        if len(parts) < 2:
            return None

        # Skip non-vehicle rows
        if not vehicle_name or vehicle_name in ['Move', 'Armour', 'Weapon', 'Special']:
            return None

        # Skip weapon performance table rows (ammunition types like "HE [M] (4/4+)" or "AP (-)")
        # These have names starting with "HE", "AP", "APCR", "APDS", "HEAT", etc.
        if re.match(r'^(HE|AP|APCR|APDS|HEAT|HESH|Smoke)\s*[\[\(]', vehicle_name, re.IGNORECASE):
            return None

        # Skip rows that are all numbers (weapon performance data columns)
        if len(parts) > 0 and all(part.strip().isdigit() or not part.strip() for part in parts):
            return None

        # Extract movement (e.g., "8   /   12")
        movement = parts[0].strip() if len(parts) > 0 else ''
        movement = re.sub(r'\s+', '', movement)  # Remove spaces: "8/12"

        # Extract armor (e.g., "N / O / O")
        armor = parts[1].strip() if len(parts) > 1 else ''
        armor = re.sub(r'\s+', '', armor)  # Remove spaces: "N/O/O"

        # Extract weapon (e.g., "20mmL55")
        weapon = parts[2].strip() if len(parts) > 2 else ''

        # Extract special rules (e.g., "Open-Topped")
        special = parts[3].strip() if len(parts) > 3 else ''

        return {
            'name': vehicle_name,
            'movement': movement,
            'armor': armor,
            'weapon': weapon,
            'special': special
        }

    def extract_equipment_from_unit_line(self, line: str) -> List[str]:
        """
        Extract equipment names from unit composition line.

        Examples:
        - "3 Panzer II/Fs" -> ["Panzer II F"]
        - "2 Panzer III G, 1 Panzer III J (lang)" -> ["Panzer III G", "Panzer III J (lang)"]
        - "76.2mmL51 Gun, 3-man loader team, Medium Truck" -> ["76.2mmL51"]
        - "SdKfz 251/1, Anti-tank grenades" -> ["SdKfz 251/1"]

        Returns list of equipment names (filters out infantry/support elements).
        """
        equipment = []

        # Skip pure infantry units
        skip_terms = [
            'squad', 'team', 'section', 'platoon', 'company',
            'infantry', 'grenadier', 'schützen', 'kradschützen',
            'loader', 'dispatch rider', 'signals', 'headquarters',
            'off-table', 'anti-tank grenades', 'smoke grenades',
            'forward observer', 'artillery observer'
        ]

        line_lower = line.lower()
        if any(term in line_lower for term in skip_terms):
            # Check if there's a vehicle mentioned despite infantry context
            # e.g., "SdKfz 251/1, Anti-tank grenades" -> extract SdKfz 251/1
            pass

        # Pattern 0: Check for gun calibers FIRST (e.g., "76.2mmL51 Gun, 3-man loader team")
        # Match specific gun calibers before trying other patterns
        gun_match = re.match(r'^(\d+(?:\.\d+)?mm\w+)\s+(?:Gun|Howitzer)', line, re.IGNORECASE)
        if gun_match:
            name = gun_match.group(1).strip()
            equipment.append(name)
            return equipment  # Return early, don't try other patterns

        # Pattern 1: "3 Panzer II/Fs" or "2 Panzer III G, 1 Panzer III J (lang)" or "1 A13 and 2 A9" (quantity + name pattern)
        # First, normalize separators: replace " and " with ", " to simplify parsing
        normalized_line = re.sub(r'\s+and\s+', ', ', line)
        # Match multiple equipment items separated by commas with quantities
        # Pattern matches: digit(s) + space + equipment name (alphanumeric with optional spaces) + lookahead for comma or end
        matches = re.findall(r'(\d+)\s+([A-Za-z0-9]+(?:\s+[A-Za-z0-9]+)*?)(?=\s*,|\s*$)', normalized_line)
        for quantity, name in matches:
            name = name.strip()
            # Clean up variant suffixes like "/Fs" -> " F"
            name = re.sub(r'/([A-Za-z])s$', r' \1', name)
            if self.is_datacard_equipment(name):
                equipment.append(name)

        # Pattern 2: Vehicle at start of line (e.g., "SdKfz 251/1, Anti-tank grenades")
        if not equipment:
            if re.match(r'^((?:SdKfz|Marder|Panzer|M\d+|Crusader|Matilda|Sherman|Grant|Lee|Stuart)\s+[\w/\(\)]+)', line, re.IGNORECASE):
                match = re.match(r'^([A-Za-z0-9][^,]+)', line)
                if match:
                    name = match.group(1).strip()
                    if self.is_datacard_equipment(name):
                        equipment.append(name)

        return equipment

    def is_datacard_equipment(self, name: str) -> bool:
        """
        Check if equipment name is something that gets a datacard.

        Returns True for:
        - Tanks (Panzer, Sherman, Matilda, etc.)
        - AFVs (SdKfz, Marder, etc.)
        - Towed guns (PaK, FlaK, etc.)
        - SPGs (StuG, Semovente, etc.)

        Returns False for:
        - Infantry (squad, team, section)
        - Transports (unless specific vehicle like SdKfz)
        - Support elements (loader team, dispatch rider)
        - Generic items (anti-tank grenades, truck)
        - Generic labels (Artillery Gun, Howitzer, Self-Propelled Anti-Tank Gun)
        """
        name_lower = name.lower()

        # Explicit exclude list
        exclude = [
            'loader team', 'dispatch rider', 'signals unit',
            'anti-tank grenades', 'smoke grenades', 'headquarters',
            'medium truck', 'light truck', 'heavy truck',
            'motorcycle', 'jeep', 'car',
            'squad', 'team', 'section', 'platoon', 'company'
        ]

        # Exclude generic section labels (but NOT specific guns like "150mmL30 Howitzer")
        generic_labels = [
            'artillery gun', 'self-propelled anti-tank gun',
            'anti-tank gun', 'anti-aircraft gun', 'specialist support',
            'forward headquarters', 'forward signals'
        ]

        # Only exclude generic labels if they don't have a caliber prefix
        for label in generic_labels:
            if name_lower == label:  # Exact match only
                return False

        for term in exclude:
            if term in name_lower:
                return False

        # Include specific patterns
        include_patterns = [
            r'panzer',      # German tanks
            r'sdkfz',       # German AFVs
            r'pak',         # Anti-tank guns
            r'flak',        # Anti-aircraft guns
            r'marder',      # SPGs
            r'stug',        # Assault guns
            r'pz\.?kpfw',   # Panzer variants
            r'matilda',     # British tanks
            r'crusader',
            r'churchill',
            r'valentine',
            r'^a\d+',       # British A9, A10, A13, A15, etc. cruiser tanks
            r'bren carrier', # British carriers
            r'sherman',     # American tanks
            r'stuart',
            r'grant',
            r'lee',
            r'm\d+',        # M3, M4, M10, etc.
            r'\d+mm',       # Guns with caliber (75mm, 88mm)
            r'howitzer',
            r'gun$',        # "76.2mm Gun"
            r'semovente',   # Italian SPGs
            r'l3',          # Italian tankettes
            r'l6',
            r'm13',         # Italian tanks
            r'm14',
        ]

        for pattern in include_patterns:
            if re.search(pattern, name_lower):
                return True

        return False

    def extract_vehicle_names_only(self, text: str) -> Set[str]:
        """
        Extract only vehicle/gun names for datacard generation.

        This is the main method to use: parses army list and returns
        clean set of equipment names ready for datacard generation.
        """
        result = self.parse_army_list(text)
        return result['equipment']


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse OSJones BattleGroup Builder army list",
        epilog="""
Examples:
  %(prog)s --input osjones_army.txt --output equipment_list.txt
  %(prog)s --input osjones_army.txt --generate-datacards datacards/

Input: Paste OSJones print output to a text file
Output: Clean list of equipment names or generated datacards
        """
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input text file (OSJones Builder print output)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output text file with equipment names (one per line)"
    )
    parser.add_argument(
        "--generate-datacards",
        type=str,
        help="Generate datacards directly to this output directory"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full parsed data (debug mode)"
    )

    args = parser.parse_args()

    # Read input
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()

    parser_obj = OSJonesArmyListParser()

    # Parse army list
    if args.verbose:
        result = parser_obj.parse_army_list(text)
        print(f"Force: {result['force_name']}")
        print(f"Points: {result['points_total']}")
        print(f"BR: {result['br_total']}")
        print(f"\nUnits:")
        for unit in result['units']:
            print(f"  - {unit.get('name', 'Unknown')}: {unit['points']} pts, {unit['br']} BR")
            for eq in unit.get('equipment', []):
                print(f"      {eq}")
        print(f"\nEquipment for datacards ({len(result['equipment'])} items):")
        for eq in sorted(result['equipment']):
            print(f"  - {eq}")
    else:
        equipment_names = parser_obj.extract_vehicle_names_only(text)
        print(f"Extracted {len(equipment_names)} equipment items:")
        for name in sorted(equipment_names):
            print(f"  - {name}")

    # Save equipment list
    if args.output:
        equipment_names = parser_obj.extract_vehicle_names_only(text)
        with open(args.output, 'w', encoding='utf-8') as f:
            for name in sorted(equipment_names):
                f.write(f"{name}\n")
        print(f"\nSaved equipment list to: {args.output}")

    # Generate datacards directly
    if args.generate_datacards:
        equipment_names = parser_obj.extract_vehicle_names_only(text)

        print(f"\nGenerating datacards for {len(equipment_names)} equipment items...")

        generator = ArmyListDatacardGenerator()
        try:
            generator.generate_datacards_from_list(list(equipment_names), args.generate_datacards)
        finally:
            generator.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
