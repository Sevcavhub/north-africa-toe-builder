#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Tobruk British.txt parser with improved weapon extraction

Key improvements:
1. Multi-line weapon detection (weapons can span multiple lines)
2. Proper weapon parsing (handles "2 x MGs", space-separated weapons)
3. Mount line detection to know when weapons section ends
4. Better weapon normalization and deduplication
"""

import sys
import io
import re
import sqlite3
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class WeaponParser:
    """Enhanced weapon parsing logic"""

    @staticmethod
    def is_mount_line(line):
        """Check if line indicates weapon mount (end of weapons section)"""
        mount_keywords = ['Turret', 'Co-axial', 'Hull', 'Fixed', 'Pintle']
        return any(keyword in line for keyword in mount_keywords)

    @staticmethod
    def parse_weapon_string(weapon_str):
        """
        Parse weapon string and extract individual weapons
        Handles:
        - "MG MG" → ["MG", "MG"]
        - "2 x MGs" → ["MG", "MG"]
        - "37mmL53 MG MG" → ["37mmL53", "MG", "MG"]
        - "3\" howitzer MG 2 x MGs" → ["3\" howitzer", "MG", "MG", "MG"]
        """
        weapons = []

        # Handle "2 x MGs" pattern (expand to individual weapons)
        expanded = re.sub(r'(\d+)\s*x\s*(\w+)', lambda m: f"{m.group(2)} " * int(m.group(1)), weapon_str)

        # Extract individual weapon tokens
        # Pattern: number + unit (37mm, 2 pdr, 3"), Besa, MG, howitzer
        patterns = [
            r'\d+\s*["\']?\s*pdr',        # 2 pdr, 6 pdr
            r'\d+mm[A-Z]*\d*',             # 37mmL53, 20mm
            r'\d+\s*["\']?\s*howitzer',   # 3" howitzer
            r'\d+\s*["\']',                # 3", 15" (caliber shorthand)
            r'\d+mm',                      # Generic mm
            r'Besa',                       # Besa MG
            r'\b(MG|HMG|LMG)\b',          # Machine guns
            r'AT\s+Rifle',                 # Anti-tank rifle
        ]

        for pattern in patterns:
            matches = re.findall(pattern, expanded, re.IGNORECASE)
            for match in matches:
                # Normalize the weapon name
                normalized = match.strip()

                # Special handling for combined weapons
                if 'howitzer' in normalized.lower():
                    # Extract caliber + "howitzer"
                    caliber = re.search(r'\d+\s*["\']?', normalized)
                    if caliber:
                        normalized = f"{caliber.group(0).strip()} howitzer"

                weapons.append(normalized)

        # If no patterns matched, try splitting by spaces
        if not weapons:
            tokens = expanded.split()
            for token in tokens:
                if re.match(r'^\d+$', token):  # Skip pure numbers (probably ammo counts)
                    continue
                if len(token) > 1 and token not in ['x', 'and', 'or', 'with']:
                    weapons.append(token)

        return weapons

class VehicleParserEnhanced:
    """Enhanced state machine parser with better weapon extraction"""

    def __init__(self):
        self.vehicles = []
        self.current_vehicle = None
        self.state = 'LOOKING_FOR_VEHICLE'
        self.current_section = None
        self.weapon_lines = []  # Buffer for collecting weapon lines

    def is_section_header(self, line):
        """Check if line is a section header"""
        headers = ['LIGHT TANKS', 'INFANTRY TANKS', 'CRUISER TANKS',
                   'ARMOURED CARS', 'SOFT-SKINNED VEHICLES', "PORTEE'D GUNS",
                   'PORTEE', 'ANTI-TANK GUNS', 'FIELD ARTILLERY',
                   'ANTI-AIRCRAFT GUNS']

        for header in headers:
            if header in line:
                return header
        return None

    def is_header_line(self, line):
        """Check if line is a table header"""
        header_keywords = ['VEHICLE', 'MOVEMENT', 'ARMOUR', 'ARMAMENT',
                           'Off-Road', 'Road', 'Special', 'Front', 'Side',
                           'Rear', 'Weapon', 'Mount', 'Ammo', 'Hits']
        return any(keyword in line for keyword in header_keywords)

    def is_vehicle_name(self, line):
        """Check if line is a vehicle name"""
        vehicle_patterns = [
            r'^(Vickers\s+\w+)',
            r'^(M3\s+.*?Honey.*?)',
            r'^(Matilda\s+\w+)',
            r'^(Valentine\s+\w+)',
            r'^(A\d+(?:\s+\w+)?)',
            r'^(Crusader\s+\w+)',
            r'^(Morris\s+\w+)',
            r'^(Austin\s+\w+)',
            r'^(Bedford\s+\w+)',
            r'^(Scammel\s+\w+)',
            r'^(Hippo\s+\w+)',
            r'^(Matador\s+\w+)',
            r'^(Chev.*?\d+\s*cwt)',
            r'^(Humber\s+\w+)',
            r'^(Daimler\s+\w+)',
            r'^(Marmon\s+\w+)',
            r'^(Motorcycle)',
        ]

        for pattern in vehicle_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False

    def is_movement_value(self, line):
        """Check if line is a movement value"""
        return re.match(r'^\d+["\']?\s*$', line.strip()) is not None

    def is_armor_value(self, line):
        """Check if line is an armor value"""
        return re.match(r'^([I-O]|SS)\s*$', line.strip()) is not None

    def is_special_rule(self, line):
        """Check if line is a special rule (not a weapon)"""
        special_rules = ['Unreliable', 'Scout', 'Elite', 'Green', 'Veteran',
                        'Slow', 'Fast', 'Amphibious', 'Open-topped']
        return any(rule in line for rule in special_rules)

    def finalize_weapons(self):
        """Process collected weapon lines and extract weapons"""
        if not self.weapon_lines or not self.current_vehicle:
            return

        # Combine all weapon lines
        combined = ' '.join(self.weapon_lines)

        # Parse weapons
        weapons = WeaponParser.parse_weapon_string(combined)

        # Count weapon occurrences
        from collections import Counter
        weapon_counts = Counter(w.lower() for w in weapons)

        # Keep weapons, but remove excessive duplicates (>3 of same weapon is likely parsing error)
        filtered_weapons = []
        weapon_seen_count = {}
        for weapon in weapons:
            weapon_lower = weapon.lower()
            count = weapon_seen_count.get(weapon_lower, 0)

            # Keep up to 3 of the same weapon (e.g., "MG MG MG" is valid)
            # Only deduplicate if we have MORE than 3 (likely a parsing error)
            if weapon_counts[weapon_lower] <= 3 or count < 3:
                filtered_weapons.append(weapon)
                weapon_seen_count[weapon_lower] = count + 1

        self.current_vehicle['weapons'] = filtered_weapons

        # Clear buffer
        self.weapon_lines = []

    def save_current_vehicle(self):
        """Save current vehicle to list"""
        if self.current_vehicle and self.current_vehicle.get('name'):
            # Finalize any pending weapons
            self.finalize_weapons()

            weapons_str = ', '.join(self.current_vehicle.get('weapons', []))
            special_str = ', '.join(self.current_vehicle.get('special_rules', []))

            self.vehicles.append(self.current_vehicle)
            print(f"   ✅ {self.current_vehicle['name']:25s}: " +
                  f"Move={self.current_vehicle.get('off_road_inches', '?')}/{self.current_vehicle.get('road_inches', '?')}, " +
                  f"Armor={self.current_vehicle.get('armor_front', '?')}-" +
                  f"{self.current_vehicle.get('armor_side', '?')}-" +
                  f"{self.current_vehicle.get('armor_rear', '?')}, " +
                  f"Weapons=[{weapons_str}]")

    def parse_line(self, line, line_num):
        """Parse a single line with enhanced state machine logic"""

        line = line.strip()

        # Skip empty lines
        if not line:
            return

        # Check for section header
        section = self.is_section_header(line)
        if section:
            self.current_section = section
            print(f"\n🏷️  Section: {section}")
            # Reset state when entering new section
            self.state = 'LOOKING_FOR_VEHICLE'
            return

        # Skip table headers
        if self.is_header_line(line):
            return

        # State machine
        if self.state == 'LOOKING_FOR_VEHICLE':
            if self.is_vehicle_name(line):
                # Save previous vehicle
                self.save_current_vehicle()

                # Start new vehicle
                self.current_vehicle = {
                    'name': line,
                    'nation': 'British',
                    'vehicle_type': self.current_section or 'Unknown',
                    'year_range': '1940-41',
                    'off_road_inches': None,
                    'road_inches': None,
                    'armor_front': None,
                    'armor_side': None,
                    'armor_rear': None,
                    'weapons': [],
                    'special_rules': [],
                    'source_file': 'Tobruk British.txt',
                    'extraction_method': 'enhanced_weapon_parsing'
                }

                print(f"   🚗 Found: {line}")
                self.state = 'READING_MOVEMENT_1'

        elif self.state == 'READING_MOVEMENT_1':
            # Expecting first movement value (off-road)
            if self.is_movement_value(line):
                value = line.replace('"', '').replace("'", '').strip()
                # Handle "6"H" case (movement + special)
                value = re.sub(r'[A-Z]', '', value)
                self.current_vehicle['off_road_inches'] = int(value)
                self.state = 'READING_MOVEMENT_2'

        elif self.state == 'READING_MOVEMENT_2':
            # Expecting second movement value (road)
            if self.is_movement_value(line):
                value = line.replace('"', '').replace("'", '').strip()
                value = re.sub(r'[A-Z]', '', value)
                self.current_vehicle['road_inches'] = int(value)
                self.state = 'READING_SPECIAL_OR_ARMOR'

        elif self.state == 'READING_SPECIAL_OR_ARMOR':
            # Could be special rule or first armor value
            if self.is_special_rule(line):
                self.current_vehicle['special_rules'].append(line)
                self.state = 'READING_ARMOR_1'
            elif self.is_armor_value(line):
                self.current_vehicle['armor_front'] = line.strip()
                self.state = 'READING_ARMOR_2'

        elif self.state == 'READING_ARMOR_1':
            # Expecting first armor value (front)
            if self.is_armor_value(line):
                self.current_vehicle['armor_front'] = line.strip()
                self.state = 'READING_ARMOR_2'

        elif self.state == 'READING_ARMOR_2':
            # Expecting second armor value (side)
            if self.is_armor_value(line):
                self.current_vehicle['armor_side'] = line.strip()
                self.state = 'READING_ARMOR_3'
            elif not self.is_movement_value(line) and not self.is_header_line(line):
                # Not an armor value - assume same as front, treat line as weapon
                self.current_vehicle['armor_side'] = self.current_vehicle.get('armor_front')
                self.current_vehicle['armor_rear'] = self.current_vehicle.get('armor_front')
                self.weapon_lines.append(line)
                self.state = 'READING_WEAPONS'

        elif self.state == 'READING_ARMOR_3':
            # Expecting third armor value (rear)
            if self.is_armor_value(line):
                self.current_vehicle['armor_rear'] = line.strip()
                self.state = 'READING_WEAPONS'
            elif not self.is_movement_value(line) and not self.is_header_line(line):
                # Not an armor value - assume same as side, treat line as weapon
                self.current_vehicle['armor_rear'] = self.current_vehicle.get('armor_side')
                self.weapon_lines.append(line)
                self.state = 'READING_WEAPONS'

        elif self.state == 'READING_WEAPONS':
            # Collect weapon lines until we hit mount line or next vehicle
            if self.is_vehicle_name(line):
                # Next vehicle - finalize current and restart
                self.save_current_vehicle()
                self.current_vehicle = {
                    'name': line,
                    'nation': 'British',
                    'vehicle_type': self.current_section or 'Unknown',
                    'year_range': '1940-41',
                    'off_road_inches': None,
                    'road_inches': None,
                    'armor_front': None,
                    'armor_side': None,
                    'armor_rear': None,
                    'weapons': [],
                    'special_rules': [],
                    'source_file': 'Tobruk British.txt',
                    'extraction_method': 'enhanced_weapon_parsing'
                }
                print(f"   🚗 Found: {line}")
                self.state = 'READING_MOVEMENT_1'

            elif WeaponParser.is_mount_line(line):
                # Mount line detected - finalize weapons and STOP collecting
                self.finalize_weapons()
                # Transition to waiting for next vehicle (ignore remaining data)
                self.state = 'WAITING_FOR_NEXT_VEHICLE'

            elif re.match(r'^\d+$', line):
                # Pure number - likely ammo count, skip
                pass

            elif line == '-':
                # Dash - no data, skip
                pass

            else:
                # Weapon line - add to buffer
                self.weapon_lines.append(line)

        elif self.state == 'WAITING_FOR_NEXT_VEHICLE':
            # After weapons finalized, wait for next vehicle or section
            if self.is_vehicle_name(line):
                # Next vehicle - start fresh
                self.save_current_vehicle()
                self.current_vehicle = {
                    'name': line,
                    'nation': 'British',
                    'vehicle_type': self.current_section or 'Unknown',
                    'year_range': '1940-41',
                    'off_road_inches': None,
                    'road_inches': None,
                    'armor_front': None,
                    'armor_side': None,
                    'armor_rear': None,
                    'weapons': [],
                    'special_rules': [],
                    'source_file': 'Tobruk British.txt',
                    'extraction_method': 'enhanced_weapon_parsing'
                }
                print(f"   🚗 Found: {line}")
                self.state = 'READING_MOVEMENT_1'
            # Otherwise, ignore all lines until next vehicle or section

    def finalize(self):
        """Save last vehicle and return results"""
        self.save_current_vehicle()
        return self.vehicles

def parse_tobruk_enhanced(file_path):
    """Parse using enhanced weapon extraction"""

    print("📖 Parsing Tobruk British.txt (Enhanced Weapon Extraction)...")
    print("="*70)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove BOM
    content = content.replace('\ufeff', '')

    parser = VehicleParserEnhanced()

    for line_num, line in enumerate(content.split('\n'), 1):
        parser.parse_line(line, line_num)

    vehicles = parser.finalize()

    print(f"\n{'='*70}")
    print(f"✅ Parsing complete!")
    print(f"   Vehicles extracted: {len(vehicles)}")

    return vehicles

def import_enhanced_vehicles(conn, vehicles):
    """Import enhanced parsing results"""

    cursor = conn.cursor()

    # Clear previous import
    cursor.execute("DELETE FROM bg_reference_vehicles_txt_import")

    print(f"\n📥 Importing {len(vehicles)} vehicles (enhanced weapon parsing)...")

    for vehicle in vehicles:
        weapons_str = ', '.join(vehicle.get('weapons', []))
        special_rules_str = ', '.join(vehicle.get('special_rules', []))

        cursor.execute("""
            INSERT INTO bg_reference_vehicles_txt_import
            (name, nation, year_range, vehicle_type, off_road_inches, road_inches,
             armor_front, armor_side, armor_rear, weapons, special_rules,
             source_file, extraction_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vehicle['name'],
            vehicle['nation'],
            vehicle['year_range'],
            vehicle['vehicle_type'],
            vehicle.get('off_road_inches'),
            vehicle.get('road_inches'),
            vehicle.get('armor_front'),
            vehicle.get('armor_side'),
            vehicle.get('armor_rear'),
            weapons_str,
            special_rules_str,
            vehicle['source_file'],
            vehicle['extraction_method']
        ))

    conn.commit()
    print(f"✅ Imported {len(vehicles)} vehicles")

