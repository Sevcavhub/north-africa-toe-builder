"""
Service layer for army list generation.
Wraps army_list_generator.py from scripts/battlegroup/generators/
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project paths
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "battlegroup" / "generators"))

# Import army list generator
from scripts.battlegroup.generators.army_list_generator import ArmyListGenerator


class ArmyListService:
    """Service for army list generation operations."""

    def __init__(self):
        """Initialize service with generator."""
        self.generator = ArmyListGenerator()

    def generate_army_list(
        self,
        nation: str,
        quarter: str,
        points: int,
        quality: str = 'regular',
        **kwargs
    ) -> Dict:
        """
        Generate complete army list.

        Args:
            nation: Nation code (e.g., 'german')
            quarter: Quarter code (e.g., '1941q2')
            points: Points budget
            quality: Unit quality ('regular', 'veteran', 'elite')
            **kwargs: Additional parameters (battle, date, etc.)

        Returns:
            Army list dictionary with units, points, BR
        """
        try:
            # Generate text army list using existing generator
            battle = kwargs.get('battle')
            date = kwargs.get('date')

            army_list_text = self.generator.generate_army_list(
                nation=nation,
                quarter=quarter,
                battle=battle,
                date=date
            )

            # Extract equipment for structured response
            categorized_equipment = self.generator.get_phase6_equipment_for_quarter(
                nation, quarter
            )

            # Build structured response
            units = []
            total_points = 0
            total_br = 0

            for category, equipment_list in categorized_equipment.items():
                for equipment in equipment_list:
                    # Select points/BR based on quality
                    if quality == 'veteran':
                        points_cost = equipment.points_veteran or equipment.points_regular
                        br_cost = equipment.br_veteran or equipment.br_regular
                    elif quality == 'elite':
                        points_cost = equipment.points_elite or equipment.points_regular
                        br_cost = equipment.br_elite or equipment.br_regular
                    else:
                        points_cost = equipment.points_regular
                        br_cost = equipment.br_regular

                    # Only include if we have room in budget
                    if total_points + points_cost <= points:
                        units.append({
                            'name': equipment.name,
                            'category': category,
                            'quantity': 1,
                            'quality': quality,
                            'points': points_cost,
                            'br': br_cost,
                            'equipment_id': equipment.canonical_id
                        })
                        total_points += points_cost
                        total_br += br_cost

                        # Stop if budget exhausted
                        if total_points >= points * 0.95:  # Use 95% of budget
                            break

                if total_points >= points * 0.95:
                    break

            return {
                'nation': nation,
                'quarter': quarter,
                'quality': quality,
                'points_budget': points,
                'points_spent': total_points,
                'battle_rating': total_br,
                'units': units,
                'army_list_text': army_list_text,
                'metadata': {
                    'generated_by': 'North Africa TO&E Builder API',
                    'unit_count': len(units)
                }
            }

        except Exception as e:
            raise ValueError(f"Failed to generate army list: {str(e)}")

    def get_available_equipment(
        self,
        nation: str,
        quarter: str,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Get available equipment for nation and quarter.

        Args:
            nation: Nation code
            quarter: Quarter code
            category: Optional category filter (ARMOR, INFANTRY, etc.)

        Returns:
            List of equipment dictionaries
        """
        try:
            categorized = self.generator.get_phase6_equipment_for_quarter(
                nation, quarter
            )

            if category:
                equipment_list = categorized.get(category, [])
            else:
                # Flatten all categories
                equipment_list = []
                for cat_equipment in categorized.values():
                    equipment_list.extend(cat_equipment)

            # Convert to dictionaries
            return [
                {
                    'name': eq.name,
                    'category': eq.category,
                    'equipment_id': eq.canonical_id,
                    'points_regular': eq.points_regular,
                    'points_veteran': eq.points_veteran,
                    'points_elite': eq.points_elite,
                    'br_regular': eq.br_regular,
                    'br_veteran': eq.br_veteran,
                    'br_elite': eq.br_elite
                }
                for eq in equipment_list
            ]

        except Exception as e:
            raise ValueError(f"Failed to get equipment: {str(e)}")

    def close(self):
        """Close database connections."""
        if hasattr(self, 'generator'):
            self.generator.close()

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
