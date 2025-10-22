/**
 * Analyze Out-of-Scope Units - Where Did They Come From?
 *
 * Questions:
 * 1. Where did agents find units NOT in seed file?
 * 2. What sources did they use?
 * 3. Are these legitimate North Africa units or extraction errors?
 */

const fs = require('fs');
const path = require('path');

console.log('=== ANALYZING OUT-OF-SCOPE UNITS ===\n');

// Load matching report
const matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf-8'));

// Get matched and unmatched unit IDs
const matchedIds = new Set();
matchingReport.matches.exact_matches.forEach(m => matchedIds.add(m.canonical_id));
matchingReport.matches.alias_matches.forEach(m => matchedIds.add(m.canonical_id));

const unmatchedUnits = matchingReport.unmatched || [];

console.log(`Total files: 276`);
console.log(`Matched to seed: ${matchedIds.size}`);
console.log(`Out-of-scope (unmatched): ${unmatchedUnits.length}\n`);

// Load and analyze each out-of-scope unit
console.log('=== ANALYZING OUT-OF-SCOPE UNIT SOURCES ===\n');

const outOfScopeAnalysis = {
    total: unmatchedUnits.length,
    by_nation: { german: 0, italian: 0, british: 0, american: 0, french: 0 },
    sources: {
        tessin: [],
        nafziger: [],
        army_lists: [],
        wikipedia: [],
        playfair: [],
        other: [],
        no_sources: []
    },
    sample_units: []
};

unmatchedUnits.forEach(unmatchedEntry => {
    const canonicalId = unmatchedEntry.canonical_id;
    const filename = `${canonicalId}_toe.json`;
    const filepath = path.join('data/output/units', filename);

    if (!fs.existsSync(filepath)) {
        return;
    }

    let unit;
    try {
        unit = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
    } catch (err) {
        return;
    }

    // Count by nation
    const nation = unit.nation;
    if (outOfScopeAnalysis.by_nation[nation] !== undefined) {
        outOfScopeAnalysis.by_nation[nation]++;
    }

    // Check sources
    let sourcesArray = null;
    if (unit.validation && unit.validation.source && Array.isArray(unit.validation.source)) {
        sourcesArray = unit.validation.source;
    } else if (unit.sources && Array.isArray(unit.sources)) {
        sourcesArray = unit.sources;
    }

    if (!sourcesArray || sourcesArray.length === 0) {
        outOfScopeAnalysis.sources.no_sources.push(canonicalId);
    } else {
        const sourceText = sourcesArray.join(' ').toLowerCase();

        if (sourceText.includes('tessin')) {
            outOfScopeAnalysis.sources.tessin.push(canonicalId);
        } else if (sourceText.includes('nafziger')) {
            outOfScopeAnalysis.sources.nafziger.push(canonicalId);
        } else if (sourceText.includes('army list')) {
            outOfScopeAnalysis.sources.army_lists.push(canonicalId);
        } else if (sourceText.includes('playfair')) {
            outOfScopeAnalysis.sources.playfair.push(canonicalId);
        } else if (sourceText.includes('wikipedia')) {
            outOfScopeAnalysis.sources.wikipedia.push(canonicalId);
        } else {
            outOfScopeAnalysis.sources.other.push(canonicalId);
        }
    }

    // Collect sample for display
    if (outOfScopeAnalysis.sample_units.length < 15) {
        outOfScopeAnalysis.sample_units.push({
            canonical_id: canonicalId,
            designation: unit.unit_designation || unit.designation,
            nation: unit.nation,
            quarter: unit.quarter,
            sources: sourcesArray ? sourcesArray.slice(0, 2) : ['No sources']
        });
    }
});

console.log('=== OUT-OF-SCOPE BY NATION ===\n');
for (const [nation, count] of Object.entries(outOfScopeAnalysis.by_nation)) {
    if (count > 0) {
        console.log(`${nation}: ${count} units`);
    }
}

console.log('\n=== OUT-OF-SCOPE SOURCES ===\n');
console.log(`Tessin: ${outOfScopeAnalysis.sources.tessin.length}`);
console.log(`Nafziger: ${outOfScopeAnalysis.sources.nafziger.length}`);
console.log(`Army Lists: ${outOfScopeAnalysis.sources.army_lists.length}`);
console.log(`Playfair: ${outOfScopeAnalysis.sources.playfair.length}`);
console.log(`Wikipedia: ${outOfScopeAnalysis.sources.wikipedia.length}`);
console.log(`Other: ${outOfScopeAnalysis.sources.other.length}`);
console.log(`No sources: ${outOfScopeAnalysis.sources.no_sources.length}`);

console.log('\n=== SAMPLE OUT-OF-SCOPE UNITS (first 15) ===\n');
outOfScopeAnalysis.sample_units.forEach((unit, idx) => {
    console.log(`${idx + 1}. ${unit.designation}`);
    console.log(`   ID: ${unit.canonical_id}`);
    console.log(`   Nation: ${unit.nation}, Quarter: ${unit.quarter}`);
    console.log(`   Sources: ${unit.sources[0]?.substring(0, 100) || 'None'}...`);
    console.log();
});

// Check if these are genuinely out-of-scope or naming variants
console.log('=== ANALYSIS: WHY ARE THESE OUT-OF-SCOPE? ===\n');

// Load seed file to check for similar units
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf-8'));

const nationMap = {
    german: 'german_units',
    italian: 'italian_units',
    british: 'british_units',
    american: 'usa_units',
    french: 'french_units'
};

let possibleNamingVariants = 0;
let genuinelyNewUnits = 0;

unmatchedUnits.slice(0, 20).forEach(unmatchedEntry => {
    const canonicalId = unmatchedEntry.canonical_id;
    const parts = canonicalId.split('_');
    const nation = parts[0];
    const quarter = parts[1];
    const designation = parts.slice(2).join('_');

    const seedKey = nationMap[nation];
    if (!seed[seedKey]) return;

    // Check if seed has similar unit in same quarter
    const similarInSeed = seed[seedKey].some(seedUnit => {
        if (!seedUnit.quarters.includes(quarter.toUpperCase().replace(/Q/, '-Q'))) return false;

        const seedDesignation = seedUnit.designation.toLowerCase();
        const fileDesignation = designation.toLowerCase();

        // Simple word overlap check
        const seedWords = seedDesignation.split(/[^a-z0-9]+/).filter(w => w.length > 2);
        const fileWords = fileDesignation.split(/[^a-z0-9]+/).filter(w => w.length > 2);

        const overlap = seedWords.filter(w => fileWords.includes(w)).length;
        return overlap >= 2; // At least 2 significant words match
    });

    if (similarInSeed) {
        possibleNamingVariants++;
    } else {
        genuinelyNewUnits++;
    }
});

console.log(`Sample of 20 out-of-scope units analyzed:`);
console.log(`  - Possible naming variants: ${possibleNamingVariants}`);
console.log(`  - Genuinely new units: ${genuinelyNewUnits}`);
console.log();

console.log('💡 CONCLUSION:');
console.log('Out-of-scope units likely include:');
console.log('  1. Naming variants not caught by alias system');
console.log('  2. Subunits extracted by agents (brigades, regiments)');
console.log('  3. Units mentioned in sources but not in original seed');
console.log('  4. Different quarter assignments than seed expected');
