#!/usr/bin/env python3
"""
Phase 9B Step 7: Book Equipment Datacard Generator v6.1

V6.1 changes (November 2025):
- Add weapon fallback: If bg_reference_vehicles doesn't have weapon data, fallback to bg_builder_vehicles/bg_builder_weapons
- Enables datacards for unlinked vehicles (e.g., M4A3E2 Sherman Jumbo) while preserving manual extraction priority
- Non-breaking: Fallback only activates when main weapon is None or missing
- Filters out infantry weapons (MG, MMG, HMG, LMG) from main gun fallback

V6 changes:
- Use bg_builder_vehicles.name as primary lookup key instead of equipment.canonical_id
- Simplify equipment extraction workflow to use builder database directly

V5.5 changes:
- Add silhouette images from data/assets/tank_silhouettes/

V5.4 changes:
- Display armor_modifier (e.g., "Open-topped") below armor values

Generates BattleGroup datacards for all equipment used in the 12 battle books.

Usage:
    python generate_book_datacards_v6.py --battle battleaxe
    python generate_book_datacards_v6.py --all
"""

import sqlite3
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Import penetration converter for on-the-fly AP calculation
from scripts.battlegroup.conversion.penetration_converter import convert_penetration
from scripts.battlegroup.conversion.he_weight_classifier import classify_he_weight, get_he_weight_and_effectiveness
from scripts.battlegroup.conversion.he_calculator import calculate_he_effect

DATABASE_PATH = project_root / "database" / "master_database.db"
UNITS_DIR = project_root / "data" / "output" / "units"
OUTPUT_BASE = project_root / "books"

# Battle definitions with quarters (all 12 North Africa battles)
BATTLES = {
    'compass': {
        'name': 'Operation Compass',
        'quarters': ['1940q4'],
        'output_dir': 'compass'
    },
    'sonnenblume': {
        'name': 'Operation Sonnenblume',
        'quarters': ['1941q1'],
        'output_dir': 'sonnenblume'
    },
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
    'tobruk': {
        'name': 'Fall of Tobruk',
        'quarters': ['1942q2'],
        'output_dir': 'tobruk'
    },
    'alamein': {
        'name': 'First El Alamein',
        'quarters': ['1942q3'],
        'output_dir': 'first_alamein'
    },
    'alam_halfa': {
        'name': 'Battle of Alam Halfa',
        'quarters': ['1942q3'],
        'output_dir': 'alam_halfa'
    },
    'second_alamein': {
        'name': 'Second Battle of El Alamein',
        'quarters': ['1942q4'],
        'output_dir': 'second_alamein'
    },
    'torch': {
        'name': 'Operation Torch',
        'quarters': ['1942q4'],
        'output_dir': 'torch'
    },
    'tunisia': {
        'name': 'Tunisia Campaign',
        'quarters': ['1943q1'],
        'output_dir': 'tunisia'
    },
    'mareth': {
        'name': 'Battle of Mareth Line',
        'quarters': ['1943q1'],
        'output_dir': 'mareth'
    }
}

NATIONS = ['german', 'british', 'italian', 'american', 'french']


