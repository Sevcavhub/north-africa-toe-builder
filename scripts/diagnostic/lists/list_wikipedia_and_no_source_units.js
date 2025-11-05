/**
 * List Wikipedia-only and No-Source out-of-scope units
 * with year-quarter breakdown
 */

const fs = require('fs');
const path = require('path');

// Load matching report
const matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf-8'));

// Get matched IDs
const matchedIds = new Set();
matchingReport.matches.exact_matches.forEach(m => matchedIds.add(m.canonical_id));
matchingReport.matches.alias_matches.forEach(m => matchedIds.add(m.canonical_id));

// Load all files
const unitsDir = 'data/output/units';
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

// Find out-of-scope units
const wikipediaOnly = [];
const noSources = [];

files.forEach(filename => {
    const canonicalId = filename.replace('_toe.json', '');

    // Only process out-of-scope units
    if (matchedIds.has(canonicalId)) return;

    const filepath = path.join(unitsDir, filename);
    let unit;

    try {
        unit = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
    } catch (err) {
        return;
    }

    // Get sources
    let sourcesArray = null;
    if (unit.validation && unit.validation.source && Array.isArray(unit.validation.source)) {
        sourcesArray = unit.validation.source;
    } else if (unit.sources && Array.isArray(unit.sources)) {
        sourcesArray = unit.sources;
    }

    // Parse year-quarter
    const parts = canonicalId.split('_');
    const nation = parts[0];
    const quarterStr = parts[1];
    const year = quarterStr.substring(0, 4);
    const quarter = quarterStr.substring(4).toUpperCase();

    const unitData = {
        canonical_id: canonicalId,
        designation: unit.unit_designation || unit.designation,
        nation: nation.charAt(0).toUpperCase() + nation.slice(1),
        year: year,
        quarter: quarter,
        yearQuarter: `${year}-${quarter}`,
        sources: sourcesArray || []
    };

    if (!sourcesArray || sourcesArray.length === 0) {
        noSources.push(unitData);
    } else {
        const sourceText = sourcesArray.join(' ').toLowerCase();

        // Check if Wikipedia is the ONLY source (or predominant)
        const hasWikipedia = sourceText.includes('wikipedia');
        const hasTessin = sourceText.includes('tessin');
        const hasNafziger = sourceText.includes('nafziger');
        const hasArmyList = sourceText.includes('army list');
        const hasTM30 = sourceText.includes('tm30') || sourceText.includes('tm-30');
        const hasFieldManual = sourceText.includes('field manual');
        const hasPlayfair = sourceText.includes('playfair');

        const hasPrimarySources = hasTessin || hasNafziger || hasArmyList || hasTM30 || hasFieldManual || hasPlayfair;

        if (hasWikipedia && !hasPrimarySources) {
            wikipediaOnly.push(unitData);
        }
    }
});

console.log('=== WIKIPEDIA-ONLY UNITS (38) ===\n');
console.log(`Found ${wikipediaOnly.length} units\n`);

// Sort by year-quarter, then nation
wikipediaOnly.sort((a, b) => {
    if (a.yearQuarter !== b.yearQuarter) return a.yearQuarter.localeCompare(b.yearQuarter);
    return a.nation.localeCompare(b.nation);
});

wikipediaOnly.forEach((unit, idx) => {
    console.log(`${idx + 1}. ${unit.yearQuarter} - ${unit.nation} - ${unit.designation}`);
    console.log(`   ID: ${unit.canonical_id}`);
    console.log(`   Source: ${unit.sources[0]?.substring(0, 120)}...`);
    console.log();
});

console.log('\n=== NO SOURCES UNITS (12) ===\n');
console.log(`Found ${noSources.length} units\n`);

// Sort by year-quarter, then nation
noSources.sort((a, b) => {
    if (a.yearQuarter !== b.yearQuarter) return a.yearQuarter.localeCompare(b.yearQuarter);
    return a.nation.localeCompare(b.nation);
});

noSources.forEach((unit, idx) => {
    console.log(`${idx + 1}. ${unit.yearQuarter} - ${unit.nation} - ${unit.designation}`);
    console.log(`   ID: ${unit.canonical_id}`);
    console.log();
});

// Summary by year-quarter
console.log('\n=== SUMMARY BY YEAR-QUARTER ===\n');

const byQuarter = {};

[...wikipediaOnly, ...noSources].forEach(unit => {
    if (!byQuarter[unit.yearQuarter]) {
        byQuarter[unit.yearQuarter] = { wikipedia: 0, noSource: 0 };
    }
    if (wikipediaOnly.includes(unit)) {
        byQuarter[unit.yearQuarter].wikipedia++;
    } else {
        byQuarter[unit.yearQuarter].noSource++;
    }
});

const sortedQuarters = Object.keys(byQuarter).sort();

console.log('Year-Quarter | Wikipedia Only | No Sources | Total');
console.log('-------------|----------------|------------|------');
sortedQuarters.forEach(q => {
    const stats = byQuarter[q];
    const total = stats.wikipedia + stats.noSource;
    console.log(`${q.padEnd(12)} | ${stats.wikipedia.toString().padEnd(14)} | ${stats.noSource.toString().padEnd(10)} | ${total}`);
});

console.log(`\nTOTAL        | ${wikipediaOnly.length.toString().padEnd(14)} | ${noSources.length.toString().padEnd(10)} | ${wikipediaOnly.length + noSources.length}`);
