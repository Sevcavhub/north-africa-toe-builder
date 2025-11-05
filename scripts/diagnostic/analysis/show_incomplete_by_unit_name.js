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

// Build map of incomplete quarters by unit
const incompleteByUnit = {};

['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'].forEach(nationKey => {
  if (!seed[nationKey]) return;

  const nation = nationKey.replace('_units', '');

  seed[nationKey].forEach(unit => {
    const key = `${nation}::${unit.designation}`;

    if (!incompleteByUnit[key]) {
      incompleteByUnit[key] = {
        nation: nation.toUpperCase(),
        designation: unit.designation,
        type: unit.type,
        incompleteQuarters: [],
        totalQuarters: unit.quarters.length
      };
    }

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
        incompleteByUnit[key].incompleteQuarters.push(quarter);
      }
    });
  });
});

// Filter out units that are fully complete
const incompleteUnits = Object.values(incompleteByUnit)
  .filter(u => u.incompleteQuarters.length > 0)
  .sort((a, b) => {
    // Sort by nation first, then by designation
    if (a.nation !== b.nation) return a.nation.localeCompare(b.nation);
    return a.designation.localeCompare(b.designation);
  });

// Display
console.log('═══════════════════════════════════════════════════════════════');
console.log('  INCOMPLETE UNITS - BY UNIT NAME');
console.log('═══════════════════════════════════════════════════════════════\n');
console.log(`Total Units with Incomplete Quarters: ${incompleteUnits.length}`);
console.log(`Total Incomplete Unit-Quarters: ${incompleteUnits.reduce((sum, u) => sum + u.incompleteQuarters.length, 0)}`);
console.log('\n═══════════════════════════════════════════════════════════════\n');

// Group by nation
const byNation = {};

incompleteUnits.forEach(unit => {
  if (!byNation[unit.nation]) {
    byNation[unit.nation] = [];
  }
  byNation[unit.nation].push(unit);
});

Object.keys(byNation).sort().forEach(nation => {
  if (byNation[nation].length === 0) return;

  console.log(`╔═══════════════════════════════════════════════════════════════╗`);
  console.log(`║  ${nation} - ${byNation[nation].length} UNITS WITH INCOMPLETE QUARTERS`.padEnd(64) + '║');
  console.log(`╚═══════════════════════════════════════════════════════════════╝\n`);

  byNation[nation].forEach(unit => {
    const completedCount = unit.totalQuarters - unit.incompleteQuarters.length;
    const progressBar = `[${completedCount}/${unit.totalQuarters}]`;

    console.log(`  ${unit.designation}`);
    console.log(`    Type: ${unit.type}`);
    console.log(`    Progress: ${progressBar} - ${unit.incompleteQuarters.length} quarters remaining`);
    console.log(`    Missing: ${unit.incompleteQuarters.join(', ')}`);
    console.log('');
  });

  console.log('');
});

console.log('═══════════════════════════════════════════════════════════════\n');
