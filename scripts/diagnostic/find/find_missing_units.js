const fs = require('fs');
const path = require('path');

// Load seed units
const seedData = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json'));

// Get completed files
const completedFiles = fs.readdirSync('data/output/units')
  .filter(f => f.endsWith('_toe.json'))
  .map(f => f.replace('_toe.json', ''));

// Combine all units from all nations
const allUnits = [
  ...(seedData.german_units || []).map(u => ({...u, nation: 'german'})),
  ...(seedData.italian_units || []).map(u => ({...u, nation: 'italian'})),
  ...(seedData.british_units || []).map(u => ({...u, nation: 'british'})),
  ...(seedData.american_units || []).map(u => ({...u, nation: 'american'})),
  ...(seedData.french_units || []).map(u => ({...u, nation: 'french'}))
];

// Generate expected filenames and find missing
const expected = [];
allUnits.forEach(unit => {
  unit.quarters.forEach(quarter => {
    const normalizedName = unit.designation
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
    // Normalize quarter format (remove hyphen)
    const normalizedQuarter = quarter.toLowerCase().replace('-', '');
    const filename = `${unit.nation}_${normalizedQuarter}_${normalizedName}`;
    expected.push({
      unit: unit.designation,
      nation: unit.nation,
      quarter: quarter,
      filename: filename
    });
  });
});

// Find missing
const missing = expected.filter(item => !completedFiles.includes(item.filename));

console.log(`Total expected: ${expected.length}`);
console.log(`Total completed: ${completedFiles.length}`);
console.log(`Total missing: ${missing.length}`);
console.log('');

// Group by quarter
const byQuarter = missing.reduce((acc, item) => {
  if (!acc[item.quarter]) acc[item.quarter] = [];
  acc[item.quarter].push(item);
  return acc;
}, {});

// Sort by count descending
const sorted = Object.entries(byQuarter).sort((a, b) => b[1].length - a[1].length);

console.log('Missing units by quarter (top 10):');
sorted.slice(0, 10).forEach(([quarter, items]) => {
  console.log(`\n${quarter}: ${items.length} missing`);
  items.slice(0, 5).forEach(item => {
    console.log(`  - ${item.nation} ${item.unit}`);
  });
  if (items.length > 5) {
    console.log(`  ... and ${items.length - 5} more`);
  }
});
