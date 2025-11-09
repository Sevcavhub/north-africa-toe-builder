#!/usr/bin/env python3
"""
Create manual linkage interface between bg_reference_vehicles and bg_builder_vehicles
- Generates CSV with side-by-side comparison
- User reviews and approves/corrects linkages
- Imports approved linkages back to database
"""
import sqlite3
import csv
from pathlib import Path
from difflib import SequenceMatcher

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
OUTPUT_CSV = Path(__file__).parent.parent.parent.parent / "manual_vehicle_linkage_review.csv"

def normalize_name(name):
    """Normalize vehicle names for comparison"""
    if not name:
        return ""

    name = name.lower().strip()

    # Common normalizations
    replacements = {
        'pzkpfw': 'panzer',
        'sdkfz': 'sdkfz',
        'mk ': 'mk',
        'mark ': 'mk',
        'sturmgeschutz': 'stug',
        'stug.': 'stug',
        'ausf.': 'ausf',
        'ausf ': 'ausf',
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    # Remove extra whitespace
    name = ' '.join(name.split())

    return name

def find_candidates(manual_name, bg_vehicles, top_n=5):
    """Find top N candidate matches from BG Builder"""
    manual_normalized = normalize_name(manual_name)

    candidates = []
    for bg_id, bg_name in bg_vehicles:
        bg_normalized = normalize_name(bg_name)
        similarity = SequenceMatcher(None, manual_normalized, bg_normalized).ratio()
        candidates.append((bg_id, bg_name, similarity))

    # Sort by similarity descending
    candidates.sort(key=lambda x: x[2], reverse=True)

    return candidates[:top_n]

def create_linkage_interface():
    print("Creating Manual Linkage Interface")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all BG Builder vehicles
    cursor.execute("SELECT id, name FROM bg_builder_vehicles ORDER BY name")
    bg_vehicles = [(row['id'], row['name']) for row in cursor.fetchall()]
    print(f"Loaded {len(bg_vehicles)} BG Builder vehicles")

    # Get all manual vehicles (both linked and unlinked)
    cursor.execute("""
        SELECT
            id,
            name,
            bg_builder_id,
            armor_front,
            armor_side,
            armor_rear,
            off_road_inches,
            road_inches,
            weapon_1,
            year_range,
            nation,
            source_battle
        FROM bg_reference_vehicles
        ORDER BY name
    """)
    manual_vehicles = cursor.fetchall()
    print(f"Loaded {len(manual_vehicles)} manual vehicles")

    # Create CSV for review
    print(f"\nGenerating linkage review CSV: {OUTPUT_CSV}")

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Headers
        writer.writerow([
            'manual_id',
            'manual_name',
            'manual_armor_f_s_r',
            'manual_movement',
            'manual_weapon1',
            'manual_nation',
            'manual_source',
            'CURRENT_bg_builder_id',
            'CURRENT_bg_name',
            'SUGGESTED_bg_id_1',
            'SUGGESTED_bg_name_1',
            'similarity_1',
            'SUGGESTED_bg_id_2',
            'SUGGESTED_bg_name_2',
            'similarity_2',
            'SUGGESTED_bg_id_3',
            'SUGGESTED_bg_name_3',
            'similarity_3',
            'APPROVED_bg_id',
            'NOTES'
        ])

        for manual in manual_vehicles:
            # Get current linkage if exists
            current_bg_id = manual['bg_builder_id']
            current_bg_name = ""
            if current_bg_id:
                cursor.execute("SELECT name FROM bg_builder_vehicles WHERE id = ?", (current_bg_id,))
                result = cursor.fetchone()
                if result:
                    current_bg_name = result['name']

            # Find top 3 candidates
            candidates = find_candidates(manual['name'], bg_vehicles, top_n=3)

            # Format armor and movement
            armor = f"{manual['armor_front'] or '?'}/{manual['armor_side'] or '?'}/{manual['armor_rear'] or '?'}"
            movement = f"{manual['off_road_inches'] or '?'}\"/{ manual['road_inches'] or '?'}\""

            # Write row
            row = [
                manual['id'],
                manual['name'],
                armor,
                movement,
                manual['weapon_1'] or '',
                manual['nation'] or '',
                manual['source_battle'] or '',
                current_bg_id or '',
                current_bg_name,
            ]

            # Add top 3 candidates
            for i in range(3):
                if i < len(candidates):
                    bg_id, bg_name, similarity = candidates[i]
                    row.extend([bg_id, bg_name, f"{similarity:.2%}"])
                else:
                    row.extend(['', '', ''])

            # Add empty fields for user approval
            row.extend(['', ''])  # APPROVED_bg_id, NOTES

            writer.writerow(row)

    conn.close()

    print("\n" + "=" * 80)
    print("LINKAGE INTERFACE CREATED")
    print("=" * 80)
    print(f"\nGenerated: {OUTPUT_CSV}")
    print(f"Total vehicles to review: {len(manual_vehicles)}")
    print("\nINSTRUCTIONS:")
    print("1. Open manual_vehicle_linkage_review.csv in Excel")
    print("2. Review each row:")
    print("   - Check CURRENT linkage (if exists)")
    print("   - Review SUGGESTED matches (with similarity %)")
    print("   - Choose best match and enter bg_id in APPROVED_bg_id column")
    print("   - Add notes if needed (e.g., 'No match found', 'Variant mismatch')")
    print("3. Save the CSV")
    print("4. Run import_manual_linkages.py to apply approved linkages")
    print("\nNOTE: Blank APPROVED_bg_id = no linkage (manual-only vehicle)")

if __name__ == '__main__':
    create_linkage_interface()
