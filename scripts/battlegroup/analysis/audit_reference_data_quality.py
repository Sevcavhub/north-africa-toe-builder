"""
Comprehensive audit of BattleGroup reference data quality.

This script analyzes ALL available data sources to identify clean, manually-entered
data suitable for reverse-engineering BattleGroup conversion formulas.

Data Sources:
1. bg_reference_vehicles - 191 manually-entered vehicles (Canada's Crucible, British DataCards, Tobruk)
2. bg_builder_vehicles - 602 scraped vehicles (QUALITY UNKNOWN - needs validation)
3. bg_reference_guns - 51 manually-entered guns
4. BG_Reference_ArmyList_Examples - 47 army list units with points/BR
5. wwiitanks_afv_data - 612 AFVs with technical specs (armor mm, speed, weight)
6. wwiitanks_gun_data - Gun penetration data (mm @ distance)

Purpose: Identify which data sources have clean BattleGroup stats for formula building.
"""

import sqlite3
import json
from collections import defaultdict
from datetime import datetime


def audit_database():
    """Comprehensive audit of all BattleGroup-related data."""

    conn = sqlite3.connect('database/master_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    audit_results = {
        'timestamp': datetime.now().isoformat(),
        'tables': {},
        'data_quality_summary': {},
        'recommended_sources': {}
    }

    print("=" * 80)
    print("BATTLEGROUP REFERENCE DATA QUALITY AUDIT")
    print("=" * 80)

    # ========== 1. BG_REFERENCE_VEHICLES (Manual extraction - HIGH QUALITY) ==========
    print("\n1. BG_REFERENCE_VEHICLES (Manual Extraction)")
    print("-" * 80)

    cursor.execute("SELECT COUNT(*) as total FROM bg_reference_vehicles")
    total_ref_vehicles = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as count FROM bg_reference_vehicles WHERE armor_front IS NOT NULL AND armor_front != ''")
    ref_with_armor = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM bg_reference_vehicles WHERE off_road_inches IS NOT NULL")
    ref_with_movement = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM bg_reference_vehicles WHERE weapon_1 IS NOT NULL AND weapon_1 != ''")
    ref_with_weapons = cursor.fetchone()['count']

    cursor.execute("""
        SELECT extraction_method, COUNT(*) as count
        FROM bg_reference_vehicles
        GROUP BY extraction_method
    """)
    extraction_methods = {row['extraction_method']: row['count'] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT nation, COUNT(*) as count
        FROM bg_reference_vehicles
        GROUP BY nation
        ORDER BY count DESC
    """)
    nations = {row['nation']: row['count'] for row in cursor.fetchall()}

    print(f"Total vehicles: {total_ref_vehicles}")
    print(f"  With armor data: {ref_with_armor} ({ref_with_armor/total_ref_vehicles*100:.1f}%)")
    print(f"  With movement data: {ref_with_movement} ({ref_with_movement/total_ref_vehicles*100:.1f}%)")
    print(f"  With weapons: {ref_with_weapons} ({ref_with_weapons/total_ref_vehicles*100:.1f}%)")
    print(f"\nExtraction methods:")
    for method, count in extraction_methods.items():
        print(f"  {method}: {count}")
    print(f"\nNations:")
    for nation, count in nations.items():
        print(f"  {nation}: {count}")

    audit_results['tables']['bg_reference_vehicles'] = {
        'total': total_ref_vehicles,
        'with_armor': ref_with_armor,
        'with_movement': ref_with_movement,
        'with_weapons': ref_with_weapons,
        'extraction_methods': extraction_methods,
        'nations': nations,
        'quality': 'HIGH - Manually entered from official BattleGroup supplements'
    }

    # ========== 2. BG_BUILDER_VEHICLES (Scraped - QUALITY UNKNOWN) ==========
    print("\n2. BG_BUILDER_VEHICLES (Scraped Data - NEEDS VALIDATION)")
    print("-" * 80)

    cursor.execute("SELECT COUNT(*) as total FROM bg_builder_vehicles")
    total_builder = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as count FROM bg_builder_vehicles WHERE armor_front IS NOT NULL AND armor_front != ''")
    builder_with_armor = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM bg_builder_vehicles WHERE movement_off_road IS NOT NULL")
    builder_with_movement = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM bg_builder_vehicles WHERE weapon_1_id IS NOT NULL")
    builder_with_weapons = cursor.fetchone()['count']

    cursor.execute("""
        SELECT import_source, COUNT(*) as count
        FROM bg_builder_vehicles
        GROUP BY import_source
    """)
    import_sources = {row['import_source']: row['count'] for row in cursor.fetchall()}

    print(f"Total vehicles: {total_builder}")
    print(f"  With armor data: {builder_with_armor} ({builder_with_armor/total_builder*100:.1f}%)")
    print(f"  With movement data: {builder_with_movement} ({builder_with_movement/total_builder*100:.1f}%)")
    print(f"  With weapons: {builder_with_weapons} ({builder_with_weapons/total_builder*100:.1f}%)")
    print(f"\nImport sources:")
    for source, count in import_sources.items():
        source_name = source if source else 'NULL'
        print(f"  {source_name}: {count}")

    print("\n[!] QUALITY CONCERNS:")
    print("  - User reported bg_builder data may have OCR errors")
    print("  - Need cross-validation with bg_reference_vehicles to assess quality")
    print("  - Recommend SPOT-CHECKING 10-20 vehicles against source PDFs")

    audit_results['tables']['bg_builder_vehicles'] = {
        'total': total_builder,
        'with_armor': builder_with_armor,
        'with_movement': builder_with_movement,
        'with_weapons': builder_with_weapons,
        'import_sources': import_sources,
        'quality': 'UNKNOWN - Scraped data, OCR errors reported, NEEDS VALIDATION'
    }

    # ========== 3. BG_REFERENCE_GUNS (Manual extraction - HIGH QUALITY) ==========
    print("\n3. BG_REFERENCE_GUNS (Manual Extraction)")
    print("-" * 80)

    cursor.execute("SELECT COUNT(*) as total FROM bg_reference_guns")
    total_guns = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as count FROM bg_reference_guns WHERE he_dice IS NOT NULL")
    guns_with_he = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM bg_reference_guns WHERE ap_0_10 IS NOT NULL")
    guns_with_pen = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM bg_reference_guns WHERE caliber_mm IS NOT NULL")
    guns_with_caliber = cursor.fetchone()['count']

    print(f"Total guns: {total_guns}")
    print(f"  With HE data: {guns_with_he} ({guns_with_he/total_guns*100:.1f}%)")
    print(f"  With penetration data: {guns_with_pen} ({guns_with_pen/total_guns*100:.1f}%)")
    print(f"  With caliber: {guns_with_caliber} ({guns_with_caliber/total_guns*100:.1f}%)")

    # Sample gun data to check quality
    cursor.execute("""
        SELECT name, caliber_mm, he_dice, he_target, ap_0_10, ap_10_20, ap_20_30
        FROM bg_reference_guns
        WHERE he_dice IS NOT NULL AND ap_0_10 IS NOT NULL
        LIMIT 5
    """)
    print("\nSample guns with complete data:")
    for row in cursor.fetchall():
        print(f"  {row['name']}: {row['caliber_mm']}mm, HE {row['he_dice']}/{row['he_target']}, AP {row['ap_0_10']}-{row['ap_10_20']}-{row['ap_20_30']}")

    audit_results['tables']['bg_reference_guns'] = {
        'total': total_guns,
        'with_he': guns_with_he,
        'with_penetration': guns_with_pen,
        'with_caliber': guns_with_caliber,
        'quality': 'HIGH - Manually entered from official BattleGroup supplements'
    }

    # ========== 4. WWIITANKS_AFV_DATA (Technical specs - HIGH QUALITY) ==========
    print("\n4. WWIITANKS_AFV_DATA (Technical Specifications)")
    print("-" * 80)

    cursor.execute("SELECT COUNT(*) as total FROM wwiitanks_afv_data")
    total_wwiitanks = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as count FROM wwiitanks_afv_data WHERE armor_hull_front_mm IS NOT NULL AND armor_hull_front_mm > 0")
    wwiitanks_with_armor = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM wwiitanks_afv_data WHERE speed_kmh IS NOT NULL AND speed_kmh > 0")
    wwiitanks_with_speed = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM wwiitanks_afv_data WHERE weight_tonnes IS NOT NULL AND weight_tonnes > 0")
    wwiitanks_with_weight = cursor.fetchone()['count']

    print(f"Total AFVs: {total_wwiitanks}")
    print(f"  With armor (mm): {wwiitanks_with_armor} ({wwiitanks_with_armor/total_wwiitanks*100:.1f}%)")
    print(f"  With speed: {wwiitanks_with_speed} ({wwiitanks_with_speed/total_wwiitanks*100:.1f}%)")
    print(f"  With weight: {wwiitanks_with_weight} ({wwiitanks_with_weight/total_wwiitanks*100:.1f}%)")

    # Sample data
    cursor.execute("""
        SELECT vehicle_name, armor_hull_front_mm, armor_hull_side_mm, speed_kmh, weight_tonnes
        FROM wwiitanks_afv_data
        WHERE armor_hull_front_mm IS NOT NULL AND armor_hull_front_mm > 0
        LIMIT 5
    """)
    print("\nSample AFVs with complete specs:")
    for row in cursor.fetchall():
        print(f"  {row['vehicle_name']}: {row['armor_hull_front_mm']}mm/{row['armor_hull_side_mm']}mm armor, {row['speed_kmh']}km/h, {row['weight_tonnes']}t")

    audit_results['tables']['wwiitanks_afv_data'] = {
        'total': total_wwiitanks,
        'with_armor': wwiitanks_with_armor,
        'with_speed': wwiitanks_with_speed,
        'with_weight': wwiitanks_with_weight,
        'quality': 'HIGH - Curated military database, no BG stats (used for formula input)'
    }

    # ========== 5. CROSS-VALIDATION: bg_reference vs bg_builder ==========
    print("\n5. CROSS-VALIDATION: Overlapping Vehicles")
    print("-" * 80)

    cursor.execute("""
        SELECT
            r.name as ref_name,
            r.armor_front as ref_armor,
            r.off_road_inches as ref_movement,
            b.name as builder_name,
            b.armor_front as builder_armor,
            b.movement_off_road as builder_movement
        FROM bg_reference_vehicles r
        LEFT JOIN bg_builder_vehicles b ON LOWER(r.name) = LOWER(b.name)
        WHERE b.id IS NOT NULL
        LIMIT 10
    """)

    overlaps = cursor.fetchall()
    print(f"Found {len(overlaps)} overlapping vehicles (first 10):")

    armor_matches = 0
    movement_matches = 0

    for row in overlaps:
        armor_match = row['ref_armor'] == row['builder_armor'] if row['ref_armor'] and row['builder_armor'] else False
        movement_match = row['ref_movement'] == row['builder_movement'] if row['ref_movement'] and row['builder_movement'] else False

        if armor_match:
            armor_matches += 1
        if movement_match:
            movement_matches += 1

        match_indicator = "[OK]" if (armor_match and movement_match) else "[!]"
        print(f"  {match_indicator} {row['ref_name'][:30]:30} | Armor: {row['ref_armor']} vs {row['builder_armor']} | Move: {row['ref_movement']} vs {row['builder_movement']}")

    if len(overlaps) > 0:
        print(f"\nMatch rates (from {len(overlaps)} overlaps):")
        print(f"  Armor matches: {armor_matches}/{len(overlaps)} ({armor_matches/len(overlaps)*100:.1f}%)")
        print(f"  Movement matches: {movement_matches}/{len(overlaps)} ({movement_matches/len(overlaps)*100:.1f}%)")

    # ========== 6. RECOMMENDATIONS ==========
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR FORMULA REVERSE-ENGINEERING")
    print("=" * 80)

    recommendations = []

    # Armor conversion
    armor_data_count = ref_with_armor + wwiitanks_with_armor
    print(f"\n1. ARMOR CONVERSION (mm -> BG letter scale)")
    print(f"   Available data points:")
    print(f"     - bg_reference_vehicles with armor: {ref_with_armor} (BG letter scale)")
    print(f"     - wwiitanks_afv_data with armor: {wwiitanks_with_armor} (mm values)")
    print(f"   Strategy: Match bg_reference armor letters to wwiitanks mm values")
    print(f"   Confidence: {'HIGH' if ref_with_armor >= 100 else 'MEDIUM'} ({ref_with_armor} samples)")
    recommendations.append({
        'formula': 'armor_conversion',
        'primary_source': 'bg_reference_vehicles',
        'cross_reference': 'wwiitanks_afv_data',
        'sample_count': ref_with_armor,
        'confidence': 'HIGH' if ref_with_armor >= 100 else 'MEDIUM'
    })

    # Movement conversion
    print(f"\n2. MOVEMENT CONVERSION (speed/weight -> BG inches)")
    print(f"   Available data points:")
    print(f"     - bg_reference_vehicles with movement: {ref_with_movement} (BG inches)")
    print(f"     - wwiitanks_afv_data with speed/weight: {wwiitanks_with_speed}/{wwiitanks_with_weight}")
    print(f"   Strategy: Correlate bg_reference inches to wwiitanks speed/weight")
    print(f"   Confidence: {'HIGH' if ref_with_movement >= 100 else 'MEDIUM'} ({ref_with_movement} samples)")
    recommendations.append({
        'formula': 'movement_conversion',
        'primary_source': 'bg_reference_vehicles',
        'cross_reference': 'wwiitanks_afv_data',
        'sample_count': ref_with_movement,
        'confidence': 'HIGH' if ref_with_movement >= 100 else 'MEDIUM'
    })

    # HE effectiveness
    print(f"\n3. HE EFFECTIVENESS (caliber -> BG HE dice/target)")
    print(f"   Available data points:")
    print(f"     - bg_reference_guns with HE: {guns_with_he} (BG dice/target format)")
    print(f"   Strategy: Map caliber_mm to he_dice and he_target patterns")
    print(f"   Confidence: {'HIGH' if guns_with_he >= 30 else 'MEDIUM'} ({guns_with_he} samples)")
    recommendations.append({
        'formula': 'he_effectiveness',
        'primary_source': 'bg_reference_guns',
        'cross_reference': None,
        'sample_count': guns_with_he,
        'confidence': 'HIGH' if guns_with_he >= 30 else 'MEDIUM'
    })

    # Penetration conversion
    print(f"\n4. PENETRATION CONVERSION (mm @ distance -> BG scale)")
    print(f"   Available data points:")
    print(f"     - bg_reference_guns with penetration: {guns_with_pen} (BG 1-15 scale)")
    print(f"   Strategy: Map caliber + penetration mm to BG penetration scale")
    print(f"   Confidence: {'MEDIUM' if guns_with_pen >= 20 else 'LOW'} ({guns_with_pen} samples)")
    recommendations.append({
        'formula': 'penetration_conversion',
        'primary_source': 'bg_reference_guns',
        'cross_reference': 'wwiitanks_gun_data or penetration_data',
        'sample_count': guns_with_pen,
        'confidence': 'MEDIUM' if guns_with_pen >= 20 else 'LOW'
    })

    # Points/BR (SKIP for now)
    print(f"\n5. POINTS/BR CALCULATION")
    print(f"   Available data points:")
    print(f"     - BG_Reference_ArmyList_Examples: 47 units (but these are complete units, not individual equipment)")
    print(f"   Strategy: DEFER - Need equipment-level points/BR from army lists")
    print(f"   Confidence: INSUFFICIENT DATA")
    recommendations.append({
        'formula': 'points_br_calculation',
        'primary_source': 'INSUFFICIENT - need equipment-level data',
        'cross_reference': None,
        'sample_count': 0,
        'confidence': 'INSUFFICIENT'
    })

    # bg_builder data quality
    print(f"\n6. BG_BUILDER_VEHICLES DATA QUALITY")
    print(f"   Action Required: SPOT-CHECK 20 vehicles")
    print(f"   Method: Compare bg_builder armor/movement to source PDFs")
    print(f"   Decision: If >90% accurate, use all 602 vehicles; if <90%, use only bg_reference_vehicles")
    print(f"   Impact: Could increase sample size from {total_ref_vehicles} to {total_builder} vehicles")

    audit_results['data_quality_summary'] = {
        'high_quality_sources': [
            'bg_reference_vehicles (191 vehicles, manually entered)',
            'bg_reference_guns (51 guns, manually entered)',
            'wwiitanks_afv_data (612 AFVs, technical specs)'
        ],
        'unknown_quality': [
            'bg_builder_vehicles (602 vehicles, OCR scraped - NEEDS VALIDATION)'
        ],
        'insufficient_data': [
            'Points/BR calculation (no equipment-level data)'
        ]
    }

    audit_results['recommended_sources'] = recommendations

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. IMMEDIATE: Build formulas using bg_reference_vehicles + bg_reference_guns")
    print("   - Armor conversion: 191 samples (HIGH confidence)")
    print("   - Movement conversion: 191 samples (HIGH confidence)")
    print("   - HE effectiveness: 37 samples (MEDIUM-HIGH confidence)")
    print("   - Penetration conversion: 29 samples (MEDIUM confidence)")
    print("\n2. VALIDATION: Spot-check bg_builder_vehicles (20 random vehicles)")
    print("   - If accurate, incorporate 602 additional samples")
    print("   - If inaccurate, discard and use only bg_reference data")
    print("\n3. DEFER: Points/BR calculation until equipment-level data available")

    conn.close()

    # Save audit results to JSON
    with open('analysis/data_quality_audit_results.json', 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"\n[SAVED] Audit results saved to: analysis/data_quality_audit_results.json")

    return audit_results


if __name__ == '__main__':
    audit_database()
