const fs = require('fs');

// Read the seed units
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));

// Read completed units
const completedFiles = fs.readdirSync('data/output/units/');
const completed1942 = completedFiles.filter(f => f.includes('_1942q'));

// Function to normalize unit designation for filename matching
function normalizeForFilename(designation) {
  return designation
    .toLowerCase()
    .replace(/\./g, '')
    .replace(/\s+/g, '_')
    .replace(/[()]/g, '')
    .replace(/'/g, '')
    .replace(/é/g, 'e')
    .replace(/è/g, 'e')
    .replace(/à/g, 'a')
    .replace(/ç/g, 'c')
    .replace(/_+/g, '_');
}

// Build list of required 1942 units from seed
const required1942 = [];

// Process each nation
const nations = {
  german: seed.german_units,
  italian: seed.italian_units,
  british: seed.british_units,
  american: seed.usa_units,
  french: seed.french_units
};

for (const [nation, units] of Object.entries(nations)) {
  for (const unit of units) {
    const quarters1942 = unit.quarters.filter(q => q.startsWith('1942'));
    for (const quarter of quarters1942) {
      // Convert quarter format: "1942-Q1" -> "1942q1"
      const normalizedQuarter = quarter.toLowerCase().replace('-', '');
      const normalizedDesignation = normalizeForFilename(unit.designation);
      const expectedFilename = `${nation}_${normalizedQuarter}_${normalizedDesignation}_toe.json`;

      required1942.push({
        nation,
        quarter: normalizedQuarter,
        designation: unit.designation,
        type: unit.type,
        expectedFilename,
        isCompleted: completed1942.includes(expectedFilename)
      });
    }
  }
}

// Group by completion status
const missing = required1942.filter(u => !u.isCompleted);
const complete = required1942.filter(u => u.isCompleted);

// Group missing by quarter and nation
const missingByQuarter = {
  '1942q1': [],
  '1942q2': [],
  '1942q3': [],
  '1942q4': []
};

for (const unit of missing) {
  missingByQuarter[unit.quarter].push(unit);
}

// Output report
console.log('\n========================================');
console.log('1942 UNITS COMPLETION STATUS');
console.log('========================================\n');

console.log(`Total 1942 unit-quarters required: ${required1942.length}`);
console.log(`Completed: ${complete.length} (${Math.round(complete.length / required1942.length * 100)}%)`);
console.log(`Missing: ${missing.length} (${Math.round(missing.length / required1942.length * 100)}%)`);

console.log('\n========================================');
console.log('MISSING UNITS BY QUARTER');
console.log('========================================\n');

for (const [quarter, units] of Object.entries(missingByQuarter)) {
  if (units.length > 0) {
    console.log(`\n--- ${quarter.toUpperCase()} (${units.length} missing) ---\n`);

    // Group by nation
    const byNation = {
      german: [],
      italian: [],
      british: [],
      american: [],
      french: []
    };

    for (const unit of units) {
      byNation[unit.nation].push(unit);
    }

    for (const [nation, nationUnits] of Object.entries(byNation)) {
      if (nationUnits.length > 0) {
        console.log(`  ${nation.toUpperCase()} (${nationUnits.length}):`);
        for (const unit of nationUnits) {
          console.log(`    - ${unit.designation} (${unit.type})`);
        }
        console.log('');
      }
    }
  }
}

console.log('\n========================================');
console.log('SUMMARY BY NATION (all 1942 quarters)');
console.log('========================================\n');

const byNationSummary = {
  german: { total: 0, complete: 0, missing: 0 },
  italian: { total: 0, complete: 0, missing: 0 },
  british: { total: 0, complete: 0, missing: 0 },
  american: { total: 0, complete: 0, missing: 0 },
  french: { total: 0, complete: 0, missing: 0 }
};

for (const unit of required1942) {
  byNationSummary[unit.nation].total++;
  if (unit.isCompleted) {
    byNationSummary[unit.nation].complete++;
  } else {
    byNationSummary[unit.nation].missing++;
  }
}

for (const [nation, stats] of Object.entries(byNationSummary)) {
  const pct = stats.total > 0 ? Math.round(stats.complete / stats.total * 100) : 0;
  console.log(`${nation.toUpperCase().padEnd(10)} | Total: ${stats.total.toString().padStart(3)} | Complete: ${stats.complete.toString().padStart(3)} (${pct}%) | Missing: ${stats.missing.toString().padStart(3)}`);
}

console.log('\n========================================\n');
