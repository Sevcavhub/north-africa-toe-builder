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
DB_PATH = PROJECT_ROOT / "database" / "battlegroup_reference.db"


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
        print(f"✅ Database initialized: {self.db_path}")

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

        print(f"\n📄 Processing: {file_path.name}")
        print(f"   Nation: {nation}")

        content = file_path.read_text(encoding='utf-8', errors='ignore')

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

        print(f"   ✅ Extracted: {vehicles_inserted} vehicles, {guns_inserted} guns")

        return vehicles_inserted, guns_inserted

    def _extract_vehicles(self, content: str, nation: str, source_file: str) -> List[VehicleProfile]:
        """Extract vehicle profiles from content"""
        vehicles = []

        # TODO: Implement vehicle extraction patterns
        # This will need sophisticated regex patterns to match:
        # - Vehicle names with year ranges (e.g., "M4 SHERMAN (A1, A2, A3) 1942-45")
        # - Movement section (Off-Road: 9", Road: 14")
        # - Armor section (Front: K, Side: L, Rear: N)
        # - Weapons section (75mm L40, MG co-axial, etc.)
        # - Special rules

        # For now, return empty list (will implement in next iteration)
        return vehicles

    def _extract_guns(self, content: str, nation: str, source_file: str) -> List[GunProfile]:
        """Extract gun profiles from content"""
        guns = []

        # TODO: Implement gun extraction patterns
        # This will need regex patterns to match:
        # - Gun designation (e.g., "50mm L60 (PaK38)")
        # - HE effect (e.g., "HE: 3/6+")
        # - AP penetration by range (e.g., "AP: - | 5, 5, 4, 3, 2, -")
        # - Range bands (0-10", 10-20", etc.)

        # For now, return empty list (will implement in next iteration)
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
    parser.add_argument('--nation', type=str, choices=['german', 'british', 'italian', 'american'],
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
            print(f"\n📊 Total Vehicles: {stats['total_vehicles']}")
            for nation, count in stats['vehicles_by_nation'].items():
                print(f"   - {nation.title()}: {count}")

            print(f"\n🔫 Total Guns: {stats['total_guns']}")
            for nation, count in stats['guns_by_nation'].items():
                print(f"   - {nation.title()}: {count}")

            print(f"\n📝 Extraction History ({len(stats['extraction_history'])} files):")
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
                    print(f"\n⚠️  File not found: {file_path.name}")

            print("\n" + "="*60)
            print(f"✅ COMPLETE: {total_vehicles} vehicles, {total_guns} guns extracted")
            print("="*60)
            print(f"\n💾 Database: {DB_PATH}")
            print("\nRun with --stats to see detailed statistics")

        else:
            parser.print_help()

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
