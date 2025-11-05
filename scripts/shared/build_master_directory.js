#!/usr/bin/env node

/**
 * Phase 3.1: Build MASTER_UNIT_DIRECTORY.json
 *
 * Purpose: Create canonical master directory from validated seed + Nafziger + completed units
 *
 * Structure:
 * - Canonical IDs (format: german_1941q2_15_panzer_division)
 * - Aliases for naming variations
 * - Nafziger reference codes
 * - Deployment dates and quarters
 * - Battle participation
 * - Scope annotations (SEED vs BONUS)
 */

const fs = require('fs');
const path = require('path');

console.log('='.repeat(80));
console.log('PHASE 3.1: BUILD MASTER_UNIT_DIRECTORY.JSON');
console.log('='.repeat(80));
console.log();

// Load source data
console.log('Step 1: Loading source data...');
const validatedSeed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));
const completedAnalysis = JSON.parse(fs.readFileSync('data/output/COMPLETED_UNITS_ANALYSIS.json', 'utf8'));
const nafzigerIndex1939_1942 = JSON.parse(fs.readFileSync('Resource Documents/Nafziger Collection/WWII/North_Africa_Index/NORTH_AFRICA_FILES.json', 'utf8'));
const nafzigerIndex1943_1945 = JSON.parse(fs.readFileSync('Resource Documents/Nafziger Collection/1943-1945/NAFZIGER_1943-1945_INDEX.json', 'utf8'));

// Load Italian sources index
let italianSourcesIndex = null;
try {
    italianSourcesIndex = JSON.parse(fs.readFileSync('data/canonical/ITALIAN_SOURCES_INDEX.json', 'utf8'));
} catch (err) {
    console.log('  ⚠️  Italian sources index not found (will skip Italian sources integration)');
}

// Load British sources index
let britishSourcesIndex = null;
try {
    britishSourcesIndex = JSON.parse(fs.readFileSync('data/canonical/BRITISH_SOURCES_INDEX.json', 'utf8'));
} catch (err) {
    console.log('  ⚠️  British sources index not found (will skip British sources integration)');
}

// Combine Nafziger indices
const nafzigerIndex = [
    ...nafzigerIndex1939_1942,
    { period: '1943-1945', entries: nafzigerIndex1943_1945 }
];

const totalNafziger = nafzigerIndex1939_1942.reduce((sum, period) => sum + period.entries.length, 0) + nafzigerIndex1943_1945.length;

console.log(`  ✅ Validated seed: ${validatedSeed.total_units} units`);
console.log(`  ✅ Completed analysis: ${completedAnalysis.units.length} unit-quarters`);
console.log(`  ✅ Nafziger 1939-1942: ${nafzigerIndex1939_1942.reduce((sum, period) => sum + period.entries.length, 0)} entries`);
console.log(`  ✅ Nafziger 1943-1945: ${nafzigerIndex1943_1945.length} entries`);
console.log(`  ✅ Total Nafziger: ${totalNafziger} entries`);
if (italianSourcesIndex) {
    console.log(`  ✅ Italian sources: ${italianSourcesIndex.metadata.total_references} references for ${italianSourcesIndex.metadata.target_divisions.length} divisions`);
}
if (britishSourcesIndex) {
    console.log(`  ✅ British sources: ${britishSourcesIndex.metadata.total_unit_quarters} unit-quarters for ${britishSourcesIndex.metadata.target_units.length} divisions`);
}
console.log();

// Helper: Normalize quarter format (1941-Q2 → 1941q2)
function normalizeQuarter(quarter) {
    return quarter.toLowerCase().replace('-', '');
}

// Helper: Generate canonical ID
function generateCanonicalId(nation, quarter, designation) {
    const nationLower = nation.toLowerCase();
    const quarterNorm = normalizeQuarter(quarter);

    // Create slug from designation
    let slug = designation
        .toLowerCase()
        .replace(/[àäâ]/g, 'a')
        .replace(/[éèêë]/g, 'e')
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '');

    return `${nationLower}_${quarterNorm}_${slug}`;
}

