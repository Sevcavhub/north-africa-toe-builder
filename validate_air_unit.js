const Ajv = require('ajv');
const fs = require('fs');

const ajv = new Ajv();
const schema = JSON.parse(fs.readFileSync('./schemas/air_force_schema.json', 'utf8'));
const data = JSON.parse(fs.readFileSync('./data/output/air_units/british_1942q4_no_238_squadron_raf_toe.json', 'utf8'));

const validate = ajv.compile(schema);
const valid = validate(data);

console.log('Schema Validation Result:', valid ? 'PASS' : 'FAIL');
if (!valid) {
  console.log('\nValidation Errors:');
  console.log(JSON.stringify(validate.errors, null, 2));
} else {
  console.log('\n✓ JSON file is valid according to air_force_schema.json v1.0');
  console.log('\nUnit Summary:');
  console.log(`  Unit: ${data.unit_designation}`);
  console.log(`  Nation: ${data.nation}`);
  console.log(`  Quarter: ${data.quarter}`);
  console.log(`  Commander: ${data.commander.rank} ${data.commander.name}`);
  console.log(`  Aircraft: ${data.aircraft.total}x ${data.aircraft.variants[0].designation}`);
  console.log(`  Tier: ${data.metadata.tier}`);
  console.log(`  Tier 1/2 %: ${data.metadata.tier_1_percentage}%`);
  console.log(`  Confidence: ${data.metadata.confidence}%`);
}
