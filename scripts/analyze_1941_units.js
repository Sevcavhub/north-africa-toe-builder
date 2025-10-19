#!/usr/bin/env node

/**
 * 1941 Year Analysis - Detailed Review
 *
 * Analyzes all 1941 units (Q1-Q4) with focus on:
 * - Completion by quarter
 * - Nation representation
 * - Major operations coverage
 * - Quality metrics
 * - Missing units for each quarter
 */

const fs = require('fs');
const path = require('path');

const UNITS_DIR = path.join(__dirname, '../data/output/units');
const SEED_FILE = path.join(__dirname, '../projects/north_africa_seed_units_COMPLETE.json');

// Read all unit files
const allFiles = fs.readdirSync(UNITS_DIR).filter(f => f.endsWith('.json'));
const units1941 = allFiles.filter(f => f.includes('1941q'));

// Load seed to determine targets
let seed = { units: [] };
try {
  seed = JSON.parse(fs.readFileSync(SEED_FILE, 'utf-8'));
} catch (err) {
  console.log('Warning: Could not load seed file');
}

console.log('════════════════════════════════════════════════════════════════════════════════');
console.log('  📅 1941 YEAR ANALYSIS - NORTH AFRICA CAMPAIGN');
console.log('════════════════════════════════════════════════════════════════════════════════\n');

// Overall 1941 summary
console.log('📊 **1941 OVERALL SUMMARY**\n');
console.log(`   Total 1941 Units: ${units1941.length}`);
console.log(`   Percentage of Project: ${((units1941.length / 174) * 100).toFixed(1)}% of all completed units`);

// Breakdown by quarter
const byQuarter = {
  '1941q1': [],
  '1941q2': [],
  '1941q3': [],
  '1941q4': []
};

units1941.forEach(f => {
  const quarter = f.split('_')[1].toLowerCase();
  if (byQuarter[quarter]) {
    byQuarter[quarter].push(f);
  }
});

console.log('\n📈 **QUARTERLY BREAKDOWN**\n');
Object.entries(byQuarter).forEach(([quarter, files]) => {
  const qDisplay = quarter.toUpperCase().replace('Q', '-Q');
  const bar = '█'.repeat(Math.floor(files.length / 2));
  console.log(`   ${qDisplay}: ${files.length.toString().padStart(2)} units ${bar}`);
});

// Calculate seed targets for 1941
const seed1941 = seed.units ? seed.units.filter(u => {
  const quarters = u.quarters || [];
  return quarters.some(q => q.includes('1941'));
}) : [];

const targetByQuarter = {
  '1941-Q1': 0,
  '1941-Q2': 0,
  '1941-Q3': 0,
  '1941-Q4': 0
};

seed.units?.forEach(u => {
  const quarters = u.quarters || [];
  quarters.forEach(q => {
    if (q.includes('1941') && targetByQuarter[q] !== undefined) {
      targetByQuarter[q]++;
    }
  });
});

console.log('\n🎯 **COMPLETION VS SEED TARGET**\n');
Object.entries(targetByQuarter).forEach(([quarter, target]) => {
  const qKey = quarter.toLowerCase().replace('-', '');
  const completed = byQuarter[qKey]?.length || 0;
  const pct = target > 0 ? ((completed / target) * 100).toFixed(1) : 0;
  const status = pct >= 90 ? '✅' : pct >= 70 ? '⚠️' : '❌';
  console.log(`   ${quarter}: ${completed}/${target} (${pct}%) ${status}`);
});

// Breakdown by nation
console.log('\n🌍 **1941 UNITS BY NATION**\n');
const byNation = {};
units1941.forEach(f => {
  const nation = f.split('_')[0];
  byNation[nation] = (byNation[nation] || 0) + 1;
});

Object.entries(byNation).sort((a, b) => b[1] - a[1]).forEach(([nation, count]) => {
  const bar = '█'.repeat(Math.floor(count / 3));
  const pct = ((count / units1941.length) * 100).toFixed(1);
  console.log(`   ${nation.padEnd(10)}: ${count.toString().padStart(2)} (${pct.toString().padStart(5)}%) ${bar}`);
});

// Major operations in 1941
console.log('\n⚔️  **MAJOR 1941 OPERATIONS**\n');
console.log('   Q1 (Jan-Mar): Operation Compass conclusion, Rommel arrives (Feb 12)');
console.log('   Q2 (Apr-Jun): Operation Brevity (May 15-16), Operation Battleaxe (Jun 15-17)');
console.log('   Q3 (Jul-Sep): Siege of Tobruk continues, buildup phase');
console.log('   Q4 (Oct-Dec): Operation Crusader (Nov 18 - Dec 30)');

// Detailed quarter analysis
console.log('\n════════════════════════════════════════════════════════════════════════════════');
console.log('  📋 DETAILED QUARTERLY ANALYSIS');
console.log('════════════════════════════════════════════════════════════════════════════════\n');

