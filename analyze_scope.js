const fs = require('fs');
const state = require('./WORKFLOW_STATE.json');
const seed = require('./projects/north_africa_seed_units_COMPLETE.json');

// Build set of all seed unit IDs
const seedUnitIds = new Set();
const nations = {
    german_units: 'german',
    italian_units: 'italian',
    british_units: 'british',
    american_units: 'american',
    french_units: 'french'
};

for (const [key, nation] of Object.entries(nations)) {
    const units = seed[key] || [];
    units.forEach(unit => {
        unit.quarters.forEach(quarter => {
            const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');
            const normalizedDesignation = unit.designation.toLowerCase()
                .replace(/[^a-z0-9]+/g, '_')
                .replace(/^_+|_+$/g, '');
            const unitId = `${nation}_${normalizedQuarter}_${normalizedDesignation}`;
            seedUnitIds.add(unitId);
        });
    });
}

console.log('Total seed unit-quarters:', seedUnitIds.size);
console.log('Total completed files:', state.completed.length);

// Categorize completed units
const inScope = [];
const outOfScope = [];

state.completed.forEach(unitId => {
    if (seedUnitIds.has(unitId)) {
        inScope.push(unitId);
    } else {
        outOfScope.push(unitId);
    }
});

console.log('\nIn-scope (match seed):', inScope.length);
console.log('Out-of-scope (NOT in seed):', outOfScope.length);

console.log('\n=== OUT-OF-SCOPE UNITS (first 30) ===\n');

// Group by pattern
const patterns = {};
outOfScope.slice(0, 30).forEach(id => {
    const parts = id.split('_');
    const nation = parts[0];
    const quarter = parts[1];
    const designation = parts.slice(2).join('_');

    const key = `${nation} (${quarter})`;
    if (!patterns[key]) patterns[key] = [];
    patterns[key].push(designation);
});

for (const [key, units] of Object.entries(patterns)) {
    console.log(`\n${key}:`);
    units.forEach(u => console.log(`  - ${u}`));
}

console.log(`\n\n... and ${outOfScope.length - 30} more out-of-scope units`);
