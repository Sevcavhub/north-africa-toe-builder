#!/usr/bin/env python3
"""
Tier 4: Artillery/Gun Linkage
Links artillery equipment to bg_reference_guns using reference_gun_id

Handles:
- Field artillery (105mm, 155mm howitzers)
- Anti-tank guns (PAK 38, 2-pounder, 6-pounder)
- Anti-aircraft guns (88mm Flak, 40mm Bofors)
- Mortars (81mm M1, 3-inch mortar)
"""

import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "database" / "master_database.db"


class GunNameNormalizer:
    """Normalize gun names for matching."""

    # Gun name patterns
    PATTERNS = {
        # Caliber + type
        r'(\d+)\s*mm': 'caliber_mm',
        r'(\d+)\s*cm': 'caliber_cm',
        r'(\d+)[-\s]?pdr': 'pounder',
        r'(\d+)[-\s]?pounder': 'pounder',

        # Gun types
        r'pak\s*\d+': 'pak',
        r'flak\s*\d+': 'flak',
        r'kwk\s*\d+': 'kwk',
        r'howitzer': 'howitzer',
        r'mortar': 'mortar',
        r'gun': 'gun',
    }

    def normalize(self, name: str) -> str:
        """Normalize gun name for matching."""
        normalized = name.lower().strip()

        # Remove common prefixes
        normalized = re.sub(r'^(german|british|american|italian|soviet)\s+', '', normalized)
        normalized = re.sub(r'^(ger|gbr|usa|ita|sov)_', '', normalized)

        # Expand abbreviations
        normalized = normalized.replace('mm.', 'mm')
        normalized = normalized.replace('cm.', 'cm')
        normalized = normalized.replace('pak ', 'pak')
        normalized = normalized.replace('flak ', 'flak')

        # Normalize spacing
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def extract_caliber(self, name: str) -> Optional[int]:
        """Extract caliber in mm from gun name."""

        # Direct mm
        match = re.search(r'(\d+)\s*mm', name, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # cm to mm
        match = re.search(r'(\d+(?:\.\d+)?)\s*cm', name, re.IGNORECASE)
        if match:
            return int(float(match.group(1)) * 10)

        # Pounder to mm (approximate)
        pounder_map = {
            2: 40,
            6: 57,
            17: 76,
            25: 88,
            32: 94,
        }
        match = re.search(r'(\d+)[-\s]?(?:pdr|pounder)', name, re.IGNORECASE)
        if match:
            pdr = int(match.group(1))
            return pounder_map.get(pdr)

        return None


class Tier4Matcher:
    """Match artillery equipment to bg_reference_guns."""

    def __init__(self, database_path: Path):
        self.conn = sqlite3.connect(database_path)
        self.conn.row_factory = sqlite3.Row
        self.normalizer = GunNameNormalizer()
        self.matches = []
        self.unmatched = []

    def load_artillery_equipment(self) -> List[Dict]:
        """Load artillery equipment needing gun linkage."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                e.canonical_id,
                e.name,
                e.nation,
                e.equipment_type,
                e.category
            FROM equipment e
            JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            WHERE eb.reference_vehicle_id IS NULL
                AND eb.reference_gun_id IS NULL
                AND (
                    e.category IN ('field_artillery', 'anti_tank', 'anti_aircraft', 'mortar')
                    OR e.equipment_type IN ('gun', 'artillery', 'mortar')
                    OR e.name LIKE '%gun%'
                    OR e.name LIKE '%howitzer%'
                    OR e.name LIKE '%mortar%'
                    OR e.name LIKE '%pak%'
                    OR e.name LIKE '%flak%'
                    OR e.name LIKE '%pounder%'
                    OR e.name LIKE '%pdr%'
                )
            ORDER BY e.nation, e.name
        """)

        return [dict(row) for row in cursor.fetchall()]

    def load_bg_reference_guns(self) -> List[Dict]:
        """Load BattleGroup reference guns."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                nation,
                caliber_mm,
                he_dice,
                ap_0_10,
                ap_10_20,
                ap_20_30,
                ap_30_40,
                ap_40_50,
                ap_50_70
            FROM bg_reference_guns
            WHERE name IS NOT NULL
            ORDER BY nation, caliber_mm, name
        """)

        return [dict(row) for row in cursor.fetchall()]

    def find_matches(self) -> List[Dict]:
        """
        Find artillery-to-gun matches.

        Strategy:
        1. Normalize both names
        2. Extract caliber from both
        3. Match on: nation + caliber + name similarity
        """
        equipment_list = self.load_artillery_equipment()
        bg_guns = self.load_bg_reference_guns()

        print(f"\nTier 4 Artillery Matching:")
        print(f"  Artillery equipment: {len(equipment_list)}")
        print(f"  BG reference guns: {len(bg_guns)}")

        # Index BG guns by nation and caliber
        bg_index = defaultdict(list)  # (nation, caliber_mm) -> [guns]

        for gun in bg_guns:
            nation = (gun['nation'] or '').lower()
            caliber = gun['caliber_mm']
            key = (nation, caliber)
            bg_index[key].append(gun)

        print(f"  BG guns indexed: {len(bg_index)} unique (nation, caliber) pairs")

        # Match equipment
        matches_found = []

        for eq in equipment_list:
            eq_normalized = self.normalizer.normalize(eq['name'])
            eq_caliber = self.normalizer.extract_caliber(eq['name'])
            eq_nation = (eq['nation'] or '').lower()

            if not eq_caliber:
                # Can't match without caliber
                self.unmatched.append({**eq, 'reason': 'no_caliber'})
                continue

            # Look for (nation, caliber) match
            match_key = (eq_nation, eq_caliber)

            if match_key in bg_index:
                candidates = bg_index[match_key]

                # If single candidate, use it
                if len(candidates) == 1:
                    gun = candidates[0]
                    matches_found.append({
                        'equipment_id': eq['canonical_id'],
                        'equipment_name': eq['name'],
                        'equipment_caliber': eq_caliber,
                        'gun_id': gun['id'],
                        'gun_name': gun['name'],
                        'gun_caliber': gun['caliber_mm'],
                        'confidence': 90,
                        'match_type': 'nation_caliber',
                        'nation': eq_nation
                    })

                # Multiple candidates - try name matching
                else:
                    best_gun = None
                    best_score = 0

                    for gun in candidates:
                        gun_normalized = self.normalizer.normalize(gun['name'])

                        # Token overlap score
                        eq_tokens = set(eq_normalized.split())
                        gun_tokens = set(gun_normalized.split())
                        overlap = len(eq_tokens & gun_tokens)
                        score = overlap

                        if score > best_score:
                            best_score = score
                            best_gun = gun

                    if best_gun and best_score > 0:
                        matches_found.append({
                            'equipment_id': eq['canonical_id'],
                            'equipment_name': eq['name'],
                            'equipment_caliber': eq_caliber,
                            'gun_id': best_gun['id'],
                            'gun_name': best_gun['name'],
                            'gun_caliber': best_gun['caliber_mm'],
                            'confidence': 85,
                            'match_type': 'nation_caliber_name',
                            'nation': eq_nation,
                            'name_score': best_score
                        })
                    else:
                        # Have caliber match but no good name match
                        self.unmatched.append({**eq, 'reason': 'ambiguous_name', 'candidates': len(candidates)})

            else:
                # No (nation, caliber) match
                self.unmatched.append({**eq, 'reason': 'no_caliber_match', 'caliber': eq_caliber})

        self.matches = matches_found

        print(f"\n  Tier 4 matches found: {len(matches_found)}")
        print(f"    Confidence 90 (single candidate): {sum(1 for m in matches_found if m['confidence'] == 90)}")
        print(f"    Confidence 85 (name scored): {sum(1 for m in matches_found if m['confidence'] == 85)}")
        print(f"  Unmatched: {len(self.unmatched)}")

        # Unmatched reasons
        reasons = defaultdict(int)
        for um in self.unmatched:
            reasons[um.get('reason', 'unknown')] += 1

        print(f"\n  Unmatched reasons:")
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"    {reason}: {count}")

        return matches_found

    def generate_sql(self, output_path: Path):
        """Generate SQL script for Tier 4 matches."""

        sql_lines = [
            "-- Tier 4: Artillery/Gun Linkage SQL Script",
            "-- Generated by tier4_artillery_linkage.py",
            "-- Links artillery to bg_reference_guns via reference_gun_id",
            "",
            "BEGIN TRANSACTION;",
            "",
        ]

        # UPDATE statements
        for i, match in enumerate(self.matches, 1):
            sql_lines.extend([
                f"-- Match {i}/{len(self.matches)}: {match['equipment_name']} → {match['gun_name']}",
                f"--   Caliber: {match['equipment_caliber']}mm",
                "UPDATE equipment_battlegroup",
                f"SET reference_gun_id = {match['gun_id']},",
                f"    reference_gun_match_confidence = {match['confidence']}",
                f"WHERE equipment_id = '{match['equipment_id']}';",
                "",
                "-- Audit log",
                "INSERT INTO normalization_audit (operation, table_name, record_id, old_value, new_value, reason, timestamp)",
                f"VALUES ('UPDATE', 'equipment_battlegroup', '{match['equipment_id']}', 'NULL', '{match['gun_id']}', 'Tier 4: {match['match_type']}', datetime('now'));",
                ""
            ])

        # Validation
        sql_lines.extend([
            "-- Validation",
            f"SELECT COUNT(*) as tier4_artillery FROM equipment_battlegroup WHERE reference_gun_id IS NOT NULL;",
            f"-- Expected: {len(self.matches)}",
            "",
            "COMMIT;",
            "",
            "-- Rollback if needed:",
            "-- ROLLBACK;",
        ])

        output_path.write_text('\n'.join(sql_lines), encoding='utf-8')
        print(f"\nSQL script generated: {output_path}")

    def generate_report(self, output_path: Path):
        """Generate Tier 4 report."""

        report_lines = [
            "# Tier 4 Artillery Linkage Report",
            "",
            f"**Matches Found**: {len(self.matches)}",
            f"**Unmatched**: {len(self.unmatched)}",
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
                "| Equipment Name | Caliber | Gun Name | Conf | Match Type |",
                "|----------------|---------|----------|------|------------|"
            ])

            for match in matches:
                report_lines.append(
                    f"| {match['equipment_name']} | {match['equipment_caliber']}mm | "
                    f"{match['gun_name']} | {match['confidence']} | {match['match_type']} |"
                )

            report_lines.append("")

        # Unmatched
        if self.unmatched:
            report_lines.extend([
                "## Unmatched Artillery",
                "",
                f"**Count**: {len(self.unmatched)}",
                "",
                "| Equipment Name | Nation | Reason |",
                "|----------------|--------|--------|"
            ])

            for um in self.unmatched[:20]:
                report_lines.append(
                    f"| {um['name']} | {um['nation']} | {um.get('reason', 'unknown')} |"
                )

            if len(self.unmatched) > 20:
                report_lines.append(f"\n*... and {len(self.unmatched) - 20} more*")

        output_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"Report generated: {output_path}")

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Run Tier 4 artillery linkage."""

    print("=" * 80)
    print("TIER 4: ARTILLERY/GUN LINKAGE")
    print("=" * 80)

    matcher = Tier4Matcher(DATABASE_PATH)

    try:
        matches = matcher.find_matches()

        # Generate SQL
        sql_path = PROJECT_ROOT / "scripts" / "linkage" / "tier4_artillery_matches.sql"
        matcher.generate_sql(sql_path)

        # Generate report
        report_path = PROJECT_ROOT / "TIER4_MATCHING_REPORT.md"
        matcher.generate_report(report_path)

        print("\n" + "=" * 80)
        print("TIER 4 ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nTotal Tier 4 matches: {len(matches)}")
        print(f"SQL script: {sql_path.relative_to(PROJECT_ROOT)}")
        print(f"Report: {report_path.relative_to(PROJECT_ROOT)}")

    finally:
        matcher.close()


if __name__ == '__main__':
    main()
