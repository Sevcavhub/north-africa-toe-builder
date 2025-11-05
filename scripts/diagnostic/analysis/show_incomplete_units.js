#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Load seed and workflow state
const seedFile = path.join(__dirname, '../projects/north_africa_seed_units_COMPLETE.json');
const stateFile = path.join(__dirname, '../WORKFLOW_STATE.json');

const seed = JSON.parse(fs.readFileSync(seedFile, 'utf8'));
const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));

// Get completed unit IDs (normalize to lowercase, no hyphen)
const completed = new Set(state.completed.map(id => id.toLowerCase()));

// Build map of incomplete units by quarter
const incompleteByQuarter = {};

['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'].forEach(nationKey => {
  if (!seed[nationKey]) return;

  const nation = nationKey.replace('_units', '');

  seed[nationKey].forEach(unit => {
    (unit.quarters || []).forEach(quarter => {
      // Build expected unit ID
      const quarterNorm = quarter.toLowerCase().replace('-q', 'q'); // 1940-Q2 -> 1940q2
      const unitSlug = unit.designation
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '');

      const unitId = `${nation}_${quarterNorm}_${unitSlug}`;

      // Check if completed
      if (!completed.has(unitId)) {
        if (!incompleteByQuarter[quarter]) {
          incompleteByQuarter[quarter] = [];
        }
        incompleteByQuarter[quarter].push({
          nation: nation.toUpperCase(),
          designation: unit.designation,
          type: unit.type,
          unitId: unitId
        });
      }
    });
  });
});

// Sort quarters chronologically
const quarters = Object.keys(incompleteByQuarter).sort((a, b) => {
  const [yearA, qA] = a.split('-Q');
  const [yearB, qB] = b.split('-Q');
  return parseInt(yearA) - parseInt(yearB) || parseInt(qA) - parseInt(qB);
});

// Display
console.log('═══════════════════════════════════════════════════════════════');
console.log('  INCOMPLETE UNITS - BY YEAR AND QUARTER');
console.log('═══════════════════════════════════════════════════════════════\n');
console.log('Total Remaining:', Object.values(incompleteByQuarter).reduce((sum, arr) => sum + arr.length, 0), 'unit-quarters\n');
console.log('═══════════════════════════════════════════════════════════════\n');

quarters.forEach(quarter => {
  const units = incompleteByQuarter[quarter];

  console.log(`╔═══════════════════════════════════════════════════════════════╗`);
  console.log(`║  ${quarter} - ${units.length} INCOMPLETE UNITS`.padEnd(64) + '║');
  console.log(`╚═══════════════════════════════════════════════════════════════╝\n`);

  // Group by nation
  const byNation = {};
  units.forEach(u => {
    if (!byNation[u.nation]) byNation[u.nation] = [];
    byNation[u.nation].push(u);
  });

  Object.keys(byNation).sort().forEach(nation => {
    console.log(`  ▸ ${nation}:\n`);
    byNation[nation].forEach(u => {
      console.log(`    [ ] ${u.designation}`);
      console.log(`        Type: ${u.type}`);
      console.log(`        ID:   ${u.unitId}\n`);
    });
  });

  console.log('');
});

console.log('═══════════════════════════════════════════════════════════════\n');

// Summary by nation
console.log('Summary by Nation:\n');
const byNation = {};
quarters.forEach(q => {
  incompleteByQuarter[q].forEach(u => {
    if (!byNation[u.nation]) byNation[u.nation] = 0;
    byNation[u.nation]++;
  });
});

Object.keys(byNation).sort().forEach(nation => {
  console.log(`  ${nation.padEnd(12)}: ${byNation[nation]} incomplete unit-quarters`);
});

console.log('\n═══════════════════════════════════════════════════════════════\n');
