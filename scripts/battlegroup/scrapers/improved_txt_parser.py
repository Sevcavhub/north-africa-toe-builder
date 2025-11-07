#!/usr/bin/env python3
"""
Improved gun parser for Battlegroup-Canadas-Crucible.txt
Handles multi-line gun format correctly.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional

TXT_PATH = Path(__file__).parent.parent.parent.parent / "Resource Documents" / "Battlegroup Game" / "Battlegroup-Canadas-Crucible.txt"

class ImprovedGunParser:
    """Parse guns from txt file with multi-line format support"""

    def __init__(self):
        self.guns = []
        self.current_category = None
        self.current_nation = None

    def parse_file(self) -> Dict[str, List[Dict]]:
        """Parse entire txt file for Canadian and German guns"""

        print(f"Reading: {TXT_PATH}")

        with open(TXT_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        print(f"Total lines: {len(lines)}")

        # Find Canadian guns section
        canadian_start = None
        german_start = None
        german_end = None

        for i, line in enumerate(lines):
            if 'CANADIAN GUNS' in line:
                canadian_start = i
            elif 'GERMAN GUNS' in line:
                german_start = i
            elif german_start and 'GERMAN EQUIPMENT' in line and i > german_start:
                german_end = i
                break

        print(f"\nCanadian guns start: line {canadian_start}")
        print(f"German guns start: line {german_start}")
        print(f"German guns end: line {german_end}")

        results = {}

        if canadian_start and german_start:
            canadian_lines = lines[canadian_start:german_start]
            print(f"\nParsing {len(canadian_lines)} lines of Canadian guns...")
            results['canadian'] = self.parse_gun_section(canadian_lines, 'canadian')

        if german_start and german_end:
            german_lines = lines[german_start:german_end]
            print(f"\nParsing {len(german_lines)} lines of German guns...")
            results['german'] = self.parse_gun_section(german_lines, 'german')

        return results

    def parse_gun_section(self, lines: List[str], nation: str) -> List[Dict]:
        """Parse a section of gun tables"""

        guns = []
        current_category = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Detect category headers
            category_match = re.search(
                r'(MORTAR|AUTOCANNON|VERY LIGHT GUN|LIGHT GUN|MEDIUM GUN|HEAVY GUN|INFANTRY ANTI-TANK|AIRCRAFT)',
                line,
                re.IGNORECASE
            )

            if category_match:
                current_category = category_match.group(1)
                print(f"  Category: {current_category}")
                i += 1
                continue

            # Skip header lines
            if re.search(r'WEAPON|AMMO|HE EFFECT|RANGE|0-10', line, re.IGNORECASE):
                i += 1
                continue

            # Skip empty lines and page numbers
            if not line or line.isdigit() or len(line) < 3:
                i += 1
                continue

            # Skip chapter headers
            if 'BATTLE GROUP' in line or 'RULEBOOK' in line:
                i += 1
                continue

            # Try to parse as gun name
            gun = self.try_parse_gun(lines, i, nation, current_category)
            if gun:
                guns.append(gun)
                print(f"    [+] {gun['name']}")
                # Skip past the gun's data lines
                i += gun['_lines_consumed']
            else:
                i += 1

        return guns

    def try_parse_gun(self, lines: List[str], start_idx: int, nation: str, category: Optional[str]) -> Optional[Dict]:
        """Try to parse a gun starting at given line index"""

        line = lines[start_idx].strip()

        # Gun name patterns
        gun_patterns = [
            r'^(\d+mmL?\d*(?:\s+\([^)]+\))?)',  # 75mmL40, 50mmL60 (PaK38)
            r'^(\d+mmL?\d*\s+[A-Za-z]+)',       # 40mmL60 Bofors
            r'^([\d.]+["\'\'"])',                # 2", 3", 4.2"
            r'^(\d+\s*pdr)',                     # 6 pdr, 17 pdr
            r'^(\d+["\'\'"]?\s*naval\s+gun)',  # 6" naval gun
            r'^([A-Z][A-Za-z]+)',                # PIAT
            r'^(\d+lb\s+Rocket)',                # 60lb Rocket
        ]

        gun_name = None
        for pattern in gun_patterns:
            match = re.match(pattern, line)
            if match:
                gun_name = match.group(1).strip()
                break

        if not gun_name:
            return None

        # Look ahead for HE and AP lines
        he_line_idx = None
        ap_line_idx = None
        lines_consumed = 1

        # Check next 3 lines for HE/AP data
        for offset in range(1, min(4, len(lines) - start_idx)):
            check_line = lines[start_idx + offset].strip()

            if not check_line or len(check_line) < 5:
                continue

            if 'HE' in check_line and 'HE EFFECT' not in check_line:
                he_line_idx = start_idx + offset
                lines_consumed = max(lines_consumed, offset + 1)

            if 'AP' in check_line and 'PENETRATION' not in check_line:
                ap_line_idx = start_idx + offset
                lines_consumed = max(lines_consumed, offset + 1)

        # Extract caliber
        caliber_mm = self.extract_caliber(gun_name)

        # Parse HE data
        he_dice = None
        he_target = None
        he_classification = None
        he_ranges = [None] * 6

        if he_line_idx:
            he_line = lines[he_line_idx]
            he_data = self.parse_he_line(he_line, caliber_mm)
            if he_data:
                he_dice = he_data['he_dice']
                he_target = he_data['he_target']
                he_classification = he_data['he_classification']
                he_ranges = he_data['he_ranges']

        # Parse AP data
        ap_ranges = [None] * 6

        if ap_line_idx:
            ap_line = lines[ap_line_idx]
            ap_ranges = self.parse_ap_line(ap_line)

        # Weapon category
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
            'rof': None,  # ROF empty for guns
            '_lines_consumed': lines_consumed
        }

        return gun

    def parse_he_line(self, line: str, caliber_mm: Optional[int]) -> Optional[Dict]:
        """Parse HE data line"""

        # Extract HE dice/target (e.g., "3/5+", "4/4+")
        he_match = re.search(r'(\d+)/(\d\+)', line)
        if not he_match:
            return None

        he_dice = int(he_match.group(1))
        he_target = he_match.group(2)

        # Auto-classify HE shell
        he_classification = self.auto_classify_he_shell(caliber_mm)

        # Extract 6 range values
        he_ranges = self.extract_range_values(line)

        return {
            'he_dice': he_dice,
            'he_target': he_target,
            'he_classification': he_classification,
            'he_ranges': he_ranges
        }

    def parse_ap_line(self, line: str) -> List[Optional[int]]:
        """Parse AP penetration line"""
        return self.extract_range_values(line)

    def extract_range_values(self, line: str) -> List[Optional[int]]:
        """Extract 6 range band values from a line"""

        # Find all numbers after the HE/AP indicator
        # Look for the pattern after "HE EFFECT" or "AP" columns

        # Remove leading text up to the numeric range data
        # The range data typically starts after several spaces

        # Split by whitespace and extract numbers
        parts = line.split()

        # Filter to just numbers (ignoring -, HE, AP, etc.)
        numbers = []
        for part in parts:
            # Try to convert to int
            try:
                num = int(part)
                numbers.append(num)
            except ValueError:
                # Not a number, skip
                continue

        # We expect 6 range values
        # But handle cases with fewer values
        result = [None] * 6

        # Skip first number if it looks like HE dice (e.g., 3/5+, 4/4+)
        # The actual range values come after the HE effect
        start_idx = 0
        if len(numbers) > 6:
            # Likely includes HE dice, skip first number
            start_idx = 1

        for i, num in enumerate(numbers[start_idx:start_idx + 6]):
            result[i] = num

        return result

    def extract_caliber(self, gun_name: str) -> Optional[int]:
        """Extract caliber from gun name"""

        # Direct mm specification
        mm_match = re.search(r'(\d+)mm', gun_name)
        if mm_match:
            return int(mm_match.group(1))

        # Inch notation (convert to mm)
        inch_match = re.search(r'([\d.]+)["\'\'"]', gun_name)
        if inch_match:
            inches = float(inch_match.group(1))
            return int(inches * 25.4)

        # Pounder guns (British designation)
        pounder_calibers = {
            '2 pdr': 40,
            '6 pdr': 57,
            '17 pdr': 76,
            '25 pdr': 88
        }
        for pounder, caliber in pounder_calibers.items():
            if pounder in gun_name:
                return caliber

        # Special weapons
        if 'PIAT' in gun_name:
            return 89

        return None

    def auto_classify_he_shell(self, caliber_mm: Optional[int]) -> Optional[str]:
        """Auto-classify HE shell by caliber"""
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
        """Infer weapon category from context"""

        # From section header
        if category:
            if 'MORTAR' in category.upper():
                return 'Mortar'
            elif 'AUTOCANNON' in category.upper():
                return 'Autocannon'
            elif 'ANTI-TANK' in category.upper():
                return 'Inf Anti-Tank'
            elif 'AIRCRAFT' in category.upper():
                return 'Aircraft Weapons'
            elif 'VERY LIGHT' in category.upper():
                return 'V. Light Gun'
            elif 'LIGHT' in category.upper():
                return 'Light Gun'
            elif 'MEDIUM' in category.upper():
                return 'Medium Gun'
            elif 'HEAVY' in category.upper():
                return 'Heavy Gun'

        # From gun name
        if '"' in gun_name or "'" in gun_name:
            if 'naval' not in gun_name.lower():
                return 'Mortar'

        if 'naval' in gun_name.lower():
            if caliber_mm and caliber_mm > 150:
                return 'Heavy Gun'
            return 'Medium Gun'

        if 'PIAT' in gun_name:
            return 'Inf Anti-Tank'

        if 'Rocket' in gun_name:
            return 'Aircraft Weapons'

        return None

def main():
    """Main parser execution"""

    parser = ImprovedGunParser()
    results = parser.parse_file()

    # Save results
    output_path = Path(__file__).parent.parent.parent.parent / "improved_gun_extraction_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n=== RESULTS ===")
    print(f"Canadian guns: {len(results.get('canadian', []))}")
    print(f"German guns: {len(results.get('german', []))}")
    print(f"\nSaved to: {output_path}")

    # Show sample
    if results.get('canadian'):
        print(f"\nSample Canadian gun:")
        sample = results['canadian'][0]
        print(json.dumps(sample, indent=2))

if __name__ == '__main__':
    main()
