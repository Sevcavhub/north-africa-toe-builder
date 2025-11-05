#!/usr/bin/env node
/**
 * Enrich Unit JSON Files with Equipment Database Specifications
 *
 * Purpose: Add detailed equipment specifications from database to unit JSON files
 *
 * Input: Unit JSON files with equipment counts (from Phase 6 agents)
 * Output: Enriched unit JSON files with counts + specifications (armor, guns, crew, production)
 *
 * This script is CRITICAL for:
 * - MDBook chapter generation with detailed variant specifications
 * - Phase 9 scenario generation with complete equipment data
 * - Historical accuracy with production context
 */

const sqlite3 = require('sqlite3').verbose();
const fs = require('fs').promises;
const path = require('path');

const DATABASE_FILE = path.join(__dirname, '..', 'database', 'master_database.db');
const UNITS_DIR = path.join(__dirname, '..', 'data', 'output', 'units');
const ENRICHED_UNITS_DIR = path.join(__dirname, '..', 'data', 'output', 'units_enriched');

/**
 * Get equipment specification from database
 * @param {sqlite3.Database} db - Database connection
 * @param {string} equipmentName - Equipment name from unit JSON
 * @param {string} nation - Nation code (british, german, italian, french, american)
 * @returns {Promise<Object>} Equipment specifications
 */
async function getEquipmentSpec(db, equipmentName, nation) {
    return new Promise((resolve, reject) => {
        // Normalize equipment name for matching
        const normalizedName = equipmentName.toLowerCase().replace(/[^a-z0-9]/g, '');

        // Try to find in match_reviews table first (has WITW canonical_id)
        const canonicalId = `${nation.toUpperCase().slice(0, 3)}_${equipmentName.toUpperCase().replace(/[^A-Z0-9]/g, '_')}`;

        db.get(`
            SELECT
                canonical_id,
                witw_name,
                reviewer_notes,
                final_confidence
            FROM match_reviews
            WHERE canonical_id = ? OR LOWER(witw_name) = ?
        `, [canonicalId, equipmentName.toLowerCase()], (err, matchReview) => {
            if (err) {
                reject(err);
                return;
            }

            if (!matchReview) {
                // Equipment not in match_reviews - return basic info
                resolve({
                    name: equipmentName,
                    witw_id: canonicalId,
                    specifications: null,
                    source: 'not_matched',
                    confidence: 0
                });
                return;
            }

            // Parse match_reviews notes to determine equipment type and database ID
            const notes = matchReview.reviewer_notes || '';
            const spec = {
                name: equipmentName,
                witw_id: canonicalId,
                confidence: matchReview.final_confidence || 0,
                source: 'match_reviews'
            };

            // Check if it's a gun
            if (notes.includes('Gun match') || notes.includes('gun') || notes.includes('howitzer') || notes.includes('artillery')) {
                // Extract gun details from notes or query guns table
                db.get(`
                    SELECT
                        gun_id,
                        name,
                        full_name,
                        caliber_mm,
                        barrel_length,
                        rate_of_fire_rpm,
                        gun_type,
                        history
                    FROM guns
                    WHERE nation = ? AND (
                        LOWER(name) LIKE ? OR
                        LOWER(full_name) LIKE ?
                    )
                    LIMIT 1
                `, [nation, `%${normalizedName}%`, `%${normalizedName}%`], (err, gun) => {
                    if (gun) {
                        spec.specifications = {
                            type: 'gun',
                            caliber_mm: gun.caliber_mm,
                            barrel_length: gun.barrel_length,
                            rate_of_fire_rpm: gun.rate_of_fire_rpm,
                            gun_type: gun.gun_type,
                            history: gun.history
                        };
                    }
                    resolve(spec);
                });
            }
            // Check if it's an aircraft
            else if (notes.includes('Aircraft match') || notes.includes('aircraft') || notes.includes('WITW ID:')) {
                // Extract WITW ID from notes
                const witwIdMatch = notes.match(/WITW ID[:\s]+(\d+)/i);
                if (witwIdMatch) {
                    const witwId = parseInt(witwIdMatch[1]);

                    db.get(`
                        SELECT
                            aircraft_id,
                            witw_id,
                            name,
                            nation as aircraft_nation,
                            max_speed,
                            max_altitude,
                            year,
                            month,
                            crew,
                            range,
                            endurance
                        FROM aircraft
                        WHERE witw_id = ?
                    `, [witwId], (err, aircraft) => {
                        if (aircraft) {
                            spec.witw_id = `WITW_${witwId}`;
                            spec.specifications = {
                                type: 'aircraft',
                                max_speed_mph: aircraft.max_speed,
                                max_altitude_ft: aircraft.max_altitude,
                                year: aircraft.year,
                                month: aircraft.month,
                                crew: aircraft.crew,
                                range_miles: aircraft.range,
                                endurance_hours: aircraft.endurance
                            };
                        }
                        resolve(spec);
                    });
                } else {
                    resolve(spec);
                }
            }
            // Check if it's an AFV
            else if (notes.includes('AFV match') || notes.includes('tank') || notes.includes('vehicle')) {
                // Try to find in wwiitanks_afv_data or afv_data
                db.get(`
                    SELECT
                        afv_id,
                        name,
                        armor_front_mm,
                        armor_side_mm,
                        armor_rear_mm,
                        armor_turret_front_mm,
                        gun_name,
                        crew,
                        weight_tonnes,
                        speed_kph
                    FROM wwiitanks_afv_data
                    WHERE nation = ? AND (
                        LOWER(name) LIKE ?
                    )
                    LIMIT 1
                `, [nation, `%${normalizedName}%`], (err, afv) => {
                    if (afv) {
                        spec.specifications = {
                            type: 'afv',
                            armor_mm: {
                                front: afv.armor_front_mm,
                                side: afv.armor_side_mm,
                                rear: afv.armor_rear_mm,
                                turret_front: afv.armor_turret_front_mm
                            },
                            armament: afv.gun_name,
                            crew: afv.crew,
                            weight_tonnes: afv.weight_tonnes,
                            speed_kph: afv.speed_kph
                        };
                    }
                    resolve(spec);
                });
            }
            // Soft-skin vehicle
            else {
                spec.specifications = {
                    type: 'soft_skin',
                    category: notes.includes('truck') ? 'truck' :
                              notes.includes('motorcycle') ? 'motorcycle' :
                              notes.includes('recovery') ? 'recovery_vehicle' :
                              'transport'
                };
                resolve(spec);
            }
        });
    });
}

