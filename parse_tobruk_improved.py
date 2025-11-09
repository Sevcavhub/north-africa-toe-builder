#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Tobruk British.txt parser using state machine for table structure

The text file has this pattern for each vehicle:
- Vehicle name
- Movement: Off-road (line 1), Road (line 2)
- Armor: Front (line 1), Side (line 2), Rear (line 3)
- Weapons: Various weapon lines
- Mount: Turret/Hull/etc
"""

import sys
import io
import re
import sqlite3
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class VehicleParser:
    """State machine parser for Tobruk British table structure"""

    def __init__(self):
        self.vehicles = []
        self.current_vehicle = None
        self.state = 'LOOKING_FOR_VEHICLE'
        self.current_section = None
        self.line_buffer = []

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
        """Check if line is a table header (not data)"""
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
        """Check if line is a movement value (e.g., 12" or 18")"""
        return re.match(r'^\d+["\']?\s*$', line.strip()) is not None

    def is_armor_value(self, line):
        """Check if line is an armor value (letter I-O or SS)"""
        return re.match(r'^([I-O]|SS)\s*$', line.strip()) is not None

    def save_current_vehicle(self):
        """Save current vehicle to list"""
        if self.current_vehicle and self.current_vehicle.get('name'):
            self.vehicles.append(self.current_vehicle)
            print(f"   ✅ {self.current_vehicle['name']}: " +
                  f"off={self.current_vehicle.get('off_road_inches')}, " +
                  f"road={self.current_vehicle.get('road_inches')}, " +
                  f"armor={self.current_vehicle.get('armor_front')}-" +
                  f"{self.current_vehicle.get('armor_side')}-" +
                  f"{self.current_vehicle.get('armor_rear')}")

    def parse_line(self, line, line_num):
        """Parse a single line with state machine logic"""

        line = line.strip()

        # Skip empty lines
        if not line:
            return

        # Check for section header
        section = self.is_section_header(line)
        if section:
            self.current_section = section
            print(f"\n🏷️  Section: {section}")
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
                    'extraction_method': 'state_machine_parsing'
                }

                print(f"   🚗 Found: {line}")
                self.state = 'READING_MOVEMENT_1'

        elif self.state == 'READING_MOVEMENT_1':
            # Expecting first movement value (off-road)
            if self.is_movement_value(line):
                value = line.replace('"', '').replace("'", '').strip()
                self.current_vehicle['off_road_inches'] = int(value)
                self.state = 'READING_MOVEMENT_2'

        elif self.state == 'READING_MOVEMENT_2':
            # Expecting second movement value (road)
            if self.is_movement_value(line):
                value = line.replace('"', '').replace("'", '').strip()
                self.current_vehicle['road_inches'] = int(value)
                self.state = 'READING_ARMOR_1'

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

        elif self.state == 'READING_ARMOR_3':
            # Expecting third armor value (rear)
            if self.is_armor_value(line):
                self.current_vehicle['armor_rear'] = line.strip()
                self.state = 'READING_WEAPONS'

        elif self.state == 'READING_WEAPONS':
            # Collect weapon lines until we hit next vehicle or section
            if self.is_vehicle_name(line):
                # Next vehicle - restart
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
                    'extraction_method': 'state_machine_parsing'
                }
                print(f"   🚗 Found: {line}")
                self.state = 'READING_MOVEMENT_1'
            else:
                # Try to extract weapons from this line
                weapon_patterns = [
                    r'(\d+\s*pdr)',
                    r'(\d+mm[A-Z]*\d*)',
                    r'\b(MG)\b',
                    r'(Besa)',
                    r'(howitzer)',
                    r'(\d+\s*["\'])',
                ]

                for pattern in weapon_patterns:
                    weapons = re.findall(pattern, line, re.IGNORECASE)
                    for weapon in weapons:
                        if weapon not in self.current_vehicle['weapons']:
                            self.current_vehicle['weapons'].append(weapon)

    def finalize(self):
        """Save last vehicle and return results"""
        self.save_current_vehicle()
        return self.vehicles

def parse_tobruk_british_txt_improved(file_path):
    """Parse using improved state machine"""

    print("📖 Parsing Tobruk British.txt (Improved State Machine)...")
    print("="*70)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove BOM
    content = content.replace('\ufeff', '')

    parser = VehicleParser()

    for line_num, line in enumerate(content.split('\n'), 1):
        parser.parse_line(line, line_num)

    vehicles = parser.finalize()

    print(f"\n{'='*70}")
    print(f"✅ Parsing complete!")
    print(f"   Vehicles extracted: {len(vehicles)}")

    return vehicles

def import_improved_vehicles(conn, vehicles):
    """Import improved parsing results"""

    cursor = conn.cursor()

    # Clear previous import
    cursor.execute("DELETE FROM bg_reference_vehicles_txt_import")

    print(f"\n📥 Importing {len(vehicles)} vehicles (improved)...")

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

def compare_improved(conn):
    """Run comparison with improved parsing"""

    cursor = conn.cursor()

    print(f"\n{'='*70}")
    print("IMPROVED COMPARISON: Manual Entry vs TXT Parsing (State Machine)")
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

    # Get improved txt parsing
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

    # Field comparison for matched names
    field_names = ['vehicle_type', 'off_road_inches', 'road_inches',
                   'armor_front', 'armor_side', 'armor_rear', 'weapons', 'special_rules']

    field_matches = {f: 0 for f in field_names}
    field_total = len(common_names)

    perfect_matches = []
    mismatches = []

    for name in sorted(common_names):
        manual_data = manual_dict[name]
        txt_data = txt_dict[name]

        vehicle_mismatches = []
        match_count = 0

        for idx, field_name in enumerate(field_names):
            manual_val = manual_data[idx + 1]
            txt_val = txt_data[idx + 1]

            if manual_val == txt_val:
                field_matches[field_name] += 1
                match_count += 1
            else:
                vehicle_mismatches.append({
                    'field': field_name,
                    'manual': manual_val,
                    'txt': txt_val
                })

        if match_count == len(field_names):
            perfect_matches.append(name)
        elif vehicle_mismatches:
            mismatches.append({
                'name': name,
                'match_count': match_count,
                'total_fields': len(field_names),
                'mismatches': vehicle_mismatches
            })

    # Print results
    print("📊 Field Match Rates:")
    for field_name in field_names:
        if field_total > 0:
            match_pct = (field_matches[field_name] / field_total) * 100
            print(f"   {field_name:20s}: {field_matches[field_name]:3d}/{field_total} ({match_pct:5.1f}%)")

    total_comparisons = field_total * len(field_names)
    total_matches = sum(field_matches.values())
    overall_pct = (total_matches / total_comparisons * 100) if total_comparisons > 0 else 0

    print(f"\n✅ OVERALL MATCH: {total_matches}/{total_comparisons} ({overall_pct:.1f}%)")
    print(f"✅ PERFECT MATCHES: {len(perfect_matches)}/{field_total} vehicles")

    if perfect_matches:
        print(f"\n🎯 Perfect Matches (100% field match):")
        for name in perfect_matches[:10]:
            print(f"   ✅ {name}")
        if len(perfect_matches) > 10:
            print(f"   ... and {len(perfect_matches) - 10} more")

    if mismatches:
        print(f"\n⚠️  Mismatches ({len(mismatches)} vehicles):")
        for vehicle in sorted(mismatches, key=lambda x: -x['match_count'])[:10]:
            match_pct = (vehicle['match_count'] / vehicle['total_fields']) * 100
            print(f"\n   {vehicle['name']} ({match_pct:.0f}% match):")
            for mm in vehicle['mismatches'][:5]:
                print(f"      {mm['field']:18s}: '{mm['manual']}' vs '{mm['txt']}'")

    return {
        'total_matches': total_matches,
        'total_comparisons': total_comparisons,
        'overall_percentage': overall_pct,
        'perfect_matches': len(perfect_matches),
        'field_matches': field_matches
    }

def main():
    print("="*70)
    print("Tobruk British - Improved TXT Parser & Comparison")
    print("="*70 + "\n")

    txt_file = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Tobruk British.txt"
    db_file = r"D:\north-africa-toe-builder\database\master_database.db"

    # Parse with improved state machine
    vehicles = parse_tobruk_british_txt_improved(txt_file)

    # Connect to database
    conn = sqlite3.connect(db_file)

    # Import improved results
    import_improved_vehicles(conn, vehicles)

    # Run improved comparison
    result = compare_improved(conn)

    conn.close()

    print(f"\n{'='*70}")
    print("✨ Improved Analysis Complete!")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
