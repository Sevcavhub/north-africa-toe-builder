#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const workflow = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf-8'));
const files = fs.readdirSync('data/output/units')
    .filter(f => f.endsWith('_toe.json'))
    .map(f => f.replace('_toe.json', ''));

const tracked = new Set(workflow.completed);
const untracked = files.filter(f => !tracked.has(f));

console.log('📊 Final Status Check\n');
console.log(`Total files:              ${files.length}`);
console.log(`Tracked in WORKFLOW_STATE: ${tracked.size}`);
console.log(`Untracked:                ${untracked.length}\n`);

if (untracked.length > 0) {
    console.log('Untracked files:');
    untracked.forEach(f => console.log(`  - ${f}`));
    console.log('');
}

const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf-8'));
console.log(`Expected (seed):          ${seed.total_unit_quarters}`);
console.log(`Completion:               ${((tracked.size / seed.total_unit_quarters) * 100).toFixed(1)}%`);
