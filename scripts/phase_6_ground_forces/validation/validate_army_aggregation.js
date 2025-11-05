const fs = require('fs');
const path = require('path');

// Army units by quarter (from previous analysis)
const armyUnits = {
  '1940q2': ['italian_1940q2_10_armata_toe.json'],
  '1940q3': ['italian_1940q3_10_armata_toe.json'],
  '1940q4': ['italian_1940q4_10_armata_toe.json'],
  '1941q1': ['italian_1941q1_10_armata_toe.json'],
  '1941q2': ['italian_1941q2_10_armata_toe.json'],
  '1941q3': ['italian_1941q3_10_armata_toe.json', 'british_1941q3_eighth_army_8th_army_toe.json'],
  '1941q4': ['italian_1941q4_10_armata_toe.json', 'british_1941q4_eighth_army_8th_army_toe.json'],
  '1942q1': ['italian_1942q1_10_armata_toe.json', 'british_1942q1_eighth_army_8th_army_toe.json'],
  '1942q2': ['british_1942q2_eighth_army_8th_army_toe.json'],
  '1942q3': ['british_1942q3_eighth_army_8th_army_toe.json'],
  '1942q4': [
    'british_1942q4_eighth_army_8th_army_toe.json',
    'british_1942q4_first_army_1st_army_toe.json',
    'german_1942q4_5_panzerarmee_toe.json'
  ],
  '1943q1': [
    'british_1943q1_eighth_army_8th_army_toe.json',
    'british_1943q1_first_army_1st_army_toe.json',
    'german_1943q1_5_panzerarmee_toe.json',
    'italian_1943q1_1_armata_toe.json'
  ],
  '1943q2': [
    'british_1943q2_eighth_army_8th_army_toe.json',
    'british_1943q2_first_army_1st_army_toe.json',
    'german_1943q2_5_panzerarmee_toe.json',
    'italian_1943q2_1_armata_toe.json'
  ]
};

const outputDir = path.join(__dirname, '..', 'data', 'output', 'units');

console.log('ARMY AGGREGATION VALIDATION REPORT');
console.log('='.repeat(80));
console.log(`Date: ${new Date().toISOString().split('T')[0]}`);
console.log(`Total Armies to Validate: 20`);
console.log('='.repeat(80));
console.log('');

const results = {
  correct: [],
  hq_only: [],
  missing_file: [],
  no_subordinates: []
};

let totalArmies = 0;

