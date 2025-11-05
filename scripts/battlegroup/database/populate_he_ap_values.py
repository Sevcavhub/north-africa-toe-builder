#!/usr/bin/env python3
"""
Populate HE/AP Values for Equipment BattleGroup Table

This script fills in missing HE/AP weapon data for all 469 equipment items.

Strategy:
1. For items linked to bg_reference_vehicles (80 items):
   - Parse weapons JSON to find turret weapon
   - Match weapon to bg_reference_guns
   - Copy HE/AP values

2. For items linked to bg_reference_guns (16 items):
   - Directly copy HE/AP values

3. For remaining items (373 items):
   - Get caliber from equipment table or WWIITANKS data
   - Use conversion formulas (he_calculator, penetration_converter)

Usage:
    python populate_he_ap_values.py              # Populate all 469 items
    python populate_he_ap_values.py --dry-run    # Preview changes without updating
    python populate_he_ap_values.py --validate   # Show final statistics
"""

import sqlite3
import json
import sys
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Import conversion tools
from scripts.battlegroup.conversion.he_calculator import calculate_he_effect
from scripts.battlegroup.conversion.penetration_converter import convert_penetration

DATABASE_PATH = project_root / "database" / "master_database.db"
MANUAL_CALIBER_MAP_PATH = Path(__file__).parent / "manual_caliber_mapping.json"


