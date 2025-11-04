#!/usr/bin/env python3
"""
Phase 5.5 - Phase 3: Equipment Matcher v3 (Name Variants Edition)
Uses equipment_name_variants table for fuzzy matching to achieve 85%+ linkage

Strategy:
1. For each equipment in equipment_master_new
2. Get all name variants from equipment_name_variants_new
3. Match variants against bg_reference_vehicles, wwiitanks_afv_data, afv_data
4. Enrich historical_specs_json with matched data
5. Update confidence scores based on match quality

Data Sources:
- bg_reference_vehicles (500 vehicles) - BattleGroup scraped data
- wwiitanks_afv_data (612 vehicles) - WWIItanks detailed specs
- afv_data (213 vehicles) - OnWar production data
- equipment_name_variants_new (2,189 variants) - Fuzzy matching keys

Target: 85%+ of 1,620 equipment items have 2+ source enrichment
"""

import sqlite3
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent.parent / "database" / "master_database.db"

# Configuration
DRY_RUN = False  # Set True to preview without modifying database
VERBOSE = False  # Set False to suppress per-match output

def connect_db():
    """Connect to SQLite database"""
    return sqlite3.connect(str(DB_PATH))

def get_equipment_with_variants(conn) -> List[Dict]:
    """Get all equipment with their name variants"""
    query = """
    SELECT
        em.master_id,
        em.canonical_name,
        em.display_name,
        em.equipment_category,
        em.original_nation,
        em.historical_specs_json,
        GROUP_CONCAT(env.variant_name, '|||') as variant_names
    FROM equipment_master_new em
    LEFT JOIN equipment_name_variants_new env ON em.master_id = env.master_id
    GROUP BY em.master_id
    ORDER BY em.master_id
    """

    cursor = conn.execute(query)
    results = []

    for row in cursor:
        master_id, canonical, display, category, nation, specs_json, variant_str = row

        # Parse variants
        variants = set()
        if variant_str:
            variants = set(variant_str.split('|||'))

        # Add display name and canonical name as variants
        if display:
            variants.add(display)
        if canonical:
            # Remove eq_123_ prefix if present
            clean_canonical = canonical
            if canonical.startswith('eq_') and '_' in canonical:
                parts = canonical.split('_', 2)
                if len(parts) == 3:
                    clean_canonical = parts[2].replace('_', ' ').title()
            variants.add(clean_canonical)

        # Parse existing specs
        specs = {}
        if specs_json:
            try:
                specs = json.loads(specs_json)
            except:
                pass

        results.append({
            'master_id': master_id,
            'canonical_name': canonical,
            'display_name': display,
            'category': category,
            'nation': nation,
            'variants': list(variants),
            'specs': specs
        })

    return results

def match_bg_reference_vehicles(conn, equipment: Dict) -> Optional[Dict]:
    """Match equipment to bg_reference_vehicles using variants"""
    # Try each variant
    for variant in equipment['variants']:
        # Case-insensitive match
        query = """
        SELECT id, name, nation, armor_front, armor_side, armor_rear,
               off_road_inches, road_inches, weapons,
               points_cost, battle_rating, special_rules
        FROM bg_reference_vehicles
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
        """

        cursor = conn.execute(query, (variant,))
        row = cursor.fetchone()

        if row:
            id, name, nation, armor_f, armor_s, armor_r, move_off, move_road, \
            weapons, pts, br, rules = row

            return {
                'source': 'bg_reference_vehicles',
                'id': id,
                'name': name,
                'nation': nation,
                'armor_front': armor_f,
                'armor_side': armor_s,
                'armor_rear': armor_r,
                'off_road_inches': move_off,
                'road_inches': move_road,
                'weapons': weapons,
                'points_cost': pts,
                'battle_rating': br,
                'special_rules': rules,
                'match_variant': variant,
                'confidence': 90  # High confidence for name match
            }

    return None

