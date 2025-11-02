#!/usr/bin/env python3
"""
Phase 6 Unit Parser for BattleGroup Army Lists

Parses Phase 6 unit JSON files and maps equipment to BattleGroup database.
Handles WITW ID mapping, equipment aggregation, and force organization.

Usage:
    from phase6_unit_parser import Phase6UnitParser

    parser = Phase6UnitParser()
    units = parser.get_units_for_quarter('german', '1941q2')
    equipment_list = parser.extract_equipment(units[0])
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"
UNITS_DIR = project_root / "data" / "output" / "units"


@dataclass
class MappedEquipment:
    """Equipment item mapped from Phase 6 to BattleGroup database"""
    canonical_id: str
    name: str
    count: int
    operational: int
    category: str
    points_regular: int
    br_regular: int
    confidence: str  # 'high', 'medium', 'low'
    mapping_method: str  # 'canonical_pattern', 'alias_search', 'fuzzy_match', 'manual'
    original_witw_id: str
    original_variant_name: str


class Phase6EquipmentMapper:
    """Maps Phase 6 WITW IDs to BattleGroup equipment canonical IDs"""

    NATION_PREFIXES = {
        'american': 'USA',
        'british': 'GBR',
        'german': 'GER',
        'italian': 'ITA',
        'french': 'FRA'
    }

    def __init__(self, db_path: str = str(DATABASE_PATH)):
        self.db_path = db_path
        self.conn = None
        self.unmapped_log = []

    def connect(self):
        """Connect to database"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def map_witw_id_to_canonical(
        self,
        phase6_witw_id: str,
        nation: str,
        variant_name: str = None
    ) -> Optional[Tuple[str, str, str]]:
        """
        Map Phase 6 WITW ID to equipment canonical_id

        Args:
            phase6_witw_id: WITW ID from Phase 6 JSON (e.g., "M4_SHERMAN")
            nation: Nation code (e.g., "american")
            variant_name: Optional variant name (e.g., "M4 Sherman")

        Returns:
            Tuple of (canonical_id, confidence, method) or None
            confidence: 'high', 'medium', 'low'
            method: 'canonical_pattern', 'alias_search', 'fuzzy_match'
        """
        if not self.conn:
            self.connect()

        # Tier 1: Direct canonical_id pattern (fast, expected 80%+ hit rate)
        result = self._try_canonical_pattern(phase6_witw_id, nation)
        if result:
            return result

        # Tier 2: Search aliases JSON (medium speed)
        result = self._try_alias_search(phase6_witw_id, nation)
        if result:
            return result

        # Tier 3: Fuzzy name match (slow but reliable)
        result = self._try_fuzzy_match(phase6_witw_id, nation, variant_name)
        if result:
            return result

        # Not found - log for manual review
        self.unmapped_log.append({
            'witw_id': phase6_witw_id,
            'nation': nation,
            'variant_name': variant_name
        })

        return None

    def _try_canonical_pattern(self, witw_id: str, nation: str) -> Optional[Tuple[str, str, str]]:
        """Try direct canonical_id pattern matching"""
        nation_prefix = self.NATION_PREFIXES.get(nation, nation.upper()[:3])

        # Try exact pattern: {NATION}_{WITW_ID}
        canonical_attempt = f"{nation_prefix}_{witw_id}"

        cursor = self.conn.execute(
            "SELECT canonical_id FROM equipment WHERE canonical_id = ?",
            (canonical_attempt,)
        )
        row = cursor.fetchone()

        if row:
            return (row['canonical_id'], 'high', 'canonical_pattern')

        # Try lowercase variant
        canonical_attempt_lower = canonical_attempt.lower()
        cursor = self.conn.execute(
            "SELECT canonical_id FROM equipment WHERE LOWER(canonical_id) = ?",
            (canonical_attempt_lower,)
        )
        row = cursor.fetchone()

        if row:
            return (row['canonical_id'], 'high', 'canonical_pattern')

        return None

    def _try_alias_search(self, witw_id: str, nation: str) -> Optional[Tuple[str, str, str]]:
        """Search aliases JSON field for WITW ID"""
        # Convert WITW ID to searchable formats
        search_variants = [
            witw_id,  # M4_SHERMAN
            witw_id.lower(),  # m4_sherman
            witw_id.replace('_', ' '),  # M4 SHERMAN
            witw_id.replace('_', ' ').title(),  # M4 Sherman
        ]

        nation_prefix = self.NATION_PREFIXES.get(nation, nation.upper()[:3])

        for variant in search_variants:
            cursor = self.conn.execute("""
                SELECT canonical_id, aliases
                FROM equipment
                WHERE nation = ?
                  AND (aliases LIKE ? OR aliases LIKE ?)
            """, (nation, f'%"{variant}"%', f"%'{variant}'%"))

            row = cursor.fetchone()
            if row:
                return (row['canonical_id'], 'medium', 'alias_search')

        return None

    def _try_fuzzy_match(
        self,
        witw_id: str,
        nation: str,
        variant_name: str = None
    ) -> Optional[Tuple[str, str, str]]:
        """Fuzzy name matching"""
        # Use variant_name if provided, otherwise convert WITW ID
        if variant_name:
            search_name = variant_name.lower()
        else:
            search_name = witw_id.replace('_', ' ').lower()

        # Try exact name match first
        cursor = self.conn.execute("""
            SELECT canonical_id, name
            FROM equipment
            WHERE nation = ?
              AND LOWER(name) = ?
        """, (nation, search_name))

        row = cursor.fetchone()
        if row:
            return (row['canonical_id'], 'medium', 'fuzzy_match_exact')

        # Try partial match
        cursor = self.conn.execute("""
            SELECT canonical_id, name
            FROM equipment
            WHERE nation = ?
              AND LOWER(name) LIKE ?
            LIMIT 1
        """, (nation, f'%{search_name}%'))

        row = cursor.fetchone()
        if row:
            return (row['canonical_id'], 'low', 'fuzzy_match_partial')

        return None

    def get_equipment_details(self, canonical_id: str) -> Optional[Dict]:
        """Get full equipment details from database"""
        if not self.conn:
            self.connect()

        cursor = self.conn.execute("""
            SELECT
                e.canonical_id,
                e.name,
                e.nation,
                e.category,
                eb.points_regular,
                eb.points_inexperienced,
                eb.points_veteran,
                eb.points_elite,
                eb.battle_rating_regular,
                eb.battle_rating_inexperienced,
                eb.battle_rating_veteran,
                eb.battle_rating_elite,
                eb.armor_front,
                eb.armor_side,
                eb.off_road_movement,
                eb.road_movement,
                eb.he_format,
                eb.special_rules
            FROM equipment e
            LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            WHERE e.canonical_id = ?
        """, (canonical_id,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


class Phase6UnitParser:
    """Parse Phase 6 unit JSON files for BattleGroup army list generation"""

    def __init__(self, units_dir: Path = UNITS_DIR):
        self.units_dir = units_dir
        self.mapper = Phase6EquipmentMapper()
        self.mapper.connect()

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'mapper'):
            self.mapper.close()

    def get_units_for_quarter(self, nation: str, quarter: str) -> List[Dict]:
        """
        Get all units for a nation and quarter

        Args:
            nation: Nation code (e.g., 'german')
            quarter: Quarter code (e.g., '1941q2')

        Returns:
            List of unit data dictionaries
        """
        pattern = f"{nation}_{quarter}_*.json"
        unit_files = list(self.units_dir.glob(pattern))

        units = []
        for unit_file in unit_files:
            try:
                with open(unit_file, 'r', encoding='utf-8') as f:
                    unit_data = json.load(f)
                    units.append(unit_data)
            except Exception as e:
                print(f"Warning: Could not load {unit_file}: {e}")

        return units

    def extract_equipment_from_unit(self, unit_data: Dict) -> List[MappedEquipment]:
        """
        Extract and map all equipment from a unit JSON

        Args:
            unit_data: Phase 6 unit JSON data

        Returns:
            List of MappedEquipment objects
        """
        nation = unit_data.get('nation', 'unknown')
        equipment_list = []

        # Extract from tanks section
        if 'tanks' in unit_data:
            equipment_list.extend(
                self._extract_from_category(unit_data['tanks'], nation, 'tanks')
            )

        # Extract from halftracks
        if 'halftracks' in unit_data:
            equipment_list.extend(
                self._extract_from_variants(
                    unit_data['halftracks'].get('variants', {}),
                    nation,
                    'halftracks'
                )
            )

        # Extract from armored_cars
        if 'armored_cars' in unit_data:
            equipment_list.extend(
                self._extract_from_variants(
                    unit_data['armored_cars'].get('variants', {}),
                    nation,
                    'armored_cars'
                )
            )

        # Extract from trucks
        if 'trucks' in unit_data:
            equipment_list.extend(
                self._extract_from_variants(
                    unit_data['trucks'].get('variants', {}),
                    nation,
                    'trucks'
                )
            )

        # Extract from artillery
        if 'artillery' in unit_data:
            equipment_list.extend(
                self._extract_from_artillery(unit_data['artillery'], nation)
            )

        return equipment_list

    def _extract_from_category(
        self,
        category_data: Dict,
        nation: str,
        category_name: str
    ) -> List[MappedEquipment]:
        """Extract equipment from a category (e.g., tanks with subcategories)"""
        equipment_list = []

        # Handle nested structure (heavy_tanks, medium_tanks, light_tanks)
        for subcategory_name, subcategory_data in category_data.items():
            if subcategory_name == 'total':
                continue

            # Handle enriched format (direct witw_id/count)
            if isinstance(subcategory_data, dict) and 'witw_id' in subcategory_data:
                witw_id = subcategory_data.get('witw_id', '')
                count = subcategory_data.get('count', 0)

                if not witw_id or count == 0:
                    continue

                # Map to canonical ID
                mapping_result = self.mapper.map_witw_id_to_canonical(
                    witw_id,
                    nation,
                    subcategory_name
                )

                if mapping_result:
                    canonical_id, confidence, method = mapping_result
                    details = self.mapper.get_equipment_details(canonical_id)

                    if details:
                        equipment_list.append(MappedEquipment(
                            canonical_id=canonical_id,
                            name=details['name'],
                            count=count,
                            operational=count,
                            category=category_name,
                            points_regular=details.get('points_regular', 0) or 0,
                            br_regular=details.get('battle_rating_regular', 0) or 0,
                            confidence=confidence,
                            mapping_method=method,
                            original_witw_id=witw_id,
                            original_variant_name=subcategory_name
                        ))

            # Handle old format (variants container)
            elif isinstance(subcategory_data, dict) and 'variants' in subcategory_data:
                equipment_list.extend(
                    self._extract_from_variants(
                        subcategory_data['variants'],
                        nation,
                        category_name
                    )
                )

        return equipment_list

    def _extract_from_variants(
        self,
        variants: Dict,
        nation: str,
        category: str
    ) -> List[MappedEquipment]:
        """Extract equipment from variants dictionary"""
        equipment_list = []

        for variant_name, variant_data in variants.items():
            # Skip if not a dict (safety check)
            if not isinstance(variant_data, dict):
                continue

            witw_id = variant_data.get('witw_id', '')
            count = variant_data.get('count', 0)
            operational = variant_data.get('operational', count)

            if not witw_id or count == 0:
                continue

            # Map to canonical ID
            mapping_result = self.mapper.map_witw_id_to_canonical(
                witw_id,
                nation,
                variant_name
            )

            if mapping_result:
                canonical_id, confidence, method = mapping_result

                # Get full equipment details
                details = self.mapper.get_equipment_details(canonical_id)

                if details:
                    equipment_list.append(MappedEquipment(
                        canonical_id=canonical_id,
                        name=details['name'],
                        count=count,
                        operational=operational,
                        category=category,
                        points_regular=details.get('points_regular', 0) or 0,
                        br_regular=details.get('battle_rating_regular', 0) or 0,
                        confidence=confidence,
                        mapping_method=method,
                        original_witw_id=witw_id,
                        original_variant_name=variant_name
                    ))

        return equipment_list

    def _extract_from_artillery(self, artillery_data: Dict, nation: str) -> List[MappedEquipment]:
        """Extract artillery equipment"""
        equipment_list = []

        # Handle nested artillery structure
        for artillery_type, type_data in artillery_data.items():
            if artillery_type == 'total':
                continue

            if isinstance(type_data, dict) and 'variants' in type_data:
                equipment_list.extend(
                    self._extract_from_variants(
                        type_data['variants'],
                        nation,
                        'artillery'
                    )
                )

        return equipment_list

    def get_unmapped_equipment(self) -> List[Dict]:
        """Get list of equipment that couldn't be mapped"""
        return self.mapper.unmapped_log


def main():
    """Test the parser"""
    import argparse

    parser = argparse.ArgumentParser(description='Test Phase 6 unit parser')
    parser.add_argument('--nation', required=True, help='Nation code (e.g., german)')
    parser.add_argument('--quarter', required=True, help='Quarter code (e.g., 1941q2)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')

    args = parser.parse_args()

    # Create parser
    unit_parser = Phase6UnitParser()

    # Get units
    print(f"Loading {args.nation} units for {args.quarter}...")
    units = unit_parser.get_units_for_quarter(args.nation, args.quarter)

    print(f"Found {len(units)} units")
    print()

    # Extract equipment from first unit
    if units:
        unit = units[0]
        unit_name = unit.get('unit_designation', 'Unknown')

        print(f"Extracting equipment from: {unit_name}")
        print()

        equipment = unit_parser.extract_equipment_from_unit(unit)

        print(f"Found {len(equipment)} equipment items:")
        print()

        # Group by confidence
        high_conf = [e for e in equipment if e.confidence == 'high']
        medium_conf = [e for e in equipment if e.confidence == 'medium']
        low_conf = [e for e in equipment if e.confidence == 'low']

        print(f"High confidence: {len(high_conf)}")
        print(f"Medium confidence: {len(medium_conf)}")
        print(f"Low confidence: {len(low_conf)}")
        print()

        if args.verbose:
            print("Equipment details:")
            print('-' * 100)
            for eq in equipment:
                print(f"{eq.name:30s} | Count: {eq.count:3d} | {eq.points_regular:3d} pts | "
                      f"{eq.br_regular:2d} BR | Conf: {eq.confidence:6s} | Method: {eq.mapping_method}")

        # Show unmapped
        unmapped = unit_parser.get_unmapped_equipment()
        if unmapped:
            print()
            print(f"WARNING: {len(unmapped)} items could not be mapped:")
            for item in unmapped:
                print(f"  - {item['witw_id']} ({item.get('variant_name', 'N/A')})")


if __name__ == '__main__':
    main()
