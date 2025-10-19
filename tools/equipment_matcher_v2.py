#!/usr/bin/env python3
"""
Enhanced Equipment Matcher v2.0
- Smart type detection (Gun/AFV/Soft-skin)
- Gun matching to database guns table
- Research agent integration for missing data

Usage:
    python tools/equipment_matcher_v2.py --nation french
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
import re

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

class EnhancedEquipmentMatcher:
    """Enhanced equipment matching with type detection"""

    def __init__(self, nation='british'):
        self.nation = nation.lower()
        self.conn = None
        self.witw_data = []
        self.onwar_data = []
        self.wwiitanks_data = []
        self.guns_data = []  # NEW: Database guns

        # Statistics
        self.total_items = 0
        self.reviewed_count = 0
        self.approved_count = 0
        self.rejected_count = 0
        self.skipped_count = 0
        self.researched_count = 0

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

        # Gun/Artillery types
        gun_types = [
            'field_artillery', 'anti_tank', 'anti_aircraft',
            'anti_tank_guns', 'anti_aircraft_guns', 'artillery',
            'towed_artillery'
        ]

        # AFV types
        afv_types = [
            'tank', 'tanks', 'armored_car', 'armored_cars',
            'halftrack', 'halftracks', 'main_tanks', 'light_tanks',
            'medium_tanks', 'heavy_tanks', 'tank_destroyer',
            'tank_destroyers', 'armored_vehicle', 'armored_vehicles',
            'armored_cars_reconnaissance'
        ]

        # Soft-skin types
        soft_skin_types = [
            'truck', 'trucks', 'motorcycle', 'motorcycles',
            'support_vehicle', 'support_vehicles',
            'recovery_vehicle', 'recovery_vehicles',
            'workshop_vehicle', 'workshop_vehicles',
            'artillery_tractor', 'artillery_tractors',
            'carrier', 'carriers', 'command_vehicle', 'command_vehicles'
        ]

        # Aircraft types
        aircraft_types = [
            'fighter', 'fighters', 'bomber', 'bombers',
            'reconnaissance', 'dive_bomber', 'dive_bombers',
            'aircraft'
        ]

        # Check type and category
        for gun_type in gun_types:
            if gun_type in eq_type or gun_type in category:
                return EquipmentType.GUN

        for afv_type in afv_types:
            if afv_type in eq_type or afv_type in category:
                return EquipmentType.AFV

        for soft_type in soft_skin_types:
            if soft_type in eq_type or soft_type in category:
                return EquipmentType.SOFT_SKIN

        for air_type in aircraft_types:
            if air_type in eq_type or air_type in category:
                return EquipmentType.AIRCRAFT

        return EquipmentType.UNKNOWN

    def is_summary_category(self, item):
        """Check if item is a summary/aggregate category, not real equipment"""
        name = item.get('canonical_name', '').lower()

        # Summary category patterns
        summary_patterns = [
            'total ', 'all ', 'summary ', 'aggregate ',
            'grand total', 'overall total', 'combined total'
        ]

        return any(pattern in name for pattern in summary_patterns)

    def load_data_sources(self):
        """Load all data sources - WITW filtered by nation, but guns/AFVs from ALL nations"""
        print("\n[...] Loading data sources...")

        # Load WITW baseline (filter by target nation only)
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

                if item_nation == self.nation:
                    item['canonical_id'] = canonical_id

                    # Filter out summary categories
                    if self.is_summary_category(item):
                        filtered_count += 1
                        continue

                    self.witw_data.append(item)

        print(f"[OK] Loaded {len(self.witw_data)} {self.nation.title()} items from WITW")
        if filtered_count > 0:
            print(f"[INFO] Filtered out {filtered_count} summary categories (e.g., 'Total Light Tanks')")

        # Load database guns from ALL nations (for captured/allied equipment)
        print(f"[...] Loading guns from ALL nations (for captured/allied equipment)...")
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM guns
        """)

        for row in cursor.fetchall():
            self.guns_data.append(dict(row))

        print(f"[OK] Loaded {len(self.guns_data)} guns from database (all nations)")

        # Load OnWar AFVs from ALL nations (for captured/allied equipment)
        print(f"[...] Loading AFVs from ALL nations (for captured/allied equipment)...")
        if ONWAR_FILE.exists():
            with open(ONWAR_FILE, 'r', encoding='utf-8') as f:
                all_onwar = json.load(f)
                self.onwar_data = all_onwar

            print(f"[OK] Loaded {len(self.onwar_data)} AFVs from OnWar (all nations)")
        else:
            print(f"[WARN] OnWar file not found: {ONWAR_FILE}")

        # Load WWII Tanks UK AFVs from ALL nations (for captured/allied equipment)
        if WWIITANKS_FILE.exists():
            with open(WWIITANKS_FILE, 'r', encoding='utf-8') as f:
                all_wwiitanks = json.load(f)
                self.wwiitanks_data = all_wwiitanks

            print(f"[OK] Loaded {len(self.wwiitanks_data)} AFVs from WWII Tanks UK (all nations)")
        else:
            print(f"[WARN] WWII Tanks UK file not found: {WWIITANKS_FILE}")

        self.total_items = len(self.witw_data)

        print(f"\n[INFO] Cross-nation matching enabled - can match captured/allied equipment")

    def parse_caliber(self, name):
        """Extract caliber from equipment name"""
        # Patterns: 75mm, 7.5cm, 3.7-inch, etc.
        patterns = [
            r'(\d+\.?\d*)\s*mm',
            r'(\d+\.?\d*)\s*cm',
            r'(\d+\.?\d*)-inch',
            r'(\d+\.?\d*)"',
        ]

        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                caliber = float(match.group(1))
                # Convert cm to mm
                if 'cm' in pattern:
                    caliber *= 10
                # Convert inches to mm
                elif 'inch' in pattern or '"' in pattern:
                    caliber *= 25.4
                return int(caliber)

        return None

    def find_gun_matches(self, witw_item):
        """Find matching guns in database"""
        name = witw_item.get('canonical_name', '')
        caliber = self.parse_caliber(name)

        matches = []

        for gun in self.guns_data:
            score = 0
            reasons = []

            # Caliber match (most important)
            if caliber and gun.get('caliber_mm') == caliber:
                score += 50
                reasons.append(f"Caliber: {caliber}mm")

            # Name similarity
            gun_name = gun.get('name', '').lower()
            witw_name = name.lower()

            # Check for common words
            gun_words = set(re.findall(r'\w+', gun_name))
            witw_words = set(re.findall(r'\w+', witw_name))
            common_words = gun_words & witw_words

            if len(common_words) >= 2:
                score += 30
                reasons.append(f"Name match: {', '.join(list(common_words)[:3])}")
            elif len(common_words) == 1:
                score += 15

            if score >= 50:
                matches.append({
                    'gun': gun,
                    'score': score,
                    'reasons': reasons
                })

        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:3]  # Top 3 matches

    def normalize_name(self, name):
        """Normalize equipment name for matching"""
        if not name:
            return ""

        name = name.lower()

        # Special handling for model numbers: convert "h-39" or "h 39" to "h39"
        # This handles variants like: H-39/H39, R-35/R35, S-35/S35, etc.
        name = re.sub(r'([a-z])[\s\-](\d+)', r'\1\2', name)

        # Remove all remaining punctuation (including hyphens)
        name = re.sub(r'[.,/\-]', ' ', name)

        # Collapse multiple spaces
        name = ' '.join(name.split())
        return name

    def find_afv_matches(self, witw_item):
        """Find matching AFVs in OnWar and WWII Tanks UK"""
        witw_name = self.normalize_name(witw_item.get('canonical_name', ''))

        matches = {
            'onwar': None,
            'onwar_confidence': 0,
            'wwiitanks': None,
            'wwiitanks_confidence': 0
        }

        # Search OnWar
        for onwar_item in self.onwar_data:
            onwar_name = self.normalize_name(onwar_item.get('vehicle_name', ''))

            if witw_name == onwar_name:
                score = 100
            elif witw_name in onwar_name or onwar_name in witw_name:
                score = 85
            else:
                witw_words = set(witw_name.split())
                onwar_words = set(onwar_name.split())
                common = len(witw_words & onwar_words)
                if common >= 2:
                    score = 70
                else:
                    continue

            if score > matches['onwar_confidence']:
                matches['onwar'] = onwar_item
                matches['onwar_confidence'] = score

        # Search WWII Tanks UK
        for wwiitanks_item in self.wwiitanks_data:
            wwiitanks_name = self.normalize_name(wwiitanks_item.get('vehicle_name', ''))

            if witw_name == wwiitanks_name:
                score = 100
            elif witw_name in wwiitanks_name or wwiitanks_name in witw_name:
                score = 85
            else:
                witw_words = set(witw_name.split())
                wwiitanks_words = set(wwiitanks_name.split())
                common = len(witw_words & wwiitanks_words)
                if common >= 2:
                    score = 70
                else:
                    continue

            if score > matches['wwiitanks_confidence']:
                matches['wwiitanks'] = wwiitanks_item
                matches['wwiitanks_confidence'] = score

        return matches

    def display_comparison(self, witw_item, eq_type, matches, item_number):
        """Display side-by-side comparison"""
        print(f"\n{'='*80}")
        print(f"Equipment Match Review #{item_number} of {self.total_items}")
        print(f"Progress: {self.reviewed_count} reviewed | {self.approved_count} approved | {self.rejected_count} rejected | {self.skipped_count} skipped")
        print(f"{'='*80}")

        # WITW Baseline
        print(f"\n[WITW CANONICAL] - Type: {eq_type.upper()}")
        print(f"  ID: {witw_item.get('canonical_id')}")
        print(f"  Name: {witw_item.get('canonical_name')}")
        print(f"  Type: {witw_item.get('type')}")
        print(f"  Category: {witw_item.get('category')}")

        if eq_type == EquipmentType.GUN:
            # Show gun matches
            gun_matches = matches.get('guns', [])
            if gun_matches:
                for idx, match in enumerate(gun_matches[:3], 1):  # Show top 3
                    gun = match['gun']
                    score = match['score']
                    reasons = match['reasons']

                    print(f"\n[GUN MATCH #{idx}] (Score: {score}%)")
                    print(f"  Gun ID: {gun.get('gun_id')}")
                    print(f"  Name: {gun.get('name')}")
                    print(f"  Nation: {gun.get('nation', 'Unknown').upper()}")  # Show nation
                    print(f"  Caliber: {gun.get('caliber_mm')}mm")
                    print(f"  Barrel: {gun.get('barrel_length')}")
                    print(f"  Type: {gun.get('gun_type')}")
                    print(f"  Match reasons: {', '.join(reasons)}")

                    # Show ammunition count
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM ammunition WHERE gun_id = ?", (gun.get('gun_id'),))
                    ammo_count = cursor.fetchone()[0]
                    print(f"  Ammunition types: {ammo_count}")
            else:
                print(f"\n[GUN MATCH] No gun matches found in database")

        elif eq_type == EquipmentType.AFV:
            # Show AFV matches
            if matches.get('onwar'):
                onwar = matches['onwar']
                print(f"\n[ONWAR MATCH] (Confidence: {matches['onwar_confidence']}%)")
                print(f"  Name: {onwar.get('vehicle_name')}")
                print(f"  Nation: {onwar.get('country', 'Unknown').upper()}")  # Show nation
                print(f"  Type: {onwar.get('vehicle_type')}")
                print(f"  Weight: {onwar.get('combat_weight')}")
                print(f"  Crew: {onwar.get('crew')}")
            else:
                print(f"\n[ONWAR MATCH] No match found")

            if matches.get('wwiitanks'):
                wwiitanks = matches['wwiitanks']
                print(f"\n[WWIITANKS MATCH] (Confidence: {matches['wwiitanks_confidence']}%)")
                print(f"  Name: {wwiitanks.get('vehicle_name')}")
                print(f"  Nation: {wwiitanks.get('country', 'Unknown').upper()}")  # Show nation
                specs = wwiitanks.get('specifications', {})
                print(f"  Weight: {specs.get('combat_weight')}")
                print(f"  Max Speed: {specs.get('max_road_speed')}")
            else:
                print(f"\n[WWIITANKS MATCH] No match found")

        elif eq_type == EquipmentType.SOFT_SKIN:
            print(f"\n[SOFT-SKIN VEHICLE] No external matching needed")
            print(f"  Recommendation: Auto-approve baseline data")

        elif eq_type == EquipmentType.AIRCRAFT:
            print(f"\n[AIRCRAFT] No external matching needed (aircraft data out of scope)")
            print(f"  Recommendation: Skip or auto-approve baseline")

    def get_user_choice(self, eq_type, matches):
        """Get user's decision based on equipment type"""

        # Handle soft-skin auto-approval
        if eq_type == EquipmentType.SOFT_SKIN:
            print(f"\n[SOFT-SKIN VEHICLE] Auto-approving baseline data...")
            confirm = input("Auto-approve? [Y/N]: ").strip().upper()
            if confirm == 'Y':
                return {'action': 'A', 'match_type': 'soft_skin'}
            else:
                print(f"\nActions:")
                print(f"  [R] Reject - Mark for manual research")
                print(f"  [S] Skip - Review later")
                print(f"  [Q] Quit - Save and exit")
                print()
                while True:
                    choice = input("Choice: ").strip().upper()
                    if choice in ['R', 'S', 'Q']:
                        return {'action': choice}
                    print("[ERROR] Invalid choice. Please enter R, S, or Q")

        # Handle gun match selection
        elif eq_type == EquipmentType.GUN:
            gun_matches = matches.get('guns', [])
            if gun_matches:
                print(f"\nActions:")
                for idx in range(len(gun_matches[:3])):
                    print(f"  [{idx+1}] Accept Gun Match #{idx+1}")
                print(f"  [N] None - Reject all matches")
                print(f"  [R] Reject - Mark for manual research")
                print(f"  [S] Skip - Review later")
                print(f"  [Q] Quit - Save and exit")
                print()

                while True:
                    choice = input("Choice: ").strip().upper()
                    if choice in ['1', '2', '3'] and int(choice) <= len(gun_matches):
                        selected_match = gun_matches[int(choice) - 1]
                        return {'action': 'A', 'match_type': 'gun', 'selected_gun': selected_match}
                    elif choice in ['N', 'R', 'S', 'Q']:
                        return {'action': choice}
                    print(f"[ERROR] Invalid choice. Please enter 1-{len(gun_matches[:3])}, N, R, S, or Q")
            else:
                # No gun matches found
                print(f"\nActions:")
                print(f"  [R] Reject - Mark for manual research")
                print(f"  [S] Skip - Review later")
                print(f"  [Q] Quit - Save and exit")
                print()
                while True:
                    choice = input("Choice: ").strip().upper()
                    if choice in ['R', 'S', 'Q']:
                        return {'action': choice}
                    print("[ERROR] Invalid choice. Please enter R, S, or Q")

        # Handle AFV or other types
        else:
            print(f"\nActions:")
            print(f"  [A] Approve - Merge/link matched data")
            print(f"  [R] Reject - Mark for manual research")
            print(f"  [S] Skip - Review later")
            print(f"  [Q] Quit - Save and exit")
            print()

            while True:
                choice = input("Choice: ").strip().upper()
                if choice in ['A', 'R', 'S', 'Q']:
                    return {'action': choice}
                print("[ERROR] Invalid choice. Please enter A, R, S, or Q")

    def save_review(self, witw_item, matches, status, notes=''):
        """Save review decision"""
        cursor = self.conn.cursor()

        canonical_id = witw_item.get('canonical_id')
        witw_name = witw_item.get('canonical_name')

        cursor.execute("""
            INSERT INTO match_reviews (
                canonical_id, witw_name,
                review_status, reviewer_notes, reviewed_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            canonical_id, witw_name,
            status, notes, datetime.now().isoformat()
        ))

        self.conn.commit()

    def launch_research_agent(self, witw_item):
        """Launch research agent to find missing data"""
        name = witw_item.get('canonical_name')
        eq_type = witw_item.get('type')
        category = witw_item.get('category', '')
        nation = self.nation
        canonical_id = witw_item.get('canonical_id')

        print(f"\n[RESEARCH] Launching research agent for: {name}")
        print(f"  Type: {eq_type}")
        print(f"  Category: {category}")
        print(f"  Nation: {nation.title()}")
        print(f"\n[INFO] Research agent will search for:")
        print(f"  - Technical specifications")
        print(f"  - Production data and variants")
        print(f"  - Historical deployment information")
        print(f"  - Cross-references from multiple sources")
        print(f"\n[...] Launching agent...")

        # Build comprehensive research prompt
        research_prompt = f"""Research and compile detailed information for the following military equipment:

**Equipment to Research:**
- Name: {name}
- Nation: {nation.title()}
- Type: {eq_type}
- Category: {category}

**Information Needed:**
1. **Technical Specifications** (if gun/artillery):
   - Caliber (mm)
   - Barrel length
   - Weight
   - Rate of fire
   - Effective range
   - Ammunition types used

2. **Technical Specifications** (if AFV/vehicle):
   - Weight (tonnes)
   - Crew size
   - Armor thickness (front/side/rear)
   - Main armament
   - Secondary armament
   - Engine and speed
   - Operational range

3. **Production Data**:
   - Production dates (start/end)
   - Total units produced
   - Known variants
   - Manufacturing locations

4. **Historical Deployment**:
   - Units that used this equipment
   - Theater of operations (focus on North Africa 1940-1943)
   - Operational history

**Search Strategy:**
- Search official military history archives
- Use curated military equipment databases (Feldgrau, Niehorster, etc.)
- Search technical manuals and field manuals
- DO NOT use Wikipedia as a primary source
- Cross-reference multiple sources for accuracy

**Output Format:**
Return findings in structured format with source citations. Include confidence level for each data point.
"""

        # Save research request to file for audit trail
        research_dir = PROJECT_ROOT / "data" / "research_requests"
        research_dir.mkdir(parents=True, exist_ok=True)

        research_file = research_dir / f"{nation}_{canonical_id}_research.txt"
        with open(research_file, 'w', encoding='utf-8') as f:
            f.write(research_prompt)
            f.write(f"\n\n--- Research initiated: {datetime.now().isoformat()} ---")

        print(f"\n[OK] Research request saved to: {research_file}")
        print(f"\n{'='*80}")
        print("RESEARCH OPTIONS:")
        print(f"{'='*80}")
        print("\nOption A - Automated Research (Recommended):")
        print(f"  1. Open Claude Code")
        print(f"  2. Run: node tools/research_equipment.js {research_file.relative_to(PROJECT_ROOT)}")
        print(f"  3. Copy the research prompt and paste into Claude Code")
        print(f"  4. Claude Code will use WebSearch and sources to find data")
        print(f"  5. Save findings and continue matching")
        print("\nOption B - Manual Research:")
        print(f"  1. Open research file: {research_file}")
        print(f"  2. Search military archives and databases manually")
        print(f"  3. Compile findings with source citations")
        print(f"  4. Update match_reviews table with notes")
        print(f"\n{'='*80}")
        print("\nPress Enter to continue with equipment matching...")
        input()

        self.researched_count += 1

    def process_items(self, start_fresh=False):
        """Process all WITW items interactively"""
        print(f"\n{'='*80}")
        print(f"Enhanced Equipment Matcher v2.0 - {self.nation.title()}")
        print(f"{'='*80}")
        print(f"Total items to review: {self.total_items}")

        for idx, witw_item in enumerate(self.witw_data, 1):
            # Detect equipment type
            eq_type = self.detect_equipment_type(witw_item)

            # Find matches based on type
            if eq_type == EquipmentType.GUN:
                matches = {'guns': self.find_gun_matches(witw_item)}
            elif eq_type == EquipmentType.AFV:
                matches = self.find_afv_matches(witw_item)
            else:
                matches = {}

            # Display comparison
            self.display_comparison(witw_item, eq_type, matches, idx)

            # Get user decision
            choice_result = self.get_user_choice(eq_type, matches)
            action = choice_result.get('action')

            if action == 'Q':
                print("\n[INFO] Quitting. Progress saved.")
                break
            elif action == 'A':
                # Handle approval
                match_type = choice_result.get('match_type')
                if match_type == 'gun':
                    selected_gun = choice_result.get('selected_gun')
                    gun_name = selected_gun['gun']['name']
                    print(f"[OK] Approved gun match: {gun_name}")
                elif match_type == 'soft_skin':
                    print(f"[OK] Auto-approved soft-skin vehicle")
                else:
                    print(f"[OK] Approved")

                self.save_review(witw_item, matches, 'approved')
                self.approved_count += 1
                self.reviewed_count += 1

            elif action == 'R' or action == 'N':
                notes = input("Enter notes for research: ").strip()

                # Offer to launch research agent
                research = input("\nLaunch research agent? [Y/N]: ").strip().upper()
                if research == 'Y':
                    self.launch_research_agent(witw_item)

                self.save_review(witw_item, matches, 'rejected', notes)
                self.rejected_count += 1
                self.reviewed_count += 1
                print("[OK] Rejected and marked for research")
            elif action == 'S':
                self.save_review(witw_item, matches, 'skipped')
                self.skipped_count += 1
                print("[OK] Skipped")

        # Final statistics
        print(f"\n{'='*80}")
        print(f"Session Complete")
        print(f"{'='*80}")
        print(f"Total reviewed: {self.reviewed_count}")
        print(f"  Approved: {self.approved_count}")
        print(f"  Rejected: {self.rejected_count} ({self.researched_count} with research agent)")
        print(f"  Skipped: {self.skipped_count}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Enhanced Equipment Matcher v2.0 with type detection'
    )
    parser.add_argument(
        '--nation',
        default='french',
        choices=['british', 'german', 'italian', 'american', 'french'],
        help='Nation to process (default: french)'
    )
    parser.add_argument(
        '--start-fresh',
        action='store_true',
        help='Review all items, ignoring previous reviews'
    )

    args = parser.parse_args()

    matcher = EnhancedEquipmentMatcher(nation=args.nation)

    try:
        matcher.connect_db()
        matcher.load_data_sources()
        matcher.process_items(start_fresh=args.start_fresh)
        matcher.close()

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n[INFO] Matching cancelled by user")
        matcher.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Matching failed: {e}")
        import traceback
        traceback.print_exc()
        matcher.close()
        sys.exit(1)

if __name__ == '__main__':
    main()
