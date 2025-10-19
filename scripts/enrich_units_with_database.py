#!/usr/bin/env python3
"""
Enrich Unit JSON Files with Equipment Database Specifications

Purpose: Add detailed equipment specifications from database to unit JSON files

Input: Unit JSON files with equipment counts (from Phase 6 agents)
Output: Enriched unit JSON files with counts + specifications (armor, guns, crew, production)

This script is CRITICAL for:
- MDBook chapter generation with detailed variant specifications
- Phase 9 scenario generation with complete equipment data
- Historical accuracy with production context
"""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"
UNITS_DIR = PROJECT_ROOT / "data" / "output" / "units"  # Canonical location (Architecture v4.0)
ENRICHED_UNITS_DIR = PROJECT_ROOT / "data" / "output" / "units"  # Write to same canonical location

def normalize_name(name):
    """Normalize equipment name for matching"""
    return re.sub(r'[^a-z0-9]', '', name.lower())

def get_equipment_spec(cursor, equipment_name, nation):
    """
    Get equipment specification from database

    Args:
        cursor: Database cursor
        equipment_name: Equipment name from unit JSON
        nation: Nation code (british, german, italian, french, american)

    Returns:
        dict: Equipment specifications
    """
    # Create canonical ID
    canonical_id = f"{nation.upper()[:3]}_{equipment_name.upper().replace(' ', '_').replace('-', '_')}"
    canonical_id = re.sub(r'[^A-Z0-9_]', '_', canonical_id)

    # Try to find in match_reviews table first
    cursor.execute("""
        SELECT canonical_id, witw_name, reviewer_notes, final_confidence
        FROM match_reviews
        WHERE canonical_id = ? OR LOWER(witw_name) = ?
    """, (canonical_id, equipment_name.lower()))

    match_review = cursor.fetchone()

    if not match_review:
        # Equipment not in match_reviews - return basic info
        return {
            'name': equipment_name,
            'witw_id': canonical_id,
            'specifications': None,
            'source': 'not_matched',
            'confidence': 0
        }

    match_canonical_id, witw_name, notes, confidence = match_review
    notes = notes or ''

    spec = {
        'name': equipment_name,
        'witw_id': match_canonical_id,
        'confidence': confidence or 0,
        'source': 'match_reviews'
    }

    # Determine equipment type from notes and query appropriate table
    normalized_name = normalize_name(equipment_name)

    # Check if it's a gun
    if any(keyword in notes.lower() for keyword in ['gun match', 'gun', 'howitzer', 'artillery', 'pak', 'flak']):
        cursor.execute("""
            SELECT gun_id, name, full_name, caliber_mm, barrel_length,
                   rate_of_fire_rpm, gun_type, history
            FROM guns
            WHERE nation = ? AND (
                LOWER(name) LIKE ? OR
                LOWER(full_name) LIKE ?
            )
            LIMIT 1
        """, (nation, f'%{normalized_name}%', f'%{normalized_name}%'))

        gun = cursor.fetchone()
        if gun:
            spec['specifications'] = {
                'type': 'gun',
                'gun_id': gun[0],
                'full_name': gun[2],
                'caliber_mm': gun[3],
                'barrel_length': gun[4],
                'rate_of_fire_rpm': gun[5],
                'gun_type': gun[6],
                'history': gun[7]
            }
        else:
            spec['specifications'] = {'type': 'gun', 'details': 'See match_reviews notes'}

    # Check if it's an aircraft
    elif any(keyword in notes.lower() for keyword in ['aircraft match', 'aircraft', 'witw id']):
        # Extract WITW ID from notes
        witw_id_match = re.search(r'WITW ID[:\s]+(\d+)', notes, re.IGNORECASE)
        if witw_id_match:
            witw_id = int(witw_id_match.group(1))

            cursor.execute("""
                SELECT aircraft_id, witw_id, name, nation, max_speed, max_altitude,
                       year, month, crew, range, endurance
                FROM aircraft
                WHERE witw_id = ?
            """, (witw_id,))

            aircraft = cursor.fetchone()
            if aircraft:
                spec['witw_id'] = f"WITW_{witw_id}"
                spec['specifications'] = {
                    'type': 'aircraft',
                    'aircraft_id': aircraft[0],
                    'aircraft_name': aircraft[2],
                    'max_speed_mph': aircraft[4],
                    'max_altitude_ft': aircraft[5],
                    'year': aircraft[6],
                    'month': aircraft[7],
                    'crew': aircraft[8],
                    'range_miles': aircraft[9],
                    'endurance_hours': aircraft[10]
                }
            else:
                spec['specifications'] = {'type': 'aircraft', 'witw_id': witw_id, 'details': 'See aircraft database'}
        else:
            spec['specifications'] = {'type': 'aircraft', 'details': 'See match_reviews notes'}

    # Check if it's an AFV
    elif any(keyword in notes.lower() for keyword in ['afv match', 'tank', 'panzer', 'carrier']):
        cursor.execute("""
            SELECT afv_id, name, armor_front_mm, armor_side_mm, armor_rear_mm,
                   armor_turret_front_mm, gun_name, crew, weight_tonnes, speed_kph
            FROM wwiitanks_afv_data
            WHERE nation = ? AND LOWER(name) LIKE ?
            LIMIT 1
        """, (nation, f'%{normalized_name}%'))

        afv = cursor.fetchone()
        if afv:
            spec['specifications'] = {
                'type': 'afv',
                'afv_id': afv[0],
                'armor_mm': {
                    'front': afv[2],
                    'side': afv[3],
                    'rear': afv[4],
                    'turret_front': afv[5]
                },
                'armament': afv[6],
                'crew': afv[7],
                'weight_tonnes': afv[8],
                'speed_kph': afv[9]
            }
        else:
            spec['specifications'] = {'type': 'afv', 'details': 'See match_reviews notes'}

    # Soft-skin vehicle
    elif 'soft-skin' in notes.lower() or 'vehicle' in notes.lower():
        category = 'truck' if 'truck' in notes.lower() else \
                   'motorcycle' if 'motorcycle' in notes.lower() else \
                   'recovery_vehicle' if 'recovery' in notes.lower() else \
                   'transport'
        spec['specifications'] = {
            'type': 'soft_skin',
            'category': category
        }

    else:
        spec['specifications'] = {'type': 'unknown', 'notes': notes[:200]}

    return spec

