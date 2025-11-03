#!/usr/bin/env python3
"""
Tier 3: Base Model Matching
Matches equipment to bg_reference_vehicles by stripping variant suffixes

Handles:
- Variant tolerance: "Panzer III Ausf F" → base "Panzer III" → match any variant
- Model year variations: "T-34 1941" → "T-34" → match closest year
- Sub-type matching: "Sherman M4A1" → "Sherman M4" → match base model
"""

import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "database" / "master_database.db"


class BaseModelExtractor:
    """Extract base model names by removing variant suffixes."""

    # Variant suffix patterns (ordered by specificity)
    VARIANT_PATTERNS = [
        # German variants
        (r'\s+ausf\s+[a-z0-9]+', 'ausf'),  # Ausf F, Ausf H
        (r'\s+sd\.?kfz\.?\s*\d+/\d+', 'sdkfz_variant'),  # SdKfz 251/1

        # British/Commonwealth variants
        (r'\s+mk\s+[ivx0-9]+[a-z]*', 'mark'),  # Mk II, Mk IIA
        (r'\s+mark\s+[ivx0-9]+[a-z]*', 'mark'),  # Mark 2, Mark IIA

        # American variants
        (r'\s+m\d+[a-z]\d*', 'model_sub'),  # M4A1, M3A3

        # Year/date suffixes
        (r'\s+\(?\d{4}\)?', 'year'),  # (1941), 1942
        (r'\s+model\s+\d{2,4}', 'model_year'),  # Model 1941
        (r'\s+mod\.?\s*\d+', 'mod'),  # Mod 1942

        # Type suffixes
        (r'\s+type\s+[a-z0-9]+', 'type'),  # Type 97

        # Production series
        (r'\s+early|late|mid', 'series'),  # Early, Late
        (r'\s+production', 'production'),

        # Special designations
        (r'\s+command', 'command'),
        (r'\s+recovery', 'recovery'),
        (r'\s+engineer', 'engineer'),
    ]

    def __init__(self):
        self.extraction_log = []

    def extract_base(self, name: str) -> Tuple[str, List[str]]:
        """
        Extract base model name and list of removed variant suffixes.

        Returns:
            (base_name, [removed_suffixes])
        """
        original = name
        base = name.lower().strip()
        removed = []

        # Apply each pattern
        for pattern, variant_type in self.VARIANT_PATTERNS:
            match = re.search(pattern, base, re.IGNORECASE)
            if match:
                removed_text = match.group(0).strip()
                base = re.sub(pattern, '', base, flags=re.IGNORECASE).strip()
                removed.append({
                    'text': removed_text,
                    'type': variant_type
                })

        # Clean up extra whitespace
        base = re.sub(r'\s+', ' ', base).strip()

        self.extraction_log.append({
            'original': original,
            'base': base,
            'removed': removed
        })

        return base, removed

    def get_variant_distance(self, variants1: List[str], variants2: List[str]) -> int:
        """
        Calculate "distance" between two variant lists.

        Lower distance = closer match.
        Same variant types but different values = distance 1
        Different variant types = distance 2
        """
        if not variants1 and not variants2:
            return 0

        types1 = {v['type'] for v in variants1}
        types2 = {v['type'] for v in variants2}

        # If same variant types, distance = 1
        if types1 == types2:
            return 1

        # Different types = distance 2
        return 2


