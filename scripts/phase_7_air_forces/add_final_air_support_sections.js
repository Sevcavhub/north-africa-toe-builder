#!/usr/bin/env node

/**
 * Add air_support sections to Army-level units for final quarterly expansion
 *
 * Integrates:
 * - 1941-Q3: British 8th Army, German Panzergruppe Afrika, Italian XXI Corps
 * - 1942-Q3: German Panzerarmee Afrika, Italian XXI Corps (British already done)
 * - 1942-Q4: German/Italian already done in previous expansion
 * - 1943-Q1: Already done in previous expansion
 */

const fs = require('fs');
const path = require('path');

const unitsDir = path.join(__dirname, '..', 'data', 'output', 'units');
const airSummariesDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');

// Define integrations: Army JSON + Air Summary JSON
const integrations = [
  // 1941-Q3
  {
    army: 'british_1941q3_eighth_army_8th_army_toe.json',
    airSummary: 'british_1941q3_air_summary.json'
  },
  {
    army: 'german_1941q3_panzergruppe_afrika_toe.json',
    airSummary: 'german_1941q3_air_summary.json'
  },
  {
    army: 'italian_1941q3_xxi_corpo_d_armata_xxi_corps_toe.json',
    airSummary: 'italian_1941q3_air_summary.json'
  },
  // 1942-Q3
  {
    army: 'german_1942q3_panzerarmee_afrika_toe.json',
    airSummary: 'german_1942q3_air_summary.json'
  },
  {
    army: 'italian_1942q3_xxi_corpo_d_armata_xxi_corps_toe.json',
    airSummary: 'italian_1942q3_air_summary.json'
  }
];

console.log('Adding air_support sections to 5 Army-level units...\n');

integrations.forEach(({ army, airSummary, note }) => {
  // Read both files
  const armyPath = path.join(unitsDir, army);
  const airPath = path.join(airSummariesDir, airSummary);

  if (!fs.existsSync(armyPath)) {
    console.log(`⚠️  Skipping ${army} - file not found`);
    console.log();
    return;
  }

  if (!fs.existsSync(airPath)) {
    console.log(`⚠️  Skipping ${airSummary} - file not found`);
    console.log();
    return;
  }

  const armyData = JSON.parse(fs.readFileSync(armyPath, 'utf8'));
  const airData = JSON.parse(fs.readFileSync(airPath, 'utf8'));

  // Skip if already has air_support
  if (armyData.air_support) {
    console.log(`⏭️  Skipping ${army} - already has air_support section`);
    console.log();
    return;
  }

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
        || airData.aggregate_strength.by_unit_composition?.squadrons_total
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
console.log('✓ Added air_support sections to 5 Army-level units');
console.log('='.repeat(60));