// Helper: Extract Nafziger codes for a unit
function findNafzigerCodes(designation, nation) {
    const codes = [];
    const designationLower = designation.toLowerCase();

    for (const period of nafzigerIndex) {
        for (const entry of period.entries) {
            const titleLower = entry.title.toLowerCase();
            let matched = false;

            // Match unit designation in title
            if (nation === 'german') {
                // Specific divisions
                if (designationLower.includes('15.') || designationLower.includes('15 ')) {
                    if (titleLower.includes('15th panzer') || titleLower.includes('15 panzer')) matched = true;
                }
                if (designationLower.includes('21.') || designationLower.includes('21 ')) {
                    if (titleLower.includes('21st panzer') || titleLower.includes('21 panzer')) matched = true;
                }
                if (designationLower.includes('5.') || designationLower.includes('5 ')) {
                    if (titleLower.includes('5th light') || titleLower.includes('5 light')) matched = true;
                }
                if (designationLower.includes('90.') || designationLower.includes('90 ')) {
                    if (titleLower.includes('90th light') || titleLower.includes('90 light')) matched = true;
                }
                if (designationLower.includes('164.') || designationLower.includes('164 ')) {
                    if (titleLower.includes('164th light') || titleLower.includes('164') && titleLower.includes('afrika')) matched = true;
                }
                // Corps/Army level
                if (designationLower.includes('afrika')) {
                    if (titleLower.includes('afrika korps') || titleLower.includes('afrika corps')) matched = true;
                }
                if (designationLower.includes('panzerarmee')) {
                    if (titleLower.includes('panzer army afrika') || titleLower.includes('panzerarmee afrika') ||
                        titleLower.includes('panzer armee afrika')) matched = true;
                }
                // Broad German North Africa entries (only for corps/army level or general OOB)
                if (designationLower.includes('afrika') || designationLower.includes('panzerarmee')) {
                    if (titleLower.includes('german') && titleLower.includes('north africa')) matched = true;
                    if (titleLower.includes('axis') && titleLower.includes('north africa')) matched = true;
                    if (titleLower.includes('italo-german') && titleLower.includes('north africa')) matched = true;
                }
            } else if (nation === 'italian') {
                // Named divisions
                const italianNames = ['ariete', 'trieste', 'brescia', 'bologna', 'pavia', 'trento', 'savona',
                                     'littorio', 'folgore', 'superga', 'centauro'];
                for (const name of italianNames) {
                    if (designationLower.includes(name) && titleLower.includes(name)) {
                        matched = true;
                        break;
                    }
                }
                // No broad Italian entries - rely on specific division name matching only
            } else if (nation === 'british') {
                // Specific divisions
                if (designationLower.includes('7th') || designationLower.includes('7 ')) {
                    if (titleLower.includes('7th armoured') || titleLower.includes('7 armoured')) matched = true;
                }
                if (designationLower.includes('1st') && designationLower.includes('armoured')) {
                    if (titleLower.includes('1st armoured') || titleLower.includes('1 armoured')) matched = true;
                }
                if (designationLower.includes('10th') && designationLower.includes('armoured')) {
                    if (titleLower.includes('10th armoured') || titleLower.includes('10 armoured')) matched = true;
                }
                if (designationLower.includes('50th') && designationLower.includes('infantry')) {
                    if (titleLower.includes('50th') || titleLower.includes('50 ')) matched = true;
                }
                if (designationLower.includes('51st') && designationLower.includes('highland')) {
                    if (titleLower.includes('51st') && titleLower.includes('highland')) matched = true;
                }
                // Commonwealth divisions
                if (designationLower.includes('indian')) {
                    if (titleLower.includes('indian')) {
                        // Match specific Indian division numbers
                        if ((designationLower.includes('4th') && titleLower.includes('4th')) ||
                            (designationLower.includes('5th') && titleLower.includes('5th')) ||
                            (designationLower.includes('8th') && titleLower.includes('8th')) ||
                            (designationLower.includes('10th') && titleLower.includes('10th'))) {
                            matched = true;
                        }
                    }
                }
                if (designationLower.includes('australian')) {
                    if (titleLower.includes('australian')) {
                        if (designationLower.includes('9th') && titleLower.includes('9th')) matched = true;
                    }
                }
                if (designationLower.includes('new zealand')) {
                    if (titleLower.includes('new zealand')) {
                        if (designationLower.includes('2nd') && (titleLower.includes('2nd') || titleLower.includes('2 '))) matched = true;
                    }
                }
                if (designationLower.includes('south african')) {
                    if (titleLower.includes('south african')) {
                        if (designationLower.includes('1st') && (titleLower.includes('1st') || titleLower.includes('1 '))) matched = true;
                    }
                }
                // Army/Force level
                if (designationLower.includes('8th army')) {
                    if (titleLower.includes('8th army') || titleLower.includes('eighth army')) matched = true;
                }
                if (designationLower.includes('western desert')) {
                    if (titleLower.includes('western desert')) matched = true;
                }
                // Broad British entries (only for army level or major operations)
                if (designationLower.includes('8th army') || designationLower.includes('western desert')) {
                    if (titleLower.includes('british') && titleLower.includes('north africa')) matched = true;
                    if (titleLower.includes('british') && (titleLower.includes('compass') || titleLower.includes('battleaxe') ||
                        titleLower.includes('crusader') || titleLower.includes('tobruk'))) matched = true;
                }
            } else if (nation === 'american') {
                // Specific divisions
                if (designationLower.includes('1st') && designationLower.includes('armored')) {
                    if ((titleLower.includes('us 1st') || titleLower.includes('1st us') ||
                         (titleLower.includes('1st') && titleLower.includes('armored') &&
                          (titleLower.includes('us ') || titleLower.includes('american'))))) matched = true;
                }
                if (designationLower.includes('1st') && designationLower.includes('infantry')) {
                    if ((titleLower.includes('us 1st') || titleLower.includes('1st us')) &&
                        titleLower.includes('infantry')) matched = true;
                }
                if (designationLower.includes('3rd') && designationLower.includes('infantry')) {
                    if ((titleLower.includes('us 3rd') || titleLower.includes('3rd us')) &&
                        titleLower.includes('infantry')) matched = true;
                }
                if (designationLower.includes('9th') && designationLower.includes('infantry')) {
                    if ((titleLower.includes('us 9th') || titleLower.includes('9th us')) &&
                        titleLower.includes('infantry')) matched = true;
                }
                // Corps
                if (designationLower.includes('ii corps')) {
                    if (titleLower.includes('ii corps') && (titleLower.includes('us') || titleLower.includes('american'))) matched = true;
                }
                // Broad American North Africa entries (only if specifically US/American)
                if ((titleLower.includes('us ') || titleLower.includes('american')) &&
                    (titleLower.includes('north africa') || titleLower.includes('tunisia'))) {
                    matched = true;
                }
            } else if (nation === 'french') {
                // Free French
                if (designationLower.includes('française libre') || designationLower.includes('francaise libre')) {
                    if (titleLower.includes('french') && (titleLower.includes('gaulist') || titleLower.includes('free'))) matched = true;
                }
                if (designationLower.includes('marocaine') || designationLower.includes('moroccan')) {
                    if (titleLower.includes('french') || titleLower.includes('morocco')) matched = true;
                }
                // Broad French entries
                if (titleLower.includes('french') && titleLower.includes('north africa')) matched = true;
            }

            if (matched) {
                codes.push({
                    code: entry.fileCode,
                    title: entry.title.trim().replace(/\s+/g, ' '),
                    pdfPath: entry.pdfPath
                });
            }
        }
    }

    return codes;
}

