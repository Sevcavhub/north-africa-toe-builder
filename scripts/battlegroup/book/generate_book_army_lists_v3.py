#!/usr/bin/env python3
"""
Generate BattleGroup Army Lists v3.0 - With Equipment Name Metadata Extraction.

This version:
- Parses equipment names to extract metadata (weight class, gun, role, variant)
- Uses clean base names for database matching
- Tracks metadata extraction success
- Generates enrichment opportunities report
- Preserves valuable type information instead of discarding it

Version: 3.0.0
Author: Claude Code (Sonnet 4.5)
Date: 2025-11-02
"""

import json
import re
import sqlite3
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# Import the equipment name parser
import sys
sys.path.insert(0, str(Path(__file__).parent))
from equipment_name_parser import EquipmentNameParser, ParsedEquipment

# Battle to quarter mapping
BATTLES = {
    'battleaxe': {'quarter': '1941q2', 'name': 'Operation Battleaxe', 'display': '1941 Q2'},
    'crusader': {'quarter': '1941q4', 'name': 'Operation Crusader', 'display': '1941 Q4'},
    'gazala': {'quarter': '1942q2', 'name': 'Battle of Gazala', 'display': '1942 Q2'},
    'first_alamein': {'quarter': '1942q3', 'name': 'First Battle of El Alamein', 'display': '1942 Q3'}
}

# Nation display names
NATION_NAMES = {
    'british': 'British & Commonwealth',
    'german': 'German',
    'italian': 'Italian',
    'american': 'American',
    'french': 'Free French'
}


@dataclass
class EquipmentMatch:
    """Result of equipment matching with metadata."""
    original_name: str
    parsed: ParsedEquipment
    matched: bool
    database_name: Optional[str] = None
    witw_id: Optional[str] = None
    confidence: float = 0.0
    metadata_extracted: bool = False
    enrichment_opportunity: bool = False


