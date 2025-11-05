#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ws = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf-8'));
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf-8'));

// Build set of all seed canonical IDs
const seedIds = new Set();
const nations = ['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'];

nations.forEach(nationKey => {
    const units = seed[nationKey] || [];
    units.forEach(unit => {
        unit.quarters.forEach(q => {
            const quarter = q.toLowerCase().replace(/-/g, '');
            const nation = nationKey.replace('_units', '');
            const designation = unit.designation.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
            const id = `${nation}_${quarter}_${designation}`;
            seedIds.add(id);
        });
    });
});

// Find units in WORKFLOW_STATE that aren't in seed
const nonMatching = [];
ws.completed.forEach(id => {
    if (!seedIds.has(id)) {
        nonMatching.push(id);
    }
});

console.log('═'.repeat(80));
console.log('Units in WORKFLOW_STATE.json that DON\'T match complete seed:');
console.log('═'.repeat(80));
console.log('Total:', nonMatching.length);
console.log('');

// Group by nation and quarter
const byNation = {};
nonMatching.forEach(id => {
    const parts = id.split('_');
    const nation = parts[0];
    if (!byNation[nation]) byNation[nation] = [];
    byNation[nation].push(id);
});

Object.keys(byNation).sort().forEach(nation => {
    console.log(`\n${nation.toUpperCase()} (${byNation[nation].length} units):`);
    console.log('─'.repeat(80));
    byNation[nation].sort().forEach(id => console.log('  ' + id));
});

console.log('\n' + '═'.repeat(80));
console.log(`\nNeed to investigate: Are these ${nonMatching.length} units genuinely out of scope,`);
console.log('or should they be added to the complete seed?');
