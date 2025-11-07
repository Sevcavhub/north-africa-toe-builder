#!/usr/bin/env python3
"""
Enhanced Gun Scraper for Battlegroup-Canadas-Crucible.txt

Extracts ALL gun data including HE ranges, classification, and ROF estimation.
Goal: 90%+ accuracy with automatic extraction.
"""

import re
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "database" / "master_database.db"

class EnhancedGunExtractor:
    """Extract complete gun profiles from Crucible text"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

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

    def estimate_rof(self, gun_name: str, caliber_mm: Optional[int], has_he: bool, has_ap: bool) -> Optional[int]:
        """Estimate ROF based on gun type and caliber"""
        name_lower = gun_name.lower()

        # Mortars: 3-4 ROF
        if 'mortar' in name_lower or gun_name.endswith('"'):
            return 4

        # Autocannons (20mm, 37mm with no HE): 6-10 ROF
        if not has_he and caliber_mm and caliber_mm <= 40:
            return 8

        # Heavy AT/Flak (88mm+): 1-2 ROF
        if caliber_mm and caliber_mm >= 88:
            if 'flak' in name_lower or 'k18' in name_lower:
                return 2
            return 1

        # Heavy artillery (105mm+ with HE): 1-2 ROF
        if caliber_mm and caliber_mm >= 105 and has_he:
            return 2

        # Medium AT (50-75mm): 2-3 ROF
        if caliber_mm and 50 <= caliber_mm <= 76:
            if 'pak' in name_lower or 'pdr' in name_lower:
                return 2
            return 3

        # Light AT (37-50mm): 3 ROF
        if caliber_mm and 37 <= caliber_mm < 50:
            return 3

        # Default: 2 ROF
        return 2

    def parse_gun_line(self, line: str, next_line: Optional[str] = None) -> Optional[Dict]:
        """Parse a gun data line into complete gun profile"""

        # Try multiple patterns for gun names
        patterns = [
            # Standard: "75mmL48    HE      4/4+        3        3..."
            r'^(\d+mmL?\d*)\s*(\([^)]+\))?\s+(HE|AP)',
            # With extra text: "40mmL60 Bofors    HE"
            r'^(\d+mmL?\d*)\s+([A-Za-z]+)\s+(HE|AP)',
            # Pounder: "6 pdr    HE"
            r'^(\d+\s*pdr)\s+(HE|AP)',
            # Inch: '2"    HE'
            r'^([\d.]+["\'\'"])\s+(HE|AP)',
        ]

        gun_match = None
        gun_name = None
        designation = None

        for pattern in patterns:
            gun_match = re.match(pattern, line, re.IGNORECASE)
            if gun_match:
                gun_name_base = gun_match.group(1).strip()

                # Handle designation/extra text
                if len(gun_match.groups()) >= 3:
                    middle = gun_match.group(2)
                    if middle and middle.startswith('('):
                        designation = middle.strip('()')
                    elif middle and middle not in ['HE', 'AP']:
                        designation = middle

                gun_name = f"{gun_name_base} ({designation})" if designation else gun_name_base
                break

        if not gun_match:
            return None

        # Extract caliber
        caliber_mm = None
        if 'mm' in gun_name:
            cal_match = re.search(r'(\d+)mm', gun_name)
            if cal_match:
                caliber_mm = int(cal_match.group(1))
        elif 'pdr' in gun_name:
            # Pounder to mm conversion
            if '6 pdr' in gun_name:
                caliber_mm = 57
            elif '17 pdr' in gun_name:
                caliber_mm = 76
            elif '2 pdr' in gun_name:
                caliber_mm = 40
        elif '"' in gun_name or "'" in gun_name:
            # Inch to mm conversion (mortar calibers)
            inch_match = re.search(r'([\d.]+)["\']', gun_name)
            if inch_match:
                inches = float(inch_match.group(1))
                caliber_mm = int(inches * 25.4)

        # Extract barrel length
        barrel_length = None
        barrel_match = re.search(r'L(\d+)', gun_name, re.IGNORECASE)
        if barrel_match:
            barrel_length = f"L{barrel_match.group(1)}"

        # Parse HE data
        he_dice = None
        he_target = None
        he_ranges = [None] * 6  # 6 range bands

        if 'HE' in line.upper():
            # Parse HE effect (e.g., "3/5+")
            he_match = re.search(r'HE\s+(\d+)/(\d\+)', line, re.IGNORECASE)
            if he_match:
                he_dice = int(he_match.group(1))
                he_target = he_match.group(2)

                # Extract HE range values after HE effect
                # Pattern: "HE  3/5+  1  1  1  1  1  1" or with dashes
                rest_of_line = line[he_match.end():]
                range_values = re.findall(r'\s+(\d+|-)\s+', rest_of_line)

                # Take first 6 values as range bands
                for idx, val in enumerate(range_values[:6]):
                    if val != '-':
                        he_ranges[idx] = int(val)

        # Parse AP data (from current line if no HE, or from next line)
        ap_ranges = [None] * 6

        ap_line = line if 'AP' in line.upper() else (next_line if next_line else None)

        if ap_line and 'AP' in ap_line.upper():
            # Parse AP values
            ap_match = re.search(r'AP\s+', ap_line, re.IGNORECASE)
            if ap_match:
                rest_of_line = ap_line[ap_match.end():]

                # Handle special cases like "4 (7)*" for Stielgranate
                # Clean up parentheses first
                rest_of_line = re.sub(r'\((\d+)\)\*?', r'\1', rest_of_line)

                ap_values = re.findall(r'\s+(\d+|-)\s+', rest_of_line)

                # Take first 6 values
                for idx, val in enumerate(ap_values[:6]):
                    if val != '-':
                        ap_ranges[idx] = int(val)

        # Auto-classify
        he_classification = self.auto_classify_he_shell(caliber_mm)

        # Estimate ROF
        has_he = he_dice is not None
        has_ap = any(ap_ranges)
        rof = self.estimate_rof(gun_name, caliber_mm, has_he, has_ap)

        return {
            'name': gun_name,
            'caliber_mm': caliber_mm,
            'barrel_length': barrel_length,
            'he_dice': he_dice,
            'he_target': he_target,
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
            'he_shell_classification': he_classification,
            'rof': rof
        }

    def extract_from_crucible(self, text_path: Path) -> Dict[str, List[Dict]]:
        """Extract all guns from Crucible text file"""

        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        canadian_guns = []
        german_guns = []

        current_nation = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Detect nation sections
            if 'CANADIAN GUNS' in line:
                current_nation = 'canadian'
                i += 1
                continue
            elif 'GERMAN GUNS' in line:
                current_nation = 'german'
                i += 1
                continue

            # Look for gun table headers
            if 'WEAPON' in line.upper() and 'AMMO' in line.upper() and 'RANGE' in line.upper():
                # Skip sub-header
                i += 1
                if i < len(lines) and '0-10' in lines[i]:
                    i += 1

                # Extract guns from this table
                while i < len(lines):
                    gun_line = lines[i].strip()

                    # Stop conditions
                    if not gun_line:
                        i += 1
                        continue
                    if gun_line.isupper() and len(gun_line) > 20:
                        break
                    if re.match(r'^\d+$', gun_line):
                        break
                    if 'WEAPON' in gun_line.upper() and 'AMMO' in gun_line.upper():
                        break

                    # Try to parse gun
                    next_line = lines[i + 1].strip() if i + 1 < len(lines) else None
                    gun_data = self.parse_gun_line(gun_line, next_line)

                    if gun_data and current_nation:
                        gun_data['nation'] = current_nation
                        gun_data['source_file'] = 'Battlegroup-Canadas-Crucible.txt'
                        gun_data['source_document'] = 'Battlegroup-Canadas-Crucible'
                        gun_data['extraction_method'] = 'enhanced_scraper'
                        gun_data['verified_by'] = 'claude'

                        if current_nation == 'canadian':
                            canadian_guns.append(gun_data)
                        else:
                            german_guns.append(gun_data)

                        # Skip next line if it was AP data
                        if next_line and 'AP' in next_line.upper():
                            i += 1

                    i += 1
            else:
                i += 1

        return {
            'canadian': canadian_guns,
            'german': german_guns
        }

    def delete_existing_guns(self, nation: str):
        """Delete existing guns for nation"""
        # Get gun IDs
        self.cursor.execute("SELECT id FROM bg_reference_guns WHERE nation = ?", (nation,))
        gun_ids = [row[0] for row in self.cursor.fetchall()]

        if gun_ids:
            # Delete variants
            placeholders = ','.join(['?'] * len(gun_ids))
            self.cursor.execute(f"DELETE FROM gun_name_variants WHERE gun_id IN ({placeholders})", gun_ids)

            # Delete guns
            self.cursor.execute("DELETE FROM bg_reference_guns WHERE nation = ?", (nation,))
            self.conn.commit()

            print(f"[*] Deleted {len(gun_ids)} existing {nation} guns")

    def insert_gun(self, gun_data: Dict) -> int:
        """Insert gun into database"""
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.cursor.execute("""
            INSERT INTO bg_reference_guns (
                name, nation, caliber_mm, barrel_length,
                he_dice, he_target,
                he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
                ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                he_shell_classification, rof,
                source_file, source_document, extraction_method, verified_by,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gun_data['name'], gun_data['nation'], gun_data['caliber_mm'], gun_data.get('barrel_length'),
            gun_data['he_dice'], gun_data['he_target'],
            gun_data['he_0_10'], gun_data['he_10_20'], gun_data['he_20_30'],
            gun_data['he_30_40'], gun_data['he_40_50'], gun_data['he_50_70'],
            gun_data['ap_0_10'], gun_data['ap_10_20'], gun_data['ap_20_30'],
            gun_data['ap_30_40'], gun_data['ap_40_50'], gun_data['ap_50_70'],
            gun_data['he_shell_classification'], gun_data['rof'],
            gun_data['source_file'], gun_data['source_document'],
            gun_data['extraction_method'], gun_data['verified_by'],
            created_at
        ))

        return self.cursor.lastrowid

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()


