#!/usr/bin/env python3
"""
OCR-based gun scraper using direct PDF page extraction with Tesseract.
Addresses poor quality of pre-existing .txt file by extracting images from PDF
and running OCR to get clean text.
"""

import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import json

# PDF processing
try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("WARNING: pdf2image, PIL, or pytesseract not available")

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
PDF_PATH = Path(__file__).parent.parent.parent.parent / "Resource Documents" / "Battlegroup Game" / "Battlegroup-Canadas-Crucible.pdf"

class OCRGunScraper:
    """Enhanced gun scraper using OCR extraction"""

    def __init__(self):
        self.guns = []

    def extract_pdf_pages(self, start_page: int, end_page: int) -> List[str]:
        """Extract text from PDF pages using OCR"""
        if not HAS_OCR:
            print("ERROR: OCR libraries not available")
            return []

        print(f"Converting PDF pages {start_page}-{end_page} to images...")

        try:
            # Convert PDF pages to images
            images = convert_from_path(
                PDF_PATH,
                first_page=start_page,
                last_page=end_page,
                dpi=300  # High DPI for better OCR
            )

            page_texts = []
            for i, image in enumerate(images, start=start_page):
                print(f"  Running OCR on page {i}...")

                # Run Tesseract OCR
                text = pytesseract.image_to_string(image, lang='eng')
                page_texts.append(text)

            return page_texts

        except Exception as e:
            print(f"ERROR extracting pages {start_page}-{end_page}: {e}")
            return []

    def parse_gun_table(self, text: str, nation: str) -> List[Dict]:
        """Parse gun table from OCR text"""
        guns = []
        lines = text.split('\n')

        current_category = None

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Detect category headers
            if re.search(r'MORTAR|VERY LIGHT GUN|LIGHT GUN|MEDIUM GUN|HEAVY GUN|AUTOCANNON|ANTI-TANK|AIRCRAFT', line, re.IGNORECASE):
                current_category = line
                print(f"  Found category: {current_category}")
                continue

            # Try to parse as gun data line
            gun = self.parse_gun_line(line, lines[i+1] if i+1 < len(lines) else None, nation, current_category)
            if gun:
                guns.append(gun)
                print(f"  Extracted: {gun['name']}")

        return guns

    def parse_gun_line(self, line: str, next_line: Optional[str], nation: str, category: Optional[str]) -> Optional[Dict]:
        """Parse a single gun data line"""

        # Skip header lines
        if re.search(r'WEAPON|AMMO|RANGE|EFFECT|PENETRATION', line, re.IGNORECASE):
            return None

        # Try multiple gun name patterns
        gun_patterns = [
            # Standard: 75mmL48, 50mmL60 (PaK38)
            r'^(\d+mmL?\d*)\s*(\([^)]+\))?\s+(HE|AP)',

            # Inch notation: 2", 3", 4.2"
            r'^([\d.]+["\'\'"])\s+(\w+)?\s*HE',

            # Naval guns: 6" naval gun, 8" naval gun
            r'^([\d.]+["\'\'"])\s+naval\s+gun',

            # Pounder: 6 pdr, 17 pdr
            r'^(\d+\s*pdr)\s+(HE|AP)',

            # Special weapons: PIAT, 60lb Rocket
            r'^([A-Z][a-z]+|[\d]+lb\s+Rocket)\s+(HE|AP|-)',
        ]

        gun_name = None
        for pattern in gun_patterns:
            match = re.search(pattern, line)
            if match:
                gun_name = match.group(1)
                if len(match.groups()) > 1 and match.group(2) and match.group(2).startswith('('):
                    gun_name += f" {match.group(2)}"
                break

        if not gun_name:
            return None

        # Clean up gun name
        gun_name = gun_name.strip()

        # Extract caliber
        caliber_mm = self.extract_caliber(gun_name, line, category)

        # Extract HE data
        he_dice = None
        he_target = None
        he_classification = None
        he_ranges = [None] * 6

        he_match = re.search(r'HE\s+(\d+)/(\d\+)', line)
        if he_match:
            he_dice = int(he_match.group(1))
            he_target = he_match.group(2)
            he_classification = self.auto_classify_he_shell(caliber_mm)

            # Extract HE range bands - look for 6 numbers
            range_pattern = r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
            range_match = re.search(range_pattern, line)
            if range_match:
                he_ranges = [int(range_match.group(i)) for i in range(1, 7)]

        # Extract AP data
        ap_ranges = [None] * 6

        # Look for AP line (might be current line or next line)
        ap_line = line if 'AP' in line else (next_line or '')

        if 'AP' in ap_line:
            # Extract AP range bands - look for 6 numbers after "AP"
            ap_pattern = r'AP.*?(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
            ap_match = re.search(ap_pattern, ap_line)
            if ap_match:
                ap_ranges = [int(ap_match.group(i)) for i in range(1, 7)]

        # Weapon category from section header
        weapon_category = self.infer_weapon_category(gun_name, category, caliber_mm)

        return {
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
            'rof': None  # ROF should be empty for guns
        }

    def extract_caliber(self, gun_name: str, line: str, category: Optional[str]) -> Optional[int]:
        """Extract caliber from gun name or context"""

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

        if 'Rocket' in gun_name:
            return None  # Rockets don't have caliber in mm

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
        if 'Mortar' in gun_name or '"' in gun_name:
            return 'Mortar'

        if 'naval' in gun_name.lower():
            if caliber_mm and caliber_mm > 150:
                return 'Heavy Gun'
            return 'Medium Gun'

        if 'PIAT' in gun_name:
            return 'Inf Anti-Tank'

        if 'Rocket' in gun_name:
            return 'Aircraft Weapons'

        if caliber_mm:
            if caliber_mm <= 40:
                return 'Autocannon'
            elif caliber_mm <= 76:
                return 'V. Light Gun'
            elif caliber_mm <= 105:
                return 'Light Gun'
            elif caliber_mm <= 150:
                return 'Medium Gun'
            else:
                return 'Heavy Gun'

        return None

    def scrape_canadian_guns(self) -> List[Dict]:
        """Scrape Canadian guns from pages 130-132"""
        print("\n=== SCRAPING CANADIAN GUNS ===")
        page_texts = self.extract_pdf_pages(130, 132)

        all_guns = []
        for text in page_texts:
            guns = self.parse_gun_table(text, 'canadian')
            all_guns.extend(guns)

        print(f"\nExtracted {len(all_guns)} Canadian guns")
        return all_guns

    def scrape_german_guns(self) -> List[Dict]:
        """Scrape German guns from pages 134-136"""
        print("\n=== SCRAPING GERMAN GUNS ===")
        page_texts = self.extract_pdf_pages(134, 136)

        all_guns = []
        for text in page_texts:
            guns = self.parse_gun_table(text, 'german')
            all_guns.extend(guns)

        print(f"\nExtracted {len(all_guns)} German guns")
        return all_guns

def main():
    """Main scraper execution"""

    if not HAS_OCR:
        print("ERROR: Required OCR libraries not installed")
        print("Please install: pip install pdf2image pillow pytesseract")
        return

    scraper = OCRGunScraper()

    # Scrape both nations
    canadian_guns = scraper.scrape_canadian_guns()
    german_guns = scraper.scrape_german_guns()

    # Save results for review
    results = {
        'canadian': canadian_guns,
        'german': german_guns
    }

    output_path = Path(__file__).parent.parent.parent.parent / "ocr_gun_extraction_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n=== RESULTS SAVED ===")
    print(f"Output: {output_path}")
    print(f"Canadian guns: {len(canadian_guns)}")
    print(f"German guns: {len(german_guns)}")
    print("\nReview results before importing to database")

if __name__ == '__main__':
    main()