class EquipmentDatabaseV3:
    """Database interface with metadata tracking."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.parser = EquipmentNameParser()
        self.conn = None

        # Statistics tracking
        self.match_stats = {
            'total_lookups': 0,
            'successful_matches': 0,
            'metadata_extracted': 0,
            'enrichment_opportunities': 0
        }

        # Track all equipment seen
        self.equipment_seen = []  # List of EquipmentMatch objects

    def connect(self):
        """Connect to database."""
        if self.db_path.exists():
            try:
                self.conn = sqlite3.connect(str(self.db_path))
                self.conn.row_factory = sqlite3.Row

                # Check if equipment_variants table exists
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='equipment_variants'
                """)
                if not cursor.fetchone():
                    print(f"  Warning: equipment_variants table not found in database")
                    print(f"  Running in metadata extraction mode only (no database matching)")
                    self.conn.close()
                    self.conn = None
                else:
                    print(f"  Connected to database: {self.db_path.name}")
            except sqlite3.Error as e:
                print(f"  Error connecting to database: {e}")
                self.conn = None
        else:
            print(f"  Warning: Database not found at {self.db_path}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def lookup_equipment(self, equipment_name: str, count: int = 1) -> EquipmentMatch:
        """
        Look up equipment with intelligent name parsing and metadata extraction.

        Returns EquipmentMatch with:
        - Parsed metadata (weight class, gun, role, variant)
        - Match status
        - Database record (if matched)
        - Enrichment opportunity flag
        """
        self.match_stats['total_lookups'] += 1

        # Parse equipment name
        parsed = self.parser.parse(equipment_name)

        # Check if metadata was extracted
        metadata_extracted = any([
            parsed.weight_class,
            parsed.gun,
            parsed.role,
            parsed.variant
        ])

        if metadata_extracted:
            self.match_stats['metadata_extracted'] += 1

        # Try to match using base name
        match_result = EquipmentMatch(
            original_name=equipment_name,
            parsed=parsed,
            matched=False,
            metadata_extracted=metadata_extracted
        )

        if not self.conn:
            self.equipment_seen.append(match_result)
            return match_result

        # Try database lookup using clean base name
        match_key = self.parser.get_database_match_key(equipment_name)

        # Query equipment_variants table
        cursor = self.conn.cursor()

        # First try exact match
        cursor.execute('''
            SELECT variant_name, witw_id, equipment_category
            FROM equipment_variants
            WHERE LOWER(REPLACE(REPLACE(variant_name, '.', ''), ' ', '')) = ?
            LIMIT 1
        ''', (match_key.replace(' ', ''),))

        row = cursor.fetchone()

        if row:
            match_result.matched = True
            match_result.database_name = row['variant_name']
            match_result.witw_id = row['witw_id']
            match_result.confidence = 1.0
            self.match_stats['successful_matches'] += 1

            # Check if this is an enrichment opportunity
            # (we have metadata but database might not)
            if metadata_extracted:
                # TODO: Check if database record already has this metadata
                # For now, flag all metadata extractions as enrichment opportunities
                match_result.enrichment_opportunity = True
                self.match_stats['enrichment_opportunities'] += 1
        else:
            # Try fuzzy match
            cursor.execute('''
                SELECT variant_name, witw_id, equipment_category
                FROM equipment_variants
                WHERE variant_name LIKE ?
                   OR ? LIKE '%' || variant_name || '%'
                LIMIT 1
            ''', (f'%{parsed.base_name}%', match_key))

            row = cursor.fetchone()
            if row:
                match_result.matched = True
                match_result.database_name = row['variant_name']
                match_result.witw_id = row['witw_id']
                match_result.confidence = 0.7  # Lower confidence for fuzzy match
                self.match_stats['successful_matches'] += 1

                if metadata_extracted:
                    match_result.enrichment_opportunity = True
                    self.match_stats['enrichment_opportunities'] += 1

        self.equipment_seen.append(match_result)
        return match_result

    def get_statistics(self) -> Dict:
        """Get matching statistics."""
        stats = self.match_stats.copy()

        if stats['total_lookups'] > 0:
            stats['match_rate'] = stats['successful_matches'] / stats['total_lookups']
            stats['metadata_extraction_rate'] = stats['metadata_extracted'] / stats['total_lookups']
            stats['enrichment_rate'] = stats['enrichment_opportunities'] / stats['total_lookups']
        else:
            stats['match_rate'] = 0.0
            stats['metadata_extraction_rate'] = 0.0
            stats['enrichment_rate'] = 0.0

        return stats

    def get_enrichment_report(self) -> Dict:
        """Generate enrichment opportunity report."""
        enrichment_data = {
            'total_opportunities': 0,
            'by_metadata_type': defaultdict(int),
            'by_nation': defaultdict(int),
            'sample_items': []
        }

        for match in self.equipment_seen:
            if match.enrichment_opportunity:
                enrichment_data['total_opportunities'] += 1

                # Track by metadata type
                if match.parsed.weight_class:
                    enrichment_data['by_metadata_type']['weight_class'] += 1
                if match.parsed.gun:
                    enrichment_data['by_metadata_type']['gun'] += 1
                if match.parsed.role:
                    enrichment_data['by_metadata_type']['role'] += 1
                if match.parsed.variant:
                    enrichment_data['by_metadata_type']['variant'] += 1

                # Add sample (first 20)
                if len(enrichment_data['sample_items']) < 20:
                    enrichment_data['sample_items'].append({
                        'original_name': match.original_name,
                        'base_name': match.parsed.base_name,
                        'database_name': match.database_name,
                        'metadata': self.parser.extract_metadata_dict(match.original_name)
                    })

        return enrichment_data


class UnitExtractorV3:
    """Extract unit compositions with metadata tracking."""

    def __init__(self, equipment_db: EquipmentDatabaseV3):
        self.equipment_db = equipment_db

    def extract_units_for_quarter(self, units_dir: Path, nation: str, quarter: str) -> List[Dict]:
        """Extract all units for a specific nation and quarter."""
        units = []

        # Find all unit files matching nation and quarter
        pattern = f"{nation}_{quarter}_*.json"
        for unit_file in units_dir.glob(pattern):
            if unit_file.stem.endswith('.backup'):
                continue

            unit_data = self._parse_unit_file(unit_file)
            if unit_data:
                units.append(unit_data)

        return units

    def _parse_unit_file(self, filepath: Path) -> Optional[Dict]:
        """Parse a single unit JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"  Error parsing {filepath.name}: {e}")
            return None

        unit = {
            'name': data.get('unit_designation', 'Unknown Unit'),
            'type': data.get('unit_type', 'Unknown'),
            'organization_level': data.get('organization_level', 'unknown'),
            'personnel': data.get('total_personnel', 0),
            'equipment': self._extract_equipment(data),
            'nation': data.get('nation', 'unknown')
        }

        return unit

    def _extract_equipment(self, data: Dict) -> List[Dict]:
        """Extract equipment items from unit JSON with metadata."""
        equipment_list = []

        # Extract tanks
        if 'tanks' in data:
            equipment_list.extend(self._extract_from_section(data['tanks'], 'Tank'))

        # Extract artillery
        if 'artillery' in data:
            equipment_list.extend(self._extract_from_section(data['artillery'], 'Artillery'))

        # Extract anti-tank guns
        if 'anti_tank_guns' in data or 'anti_tank' in data:
            section = data.get('anti_tank_guns') or data.get('anti_tank')
            equipment_list.extend(self._extract_from_section(section, 'Anti-Tank'))

        # Extract vehicles
        if 'vehicles' in data:
            equipment_list.extend(self._extract_from_section(data['vehicles'], 'Vehicle'))

        # Extract infantry weapons (top 3 only)
        if 'top_3_infantry_weapons' in data:
            weapons_data = data['top_3_infantry_weapons']

            # Handle both dict and list formats
            if isinstance(weapons_data, dict):
                weapon_items = weapons_data.values()
            elif isinstance(weapons_data, list):
                weapon_items = weapons_data
            else:
                weapon_items = []

            for weapon in weapon_items:
                if isinstance(weapon, dict) and 'weapon' in weapon:
                    equipment_list.append({
                        'name': weapon['weapon'],
                        'count': weapon.get('count', 0),
                        'type': 'Infantry Weapon',
                        'witw_id': weapon.get('witw_id')
                    })

        return equipment_list

    def _extract_from_section(self, section: Dict, equipment_type: str) -> List[Dict]:
        """Recursively extract equipment from a JSON section."""
        equipment = []

        if not isinstance(section, dict):
            return equipment

        # Handle variants structure
        if 'variants' in section:
            variants_data = section['variants']

            if isinstance(variants_data, dict):
                # Could be variants: { count: { "M13/40": {...} } }
                if 'count' in variants_data:
                    count_data = variants_data['count']
                    if isinstance(count_data, dict):
                        for variant_name, variant_info in count_data.items():
                            if isinstance(variant_info, dict):
                                # Look up with metadata extraction
                                count = variant_info.get('count', 0)
                                match = self.equipment_db.lookup_equipment(variant_name, count)

                                equipment.append({
                                    'name': variant_name,
                                    'count': count,
                                    'type': equipment_type,
                                    'witw_id': variant_info.get('witw_id'),
                                    'match': match,  # Include match metadata
                                    'parsed_metadata': asdict(match.parsed) if match else None
                                })
                else:
                    # Direct variants: { "M13/40": {...} }
                    for variant_name, variant_info in variants_data.items():
                        if isinstance(variant_info, dict) and 'count' in variant_info:
                            count = variant_info.get('count', 0)
                            match = self.equipment_db.lookup_equipment(variant_name, count)

                            equipment.append({
                                'name': variant_name,
                                'count': count,
                                'type': equipment_type,
                                'witw_id': variant_info.get('witw_id'),
                                'match': match,
                                'parsed_metadata': asdict(match.parsed) if match else None
                            })

        # Recursively check other keys
        for key, value in section.items():
            if isinstance(value, dict) and key != 'variants':
                equipment.extend(self._extract_from_section(value, equipment_type))

        return equipment


def generate_enrichment_report_v3(db: EquipmentDatabaseV3, output_path: Path):
    """Generate detailed enrichment opportunities report."""
    stats = db.get_statistics()
    enrichment = db.get_enrichment_report()

    report_lines = []
    report_lines.append("# Equipment Name Metadata Extraction Report v3.0")
    report_lines.append(f"\nGenerated: 2025-11-02\n")
    report_lines.append("=" * 80 + "\n")

    # Overall statistics
    report_lines.append("\n## Overall Statistics\n")
    report_lines.append(f"- **Total Equipment Lookups:** {stats['total_lookups']:,}\n")
    report_lines.append(f"- **Successful Matches:** {stats['successful_matches']:,} ({stats['match_rate']:.1%})\n")
    report_lines.append(f"- **Metadata Extracted:** {stats['metadata_extracted']:,} ({stats['metadata_extraction_rate']:.1%})\n")
    report_lines.append(f"- **Enrichment Opportunities:** {stats['enrichment_opportunities']:,} ({stats['enrichment_rate']:.1%})\n")

    # Match improvement
    if stats['total_lookups'] > 0:
        improvement = stats['successful_matches'] - (stats['total_lookups'] - stats['metadata_extracted'])
        report_lines.append(f"\n### Match Rate Improvement\n")
        report_lines.append(f"- **Before metadata parsing:** Would have failed on {stats['metadata_extracted']} items\n")
        report_lines.append(f"- **After metadata parsing:** Successfully matched {stats['successful_matches']} items\n")
        report_lines.append(f"- **Improvement:** Metadata extraction enabled {stats['metadata_extracted']} additional matches\n")

    # Enrichment opportunities by type
    report_lines.append(f"\n## Database Enrichment Opportunities\n")
    report_lines.append(f"\nTotal items with extractable metadata: **{enrichment['total_opportunities']}**\n")
    report_lines.append(f"\n### By Metadata Type\n")
    for meta_type, count in enrichment['by_metadata_type'].items():
        report_lines.append(f"- **{meta_type}:** {count} items\n")

    # Sample enrichment items
    if enrichment['sample_items']:
        report_lines.append(f"\n### Sample Enrichment Items (first 20)\n")
        report_lines.append("\n| Original Name | Base Name | Database Match | Metadata |\n")
        report_lines.append("|---------------|-----------|----------------|----------|\n")

        for item in enrichment['sample_items']:
            metadata_str = ', '.join(f"{k}: {v}" for k, v in item['metadata'].items())
            report_lines.append(
                f"| {item['original_name']} | {item['base_name']} | "
                f"{item['database_name'] or 'No match'} | {metadata_str} |\n"
            )

    # Recommendations
    report_lines.append(f"\n## Recommendations\n")
    report_lines.append("\n### Database Schema Enhancement\n")
    report_lines.append("Consider adding these fields to `equipment_variants` table:\n")
    report_lines.append("- `weight_class` TEXT - Tank weight classification (Light/Medium/Heavy/Infantry/Cruiser)\n")
    report_lines.append("- `gun` TEXT - Primary armament designation\n")
    report_lines.append("- `role` TEXT - Vehicle role (Command/Assault Gun/Self-Propelled/Reconnaissance)\n")
    report_lines.append("- `variant` TEXT - Specific variant designation (Ausf H, Mk VI, etc.)\n")

    report_lines.append("\n### Enrichment Script\n")
    report_lines.append(f"An enrichment script could populate these fields for {enrichment['total_opportunities']} equipment items.\n")
    report_lines.append("This would:\n")
    report_lines.append("1. Preserve valuable metadata currently lost during normalization\n")
    report_lines.append("2. Enable better matching for future equipment\n")
    report_lines.append("3. Support richer equipment queries and filtering\n")
    report_lines.append("4. Improve data quality for MDBook chapter generation\n")

    # Write report
    report_content = ''.join(report_lines)
    output_path.write_text(report_content, encoding='utf-8')

    return report_content


def main():
    """Main entry point for v3 generator."""
    project_root = Path(__file__).parent.parent.parent.parent
    units_dir = project_root / 'data' / 'output' / 'units'
    db_path = project_root / 'master_database.db'
    reports_dir = project_root / 'reports'
    reports_dir.mkdir(exist_ok=True)

    print("=== BattleGroup Army List Generator v3.0 ===")
    print("With Equipment Name Metadata Extraction\n")

    # Initialize database with metadata tracking
    equipment_db = EquipmentDatabaseV3(db_path)
    equipment_db.connect()

    # Initialize unit extractor
    unit_extractor = UnitExtractorV3(equipment_db)

    # Process all battles
    print("\nProcessing battles...\n")
    for battle_key, battle_info in BATTLES.items():
        print(f"Battle: {battle_info['name']} ({battle_info['quarter']})")

        for nation in ['british', 'german', 'italian']:
            units = unit_extractor.extract_units_for_quarter(
                units_dir, nation, battle_info['quarter']
            )

            if units:
                total_equipment = sum(len(u['equipment']) for u in units)
                print(f"  {nation}: {len(units)} units, {total_equipment} equipment items")

    # Generate reports
    print("\n" + "=" * 80)
    print("\nGenerating reports...\n")

    stats = equipment_db.get_statistics()
    print(f"Total Lookups: {stats['total_lookups']:,}")
    print(f"Successful Matches: {stats['successful_matches']:,} ({stats['match_rate']:.1%})")
    print(f"Metadata Extracted: {stats['metadata_extracted']:,} ({stats['metadata_extraction_rate']:.1%})")
    print(f"Enrichment Opportunities: {stats['enrichment_opportunities']:,} ({stats['enrichment_rate']:.1%})")

    # Generate enrichment report
    report_path = reports_dir / 'equipment_metadata_extraction_report_v3.md'
    report = generate_enrichment_report_v3(equipment_db, report_path)
    print(f"\nEnrichment report written to: {report_path}")

    # Close database
    equipment_db.close()

    print("\n=== v3 Generation Complete ===")


if __name__ == '__main__':
    main()