class BookDatacardGenerator:
    """Generate equipment datacards for battle books."""

    def __init__(self, database_path=None):
        """Initialize generator.

        Args:
            database_path: Optional path to database file.
                          If not provided, uses default DATABASE_PATH.
        """
        db_path = database_path or DATABASE_PATH
        self.conn = sqlite3.connect(db_path)
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
            elif any(x in name for x in [' tank', 'panzer', 'sherman', 'matilda', 'valentine', 'crusader', 'grant', 'stuart', 'tiger', 'cruiser', 'churchill']):
                # But exclude "fuel tankers" and metadata
                if 'tanker' not in name and 'total' not in name:
                    category = 'Tanks'
                else:
                    category = 'Support Equipment'
            elif 'tank' in eq_type and 'tanker' not in name:
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
            equipment: Equipment dict with 'bg_builder_vehicle_id' or 'name' key
            experience: Experience level (i/r/v/e)

        Returns:
            Markdown formatted datacard
        """
        cursor = self.conn.cursor()

        # V6 Change: Use bg_builder_vehicle_id as primary lookup
        # Get data directly from bg_builder_vehicles
        if 'bg_builder_vehicle_id' in equipment:
            vehicle_id = equipment['bg_builder_vehicle_id']
        else:
            # Fallback: lookup by name
            cursor.execute("""
                SELECT id FROM bg_builder_vehicles WHERE name = ?
            """, (equipment.get('name', ''),))
            result = cursor.fetchone()
            if not result:
                return f"<!-- Datacard not available for {equipment.get('name', 'Unknown')} -->\n"
            vehicle_id = result['id']

        # Get vehicle data from bg_builder_vehicles
        cursor.execute("""
            SELECT
                bgv.id, bgv.name,
                bgv.armor_front, bgv.armor_side, bgv.armor_rear,
                bgv.movement_off_road, bgv.movement_road
            FROM bg_builder_vehicles bgv
            WHERE bgv.id = ?
        """, (vehicle_id,))

        row = cursor.fetchone()
        if not row:
            return f"<!-- Datacard not available for {equipment.get('name', 'Unknown')} -->\n"

        # V6: Use bg_builder_vehicles data directly (already queried)
        display_name = row['name']
        armor_front_val = row['armor_front']
        armor_side_val = row['armor_side']
        armor_rear_val = row['armor_rear']
        off_road_val = row['movement_off_road']
        road_val = row['movement_road']
        crew_count = 'Unknown'  # bg_builder_vehicles doesn't have crew_count

        # Get metadata AND nation from bg_reference_vehicles if linked
        year_range = ''
        dc_meta = ''
        armor_modifier = None
        armor_side_schurzen = None

        # V6: Check for nation override first (user-specified nation takes priority)
        nation = equipment.get('nation_override') if equipment.get('nation_override') else None

        cursor.execute("""
            SELECT year_range, dc_meta, armor_modifier, nation
            FROM bg_reference_vehicles
            WHERE bg_builder_id = ?
        """, (vehicle_id,))
        ref_data = cursor.fetchone()
        if ref_data:
            year_range = ref_data['year_range'] or ''
            dc_meta = ref_data['dc_meta'] or ''
            armor_modifier = ref_data['armor_modifier']
            # Handle nation - may be comma-separated list (e.g., "canadian, british, american")
            # Only set nation from database if not already overridden by user
            if not nation and ref_data['nation']:
                nation_str = ref_data['nation'].lower()
                # Take first nation from comma-separated list
                if ',' in nation_str:
                    # Priority: american > british > german > italian > french
                    if 'american' in nation_str:
                        nation = 'american'
                    elif 'british' in nation_str:
                        nation = 'british'
                    elif 'german' in nation_str:
                        nation = 'german'
                    elif 'italian' in nation_str:
                        nation = 'italian'
                    elif 'french' in nation_str:
                        nation = 'french'
                    else:
                        nation = nation_str.split(',')[0].strip()
                else:
                    nation = nation_str.strip()

        # Get points/BR for experience level from bg_builder_vehicle_costs
        # Default to regular experience if not specified
        exp_map = {
            'i': 'Inexperienced',
            'r': 'Regular',
            'v': 'Veteran',
            'e': 'Elite'
        }
        experience_level = exp_map.get(experience, 'Regular')

        # V6: Get nation - Priority order:
        # 1. bg_reference_vehicles.nation (set above)
        # 2. bg_builder_vehicle_costs.force_name
        # 3. Fallback to 'british'

        if not nation:
            # Try to get from force_name in bg_builder_vehicle_costs
            cursor.execute("""
                SELECT force_name
                FROM bg_builder_vehicle_costs
                WHERE vehicle_id = ?
                LIMIT 1
            """, (vehicle_id,))
            force_row = cursor.fetchone()

            if force_row and force_row['force_name']:
                force_name_lower = force_row['force_name'].lower()
                if 'german' in force_name_lower or 'panzer' in force_name_lower or 'fallschirmj' in force_name_lower:
                    nation = 'german'
                elif 'italian' in force_name_lower or 'italy' in force_name_lower:
                    nation = 'italian'
                elif 'american' in force_name_lower or 'us ' in force_name_lower or 'usa' in force_name_lower:
                    nation = 'american'
                elif 'french' in force_name_lower or 'france' in force_name_lower:
                    nation = 'french'
                else:
                    nation = 'british'
            else:
                nation = 'british'  # Final fallback

        # Query bg_builder_vehicle_costs for points/BR
        # Map experience to column names
        cost_col = f'cost_{experience.lower()}' if experience in ['i', 'r', 'v', 'e'] else 'cost_regular'
        br_col = f'br_{experience.lower()}' if experience in ['i', 'r', 'v', 'e'] else 'br_regular'

        # Translate single-letter experience codes to full column suffixes
        exp_suffix_map = {
            'i': 'inexperienced',
            'r': 'regular',
            'v': 'veteran',
            'e': 'elite'
        }
        suffix = exp_suffix_map.get(experience, 'regular')

        cursor.execute(f"""
            SELECT cost_{suffix}, br_{suffix}
            FROM bg_builder_vehicle_costs
            WHERE vehicle_id = ?
            LIMIT 1
        """, (vehicle_id,))

        cost_row = cursor.fetchone()
        if cost_row:
            points = cost_row[f'cost_{suffix}']
            br = cost_row[f'br_{suffix}']
        else:
            # Fallback to None if no cost data
            points = None
            br = None

        # V6: Get weapons from bg_reference_vehicles (if linked) or extract from bg_builder_vehicles
        main_gun = None
        main_gun_ammo = None
        main_gun_mount = None  # Track actual mount type (Turret, Hull, etc.)
        weapon_data = None  # Store full weapon data for penetration lookup

        # Source 1: bg_reference_vehicles (if linked via bg_builder_id)
        cursor.execute("""
            SELECT weapon_1, weapon_2, weapon_3, weapon_4,
                   mount_1, mount_2, mount_3, mount_4,
                   ammo_1, ammo_2, ammo_3, ammo_4
            FROM bg_reference_vehicles
            WHERE bg_builder_id = ?
        """, (vehicle_id,))
        ref_row = cursor.fetchone()

        if ref_row:
                # Build weapons list from weapon_1-4 fields
                weapons_list = []
                for i in range(1, 5):
                    weapon = ref_row[f'weapon_{i}']
                    mount = ref_row[f'mount_{i}']
                    ammo = ref_row[f'ammo_{i}']
                    if weapon:
                        weapons_list.append({
                            'weapon': weapon,
                            'mount': mount or 'Unknown',
                            'ammo': ammo
                        })

                # Find main gun - prioritize turret, fallback to hull (for assault guns/tank destroyers)
                # First pass: look for turret-mounted main gun (tanks)
                for weapon_data in weapons_list:
                    mount = weapon_data.get('mount', '').lower()
                    weapon_name = weapon_data.get('weapon', '')
                    ammo = weapon_data.get('ammo', None)
                    if 'turret' in mount and weapon_name.upper() != 'MG':
                        main_gun = weapon_name
                        main_gun_ammo = ammo
                        main_gun_mount = weapon_data.get('mount', 'Turret')  # Preserve original mount case
                        break

                # Second pass: if no turret gun, look for hull-mounted main gun (assault guns)
                if not main_gun:
                    for weapon_data in weapons_list:
                        mount = weapon_data.get('mount', '').lower()
                        weapon_name = weapon_data.get('weapon', '')
                        ammo = weapon_data.get('ammo', None)
                        if 'hull' in mount and weapon_name.upper() != 'MG':
                            main_gun = weapon_name
                            main_gun_ammo = ammo
                            main_gun_mount = weapon_data.get('mount', 'Hull')  # Preserve original mount case
                            break

        # V6.1 FALLBACK: If no weapons from bg_reference_vehicles, try bg_builder_vehicles
        fallback_weapon_id = None  # Track if we used fallback
        if not main_gun or main_gun == 'None':
            cursor.execute("""
                SELECT weapon_1_id, weapon_2_id, weapon_3_id, weapon_4_id
                FROM bg_builder_vehicles
                WHERE id = ?
            """, (vehicle_id,))
            builder_weapons_row = cursor.fetchone()

            if builder_weapons_row:
                # Try each weapon ID until we find a main gun (skip MGs)
                for i in range(1, 5):
                    weapon_id = builder_weapons_row[f'weapon_{i}_id']
                    if weapon_id:
                        cursor.execute("""
                            SELECT weapon_name
                            FROM bg_builder_weapons
                            WHERE weapon_id = ?
                        """, (weapon_id,))
                        fallback_weapon_data = cursor.fetchone()

                        if fallback_weapon_data and fallback_weapon_data['weapon_name']:
                            weapon_name = fallback_weapon_data['weapon_name']
                            # Skip machine guns - we want the main gun (cannon/AT gun)
                            if weapon_name.upper() not in ['MG', 'MMG', 'HMG', 'LMG']:
                                main_gun = weapon_name
                                main_gun_mount = 'Turret'  # Default assumption for builder data
                                main_gun_ammo = None  # Not available in bg_builder_vehicles
                                fallback_weapon_id = weapon_id  # Remember we used fallback
                                break  # Found main gun, stop searching

        # Look up weapon in bg_weapon_name_lookup to get HE/AP data from bg_builder_weapons
        bg_weapon_he_ap_data = None
        if main_gun and main_gun not in ['None', '-', '']:
            # If we used fallback, directly query with weapon_id
            if fallback_weapon_id:
                cursor.execute("""
                    SELECT weapon_name, he_type, he_effect,
                           he_strength_0, he_strength_10, he_strength_20,
                           he_strength_30, he_strength_40, he_strength_50,
                           ap_effect, ap_strength_0, ap_strength_10, ap_strength_20,
                           ap_strength_30, ap_strength_40, ap_strength_50
                    FROM bg_builder_weapons
                    WHERE weapon_id = ?
                """, (fallback_weapon_id,))
                bg_weapon_he_ap_data = cursor.fetchone()
            else:
                # Otherwise use lookup table (original method for manual extraction data)
                cursor.execute("""
                    SELECT bg_builder_weapon_id
                    FROM bg_weapon_name_lookup
                    WHERE bg_reference_name = ?
                """, (main_gun,))
                lookup_result = cursor.fetchone()

                if lookup_result and lookup_result['bg_builder_weapon_id']:
                    # Get HE/AP data from bg_builder_weapons
                    cursor.execute("""
                        SELECT weapon_name, he_type, he_effect,
                               he_strength_0, he_strength_10, he_strength_20,
                               he_strength_30, he_strength_40, he_strength_50,
                               ap_effect, ap_strength_0, ap_strength_10, ap_strength_20,
                               ap_strength_30, ap_strength_40, ap_strength_50
                        FROM bg_builder_weapons
                        WHERE weapon_id = ?
                    """, (lookup_result['bg_builder_weapon_id'],))
                    bg_weapon_he_ap_data = cursor.fetchone()

        # Fallback
        if not main_gun:
            main_gun = 'None'

        # Get secondary weapons from bg_reference_vehicles (already queried above as ref_row)
        secondary = []
        if ref_row:
                # Build weapons list from weapon_1-4 fields
                secondary = []
                for i in range(1, 5):
                    weapon_name = ref_row[f'weapon_{i}']
                    mount = ref_row[f'mount_{i}']
                    ammo = ref_row[f'ammo_{i}']
                    if weapon_name:
                        # Get all weapons except the main gun we already extracted
                        # Include co-axial/bow MGs and other secondary armament
                        if weapon_name != main_gun and weapon_name.upper() != 'NONE':
                            secondary.append({
                                'name': weapon_name,
                                'mount': mount or 'Unknown',
                                'ammo': ammo
                            })

        # V6.1 FALLBACK: Get secondary weapons from bg_builder_vehicles if ref_row was empty
        if not secondary and not ref_row:
            cursor.execute("""
                SELECT weapon_1_id, weapon_2_id, weapon_3_id, weapon_4_id
                FROM bg_builder_vehicles
                WHERE id = ?
            """, (vehicle_id,))
            builder_sec_row = cursor.fetchone()

            if builder_sec_row:
                for i in range(1, 5):
                    weapon_id = builder_sec_row[f'weapon_{i}_id']
                    if weapon_id:
                        cursor.execute("""
                            SELECT weapon_name
                            FROM bg_builder_weapons
                            WHERE weapon_id = ?
                        """, (weapon_id,))
                        sec_weapon_data = cursor.fetchone()

                        if sec_weapon_data and sec_weapon_data['weapon_name']:
                            weapon_name = sec_weapon_data['weapon_name']
                            # Include all weapons except the main gun we already found
                            if weapon_name != main_gun:
                                secondary.append({
                                    'name': weapon_name,
                                    'mount': 'Unknown',  # bg_builder doesn't track mount type
                                    'ammo': None  # Not available in bg_builder_vehicles
                                })

        # V6: Special rules - parse from bg_builder_vehicles.special_rules TEXT field
        # Get special_rules from the row we already fetched
        cursor.execute("""
            SELECT special_rules
            FROM bg_builder_vehicles
            WHERE id = ?
        """, (vehicle_id,))
        special_rules_row = cursor.fetchone()
        special_rules_line = special_rules_row['special_rules'] if special_rules_row and special_rules_row['special_rules'] else ''

        # Format armor values (using values from bg_reference_vehicles if available)
        armor_front = armor_front_val or '-'
        armor_side = armor_side_val or '-'
        armor_rear = armor_rear_val or '-'

        # Handle Schürzen format: N(M) when armor_side_schurzen exists
        if armor_side_schurzen:
            armor_side = f"{armor_side}({armor_side_schurzen})"

        # V6: Movement values - use vehicle speeds from bg_builder_vehicles
        if True:  # Simplified - all entries in bg_builder_vehicles are vehicles
            # Use vehicle speeds from bg_builder_vehicles
            if off_road_val is not None:
                off_road = f"{off_road_val}\""
            else:
                off_road = '-'
            if road_val is not None:
                road = f"{road_val}\""
            else:
                road = '-'

        # V6: Crew count already retrieved above
        # crew_count variable already set from bg_builder_vehicles query

        # V6: Production dates - not in bg_builder_vehicles, use default
        production_period = year_range if year_range else "1940-1945"

        # Get penetration values - PRIORITY: use bg_builder_weapons data if available
        ap_vals = []
        he_weight = '-'
        he_effectiveness = '-'
        he_range_vals = ['-', '-', '-', '-', '-', '-']

        # PRIORITY 1: Use bg_builder_weapons data if we found it via lookup
        if bg_weapon_he_ap_data:
            # Extract AP values from bg_builder_weapons
            ap_vals = [
                str(bg_weapon_he_ap_data['ap_strength_0']) if bg_weapon_he_ap_data['ap_strength_0'] is not None else '-',
                str(bg_weapon_he_ap_data['ap_strength_10']) if bg_weapon_he_ap_data['ap_strength_10'] is not None else '-',
                str(bg_weapon_he_ap_data['ap_strength_20']) if bg_weapon_he_ap_data['ap_strength_20'] is not None else '-',
                str(bg_weapon_he_ap_data['ap_strength_30']) if bg_weapon_he_ap_data['ap_strength_30'] is not None else '-',
                str(bg_weapon_he_ap_data['ap_strength_40']) if bg_weapon_he_ap_data['ap_strength_40'] is not None else '-',
                str(bg_weapon_he_ap_data['ap_strength_50']) if bg_weapon_he_ap_data['ap_strength_50'] is not None else '-'
            ]

            # Extract HE values
            he_type = bg_weapon_he_ap_data['he_type'] or ''
            he_effect = bg_weapon_he_ap_data['he_effect'] or ''

            # Extract text inside brackets for he_weight (e.g., "HE [VL]" -> "VL")
            if he_type and '[' in he_type and ']' in he_type:
                match = re.search(r'\[([^\]]+)\]', he_type)
                he_weight = match.group(1) if match else he_type
            else:
                he_weight = he_type if he_type else '-'

            he_effectiveness = he_effect if he_effect else '-'

            # Get HE range values
            he_range_vals = [
                str(bg_weapon_he_ap_data['he_strength_0']) if bg_weapon_he_ap_data['he_strength_0'] is not None else '-',
                str(bg_weapon_he_ap_data['he_strength_10']) if bg_weapon_he_ap_data['he_strength_10'] is not None else '-',
                str(bg_weapon_he_ap_data['he_strength_20']) if bg_weapon_he_ap_data['he_strength_20'] is not None else '-',
                str(bg_weapon_he_ap_data['he_strength_30']) if bg_weapon_he_ap_data['he_strength_30'] is not None else '-',
                str(bg_weapon_he_ap_data['he_strength_40']) if bg_weapon_he_ap_data['he_strength_40'] is not None else '-',
                str(bg_weapon_he_ap_data['he_strength_50']) if bg_weapon_he_ap_data['he_strength_50'] is not None else '-'
            ]

        # PRIORITY 2 (FALLBACK): If no bg_weapon_he_ap_data, use defaults
        gun_data = None  # V6: No equipment_guns table in new architecture

        if gun_data:
            # V6: This block won't execute since gun_data is None
            # All penetration data comes from bg_weapon_he_ap_data above
            pass
        else:
            # V6: No gun data found, use defaults
            if not ap_vals:  # Only set defaults if not already populated
                ap_vals = ['-', '-', '-', '-', '-', '-']

        # Determine equipment type label (for armament table)
        eq_type = equipment.get('equipment_type', '')
        if eq_type:
            type_label = eq_type.replace('_', ' ').title()
        else:
            type_label = "Vehicle"

        # Build armament table rows for HTML (main gun + secondary weapons)
        # Now that we have all the data: off_road, road, armor values, type_label
        has_main_gun = main_gun and main_gun != 'None' and main_gun != '-'
        has_secondary = len(secondary) > 0
        has_weapons = has_main_gun or has_secondary

        armament_rows_html = []
        if has_weapons:
            # First row: vehicle + movement + armor + weapon
            if has_main_gun:
                # Use tracked mount if available, otherwise default to Turret (or - for towed guns)
                if not main_gun_mount:
                    main_gun_mount = 'Turret' if main_gun != 'None' and main_gun != 'Self (towed gun)' else '-'
                main_gun_ammo_display = str(main_gun_ammo) if main_gun_ammo is not None else '-'

                armament_rows_html.append(f"""<tr>
