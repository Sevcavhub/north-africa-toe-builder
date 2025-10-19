#!/usr/bin/env python3
"""
Automated Equipment Matcher v2.1 (Autonomous)
- Same matching logic as v2.1
- Automated decision-making
- No interactive input required
- Comprehensive logging

Automated Decision Rules:
- Gun matches ≥80%: Auto-accept first match
- AFV matches ≥85%: Auto-accept
- Soft-skin vehicles: Auto-approve
- Summary categories: Auto-filter
- Low confidence (<80%): Flag for manual review

Usage:
    python tools/equipment_matcher_auto.py --nation american
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
import re
import argparse

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"
WITW_FILE = PROJECT_ROOT / "data" / "iterations" / "iteration_2" / "Timeline_TOE_Reconstruction" / "OUTPUT" / "v5_development" / "canonical_equipment_master_with_witw_ALL_NATIONS.json"
ONWAR_FILE = PROJECT_ROOT / "data" / "output" / "afv_data" / "afv_complete_with_specs.json"
WWIITANKS_FILE = PROJECT_ROOT / "data" / "output" / "afv_data" / "wwiitanks" / "all_afvs.json"

class EquipmentType:
    """Equipment type categories"""
    GUN = "gun"
    AFV = "afv"
    SOFT_SKIN = "soft_skin"
    AIRCRAFT = "aircraft"
    UNKNOWN = "unknown"

class AutomatedEquipmentMatcher:
    """Automated equipment matching with no user interaction"""

    def __init__(self, nation='british'):
        self.nation = nation.lower()
        self.conn = None
        self.witw_data = []
        self.onwar_data = []
        self.wwiitanks_data = []
        self.guns_data = []
        self.aircraft_data = []

        # Statistics
        self.total_items = 0
        self.reviewed_count = 0
        self.approved_count = 0
        self.rejected_count = 0
        self.skipped_count = 0
        self.researched_count = 0
        self.auto_accepted_count = 0
        self.manual_review_count = 0
        self.filtered_count = 0

        # Decision log
        self.decisions = []

    def log_decision(self, item, decision, reason, confidence=None):
        """Log automated decision"""
        self.decisions.append({
            'item': item.get('canonical_name'),
            'canonical_id': item.get('canonical_id'),
            'decision': decision,
            'reason': reason,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })

    def connect_db(self):
        """Connect to database"""
        if not DATABASE_FILE.exists():
            print(f"[ERROR] Database not found: {DATABASE_FILE}")
            sys.exit(1)

        self.conn = sqlite3.connect(DATABASE_FILE)
        self.conn.row_factory = sqlite3.Row
        print(f"[OK] Connected to database: {DATABASE_FILE}")

    def detect_equipment_type(self, witw_item):
        """Detect equipment type from WITW data"""
        eq_type = witw_item.get('type', '').lower()
        category = witw_item.get('category', '').lower()

        gun_types = [
            'field_artillery', 'anti_tank', 'anti_aircraft',
            'anti_tank_guns', 'anti_aircraft_guns', 'artillery',
            'towed_artillery'
        ]

        afv_types = [
            'tank', 'tanks', 'armored_car', 'armored_cars',
            'halftrack', 'halftracks', 'main_tanks', 'light_tanks',
            'medium_tanks', 'heavy_tanks', 'tank_destroyer',
            'tank_destroyers', 'armored_vehicle', 'armored_vehicles',
            'armored_cars_reconnaissance'
        ]

        soft_skin_types = [
            'truck', 'trucks', 'motorcycle', 'motorcycles',
            'support_vehicle', 'support_vehicles',
            'recovery_vehicle', 'recovery_vehicles',
            'workshop_vehicle', 'workshop_vehicles',
            'artillery_tractor', 'artillery_tractors',
            'carrier', 'carriers', 'command_vehicle', 'command_vehicles'
        ]

        aircraft_types = [
            'fighter', 'fighters', 'bomber', 'bombers',
            'dive_bomber', 'dive_bombers', 'lightning'
        ]

        # CRITICAL: Check soft-skin BEFORE guns to avoid false matches
        # "artillery_tractor" contains "artillery" which would match gun_types
        for soft_type in soft_skin_types:
            if soft_type in eq_type or soft_type in category:
                return EquipmentType.SOFT_SKIN

        # Check aircraft - use exact match for 'aircraft' to avoid matching 'anti_aircraft'
        if eq_type == 'aircraft':
            return EquipmentType.AIRCRAFT

        # Check for aircraft-specific patterns
        for air_type in aircraft_types:
            if air_type in eq_type or air_type in category:
                return EquipmentType.AIRCRAFT

        for gun_type in gun_types:
            if gun_type in eq_type or gun_type in category:
                return EquipmentType.GUN

        for afv_type in afv_types:
            if afv_type in eq_type or afv_type in category:
                return EquipmentType.AFV

        return EquipmentType.UNKNOWN

    def is_summary_category(self, item):
        """Check if item is a summary/aggregate category"""
        name = item.get('canonical_name', '').lower()
        summary_patterns = [
            'total ', 'all ', 'summary ', 'aggregate ',
            'grand total', 'overall total', 'combined total'
        ]
        return any(pattern in name for pattern in summary_patterns)

    def normalize_name(self, name):
        """Normalize equipment name for matching"""
        if not name:
            return ""

        name = name.lower()

        # Special handling for model numbers: convert "h-39" or "h 39" to "h39"
        name = re.sub(r'([a-z])[\s\-](\d+)', r'\1\2', name)

        # Remove all remaining punctuation
        name = re.sub(r'[.,/\-]', ' ', name)

        # Collapse multiple spaces
        name = ' '.join(name.split())
        return name

    def load_data_sources(self):
        """Load all data sources"""
        print("\n[...] Loading data sources...")

        # Load WITW baseline (filter by target nation)
        if not WITW_FILE.exists():
            print(f"[ERROR] WITW file not found: {WITW_FILE}")
            sys.exit(1)

        with open(WITW_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_equipment = data.get('equipment', {})

            filtered_count = 0
            for canonical_id, item in all_equipment.items():
                item_nation = item.get('nation', '').lower()
                if 'british' in item_nation or 'commonwealth' in item_nation:
                    item_nation = 'british'
                elif 'american' in item_nation or 'usa' in item_nation or 'us' in item_nation:
                    item_nation = 'american'

                if item_nation == self.nation:
                    item['canonical_id'] = canonical_id
                    self.witw_data.append(item)
                    filtered_count += 1

            self.total_items = len(self.witw_data)
            print(f"[OK] Loaded {self.total_items} {self.nation.title()} items from WITW")

        # Load database guns from ALL nations (for captured/lend-lease)
        print(f"[...] Loading guns from ALL nations (for captured/allied equipment)...")
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM guns")
        self.guns_data = [dict(row) for row in cursor.fetchall()]
        print(f"[OK] Loaded {len(self.guns_data)} guns from database (all nations)")

        # Load aircraft from ALL nations
        print(f"[...] Loading aircraft from ALL nations...")
        cursor.execute("SELECT * FROM aircraft")
        self.aircraft_data = [dict(row) for row in cursor.fetchall()]
        print(f"[OK] Loaded {len(self.aircraft_data)} aircraft from database (all nations)")

        # Load OnWar AFVs from ALL nations
        print(f"[...] Loading AFVs from ALL nations (for captured/allied equipment)...")
        if ONWAR_FILE.exists():
            with open(ONWAR_FILE, 'r', encoding='utf-8') as f:
                all_onwar = json.load(f)
                self.onwar_data = all_onwar
                print(f"[OK] Loaded {len(self.onwar_data)} AFVs from OnWar (all nations)")

        # Load WWIITANKS from ALL nations
        if WWIITANKS_FILE.exists():
            with open(WWIITANKS_FILE, 'r', encoding='utf-8') as f:
                all_wwiitanks = json.load(f)
                self.wwiitanks_data = all_wwiitanks
                print(f"[OK] Loaded {len(self.wwiitanks_data)} AFVs from WWII Tanks UK (all nations)")

        print(f"\n[INFO] Cross-nation matching enabled - can match captured/allied equipment")

    def extract_caliber(self, name):
        """Extract caliber from name (handles mm and British pdr)"""
        import re

        # British pounder conversions (approximate)
        pdr_to_mm = {
            '2': 40,   # 2-pounder = 40mm
            '6': 57,   # 6-pounder = 57mm
            '17': 76,  # 17-pounder = 76mm
            '25': 87,  # 25-pounder = 87mm (actually 88mm)
            '18': 84,  # 18-pounder = 84mm
            '13': 76,  # 13-pounder = 76mm
            '32': 94   # 32-pounder = 94mm
        }

        # Check for pdr/pounder pattern
        pdr_match = re.search(r'(\d+)\s*[-\s]*(pdr|pounder)', name.lower())
        if pdr_match:
            pdr_num = pdr_match.group(1)
            if pdr_num in pdr_to_mm:
                return pdr_to_mm[pdr_num]

        # Check for mm pattern
        mm_match = re.search(r'(\d+)\s*mm', name.lower())
        if mm_match:
            return int(mm_match.group(1))

        # Check for inch pattern (convert to mm)
        inch_match = re.search(r'(\d+\.?\d*)\s*[-\s]*inch', name.lower())
        if inch_match:
            inches = float(inch_match.group(1))
            return int(inches * 25.4)

        return None

    def find_gun_matches(self, witw_item):
        """Find matching guns in database with caliber-based matching"""
        matches = []
        witw_name = witw_item.get('canonical_name', '')
        witw_name_norm = self.normalize_name(witw_name)
        witw_caliber = self.extract_caliber(witw_name)

        for gun in self.guns_data:
            gun_name = gun.get('name', '')
            gun_name_norm = self.normalize_name(gun_name)
            gun_caliber = gun.get('caliber_mm')

            score = 0
            reasons = []

            # Exact match (normalized)
            if witw_name_norm == gun_name_norm:
                score = 100
                reasons.append("Exact match (normalized)")
            # Substring match
            elif witw_name_norm in gun_name_norm or gun_name_norm in witw_name_norm:
                score = 85
                reasons.append("Substring match")
            # Word match
            else:
                witw_words = set(witw_name_norm.split())
                gun_words = set(gun_name_norm.split())
                common_words = witw_words & gun_words
                if len(common_words) >= 2:
                    score = 70 + (len(common_words) * 5)
                    reasons.append(f"Word match: {', '.join(common_words)}")

            # CRITICAL: Caliber-based matching for British guns
            if witw_caliber and gun_caliber:
                # Allow 2mm tolerance for caliber matching
                if abs(witw_caliber - gun_caliber) <= 2:
                    if score == 0:
                        score = 85  # Caliber match alone = 85%
                        reasons.append(f"Caliber match: {witw_caliber}mm ≈ {gun_caliber}mm")
                    else:
                        score += 15  # Bonus for caliber match
                        reasons.append(f"Caliber bonus: {witw_caliber}mm ≈ {gun_caliber}mm")

            if score >= 65:
                matches.append({
                    'gun': gun,
                    'score': min(100, score),  # Cap at 100
                    'reasons': reasons
                })

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:3]  # Top 3 matches

    def find_afv_matches(self, witw_item):
        """Find matching AFVs"""
        matches = {
            'onwar': [],
            'wwiitanks': []
        }

        witw_name = witw_item.get('canonical_name', '')
        witw_name_norm = self.normalize_name(witw_name)

        # Search OnWar
        for afv in self.onwar_data:
            afv_name = afv.get('name', '')
            afv_name_norm = self.normalize_name(afv_name)

            score = 0
            if witw_name_norm == afv_name_norm:
                score = 100
            elif witw_name_norm in afv_name_norm or afv_name_norm in witw_name_norm:
                score = 85
            else:
                witw_words = set(witw_name_norm.split())
                afv_words = set(afv_name_norm.split())
                common_words = witw_words & afv_words
                if len(common_words) >= 2:
                    score = 70 + (len(common_words) * 5)

            if score >= 70:
                matches['onwar'].append({'afv': afv, 'score': score})

        # Search WWIITANKS
        for afv in self.wwiitanks_data:
            afv_name = afv.get('name', '')
            afv_name_norm = self.normalize_name(afv_name)

            score = 0
            if witw_name_norm == afv_name_norm:
                score = 100
            elif witw_name_norm in afv_name_norm or afv_name_norm in witw_name_norm:
                score = 85
            else:
                witw_words = set(witw_name_norm.split())
                afv_words = set(afv_name_norm.split())
                common_words = witw_words & afv_words
                if len(common_words) >= 2:
                    score = 70 + (len(common_words) * 5)

            if score >= 70:
                matches['wwiitanks'].append({'afv': afv, 'score': score})

        # Sort by score
        matches['onwar'].sort(key=lambda x: x['score'], reverse=True)
        matches['wwiitanks'].sort(key=lambda x: x['score'], reverse=True)

        return matches

    def normalize_aircraft_name(self, name):
        """Normalize aircraft name - strip nation codes and convert Mk variants"""
        import re

        # Remove nation codes like (FI), (RU), (SU), (Nation_XX)
        name = re.sub(r'\s*\([A-Z]{2}\)', '', name)
        name = re.sub(r'\s*\(Nation_\d+\)', '', name)
        name = re.sub(r'\s*\(SU\)', '', name)

        # Convert Roman numerals to Mk format or vice versa
        # Mk1 → Mk I, Mk4 → Mk IV, etc.
        roman_map = {
            '1': 'i', '2': 'ii', '3': 'iii', '4': 'iv', '5': 'v',
            '6': 'vi', '7': 'vii', '8': 'viii', '9': 'ix', '10': 'x'
        }

        # Try both directions for matching
        for arabic, roman in roman_map.items():
            # Mk1 → Mk I
            name = re.sub(rf'\bmk\s*{arabic}\b', f'mk {roman}', name.lower())
            # Mk I → Mk 1 (also try)
            name = re.sub(rf'\bmk\s*{roman}\b', f'mk {arabic}', name.lower())

        return self.normalize_name(name)

    def find_aircraft_matches(self, witw_item):
        """Find matching aircraft in database with improved variant handling"""
        matches = []
        witw_name = witw_item.get('canonical_name', '')
        witw_name_norm = self.normalize_aircraft_name(witw_name)
        witw_name_simple = self.normalize_name(witw_name)

        for aircraft in self.aircraft_data:
            aircraft_name = aircraft.get('name', '')

            # Skip blank/empty names
            if not aircraft_name or aircraft_name.strip() == '':
                continue

            aircraft_name_norm = self.normalize_aircraft_name(aircraft_name)
            aircraft_name_simple = self.normalize_name(aircraft_name)

            score = 0
            reasons = []

            # Exact match (normalized)
            if witw_name_norm == aircraft_name_norm:
                score = 100
                reasons.append("Exact match (normalized)")
            # Try simple match too
            elif witw_name_simple == aircraft_name_simple:
                score = 95
                reasons.append("Exact match (simple)")
            # Substring match
            elif witw_name_norm in aircraft_name_norm or aircraft_name_norm in witw_name_norm:
                score = 85
                reasons.append("Substring match")
            # Word match (try both normalized versions)
            else:
                witw_words = set(witw_name_norm.split())
                aircraft_words = set(aircraft_name_norm.split())
                common_words = witw_words & aircraft_words

                if len(common_words) >= 2:
                    score = 70 + (len(common_words) * 5)
                    reasons.append(f"Word match: {', '.join(common_words)}")
                elif len(common_words) == 1:
                    # Check if it's the base aircraft name (e.g. "hurricane", "spitfire")
                    base_name = witw_name_simple.split()[0] if witw_name_simple else ""
                    if base_name and base_name in aircraft_name_simple:
                        score = 75
                        reasons.append(f"Base aircraft match: {base_name}")

            if score >= 70:
                matches.append({
                    'aircraft': aircraft,
                    'score': score,
                    'reasons': reasons
                })

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:3]  # Top 3 matches

    def automated_decision(self, witw_item, eq_type, matches):
        """Make automated decision based on rules"""
        canonical_id = witw_item.get('canonical_id')
        canonical_name = witw_item.get('canonical_name')

        # Rule 1: Summary categories - Auto-filter
        if self.is_summary_category(witw_item):
            self.save_decision(canonical_id, 'skipped', 'Summary category - auto-filtered')
            self.log_decision(witw_item, 'FILTERED', 'Summary category')
            self.skipped_count += 1
            self.filtered_count += 1
            print(f"[AUTO-FILTER] {canonical_name} - Summary category")
            return True

        # Rule 2: Soft-skin vehicles - Auto-approve
        if eq_type == EquipmentType.SOFT_SKIN:
            self.save_decision(canonical_id, 'approved', 'Soft-skin vehicle - auto-approved')
            self.log_decision(witw_item, 'AUTO-APPROVED', 'Soft-skin vehicle', confidence=90)
            self.approved_count += 1
            self.auto_accepted_count += 1
            print(f"[AUTO-APPROVE] {canonical_name} - Soft-skin vehicle")
            return True

        # Rule 3: Aircraft - Match to WITW aircraft database
        if eq_type == EquipmentType.AIRCRAFT:
            if matches and matches[0]['score'] >= 80:
                aircraft = matches[0]['aircraft']
                score = matches[0]['score']
                witw_id = aircraft.get('witw_id')

                self.save_decision(canonical_id, 'approved',
                    f"Aircraft match: {aircraft.get('name')} (WITW ID: {witw_id}, score: {score}%)")
                self.log_decision(witw_item, 'AUTO-MATCHED',
                    f"Aircraft match: {aircraft.get('name')} (WITW ID: {witw_id})", confidence=score)
                self.approved_count += 1
                self.auto_accepted_count += 1
                print(f"[AUTO-MATCH] {canonical_name} -> {aircraft.get('name')} (WITW ID: {witw_id}, {score}%)")
                return True
            else:
                # No match or low confidence - skip for now
                self.save_decision(canonical_id, 'skipped', 'Aircraft - no match found in WITW aircraft database')
                self.log_decision(witw_item, 'SKIPPED', 'Aircraft - no match')
                self.skipped_count += 1
                print(f"[SKIP] {canonical_name} - Aircraft (no match in database)")
                return True

        # Rule 4: Gun matches ≥80% - Auto-accept first match
        if eq_type == EquipmentType.GUN and matches:
            gun_matches = matches
            if gun_matches and gun_matches[0]['score'] >= 80:
                gun = gun_matches[0]['gun']
                score = gun_matches[0]['score']
                gun_id = gun.get('gun_id')

                self.save_gun_match(canonical_id, gun_id, score)
                self.log_decision(witw_item, 'AUTO-MATCHED',
                    f"Gun match: {gun.get('name')} (score: {score}%)", confidence=score)
                self.approved_count += 1
                self.auto_accepted_count += 1
                print(f"[AUTO-MATCH] {canonical_name} -> {gun.get('name')} ({score}%)")
                return True

        # Rule 5: AFV matches ≥85% - Auto-accept
        if eq_type == EquipmentType.AFV and matches:
            best_match = None
            best_score = 0
            source = None

            if matches.get('onwar') and matches['onwar'][0]['score'] >= 85:
                best_match = matches['onwar'][0]
                best_score = best_match['score']
                source = 'onwar'
            elif matches.get('wwiitanks') and matches['wwiitanks'][0]['score'] >= 85:
                best_match = matches['wwiitanks'][0]
                best_score = best_match['score']
                source = 'wwiitanks'

            if best_match:
                afv = best_match['afv']
                self.save_decision(canonical_id, 'approved',
                    f"AFV match: {afv.get('name')} from {source} (score: {best_score}%)")
                self.log_decision(witw_item, 'AUTO-MATCHED',
                    f"AFV match: {afv.get('name')} ({best_score}%)", confidence=best_score)
                self.approved_count += 1
                self.auto_accepted_count += 1
                print(f"[AUTO-MATCH] {canonical_name} -> {afv.get('name')} ({best_score}%)")
                return True

        # Rule 6: Low confidence or no matches - Flag for manual review
        best_score = 0
        if eq_type == EquipmentType.GUN and matches:
            best_score = matches[0]['score'] if matches else 0
        elif eq_type == EquipmentType.AFV and matches:
            onwar_score = matches['onwar'][0]['score'] if matches.get('onwar') else 0
            wwiitanks_score = matches['wwiitanks'][0]['score'] if matches.get('wwiitanks') else 0
            best_score = max(onwar_score, wwiitanks_score)

        if best_score > 0 and best_score < 80:
            self.save_decision(canonical_id, 'rejected',
                f"Low confidence match ({best_score}%) - flagged for manual review")
            self.log_decision(witw_item, 'MANUAL_REVIEW',
                f"Low confidence ({best_score}%)", confidence=best_score)
            self.rejected_count += 1
            self.manual_review_count += 1
            print(f"[MANUAL_REVIEW] {canonical_name} - Low confidence ({best_score}%)")
            return True

        # Rule 7: No matches - Flag for research
        self.save_decision(canonical_id, 'rejected', 'No matches found - needs research')
        self.log_decision(witw_item, 'NEEDS_RESEARCH', 'No matches found')
        self.rejected_count += 1
        self.manual_review_count += 1
        print(f"[NEEDS_RESEARCH] {canonical_name} - No matches found")
        return True

    def save_decision(self, canonical_id, status, notes):
        """Save decision to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO match_reviews (canonical_id, review_status, reviewer_notes, reviewed_at)
            VALUES (?, ?, ?, ?)
        """, (canonical_id, status, notes, datetime.now().isoformat()))
        self.conn.commit()

    def save_gun_match(self, canonical_id, gun_id, confidence):
        """Save gun match to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO match_reviews (canonical_id, review_status, reviewer_notes, reviewed_at)
            VALUES (?, ?, ?, ?)
        """, (canonical_id, 'approved', f"Matched to gun_id: {gun_id} (confidence: {confidence}%)",
              datetime.now().isoformat()))
        self.conn.commit()

    def process_items(self):
        """Process all items automatically"""
        print(f"\n{'='*80}")
        print(f"Automated Equipment Matcher - {self.nation.title()}")
        print(f"{'='*80}")
        print(f"Total items to process: {self.total_items}\n")

        for idx, item in enumerate(self.witw_data, 1):
            canonical_name = item.get('canonical_name')
            print(f"\n[{idx}/{self.total_items}] Processing: {canonical_name}")

            # Detect type
            eq_type = self.detect_equipment_type(item)
            print(f"  Type: {eq_type}")

            # Find matches based on type
            matches = None
            if eq_type == EquipmentType.GUN:
                matches = self.find_gun_matches(item)
                if matches:
                    print(f"  Found {len(matches)} gun match(es), best score: {matches[0]['score']}%")
            elif eq_type == EquipmentType.AFV:
                matches = self.find_afv_matches(item)
                onwar_count = len(matches.get('onwar', []))
                wwiitanks_count = len(matches.get('wwiitanks', []))
                print(f"  Found {onwar_count} OnWar + {wwiitanks_count} WWIITANKS match(es)")
            elif eq_type == EquipmentType.AIRCRAFT:
                matches = self.find_aircraft_matches(item)
                if matches:
                    print(f"  Found {len(matches)} aircraft match(es), best score: {matches[0]['score']}%")

            # Make automated decision
            self.automated_decision(item, eq_type, matches)
            self.reviewed_count += 1

        # Final statistics
        self.print_statistics()
        self.save_decision_log()

    def print_statistics(self):
        """Print final statistics"""
        print(f"\n{'='*80}")
        print(f"AUTOMATED MATCHING COMPLETE - {self.nation.title()}")
        print(f"{'='*80}\n")

        print(f"Total items processed: {self.reviewed_count}/{self.total_items}")
        print(f"\nDecision Breakdown:")
        print(f"  Auto-accepted: {self.auto_accepted_count} ({self.auto_accepted_count*100//self.reviewed_count if self.reviewed_count else 0}%)")
        print(f"  Auto-filtered: {self.filtered_count}")
        print(f"  Manual review needed: {self.manual_review_count}")
        print(f"  Skipped (aircraft): {self.skipped_count - self.filtered_count}")
        print(f"\nDatabase Updates:")
        print(f"  Approved: {self.approved_count}")
        print(f"  Rejected/Flagged: {self.rejected_count}")
        print(f"  Skipped: {self.skipped_count}")

    def save_decision_log(self):
        """Save decision log to file"""
        log_dir = PROJECT_ROOT / "data" / "equipment_matching_logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{self.nation}_automated_matching_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        log_data = {
            'nation': self.nation,
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_items': self.total_items,
                'reviewed': self.reviewed_count,
                'auto_accepted': self.auto_accepted_count,
                'auto_filtered': self.filtered_count,
                'manual_review': self.manual_review_count,
                'approved': self.approved_count,
                'rejected': self.rejected_count,
                'skipped': self.skipped_count
            },
            'decisions': self.decisions
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)

        print(f"\n[OK] Decision log saved: {log_file}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='Automated Equipment Matcher v2.1')
    parser.add_argument('--nation', default='british',
        choices=['british', 'german', 'italian', 'american', 'french'],
        help='Nation to process (default: british)')

    args = parser.parse_args()

    matcher = AutomatedEquipmentMatcher(nation=args.nation)

    try:
        matcher.connect_db()
        matcher.load_data_sources()
        matcher.process_items()
    finally:
        matcher.close()

if __name__ == '__main__':
    main()
