#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Load master directory
const master = JSON.parse(fs.readFileSync('data/canonical/MASTER_UNIT_DIRECTORY.json', 'utf8'));

// Get seed canonical IDs
const seedCanonicalIds = new Set(master.canonical_units.map(u => u.canonical_id));

// Scan completed units
const canonicalUnitsDir = 'data/output/units/';
const completedFiles = fs.readdirSync(canonicalUnitsDir).filter(f => f.endsWith('_toe.json'));

console.log('COMPLETED UNITS NOT IN SEED:');
console.log('');

const nonMatching = [];

for (const file of completedFiles) {
    const canonicalId = file.replace('_toe.json', '');

    if (!seedCanonicalIds.has(canonicalId)) {
        nonMatching.push(canonicalId);
        console.log(`  ${canonicalId}`);
    }
}

console.log('');
console.log(`Total non-matching: ${nonMatching.length}`);
console.log('');

// Group by nation
const byNation = {};
for (const id of nonMatching) {
    const nation = id.split('_')[0];
    if (!byNation[nation]) byNation[nation] = 0;
    byNation[nation]++;
}

console.log('BY NATION:');
for (const [nation, count] of Object.entries(byNation)) {
    console.log(`  ${nation}: ${count}`);
}
