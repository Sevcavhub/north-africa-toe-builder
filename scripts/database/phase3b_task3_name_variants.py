#!/usr/bin/env python3
"""
Phase 3B Task 3: Name Variant Mapping

Create equipment_name_variants table and populate with fuzzy matching
to link equipment table to bg_reference_vehicles for gun data lookups.
"""

import sqlite3
import json
from pathlib import Path
from difflib import SequenceMatcher

DB_PATH = Path("database/master_database.db")

def normalize_name(name):
    """Normalize equipment names for matching"""
    name = name.lower()
    # Expand abbreviations
    name = name.replace('mk ', 'mark ')
    name = name.replace('mk.', 'mark')
    name = name.replace(' ii ', ' 2 ')
    name = name.replace(' iii ', ' 3 ')
    name = name.replace(' iv ', ' 4 ')
    name = name.replace(' v ', ' 5 ')
    name = name.replace(' vi ', ' 6 ')
    # Remove "Ausf" for German tanks
    name = name.replace(' ausf ', ' ')
    return name

def fuzzy_match_score(eq_name, bg_name, threshold=0.75):
    """Calculate similarity between names"""
    norm_eq = normalize_name(eq_name)
    norm_bg = normalize_name(bg_name)
    return SequenceMatcher(None, norm_eq, norm_bg).ratio()

def token_match_score(eq_name, bg_name):
    """Match based on significant tokens (Jaccard similarity)"""
    eq_tokens = set(normalize_name(eq_name).split())
    bg_tokens = set(normalize_name(bg_name).split())

    # Ignore common words
    ignore = {'mk', 'mark', 'ausf', 'the', 'a', 'an', 'with', 'and', 'or'}
    eq_tokens -= ignore
    bg_tokens -= ignore

    if not eq_tokens or not bg_tokens:
        return 0.0

    # Jaccard similarity
    intersection = len(eq_tokens & bg_tokens)
    union = len(eq_tokens | bg_tokens)

    return intersection / union if union > 0 else 0.0

