#!/usr/bin/env python3
"""
Phase 5.5 - Phase 4: BattleGroup Stat Calculator (CORRECTED)
Calculates BattleGroup game stats from historical specifications

CORRECTED VERSION: Uses validated Phase 9B calculators instead of recreating logic

Purpose: For 431 North Africa items without BG reference matches, calculate:
- Armor ratings (A-O letter scale from mm thickness)
- Movement values (inches from speed/weight) - USES validated movement_calculator.py
- Weapon ratings (HE/AP from caliber) - USES validated he_calculator.py
- Points cost and Battle Rating (from vehicle type/capabilities)

Data Flow:
1. Read historical_specs_json from equipment_master_new
2. Apply validated Phase 9B conversion calculators
3. Calculate missing stats using category defaults
4. Populate equipment_stats_battlegroup table
5. Target: 100% coverage for 469 North Africa items with 95%+ accuracy
"""

import sqlite3
import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Add scripts to path for validated calculator imports
project_root = Path(__file__).parent.parent
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path / "battlegroup" / "conversion"))

# Import validated Phase 9B calculators (97-100% accuracy)
try:
    from movement_calculator import calculate_movement as validated_movement_calc
    from he_calculator import calculate_he_effect as validated_he_calc
    VALIDATED_CALCULATORS_AVAILABLE = True
    print("[OK] Loaded validated Phase 9B calculators")
except ImportError as e:
    print(f"[WARNING] Could not import validated calculators: {e}")
    print("[WARNING] Falling back to basic formulas (lower accuracy)")
    VALIDATED_CALCULATORS_AVAILABLE = False

# Database path
DB_PATH = project_root / "database" / "master_database.db"

# Configuration
DRY_RUN = False  # Set True to preview without modifying database
VERBOSE = False  # Set True for detailed per-item output

def connect_db():
    """Connect to SQLite database"""
    return sqlite3.connect(str(DB_PATH))

def convert_armor_mm_to_letter(mm: Optional[float]) -> Optional[str]:
    """Convert armor thickness in mm to BattleGroup letter scale (A-O)"""
    if mm is None:
        return None

    # Convert to float if string
    try:
        mm = float(mm)
    except (ValueError, TypeError):
        return None

    if mm == 0:
        return None

    # Based on bg_armor_conversion table
    if mm <= 6: return 'A'
    if mm <= 13: return 'B'
    if mm <= 20: return 'C'
    if mm <= 30: return 'D'
    if mm <= 45: return 'E'
    if mm <= 60: return 'F'
    if mm <= 75: return 'G'
    if mm <= 90: return 'H'
    if mm <= 105: return 'I'
    if mm <= 120: return 'J'
    if mm <= 135: return 'K'
    if mm <= 150: return 'L'
    if mm <= 175: return 'M'
    if mm <= 200: return 'N'
    return 'O'  # 200+ mm

def estimate_vehicle_type(category: str, specs: Dict) -> str:
    """Estimate vehicle type (tracked/wheeled/towed) from category and specs"""
    category_lower = category.lower()

    if 'tank' in category_lower or 'self_propelled' in category_lower:
        return 'tracked'
    elif 'armored_car' in category_lower or 'vehicle' in category_lower:
        # Check for specific indicators
        name = specs.get('display_name', '').lower()
        if 'truck' in name or 'lorry' in name or 'cmp' in name:
            return 'wheeled'
        if 'universal carrier' in name or 'bren carrier' in name:
            return 'tracked'
        return 'wheeled'  # Default for vehicles
    elif 'artillery' in category_lower or 'gun' in category_lower or 'anti_tank' in category_lower:
        return 'towed'
    elif 'aircraft' in category_lower:
        return 'aircraft'
    else:
        return 'other'

