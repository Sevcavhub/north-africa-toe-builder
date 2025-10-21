const fs = require('fs');

// Load seed units
const seedData = JSON.parse(fs.readFileSync('projects/north_africa_seed_units.json', 'utf8'));

// Get existing completed units
const existingFiles = fs.readdirSync('data/output/units/').filter(f => f.endsWith('_toe.json'));

/**
 * Extract key identifying terms from unit designation
 * Handles formal vs informal names, multiple languages
 */
function extractKeyTerms(designation) {
  const terms = [];

  // Extract numbers (15, 21, 90, 132, etc.)
  const numbers = designation.match(/\d+/g) || [];
  terms.push(...numbers);

  // Extract distinctive names (Ariete, Folgore, Trieste, etc.)
  const distinctiveNames = [
    'ariete', 'trieste', 'littorio', 'bologna', 'brescia', 'pavia',
    'trento', 'savona', 'folgore', 'afrikakorps', 'panzerarmee',
    'panzergruppe', 'highland', 'indian', 'australian', 'zealand',
    'african', 'armoured', 'infantry', 'desert'
  ];

  const lowerDesig = designation.toLowerCase();
  distinctiveNames.forEach(name => {
    if (lowerDesig.includes(name)) {
      terms.push(name);
    }
  });

  // Extract unit type keywords
  if (lowerDesig.includes('panzer') || lowerDesig.includes('armor')) terms.push('panzer');
  if (lowerDesig.includes('leichte') || lowerDesig.includes('light')) terms.push('leichte');
  if (lowerDesig.includes('division')) terms.push('division');
  if (lowerDesig.includes('corps') || lowerDesig.includes('corpo')) terms.push('corps');
  if (lowerDesig.includes('army') || lowerDesig.includes('armata') || lowerDesig.includes('armee')) terms.push('army');

  return terms;
}

/**
 * Check if filename matches unit designation using fuzzy key term matching
 */
function filenameMatchesUnit(filename, nation, quarter, designation) {
  const fname = filename.toLowerCase();

  // Must match nation and quarter
  if (!fname.includes(nation.toLowerCase()) || !fname.includes('_' + quarter + '_')) {
    return false;
  }

  // Extract key terms from both seed designation and filename
  const seedTerms = extractKeyTerms(designation);
  const fileTerms = extractKeyTerms(filename);

  // Match if at least 2 key terms overlap (or all if only 1-2 terms total)
  const minMatchTerms = Math.min(2, seedTerms.length);
  const matchedTerms = seedTerms.filter(term => fileTerms.includes(term));

  return matchedTerms.length >= minMatchTerms;
}

// Convert seed format to quarter-indexed format
const byQuarter = {};

// Process each nation's units
['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'].forEach(nationKey => {
  const units = seedData[nationKey] || [];
  const nation = nationKey.replace('_units', '');

  units.forEach(unit => {
    unit.quarters.forEach(quarter => {
      const normalizedQuarter = quarter.toLowerCase().replace('-', '');
      if (!byQuarter[normalizedQuarter]) {
        byQuarter[normalizedQuarter] = [];
      }
      byQuarter[normalizedQuarter].push({
        nation: nation,
        designation: unit.designation
      });
    });
  });
});

// Check 1942 quarters
const quarters1942 = ['1942q1', '1942q2', '1942q3', '1942q4'];

console.log('════════════════════════════════════════════════════════════');
console.log('  1942 MISSING UNITS (Improved Name Matching)');
console.log('════════════════════════════════════════════════════════════\n');

let totalMissing = 0;
let totalExpected = 0;

quarters1942.forEach(quarter => {
  const expected = byQuarter[quarter] || [];
  totalExpected += expected.length;
  const missing = [];
  const found = [];

  expected.forEach(unit => {
    // Check if file exists using improved fuzzy matching
    const matchingFile = existingFiles.find(f =>
      filenameMatchesUnit(f, unit.nation, quarter, unit.designation)
    );

    if (!matchingFile) {
      missing.push(unit);
    } else {
      found.push({unit, file: matchingFile});
    }
  });

  console.log('📅 ' + quarter.toUpperCase() + ': ' + found.length + '/' + expected.length + ' units');

  if (missing.length > 0) {
    console.log('\n❌ MISSING (' + missing.length + ' units):\n');
    missing.forEach(unit => {
      console.log('   • ' + unit.nation + ' - ' + unit.designation);
    });
    totalMissing += missing.length;
  } else {
    console.log('   ✅ All units complete');
  }

  // Show matched files for verification (first 3 only to avoid clutter)
  if (found.length > 0 && found.length <= 5) {
    console.log('\n✅ FOUND (' + found.length + ' units):');
    found.forEach(({unit, file}) => {
      console.log('   • ' + unit.nation + ' - ' + unit.designation);
      console.log('     → ' + file);
    });
  }

  console.log('');
});

console.log('════════════════════════════════════════════════════════════');
console.log('  TOTAL 1942: ' + (totalExpected - totalMissing) + '/' + totalExpected + ' complete');
console.log('  MISSING: ' + totalMissing + ' units');
console.log('════════════════════════════════════════════════════════════');
