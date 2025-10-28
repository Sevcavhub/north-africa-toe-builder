const fs = require('fs');
const path = require('path');

// Load seed and workflow
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));
const workflow = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf8'));

const completed = new Set(workflow.completed);

const nationMapping = {
  'german_units': 'german',
  'italian_units': 'italian',
  'british_units': 'british',
  'usa_units': 'american',
  'french_units': 'french'
};

function normalizeDesignation(str) {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '_')
    .trim();
}

const missing = [];

for (const [key, nation] of Object.entries(nationMapping)) {
  if (!seed[key]) continue;

  for (const unit of seed[key]) {
    const quarters = Array.isArray(unit.quarters) ? unit.quarters : [unit.quarter || unit.quarters];

    for (const quarter of quarters) {
      if (!quarter) continue;

      const quarterNorm = quarter.toLowerCase().replace('-', '');
      const desigNorm = normalizeDesignation(unit.designation);
      const unitId = `${nation}_${quarterNorm}_${desigNorm}`;

      // Check if this unit ID exists in completed
      const found = Array.from(completed).some(id => {
        // Exact match
        if (id === unitId) return true;

        // Fuzzy match - same nation, same quarter, similar designation
        if (id.startsWith(`${nation}_${quarterNorm}_`)) {
          const idDesig = id.replace(`${nation}_${quarterNorm}_`, '');
          const words1 = new Set(desigNorm.split('_').filter(w => w.length > 2));
          const words2 = new Set(idDesig.split('_').filter(w => w.length > 2));
          const intersection = new Set([...words1].filter(x => words2.has(x)));
          const similarity = intersection.size / Math.min(words1.size, words2.size);

          return similarity > 0.6;
        }

        return false;
      });

      if (!found) {
        missing.push({
          nation: nation.toUpperCase(),
          quarter,
          designation: unit.designation,
          type: unit.type || 'unknown',
          expectedId: unitId
        });
      }
    }
  }
}

console.log(`\nMISSING UNITS (${missing.length} total):\n`);
console.log('='.repeat(80));

const byNation = {};
for (const unit of missing) {
  if (!byNation[unit.nation]) byNation[unit.nation] = [];
  byNation[unit.nation].push(unit);
}

for (const [nation, units] of Object.entries(byNation).sort()) {
  console.log(`\n${nation} (${units.length} missing):`);
  for (const unit of units.sort((a, b) => a.quarter.localeCompare(b.quarter))) {
    console.log(`  - ${unit.quarter} - ${unit.designation} (${unit.type})`);
  }
}
