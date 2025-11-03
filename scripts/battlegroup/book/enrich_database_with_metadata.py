#!/usr/bin/env python3
"""
Database Enrichment Script - Add Equipment Metadata Fields.

This script:
1. Analyzes equipment_variants table schema
2. Adds metadata fields if needed (weight_class, gun, role, variant)
3. Scans Phase 6 unit JSONs for equipment names
4. Extracts metadata using EquipmentNameParser
5. Updates database records where metadata can be enriched
6. Generates audit trail and enrichment report

IMPORTANT: This script makes schema and data changes to master_database.db
Run with --dry-run flag first to preview changes.

Author: Claude Code (Sonnet 4.5)
Date: 2025-11-02
"""

import json
import sqlite3
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Import parser
sys.path.insert(0, str(Path(__file__).parent))
from equipment_name_parser import EquipmentNameParser


class DatabaseEnricher:
    """Enriches database with metadata from Phase 6 equipment names."""

    def __init__(self, db_path: Path, dry_run: bool = True):
        self.db_path = db_path
        self.dry_run = dry_run
        self.parser = EquipmentNameParser()
        self.conn = None

        # Statistics
        self.stats = {
            'equipment_scanned': 0,
            'metadata_extracted': 0,
            'records_updated': 0,
            'new_fields_added': 0,
            'errors': []
        }

        # Enrichment log
        self.enrichment_log = []

    def connect(self):
        """Connect to database."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        print(f"Connected to database: {self.db_path.name}")

    def close(self):
        """Close database connection."""
        if self.conn:
            if not self.dry_run:
                self.conn.commit()
            self.conn.close()

    def check_schema(self) -> Dict[str, bool]:
        """Check which metadata fields exist in equipment_variants table."""
        cursor = self.conn.cursor()

        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='equipment_variants'
        """)

        if not cursor.fetchone():
            print("WARNING: equipment_variants table does not exist!")
            print("This script requires the equipment_variants table from Phase 5.")
            return {}

        # Get current schema
        cursor.execute("PRAGMA table_info(equipment_variants)")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}

        print("\nCurrent equipment_variants schema:")
        for col, col_type in columns.items():
            print(f"  {col}: {col_type}")

        # Check for metadata fields
        metadata_fields = {
            'weight_class': 'weight_class' in columns,
            'gun': 'gun' in columns,
            'role': 'role' in columns,
            'variant': 'variant' in columns
        }

        print("\nMetadata fields status:")
        for field, exists in metadata_fields.items():
            status = "EXISTS" if exists else "MISSING"
            print(f"  {field}: {status}")

        return metadata_fields

    def add_metadata_fields(self, existing_fields: Dict[str, bool]):
        """Add missing metadata fields to equipment_variants table."""
        cursor = self.conn.cursor()

        fields_to_add = [
            ('weight_class', 'TEXT'),
            ('gun', 'TEXT'),
            ('role', 'TEXT'),
            ('variant', 'TEXT')
        ]

        for field_name, field_type in fields_to_add:
            if not existing_fields.get(field_name, False):
                sql = f"ALTER TABLE equipment_variants ADD COLUMN {field_name} {field_type}"

                if self.dry_run:
                    print(f"[DRY-RUN] Would execute: {sql}")
                else:
                    print(f"Adding field: {field_name} {field_type}")
                    cursor.execute(sql)
                    self.stats['new_fields_added'] += 1

    def collect_equipment_from_phase6(self, units_dir: Path) -> Dict[str, set]:
        """Collect all equipment names from Phase 6 unit JSONs."""
        equipment_by_category = defaultdict(set)

        for json_file in units_dir.glob('*.json'):
            if json_file.stem.endswith('.backup'):
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                continue

            # Extract from various sections
            for section_key in ['tanks', 'artillery', 'anti_tank', 'anti_tank_guns', 'armored_vehicles', 'armored_cars']:
                if section_key in data:
                    names = self._extract_names_from_section(data[section_key])
                    equipment_by_category[section_key].update(names)

        return equipment_by_category

    def _extract_names_from_section(self, section: dict) -> set:
        """Recursively extract equipment names."""
        names = set()

        if not isinstance(section, dict):
            return names

        if 'variants' in section:
            variants = section['variants']
            if isinstance(variants, dict):
                if 'count' in variants:
                    count_data = variants['count']
                    if isinstance(count_data, dict):
                        names.update(count_data.keys())
                else:
                    names.update(variants.keys())

        for value in section.values():
            if isinstance(value, dict):
                names.update(self._extract_names_from_section(value))

        return names

    def enrich_equipment_records(self, equipment_names: set):
        """Enrich database records with extracted metadata."""
        cursor = self.conn.cursor()

        for name in equipment_names:
            self.stats['equipment_scanned'] += 1

            # Parse metadata
            parsed = self.parser.parse(name)

            # Check if any metadata was extracted
            has_metadata = any([
                parsed.weight_class,
                parsed.gun,
                parsed.role,
                parsed.variant
            ])

            if not has_metadata:
                continue

            self.stats['metadata_extracted'] += 1

            # Try to find matching database record
            match_key = self.parser.get_database_match_key(name)

            # Search for matching record
            cursor.execute("""
                SELECT id, variant_name, witw_id
                FROM equipment_variants
                WHERE LOWER(REPLACE(REPLACE(variant_name, '.', ''), ' ', '')) = ?
                LIMIT 1
            """, (match_key.replace(' ', ''),))

            row = cursor.fetchone()

            if row:
                # Found matching record - enrich it
                updates = []
                values = []

                if parsed.weight_class:
                    updates.append("weight_class = ?")
                    values.append(parsed.weight_class)

                if parsed.gun:
                    updates.append("gun = ?")
                    values.append(parsed.gun)

                if parsed.role:
                    updates.append("role = ?")
                    values.append(parsed.role)

                if parsed.variant:
                    updates.append("variant = ?")
                    values.append(parsed.variant)

                if updates:
                    values.append(row['id'])  # WHERE id = ?

                    sql = f"""
                        UPDATE equipment_variants
                        SET {', '.join(updates)}
                        WHERE id = ?
                    """

                    if self.dry_run:
                        print(f"[DRY-RUN] Would update: {row['variant_name']}")
                        print(f"  Metadata: {self.parser.extract_metadata_dict(name)}")
                    else:
                        cursor.execute(sql, values)
                        self.stats['records_updated'] += 1

                    # Log enrichment
                    self.enrichment_log.append({
                        'equipment_name': name,
                        'database_record': row['variant_name'],
                        'witw_id': row['witw_id'],
                        'metadata': self.parser.extract_metadata_dict(name)
                    })

    def generate_report(self, output_path: Path):
        """Generate enrichment report."""
        report_lines = []
        report_lines.append("# Database Enrichment Report\n")
        report_lines.append(f"\nGenerated: 2025-11-02\n")
        report_lines.append(f"Mode: {'DRY-RUN (no changes made)' if self.dry_run else 'LIVE (database updated)'}\n")
        report_lines.append("=" * 80 + "\n")

        # Statistics
        report_lines.append("\n## Statistics\n")
        report_lines.append(f"- **Equipment Names Scanned:** {self.stats['equipment_scanned']:,}\n")
        report_lines.append(f"- **Metadata Extracted:** {self.stats['metadata_extracted']:,}\n")
        report_lines.append(f"- **Database Records Updated:** {self.stats['records_updated']:,}\n")
        report_lines.append(f"- **New Fields Added:** {self.stats['new_fields_added']}\n")

        if self.stats['errors']:
            report_lines.append(f"- **Errors:** {len(self.stats['errors'])}\n")

        # Enrichment log
        if self.enrichment_log:
            report_lines.append(f"\n## Enrichment Log ({len(self.enrichment_log)} records)\n")

            # Group by metadata type
            by_metadata_type = defaultdict(list)
            for entry in self.enrichment_log:
                for meta_type in entry['metadata'].keys():
                    by_metadata_type[meta_type].append(entry)

            for meta_type, entries in by_metadata_type.items():
                report_lines.append(f"\n### {meta_type.replace('_', ' ').title()} ({len(entries)} records)\n")

                for entry in entries[:20]:  # First 20
                    report_lines.append(
                        f"- `{entry['equipment_name']}` → `{entry['database_record']}` "
                        f"(WITW: {entry['witw_id']}) - {meta_type}: {entry['metadata'][meta_type]}\n"
                    )

        # Errors
        if self.stats['errors']:
            report_lines.append("\n## Errors\n")
            for error in self.stats['errors'][:50]:  # First 50
                report_lines.append(f"- {error}\n")

        # Recommendations
        report_lines.append("\n## Next Steps\n")
        if self.dry_run:
            report_lines.append("\nThis was a DRY-RUN. To apply changes:\n")
            report_lines.append("```bash\n")
            report_lines.append("python enrich_database_with_metadata.py --apply\n")
            report_lines.append("```\n")
        else:
            report_lines.append("\nDatabase has been enriched with metadata.\n")
            report_lines.append(f"- {self.stats['records_updated']} equipment records updated\n")
            report_lines.append(f"- {self.stats['new_fields_added']} new fields added to schema\n")

        # Write report
        report_content = ''.join(report_lines)
        output_path.write_text(report_content, encoding='utf-8')

        return report_content


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Enrich database with equipment metadata')
    parser.add_argument('--apply', action='store_true',
                        help='Apply changes to database (default is dry-run)')
    parser.add_argument('--db', type=str, default='master_database.db',
                        help='Database file path')
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent.parent
    db_path = project_root / args.db
    units_dir = project_root / 'data' / 'output' / 'units'
    reports_dir = project_root / 'reports'
    reports_dir.mkdir(exist_ok=True)

    dry_run = not args.apply

    print("=" * 80)
    print("Database Enrichment Script v1.0")
    print("=" * 80)
    print(f"Mode: {'DRY-RUN (preview only)' if dry_run else 'LIVE (will modify database)'}")
    print(f"Database: {db_path}")
    print("=" * 80)

    if not dry_run:
        confirm = input("\nWARNING: This will modify the database. Continue? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("Aborted.")
            return

    # Initialize enricher
    enricher = DatabaseEnricher(db_path, dry_run=dry_run)
    enricher.connect()

    # Check schema
    print("\n" + "=" * 80)
    print("Step 1: Check Schema")
    print("=" * 80)
    existing_fields = enricher.check_schema()

    if not existing_fields:
        print("\nERROR: Cannot proceed without equipment_variants table")
        print("Please run Phase 5 equipment matching first")
        return

    # Add missing fields
    print("\n" + "=" * 80)
    print("Step 2: Add Metadata Fields (if needed)")
    print("=" * 80)
    enricher.add_metadata_fields(existing_fields)

    # Collect Phase 6 equipment
    print("\n" + "=" * 80)
    print("Step 3: Collect Phase 6 Equipment Names")
    print("=" * 80)
    equipment_by_category = enricher.collect_equipment_from_phase6(units_dir)

    total_equipment = sum(len(names) for names in equipment_by_category.values())
    print(f"\nFound {total_equipment} unique equipment names:")
    for category, names in equipment_by_category.items():
        print(f"  {category}: {len(names)} items")

    # Enrich database
    print("\n" + "=" * 80)
    print("Step 4: Enrich Database Records")
    print("=" * 80)

    all_equipment = set()
    for names in equipment_by_category.values():
        all_equipment.update(names)

    enricher.enrich_equipment_records(all_equipment)

    # Generate report
    print("\n" + "=" * 80)
    print("Step 5: Generate Report")
    print("=" * 80)

    report_filename = 'database_enrichment_report_dry_run.md' if dry_run else 'database_enrichment_report_applied.md'
    report_path = reports_dir / report_filename

    enricher.generate_report(report_path)

    print(f"\nReport written to: {report_path}")
    print(f"\nScanned: {enricher.stats['equipment_scanned']} equipment names")
    print(f"Extracted metadata: {enricher.stats['metadata_extracted']}")
    print(f"Records updated: {enricher.stats['records_updated']}")

    # Close database
    enricher.close()

    print("\n" + "=" * 80)
    print("Enrichment Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()
