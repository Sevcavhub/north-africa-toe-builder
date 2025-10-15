const fs = require('fs');

const masterDir = JSON.parse(fs.readFileSync('data/canonical/MASTER_UNIT_DIRECTORY.json', 'utf8'));
const matchReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf8'));

// Get all matched files (in-scope)
const matchedFiles = new Set();
for (const match of matchReport.matches.exact_matches) {
    matchedFiles.add(match.matched_file);
}
for (const match of matchReport.matches.alias_matches) {
    matchedFiles.add(match.matched_file);
}

// Get all actual files
const unitsDir = 'data/output/units';
const allFiles = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

// Find out-of-scope files
const outOfScope = allFiles.filter(f => !matchedFiles.has(f));

console.log('═══════════════════════════════════════════════════════════');
console.log(`OUT OF SCOPE UNITS (${outOfScope.length} files)`);
console.log('═══════════════════════════════════════════════════════════\n');

// Read each out-of-scope file to get unit designation
const outOfScopeData = [];
for (const file of outOfScope) {
    try {
        const content = JSON.parse(fs.readFileSync(`${unitsDir}/${file}`, 'utf8'));
        const match = file.match(/^(american|british|french|german|italian)_(\d{4}q\d)_/);
        if (match) {
            outOfScopeData.push({
                file,
                nation: match[1],
                quarter: match[2],
                designation: content.unit_designation || 'Unknown'
            });
        }
    } catch (err) {
        outOfScopeData.push({
            file,
            nation: 'unknown',
            quarter: 'unknown',
            designation: 'Failed to read'
        });
    }
}

// Group by nation
const byNation = {};
for (const unit of outOfScopeData) {
    if (!byNation[unit.nation]) {
        byNation[unit.nation] = [];
    }
    byNation[unit.nation].push(unit);
}

for (const [nation, units] of Object.entries(byNation).sort()) {
    console.log(`${nation.toUpperCase()} (${units.length} out-of-scope units):`);
    for (const unit of units) {
        console.log(`  ${unit.quarter}: ${unit.designation}`);
        console.log(`    File: ${unit.file}`);
    }
    console.log();
}

console.log('\n═══════════════════════════════════════════════════════════');
console.log('SUMMARY');
console.log('═══════════════════════════════════════════════════════════\n');

console.log(`Total files: ${allFiles.length}`);
console.log(`In-scope (seed) units matched: ${matchedFiles.size}`);
console.log(`Out-of-scope units: ${outOfScope.length}`);
console.log(`\nSeed completion: ${matchedFiles.size}/215 (${(matchedFiles.size / 215 * 100).toFixed(1)}%)`);