// Helper: Extract Italian source references
function findItalianSourceRefs(designation, nation) {
    if (!italianSourcesIndex || nation !== 'italian') {
        return [];
    }

    const refs = [];
    const designationLower = designation.toLowerCase();

    // Check if designation matches any of the target divisions
    for (const [divisionName, divisionData] of Object.entries(italianSourcesIndex.divisions)) {
        if (designationLower.includes(divisionName.toLowerCase())) {
            // Add source references
            for (const source of divisionData.sources) {
                const sourceMetadata = italianSourcesIndex.metadata.sources.find(s => s.name === source);
                if (sourceMetadata) {
                    refs.push({
                        source: sourceMetadata.name,
                        title: sourceMetadata.full_title,
                        path: sourceMetadata.path,
                        confidence: sourceMetadata.confidence,
                        type: sourceMetadata.type,
                        reference_count: divisionData.references.filter(r => r.source === source).length
                    });
                }
            }
            break; // Only match once
        }
    }

    return refs;
}

// Helper: Extract British source references
function findBritishSourceRefs(designation, nation, quarter) {
    if (!britishSourcesIndex || nation !== 'british') {
        return [];
    }

    const refs = [];
    const quarterNorm = normalizeQuarter(quarter);

    // Check if designation matches any of the target units
    for (const [unitName, unitData] of Object.entries(britishSourcesIndex.units)) {
        if (unitName.toLowerCase() === designation.toLowerCase()) {
            // Get sources for this specific quarter
            const quarterData = unitData.quarters[quarterNorm];
            if (quarterData && quarterData.sources) {
                for (const source of quarterData.sources) {
                    refs.push({
                        source: source.source,
                        title: source.title,
                        specific_file: source.specific_file || null,
                        confidence: source.confidence,
                        note: source.note
                    });
                }
            }
            break; // Only match once
        }
    }

    return refs;
}