<td>{type_label}</td>
<td>{off_road}</td>
<td>{road}</td>
<td>-</td>
<td>{{armor_front}}</td>
<td>{{armor_side}}</td>
<td>{{armor_rear}}</td>
<td>{main_gun}</td>
<td>{main_gun_mount}</td>
<td>{main_gun_ammo_display}</td>
</tr>""")

                # Add armor modifier row if present (e.g., "Open-topped")
                if armor_modifier and armor_modifier.strip() and armor_modifier != '-':
                    armament_rows_html.append(f"""<tr class="armor-modifier-row">
<td></td>
<td></td>
<td></td>
<td></td>
<td colspan="3" style="text-align: center; font-style: italic; font-size: 7px;">{armor_modifier}</td>
<td></td>
<td></td>
<td></td>
</tr>""")
            elif has_secondary:
                # No main gun, but has secondary weapons - show first secondary in first row
                first_sec = secondary[0]
                sec_name = first_sec.get('name', 'Unknown')
                sec_mount = first_sec.get('mount', 'Unknown')
                sec_ammo = first_sec.get('ammo', None)
                sec_ammo_display = str(sec_ammo) if sec_ammo is not None else '-'

                armament_rows_html.append(f"""<tr>
<td>{type_label}</td>
<td>{off_road}</td>
<td>{road}</td>
<td>-</td>
<td>{{armor_front}}</td>
<td>{{armor_side}}</td>
<td>{{armor_rear}}</td>
<td>{sec_name}</td>
<td>{sec_mount.title()}</td>
<td>{sec_ammo_display}</td>
</tr>""")

                # Add armor modifier row if present (e.g., "Open-topped")
                if armor_modifier and armor_modifier.strip() and armor_modifier != '-':
                    armament_rows_html.append(f"""<tr class="armor-modifier-row">