class Tier3Matcher:
    """Match equipment using base model extraction."""

    def __init__(self, database_path: Path):
        self.conn = sqlite3.connect(database_path)
        self.conn.row_factory = sqlite3.Row
        self.extractor = BaseModelExtractor()
        self.matches = []
        self.unmatched = []

    def load_unmatched_equipment(self) -> List[Dict]:
        """Load equipment not matched in Tier 1 or Tier 2."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                e.canonical_id,
                e.name,
                e.nation,
                e.equipment_type
            FROM equipment e
            JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            WHERE eb.reference_vehicle_id IS NULL
                AND e.equipment_type IN ('tank', 'vehicle', 'armored_car', 'halftrack')
            ORDER BY e.nation, e.name
        """)

        return [dict(row) for row in cursor.fetchall()]

    def load_bg_reference_vehicles(self) -> List[Dict]:
        """Load BattleGroup reference vehicles."""
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
        Find base model matches.

        Strategy:
        1. Extract base model for each equipment
        2. Extract base model for each bg_vehicle
        3. Match on base + nation
        4. If multiple BG matches, select by variant distance
        """
        equipment_list = self.load_unmatched_equipment()
        bg_vehicles = self.load_bg_reference_vehicles()

        print(f"\nTier 3 Matching:")
        print(f"  Equipment to match: {len(equipment_list)}")
        print(f"  BG reference vehicles: {len(bg_vehicles)}")

        # Build base model index for bg_vehicles
        bg_base_index = defaultdict(list)  # (base_name, nation) -> [bg_vehicles]

        for bg in bg_vehicles:
            base, variants = self.extractor.extract_base(bg['name'])
            nation = (bg['nation'] or '').lower()
            key = (base, nation)

            bg_base_index[key].append({
                'bg_record': bg,
                'base': base,
                'variants': variants
            })

        print(f"  BG base models indexed: {len(bg_base_index)}")

        # Match equipment
        matches_found = []

        for eq in equipment_list:
            eq_base, eq_variants = self.extractor.extract_base(eq['name'])
            eq_nation = (eq['nation'] or '').lower()

            match_key = (eq_base, eq_nation)

            if match_key in bg_base_index:
                candidates = bg_base_index[match_key]

                # If single match, use it
                if len(candidates) == 1:
                    bg_data = candidates[0]
                    bg_record = bg_data['bg_record']

                    matches_found.append({
                        'equipment_id': eq['canonical_id'],
                        'equipment_name': eq['name'],
                        'equipment_base': eq_base,
                        'bg_vehicle_id': bg_record['id'],
                        'bg_vehicle_name': bg_record['name'],
                        'bg_base': bg_data['base'],
                        'confidence': 80,
                        'match_type': 'base_model',
                        'nation': eq_nation,
                        'variant_distance': self.extractor.get_variant_distance(eq_variants, bg_data['variants'])
                    })

                # Multiple matches - select by variant distance
                else:
                    # Calculate variant distance for each candidate
                    scored_candidates = []
                    for bg_data in candidates:
                        distance = self.extractor.get_variant_distance(eq_variants, bg_data['variants'])
                        scored_candidates.append((distance, bg_data))

                    # Sort by distance (lower = better)
                    scored_candidates.sort(key=lambda x: x[0])

                    # Use closest match
                    best_distance, best_bg_data = scored_candidates[0]
                    bg_record = best_bg_data['bg_record']

                    # Lower confidence if distance > 0
                    confidence = 80 if best_distance == 0 else 75

                    matches_found.append({
                        'equipment_id': eq['canonical_id'],
                        'equipment_name': eq['name'],
                        'equipment_base': eq_base,
                        'bg_vehicle_id': bg_record['id'],
                        'bg_vehicle_name': bg_record['name'],
                        'bg_base': best_bg_data['base'],
                        'confidence': confidence,
                        'match_type': 'base_model_variants',
                        'nation': eq_nation,
                        'variant_distance': best_distance,
                        'candidate_count': len(candidates)
                    })

            else:
                # No base model match
                self.unmatched.append(eq)

        self.matches = matches_found

        print(f"\n  Tier 3 matches found: {len(matches_found)}")
        print(f"    Confidence 80 (exact base): {sum(1 for m in matches_found if m['confidence'] == 80)}")
        print(f"    Confidence 75 (variant diff): {sum(1 for m in matches_found if m['confidence'] == 75)}")
        print(f"  Still unmatched: {len(self.unmatched)}")

        return matches_found

    def generate_sql(self, output_path: Path):
        """Generate SQL script to apply Tier 3 matches."""

        sql_lines = [
            "-- Tier 3: Base Model Matches SQL Script",
            "-- Generated by tier3_base_model.py",
            "-- Applies base model matching (variant tolerance)",
            "",
            "BEGIN TRANSACTION;",
            "",
        ]

        # Generate UPDATE statements
        for i, match in enumerate(self.matches, 1):
            sql_lines.extend([
                f"-- Match {i}/{len(self.matches)}: {match['equipment_name']} → {match['bg_vehicle_name']}",
                f"--   Base model: {match['equipment_base']} (distance: {match['variant_distance']})",
                "UPDATE equipment_battlegroup",
                f"SET reference_vehicle_id = {match['bg_vehicle_id']},",
                f"    reference_match_confidence = {match['confidence']}",
                f"WHERE equipment_id = '{match['equipment_id']}';",
                "",
                "-- Log to audit",
                "INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)",
                f"VALUES ('UPDATE', 'equipment_battlegroup', '{match['equipment_id']}', 'NULL', '{match['bg_vehicle_id']}', 'Tier 3: {match['match_type']} (dist={match['variant_distance']})', datetime('now'));",
                ""
            ])

        # Validation
        sql_lines.extend([
            "-- Validation",
            f"SELECT COUNT(*) as tier3_conf80 FROM equipment_battlegroup WHERE reference_match_confidence = 80;",
            f"-- Expected: {sum(1 for m in self.matches if m['confidence'] == 80)}",
            "",
            f"SELECT COUNT(*) as tier3_conf75 FROM equipment_battlegroup WHERE reference_match_confidence = 75;",
            f"-- Expected: {sum(1 for m in self.matches if m['confidence'] == 75)}",
            "",
            "COMMIT;",
            "",
            "-- Rollback if needed:",
            "-- ROLLBACK;",
        ])

        output_path.write_text('\n'.join(sql_lines), encoding='utf-8')
        print(f"\nSQL script generated: {output_path}")

    def generate_report(self, output_path: Path):
        """Generate Tier 3 matching report."""

        report_lines = [
            "# Tier 3 Base Model Matching Report",
            "",
            f"**Matches Found**: {len(self.matches)}",
            f"**Still Unmatched**: {len(self.unmatched)}",
            "",
            "## Strategy",
            "",
            "Tier 3 strips variant suffixes to match base models:",
            "- Example: 'Panzer III Ausf F' → base 'panzer iii' → matches 'Panzer III J'",
            "- Confidence 80: Exact base model match",
            "- Confidence 75: Base model match but different variant types",
            "",
            "## Matches by Nation",
            ""
        ]

        # Group by nation
        by_nation = defaultdict(list)
        for match in self.matches:
            by_nation[match['nation']].append(match)

        for nation in sorted(by_nation.keys()):
            matches = by_nation[nation]
            report_lines.extend([
                f"### {nation.capitalize()}",
                "",
                f"**Count**: {len(matches)}",
                "",
                "| Equipment Name | Base | BG Vehicle | BG Base | Conf | Var Dist |",
                "|----------------|------|------------|---------|------|----------|"
            ])

            for match in matches:
                report_lines.append(
                    f"| {match['equipment_name']} | {match['equipment_base']} | "
                    f"{match['bg_vehicle_name']} | {match['bg_base']} | "
                    f"{match['confidence']} | {match['variant_distance']} |"
                )

            report_lines.append("")

        # Still unmatched
        if self.unmatched:
            report_lines.extend([
                "## Still Unmatched After Tier 3",
                "",
                f"**Count**: {len(self.unmatched)}",
                "",
                "These require manual review or are unmatchable (aircraft, support vehicles, etc.).",
                "",
                "| Canonical ID | Name | Nation | Type |",
                "|--------------|------|--------|------|"
            ])

            for eq in self.unmatched[:30]:
                report_lines.append(
                    f"| {eq['canonical_id']} | {eq['name']} | {eq['nation']} | {eq['equipment_type']} |"
                )

            if len(self.unmatched) > 30:
                report_lines.append(f"\n*... and {len(self.unmatched) - 30} more*")

        output_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"Report generated: {output_path}")

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Run Tier 3 base model matching."""

    print("=" * 80)
    print("TIER 3: BASE MODEL MATCHING")
    print("=" * 80)

    matcher = Tier3Matcher(DATABASE_PATH)

    try:
        # Find matches
        matches = matcher.find_matches()

        # Generate SQL script
        sql_path = PROJECT_ROOT / "scripts" / "linkage" / "tier3_base_model_matches.sql"
        matcher.generate_sql(sql_path)

        # Generate report
        report_path = PROJECT_ROOT / "TIER3_MATCHING_REPORT.md"
        matcher.generate_report(report_path)

        print("\n" + "=" * 80)
        print("TIER 3 ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nTotal Tier 3 matches: {len(matches)}")
        print(f"SQL script: {sql_path.relative_to(PROJECT_ROOT)}")
        print(f"Report: {report_path.relative_to(PROJECT_ROOT)}")

    finally:
        matcher.close()


if __name__ == '__main__':
    main()
