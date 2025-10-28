const Ajv = require('ajv');
const fs = require('fs');

const ajv = new Ajv();
const schema = JSON.parse(fs.readFileSync('./schemas/air_force_schema.json', 'utf8'));
const data = JSON.parse(fs.readFileSync('./data/output/air_units/british_1942q4_no_40_squadron_raf_toe.json', 'utf8'));

const validate = ajv.compile(schema);
const valid = validate(data);

console.log('Schema Validation Result:', valid ? 'PASS' : 'FAIL');
if (!valid) {
  console.log('\nValidation Errors:');
  console.log(JSON.stringify(validate.errors, null, 2));
} else {
  console.log('\n✓ JSON file is valid according to air_force_schema.json v1.0');
  console.log('\nUnit Summary:');
  console.log('  Unit:', data.unit_designation);
  console.log('  Nation:', data.nation);
  console.log('  Quarter:', data.quarter);
  console.log('  Aircraft:', data.aircraft.primary_aircraft.actual_strength + 'x', data.aircraft.primary_aircraft.type);
  console.log('  Tier:', data.metadata.data_quality.tier);
  console.log('  Tier 1/2 %:', data.metadata.source_validation.tier_1_2_percentage + '%');
  console.log('  Confidence:', data.metadata.data_quality.confidence_score + '%');
}
