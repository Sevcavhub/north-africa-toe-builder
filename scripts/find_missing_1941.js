const fs = require('fs');
const path = require('path');

// Load seed file
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));

// Load workflow state
const workflow = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf8'));
const completed = new Set(workflow.completed);

// Extract all 1941 quarters from seed
const quarters1941 = ['1941-Q1', '1941-Q2', '1941-Q3', '1941-Q4'];

const missing = {
  '1941-Q1': [],
  '1941-Q2': [],
  '1941-Q3': [],
  '1941-Q4': []
};

// Helper to normalize unit names
function normalizeUnit(designation, nation) {
  return designation.toLowerCase()
    .replace(/[^a-z0-9]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '');
}

// Check each nation's units
['german_units', 'italian_units', 'british_units'].forEach(nationKey => {
  const nation = nationKey.replace('_units', '');

  seed[nationKey].forEach(unit => {
    unit.quarters.forEach(quarter => {
      if (quarters1941.includes(quarter)) {
        const normalized = normalizeUnit(unit.designation, nation);
        const canonicalId = `${nation}_${quarter.toLowerCase().replace('-', '')}_${normalized}`;

        if (!completed.has(canonicalId)) {
          missing[quarter].push({
            nation: nation,
            quarter: quarter,
            designation: unit.designation,
            type: unit.type,
            canonical_id: canonicalId,
            battles: unit.battles || [],
            note: unit.note || ''
          });
        }
      }
    });
  });
});

// Report
console.log('MISSING 1941 UNITS BY QUARTER:\n');
console.log('='.repeat(80));

quarters1941.forEach(quarter => {
  const units = missing[quarter];
  console.log(`\n${quarter}: ${units.length} missing units`);
  console.log('-'.repeat(80));

  if (units.length > 0) {
    units.forEach((u, i) => {
      console.log(`${i+1}. [${u.nation.toUpperCase()}] ${u.designation}`);
      console.log(`   Type: ${u.type}`);
      console.log(`   Canonical ID: ${u.canonical_id}`);
      if (u.battles && u.battles.length > 0) {
        console.log(`   Battles: ${u.battles.join(', ')}`);
      }
      if (u.note) {
        console.log(`   Note: ${u.note}`);
      }
      console.log('');
    });
  } else {
    console.log('   ✅ ALL COMPLETE!\n');
  }
});

// Summary
const totalMissing = Object.values(missing).reduce((sum, arr) => sum + arr.length, 0);
console.log('\n' + '='.repeat(80));
console.log(`TOTAL 1941 MISSING: ${totalMissing} unit-quarters`);
console.log('='.repeat(80));

// Save detailed report
fs.writeFileSync(
  'data/output/MISSING_1941_UNITS.json',
  JSON.stringify(missing, null, 2)
);
console.log('\n✅ Detailed report saved to: data/output/MISSING_1941_UNITS.json');
