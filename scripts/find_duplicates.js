const fs = require('fs');
const path = require('path');

const unitsDir = 'data/output/units';
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

console.log(`Total files: ${files.length}\n`);

// Group files by nation_quarter to find duplicates
const byNationQuarter = {};

for (const file of files) {
    // Extract nation and quarter
    const match = file.match(/^(american|british|french|german|italian)_(\d{4}q\d)_(.+)_toe\.json$/);

    if (match) {
        const [_, nation, quarter, designation] = match;
        const key = `${nation}_${quarter}`;

        if (!byNationQuarter[key]) {
            byNationQuarter[key] = [];
        }

        byNationQuarter[key].push({
            file,
            nation,
            quarter,
            designation
        });
    }
}

// Find duplicates (same nation_quarter with multiple files)
const duplicates = {};
const unique = {};

for (const [key, fileList] of Object.entries(byNationQuarter)) {
    if (fileList.length > 1) {
        duplicates[key] = fileList;
    } else {
        unique[key] = fileList[0];
    }
}

console.log('═══════════════════════════════════════════════════════════');
console.log('DUPLICATE FILES (same nation_quarter, different designations)');
console.log('═══════════════════════════════════════════════════════════\n');

const duplicateKeys = Object.keys(duplicates).sort();
for (const key of duplicateKeys) {
    console.log(`${key}:`);
    for (const item of duplicates[key]) {
        console.log(`  - ${item.file}`);
    }
    console.log();
}

console.log('\n═══════════════════════════════════════════════════════════');
console.log('SUMMARY');
console.log('═══════════════════════════════════════════════════════════\n');

console.log(`Total files: ${files.length}`);
console.log(`Unique unit-quarters: ${Object.keys(unique).length + Object.keys(duplicates).length}`);
console.log(`Unit-quarters with duplicates: ${Object.keys(duplicates).length}`);
console.log(`Duplicate files: ${Object.values(duplicates).reduce((sum, list) => sum + list.length, 0)}`);
console.log(`Extra files (duplicates - 1): ${Object.values(duplicates).reduce((sum, list) => sum + list.length - 1, 0)}`);

console.log('\n═══════════════════════════════════════════════════════════');
console.log('BREAKDOWN BY NATION');
console.log('═══════════════════════════════════════════════════════════\n');

const nations = ['american', 'british', 'french', 'german', 'italian'];
for (const nation of nations) {
    const nationFiles = files.filter(f => f.startsWith(nation + '_'));
    const nationUnique = Object.keys(unique).filter(k => k.startsWith(nation + '_')).length;
    const nationDupes = Object.keys(duplicates).filter(k => k.startsWith(nation + '_')).length;
    const totalUniqueQuarters = nationUnique + nationDupes;

    console.log(`${nation}: ${nationFiles.length} files → ${totalUniqueQuarters} unique unit-quarters`);
    if (nationFiles.length > totalUniqueQuarters) {
        console.log(`  ⚠️  ${nationFiles.length - totalUniqueQuarters} duplicate files`);
    }
}