def compare_enhanced(conn):
    """Run comparison with enhanced weapon parsing"""

    cursor = conn.cursor()

    print(f"\n{'='*70}")
    print("ENHANCED COMPARISON: Manual Entry vs Enhanced Weapon Parsing")
    print(f"{'='*70}\n")

    # Get manual British vehicles
    cursor.execute("""
        SELECT name, vehicle_type, off_road_inches, road_inches,
               armor_front, armor_side, armor_rear, weapons, special_rules
        FROM bg_reference_vehicles
        WHERE nation LIKE '%British%'
        ORDER BY name
    """)
    manual_vehicles = cursor.fetchall()

    # Get enhanced txt parsing
    cursor.execute("""
        SELECT name, vehicle_type, off_road_inches, road_inches,
               armor_front, armor_side, armor_rear, weapons, special_rules
        FROM bg_reference_vehicles_txt_import
        ORDER BY name
    """)
    txt_vehicles = cursor.fetchall()

    print(f"📊 Dataset Sizes:")
    print(f"   Manual entry: {len(manual_vehicles)} British vehicles")
    print(f"   TXT parsing:  {len(txt_vehicles)} vehicles\n")

    # Create dictionaries
    manual_dict = {v[0]: v for v in manual_vehicles}
    txt_dict = {v[0]: v for v in txt_vehicles}

    # Find matches
    manual_names = set(manual_dict.keys())
    txt_names = set(txt_dict.keys())

    common_names = manual_names & txt_names

    print(f"📋 Name Matching:")
    print(f"   Common names: {len(common_names)} vehicles\n")

    # Field comparison
    field_names = ['vehicle_type', 'off_road_inches', 'road_inches',
                   'armor_front', 'armor_side', 'armor_rear', 'weapons', 'special_rules']

    field_matches = {f: 0 for f in field_names}
    field_total = len(common_names)

    perfect_matches = []
    weapon_improvements = []

    for name in sorted(common_names):
        manual_data = manual_dict[name]
        txt_data = txt_dict[name]

        match_count = 0
        weapon_match = False

        for idx, field_name in enumerate(field_names):
            manual_val = manual_data[idx + 1]
            txt_val = txt_data[idx + 1]

            if manual_val == txt_val:
                field_matches[field_name] += 1
                match_count += 1
                if field_name == 'weapons':
                    weapon_match = True
            elif field_name == 'weapons':
                # Check if weapons are substantially similar (different format but same weapons)
                manual_weapons = set(w.strip() for w in str(manual_val).split(','))
                txt_weapons = set(w.strip() for w in str(txt_val).split(','))

                overlap = len(manual_weapons & txt_weapons)
                total_unique = len(manual_weapons | txt_weapons)

                if overlap / total_unique >= 0.7:  # 70% overlap
                    weapon_improvements.append({
                        'name': name,
                        'manual': manual_val,
                        'txt': txt_val,
                        'overlap': overlap,
                        'total': total_unique,
                        'percentage': (overlap / total_unique * 100)
                    })

        if match_count == len(field_names):
            perfect_matches.append(name)

    # Print results
    print("📊 Field Match Rates:")
    for field_name in field_names:
        if field_total > 0:
            match_pct = (field_matches[field_name] / field_total) * 100
            status = "✅" if match_pct >= 80 else "⚠️" if match_pct >= 50 else "❌"
            print(f"   {status} {field_name:20s}: {field_matches[field_name]:3d}/{field_total} ({match_pct:5.1f}%)")

    total_comparisons = field_total * len(field_names)
    total_matches = sum(field_matches.values())
    overall_pct = (total_matches / total_comparisons * 100) if total_comparisons > 0 else 0

    print(f"\n✅ OVERALL MATCH: {total_matches}/{total_comparisons} ({overall_pct:.1f}%)")
    print(f"✅ PERFECT MATCHES: {len(perfect_matches)}/{field_total} vehicles")

    # Show weapon improvements
    if weapon_improvements:
        print(f"\n🎯 Weapon Extraction Improvements ({len(weapon_improvements)} vehicles):")
        for item in weapon_improvements:
            print(f"\n   {item['name']} ({item['percentage']:.0f}% weapon overlap):")
            print(f"      Manual: {item['manual']}")
            print(f"      Parsed: {item['txt']}")

    return {
        'total_matches': total_matches,
        'total_comparisons': total_comparisons,
        'overall_percentage': overall_pct,
        'perfect_matches': len(perfect_matches),
        'weapon_improvements': len(weapon_improvements),
        'field_matches': field_matches
    }

def main():
    print("="*70)
    print("Tobruk British - Enhanced Weapon Extraction")
    print("="*70 + "\n")

    txt_file = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Tobruk British.txt"
    db_file = r"D:\north-africa-toe-builder\database\master_database.db"

    # Parse with enhanced weapon extraction
    vehicles = parse_tobruk_enhanced(txt_file)

    # Connect to database
    conn = sqlite3.connect(db_file)

    # Import enhanced results
    import_enhanced_vehicles(conn, vehicles)

    # Run enhanced comparison
    result = compare_enhanced(conn)

    conn.close()

    print(f"\n{'='*70}")
    print("✨ Enhanced Weapon Extraction Complete!")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
