"""
Phase C: Populate Name Variants to 100% Coverage

Extracts names from all source tables and links to equipment_master_new.
Target: 4,000-5,000 variants covering 100% of 1,129 masters.
"""

import sqlite3
import re
from typing import Dict, List, Tuple, Set


def normalize_name(name: str) -> str:
    """Normalize name for matching."""
    name = name.lower()
    name = name.replace(' ', '_')
    name = re.sub(r'\(([^)]+)\)', r'_\1_', name)
    name = re.sub(r'[^a-z0-9_\-]', '', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name


def extract_names_from_tables(conn: sqlite3.Connection):
    """Extract all unique names from source tables."""
    cursor = conn.cursor()

    all_names = {}  # {normalized_name: [(original_name, source, count)]}

    print("Extracting names from source tables...")
    print()

    # Source 1: bg_reference_vehicles
    cursor.execute("SELECT DISTINCT name FROM bg_reference_vehicles WHERE name IS NOT NULL")
    bg_names = [row[0] for row in cursor.fetchall()]
    print(f"  bg_reference_vehicles: {len(bg_names)} unique names")

    for name in bg_names:
        norm = normalize_name(name)
        if norm not in all_names:
            all_names[norm] = []
        all_names[norm].append((name, 'bg_pdf', 1))

    # Source 2: wwiitanks_afv_data
    cursor.execute("SELECT DISTINCT vehicle_name FROM wwiitanks_afv_data WHERE vehicle_name IS NOT NULL")
    wwiitanks_names = [row[0] for row in cursor.fetchall()]
    print(f"  wwiitanks_afv_data: {len(wwiitanks_names)} unique names")

    for name in wwiitanks_names:
        norm = normalize_name(name)
        if norm not in all_names:
            all_names[norm] = []
        all_names[norm].append((name, 'wwiitanks', 1))

    # Source 3: wwiitanks_gun_data
    cursor.execute("SELECT DISTINCT gun_name FROM wwiitanks_gun_data WHERE gun_name IS NOT NULL")
    wwiitanks_gun_names = [row[0] for row in cursor.fetchall()]
    print(f"  wwiitanks_gun_data: {len(wwiitanks_gun_names)} unique names")

    for name in wwiitanks_gun_names:
        norm = normalize_name(name)
        if norm not in all_names:
            all_names[norm] = []
        all_names[norm].append((name, 'wwiitanks', 1))

    # Source 4: afv_data (OnWar)
    cursor.execute("SELECT DISTINCT vehicle_name FROM afv_data WHERE vehicle_name IS NOT NULL")
    onwar_names = [row[0] for row in cursor.fetchall()]
    print(f"  afv_data (OnWar): {len(onwar_names)} unique names")

    for name in onwar_names:
        norm = normalize_name(name)
        if norm not in all_names:
            all_names[norm] = []
        all_names[norm].append((name, 'onwar', 1))

    # Source 5: equipment (Phase 5 baseline)
    cursor.execute("SELECT DISTINCT name FROM equipment WHERE name IS NOT NULL")
    eq_names = [row[0] for row in cursor.fetchall()]
    print(f"  equipment: {len(eq_names)} unique names")

    for name in eq_names:
        norm = normalize_name(name)
        if norm not in all_names:
            all_names[norm] = []
        all_names[norm].append((name, 'witw', 1))

    print()
    print(f"Total unique normalized names: {len(all_names)}")
    print(f"Total name variants to process: {sum(len(v) for v in all_names.values())}")
    print()

    return all_names


def match_to_masters(conn: sqlite3.Connection, all_names: Dict):
    """Match normalized names to equipment_master_new records."""
    cursor = conn.cursor()

    # Get all masters
    cursor.execute("SELECT master_id, canonical_name, display_name FROM equipment_master_new")
    masters = {}  # {normalized_canonical: master_id}

    for master_id, canonical, display in cursor.fetchall():
        norm = normalize_name(canonical)
        masters[norm] = master_id

    print(f"Equipment masters to match against: {len(masters)}")
    print()

    # Match names to masters
    matches = []  # [(master_id, variant_name, source)]
    unmatched = []

    for norm_name, variants in all_names.items():
        if norm_name in masters:
            master_id = masters[norm_name]
            for original_name, source, _ in variants:
                matches.append((master_id, original_name, source))
        else:
            unmatched.extend([(name, src) for name, src, _ in variants])

    print(f"Matching results:")
    print(f"  Matched: {len(matches)} variants")
    print(f"  Unmatched: {len(unmatched)} variants")
    print()

    # Calculate coverage
    masters_with_variants = len(set(m[0] for m in matches))
    total_masters = len(masters)
    coverage_pct = 100 * masters_with_variants / total_masters if total_masters > 0 else 0

    print(f"Coverage:")
    print(f"  Masters with variants: {masters_with_variants} / {total_masters} ({coverage_pct:.1f}%)")
    print()

    return matches, unmatched


def insert_variants(conn: sqlite3.Connection, matches: List[Tuple], dry_run=True):
    """Insert name variants into equipment_name_variants_new."""
    cursor = conn.cursor()

    # Check existing variants
    cursor.execute("SELECT COUNT(*) FROM equipment_name_variants_new")
    existing_count = cursor.fetchone()[0]

    print(f"Existing variants: {existing_count}")
    print(f"New variants to insert: {len(matches)}")
    print()

    if not dry_run:
        # Get existing variants to avoid duplicates
        cursor.execute("SELECT variant_name FROM equipment_name_variants_new")
        existing_variants = {row[0] for row in cursor.fetchall()}

        inserted = 0
        duplicates = 0

        for master_id, variant_name, source in matches:
            if variant_name in existing_variants:
                duplicates += 1
                continue

            cursor.execute("""
                INSERT INTO equipment_name_variants_new
                (master_id, variant_name, variant_source, is_official)
                VALUES (?, ?, ?, 0)
            """, (master_id, variant_name, source))

            inserted += 1
            existing_variants.add(variant_name)

        conn.commit()

        print(f"[OK] Inserted {inserted} new variants")
        print(f"[INFO] Skipped {duplicates} duplicates")
        print()

        # Final verification
        cursor.execute("SELECT COUNT(*) FROM equipment_name_variants_new")
        final_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT master_id) FROM equipment_name_variants_new")
        masters_covered = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM equipment_master_new")
        total_masters = cursor.fetchone()[0]

        coverage_pct = 100 * masters_covered / total_masters if total_masters > 0 else 0

        print(f"Final state:")
        print(f"  Total variants: {final_count}")
        print(f"  Masters covered: {masters_covered} / {total_masters} ({coverage_pct:.1f}%)")
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Populate name variants to 100% coverage")
    parser.add_argument('--db', default='database/master_database.db', help='Path to SQLite database')
    parser.add_argument('--execute', action='store_true', help='Apply changes (default: dry run)')

    args = parser.parse_args()

    conn = sqlite3.connect(args.db)

    print("=" * 100)
    print("PHASE C: POPULATE NAME VARIANTS")
    print("=" * 100)
    print()

    # Step 1: Extract names from all tables
    all_names = extract_names_from_tables(conn)

    # Step 2: Match to masters
    matches, unmatched = match_to_masters(conn, all_names)

    # Step 3: Insert variants
    insert_variants(conn, matches, dry_run=not args.execute)

    if not args.execute:
        print("DRY RUN - No changes applied. Run with --execute to apply changes.")
    else:
        print("[OK] Phase C complete - name variants populated")

    print()
    conn.close()


if __name__ == '__main__':
    main()
