#!/usr/bin/env python3
"""
BattleGroup Datacard Scraper

Extracts vehicle and gun profiles from BattleGroup text files to build
a reference database for conversion formula development.

Input Files:
- Resource Documents/Battlegroup Game/Battlegroup-Kursk.txt
- Resource Documents/Battlegroup Game/Battlegroup-DataCards-British.txt
- Resource Documents/Battlegroup Game/Avanti Italian Forces.txt
- Additional datacard PDFs (future)

Output:
- SQLite database: database/battlegroup_reference.db
  - bg_reference_vehicles table (200+ vehicle profiles)
  - bg_reference_guns table (150+ gun profiles)

Usage:
    python scripts/battlegroup/scrapers/datacard_scraper.py
    python scripts/battlegroup/scrapers/datacard_scraper.py --file "path/to/datacard.txt"
    python scripts/battlegroup/scrapers/datacard_scraper.py --stats  # Show database stats
"""

import re
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESOURCE_DIR = PROJECT_ROOT / "Resource Documents" / "Battlegroup Game"
DB_PATH = PROJECT_ROOT / "database" / "master_database.db"  # Integrated with master database


@dataclass
class VehicleProfile:
    """Represents a complete BattleGroup vehicle datacard"""
    name: str
    nation: str
    year_range: str  # e.g., "1941-1943"
    vehicle_type: str  # tank, light_tank, armored_car, halftrack, etc.

    # Movement
    off_road_inches: Optional[int] = None
    road_inches: Optional[int] = None
    special_movement: Optional[str] = None  # Unreliable, Amphib, etc.

    # Armor (letter scale A-O)
    armor_front: Optional[str] = None
    armor_side: Optional[str] = None
    armor_rear: Optional[str] = None

    # Weapons (JSON array of weapon objects)
    weapons: str = "[]"  # JSON string

    # Game stats
    points_cost: Optional[int] = None
    battle_rating: Optional[int] = None

    # Special rules
    special_rules: Optional[str] = None  # Comma-separated

    # Source metadata
    source_file: Optional[str] = None
    source_page: Optional[str] = None
    extraction_confidence: str = "high"  # high, medium, low
    notes: Optional[str] = None


@dataclass
class GunProfile:
    """Represents a complete BattleGroup gun profile"""
    name: str
    nation: str
    caliber_mm: Optional[int] = None
    barrel_length: Optional[str] = None  # e.g., "L60", "L40"

    # HE Performance (dice/target format: "4/4+")
    he_dice: Optional[int] = None
    he_target: Optional[str] = None  # "3+", "4+", "5+", "6+"

    # AP Penetration by range band (0-10", 10-20", 20-30", 30-40", 40-50", 50-70")
    ap_0_10: Optional[int] = None
    ap_10_20: Optional[int] = None
    ap_20_30: Optional[int] = None
    ap_30_40: Optional[int] = None
    ap_40_50: Optional[int] = None
    ap_50_70: Optional[int] = None

    # Game stats
    points_cost: Optional[int] = None
    battle_rating: Optional[int] = None

    # Source metadata
    source_file: Optional[str] = None
    source_page: Optional[str] = None
    extraction_confidence: str = "high"
    notes: Optional[str] = None


