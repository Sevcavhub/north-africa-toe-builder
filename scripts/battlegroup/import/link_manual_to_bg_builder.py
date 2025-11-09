#!/usr/bin/env python3
"""
Link manual bg_reference_vehicles to BG Builder via fuzzy name matching.
Adds bg_builder_id column to track linkage.
"""
import sqlite3
from pathlib import Path
from difflib import SequenceMatcher

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"

def similarity(a, b):
    """Calculate string similarity (0-1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_name(name):
    """Normalize vehicle name for better matching."""
    if not name:
        return ""
    name = name.lower()
    # Common substitutions
    name = name.replace("pzkpfw", "panzer")
    name = name.replace("pz.kpfw.", "panzer")
    name = name.replace("mk ", "mk")
    name = name.replace("mark ", "mk")
    return name.strip()

def link_manual_data():
    print("Linking Manual bg_reference_vehicles to BG Builder")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if bg_reference_vehicles table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='bg_reference_vehicles'
    """)
    if not cursor.fetchone():
        print("\nNo bg_reference_vehicles table found - nothing to link")
        print("This is OK if you haven't done manual extractions yet")
        conn.close()
        return

    # Add column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE bg_reference_vehicles ADD COLUMN bg_builder_id INTEGER")
        print("\nAdded bg_builder_id column to bg_reference_vehicles")
    except:
        print("\nbg_builder_id column already exists")

    # Get all BG Builder vehicles
    cursor.execute("SELECT id, name FROM bg_builder_vehicles ORDER BY name")
    bg_vehicles = cursor.fetchall()
    print(f"Loaded {len(bg_vehicles)} BG Builder vehicles")

    # Get all manual vehicles
    cursor.execute("SELECT id, name FROM bg_reference_vehicles")
    manual_vehicles = cursor.fetchall()
    print(f"Loaded {len(manual_vehicles)} manual vehicles")

    if len(manual_vehicles) == 0:
        print("\nNo manual vehicles to link - skipping")
        conn.close()
        return

    # Match vehicles
    print("\nMatching vehicles...")
    matches = []
    exact_matches = 0
    fuzzy_matches = 0
    no_matches = 0

    for manual in manual_vehicles:
        best_match = None
        best_score = 0.0
        match_type = None

        manual_norm = normalize_name(manual['name'])

        for bg in bg_vehicles:
            bg_norm = normalize_name(bg['name'])

            # Check for exact match first
            if manual_norm == bg_norm:
                best_score = 1.0
                best_match = bg
                match_type = 'exact'
                break

            # Otherwise use fuzzy matching
            score = similarity(manual_norm, bg_norm)
            if score > best_score:
                best_score = score
                best_match = bg
                match_type = 'fuzzy'

        if best_score >= 0.85:  # 85% similarity threshold
            cursor.execute("""
                UPDATE bg_reference_vehicles
                SET bg_builder_id = ?
                WHERE id = ?
            """, (best_match['id'], manual['id']))

            matches.append({
                'manual_id': manual['id'],
                'manual_name': manual['name'],
                'bg_id': best_match['id'],
                'bg_name': best_match['name'],
                'score': best_score,
                'type': match_type
            })

            if match_type == 'exact':
                exact_matches += 1
            else:
                fuzzy_matches += 1

            if best_score < 0.95:  # Show fuzzy matches for review
                print(f"   [{best_score:.2f}] {manual['name']:40s} -> {best_match['name']}")
        else:
            no_matches += 1
            print(f"   [NO MATCH] {manual['name']}")

    conn.commit()

    # Summary
    print("\n" + "=" * 80)
    print("LINKAGE COMPLETE")
    print("=" * 80)
    print(f"\nTotal manual vehicles:  {len(manual_vehicles)}")
    print(f"Exact matches:          {exact_matches}")
    print(f"Fuzzy matches (85%+):   {fuzzy_matches}")
    print(f"No matches (<85%):      {no_matches}")
    print(f"Total linked:           {exact_matches + fuzzy_matches}")
    print(f"Linkage rate:           {100 * (exact_matches + fuzzy_matches) / len(manual_vehicles):.1f}%")

    # Verify linkage
    cursor.execute("""
        SELECT COUNT(*) FROM bg_reference_vehicles
        WHERE bg_builder_id IS NOT NULL
    """)
    linked_count = cursor.fetchone()[0]
    print(f"\nVerified linked count:  {linked_count}")

    conn.close()

if __name__ == '__main__':
    link_manual_data()
