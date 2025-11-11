#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 9B Phase 1.1: Equipment Stats Validation

Validates equipment_battlegroup stats against BG Builder 599 vehicles.
Creates linkage from equipment_battlegroup to bg_builder_vehicles.
Documents confidence scores and gaps.

Author: North Africa TO&E Builder
Date: November 11, 2025
"""

import sqlite3
import sys
import io
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DATABASE_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")

@dataclass
class ValidationResult:
    """Equipment validation result."""
    equipment_id: str
    equipment_name: str
    bg_builder_id: Optional[int]
    bg_builder_name: Optional[str]
    confidence: int  # 0-100
    armor_match: bool
    movement_match: bool
    weapons_match: bool
    notes: str

class EquipmentValidator:
    """Validate equipment stats against BG Builder data."""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        self.conn.close()

    def add_bg_builder_linkage_column(self):
        """Add bg_builder_vehicle_id column to equipment_battlegroup if not exists."""
        cursor = self.conn.cursor()

        # Check if column exists
        cursor.execute('PRAGMA table_info(equipment_battlegroup)')
        cols = [col[1] for col in cursor.fetchall()]

        if 'bg_builder_vehicle_id' not in cols:
            print("Adding bg_builder_vehicle_id column to equipment_battlegroup...")
            cursor.execute('''
                ALTER TABLE equipment_battlegroup
                ADD COLUMN bg_builder_vehicle_id INTEGER
            ''')
            cursor.execute('''
                ALTER TABLE equipment_battlegroup
                ADD COLUMN bg_builder_match_confidence INTEGER
            ''')
            self.conn.commit()
            print("✓ Columns added")
        else:
            print("✓ bg_builder_vehicle_id column already exists")

    def normalize_name(self, name: str) -> str:
        """
        Normalize equipment name for fuzzy matching.

        Examples:
        - "M4 Sherman" → "m4 sherman"
        - "Pz.Kw. III" → "pzkw iii"
        - "SdKfz 222" → "sdkfz 222"
        """
        normalized = name.lower()

        # Remove punctuation
        normalized = re.sub(r'[\.,-]', ' ', normalized)

        # Normalize whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    def generate_name_variants(self, name: str) -> List[str]:
        """
        Generate name variants for fuzzy matching.

        Examples:
        - "M4 Sherman" → ["m4 sherman", "m4", "sherman", "m4a1", "m4a2"]
        - "PzKw III" → ["pzkw iii", "panzer iii", "pz kw iii", "pzkpfw iii"]
        """
        variants = [self.normalize_name(name)]

        # Common substitutions
        substitutions = {
            'pzkw': ['panzer', 'pz kw', 'pzkpfw', 'pz kpfw'],
            'sdkfz': ['sd kfz', 'sonderkraftfahrzeug'],
            'mk': ['mark'],
        }

        for abbrev, expansions in substitutions.items():
            if abbrev in variants[0]:
                for expansion in expansions:
                    variants.append(variants[0].replace(abbrev, expansion))

        # Extract model numbers
        model_match = re.search(r'\b(m\d+[a-z]?\d*)\b', variants[0])
        if model_match:
            variants.append(model_match.group(1))

        # Roman numerals
        roman_match = re.search(r'\b([ivx]+)\b', variants[0])
        if roman_match:
            variants.append(roman_match.group(1))

        return variants

    def find_bg_builder_match(self, equipment_id: str, equipment_name: str, nation: str) -> Tuple[Optional[int], int, str]:
        """
        Find best BG Builder vehicle match for equipment.

        Returns:
            (bg_builder_id, confidence, match_method)
        """
        cursor = self.conn.cursor()

        variants = self.generate_name_variants(equipment_name)

        # Try exact match first (bg_builder_vehicles doesn't have nation, so search by name only)
        for variant in variants:
            cursor.execute('''
                SELECT id, name
                FROM bg_builder_vehicles
                WHERE LOWER(REPLACE(REPLACE(name, '.', ''), ',', '')) = ?
                LIMIT 1
            ''', (variant,))

            row = cursor.fetchone()
            if row:
                return (row['id'], 100, f"Exact match: {row['name']}")

        # Try fuzzy match (contains)
        for variant in variants:
            cursor.execute('''
                SELECT id, name
                FROM bg_builder_vehicles
                WHERE LOWER(REPLACE(REPLACE(name, '.', ''), ',', '')) LIKE ?
                LIMIT 1
            ''', (f'%{variant}%',))

            row = cursor.fetchone()
            if row:
                return (row['id'], 85, f"Fuzzy match: {row['name']}")

        # Try individual words
        words = variants[0].split()
        if len(words) >= 2:
            for word in words:
                if len(word) >= 3:  # Skip short words like "mk", "ii"
                    cursor.execute('''
                        SELECT id, name
                        FROM bg_builder_vehicles
                        WHERE LOWER(name) LIKE ?
                        LIMIT 1
                    ''', (f'%{word}%',))

                    row = cursor.fetchone()
                    if row:
                        return (row['id'], 70, f"Partial match: {row['name']}")

        return (None, 0, "No match found")

    def validate_armor(self, equipment_id: str, bg_builder_id: int) -> Tuple[bool, str]:
        """Validate armor values match."""
        cursor = self.conn.cursor()

        # Get equipment armor
        cursor.execute('''
            SELECT armor_front, armor_side, armor_rear
            FROM equipment_battlegroup
            WHERE equipment_id = ?
        ''', (equipment_id,))
        eq_armor = cursor.fetchone()

        # Get BG Builder armor
        cursor.execute('''
            SELECT armor_front, armor_side, armor_rear
            FROM bg_builder_vehicles
            WHERE id = ?
        ''', (bg_builder_id,))
        bg_armor = cursor.fetchone()

        if not eq_armor or not bg_armor:
            return (False, "Missing armor data")

        # Compare (allow exact match or close match within 1 letter)
        matches = []
        for field in ['armor_front', 'armor_side', 'armor_rear']:
            eq_val = eq_armor[field]
            bg_val = bg_armor[field]

            if eq_val == bg_val:
                matches.append(True)
            elif eq_val and bg_val:
                # Check if within 1 armor letter (e.g., "G" vs "H")
                try:
                    eq_ord = ord(eq_val.upper())
                    bg_ord = ord(bg_val.upper())
                    if abs(eq_ord - bg_ord) <= 1:
                        matches.append(True)
                    else:
                        matches.append(False)
                except:
                    matches.append(False)
            else:
                matches.append(False)

        if all(matches):
            return (True, "Armor match")
        elif sum(matches) >= 2:
            return (True, "Armor close match (2/3)")
        else:
            return (False, f"Armor mismatch: {eq_armor['armor_front']}/{eq_armor['armor_side']}/{eq_armor['armor_rear']} vs {bg_armor['armor_front']}/{bg_armor['armor_side']}/{bg_armor['armor_rear']}")

    def validate_all_equipment(self) -> List[ValidationResult]:
        """Validate all equipment in equipment_battlegroup."""
        cursor = self.conn.cursor()

        # Get all equipment
        cursor.execute('''
            SELECT eb.equipment_id, e.name, e.nation
            FROM equipment_battlegroup eb
            JOIN equipment e ON eb.equipment_id = e.canonical_id
        ''')

        results = []
        total = 0
        matched = 0

        for row in cursor.fetchall():
            total += 1
            equipment_id = row['equipment_id']
            equipment_name = row['name']
            nation = row['nation']

            # Find BG Builder match
            bg_id, confidence, match_notes = self.find_bg_builder_match(equipment_id, equipment_name, nation)

            if bg_id:
                matched += 1
                # Validate armor
                armor_match, armor_notes = self.validate_armor(equipment_id, bg_id)

                result = ValidationResult(
                    equipment_id=equipment_id,
                    equipment_name=equipment_name,
                    bg_builder_id=bg_id,
                    bg_builder_name=match_notes.split(': ')[1] if ': ' in match_notes else "",
                    confidence=confidence,
                    armor_match=armor_match,
                    movement_match=False,  # TODO: implement
                    weapons_match=False,   # TODO: implement
                    notes=f"{match_notes} | {armor_notes}"
                )
            else:
                result = ValidationResult(
                    equipment_id=equipment_id,
                    equipment_name=equipment_name,
                    bg_builder_id=None,
                    bg_builder_name=None,
                    confidence=0,
                    armor_match=False,
                    movement_match=False,
                    weapons_match=False,
                    notes=match_notes
                )

            results.append(result)

            if total % 50 == 0:
                print(f"Processed {total} equipment items...")

        print(f"\n✓ Validation complete: {matched}/{total} matches ({100.0*matched/total:.1f}%)")
        return results

    def update_linkages(self, results: List[ValidationResult]):
        """Update equipment_battlegroup with BG Builder linkages."""
        cursor = self.conn.cursor()

        updates = 0
        for result in results:
            if result.bg_builder_id:
                cursor.execute('''
                    UPDATE equipment_battlegroup
                    SET bg_builder_vehicle_id = ?,
                        bg_builder_match_confidence = ?
                    WHERE equipment_id = ?
                ''', (result.bg_builder_id, result.confidence, result.equipment_id))
                updates += 1

        self.conn.commit()
        print(f"✓ Updated {updates} linkages in equipment_battlegroup")

    def generate_report(self, results: List[ValidationResult]):
        """Generate validation report."""
        print("\n" + "="*80)
        print("VALIDATION REPORT")
        print("="*80)

        # Summary statistics
        total = len(results)
        matched = sum(1 for r in results if r.bg_builder_id is not None)
        high_conf = sum(1 for r in results if r.confidence >= 90)
        medium_conf = sum(1 for r in results if 70 <= r.confidence < 90)
        low_conf = sum(1 for r in results if 50 <= r.confidence < 70)

        print(f"\nTotal equipment: {total}")
        print(f"Matched to BG Builder: {matched} ({100.0*matched/total:.1f}%)")
        print(f"  High confidence (90-100): {high_conf}")
        print(f"  Medium confidence (70-89): {medium_conf}")
        print(f"  Low confidence (50-69): {low_conf}")
        print(f"Not matched: {total - matched} ({100.0*(total-matched)/total:.1f}%)")

        # Armor validation
        armor_matches = sum(1 for r in results if r.armor_match)
        print(f"\nArmor validation:")
        print(f"  Matches: {armor_matches}/{matched} ({100.0*armor_matches/matched:.1f}% of matched)")

        # Sample high confidence matches
        print("\nSample high confidence matches (first 10):")
        high_conf_results = [r for r in results if r.confidence >= 90][:10]
        for r in high_conf_results:
            print(f"  {r.equipment_name} → {r.bg_builder_name} ({r.confidence}%)")

        # Sample unmatched
        print("\nSample unmatched equipment (first 10):")
        unmatched = [r for r in results if r.bg_builder_id is None][:10]
        for r in unmatched:
            print(f"  {r.equipment_name} - {r.notes}")

def main():
    """Main execution."""
    print("="*80)
    print("PHASE 9B PHASE 1.1: EQUIPMENT STATS VALIDATION")
    print("="*80)

    validator = EquipmentValidator()

    try:
        # Step 1: Add linkage column
        print("\n[Step 1/4] Adding BG Builder linkage column...")
        validator.add_bg_builder_linkage_column()

        # Step 2: Validate all equipment
        print("\n[Step 2/4] Validating equipment against BG Builder...")
        results = validator.validate_all_equipment()

        # Step 3: Update linkages
        print("\n[Step 3/4] Updating database linkages...")
        validator.update_linkages(results)

        # Step 4: Generate report
        print("\n[Step 4/4] Generating validation report...")
        validator.generate_report(results)

        print("\n" + "="*80)
        print("✅ VALIDATION COMPLETE")
        print("="*80)
        print("\nNext steps:")
        print("1. Review unmatched equipment and create manual mappings")
        print("2. Validate movement and weapons data")
        print("3. Extract Points/BR from BG Builder forces.js")

    finally:
        validator.close()

if __name__ == '__main__':
    main()
