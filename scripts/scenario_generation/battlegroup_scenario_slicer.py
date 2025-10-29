#!/usr/bin/env python3
"""
BattleGroup Scenario Slicer

Purpose: Create playable scenario "slices" from full division TO&E data

Input: Full equipment list with BattleGroup stats (points, BR, counts)
Output: 4 scenario sizes - Squad, Platoon, Company, Battalion

Force Selection Strategy:
- Respects organizational structure (don't split platoons)
- Maintains force balance (tanks + AT guns + infantry + support)
- Prioritizes command/elite units
- Targets specific points ranges per scenario size

Based on BattleGroup Rules:
- Squad: 100-350pts (target 250pts)
- Platoon: 351-750pts (target 500pts)
- Company: 751-1250pts (target 1000pts)
- Battalion: 1251-2000pts (target 1500pts)
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import copy

class BattleGroupScenarioSlicer:
    """Slice full division forces into playable scenarios"""

    # Scenario size definitions (from BattleGroup Rules pages 1-10)
    SCENARIO_SIZES = {
        'squad': {
            'name': 'Squad',
            'points_min': 100,
            'points_max': 350,
            'points_target': 250,
            'br_target': 20,
            'force_composition': {
                'tanks': (1, 2),      # 1-2 tanks
                'at_guns': (1, 2),    # 1-2 AT guns
                'artillery': (0, 1),  # 0-1 artillery
                'vehicles': (2, 4)    # 2-4 support vehicles
            }
        },
        'platoon': {
            'name': 'Platoon',
            'points_min': 351,
            'points_max': 750,
            'points_target': 500,
            'br_target': 40,
            'force_composition': {
                'tanks': (3, 5),      # 3-5 tanks
                'at_guns': (2, 3),    # 2-3 AT guns
                'artillery': (1, 2),  # 1-2 artillery
                'vehicles': (4, 8)    # 4-8 support vehicles
            }
        },
        'company': {
            'name': 'Company',
            'points_min': 751,
            'points_max': 1250,
            'points_target': 1000,
            'br_target': 80,
            'force_composition': {
                'tanks': (8, 12),     # 8-12 tanks
                'at_guns': (4, 6),    # 4-6 AT guns
                'artillery': (2, 3),  # 2-3 artillery
                'vehicles': (8, 12)   # 8-12 support vehicles
            }
        },
        'battalion': {
            'name': 'Battalion',
            'points_min': 1251,
            'points_max': 2000,
            'points_target': 1500,
            'br_target': 120,
            'force_composition': {
                'tanks': (15, 20),    # 15-20 tanks
                'at_guns': (6, 10),   # 6-10 AT guns
                'artillery': (3, 5),  # 3-5 artillery
                'vehicles': (12, 20)  # 12-20 support vehicles
            }
        }
    }

    def __init__(self):
        """Initialize slicer with priority weights"""
        # Priority weights for selection (higher = selected first)
        self.priority_weights = {
            'command': 100,  # Command tanks/vehicles always highest priority
            'heavy': 80,     # Heavy tanks
            'medium': 60,    # Medium tanks
            'light': 40,     # Light tanks
            'at_heavy': 70,  # Heavy AT guns (88mm, 90mm)
            'at_medium': 50, # Medium AT guns (50mm, 75mm)
            'at_light': 30,  # Light AT guns (37mm)
            'artillery': 50, # Field artillery
            'vehicle': 20    # Support vehicles
        }

    def slice_force(self, equipment_list: List[Dict], scenario_size: str) -> Dict:
        """
        Create a playable force slice for a specific scenario size

        Args:
            equipment_list: Full equipment list with BattleGroup stats
            scenario_size: 'squad', 'platoon', 'company', or 'battalion'

        Returns:
            Dict with:
            - equipment: Sliced equipment list
            - totals: {points, br, counts_by_type}
            - composition: Force breakdown
        """
        if scenario_size not in self.SCENARIO_SIZES:
            raise ValueError(f"Invalid scenario size: {scenario_size}. Must be: {list(self.SCENARIO_SIZES.keys())}")

        size_config = self.SCENARIO_SIZES[scenario_size]
        target_points = size_config['points_target']
        target_br = size_config['br_target']
        composition_targets = size_config['force_composition']

        # Step 1: Categorize and prioritize equipment
        categorized = self._categorize_equipment(equipment_list)

        # Step 2: Select equipment by priority until points target reached
        selected = self._select_equipment_by_priority(
            categorized,
            target_points,
            composition_targets
        )

        # Step 3: Calculate totals
        totals = self._calculate_totals(selected)

        # Step 4: Generate composition breakdown
        composition = self._analyze_composition(selected)

        return {
            'equipment': selected,
            'totals': totals,
            'composition': composition,
            'scenario_size': size_config['name'],
            'points_target': target_points,
            'points_actual': totals['points'],
            'br_target': target_br,
            'br_actual': totals['br']
        }

    def _categorize_equipment(self, equipment_list: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize equipment by type and priority

        Returns dict with keys:
        - command_tanks
        - heavy_tanks
        - medium_tanks
        - light_tanks
        - at_heavy
        - at_medium
        - at_light
        - artillery
        - vehicles
        """
        categories = {
            'command_tanks': [],
            'heavy_tanks': [],
            'medium_tanks': [],
            'light_tanks': [],
            'at_heavy': [],
            'at_medium': [],
            'at_light': [],
            'artillery': [],
            'vehicles': []
        }

        for item in equipment_list:
            if not isinstance(item, dict) or 'battlegroup_stats' not in item:
                continue

            equipment_type = item.get('type', 'unknown')
            stats = item['battlegroup_stats']

            # Tanks
            if equipment_type == 'tank':
                # Check if command tank
                special_rules = stats.get('special_rules', [])
                if 'command' in special_rules or 'command' in item.get('name', '').lower():
                    categories['command_tanks'].append(item)
                else:
                    # Categorize by armor
                    armor_str = stats.get('armor', '0/0/0')
                    front_armor = int(armor_str.split('/')[0])

                    if front_armor >= 11:  # Heavy (armor 11+)
                        categories['heavy_tanks'].append(item)
                    elif front_armor >= 7:  # Medium (armor 7-10)
                        categories['medium_tanks'].append(item)
                    else:  # Light (armor <7)
                        categories['light_tanks'].append(item)

            # AT Guns
            elif equipment_type == 'anti_tank':
                penetration = stats.get('penetration', 0)

                if penetration >= 11:  # Heavy AT (pen 11+)
                    categories['at_heavy'].append(item)
                elif penetration >= 7:  # Medium AT (pen 7-10)
                    categories['at_medium'].append(item)
                else:  # Light AT (pen <7)
                    categories['at_light'].append(item)

            # Artillery
            elif equipment_type == 'artillery':
                categories['artillery'].append(item)

            # Vehicles
            elif equipment_type in ['halftracks', 'trucks', 'armored_cars', 'motorcycles']:
                categories['vehicles'].append(item)

        return categories

    def _select_equipment_by_priority(self, categorized: Dict[str, List[Dict]],
                                     target_points: int,
                                     composition_targets: Dict) -> List[Dict]:
        """
        Select equipment by priority until target points reached

        Strategy:
        1. Always include 1 command tank if available
        2. Fill tank quota (heavy > medium > light)
        3. Fill AT gun quota (heavy > medium > light)
        4. Fill artillery quota
        5. Fill vehicle quota
        6. Stop when target points ±10% reached
        """
        selected = []
        current_points = 0
        points_tolerance = target_points * 0.15  # ±15% tolerance (more flexible)
        min_points = target_points - points_tolerance
        max_points = target_points + points_tolerance

        counts = {
            'tanks': 0,
            'at_guns': 0,
            'artillery': 0,
            'vehicles': 0
        }

        # Selection priority order
        selection_order = [
            ('command_tanks', 'tanks', 1, 1),  # Always include 1 command tank if available
            ('heavy_tanks', 'tanks', *composition_targets['tanks']),
            ('medium_tanks', 'tanks', *composition_targets['tanks']),
            ('light_tanks', 'tanks', *composition_targets['tanks']),
            ('at_heavy', 'at_guns', *composition_targets['at_guns']),
            ('at_medium', 'at_guns', *composition_targets['at_guns']),
            ('at_light', 'at_guns', *composition_targets['at_guns']),
            ('artillery', 'artillery', *composition_targets['artillery']),
            ('vehicles', 'vehicles', *composition_targets['vehicles'])
        ]

        for category_key, count_key, min_count, max_count in selection_order:
            items = categorized.get(category_key, [])
            if not items:
                continue  # Skip empty categories

            for item in items:
                # Check if we've reached max count for this type
                if counts[count_key] >= max_count:
                    break

                # Calculate points for this item
                stats = item['battlegroup_stats']
                item_points = stats.get('points_total', 0)
                item_count = item.get('count', 1)

                # Try to add individual units from this equipment type
                points_each = stats.get('points_each', item_points // max(item_count, 1))
                br_each = stats.get('br_each', 1)

                # Add as many units as we can without exceeding limits
                units_added = 0
                for _ in range(item_count):
                    # Stop if we've hit count limit
                    if counts[count_key] >= max_count:
                        break

                    # Check if we can afford this unit
                    if current_points + points_each <= max_points:
                        units_added += 1
                        current_points += points_each
                        counts[count_key] += 1
                    else:
                        # Would exceed max points, stop adding from this type
                        break

                # If we added any units, create the equipment entry
                if units_added > 0:
                    item_copy = copy.deepcopy(item)
                    item_copy['count'] = units_added
                    item_copy['battlegroup_stats']['points_total'] = points_each * units_added
                    item_copy['battlegroup_stats']['br_total'] = br_each * units_added
                    selected.append(item_copy)

                # Stop if we're near max points
                if current_points >= max_points * 0.95:  # Stop at 95% of max
                    break

        return selected

    def _calculate_totals(self, equipment_list: List[Dict]) -> Dict:
        """Calculate total points, BR, and counts"""
        totals = {
            'points': 0,
            'br': 0,
            'equipment_count': len(equipment_list),
            'unit_count': 0,
            'by_type': {}
        }

        for item in equipment_list:
            if 'battlegroup_stats' not in item:
                continue

            stats = item['battlegroup_stats']
            count = item.get('count', 1)
            equipment_type = item.get('type', 'unknown')

            totals['points'] += stats.get('points_total', 0)
            totals['br'] += stats.get('br_total', 0)
            totals['unit_count'] += count

            if equipment_type not in totals['by_type']:
                totals['by_type'][equipment_type] = {
                    'count': 0,
                    'points': 0,
                    'br': 0
                }

            totals['by_type'][equipment_type]['count'] += count
            totals['by_type'][equipment_type]['points'] += stats.get('points_total', 0)
            totals['by_type'][equipment_type]['br'] += stats.get('br_total', 0)

        return totals

    def _analyze_composition(self, equipment_list: List[Dict]) -> Dict:
        """Analyze force composition"""
        composition = {
            'tanks': [],
            'at_guns': [],
            'artillery': [],
            'vehicles': []
        }

        for item in equipment_list:
            equipment_type = item.get('type', 'unknown')
            name = item.get('name', 'Unknown')
            count = item.get('count', 1)

            if equipment_type == 'tank':
                composition['tanks'].append(f"{name} (x{count})")
            elif equipment_type == 'anti_tank':
                composition['at_guns'].append(f"{name} (x{count})")
            elif equipment_type == 'artillery':
                composition['artillery'].append(f"{name} (x{count})")
            elif equipment_type in ['halftracks', 'trucks', 'armored_cars', 'motorcycles']:
                composition['vehicles'].append(f"{name} (x{count})")

        return composition


def main():
    """Test the slicer with sample data"""
    print("BattleGroup Scenario Slicer - Test Mode")
    print("="*60)

    # Sample equipment list (simulating full division)
    sample_equipment = [
        {
            'name': 'Panzer III Ausf F',
            'type': 'tank',
            'count': 44,
            'battlegroup_stats': {
                'armor': '4/2/2',
                'penetration': 5,
                'points_each': 100,
                'points_total': 4400,
                'br_each': 3,
                'br_total': 132,
                'experience': 'veteran',
                'special_rules': []
            }
        },
        {
            'name': 'Panzer IV Ausf D',
            'type': 'tank',
            'count': 12,
            'battlegroup_stats': {
                'armor': '5/3/3',
                'penetration': 6,
                'points_each': 120,
                'points_total': 1440,
                'br_each': 4,
                'br_total': 48,
                'experience': 'veteran',
                'special_rules': ['command']
            }
        },
        {
            'name': '5cm PaK 38',
            'type': 'anti_tank',
            'count': 24,
            'battlegroup_stats': {
                'penetration': 7,
                'he_size': 'very_light',
                'points_each': 60,
                'points_total': 1440,
                'br_each': 3,
                'br_total': 72,
                'mobility': 'towed'
            }
        }
    ]

    slicer = BattleGroupScenarioSlicer()

    for size in ['squad', 'platoon', 'company', 'battalion']:
        print(f"\n{size.upper()} SCENARIO")
        print("-" * 60)

        result = slicer.slice_force(sample_equipment, size)

        print(f"Target: {result['points_target']}pts, BR ~{result['br_target']}")
        print(f"Actual: {result['points_actual']}pts, BR {result['br_actual']}")
        print(f"Equipment: {result['totals']['equipment_count']} types, {result['totals']['unit_count']} units")
        print(f"\nComposition:")
        for category, items in result['composition'].items():
            if items:
                print(f"  {category.title()}: {', '.join(items)}")


if __name__ == '__main__':
    main()
