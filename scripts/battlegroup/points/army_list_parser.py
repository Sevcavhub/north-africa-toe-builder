#!/usr/bin/env python3
"""
Phase 9B Step 3: Army List Parser
Extracts points and BR values from BattleGroup army list documents.

Multi-pass parsing strategy to handle:
- Unit entries with points/BR
- Defensive structures
- Off-board fire support
- Nested options and upgrades
- OCR artifacts and formatting variations
"""

import re
import sqlite3
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"


@dataclass
class UnitEntry:
    """Represents a unit/vehicle/gun with points and BR."""
    name: str
    points_cost: int
    battle_rating: int
    experience: str  # 'r', 'v', 'e', 'i'
    restrictions: Optional[str] = None  # 'Restricted', 'Unique', etc.
    unit_type: Optional[str] = None  # Inferred category
    composition: Optional[str] = None
    options: Optional[List[str]] = None
    extraction_confidence: str = "High"
    extraction_notes: Optional[str] = None


@dataclass
class DefenceEntry:
    """Represents a defensive structure."""
    name: str
    points_cost: int
    battle_rating: int
    defence_type: Optional[str] = None
    class_rating: Optional[str] = None  # 'Class 1', 'Class 2', etc.
    description: Optional[str] = None
    special_rules: Optional[str] = None
    extraction_confidence: str = "High"
    extraction_notes: Optional[str] = None


@dataclass
class FireSupportEntry:
    """Represents off-board fire support."""
    name: str
    points_cost: int
    battle_rating: int
    support_type: Optional[str] = None
    priority_level: Optional[str] = None  # '1st (3+)', '2nd (4+)', '3rd (5+)'
    fire_mission_type: Optional[str] = None
    battery_composition: Optional[str] = None
    special_rules: Optional[str] = None
    extraction_confidence: str = "High"
    extraction_notes: Optional[str] = None