<td></td>
<td></td>
<td></td>
<td></td>
<td colspan="3" style="text-align: center; font-style: italic; font-size: 7px;">{armor_modifier}</td>
<td></td>
<td></td>
<td></td>
</tr>""")

                # Remove first secondary from list so we don't duplicate it
                secondary = secondary[1:]

            # Additional rows: only weapon columns (empty vehicle/movement/armor cells)
            for sec in secondary:
                if isinstance(sec, dict):
                    # From bg_reference_vehicles JSON
                    sec_name = sec.get('name', 'Unknown')
                    sec_mount = sec.get('mount', 'Unknown')
                    sec_ammo = sec.get('ammo', None)
                else:
                    # From equipment_guns database query (Row object)
                    sec_name = sec['name']
                    sec_mount = sec['mount_type']
                    sec_ammo = sec['ammunition_count']
                sec_ammo_display = str(sec_ammo) if sec_ammo is not None else '-'

                armament_rows_html.append(f"""<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>{sec_name}</td>
<td>{sec_mount.title()}</td>
<td>{sec_ammo_display}</td>
</tr>""")
        else:
            # Soft-skinned/unarmed vehicle - single row
            armament_rows_html.append(f"""<tr>
<td>{type_label}</td>
<td>{off_road}</td>
<td>{road}</td>
<td>-</td>
<td>{{armor_front}}</td>
<td>{{armor_side}}</td>
<td>{{armor_rear}}</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>""")

            # Add armor modifier row if present (e.g., "Open-topped")
            if armor_modifier and armor_modifier.strip() and armor_modifier != '-':
                armament_rows_html.append(f"""<tr class="armor-modifier-row">
