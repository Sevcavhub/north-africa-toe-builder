#!/usr/bin/env python3
"""
Phase 9B Step 7: Book Equipment Datacard Generator

Generates BattleGroup datacards for all equipment used in the 4 battle books:
- Operation Battleaxe (1941-Q2)
- Operation Crusader (1941-Q4)
- Battle of Gazala (1942-Q2)
- First El Alamein (1942-Q3)

Reads Phase 6 unit JSONs to extract equipment lists, then generates
datacards organized by book and category.

Usage:
    python generate_book_datacards.py --battle battleaxe
    python generate_book_datacards.py --all
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"
UNITS_DIR = project_root / "data" / "output" / "units"
OUTPUT_BASE = project_root / "books"

# Battle definitions with quarters
BATTLES = {
    'battleaxe': {
        'name': 'Operation Battleaxe',
        'quarters': ['1941q2'],
        'output_dir': 'battleaxe'
    },
    'crusader': {
        'name': 'Operation Crusader',
        'quarters': ['1941q4'],
        'output_dir': 'crusader'
    },
    'gazala': {
        'name': 'Battle of Gazala',
        'quarters': ['1942q2'],
        'output_dir': 'gazala'
    },
    'alamein': {
        'name': 'First El Alamein',
        'quarters': ['1942q3'],
        'output_dir': 'first_alamein'
    }
}

NATIONS = ['german', 'british', 'italian', 'american', 'french']


class BookDatacardGenerator:
    """Generate equipment datacards for battle books."""

    def __init__(self):
        """Initialize generator."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def get_units_for_battle(self, battle_key: str) -> List[Path]:
        """
        Get all Phase 6 unit JSON files for a battle.

        Args:
            battle_key: Battle key (battleaxe, crusader, gazala, alamein)

        Returns:
            List of unit JSON file paths
        """
        battle = BATTLES[battle_key]
        quarters = battle['quarters']

        unit_files = []

        for quarter in quarters:
            # Find all units for this quarter
            for nation in NATIONS:
                pattern = f"{nation}_{quarter}_*.json"
                files = list(UNITS_DIR.glob(pattern))
                unit_files.extend(files)

        print(f"Found {len(unit_files)} unit files for {battle['name']}")
        return unit_files

    def extract_equipment_from_unit(self, unit_file: Path) -> Set[str]:
        """
        Extract equipment names from a unit JSON file.

        Args:
            unit_file: Path to unit JSON

        Returns:
            Set of equipment WITW IDs
        """
        try:
            with open(unit_file, 'r', encoding='utf-8') as f:
                unit_data = json.load(f)
        except Exception as e:
            print(f"[WARNING] Failed to read {unit_file.name}: {e}")
            return set()

        equipment_ids = set()

        # Helper function to extract witw_id from nested structures
        def extract_witw_ids(obj):
            if isinstance(obj, dict):
                # Direct witw_id field
                if 'witw_id' in obj:
                    witw_id = obj['witw_id']
                    # Filter out generic/summary IDs and metadata
                    excluded_terms = [
                        'TOTAL', 'OPERATIONAL', 'VARIANTS', 'UNKNOWN',
                        'COUNT', 'NOTES', 'NOTE', 'SOURCE', 'READINESS',
                        'ORGANIZATION', 'MODELS', 'MISC_SUPPORT',
                        '_GER_', '_BRI_', '_ITA_', '_USA_', '_GBR_',
                        'PERCENTAGE'
                    ]
                    # Also exclude if it's just a number
                    if witw_id and not witw_id.isdigit():
                        if not any(x in witw_id.upper() for x in excluded_terms):
                            # Additional specific exclusions for edge cases
                            if witw_id.upper() not in ['FIELD', 'ARTILLERY', 'TOTAL']:
                                equipment_ids.add(witw_id)
                # Recursively check all dict values
                for value in obj.values():
                    extract_witw_ids(value)
            elif isinstance(obj, list):
                # Recursively check all list items
                for item in obj:
                    extract_witw_ids(item)

        # Extract from top-level categories
        categories_to_check = [
            'top_3_infantry_weapons',
            'tanks',
            'halftracks',
            'armored_cars',
            'trucks',
            'motorcycles',
            'support_vehicles',
            'field_artillery',
            'anti_tank_guns',
            'anti_aircraft_guns',
            'heavy_artillery',
            'mortars'
        ]

        for category in categories_to_check:
            if category in unit_data:
                extract_witw_ids(unit_data[category])

        return equipment_ids

    def get_all_equipment_for_battle(self, battle_key: str) -> Dict[str, Set[str]]:
        """
        Get all unique equipment used in a battle.

        Args:
            battle_key: Battle key

        Returns:
            Dict mapping category to set of equipment canonical IDs
        """
        unit_files = self.get_units_for_battle(battle_key)

        all_equipment = set()

        for unit_file in unit_files:
            equipment = self.extract_equipment_from_unit(unit_file)
            all_equipment.update(equipment)

        print(f"Found {len(all_equipment)} unique equipment items")

        # Categorize equipment
        categorized = self.categorize_equipment(all_equipment)

        return categorized

    def categorize_equipment(self, equipment_ids: Set[str]) -> Dict[str, List[Dict]]:
        """
        Categorize equipment by type.

        Args:
            equipment_ids: Set of equipment WITW IDs

        Returns:
            Dict mapping category name to list of equipment dicts
        """
        cursor = self.conn.cursor()

        categories = defaultdict(list)

        for witw_id in equipment_ids:
            # Try multiple matching strategies
            # 1. Try canonical_id exact match
            cursor.execute("""
                SELECT
                    e.canonical_id, e.name, e.nation,
                    e.equipment_type, e.category
                FROM equipment e
                WHERE e.canonical_id = ?
                LIMIT 1
            """, (witw_id,))

            row = cursor.fetchone()

            # 2. Fallback: fuzzy name search (convert WITW_ID format)
            if not row:
                # Convert WITW_ID to searchable name (e.g., TANK_M4_SHERMAN -> "M4" and "Sherman")
                search_terms = []
                if '_' in witw_id:
                    parts = witw_id.split('_')
                    # Get last part (usually model name)
                    if len(parts) > 1:
                        search_terms.append(parts[-1])
                    # Get second-to-last part (usually model number)
                    if len(parts) > 2:
                        search_terms.append(parts[-2])
                else:
                    search_terms = [witw_id]

                for term in search_terms:
                    cursor.execute("""
                        SELECT
                            e.canonical_id, e.name, e.nation,
                            e.equipment_type, e.category
                        FROM equipment e
                        WHERE e.name LIKE ? OR e.canonical_id LIKE ?
                        LIMIT 1
                    """, (f"%{term}%", f"%{term}%"))
                    row = cursor.fetchone()
                    if row:
                        break

            if not row:
                print(f"[WARNING] Equipment not found in database: {witw_id}")
                continue

            equipment = {
                'canonical_id': row['canonical_id'],
                'name': row['name'],
                'nation': row['nation'],
                'equipment_type': row['equipment_type'],
                'category': row['category']
            }

            # Categorize with improved logic
            eq_type = (row['equipment_type'] or '').lower()
            eq_category = (row['category'] or '').lower()
            name = (row['name'] or '').lower()

            # Priority-based categorization (most specific first)

            # 0. Explicit exclusions (non-equipment items that slipped through)
            if any(x in name for x in ['fuel tanker', 'total', 'artillery tractor']):
                continue  # Skip this item entirely

            # 1. Infantry weapons (rifles, LMGs, ATRs, SMGs)
            if any(x in name for x in ['rifle', 'bren', 'boys', 'thompson', 'mp40', 'mp38', 'sten', 'carcano', 'enfield']):
                category = 'Infantry Weapons'
            # 2. Tanks (actual armored fighting vehicles with "tank" in name)
            elif any(x in name for x in [' tank', 'panzer', 'sherman', 'matilda', 'valentine', 'crusader', 'grant', 'stuart', 'tiger']):
                # But exclude "fuel tankers" and metadata
                if 'tanker' not in name and 'total' not in name:
                    category = 'Tanks'
                else:
                    category = 'Support Equipment'
            elif 'tank' in eq_type and 'tank' not in eq_category and 'tanker' not in name:
                category = 'Tanks'
            # 3. Guns & Artillery (towed/self-propelled guns, howitzers, mortars)
            elif any(x in name for x in ['pounder', 'howitzer', 'mortar', 'pak', 'flak', 'gun', 'artillery']):
                category = 'Guns & Artillery'
            elif any(x in eq_type for x in ['gun', 'artillery', 'mortar', 'howitzer']):
                category = 'Guns & Artillery'
            elif any(x in eq_category for x in ['anti_tank', 'anti_aircraft', 'field_artillery', 'heavy_artillery']):
                category = 'Guns & Artillery'
            # 4. Vehicles (trucks, cars, halftracks, transporters - NOT tanks)
            elif any(x in name for x in ['truck', 'lorry', 'car', 'halftrack', 'carrier', 'transporter', 'tractor', 'motorcycle']):
                category = 'Vehicles'
            elif any(x in eq_type for x in ['vehicle', 'car', 'halftrack', 'truck']):
                category = 'Vehicles'
            # 5. Support equipment
            elif any(x in name for x in ['ambulance', 'workshop', 'tanker', 'fuel', 'water', 'command']):
                category = 'Support Equipment'
            # 6. Default fallback
            else:
                category = 'Other Equipment'

            categories[category].append(equipment)

        return categories

    def generate_datacard_markdown(self, equipment: Dict, experience: str = 'r') -> str:
        """
        Generate markdown datacard for equipment.

        Args:
            equipment: Equipment dict
            experience: Experience level (i/r/v/e)

        Returns:
            Markdown formatted datacard
        """
        cursor = self.conn.cursor()

        # Get BattleGroup stats + crew + production info
        cursor.execute("""
            SELECT
                eb.armor_front, eb.armor_side, eb.armor_rear,
                eb.armor_turret_front,
                eb.off_road_movement, eb.road_movement,
                eb.he_dice, eb.he_target, eb.he_format,
                eb.ap_0_10, eb.ap_10_20, eb.ap_20_30,
                eb.ap_30_40, eb.ap_40_50, eb.ap_50_70,
                eb.points_regular, eb.points_inexperienced,
                eb.points_veteran, eb.points_elite,
                eb.battle_rating_regular, eb.battle_rating_inexperienced,
                eb.battle_rating_veteran, eb.battle_rating_elite,
                e.crew, e.production_start, e.production_end
            FROM equipment_battlegroup eb
            JOIN equipment e ON eb.equipment_id = e.canonical_id
            WHERE eb.equipment_id = ?
        """, (equipment['canonical_id'],))

        row = cursor.fetchone()
        if not row:
            return f"<!-- Datacard not available for {equipment['name']} -->\n"

        # Get points/BR for experience level
        exp_map = {
            'i': ('points_inexperienced', 'battle_rating_inexperienced'),
            'r': ('points_regular', 'battle_rating_regular'),
            'v': ('points_veteran', 'battle_rating_veteran'),
            'e': ('points_elite', 'battle_rating_elite')
        }
        points_col, br_col = exp_map[experience]

        points = row[points_col]
        br = row[br_col]

        # Get main gun - try multiple sources
        main_gun = None

        # Source 1: equipment_guns table (if populated)
        cursor.execute("""
            SELECT g.name, g.caliber_mm
            FROM equipment_guns eg
            JOIN guns g ON eg.gun_id = g.gun_id
            WHERE eg.equipment_id = ? AND eg.mount_type = 'main'
            LIMIT 1
        """, (equipment['canonical_id'],))
        gun_row = cursor.fetchone()
        if gun_row:
            main_gun = gun_row['name']

        # Source 2: bg_reference_vehicles (JSON weapons field)
        if not main_gun:
            # Try exact match first, then fuzzy match
            search_terms = [equipment['name']]

            # For variants, also try base model name
            # e.g., "Panzer III Command" -> also try "Panzer III"
            import re
            base_name_match = re.match(r'(.*?(?:Panzer|Tank|Sherman|Matilda|Valentine|Crusader|Stuart))\s+(?:I+|Command|CS|AA)', equipment['name'], re.IGNORECASE)
            if base_name_match:
                search_terms.append(base_name_match.group(1))

            ref_rows = []
            for search_term in search_terms:
                cursor.execute("""
                    SELECT weapons
                    FROM bg_reference_vehicles
                    WHERE name LIKE ?
                    ORDER BY LENGTH(weapons) DESC
                """, (f"%{search_term}%",))
                ref_rows.extend(cursor.fetchall())
                if ref_rows:
                    break  # Stop if we found matches

            for ref_row in ref_rows:
                if ref_row and ref_row['weapons']:
                    try:
                        import json
                        weapons = json.loads(ref_row['weapons'])
                        # Find main gun (usually turret-mounted, not MG)
                        for weapon in weapons:
                            mount = weapon.get('mount', '').lower()
                            weapon_name = weapon.get('weapon', '')
                            # Look for turret-mounted weapon that's not just "MG"
                            if 'turret' in mount and weapon_name.upper() != 'MG':
                                main_gun = weapon_name
                                break
                        # If we found a gun, stop searching
                        if main_gun:
                            break
                    except (json.JSONDecodeError, TypeError):
                        continue

        # For towed guns, the gun IS the equipment
        if not main_gun and any(x in equipment['name'].lower() for x in ['pak', 'pounder', 'howitzer', 'flak']):
            # Extract caliber from name if present
            import re
            caliber_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:mm|cm|inch|pounder|pdr)', equipment['name'], re.IGNORECASE)
            if caliber_match:
                main_gun = f"{caliber_match.group(1)} gun"
            else:
                main_gun = "Self (towed gun)"

        # Fallback
        if not main_gun:
            main_gun = 'None'

        # Get secondary weapons
        cursor.execute("""
            SELECT g.name, eg.mount_type
            FROM equipment_guns eg
            JOIN guns g ON eg.gun_id = g.gun_id
            WHERE eg.equipment_id = ? AND eg.mount_type != 'main'
            ORDER BY eg.mount_type
        """, (equipment['canonical_id'],))

        secondary = cursor.fetchall()

        # If no secondary weapons, try bg_reference_vehicles
        if not secondary:
            # Get the entry with most complete weapon data (longest JSON)
            cursor.execute("""
                SELECT weapons
                FROM bg_reference_vehicles
                WHERE name LIKE ?
                ORDER BY LENGTH(weapons) DESC
                LIMIT 1
            """, (f"%{equipment['name']}%",))
            ref_row = cursor.fetchone()
            if ref_row and ref_row['weapons']:
                try:
                    import json
                    weapons = json.loads(ref_row['weapons'])
                    # Get secondary weapons (MGs, etc.)
                    secondary = []
                    for weapon in weapons:
                        mount = weapon.get('mount', 'Unknown')
                        weapon_name = weapon.get('weapon', 'Unknown')
                        # Get all weapons except the main gun we already extracted
                        # Include co-axial/bow MGs and other secondary armament
                        if 'turret' not in mount.lower() or weapon_name.upper() == 'MG' or weapon_name == main_gun:
                            if weapon_name.upper() != 'MG' or 'mg' in weapon_name.lower():
                                # Only add if it's not the duplicate of main_gun
                                if weapon_name != main_gun:
                                    secondary.append({'name': weapon_name, 'mount': mount})
                except (json.JSONDecodeError, TypeError):
                    pass

        # Build armament table rows
        main_gun_mount = 'Turret' if main_gun != 'None' and main_gun != 'Self (towed gun)' else '-'
        armament_rows = [f"| {main_gun} | {main_gun_mount} | - |"]

        for sec in secondary:
            if isinstance(sec, dict):
                sec_name = sec.get('name', 'Unknown')
                sec_mount = sec.get('mount', 'Unknown')
            else:
                sec_name = sec['name']
                sec_mount = sec[1] if len(sec) > 1 else 'Unknown'
            armament_rows.append(f"| {sec_name} | {sec_mount.title()} | - |")

        armament_table = '\n'.join(armament_rows)

        # Get special rules
        cursor.execute("""
            SELECT sr.name, sr.description
            FROM equipment_special_rules esr
            JOIN bg_special_rules sr ON esr.rule_id = sr.rule_id
            WHERE esr.equipment_id = ?
            ORDER BY sr.name
        """, (equipment['canonical_id'],))

        rules = cursor.fetchall()
        special_rules = []
        if rules:
            special_rules.append("\n**Special Rules:**")
            for rule in rules:
                special_rules.append(f"- **{rule['name']}**: {rule['description']}")

        special_rules_section = '\n'.join(special_rules) if special_rules else ''

        # Format values
        armor_front = row['armor_front'] or '-'
        armor_side = row['armor_side'] or '-'
        armor_rear = row['armor_rear'] or '-'
        off_road = row['off_road_movement'] or '-'
        road = row['road_movement'] or '-'
        he_format = row['he_format'] or '-'

        # Get crew count (by column name - using row_factory = sqlite3.Row)
        crew_count = row['crew'] if 'crew' in row.keys() and row['crew'] else 'Unknown'

        # Get production dates (by column name)
        prod_start = row['production_start'] if 'production_start' in row.keys() else None
        prod_end = row['production_end'] if 'production_end' in row.keys() else None

        if prod_start and prod_end:
            production_period = f"{prod_start}-{prod_end}"
        elif prod_start:
            production_period = f"{prod_start}-present"
        else:
            production_period = "1940-1945"

        ap_vals = []
        for col in ['ap_0_10', 'ap_10_20', 'ap_20_30', 'ap_30_40', 'ap_40_50', 'ap_50_70']:
            val = row[col]
            ap_vals.append(str(val) if val is not None else '-')

        # Determine equipment type label
        eq_type = equipment.get('equipment_type', '')
        if eq_type:
            type_label = eq_type.replace('_', ' ').title()
        else:
            type_label = "Vehicle"

        # Generate markdown using template
        template = f"""## {equipment['name'].upper()}

**{production_period}** | **Standard production version**

| TYPE | MOVEMENT | | | ARMOUR | | | |
|------|----------|----------|----------|--------|---|---|---|
| | **Off-Road** | **Road** | **Special** | **F** | **S** | **R** | **Weapon** |
| {type_label} | {off_road}" | {road}" | - | {armor_front} | {armor_side} | {armor_rear} | {main_gun} |

### ARMAMENT

| Weapon | Mount | Ammo |
|--------|-------|------|
{armament_table}

### WEAPON PERFORMANCE

| WEAPON | AMMO | HE | RANGE | | | | | |
|--------|------|----|----|----|----|----|----|----|
| | | | **0-10"** | **10-20"** | **20-30"** | **30-40"** | **40-50"** | **50-70"** |
| {main_gun} | HE/AP | {he_format} | {ap_vals[0]} | {ap_vals[1]} | {ap_vals[2]} | {ap_vals[3]} | {ap_vals[4]} | {ap_vals[5]} |

**Points:** {points} | **Battle Rating:** {br} | **Crew:** {crew_count}{special_rules_section}

---
"""

        return template

    def generate_book_datacards(self, battle_key: str):
        """
        Generate all datacards for a battle book.

        Args:
            battle_key: Battle key
        """
        battle = BATTLES[battle_key]
        print(f"\n{'='*70}")
        print(f"Generating datacards for: {battle['name']}")
        print(f"{'='*70}\n")

        # Get equipment
        categorized_equipment = self.get_all_equipment_for_battle(battle_key)

        # Create output directory
        output_dir = OUTPUT_BASE / battle['output_dir'] / 'chapter2'
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nOutput directory: {output_dir}")

        # Generate datacards by category
        for category, equipment_list in categorized_equipment.items():
            # Deduplicate by canonical_id
            seen_ids = set()
            unique_equipment = []
            for equipment in equipment_list:
                if equipment['canonical_id'] not in seen_ids:
                    seen_ids.add(equipment['canonical_id'])
                    unique_equipment.append(equipment)

            print(f"\n{category}: {len(unique_equipment)} items (deduplicated from {len(equipment_list)})")

            # Sort by nation then name
            unique_equipment.sort(key=lambda x: (x['nation'], x['name']))

            # Generate markdown file
            category_file = category.lower().replace(' ', '_').replace('&', 'and') + '.md'
            output_file = output_dir / category_file

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# {category}\n\n")

                current_nation = None
                for equipment in unique_equipment:
                    # Add nation header
                    if equipment['nation'] != current_nation:
                        current_nation = equipment['nation']
                        f.write(f"\n## {current_nation.title()}\n\n")

                    # Generate datacard
                    datacard = self.generate_datacard_markdown(equipment, 'r')
                    f.write(datacard)
                    f.write('\n')

            print(f"  -> {output_file.name}")

        print(f"\n{'='*70}")
        print(f"Datacard generation complete for {battle['name']}")
        print(f"{'='*70}\n")

    def generate_all_books(self):
        """Generate datacards for all 4 battle books."""
        for battle_key in BATTLES.keys():
            self.generate_book_datacards(battle_key)

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 7: Book Equipment Datacard Generator"
    )
    parser.add_argument(
        "--battle",
        choices=['battleaxe', 'crusader', 'gazala', 'alamein'],
        help="Generate datacards for specific battle"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate datacards for all 4 battles"
    )

    args = parser.parse_args()

    generator = BookDatacardGenerator()

    try:
        if args.all:
            generator.generate_all_books()
        elif args.battle:
            generator.generate_book_datacards(args.battle)
        else:
            parser.print_help()
            return 1
    finally:
        generator.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