def match_wwiitanks(conn, equipment: Dict) -> Optional[Dict]:
    """Match equipment to wwiitanks_afv_data using variants"""
    for variant in equipment['variants']:
        query = """
        SELECT vehicle_name, country
        FROM wwiitanks_afv_data
        WHERE LOWER(TRIM(vehicle_name)) = LOWER(TRIM(?))
        OR LOWER(TRIM(full_name)) = LOWER(TRIM(?))
        LIMIT 1
        """

        cursor = conn.execute(query, (variant, variant))
        row = cursor.fetchone()

        if row:
            return {
                'source': 'wwiitanks',
                'vehicle_name': row[0],
                'country': row[1],
                'match_variant': variant,
                'confidence': 85  # Good confidence for WWIItanks match
            }

    return None

def match_onwar(conn, equipment: Dict) -> Optional[Dict]:
    """Match equipment to afv_data (OnWar) using variants"""
    for variant in equipment['variants']:
        query = """
        SELECT vehicle_name, country
        FROM afv_data
        WHERE LOWER(TRIM(vehicle_name)) = LOWER(TRIM(?))
        OR LOWER(TRIM(formal_designation)) = LOWER(TRIM(?))
        LIMIT 1
        """

        cursor = conn.execute(query, (variant, variant))
        row = cursor.fetchone()

        if row:
            return {
                'source': 'onwar',
                'vehicle_name': row[0],
                'country': row[1],
                'match_variant': variant,
                'confidence': 80  # Reasonable confidence for OnWar
            }

    return None

def merge_specs(existing: Dict, new_data: Dict, source: str) -> Dict:
    """Merge new data into existing specs without overwriting"""
    merged = existing.copy()

    # Add source-specific fields
    for key, value in new_data.items():
        if key in ['source', 'match_variant', 'confidence']:
            continue  # Skip metadata

        # Create source-prefixed key
        source_key = f"{source}_{key}"

        # Only add if not already present
        if source_key not in merged and value is not None:
            merged[source_key] = value

    # Track sources
    if 'data_sources' not in merged:
        merged['data_sources'] = []

    if source not in merged['data_sources']:
        merged['data_sources'].append(source)

    # Update confidence score (average of all sources)
    if 'source_confidences' not in merged:
        merged['source_confidences'] = {}

    merged['source_confidences'][source] = new_data.get('confidence', 75)

    return merged

def calculate_overall_confidence(specs: Dict) -> float:
    """Calculate overall confidence score based on source count and quality"""
    if 'source_confidences' not in specs:
        return 0.0

    confidences = list(specs['source_confidences'].values())
    if not confidences:
        return 0.0

    # Average confidence, weighted by number of sources
    avg = sum(confidences) / len(confidences)
    source_count = len(specs.get('data_sources', []))

    # Bonus for multiple sources (max +10 points)
    bonus = min(source_count * 3, 10)

    return min(avg + bonus, 100.0)

