const Ajv = require('ajv');
const fs = require('fs');

const ajv = new Ajv({strict: false});
const schema = JSON.parse(fs.readFileSync('./schemas/air_force_schema.json', 'utf8'));

// Test existing 37 Squadron file
const data37 = JSON.parse(fs.readFileSync('./data/output/air_units/british_1942q4_no_37_squadron_raf_toe.json', 'utf8'));
const validate37 = ajv.compile(schema);
const valid37 = validate37(data37);
console.log('37 Squadron validation:', valid37 ? 'PASS' : 'FAIL');
if (!valid37) {
  console.log('First 3 errors:');
  console.log(JSON.stringify(validate37.errors.slice(0, 3), null, 2));
}

console.log('\n---\n');

// Test new 40 Squadron file
const data40 = JSON.parse(fs.readFileSync('./data/output/air_units/british_1942q4_no_40_squadron_raf_toe.json', 'utf8'));
const validate40 = ajv.compile(schema);
const valid40 = validate40(data40);
console.log('40 Squadron validation:', valid40 ? 'PASS' : 'FAIL');
if (!valid40) {
  console.log('First 3 errors:');
  console.log(JSON.stringify(validate40.errors.slice(0, 3), null, 2));
}