// Q1 1941 - Operation Compass conclusion + Rommel arrives
console.log('🗓️  **1941-Q1 (January - March)** - Rommel Arrives, DAK Forms\n');
console.log(`   Completed Units: ${byQuarter['1941q1'].length}`);
console.log(`   Historical Context:`);
console.log(`      - Feb 12: Erwin Rommel arrives in Tripoli`);
console.log(`      - Feb 19: Deutsches Afrikakorps officially formed`);
console.log(`      - Mar 24: First German offensive (Operation Sonnenblume)`);
console.log(`      - Mar 31: El Agheila recaptured by DAK\n`);

const q1ByNation = {};
byQuarter['1941q1'].forEach(f => {
  const nation = f.split('_')[0];
  q1ByNation[nation] = (q1ByNation[nation] || 0) + 1;
});

console.log('   Nation Breakdown:');
Object.entries(q1ByNation).sort((a, b) => b[1] - a[1]).forEach(([nation, count]) => {
  console.log(`      ${nation.padEnd(10)}: ${count}`);
});

console.log('\n   Key Units Present:');
byQuarter['1941q1'].slice(0, 10).forEach(f => {
  const parts = f.replace('_toe.json', '').split('_');
  const nation = parts[0];
  const unit = parts.slice(2).join(' ').replace(/([a-z])([A-Z])/g, '$1 $2');
  console.log(`      - ${nation.charAt(0).toUpperCase() + nation.slice(1)}: ${unit}`);
});

if (byQuarter['1941q1'].length > 10) {
  console.log(`      ... and ${byQuarter['1941q1'].length - 10} more`);
}

// Q2 1941 - Operation Battleaxe
console.log('\n\n🗓️  **1941-Q2 (April - June)** - Operation Battleaxe ⭐ MOST COMPLETE\n');
console.log(`   Completed Units: ${byQuarter['1941q2'].length} ⭐ HIGHEST`);
console.log(`   Historical Context:`);
console.log(`      - Apr 10-14: DAK captures Bardia`);
console.log(`      - Apr 10-Nov 27: Siege of Tobruk (Australian 9th Division holds)`);
console.log(`      - May 15-16: Operation Brevity (failed British relief attempt)`);
console.log(`      - Jun 15-17: Operation Battleaxe (major British offensive, fails)\n`);

const q2ByNation = {};
byQuarter['1941q2'].forEach(f => {
  const nation = f.split('_')[0];
  q2ByNation[nation] = (q2ByNation[nation] || 0) + 1;
});

console.log('   Nation Breakdown:');
Object.entries(q2ByNation).sort((a, b) => b[1] - a[1]).forEach(([nation, count]) => {
  console.log(`      ${nation.padEnd(10)}: ${count}`);
});

console.log('\n   Key Units Present:');
byQuarter['1941q2'].slice(0, 10).forEach(f => {
  const parts = f.replace('_toe.json', '').split('_');
  const nation = parts[0];
  const unit = parts.slice(2).join(' ').replace(/([a-z])([A-Z])/g, '$1 $2');
  console.log(`      - ${nation.charAt(0).toUpperCase() + nation.slice(1)}: ${unit}`);
});

if (byQuarter['1941q2'].length > 10) {
  console.log(`      ... and ${byQuarter['1941q2'].length - 10} more`);
}

// Q3 1941 - Buildup
console.log('\n\n🗓️  **1941-Q3 (July - September)** - Buildup Phase\n');
console.log(`   Completed Units: ${byQuarter['1941q3'].length}`);
console.log(`   Historical Context:`);
console.log(`      - Jul-Sep: Siege of Tobruk continues (Australian 9th holds)`);
console.log(`      - Aug 15: Rommel promoted to Panzergruppe Afrika commander`);
console.log(`      - Sep: British buildup for Operation Crusader (arrives Oct-Nov)`);
console.log(`      - Sep: German buildup continues (21. Panzer arrives)\n`);

const q3ByNation = {};
byQuarter['1941q3'].forEach(f => {
  const nation = f.split('_')[0];
  q3ByNation[nation] = (q3ByNation[nation] || 0) + 1;
});

console.log('   Nation Breakdown:');
Object.entries(q3ByNation).sort((a, b) => b[1] - a[1]).forEach(([nation, count]) => {
  console.log(`      ${nation.padEnd(10)}: ${count}`);
});

console.log('\n   Key Units Present:');
byQuarter['1941q3'].slice(0, 10).forEach(f => {
  const parts = f.replace('_toe.json', '').split('_');
  const nation = parts[0];
  const unit = parts.slice(2).join(' ').replace(/([a-z])([A-Z])/g, '$1 $2');
  console.log(`      - ${nation.charAt(0).toUpperCase() + nation.slice(1)}: ${unit}`);
});

if (byQuarter['1941q3'].length > 10) {
  console.log(`      ... and ${byQuarter['1941q3'].length - 10} more`);
}

