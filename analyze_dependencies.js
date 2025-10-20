const seed = require('./projects/north_africa_seed_units_COMPLETE.json');
const workflow = require('./WORKFLOW_STATE.json');
const fs = require('fs');

// Helper to create canonical ID
function canonicalId(nation, quarter, designation) {
  return `${nation}_${quarter.toLowerCase().replace('-', '')}_${designation.toLowerCase().replace(/[^a-z0-9]+/g, '_')}`;
}

// Parse all units with metadata
const allUnits = [];
const nationMap = {
  'german_units': 'german',
  'italian_units': 'italian',
  'british_units': 'british',
  'usa_units': 'american',
  'french_units': 'french'
};

Object.entries(nationMap).forEach(([key, nation]) => {
  seed[key].forEach(unit => {
    unit.quarters.forEach(q => {
      const id = canonicalId(nation, q, unit.designation);
      const isComplete = workflow.completed.includes(id);

      allUnits.push({
        id,
        nation,
        quarter: q,
        year: q.split('-')[0],
        quarterNum: q.split('-')[1],
        designation: unit.designation,
        type: unit.type,
        complete: isComplete
      });
    });
  });
});

// Find remaining units
const remaining = allUnits.filter(u => !u.complete);

console.log('=== SUMMARY ===');
console.log(`Total unit-quarters: ${allUnits.length}`);
console.log(`Completed: ${allUnits.filter(u => u.complete).length}`);
console.log(`Remaining: ${remaining.length}\n`);

// Group by year
const byYear = {};
remaining.forEach(u => {
  if (!byYear[u.year]) byYear[u.year] = [];
  byYear[u.year].push(u);
});

console.log('=== REMAINING BY YEAR ===');
Object.keys(byYear).sort().forEach(year => {
  console.log(`${year}: ${byYear[year].length} unit-quarters`);
});

// Group by nation
const byNation = {};
remaining.forEach(u => {
  if (!byNation[u.nation]) byNation[u.nation] = [];
  byNation[u.nation].push(u);
});

console.log('\n=== REMAINING BY NATION ===');
Object.keys(byNation).sort().forEach(nation => {
  console.log(`${nation}: ${byNation[nation].length} unit-quarters`);
});

// Find hierarchical relationships
console.log('\n=== HIERARCHICAL DEPENDENCIES ===');

const hierarchyOrder = ['army', 'army_group', 'corps', 'division'];
const parentChildPairs = [];

remaining.forEach(unit => {
  // Check if this unit's parent exists in remaining list
  const unitHierarchy = hierarchyOrder.indexOf(unit.type.toLowerCase()) ||
    hierarchyOrder.findIndex(h => unit.type.toLowerCase().includes(h));

  if (unitHierarchy === -1) return;

  // Find potential parents (higher in hierarchy, same nation, same quarter)
  const potentialParents = remaining.filter(p => {
    const parentHierarchy = hierarchyOrder.indexOf(p.type.toLowerCase()) ||
      hierarchyOrder.findIndex(h => p.type.toLowerCase().includes(h));

    return p.nation === unit.nation &&
           p.quarter === unit.quarter &&
           parentHierarchy >= 0 &&
           parentHierarchy < unitHierarchy;
  });

  if (potentialParents.length > 0) {
    parentChildPairs.push({
      parent: potentialParents[0].designation,
      child: unit.designation,
      quarter: unit.quarter,
      nation: unit.nation
    });
  }
});

console.log(`Found ${parentChildPairs.length} potential parent-child dependencies\n`);
parentChildPairs.slice(0, 20).forEach(pair => {
  console.log(`${pair.nation} ${pair.quarter}: ${pair.parent} → ${pair.child}`);
});

// Find temporal dependencies (same unit, different quarters)
console.log('\n=== TEMPORAL DEPENDENCIES (Same Unit Across Quarters) ===');

const unitSequences = {};
remaining.forEach(u => {
  const key = `${u.nation}_${u.designation}`;
  if (!unitSequences[key]) unitSequences[key] = [];
  unitSequences[key].push(u);
});

// Only show units with multiple quarters
const multiQuarter = Object.entries(unitSequences)
  .filter(([key, units]) => units.length > 1)
  .sort((a, b) => b[1].length - a[1].length);

console.log(`Found ${multiQuarter.length} units appearing in multiple quarters\n`);
multiQuarter.slice(0, 15).forEach(([key, units]) => {
  const quarters = units.map(u => u.quarter).sort().join(', ');
  console.log(`${units[0].designation} (${units[0].nation}): ${units.length} quarters [${quarters}]`);
});

// Identify independent units (can be parallel)
console.log('\n=== PARALLEL EXTRACTION OPPORTUNITIES ===');

const by1942 = remaining.filter(u => u.year === '1942');
const nations1942 = [...new Set(by1942.map(u => u.nation))];

console.log(`1942 has ${by1942.length} unit-quarters across ${nations1942.length} nations:`);
nations1942.forEach(nation => {
  const count = by1942.filter(u => u.nation === nation).length;
  console.log(`  ${nation}: ${count} unit-quarters`);
});

console.log('\nThese can be extracted in parallel (different nations, no dependencies)');

// Generate dependency map JSON
const dependencyMap = {
  summary: {
    total_remaining: remaining.length,
    by_year: Object.keys(byYear).reduce((acc, year) => {
      acc[year] = byYear[year].length;
      return acc;
    }, {}),
    by_nation: Object.keys(byNation).reduce((acc, nation) => {
      acc[nation] = byNation[nation].length;
      return acc;
    }, {})
  },
  hierarchical_dependencies: parentChildPairs,
  temporal_sequences: multiQuarter.map(([key, units]) => ({
    unit: units[0].designation,
    nation: units[0].nation,
    quarters: units.map(u => u.quarter).sort(),
    sequence_type: 'temporal',
    extraction_order: 'sequential'
  })),
  parallel_groups: nations1942.map(nation => ({
    nation,
    year: '1942',
    count: by1942.filter(u => u.nation === nation).length,
    parallelizable: true,
    reason: 'Different nations - no cross-nation dependencies'
  }))
};

fs.writeFileSync('dependency_analysis.json', JSON.stringify(dependencyMap, null, 2));
console.log('\n✅ Saved dependency_analysis.json');
