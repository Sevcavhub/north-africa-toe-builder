/**
 * Investigate files with no source documentation
 *
 * Questions:
 * 1. Do they genuinely have no sources field?
 * 2. Are sources stored elsewhere in the JSON?
 * 3. Are these out-of-scope units or in-scope units?
 */

const fs = require('fs');
const path = require('path');

const unitsDir = 'data/output/units';
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('.json'));

console.log('=== INVESTIGATING FILES WITH NO SOURCE DOCUMENTATION ===\n');

const noSourcesFiles = [];
const hasSources = [];

files.forEach(filename => {
    const filepath = path.join(unitsDir, filename);
    const content = fs.readFileSync(filepath, 'utf-8');

    // Check for any mention of sources
    const hasSourcesField = content.includes('"sources"') ||
                           content.includes('"source_documentation"') ||
                           content.includes('Tessin') ||
                           content.includes('Nafziger') ||
                           content.includes('Army List') ||
                           content.includes('TM30') ||
                           content.includes('Field Manual');

    if (!hasSourcesField) {
        noSourcesFiles.push(filename);
    } else {
        hasSources.push(filename);
    }
});

console.log(`Total files: ${files.length}`);
console.log(`Files with sources: ${hasSources.length} (${Math.round(hasSources.length/files.length*100)}%)`);
console.log(`Files with NO sources: ${noSourcesFiles.length} (${Math.round(noSourcesFiles.length/files.length*100)}%)`);
console.log();

// Sample files with no sources
console.log('=== SAMPLE FILES WITH NO SOURCES (first 10) ===\n');
noSourcesFiles.slice(0, 10).forEach(filename => {
    const filepath = path.join(unitsDir, filename);
    const unit = JSON.parse(fs.readFileSync(filepath, 'utf-8'));

    console.log(`📄 ${filename}`);
    console.log(`   Designation: ${unit.unit_designation || unit.designation}`);
    console.log(`   Nation: ${unit.nation}`);
    console.log(`   Quarter: ${unit.quarter}`);

    // Check all top-level keys
    const keys = Object.keys(unit);
    const potentialSourceKeys = keys.filter(k =>
        k.toLowerCase().includes('source') ||
        k.toLowerCase().includes('data') ||
        k.toLowerCase().includes('quality') ||
        k.toLowerCase().includes('validation')
    );

    if (potentialSourceKeys.length > 0) {
        console.log(`   Potential source keys: ${potentialSourceKeys.join(', ')}`);
    }

    // Check for metadata
    if (unit.metadata) {
        console.log(`   Has metadata: ${Object.keys(unit.metadata).join(', ')}`);
    }

    console.log();
});

// Analyze by nation
console.log('\n=== NO SOURCES BY NATION ===\n');
const byNation = {
    german: { total: 0, noSources: 0 },
    italian: { total: 0, noSources: 0 },
    british: { total: 0, noSources: 0 },
    american: { total: 0, noSources: 0 },
    french: { total: 0, noSources: 0 }
};

files.forEach(f => {
    let nation = null;
    if (f.startsWith('german_')) nation = 'german';
    else if (f.startsWith('italian_')) nation = 'italian';
    else if (f.startsWith('british_')) nation = 'british';
    else if (f.startsWith('american_')) nation = 'american';
    else if (f.startsWith('french_')) nation = 'french';

    if (nation) {
        byNation[nation].total++;
        if (noSourcesFiles.includes(f)) {
            byNation[nation].noSources++;
        }
    }
});

for (const [nation, stats] of Object.entries(byNation)) {
    if (stats.total > 0) {
        const percent = Math.round((stats.noSources / stats.total) * 100);
        console.log(`${nation}: ${stats.noSources}/${stats.total} (${percent}%) have no sources`);
    }
}

// Load workflow state to check if these are in-scope or out-of-scope
console.log('\n=== IN-SCOPE vs OUT-OF-SCOPE (No Sources) ===\n');

const state = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf-8'));
const completedSet = new Set(state.completed);

// Load matching report
let matchingReport;
try {
    matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf-8'));
} catch (err) {
    console.log('⚠️  No matching report found');
    matchingReport = null;
}

if (matchingReport) {
    const matchedIds = new Set();
    matchingReport.matches.exact_matches.forEach(m => matchedIds.add(m.canonical_id));
    matchingReport.matches.alias_matches.forEach(m => matchedIds.add(m.canonical_id));

    let inScopeNoSources = 0;
    let outOfScopeNoSources = 0;

    noSourcesFiles.forEach(filename => {
        const canonicalId = filename.replace('_toe.json', '');
        if (matchedIds.has(canonicalId)) {
            inScopeNoSources++;
        } else {
            outOfScopeNoSources++;
        }
    });

    console.log(`In-scope units with no sources: ${inScopeNoSources}/${matchingReport.matches.exact_matches.length + matchingReport.matches.alias_matches.length} (${Math.round((inScopeNoSources/(matchingReport.matches.exact_matches.length + matchingReport.matches.alias_matches.length))*100)}%)`);
    console.log(`Out-of-scope units with no sources: ${outOfScopeNoSources}/${matchingReport.unmatched.length} (${Math.round((outOfScopeNoSources/matchingReport.unmatched.length)*100)}%)`);
}
