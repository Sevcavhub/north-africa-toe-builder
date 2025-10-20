#!/usr/bin/env node

/**
 * Migrate units from old schema format to v3.1.0 nested structure
 *
 * Changes:
 * - Migrate fuel_days, ammo_days, water_days, operational_radius_km, supply_notes
 *   into "supply_logistics" object
 * - Migrate season, temperature_range_c, terrain_conditions, weather_impact
 *   into "weather_environment" object
 * - Parse temperature_range_c string (e.g., "10-25") into {min: 10, max: 25}
 */

const fs = require('fs');
const path = require('path');

// Units to migrate
const unitsToMigrate = [
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q1_xiii_corps_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q3_8th_army_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q3_polish_carpathian_brigade_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q4_polish_carpathian_brigade_toe.json'
];

function parseTemperatureRange(tempStr) {
  // Parse "10-25" or "25-40" into {min: 10, max: 25}
  if (!tempStr || typeof tempStr !== 'string') {
    return {min: 15, max: 30}; // Default
  }

  const parts = tempStr.split('-');
  if (parts.length === 2) {
    return {
      min: parseInt(parts[0]),
      max: parseInt(parts[1])
    };
  }

  return {min: 15, max: 30}; // Default
}

function estimateDaylightHours(quarter) {
  // Estimate daylight hours based on quarter
  const quarterMap = {
    'q1': 11.5,  // Jan-Mar (winter)
    'q2': 13.5,  // Apr-Jun (spring/summer)
    'q3': 13.0,  // Jul-Sep (summer/autumn)
    'q4': 11.0   // Oct-Dec (autumn/winter)
  };

  const q = quarter.toLowerCase().match(/q\d/);
  return q ? quarterMap[q[0]] : 12.0;
}

function migrateUnit(unitPath) {
  console.log(`\nMigrating: ${path.basename(unitPath)}`);

  // Read unit
  const unitData = JSON.parse(fs.readFileSync(unitPath, 'utf8'));

  // Check if already migrated
  if (unitData.supply_logistics && typeof unitData.supply_logistics === 'object' &&
      unitData.supply_logistics.fuel_reserves_days !== undefined) {
    console.log('  ✓ Already migrated (has supply_logistics.fuel_reserves_days)');
    return;
  }

  // Create backup
  const backupPath = unitPath.replace('.json', '.backup.json');
  fs.writeFileSync(backupPath, JSON.stringify(unitData, null, 2));
  console.log(`  ✓ Backup created: ${path.basename(backupPath)}`);

  // Extract old fields
  const fuelDays = unitData.fuel_days || 10;
  const ammoDays = unitData.ammo_days || unitData.ammunition_days || 15;
  const waterDays = unitData.water_days || unitData.water_liters_per_day || 5;
  const opRadius = unitData.operational_radius_km || 200;
  const supplyNotes = unitData.supply_notes || '';

  const season = unitData.season || 'Unknown';
  const tempRangeStr = unitData.temperature_range_c || '15-30';
  const terrainConditions = unitData.terrain_conditions || '';
  const weatherImpact = unitData.weather_impact || '';

  // Parse temperature
  const tempRange = parseTemperatureRange(tempRangeStr);

  // Estimate daylight hours
  const daylightHours = estimateDaylightHours(unitData.quarter);

  // Create supply_logistics object
  const supplyLogistics = {
    supply_status: supplyNotes || `Supply status for ${unitData.unit_designation} during ${unitData.quarter}`,
    operational_radius_km: opRadius,
    fuel_reserves_days: fuelDays,
    ammunition_days: ammoDays,
    water_liters_per_day: waterDays
  };

  // Create weather_environment object
  const weatherEnvironment = {
    season_quarter: `${unitData.quarter} (${season})`,
    temperature_range_c: tempRange,
    terrain_type: terrainConditions || 'Western Desert terrain',
    storm_frequency_days: 2,  // Reasonable default for North Africa
    daylight_hours: daylightHours
  };

  // If we have weatherImpact, append it to terrain_type or create notes
  if (weatherImpact) {
    weatherEnvironment.weather_notes = weatherImpact;
  }

  // Build new unit object preserving order
  const newUnit = {};

  // Copy all fields in original order, replacing old fields with new objects
  let insertedSupply = false;
  let insertedWeather = false;

  for (const [key, value] of Object.entries(unitData)) {
    // Skip old fields that are being migrated
    if (['fuel_days', 'ammo_days', 'ammunition_days', 'water_days',
         'operational_radius_km', 'supply_notes', 'season',
         'temperature_range_c', 'terrain_conditions', 'weather_impact'].includes(key)) {
      continue;
    }

    // Insert supply_logistics after aircraft_total
    if (key === 'aircraft_total' || key === 'reconnaissance') {
      newUnit[key] = value;
      if (!insertedSupply) {
        newUnit.supply_logistics = supplyLogistics;
        insertedSupply = true;
      }
      continue;
    }

    // Insert weather_environment after supply_logistics or before combat_status
    if (key === 'combat_status' && !insertedWeather) {
      newUnit.supply_logistics = supplyLogistics;
      newUnit.weather_environment = weatherEnvironment;
      insertedSupply = true;
      insertedWeather = true;
      newUnit[key] = value;
      continue;
    }

    newUnit[key] = value;
  }

  // Ensure both objects are present (fallback if not inserted above)
  if (!insertedSupply) {
    newUnit.supply_logistics = supplyLogistics;
  }
  if (!insertedWeather) {
    newUnit.weather_environment = weatherEnvironment;
  }

  // Update schema version if needed
  if (newUnit.schema_version !== '3.1.0') {
    newUnit.schema_version = '3.1.0';
    console.log('  ✓ Updated schema_version to 3.1.0');
  }

  // Write updated unit
  fs.writeFileSync(unitPath, JSON.stringify(newUnit, null, 2));
  console.log('  ✓ Migration complete');
  console.log(`  ✓ Added supply_logistics: fuel=${supplyLogistics.fuel_reserves_days}d, ammo=${supplyLogistics.ammunition_days}d, water=${supplyLogistics.water_liters_per_day}L/d`);
  console.log(`  ✓ Added weather_environment: temp=${tempRange.min}-${tempRange.max}°C, daylight=${daylightHours}h`);
}

// Main
console.log('=== Schema v3.1.0 Migration Tool ===\n');
console.log('Migrating 4 units to nested supply_logistics and weather_environment objects...\n');

let successCount = 0;
let errorCount = 0;

for (const unitPath of unitsToMigrate) {
  try {
    if (!fs.existsSync(unitPath)) {
      console.log(`\nSkipping ${path.basename(unitPath)}: File not found`);
      errorCount++;
      continue;
    }

    migrateUnit(unitPath);
    successCount++;
  } catch (error) {
    console.error(`\nError migrating ${path.basename(unitPath)}: ${error.message}`);
    errorCount++;
  }
}

console.log('\n=== Migration Summary ===');
console.log(`Success: ${successCount}`);
console.log(`Errors: ${errorCount}`);
console.log(`Total: ${unitsToMigrate.length}`);

if (successCount === unitsToMigrate.length) {
  console.log('\n✅ All units migrated successfully!');
} else {
  console.log('\n⚠️  Some units failed migration. Check errors above.');
}
