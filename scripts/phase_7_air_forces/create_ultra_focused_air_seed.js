#!/usr/bin/env node
/**
 * Create ULTRA-focused air forces seed - ONE QUARTER PER UNIT
 * Peak battle quarter only
 */

const fs = require('fs');
const path = require('path');

// Major battles ranked by priority (most significant)
const BATTLE_PRIORITY = {
  '1942-Q4': 10, // Second El Alamein - turning point
  '1941-Q4': 9,  // Operation Crusader
  '1943-Q1': 8,  // Tunisia Campaign
  '1942-Q2': 7,  // Battle of Gazala
  '1942-Q3': 6,  // First El Alamein
  '1941-Q2': 5,  // Operation Battleaxe
  '1940-Q4': 4   // Operation Compass
};

const MAJOR_QUARTERS = Object.keys(BATTLE_PRIORITY);

console.log('🎯 Creating ULTRA-Focused Air Forces Seed - ONE QUARTER PER UNIT\n');

// Read focused seed
const seedPath = path.join(__dirname, '..', 'projects', 'north_africa_air_units_seed_FOCUSED.json');
const focusedSeed = JSON.parse(fs.readFileSync(seedPath, 'utf8'));

// Select BEST quarter for each unit
function selectPeakQuarter(unit) {
  // Filter to major battle quarters
  const majorQuarters = unit.quarters.filter(q => MAJOR_QUARTERS.includes(q));

  if (majorQuarters.length === 0) {
    return null;
  }

  // Select highest priority quarter
  const peakQuarter = majorQuarters.sort((a, b) => {
    return BATTLE_PRIORITY[b] - BATTLE_PRIORITY[a];
  })[0];

  return {
    ...unit,
    quarters: [peakQuarter],
    notes: unit.notes + ` [ULTRA-FOCUSED: Peak quarter ${peakQuarter} selected]`
  };
}

// Create ultra-focused seed
const ultraSeed = {
  comment: "North Africa Air Forces - ULTRA-FOCUSED (Peak Quarter Only)",
  description: "ONE quarter per unit - their most significant battle quarter. For Phase 7 initial proof-of-concept extraction.",
  validation_date: new Date().toISOString().split('T')[0],
  validation_sources: focusedSeed.validation_sources,
  battles_covered: focusedSeed.battles_covered,
  scope_rule: "ONE quarter per unit - peak battle quarter only (highest priority battle they participated in).",
  total_units: 0,
  total_unit_quarters: 0,
  by_nation: {
    luftwaffe: 0,
    regia_aeronautica: 0,
    raf_commonwealth: 0,
    usaaf: 0
  },
  data_quality_note: focusedSeed.data_quality_note,
  luftwaffe_units: [],
  regia_aeronautica_units: [],
  raf_commonwealth_units: [],
  usaaf_units: []
};

// Process each nation
['luftwaffe_units', 'regia_aeronautica_units', 'raf_commonwealth_units', 'usaaf_units'].forEach(nationKey => {
  const units = focusedSeed[nationKey] || [];
  const ultraFocused = units
    .map(selectPeakQuarter)
    .filter(u => u !== null);

  ultraSeed[nationKey] = ultraFocused;

  // Count
  const nationName = nationKey.replace('_units', '');
  ultraSeed.by_nation[nationName] = ultraFocused.length;
  ultraSeed.total_units += ultraFocused.length;
  ultraSeed.total_unit_quarters += ultraFocused.length; // 1 quarter per unit

  console.log(`${nationKey}: ${ultraFocused.length} units (${ultraFocused.length} unit-quarters)`);
});

console.log(`\n✅ Total: ${ultraSeed.total_units} units (${ultraSeed.total_unit_quarters} unit-quarters)`);
console.log(`📊 Reduction: ${focusedSeed.total_unit_quarters} → ${ultraSeed.total_unit_quarters} (${Math.round((1 - ultraSeed.total_unit_quarters / focusedSeed.total_unit_quarters) * 100)}% reduction)\n`);

// Write ultra-focused seed
const outputPath = path.join(__dirname, '..', 'projects', 'north_africa_air_units_seed_ULTRA_FOCUSED.json');
fs.writeFileSync(outputPath, JSON.stringify(ultraSeed, null, 2));
console.log(`📝 Written: ${outputPath}`);
console.log(`\n🚀 Ready for Phase 7 extraction with manageable scope!`);