/**
 * Enrich a single unit JSON file
 * @param {string} unitFilePath - Path to unit JSON file
 * @param {sqlite3.Database} db - Database connection
 */
async function enrichUnitFile(unitFilePath, db) {
    console.log(`\nProcessing: ${path.basename(unitFilePath)}`);

    // Read unit JSON
    const unitData = JSON.parse(await fs.readFile(unitFilePath, 'utf-8'));

    // Extract nation from filename (e.g., german_1941q2_15_panzer_division_toe.json)
    const filename = path.basename(unitFilePath);
    const nationMatch = filename.match(/^(british|german|italian|french|american)/i);
    if (!nationMatch) {
        console.log('  [SKIP] Cannot determine nation from filename');
        return null;
    }
    const nation = nationMatch[1].toLowerCase();

    console.log(`  Nation: ${nation}`);

    // Enrich equipment sections
    let enrichedCount = 0;
    const equipmentSections = [
        'tanks',
        'armored_cars',
        'artillery',
        'anti_tank_guns',
        'anti_aircraft_guns',
        'small_arms',
        'mortars',
        'ground_vehicles',
        'aircraft'
    ];

    for (const section of equipmentSections) {
        if (unitData[section] && typeof unitData[section] === 'object') {
            const enrichedSection = {};

            for (const [equipmentName, count] of Object.entries(unitData[section])) {
                // Skip if already enriched (has 'count' property)
                if (typeof count === 'object' && count.count !== undefined) {
                    enrichedSection[equipmentName] = count;
                    continue;
                }

                try {
                    const spec = await getEquipmentSpec(db, equipmentName, nation);

                    enrichedSection[equipmentName] = {
                        count: typeof count === 'number' ? count : parseInt(count) || 0,
                        witw_id: spec.witw_id,
                        specifications: spec.specifications,
                        confidence: spec.confidence,
                        source: spec.source
                    };

                    enrichedCount++;
                } catch (err) {
                    console.error(`  [ERROR] Failed to enrich ${equipmentName}:`, err.message);
                    enrichedSection[equipmentName] = {
                        count: typeof count === 'number' ? count : parseInt(count) || 0,
                        error: err.message
                    };
                }
            }

            unitData[section] = enrichedSection;
        }
    }

    // Add enrichment metadata
    unitData._enrichment = {
        enriched_at: new Date().toISOString(),
        enriched_count: enrichedCount,
        source_file: path.basename(unitFilePath),
        database_version: 'master_database.db',
        phase: 'phase_5_equipment_matching_complete'
    };

    console.log(`  Enriched ${enrichedCount} equipment items`);

    return unitData;
}