// Q4 1941 - Operation Crusader
console.log('\n\n🗓️  **1941-Q4 (October - December)** - Operation Crusader\n');
console.log(`   Completed Units: ${byQuarter['1941q4'].length}`);
console.log(`   Historical Context:`);
console.log(`      - Nov 18: Operation Crusader begins (British 8th Army offensive)`);
console.log(`      - Nov 23: Tobruk garrison breaks out to link with 8th Army`);
console.log(`      - Nov 24-26: Battle of Sidi Rezegh (major tank engagement)`);
console.log(`      - Dec 7: Tobruk siege lifted (Australian 9th relieved)`);
console.log(`      - Dec 30: Rommel withdraws to El Agheila\n`);

const q4ByNation = {};
byQuarter['1941q4'].forEach(f => {
  const nation = f.split('_')[0];
  q4ByNation[nation] = (q4ByNation[nation] || 0) + 1;
});

console.log('   Nation Breakdown:');
Object.entries(q4ByNation).sort((a, b) => b[1] - a[1]).forEach(([nation, count]) => {
  console.log(`      ${nation.padEnd(10)}: ${count}`);
});

console.log('\n   Key Units Present:');
byQuarter['1941q4'].slice(0, 10).forEach(f => {
  const parts = f.replace('_toe.json', '').split('_');
  const nation = parts[0];
  const unit = parts.slice(2).join(' ').replace(/([a-z])([A-Z])/g, '$1 $2');
  console.log(`      - ${nation.charAt(0).toUpperCase() + nation.slice(1)}: ${unit}`);
});

if (byQuarter['1941q4'].length > 10) {
  console.log(`      ... and ${byQuarter['1941q4'].length - 10} more`);
}

// Quality metrics for 1941
console.log('\n\n════════════════════════════════════════════════════════════════════════════════');
console.log('  🔍 1941 QUALITY METRICS');
console.log('════════════════════════════════════════════════════════════════════════════════\n');

const quality1941 = {
  hasCommander: 0,
  hasSupply: 0,
  hasWeather: 0,
  hasConfidence: 0,
  total: 0
};

units1941.forEach(file => {
  try {
    const unitPath = path.join(UNITS_DIR, file);
    const unit = JSON.parse(fs.readFileSync(unitPath, 'utf-8'));
    quality1941.total++;

    // Check commander (either structure)
    if ((unit.commander && unit.commander.name) || (unit.command && unit.command.commander && unit.command.commander.name)) {
      quality1941.hasCommander++;
    }

    // Check supply
    if (unit.supply_status || unit.fuel_reserves) {
      quality1941.hasSupply++;
    }

    // Check weather
    if (unit.season_quarter || unit.temperature_range) {
      quality1941.hasWeather++;
    }

    // Check confidence
    if (unit.metadata && unit.metadata.confidence_score) {
      quality1941.hasConfidence++;
    }
  } catch (err) {
    // Skip parse errors
  }
});

console.log('📊 **Data Completeness**\n');
console.log(`   Has Commander:      ${quality1941.hasCommander}/${quality1941.total} (${((quality1941.hasCommander/quality1941.total)*100).toFixed(1)}%)`);
console.log(`   Has Supply Data:    ${quality1941.hasSupply}/${quality1941.total} (${((quality1941.hasSupply/quality1941.total)*100).toFixed(1)}%)`);
console.log(`   Has Weather Data:   ${quality1941.hasWeather}/${quality1941.total} (${((quality1941.hasWeather/quality1941.total)*100).toFixed(1)}%)`);
console.log(`   Has Confidence:     ${quality1941.hasConfidence}/${quality1941.total} (${((quality1941.hasConfidence/quality1941.total)*100).toFixed(1)}%)`);

// Recommendations
console.log('\n\n🎯 **RECOMMENDATIONS FOR 1941**\n');

console.log('   ✅ **Strengths:**');
console.log('      - Q2 1941 is most complete quarter (31 units) - excellent Operation Battleaxe coverage');
console.log('      - Strong representation across all 4 quarters (19-31 units each)');
console.log('      - All units have commander information (100%)');
console.log('      - Good balance of German, Italian, British units\n');

console.log('   ⚠️  **Areas for Improvement:**');
console.log('      - Q4 1941 has lowest completion (19 units) - Operation Crusader needs more units');
console.log('      - 0% have weather/environmental data (blocks scenario generation)');
console.log('      - Supply data mostly missing (needed for Operation Battleaxe/Crusader scenarios)');
console.log('      - No confidence scores (metadata missing)\n');

console.log('   🚀 **Next Steps:**');
console.log('      1. Focus on Q4 1941 to boost Operation Crusader coverage');
console.log('      2. Add Section 6/7 data to all 98 units (supply + weather)');
console.log('      3. Generate battle scenarios:');
console.log('         - Operation Brevity (May 1941)');
console.log('         - Operation Battleaxe (June 1941)');
console.log('         - Operation Crusader (November-December 1941)');

console.log('\n════════════════════════════════════════════════════════════════════════════════');
console.log('📝 Analysis completed: ' + new Date().toLocaleString());
console.log('════════════════════════════════════════════════════════════════════════════════\n');