class DatacardScraper:
    """Scrapes BattleGroup datacards from text files"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with tables"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # Create vehicles table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bg_reference_vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                nation TEXT NOT NULL,
                year_range TEXT,
                vehicle_type TEXT,
                off_road_inches INTEGER,
                road_inches INTEGER,
                special_movement TEXT,
                armor_front TEXT,
                armor_side TEXT,
                armor_rear TEXT,
                weapons TEXT,  -- JSON array
                points_cost INTEGER,
                battle_rating INTEGER,
                special_rules TEXT,
                source_file TEXT,
                source_page TEXT,
                extraction_confidence TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, nation, year_range)
            )
        """)

        # Create guns table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bg_reference_guns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                nation TEXT NOT NULL,
                caliber_mm INTEGER,
                barrel_length TEXT,
                he_dice INTEGER,
                he_target TEXT,
                ap_0_10 INTEGER,
                ap_10_20 INTEGER,
                ap_20_30 INTEGER,
                ap_30_40 INTEGER,
                ap_40_50 INTEGER,
                ap_50_70 INTEGER,
                points_cost INTEGER,
                battle_rating INTEGER,
                source_file TEXT,
                source_page TEXT,
                extraction_confidence TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, nation)
            )
        """)

        # Create extraction log
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS extraction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                vehicles_extracted INTEGER DEFAULT 0,
                guns_extracted INTEGER DEFAULT 0,
                extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)

        self.conn.commit()
        print(f"[OK] Database initialized: {self.db_path}")

    def scrape_file(self, file_path: Path, nation: str = None) -> Tuple[int, int]:
        """
        Scrape a BattleGroup text file for vehicle and gun profiles

        Args:
            file_path: Path to text file
            nation: Nation to assign (german, british, italian, american)
                   If None, will attempt to detect from filename

        Returns:
            Tuple of (vehicles_count, guns_count)
        """
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 0, 0

        # Detect nation from filename if not provided
        if nation is None:
            filename_lower = file_path.name.lower()
            if "british" in filename_lower or "british" in str(file_path).lower():
                nation = "british"
            elif "german" in filename_lower or "kursk" in filename_lower:
                nation = "german"
            elif "italian" in filename_lower or "avanti" in filename_lower:
                nation = "italian"
            elif "american" in filename_lower or "usa" in filename_lower:
                nation = "american"
            else:
                nation = "unknown"

        print(f"\n[FILE] Processing: {file_path.name}")
        print(f"   Nation: {nation}")

        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Detect format type: Kursk table vs datacard
        is_datacard_format = "DataCards" in file_path.name or "DataCard" in file_path.name
        format_type = "datacard" if is_datacard_format else "table"
        print(f"   Format: {format_type}")

        # Use appropriate parser for format
        if is_datacard_format:
            vehicles = self._extract_vehicles_from_datacards(content, nation, file_path.name)
        else:
            vehicles = self._extract_vehicles(content, nation, file_path.name)

        guns = self._extract_guns(content, nation, file_path.name)

        # Insert into database
        vehicles_inserted = self._insert_vehicles(vehicles)
        guns_inserted = self._insert_guns(guns)

        # Log extraction
        self.conn.execute("""
            INSERT INTO extraction_log (file_path, vehicles_extracted, guns_extracted)
            VALUES (?, ?, ?)
        """, (str(file_path), vehicles_inserted, guns_inserted))
        self.conn.commit()

        print(f"   [OK] Extracted: {vehicles_inserted} vehicles, {guns_inserted} guns")

        return vehicles_inserted, guns_inserted

    def _extract_vehicles(self, content: str, nation: str, source_file: str) -> List[VehicleProfile]:
        """Extract vehicle profiles from content"""
        vehicles = []
        lines = content.split('\n')

        # Find vehicle table sections
        # Look for "VEHICLE" header followed by "MOVEMENT" and "ARMOUR"
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if this is a vehicle table header
            if 'VEHICLE' in line.upper() and 'MOVEMENT' in line.upper() and 'ARMOUR' in line.upper():
                # Skip the sub-header line (Off-Road, Road, etc.)
                i += 1
                if i < len(lines) and ('Off-Road' in lines[i] or 'Road' in lines[i]):
                    i += 1

                # Skip blank lines
                while i < len(lines) and not lines[i].strip():
                    i += 1

                # Now extract vehicles until we hit a section break
                while i < len(lines):
                    veh_line = lines[i].strip()

                    # Stop if we hit a new section (all caps header, page number, or another table)
                    if not veh_line or veh_line.isupper() and len(veh_line) > 20:
                        break
                    if re.match(r'^\d+$', veh_line):  # Page numbers
                        break
                    if 'VEHICLE' in veh_line.upper() and 'MOVEMENT' in veh_line.upper():
                        break

                    # Try to extract vehicle name (should be at start of line, may have variants)
                    # Pattern: "Panzer III J" or "M4 Sherman (A1, A2)"
                    vehicle_name_match = re.match(r'^([A-Za-z0-9\s\-\'/]+(?:\([^)]+\))?)', veh_line)

                    if vehicle_name_match:
                        vehicle_name = vehicle_name_match.group(1).strip()

                        # Skip if this looks like a table continuation
                        if vehicle_name.lower().startswith('weapon') or vehicle_name.lower().startswith('mg'):
                            i += 1
                            continue

                        # Next line should have the vehicle data
                        i += 1
                        if i >= len(lines):
                            break

                        data_line = lines[i]

                        # Try to parse the data line
                        # Format: movement(off-road road special) armor(front side rear) weapon mount ammo
                        # Example: "  8" 12" - L N N                                                              50mmL42        Turret        10"

                        # Extract movement (first two numbers with quotes)
                        movement_match = re.search(r'(\d+)"?\s+(\d+)"?\s+([A-Za-z\-]*)\s+([A-O])\s+([A-O])\s+([A-O])', data_line)

                        if movement_match:
                            off_road = int(movement_match.group(1))
                            road = int(movement_match.group(2))
                            special = movement_match.group(3).strip() if movement_match.group(3).strip() != '-' else None
                            armor_front = movement_match.group(4)
                            armor_side = movement_match.group(5)
                            armor_rear = movement_match.group(6)

                            # Extract weapons (may span multiple lines)
                            weapons = []
                            weapon_line = data_line[movement_match.end():]

                            # Parse first weapon from same line
                            weapon_match = re.search(r'(\d+mm\s*L?\d*|MG|HMG)\s+(Turret|Co-axial|Bow|Hull|Fixed)\s+(\d+|-)', weapon_line)
                            if weapon_match:
                                weapons.append({
                                    'weapon': weapon_match.group(1).strip(),
                                    'mount': weapon_match.group(2).strip(),
                                    'ammo': weapon_match.group(3) if weapon_match.group(3) != '-' else None
                                })

                            # Check next lines for additional weapons
                            temp_i = i + 1
                            while temp_i < len(lines):
                                next_line = lines[temp_i]
                                # Additional weapons are indented and start with weapon designation
                                if re.match(r'^\s{20,}(MG|HMG|\d+mm)', next_line):
                                    weapon_match = re.search(r'(MG|HMG|\d+mm[^A-Z]*)\s+(Turret|Co-axial|Bow|Hull|Fixed)\s+(\d+|-)', next_line)
                                    if weapon_match:
                                        weapons.append({
                                            'weapon': weapon_match.group(1).strip(),
                                            'mount': weapon_match.group(2).strip(),
                                            'ammo': weapon_match.group(3) if weapon_match.group(3) != '-' else None
                                        })
                                    temp_i += 1
                                else:
                                    break

                            # Create vehicle profile
                            vehicle = VehicleProfile(
                                name=vehicle_name,
                                nation=nation,
                                year_range=None,  # TODO: Extract from section header or name
                                vehicle_type=self._classify_vehicle_type(vehicle_name),
                                off_road_inches=off_road,
                                road_inches=road,
                                special_movement=special,
                                armor_front=armor_front,
                                armor_side=armor_side,
                                armor_rear=armor_rear,
                                weapons=json.dumps(weapons),
                                source_file=source_file,
                                extraction_confidence='high' if weapons else 'medium'
                            )

                            vehicles.append(vehicle)

                    i += 1
            else:
                i += 1

        return vehicles

    def _classify_vehicle_type(self, name: str) -> str:
        """Classify vehicle type from name"""
        name_lower = name.lower()

        if 'panzer i' in name_lower or 'l3' in name_lower or 'stuart' in name_lower:
            return 'light_tank'
        elif 'panzer' in name_lower or 'tiger' in name_lower or 'sherman' in name_lower or 't-34' in name_lower or 'kv-' in name_lower:
            return 'tank'
        elif 'armored car' in name_lower or 'sdkfz 222' in name_lower or 'daimler' in name_lower or 'ab41' in name_lower:
            return 'armored_car'
        elif 'halftrack' in name_lower or 'sdkfz 251' in name_lower or 'carrier' in name_lower:
            return 'halftrack'
        elif 'truck' in name_lower or 'lorry' in name_lower:
            return 'truck'
        else:
            return 'unknown'

    def _extract_vehicles_from_datacards(self, content: str, nation: str, source_file: str) -> List[VehicleProfile]:
        """
        Extract vehicle profiles from datacard format (card-based layout).
        Different from Kursk table format - each vehicle is its own card.

        Format:
            M4 SHERMAN
            1942-1945
            Description text

            VEHICLE    MOVEMENT       ARMOUR      ARMAMENT
                    Off-Road Road Special F S R  Weapon  Mount Ammo
            M4 Sherman  9"   14"    -   K L N   75mmL40 Turret  9
                                                 MG      Co-axial -
        """
        vehicles = []
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for VEHICLE header as primary trigger
            if 'VEHICLE' in line.upper() and 'MOVEMENT' in line.upper() and 'ARMOUR' in line.upper():
                header_line = i

                # Look backwards for vehicle name (should be 1-5 lines before, all caps)
                vehicle_name = "Unknown"
                year_range = None
                for j in range(max(0, header_line - 5), header_line):
                    back_line = lines[j].strip()
                    # Look for all-caps line that's a reasonable length
                    if back_line and len(back_line) > 2 and len(back_line) < 60:
                        # Check if mostly uppercase (handles OCR errors)
                        upper_chars = sum(1 for c in back_line if c.isupper())
                        total_alpha = sum(1 for c in back_line if c.isalpha())
                        if total_alpha > 0 and upper_chars / total_alpha > 0.7:
                            vehicle_name = back_line

                            # Check next line for year
                            if j + 1 < len(lines):
                                year_line = lines[j + 1].strip()
                                year_match = re.match(r'^(\d{4})[-\s](\d{4})$', year_line)
                                if year_match:
                                    year_range = f"{year_match.group(1)}-{year_match.group(2)}"
                            break

                # Find the data line (has movement values with inches)
                data_line_idx = None
                for j in range(header_line + 1, min(header_line + 5, len(lines))):
                    data_line = lines[j].strip()
                    # Data line has digits followed by " and more digits
                    if re.search(r'\d+"\s+\d+"', data_line):
                        data_line_idx = j
                        break

                if data_line_idx is None:
                    i += 1
                    continue

                data_line = lines[data_line_idx].strip()

                # Extract movement values (first two digits with ")
                movement_match = re.search(r'(\d+)"\s+(\d+)"', data_line)
                off_road = int(movement_match.group(1)) if movement_match else None
                road = int(movement_match.group(2)) if movement_match else None

                # Extract special movement (between movement and armor)
                special = None
                if movement_match:
                    after_movement = data_line[movement_match.end():].strip()
                    special_match = re.match(r'^([\w\-]+)\s+', after_movement)
                    if special_match and special_match.group(1) not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']:
                        special = special_match.group(1) if special_match.group(1) != '-' else None

                # Extract armor values (3 single letters A-O)
                armor_match = re.search(r'\b([A-O])\s+([A-O])\s+([A-O])\b', data_line)
                armor_front = armor_match.group(1) if armor_match else None
                armor_side = armor_match.group(2) if armor_match else None
                armor_rear = armor_match.group(3) if armor_match else None

                # Extract weapons (after armor or after special)
                weapons = []
                if armor_match:
                    weapons_text = data_line[armor_match.end():].strip()
                elif movement_match:
                    weapons_text = data_line[movement_match.end():].strip()
                else:
                    weapons_text = ""

                # Parse main weapon
                weapon_match = re.search(r'(\d+mm\w*|\w+pdr|MG|HMG)\s+(Turret|Co-axial|Hull|Bow|Fixed|Pin[tl]e|Mouilt)\s+(\d+|-)', weapons_text)
                if weapon_match:
                    weapons.append({
                        'weapon': weapon_match.group(1).strip(),
                        'mount': weapon_match.group(2).strip().replace('Mouilt', 'Mount'),
                        'ammo': int(weapon_match.group(3)) if weapon_match.group(3).isdigit() else None
                    })

                # Check next few lines for additional weapons
                j = data_line_idx + 1
                while j < len(lines) and j < data_line_idx + 5:
                    extra_line = lines[j].strip()
                    if not extra_line or 'WEAPON' in extra_line.upper() or 'VEHICLE' in extra_line.upper():
                        break
                    extra_match = re.search(r'(\d+mm\w*|\w+pdr|MG|HMG)\s+(Turret|Co-axial|Hull|Bow|Fixed|Pin[tl]e)\s+(\d+|-)', extra_line)
                    if extra_match:
                        weapons.append({
                            'weapon': extra_match.group(1).strip(),
                            'mount': extra_match.group(2).strip(),
                            'ammo': int(extra_match.group(3)) if extra_match.group(3).isdigit() else None
                        })
                    j += 1

                # Create vehicle profile
                vehicle = VehicleProfile(
                    name=vehicle_name,
                    nation=nation,
                    year_range=year_range,
                    vehicle_type=self._classify_vehicle_type(vehicle_name),
                    off_road_inches=off_road,
                    road_inches=road,
                    special_movement=special,
                    armor_front=armor_front,
                    armor_side=armor_side,
                    armor_rear=armor_rear,
                    weapons=json.dumps(weapons) if weapons else None,
                    source_file=source_file,
                    extraction_confidence='medium'
                )

                vehicles.append(vehicle)

                # Skip past this vehicle card
                i = data_line_idx + 5
            else:
                i += 1

        return vehicles

    def _extract_guns(self, content: str, nation: str, source_file: str) -> List[GunProfile]:
        """Extract gun profiles from content"""
        guns = []
        lines = content.split('\n')

        # Find gun table sections
        # Look for "WEAPON" header followed by "AMMO" and "HE EFFECT" and "RANGE"
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if this is a gun table header
            if 'WEAPON' in line.upper() and 'AMMO' in line.upper() and 'HE EFFECT' in line.upper() and 'RANGE' in line.upper():
                # Skip the sub-header line (0-10", 10-20", etc.)
                i += 1
                if i < len(lines) and '0-10' in lines[i]:
                    i += 1

                # Skip blank lines
                while i < len(lines) and not lines[i].strip():
                    i += 1

                # Now extract guns until we hit a section break
                while i < len(lines):
                    gun_line = lines[i].strip()

                    # Stop if we hit a new section
                    if not gun_line:
                        i += 1
                        continue
                    if gun_line.isupper() and len(gun_line) > 20:
                        break
                    if re.match(r'^\d+$', gun_line):  # Page numbers
                        break
                    if 'WEAPON' in gun_line.upper() and 'AMMO' in gun_line.upper():
                        break

                    # Try to extract gun name with HE data
                    # Pattern: "50mmL60 (PaK38)    HE      3/5+       2        2        2        2        2        -"
                    #                                                  ^0-10   ^10-20  ^20-30   ^30-40   ^40-50  ^50-70

                    # Match gun name: caliber + barrel length + optional designation
                    gun_match = re.match(r'^(\d+mm\s*L?\d*)\s*(\([^)]+\))?\s+(HE|AP)', gun_line, re.IGNORECASE)

                    if gun_match:
                        gun_name_base = gun_match.group(1).strip()
                        designation = gun_match.group(2).strip('()') if gun_match.group(2) else None
                        gun_name = f"{gun_name_base} ({designation})" if designation else gun_name_base

                        # Extract caliber from name (e.g., "50mm" -> 50)
                        caliber_match = re.search(r'(\d+)mm', gun_name_base)
                        caliber = int(caliber_match.group(1)) if caliber_match else None

                        # Extract barrel length (e.g., "L60")
                        barrel_match = re.search(r'L(\d+)', gun_name_base, re.IGNORECASE)
                        barrel_length = f"L{barrel_match.group(1)}" if barrel_match else None

                        # Now parse the HE and AP lines
                        he_dice = None
                        he_target = None
                        ap_0_10 = None
                        ap_10_20 = None
                        ap_20_30 = None
                        ap_30_40 = None
                        ap_40_50 = None
                        ap_50_70 = None

                        # Check if current line has HE data
                        if 'HE' in gun_line.upper():
                            # Parse HE effect (e.g., "3/5+")
                            he_match = re.search(r'HE\s+(\d+)/(\d\+)', gun_line, re.IGNORECASE)
                            if he_match:
                                he_dice = int(he_match.group(1))
                                he_target = he_match.group(2)

                            # Parse HE range values (6 numbers or dashes)
                            # After HE effect, there should be 6 range band values
                            he_ranges = re.findall(r'(\d+|-)\s+(\d+|-)\s+(\d+|-)\s+(\d+|-)\s+(\d+|-)\s+(\d+|-)', gun_line[he_match.end():] if he_match else gun_line)
                            if he_ranges:
                                # HE values are constant across range (stored but not critical)
                                pass

                        # Check next line for AP data
                        i += 1
                        if i < len(lines):
                            ap_line = lines[i].strip()
                            if 'AP' in ap_line.upper():
                                # Parse AP penetration values
                                # Example: "AP        -        5        5        4        3        2        -"
                                ap_values = re.findall(r'(\d+|-)', ap_line)
                                if len(ap_values) >= 6:
                                    # Skip first value (the dash in "AP -")
                                    # Take next 6 values as range bands
                                    start_idx = 1 if ap_values[0] == '-' else 0
                                    if len(ap_values) > start_idx + 5:
                                        ap_0_10 = int(ap_values[start_idx]) if ap_values[start_idx] != '-' else None
                                        ap_10_20 = int(ap_values[start_idx + 1]) if ap_values[start_idx + 1] != '-' else None
                                        ap_20_30 = int(ap_values[start_idx + 2]) if ap_values[start_idx + 2] != '-' else None
                                        ap_30_40 = int(ap_values[start_idx + 3]) if ap_values[start_idx + 3] != '-' else None
                                        ap_40_50 = int(ap_values[start_idx + 4]) if ap_values[start_idx + 4] != '-' else None
                                        ap_50_70 = int(ap_values[start_idx + 5]) if ap_values[start_idx + 5] != '-' else None

                        # Create gun profile
                        gun = GunProfile(
                            name=gun_name,
                            nation=nation,
                            caliber_mm=caliber,
                            barrel_length=barrel_length,
                            he_dice=he_dice,
                            he_target=he_target,
                            ap_0_10=ap_0_10,
                            ap_10_20=ap_10_20,
                            ap_20_30=ap_20_30,
                            ap_30_40=ap_30_40,
                            ap_40_50=ap_40_50,
                            ap_50_70=ap_50_70,
                            source_file=source_file,
                            extraction_confidence='high' if (he_dice or ap_0_10) else 'medium'
                        )

                        guns.append(gun)
                    else:
                        i += 1
            else:
                i += 1

        return guns

    def _insert_vehicles(self, vehicles: List[VehicleProfile]) -> int:
        """Insert vehicles into database, skip duplicates"""
        inserted = 0
        for vehicle in vehicles:
            try:
                self.conn.execute("""
                    INSERT INTO bg_reference_vehicles (
                        name, nation, year_range, vehicle_type,
                        off_road_inches, road_inches, special_movement,
                        armor_front, armor_side, armor_rear,
                        weapons, points_cost, battle_rating, special_rules,
                        source_file, source_page, extraction_confidence, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vehicle.name, vehicle.nation, vehicle.year_range, vehicle.vehicle_type,
                    vehicle.off_road_inches, vehicle.road_inches, vehicle.special_movement,
                    vehicle.armor_front, vehicle.armor_side, vehicle.armor_rear,
                    vehicle.weapons, vehicle.points_cost, vehicle.battle_rating,
                    vehicle.special_rules, vehicle.source_file, vehicle.source_page,
                    vehicle.extraction_confidence, vehicle.notes
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                # Duplicate, skip
                pass

        self.conn.commit()
        return inserted

    def _insert_guns(self, guns: List[GunProfile]) -> int:
        """Insert guns into database, skip duplicates"""
        inserted = 0
        for gun in guns:
            try:
                self.conn.execute("""
                    INSERT INTO bg_reference_guns (
                        name, nation, caliber_mm, barrel_length,
                        he_dice, he_target,
                        ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
                        points_cost, battle_rating,
                        source_file, source_page, extraction_confidence, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    gun.name, gun.nation, gun.caliber_mm, gun.barrel_length,
                    gun.he_dice, gun.he_target,
                    gun.ap_0_10, gun.ap_10_20, gun.ap_20_30, gun.ap_30_40,
                    gun.ap_40_50, gun.ap_50_70,
                    gun.points_cost, gun.battle_rating,
                    gun.source_file, gun.source_page,
                    gun.extraction_confidence, gun.notes
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                # Duplicate, skip
                pass

        self.conn.commit()
        return inserted

    def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}

        cursor = self.conn.execute("SELECT COUNT(*) as count FROM bg_reference_vehicles")
        stats['total_vehicles'] = cursor.fetchone()['count']

        cursor = self.conn.execute("SELECT COUNT(*) as count FROM bg_reference_guns")
        stats['total_guns'] = cursor.fetchone()['count']

        cursor = self.conn.execute("""
            SELECT nation, COUNT(*) as count
            FROM bg_reference_vehicles
            GROUP BY nation
        """)
        stats['vehicles_by_nation'] = {row['nation']: row['count'] for row in cursor.fetchall()}

        cursor = self.conn.execute("""
            SELECT nation, COUNT(*) as count
            FROM bg_reference_guns
            GROUP BY nation
        """)
        stats['guns_by_nation'] = {row['nation']: row['count'] for row in cursor.fetchall()}

        cursor = self.conn.execute("""
            SELECT file_path, vehicles_extracted, guns_extracted, extraction_date
            FROM extraction_log
            ORDER BY extraction_date DESC
        """)
        stats['extraction_history'] = [
            {
                'file': row['file_path'],
                'vehicles': row['vehicles_extracted'],
                'guns': row['guns_extracted'],
                'date': row['extraction_date']
            }
            for row in cursor.fetchall()
        ]

        return stats

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Scrape BattleGroup datacards")
    parser.add_argument('--file', type=str, help="Specific file to scrape")
    parser.add_argument('--nation', type=str, choices=['german', 'british', 'italian', 'american', 'french', 'soviet'],
                       help="Nation to assign (otherwise auto-detect)")
    parser.add_argument('--stats', action='store_true', help="Show database statistics")
    parser.add_argument('--all', action='store_true', help="Scrape all known datacard files")

    args = parser.parse_args()

    scraper = DatacardScraper()

    try:
        if args.stats:
            # Show statistics
            stats = scraper.get_stats()
            print("\n" + "="*60)
            print("BATTLEGROUP REFERENCE DATABASE STATISTICS")
            print("="*60)
            print(f"\n[VEHICLES] Total Vehicles: {stats['total_vehicles']}")
            for nation, count in stats['vehicles_by_nation'].items():
                print(f"   - {nation.title()}: {count}")

            print(f"\n[GUNS] Total Guns: {stats['total_guns']}")
            for nation, count in stats['guns_by_nation'].items():
                print(f"   - {nation.title()}: {count}")

            print(f"\n[LOG] Extraction History ({len(stats['extraction_history'])} files):")
            for entry in stats['extraction_history'][:10]:  # Show last 10
                print(f"   - {Path(entry['file']).name}: {entry['vehicles']}v, {entry['guns']}g ({entry['date']})")

            print("\n" + "="*60)

        elif args.file:
            # Scrape specific file
            file_path = Path(args.file)
            scraper.scrape_file(file_path, args.nation)

        elif args.all:
            # Scrape all known files
            files_to_scrape = [
                (RESOURCE_DIR / "Battlegroup-Kursk.txt", "german"),
                (RESOURCE_DIR / "Battlegroup-DataCards-British.txt", "british"),
                (RESOURCE_DIR / "Avanti Italian Forces.txt", "italian"),
            ]

            total_vehicles = 0
            total_guns = 0

            print("\n" + "="*60)
            print("SCRAPING ALL BATTLEGROUP DATACARD FILES")
            print("="*60)

            for file_path, nation in files_to_scrape:
                if file_path.exists():
                    v, g = scraper.scrape_file(file_path, nation)
                    total_vehicles += v
                    total_guns += g
                else:
                    print(f"\n[WARN] File not found: {file_path.name}")

            print("\n" + "="*60)
            print(f"[OK] COMPLETE: {total_vehicles} vehicles, {total_guns} guns extracted")
            print("="*60)
            print(f"\n[DB] Database: {DB_PATH}")
            print("\nRun with --stats to see detailed statistics")

        else:
            parser.print_help()

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