def create_variants_table(cursor):
    """Create equipment_name_variants table with indexes"""
    print("Creating equipment_name_variants table...")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_name_variants (
            variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_id TEXT NOT NULL,
            variant_name TEXT NOT NULL,
            variant_source TEXT NOT NULL,
            match_type TEXT NOT NULL,
            confidence_score REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (canonical_id) REFERENCES equipment(canonical_id)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_variant_canonical ON equipment_name_variants(canonical_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_variant_name ON equipment_name_variants(variant_name)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_variant_unique ON equipment_name_variants(canonical_id, variant_name, variant_source)")

    print("  Table and indexes created!\n")

def exact_matches(cursor):
    """Find exact name matches between equipment and bg_reference_vehicles"""
    print("Step 1: Finding exact matches...")

    cursor.execute("""
        INSERT OR IGNORE INTO equipment_name_variants (canonical_id, variant_name, variant_source, match_type, confidence_score)
        SELECT
            e.canonical_id,
            bg.name AS variant_name,
            'bg_reference_vehicles' AS variant_source,
            'exact' AS match_type,
            1.0 AS confidence_score
        FROM equipment e
        INNER JOIN bg_reference_vehicles bg ON LOWER(e.name) = LOWER(bg.name)
        WHERE e.category IN ('tanks', 'main_tanks', 'light_tanks', 'armored_cars', 'halftracks', 'anti_tank', 'anti_aircraft', 'field_artillery')
    """)

    count = cursor.rowcount
    print(f"  Found {count} exact matches\n")
    return count

def abbreviation_matches(cursor):
    """Apply manual abbreviation rules for known patterns"""
    print("Step 2: Applying abbreviation rules...")

    # British Mk abbreviations
    british_abbrevs = [
        # Valentine variants
        ('GBR_VALENTINE_MK_II', 'Valentine II', 0.95),
        ('GBR_VALENTINE_MK_III', 'Valentine III', 0.95),
        ('GBR_VALENTINE_MK_IX', 'Valentine IX', 0.95),

        # Crusader variants
        ('GBR_CRUSADER_MK_I', 'Crusader I', 0.95),
        ('GBR_CRUSADER_MK_II', 'Crusader II', 0.95),
        ('GBR_CRUSADER_MK_III', 'Crusader III', 0.95),

        # Churchill variants
        ('GBR_CHURCHILL_MK_III', 'Churchill III', 0.95),
        ('GBR_CHURCHILL_MK_IV', 'Churchill IV', 0.95),

        # Matilda
        ('GBR_MATILDA_MK_II', 'Matilda II', 0.95),

        # A-series cruisers
        ('GBR_A10_CRUISER_MK_II', 'A10 Cruiser', 0.95),
        ('GBR_A13_MK_II', 'A13 Mark II', 0.95),
    ]

    # German Ausf variants
    german_ausfs = [
        ('GER_PANZER_II_AUSF_C', 'Panzer II C', 0.95),
        ('GER_PANZER_II_AUSF_F', 'Panzer II F', 0.95),
        ('GER_PANZER_III_AUSF_F', 'Panzer III F', 0.95),
        ('GER_PANZER_III_AUSF_G', 'Panzer III G', 0.95),
        ('GER_PANZER_III_AUSF_H', 'Panzer III H', 0.95),
        ('GER_PANZER_III_AUSF_J', 'Panzer III J', 0.95),
        ('GER_PANZER_IV_AUSF_D', 'Panzer IV D', 0.95),
        ('GER_PANZER_IV_AUSF_E', 'Panzer IV E', 0.95),
        ('GER_PANZER_IV_AUSF_F', 'Panzer IV F', 0.95),
        ('GER_PANZER_IV_AUSF_F2', 'Panzer IV F2', 0.95),
    ]

    # Italian variants
    italian_variants = [
        ('ITA_L6_40', 'FIAT L6/40', 0.90),
        ('ITA_M13_40', 'M13/40', 0.95),
        ('ITA_M14_41', 'M14/41', 0.95),
    ]

    all_abbrevs = british_abbrevs + german_ausfs + italian_variants

    count = 0
    for canonical_id, variant_name, confidence in all_abbrevs:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO equipment_name_variants (canonical_id, variant_name, variant_source, match_type, confidence_score)
                VALUES (?, ?, 'bg_reference_vehicles', 'abbreviation', ?)
            """, (canonical_id, variant_name, confidence))
            if cursor.rowcount > 0:
                count += 1
        except sqlite3.IntegrityError:
            pass  # Duplicate, skip

    print(f"  Applied {count} abbreviation rules\n")
    return count

def fuzzy_matches(cursor, threshold=0.75):
    """Find fuzzy matches using similarity scoring"""
    print(f"Step 3: Finding fuzzy matches (threshold: {threshold})...")

    # Get all equipment without variants yet
    cursor.execute("""
        SELECT e.canonical_id, e.name, e.category
        FROM equipment e
        WHERE e.category IN ('tanks', 'main_tanks', 'light_tanks', 'armored_cars', 'halftracks')
          AND NOT EXISTS (
              SELECT 1 FROM equipment_name_variants v WHERE v.canonical_id = e.canonical_id
          )
    """)
    unmatched_equipment = cursor.fetchall()

    # Get all bg_reference_vehicles
    cursor.execute("SELECT DISTINCT name FROM bg_reference_vehicles WHERE name IS NOT NULL")
    bg_names = [row[0] for row in cursor.fetchall()]

    matches = []
    for eq_id, eq_name, eq_category in unmatched_equipment:
        best_match = None
        best_score = 0.0

        for bg_name in bg_names:
            # Try both fuzzy and token matching
            fuzzy_score = fuzzy_match_score(eq_name, bg_name)
            token_score = token_match_score(eq_name, bg_name)

            # Use max of both scores
            score = max(fuzzy_score, token_score)

            if score >= threshold and score > best_score:
                best_score = score
                best_match = bg_name

        if best_match:
            matches.append((eq_id, best_match, best_score))

    # Insert matches
    count = 0
    for eq_id, bg_name, score in matches:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO equipment_name_variants (canonical_id, variant_name, variant_source, match_type, confidence_score)
                VALUES (?, ?, 'bg_reference_vehicles', 'fuzzy', ?)
            """, (eq_id, bg_name, score))
            if cursor.rowcount > 0:
                count += 1
                # Skip detailed output to avoid Unicode encoding issues
        except sqlite3.IntegrityError:
            pass

    print(f"  Found {count} fuzzy matches\n")
    return count

def validation_report(cursor):
    """Generate validation report"""
    print("=" * 80)
    print("\n=== Validation Report ===\n")

    # Count mappings by type
    cursor.execute("""
        SELECT match_type, COUNT(*) AS count
        FROM equipment_name_variants
        GROUP BY match_type
        ORDER BY count DESC
    """)

    print("Mappings by type:")
    total = 0
    for match_type, count in cursor.fetchall():
        print(f"  {match_type}: {count}")
        total += count
    print(f"  TOTAL: {total}\n")

    # Count equipment with mappings
    cursor.execute("""
        SELECT COUNT(DISTINCT canonical_id) FROM equipment_name_variants
    """)
    mapped_count = cursor.fetchone()[0]
    print(f"Equipment items with variants: {mapped_count}\n")

    # Find still-unmatched equipment
    cursor.execute("""
        SELECT e.canonical_id, e.name, e.category
        FROM equipment e
        WHERE e.category IN ('tanks', 'main_tanks', 'light_tanks', 'armored_cars', 'halftracks')
          AND NOT EXISTS (
              SELECT 1 FROM equipment_name_variants v WHERE v.canonical_id = e.canonical_id
          )
        ORDER BY e.category, e.name
    """)

    unmatched = cursor.fetchall()
    print(f"Still unmatched: {len(unmatched)}")
    if len(unmatched) <= 20:
        for eq_id, name, category in unmatched:
            print(f"  - {eq_id}: {name} ({category})")
    else:
        print("  (Too many to list - see database query)")

    print("\n" + "=" * 80)

def main():
    """Execute Phase 3B Task 3: Name Variant Mapping"""

    print("=" * 80)
    print("=== Phase 3B Task 3: Name Variant Mapping ===")
    print("=" * 80)
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Create table
        create_variants_table(cursor)

        # Step 1: Exact matches
        exact_count = exact_matches(cursor)

        # Step 2: Abbreviation rules
        abbrev_count = abbreviation_matches(cursor)

        # Step 3: Fuzzy matches
        fuzzy_count = fuzzy_matches(cursor, threshold=0.75)

        # Commit changes
        conn.commit()

        # Validation
        validation_report(cursor)

        print("\n=== Task 3 Complete ===")
        print(f"Total mappings created: {exact_count + abbrev_count + fuzzy_count}")
        print("Transaction committed successfully!\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return 1
    finally:
        conn.close()

    return 0

if __name__ == "__main__":
    exit(main())