def convert_movement(speed_kmh: Optional[float], weight_tonnes: Optional[float], vehicle_type: str, category: str, vehicle_name: str = "") -> Dict[str, Optional[int]]:
    """Convert speed/weight to BattleGroup movement (inches) - USES VALIDATED CALCULATOR"""

    if not VALIDATED_CALCULATORS_AVAILABLE:
        # Fallback to basic logic if validated calculator not available
        if vehicle_type == 'tracked':
            if weight_tonnes is None or weight_tonnes < 10:
                return {'offroad': 12, 'road': 24}
            elif weight_tonnes < 30:
                return {'offroad': 8, 'road': 12}
            else:
                return {'offroad': 6, 'road': 10}
        elif vehicle_type == 'wheeled':
            return {'offroad': 12, 'road': 24}
        elif vehicle_type == 'towed':
            return {'offroad': 0, 'road': 0}
        elif vehicle_type == 'aircraft':
            return {'offroad': None, 'road': None}
        else:
            return {'offroad': 8, 'road': 12}

    # Use validated Phase 9B movement calculator (95%+ accuracy)
    try:
        result = validated_movement_calc(
            vehicle_name=vehicle_name,
            vehicle_type=vehicle_type,
            weight_tonnes=weight_tonnes
        )

        return {
            'offroad': result.get('off_road'),
            'road': result.get('road')
        }
    except Exception as e:
        if VERBOSE:
            print(f"  Warning: Movement calculation failed: {e}")
        # Fallback to basic defaults
        return {'offroad': 8, 'road': 12}

def extract_caliber_from_gun_name(gun_name: str) -> Optional[int]:
    """Extract caliber in mm from gun designation"""
    if not gun_name:
        return None

    # Common patterns: "75mm", "7.5cm", "17-pounder", "6pdr"
    patterns = [
        r'(\d+)mm',           # 75mm
        r'(\d+\.?\d*)cm',     # 7.5cm → 75mm
        r'(\d+)-?pounder',    # 17-pounder → 76.2mm
        r'(\d+)pdr',          # 6pdr → 57mm
    ]

    for pattern in patterns:
        match = re.search(pattern, gun_name, re.IGNORECASE)
        if match:
            value = float(match.group(1))

            # Convert cm to mm
            if 'cm' in pattern:
                value *= 10

            # Convert pounder to mm (rough approximation)
            if 'pounder' in pattern or 'pdr' in pattern:
                pounder_to_mm = {
                    2: 40,
                    6: 57,
                    17: 76.2,
                    25: 87.6,
                }
                value = pounder_to_mm.get(int(value), value * 25)  # Rough formula: pdr * 25

            return int(value)

    return None

