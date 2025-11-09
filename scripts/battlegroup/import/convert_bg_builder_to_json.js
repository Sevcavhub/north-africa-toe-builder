#!/usr/bin/env node
/**
 * Convert BattleGroup Builder JavaScript data files to JSON
 *
 * Source: https://osjones.github.io/BattlegroupBuilder/
 * Input: vehicles.js, weapons.js, forces.js (JavaScript variable declarations)
 * Output: JSON files in sources/ directory
 */

const fs = require('fs');
const path = require('path');

// Paths to source files
const BASE_PATH = path.join(__dirname, '..', '..', '..', 'Resource Documents', 'Battlegroup Game',
    'Army List Builder Data All Books', 'BattlegroupBuilder-main', 'BattlegroupBuilder-main', 'js');

const vehiclesPath = path.join(BASE_PATH, 'vehicles.js');
const weaponsPath = path.join(BASE_PATH, 'weapons.js');
const forcesPath = path.join(BASE_PATH, 'forces.js');

// Output directory
const OUTPUT_DIR = path.join(__dirname, '..', '..', '..', 'sources');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

console.log('🔄 BattleGroup Builder JS → JSON Conversion');
console.log('='.repeat(80));

// Execute the JavaScript files and extract variables
console.log('\n📂 Loading JavaScript files...');

try {
    // Load vehicles.js
    console.log(`   Loading: ${vehiclesPath}`);
    const vehiclesCode = fs.readFileSync(vehiclesPath, 'utf8');
    eval(vehiclesCode);
    console.log(`   ✅ Loaded vehicles array: ${vehicles.length} entries`);

    // Load weapons.js
    console.log(`   Loading: ${weaponsPath}`);
    const weaponsCode = fs.readFileSync(weaponsPath, 'utf8');
    eval(weaponsCode);
    const weaponsCount = Object.keys(weapons).length;
    console.log(`   ✅ Loaded weapons object: ${weaponsCount} entries`);

    // Load forces.js
    console.log(`   Loading: ${forcesPath}`);
    const forcesCode = fs.readFileSync(forcesPath, 'utf8');
    eval(forcesCode);
    console.log(`   ✅ Loaded forces array: ${forces.length} entries`);

    // Write JSON files
    console.log('\n💾 Writing JSON files...');

    const vehiclesOutput = path.join(OUTPUT_DIR, 'bg_builder_vehicles.json');
    fs.writeFileSync(vehiclesOutput, JSON.stringify(vehicles, null, 2));
    console.log(`   ✅ ${vehiclesOutput}`);
    console.log(`      ${vehicles.length} vehicles`);

    const weaponsOutput = path.join(OUTPUT_DIR, 'bg_builder_weapons.json');
    fs.writeFileSync(weaponsOutput, JSON.stringify(weapons, null, 2));
    console.log(`   ✅ ${weaponsOutput}`);
    console.log(`      ${weaponsCount} weapons`);

    const forcesOutput = path.join(OUTPUT_DIR, 'bg_builder_forces.json');
    fs.writeFileSync(forcesOutput, JSON.stringify(forces, null, 2));
    console.log(`   ✅ ${forcesOutput}`);
    console.log(`      ${forces.length} force lists`);

    // Summary statistics
    console.log('\n' + '='.repeat(80));
    console.log('✅ CONVERSION COMPLETE');
    console.log('='.repeat(80));
    console.log('\n📊 SUMMARY:');
    console.log(`   Vehicles:    ${vehicles.length} entries`);
    console.log(`   Weapons:     ${weaponsCount} entries`);
    console.log(`   Force Lists: ${forces.length} entries`);

    // Sample vehicle data
    const sampleVehicle = vehicles.find(v => v.name === 'Panzer III J');
    if (sampleVehicle) {
        console.log('\n📋 Sample Vehicle (Panzer III J):');
        console.log(JSON.stringify(sampleVehicle, null, 2));
    }

    // Sample weapon data
    if (weapons[8]) {
        console.log('\n🔫 Sample Weapon (ID 8 - 50mmL42):');
        console.log(JSON.stringify(weapons[8], null, 2));
    }

    console.log('\n✅ Next step: Run import scripts to load data into database');

} catch (error) {
    console.error('\n❌ ERROR during conversion:');
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
}