def safe_print(text):
    """Safely print text, handling unicode encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


class HEAPPopulator:
    """Populate HE/AP weapon data for equipment_battlegroup table."""

    def __init__(self, dry_run=False):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
        self.dry_run = dry_run

        # Load manual caliber mapping
        self.manual_caliber_map = {}
        if MANUAL_CALIBER_MAP_PATH.exists():
            with open(MANUAL_CALIBER_MAP_PATH, 'r') as f:
                data = json.load(f)
                self.manual_caliber_map = data.get('mappings', {})

        self.stats = {
            'total': 0,
            'method_1_reference_vehicle': 0,
            'method_2_reference_gun': 0,
            'method_3_formula': 0,
            'method_3_5_manual_map': 0,
            'method_4_no_weapon': 0,
            'failed': 0
        }

    def parse_weapon_json(self, weapons_json: str) -> Optional[str]:
        """
        Parse weapons JSON and extract turret weapon name.

        Args:
            weapons_json: JSON string like '[{"weapon": "50mmL60", "mount": "Turret"...}]'

        Returns:
            Weapon name (e.g., "50mmL60") or None
        """
        try:
            weapons = json.loads(weapons_json)
            for wpn in weapons:
                if wpn.get('mount', '').lower() == 'turret':
                    return wpn.get('weapon')
            # If no turret weapon, take first weapon
            if weapons:
                return weapons[0].get('weapon')
        except:
            pass
        return None

    def get_reference_gun_data(self, gun_name: str) -> Optional[Dict]:
        """
        Look up gun in bg_reference_guns by name.

        Args:
            gun_name: Gun name like "50mmL60"

        Returns:
            Dict with HE/AP values or None
        """
        cursor = self.conn.cursor()

        # Try exact match
        cursor.execute("""
            SELECT he_dice, he_target,
                   ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
            FROM bg_reference_guns
            WHERE name = ? OR name LIKE ?
            LIMIT 1
        """, (gun_name, f'%{gun_name}%'))

        row = cursor.fetchone()
        if row:
            return dict(row)

        return None

    def extract_caliber_from_name(self, equipment_name: str) -> Optional[int]:
        """
        Extract caliber from equipment name.

        Examples:
            "2 Pdr AT" → 40mm (2 pounder)
            "25 Pdr" → 88mm (25 pounder)
            "75mm Gun" → 75mm
            "3.7 Inch Howitzer" → 94mm

        Returns:
            Caliber in mm or None
        """
        name_lower = equipment_name.lower()

        # Pattern 1: Direct mm mention (e.g., "75mm", "88 mm")
        mm_match = re.search(r'(\d+)\s*mm', name_lower)
        if mm_match:
            return int(mm_match.group(1))

        # Pattern 2: Pounder (British designation) - matches "pdr", "pounder", with optional hyphen
        # Pounder to mm conversion:
        # 2 pdr = 40mm, 6 pdr = 57mm, 17 pdr = 76mm, 25 pdr = 88mm
        pdr_match = re.search(r'(\d+)\s*[-\s]?\s*(?:pdr|pounder)\.?', name_lower)
        if pdr_match:
            pdr = int(pdr_match.group(1))
            pdr_to_mm = {
                2: 40,
                3: 47,
                6: 57,
                17: 76,
                18: 84,
                20: 94,
                25: 88,
                32: 94,
                40: 100,
                60: 127
            }
            return pdr_to_mm.get(pdr)

        # Pattern 3: Inch designation (e.g., "3.7 Inch", "4.5-inch", "3.7-inch")
        inch_match = re.search(r'(\d+(?:\.\d+)?)\s*[-\s]?\s*(?:inch|in)\.?', name_lower)
        if inch_match:
            inches = float(inch_match.group(1))
            return int(inches * 25.4)  # Convert to mm

        # Pattern 4: cm designation (e.g., "8.8cm", "7.5 cm", "8.8-cm")
        cm_match = re.search(r'(\d+(?:\.\d+)?)\s*[-\s]?\s*cm\.?', name_lower)
        if cm_match:
            cm = float(cm_match.group(1))
            return int(cm * 10)  # Convert to mm

        return None

    def populate_item(self, equipment_id: str) -> bool:
        """
        Populate HE/AP values for a single equipment item.

        Returns:
            True if successful, False otherwise
        """
        cursor = self.conn.cursor()

        # Get equipment data
        cursor.execute("""
            SELECT eb.*, e.name, e.equipment_type
            FROM equipment_battlegroup eb
            JOIN equipment e ON eb.equipment_id = e.canonical_id
            WHERE eb.equipment_id = ?
        """, (equipment_id,))

        row = cursor.fetchone()
        if not row:
            return False

        name = row['name']
        equipment_type = row['equipment_type']
        ref_vehicle_id = row['reference_vehicle_id']
        ref_gun_id = row['reference_gun_id']

        he_dice = None
        he_target = None
        he_format = None
        ap_0_10 = None
        ap_10_20 = None
        ap_20_30 = None
        ap_30_40 = None
        ap_40_50 = None
        ap_50_70 = None
        method = None

        # METHOD 1: Reference vehicle link
        if ref_vehicle_id:
            cursor.execute("""
                SELECT weapons FROM bg_reference_vehicles WHERE id = ?
            """, (ref_vehicle_id,))

            ref_row = cursor.fetchone()
            if ref_row and ref_row['weapons']:
                weapon_name = self.parse_weapon_json(ref_row['weapons'])
                if weapon_name:
                    gun_data = self.get_reference_gun_data(weapon_name)
                    if gun_data:
                        he_dice = gun_data['he_dice']
                        he_target = gun_data['he_target']
                        he_format = f"{he_dice}/{he_target}" if he_dice and he_target else None
                        ap_0_10 = gun_data['ap_0_10']
                        ap_10_20 = gun_data['ap_10_20']
                        ap_20_30 = gun_data['ap_20_30']
                        ap_30_40 = gun_data['ap_30_40']
                        ap_40_50 = gun_data['ap_40_50']
                        ap_50_70 = gun_data['ap_50_70']
                        method = 'reference_vehicle'
                        self.stats['method_1_reference_vehicle'] += 1

        # METHOD 2: Reference gun link
        if not method and ref_gun_id:
            cursor.execute("""
                SELECT he_dice, he_target,
                       ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
                FROM bg_reference_guns WHERE id = ?
            """, (ref_gun_id,))

            gun_row = cursor.fetchone()
            if gun_row:
                he_dice = gun_row['he_dice']
                he_target = gun_row['he_target']
                he_format = f"{he_dice}/{he_target}" if he_dice and he_target else None
                ap_0_10 = gun_row['ap_0_10']
                ap_10_20 = gun_row['ap_10_20']
                ap_20_30 = gun_row['ap_20_30']
                ap_30_40 = gun_row['ap_30_40']
                ap_40_50 = gun_row['ap_40_50']
                ap_50_70 = gun_row['ap_50_70']
                method = 'reference_gun'
                self.stats['method_2_reference_gun'] += 1

        # METHOD 3: Formula-based conversion (extract caliber from name)
        if not method:
            caliber_mm = self.extract_caliber_from_name(name)
            if caliber_mm:
                # Extract barrel length from name if present
                barrel_match = re.search(r'L[/-]?(\d+)', name, re.IGNORECASE)
                barrel_length = f"L{barrel_match.group(1)}" if barrel_match else None

                # Calculate HE
                he_result = calculate_he_effect(caliber_mm, gun_name=name)
                he_dice = he_result.get('dice')
                he_target = he_result.get('target')
                he_format = he_result.get('format')

                # Calculate AP
                ap_result = convert_penetration(caliber_mm, barrel_length, gun_name=name)
                ap_0_10 = ap_result.get('ap_0_10')
                ap_10_20 = ap_result.get('ap_10_20')
                ap_20_30 = ap_result.get('ap_20_30')
                ap_30_40 = ap_result.get('ap_30_40')
                ap_40_50 = ap_result.get('ap_40_50')
                ap_50_70 = ap_result.get('ap_50_70')
                method = 'formula'
                self.stats['method_3_formula'] += 1

        # METHOD 3.5: Manual caliber mapping (for tanks without caliber in name)
        if not method:
            # Check manual mapping by partial name match
            for map_key, map_data in self.manual_caliber_map.items():
                if map_key.lower() in name.lower():
                    caliber_mm = map_data.get('caliber')
                    barrel_length = map_data.get('barrel')

                    if caliber_mm:
                        # Calculate HE
                        he_result = calculate_he_effect(caliber_mm, gun_name=name)
                        he_dice = he_result.get('dice')
                        he_target = he_result.get('target')
                        he_format = he_result.get('format')

                        # Calculate AP
                        ap_result = convert_penetration(caliber_mm, barrel_length, gun_name=name)
                        ap_0_10 = ap_result.get('ap_0_10')
                        ap_10_20 = ap_result.get('ap_10_20')
                        ap_20_30 = ap_result.get('ap_20_30')
                        ap_30_40 = ap_result.get('ap_30_40')
                        ap_40_50 = ap_result.get('ap_40_50')
                        ap_50_70 = ap_result.get('ap_50_70')
                        method = 'manual_map'
                        self.stats['method_3_5_manual_map'] += 1
                        break

        # METHOD 4: No weapon (transport, aircraft, etc.)
        if not method and equipment_type in ['aircraft', 'vehicle']:
            # Most transport vehicles and all aircraft don't have ground weapons
            method = 'no_weapon'
            self.stats['method_4_no_weapon'] += 1

        # Update database
        if method:
            if not self.dry_run:
                cursor.execute("""
                    UPDATE equipment_battlegroup
                    SET he_dice = ?,
                        he_target = ?,
                        he_format = ?,
                        ap_0_10 = ?,
                        ap_10_20 = ?,
                        ap_20_30 = ?,
                        ap_30_40 = ?,
                        ap_40_50 = ?,
                        ap_50_70 = ?
                    WHERE equipment_id = ?
                """, (he_dice, he_target, he_format, ap_0_10, ap_10_20, ap_20_30,
                      ap_30_40, ap_40_50, ap_50_70, equipment_id))
                self.conn.commit()

            # Display result
            he_str = he_format or "N/A"
            ap_str = f"{ap_0_10 or '-'}/{ap_10_20 or '-'}/{ap_20_30 or '-'}"
            mode_str = "[DRY-RUN] " if self.dry_run else ""
            safe_print(f"{mode_str}{name[:40]:40} | HE: {he_str:7} | AP: {ap_str:11} | {method}")

            return True
        else:
            self.stats['failed'] += 1
            safe_print(f"[FAILED] {name[:40]:40} | No caliber data found")
            return False

    def populate_all(self):
        """Populate HE/AP values for all 469 equipment items."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT equipment_id
            FROM equipment_battlegroup
            ORDER BY equipment_id
        """)

        equipment_list = [row['equipment_id'] for row in cursor.fetchall()]
        self.stats['total'] = len(equipment_list)

        print("=" * 80)
        print("Populate HE/AP Values for Equipment BattleGroup")
        print("=" * 80)
        print(f"\nTotal items: {self.stats['total']}")
        if self.dry_run:
            print("MODE: DRY-RUN (no database changes will be made)")
        print()
        print(f"{'Equipment':40} | {'HE':7} | {'AP':11} | Method")
        print("-" * 80)

        for equipment_id in equipment_list:
            self.populate_item(equipment_id)

        self.show_summary()

    def show_summary(self):
        """Display population summary."""
        print()
        print("=" * 80)
        print("Population Summary")
        print("=" * 80)
        print(f"\nTotal items:                    {self.stats['total']}")
        print(f"Method 1 (Reference Vehicle):   {self.stats['method_1_reference_vehicle']}")
        print(f"Method 2 (Reference Gun):       {self.stats['method_2_reference_gun']}")
        print(f"Method 3 (Formula):             {self.stats['method_3_formula']}")
        print(f"Method 3.5 (Manual Map):        {self.stats['method_3_5_manual_map']}")
        print(f"Method 4 (No Weapon):           {self.stats['method_4_no_weapon']}")
        print(f"Failed:                         {self.stats['failed']}")
        print()

        success = (self.stats['total'] - self.stats['failed'])
        success_rate = (success / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}% ({success}/{self.stats['total']})")
        print()

    def validate(self):
        """Show validation statistics."""
        cursor = self.conn.cursor()

        print()
        print("=" * 80)
        print("Validation Report")
        print("=" * 80)
        print()

        # Count items with HE/AP data
        cursor.execute("""
            SELECT COUNT(*) FROM equipment_battlegroup
            WHERE he_dice IS NOT NULL OR ap_0_10 IS NOT NULL
        """)
        with_data = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM equipment_battlegroup")
        total = cursor.fetchone()[0]

        print(f"Items with HE/AP data: {with_data}/{total} ({with_data*100//total}%)")
        print()

        # Sample successful entries
        cursor.execute("""
            SELECT e.name, e.equipment_type, eb.he_format,
                   eb.ap_0_10, eb.ap_10_20, eb.ap_20_30
            FROM equipment_battlegroup eb
            JOIN equipment e ON eb.equipment_id = e.canonical_id
            WHERE eb.he_dice IS NOT NULL
            LIMIT 10
        """)

        print("Sample Items with HE/AP Data:")
        print(f"{'Equipment':35} | {'Type':15} | HE      | AP (0-30\")")
        print("-" * 80)
        for name, eq_type, he_fmt, ap1, ap2, ap3 in cursor.fetchall():
            ap_str = f"{ap1 or '-'}/{ap2 or '-'}/{ap3 or '-'}"
            safe_print(f"{name[:35]:35} | {eq_type[:15]:15} | {he_fmt or 'N/A':7} | {ap_str}")
        print()

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Populate HE/AP Values for Equipment BattleGroup"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Show validation statistics after population"
    )

    args = parser.parse_args()

    populator = HEAPPopulator(dry_run=args.dry_run)

    try:
        populator.populate_all()

        if args.validate:
            populator.validate()

    finally:
        populator.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
