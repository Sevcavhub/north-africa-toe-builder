#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const seedFile = path.join(__dirname, '../projects/north_africa_seed_units_COMPLETE.json');
const data = JSON.parse(fs.readFileSync(seedFile, 'utf8'));

console.log('═══════════════════════════════════════════════════════════════');
console.log('  NORTH AFRICA SEED UNITS - COMPLETE LIST BY QUARTER');
console.log('═══════════════════════════════════════════════════════════════\n');
console.log('Total Unique Units:', data.total_units);
console.log('Total Unit-Quarters:', data.total_unit_quarters);
console.log('Validation Date:', data.validation_date);
console.log('\n═══════════════════════════════════════════════════════════════\n');

// Get all quarters sorted
const quarterMap = {};
['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'].forEach(nationKey => {
  if (!data[nationKey]) return;
  data[nationKey].forEach(unit => {
    (unit.quarters || []).forEach(q => {
      if (!quarterMap[q]) quarterMap[q] = [];
      quarterMap[q].push({
        nation: nationKey.replace('_units', '').toUpperCase(),
        designation: unit.designation,
        type: unit.type
      });
    });
  });
});

// Sort quarters chronologically
const quarters = Object.keys(quarterMap).sort((a, b) => {
  const [yearA, qA] = a.split('-Q');
  const [yearB, qB] = b.split('-Q');
  return parseInt(yearA) - parseInt(yearB) || parseInt(qA) - parseInt(qB);
});

// Display by quarter
quarters.forEach(q => {
  const units = quarterMap[q];
  console.log('╔═══════════════════════════════════════════════════════════════╗');
  console.log('║  ' + q + ' (' + units.length + ' units)'.padEnd(60) + '║');
  console.log('╚═══════════════════════════════════════════════════════════════╝\n');

  // Group by nation
  const byNation = {};
  units.forEach(u => {
    if (!byNation[u.nation]) byNation[u.nation] = [];
    byNation[u.nation].push(u);
  });

  Object.keys(byNation).sort().forEach(nation => {
    console.log('  ▸ ' + nation + ':');
    byNation[nation].forEach(u => {
      console.log('    - ' + u.designation + ' (' + u.type + ')');
    });
    console.log('');
  });
  console.log('');
});

console.log('═══════════════════════════════════════════════════════════════\n');
console.log('Summary by Nation:\n');

['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'].forEach(nationKey => {
  if (!data[nationKey]) return;
  const nation = nationKey.replace('_units', '').toUpperCase();
  const totalQuarters = data[nationKey].reduce((sum, u) => sum + (u.quarters || []).length, 0);
  console.log('  ' + nation.padEnd(12) + ': ' + data[nationKey].length + ' unique units, ' + totalQuarters + ' unit-quarters');
});

console.log('\n═══════════════════════════════════════════════════════════════\n');
