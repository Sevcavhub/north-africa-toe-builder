#!/usr/bin/env python3
"""
Phase 9B Step 4: Equipment Enrichment Pipeline
Generates BattleGroup stats for all 469 equipment items using Steps 2-3 conversion tools.

Process:
1. Query all equipment from equipment table
2. For each item:
   - Convert armor thickness to BattleGroup letters
   - Calculate movement values
   - Calculate HE effectiveness
   - Convert penetration values
   - Calculate points cost (all experience levels)
   - Assign battle rating (all experience levels)
3. Insert into equipment_battlegroup table

Usage:
    python enrich_equipment_battlegroup.py                    # Enrich all 469 items
    python enrich_equipment_battlegroup.py --nation german    # German equipment only
    python enrich_equipment_battlegroup.py --limit 10         # First 10 items (testing)
    python enrich_equipment_battlegroup.py --validate         # Show stats after enrichment
"""

import sqlite3
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Import conversion tools from Steps 2-3
from scripts.battlegroup.conversion.armor_converter import convert_armor
from scripts.battlegroup.conversion.movement_calculator import calculate_movement
from scripts.battlegroup.conversion.he_calculator import calculate_he_effect
from scripts.battlegroup.conversion.penetration_converter import convert_penetration
from scripts.battlegroup.points.points_calculator import PointsCalculator
from scripts.battlegroup.points.battle_rating_assigner import BattleRatingAssigner

DATABASE_PATH = project_root / "database" / "master_database.db"