// Helper: Extract battles from completed units
function extractBattles(designation, nation) {
    const battles = new Set();

    for (const unit of completedAnalysis.units) {
        if (unit.nation === nation && unit.designation) {
            // Fuzzy match designation
            const unitWords = unit.designation.toLowerCase().split(/\s+/).filter(w => w.length > 2);
            const desigWords = designation.toLowerCase().split(/\s+/).filter(w => w.length > 2);
            const matches = unitWords.filter(uw => desigWords.includes(uw)).length;

            if (matches / Math.min(unitWords.length, desigWords.length) >= 0.6) {
                // Extract battles from wargaming_data or deployment
                if (unit.deployment && unit.deployment.battles) {
                    unit.deployment.battles.forEach(b => battles.add(b));
                }
            }
        }
    }

    return Array.from(battles);
}

// Helper: Find completed unit IDs
function findCompletedUnits(designation, nation) {
    const completedIds = [];

    for (const unit of completedAnalysis.units) {
        if (unit.nation === nation && unit.designation) {
            const unitWords = unit.designation.toLowerCase().split(/\s+/).filter(w => w.length > 2);
            const desigWords = designation.toLowerCase().split(/\s+/).filter(w => w.length > 2);
            const matches = unitWords.filter(uw => desigWords.includes(uw)).length;

            if (matches / Math.min(unitWords.length, desigWords.length) >= 0.6) {
                completedIds.push(unit.unit_id);
            }
        }
    }

    return completedIds;
}

// Step 2: Build canonical directory from seed
console.log('Step 2: Building canonical entries from validated seed...');

const masterDirectory = {
    metadata: {
        created: new Date().toISOString(),
        version: '1.0.0',
        source: 'Phase 2 validated seed file + Nafziger Collection + completed units',
        scope: 'Units physically in Africa + documented combat participation',
        total_units: 0,
        total_unit_quarters: 0
    },
    canonical_units: []
};

// Process each nation in seed
for (const [key, units] of Object.entries(validatedSeed)) {
    if (!key.endsWith('_units')) continue;
    if (!Array.isArray(units)) continue; // Skip non-array entries

    const nation = key.replace('_units', '').replace('usa', 'american');
    console.log(`  Processing ${nation} units...`);

    for (const unit of units) {
        // Create entry for each quarter
        for (const quarter of unit.quarters) {
            const canonicalId = generateCanonicalId(nation, quarter, unit.designation);
            const quarterNorm = normalizeQuarter(quarter);

            // Find Nafziger codes
            const nafzigerCodes = findNafzigerCodes(unit.designation, nation);

            // Find Italian source refs
            const italianRefs = findItalianSourceRefs(unit.designation, nation);

            // Find British source refs
            const britishRefs = findBritishSourceRefs(unit.designation, nation, quarter);

            // Find battles
            const battles = extractBattles(unit.designation, nation);

            // Find completed unit IDs
            const completedIds = findCompletedUnits(unit.designation, nation);

            const entry = {
                canonical_id: canonicalId,
                nation: nation,
                quarter: quarterNorm,
                designation: unit.designation,
                aliases: [
                    unit.designation,
                    // Add common variations
                    ...(unit.designation.includes('.') ? [unit.designation.replace('.', '')] : []),
                    ...(unit.designation.includes('-') ? [unit.designation.replace('-', ' ')] : [])
                ],
                authoritative_sources: {
                    nafziger_refs: nafzigerCodes,
                    italian_source_refs: italianRefs,
                    british_source_refs: britishRefs,
                    seed_file: true,
                    completed: completedIds.length > 0,
                    completed_ids: completedIds
                },
                deployment: {
                    quarter: quarterNorm,
                    battles: battles.length > 0 ? battles : ["To be researched"],
                    scope_classification: "SEED"
                }
            };

            masterDirectory.canonical_units.push(entry);
            masterDirectory.metadata.total_unit_quarters++;
        }
    }
}

