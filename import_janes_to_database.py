#!/usr/bin/env python3
"""
Import Jane's Guide Ammunition Data to bg_reference_vehicles Database

Strategy:
1. Load Jane's ammunition JSON
2. Match to bg_reference_vehicles by name
3. Update ammo_1 field (main gun ammunition)
4. Report matches and misses
"""

import json
import sqlite3
from pathlib import Path
from difflib import SequenceMatcher

JANES_JSON = Path("janes_ammunition_v2.json")
DATABASE_PATH = Path("database/master_database.db")


def normalize_name(name):
    """Normalize vehicle name for matching."""
    import re
    name = name.lower()
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()

    replacements = {
        'mark ': 'mk ',
        ' tank': '',
        ' light': '',
        ' medium': '',
        ' heavy': '',
        ' infantry': '',
        ' cruiser': '',
        'pzkw ': 'panzer ',
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    return name


def similarity_ratio(str1, str2):
    """Calculate similarity ratio."""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def main():
    """Main execution."""

    print("=" * 80)
    print("IMPORT JANE'S AMMUNITION DATA TO DATABASE")
    print("=" * 80)

    # Load Jane's data
    print(f"\nLoading: {JANES_JSON}")
    with open(JANES_JSON, 'r') as f:
        janes_data = json.load(f)

    # Filter obvious non-vehicles
    filtered = []
    for entry in janes_data:
        name = entry['vehicle_name']
        if any(x in name.lower() for x in ['carried', 'ammunition', 'rounds for', 'jane', 'world war', 'gun-howitzer with']):
            continue
        if len(name) < 5:
            continue
        filtered.append(entry)

    print(f"Loaded {len(janes_data)} entries, filtered to {len(filtered)} likely vehicles")

    # Load database vehicles
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('SELECT id, name, ammo_1 FROM bg_reference_vehicles ORDER BY name')
    db_vehicles = {row['id']: {'name': row['name'], 'ammo_1': row['ammo_1']} for row in cur.fetchall()}

    print(f"Database has {len(db_vehicles)} vehicles")

    # Match Jane's data to database
    print("\n" + "=" * 80)
    print("MATCHING")
    print("=" * 80)

    matches = []
    no_matches = []

    for janes_entry in filtered:
        janes_name = janes_entry['vehicle_name']
        ammo_count = janes_entry['ammunition_count']

        # Find best match
        best_match = None
        best_score = 0.6

        for db_id, db_data in db_vehicles.items():
            score = similarity_ratio(normalize_name(janes_name), normalize_name(db_data['name']))

            if score > best_score:
                best_score = score
                best_match = (db_id, db_data['name'], db_data['ammo_1'], score)

        if best_match:
            db_id, db_name, current_ammo, score = best_match
            matches.append({
                'janes_name': janes_name,
                'db_id': db_id,
                'db_name': db_name,
                'current_ammo': current_ammo,
                'new_ammo': ammo_count,
                'score': score
            })
        else:
            no_matches.append({'janes_name': janes_name, 'ammo': ammo_count})

    print(f"\nMatched: {len(matches)} vehicles")
    print(f"No match: {len(no_matches)} vehicles")

    # Display matches
    if matches:
        print(f"\nTop 30 matches:\n")
        print(f"{'Jane\\'s Name':40} | {'DB Name':30} | {'Curr':>4} | {'New':>4} | {'Score':>5}")
        print("-" * 95)

        for match in sorted(matches, key=lambda x: x['score'], reverse=True)[:30]:
            curr = match['current_ammo'] if match['current_ammo'] else '-'
            print(f"{match['janes_name'][:40]:40} | {match['db_name'][:30]:30} | "
                  f"{str(curr):>4} | {match['new_ammo']:>4} | {match['score']*100:5.1f}%")

        if len(matches) > 30:
            print(f"\n... and {len(matches) - 30} more")

    # Ask confirmation
    print(f"\n" + "=" * 80)
    print("IMPORT")
    print("=" * 80)

    proceed = input(f"\nImport {len(matches)} ammunition values? (y/n): ")

    if proceed.lower() != 'y':
        print("Cancelled.")
        conn.close()
        return

    # Import
    updates = 0
    skipped = 0

    for match in matches:
        if match['current_ammo'] is None or match['current_ammo'] == '':
            cur.execute('UPDATE bg_reference_vehicles SET ammo_1 = ? WHERE id = ?',
                       (match['new_ammo'], match['db_id']))
            updates += 1
            print(f"  Updated: {match['db_name']} -> ammo_1 = {match['new_ammo']}")
        else:
            skipped += 1

    conn.commit()
    conn.close()

    print(f"\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"\nUpdated: {updates} vehicles")
    print(f"Skipped: {skipped} (already had ammo)")
    print(f"No match: {len(no_matches)} vehicles\n")

    if no_matches:
        print("No matches for:")
        for item in no_matches[:10]:
            print(f"  - {item['janes_name']} ({item['ammo']} rounds)")
        if len(no_matches) > 10:
            print(f"  ... and {len(no_matches) - 10} more")


if __name__ == "__main__":
    main()