def safe_print(text):
    """Safely print text, handling unicode encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic characters with ASCII equivalents
        print(text.encode('ascii', 'replace').decode('ascii'))


@dataclass
class EnrichmentResult:
    """Result of enriching a single equipment item."""
    equipment_id: str
    success: bool
    confidence_score: int  # 0-100
    generation_method: str
    error_message: Optional[str] = None


class EquipmentEnricher:
    """
    Enrich equipment database with BattleGroup stats.

    Uses Step 2 conversion tools (armor, movement, HE, penetration)
    and Step 3 points/BR calculators.
    """

    def __init__(self):
        """Initialize enricher with database and calculators."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.points_calc = PointsCalculator()
        self.br_assigner = BattleRatingAssigner()

        # Track stats
        self.stats = {
            'total': 0,
            'enriched': 0,
            'failed': 0,
            'high_confidence': 0,  # 80-100%
            'medium_confidence': 0,  # 60-79%
            'low_confidence': 0,  # 0-59%
        }

    def get_equipment_list(
        self,
        nation: Optional[str] = None,
        equipment_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get list of equipment to enrich."""

        cursor = self.conn.cursor()

        # Build query
        query = "SELECT * FROM equipment WHERE 1=1"
        params = []

        if nation:
            query += " AND nation = ?"
            params.append(nation)

        if equipment_type:
            query += " AND equipment_type = ?"
            params.append(equipment_type)

        query += " ORDER BY nation, equipment_type, name"

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]

        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def enrich_equipment(self, equipment: Dict) -> EnrichmentResult:
        """
        Enrich a single equipment item with BattleGroup stats.

        Args:
            equipment: Equipment dict from database

        Returns:
            EnrichmentResult with success status and confidence
        """

        equipment_id = equipment['canonical_id']
        name = equipment['name']

        safe_print(f"\nEnriching: {name} ({equipment_id})")

        try:
            # ========================================
            # STEP 1: Armor Conversion
            # ========================================
            armor_result = convert_armor(
                front_mm=equipment.get('armor_front_mm'),
                side_mm=equipment.get('armor_side_mm'),
                rear_mm=equipment.get('armor_rear_mm'),
                vehicle_name=name
            )

            armor_front = armor_result.get('front', 'Soft-Skinned')
            armor_side = armor_result.get('side', 'Soft-Skinned')
            armor_rear = armor_result.get('rear', 'Soft-Skinned')
            armor_confidence = armor_result.get('confidence', 'low')

            # Turret armor (if applicable)
            armor_turret_front = None
            armor_turret_side = None
            armor_turret_rear = None

            if equipment.get('turret_front_mm'):
                turret_result = convert_armor(front_mm=equipment['turret_front_mm'])
                armor_turret_front = turret_result.get('front')
                armor_turret_side = turret_result.get('side')
                armor_turret_rear = turret_result.get('rear')

            safe_print(f"  Armor: {armor_front}/{armor_side}/{armor_rear} ({armor_confidence})")

            # ========================================
            # STEP 2: Movement Calculation
            # ========================================
            movement_result = calculate_movement(
                vehicle_name=name,
                vehicle_type=equipment.get('equipment_type'),
                weight_tonnes=equipment.get('weight_tonnes')
            )

            off_road = movement_result.get('off_road', 0)
            road = movement_result.get('road', 0)
            movement_confidence = movement_result.get('confidence', 'low')

            safe_print(f"  Movement: {off_road}\"/{ road}\" ({movement_confidence})")

            # ========================================
            # STEP 3: HE Effectiveness (if has gun)
            # ========================================
            he_dice = None
            he_target = None
            he_format = None
            he_confidence = 'none'

            # Get main gun caliber from equipment_guns relationship
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT g.caliber_mm, g.name
                FROM equipment_guns eg
                JOIN guns g ON eg.gun_id = g.gun_id
                WHERE eg.equipment_id = ? AND eg.mount_type = 'main'
                LIMIT 1
            """, (equipment_id,))

            gun_row = cursor.fetchone()
            if gun_row:
                caliber_mm, gun_name = gun_row
                he_result = calculate_he_effect(caliber_mm=caliber_mm, gun_name=gun_name)

                he_dice = he_result.get('dice')
                he_target = he_result.get('target')
                he_format = he_result.get('format')
                he_confidence = he_result.get('confidence', 'medium')

                safe_print(f"  HE: {he_format} ({he_confidence})")

            # ========================================
            # STEP 4: Penetration Conversion (if has gun)
            # ========================================
            ap_0_10 = None
            ap_10_20 = None
            ap_20_30 = None
            ap_30_40 = None
            ap_40_50 = None
            ap_50_70 = None
            pen_confidence = 'none'

            if gun_row:
                caliber_mm, gun_name = gun_row

                # Try to extract barrel length from gun name
                import re
                barrel_match = re.search(r'L[/-](\d+)', gun_name)
                barrel_length = f"L/{barrel_match.group(1)}" if barrel_match else None

                pen_result = convert_penetration(
                    caliber_mm=caliber_mm,
                    barrel_length=barrel_length
                )

                ap_0_10 = pen_result.get('ap_0_10')
                ap_10_20 = pen_result.get('ap_10_20')
                ap_20_30 = pen_result.get('ap_20_30')
                ap_30_40 = pen_result.get('ap_30_40')
                ap_40_50 = pen_result.get('ap_40_50')
                ap_50_70 = pen_result.get('ap_50_70')
                pen_confidence = pen_result.get('confidence', 'medium')

                safe_print(f"  AP: {ap_0_10}/{ap_10_20}/{ap_20_30} ({pen_confidence})")

            # ========================================
            # STEP 5: Points Calculation (all experience levels)
            # ========================================
            points_result = self.points_calc.calculate_points(
                unit_name=name,
                armor_front=armor_front,
                armor_side=armor_side,
                movement_off_road=off_road,
                movement_road=road,
                main_weapon=gun_name if gun_row else None,
                experience='r',
                date='1944',
                unit_type=equipment.get('equipment_type')
            )

            points_regular = points_result.final_points
            points_inexperienced = int(points_regular * 0.85)
            points_veteran = int(points_regular * 1.10)
            points_elite = int(points_regular * 1.20)
            points_confidence = points_result.confidence.lower()

            safe_print(f"  Points: {points_regular} (r) | {points_inexperienced} (i) | {points_veteran} (v) | {points_elite} (e) ({points_confidence})")

            # ========================================
            # STEP 6: Battle Rating Assignment (all experience levels)
            # ========================================
            br_result = self.br_assigner.assign_br(
                unit_name=name,
                unit_type=equipment.get('equipment_type', 'vehicle'),
                points_cost=points_regular,
                experience='r'
            )

            br_regular = br_result.final_br
            br_inexperienced = max(0, br_regular - 1)
            br_veteran = br_regular  # Usually same as regular
            br_elite = br_regular + 1
            br_confidence = br_result.confidence.lower()

            safe_print(f"  BR: {br_regular} (r) | {br_inexperienced} (i) | {br_veteran} (v) | {br_elite} (e) ({br_confidence})")

            # ========================================
            # STEP 7: Calculate Overall Confidence
            # ========================================
            confidence_map = {'high': 100, 'medium': 70, 'low': 40, 'none': 0}

            confidences = [
                confidence_map.get(armor_confidence, 40),
                confidence_map.get(movement_confidence, 40),
                confidence_map.get(he_confidence, 0),
                confidence_map.get(pen_confidence, 0),
                confidence_map.get(points_confidence, 40),
                confidence_map.get(br_confidence, 40),
            ]

            # Weighted average (HE/pen only matter if vehicle has gun)
            if gun_row:
                overall_confidence = sum(confidences) // len(confidences)
            else:
                # Skip HE/pen for vehicles without guns
                overall_confidence = sum([c for c, conf in zip(confidences, ['armor', 'movement', 'he', 'pen', 'points', 'br']) if conf not in ['he', 'pen']]) // 4

            # Determine generation method
            methods = []
            if armor_confidence == 'high':
                methods.append('armor_lookup')
            if movement_confidence == 'high':
                methods.append('movement_lookup')
            if points_confidence == 'high':
                methods.append('points_lookup')

            generation_method = '+'.join(methods) if methods else 'formula_based'

            # ========================================
            # STEP 8: Insert into database
            # ========================================
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO equipment_battlegroup (
                    equipment_id,
                    armor_front, armor_side, armor_rear,
                    armor_turret_front, armor_turret_side, armor_turret_rear,
                    off_road_movement, road_movement,
                    he_dice, he_target, he_format,
                    ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                    points_regular, points_inexperienced, points_veteran, points_elite,
                    battle_rating_regular, battle_rating_inexperienced,
                    battle_rating_veteran, battle_rating_elite,
                    crew,
                    generated_date, generation_method, confidence_score
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?
                )
            """, (
                equipment_id,
                armor_front, armor_side, armor_rear,
                armor_turret_front, armor_turret_side, armor_turret_rear,
                off_road, road,
                he_dice, he_target, he_format,
                ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                points_regular, points_inexperienced, points_veteran, points_elite,
                br_regular, br_inexperienced, br_veteran, br_elite,
                equipment.get('crew'),
                generation_method, overall_confidence
            ))

            self.conn.commit()

            safe_print(f"  [OK] Enriched successfully (confidence: {overall_confidence}%)")

            return EnrichmentResult(
                equipment_id=equipment_id,
                success=True,
                confidence_score=overall_confidence,
                generation_method=generation_method
            )

        except Exception as e:
            safe_print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()

            return EnrichmentResult(
                equipment_id=equipment_id,
                success=False,
                confidence_score=0,
                generation_method='failed',
                error_message=str(e)
            )

    def enrich_all(
        self,
        nation: Optional[str] = None,
        equipment_type: Optional[str] = None,
        limit: Optional[int] = None
    ):
        """Enrich all equipment matching criteria."""

        equipment_list = self.get_equipment_list(nation, equipment_type, limit)
        self.stats['total'] = len(equipment_list)

        print("=" * 70)
        print("Phase 9B Step 4: Equipment Enrichment Pipeline")
        print("=" * 70)
        print()
        print(f"Total items to enrich: {len(equipment_list)}")
        if nation:
            print(f"Nation filter: {nation}")
        if equipment_type:
            print(f"Type filter: {equipment_type}")
        if limit:
            print(f"Limit: {limit}")
        print()

        results = []

        for i, equipment in enumerate(equipment_list, 1):
            print(f"\n[{i}/{len(equipment_list)}] ", end="")

            result = self.enrich_equipment(equipment)
            results.append(result)

            if result.success:
                self.stats['enriched'] += 1

                # Track confidence distribution
                if result.confidence_score >= 80:
                    self.stats['high_confidence'] += 1
                elif result.confidence_score >= 60:
                    self.stats['medium_confidence'] += 1
                else:
                    self.stats['low_confidence'] += 1
            else:
                self.stats['failed'] += 1

        self.show_summary()

        return results

    def show_summary(self):
        """Display enrichment summary."""

        print()
        print("=" * 70)
        print("Enrichment Summary")
        print("=" * 70)
        print()
        print(f"Total items:              {self.stats['total']}")
        print(f"Successfully enriched:    {self.stats['enriched']}")
        print(f"Failed:                   {self.stats['failed']}")
        print()
        print("Confidence Distribution:")
        print(f"  High (80-100%):         {self.stats['high_confidence']}")
        print(f"  Medium (60-79%):        {self.stats['medium_confidence']}")
        print(f"  Low (0-59%):            {self.stats['low_confidence']}")
        print()

        if self.stats['total'] > 0:
            success_rate = (self.stats['enriched'] / self.stats['total']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            print()

    def validate(self):
        """Show validation statistics."""

        cursor = self.conn.cursor()

        print()
        print("=" * 70)
        print("Validation Report")
        print("=" * 70)
        print()

        # Count enriched items
        cursor.execute("SELECT COUNT(*) FROM equipment_battlegroup")
        total_enriched = cursor.fetchone()[0]
        print(f"Total enriched items: {total_enriched}")
        print()

        # Confidence distribution
        cursor.execute("""
            SELECT
                CASE
                    WHEN confidence_score >= 80 THEN 'High (80-100%)'
                    WHEN confidence_score >= 60 THEN 'Medium (60-79%)'
                    ELSE 'Low (0-59%)'
                END as confidence_tier,
                COUNT(*) as count
            FROM equipment_battlegroup
            GROUP BY confidence_tier
            ORDER BY confidence_score DESC
        """)

        print("Confidence Distribution:")
        for tier, count in cursor.fetchall():
            print(f"  {tier}: {count} items")
        print()

        # Sample high-confidence entries
        cursor.execute("""
            SELECT e.name, eb.points_regular, eb.battle_rating_regular,
                   eb.confidence_score, eb.generation_method
            FROM equipment_battlegroup eb
            JOIN equipment e ON eb.equipment_id = e.canonical_id
            WHERE eb.confidence_score >= 80
            ORDER BY eb.confidence_score DESC
            LIMIT 10
        """)

        print("Sample High-Confidence Items:")
        for name, pts, br, conf, method in cursor.fetchall():
            print(f"  {name:30s} | {pts:3d} pts | {br:2d} BR | {conf}% | {method}")
        print()

    def close(self):
        """Close database connections."""
        self.conn.close()
        self.points_calc.conn.close()
        self.br_assigner.conn.close()


def main():
    """Main execution function."""

    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 4: Equipment Enrichment Pipeline"
    )
    parser.add_argument(
        "--nation",
        choices=["german", "italian", "british", "american", "french"],
        help="Filter by nation"
    )
    parser.add_argument(
        "--type",
        help="Filter by equipment type (tank, artillery, etc.)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of items (for testing)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Show validation statistics after enrichment"
    )

    args = parser.parse_args()

    enricher = EquipmentEnricher()

    try:
        enricher.enrich_all(
            nation=args.nation,
            equipment_type=args.type,
            limit=args.limit
        )

        if args.validate:
            enricher.validate()

    finally:
        enricher.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
