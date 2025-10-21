const fs = require('fs');
const naming = require('./scripts/lib/naming_standard');

// Load seed data
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));

// Load workflow state
const state = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf8'));
const completedSet = new Set(state.completed || []);

// Find all 1943-Q1 units that are NOT completed
const missing = [];
const nations = naming.NATION_MAP;

for (const [key, nation] of Object.entries(nations)) {
    const units = seed[key] || [];
    const q1Units = units.filter(u => u.quarters && u.quarters.includes('1943-Q1'));

    q1Units.forEach(u => {
        const normalizedQuarter = '1943q1';
        const normalizedDesignation = u.designation.toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_+|_+$/g, '');
        const canonicalId = `${nation}_${normalizedQuarter}_${normalizedDesignation}`;

        if (!completedSet.has(canonicalId)) {
            missing.push({
                nation: nation.charAt(0).toUpperCase() + nation.slice(1),
                designation: u.designation,
                type: u.type || 'unknown',
                quarter: '1943-Q1'
            });
        }
    });
}

// Sort by organization level priority
const orgLevelPriority = {
    'division': 1,
    'brigade': 2,
    'regiment': 3,
    'corps': 4,
    'army': 5,
    'theater': 6,
    'unknown': 99
};

missing.sort((a, b) => {
    const aPriority = orgLevelPriority[a.type] || 99;
    const bPriority = orgLevelPriority[b.type] || 99;
    return aPriority - bPriority;
});

console.log('ALL 11 REMAINING UNITS FOR 1943-Q1:\n');
console.log('Priority | Type     | Nation   | Unit');
console.log('---------|----------|----------|-------------------------------------');
missing.forEach((u, i) => {
    const priority = orgLevelPriority[u.type] || 99;
    console.log(`${(i+1).toString().padStart(2)}       | ${u.type.padEnd(8)} | ${u.nation.padEnd(8)} | ${u.designation}`);
});

console.log(`\nTotal: ${missing.length} units\n`);

// Group by type
const byType = {};
missing.forEach(u => {
    if (!byType[u.type]) byType[u.type] = [];
    byType[u.type].push(u);
});

console.log('GROUPED BY ORGANIZATION LEVEL:\n');
for (const [type, units] of Object.entries(byType)) {
    console.log(`${type.toUpperCase()} (${units.length}):`);
    units.forEach(u => console.log(`  - ${u.nation}: ${u.designation}`));
    console.log('');
}
