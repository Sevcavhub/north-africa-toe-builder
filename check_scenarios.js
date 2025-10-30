const fs = require('fs');
const path = require('path');

const baseDir = 'data/output/battle_scenarios';
const expectedFiles = [
  'oob_ground.json',
  'oob_air.json',
  'supply_state.json',
  'weather.json',
  'air_support.json',
  'map_data.json',
  'victory_conditions.json'
];

const scenarios = fs.readdirSync(baseDir);

console.log(`\nChecking ${scenarios.length} scenarios for completeness...\n`);

let allComplete = true;

scenarios.forEach(scenario => {
  const scenarioPath = path.join(baseDir, scenario);
  if (fs.statSync(scenarioPath).isDirectory()) {
    const files = fs.readdirSync(scenarioPath);
    const missing = expectedFiles.filter(f => !files.includes(f));

    if (missing.length > 0) {
      allComplete = false;
      console.log(`❌ ${scenario}`);
      console.log(`   MISSING: ${missing.join(', ')}`);
      console.log(`   HAS: ${files.join(', ')}\n`);
    }
  }
});

if (allComplete) {
  console.log(`✅ All ${scenarios.length} scenarios have all 7 required files.\n`);
} else {
  console.log(`\n⚠️ Some scenarios are incomplete.\n`);
}