<td></td>
<td></td>
<td></td>
<td></td>
<td colspan="3" style="text-align: center; font-style: italic; font-size: 7px;">{armor_modifier}</td>
<td></td>
<td></td>
<td></td>
</tr>""")

        # Generate V5.5 datacard format
        # Build weapon performance table for ALL weapons with ammo
        weapon_table = ''

        # Collect all weapons with ammo for performance table
        weapons_for_table = []

        # Add main gun if it exists (V6.1: Include fallback weapons even without ammo data)
        if main_gun and main_gun not in ['-', 'None', ''] and (main_gun_ammo or fallback_weapon_id):
            weapons_for_table.append({
                'name': main_gun,
                'he_weight': he_weight,
                'he_effectiveness': he_effectiveness,
                'he_range_vals': he_range_vals,
                'ap_vals': ap_vals
            })

        # Add secondary weapons with ammo
        for sec_weapon in secondary:
            if sec_weapon.get('ammo'):  # Only include weapons with ammo
                sec_name = sec_weapon.get('name', '')

                # Look up weapon data in bg_weapon_name_lookup
                sec_he_weight = '-'
                sec_he_effectiveness = '-'
                sec_he_range_vals = ['-', '-', '-', '-', '-', '-']
                sec_ap_vals = ['-', '-', '-', '-', '-', '-']

                cursor.execute("""
                    SELECT bg_builder_weapon_id
                    FROM bg_weapon_name_lookup
                    WHERE bg_reference_name = ?
                """, (sec_name,))
                lookup_result = cursor.fetchone()

                if lookup_result and lookup_result['bg_builder_weapon_id']:
                    cursor.execute("""
                        SELECT weapon_name, he_type, he_effect,
                               he_strength_0, he_strength_10, he_strength_20,
                               he_strength_30, he_strength_40, he_strength_50,
                               ap_effect, ap_strength_0, ap_strength_10, ap_strength_20,
                               ap_strength_30, ap_strength_40, ap_strength_50
                        FROM bg_builder_weapons
                        WHERE weapon_id = ?
                    """, (lookup_result['bg_builder_weapon_id'],))
                    sec_weapon_data = cursor.fetchone()

                    if sec_weapon_data:
                        # Extract HE weight
                        he_type = sec_weapon_data['he_type'] or ''
                        if he_type and '[' in he_type and ']' in he_type:
                            match = re.search(r'\[([^\]]+)\]', he_type)
                            sec_he_weight = match.group(1) if match else he_type
                        else:
                            sec_he_weight = he_type if he_type else '-'

                        sec_he_effectiveness = sec_weapon_data['he_effect'] or '-'

                        # Extract HE range values
                        sec_he_range_vals = [
                            str(sec_weapon_data['he_strength_0']) if sec_weapon_data['he_strength_0'] is not None else '-',
                            str(sec_weapon_data['he_strength_10']) if sec_weapon_data['he_strength_10'] is not None else '-',
                            str(sec_weapon_data['he_strength_20']) if sec_weapon_data['he_strength_20'] is not None else '-',
                            str(sec_weapon_data['he_strength_30']) if sec_weapon_data['he_strength_30'] is not None else '-',
                            str(sec_weapon_data['he_strength_40']) if sec_weapon_data['he_strength_40'] is not None else '-',
                            str(sec_weapon_data['he_strength_50']) if sec_weapon_data['he_strength_50'] is not None else '-'
                        ]

                        # Extract AP values
                        sec_ap_vals = [
                            str(sec_weapon_data['ap_strength_0']) if sec_weapon_data['ap_strength_0'] is not None else '-',
                            str(sec_weapon_data['ap_strength_10']) if sec_weapon_data['ap_strength_10'] is not None else '-',
                            str(sec_weapon_data['ap_strength_20']) if sec_weapon_data['ap_strength_20'] is not None else '-',
                            str(sec_weapon_data['ap_strength_30']) if sec_weapon_data['ap_strength_30'] is not None else '-',
                            str(sec_weapon_data['ap_strength_40']) if sec_weapon_data['ap_strength_40'] is not None else '-',
                            str(sec_weapon_data['ap_strength_50']) if sec_weapon_data['ap_strength_50'] is not None else '-'
                        ]

                weapons_for_table.append({
                    'name': sec_name,
                    'he_weight': sec_he_weight,
                    'he_effectiveness': sec_he_effectiveness,
                    'he_range_vals': sec_he_range_vals,
                    'ap_vals': sec_ap_vals
                })

        # Build weapon performance table if any weapons have ammo
        if weapons_for_table:
            # Build weapon rows
            weapon_rows = []
            for weapon in weapons_for_table:
                has_he = weapon['he_effectiveness'] and weapon['he_effectiveness'] not in ['-', '']

                # Add HE row if HE data exists
                if has_he:
                    weapon_rows.append(f"""<tr>