def enrich_unit_file(unit_file_path, cursor):
    """
    Enrich a single unit JSON file

    Args:
        unit_file_path: Path to unit JSON file
        cursor: Database cursor

    Returns:
        dict: Enriched unit data
    """
    print(f"\nProcessing: {unit_file_path.name}")

    # Read unit JSON
    with open(unit_file_path, 'r', encoding='utf-8') as f:
        unit_data = json.load(f)

    # Extract nation from filename (e.g., german_1941q2_15_panzer_division_toe.json)
    filename = unit_file_path.name
    nation_match = re.match(r'^(british|german|italian|french|american)', filename, re.IGNORECASE)
    if not nation_match:
        print('  [SKIP] Cannot determine nation from filename')
        return None

    nation = nation_match.group(1).lower()
    print(f"  Nation: {nation}")

    # Enrich equipment sections
    enriched_count = 0
    equipment_sections = [
        'tanks',
        'armored_cars',
        'artillery',
        'anti_tank_guns',
        'anti_aircraft_guns',
        'small_arms',
        'mortars',
        'ground_vehicles',
        'aircraft'
    ]

    for section in equipment_sections:
        if section in unit_data and isinstance(unit_data[section], dict):
            enriched_section = {}

            for equipment_name, count in unit_data[section].items():
                # Skip if already enriched (has 'count' property)
                if isinstance(count, dict) and 'count' in count:
                    enriched_section[equipment_name] = count
                    continue

                try:
                    spec = get_equipment_spec(cursor, equipment_name, nation)

                    enriched_section[equipment_name] = {
                        'count': int(count) if isinstance(count, (int, str)) and str(count).isdigit() else count,
                        'witw_id': spec['witw_id'],
                        'specifications': spec['specifications'],
                        'confidence': spec['confidence'],
                        'source': spec['source']
                    }

                    enriched_count += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to enrich {equipment_name}: {e}")
                    enriched_section[equipment_name] = {
                        'count': int(count) if isinstance(count, (int, str)) and str(count).isdigit() else count,
                        'error': str(e)
                    }

            unit_data[section] = enriched_section

    # Add enrichment metadata
    unit_data['_enrichment'] = {
        'enriched_at': datetime.now().isoformat(),
        'enriched_count': enriched_count,
        'source_file': filename,
        'database_version': 'master_database.db',
        'phase': 'phase_5_equipment_matching_complete'
    }

    print(f"  Enriched {enriched_count} equipment items")

    return unit_data

def enrich_all_units():
    """Main enrichment function"""

    # Ensure enriched units directory exists
    ENRICHED_UNITS_DIR.mkdir(parents=True, exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    print('=' * 80)
    print('ENRICHING UNIT JSON FILES WITH DATABASE SPECIFICATIONS')
    print('=' * 80)
    print(f'\nInput directory: {UNITS_DIR}')
    print(f'Output directory: {ENRICHED_UNITS_DIR}\n')

    # Get all unit JSON files
    unit_files = list(UNITS_DIR.glob('*_toe.json'))
    print(f'Found {len(unit_files)} unit files to enrich\n')

    enriched = 0
    skipped = 0
    errors = 0

    for unit_file in unit_files:
        try:
            enriched_unit = enrich_unit_file(unit_file, cursor)

            if enriched_unit:
                output_path = ENRICHED_UNITS_DIR / unit_file.name
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(enriched_unit, f, indent=2, ensure_ascii=False)
                print(f"  [OK] Saved enriched file: {unit_file.name}")
                enriched += 1
            else:
                print(f"  [SKIP] {unit_file.name}")
                skipped += 1
        except Exception as e:
            print(f"  [ERROR] Failed to enrich {unit_file.name}: {e}")
            errors += 1

    conn.close()

    print('\n' + '=' * 80)
    print('ENRICHMENT SUMMARY')
    print('=' * 80)
    print(f'Units enriched: {enriched}')
    print(f'Units skipped: {skipped}')
    print(f'Errors: {errors}')
    print('\n[OK] Unit enrichment complete!')
    print(f'\nEnriched files saved to: {ENRICHED_UNITS_DIR}')
    print('=' * 80)

    return {'enriched': enriched, 'skipped': skipped, 'errors': errors}

if __name__ == '__main__':
    enrich_all_units()
