const fs = require('fs');

const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));

const divisions1942 = [];
const divisionTypes = ['division', 'armored_division', 'armoured_division', 'infantry_division', 'panzer_division', 'motorized_division', 'light_division', 'airborne_division', 'colonial_division', 'blackshirt_division', 'march_division'];

// Process each nation's units
['german_units', 'italian_units', 'british_units', 'american_units', 'french_units'].forEach(nationKey => {
  const nation = nationKey.replace('_units', '');
  if (seed[nationKey]) {
    seed[nationKey].forEach(unit => {
      if (divisionTypes.includes(unit.type)) {
        unit.quarters.forEach(quarter => {
          if (quarter.startsWith('1942')) {
            divisions1942.push({
              nation: nation,
              quarter: quarter,
              designation: unit.designation,
              type: unit.type
            });
          }
        });
      }
    });
  }
});

console.log('1942 DIVISION-LEVEL UNITS IN SEED:\n');
divisions1942.sort((a, b) => {
  if (a.quarter !== b.quarter) return a.quarter.localeCompare(b.quarter);
  if (a.nation !== b.nation) return a.nation.localeCompare(b.nation);
  return a.designation.localeCompare(b.designation);
}).forEach(d => {
  console.log(`${d.nation.padEnd(10)} | ${d.quarter} | ${d.type.padEnd(20)} | ${d.designation}`);
});

console.log(`\n\nTotal 1942 division-quarters in seed: ${divisions1942.length}`);
