#!/usr/bin/env python3
"""
Create equipment_name_aliases table for resolving display names to canonical IDs.

This table helps map human-readable equipment names from scenarios (e.g., "Matilda II")
to database canonical IDs (e.g., "BRI_MATILDA_II").
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def create_aliases_table():
    """Create the equipment_name_aliases table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_name_aliases (
            alias TEXT PRIMARY KEY,
            canonical_id TEXT NOT NULL,
            category TEXT,
            nation TEXT,
            notes TEXT,
            FOREIGN KEY (canonical_id) REFERENCES equipment(canonical_id)
        )
    """)

    print("[OK] Created equipment_name_aliases table")

    # Populate with common aliases from North Africa scenarios
    aliases = [
        # British AFVs
        ("Matilda II", "BRI_MATILDA_II", "tank", "british", "Infantry Tank Mk II"),
        ("Matilda", "BRI_MATILDA_II", "tank", "british", "Short form"),
        ("Crusader", "BRI_CRUSADER_I", "tank", "british", "Cruiser Tank Mk VI"),
        ("Crusader I", "BRI_CRUSADER_I", "tank", "british", None),
        ("Crusader II", "BRI_CRUSADER_II", "tank", "british", None),
        ("Crusader III", "BRI_CRUSADER_III", "tank", "british", None),
        ("Stuart", "USA_M3_STUART", "tank", "american", "M3 Light Tank (British name)"),
        ("Honey", "USA_M3_STUART", "tank", "american", "British nickname for Stuart"),
        ("M3 Stuart", "USA_M3_STUART", "tank", "american", None),
        ("M3 Light", "USA_M3_STUART", "tank", "american", None),
        ("Valentine", "BRI_VALENTINE_II", "tank", "british", "Infantry Tank Mk III"),
        ("Valentine II", "BRI_VALENTINE_II", "tank", "british", None),
        ("Grant", "USA_M3_GRANT", "tank", "american", "M3 Medium (British turret)"),
        ("M3 Grant", "USA_M3_GRANT", "tank", "american", None),
        ("Lee", "USA_M3_LEE", "tank", "american", "M3 Medium (US turret)"),
        ("M3 Lee", "USA_M3_LEE", "tank", "american", None),
        ("Sherman", "USA_M4_SHERMAN", "tank", "american", "M4 Medium Tank"),
        ("M4 Sherman", "USA_M4_SHERMAN", "tank", "american", None),
        ("M4", "USA_M4_SHERMAN", "tank", "american", None),

        # German AFVs
        ("Panzer II", "GER_PANZER_II_F", "tank", "german", "PzKpfw II"),
        ("Pz II", "GER_PANZER_II_F", "tank", "german", None),
        ("PzKpfw II", "GER_PANZER_II_F", "tank", "german", None),
        ("Panzer III", "GER_PANZER_III_H", "tank", "german", "PzKpfw III"),
        ("Pz III", "GER_PANZER_III_H", "tank", "german", None),
        ("PzKpfw III", "GER_PANZER_III_H", "tank", "german", None),
        ("Panzer IV", "GER_PANZER_IV_F2", "tank", "german", "PzKpfw IV"),
        ("Pz IV", "GER_PANZER_IV_F2", "tank", "german", None),
        ("PzKpfw IV", "GER_PANZER_IV_F2", "tank", "german", None),
        ("Panzer IV F2", "GER_PANZER_IV_F2", "tank", "german", "Long 75mm gun"),
        ("StuG III", "GER_STUG_III_F", "tank_destroyer", "german", "Sturmgeschütz III"),
        ("StuG", "GER_STUG_III_F", "tank_destroyer", "german", None),
        ("Marder III", "GER_MARDER_III", "tank_destroyer", "german", None),
        ("SdKfz 222", "GER_SDKFZ_222", "armored_car", "german", "2cm armed car"),
        ("SdKfz 231", "GER_SDKFZ_231_8RAD", "armored_car", "german", "8-wheeled"),
        ("SdKfz 232", "GER_SDKFZ_232_8RAD", "armored_car", "german", "8-wheeled radio"),

        # Italian AFVs
        ("M13/40", "ITA_M13_40", "tank", "italian", None),
        ("M14/41", "ITA_M14_41", "tank", "italian", None),
        ("L6/40", "ITA_L6_40", "tank", "italian", "Light tank"),
        ("Semovente 75/18", "ITA_SEMOVENTE_75_18", "tank_destroyer", "italian", None),
        ("Autoblinda 40", "ITA_AB40", "armored_car", "italian", "AB40"),
        ("Autoblinda 41", "ITA_AB41", "armored_car", "italian", "AB41"),
        ("AB40", "ITA_AB40", "armored_car", "italian", None),
        ("AB41", "ITA_AB41", "armored_car", "italian", None),
    ]

    # Insert aliases (ignore if already exists)
    for alias, canonical_id, category, nation, notes in aliases:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO equipment_name_aliases
                (alias, canonical_id, category, nation, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (alias, canonical_id, category, nation, notes))
        except sqlite3.IntegrityError:
            print(f"  [WARN] Skipped duplicate: {alias}")

    conn.commit()

    # Report
    count = cursor.execute("SELECT COUNT(*) FROM equipment_name_aliases").fetchone()[0]
    print(f"[OK] Populated {count} equipment name aliases")

    # Show sample
    print("\nSample aliases:")
    cursor.execute("SELECT alias, canonical_id FROM equipment_name_aliases LIMIT 10")
    for alias, canonical_id in cursor.fetchall():
        print(f"  {alias} -> {canonical_id}")

    conn.close()
    print(f"\n[OK] Database updated: {DB_PATH}")

if __name__ == "__main__":
    create_aliases_table()