/**
 * Main enrichment function
 */
async function enrichAllUnits() {
    return new Promise(async (resolve, reject) => {
        // Ensure enriched units directory exists
        await fs.mkdir(ENRICHED_UNITS_DIR, { recursive: true });

        // Connect to database
        const db = new sqlite3.Database(DATABASE_FILE, sqlite3.OPEN_READONLY, (err) => {
            if (err) {
                reject(err);
                return;
            }
            console.log('Connected to database:', DATABASE_FILE);
        });

        console.log('\n' + '='.repeat(80));
        console.log('ENRICHING UNIT JSON FILES WITH DATABASE SPECIFICATIONS');
        console.log('='.repeat(80));
        console.log(`\nInput directory: ${UNITS_DIR}`);
        console.log(`Output directory: ${ENRICHED_UNITS_DIR}\n`);

        try {
            // Get all unit JSON files
            const files = await fs.readdir(UNITS_DIR);
            const unitFiles = files.filter(f => f.endsWith('_toe.json'));

            console.log(`Found ${unitFiles.length} unit files to enrich\n`);

            let enriched = 0;
            let skipped = 0;
            let errors = 0;

            for (const file of unitFiles) {
                const inputPath = path.join(UNITS_DIR, file);
                const outputPath = path.join(ENRICHED_UNITS_DIR, file);

                try {
                    const enrichedUnit = await enrichUnitFile(inputPath, db);

                    if (enrichedUnit) {
                        await fs.writeFile(outputPath, JSON.stringify(enrichedUnit, null, 2));
                        console.log(`  [OK] Saved enriched file: ${file}`);
                        enriched++;
                    } else {
                        console.log(`  [SKIP] ${file}`);
                        skipped++;
                    }
                } catch (err) {
                    console.error(`  [ERROR] Failed to enrich ${file}:`, err.message);
                    errors++;
                }
            }

            console.log('\n' + '='.repeat(80));
            console.log('ENRICHMENT SUMMARY');
            console.log('='.repeat(80));
            console.log(`Units enriched: ${enriched}`);
            console.log(`Units skipped: ${skipped}`);
            console.log(`Errors: ${errors}`);
            console.log('\n[OK] Unit enrichment complete!');
            console.log(`\nEnriched files saved to: ${ENRICHED_UNITS_DIR}`);
            console.log('='.repeat(80));

            db.close(() => {
                resolve({ enriched, skipped, errors });
            });
        } catch (err) {
            db.close();
            reject(err);
        }
    });
}

// Run if called directly
if (require.main === module) {
    enrichAllUnits()
        .then(() => process.exit(0))
        .catch((err) => {
            console.error('Enrichment failed:', err);
            process.exit(1);
        });
}

module.exports = { enrichAllUnits, enrichUnitFile };
