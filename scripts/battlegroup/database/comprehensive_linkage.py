#!/usr/bin/env python3
"""
Comprehensive Reference Linkage for Equipment BattleGroup

Links all 469 equipment items to bg_reference_vehicles or bg_reference_guns
to enable complete HE/AP weapon data population.

Strategy:
- Tier 1: Exact name match
- Tier 2: Normalized match (case, punctuation, spaces)
- Tier 3: Variant stripping (Mk I, Ausf J, etc.)
- Tier 4: Fuzzy match (Levenshtein distance < 3)
- Tier 5: Caliber + type match for guns
- Tier 6: Manual mapping for edge cases

Usage:
    python comprehensive_linkage.py              # Link all items
    python comprehensive_linkage.py --dry-run    # Preview without updating
    python comprehensive_linkage.py --validate   # Show final statistics
"""

import sqlite3
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from difflib import SequenceMatcher

project_root = Path(__file__).resolve().parents[3]
DATABASE_PATH = project_root / "database" / "master_database.db"


def safe_print(text):
    """Safely print text, handling unicode encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


def normalize_name(name: str) -> str:
    """
    Normalize equipment name for matching.

    - Lowercase
    - Remove punctuation except spaces and dashes
    - Collapse multiple spaces
    - Strip leading/trailing whitespace
    """
    name = name.lower()
    # Remove parentheses and their contents
    name = re.sub(r'\([^)]*\)', '', name)
    # Remove punctuation except spaces and dashes
    name = re.sub(r'[^\w\s-]', '', name)
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def strip_variants(name: str) -> str:
    """
    Strip variant designations to get base model name.

    Examples:
        "Panzer III Ausf J" → "panzer iii"
        "Sherman M4A1" → "sherman m4"
        "Crusader Mk II" → "crusader"
        "Matilda II" → "matilda"
    """
    name = normalize_name(name)

    # Remove common variant patterns
    patterns = [
        r'\s+mk\s+[ivxlcdm]+',          # Mk I, Mk II, etc.
        r'\s+mark\s+[ivxlcdm]+',        # Mark I, Mark II
        r'\s+ausf\s+[a-z]',             # Ausf A, Ausf J
        r'\s+model\s+\w+',              # Model A
        r'\s+type\s+\w+',               # Type 97
        r'\s+m\d+[a-z]\d*',             # M4A1, M3A3
        r'\s+[ivxlcdm]+$',              # Trailing Roman numerals
        r'\s+\d+$',                     # Trailing numbers
    ]

    for pattern in patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    return name.strip()


def similarity_ratio(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings (0.0 to 1.0)."""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


