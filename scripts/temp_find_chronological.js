const fs = require('fs');
const path = require('path');

// Read seed file
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));

// Read WORKFLOW_STATE to see what's completed
const workflow = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf8'));
const completed = new Set(workflow.completed || []);

// Flatten all units
const allUnits = [];
['german_units', 'italian_units', 'british_units', 'american_units', 'french_units'].forEach(key => {
  if (seed[key]) {
    seed[key].forEach(unit => {
      unit.quarters.forEach(q => {
        const quarter = q.toLowerCase().replace(/-/g, '');
        const nation = key.replace('_units', '');
        const unitKey = `${nation}_${quarter}_${unit.designation.toLowerCase().replace(/[^a-z0-9]/g, '_').replace(/_+/g, '_')}`;

        allUnits.push({
          nation,
          unit: unit.designation,
          quarter,
          unitKey,
          completed: completed.has(unitKey)
        });
      });
    });
  }
});

// Sort chronologically
allUnits.sort((a, b) => a.quarter.localeCompare(b.quarter));

// Get incomplete units
const incomplete = allUnits.filter(u => !u.completed);

// Group by quarter
const byQuarter = {};
incomplete.forEach(u => {
  if (!byQuarter[u.quarter]) byQuarter[u.quarter] = [];
  byQuarter[u.quarter].push(u);
});

// Show first 5 quarters with incomplete units
console.log('INCOMPLETE UNITS (Chronological Order):\n');
Object.keys(byQuarter).sort().slice(0, 5).forEach(q => {
  console.log(`${q.toUpperCase()}: ${byQuarter[q].length} units`);
  byQuarter[q].slice(0, 5).forEach(u => {
    console.log(`  - ${u.nation} - ${u.unit}`);
  });
  if (byQuarter[q].length > 5) {
    console.log(`  ... and ${byQuarter[q].length - 5} more`);
  }
  console.log('');
});