class ArmyListParser:
    """
    Multi-pass parser for BattleGroup army list documents.

    Handles OCR artifacts, nested structures, and multiple formats.
    """

    # Regex patterns for matching unit entries
    PATTERNS = {
        # Main pattern: "Unit name . . . XXX pts XX-r/v/e/i BR"
        # Handles variations in spacing, dots, and formatting
        'unit_standard': re.compile(
            r'^([A-Z][A-Za-z\s\-/\'\"()0-9.]+?)\s*[.\s]+\s*'  # Unit name
            r'(\+)?(\d+)\s*pts?\s+'  # Points (optional + for upgrades)
            r'(\d+|D6|[A-Z])-([rvei])\s*BR'  # BR value and experience
            r'(?:\s*\((Restricted|Unique|[A-Za-z\s]+)\))?'  # Optional restrictions
        , re.IGNORECASE),

        # Fire support pattern: "Support name . . . XX pts 0 BR"
        'fire_support': re.compile(
            r'^([A-Z][A-Za-z\s\-/\'"()0-9.]+?)\s*[.\s]+\s*'
            r'(\d+)\s*pts?\s+'
            r'(0|OBR)\s*(?:BR)?'
            r'(?:\s*\((Restricted|Unique)\))?'
        , re.IGNORECASE),

        # Defence pattern: Similar to unit but may have "Class X" in name
        'defence': re.compile(
            r'^([A-Z][A-Za-z\s\-/\'"()0-9.]+?(?:Class\s+\d)?)\s*[.\s]+\s*'
            r'(\d+)\s*(?:pts?|points)\s+'
            r'(\d+|0)\s*(?:BR)?'
            r'(?:\s*\((Restricted|Unique)\))?'
        , re.IGNORECASE),

        # Upgrade/option pattern: "+XX pts +XX-r/v/e/i BR"
        'upgrade': re.compile(
            r'^\+(\d+)\s*pts?\s+'
            r'\+(\d+|D6)-([rvei])\s*BR'
        , re.IGNORECASE),

        # Target priority pattern: "1st/2nd/3rd Target priority (3+/4+/5+)"
        'target_priority': re.compile(
            r'^(1st|2nd|3rd)\s*Target\s*priority\s*\(([345])\+\)\s*[.\s]+\s*'
            r'(\d+)\s*pts?\s+(0|OBR)'
        , re.IGNORECASE),

        # Timed barrage pattern: "Timed XX Barrage"
        'timed_barrage': re.compile(
            r'^Timed\s+([A-Za-z0-9."\s]+)\s+(?:Barrage|Airstrike)\s*[.\s]+\s*'
            r'(\d+)\s*pts?\s+(0|OBR)'
        , re.IGNORECASE),
    }

    # Keywords to identify categories
    DEFENCE_KEYWORDS = [
        'pillbox', 'bunker', 'fortification', 'trench', 'foxhole',
        'barbed wire', 'minefield', 'road block', 'obstacle',
        'hard cover', 'hideout', 'class 1', 'class 2', 'class 3'
    ]

    FIRE_SUPPORT_KEYWORDS = [
        'target priority', 'fire mission', 'barrage', 'airstrike',
        'counter-battery', 'off-table', 'artillery support', 'mortar fire',
        'spitfire', 'typhoon', 'stuka'
    ]

    def __init__(self, source_document: str, source_battle: str, source_date: str):
        """
        Initialize parser for a specific document.

        Args:
            source_document: Document filename
            source_battle: Battle context (e.g., 'Kursk', 'Normandy')
            source_date: Battle date (e.g., '1943-07', '1944-06')
        """
        self.source_document = source_document
        self.source_battle = source_battle
        self.source_date = source_date

        self.units: List[UnitEntry] = []
        self.defences: List[DefenceEntry] = []
        self.fire_support: List[FireSupportEntry] = []

        self.current_section = None
        self.line_number = 0

    def parse_file(self, file_path: Path) -> Dict:
        """
        Parse army list file with multi-pass strategy.

        Returns:
            Dictionary with extraction stats and results
        """
        print(f"\nParsing: {file_path.name}")
        print(f"Battle: {self.source_battle}, Date: {self.source_date}")
        print("=" * 60)

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Pass 1: Section detection
        self._detect_sections(lines)

        # Pass 2: Extract all entries
        self._extract_entries(lines)

        # Pass 3: Classify ambiguous entries
        self._classify_entries()

        # Pass 4: Quality checks
        stats = self._quality_check()

        print("\nExtraction Summary:")
        print(f"  Units: {stats['units']}")
        print(f"  Defences: {stats['defences']}")
        print(f"  Fire Support: {stats['fire_support']}")
        print(f"  Total: {stats['total']}")
        print(f"  High Confidence: {stats['high_confidence']}")
        print(f"  Medium Confidence: {stats['medium_confidence']}")
        print(f"  Low Confidence: {stats['low_confidence']}")

        return stats

    def _detect_sections(self, lines: List[str]):
        """Pass 1: Detect major sections in document."""
        # For now, simple implementation
        # Could be extended to detect INFANTRY UNITS, TANK UNITS, etc.
        pass

    def _extract_entries(self, lines: List[str]):
        """Pass 2: Extract all unit/defence/fire support entries."""
        for i, line in enumerate(lines):
            self.line_number = i + 1
            line = line.strip()

            if not line or len(line) < 10:
                continue

            # Try each pattern
            self._try_parse_unit_standard(line)
            self._try_parse_fire_support(line)
            self._try_parse_target_priority(line)
            self._try_parse_timed_barrage(line)
            self._try_parse_defence(line)

    def _try_parse_unit_standard(self, line: str):
        """Try to parse as standard unit entry."""
        match = self.PATTERNS['unit_standard'].search(line)
        if not match:
            return

        name = match.group(1).strip()
        is_upgrade = match.group(2) == '+'
        points = int(match.group(3))
        br_value = match.group(4)
        experience = match.group(5)
        restrictions = match.group(6)

        # Convert BR value
        if br_value == 'D6':
            br_int = 0  # Special case
            notes = "BR is D6 (variable)"
        elif br_value.isalpha():
            br_int = 0
            notes = f"BR is letter: {br_value}"
        else:
            br_int = int(br_value)
            notes = None

        # Check if this is a defence
        if self._is_defence(name):
            defence = DefenceEntry(
                name=name,
                points_cost=points,
                battle_rating=br_int,
                special_rules=restrictions,
                extraction_notes=notes
            )
            self.defences.append(defence)
        else:
            unit = UnitEntry(
                name=name,
                points_cost=points,
                battle_rating=br_int,
                experience=experience,
                restrictions=restrictions,
                extraction_notes=notes
            )
            self.units.append(unit)

    def _try_parse_fire_support(self, line: str):
        """Try to parse as fire support entry."""
        match = self.PATTERNS['fire_support'].search(line)
        if not match:
            return

        name = match.group(1).strip()

        # Only process if it looks like fire support
        if not self._is_fire_support(name):
            return

        points = int(match.group(2))
        restrictions = match.group(4)

        entry = FireSupportEntry(
            name=name,
            points_cost=points,
            battle_rating=0,  # Fire support typically 0 BR
            special_rules=restrictions
        )
        self.fire_support.append(entry)

    def _try_parse_target_priority(self, line: str):
        """Try to parse as target priority entry."""
        match = self.PATTERNS['target_priority'].search(line)
        if not match:
            return

        priority = match.group(1)  # '1st', '2nd', '3rd'
        roll = match.group(2)  # '3', '4', '5'
        points = int(match.group(3))

        name = f"{priority} Target priority ({roll}+)"

        entry = FireSupportEntry(
            name=name,
            points_cost=points,
            battle_rating=0,
            support_type='off-table-artillery',
            priority_level=name
        )
        self.fire_support.append(entry)

    def _try_parse_timed_barrage(self, line: str):
        """Try to parse as timed barrage/airstrike entry."""
        match = self.PATTERNS['timed_barrage'].search(line)
        if not match:
            return

        weapon = match.group(1).strip()
        points = int(match.group(2))

        # Determine if barrage or airstrike
        if 'airstrike' in line.lower():
            support_type = 'air-strike'
            name = f"Timed {weapon} Airstrike"
        else:
            support_type = 'timed-barrage'
            name = f"Timed {weapon} Barrage"

        entry = FireSupportEntry(
            name=name,
            points_cost=points,
            battle_rating=0,
            support_type=support_type,
            battery_composition=weapon
        )
        self.fire_support.append(entry)

    def _try_parse_defence(self, line: str):
        """Try to parse as defence entry."""
        match = self.PATTERNS['defence'].search(line)
        if not match:
            return

        name = match.group(1).strip()

        # Only process if it looks like a defence
        if not self._is_defence(name):
            return

        points = int(match.group(2))
        br_value = match.group(3)
        restrictions = match.group(4)

        br_int = 0 if br_value == '0' else int(br_value)

        # Extract class rating if present
        class_match = re.search(r'Class\s+(\d)', name, re.IGNORECASE)
        class_rating = class_match.group(0) if class_match else None

        entry = DefenceEntry(
            name=name,
            points_cost=points,
            battle_rating=br_int,
            class_rating=class_rating,
            special_rules=restrictions
        )
        self.defences.append(entry)

    def _is_defence(self, name: str) -> bool:
        """Check if name indicates a defensive structure."""
        name_lower = name.lower()
        return any(keyword in name_lower for keyword in self.DEFENCE_KEYWORDS)

    def _is_fire_support(self, name: str) -> bool:
        """Check if name indicates fire support."""
        name_lower = name.lower()
        return any(keyword in name_lower for keyword in self.FIRE_SUPPORT_KEYWORDS)

    def _classify_entries(self):
        """Pass 3: Classify ambiguous entries."""
        # For now, classification is done during extraction
        # Could be extended for more sophisticated classification
        pass

    def _quality_check(self) -> Dict:
        """Pass 4: Quality checks and statistics."""
        total = len(self.units) + len(self.defences) + len(self.fire_support)

        high_conf = sum(
            1 for u in self.units if u.extraction_confidence == "High"
        ) + sum(
            1 for d in self.defences if d.extraction_confidence == "High"
        ) + sum(
            1 for f in self.fire_support if f.extraction_confidence == "High"
        )

        return {
            'units': len(self.units),
            'defences': len(self.defences),
            'fire_support': len(self.fire_support),
            'total': total,
            'high_confidence': high_conf,
            'medium_confidence': 0,
            'low_confidence': total - high_conf
        }

    def save_to_database(self, conn: sqlite3.Connection):
        """Save extracted entries to database."""
        cursor = conn.cursor()

        # Save units (to bg_reference_vehicles for now)
        for unit in self.units:
            try:
                cursor.execute("""
                    INSERT INTO bg_reference_vehicles (
                        name, nation, points_cost, battle_rating,
                        source_battle, source_date, source_document,
                        unit_experience, special_rules, extraction_notes,
                        extraction_confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    unit.name,
                    'Unknown',  # Will be determined from document
                    unit.points_cost,
                    unit.battle_rating,
                    self.source_battle,
                    self.source_date,
                    self.source_document,
                    unit.experience,
                    unit.restrictions,
                    unit.extraction_notes,
                    unit.extraction_confidence
                ))
            except sqlite3.IntegrityError:
                # Duplicate - this is expected, we keep all entries
                pass

        # Save defences
        for defence in self.defences:
            try:
                cursor.execute("""
                    INSERT INTO bg_reference_defences (
                        name, defence_type, class_rating, points_cost,
                        battle_rating, special_rules, source_battle,
                        source_date, source_document, extraction_confidence,
                        notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    defence.name,
                    defence.defence_type,
                    defence.class_rating,
                    defence.points_cost,
                    defence.battle_rating,
                    defence.special_rules,
                    self.source_battle,
                    self.source_date,
                    self.source_document,
                    defence.extraction_confidence,
                    defence.extraction_notes
                ))
            except sqlite3.IntegrityError:
                pass

        # Save fire support
        for fire_sup in self.fire_support:
            try:
                cursor.execute("""
                    INSERT INTO bg_reference_fire_support (
                        name, support_type, priority_level, battery_composition,
                        points_cost, battle_rating, special_rules,
                        source_battle, source_date, source_document,
                        extraction_confidence, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    fire_sup.name,
                    fire_sup.support_type,
                    fire_sup.priority_level,
                    fire_sup.battery_composition,
                    fire_sup.points_cost,
                    fire_sup.battle_rating,
                    fire_sup.special_rules,
                    self.source_battle,
                    self.source_date,
                    self.source_document,
                    fire_sup.extraction_confidence,
                    fire_sup.extraction_notes
                ))
            except sqlite3.IntegrityError:
                pass

        # Update extraction log
        cursor.execute("""
            INSERT OR REPLACE INTO bg_extraction_log (
                document_name, source_battle, source_date,
                total_entries, vehicles_extracted, defences_extracted,
                fire_support_extracted, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.source_document,
            self.source_battle,
            self.source_date,
            len(self.units) + len(self.defences) + len(self.fire_support),
            len(self.units),
            len(self.defences),
            len(self.fire_support),
            'Complete',
            f'Extracted {len(self.units)} units, {len(self.defences)} defences, {len(self.fire_support)} fire support'
        ))

        conn.commit()
        print(f"\n[OK] Saved to database")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 9B Step 3: Army List Parser"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to army list text file"
    )
    parser.add_argument(
        "--battle",
        type=str,
        help="Battle context (e.g., 'Kursk', 'Normandy')"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Battle date (e.g., '1943-07')"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Parse all 7 documents"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode - don't save to database"
    )

    args = parser.parse_args()

    if args.all:
        # Parse all 7 documents
        documents = [
            ("Battlegroup-Kursk.txt", "Kursk", "1943-07"),
            ("Battlegroup-Canadas-Crucible.txt", "Normandy", "1944-06"),
            ("Battlegroup-Market-Garden-Army-List.txt", "Market Garden", "1944-09"),
            ("Battlegroup-Wacht-Am-Rhein.txt", "Ardennes", "1944-12"),
            ("Battlegroup-Westwall.txt", "Westwall", "1944"),
            ("Battlegroup-Dispatches-1.txt", "Various", "Various"),
            ("Battlegroup-Dispatches-2.txt", "Various", "Various"),
        ]

        conn = sqlite3.connect(DATABASE_PATH) if not args.test else None

        for doc_name, battle, date in documents:
            file_path = project_root / "Resource Documents" / "Battlegroup Game" / doc_name

            if not file_path.exists():
                print(f"[SKIP] File not found: {doc_name}")
                continue

            parser_obj = ArmyListParser(doc_name, battle, date)
            stats = parser_obj.parse_file(file_path)

            if not args.test and conn:
                parser_obj.save_to_database(conn)

            print()

        if conn:
            conn.close()

    elif args.file and args.battle and args.date:
        # Parse single file
        file_path = Path(args.file)

        if not file_path.exists():
            print(f"[ERROR] File not found: {args.file}")
            sys.exit(1)

        parser_obj = ArmyListParser(file_path.name, args.battle, args.date)
        stats = parser_obj.parse_file(file_path)

        if not args.test:
            conn = sqlite3.connect(DATABASE_PATH)
            parser_obj.save_to_database(conn)
            conn.close()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