def main():
    print("="*120)
    print("ENHANCED GUN SCRAPER - Battlegroup Canadas Crucible")
    print("="*120)
    print("[*] Goal: 90%+ accuracy with automatic field extraction")
    print("[*] Extracts: HE ranges, classification, ROF estimation\n")

    text_path = PROJECT_ROOT / "Resource Documents" / "Battlegroup Game" / "Battlegroup-Canadas-Crucible.txt"

    if not text_path.exists():
        print(f"[ERROR] File not found: {text_path}")
        return

    extractor = EnhancedGunExtractor()

    try:
        # Extract from text file
        print(f"[*] Extracting from: {text_path.name}")
        all_guns = extractor.extract_from_crucible(text_path)

        print(f"[*] Extracted: {len(all_guns['canadian'])} Canadian, {len(all_guns['german'])} German guns\n")

        # Delete existing guns
        print("[*] Deleting existing guns...")
        extractor.delete_existing_guns('canadian')
        extractor.delete_existing_guns('german')

        # Insert new guns
        print("\n[*] Inserting enhanced gun data...\n")

        for nation in ['canadian', 'german']:
            print(f"\n{nation.upper()} GUNS:")
            print("-"*120)

            for gun in all_guns[nation]:
                gun_id = extractor.insert_gun(gun)

                # Show what was extracted
                he_str = f"{gun['he_dice']}D6/{gun['he_target']}" if gun['he_dice'] else "None"
                he_ranges = [gun[f'he_{r}'] for r in ['0_10', '10_20', '20_30', '30_40', '40_50', '50_70']]
                he_range_str = "/".join([str(v) if v else "-" for v in he_ranges])

                cal_str = str(gun['caliber_mm']) if gun['caliber_mm'] else '?'
                rof_str = str(gun['rof']) if gun['rof'] else '?'
                print(f"  ID {gun_id:3d}: {gun['name']:30s} | {cal_str:>3s}mm | HE:{he_str:12s} | Ranges:{he_range_str:20s} | Class:{gun['he_shell_classification'] or 'None':8s} | ROF:{rof_str}")

        print(f"\n{'='*120}")
        print("EXTRACTION COMPLETE")
        print(f"{'='*120}")
        print(f"[*] Total guns: {len(all_guns['canadian']) + len(all_guns['german'])}")
        print(f"[*] Database: {DB_PATH}")
        print(f"\n[*] Next: Review accuracy and make corrections if needed")

    finally:
        extractor.close()


if __name__ == '__main__':
    main()
