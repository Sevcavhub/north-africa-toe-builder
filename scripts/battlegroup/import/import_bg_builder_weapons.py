#!/usr/bin/env python3
"""Import BG Builder weapons (241 entries) to database."""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
JSON_PATH = Path(__file__).parent.parent.parent.parent / "sources" / "bg_builder_weapons.json"

def parse_strength_value(val):
    """Convert strength value to integer, handling empty strings."""
    if val == '' or val is None:
        return None
    try:
        return int(val)
    except:
        return None

def import_weapons():
    print("BG Builder Weapons Import")
    print("=" * 80)

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        weapons_dict = json.load(f)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    cursor = conn.cursor()

    imported = 0
    skipped = 0

    for weapon_id, weapon_data in weapons_dict.items():
        weapon_id = int(weapon_id)

        # Skip if no name or placeholder
        if not weapon_data.get('name') or weapon_data.get('name') == 'Placeholder':
            skipped += 1
            continue

        name = weapon_data['name']
        stats = weapon_data.get('stats', [])

        # Parse HE stats
        he_stat = next((s for s in stats if 'HE' in s.get('type', '')), None)
        he_type = he_stat.get('type') if he_stat else None
        he_effect = he_stat.get('effect') if he_stat else None
        he_strength = he_stat.get('strength', []) if he_stat else []

        # Parse AP stats
        ap_stat = next((s for s in stats if s.get('type') == 'AP'), None)
        ap_effect = ap_stat.get('effect') if ap_stat else None
        ap_strength = ap_stat.get('strength', []) if ap_stat else []

        cursor.execute("""
            INSERT INTO bg_builder_weapons
            (weapon_id, weapon_name, he_type, he_effect,
             he_strength_0, he_strength_10, he_strength_20, he_strength_30, he_strength_40, he_strength_50,
             ap_effect, ap_strength_0, ap_strength_10, ap_strength_20, ap_strength_30, ap_strength_40, ap_strength_50)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            weapon_id, name, he_type, he_effect,
            parse_strength_value(he_strength[0] if len(he_strength) > 0 else None),
            parse_strength_value(he_strength[1] if len(he_strength) > 1 else None),
            parse_strength_value(he_strength[2] if len(he_strength) > 2 else None),
            parse_strength_value(he_strength[3] if len(he_strength) > 3 else None),
            parse_strength_value(he_strength[4] if len(he_strength) > 4 else None),
            parse_strength_value(he_strength[5] if len(he_strength) > 5 else None),
            ap_effect,
            parse_strength_value(ap_strength[0] if len(ap_strength) > 0 else None),
            parse_strength_value(ap_strength[1] if len(ap_strength) > 1 else None),
            parse_strength_value(ap_strength[2] if len(ap_strength) > 2 else None),
            parse_strength_value(ap_strength[3] if len(ap_strength) > 3 else None),
            parse_strength_value(ap_strength[4] if len(ap_strength) > 4 else None),
            parse_strength_value(ap_strength[5] if len(ap_strength) > 5 else None)
        ))
        imported += 1

    conn.commit()

    print(f"\nImported: {imported} weapons")
    print(f"Skipped: {skipped} (placeholders)")

    # Sample check
    cursor.execute("SELECT weapon_id, weapon_name, ap_strength_0 FROM bg_builder_weapons WHERE weapon_id = 8")
    sample = cursor.fetchone()
    if sample:
        print(f"\nSample: {sample[1]} (ID {sample[0]})")
        print(f"   AP Strength at 0\": {sample[2]}")

    cursor.execute("SELECT COUNT(*) FROM bg_builder_weapons")
    print(f"\nTotal weapons in database: {cursor.fetchone()[0]}")

    conn.close()

if __name__ == '__main__':
    import_weapons()
