const naming = require('./lib/naming_standard');
const state = require('../WORKFLOW_STATE.json');
const seed = require('../projects/north_africa_seed_units.json');

const nationMap = {
  'Germany': 'german',
  'Italy': 'italian',
  'Britain': 'british',
  'USA': 'american',
  'France': 'french'
};

const seedSet = new Set();
const nations = ['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'];
const nationKeyMap = {
  'german_units': 'Germany',
  'italian_units': 'Italy',
  'british_units': 'Britain',
  'usa_units': 'USA',
  'french_units': 'France'
};

// Build set of all seed unit IDs
nations.forEach(key => {
  if (seed[key]) {
    seed[key].forEach(unit => {
      unit.quarters.forEach(quarter => {
        const nation = nationMap[nationKeyMap[key]];
        const designation = naming.normalizeDesignation(unit.designation);
        const unitId = `${nation}_${quarter}_${designation}`;
        seedSet.add(unitId);
      });
    });
  }
});

// Find units in WORKFLOW_STATE but not in seed
const notInSeed = state.completed.filter(id => !seedSet.has(id));

console.log('Units in WORKFLOW_STATE but NOT in seed file:', notInSeed.length);
console.log('\nFirst 10 examples:');
notInSeed.slice(0, 10).forEach(id => console.log('  ', id));

// Group by nation
const byNation = {};
notInSeed.forEach(id => {
  const nation = id.split('_')[0];
  if (!byNation[nation]) byNation[nation] = [];
  byNation[nation].push(id);
});

console.log('\n\nOrphaned units by nation:');
Object.entries(byNation).forEach(([nation, units]) => {
  console.log(`\n${nation}: ${units.length} units`);
  units.forEach(id => console.log('  -', id));
});

// Also check the reverse - seed units not in WORKFLOW_STATE
const notCompleted = Array.from(seedSet).filter(id => !state.completed.includes(id));
console.log('\n\nSeed units NOT in WORKFLOW_STATE:', notCompleted.length);
console.log('(These are the remaining units to complete)');

console.log('\n=== SUMMARY ===');
console.log('Current seed file: 213 units');
console.log('WORKFLOW_STATE completed: 153 units');
console.log('Matching current scope: ' + (153 - notInSeed.length) + ' units');
console.log('Orphaned (not in scope): ' + notInSeed.length + ' units');
console.log('Remaining to complete: ' + notCompleted.length + ' units');
console.log('REAL progress: ' + ((153 - notInSeed.length) / 213 * 100).toFixed(1) + '%');
