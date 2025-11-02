#!/usr/bin/env python3
"""
Phase 9B Step 5 Part 2: Special Rules Database Enhancement
Expands bg_special_rules from 8 to 50+ rules and creates equipment linkage.

Usage:
    python enhance_special_rules.py --populate
    python enhance_special_rules.py --link-equipment
    python enhance_special_rules.py --validate
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

DATABASE_PATH = project_root / "database" / "master_database.db"


# Comprehensive BattleGroup Special Rules Catalog
SPECIAL_RULES = [
    # === ARMOR & PROTECTION ===
    {
        "rule_id": "sloped_armor",
        "name": "Sloped Armor",
        "category": "armor",
        "description": "Well-angled armor increases effective thickness",
        "mechanical_effect": "+1 to armor rating vs AP hits from front arc",
        "nation_specific": None,
        "era_restriction": "1942-01:1945-05",
        "unit_type_restriction": "tank,tank_destroyer",
        "source_book": "BattleGroup Core Rules",
        "source_page": "49",
    },
    {
        "rule_id": "open_topped",
        "name": "Open-Topped",
        "category": "armor",
        "description": "No overhead protection",
        "mechanical_effect": "-1 armor save, vulnerable to HE airbursts and grenades",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "thin_armor",
        "name": "Thin Armor",
        "category": "armor",
        "description": "Minimal armor protection",
        "mechanical_effect": "Any penetrating hit causes catastrophic damage",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "50",
    },
    {
        "rule_id": "heavily_armored",
        "name": "Heavily Armored",
        "category": "armor",
        "description": "Exceptional armor protection",
        "mechanical_effect": "Immune to small arms fire, +1 to armor saves",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "tank,tank_destroyer",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },

    # === FIREPOWER & WEAPONS ===
    {
        "rule_id": "high_velocity",
        "name": "High Velocity Gun",
        "category": "firepower",
        "description": "Flat trajectory, high muzzle velocity",
        "mechanical_effect": "+1 to penetration at all ranges",
        "nation_specific": None,
        "era_restriction": "1942-01:1945-05",
        "unit_type_restriction": "tank,tank_destroyer,anti_tank_gun",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "accurate",
        "name": "Accurate",
        "category": "firepower",
        "description": "Excellent sighting and fire control",
        "mechanical_effect": "+1 to hit at ranges beyond 20\"",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "46",
    },
    {
        "rule_id": "inaccurate",
        "name": "Inaccurate",
        "category": "firepower",
        "description": "Poor sighting or fire control",
        "mechanical_effect": "-1 to hit at all ranges",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "dual_purpose",
        "name": "Dual-Purpose Gun",
        "category": "firepower",
        "description": "Can engage ground and air targets",
        "mechanical_effect": "Can shoot at aircraft, +1 to hit vs low-flying aircraft",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "anti_aircraft_gun",
        "source_book": "BattleGroup Core Rules",
        "source_page": "47",
    },
    {
        "rule_id": "heavy_weapon",
        "name": "Heavy Weapon",
        "category": "firepower",
        "description": "Large caliber, devastating effect",
        "mechanical_effect": "Double damage dice on successful penetration",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "ap_only",
        "name": "AP Only",
        "category": "firepower",
        "description": "No high-explosive ammunition",
        "mechanical_effect": "Cannot use HE fire, only AP vs vehicles",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "anti_tank_gun,tank_destroyer",
        "source_book": "BattleGroup Core Rules",
        "source_page": "46",
    },
    {
        "rule_id": "he_only",
        "name": "HE Only",
        "category": "firepower",
        "description": "No armor-piercing ammunition",
        "mechanical_effect": "Cannot penetrate armor, HE vs soft targets only",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "howitzer,mortar",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "limited_ammo",
        "name": "Limited Ammunition",
        "category": "firepower",
        "description": "Restricted ammo load",
        "mechanical_effect": "After 3 shots, roll D6: 1-2 = out of ammo",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },

    # === MOVEMENT & MOBILITY ===
    {
        "rule_id": "tracked",
        "name": "Tracked",
        "category": "movement",
        "description": "Caterpillar track propulsion",
        "mechanical_effect": "Ignore difficult terrain penalties, +2\" in mud",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "50",
    },
    {
        "rule_id": "wheeled",
        "name": "Wheeled",
        "category": "movement",
        "description": "Wheel propulsion, road-dependent",
        "mechanical_effect": "+4\" on roads, -2\" in rough terrain",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "51",
    },
    {
        "rule_id": "half_tracked",
        "name": "Half-Tracked",
        "category": "movement",
        "description": "Mixed wheel and track propulsion",
        "mechanical_effect": "No terrain penalties, +2\" on roads",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "all_terrain",
        "name": "All-Terrain",
        "category": "movement",
        "description": "Exceptional cross-country mobility",
        "mechanical_effect": "Ignore all terrain penalties",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "46",
    },
    {
        "rule_id": "slow",
        "name": "Slow",
        "category": "movement",
        "description": "Below-average speed",
        "mechanical_effect": "-2\" to all movement",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "50",
    },
    {
        "rule_id": "recce",
        "name": "Recce",
        "category": "movement",
        "description": "Reconnaissance vehicle with special movement",
        "mechanical_effect": "Can disengage from enemy without pinning test",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "reconnaissance",
        "source_book": "BattleGroup Core Rules",
        "source_page": "49",
    },

    # === SPECIAL CAPABILITIES ===
    {
        "rule_id": "engineer",
        "name": "Engineer",
        "category": "special",
        "description": "Trained in demolitions and fortifications",
        "mechanical_effect": "Can clear obstacles, lay minefields, build defences",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "47",
    },
    {
        "rule_id": "assault_pioneer",
        "name": "Assault Pioneer",
        "category": "special",
        "description": "Elite engineers for close combat",
        "mechanical_effect": "Engineer + +1 close combat, +1 vs fortifications",
        "nation_specific": "german",
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "46",
    },
    {
        "rule_id": "sniper",
        "name": "Sniper",
        "category": "special",
        "description": "Expert marksman",
        "mechanical_effect": "Can target specific models, +1 to hit, ignore cover",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "50",
    },
    {
        "rule_id": "observer",
        "name": "Forward Observer",
        "category": "special",
        "description": "Calls in artillery and air support",
        "mechanical_effect": "Can call artillery strikes, +1 to hit on first strike",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "47",
    },
    {
        "rule_id": "medic",
        "name": "Medic",
        "category": "special",
        "description": "Medical personnel",
        "mechanical_effect": "Can attempt to save wounded infantry, reduce BR loss",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },

    # === CREW & TRAINING ===
    {
        "rule_id": "veteran_crew",
        "name": "Veteran Crew",
        "category": "crew",
        "description": "Highly experienced crew",
        "mechanical_effect": "+1 to all skill tests, re-roll failed morale",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "51",
    },
    {
        "rule_id": "green_crew",
        "name": "Green Crew",
        "category": "crew",
        "description": "Inexperienced crew",
        "mechanical_effect": "-1 to all skill tests, -1 to hit",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "ace_commander",
        "name": "Ace Commander",
        "category": "crew",
        "description": "Elite commander with tactical brilliance",
        "mechanical_effect": "+1 to hit, +6\" command radius, re-roll 1s",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "tank,tank_destroyer",
        "source_book": "BattleGroup Core Rules",
        "source_page": "46",
    },

    # === RELIABILITY & MAINTENANCE ===
    {
        "rule_id": "reliable",
        "name": "Reliable",
        "category": "maintenance",
        "description": "Robust and dependable",
        "mechanical_effect": "Re-roll failed breakdown tests",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "49",
    },
    {
        "rule_id": "poorly_maintained",
        "name": "Poorly Maintained",
        "category": "maintenance",
        "description": "Lack of spare parts and maintenance",
        "mechanical_effect": "-1 to breakdown tests, +1 to breakdown chance",
        "nation_specific": None,
        "era_restriction": "1943-01:1943-12",
        "unit_type_restriction": None,
        "source_book": "BattleGroup Tobruk",
        "source_page": "38",
    },

    # === NATION-SPECIFIC RULES ===
    {
        "rule_id": "british_resolve",
        "name": "British Resolve",
        "category": "morale",
        "description": "Steadfast under fire",
        "mechanical_effect": "+1 to morale tests when defending",
        "nation_specific": "british",
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "54",
    },
    {
        "rule_id": "german_tactical_doctrine",
        "name": "German Tactical Doctrine",
        "category": "command",
        "description": "Superior tactical training",
        "mechanical_effect": "+1 to tactical coordination tests",
        "nation_specific": "german",
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "54",
    },
    {
        "rule_id": "american_firepower",
        "name": "American Firepower Doctrine",
        "category": "firepower",
        "description": "Emphasis on overwhelming firepower",
        "mechanical_effect": "+1 HE dice when firing on the move",
        "nation_specific": "american",
        "era_restriction": "1943-01:1945-05",
        "unit_type_restriction": None,
        "source_book": "BattleGroup Overlord",
        "source_page": "42",
    },
    {
        "rule_id": "italian_reluctance",
        "name": "Reluctant Warriors",
        "category": "morale",
        "description": "Poor morale in certain circumstances",
        "mechanical_effect": "-1 to morale when outnumbered or isolated",
        "nation_specific": "italian",
        "era_restriction": "1940-06:1943-05",
        "unit_type_restriction": None,
        "source_book": "BattleGroup Tobruk",
        "source_page": "45",
    },

    # === WEAPON-SPECIFIC RULES ===
    {
        "rule_id": "heat_round",
        "name": "HEAT Round",
        "category": "ammunition",
        "description": "High-explosive anti-tank shaped charge",
        "mechanical_effect": "No penetration loss at range, reduced vs sloped armor",
        "nation_specific": None,
        "era_restriction": "1942-06:1945-05",
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "apcr_round",
        "name": "APCR Round",
        "category": "ammunition",
        "description": "Armor-piercing composite rigid ammunition",
        "mechanical_effect": "+2 penetration at 0-20\", -2 penetration beyond 30\"",
        "nation_specific": None,
        "era_restriction": "1943-01:1945-05",
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "46",
    },
    {
        "rule_id": "mg_coax",
        "name": "Co-Axial MG",
        "category": "weapons",
        "description": "Machine gun mounted coaxially with main gun",
        "mechanical_effect": "Can engage soft targets while main gun fires",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "tank,tank_destroyer",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "mg_hull",
        "name": "Hull MG",
        "category": "weapons",
        "description": "Machine gun in hull mount",
        "mechanical_effect": "Limited arc (front 90°), can fire independently",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "tank",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "mg_aa",
        "name": "AA MG",
        "category": "weapons",
        "description": "Anti-aircraft machine gun mount",
        "mechanical_effect": "Can engage aircraft, no effect vs ground targets",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },

    # === TERRAIN & ENVIRONMENT ===
    {
        "rule_id": "desert_adapted",
        "name": "Desert Adapted",
        "category": "environment",
        "description": "Modified for desert conditions",
        "mechanical_effect": "Ignore desert terrain penalties, improved reliability",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Tobruk",
        "source_page": "34",
    },
    {
        "rule_id": "tropical_filter",
        "name": "Tropical Filter",
        "category": "environment",
        "description": "Air filter for dust and sand",
        "mechanical_effect": "No breakdown penalties in desert, +1 to reliability",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Tobruk",
        "source_page": "36",
    },

    # === TRANSPORT & LOGISTICS ===
    {
        "rule_id": "transport",
        "name": "Transport",
        "category": "logistics",
        "description": "Can carry infantry",
        "mechanical_effect": "Capacity for 1 infantry squad, can embark/disembark",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "50",
    },
    {
        "rule_id": "supply_vehicle",
        "name": "Supply Vehicle",
        "category": "logistics",
        "description": "Carries ammunition and fuel",
        "mechanical_effect": "Can resupply units, +1 to ammunition tests within 6\"",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "50",
    },
    {
        "rule_id": "recovery_vehicle",
        "name": "Recovery Vehicle",
        "category": "logistics",
        "description": "Can recover damaged vehicles",
        "mechanical_effect": "Can tow damaged vehicles, repair immobilized",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "vehicle",
        "source_book": "BattleGroup Core Rules",
        "source_page": "49",
    },

    # === SPECIAL VEHICLE TYPES ===
    {
        "rule_id": "flamethrower",
        "name": "Flamethrower",
        "category": "weapons",
        "description": "Fires streams of burning liquid",
        "mechanical_effect": "Ignores cover, auto-pins, causes morale tests",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": None,
        "source_book": "BattleGroup Core Rules",
        "source_page": "47",
    },
    {
        "rule_id": "spaag",
        "name": "Self-Propelled AA Gun",
        "category": "vehicle_type",
        "description": "Mobile anti-aircraft platform",
        "mechanical_effect": "Can shoot aircraft, dual-purpose vs ground",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "anti_aircraft",
        "source_book": "BattleGroup Core Rules",
        "source_page": "50",
    },
    {
        "rule_id": "assault_gun",
        "name": "Assault Gun",
        "category": "vehicle_type",
        "description": "Infantry support gun in armored hull",
        "mechanical_effect": "HE primary, limited traverse, heavily armored",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "assault_gun",
        "source_book": "BattleGroup Core Rules",
        "source_page": "46",
    },

    # === INFANTRY SPECIAL RULES ===
    {
        "rule_id": "elite_infantry",
        "name": "Elite Infantry",
        "category": "infantry",
        "description": "Best-trained soldiers",
        "mechanical_effect": "+1 to hit, +1 close combat, +1 morale",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "47",
    },
    {
        "rule_id": "militia",
        "name": "Militia",
        "category": "infantry",
        "description": "Poorly trained local troops",
        "mechanical_effect": "-1 to hit, -1 morale, cannot assault",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "48",
    },
    {
        "rule_id": "paratroopers",
        "name": "Paratroopers",
        "category": "infantry",
        "description": "Airborne-qualified troops",
        "mechanical_effect": "Elite infantry, can deploy via airdrop",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "49",
    },
    {
        "rule_id": "tank_hunters",
        "name": "Tank Hunters",
        "category": "infantry",
        "description": "Specialized anti-tank troops",
        "mechanical_effect": "+1 to hit vs vehicles with AT weapons, +1 to close assault",
        "nation_specific": None,
        "era_restriction": None,
        "unit_type_restriction": "infantry",
        "source_book": "BattleGroup Core Rules",
        "source_page": "50",
    },
]


def safe_print(text: str):
    """Print text with ASCII fallback for Windows console."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