// Count unique units
const uniqueUnits = new Set(masterDirectory.canonical_units.map(u => u.designation));
masterDirectory.metadata.total_units = uniqueUnits.size;

console.log(`  ✅ Created ${masterDirectory.canonical_units.length} unit-quarter entries`);
console.log(`  ✅ ${masterDirectory.metadata.total_units} unique units`);
console.log();

// Step 3: Add orphaned units from completed analysis
console.log('Step 3: Adding orphaned units (BONUS scope)...');

const seedUnits = new Set();
for (const [key, units] of Object.entries(validatedSeed)) {
    if (!key.endsWith('_units')) continue;
    if (!Array.isArray(units)) continue; // Skip non-array entries
    for (const unit of units) {
        seedUnits.add(unit.designation.toLowerCase());
    }
}

const orphanedUnits = {};

for (const unit of completedAnalysis.units) {
    if (!unit.designation || unit.designation === 'unknown') continue;

    // Check if already in seed (fuzzy match)
    const inSeed = Array.from(seedUnits).some(seedUnit => {
        const unitWords = unit.designation.toLowerCase().split(/\s+/).filter(w => w.length > 2);
        const seedWords = seedUnit.split(/\s+/).filter(w => w.length > 2);
        const matches = unitWords.filter(uw => seedWords.includes(uw)).length;
        return matches / Math.min(unitWords.length, seedWords.length) >= 0.6;
    });

    if (inSeed) continue;

    // Add to orphaned units
    const key = `${unit.nation}:${unit.designation}`;
    if (!orphanedUnits[key]) {
        orphanedUnits[key] = {
            nation: unit.nation,
            designation: unit.designation,
            quarters: [],
            unit_ids: []
        };
    }

    orphanedUnits[key].quarters.push(unit.quarter);
    orphanedUnits[key].unit_ids.push(unit.unit_id);
}

console.log(`  Found ${Object.keys(orphanedUnits).length} orphaned units`);

// Add orphaned units to master directory
for (const [key, orphan] of Object.entries(orphanedUnits)) {
    for (const quarter of orphan.quarters) {
        const canonicalId = generateCanonicalId(orphan.nation, quarter, orphan.designation);
        const quarterNorm = normalizeQuarter(quarter);

        const nafzigerCodes = findNafzigerCodes(orphan.designation, orphan.nation);
        const italianRefs = findItalianSourceRefs(orphan.designation, orphan.nation);
        const britishRefs = findBritishSourceRefs(orphan.designation, orphan.nation, quarter);
        const battles = extractBattles(orphan.designation, orphan.nation);

        const entry = {
            canonical_id: canonicalId,
            nation: orphan.nation,
            quarter: quarterNorm,
            designation: orphan.designation,
            aliases: [
                orphan.designation,
                ...(orphan.designation.includes('.') ? [orphan.designation.replace('.', '')] : []),
                ...(orphan.designation.includes('-') ? [orphan.designation.replace('-', ' ')] : [])
            ],
            authoritative_sources: {
                nafziger_refs: nafzigerCodes,
                italian_source_refs: italianRefs,
                british_source_refs: britishRefs,
                seed_file: false,
                completed: true,
                completed_ids: orphan.unit_ids.filter(id => id.includes(quarterNorm))
            },
            deployment: {
                quarter: quarterNorm,
                battles: battles.length > 0 ? battles : ["To be researched"],
                scope_classification: "BONUS"
            }
        };

        masterDirectory.canonical_units.push(entry);
    }
}

console.log(`  ✅ Added ${Object.keys(orphanedUnits).length} orphaned units to master directory`);
console.log();

// Step 4: Update metadata
const allUnits = new Set(masterDirectory.canonical_units.map(u => u.designation));
masterDirectory.metadata.total_units = allUnits.size;
masterDirectory.metadata.total_unit_quarters = masterDirectory.canonical_units.length;

// Count by scope
const seedCount = masterDirectory.canonical_units.filter(u => u.deployment.scope_classification === 'SEED').length;
const bonusCount = masterDirectory.canonical_units.filter(u => u.deployment.scope_classification === 'BONUS').length;

