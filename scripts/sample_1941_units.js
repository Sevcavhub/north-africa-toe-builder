#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const unitsDir = path.join(__dirname, '../data/output/units');
const units = fs.readdirSync(unitsDir)
  .filter(f => f.includes('1941q') && f.endsWith('.json'));

// Sample one from each quarter
const samples = {
  'Q1': units.find(f => f.includes('1941q1_deutsches')),
  'Q2': units.find(f => f.includes('1941q2_deutsches_afrikakorps_dak')),
  'Q3': units.find(f => f.includes('1941q3_deutsches')),
  'Q4': units.find(f => f.includes('1941q4_deutsches'))
};

console.log('📋 SAMPLE 1941 UNITS - DATA STRUCTURE CHECK\n');

Object.entries(samples).forEach(([quarter, file]) => {
  if (!file) return;

  const unit = JSON.parse(fs.readFileSync(path.join(unitsDir, file), 'utf-8'));

  console.log('═'.repeat(80));
  console.log(`1941-${quarter}: ${file.replace('_toe.json', '')}`);
  console.log('═'.repeat(80));

  // Check schema structure
  console.log(`\nSchema: ${unit.schema_version || 'UNKNOWN'}`);
  console.log(`Nation: ${unit.nation || unit.unit_identification?.nation || 'MISSING'}`);
  console.log(`Quarter: ${unit.quarter || unit.unit_identification?.quarter || 'MISSING'}`);
  console.log(`Organization: ${unit.organization_level || 'MISSING'}`);

  // Check commander structure
  if (unit.commander && unit.commander.name) {
    console.log(`Commander: ✅ Top-level - ${unit.commander.name}`);
  } else if (unit.command && unit.command.commander && unit.command.commander.name) {
    console.log(`Commander: ⚠️  Nested - ${unit.command.commander.name}`);
  } else {
    console.log('Commander: ❌ MISSING');
  }

  // Check personnel
  console.log(`Personnel: ${unit.total_personnel || unit.personnel_summary?.total_personnel || 'MISSING'}`);

  // Check tanks
  if (unit.tanks) {
    const total = unit.tanks.total || 0;
    const variants = Object.keys(unit.tanks).filter(k => k !== 'total' && k !== 'operational' && typeof unit.tanks[k] === 'object').length;
    console.log(`Tanks: ${total} total, ${variants} variants detailed`);
  } else {
    console.log('Tanks: NO DATA');
  }

  // Check supply data (Section 6)
  console.log(`\nSection 6 (Supply/Logistics):`);
  console.log(`  supply_status: ${unit.supply_status ? '✅' : '❌'}`);
  console.log(`  fuel_reserves: ${unit.fuel_reserves ? '✅' : '❌'}`);
  console.log(`  ammunition: ${unit.ammunition ? '✅' : '❌'}`);
  console.log(`  operational_radius: ${unit.operational_radius ? '✅' : '❌'}`);
  console.log(`  water: ${unit.water ? '✅' : '❌'}`);

  // Check weather data (Section 7)
  console.log(`\nSection 7 (Weather/Environmental):`);
  console.log(`  season_quarter: ${unit.season_quarter ? '✅' : '❌'}`);
  console.log(`  temperature_range: ${unit.temperature_range ? '✅' : '❌'}`);
  console.log(`  terrain_type: ${unit.terrain_type ? '✅' : '❌'}`);
  console.log(`  storm_frequency: ${unit.storm_frequency ? '✅' : '❌'}`);

  // Check confidence
  console.log(`\nMetadata:`);
  console.log(`  confidence_score: ${unit.metadata?.confidence_score ? '✅ ' + unit.metadata.confidence_score + '%' : '❌'}`);
  console.log(`  sources: ${unit.metadata?.sources ? unit.metadata.sources.length + ' sources' : '❌'}`);

  console.log('');
});
