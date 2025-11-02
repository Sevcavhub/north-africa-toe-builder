#!/usr/bin/env python3
"""
Phase 9B Step 3 Chunk 1: Points and Battle Rating Pattern Analysis

Analyzes 557 reference items (500 vehicles + 57 guns) to discover:
- Points distribution patterns by type/category
- BR distribution patterns by unit type and experience
- Correlations between points and combat characteristics
- Formulas for points calculator and BR assigner

Usage:
    python scripts/battlegroup/analysis/points_br_analysis.py
    python scripts/battlegroup/analysis/points_br_analysis.py --export-json
"""

import sqlite3
import json
import statistics
from collections import defaultdict
from pathlib import Path


class PointsBRAnalyzer:
    """Analyzes BattleGroup reference database to discover points/BR patterns."""

    def __init__(self, db_path="database/master_database.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        self.vehicles = []
        self.guns = []
        self.analysis_results = {}

    def load_data(self):
        """Load all reference data from database."""
        print("Loading reference data from database...")

        # Load vehicles
        cursor = self.conn.execute("""
            SELECT
                name as vehicle_name,
                nation,
                vehicle_type as type,
                points_cost as points,
                battle_rating,
                armor_front,
                armor_side,
                armor_rear,
                weapons as main_gun,
                off_road_inches as movement_off_road,
                road_inches as movement_road
            FROM bg_reference_vehicles
            WHERE points_cost IS NOT NULL AND battle_rating IS NOT NULL
        """)

        self.vehicles = [dict(row) for row in cursor.fetchall()]
        print(f"  Loaded {len(self.vehicles)} vehicles with points/BR data")

        # Load guns
        cursor = self.conn.execute("""
            SELECT
                name as gun_name,
                nation,
                caliber_mm,
                'Gun' as gun_type,
                points_cost as points,
                battle_rating,
                he_dice,
                he_target,
                ap_0_10 as penetration_0_10,
                ap_10_20 as penetration_10_20,
                ap_20_30 as penetration_20_30
            FROM bg_reference_guns
            WHERE points_cost IS NOT NULL AND battle_rating IS NOT NULL
        """)

        self.guns = [dict(row) for row in cursor.fetchall()]
        print(f"  Loaded {len(self.guns)} guns with points/BR data")

        total = len(self.vehicles) + len(self.guns)
        print(f"\n[OK] Total reference items: {total}\n")

        return total

    def analyze_points_distribution(self):
        """Analyze how points are distributed across vehicle types."""
        print("=" * 80)
        print("POINTS DISTRIBUTION ANALYSIS")
        print("=" * 80)

        # Group vehicles by type
        by_type = defaultdict(list)
        for vehicle in self.vehicles:
            vtype = vehicle['type'] or 'Unknown'
            by_type[vtype].append(vehicle['points'])

        # Calculate statistics per type
        type_stats = {}
        for vtype, points_list in sorted(by_type.items()):
            if len(points_list) < 2:
                continue

            type_stats[vtype] = {
                'count': len(points_list),
                'min': min(points_list),
                'max': max(points_list),
                'mean': statistics.mean(points_list),
                'median': statistics.median(points_list),
                'stdev': statistics.stdev(points_list) if len(points_list) > 1 else 0
            }

        # Print results
        print("\nVehicle Points by Type:")
        print(f"{'Type':<30} {'Count':<8} {'Min':<8} {'Max':<8} {'Mean':<8} {'Median':<8} {'StDev':<8}")
        print("-" * 90)

        for vtype, stats in sorted(type_stats.items(), key=lambda x: x[1]['mean'], reverse=True):
            print(f"{vtype:<30} {stats['count']:<8} {stats['min']:<8} {stats['max']:<8} "
                  f"{stats['mean']:<8.1f} {stats['median']:<8.1f} {stats['stdev']:<8.1f}")

        # Gun points analysis
        if self.guns:
            gun_points = [g['points'] for g in self.guns]
            print(f"\nGun Points Statistics:")
            print(f"  Count: {len(gun_points)}")
            print(f"  Range: {min(gun_points)} - {max(gun_points)}")
            print(f"  Mean: {statistics.mean(gun_points):.1f}")
            print(f"  Median: {statistics.median(gun_points):.1f}")

        self.analysis_results['points_by_type'] = type_stats
        self.analysis_results['gun_points_stats'] = {
            'count': len(gun_points),
            'min': min(gun_points),
            'max': max(gun_points),
            'mean': statistics.mean(gun_points),
            'median': statistics.median(gun_points)
        } if self.guns else {}

        print()

    def analyze_br_distribution(self):
        """Analyze Battle Rating distribution patterns."""
        print("=" * 80)
        print("BATTLE RATING DISTRIBUTION ANALYSIS")
        print("=" * 80)

        # Count BR values
        br_counts = defaultdict(int)
        br_by_type = defaultdict(lambda: defaultdict(int))

        for vehicle in self.vehicles:
            br = vehicle['battle_rating']
            vtype = vehicle['type'] or 'Unknown'
            br_counts[br] += 1
            br_by_type[vtype][br] += 1

        # Add guns
        for gun in self.guns:
            br = gun['battle_rating']
            gtype = gun['gun_type'] or 'Unknown'
            br_counts[br] += 1
            br_by_type[f"Gun-{gtype}"][br] += 1

        # Print overall BR distribution
        print("\nOverall BR Distribution:")
        for br in sorted(br_counts.keys()):
            count = br_counts[br]
            pct = (count / (len(self.vehicles) + len(self.guns))) * 100
            print(f"  BR {br}: {count:>4} units ({pct:>5.1f}%)")

        # Print BR by type
        print("\nBR Distribution by Type:")
        print(f"{'Type':<30} ", end='')
        for br in sorted(br_counts.keys()):
            print(f"BR{br:<3}", end=' ')
        print("Total")
        print("-" * 100)

        for vtype in sorted(br_by_type.keys()):
            print(f"{vtype:<30} ", end='')
            total = 0
            for br in sorted(br_counts.keys()):
                count = br_by_type[vtype].get(br, 0)
                print(f"{count:<5}", end=' ')
                total += count
            print(f"{total}")

        self.analysis_results['br_distribution'] = dict(br_counts)
        self.analysis_results['br_by_type'] = {k: dict(v) for k, v in br_by_type.items()}

        print()

    def analyze_points_correlations(self):
        """Analyze correlation between points and combat characteristics."""
        print("=" * 80)
        print("POINTS CORRELATION ANALYSIS")
        print("=" * 80)

        # Prepare data: convert armor letters to numbers for analysis
        armor_map = {
            'A': 15, 'B': 14, 'C': 13, 'D': 12, 'E': 11,
            'F': 10, 'G': 9, 'H': 8, 'I': 7, 'J': 6,
            'K': 5, 'L': 4, 'M': 3, 'N': 2, 'O': 1,
            'Soft-Skinned': 0, None: 0
        }

        # Collect data for correlation
        correlations = {
            'armor_front': [],
            'armor_avg': [],
            'movement_avg': [],
            'points': []
        }

        for vehicle in self.vehicles:
            if not all([vehicle.get('armor_front'), vehicle.get('points')]):
                continue

            front = armor_map.get(vehicle['armor_front'], 0)
            side = armor_map.get(vehicle.get('armor_side'), 0)
            rear = armor_map.get(vehicle.get('armor_rear'), 0)
            armor_avg = (front + side + rear) / 3 if side and rear else front

            move_off = vehicle.get('movement_off_road', 0) or 0
            move_road = vehicle.get('movement_road', 0) or 0
            move_avg = (move_off + move_road) / 2 if move_road else move_off

            correlations['armor_front'].append(front)
            correlations['armor_avg'].append(armor_avg)
            correlations['movement_avg'].append(move_avg)
            correlations['points'].append(vehicle['points'])

        # Calculate correlations (Pearson correlation coefficient)
        def pearson_correlation(x, y):
            """Calculate Pearson correlation coefficient."""
            if len(x) != len(y) or len(x) < 2:
                return 0.0

            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi ** 2 for xi in x)
            sum_y2 = sum(yi ** 2 for yi in y)

            numerator = (n * sum_xy) - (sum_x * sum_y)
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5

            return numerator / denominator if denominator != 0 else 0.0

        print("\nCorrelation with Points:")
        print(f"{'Factor':<30} {'Correlation':<15} {'Interpretation'}")
        print("-" * 70)

        points = correlations['points']
        corr_results = {}

        for factor in ['armor_front', 'armor_avg', 'movement_avg']:
            if correlations[factor]:
                corr = pearson_correlation(correlations[factor], points)
                corr_results[factor] = corr

                # Interpretation
                if abs(corr) > 0.7:
                    interp = "Strong correlation"
                elif abs(corr) > 0.4:
                    interp = "Moderate correlation"
                elif abs(corr) > 0.2:
                    interp = "Weak correlation"
                else:
                    interp = "Very weak correlation"

                print(f"{factor:<30} {corr:>+.3f}          {interp}")

        self.analysis_results['points_correlations'] = corr_results

        print()

    def analyze_points_formula_components(self):
        """Attempt to reverse-engineer points formula components."""
        print("=" * 80)
        print("POINTS FORMULA COMPONENT ANALYSIS")
        print("=" * 80)

        # Analyze a sample of well-known vehicles
        print("\nSample Vehicle Analysis (Points Breakdown Estimation):")
        print(f"{'Vehicle':<25} {'Type':<15} {'Points':<8} {'Armor':<8} {'Gun':<8} {'Move':<8}")
        print("-" * 90)

        # Sort by points and take diverse sample
        sample_vehicles = sorted(self.vehicles, key=lambda v: v['points'])
        sample_indices = [0, len(sample_vehicles)//4, len(sample_vehicles)//2,
                         3*len(sample_vehicles)//4, len(sample_vehicles)-1]

        for idx in sample_indices:
            if idx < len(sample_vehicles):
                v = sample_vehicles[idx]
                print(f"{v['vehicle_name'][:24]:<25} {str(v['type'])[:14]:<15} "
                      f"{v['points']:<8} {v['armor_front']:<8} "
                      f"{str(v.get('main_gun', ''))[:7]:<8} "
                      f"{v.get('movement_off_road', 0):<8}")

        # Identify base costs by type
        print("\nEstimated Base Costs by Type:")
        by_type = defaultdict(list)
        for vehicle in self.vehicles:
            vtype = vehicle['type'] or 'Unknown'
            by_type[vtype].append(vehicle['points'])

        base_costs = {}
        for vtype, points_list in sorted(by_type.items()):
            if len(points_list) >= 3:
                # Use 25th percentile as rough "base cost"
                sorted_points = sorted(points_list)
                base_idx = len(sorted_points) // 4
                base_costs[vtype] = sorted_points[base_idx]

        for vtype, base in sorted(base_costs.items(), key=lambda x: x[1]):
            print(f"  {vtype:<30} ~{base} pts (base)")

        self.analysis_results['estimated_base_costs'] = base_costs

        print()

    def export_results(self, output_path="scripts/battlegroup/analysis/analysis_results.json"):
        """Export analysis results to JSON."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"[OK] Analysis results exported to: {output_file}")
        print(f"   File size: {output_file.stat().st_size:,} bytes")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Main analysis execution."""
    import sys

    print("\n" + "=" * 80)
    print("PHASE 9B STEP 3 CHUNK 1: POINTS/BR PATTERN ANALYSIS")
    print("=" * 80)
    print()

    try:
        analyzer = PointsBRAnalyzer()

        # Load data
        total_items = analyzer.load_data()

        # Run analyses
        analyzer.analyze_points_distribution()
        analyzer.analyze_br_distribution()
        analyzer.analyze_points_correlations()
        analyzer.analyze_points_formula_components()

        # Export results
        if '--export-json' in sys.argv or True:  # Always export
            analyzer.export_results()

        analyzer.close()

        print("\n" + "=" * 80)
        print(f"[OK] ANALYSIS COMPLETE - {total_items} items analyzed")
        print("=" * 80)
        print("\nNext: Use these patterns to build points_calculator.py (Chunk 2)")
        print()

    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
