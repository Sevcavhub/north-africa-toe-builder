"""
Service layer for scenario generation.
Wraps existing scenario generators from scripts/phase9b/ and scripts/battlegroup/generators/
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import json

# Add project paths
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "phase9b"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "battlegroup" / "generators"))

# Import generators
from scripts.phase9b.scenario_auto_generator import ScenarioAutoGenerator
from scripts.battlegroup.generators.historical_scenario_generator import (
    Scenario, ScenarioType, TableSize, VictoryType
)


class ScenarioService:
    """Service for scenario generation operations."""

    def __init__(self):
        """Initialize service with generators."""
        self.auto_generator = ScenarioAutoGenerator()

    def generate_historical_scenario(
        self,
        quarter: str,
        battle: str,
        location: str,
        **kwargs
    ) -> Dict:
        """
        Generate historical scenario.

        Args:
            quarter: Quarter code (e.g., '1941q2')
            battle: Battle name (e.g., 'battleaxe')
            location: Battlefield location (e.g., 'Halfaya Pass')
            **kwargs: Additional scenario parameters

        Returns:
            Complete scenario dictionary
        """
        # Create scenario template from historical data
        scenario_data = {
            'title': f"Historical Scenario - {location}",
            'date': quarter,
            'quarter': quarter,
            'location': location,
            'battle': battle,
            'forces': {},
            'metadata': {
                'generated_by': 'North Africa TO&E Builder API',
                'generation_method': 'historical'
            }
        }

        # Add optional parameters
        if 'nations' in kwargs:
            scenario_data['nations'] = kwargs['nations']
        if 'points' in kwargs:
            scenario_data['points'] = kwargs['points']

        # Use auto-generator to enrich with terrain, weather, etc.
        try:
            complete_scenario = self.auto_generator.generate_scenario_from_imported(
                scenario_data
            )
            return complete_scenario
        except Exception as e:
            # Return basic scenario if enrichment fails
            return {
                **scenario_data,
                'error': f"Enrichment failed: {str(e)}",
                'basic_scenario': True
            }

    def generate_random_scenario(
        self,
        points: int,
        nations: List[str],
        quarter: str,
        **kwargs
    ) -> Dict:
        """
        Generate random scenario with balanced forces.

        Args:
            points: Points budget per side
            nations: List of 2 nations (e.g., ['german', 'british'])
            quarter: Quarter code
            **kwargs: Additional parameters

        Returns:
            Random scenario dictionary
        """
        if len(nations) != 2:
            raise ValueError("Exactly 2 nations required for random scenario")

        # Select random battlefield location for quarter
        from scripts.phase9b.scenario_auto_generator import BATTLEFIELD_LOCATIONS
        import random

        locations = BATTLEFIELD_LOCATIONS.get(quarter, ['North Africa'])
        location = random.choice(locations)

        # Create scenario template
        scenario_data = {
            'title': f"Random Engagement - {location}",
            'date': quarter,
            'quarter': quarter,
            'location': location,
            'forces': {
                nations[0]: {
                    'nation': nations[0],
                    'force_name': f"{nations[0].title()} Task Force",
                    'total_points': points,
                    'battle_rating': int(points * 0.08),  # Approximate BR
                    'units': []
                },
                nations[1]: {
                    'nation': nations[1],
                    'force_name': f"{nations[1].title()} Task Force",
                    'total_points': points,
                    'battle_rating': int(points * 0.08),
                    'units': []
                }
            },
            'metadata': {
                'generated_by': 'North Africa TO&E Builder API',
                'generation_method': 'random'
            }
        }

        # Enrich with full scenario details
        try:
            complete_scenario = self.auto_generator.generate_scenario_from_imported(
                scenario_data
            )
            return complete_scenario
        except Exception as e:
            return {
                **scenario_data,
                'error': f"Generation failed: {str(e)}"
            }

    def generate_from_imported(
        self,
        imported_scenario: Dict
    ) -> Dict:
        """
        Generate complete scenario from BG Builder import.

        Args:
            imported_scenario: Imported scenario JSON from bg_builder_import.py

        Returns:
            Complete enriched scenario
        """
        try:
            return self.auto_generator.generate_scenario_from_imported(imported_scenario)
        except Exception as e:
            raise ValueError(f"Failed to generate scenario: {str(e)}")

    def get_available_locations(self, quarter: str) -> List[str]:
        """
        Get available battlefield locations for quarter.

        Args:
            quarter: Quarter code

        Returns:
            List of location names
        """
        from scripts.phase9b.scenario_auto_generator import BATTLEFIELD_LOCATIONS
        return BATTLEFIELD_LOCATIONS.get(quarter, ['North Africa'])

    def close(self):
        """Close database connections."""
        if hasattr(self, 'auto_generator'):
            self.auto_generator.close()

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
