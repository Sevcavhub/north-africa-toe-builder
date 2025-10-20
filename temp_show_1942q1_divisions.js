const fs = require('fs');
const naming = require('./scripts/lib/naming_standard');

// Load seed units
const seedData = JSON.parse(fs.readFileSync('./projects/north_africa_seed_units_COMPLETE.json', 'utf8'));

// Load completed units
const state = JSON.parse(fs.readFileSync('./WORKFLOW_STATE.json', 'utf8'));
const completedSet = new Set(state.completed);

// Extract all 1942-Q1 units from seed
const q1_units = [];
for (const [key, value] of Object.entries(seedData)) {
  if (key.endsWith('_units') && Array.isArray(value)) {
    const nation = naming.NATION_MAP[key] || key.replace('_units', '');
    for (const unit of value) {
      if (unit.quarters && unit.quarters.includes('1942-Q1')) {
        q1_units.push({
          nation: naming.normalizeNation(nation),
          designation: unit.designation,
          type: unit.type
        });
      }
    }
  }
}

// Separate divisions from higher formations
const divisions = q1_units.filter(u => {
  const designation = u.designation.toLowerCase();
  return designation.includes('division') || designation.includes('divisione');
});

const higher = q1_units.filter(u => {
  const designation = u.designation.toLowerCase();
  return !designation.includes('division') && !designation.includes('divisione');
});

// Check completion
function isCompleted(unit) {
  const normalizedDesignation = unit.designation.toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
  const canonicalId = `${unit.nation}_1942q1_${normalizedDesignation}`;

  // Check exact match
  if (completedSet.has(canonicalId)) return true;

  // Check partial match
  const prefix = `${unit.nation}_1942q1`;
  const designationWords = unit.designation.toLowerCase().split(/\s+/).filter(w => w.length > 3);

  for (const completedId of completedSet) {
    if (completedId.startsWith(prefix)) {
      const match = designationWords.every(word => completedId.includes(word.substring(0, 4)));
      if (match) return true;
    }
  }

  return false;
}

console.log('═══════════════════════════════════════════');
console.log('1942-Q1 DIVISIONS (' + divisions.length + ' total)\n');

const incompleteDivs = [];
divisions.forEach((u, i) => {
  const done = isCompleted(u);
  const status = done ? '✅' : '⬜';
  console.log((i+1) + '. ' + status + ' ' + u.nation.toUpperCase() + ' - ' + u.designation);
  if (!done) incompleteDivs.push(u);
});

console.log('\n═══════════════════════════════════════════');
console.log('1942-Q1 CORPS/ARMY/THEATER (' + higher.length + ' total)\n');

higher.forEach((u, i) => {
  const done = isCompleted(u);
  const status = done ? '✅' : '⬜';
  console.log((i+1) + '. ' + status + ' ' + u.nation.toUpperCase() + ' - ' + u.designation);
});

console.log('\n═══════════════════════════════════════════');
console.log('🎯 INCOMPLETE DIVISIONS: ' + incompleteDivs.length + '/' + divisions.length + '\n');
console.log('FIRST 3 INCOMPLETE DIVISIONS:\n');
incompleteDivs.slice(0, 3).forEach((u, i) => {
  console.log((i+1) + '. ' + u.nation.toUpperCase() + ' - ' + u.designation);
});
