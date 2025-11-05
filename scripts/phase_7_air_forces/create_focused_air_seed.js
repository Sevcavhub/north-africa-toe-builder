#!/usr/bin/env node
/**
 * Create focused air forces seed - MAJOR BATTLES ONLY
 * Reduces scope from 761 unit-quarters to ~120-150
 */

const fs = require('fs');
const path = require('path');

// Major battles by quarter
const MAJOR_BATTLES = {
  '1940-Q4': ['Operation Compass'],
  '1941-Q2': ['Operation Battleaxe', 'Siege of Tobruk'],
  '1941-Q4': ['Operation Crusader'],
  '1942-Q2': ['Gazala', 'Battle of Gazala'],
  '1942-Q3': ['First El Alamein', 'First Battle of El Alamein'],
  '1942-Q4': ['Second El Alamein', 'Second Battle of El Alamein', 'Operation Torch'],
  '1943-Q1': ['Tunisia Campaign']
};

const MAJOR_BATTLE_QUARTERS = Object.keys(MAJOR_BATTLES);

console.log('🎯 Creating Focused Air Forces Seed - Major Battles Only\n');
console.log('Major Battle Quarters:', MAJOR_BATTLE_QUARTERS.join(', '), '\n');

// Read full seed file
const seedPath = path.join(__dirname, '..', 'projects', 'north_africa_air_units_seed_COMPLETE.json');
const fullSeed = JSON.parse(fs.readFileSync(seedPath, 'utf8'));

// Filter function
function filterUnitToMajorBattles(unit) {
  // Filter quarters to only major battle quarters
  const majorQuarters = unit.quarters.filter(q => MAJOR_BATTLE_QUARTERS.includes(q));

  if (majorQuarters.length === 0) {
    return null; // Unit not in any major battle
  }

  // Check if unit participated in actual major battles
  const battles = unit.battles || [];
  const participatedInMajorBattle = battles.some(battle => {
    return MAJOR_BATTLE_QUARTERS.some(quarter => {
      const majorBattlesForQuarter = MAJOR_BATTLES[quarter];
      return majorBattlesForQuarter.some(majorBattle =>
        battle.toLowerCase().includes(majorBattle.toLowerCase()) ||
        majorBattle.toLowerCase().includes(battle.toLowerCase())
      );
    });
  });

  if (!participatedInMajorBattle && battles.length > 0) {
    // Has battles listed but none are major - skip unless it's a command/headquarters unit
    if (!unit.type.includes('command') && !unit.type.includes('staff')) {
      return null;
    }
  }

  // Return filtered unit
  return {
    ...unit,
    quarters: majorQuarters
  };
}

// Filter all nation units
const focusedSeed = {
  comment: "North Africa Air Forces - MAJOR BATTLES ONLY (Focused Scope)",
  description: "Focused list of air units that participated in MAJOR North Africa battles only. Reduces scope for Phase 7 initial extraction.",
  validation_date: new Date().toISOString().split('T')[0],
  validation_sources: fullSeed.validation_sources,
  battles_covered: [
    "Operation Compass (1940-Q4)",
    "Operation Battleaxe / Siege of Tobruk (1941-Q2)",
    "Operation Crusader (1941-Q4)",
    "Battle of Gazala (1942-Q2)",
    "First Battle of El Alamein (1942-Q3)",
    "Second Battle of El Alamein / Operation Torch (1942-Q4)",
    "Tunisia Campaign (1943-Q1)"
  ],
  scope_rule: "ONLY air units that participated in the 7 major North Africa battles. Excludes routine garrison, convoy escort, and minor operations.",
  total_units: 0, // Will calculate
  total_unit_quarters: 0, // Will calculate
  by_nation: {
    luftwaffe: 0,
    regia_aeronautica: 0,
    raf_commonwealth: 0,
    usaaf: 0
  },
  data_quality_note: fullSeed.data_quality_note,
  luftwaffe_units: [],
  regia_aeronautica_units: [],
  raf_commonwealth_units: [],
  usaaf_units: []
};

// Process each nation
['luftwaffe_units', 'regia_aeronautica_units', 'raf_commonwealth_units', 'usaaf_units'].forEach(nationKey => {
  const units = fullSeed[nationKey] || [];
  const filtered = units
    .map(filterUnitToMajorBattles)
    .filter(u => u !== null);

  focusedSeed[nationKey] = filtered;

  // Count
  const nationName = nationKey.replace('_units', '');
  focusedSeed.by_nation[nationName] = filtered.length;
  focusedSeed.total_units += filtered.length;

  // Count unit-quarters
  const unitQuarters = filtered.reduce((sum, u) => sum + u.quarters.length, 0);
  focusedSeed.total_unit_quarters += unitQuarters;

  console.log(`${nationKey}: ${filtered.length} units (${unitQuarters} unit-quarters)`);
});

console.log(`\n✅ Total: ${focusedSeed.total_units} units (${focusedSeed.total_unit_quarters} unit-quarters)`);
console.log(`📊 Reduction: ${fullSeed.total_unit_quarters} → ${focusedSeed.total_unit_quarters} (${Math.round((1 - focusedSeed.total_unit_quarters / fullSeed.total_unit_quarters) * 100)}% reduction)\n`);

// Write focused seed
const outputPath = path.join(__dirname, '..', 'projects', 'north_africa_air_units_seed_FOCUSED.json');
fs.writeFileSync(outputPath, JSON.stringify(focusedSeed, null, 2));
console.log(`📝 Written: ${outputPath}`);
