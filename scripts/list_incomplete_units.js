#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const seedFile = path.join(__dirname, '../projects/north_africa_seed_units_COMPLETE.json');
const stateFile = path.join(__dirname, '../WORKFLOW_STATE.json');

const seed = JSON.parse(fs.readFileSync(seedFile, 'utf8'));
const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));

const completed = new Set(state.completed.map(id => id.toLowerCase()));

const incomplete = [];

['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'].forEach(nationKey => {
  if (!seed[nationKey]) return;

  const nation = nationKey.replace('_units', '');

  seed[nationKey].forEach(unit => {
    (unit.quarters || []).forEach(quarter => {
      const quarterNorm = quarter.toLowerCase().replace('-q', 'q');
      const unitSlug = unit.designation
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '');

      const unitId = `${nation}_${quarterNorm}_${unitSlug}`;

      if (!completed.has(unitId)) {
        incomplete.push({
          nation: nation,
          quarter: quarter,
          designation: unit.designation
        });
      }
    });
  });
});

// Sort by quarter, then nation, then designation
incomplete.sort((a, b) => {
  const [yearA, qA] = a.quarter.split('-Q');
  const [yearB, qB] = b.quarter.split('-Q');

  if (yearA !== yearB) return parseInt(yearA) - parseInt(yearB);
  if (qA !== qB) return parseInt(qA) - parseInt(qB);
  if (a.nation !== b.nation) return a.nation.localeCompare(b.nation);
  return a.designation.localeCompare(b.designation);
});

incomplete.forEach(item => {
  console.log(`${item.quarter} - ${item.nation} - ${item.designation}`);
});
