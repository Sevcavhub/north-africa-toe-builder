#!/usr/bin/env python3
"""
Create bg_weapon_name_lookup table to map weapon names
from bg_reference_vehicles to bg_builder_weapons
"""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "database" / "master_database.db"

def create_weapon_lookup():
    """Create weapon name lookup table and populate with automatic matches."""

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create lookup table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bg_weapon_name_lookup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bg_reference_name TEXT NOT NULL UNIQUE,
            bg_builder_weapon_id INTEGER,
            match_confidence TEXT,
            notes TEXT,
            FOREIGN KEY (bg_builder_weapon_id) REFERENCES bg_builder_weapons(weapon_id)
        )
    """)

    print("Created bg_weapon_name_lookup table")

    # Get all unique weapons from bg_reference_vehicles
    cursor.execute("""
        SELECT DISTINCT weapon_1 as weapon FROM bg_reference_vehicles WHERE weapon_1 IS NOT NULL
        UNION
        SELECT DISTINCT weapon_2 FROM bg_reference_vehicles WHERE weapon_2 IS NOT NULL
        UNION
        SELECT DISTINCT weapon_3 FROM bg_reference_vehicles WHERE weapon_3 IS NOT NULL
        UNION
        SELECT DISTINCT weapon_4 FROM bg_reference_vehicles WHERE weapon_4 IS NOT NULL
    """)

    ref_weapons = [row['weapon'] for row in cursor.fetchall()]

    # Get all bg_builder_weapons
    cursor.execute('SELECT weapon_id, weapon_name FROM bg_builder_weapons')
    builder_weapons = {row['weapon_name']: row['weapon_id'] for row in cursor.fetchall()}

    print(f"\nProcessing {len(ref_weapons)} unique weapons from bg_reference_vehicles")
    print(f"Matching against {len(builder_weapons)} weapons in bg_builder_weapons\n")

    exact_matches = 0
    normalized_matches = 0
    no_matches = 0

    for ref_weapon in ref_weapons:
        weapon_id = None
        confidence = None

        # Try exact match
        if ref_weapon in builder_weapons:
            weapon_id = builder_weapons[ref_weapon]
            confidence = 'exact'
            exact_matches += 1
        else:
            # Try normalized match (case-insensitive, space/punctuation variations)
            ref_normalized = ref_weapon.lower().replace(' ', '').replace('-', '').replace('_', '')

            for builder_name, builder_id in builder_weapons.items():
                builder_normalized = builder_name.lower().replace(' ', '').replace('-', '').replace('_', '')
                if ref_normalized == builder_normalized:
                    weapon_id = builder_id
                    confidence = 'normalized'
                    normalized_matches += 1
                    break

        if weapon_id is None:
            confidence = 'no_match'
            no_matches += 1

        # Insert into lookup table
        cursor.execute("""
            INSERT OR IGNORE INTO bg_weapon_name_lookup
            (bg_reference_name, bg_builder_weapon_id, match_confidence)
            VALUES (?, ?, ?)
        """, (ref_weapon, weapon_id, confidence))

    conn.commit()

    print(f"Results:")
    print(f"  Exact matches:      {exact_matches}")
    print(f"  Normalized matches: {normalized_matches}")
    print(f"  No matches:         {no_matches}")
    print(f"  Total:              {len(ref_weapons)}")
    print(f"  Coverage:           {100*(exact_matches+normalized_matches)//len(ref_weapons)}%")

    # Show unmatched weapons
    cursor.execute("""
        SELECT bg_reference_name
        FROM bg_weapon_name_lookup
        WHERE match_confidence = 'no_match'
        ORDER BY bg_reference_name
    """)

    unmatched = [row['bg_reference_name'] for row in cursor.fetchall()]

    if unmatched:
        print(f"\nUnmatched weapons ({len(unmatched)}):")
        for weapon in unmatched[:20]:
            print(f"  - {weapon}")
        if len(unmatched) > 20:
            print(f"  ... and {len(unmatched)-20} more")

    conn.close()
    print(f"\nLookup table created: {DATABASE_PATH}")

if __name__ == "__main__":
    create_weapon_lookup()
