#!/usr/bin/env python3
"""
Add 5 missing guns to database (identified during Phase 5 Equipment Matching)

Guns to add:
1. British: BL 7.2-inch Howitzer (183mm)
2. German: 7.5cm leIG 18 (light infantry gun)
3. German: 17cm Kanone 18 (heavy artillery)
4. Italian: Obice da 100/17 Modello 14/16 (captured Škoda 10cm)
5. Italian: Obice da 149/13 Modello 14/16 (captured Škoda 15cm)
"""

import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"

# Missing guns with complete specifications
missing_guns = [
    {
        'gun_id': 'BL_7.2_INCH_HOWITZER',
        'name': 'BL 7.2-inch Howitzer',
        'full_name': 'Ordnance BL 7.2-inch Howitzer',
        'nation': 'British',
        'caliber_mm': 183,  # 7.2 inches
        'barrel_length': '33 calibers (Mk 6)',
        'rate_of_fire_rpm': None,
        'manufactured_start': 1940,
        'manufactured_end': 1945,
        'gun_type': 'heavy_howitzer',
        'wwiitanks_id': None,
        'source_url': 'https://nigelef.tripod.com/72inchsheet.htm',
        'scraper_version': 'manual_research_v1',
        'history': 'British heavy howitzer created by re-lining 8-inch howitzer barrels. Caliber 7.2 inches (183mm). Marks I-IV range 16,900 yd (15,500m), Mark 6 range 19,600 yd (17,900m). Shell weight 200 lb. Muzzle velocity 1,700 fps. Used extensively in North Africa and European theater.',
        'notes': 'Added during Phase 5 Equipment Matching. Not found in WWIITANKS database (focus on tank/AT guns). Research from nigelef.tripod.com and multiple sources. Confidence: 95%'
    },
    {
        'gun_id': '7.5CM_LEIG_18',
        'name': '7.5cm leIG 18',
        'full_name': '7.5cm leichtes Infanteriegeschütz 18',
        'nation': 'German',
        'caliber_mm': 75,
        'barrel_length': 'L/13',
        'rate_of_fire_rpm': 10,  # 8-12 rpm
        'manufactured_start': 1939,
        'manufactured_end': 1945,
        'gun_type': 'light_infantry_gun',
        'wwiitanks_id': None,
        'source_url': 'https://www.militaryfactory.com/armor/detail.php?armor_id=674',
        'scraper_version': 'manual_research_v1',
        'history': 'German light infantry gun developed by Rheinmetall-Borsig 1927, adopted by Reichswehr 1932. Most-built German artillery except 10.5cm leFH 18. Weight 400kg (combat), 1,560kg (travel). Range 4,000m. Shell weight 12 lb (5.5-6kg). Elevation -10° to +73°, traverse ±12°. Crew 5. Production: 9,037-12,000 units (1939-1945). Variants: le.GebIG 18 (mountain gun), le.IG 18F (airborne gun).',
        'notes': 'Added during Phase 5 Equipment Matching. Infantry support weapon for both direct and indirect fire. Armored shield for crew protection. Research from MilitaryFactory and Wikipedia. Confidence: 95%'
    },
    {
        'gun_id': '17CM_KANONE_18',
        'name': '17cm Kanone 18',
        'full_name': '17cm Kanone 18',
        'nation': 'German',
        'caliber_mm': 172.5,  # Actually 172.5mm, often listed as 173mm
        'barrel_length': 'L/50',
        'rate_of_fire_rpm': 1.5,  # 1-2 rpm
        'manufactured_start': 1941,
        'manufactured_end': 1945,
        'gun_type': 'heavy_field_gun',
        'wwiitanks_id': None,
        'source_url': 'https://www.militaryfactory.com/armor/detail.php?armor_id=520',
        'scraper_version': 'manual_research_v1',
        'history': 'German heavy artillery gun designed by Krupp, entered service 1941. Caliber 172.5mm (6.79 inches). Weight 17,510 kg (38,602 lb). Shell weight 68 kg (149.9 lb). Muzzle velocity 925 m/s (3,035 ft/sec). Range 29,600m (32,382 yards / 18.4 miles). Elevation 0° to +50°, traverse 360° (dual-recoil carriage). Innovation: "Double recoil" / dual-recoil carriage system. Used for long-range counter-battery fire at corps level.',
        'notes': 'Added during Phase 5 Equipment Matching. One of heaviest German guns, corps-level asset. Not in WWIITANKS database (focus on tank/AT guns). Research from MilitaryFactory and multiple sources. Confidence: 95%'
    },
    {
        'gun_id': 'OBICE_DA_100_17_M14',
        'name': 'Obice da 100/17 Mod. 14',
        'full_name': 'Obice da 100/17 Modello 14/16',
        'nation': 'Italian',
        'caliber_mm': 100,
        'barrel_length': 'L/14',
        'rate_of_fire_rpm': 10,
        'manufactured_start': 1914,
        'manufactured_end': 1918,
        'gun_type': 'field_howitzer',
        'wwiitanks_id': None,
        'source_url': 'https://en.wikipedia.org/wiki/10_cm_M._14_Feldhaubitze',
        'scraper_version': 'manual_research_v1',
        'history': 'Italian designation for captured/war reparation Austro-Hungarian Škoda 10 cm M. 14 Feldhaubitze. 1,222 captured during WWI + 1,472 war reparations = 2,694 total. Weight 1,417kg (battery position). Range 8,180m (upgraded to ~9,000m with 1932 projectile). Muzzle velocity 430 m/s (HE rounds). Elevation -8° to +48°, traverse 5°21′. Dual-purpose field and mountain gun - can be broken down into 3 parts for mule transport. Still in service WWII.',
        'notes': 'Added during Phase 5 Equipment Matching. WWI-era Škoda design captured by Italy. Not in WWIITANKS database (WWI origin, not tank gun). Research from Wikipedia and multiple sources. Confidence: 95%'
    },
    {
        'gun_id': 'OBICE_DA_149_13_M14',
        'name': 'Obice da 149/13 Mod. 14',
        'full_name': 'Obice da 149/13 Modello 14/16',
        'nation': 'Italian',
        'caliber_mm': 149.1,
        'barrel_length': 'L/14 (M14), L/14.1 (M14/16)',
        'rate_of_fire_rpm': 1.5,  # 1-2 rpm
        'manufactured_start': 1914,
        'manufactured_end': 1918,
        'gun_type': 'heavy_howitzer',
        'wwiitanks_id': None,
        'source_url': 'https://en.wikipedia.org/wiki/15_cm_schwere_Feldhaubitze_M_14',
        'scraper_version': 'manual_research_v1',
        'history': 'Italian designation for captured/war reparation Austro-Hungarian Škoda 15 cm schwere Feldhaubitze M 14/M 14/16. Shell weight 41kg. Weight M 14: 2,344kg / M 14/16: 2,765kg. Barrel length M 14: 2.09m (L/14) / M 14/16: 2.12m (L/14.1). Range M 14: 6,900m / M 14/16: 8,760m. Muzzle velocity M 14: 300 m/s / M 14/16: 336 m/s. Elevation M 14: -5° to +43° / M 14/16: -5° to +70°. Traverse M 14: 5° / M 14/16: 6°. 490 on hand 1939. Heavy divisional/corps howitzer.',
        'notes': 'Added during Phase 5 Equipment Matching. WWI-era Škoda design captured by Italy. Not in WWIITANKS database (WWI origin, heavy howitzer). Research from Wikipedia and multiple sources. Confidence: 95%'
    }
]

