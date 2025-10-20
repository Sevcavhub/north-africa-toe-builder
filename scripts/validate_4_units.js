#!/usr/bin/env node

/**
 * Validate the 4 critical units for 1941 completion
 */

const fs = require('fs');
const path = require('path');

const unitsToValidate = [
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q1_xiii_corps_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q3_8th_army_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q3_polish_carpathian_brigade_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q4_polish_carpathian_brigade_toe.json'
];

console.log('=== Schema v3.1.0 Validation for 4 Critical Units ===\n');

let allValid = true;
let validCount = 0;

for (const unitPath of unitsToValidate) {
  const unitName = path.basename(unitPath);
  console.log(`\nValidating: ${unitName}`);

  if (!fs.existsSync(unitPath)) {
    console.log('  ❌ File not found');
    allValid = false;
    continue;
  }

  const unit = JSON.parse(fs.readFileSync(unitPath, 'utf8'));
  let errors = [];
  let warnings = [];

  // Check schema version
  if (unit.schema_version !== '3.1.0') {
    errors.push(`Schema version is ${unit.schema_version}, expected 3.1.0`);
  } else {
    console.log('  ✓ Schema version: 3.1.0');
  }

  // Check required top-level fields
  const requiredFields = ['nation', 'quarter', 'unit_designation', 'organization_level',
                          'command', 'total_personnel', 'officers', 'enlisted',
                          'top_3_infantry_weapons', 'ground_vehicles_total',
                          'tanks', 'artillery_total', 'aircraft_total',
                          'supply_logistics', 'weather_environment',
                          'subordinate_units', 'validation'];

  for (const field of requiredFields) {
    if (!unit[field] && unit[field] !== 0) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  if (errors.length === 0) {
    console.log('  ✓ All required fields present');
  }

  // Check supply_logistics object structure
  if (!unit.supply_logistics || typeof unit.supply_logistics !== 'object') {
    errors.push('supply_logistics is missing or not an object');
  } else {
    const supplyFields = ['supply_status', 'operational_radius_km',
                          'fuel_reserves_days', 'ammunition_days',
                          'water_liters_per_day'];
    let supplyValid = true;
    for (const field of supplyFields) {
      if (unit.supply_logistics[field] === undefined) {
        errors.push(`supply_logistics.${field} is missing`);
        supplyValid = false;
      }
    }
    if (supplyValid) {
      console.log('  ✓ supply_logistics object valid (5 fields)');
    }
  }

  // Check weather_environment object structure
  if (!unit.weather_environment || typeof unit.weather_environment !== 'object') {
    errors.push('weather_environment is missing or not an object');
  } else {
    const weatherFields = ['season_quarter', 'temperature_range_c',
                           'terrain_type', 'storm_frequency_days',
                           'daylight_hours'];
    let weatherValid = true;
    for (const field of weatherFields) {
      if (unit.weather_environment[field] === undefined) {
        errors.push(`weather_environment.${field} is missing`);
        weatherValid = false;
      }
    }
    // Check temperature_range_c structure
    if (unit.weather_environment.temperature_range_c) {
      const temp = unit.weather_environment.temperature_range_c;
      if (typeof temp !== 'object' || temp.min === undefined || temp.max === undefined) {
        errors.push('temperature_range_c must be object with min and max');
        weatherValid = false;
      } else if (temp.min >= temp.max) {
        warnings.push('temperature_range_c.min should be < max');
      }
    }
    if (weatherValid) {
      console.log('  ✓ weather_environment object valid (5 fields)');
    }
  }

  // Check nation value
  if (unit.nation !== 'british') {
    errors.push(`Nation is '${unit.nation}', expected 'british'`);
  } else {
    console.log('  ✓ Nation: british');
  }

  // Check quarter format
  if (!/^\d{4}q[1-4]$/.test(unit.quarter)) {
    errors.push(`Quarter '${unit.quarter}' doesn't match format YYYYqN`);
  } else {
    console.log(`  ✓ Quarter: ${unit.quarter}`);
  }

  // Check organization_level
  const validLevels = ['theater', 'corps', 'army', 'division', 'brigade', 'regiment',
                       'battalion', 'company', 'platoon', 'squad'];
  if (!validLevels.includes(unit.organization_level)) {
    errors.push(`Invalid organization_level: ${unit.organization_level}`);
  } else {
    console.log(`  ✓ Organization level: ${unit.organization_level}`);
  }

  // Check tanks structure
  if (unit.tanks) {
    if (unit.tanks.heavy_tanks === undefined ||
        unit.tanks.medium_tanks === undefined ||
        unit.tanks.light_tanks === undefined) {
      errors.push('tanks object missing heavy_tanks, medium_tanks, or light_tanks');
    } else {
      // Validate tank totals
      const heavyTotal = unit.tanks.heavy_tanks.total || 0;
      const mediumTotal = unit.tanks.medium_tanks.total || 0;
      const lightTotal = unit.tanks.light_tanks.total || 0;
      const calculatedTotal = heavyTotal + mediumTotal + lightTotal;

      if (Math.abs(unit.tanks.total - calculatedTotal) > 1) {
        errors.push(`tanks.total (${unit.tanks.total}) != sum of categories (${calculatedTotal})`);
      } else {
        console.log(`  ✓ Tank totals validate: ${unit.tanks.total}`);
      }
    }
  }

  // Check validation object
  if (unit.validation) {
    if (!unit.validation.source || !Array.isArray(unit.validation.source)) {
      errors.push('validation.source must be an array');
    }
    if (unit.validation.confidence === undefined) {
      warnings.push('validation.confidence is missing');
    } else {
      console.log(`  ✓ Confidence: ${unit.validation.confidence}%`);
    }
    if (unit.validation.tier !== undefined) {
      console.log(`  ✓ Tier: ${unit.validation.tier}`);
    }
  }

  // Report results
  if (errors.length > 0) {
    console.log(`\n  ❌ ERRORS (${errors.length}):`);
    errors.forEach(err => console.log(`     • ${err}`));
    allValid = false;
  } else {
    console.log(`\n  ✅ VALID - No critical errors`);
    validCount++;
  }

  if (warnings.length > 0) {
    console.log(`\n  ⚠️  WARNINGS (${warnings.length}):`);
    warnings.forEach(warn => console.log(`     • ${warn}`));
  }
}

console.log('\n=== Validation Summary ===');
console.log(`Valid: ${validCount}/${unitsToValidate.length}`);

if (allValid) {
  console.log('\n✅ All 4 units are schema v3.1.0 compliant!');
  process.exit(0);
} else {
  console.log('\n❌ Some units have validation errors. See above.');
  process.exit(1);
}
