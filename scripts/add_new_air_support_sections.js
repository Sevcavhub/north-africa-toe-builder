#!/usr/bin/env node

/**
 * Add air_support sections to Army-level ground forces units for new quarters
 *
 * Integrates:
 * - British 1941-Q4 8th Army
 * - British 1942-Q4 8th Army & 1st Army
 * - Italian 1941-Q1 10th Army
 * - German 1943-Q1 5th Panzer Army & Panzerarmee Afrika
 */

const fs = require('fs');
const path = require('path');

const unitsDir = path.join(__dirname, '..', 'data', 'output', 'units');
const airSummariesDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');

// Define integrations: Army JSON + Air Summary JSON
const integrations = [
  {
    army: 'british_1941q4_eighth_army_8th_army_toe.json',
    airSummary: 'british_1941q4_air_summary.json'
  },
  {
    army: 'british_1942q4_eighth_army_8th_army_toe.json',
    airSummary: 'british_1942q4_air_summary.json'
  },
  {
    army: 'british_1942q4_first_army_toe.json',
    airSummary: 'british_1942q4_air_summary.json',
    note: 'Same RAF air forces support both 8th and 1st Armies in theater'
  },
  {
    army: 'italian_1941q1_10_armata_italian_10th_army_toe.json',
    airSummary: 'italian_1941q1_air_summary.json'
  },
  {
    army: 'german_1943q1_5th_panzer_army_toe.json',
    airSummary: 'german_1943q1_air_summary.json'
  },
  {
    army: 'german_1943q1_panzerarmee_afrika_toe.json',
    airSummary: 'german_1943q1_air_summary.json',
    note: 'Both Panzer armies supported by same Luftwaffe forces'
  }
];

console.log('Adding air_support sections to 6 Army-level units...\n');

integrations.forEach(({ army, airSummary, note }) => {
  // Read both files
  const armyPath = path.join(unitsDir, army);
  const airPath = path.join(airSummariesDir, airSummary);

  const armyData = JSON.parse(fs.readFileSync(armyPath, 'utf8'));
  const airData = JSON.parse(fs.readFileSync(airPath, 'utf8'));

  // Build air_support section
  const airSupport = {
    air_summary_reference: airSummary.replace('_air_summary.json', ''),
    theater_air_command: {
      designation: airData.air_command_structure.theater_command.designation,
      commander: airData.air_command_structure.theater_command.commander,
      headquarters: airData.air_command_structure.theater_command.headquarters
    },
    aggregate_strength: {
      total_aircraft: airData.aggregate_strength.total_aircraft,
      operational_aircraft: airData.aggregate_strength.operational_aircraft,
      serviceability_rate: airData.aggregate_strength.serviceability_rate
    },
    organizational_summary: {
      total_units: airData.aggregate_strength.by_unit_composition?.total_squadrons
        || airData.aggregate_strength.known_units?.length
        || 'See air summary',
      unit_composition: airData.aggregate_strength.by_unit_composition
        || airData.aggregate_strength.note
        || 'See air summary for detailed composition'
    },
    data_source: {
      summary_file: airSummary,
      confidence: airData.metadata.confidence,
      tier: airData.metadata.tier,
      extraction_method: airData.metadata.extraction_method
    }
  };

  if (note) {
    airSupport.integration_note = note;
  }

  // Insert air_support section before validation
  const updatedData = { ...armyData };
  const { validation, ...rest } = updatedData;

  const finalData = {
    ...rest,
    air_support: airSupport,
    validation
  };

  // Write updated file
  fs.writeFileSync(armyPath, JSON.stringify(finalData, null, 2));

  console.log(`✓ ${army}`);
  console.log(`  + Added air_support from ${airSummary}`);
  console.log(`  - ${airSupport.aggregate_strength.total_aircraft} aircraft, ${airSupport.aggregate_strength.operational_aircraft} operational`);
  if (note) {
    console.log(`  - Note: ${note}`);
  }
  console.log();
});

console.log('='.repeat(60));
console.log('✓ Added air_support sections to 6 Army-level units');
console.log('='.repeat(60));
