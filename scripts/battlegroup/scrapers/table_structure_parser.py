#!/usr/bin/env python3
"""
Table-structure-aware gun parser.
Respects the table format: gun names are left-aligned, AP lines are indented.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

TXT_PATH = Path(__file__).parent.parent.parent.parent / "Resource Documents" / "Battlegroup Game" / "Battlegroup-Canadas-Crucible.txt"

class TableGunParser:
    """Parse guns respecting table structure"""

    def parse_file(self) -> Dict[str, List[Dict]]:
        """Parse entire txt file"""

        with open(TXT_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Find section boundaries
        canadian_start = None
        german_start = None

        for i, line in enumerate(lines):
            if 'CANADIAN GUNS' in line:
                canadian_start = i
            elif 'GERMAN GUNS' in line and i > (canadian_start or 0):
                german_start = i
                break

        print(f"Canadian guns: line {canadian_start}")
        print(f"German guns: line {german_start}")

        results = {}

        if canadian_start and german_start:
            canadian_lines = lines[canadian_start:german_start]
            print(f"\nParsing Canadian guns ({len(canadian_lines)} lines)...")
            results['canadian'] = self.parse_gun_tables(canadian_lines, 'canadian')

        if german_start:
            # German section goes to end of relevant content
            german_lines = lines[german_start:german_start + 300]  # Reasonable range
            print(f"\nParsing German guns ({len(german_lines)} lines)...")
            results['german'] = self.parse_gun_tables(german_lines, 'german')

        return results

    def parse_gun_tables(self, lines: List[str], nation: str) -> List[Dict]:
        """Parse gun tables from section"""

        guns = []
        current_category = None
        i = 0

        while i < len(lines):
            line = lines[i]

            # Detect category headers (all caps, specific keywords)
            if re.search(r'(MORTARS|AUTOCANNONS|VERY LIGHT GUNS|LIGHT GUNS|MEDIUM GUNS|HEAVY GUNS|INFANTRY ANTI-TANK|AIRCRAFT WEAPONS)', line, re.IGNORECASE):
                current_category = line.strip()
                print(f"  Category: {current_category}")
                i += 1
                continue

            # Skip table headers
            if re.search(r'WEAPON|AMMO|HE EFFECT|RANGE|PENETRATION|0-10', line, re.IGNORECASE):
                i += 1
                continue

            # Try to parse as gun data line (must be table-formatted)
            if self.is_gun_data_line(line):
                gun, lines_consumed = self.parse_gun_entry(lines, i, nation, current_category)
                if gun:
                    guns.append(gun)
                    print(f"    [+] {gun['name']}")
                    i += lines_consumed
                else:
                    i += 1
            else:
                i += 1

        return guns

    def is_gun_data_line(self, line: str) -> bool:
        """Check if line is a gun data line (left-aligned, has gun name pattern)"""

        # Must start with space (table indent) followed by non-whitespace
        if not line.startswith(' '):
            return False

        # Must NOT be heavily indented (AP continuation lines are indented more)
        if line.startswith('                   '):  # ~19 spaces = AP line
            return False

        stripped = line.strip()

        # Skip empty, page numbers, chapter headers
        if not stripped or stripped.isdigit() or len(stripped) < 2:
            return False

        if 'BATTLE GROUP' in stripped or 'RULEBOOK' in stripped:
            return False

        # Must have gun name pattern
        gun_patterns = [
            r'^\d+mm',           # 75mmL40, 20mm
            r'^\d+["\'\'"]',    # 2", 3", 4.2"
            r'^\d+\s*pdr',       # 6 pdr, 17 pdr
            r'^\d+["\'\'"]?\s+naval',  # 6" naval gun
            r'^[A-Z][A-Za-z]+',  # PIAT, etc.
            r'^\d+lb\s+Rocket',  # 60lb Rocket
        ]

        for pattern in gun_patterns:
            if re.search(pattern, stripped):
                return True

        return False

    def parse_gun_entry(self, lines: List[str], start_idx: int, nation: str, category: Optional[str]) -> Tuple[Optional[Dict], int]:
        """Parse complete gun entry (may span 1-2 lines)"""

        gun_line = lines[start_idx]
        gun_name, he_data, he_ranges = self.parse_gun_line(gun_line)

        if not gun_name:
            return None, 1

        # Check if next line is AP continuation
        ap_ranges = [None] * 6
        lines_consumed = 1

        if start_idx + 1 < len(lines):
            next_line = lines[start_idx + 1]
            if self.is_ap_continuation_line(next_line):
                ap_ranges = self.parse_ap_line(next_line)
                lines_consumed = 2

        # Extract caliber
        caliber_mm = self.extract_caliber(gun_name)

        # Build gun dict
        he_dice = he_data[0] if he_data else None
        he_target = he_data[1] if he_data else None
        he_classification = self.auto_classify_he_shell(caliber_mm) if he_dice else None

        weapon_category = self.infer_weapon_category(gun_name, category, caliber_mm)

        gun = {
            'name': gun_name,
            'nation': nation,
            'caliber_mm': caliber_mm,
            'he_dice': he_dice,
            'he_target': he_target,
            'he_shell_classification': he_classification,
            'he_0_10': he_ranges[0],
            'he_10_20': he_ranges[1],
            'he_20_30': he_ranges[2],
            'he_30_40': he_ranges[3],
            'he_40_50': he_ranges[4],
            'he_50_70': he_ranges[5],
            'ap_0_10': ap_ranges[0],
            'ap_10_20': ap_ranges[1],
            'ap_20_30': ap_ranges[2],
            'ap_30_40': ap_ranges[3],
            'ap_40_50': ap_ranges[4],
            'ap_50_70': ap_ranges[5],
            'weapon_category': weapon_category,
            'rof': None
        }

        return gun, lines_consumed

    def parse_gun_line(self, line: str) -> Tuple[Optional[str], Optional[Tuple], List]:
        """Parse gun name line, extract gun name, HE data, HE ranges"""

        # Extract gun name (first column, before "HE" or "AP")
        name_match = re.search(r'^\s+([^\s].*?)\s+(HE|AP)', line)
        if not name_match:
            return None, None, [None] * 6

        gun_name = name_match.group(1).strip()

        # Extract HE effect (e.g., "3/5+", "4/4+")
        he_data = None
        he_match = re.search(r'(\d+)/(\d\+)', line)
        if he_match:
            he_dice = int(he_match.group(1))
            he_target = he_match.group(2)
            he_data = (he_dice, he_target)

        # Extract range values (6 numbers after the HE effect column)
        he_ranges = self.extract_ranges(line)

        return gun_name, he_data, he_ranges

    def is_ap_continuation_line(self, line: str) -> bool:
        """Check if line is AP continuation (heavily indented, starts with AP)"""
        return 'AP' in line and line.startswith('                   ')

    def parse_ap_line(self, line: str) -> List[Optional[int]]:
        """Parse AP penetration ranges"""
        return self.extract_ranges(line)

    def extract_ranges(self, line: str) -> List[Optional[int]]:
        """Extract 6 range band values using column positions"""

        # The table has fixed column positions for range values
        # After examining the txt file, the range columns start around column 35
        # and are spaced with varying widths

        # Split the line at the range data section
        # Look for the part after "HE EFFECT" or after "AP -"

        result = [None] * 6

        # Find where the numeric range data starts
        # It's after the HE effect column (which ends around column 35-40)

        # Strategy: Find all number tokens AFTER the HE/AP indicator
        # Skip the first few tokens (gun name, HE/AP, effect value)

        tokens = line.split()

        # Find index of "HE" or "AP" token
        data_start_idx = -1
        for i, token in enumerate(tokens):
            if token in ['HE', 'AP']:
                data_start_idx = i
                break

        if data_start_idx == -1:
            return result

        # Skip past HE/AP and the effect column (e.g., "3/5+" or "-")
        # Range data starts after that
        range_start_idx = data_start_idx + 2

        # Extract numbers from range section
        numbers = []
        for token in tokens[range_start_idx:]:
            # Skip "/" (part of HE dice)
            if '/' in token:
                continue

            # Try to parse as int
            try:
                num = int(token)
                numbers.append(num)
            except ValueError:
                # "-" or other non-number, treat as None
                if token == '-':
                    numbers.append(None)
                continue

        # Fill result with extracted numbers (up to 6)
        for i in range(min(6, len(numbers))):
            result[i] = numbers[i]

        return result

    def extract_caliber(self, gun_name: str) -> Optional[int]:
        """Extract caliber from gun name"""

        # Direct mm
        mm_match = re.search(r'(\d+)mm', gun_name)
        if mm_match:
            return int(mm_match.group(1))

        # Inch (convert to mm)
        inch_match = re.search(r'([\d.]+)["\'\'"]', gun_name)
        if inch_match:
            inches = float(inch_match.group(1))
            return int(inches * 25.4)

        # Pounder
        pounder_map = {
            '2 pdr': 40, '6 pdr': 57, '17 pdr': 76, '25 pdr': 88
        }
        for key, val in pounder_map.items():
            if key in gun_name:
                return val

        # Special
        if 'PIAT' in gun_name:
            return 89

        return None

    def auto_classify_he_shell(self, caliber_mm: Optional[int]) -> Optional[str]:
        """Auto-classify HE shell"""
        if not caliber_mm:
            return None

        if caliber_mm <= 20:
            return "v. light"
        elif caliber_mm <= 50:
            return "v. light"
        elif caliber_mm <= 76:
            return "light"
        elif caliber_mm <= 105:
            return "medium"
        else:
            return "heavy"

    def infer_weapon_category(self, gun_name: str, category: Optional[str], caliber_mm: Optional[int]) -> Optional[str]:
        """Infer weapon category"""

        if category:
            cat_upper = category.upper()
            if 'MORTAR' in cat_upper:
                return 'Mortar'
            elif 'AUTOCANNON' in cat_upper:
                return 'Autocannon'
            elif 'ANTI-TANK' in cat_upper:
                return 'Inf Anti-Tank'
            elif 'AIRCRAFT' in cat_upper:
                return 'Aircraft Weapons'
            elif 'VERY LIGHT' in cat_upper:
                return 'V. Light Gun'
            elif 'LIGHT' in cat_upper:
                return 'Light Gun'
            elif 'MEDIUM' in cat_upper:
                return 'Medium Gun'
            elif 'HEAVY' in cat_upper:
                return 'Heavy Gun'

        # From gun name
        if '"' in gun_name and 'naval' not in gun_name.lower():
            return 'Mortar'

        if 'naval' in gun_name.lower():
            return 'Heavy Gun' if (caliber_mm and caliber_mm > 150) else 'Medium Gun'

        if 'PIAT' in gun_name:
            return 'Inf Anti-Tank'

        if 'Rocket' in gun_name:
            return 'Aircraft Weapons'

        return None

def main():
    """Main execution"""

    parser = TableGunParser()
    results = parser.parse_file()

    # Save results
    output_path = Path(__file__).parent.parent.parent.parent / "table_gun_extraction_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n=== RESULTS ===")
    print(f"Canadian guns: {len(results.get('canadian', []))}")
    print(f"German guns: {len(results.get('german', []))}")
    print(f"\nSaved to: {output_path}")

    # Show samples
    if results.get('canadian'):
        print(f"\nFirst 3 Canadian guns:")
        for gun in results['canadian'][:3]:
            print(f"  {gun['name']}: HE={gun['he_dice']}/{gun['he_target']}, ranges={gun['he_0_10']}/{gun['he_10_20']}/{gun['he_20_30']}/{gun['he_30_40']}/{gun['he_40_50']}/{gun['he_50_70']}")

if __name__ == '__main__':
    main()
