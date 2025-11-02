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
        self.conn.row_factory = sqlite3.Row

        # Load all templates
        vehicle_template_path = TEMPLATE_DIR / "datacard_vehicle.txt"
        with open(vehicle_template_path, 'r', encoding='utf-8') as f:
            self.vehicle_template = f.read()

        # Load gun template
        try:
            gun_template_path = TEMPLATE_DIR / "datacard_gun.txt"
            with open(gun_template_path, 'r', encoding='utf-8') as f:
                self.gun_template = f.read()
        except FileNotFoundError:
            self.gun_template = None

        # Load defence template
        try:
            defence_template_path = TEMPLATE_DIR / "datacard_defence.txt"
            with open(defence_template_path, 'r', encoding='utf-8') as f:
                self.defence_template = f.read()
        except FileNotFoundError:
            self.defence_template = None

        # Load fire support template
        try:
            support_template_path = TEMPLATE_DIR / "datacard_fire_support.txt"
            with open(support_template_path, 'r', encoding='utf-8') as f:
                self.fire_support_template = f.read()
        except FileNotFoundError:
            self.fire_support_template = None

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
                e.canonical_id, e.name, e.nation, e.equipment_type, e.category,
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
            'canonical_id', 'name', 'nation', 'equipment_type', 'category',
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

        # Get special rules
        data['special_rules'] = self.get_special_rules(data['canonical_id'])

        # If HE/AP data is missing and this is a gun, try bg_reference_guns
        if (not data['he_dice'] or not data['ap_0_10']):
            gun_data = self.get_reference_gun_data(data['name'])
            if gun_data:
                # Merge gun data
                data['he_dice'] = gun_data.get('he_dice') or data['he_dice']
                data['he_target'] = gun_data.get('he_target') or data['he_target']
                data['he_format'] = f"{data['he_dice']}/{data['he_target']}" if data['he_dice'] and data['he_target'] else data['he_format']
                data['ap_0_10'] = gun_data.get('ap_0_10') or data['ap_0_10']
                data['ap_10_20'] = gun_data.get('ap_10_20') or data['ap_10_20']
                data['ap_20_30'] = gun_data.get('ap_20_30') or data['ap_20_30']
                data['ap_30_40'] = gun_data.get('ap_30_40') or data['ap_30_40']
                data['ap_40_50'] = gun_data.get('ap_40_50') or data['ap_40_50']
                data['ap_50_70'] = gun_data.get('ap_50_70') or data['ap_50_70']

        return data

    def get_reference_gun_data(self, equipment_name: str) -> Optional[Dict]:
        """
        Get gun data from bg_reference_guns table.

        Args:
            equipment_name: Name of equipment

        Returns:
            Dict with gun data, or None if not found
        """
        cursor = self.conn.cursor()

        # Extract key parts from name (e.g., "50mm Pak 38" -> search for "pak 38" or "50mm")
        import re
        name_parts = []

        # Extract caliber (e.g., "50mm", "37mm", "75mm")
        caliber_match = re.search(r'(\d+(?:\.\d+)?)\s*mm', equipment_name, re.IGNORECASE)
        if caliber_match:
            name_parts.append(caliber_match.group(1))

        # Extract gun designation (e.g., "Pak 38", "QF 25")
        designation_match = re.search(r'(pak|pdr|qf|bofors|ordnance)\s*(\d+)', equipment_name, re.IGNORECASE)
        if designation_match:
            name_parts.append(f"{designation_match.group(1)}{designation_match.group(2)}")

        # Try multiple search patterns
        for part in name_parts:
            cursor.execute("""
                SELECT he_dice, he_target, ap_0_10, ap_10_20, ap_20_30,
                       ap_30_40, ap_40_50, ap_50_70, caliber_mm
                FROM bg_reference_guns
                WHERE name LIKE ?
                LIMIT 1
            """, (f"%{part}%",))

            row = cursor.fetchone()
            if row:
                return {
                    'he_dice': row[0],
                    'he_target': row[1],
                    'ap_0_10': row[2],
                    'ap_10_20': row[3],
                    'ap_20_30': row[4],
                    'ap_30_40': row[5],
                    'ap_40_50': row[6],
                    'ap_50_70': row[7],
                    'caliber_mm': row[8]
                }

        # Final fallback: try direct name match
        cursor.execute("""
            SELECT he_dice, he_target, ap_0_10, ap_10_20, ap_20_30,
                   ap_30_40, ap_40_50, ap_50_70, caliber_mm
            FROM bg_reference_guns
            WHERE name LIKE ?
            LIMIT 1
        """, (f"%{equipment_name}%",))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'he_dice': row[0],
            'he_target': row[1],
            'ap_0_10': row[2],
            'ap_10_20': row[3],
            'ap_20_30': row[4],
            'ap_30_40': row[5],
            'ap_40_50': row[6],
            'ap_50_70': row[7],
            'caliber_mm': row[8]
        }

    def get_special_rules(self, equipment_id: str) -> List[Dict]:
        """
        Get special rules for equipment from database.

        Args:
            equipment_id: Equipment canonical ID

        Returns:
            List of special rule dicts
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT sr.name, sr.description, sr.mechanical_effect, esr.confidence_score
            FROM equipment_special_rules esr
            JOIN bg_special_rules sr ON esr.rule_id = sr.rule_id
            WHERE esr.equipment_id = ?
            ORDER BY esr.confidence_score DESC, sr.name
        """, (equipment_id,))

        rules = []
        for row in cursor.fetchall():
            rules.append({
                'name': row[0],
                'description': row[1],
                'mechanical_effect': row[2],
                'confidence': row[3]
            })

        return rules

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

        # Format AP values (handle None, ensure string for formatting)
        ap_0_10 = str(data['ap_0_10']) if data['ap_0_10'] is not None else '-'
        ap_10_20 = str(data['ap_10_20']) if data['ap_10_20'] is not None else '-'
        ap_20_30 = str(data['ap_20_30']) if data['ap_20_30'] is not None else '-'
        ap_30_40 = str(data['ap_30_40']) if data['ap_30_40'] is not None else '-'
        ap_40_50 = str(data['ap_40_50']) if data['ap_40_50'] is not None else '-'
        ap_50_70 = str(data['ap_50_70']) if data['ap_50_70'] is not None else '-'

        # Format special rules
        if data['special_rules']:
            special_lines = []
            for rule in data['special_rules']:
                special_lines.append(f"• {rule['name']}: {rule['mechanical_effect']}")
            special_rules = "\n        ".join([''] + special_lines)
        else:
            special_rules = "\n        • None"

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

    def format_gun_datacard(
        self,
        data: Dict,
        experience: str = 'r'
    ) -> str:
        """
        Format gun datacard from data.

        Args:
            data: Equipment data dict
            experience: Experience level (i/r/v/e)

        Returns:
            Formatted datacard text
        """
        if not self.gun_template:
            # Fall back to vehicle template if gun template not available
            return self.format_vehicle_datacard(data, experience)

        # Determine gun type
        gun_type_map = {
            'anti_tank_guns': 'Anti-Tank Gun',
            'anti_aircraft_guns': 'Anti-Aircraft Gun',
            'field_artillery': 'Field Artillery',
            'towed_artillery': 'Towed Artillery',
            'howitzer': 'Howitzer',
            'mortar': 'Mortar'
        }

        equipment_type = data.get('equipment_type', '')
        category = data.get('category', '')

        if equipment_type:
            gun_type = gun_type_map.get(equipment_type, equipment_type.replace('_', ' ').title())
        elif category:
            gun_type = gun_type_map.get(category, category.replace('_', ' ').title())
        else:
            gun_type = 'Gun'

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

        # Extract caliber from name (e.g., "75mm Pak 40" -> "75mm")
        import re
        caliber_match = re.search(r'(\d+(?:\.\d+)?)\s*mm', data['name'], re.IGNORECASE)
        if caliber_match:
            caliber = caliber_match.group(0)
        else:
            caliber = 'Unknown'

        # Format HE
        if data['he_dice'] and data['he_target']:
            he_dice = data['he_dice']
            he_target = data['he_target']
            he_format = f"{he_dice}/{he_target}"
        else:
            he_dice = 'N/A'
            he_target = 'N/A'
            he_format = 'N/A'

        # Format AP values (handle None, ensure string for formatting)
        ap_0_10 = str(data['ap_0_10']) if data['ap_0_10'] is not None else '-'
        ap_10_20 = str(data['ap_10_20']) if data['ap_10_20'] is not None else '-'
        ap_20_30 = str(data['ap_20_30']) if data['ap_20_30'] is not None else '-'
        ap_30_40 = str(data['ap_30_40']) if data['ap_30_40'] is not None else '-'
        ap_40_50 = str(data['ap_40_50']) if data['ap_40_50'] is not None else '-'
        ap_50_70 = str(data['ap_50_70']) if data['ap_50_70'] is not None else '-'

        # Format special rules
        if data['special_rules']:
            special_lines = []
            for rule in data['special_rules']:
                special_lines.append(f"  • {rule['name']}: {rule['mechanical_effect']}")
            special_rules = "\n".join(special_lines)
        else:
            special_rules = "  • None"

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
        datacard = self.gun_template.format(
            name=data['name'].upper(),
            gun_type=gun_type,
            nation=nation,
            experience=self.EXPERIENCE_LABELS[experience],
            crew=crew,
            caliber=caliber,
            he_format=he_format,
            he_dice=he_dice,
            he_target=he_target,
            ap_0_10=ap_0_10,
            ap_10_20=ap_10_20,
            ap_20_30=ap_20_30,
            ap_30_40=ap_30_40,
            ap_40_50=ap_40_50,
            ap_50_70=ap_50_70,
            special_rules=special_rules,
            points=points,
            battle_rating=f"{br}-{experience}"
        )

        return datacard

    def is_gun(self, data: Dict) -> bool:
        """
        Determine if equipment is a gun.

        Args:
            data: Equipment data dict

        Returns:
            True if equipment is a gun
        """
        equipment_type = (data.get('equipment_type') or '').lower()
        category = (data.get('category') or '').lower()
        name = (data.get('name') or '').lower()

        gun_indicators = [
            'gun', 'artillery', 'howitzer', 'mortar',
            'anti_tank', 'anti_aircraft', 'pak', 'flak', 'pdr'
        ]

        return any(indicator in equipment_type or indicator in category or indicator in name
                   for indicator in gun_indicators)

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

        # Route to appropriate formatter
        if self.is_gun(data):
            print(f"  [INFO] Detected as gun, using gun template")
            datacard = self.format_gun_datacard(data, experience)
        else:
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
