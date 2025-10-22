#!/usr/bin/env node

/**
 * Check Matching Between WORKFLOW_STATE.json and Seed File
 *
 * Diagnoses discrepancy between completed units count and work queue matching.
 */

const fs = require('fs');
const naming = require('./lib/naming_standard');

// Load WORKFLOW_STATE.json
const state = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf-8'));

// Load seed file
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf-8'));

// Generate all seed unit IDs
const seedUnitIds = new Set();
for (const [nationKey, units] of Object.entries(seed)) {
    if (!nationKey.endsWith('_units') || !Array.isArray(units)) continue;

    const nation = naming.NATION_MAP[nationKey];
    if (!nation) continue;

    for (const unit of units) {
        for (const quarter of unit.quarters) {
            const cleanNation = naming.normalizeNation(nation);
            const cleanQuarter = naming.normalizeQuarter(quarter);
            const cleanDesignation = naming.normalizeDesignation(unit.designation);
            const unitId = `${cleanNation}_${cleanQuarter}_${cleanDesignation}`;
            seedUnitIds.add(unitId);
        }
    }
}

// Check how many completed units are in seed
let inSeed = 0;
let notInSeed = [];
for (const completed of state.completed) {
    if (seedUnitIds.has(completed)) {
        inSeed++;
    } else {
        notInSeed.push(completed);
    }
}

console.log('Completed units in WORKFLOW_STATE.json: ' + state.completed.length);
console.log('Units in seed file: ' + seedUnitIds.size);
console.log('Completed units that match seed: ' + inSeed);
console.log('Completed units NOT in seed: ' + notInSeed.length);
console.log('');
console.log('Sample units NOT in seed (first 20):');
notInSeed.slice(0, 20).forEach(u => console.log('  - ' + u));
