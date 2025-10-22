const fs = require('fs');

const seedData = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json'));
const completedFiles = fs.readdirSync('data/output/units')
  .filter(f => f.endsWith('_toe.json'))
  .map(f => f.replace('_toe.json', ''));

const allUnits = [
  ...(seedData.german_units || []).map(u => ({...u, nation: 'german'})),
  ...(seedData.italian_units || []).map(u => ({...u, nation: 'italian'})),
  ...(seedData.british_units || []).map(u => ({...u, nation: 'british'})),
  ...(seedData.american_units || []).map(u => ({...u, nation: 'american'})),
  ...(seedData.french_units || []).map(u => ({...u, nation: 'french'}))
];

const expected = [];
allUnits.forEach(unit => {
  unit.quarters.forEach(quarter => {
    if (quarter === '1941-Q1') {
      const normalizedName = unit.designation
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '');
      const normalizedQuarter = quarter.toLowerCase().replace('-', '');
      const filename = `${unit.nation}_${normalizedQuarter}_${normalizedName}`;
      expected.push({
        unit: unit.designation,
        nation: unit.nation,
        quarter: quarter,
        filename: filename
      });
    }
  });
});

const missing = expected.filter(item => !completedFiles.includes(item.filename));

console.log(`1941-Q1 Missing (${missing.length} units):`);
missing.forEach((item, i) => {
  console.log(`${i+1}. ${item.nation} - ${item.unit}`);
});
