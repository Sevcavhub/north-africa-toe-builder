const fs = require('fs');
const path = require('path');

/**
 * Analyzes which seed file units remain to be completed
 * Uses fuzzy matching to account for name variations
 */

const seedPath = path.join(__dirname, '../projects/north_africa_seed_units.json');
const statePath = path.join(__dirname, '../WORKFLOW_STATE.json');

const seed = JSON.parse(fs.readFileSync(seedPath, 'utf-8'));
const state = JSON.parse(fs.readFileSync(statePath, 'utf-8'));

console.log('=== REMAINING SEED UNITS ANALYSIS ===\n');

// Nation mappings
const nationMap = {
  'german_units': 'german',
  'italian_units': 'italian',
  'british_units': 'british',
  'usa_units': 'american',
  'french_units': 'french'
};

// Normalize quarter format
function normalizeQuarter(q) {
  // Convert "1941-Q1" to "1941q1"
  return q.toLowerCase().replace('-', '');
}

// Fuzzy match unit designation
function fuzzyMatch(seed, completed) {
  const seedWords = seed.toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2);

  const compWords = completed.toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2);

  const matches = seedWords.filter(w => compWords.includes(w)).length;
  const threshold = Math.min(seedWords.length, compWords.length) * 0.6;

  return matches >= threshold;
}

// Build list of all seed unit-quarters
const allSeedUnits = [];
const remaining = [];
const completed = [];

for (const [key, nation] of Object.entries(nationMap)) {
  const units = seed[key] || [];

  for (const unit of units) {
    for (const quarter of unit.quarters) {
      const normalizedQ = normalizeQuarter(quarter);

      // Check if this unit-quarter is completed
      let found = false;
      for (const completedId of state.completed) {
        const parts = completedId.split('_');
        if (parts.length < 3) continue;

        const compNation = parts[0];
        const compQuarter = parts[1].replace('-', '').toLowerCase();
        const compDesignation = parts.slice(2).join(' ');

        if (compNation === nation && compQuarter === normalizedQ) {
          if (fuzzyMatch(unit.designation, compDesignation)) {
            found = true;
            completed.push({
              nation,
              quarter: normalizedQ,
              designation: unit.designation,
              completed_as: completedId
            });
            break;
          }
        }
      }

      const seedUnit = {
        nation,
        quarter: normalizedQ,
        designation: unit.designation,
        seed_entry: `${nation}_${normalizedQ}_${unit.designation}`
      };

      allSeedUnits.push(seedUnit);

      if (!found) {
        remaining.push(seedUnit);
      }
    }
  }
}

console.log(`Total seed unit-quarters: ${allSeedUnits.length}`);
console.log(`Completed from seed: ${completed.length}`);
console.log(`Remaining to complete: ${remaining.length}`);
console.log('');

// Break down by nation
console.log('=== REMAINING BY NATION ===\n');

const byNation = {
  german: [],
  italian: [],
  british: [],
  american: [],
  french: []
};

remaining.forEach(u => byNation[u.nation].push(u));

for (const [nation, units] of Object.entries(byNation)) {
  if (units.length > 0) {
    console.log(`**${nation.toUpperCase()}**: ${units.length} units remaining`);

    // Group by division
    const byDivision = {};
    units.forEach(u => {
      if (!byDivision[u.designation]) {
        byDivision[u.designation] = [];
      }
      byDivision[u.designation].push(u.quarter);
    });

    for (const [div, quarters] of Object.entries(byDivision)) {
      console.log(`  - ${div}: ${quarters.join(', ')}`);
    }
    console.log('');
  }
}

// Check for "orphaned" completed units (not in seed)
console.log('=== UNITS COMPLETED BUT NOT IN SEED FILE ===\n');

const orphaned = [];
for (const completedId of state.completed) {
  const parts = completedId.split('_');
  if (parts.length < 3) continue;

  const nation = parts[0];
  const quarter = parts[1].replace('-', '').toLowerCase();
  const designation = parts.slice(2).join(' ');

  let foundInSeed = false;
  for (const seedUnit of allSeedUnits) {
    if (seedUnit.nation === nation && seedUnit.quarter === quarter) {
      if (fuzzyMatch(seedUnit.designation, designation)) {
        foundInSeed = true;
        break;
      }
    }
  }

  if (!foundInSeed) {
    orphaned.push({
      id: completedId,
      nation,
      quarter,
      designation
    });
  }
}

console.log(`Found ${orphaned.length} "orphaned" units (completed but not in seed file)`);
console.log('');

// Group orphans by nation
const orphansByNation = {
  german: [],
  italian: [],
  british: [],
  american: [],
  french: []
};

orphaned.forEach(u => {
  if (orphansByNation[u.nation]) {
    orphansByNation[u.nation].push(u);
  }
});

for (const [nation, units] of Object.entries(orphansByNation)) {
  if (units.length > 0) {
    console.log(`**${nation.toUpperCase()}**: ${units.length} orphaned units`);
    units.slice(0, 10).forEach(u => {
      console.log(`  - ${u.id}`);
    });
    if (units.length > 10) {
      console.log(`  ... and ${units.length - 10} more`);
    }
    console.log('');
  }
}

// Save analysis
const output = {
  analysis_date: new Date().toISOString(),
  seed_file: 'projects/north_africa_seed_units.json',
  total_seed_units: allSeedUnits.length,
  completed_from_seed: completed.length,
  remaining_from_seed: remaining.length,
  orphaned_units: orphaned.length,
  remaining_by_nation: {
    german: byNation.german.length,
    italian: byNation.italian.length,
    british: byNation.british.length,
    american: byNation.american.length,
    french: byNation.french.length
  },
  orphaned_by_nation: {
    german: orphansByNation.german.length,
    italian: orphansByNation.italian.length,
    british: orphansByNation.british.length,
    american: orphansByNation.american.length,
    french: orphansByNation.french.length
  },
  remaining_units: remaining.map(u => ({
    nation: u.nation,
    quarter: u.quarter,
    designation: u.designation
  })),
  orphaned_units_list: orphaned.map(u => u.id)
};

const outputPath = path.join(__dirname, '../data/output/REMAINING_SEED_ANALYSIS.json');
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
console.log(`\n✅ Analysis saved to: ${outputPath}\n`);

// Summary
console.log('=== SUMMARY ===');
console.log('');
console.log(`📋 Seed file scope: ${allSeedUnits.length} unit-quarters (after removing 2 out-of-scope)`);
console.log(`✅ Completed from seed: ${completed.length} (${Math.round(completed.length / allSeedUnits.length * 100)}%)`);
console.log(`⏳ Remaining from seed: ${remaining.length} (${Math.round(remaining.length / allSeedUnits.length * 100)}%)`);
console.log(`📦 Orphaned (not in seed): ${orphaned.length}`);
console.log('');
console.log(`🎯 Total completed units in Africa: ${state.completed.length} (seed + orphaned)`);
console.log('');
console.log('**Next Steps**:');
console.log('1. Complete remaining 60 units from seed file');
console.log(`2. Decide whether to keep ${orphaned.length} orphaned units (most are garrison divisions)`);
console.log('3. Update PROJECT_SCOPE.md with final scope definition');
