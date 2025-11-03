#!/usr/bin/env python3
"""
Tier 2: Normalization-Based Equipment Linkage
Populates equipment_battlegroup.reference_vehicle_id using name normalization

Handles:
- Punctuation variations (Pz.Kpfw. vs Panzer)
- Spacing issues (multiple spaces, leading/trailing)
- Reverse order (Sherman M4 vs M4 Sherman)
- Roman numerals (Mk1 vs Mk I)
- Abbreviation expansion (Ausf. vs Ausf)
"""

import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "database" / "master_database.db"


class NameNormalizer:
    """Normalize equipment names for fuzzy matching."""

    # Abbreviation expansion dictionary
    ABBREVIATIONS = {
        'pz.kpfw.': 'panzer',
        'pz.kpfw': 'panzer',
        'pzkpfw': 'panzer',
        'pz': 'panzer',
        'ausf.': 'ausf',
        'mk.': 'mk',
        'pdr': 'pounder',
        'cm': 'mm',  # 8.8cm -> 88mm
        'sdkfz.': 'sdkfz',
        'qf': '',  # Quick Firing - remove
        'ord.': 'ordnance',
    }

    # Roman numeral to Arabic
    ROMAN_TO_ARABIC = {
        'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5',
        'vi': '6', 'vii': '7', 'viii': '8', 'ix': '9', 'x': '10'
    }

    def __init__(self):
        self.normalization_log = []

    def normalize(self, name: str) -> str:
        """
        Apply all normalization rules to a name.

        Steps:
        1. Lowercase
        2. Remove punctuation
        3. Normalize spacing
        4. Expand abbreviations
        5. Convert roman numerals
        6. Strip common prefixes/suffixes
        """
        if not name:
            return ""

        original = name

        # 1. Lowercase
        name = name.lower()

        # 2. Expand abbreviations (before removing punctuation)
        for abbr, expansion in self.ABBREVIATIONS.items():
            name = name.replace(abbr, expansion)

        # 3. Remove punctuation (keep hyphens and spaces)
        name = re.sub(r'[^\w\s-]', ' ', name)

        # 4. Normalize spacing (multiple spaces -> single)
        name = re.sub(r'\s+', ' ', name).strip()

        # 5. Convert roman numerals (whole words only)
        tokens = name.split()
        converted_tokens = []
        for token in tokens:
            if token in self.ROMAN_TO_ARABIC:
                converted_tokens.append(self.ROMAN_TO_ARABIC[token])
            else:
                converted_tokens.append(token)
        name = ' '.join(converted_tokens)

        # 6. Normalize caliber formats (88mm = 8.8cm)
        name = self.normalize_caliber(name)

        self.normalization_log.append({
            'original': original,
            'normalized': name
        })

        return name

    def normalize_caliber(self, name: str) -> str:
        """Normalize caliber formats (8.8cm -> 88mm, 2pdr -> 40mm)."""
        # Convert cm to mm (8.8cm -> 88mm)
        name = re.sub(r'(\d+)\.(\d+)\s*cm', lambda m: f"{int(float(m.group(1) + '.' + m.group(2)) * 10)}mm", name)
        name = re.sub(r'(\d+)\s*cm', lambda m: f"{int(m.group(1)) * 10}mm", name)

        # Pounder to mm conversions (common British guns)
        pounder_to_mm = {
            '2': '40',
            '6': '57',
            '17': '76',
            '25': '88'  # 25-pdr is actually 87.6mm
        }
        for pdr, mm in pounder_to_mm.items():
            name = re.sub(rf'{pdr}\s*pounder', f'{mm}mm', name)

        return name

    def reverse_order_match(self, name1: str, name2: str) -> bool:
        """
        Check if names match when word order is reversed.

        Example: "Sherman M4" vs "M4 Sherman"
        """
        tokens1 = set(name1.split())
        tokens2 = set(name2.split())

        # If all tokens match (ignoring order), it's a reverse match
        return len(tokens1) > 1 and tokens1 == tokens2

    def extract_base_model(self, name: str) -> str:
        """
        Extract base model name by removing variant suffixes.

        Example: "Panzer III Ausf F" -> "Panzer III"
        """
        # Remove common variant patterns
        variant_patterns = [
            r'\s+ausf\s+[a-z0-9]+',  # Ausf F, Ausf H
            r'\s+mk\s+[0-9ivx]+',     # Mk II, Mk 2
            r'\s+model\s+[0-9]+',     # Model 1941
            r'\s+mod\s+[0-9]+',       # Mod 1942
            r'\s+type\s+[0-9]+',      # Type 97
            r'\s+m[0-9]+[a-z]*$',     # M4A1, M3 (at end)
        ]

        base = name
        for pattern in variant_patterns:
            base = re.sub(pattern, '', base, flags=re.IGNORECASE)

        return base.strip()


