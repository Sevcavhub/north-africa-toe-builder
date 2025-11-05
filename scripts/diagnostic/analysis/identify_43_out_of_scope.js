/**
 * Identify the 43 out-of-scope units
 * (272 total files - 229 matched to seed = 43 out-of-scope)
 */

const fs = require('fs');
const path = require('path');

// Load matching report
const matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf-8'));

// Get matched IDs
const matchedIds = new Set();
matchingReport.matches.exact_matches.forEach(m => matchedIds.add(m.canonical_id));
matchingReport.matches.alias_matches.forEach(m => matchedIds.add(m.canonical_id));

console.log(`Exact matches: ${matchingReport.matches.exact_matches.length}`);
console.log(`Alias matches: ${matchingReport.matches.alias_matches.length}`);
console.log(`Total matched: ${matchedIds.size}\n`);

// Load all files
const unitsDir = 'data/output/units';
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

console.log(`Total files: ${files.length}\n`);

// Find out-of-scope
const outOfScope = [];

files.forEach(filename => {
    const canonicalId = filename.replace('_toe.json', '');
    if (!matchedIds.has(canonicalId)) {
        outOfScope.push(canonicalId);
    }
});

console.log(`=== OUT-OF-SCOPE UNITS (${outOfScope.length}) ===\n`);

// Load unit data for each out-of-scope unit
outOfScope.forEach((canonicalId, idx) => {
    const filepath = path.join(unitsDir, `${canonicalId}_toe.json`);

    let unit;
    try {
        unit = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
    } catch (err) {
        console.log(`${idx + 1}. ${canonicalId} - ERROR reading file`);
        return;
    }

    // Get sources
    let sources = [];
    if (unit.validation && unit.validation.source && Array.isArray(unit.validation.source)) {
        sources = unit.validation.source.slice(0, 1);
    }

    console.log(`${idx + 1}. ${unit.unit_designation || unit.designation}`);
    console.log(`   ID: ${canonicalId}`);
    console.log(`   Nation: ${unit.nation}, Quarter: ${unit.quarter}`);
    if (sources.length > 0) {
        console.log(`   Source: ${sources[0].substring(0, 120)}...`);
    } else {
        console.log(`   Source: None`);
    }
    console.log();
});

// Analyze patterns
console.log('\n=== PATTERN ANALYSIS ===\n');

const byNation = { german: 0, italian: 0, british: 0, american: 0, french: 0 };
const hasWikipedia = [];
const hasPrimarySources = [];
const noSources = [];

outOfScope.forEach(canonicalId => {
    const nation = canonicalId.split('_')[0];
    if (byNation[nation] !== undefined) {
        byNation[nation]++;
    }

    const filepath = path.join(unitsDir, `${canonicalId}_toe.json`);
    try {
        const unit = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
        const sourcesArray = unit.validation?.source || unit.sources || [];
        const sourceText = sourcesArray.join(' ').toLowerCase();

        if (sourcesArray.length === 0) {
            noSources.push(canonicalId);
        } else if (sourceText.includes('wikipedia')) {
            hasWikipedia.push(canonicalId);
        } else {
            hasPrimarySources.push(canonicalId);
        }
    } catch (err) {
        // ignore
    }
});

console.log('By Nation:');
for (const [nation, count] of Object.entries(byNation)) {
    if (count > 0) {
        console.log(`  ${nation}: ${count}`);
    }
}

console.log(`\nBy Source Type:`);
console.log(`  Primary sources (Tessin, Nafziger, etc): ${hasPrimarySources.length}`);
console.log(`  Wikipedia only: ${hasWikipedia.length}`);
console.log(`  No sources: ${noSources.length}`);
