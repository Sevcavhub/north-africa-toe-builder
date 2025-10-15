const fs = require('fs');
const path = require('path');

const unitsDir = path.join(__dirname, '../data/output/units');
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

console.log('=== UNIT LOCATION ANALYSIS ===\n');
console.log('Checking which units were actually IN AFRICA vs. preparing in Europe\n');

const inAfrica = [];
const notInAfrica = [];
const unknown = [];

for (const file of files) {
  const filePath = path.join(unitsDir, file);
  let unit;
  try {
    unit = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (err) {
    console.warn(`⚠️  Skipping ${file} - JSON parse error`);
    continue;
  }

  const unitName = file.replace('_toe.json', '');
  const theater = unit.theater || '';
  const hq = unit.command?.headquarters_location || '';
  const context = unit.historical_context?.period_summary || '';
  const tactical = unit.tactical_doctrine?.desert_adaptations || '';

  // Combine all location indicators
  const locationText = (theater + ' ' + hq + ' ' + context + ' ' + tactical).toLowerCase();

  let status = 'unknown';
  if (locationText.includes('africa') || locationText.includes('libya') || locationText.includes('egypt') || locationText.includes('tunisia') || locationText.includes('tripoli') || locationText.includes('benghazi') || locationText.includes('tobruk') || locationText.includes('el alamein')) {
    if (locationText.includes('not yet deployed') || locationText.includes('not yet in') || locationText.includes('stationed in italy') || locationText.includes('stationed in germany')) {
      status = 'not_in_africa';
      notInAfrica.push({unit: unitName, theater, hq, reason: 'Preparing for deployment, not yet in theater'});
    } else {
      status = 'in_africa';
      inAfrica.push({unit: unitName, theater, hq});
    }
  } else if (locationText.includes('italy') || locationText.includes('germany') || locationText.includes('europe') || locationText.includes('france')) {
    status = 'not_in_africa';
    notInAfrica.push({unit: unitName, theater, hq, reason: 'In Europe'});
  } else {
    status = 'unknown';
    unknown.push({unit: unitName, theater, hq});
  }
}

console.log(`✅ IN AFRICA: ${inAfrica.length} units`);
console.log(`❌ NOT IN AFRICA: ${notInAfrica.length} units`);
console.log(`❓ UNKNOWN: ${unknown.length} units`);
console.log('');

console.log('=== NOT IN AFRICA (Should be OUT OF SCOPE) ===');
notInAfrica.slice(0, 20).forEach(u => {
  console.log(`  - ${u.unit}`);
  console.log(`    HQ: ${u.hq}`);
  console.log(`    Reason: ${u.reason}`);
  console.log('');
});

if (notInAfrica.length > 20) {
  console.log(`  ... and ${notInAfrica.length - 20} more\n`);
}

console.log('=== UNKNOWN (Need manual review) ===');
unknown.slice(0, 10).forEach(u => {
  console.log(`  - ${u.unit}`);
  console.log(`    Theater: ${u.theater}`);
  console.log(`    HQ: ${u.hq}`);
  console.log('');
});

if (unknown.length > 10) {
  console.log(`  ... and ${unknown.length - 10} more\n`);
}

console.log('=== SUMMARY ===');
console.log(`Total completed units: ${files.length}`);
console.log(`Actually in Africa (IN SCOPE): ${inAfrica.length}`);
console.log(`Not in Africa (OUT OF SCOPE): ${notInAfrica.length}`);
console.log(`Unknown location: ${unknown.length}`);
console.log('');
console.log('User rule: "ALL UNITS THAT WERE ON SOIL IN AFRICA"');
console.log(`TRUE SCOPE: ${inAfrica.length} units completed`);
