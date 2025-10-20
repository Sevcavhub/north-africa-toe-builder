const fs = require('fs');
const path = require('path');

// Load seed file
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));

// Get all actual files in canonical directory
const unitsDir = 'data/output/units';
const allFiles = fs.readdirSync(unitsDir)
  .filter(f => f.endsWith('_toe.json'))
  .map(f => f.replace('_toe.json', ''));

// Extract all 1941 quarters from seed
const quarters1941 = ['1941-Q1', '1941-Q2', '1941-Q3', '1941-Q4'];

const analysis = {
  '1941-Q1': { expected: [], found: [], missing: [] },
  '1941-Q2': { expected: [], found: [], missing: [] },
  '1941-Q3': { expected: [], found: [], missing: [] },
  '1941-Q4': { expected: [], found: [], missing: [] }
};

// Check each nation's units
['german_units', 'italian_units', 'british_units'].forEach(nationKey => {
  const nation = nationKey.replace('_units', '');

  seed[nationKey].forEach(unit => {
    unit.quarters.forEach(quarter => {
      if (quarters1941.includes(quarter)) {
        const quarterKey = quarter.replace('-', '').toLowerCase();

        // Add to expected list
        analysis[quarter].expected.push({
          nation: nation,
          designation: unit.designation,
          type: unit.type,
          battles: unit.battles || []
        });

        // Check if ANY file matches this nation/quarter/designation
        // Be flexible with designation matching
        const designation_parts = unit.designation.toLowerCase()
          .replace(/[^a-z0-9]/g, ' ')
          .split(' ')
          .filter(p => p.length > 2); // Keep significant words

        const matchingFiles = allFiles.filter(f => {
          if (!f.startsWith(`${nation}_${quarterKey}_`)) return false;

          // Check if file contains key designation parts
          const filenameLower = f.toLowerCase();
          return designation_parts.some(part => filenameLower.includes(part));
        });

        if (matchingFiles.length > 0) {
          analysis[quarter].found.push({
            nation: nation,
            designation: unit.designation,
            files: matchingFiles
          });
        } else {
          analysis[quarter].missing.push({
            nation: nation,
            designation: unit.designation,
            type: unit.type,
            battles: unit.battles || []
          });
        }
      }
    });
  });
});

// Report
console.log('TRUE MISSING 1941 UNITS (after fuzzy matching):\n');
console.log('='.repeat(80));

let totalMissing = 0;

quarters1941.forEach(quarter => {
  const { expected, found, missing } = analysis[quarter];

  console.log(`\n${quarter}:`);
  console.log(`  Expected: ${expected.length} units`);
  console.log(`  Found: ${found.length} units`);
  console.log(`  Truly Missing: ${missing.length} units`);
  console.log('-'.repeat(80));

  if (missing.length > 0) {
    missing.forEach((u, i) => {
      console.log(`${i+1}. [${u.nation.toUpperCase()}] ${u.designation}`);
      console.log(`   Type: ${u.type}`);
      if (u.battles && u.battles.length > 0) {
        console.log(`   Battles: ${u.battles.slice(0, 3).join(', ')}${u.battles.length > 3 ? '...' : ''}`);
      }
    });
    totalMissing += missing.length;
  } else {
    console.log('   ✅ ALL COMPLETE!\n');
  }
});

console.log('\n' + '='.repeat(80));
console.log(`TOTAL TRULY MISSING: ${totalMissing} unit-quarters`);
console.log('='.repeat(80));

// Save detailed report
fs.writeFileSync(
  'data/output/TRULY_MISSING_1941_UNITS.json',
  JSON.stringify(analysis, null, 2)
);
console.log('\n✅ Detailed report saved to: data/output/TRULY_MISSING_1941_UNITS.json');