masterDirectory.metadata.scope_breakdown = {
    seed_units: seedCount,
    bonus_units: bonusCount
};

// Count by nation
const nationCounts = {};
for (const unit of masterDirectory.canonical_units) {
    if (!nationCounts[unit.nation]) {
        nationCounts[unit.nation] = 0;
    }
    nationCounts[unit.nation]++;
}
masterDirectory.metadata.by_nation = nationCounts;

// Step 5: Sort canonical units
console.log('Step 4: Sorting canonical units...');
masterDirectory.canonical_units.sort((a, b) => {
    // Sort by nation, then quarter, then designation
    if (a.nation !== b.nation) return a.nation.localeCompare(b.nation);
    if (a.quarter !== b.quarter) return a.quarter.localeCompare(b.quarter);
    return a.designation.localeCompare(b.designation);
});
console.log('  ✅ Sorted alphabetically by nation → quarter → designation');
console.log();

// Step 6: Write master directory
console.log('Step 5: Writing MASTER_UNIT_DIRECTORY.json...');
const outputPath = 'data/canonical/MASTER_UNIT_DIRECTORY.json';

// Ensure directory exists
const outputDir = path.dirname(outputPath);
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

fs.writeFileSync(outputPath, JSON.stringify(masterDirectory, null, 2));
console.log(`  ✅ Written to: ${outputPath}`);
console.log();

// Step 7: Generate summary report
console.log('='.repeat(80));
console.log('MASTER UNIT DIRECTORY SUMMARY');
console.log('='.repeat(80));
console.log();
console.log('📊 OVERALL STATISTICS:');
console.log(`  Total unique units: ${masterDirectory.metadata.total_units}`);
console.log(`  Total unit-quarters: ${masterDirectory.metadata.total_unit_quarters}`);
console.log();
console.log('🎯 SCOPE BREAKDOWN:');
console.log(`  SEED scope (validated): ${seedCount} unit-quarters`);
console.log(`  BONUS scope (orphaned): ${bonusCount} unit-quarters`);
console.log();
console.log('🌍 BY NATION:');
for (const [nation, count] of Object.entries(nationCounts)) {
    console.log(`  ${nation}: ${count} unit-quarters`);
}
console.log();
console.log('📚 SOURCE COVERAGE:');
const withNafziger = masterDirectory.canonical_units.filter(u => u.authoritative_sources.nafziger_refs.length > 0).length;
const withItalian = masterDirectory.canonical_units.filter(u => u.authoritative_sources.italian_source_refs && u.authoritative_sources.italian_source_refs.length > 0).length;
const withBritish = masterDirectory.canonical_units.filter(u => u.authoritative_sources.british_source_refs && u.authoritative_sources.british_source_refs.length > 0).length;
const withAnySource = masterDirectory.canonical_units.filter(u =>
    u.authoritative_sources.nafziger_refs.length > 0 ||
    (u.authoritative_sources.italian_source_refs && u.authoritative_sources.italian_source_refs.length > 0) ||
    (u.authoritative_sources.british_source_refs && u.authoritative_sources.british_source_refs.length > 0)
).length;
console.log(`  Nafziger sources: ${withNafziger} / ${masterDirectory.canonical_units.length} (${(withNafziger / masterDirectory.canonical_units.length * 100).toFixed(1)}%)`);
if (italianSourcesIndex) {
    console.log(`  Italian G2/TME sources: ${withItalian} / ${masterDirectory.canonical_units.length} (${(withItalian / masterDirectory.canonical_units.length * 100).toFixed(1)}%)`);
}
if (britishSourcesIndex) {
    console.log(`  British MOD/TM sources: ${withBritish} / ${masterDirectory.canonical_units.length} (${(withBritish / masterDirectory.canonical_units.length * 100).toFixed(1)}%)`);
}
console.log(`  ANY authoritative source: ${withAnySource} / ${masterDirectory.canonical_units.length} (${(withAnySource / masterDirectory.canonical_units.length * 100).toFixed(1)}%)`);
console.log();
console.log('✅ COMPLETION STATUS:');
const completed = masterDirectory.canonical_units.filter(u => u.authoritative_sources.completed).length;
console.log(`  Completed unit-quarters: ${completed} / ${masterDirectory.canonical_units.length}`);
console.log();
console.log('Next: Create canonical_master_matcher.js agent (Phase 3.2)');
console.log('='.repeat(80));