def add_missing_guns():
    """Add missing guns to database"""

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    print('=' * 80)
    print('ADDING MISSING GUNS TO DATABASE')
    print('=' * 80)
    print(f'\nAdding {len(missing_guns)} guns identified during Phase 5 Equipment Matching...\n')

    added = 0
    skipped = 0
    errors = 0

    for gun in missing_guns:
        # Check if gun already exists
        cursor.execute('SELECT gun_id FROM guns WHERE gun_id = ?', (gun['gun_id'],))
        existing = cursor.fetchone()

        if existing:
            print(f"[SKIP] {gun['name']} ({gun['gun_id']}) - already exists")
            skipped += 1
        else:
            try:
                cursor.execute("""
                    INSERT INTO guns (
                        gun_id, name, full_name, nation, caliber_mm, barrel_length,
                        rate_of_fire_rpm, manufactured_start, manufactured_end,
                        gun_type, wwiitanks_id, source_url, scraped_at,
                        scraper_version, history, notes,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    gun['gun_id'],
                    gun['name'],
                    gun['full_name'],
                    gun['nation'],
                    gun['caliber_mm'],
                    gun['barrel_length'],
                    gun['rate_of_fire_rpm'],
                    gun['manufactured_start'],
                    gun['manufactured_end'],
                    gun['gun_type'],
                    gun['wwiitanks_id'],
                    gun['source_url'],
                    datetime.now().isoformat(),
                    gun['scraper_version'],
                    gun['history'],
                    gun['notes'],
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))

                print(f"[OK] Added {gun['name']} ({gun['gun_id']})")
                print(f"     Nation: {gun['nation']}, Caliber: {gun['caliber_mm']}mm, Type: {gun['gun_type']}")
                added += 1
            except sqlite3.Error as e:
                print(f"[ERROR] Failed to add {gun['name']}: {e}")
                errors += 1

    conn.commit()
    conn.close()

    print('\n' + '=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Guns added: {added}')
    print(f'Guns skipped (already exist): {skipped}')
    print(f'Errors: {errors}')
    print('\n[OK] Missing guns added to database!')
    print('=' * 80)

    return {'added': added, 'skipped': skipped, 'errors': errors}

if __name__ == '__main__':
    add_missing_guns()
