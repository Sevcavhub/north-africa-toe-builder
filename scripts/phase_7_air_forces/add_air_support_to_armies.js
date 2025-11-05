#!/usr/bin/env node

/**
 * Add air_support sections to Army-level ground forces JSONs
 *
 * Integrates quarterly air summaries with corresponding Army/Corps-level units
 */

const fs = require('fs');
const path = require('path');

const unitsDir = path.join(__dirname, '..', 'data', 'output', 'units');
const airSummariesDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');

// Mappings: Army JSON → Air Summary JSON
const integrations = [
  {
    army: 'british_1942q2_eighth_army_8th_army_toe.json',
    airSummary: 'british_1942q2_air_summary.json',
    commandDesignation: 'RAF Desert Air Force',
    commander: 'Air Vice-Marshal Arthur Coningham'
  },
  {
    army: 'british_1942q3_eighth_army_8th_army_toe.json',
    airSummary: 'british_1942q3_air_summary.json',
    commandDesignation: 'RAF Desert Air Force',
    commander: 'Air Vice-Marshal Arthur Coningham'
  },
  {
    army: 'german_1942q2_panzerarmee_afrika_toe.json',
    airSummary: 'german_1942q2_air_summary.json',
    commandDesignation: 'Fliegerführer Afrika',
    commander: 'Unknown'
  },
  {
    army: 'italian_1942q1_xxi_corpo_d_armata_xxi_corps_toe.json',
    airSummary: 'italian_1942q1_air_summary.json',
    commandDesignation: 'Regia Aeronautica - North Africa',
    commander: 'Unknown'
  },
  {
    army: 'italian_1942q2_xxi_corpo_d_armata_xxi_corps_toe.json',
    airSummary: 'italian_1942q2_air_summary.json',
    commandDesignation: 'Regia Aeronautica - North Africa',
    commander: 'Unknown'
  }
];

console.log('Adding air_support sections to Army-level JSONs...\n');

integrations.forEach(integration => {
  try {
    // Read Army JSON
    const armyPath = path.join(unitsDir, integration.army);
    const armyData = JSON.parse(fs.readFileSync(armyPath, 'utf8'));

    // Read Air Summary JSON
    const airPath = path.join(airSummariesDir, integration.airSummary);
    const airData = JSON.parse(fs.readFileSync(airPath, 'utf8'));

    // Extract key air data
    const totalAircraft = airData.aggregate_strength.total_aircraft;
    const operationalAircraft = airData.aggregate_strength.operational_aircraft;
    const serviceability = airData.aggregate_strength.serviceability_rate;
    const unitCount = airData.aggregate_strength.by_unit?.length || 0;

    // Get key aircraft types
    let aircraftTypes = [];
    if (airData.aggregate_strength.by_unit && airData.aggregate_strength.by_unit.length > 0) {
      // Extract unique aircraft types from unit list
      const typesSet = new Set();
      airData.aggregate_strength.by_unit.forEach(unit => {
        unit.aircraft_types?.forEach(type => typesSet.add(type));
      });
      aircraftTypes = Array.from(typesSet).slice(0, 6); // Top 6 types
    } else if (airData.aggregate_strength.aircraft_types) {
      // Italian format with categorized types
      const types = airData.aggregate_strength.aircraft_types;
      aircraftTypes = [
        ...(types.fighters || []).slice(0, 3),
        ...(types.bombers || []).slice(0, 2),
        ...(types.reconnaissance || []).slice(0, 1)
      ];
    }

    // Create air_support section
    const airSupport = {
      theater_air_command: {
        designation: integration.commandDesignation,
        commander: integration.commander,
        headquarters: airData.air_command_structure.theater_command.headquarters || "Unknown"
      },
      aggregate_strength: {
        total_aircraft: totalAircraft,
        operational_aircraft: operationalAircraft,
        serviceability_rate: serviceability,
        unit_count: unitCount,
        note: airData.aggregate_strength.note || `Data from ${airData.source_document.title}`
      },
      key_aircraft_types: aircraftTypes,
      organizational_summary: `${unitCount} operational units providing air support to ground forces`,
      source: {
        file: airData.source_document.file,
        title: airData.source_document.title,
        date: airData.source_document.date,
        confidence: airData.metadata.confidence,
        tier: airData.metadata.tier
      },
      integration_note: `Air forces data integrated from quarterly air summary. See ${integration.airSummary} for detailed squadron/gruppo breakdown.`
    };

    // Insert air_support section before validation
    // Find where validation starts
    const armyDataCopy = { ...armyData };
    const validation = armyDataCopy.validation;
    const metadata = armyDataCopy.metadata;
    const aggregationStatus = armyDataCopy.aggregation_status;
    const aggregationDate = armyDataCopy.aggregation_date;
    const aggregationNotes = armyDataCopy.aggregation_notes;

    // Remove these fields
    delete armyDataCopy.validation;
    delete armyDataCopy.metadata;
    delete armyDataCopy.aggregation_status;
    delete armyDataCopy.aggregation_date;
    delete armyDataCopy.aggregation_notes;

    // Build new structure with air_support before validation
    const updatedArmy = {
      ...armyDataCopy,
      air_support: airSupport,
      validation: validation,
      metadata: {
        ...metadata,
        air_support_integration_date: new Date().toISOString().split('T')[0],
        air_support_source: integration.airSummary
      },
      aggregation_status: aggregationStatus,
      aggregation_date: aggregationDate,
      aggregation_notes: aggregationNotes
    };

    // Write updated Army JSON
    fs.writeFileSync(armyPath, JSON.stringify(updatedArmy, null, 2));

    console.log(`✓ ${integration.army}`);
    console.log(`  - Nation: ${armyData.nation}`);
    console.log(`  - Quarter: ${armyData.quarter}`);
    console.log(`  - Air support: ${totalAircraft} total aircraft (${operationalAircraft} operational)`);
    console.log(`  - Units: ${unitCount} squadrons/gruppi`);
    console.log(`  - Confidence: ${airData.metadata.confidence}%`);
    console.log();

  } catch (error) {
    console.error(`✗ Failed to process ${integration.army}:`, error.message);
    console.log();
  }
});

console.log('✓ Air support integration complete');
console.log('\nNext steps:');
console.log('1. Regenerate MDBook chapters with air sections');
console.log('2. Create quarterly theater overview chapters');
console.log('3. Update documentation');
