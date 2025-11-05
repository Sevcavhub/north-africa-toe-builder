const fs = require('fs');
const path = require('path');

/**
 * Analyzes all completed units to determine battle participation
 * Creates filtered lists for different inclusion criteria
 */

const unitsDir = path.join(__dirname, '../data/output/units');
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

console.log('=== BATTLE PARTICIPATION ANALYSIS ===\n');
console.log(`Analyzing ${files.length} completed units...\n`);

const categories = {
  combatUnits: [],           // Units with documented combat
  defensiveBattles: [],      // Garrison units that fought defensively
  destroyed: [],             // Units destroyed/disbanded in combat
  mobileDivisions: [],       // Armored/motorized/infantry divisions
  corps: [],                 // Corps-level formations
  garrison: [],              // Garrison with no clear combat record
  unknownCombat: []          // Combat status unclear
};

for (const file of files) {
  const filePath = path.join(unitsDir, file);
  let unit;

  try {
    unit = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (err) {
    console.warn(`⚠️  Skipping ${file} - JSON parse error`);
    continue;
  }

  const unitId = file.replace('_toe.json', '');
  const designation = unit.unit_designation || '';
  const theater = unit.theater || '';
  const orgLevel = unit.organization_level || '';

  // Check for combat participation
  const engagements = unit.wargaming_data?.historical_engagements || [];
  const context = unit.historical_context?.period_summary || '';
  const operations = unit.operational_history || '';

  const combatText = (engagements.join(' ') + ' ' + context + ' ' + operations).toLowerCase();

  let hasCombat = false;
  let isDefensive = false;
  let wasDestroyed = false;
  let isMobile = false;
  let isCorps = orgLevel.toLowerCase().includes('corps') || orgLevel.toLowerCase().includes('army');
  let isGarrison = designation.toLowerCase().includes('garrison') ||
                   designation.toLowerCase().includes('static') ||
                   designation.match(/\d+(st|nd|rd|th)\s+(sirte|marmarica|cirene|sabratha)/i);

  // Check for combat indicators
  if (combatText.includes('operation') ||
      combatText.includes('battle') ||
      combatText.includes('offensive') ||
      combatText.includes('attack') ||
      combatText.includes('assault')) {
    hasCombat = true;
  }

  // Check for defensive combat
  if (combatText.includes('defense') ||
      combatText.includes('defensive') ||
      combatText.includes('retreat') ||
      combatText.includes('withdrawal')) {
    hasCombat = true;
    isDefensive = true;
  }

  // Check if destroyed
  if (combatText.includes('destroyed') ||
      combatText.includes('disbanded') ||
      combatText.includes('annihilated') ||
      combatText.includes('surrendered') ||
      combatText.includes('captured')) {
    wasDestroyed = true;
    hasCombat = true;
  }

  // Check if mobile division
  if (designation.match(/panzer|armou?red|motorized|mechanized|cavalry/i) ||
      (orgLevel.toLowerCase().includes('division') && !isGarrison)) {
    isMobile = true;
  }

  // Categorize
  const unitData = {
    id: unitId,
    designation: designation,
    nation: unitId.split('_')[0],
    quarter: unitId.split('_')[1],
    orgLevel: orgLevel,
    engagements: engagements.length,
    theater: theater
  };

  if (isCorps) {
    categories.corps.push(unitData);
  }

  if (wasDestroyed) {
    categories.destroyed.push(unitData);
  }

  if (hasCombat) {
    categories.combatUnits.push(unitData);
    if (isDefensive && isGarrison) {
      categories.defensiveBattles.push(unitData);
    }
  } else if (isGarrison) {
    categories.garrison.push(unitData);
  } else if (!hasCombat && engagements.length === 0) {
    categories.unknownCombat.push(unitData);
  }

  if (isMobile) {
    categories.mobileDivisions.push(unitData);
  }
}

// Output results
console.log('=== SUMMARY BY CATEGORY ===\n');
console.log(`✅ Combat Units: ${categories.combatUnits.length}`);
console.log(`   - Mobile Divisions: ${categories.mobileDivisions.length}`);
console.log(`   - Corps/Army: ${categories.corps.length}`);
console.log(`   - Defensive Battles (Garrison): ${categories.defensiveBattles.length}`);
console.log(`   - Destroyed in Combat: ${categories.destroyed.length}`);
console.log(`\n❓ Unknown Combat Status: ${categories.unknownCombat.length}`);
console.log(`📍 Pure Garrison (No Combat): ${categories.garrison.length}`);
console.log('');

// Detailed breakdown
console.log('=== GARRISON DIVISIONS THAT FOUGHT DEFENSIVELY ===');
categories.defensiveBattles.forEach(u => {
  console.log(`  - ${u.designation} (${u.quarter})`);
  console.log(`    Engagements: ${u.engagements}`);
});
console.log('');

console.log('=== UNITS DESTROYED/DISBANDED IN COMBAT ===');
categories.destroyed.slice(0, 15).forEach(u => {
  console.log(`  - ${u.designation} (${u.quarter})`);
});
if (categories.destroyed.length > 15) {
  console.log(`  ... and ${categories.destroyed.length - 15} more\n`);
}
console.log('');

console.log('=== UNKNOWN COMBAT STATUS (Need Review) ===');
categories.unknownCombat.forEach(u => {
  console.log(`  - ${u.designation} (${u.quarter})`);
  console.log(`    Theater: ${u.theater}`);
});
console.log('');

console.log('=== PURE GARRISON (No Documented Combat) ===');
categories.garrison.forEach(u => {
  console.log(`  - ${u.designation} (${u.quarter})`);
});
console.log('');

// Save results
const output = {
  analysis_date: new Date().toISOString(),
  total_units_analyzed: files.length,
  scope_recommendation: "Modified Hybrid Approach",
  criteria: "Include all units physically in Africa that participated in battles (offensive or defensive)",
  categories: {
    combat_units: categories.combatUnits.length,
    mobile_divisions: categories.mobileDivisions.length,
    corps_formations: categories.corps.length,
    defensive_garrison_battles: categories.defensiveBattles.length,
    destroyed_in_combat: categories.destroyed.length,
    unknown_combat: categories.unknownCombat.length,
    pure_garrison_no_combat: categories.garrison.length
  },
  units_by_category: {
    combat_units: categories.combatUnits.map(u => u.id),
    defensive_battles: categories.defensiveBattles.map(u => u.id),
    destroyed: categories.destroyed.map(u => u.id),
    mobile_divisions: categories.mobileDivisions.map(u => u.id),
    corps: categories.corps.map(u => u.id),
    garrison_no_combat: categories.garrison.map(u => u.id),
    unknown_combat: categories.unknownCombat.map(u => u.id)
  }
};

const outputPath = path.join(__dirname, '../data/output/BATTLE_PARTICIPATION_ANALYSIS.json');
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
console.log(`\n✅ Analysis saved to: ${outputPath}\n`);

// Scope recommendation
console.log('=== SCOPE RECOMMENDATION ===');
console.log('');
console.log('**Modified Hybrid Approach**: Include all units that were physically in Africa AND:');
console.log('  1. Participated in offensive operations, OR');
console.log('  2. Participated in defensive battles (including garrison units), OR');
console.log('  3. Were destroyed/disbanded due to combat');
console.log('');
console.log('**INCLUDE**:');
console.log(`  - ${categories.combatUnits.length} combat units (offensive + defensive)`);
console.log(`  - Includes ${categories.defensiveBattles.length} garrison divisions that fought defensively`);
console.log('');
console.log('**EXCLUDE**:');
console.log(`  - ${categories.garrison.length} pure garrison units with no documented combat`);
console.log(`  - Need manual review: ${categories.unknownCombat.length} units with unclear combat status`);
console.log('');
console.log(`**CURRENT STATUS**: ${categories.combatUnits.length} battle-participating units completed`);