def main():
    """Main execution"""
    print("=" * 80)
    print("Phase 5.5 - Phase 3: Equipment Matcher v3 (Name Variants)")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (preview only)' if DRY_RUN else 'REAL (database will be modified)'}")
    print()

    # Connect to database
    conn = connect_db()

    # Get all equipment with variants
    print("Step 1: Loading equipment with name variants...")
    equipment_list = get_equipment_with_variants(conn)
    print(f"  Loaded: {len(equipment_list)} equipment items")

    # Match statistics
    stats = {
        'total_equipment': len(equipment_list),
        'bg_matched': 0,
        'wwiitanks_matched': 0,
        'onwar_matched': 0,
        'multi_source': 0,  # 2+ sources
        'single_source': 0,  # 1 source
        'no_match': 0,  # 0 sources
        'enriched': 0,  # historical_specs_json updated
    }

    print("\nStep 2: Matching against reference databases...")

    updates = []

    for eq in equipment_list:
        master_id = eq['master_id']
        specs = eq['specs'].copy()

        matched_sources = []

        # Try BG reference match
        bg_match = match_bg_reference_vehicles(conn, eq)
        if bg_match:
            specs = merge_specs(specs, bg_match, 'bg_reference_vehicles')
            matched_sources.append('bg_reference_vehicles')
            stats['bg_matched'] += 1

            if VERBOSE:
                print(f"  [BG] master_id {master_id}: {eq['display_name']} -> {bg_match.get('name', 'N/A')}")

        # Try WWIItanks match
        wwiitanks_match = match_wwiitanks(conn, eq)
        if wwiitanks_match:
            specs = merge_specs(specs, wwiitanks_match, 'wwiitanks')
            matched_sources.append('wwiitanks')
            stats['wwiitanks_matched'] += 1

            if VERBOSE:
                print(f"  [WWIITANKS] master_id {master_id}: {eq['display_name']} -> {wwiitanks_match.get('vehicle_name', 'N/A')}")

        # Try OnWar match
        onwar_match = match_onwar(conn, eq)
        if onwar_match:
            specs = merge_specs(specs, onwar_match, 'onwar')
            matched_sources.append('onwar')
            stats['onwar_matched'] += 1

            if VERBOSE:
                print(f"  [ONWAR] master_id {master_id}: {eq['display_name']} -> {onwar_match.get('vehicle_name', 'N/A')}")

        # Update statistics
        source_count = len(matched_sources)
        if source_count == 0:
            stats['no_match'] += 1
        elif source_count == 1:
            stats['single_source'] += 1
        else:
            stats['multi_source'] += 1

        # If any matches, prepare update
        if source_count > 0:
            stats['enriched'] += 1

            # Calculate overall confidence
            confidence = calculate_overall_confidence(specs)

            updates.append({
                'master_id': master_id,
                'specs_json': json.dumps(specs, indent=2),
                'confidence': confidence,
                'sources': matched_sources
            })

    # Apply updates
    print(f"\nStep 3: Updating equipment_master_new...")

    if not DRY_RUN:
        cursor = conn.cursor()
        update_count = 0

        for update in updates:
            try:
                cursor.execute(
                    "UPDATE equipment_master_new SET historical_specs_json = ?, confidence_score = ?, updated_at = CURRENT_TIMESTAMP WHERE master_id = ?",
                    (update['specs_json'], update['confidence'], update['master_id'])
                )
                update_count += 1
            except Exception as e:
                print(f"  Error updating master_id {update['master_id']}: {e}")

        conn.commit()
        print(f"  Updated: {update_count} equipment items")
    else:
        print(f"  [DRY RUN] Would update: {len(updates)} equipment items")

    # Summary
    print("\n" + "=" * 80)
    print("MATCHING SUMMARY")
    print("=" * 80)
    print(f"Total equipment:           {stats['total_equipment']}")
    print(f"BG reference matched:      {stats['bg_matched']} ({stats['bg_matched']/stats['total_equipment']*100:.1f}%)")
    print(f"WWIItanks matched:         {stats['wwiitanks_matched']} ({stats['wwiitanks_matched']/stats['total_equipment']*100:.1f}%)")
    print(f"OnWar matched:             {stats['onwar_matched']} ({stats['onwar_matched']/stats['total_equipment']*100:.1f}%)")
    print()
    print(f"Multi-source (2+):         {stats['multi_source']} ({stats['multi_source']/stats['total_equipment']*100:.1f}%)")
    print(f"Single source (1):         {stats['single_source']} ({stats['single_source']/stats['total_equipment']*100:.1f}%)")
    print(f"No match (0):              {stats['no_match']} ({stats['no_match']/stats['total_equipment']*100:.1f}%)")
    print()
    print(f"Total enriched:            {stats['enriched']} ({stats['enriched']/stats['total_equipment']*100:.1f}%)")

    # Validation
    enrichment_pct = (stats['enriched'] / stats['total_equipment']) * 100
    multi_source_pct = (stats['multi_source'] / stats['total_equipment']) * 100

    if multi_source_pct >= 85:
        print("\n[SUCCESS] Target achieved: 85%+ multi-source enrichment")
    elif enrichment_pct >= 85:
        print(f"\n[PARTIAL SUCCESS] 85%+ total enrichment, but only {multi_source_pct:.1f}% multi-source")
    else:
        print(f"\n[WARNING] Only {enrichment_pct:.1f}% enrichment (target: 85%+)")

    conn.close()
    print("\n[COMPLETE] Equipment matching finished")

if __name__ == "__main__":
    main()