<td>{weapon['name']}</td>
<td>HE</td>
<td>{weapon['he_effectiveness']}</td>
<td>{weapon['he_range_vals'][0]}</td>
<td>{weapon['he_range_vals'][1]}</td>
<td>{weapon['he_range_vals'][2]}</td>
<td>{weapon['he_range_vals'][3]}</td>
<td>{weapon['he_range_vals'][4]}</td>
<td>{weapon['he_range_vals'][5]}</td>
</tr>
""")

                # Add AP row
                weapon_rows.append(f"""<tr>
<td>{weapon['name']}</td>
<td>AP</td>
<td>-</td>
<td>{weapon['ap_vals'][0]}</td>
<td>{weapon['ap_vals'][1]}</td>
<td>{weapon['ap_vals'][2]}</td>
<td>{weapon['ap_vals'][3]}</td>
<td>{weapon['ap_vals'][4]}</td>
<td>{weapon['ap_vals'][5]}</td>
</tr>
""")

            # Get HE weight for header (from first weapon with HE)
            header_he_weight = ''
            for weapon in weapons_for_table:
                if weapon['he_effectiveness'] and weapon['he_effectiveness'] not in ['-', '']:
                    header_he_weight = weapon['he_weight']
                    break

            weapon_table = f"""
<table>
<tr>
<th class="main-header">WEAPON</th>
<th class="main-header">AMMO</th>
<th class="main-header">HE</th>
<th class="main-header" colspan="6">RANGE</th>
</tr>
<tr>
<th></th>
<th></th>
<th>{header_he_weight}</th>
<th>0-10"</th>
<th>10-20"</th>
<th>20-30"</th>
<th>30-40"</th>
<th>40-50"</th>
<th>50-70"</th>
</tr>
{''.join(weapon_rows)}
</table>"""

        # V6: Nation already set above from bg_reference_vehicles or bg_builder_vehicle_costs
        # Do NOT override it here

        # Find silhouette image
        silhouette_html = '<span style="color: white; font-size: 10px;">🔲</span>'  # Default placeholder
        from pathlib import Path
        import base64

        # Try to find silhouette in data/assets/tank_silhouettes/{nation}/Side/{name}.png
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        silhouette_base = project_root / "data" / "assets" / "tank_silhouettes"

        # Try display_name first, then fall back to equipment name
        potential_names = [display_name, equipment.get('name', '')]

        for search_name in potential_names:
            if not search_name:
                continue
            # --- FILENAME SANITATION STEP ---
            # Replace illegal file path characters (like '/') with an underscore '_'
            search_name = search_name.replace('/', '_')
            # --------------------------------

            # Try exact match first
            silhouette_path = silhouette_base / nation / "Side" / f"{search_name}.png"
            if silhouette_path.exists():
                # Embed image as base64 data URI for portability
                with open(silhouette_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    silhouette_html = f'<img src="data:image/png;base64,{img_data}" alt="{search_name}">'
                break

            # Try case-insensitive search if exact match failed
            side_dir = silhouette_base / nation / "Side"
            if side_dir.exists():
                for file in side_dir.iterdir():
                    if file.name.lower() == f"{search_name.lower()}.png":
                        with open(file, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            silhouette_html = f'<img src="data:image/png;base64,{img_data}" alt="{search_name}">'
                        break
                if silhouette_html != '<span style="color: white; font-size: 10px;">🔲</span>':
                    break

        template = f"""<div class="datacard datacard-{nation}">
