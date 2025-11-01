#!/usr/bin/env python3
"""
Extract vehicle and gun data from BattleGroup Fall of the Reich PDF.
Includes duplicate detection against existing master_database.db entries.
"""

import pdfplumber
import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

# Paths
PDF_PATH = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-Fall-of-the-Reich-Full.pdf")
DB_PATH = Path(r"D:\north-africa-toe-builder\database\master_database.db")
OUTPUT_DIR = Path(r"D:\north-africa-toe-builder\data\output")

# Output files
VEHICLES_JSON = OUTPUT_DIR / "battlegroup_fall_of_reich_vehicles.json"
GUNS_JSON = OUTPUT_DIR / "battlegroup_fall_of_reich_guns.json"
REPORT_MD = OUTPUT_DIR / "BATTLEGROUP_FALL_OF_REICH_EXTRACTION_REPORT.md"

class FallOfReichExtractor:
    def __init__(self):
        self.existing_vehicles: Set[Tuple[str, str]] = set()
        self.existing_guns: Set[Tuple[str, str]] = set()
        self.extracted_vehicles: List[Dict] = []
        self.extracted_guns: List[Dict] = []
        self.duplicate_vehicles: List[Tuple[str, str]] = []
        self.duplicate_guns: List[Tuple[str, str]] = []
        self.stats = {
            'total_pages': 0,
            'vehicles_found': 0,
            'guns_found': 0,
            'vehicles_duplicates': 0,
            'guns_duplicates': 0,
            'vehicles_new': 0,
            'guns_new': 0
        }

    def load_existing_data(self):
        """Query existing database for duplicate detection."""
        print("Loading existing database entries...")
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Get existing vehicles
        cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
        for row in cursor.fetchall():
            name = row[0].lower().strip() if row[0] else ''
            nation = row[1].lower().strip() if row[1] else ''
            self.existing_vehicles.add((name, nation))

        # Get existing guns
        cursor.execute("SELECT name, nation FROM bg_reference_guns")
        for row in cursor.fetchall():
            name = row[0].lower().strip() if row[0] else ''
            nation = row[1].lower().strip() if row[1] else ''
            self.existing_guns.add((name, nation))

        conn.close()

        print(f"Loaded {len(self.existing_vehicles)} existing vehicles")
        print(f"Loaded {len(self.existing_guns)} existing guns")

    def extract_pdf_text(self) -> str:
        """Extract all text from PDF."""
        print(f"Extracting text from {PDF_PATH.name}...")
        full_text = []

        with pdfplumber.open(str(PDF_PATH)) as pdf:
            self.stats['total_pages'] = len(pdf.pages)
            print(f"Processing {self.stats['total_pages']} pages...")

            for i, page in enumerate(pdf.pages, 1):
                if i % 10 == 0:
                    print(f"  Page {i}/{self.stats['total_pages']}")
                text = page.extract_text()
                if text:
                    full_text.append(text)

        return "\n".join(full_text)

    def normalize_name(self, name: str) -> str:
        """Normalize vehicle/gun name for comparison."""
        return name.lower().strip()

    def is_duplicate_vehicle(self, name: str, nation: str) -> bool:
        """Check if vehicle already exists in database."""
        key = (self.normalize_name(name), nation.lower().strip())
        return key in self.existing_vehicles

    def is_duplicate_gun(self, name: str, nation: str) -> bool:
        """Check if gun already exists in database."""
        key = (self.normalize_name(name), nation.lower().strip())
        return key in self.existing_guns

    def parse_armor_value(self, text: str) -> Optional[str]:
        """Extract armor value (A-O scale)."""
        match = re.search(r'\b([A-O])\b', text)
        return match.group(1) if match else None

    def parse_movement(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse movement values (off-road, road)."""
        # Look for movement pattern like "6/12" or "8"
        match = re.search(r'(\d+)(?:/(\d+))?', text)
        if match:
            off_road = int(match.group(1))
            road = int(match.group(2)) if match.group(2) else None
            return off_road, road
        return None, None

    def parse_vehicle_datacard(self, text: str, nation: str) -> Optional[Dict]:
        """Parse a single vehicle datacard."""
        # This is a complex pattern - looking for vehicle name, stats, armor, weapons
        # Pattern varies by format (datacard vs table)

        # Try to extract vehicle name (usually at start or in bold)
        name_match = re.search(r'^([A-Z][A-Za-z0-9\s\-/]+?)(?:\s+\d+|\s+BR|\s+ARMOUR)', text, re.MULTILINE)
        if not name_match:
            return None

        name = name_match.group(1).strip()

        # Check for duplicate
        if self.is_duplicate_vehicle(name, nation):
            self.duplicate_vehicles.append((name, nation))
            self.stats['vehicles_duplicates'] += 1
            return None

        # Extract armor values
        armor_section = re.search(r'ARMOUR[:\s]+([A-O])[/\s]+([A-O])[/\s]+([A-O])', text, re.IGNORECASE)
        armor_front = armor_section.group(1) if armor_section else None
        armor_side = armor_section.group(2) if armor_section else None
        armor_rear = armor_section.group(3) if armor_section else None

        # Extract movement
        movement_section = re.search(r'(?:MOVE|MOVEMENT)[:\s]+(\d+)(?:/(\d+))?', text, re.IGNORECASE)
        off_road = int(movement_section.group(1)) if movement_section else None
        road = int(movement_section.group(2)) if movement_section and movement_section.group(2) else None

        # Extract weapons (complex - look for weapon patterns)
        weapons = []
        weapon_patterns = [
            r'(\d+x\s+[A-Za-z0-9\s\-/]+(?:MG|gun|cannon|mortar))',
            r'([A-Za-z0-9\s\-/]+(?:mm|cm)\s+(?:gun|cannon|mortar))'
        ]
        for pattern in weapon_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                weapons.append(match.group(1).strip())

        vehicle = {
            'name': name,
            'nation': nation,
            'armor_front': armor_front,
            'armor_side': armor_side,
            'armor_rear': armor_rear,
            'off_road_inches': off_road,
            'road_inches': road,
            'weapons': weapons if weapons else None,
            'source_file': 'Battlegroup-Fall-of-the-Reich-Full',
            'extraction_date': datetime.now().isoformat()
        }

        return vehicle

    def parse_gun_datacard(self, text: str) -> Optional[Dict]:
        """Parse a single gun datacard."""
        # Look for gun name and caliber
        name_match = re.search(r'([A-Za-z0-9\s\-/]+?)\s+(\d+)mm', text)
        if not name_match:
            return None

        name = name_match.group(0).strip()
        caliber = int(name_match.group(2))

        # Try to determine nation from context (German vs Soviet naming)
        nation = 'german'  # Default for Fall of Reich
        if any(term in name.lower() for term in ['zis', 'm1', 'bs-3', 'su-']):
            nation = 'soviet'
        elif any(term in name.lower() for term in ['sherman', 'm4', 'm3']):
            nation = 'american'

        # Check for duplicate
        if self.is_duplicate_gun(name, nation):
            self.duplicate_guns.append((name, nation))
            self.stats['guns_duplicates'] += 1
            return None

        # Extract HE values
        he_match = re.search(r'HE[:\s]+(\d+)D\d+[+\-]?(\d+)?', text, re.IGNORECASE)
        he_dice = int(he_match.group(1)) if he_match else None

        # Extract AP penetration values (range bands)
        ap_values = {}
        ap_pattern = r'(?:0-10|10-20|20-30|30-40|40-50|50-70)["\']\s+(\d+)'
        for match in re.finditer(ap_pattern, text):
            # This is simplified - real parsing would map ranges
            pass

        gun = {
            'name': name,
            'nation': nation,
            'caliber_mm': caliber,
            'he_dice': he_dice,
            'source_file': 'Battlegroup-Fall-of-the-Reich-Full',
            'extraction_date': datetime.now().isoformat()
        }

        return gun

    def extract_from_text(self, text: str):
        """Main extraction logic from PDF text."""
        print("\nParsing extracted text for vehicles and guns...")

        # Split into sections by nation/army list
        # Look for section headers like "GERMAN ARMY LIST", "SOVIET FORCES", etc.
        sections = re.split(r'(?:GERMAN|SOVIET|RUSSIAN|AMERICAN)\s+(?:ARMY|FORCES?|UNITS?)', text, flags=re.IGNORECASE)

        # Also try to find individual datacards
        # Fall of Reich format typically has vehicle stats in tables or datacards

        # Strategy 1: Look for vehicle table sections
        vehicle_table_pattern = r'([A-Z][A-Za-z0-9\s\-/]+)\s+\d+\s+(?:BR|ARMOUR|MOVE)'

        for match in re.finditer(vehicle_table_pattern, text, re.MULTILINE):
            # Get context around match (200 chars)
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 300)
            context = text[start:end]

            # Determine nation from context
            nation = 'german'  # Default
            if any(term in context.lower() for term in ['soviet', 'russian', 'red army']):
                nation = 'soviet'
            elif any(term in context.lower() for term in ['american', 'us army']):
                nation = 'american'

            vehicle = self.parse_vehicle_datacard(context, nation)
            if vehicle:
                self.extracted_vehicles.append(vehicle)
                self.stats['vehicles_new'] += 1

        # Strategy 2: Look for gun data (similar approach)
        gun_pattern = r'(\d+mm\s+[A-Za-z0-9\s\-/]+(?:gun|cannon|mortar|howitzer))'

        for match in re.finditer(gun_pattern, text, re.IGNORECASE):
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 300)
            context = text[start:end]

            gun = self.parse_gun_datacard(context)
            if gun:
                self.extracted_guns.append(gun)
                self.stats['guns_new'] += 1

        self.stats['vehicles_found'] = self.stats['vehicles_new'] + self.stats['vehicles_duplicates']
        self.stats['guns_found'] = self.stats['guns_new'] + self.stats['guns_duplicates']

        print(f"Found {self.stats['vehicles_found']} vehicles ({self.stats['vehicles_new']} new, {self.stats['vehicles_duplicates']} duplicates)")
        print(f"Found {self.stats['guns_found']} guns ({self.stats['guns_new']} new, {self.stats['guns_duplicates']} duplicates)")

    def save_outputs(self):
        """Save JSON outputs and generate report."""
        print("\nSaving outputs...")

        # Save vehicles JSON
        with open(VEHICLES_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_vehicles, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.extracted_vehicles)} vehicles to {VEHICLES_JSON.name}")

        # Save guns JSON
        with open(GUNS_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_guns, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.extracted_guns)} guns to {GUNS_JSON.name}")

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive extraction report."""
        report = f"""# BattleGroup Fall of the Reich Extraction Report

**Extraction Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source**: Battlegroup-Fall-of-the-Reich-Full.pdf
**Database**: master_database.db

---

## Extraction Statistics

### PDF Processing
- **Total Pages Processed**: {self.stats['total_pages']}
- **Source Book**: Fall of the Reich (Eastern Front 1945)

### Vehicle Extraction
- **Total Vehicles Found**: {self.stats['vehicles_found']}
- **New Vehicles Extracted**: {self.stats['vehicles_new']}
- **Duplicates Detected**: {self.stats['vehicles_duplicates']}
- **Duplicate Rate**: {(self.stats['vehicles_duplicates'] / self.stats['vehicles_found'] * 100) if self.stats['vehicles_found'] > 0 else 0:.1f}%

### Gun Extraction
- **Total Guns Found**: {self.stats['guns_found']}
- **New Guns Extracted**: {self.stats['guns_new']}
- **Duplicates Detected**: {self.stats['guns_duplicates']}
- **Duplicate Rate**: {(self.stats['guns_duplicates'] / self.stats['guns_found'] * 100) if self.stats['guns_found'] > 0 else 0:.1f}%

---

## Database State

### Before Extraction
**Existing Database Entries**:
- bg_reference_vehicles: {len(self.existing_vehicles)} entries
- bg_reference_guns: {len(self.existing_guns)} entries

### After Import (Projected)
**Expected Database Growth**:
- bg_reference_vehicles: {len(self.existing_vehicles)} → {len(self.existing_vehicles) + self.stats['vehicles_new']} (+{self.stats['vehicles_new']})
- bg_reference_guns: {len(self.existing_guns)} → {len(self.existing_guns) + self.stats['guns_new']} (+{self.stats['guns_new']})

---

## Duplicate Detection Results

### Duplicate Vehicles ({self.stats['vehicles_duplicates']})
"""

        if self.duplicate_vehicles:
            for name, nation in sorted(self.duplicate_vehicles)[:20]:  # Show first 20
                report += f"- {name} ({nation})\n"
            if len(self.duplicate_vehicles) > 20:
                report += f"\n*... and {len(self.duplicate_vehicles) - 20} more*\n"
        else:
            report += "*No duplicate vehicles detected*\n"

        report += f"""
### Duplicate Guns ({self.stats['guns_duplicates']})
"""

        if self.duplicate_guns:
            for name, nation in sorted(self.duplicate_guns)[:20]:
                report += f"- {name} ({nation})\n"
            if len(self.duplicate_guns) > 20:
                report += f"\n*... and {len(self.duplicate_guns) - 20} more*\n"
        else:
            report += "*No duplicate guns detected*\n"

        report += f"""
---

## Sample Extracted Entries

### New Vehicles (Sample)
"""

        for vehicle in self.extracted_vehicles[:5]:
            report += f"""
**{vehicle['name']}** ({vehicle['nation']})
- Armor: F:{vehicle.get('armor_front', 'N/A')} S:{vehicle.get('armor_side', 'N/A')} R:{vehicle.get('armor_rear', 'N/A')}
- Movement: {vehicle.get('off_road_inches', 'N/A')}/{vehicle.get('road_inches', 'N/A')} inches
- Weapons: {', '.join(vehicle.get('weapons', [])) if vehicle.get('weapons') else 'N/A'}
"""

        report += f"""
### New Guns (Sample)
"""

        for gun in self.extracted_guns[:5]:
            report += f"""
**{gun['name']}** ({gun['nation']})
- Caliber: {gun.get('caliber_mm', 'N/A')}mm
- HE: {gun.get('he_dice', 'N/A')}D6
"""

        report += f"""
---

## Output Files

### JSON Exports
- **Vehicles**: `{VEHICLES_JSON.name}` ({self.stats['vehicles_new']} entries)
- **Guns**: `{GUNS_JSON.name}` ({self.stats['guns_new']} entries)

### Database Import
To import new entries into master_database.db:
```bash
python tools/import_fall_of_reich.py
```

---

## Data Quality Assessment

### Coverage
- **Vehicle Data Completeness**: {"High" if self.stats['vehicles_new'] > 20 else "Medium" if self.stats['vehicles_new'] > 10 else "Low"}
- **Gun Data Completeness**: {"High" if self.stats['guns_new'] > 10 else "Medium" if self.stats['guns_new'] > 5 else "Low"}

### Extraction Method
- PDF text extraction using pdfplumber
- Pattern matching for vehicle/gun datacards
- Duplicate detection using name + nation keys

### Known Limitations
- Complex table formats may require manual verification
- Some vehicle variants may be grouped together
- Gun penetration data requires detailed parsing

---

## Next Steps

1. Review sample entries for accuracy
2. Run import script to add to database
3. Verify no data corruption
4. Update BattleGroup extraction tracking

---

*Report generated by extract_fall_of_reich.py*
"""

        with open(REPORT_MD, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Generated report: {REPORT_MD.name}")

    def run(self):
        """Main execution flow."""
        print("=" * 70)
        print("BattleGroup Fall of the Reich Extraction")
        print("=" * 70)

        # Step 1: Load existing database
        self.load_existing_data()

        # Step 2: Extract PDF text
        pdf_text = self.extract_pdf_text()

        # Step 3: Parse and extract data
        self.extract_from_text(pdf_text)

        # Step 4: Save outputs
        self.save_outputs()

        print("\n" + "=" * 70)
        print("Extraction Complete!")
        print("=" * 70)
        print(f"New vehicles: {self.stats['vehicles_new']}")
        print(f"New guns: {self.stats['guns_new']}")
        print(f"Report: {REPORT_MD}")

if __name__ == '__main__':
    extractor = FallOfReichExtractor()
    extractor.run()