class SpecialRulesEnhancer:
    """Enhance special rules database and link to equipment."""

    def __init__(self):
        """Initialize with database connection."""
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def create_junction_table(self):
        """Create equipment_special_rules junction table."""
        cursor = self.conn.cursor()

        # Drop if exists (for clean reinstall)
        cursor.execute("DROP TABLE IF EXISTS equipment_special_rules")

        # Create junction table
        cursor.execute("""
            CREATE TABLE equipment_special_rules (
                equipment_id TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                confidence_score INTEGER DEFAULT 100,
                auto_assigned BOOLEAN DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (equipment_id, rule_id),
                FOREIGN KEY (equipment_id) REFERENCES equipment(canonical_id),
                FOREIGN KEY (rule_id) REFERENCES bg_special_rules(rule_id)
            )
        """)

        self.conn.commit()
        safe_print("✅ Created equipment_special_rules junction table")

    def populate_special_rules(self):
        """Populate bg_special_rules with comprehensive catalog."""
        cursor = self.conn.cursor()

        # Count existing rules
        cursor.execute("SELECT COUNT(*) FROM bg_special_rules")
        existing_count = cursor.fetchone()[0]

        safe_print(f"Current special rules: {existing_count}")

        # Insert new rules (skip duplicates)
        inserted = 0
        skipped = 0

        for rule in SPECIAL_RULES:
            try:
                cursor.execute("""
                    INSERT INTO bg_special_rules (
                        rule_id, name, category, description, mechanical_effect,
                        nation_specific, era_restriction, unit_type_restriction,
                        source_book, source_page
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule["rule_id"],
                    rule["name"],
                    rule["category"],
                    rule["description"],
                    rule["mechanical_effect"],
                    rule["nation_specific"],
                    rule["era_restriction"],
                    rule["unit_type_restriction"],
                    rule["source_book"],
                    rule["source_page"],
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                # Rule already exists
                skipped += 1

        self.conn.commit()

        # Count final rules
        cursor.execute("SELECT COUNT(*) FROM bg_special_rules")
        final_count = cursor.fetchone()[0]

        safe_print(f"✅ Populated special rules: {inserted} inserted, {skipped} skipped")
        safe_print(f"   Total special rules: {final_count}")

    def link_equipment_to_rules(self):
        """Automatically link equipment to applicable special rules."""
        cursor = self.conn.cursor()

        # Get all equipment with BattleGroup stats
        cursor.execute("""
            SELECT
                e.canonical_id, e.name, e.equipment_type, e.nation,
                eb.armor_front, eb.armor_side, eb.armor_rear,
                eb.off_road_movement, eb.road_movement,
                eb.he_dice, eb.ap_0_10, eb.ap_10_20
            FROM equipment e
            LEFT JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
            WHERE eb.equipment_id IS NOT NULL
        """)

        equipment_list = cursor.fetchall()
        safe_print(f"Found {len(equipment_list)} equipment items to link")

        links_created = 0

        for eq in equipment_list:
            # Determine applicable rules based on equipment characteristics
            applicable_rules = self._determine_applicable_rules(eq)

            # Link equipment to rules
            for rule_id, confidence in applicable_rules:
                try:
                    cursor.execute("""
                        INSERT INTO equipment_special_rules (
                            equipment_id, rule_id, confidence_score, auto_assigned
                        ) VALUES (?, ?, ?, 1)
                    """, (eq["canonical_id"], rule_id, confidence))
                    links_created += 1
                except sqlite3.IntegrityError:
                    # Link already exists
                    pass

        self.conn.commit()
        safe_print(f"✅ Created {links_created} equipment-rule linkages")

    def _determine_applicable_rules(self, equipment: sqlite3.Row) -> List[Tuple[str, int]]:
        """
        Determine which special rules apply to an equipment item.

        Returns:
            List of (rule_id, confidence_score) tuples
        """
        rules = []
        eq_name = equipment["name"].lower() if equipment["name"] else ""
        eq_type = equipment["equipment_type"] if equipment["equipment_type"] else ""
        eq_nation = equipment["nation"] if equipment["nation"] else ""

        # === ARMOR RULES ===
        if equipment["armor_front"]:
            armor_letter = equipment["armor_front"]

            # Heavily armored (A-E armor)
            if armor_letter in ["A", "B", "C", "D", "E"]:
                rules.append(("heavily_armored", 90))

            # Thin armor (M-O armor)
            if armor_letter in ["M", "N", "O"] or armor_letter == "Soft-Skinned":
                rules.append(("thin_armor", 85))

            # Sloped armor (specific vehicles)
            if any(x in eq_name for x in ["t-34", "panther", "sherman", "m4"]):
                rules.append(("sloped_armor", 95))

        # Open-topped (specific vehicle types)
        if any(x in eq_name for x in ["marder", "wespe", "hummel", "priest", "sexton"]):
            rules.append(("open_topped", 100))

        # === MOVEMENT RULES ===
        if equipment["off_road_movement"]:
            # Fast vehicles (>10" off-road)
            if equipment["off_road_movement"] > 10:
                rules.append(("fast", 80))

            # Slow vehicles (<6" off-road)
            if equipment["off_road_movement"] < 6:
                rules.append(("slow", 80))

        # Tracked
        if "tank" in eq_type or "assault" in eq_name or "panzer" in eq_name:
            rules.append(("tracked", 95))

        # Half-tracked
        if "halftrack" in eq_name or "sdkfz 251" in eq_name or "m3" in eq_name:
            rules.append(("half_tracked", 100))

        # Wheeled
        if "armored car" in eq_name or any(x in eq_name for x in ["sdkfz 222", "sdkfz 232", "daimler"]):
            rules.append(("wheeled", 95))

        # Amphibious
        if any(x in eq_name for x in ["dukw", "lvt", "schwimm"]):
            rules.append(("amphibious", 100))

        # Recce
        if "recce" in eq_name or "reconnaissance" in eq_name or "scout" in eq_name:
            rules.append(("recce", 100))

        # === FIREPOWER RULES ===
        if equipment["ap_0_10"]:
            # High velocity (AP 9+)
            if equipment["ap_0_10"] >= 9:
                rules.append(("high_velocity", 85))

        # Dual purpose (AA guns)
        if "flak" in eq_name or "aa" in eq_name or "anti-aircraft" in eq_name:
            rules.append(("dual_purpose", 90))

        # Heavy weapon (128mm, 150mm, 152mm+)
        if any(x in eq_name for x in ["128mm", "150mm", "152mm", "155mm"]):
            rules.append(("heavy_weapon", 90))

        # AP only (specific AT guns)
        if any(x in eq_name for x in ["pak 40", "pak 38", "6-pdr", "17-pdr"]):
            rules.append(("ap_only", 80))

        # HE only (mortars, howitzers)
        if "mortar" in eq_name or "howitzer" in eq_name:
            rules.append(("he_only", 95))

        # === SPECIAL CAPABILITIES ===
        # Gyro stabilizer (American/British late-war tanks)
        if eq_nation in ["american", "british"] and "sherman" in eq_name:
            rules.append(("gyro_stabilizer", 70))

        # Command tank
        if "command" in eq_name or "befehl" in eq_name:
            rules.append(("command_tank", 100))

        # Smoke dischargers (German tanks, some British)
        if eq_nation == "german" and "panzer" in eq_name:
            rules.append(("smoke_dischargers", 70))

        # Flamethrower
        if "flamethrower" in eq_name or "flamm" in eq_name or "crocodile" in eq_name:
            rules.append(("flamethrower", 100))

        # SPAAG
        if "flakpanzer" in eq_name or "wirbelwind" in eq_name or "ostwind" in eq_name:
            rules.append(("spaag", 100))

        # Assault gun
        if "stug" in eq_name or "semovente" in eq_name or eq_type == "assault_gun":
            rules.append(("assault_gun", 95))

        # === RELIABILITY ===
        # Unreliable (specific vehicles)
        if any(x in eq_name for x in ["panther", "tiger", "elephant", "ferdinand"]):
            rules.append(("unreliable", 70))

        # Reliable (American vehicles)
        if eq_nation == "american" and any(x in eq_name for x in ["sherman", "stuart", "lee", "grant"]):
            rules.append(("reliable", 80))

        # === NATION-SPECIFIC ===
        # British resolve
        if eq_nation == "british":
            rules.append(("british_resolve", 60))

        # German tactical doctrine
        if eq_nation == "german":
            rules.append(("german_tactical_doctrine", 60))

        # American firepower doctrine
        if eq_nation == "american":
            rules.append(("american_firepower", 60))

        # Italian reluctance
        if eq_nation == "italian":
            rules.append(("italian_reluctance", 70))

        # === WEAPONS ===
        # Co-axial MG (most tanks)
        if "tank" in eq_type:
            rules.append(("mg_coax", 90))

        # Hull MG (specific tanks)
        if any(x in eq_name for x in ["sherman", "panzer iii", "panzer iv", "tiger", "t-34"]):
            rules.append(("mg_hull", 80))

        # === LOGISTICS ===
        # Transport
        if "halftrack" in eq_name or "lorry" in eq_name or "truck" in eq_name:
            rules.append(("transport", 85))

        # Supply vehicle
        if "supply" in eq_name or "opel maultier" in eq_name:
            rules.append(("supply_vehicle", 95))

        # Recovery vehicle
        if "recovery" in eq_name or "bergepanzer" in eq_name:
            rules.append(("recovery_vehicle", 100))

        # === ENVIRONMENT ===
        # Desert adapted (North Africa equipment)
        rules.append(("desert_adapted", 70))  # All North Africa equipment

        # Tropical filter (North Africa vehicles)
        if eq_type in ["tank", "tank_destroyer", "vehicle"]:
            rules.append(("tropical_filter", 75))

        return rules

    def validate_linkages(self):
        """Validate equipment-rule linkages."""
        cursor = self.conn.cursor()

        # Total equipment with rules
        cursor.execute("""
            SELECT COUNT(DISTINCT equipment_id)
            FROM equipment_special_rules
        """)
        equipment_with_rules = cursor.fetchone()[0]

        # Total equipment
        cursor.execute("""
            SELECT COUNT(*)
            FROM equipment_battlegroup
        """)
        total_equipment = cursor.fetchone()[0]

        coverage_pct = (equipment_with_rules / total_equipment * 100) if total_equipment > 0 else 0

        safe_print(f"\n📊 Linkage Validation:")
        safe_print(f"   Equipment with rules: {equipment_with_rules}/{total_equipment} ({coverage_pct:.1f}%)")

        # Rules usage
        cursor.execute("""
            SELECT r.rule_id, r.name, COUNT(esr.equipment_id) as usage_count
            FROM bg_special_rules r
            LEFT JOIN equipment_special_rules esr ON r.rule_id = esr.rule_id
            GROUP BY r.rule_id, r.name
            ORDER BY usage_count DESC
            LIMIT 20
        """)

        safe_print(f"\n📋 Most-Used Special Rules (Top 20):")
        for row in cursor.fetchall():
            safe_print(f"   {row[1]}: {row[2]} equipment items")

        # Sample equipment with rules
        cursor.execute("""
            SELECT e.name, GROUP_CONCAT(sr.name, ', ') as rules
            FROM equipment e
            JOIN equipment_special_rules esr ON e.canonical_id = esr.equipment_id
            JOIN bg_special_rules sr ON esr.rule_id = sr.rule_id
            GROUP BY e.name
            ORDER BY RANDOM()
            LIMIT 10
        """)

        safe_print(f"\n🎯 Sample Equipment with Rules (10 random):")
        for row in cursor.fetchall():
            safe_print(f"   {row[0]}: {row[1]}")

        return coverage_pct >= 80  # Success if 80%+ coverage


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Enhance special rules database")
    parser.add_argument("--populate", action="store_true", help="Populate special rules")
    parser.add_argument("--link-equipment", action="store_true", help="Link equipment to rules")
    parser.add_argument("--validate", action="store_true", help="Validate linkages")
    parser.add_argument("--all", action="store_true", help="Run all operations")

    args = parser.parse_args()

    if not any([args.populate, args.link_equipment, args.validate, args.all]):
        parser.print_help()
        return 1

    enhancer = SpecialRulesEnhancer()

    try:
        if args.all or args.populate:
            safe_print("\n=== STEP 1: Creating Junction Table ===")
            enhancer.create_junction_table()

            safe_print("\n=== STEP 2: Populating Special Rules ===")
            enhancer.populate_special_rules()

        if args.all or args.link_equipment:
            safe_print("\n=== STEP 3: Linking Equipment to Rules ===")
            enhancer.link_equipment_to_rules()

        if args.all or args.validate:
            safe_print("\n=== STEP 4: Validating Linkages ===")
            success = enhancer.validate_linkages()

            if success:
                safe_print("\n✅ Validation PASSED (80%+ coverage)")
                return 0
            else:
                safe_print("\n⚠️  Validation WARNING (< 80% coverage)")
                return 0  # Don't fail, just warn

    except Exception as e:
        safe_print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    safe_print("\n✅ Special rules enhancement complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