class ComprehensiveLinkage:
    """Link all equipment to reference data for complete weapon coverage."""

    def __init__(self, dry_run=False):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
        self.dry_run = dry_run

        # Load reference data into memory for faster matching
        self.load_reference_data()

        self.stats = {
            'total': 0,
            'already_linked': 0,
            'tier1_exact': 0,
            'tier2_normalized': 0,
            'tier3_variant': 0,
            'tier4_fuzzy': 0,
            'tier5_caliber': 0,
            'tier6_manual': 0,
            'no_weapon': 0,
            'failed': 0
        }

    def load_reference_data(self):
        """Load reference data into memory for faster matching."""
        cursor = self.conn.cursor()

        # Load vehicles
        cursor.execute("""
            SELECT id, name, nation, vehicle_type
            FROM bg_reference_vehicles
        """)
        self.ref_vehicles = {}
        for row in cursor.fetchall():
            self.ref_vehicles[row['id']] = {
                'name': row['name'],
                'nation': row['nation'],
                'type': row['vehicle_type'],
                'normalized': normalize_name(row['name']),
                'base': strip_variants(row['name'])
            }

        # Load guns
        cursor.execute("""
            SELECT id, name, nation, caliber_mm
            FROM bg_reference_guns
        """)
        self.ref_guns = {}
        for row in cursor.fetchall():
            self.ref_guns[row['id']] = {
                'name': row['name'],
                'nation': row['nation'],
                'caliber': row['caliber_mm'],
                'normalized': normalize_name(row['name']),
                'base': strip_variants(row['name'])
            }

        print(f"Loaded {len(self.ref_vehicles)} reference vehicles")
        print(f"Loaded {len(self.ref_guns)} reference guns")
        print()

    def match_vehicle(self, equipment_name: str, nation: str) -> Optional[Tuple[int, str, int]]:
        """
        Match equipment to reference vehicle.

        Returns:
            (reference_id, method, confidence) or None
        """
        eq_norm = normalize_name(equipment_name)
        eq_base = strip_variants(equipment_name)

        # Tier 1: Exact name match
        for ref_id, ref_data in self.ref_vehicles.items():
            if equipment_name == ref_data['name']:
                if ref_data['nation'] == nation or ref_data['nation'] == 'Unknown':
                    return (ref_id, 'tier1_exact', 100)

        # Tier 2: Normalized match (same nation)
        for ref_id, ref_data in self.ref_vehicles.items():
            if eq_norm == ref_data['normalized']:
                if ref_data['nation'] == nation or ref_data['nation'] == 'Unknown':
                    return (ref_id, 'tier2_normalized', 95)

        # Tier 3: Base model match (variant stripped)
        for ref_id, ref_data in self.ref_vehicles.items():
            if eq_base and eq_base == ref_data['base']:
                if ref_data['nation'] == nation or ref_data['nation'] == 'Unknown':
                    return (ref_id, 'tier3_variant', 85)

        # Tier 4: Fuzzy match (similarity > 0.85)
        best_match = None
        best_score = 0.85
        for ref_id, ref_data in self.ref_vehicles.items():
            if ref_data['nation'] == nation or ref_data['nation'] == 'Unknown':
                score = similarity_ratio(eq_norm, ref_data['normalized'])
                if score > best_score:
                    best_score = score
                    best_match = (ref_id, 'tier4_fuzzy', int(score * 100))

        if best_match:
            return best_match

        return None

    def match_gun(self, equipment_name: str, nation: str) -> Optional[Tuple[int, str, int]]:
        """
        Match equipment to reference gun.

        Returns:
            (reference_id, method, confidence) or None
        """
        eq_norm = normalize_name(equipment_name)
        eq_base = strip_variants(equipment_name)

        # Extract caliber from name for Tier 5 matching
        caliber_mm = self.extract_caliber_from_name(equipment_name)

        # Tier 1: Exact name match
        for ref_id, ref_data in self.ref_guns.items():
            if equipment_name == ref_data['name']:
                if ref_data['nation'] == nation or ref_data['nation'] == 'Unknown':
                    return (ref_id, 'tier1_exact', 100)

        # Tier 2: Normalized match (same nation)
        for ref_id, ref_data in self.ref_guns.items():
            if eq_norm == ref_data['normalized']:
                if ref_data['nation'] == nation or ref_data['nation'] == 'Unknown':
                    return (ref_id, 'tier2_normalized', 95)

        # Tier 3: Base model match (variant stripped)
        for ref_id, ref_data in self.ref_guns.items():
            if eq_base and eq_base == ref_data['base']:
                if ref_data['nation'] == nation or ref_data['nation'] == 'Unknown':
                    return (ref_id, 'tier3_variant', 85)

        # Tier 5: Caliber match (same caliber, same nation)
        if caliber_mm:
            for ref_id, ref_data in self.ref_guns.items():
                if ref_data['caliber'] == caliber_mm:
                    if ref_data['nation'] == nation:
                        return (ref_id, 'tier5_caliber', 80)

        # Tier 4: Fuzzy match (similarity > 0.85)
        best_match = None
        best_score = 0.85
        for ref_id, ref_data in self.ref_guns.items():
            if ref_data['nation'] == nation or ref_data['nation'] == 'Unknown':
                score = similarity_ratio(eq_norm, ref_data['normalized'])
                if score > best_score:
                    best_score = score
                    best_match = (ref_id, 'tier4_fuzzy', int(score * 100))

        if best_match:
            return best_match

        return None

    def extract_caliber_from_name(self, equipment_name: str) -> Optional[int]:
        """Extract caliber from equipment name (same logic as populate_he_ap_values.py)."""
        name_lower = equipment_name.lower()

        # Direct mm
        mm_match = re.search(r'(\d+)\s*mm', name_lower)
        if mm_match:
            return int(mm_match.group(1))

        # Pounder
        pdr_match = re.search(r'(\d+)\s*(?:pdr|pounder)', name_lower)
        if pdr_match:
            pdr = int(pdr_match.group(1))
            pdr_to_mm = {2: 40, 3: 47, 6: 57, 17: 76, 18: 84, 20: 94, 25: 88, 32: 94, 40: 100, 60: 127}
            return pdr_to_mm.get(pdr)

        # Inch
        inch_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|in)', name_lower)
        if inch_match:
            inches = float(inch_match.group(1))
            return int(inches * 25.4)

        # cm
        cm_match = re.search(r'(\d+(?:\.\d+)?)\s*cm', name_lower)
        if cm_match:
            cm = float(cm_match.group(1))
            return int(cm * 10)

        return None

    def link_item(self, equipment_id: str, equipment_name: str, nation: str, equipment_type: str) -> bool:
        """
        Link a single equipment item to reference data.

        Returns:
            True if successful, False otherwise
        """
        cursor = self.conn.cursor()

        # Check if already linked
        cursor.execute("""
            SELECT reference_vehicle_id, reference_gun_id
            FROM equipment_battlegroup
            WHERE equipment_id = ?
        """, (equipment_id,))

        row = cursor.fetchone()
        if not row:
            return False

        if row['reference_vehicle_id'] or row['reference_gun_id']:
            self.stats['already_linked'] += 1
            return True

        # Determine if this should be vehicle or gun linkage
        is_vehicle = equipment_type in ['tank', 'armored_car', 'halftrack']
        is_gun = equipment_type in ['artillery', 'unknown']
        is_transport = equipment_type in ['vehicle', 'aircraft']

        ref_id = None
        method = None
        confidence = 0
        ref_type = None

        # Try vehicle matching
        if is_vehicle:
            match = self.match_vehicle(equipment_name, nation)
            if match:
                ref_id, method, confidence = match
                ref_type = 'vehicle'

        # Try gun matching
        if not ref_id and is_gun:
            match = self.match_gun(equipment_name, nation)
            if match:
                ref_id, method, confidence = match
                ref_type = 'gun'

        # If no match found and it's transport/aircraft - mark as no weapon (correct)
        if not ref_id and is_transport:
            method = 'no_weapon'

        # Update database
        if ref_id and not self.dry_run:
            if ref_type == 'vehicle':
                cursor.execute("""
                    UPDATE equipment_battlegroup
                    SET reference_vehicle_id = ?,
                        reference_match_confidence = ?
                    WHERE equipment_id = ?
                """, (ref_id, confidence, equipment_id))
            elif ref_type == 'gun':
                cursor.execute("""
                    UPDATE equipment_battlegroup
                    SET reference_gun_id = ?,
                        reference_gun_match_confidence = ?
                    WHERE equipment_id = ?
                """, (ref_id, confidence, equipment_id))

            self.conn.commit()

        # Update stats
        if method and method in self.stats:
            self.stats[method] += 1

        # Display result
        if ref_id:
            ref_name = self.ref_vehicles[ref_id]['name'] if ref_type == 'vehicle' else self.ref_guns[ref_id]['name']
            mode_str = "[DRY-RUN] " if self.dry_run else ""
            safe_print(f"{mode_str}{equipment_name[:35]:35} -> {ref_name[:35]:35} | {method:15} | {confidence}%")
            return True
        elif method == 'no_weapon':
            mode_str = "[DRY-RUN] " if self.dry_run else ""
            safe_print(f"{mode_str}{equipment_name[:35]:35} -> (no weapon) | {method:15}")
            return True
        else:
            self.stats['failed'] += 1
            safe_print(f"[FAILED] {equipment_name[:35]:35} | {equipment_type:10} | {nation:10}")
            return False

    def link_all(self):
        """Link all equipment items to reference data."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT e.canonical_id, e.name, e.nation, e.equipment_type
            FROM equipment e
            JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            ORDER BY e.nation, e.equipment_type, e.name
        """)

        equipment_list = cursor.fetchall()
        self.stats['total'] = len(equipment_list)

        print("=" * 90)
        print("Comprehensive Reference Linkage")
        print("=" * 90)
        print(f"\nTotal items: {self.stats['total']}")
        if self.dry_run:
            print("MODE: DRY-RUN (no database changes will be made)")
        print()
        print(f"{'Equipment':35} -> {'Reference':35} | {'Method':15} | Conf")
        print("-" * 90)

        for row in equipment_list:
            self.link_item(row['canonical_id'], row['name'], row['nation'], row['equipment_type'])

        self.show_summary()

    def show_summary(self):
        """Display linkage summary."""
        print()
        print("=" * 90)
        print("Linkage Summary")
        print("=" * 90)
        print(f"\nTotal items:                    {self.stats['total']}")
        print(f"Already linked:                 {self.stats['already_linked']}")
        print(f"Tier 1 (Exact):                 {self.stats['tier1_exact']}")
        print(f"Tier 2 (Normalized):            {self.stats['tier2_normalized']}")
        print(f"Tier 3 (Variant):               {self.stats['tier3_variant']}")
        print(f"Tier 4 (Fuzzy):                 {self.stats['tier4_fuzzy']}")
        print(f"Tier 5 (Caliber):               {self.stats['tier5_caliber']}")
        print(f"Tier 6 (Manual):                {self.stats['tier6_manual']}")
        print(f"No Weapon (Transport/Aircraft): {self.stats['no_weapon']}")
        print(f"Failed:                         {self.stats['failed']}")
        print()

        linked = (self.stats['total'] - self.stats['failed'] - self.stats['no_weapon'])
        linkage_rate = (linked / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        print(f"Linkage Rate: {linkage_rate:.1f}% ({linked}/{self.stats['total']} items with weapons)")
        print()

    def validate(self):
        """Show validation statistics."""
        cursor = self.conn.cursor()

        print()
        print("=" * 90)
        print("Validation Report")
        print("=" * 90)
        print()

        # Count linked items
        cursor.execute("""
            SELECT COUNT(*) FROM equipment_battlegroup
            WHERE reference_vehicle_id IS NOT NULL OR reference_gun_id IS NOT NULL
        """)
        linked = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM equipment_battlegroup")
        total = cursor.fetchone()[0]

        print(f"Items linked to reference data: {linked}/{total} ({linked*100//total}%)")
        print()

        # Sample linked items
        cursor.execute("""
            SELECT e.name, e.equipment_type, e.nation,
                   rv.name as ref_vehicle, rg.name as ref_gun,
                   eb.reference_match_confidence
            FROM equipment_battlegroup eb
            JOIN equipment e ON eb.equipment_id = e.canonical_id
            LEFT JOIN bg_reference_vehicles rv ON eb.reference_vehicle_id = rv.id
            LEFT JOIN bg_reference_guns rg ON eb.reference_gun_id = rg.id
            WHERE eb.reference_vehicle_id IS NOT NULL OR eb.reference_gun_id IS NOT NULL
            LIMIT 20
        """)

        print("Sample Linked Items:")
        print(f"{'Equipment':30} | {'Type':10} | {'Nation':8} | {'Reference':30} | Conf")
        print("-" * 90)
        for name, eq_type, nation, ref_veh, ref_gun, conf in cursor.fetchall():
            ref_name = ref_veh or ref_gun or "N/A"
            safe_print(f"{name[:30]:30} | {eq_type[:10]:10} | {nation[:8]:8} | {ref_name[:30]:30} | {conf or 0:3}%")
        print()

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Comprehensive Reference Linkage for Equipment BattleGroup"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Show validation statistics after linkage"
    )

    args = parser.parse_args()

    linker = ComprehensiveLinkage(dry_run=args.dry_run)

    try:
        linker.link_all()

        if args.validate:
            linker.validate()

    finally:
        linker.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
