#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Correct Tobruk British.txt parser matching actual table structure

Based on actual Tobruk table format (Crusader I example):
- VEHICLE | MOVEMENT (Off-Road, Road, Special) | ARMOUR (Front, Side, Rear) | ARMAMENT (Weapon, Mount, Ammo)
- Mount field: Multiple entries (Turret, Co-axial, Hull) - one per weapon
- Ammo field: Multiple entries (13, -, -) - one per weapon
- Special movement: Captured in special_movement field
- open_topped: Separate field
- NO year_range inference (test scrape only)
"""

import sys
import io
import re
import sqlite3
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class TobrukTableParser:
    """Parser matching actual Tobruk table structure"""

    def __init__(self):
        self.vehicles = []
        self.current_vehicle = None
        self.state = 'LOOKING_FOR_VEHICLE'
        self.current_section = None
        self.weapon_lines = []
        self.mount_lines = []
        self.ammo_lines = []
        self.pending_name_fragment = None  # For multi-line vehicle names
        self.incomplete_marmon = False  # Track incomplete Marmon- names

    def is_section_header(self, line):
        """Check if line is a section header"""
        headers = ['LIGHT TANKS', 'INFANTRY TANKS', 'CRUISER TANKS',
                   'ARMOURED CARS', 'SOFT-SKINNED VEHICLES', "PORTEE'D GUNS",
                   'PORTEE', 'ANTI-TANK GUNS', 'FIELD ARTILLERY',
                   'ANTI-AIRCRAFT GUNS', 'ARMOURED VEHICLES']

        for header in headers:
            if header in line:
                return header
        return None

    def is_header_line(self, line):
        """Check if line is a table header"""
        header_keywords = ['VEHICLE', 'MOVEMENT', 'ARMOUR', 'ARMAMENT',
                           'Off-Road', 'Road', 'Special', 'Front', 'Side',
                           'Rear', 'Weapon', 'Mount', 'Ammo', 'Hits',
                           'Transport', 'Capacity']
        return any(keyword in line for keyword in header_keywords)

    def is_vehicle_name(self, line):
        """Check if line is a vehicle name"""
        # Skip if it's a header line
        if self.is_header_line(line):
            return False

        # Skip pure section headers
        if self.is_section_header(line):
            return False

        # Skip lines that are clearly not vehicle names or page headers
        skip_list = ['BATTLE GROUP TOBRUP', 'GROUP TOBRUK', 'BRITISH EQUIPMENT',
                     'Vickers VI A', 'Medium Bomber', 'Light Bomber', 'Heavy Bomber',
                     'MEDIUM GUNS', 'LIGHT GUNS', 'HEAVY GUNS']
        if line in skip_list:
            return False

        # Vehicle name patterns
        vehicle_patterns = [
            r'^(Vickers\s+\w+)',
            r'^(M3\s+)',
            r'^(Matilda\s+)',
            r'^(Valentine\s+)',
            r'^(A\d+)',
            r'^(Crusader\s+)',
            r'^(Morris\s+)',
            r'^(Austin\s+)',
            r'^(Bedford\s+)',
            r'^(Scammel\s+)',
            r'^(Hippo\s+)',
            r'^(Matador\s+)',
            r'^(Chev)',
            r'^(Humber\s+)',
            r'^(Daimler\s+)',
            r'^(Marmon)',
            r'^(Herrington)',  # Abbreviated Marmon-Herrington
            r'^(Medium\s+)',   # Medium Truck
            r'^(Motorcycle)',
            r'^(Ford\s+)',
            r'^(Quad\s+)',
        ]

        for pattern in vehicle_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False

    def is_movement_value(self, line):
        """Check if line is a movement value"""
        return re.match(r'^\d+["\']?[A-Z]?\s*$', line.strip()) is not None

    def is_armor_value(self, line):
        """Check if line is an armor value"""
        return re.match(r'^([I-O]|SS)\s*$', line.strip()) is not None

    def is_special_movement(self, line):
        """Check if line is a special movement rule"""
        special_movements = ['Unreliable', 'Slow', 'Fast', 'Amphibious']
        return any(sm in line for sm in special_movements)

    def parse_weapons(self, lines):
        """Parse weapon lines into list"""
        weapons = []
        for line in lines:
            # Split by spaces and extract weapons
            tokens = line.split()
            for token in tokens:
                # Check if it's a weapon pattern
                if re.match(r'\d+\s*pdr', token, re.IGNORECASE):
                    weapons.append(token)
                elif re.match(r'\d+mm', token, re.IGNORECASE):
                    weapons.append(token)
                elif re.match(r'\d+["\']', token):
                    weapons.append(token)
                elif token.upper() in ['MG', 'HMG', 'LMG', 'BESA']:
                    weapons.append(token)
                elif 'howitzer' in token.lower():
                    weapons.append(token)
                elif re.match(r'AT\s+Rifle', token, re.IGNORECASE):
                    weapons.append('AT Rifle')
        return weapons

    def parse_mounts(self, lines):
        """Parse mount lines into list"""
        mounts = []
        for line in lines:
            # Split by spaces and extract mount types
            tokens = line.split()
            for token in tokens:
                if token in ['Turret', 'Co-axial', 'Hull', 'Fixed', 'Pintle', 'Bow']:
                    mounts.append(token)
        return mounts

    def parse_ammo(self, lines):
        """Parse ammo lines into list"""
        ammo = []
        for line in lines:
            # Extract numbers or dashes
            tokens = line.split()
            for token in tokens:
                if re.match(r'^\d+$', token):
                    ammo.append(token)
                elif token == '-':
                    ammo.append('-')
        return ammo

    def finalize_armament(self):
        """Process collected weapon/mount/ammo lines"""
        if not self.current_vehicle:
            return

        # Parse weapons
        weapons = []
        for line in self.weapon_lines:
            # Simple space-separated parsing
            parts = line.split()
            for part in parts:
                # Check weapon patterns
                if (re.match(r'\d+\s*pdr', part, re.IGNORECASE) or
                    re.match(r'\d+mm', part, re.IGNORECASE) or
                    re.match(r'\d+["\']', part) or
                    part.upper() in ['MG', 'HMG', 'LMG', 'BESA'] or
                    'howitzer' in part.lower()):
                    weapons.append(part)

        # Parse mounts
        mounts = []
        for line in self.mount_lines:
            parts = line.split()
            for part in parts:
                if part in ['Turret', 'Co-axial', 'Hull', 'Fixed', 'Pintle', 'Bow']:
                    mounts.append(part)

        # Parse ammo
        ammo = []
        for line in self.ammo_lines:
            parts = line.split()
            for part in parts:
                if re.match(r'^\d+$', part) or part == '-':
                    ammo.append(part)

        # Store as comma-separated strings
        self.current_vehicle['weapons'] = ', '.join(weapons) if weapons else ''
        self.current_vehicle['mount'] = ', '.join(mounts) if mounts else ''
        self.current_vehicle['ammo'] = ', '.join(ammo) if ammo else ''

        # Clear buffers
        self.weapon_lines = []
        self.mount_lines = []
        self.ammo_lines = []

    def save_current_vehicle(self):
        """Save current vehicle to list"""
        if self.current_vehicle and self.current_vehicle.get('name'):
            # Finalize any pending armament data
            self.finalize_armament()

            self.vehicles.append(self.current_vehicle)
            special = str(self.current_vehicle.get('special_movement') or '-')
            print(f"   ✅ {self.current_vehicle['name']:30s}: " +
                  f"Move={self.current_vehicle.get('off_road_inches', '?')}/{self.current_vehicle.get('road_inches', '?')} " +
                  f"Special={special:12s} " +
                  f"Armor={self.current_vehicle.get('armor_front', '?')}-{self.current_vehicle.get('armor_side', '?')}-{self.current_vehicle.get('armor_rear', '?')}")

    def parse_line(self, line, line_num):
        """Parse a single line"""

        line = line.strip()

        # Skip empty lines
        if not line:
            return

        # Check for "Herrington *" to complete Marmon- names
        if self.current_vehicle and self.current_vehicle.get('name') == 'Marmon-':
            if re.match(r'^Herrington\s+\w+', line):
                self.current_vehicle['name'] = f"Marmon-{line}"
                print(f"      → Completed name: Marmon-{line}")
                return

        # Check for section header
        section = self.is_section_header(line)
        if section:
            self.current_section = section
            print(f"\n🏷️  Section: {section}")
            self.state = 'LOOKING_FOR_VEHICLE'
            return

        # Skip table headers
        if self.is_header_line(line):
            return

        # Universal vehicle name check - works in any state
        # This catches vehicles that appear while processing previous vehicle's data
        if self.state != 'LOOKING_FOR_VEHICLE' and self.is_vehicle_name(line):
            # Save current vehicle and start new one
            self.save_current_vehicle()
            self.current_vehicle = {
                'name': line,
                'nation': 'British',
                'vehicle_type': self.current_section or None,
                'off_road_inches': None,
                'road_inches': None,
                'special_movement': None,
                'armor_front': None,
                'armor_side': None,
                'armor_rear': None,
                'weapons': '',
                'mount': '',
                'ammo': '',
                'special_rules': '',
                'open_topped': None,
                'source_file': 'Tobruk British.txt',
                'extraction_method': 'final_correct_parsing'
            }
            print(f"   🚗 Found: {line}")
            self.state = 'READING_MOVEMENT_1'
            return

        # State machine
        if self.state == 'LOOKING_FOR_VEHICLE':
            # Handle multi-line vehicle names (e.g., "Marmon-" + "Herrington I")
            if self.pending_name_fragment:
                # Check if current line could be second part of name
                if re.match(r'^(Herrington|[A-Z][a-z]+)\s+', line):
                    # Concatenate the name
                    full_name = self.pending_name_fragment + line
                    self.pending_name_fragment = None
                    line = full_name
                else:
                    # Not a continuation, treat fragment as complete name
                    line = self.pending_name_fragment
                    self.pending_name_fragment = None

            # Check if line ends with hyphen (split name)
            if line.endswith('-') and self.is_vehicle_name(line):
                self.pending_name_fragment = line
                return

            if self.is_vehicle_name(line):
                # Save previous vehicle
                self.save_current_vehicle()

                # Start new vehicle
                self.current_vehicle = {
                    'name': line,
                    'nation': 'British',
                    'vehicle_type': self.current_section or None,
                    'off_road_inches': None,
                    'road_inches': None,
                    'special_movement': None,
                    'armor_front': None,
                    'armor_side': None,
                    'armor_rear': None,
                    'weapons': '',
                    'mount': '',
                    'ammo': '',
                    'special_rules': '',
                    'open_topped': None,
                    'source_file': 'Tobruk British.txt',
                    'extraction_method': 'final_correct_parsing'
                }

                print(f"   🚗 Found: {line}")
                self.state = 'READING_MOVEMENT_1'

        elif self.state == 'READING_MOVEMENT_1':
            # Expecting first movement value (off-road)
            if self.is_movement_value(line):
                value = line.replace('"', '').replace("'", '').strip()
                # Remove letters (like "H" in "6"H")
                value = re.sub(r'[A-Z]', '', value)
                try:
                    self.current_vehicle['off_road_inches'] = int(value)
                except:
                    pass
                self.state = 'READING_MOVEMENT_2'

        elif self.state == 'READING_MOVEMENT_2':
            # Expecting second movement value (road)
            if self.is_movement_value(line):
                value = line.replace('"', '').replace("'", '').strip()
                value = re.sub(r'[A-Z]', '', value)
                try:
                    self.current_vehicle['road_inches'] = int(value)
                except:
                    pass
                self.state = 'READING_SPECIAL_OR_ARMOR'
            elif self.is_special_movement(line):
                self.current_vehicle['special_movement'] = line
                self.state = 'READING_ARMOR_1'

        elif self.state == 'READING_SPECIAL_OR_ARMOR':
            # Could be special movement or first armor value
            if self.is_special_movement(line):
                self.current_vehicle['special_movement'] = line
                self.state = 'READING_ARMOR_1'
            elif self.is_armor_value(line):
                self.current_vehicle['armor_front'] = line.strip()
                self.state = 'READING_ARMOR_2'
            else:
                # Assume no special movement, go to armor
                self.state = 'READING_ARMOR_1'
                # Re-process this line as armor
                if self.is_armor_value(line):
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

        elif self.state == 'READING_ARMOR_3':
            # Expecting third armor value (rear)
            if self.is_armor_value(line):
                self.current_vehicle['armor_rear'] = line.strip()
                self.state = 'READING_WEAPONS'
            else:
                # Might go straight to weapons
                self.state = 'READING_WEAPONS'
                # Don't process this line, will be caught as weapon

        elif self.state == 'READING_WEAPONS':
            # Collect weapon/mount/ammo lines
            if self.is_vehicle_name(line):
                # Next vehicle
                self.save_current_vehicle()
                self.current_vehicle = {
                    'name': line,
                    'nation': 'British',
                    'vehicle_type': self.current_section or None,
                    'off_road_inches': None,
                    'road_inches': None,
                    'special_movement': None,
                    'armor_front': None,
                    'armor_side': None,
                    'armor_rear': None,
                    'weapons': '',
                    'mount': '',
                    'ammo': '',
                    'special_rules': '',
                    'open_topped': None,
                    'source_file': 'Tobruk British.txt',
                    'extraction_method': 'final_correct_parsing'
                }
                print(f"   🚗 Found: {line}")
                self.state = 'READING_MOVEMENT_1'

            # Check if line contains mount keywords
            elif any(mount in line for mount in ['Turret', 'Co-axial', 'Hull', 'Fixed', 'Pintle', 'Bow']):
                self.mount_lines.append(line)

            # Check if line is pure numbers or dashes (ammo)
            elif re.match(r'^[\d\s-]+$', line):
                self.ammo_lines.append(line)

            # Check if it's open-topped
            elif 'open-topped' in line.lower() or 'open topped' in line.lower():
                self.current_vehicle['open_topped'] = 'Yes'

            # Otherwise treat as weapon line
            elif not self.is_header_line(line):
                self.weapon_lines.append(line)

    def finalize(self):
        """Save last vehicle and return results"""
        self.save_current_vehicle()
        return self.vehicles

def parse_tobruk_final(file_path):
    """Parse using final correct format"""

    print("📖 Parsing Tobruk British.txt (Final Correct Format)...")
    print("="*70)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove BOM
    content = content.replace('\ufeff', '')

    parser = TobrukTableParser()

    for line_num, line in enumerate(content.split('\n'), 1):
        parser.parse_line(line, line_num)

    vehicles = parser.finalize()

    print(f"\n{'='*70}")
    print(f"✅ Parsing complete!")
    print(f"   Vehicles extracted: {len(vehicles)}")
    print(f"   Expected: 29 vehicles")
    if len(vehicles) != 29:
        print(f"   ⚠️  Missing {29 - len(vehicles)} vehicles!")

    return vehicles

def create_correct_schema(conn):
    """Create table with correct schema (mount, ammo, open_topped)"""

    cursor = conn.cursor()

    print("\n📋 Creating table with correct schema...")

    # Drop if exists
    cursor.execute("DROP TABLE IF EXISTS bg_reference_vehicles_txt_final")

    # Create with correct schema
    cursor.execute("""
        CREATE TABLE bg_reference_vehicles_txt_final (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            nation TEXT,
            vehicle_type TEXT,
            off_road_inches INTEGER,
            road_inches INTEGER,
            special_movement TEXT,
            armor_front TEXT,
            armor_side TEXT,
            armor_rear TEXT,
            weapons TEXT,
            mount TEXT,
            ammo TEXT,
            special_rules TEXT,
            open_topped TEXT,
            source_file TEXT,
            extraction_method TEXT
        )
    """)

    conn.commit()
    print("✅ Table created with mount, ammo, open_topped fields")

def import_final_vehicles(conn, vehicles):
    """Import with correct schema"""

    cursor = conn.cursor()

    print(f"\n📥 Importing {len(vehicles)} vehicles...")

    for vehicle in vehicles:
        cursor.execute("""
            INSERT INTO bg_reference_vehicles_txt_final
            (name, nation, vehicle_type, off_road_inches, road_inches,
             special_movement, armor_front, armor_side, armor_rear,
             weapons, mount, ammo, special_rules, open_topped,
             source_file, extraction_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vehicle['name'],
            vehicle['nation'],
            vehicle['vehicle_type'],
            vehicle.get('off_road_inches'),
            vehicle.get('road_inches'),
            vehicle.get('special_movement'),
            vehicle.get('armor_front'),
            vehicle.get('armor_side'),
            vehicle.get('armor_rear'),
            vehicle.get('weapons', ''),
            vehicle.get('mount', ''),
            vehicle.get('ammo', ''),
            vehicle.get('special_rules', ''),
            vehicle.get('open_topped'),
            vehicle['source_file'],
            vehicle['extraction_method']
        ))

    conn.commit()
    print(f"✅ Imported {len(vehicles)} vehicles")

def main():
    print("="*70)
    print("Tobruk British - Final Correct Parser")
    print("="*70 + "\n")

    txt_file = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Tobruk British.txt"
    db_file = r"D:\north-africa-toe-builder\database\master_database.db"

    # Parse
    vehicles = parse_tobruk_final(txt_file)

    # Connect to database
    conn = sqlite3.connect(db_file)

    # Create correct schema table
    create_correct_schema(conn)

    # Import
    import_final_vehicles(conn, vehicles)

    conn.close()

    print(f"\n{'='*70}")
    print("✨ Final Parsing Complete!")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