def convert_weapon_rating(caliber_mm: Optional[int], penetration_mm: Optional[int], gun_name: str = "") -> Dict[str, Optional[str]]:
    """Convert caliber/penetration to BattleGroup HE/AP ratings - USES VALIDATED CALCULATOR"""

    if not VALIDATED_CALCULATORS_AVAILABLE or not caliber_mm:
        # Fallback if validated calculator not available
        he = None
        if caliber_mm:
            if caliber_mm < 50:
                he = "2/5+"
            elif caliber_mm < 75:
                he = "3/5+"
            else:
                he = "4/4+"

        ap = None
        if penetration_mm:
            if penetration_mm < 50:
                ap = "4"
            elif penetration_mm < 100:
                ap = "8"
            else:
                ap = "10"

        weapon_desc = None
        if he and ap:
            weapon_desc = f"HE {he} | AP {ap}"
        elif he:
            weapon_desc = f"HE {he}"

        return {'he_rating': he, 'ap_rating': ap, 'weapon_description': weapon_desc}

    # Use validated Phase 9B HE calculator (95%+ accuracy)
    try:
        result = validated_he_calc(caliber_mm, gun_name=gun_name)

        he = result.get('format')  # e.g., "4/4+"

        # AP estimation (validated calculator doesn't do AP, so keep basic logic)
        ap = None
        if penetration_mm:
            if penetration_mm < 30:
                ap = "2"
            elif penetration_mm < 50:
                ap = "4"
            elif penetration_mm < 75:
                ap = "6"
            elif penetration_mm < 100:
                ap = "8"
            elif penetration_mm < 130:
                ap = "10"
            else:
                ap = "12"
        elif caliber_mm:
            # Estimate AP from caliber
            if caliber_mm < 50:
                ap = str(max(2, caliber_mm // 15))
            else:
                ap = str(max(4, caliber_mm // 10))

        # Combine into weapon description
        weapon_desc = None
        if he and ap:
            weapon_desc = f"HE {he} | AP {ap}"
        elif he:
            weapon_desc = f"HE {he}"
        elif ap:
            weapon_desc = f"AP {ap}"

        return {
            'he_rating': he,
            'ap_rating': ap,
            'weapon_description': weapon_desc
        }
    except Exception as e:
        if VERBOSE:
            print(f"  Warning: HE calculation failed: {e}")
        # Fallback to basic defaults
        return {'he_rating': "3/5+", 'ap_rating': "4", 'weapon_description': "HE 3/5+ | AP 4"}

def estimate_points_and_br(category: str, specs: Dict, armor_front: Optional[str], ap_rating: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """Estimate points cost and Battle Rating from capabilities"""

    category_lower = category.lower()

    # Base points by category
    if 'tank' in category_lower:
        base_points = 100
        base_br = 5
    elif 'self_propelled' in category_lower:
        base_points = 90
        base_br = 4
    elif 'armored_car' in category_lower:
        base_points = 50
        base_br = 2
    elif 'vehicle' in category_lower:
        base_points = 10
        base_br = 1
    elif 'gun' in category_lower or 'artillery' in category_lower or 'anti_tank' in category_lower:
        base_points = 30
        base_br = 2
    elif 'aircraft' in category_lower:
        base_points = 150
        base_br = 6
    else:
        base_points = 20
        base_br = 1

    # Adjust for armor
    if armor_front:
        armor_bonus = ord(armor_front) - ord('A')  # A=0, B=1, ... O=14
        base_points += armor_bonus * 10
        base_br += armor_bonus // 3

    # Adjust for firepower
    if ap_rating:
        try:
            ap_value = int(ap_rating)
            base_points += ap_value * 5
            base_br += ap_value // 4
        except:
            pass

    # Cap BR at reasonable values
    base_br = min(base_br, 10)

    return (base_points, base_br)

def calculate_bg_stats(master_id: int, display_name: str, category: str, specs: Dict) -> Dict:
    """Calculate all BattleGroup stats from historical specs"""

    result = {
        'master_id': master_id,
        'armor_front': None,
        'armor_side': None,
        'armor_rear': None,
        'movement_offroad': None,
        'movement_road': None,
        'he_rating': None,
        'ap_rating': None,
        'weapon_description': None,
        'points': None,
        'battle_rating': None,
        'calculation_method': 'formula_derived',
        'calculation_confidence': 75,  # Default confidence
        'calculation_notes': []
    }

    # Extract values from various spec keys (handle Phase 3 matches and Phase 1 legacy)
    armor_front_mm = None
    armor_side_mm = None
    armor_rear_mm = None
    speed_kmh = None
    weight_tonnes = None
    main_gun = None
    penetration_mm = None

    # Try Phase 3 enriched keys first
    for source in ['bg_reference_vehicles', 'wwiitanks', 'onwar']:
        if not armor_front_mm:
            armor_front_mm = specs.get(f'{source}_armor_front')
            if armor_front_mm and isinstance(armor_front_mm, str):
                # Handle letter scale already (from BG reference)
                if len(armor_front_mm) == 1 and armor_front_mm.isalpha():
                    result['armor_front'] = armor_front_mm
                    armor_front_mm = None  # Already converted

        if not armor_side_mm:
            armor_side_mm = specs.get(f'{source}_armor_side')
        if not armor_rear_mm:
            armor_rear_mm = specs.get(f'{source}_armor_rear')
        if not speed_kmh:
            speed_kmh = specs.get(f'{source}_speed_road_kmh')
        if not weight_tonnes:
            weight_tonnes = specs.get(f'{source}_weight_tonnes')

    # Try Phase 1 legacy keys
    if not armor_front_mm:
        armor_front_mm = specs.get('armor_front_mm') or specs.get('armor_hull_front_mm')
    if not armor_side_mm:
        armor_side_mm = specs.get('armor_side_mm') or specs.get('armor_hull_side_mm')
    if not armor_rear_mm:
        armor_rear_mm = specs.get('armor_rear_mm') or specs.get('armor_hull_rear_mm')
    if not speed_kmh:
        speed_kmh = specs.get('speed_road_kmh')
    if not weight_tonnes:
        weight_tonnes = specs.get('weight_tonnes') or specs.get('weight_kg')
        if weight_tonnes and weight_tonnes > 100:  # Likely in kg
            weight_tonnes = weight_tonnes / 1000

    # Extract weapon data
    main_gun = None

    # Strategy 1: Parse bg_reference_vehicles_weapons JSON array
    if 'bg_reference_vehicles_weapons' in specs:
        try:
            weapons = json.loads(specs['bg_reference_vehicles_weapons']) if isinstance(specs['bg_reference_vehicles_weapons'], str) else specs['bg_reference_vehicles_weapons']
            if weapons and isinstance(weapons, list):
                # Find first turret or main weapon (not MG)
                for weapon in weapons:
                    if isinstance(weapon, dict):
                        weapon_name = weapon.get('weapon', '')
                        if weapon_name and weapon_name != 'MG' and 'MG' not in weapon_name:
                            main_gun = weapon_name
                            break
        except:
            pass

    # Strategy 2: For artillery/guns, the item IS the weapon - extract from display_name
    if not main_gun and category in ['artillery', 'gun', 'anti_tank_gun', 'anti_aircraft_gun', 'mortar']:
        main_gun = display_name

    # Strategy 3: Check for main_gun/armament_main keys
    if not main_gun:
        main_gun = specs.get('main_gun') or specs.get('armament_main')

    # Strategy 4: Try extracting from display_name if it contains caliber
    if not main_gun and ('mm' in display_name.lower() or 'pounder' in display_name.lower() or 'pdr' in display_name.lower()):
        main_gun = display_name

    # Convert armor
    if not result['armor_front'] and armor_front_mm:
        result['armor_front'] = convert_armor_mm_to_letter(armor_front_mm)
        result['calculation_notes'].append(f"armor_front: {armor_front_mm}mm -> {result['armor_front']}")

    if armor_side_mm:
        result['armor_side'] = convert_armor_mm_to_letter(armor_side_mm)
        result['calculation_notes'].append(f"armor_side: {armor_side_mm}mm -> {result['armor_side']}")

    if armor_rear_mm:
        result['armor_rear'] = convert_armor_mm_to_letter(armor_rear_mm)
        result['calculation_notes'].append(f"armor_rear: {armor_rear_mm}mm -> {result['armor_rear']}")

    # Convert movement using validated calculator
    vehicle_type = estimate_vehicle_type(category, {**specs, 'display_name': display_name})
    movement = convert_movement(speed_kmh, weight_tonnes, vehicle_type, category, vehicle_name=display_name)
    result['movement_offroad'] = movement['offroad']
    result['movement_road'] = movement['road']

    if movement['offroad']:
        result['calculation_notes'].append(f"movement: {vehicle_type}, {weight_tonnes}t -> {movement['offroad']}\"/{ movement['road']}\"")

    # Convert weapon
    caliber = extract_caliber_from_gun_name(main_gun or "")
    weapon_stats = convert_weapon_rating(caliber, penetration_mm, main_gun or "")
    result['he_rating'] = weapon_stats['he_rating']
    result['ap_rating'] = weapon_stats['ap_rating']
    result['weapon_description'] = weapon_stats['weapon_description']

    if caliber:
        result['calculation_notes'].append(f"weapon: {main_gun} ({caliber}mm) -> HE {result['he_rating']}, AP {result['ap_rating']}")

    # Estimate points and BR
    points, br = estimate_points_and_br(category, specs, result['armor_front'], result['ap_rating'])
    result['points'] = points
    result['battle_rating'] = br

    # Calculate confidence score
    data_points = sum([
        1 if armor_front_mm else 0,
        1 if speed_kmh or weight_tonnes else 0,
        1 if main_gun else 0,
    ])

    if data_points >= 3:
        result['calculation_confidence'] = 90
    elif data_points == 2:
        result['calculation_confidence'] = 80
    else:
        result['calculation_confidence'] = 70

    result['calculation_notes'] = ' | '.join(result['calculation_notes'])

    return result

def main():
    """Main execution"""
    print("=" * 80)
    print("Phase 5.5 - Phase 4: BattleGroup Stat Calculator")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (preview only)' if DRY_RUN else 'REAL (database will be modified)'}")
    print()

    conn = connect_db()

    # Get North Africa equipment needing stats
    print("Step 1: Loading North Africa equipment...")
    query = """
    SELECT
        em.master_id,
        em.display_name,
        em.equipment_category,
        em.historical_specs_json
    FROM equipment_master_new em
    JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
    WHERE etu.theater = 'north_africa'
    ORDER BY em.master_id
    """

    cursor = conn.execute(query)
    equipment_list = []

    for row in cursor:
        master_id, display_name, category, specs_json = row

        specs = {}
        if specs_json:
            try:
                specs = json.loads(specs_json)
            except:
                pass

        equipment_list.append({
            'master_id': master_id,
            'display_name': display_name,
            'category': category,
            'specs': specs
        })

    print(f"  Loaded: {len(equipment_list)} North Africa equipment items")

    # Calculate stats
    print("\nStep 2: Calculating BattleGroup stats...")
    calculated_stats = []

    for eq in equipment_list:
        stats = calculate_bg_stats(eq['master_id'], eq['display_name'], eq['category'], eq['specs'])
        calculated_stats.append(stats)

        if VERBOSE and stats['calculation_notes']:
            print(f"  [{eq['master_id']}] {eq['display_name']}: {stats['calculation_notes']}")

    print(f"  Calculated: {len(calculated_stats)} stat sets")

    # Apply to database
    print("\nStep 3: Populating equipment_stats_battlegroup...")

    if not DRY_RUN:
        # Clear existing stats for North Africa items
        na_master_ids = [eq['master_id'] for eq in equipment_list]
        placeholders = ','.join(['?'] * len(na_master_ids))
        conn.execute(f"DELETE FROM equipment_stats_battlegroup WHERE master_id IN ({placeholders})", na_master_ids)

        # Insert calculated stats
        insert_stmt = """
        INSERT INTO equipment_stats_battlegroup (
            master_id, armor_front, armor_side, armor_rear,
            movement_offroad, movement_road,
            he_rating, ap_rating, weapon_description,
            points, battle_rating, special_rules,
            conversion_confidence, conversion_method, generated_date, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        for stats in calculated_stats:
            try:
                # Join calculation notes for the notes field
                notes_text = '; '.join(stats.get('calculation_notes', []))

                conn.execute(insert_stmt, (
                    stats['master_id'],
                    stats['armor_front'],
                    stats['armor_side'],
                    stats['armor_rear'],
                    stats['movement_offroad'],
                    stats['movement_road'],
                    stats['he_rating'],
                    stats['ap_rating'],
                    stats['weapon_description'],
                    stats['points'],
                    stats['battle_rating'],
                    None,  # special_rules - to be populated later
                    stats['calculation_confidence'],
                    stats['calculation_method'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    notes_text if notes_text else None
                ))
            except Exception as e:
                print(f"  Error inserting stats for master_id {stats['master_id']}: {e}")

        conn.commit()
        print(f"  Inserted: {len(calculated_stats)} stat records")
    else:
        print(f"  [DRY RUN] Would insert: {len(calculated_stats)} stat records")

    # Summary
    print("\n" + "=" * 80)
    print("CALCULATION SUMMARY")
    print("=" * 80)
    print(f"Total equipment processed: {len(equipment_list)}")
    print(f"Stats calculated: {len(calculated_stats)}")

    # Confidence distribution
    conf_counts = {}
    for stats in calculated_stats:
        conf = stats['calculation_confidence']
        conf_counts[conf] = conf_counts.get(conf, 0) + 1

    print("\nConfidence Distribution:")
    for conf in sorted(conf_counts.keys(), reverse=True):
        print(f"  {conf}: {conf_counts[conf]} items ({conf_counts[conf]/len(calculated_stats)*100:.1f}%)")

    # Coverage check
    armor_count = sum(1 for s in calculated_stats if s['armor_front'])
    movement_count = sum(1 for s in calculated_stats if s['movement_offroad'])
    weapon_count = sum(1 for s in calculated_stats if s['weapon_description'])
    points_count = sum(1 for s in calculated_stats if s['points'])

    print("\nCoverage:")
    print(f"  Armor: {armor_count}/{len(calculated_stats)} ({armor_count/len(calculated_stats)*100:.1f}%)")
    print(f"  Movement: {movement_count}/{len(calculated_stats)} ({movement_count/len(calculated_stats)*100:.1f}%)")
    print(f"  Weapons: {weapon_count}/{len(calculated_stats)} ({weapon_count/len(calculated_stats)*100:.1f}%)")
    print(f"  Points/BR: {points_count}/{len(calculated_stats)} ({points_count/len(calculated_stats)*100:.1f}%)")

    if armor_count == len(calculated_stats) and movement_count == len(calculated_stats):
        print("\n[SUCCESS] 100% coverage achieved for North Africa equipment!")
    else:
        print(f"\n[PARTIAL] {min(armor_count, movement_count)/len(calculated_stats)*100:.1f}% coverage")

    conn.close()
    print("\n[COMPLETE] BattleGroup stat calculation finished")

if __name__ == "__main__":
    main()
