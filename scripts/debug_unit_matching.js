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

// Build map of seed units (for fuzzy matching)
const seedUnits = [];
nations.forEach(key => {
  if (seed[key]) {
    seed[key].forEach(unit => {
      unit.quarters.forEach(quarter => {
        const nation = nationMap[nationKeyMap[key]];
        seedUnits.push({
          nation: nation,
          quarter: quarter,
          designation: unit.designation,
          normalized: naming.normalizeDesignation(unit.designation)
        });
      });
    });
  }
});

console.log('Total seed units:', seedUnits.length);

// Use fuzzy matching to find which completed units match seed
const matchedUnits = new Set();
const notInSeed = [];

state.completed.forEach(completedId => {
  // Parse completed ID: nation_quarter_designation
  const parts = completedId.split('_');
  if (parts.length < 3) {
    notInSeed.push(completedId);
    return;
  }

  const nation = parts[0];
  const quarter = parts[1];
  const designation = parts.slice(2).join('_');

  // Try to find matching seed unit using fuzzy logic
  let found = false;
  for (const seedUnit of seedUnits) {
    if (seedUnit.nation !== nation || seedUnit.quarter !== quarter) continue;

    // Use naming standard's fuzzy matching logic
    // Check if key words overlap
    const seedWords = seedUnit.normalized.split('_').filter(w => w.length > 2);
    const completedWords = designation.split('_').filter(w => w.length > 2);

    // Count matching words
    const matches = seedWords.filter(w => completedWords.includes(w)).length;

    // Need at least 60% of words to match
    if (matches >= Math.min(seedWords.length, completedWords.length) * 0.6) {
      found = true;
      matchedUnits.add(completedId);
      break;
    }
  }

  if (!found) {
    notInSeed.push(completedId);
  }
});

console.log('Units in WORKFLOW_STATE but NOT in seed file:', notInSeed.length);
console.log('\nFirst 10 examples:');
notInSeed.slice(0, 10).forEach(id => console.log('  ', id));

// Group orphaned by nation
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

// Check which seed units are NOT completed yet
const notCompleted = [];
seedUnits.forEach(seedUnit => {
  // Build expected pattern for this seed unit
  const seedNation = seedUnit.nation;
  const seedQuarter = seedUnit.quarter;
  const seedNorm = seedUnit.normalized;

  // Check if any completed unit matches this seed unit
  let found = false;
  for (const completedId of state.completed) {
    const parts = completedId.split('_');
    if (parts.length < 3) continue;

    const nation = parts[0];
    const quarter = parts[1];
    const designation = parts.slice(2).join('_');

    if (nation !== seedNation || quarter !== seedQuarter) continue;

    // Fuzzy match
    const seedWords = seedNorm.split('_').filter(w => w.length > 2);
    const completedWords = designation.split('_').filter(w => w.length > 2);
    const matches = seedWords.filter(w => completedWords.includes(w)).length;

    if (matches >= Math.min(seedWords.length, completedWords.length) * 0.6) {
      found = true;
      break;
    }
  }

  if (!found) {
    notCompleted.push(`${seedNation}_${seedQuarter}_${seedNorm}`);
  }
});

console.log('\n\nSeed units NOT in WORKFLOW_STATE:', notCompleted.length);
console.log('(These are the remaining units to complete)');

console.log('\n=== SUMMARY (with fuzzy matching) ===');
console.log('Current seed file: ' + seedUnits.length + ' units');
console.log('WORKFLOW_STATE completed: ' + state.completed.length + ' units');
console.log('Matching current scope: ' + matchedUnits.size + ' units');
console.log('Orphaned (not in scope): ' + notInSeed.length + ' units');
console.log('Remaining to complete: ' + notCompleted.length + ' units');
console.log('REAL progress: ' + (matchedUnits.size / seedUnits.length * 100).toFixed(1) + '%');