for (const [quarter, armies] of Object.entries(armyUnits)) {
  console.log(`\n${quarter.toUpperCase()}:`);
  console.log('-'.repeat(80));

  for (const armyFile of armies) {
    totalArmies++;
    const filePath = path.join(outputDir, armyFile);

    if (!fs.existsSync(filePath)) {
      console.log(`  MISSING FILE: ${armyFile}`);
      results.missing_file.push({ quarter, file: armyFile });
      continue;
    }

    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const designation = data.unit_designation || armyFile;

    // Check aggregation status
    const personnel = data.total_personnel || 0;
    const tanks = data.tanks?.total || 0;
    const subordinates = data.subordinate_units || [];
    const aggStatus = data.aggregation_status || 'unknown';

    // Calculate expected totals from subordinate units
    let expectedPersonnel = 0;
    let expectedTanks = 0;
    let hasSubordinateData = false;

    for (const sub of subordinates) {
      if (sub.strength && sub.strength > 0) {
        expectedPersonnel += sub.strength;
        hasSubordinateData = true;
      }
      if (sub.tanks && sub.tanks > 0) {
        expectedTanks += sub.tanks;
      }
    }

    // Determine status
    let status = 'UNKNOWN';
    let issue = null;

    if (subordinates.length === 0) {
      status = 'NO_SUBORDINATES';
      issue = 'No subordinate units listed';
      results.no_subordinates.push({
        quarter,
        file: armyFile,
        designation,
        personnel,
        tanks
      });
    } else if (!hasSubordinateData) {
      status = 'HQ_ONLY';
      issue = 'Subordinates listed but no strength data';
      results.hq_only.push({
        quarter,
        file: armyFile,
        designation,
        personnel,
        tanks,
        subordinates: subordinates.length,
        aggStatus
      });
    } else {
      // Has subordinate data - check if totals match
      const personnelMatch = Math.abs(personnel - expectedPersonnel) / expectedPersonnel < 0.15; // 15% tolerance
      const tanksMatch = expectedTanks === 0 || Math.abs(tanks - expectedTanks) / expectedTanks < 0.15;

      if (personnelMatch && tanksMatch) {
        status = 'CORRECT';
        results.correct.push({
          quarter,
          file: armyFile,
          designation,
          personnel,
          tanks,
          expected: { personnel: expectedPersonnel, tanks: expectedTanks }
        });
      } else {
        status = 'INCORRECT_TOTALS';
        issue = `Personnel: ${personnel} vs ${expectedPersonnel} expected, Tanks: ${tanks} vs ${expectedTanks} expected`;
        results.hq_only.push({
          quarter,
          file: armyFile,
          designation,
          personnel,
          tanks,
          expected: { personnel: expectedPersonnel, tanks: expectedTanks },
          aggStatus
        });
      }
    }

    // Print result
    console.log(`  ${designation}`);
    console.log(`    File: ${armyFile}`);
    console.log(`    Status: ${status}`);
    console.log(`    Personnel: ${personnel.toLocaleString()}, Tanks: ${tanks}`);
    console.log(`    Subordinates: ${subordinates.length} units`);
    if (hasSubordinateData) {
      console.log(`    Expected (from subs): Personnel: ${expectedPersonnel.toLocaleString()}, Tanks: ${expectedTanks}`);
    }
    console.log(`    Aggregation Status: ${aggStatus}`);
    if (issue) {
      console.log(`    ISSUE: ${issue}`);
    }
    console.log('');
  }
}

// Summary
console.log('\n' + '='.repeat(80));
console.log('SUMMARY');
console.log('='.repeat(80));
console.log(`Total Armies Validated: ${totalArmies}`);
console.log(`  CORRECT Aggregation: ${results.correct.length}`);
console.log(`  HQ-ONLY (needs fix): ${results.hq_only.length}`);
console.log(`  NO SUBORDINATES: ${results.no_subordinates.length}`);
console.log(`  MISSING FILES: ${results.missing_file.length}`);
console.log('');

if (results.hq_only.length > 0) {
  console.log('ARMIES NEEDING CORRECTION:');
  console.log('-'.repeat(80));
  for (const army of results.hq_only) {
    console.log(`  ${army.designation} (${army.quarter})`);
    console.log(`    Current: ${army.personnel?.toLocaleString() || 'N/A'} personnel, ${army.tanks || 0} tanks`);
    if (army.expected) {
      console.log(`    Expected: ${army.expected.personnel.toLocaleString()} personnel, ${army.expected.tanks} tanks`);
    }
    console.log(`    File: ${army.file}`);
    console.log('');
  }
}

if (results.correct.length > 0) {
  console.log('\nARMIES WITH CORRECT AGGREGATION:');
  console.log('-'.repeat(80));
  for (const army of results.correct) {
    console.log(`  ${army.designation} (${army.quarter})`);
    console.log(`    Personnel: ${army.personnel.toLocaleString()}, Tanks: ${army.tanks}`);
    console.log('');
  }
}

// Export results to JSON for further processing
const reportPath = path.join(__dirname, '..', 'ARMY_AGGREGATION_AUDIT.json');
fs.writeFileSync(reportPath, JSON.stringify({
  date: new Date().toISOString(),
  total_armies: totalArmies,
  results,
  summary: {
    correct: results.correct.length,
    needs_fix: results.hq_only.length,
    no_subordinates: results.no_subordinates.length,
    missing_files: results.missing_file.length
  }
}, null, 2));

console.log(`\nDetailed results saved to: ARMY_AGGREGATION_AUDIT.json`);