class Tier2Matcher:
    """Match equipment to bg_reference_vehicles using normalization."""

    def __init__(self, database_path: Path):
        self.conn = sqlite3.connect(database_path)
        self.conn.row_factory = sqlite3.Row
        self.normalizer = NameNormalizer()
        self.matches = []
        self.unmatched = []

    def load_equipment(self) -> List[Dict]:
        """Load equipment needing links (Tier 1 not yet matched)."""
        cursor = self.conn.cursor()

        # Get equipment not matched in Tier 1
        cursor.execute("""
            SELECT
                e.canonical_id,
                e.name,
                e.nation,
                eb.reference_vehicle_id
            FROM equipment e
            JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            WHERE eb.reference_vehicle_id IS NULL
                AND e.equipment_type IN ('tank', 'vehicle', 'armored_car', 'halftrack')
            ORDER BY e.nation, e.name
        """)

        return [dict(row) for row in cursor.fetchall()]

    def load_bg_reference_vehicles(self) -> List[Dict]:
        """Load BattleGroup reference vehicles with known nations."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                nation,
                vehicle_type,
                weapons
            FROM bg_reference_vehicles
            WHERE nation IS NOT NULL
                AND nation != 'Unknown'
                AND nation != ''
            ORDER BY nation, name
        """)

        return [dict(row) for row in cursor.fetchall()]

    def find_matches(self) -> List[Dict]:
        """
        Find normalized matches between equipment and bg_reference.

        Returns list of matches with confidence scores.
        """
        equipment_list = self.load_equipment()
        bg_vehicles = self.load_bg_reference_vehicles()

        print(f"\nTier 2 Matching:")
        print(f"  Equipment to match: {len(equipment_list)}")
        print(f"  BG reference vehicles: {len(bg_vehicles)}")

        # Build normalized lookup for bg_vehicles
        bg_normalized = {}
        for bg in bg_vehicles:
            normalized_name = self.normalizer.normalize(bg['name'])
            nation = (bg['nation'] or '').lower()
            key = (normalized_name, nation)

            if key not in bg_normalized:
                bg_normalized[key] = []
            bg_normalized[key].append(bg)

        print(f"  BG vehicles indexed: {len(bg_normalized)}")

        # Match equipment
        matches_found = []

        for eq in equipment_list:
            eq_normalized = self.normalizer.normalize(eq['name'])
            eq_nation = (eq['nation'] or '').lower()

            match_key = (eq_normalized, eq_nation)

            # Strategy 1: Direct normalized match
            if match_key in bg_normalized:
                bg_matches = bg_normalized[match_key]

                # If multiple matches, use first (or could apply additional logic)
                bg_match = bg_matches[0]

                matches_found.append({
                    'equipment_id': eq['canonical_id'],
                    'equipment_name': eq['name'],
                    'bg_vehicle_id': bg_match['id'],
                    'bg_vehicle_name': bg_match['name'],
                    'confidence': 90,
                    'match_type': 'normalized',
                    'nation': eq_nation
                })
                continue

            # Strategy 2: Reverse order match
            reverse_matched = False
            for (bg_norm, bg_nation), bg_list in bg_normalized.items():
                if bg_nation == eq_nation:
                    if self.normalizer.reverse_order_match(eq_normalized, bg_norm):
                        bg_match = bg_list[0]
                        matches_found.append({
                            'equipment_id': eq['canonical_id'],
                            'equipment_name': eq['name'],
                            'bg_vehicle_id': bg_match['id'],
                            'bg_vehicle_name': bg_match['name'],
                            'confidence': 85,
                            'match_type': 'reverse_order',
                            'nation': eq_nation
                        })
                        reverse_matched = True
                        break

            if reverse_matched:
                continue

            # Not matched in Tier 2
            self.unmatched.append(eq)

        self.matches = matches_found

        print(f"\n  Tier 2 matches found: {len(matches_found)}")
        print(f"  Still unmatched: {len(self.unmatched)}")

        return matches_found

    def generate_sql(self, output_path: Path):
        """Generate SQL script to apply Tier 2 matches."""

        sql_lines = [
            "-- Tier 2: Normalized Matches SQL Script",
            "-- Generated by tier2_normalization.py",
            "-- Applies normalization-based equipment linkage",
            "",
            "BEGIN TRANSACTION;",
            "",
            "-- Validate starting state",
            "SELECT COUNT(*) as tier2_candidates FROM equipment_battlegroup WHERE reference_vehicle_id IS NULL;",
            "",
        ]

        # Generate UPDATE statements
        for i, match in enumerate(self.matches, 1):
            sql_lines.extend([
                f"-- Match {i}/{len(self.matches)}: {match['equipment_name']} → {match['bg_vehicle_name']}",
                "UPDATE equipment_battlegroup",
                f"SET reference_vehicle_id = {match['bg_vehicle_id']},",
                f"    reference_match_confidence = {match['confidence']}",
                f"WHERE equipment_id = '{match['equipment_id']}';",
                "",
                "-- Log to audit",
                "INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)",
                f"VALUES ('UPDATE', 'equipment_battlegroup', '{match['equipment_id']}', 'NULL', '{match['bg_vehicle_id']}', 'Tier 2: {match['match_type']}', datetime('now'));",
                ""
            ])

        # Validation
        sql_lines.extend([
            "-- Validation: Check matches applied",
            f"SELECT COUNT(*) as tier2_applied FROM equipment_battlegroup WHERE reference_match_confidence = 90;",
            f"-- Expected: {sum(1 for m in self.matches if m['confidence'] == 90)}",
            "",
            f"SELECT COUNT(*) as tier2_reverse FROM equipment_battlegroup WHERE reference_match_confidence = 85;",
            f"-- Expected: {sum(1 for m in self.matches if m['confidence'] == 85)}",
            "",
            "-- If validation passes:",
            "COMMIT;",
            "",
            "-- If validation fails, rollback:",
            "-- ROLLBACK;",
        ])

        output_path.write_text('\n'.join(sql_lines), encoding='utf-8')
        print(f"\nSQL script generated: {output_path}")

    def generate_report(self, output_path: Path):
        """Generate Tier 2 matching report."""

        report_lines = [
            "# Tier 2 Normalization Matching Report",
            "",
            f"**Generated**: {Path(__file__).name}",
            f"**Matches Found**: {len(self.matches)}",
            f"**Still Unmatched**: {len(self.unmatched)}",
            "",
            "## Matches by Nation",
            ""
        ]

        # Group by nation
        by_nation = {}
        for match in self.matches:
            nation = match['nation']
            if nation not in by_nation:
                by_nation[nation] = []
            by_nation[nation].append(match)

        for nation, matches in sorted(by_nation.items()):
            report_lines.extend([
                f"### {nation.capitalize()}",
                "",
                f"**Count**: {len(matches)}",
                "",
                "| Equipment Name | BG Vehicle Name | Confidence | Match Type |",
                "|----------------|-----------------|------------|------------|"
            ])

            for match in matches:
                report_lines.append(
                    f"| {match['equipment_name']} | {match['bg_vehicle_name']} | {match['confidence']} | {match['match_type']} |"
                )

            report_lines.append("")

        # Unmatched section
        if self.unmatched:
            report_lines.extend([
                "## Still Unmatched After Tier 2",
                "",
                f"**Count**: {len(self.unmatched)}",
                "",
                "These will be candidates for Tier 3 (base model matching).",
                "",
                "| Canonical ID | Name | Nation |",
                "|--------------|------|--------|"
            ])

            for eq in self.unmatched[:20]:  # Show first 20
                report_lines.append(
                    f"| {eq['canonical_id']} | {eq['name']} | {eq['nation']} |"
                )

            if len(self.unmatched) > 20:
                report_lines.append(f"\n*... and {len(self.unmatched) - 20} more*")

        output_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"Report generated: {output_path}")

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Run Tier 2 normalization matching."""

    print("=" * 80)
    print("TIER 2: NORMALIZATION-BASED EQUIPMENT LINKAGE")
    print("=" * 80)

    matcher = Tier2Matcher(DATABASE_PATH)

    try:
        # Find matches
        matches = matcher.find_matches()

        # Generate SQL script
        sql_path = PROJECT_ROOT / "scripts" / "linkage" / "tier2_normalized_matches.sql"
        matcher.generate_sql(sql_path)

        # Generate report
        report_path = PROJECT_ROOT / "TIER2_MATCHING_REPORT.md"
        matcher.generate_report(report_path)

        print("\n" + "=" * 80)
        print("TIER 2 ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nTotal Tier 2 matches: {len(matches)}")
        print(f"SQL script: {sql_path.relative_to(PROJECT_ROOT)}")
        print(f"Report: {report_path.relative_to(PROJECT_ROOT)}")
        print("\nReview the report, then execute the SQL script to apply matches.")

    finally:
        matcher.close()


if __name__ == '__main__':
    main()
