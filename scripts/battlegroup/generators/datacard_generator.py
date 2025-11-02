#!/usr/bin/env python3
"""
Phase 9B Step 4: Equipment Datacard Generator
Generates BattleGroup-formatted datacards for vehicles and guns.

Usage:
    python datacard_generator.py --equipment "M4 Sherman"
    python datacard_generator.py --equipment "Tiger I" --experience veteran
    python datacard_generator.py --nation german --output datacards/
    python datacard_generator.py --all --output datacards/
"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"
TEMPLATE_DIR = project_root / "scripts" / "battlegroup" / "templates"
OUTPUT_DIR = project_root / "data" / "output" / "battlegroup" / "datacards"


class DatacardGenerator:
    """Generate BattleGroup equipment datacards."""

    EXPERIENCE_LABELS = {
        'i': 'Inexperienced',
        'r': 'Regular',
        'v': 'Veteran',
        'e': 'Elite'
    }

    def __init__(self):
        """Initialize generator with database connection."""
        self.conn = sqlite3.connect(DATABASE_PATH)

        # Load vehicle template
        vehicle_template_path = TEMPLATE_DIR / "datacard_vehicle.txt"
        with open(vehicle_template_path, 'r') as f:
            self.vehicle_template = f.read()

    def get_equipment_data(self, equipment_name: str) -> Optional[Dict]:
        """
        Get equipment data from database.

        Args:
            equipment_name: Name of equipment

        Returns:
            Dict with equipment and BattleGroup stats, or None if not found
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                e.canonical_id, e.name, e.nation, e.equipment_type,
                e.crew, e.weight_tonnes,
                eb.armor_front, eb.armor_side, eb.armor_rear,
                eb.armor_turret_front, eb.armor_turret_side, eb.armor_turret_rear,
                eb.off_road_movement, eb.road_movement,
                eb.he_dice, eb.he_target, eb.he_format,
                eb.ap_0_10, eb.ap_10_20, eb.ap_20_30,
                eb.ap_30_40, eb.ap_40_50, eb.ap_50_70,
                eb.points_regular, eb.points_inexperienced,
                eb.points_veteran, eb.points_elite,
                eb.battle_rating_regular, eb.battle_rating_inexperienced,
                eb.battle_rating_veteran, eb.battle_rating_elite,
                eb.confidence_score, eb.generation_method
            FROM equipment e
            JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            WHERE e.name LIKE ?
            LIMIT 1
        """, (f"%{equipment_name}%",))

        row = cursor.fetchone()
        if not row:
            return None

        columns = [
            'canonical_id', 'name', 'nation', 'equipment_type',
            'crew', 'weight_tonnes',
            'armor_front', 'armor_side', 'armor_rear',
            'armor_turret_front', 'armor_turret_side', 'armor_turret_rear',
            'off_road_movement', 'road_movement',
            'he_dice', 'he_target', 'he_format',
            'ap_0_10', 'ap_10_20', 'ap_20_30',
            'ap_30_40', 'ap_40_50', 'ap_50_70',
            'points_regular', 'points_inexperienced',
            'points_veteran', 'points_elite',
            'battle_rating_regular', 'battle_rating_inexperienced',
            'battle_rating_veteran', 'battle_rating_elite',
            'confidence_score', 'generation_method'
        ]

        data = dict(zip(columns, row))

        # Get main gun info
        cursor.execute("""
            SELECT g.name, g.caliber_mm
            FROM equipment_guns eg
            JOIN guns g ON eg.gun_id = g.gun_id
            WHERE eg.equipment_id = ? AND eg.mount_type = 'main'
            LIMIT 1
        """, (data['canonical_id'],))

        gun_row = cursor.fetchone()
        if gun_row:
            data['main_gun_name'] = gun_row[0]
            data['main_gun_caliber'] = gun_row[1]
        else:
            data['main_gun_name'] = None
            data['main_gun_caliber'] = None

        # Get secondary weapons
        cursor.execute("""
            SELECT g.name, eg.mount_type
            FROM equipment_guns eg
            JOIN guns g ON eg.gun_id = g.gun_id
            WHERE eg.equipment_id = ? AND eg.mount_type != 'main'
            ORDER BY eg.mount_type
        """, (data['canonical_id'],))

        data['secondary_weapons'] = cursor.fetchall()

        return data

    def format_vehicle_datacard(
        self,
        data: Dict,
        experience: str = 'r'
    ) -> str:
        """
        Format vehicle datacard from data.

        Args:
            data: Equipment data dict
            experience: Experience level (i/r/v/e)

        Returns:
            Formatted datacard text
        """

        # Format vehicle type
        vehicle_type_map = {
            'tank': 'Medium Tank',
            'light_tank': 'Light Tank',
            'heavy_tank': 'Heavy Tank',
            'tank_destroyer': 'Tank Destroyer',
            'assault_gun': 'Assault Gun',
            'armored_car': 'Armored Car',
            'halftrack': 'Halftrack',
            'artillery': 'Artillery',
            'anti_tank': 'Anti-Tank Gun',
            'anti_aircraft': 'Anti-Aircraft Gun'
        }
        if data['equipment_type']:
            vehicle_type = vehicle_type_map.get(data['equipment_type'], data['equipment_type'].replace('_', ' ').title())
        else:
            vehicle_type = 'Vehicle'

        # Get experience-specific values
        if experience == 'i':
            points = data['points_inexperienced']
            br = data['battle_rating_inexperienced']
        elif experience == 'v':
            points = data['points_veteran']
            br = data['battle_rating_veteran']
        elif experience == 'e':
            points = data['points_elite']
            br = data['battle_rating_elite']
        else:  # regular
            points = data['points_regular']
            br = data['battle_rating_regular']

        # Format armor turret (if present)
        if data['armor_turret_front']:
            armor_turret = data['armor_turret_front']
        else:
            armor_turret = 'N/A'

        # Format main gun
        if data['main_gun_name']:
            main_gun = data['main_gun_name']
        else:
            main_gun = 'None'

        # Format HE
        he_format = data['he_format'] if data['he_format'] else 'N/A'

        # Format secondary weapons
        if data['secondary_weapons']:
            secondary_lines = []
            for gun_name, mount_type in data['secondary_weapons']:
                secondary_lines.append(f"{mount_type.title()}: {gun_name}")
            secondary_weapon = "\n        ".join(secondary_lines)
        else:
            secondary_weapon = ""

        # Format AP values (handle None)
        ap_0_10 = data['ap_0_10'] if data['ap_0_10'] is not None else '-'
        ap_10_20 = data['ap_10_20'] if data['ap_10_20'] is not None else '-'
        ap_20_30 = data['ap_20_30'] if data['ap_20_30'] is not None else '-'
        ap_30_40 = data['ap_30_40'] if data['ap_30_40'] is not None else '-'
        ap_40_50 = data['ap_40_50'] if data['ap_40_50'] is not None else '-'
        ap_50_70 = data['ap_50_70'] if data['ap_50_70'] is not None else '-'

        # Format special rules (placeholder for now)
        special_rules = "\n        • N/A"

        # Format crew
        crew = data['crew'] if data['crew'] else 'Unknown'

        # Format nation
        nation_map = {
            'german': 'German',
            'british': 'British',
            'american': 'American',
            'italian': 'Italian',
            'french': 'French'
        }
        nation = nation_map.get(data['nation'], data['nation'].title())

        # Fill template
        datacard = self.vehicle_template.format(
            name=data['name'].upper(),
            vehicle_type=vehicle_type,
            nation=nation,
            experience=self.EXPERIENCE_LABELS[experience],
            armor_front=data['armor_front'],
            armor_side=data['armor_side'],
            armor_rear=data['armor_rear'],
            armor_turret=armor_turret,
            off_road=data['off_road_movement'],
            road=data['road_movement'],
            main_gun=main_gun,
            he_format=he_format,
            secondary_weapon=secondary_weapon,
            ap_0_10=ap_0_10,
            ap_10_20=ap_10_20,
            ap_20_30=ap_20_30,
            ap_30_40=ap_30_40,
            ap_40_50=ap_40_50,
            ap_50_70=ap_50_70,
            special_rules=special_rules,
            points=points,
            battle_rating=f"{br}-{experience}",
            crew=crew
        )

        return datacard

    def generate_datacard(
        self,
        equipment_name: str,
        experience: str = 'r',
        output_file: Optional[Path] = None
    ) -> str:
        """
        Generate a datacard for equipment.

        Args:
            equipment_name: Name of equipment
            experience: Experience level (i/r/v/e)
            output_file: Optional output file path

        Returns:
            Formatted datacard text
        """

        # Get equipment data
        data = self.get_equipment_data(equipment_name)

        if not data:
            print(f"[ERROR] Equipment not found: {equipment_name}")
            return None

        print(f"Generating datacard for: {data['name']} ({self.EXPERIENCE_LABELS[experience]})")

        # Format datacard
        datacard = self.format_vehicle_datacard(data, experience)

        # Save to file if specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(datacard)
            print(f"  [OK] Saved to: {output_file}")

        return datacard

    def generate_all_datacards(
        self,
        nation: Optional[str] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Generate datacards for all equipment.

        Args:
            nation: Optional nation filter
            output_dir: Output directory for datacards
        """

        cursor = self.conn.cursor()

        # Build query
        query = "SELECT name, nation FROM equipment ORDER BY nation, name"
        params = []

        if nation:
            query = "SELECT name, nation FROM equipment WHERE nation = ? ORDER BY name"
            params = [nation]

        cursor.execute(query, params)
        equipment_list = cursor.fetchall()

        print(f"\nGenerating datacards for {len(equipment_list)} items...")
        print()

        generated = 0
        failed = 0

        for equipment_name, eq_nation in equipment_list:
            try:
                if output_dir:
                    # Create output file path
                    safe_name = equipment_name.replace('/', '_').replace('\\', '_').replace(':', '_')
                    output_file = output_dir / eq_nation / f"{safe_name}_regular.txt"
                else:
                    output_file = None

                datacard = self.generate_datacard(equipment_name, 'r', output_file)

                if datacard:
                    generated += 1
                else:
                    failed += 1

            except Exception as e:
                print(f"[ERROR] Failed to generate datacard for {equipment_name}: {e}")
                failed += 1

        print()
        print("=" * 70)
        print(f"Datacard generation complete!")
        print(f"  Generated: {generated}")
        print(f"  Failed: {failed}")
        print("=" * 70)

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution function."""

    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 4: Equipment Datacard Generator"
    )
    parser.add_argument(
        "--equipment",
        help="Equipment name to generate datacard for"
    )
    parser.add_argument(
        "--experience",
        choices=['i', 'r', 'v', 'e'],
        default='r',
        help="Experience level (default: regular)"
    )
    parser.add_argument(
        "--nation",
        choices=['german', 'british', 'american', 'italian', 'french'],
        help="Generate datacards for all equipment of this nation"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate datacards for all equipment"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for datacards"
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print datacard to console"
    )

    args = parser.parse_args()

    generator = DatacardGenerator()

    try:
        if args.all:
            # Generate all datacards
            output_dir = args.output if args.output else OUTPUT_DIR
            generator.generate_all_datacards(output_dir=output_dir)

        elif args.nation:
            # Generate datacards for nation
            output_dir = args.output if args.output else OUTPUT_DIR
            generator.generate_all_datacards(nation=args.nation, output_dir=output_dir)

        elif args.equipment:
            # Generate single datacard
            output_file = None
            if args.output:
                safe_name = args.equipment.replace('/', '_').replace('\\', '_')
                output_file = args.output / f"{safe_name}_{args.experience}.txt"

            datacard = generator.generate_datacard(
                args.equipment,
                args.experience,
                output_file
            )

            if datacard and args.print:
                print()
                print(datacard)

        else:
            parser.print_help()
            return 1

    finally:
        generator.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
