const fs = require('fs');
const unitsData = JSON.parse(fs.readFileSync('./data/canonical/COMPLETE_NORTH_AFRICA_COMBAT_UNITS.json', 'utf8'));
const state = JSON.parse(fs.readFileSync('./WORKFLOW_STATE.json', 'utf8'));

// Collect all units from all nations
const allUnits = [];
['american_units', 'german_units', 'italian_units', 'british_units', 'french_units'].forEach(key => {
  if (unitsData[key]) {
    unitsData[key].forEach(u => {
      allUnits.push({
        nation: key.replace('_units', ''),
        designation: u.designation,
        type: u.type,
        period: u.period
      });
    });
  }
});

// Filter for 1942-Q1 (period includes "1942q1")
const q1_units = allUnits.filter(u => {
  if (!u.period) return false;
  // Handle period ranges like "1942q1-1942q4" or single "1942q1"
  return u.period.includes('1942q1');
});

// Separate divisions from higher formations
const divisions = q1_units.filter(u => {
  const designation = u.designation.toLowerCase();
  return designation.includes('division') || designation.includes('divisione');
});

const higher = q1_units.filter(u => {
  const designation = u.designation.toLowerCase();
  return !designation.includes('division') && !designation.includes('divisione');
});

// Check completion status
const isCompleted = (unit) => {
  const id = (unit.nation + '_1942q1_' + unit.designation).toLowerCase().replace(/[^a-z0-9_]+/g, '_');
  return state.completed.some(c => c.includes(id.substring(0, 30)));
};

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
console.log('🎯 FIRST 3 INCOMPLETE DIVISIONS:\n');
incompleteDivs.slice(0, 3).forEach((u, i) => {
  console.log((i+1) + '. ' + u.nation.toUpperCase() + ' - ' + u.designation);
});