<div class="datacard-header">
<div class="datacard-silhouette">
{silhouette_html}
</div>
<div class="datacard-title-block">
<p class="datacard-title">{display_name.upper()}</p>
<p class="datacard-subtitle">{year_range}</p>
<p class="datacard-subtitle">{dc_meta}</p>
</div>
</div>

<table>
<tr>
<th class="main-header">VEHICLE</th>
<th class="main-header" colspan="3">MOVEMENT</th>
<th class="main-header" colspan="3">ARMOUR</th>
<th class="main-header" colspan="3">ARMAMENT</th>
</tr>
<tr>
<th></th>
<th>Off-Road</th>
<th>Road</th>
<th>Special</th>
<th>F</th>
<th>S</th>
<th>R</th>
<th>Weapon</th>
<th>Mount</th>
<th>Ammo</th>
</tr>
""" + '\n'.join([row.format(armor_front=armor_front, armor_side=armor_side, armor_rear=armor_rear) for row in armament_rows_html]) + f"""
</table>
{weapon_table}
<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> {points if points else '-'}</div>
<div class="footer-stat"><strong>BR:</strong> {br if br else '-'}</div>
</div>
</div>
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
        output_dir = OUTPUT_BASE / battle['output_dir'] / 'book' / 'src' / 'chapter2'
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
                # Write title
                f.write(f"# {category}\n\n")

                # Write CSS (EXACT copy from working SAMPLE_DATACARDS_V4.md)
                css = """<style>
@media print {
    @page {
        size: A4 landscape;
        margin: 10mm;
    }

    .datacard-grid {
        page-break-after: always;
    }

    .datacard {
        page-break-inside: avoid;
    }
}

.datacard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 20px 0;
}

.datacard {
    border: 3px solid #2c2416;
    padding: 8px;
    background-color: #d4c5a0;
    box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
}

/* Nation-Specific Color Themes */
.datacard.datacard-german {
    background-color: #797768;
    border-color: #1a1a1a;
}

.datacard.datacard-german .datacard-title {
    color: white;
}

.datacard.datacard-german .datacard-subtitle {
    color: white;
}

.datacard.datacard-german .datacard-special-rules {
    color: white;
}

.datacard.datacard-german th {
    background-color: #ECD1A2;
    color: #1a1a1a;
}

.datacard.datacard-german td {
    background-color: #e8dcc8;
    color: #1a1a1a;
}

.datacard.datacard-british {
    background-color: #d4c5a0;
    border-color: #2c2416;
}

.datacard.datacard-british th {
    background-color: #8b7355;
    color: white;
}

.datacard.datacard-british td {
    background-color: #f5f5dc;
    color: #1a1a1a;
}

.datacard.datacard-italian {
    background-color: #739A64;
    border-color: #5a4a2a;
}

.datacard.datacard-italian th {
    background-color: #6b5d3f;
    color: white;
}

.datacard.datacard-italian td {
    background-color: #e8dcc0;
    color: #1a1a1a;
}

.datacard.datacard-american {
    background-color: #b8c5a0;
    border-color: #3a4a2a;
}

.datacard.datacard-american th {
    background-color: #5a6d45;
    color: white;
}

.datacard.datacard-american td {
    background-color: #dce8cf;
    color: #1a1a1a;
}

.datacard.datacard-french {
    background-color: #b8c4d4;
    border-color: #2a3a4a;
}

.datacard.datacard-french th {
    background-color: #4a5a6d;
    color: white;
}

.datacard.datacard-french td {
    background-color: #d8e4f4;
    color: #1a1a1a;
}

.datacard-header {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
    align-items: center;
}

.datacard-silhouette {
    width: 140px;
    height: 70px;
    background-color: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    padding: 5px;
}

.datacard-silhouette img {
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    object-fit: contain;
    mix-blend-mode: multiply;
}

.datacard-title-block {
    flex: 1;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.datacard-title {
    font-weight: bold;
    font-size: 16px;
    margin: 0;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.datacard-subtitle {
    font-size: 9px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
}

.datacard-special-rules {
    font-size: 7px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
    color: #5a4a3a;
}

.datacard table {
    width: 100%;
    border-collapse: collapse;
    margin: 2px 0;
    font-size: 8px;
}

.datacard th {
    background-color: #8b7355;
    color: white;
    font-weight: bold;
    padding: 1px 2px;
    border: 1px solid #2c2416;
    text-align: center;
    font-size: 7px;
    line-height: 1.0;
}

.datacard td {
    background-color: #f5f5dc;
    border: 1px solid #2c2416;
    padding: 1px 2px;
    text-align: center;
    font-size: 8px;
    line-height: 1.0;
}

.datacard .main-header {
    font-size: 8px;
    font-weight: bold;
}

.armor-modifier-row td {
    font-style: italic;
    font-size: 7px;
    padding: 1px 3px;
}

.datacard-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 5px;
    padding: 3px 5px;
    font-size: 9px;
    font-weight: bold;
}

.datacard-footer .footer-stat {
    flex: 1;
    text-align: center;
}
</style>

---

"""
                f.write(css)

                # Open single grid for all datacards (no nation headers - flags in silhouettes will distinguish)
                f.write('<div class="datacard-grid">\n\n')

                # Generate all datacards in one continuous grid
                for equipment in unique_equipment:
                    datacard = self.generate_datacard_markdown(equipment, 'r')
                    f.write(datacard)
                    f.write('\n')

                # Close grid
                f.write("</div>\n")

            print(f"  -> {output_file.name}")

        print(f"\n{'='*70}")
        print(f"Datacard generation complete for {battle['name']}")
        print(f"{'='*70}\n")

    def generate_all_books(self):
        """Generate datacards for all 12 battle books."""
        for battle_key in BATTLES.keys():
            self.generate_book_datacards(battle_key)

    def extract_equipment_from_scenario(self, scenario_path: Path) -> Set[str]:
        """
        Extract equipment IDs from a scenario markdown file.

        Parses scenario markdown to find equipment mentioned in FORCES sections.
        Looks for patterns like:
        - "8x Matilda II"
        - "2x 25-pdr"
        - Equipment names in force lists

        Returns:
            Set of equipment IDs found in scenario
        """
        equipment_ids = set()

        if not scenario_path.exists():
            print(f"[WARNING] Scenario file not found: {scenario_path}")
            return equipment_ids

        with open(scenario_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract equipment from unit lines like "8x Matilda II (veteran) - 400 pts, BR: 2"
        # Pattern: number + 'x' + equipment name + optional details
        import re
        unit_pattern = r'\d+x\s+([^(]+)'
        matches = re.findall(unit_pattern, content)

        for match in matches:
            equipment_name = match.strip()

            # Try to find matching equipment in database
            cursor = self.conn.cursor()

            # Try exact name match first
            cursor.execute("""
                SELECT canonical_id FROM equipment
                WHERE LOWER(name) = LOWER(?)
            """, (equipment_name,))
            result = cursor.fetchone()

            if result:
                equipment_ids.add(result['canonical_id'])
            else:
                # Try fuzzy match (contains)
                cursor.execute("""
                    SELECT canonical_id FROM equipment
                    WHERE LOWER(name) LIKE LOWER(?)
                """, (f'%{equipment_name}%',))
                result = cursor.fetchone()

                if result:
                    equipment_ids.add(result['canonical_id'])

        return equipment_ids

    def generate_scenario_datacards(self, battle_key: str, scenario_file: str):
        """
        Generate datacards only for equipment used in a specific scenario.

        Args:
            battle_key: Battle identifier (e.g., 'battleaxe')
            scenario_file: Scenario filename (e.g., 'scenario_01.md')
        """
        if battle_key not in BATTLES:
            print(f"Error: Unknown battle '{battle_key}'")
            return

        battle = BATTLES[battle_key]
        output_dir = OUTPUT_BASE / battle['output_dir'] / "book" / "src"
        scenario_path = output_dir / "scenarios" / scenario_file

        print(f"\n{'='*70}")
        print(f"Generating scenario-specific datacards for: {battle['name']}")
        print(f"Scenario: {scenario_file}")
        print(f"{'='*70}\n")

        # Extract equipment from scenario
        equipment_ids = self.extract_equipment_from_scenario(scenario_path)

        if not equipment_ids:
            print("[WARNING] No equipment found in scenario file")
            return

        print(f"Found {len(equipment_ids)} unique equipment items in scenario\n")

        # Generate datacards organized by category (pass IDs, not dicts)
        categorized_equipment = self.categorize_equipment(equipment_ids)

        chapter2_dir = output_dir / "chapter2"
        chapter2_dir.mkdir(parents=True, exist_ok=True)

        print(f"Output directory: {chapter2_dir}\n")

        # Generate datacards by category (same pattern as generate_book_datacards)
        for category, equipment_list in categorized_equipment.items():
            # Deduplicate by canonical_id
            seen_ids = set()
            unique_equipment = []
            for equipment in equipment_list:
                if equipment['canonical_id'] not in seen_ids:
                    seen_ids.add(equipment['canonical_id'])
                    unique_equipment.append(equipment)

            print(f"{category}: {len(unique_equipment)} items (scenario-specific)")

            # Sort by nation then name
            unique_equipment.sort(key=lambda x: (x['nation'], x['name']))

            # Generate markdown file
            category_file = category.lower().replace(' ', '_').replace('&', 'and') + '.md'
            output_file = chapter2_dir / category_file

            with open(output_file, 'w', encoding='utf-8') as f:
                # Write title
                f.write(f"# {category}\n\n")

                # Write CSS (same as generate_book_datacards - omitted for brevity, just write datacards)
                f.write('<div class="datacard-grid">\n\n')

                # Generate all datacards in one continuous grid
                for equipment in unique_equipment:
                    datacard = self.generate_datacard_markdown(equipment, 'r')
                    f.write(datacard)
                    f.write('\n')

                # Close grid
                f.write("</div>\n")

            print(f"  -> {output_file.name}\n")

        print(f"{'='*70}")
        print(f"Scenario datacard generation complete")
        print(f"{'='*70}\n")

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 7: Book Equipment Datacard Generator v5.5",
        epilog="""
Examples:
  %(prog)s --battle battleaxe              # Generate all datacards for Battleaxe
  %(prog)s --all                           # Generate datacards for all 12 battles
  %(prog)s --scenario battleaxe scenario_01.md  # Generate only equipment from specific scenario
        """
    )
    parser.add_argument(
        "--battle",
        choices=list(BATTLES.keys()),
        help="Generate datacards for specific battle (one of 12 North Africa battles)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate datacards for all 12 battles"
    )
    parser.add_argument(
        "--scenario",
        nargs=2,
        metavar=('BATTLE', 'SCENARIO_FILE'),
        help="Generate datacards only for equipment in specific scenario (e.g., --scenario battleaxe scenario_01.md)"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.battle and not args.all and not args.scenario:
        parser.error("Must specify --battle, --all, or --scenario")

    generator = BookDatacardGenerator()

    try:
        if args.all:
            generator.generate_all_books()
        elif args.scenario:
            battle_key, scenario_file = args.scenario
            generator.generate_scenario_datacards(battle_key, scenario_file)
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
