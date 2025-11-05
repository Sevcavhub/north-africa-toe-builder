const fs = require('fs');

const unitsDir = 'data/output/units';
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

console.log(`Total files in data/output/units/: ${files.length}\n`);

// Read each JSON to get the actual unit designation
const unitData = [];

for (const file of files) {
    try {
        const content = JSON.parse(fs.readFileSync(`${unitsDir}/${file}`, 'utf8'));
        const match = file.match(/^(american|british|french|german|italian)_(\d{4}q\d)_(.+)_toe\.json$/);

        if (match) {
            const [_, nation, quarter] = match;

            unitData.push({
                file,
                nation,
                quarter,
                unit_designation: content.unit_designation || 'Unknown',
                canonical_id: content.canonical_id || null
            });
        }
    } catch (err) {
        console.log(`⚠️  Failed to read ${file}: ${err.message}`);
    }
}

console.log(`Successfully read: ${unitData.length} files\n`);

// Group by nation_quarter_designation to find REAL duplicates
const byUnitQuarter = {};

for (const unit of unitData) {
    // Normalize designation to catch variations
    const normalizedDesig = unit.unit_designation
        .toLowerCase()
        .replace(/\./g, '')
        .replace(/'/g, '')
        .replace(/\s+/g, '_');

    const key = `${unit.nation}|${unit.quarter}|${normalizedDesig}`;

    if (!byUnitQuarter[key]) {
        byUnitQuarter[key] = [];
    }

    byUnitQuarter[key].push(unit);
}

// Find real duplicates
const realDuplicates = {};
const uniqueUnits = {};

for (const [key, units] of Object.entries(byUnitQuarter)) {
    if (units.length > 1) {
        realDuplicates[key] = units;
    } else {
        uniqueUnits[key] = units[0];
    }
}

console.log('═══════════════════════════════════════════════════════════');
console.log('REAL DUPLICATES (same unit, same quarter, different filenames)');
console.log('═══════════════════════════════════════════════════════════\n');

const dupKeys = Object.keys(realDuplicates).sort();
for (const key of dupKeys) {
    const units = realDuplicates[key];
    const [nation, quarter, _] = key.split('|');

    console.log(`${nation} ${quarter} - ${units[0].unit_designation}:`);
    for (const unit of units) {
        console.log(`  - ${unit.file}`);
        if (unit.canonical_id) {
            console.log(`    (canonical_id: ${unit.canonical_id})`);
        }
    }
    console.log();
}

console.log('\n═══════════════════════════════════════════════════════════');
console.log('SUMMARY');
console.log('═══════════════════════════════════════════════════════════\n');

const totalDupFiles = Object.values(realDuplicates).reduce((sum, list) => sum + list.length, 0);
const extraFiles = Object.values(realDuplicates).reduce((sum, list) => sum + list.length - 1, 0);

console.log(`Total files: ${files.length}`);
console.log(`Unique unit-quarters: ${Object.keys(uniqueUnits).length + Object.keys(realDuplicates).length}`);
console.log(`Unit-quarters with duplicate files: ${Object.keys(realDuplicates).length}`);
console.log(`Total duplicate files: ${totalDupFiles}`);
console.log(`Extra files (should delete): ${extraFiles}`);
console.log(`\nTRUE unique unit files if deduplicated: ${files.length - extraFiles}`);
