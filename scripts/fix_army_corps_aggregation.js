const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, '..', 'data', 'output', 'units');

// Units that need fixing (from audit report)
// NOTE: First 3 already fixed, keeping them for reference but script will skip if backup exists
const unitsToFix = [
  // CRITICAL - HQ-only with very low counts (ALREADY FIXED: british_1942q4, german_1941q3, german_1942q1)
  // 'british_1942q4_eighth_army_8th_army_toe.json',  // DONE
  // 'german_1941q3_panzergruppe_afrika_toe.json',    // DONE
  // 'german_1942q1_panzergruppe_afrika_toe.json',    // DONE
  'italian_1940q4_xxi_corpo_d_armata_xxi_corps_toe.json',
  'italian_1940q4_xxii_corpo_d_armata_xxii_corps_toe.json',

  // HQ-only
  'british_1942q2_eighth_army_8th_army_toe.json',
  'british_1942q3_eighth_army_8th_army_toe.json',
  'italian_1940q2_10_armata_italian_10th_army_toe.json',
  'italian_1940q3_10_armata_italian_10th_army_toe.json',
  'italian_1940q3_xxii_corpo_d_armata_xxii_corps_toe.json',
  'italian_1941q1_xxii_corpo_d_armata_xxii_corps_toe.json',

  // Incorrect totals
  'british_1941q3_eighth_army_8th_army_toe.json',
  'british_1942q4_first_army_toe.json',
  'british_1943q2_first_army_toe.json',
  'german_1942q3_panzerarmee_afrika_toe.json',
  'german_1942q4_panzerarmee_afrika_toe.json',
  'german_1943q1_panzerarmee_afrika_toe.json',
  'italian_1941q1_xxi_corpo_d_armata_xxi_corps_toe.json'
];

console.log('ARMY/CORPS AGGREGATION FIX SCRIPT');
console.log('='.repeat(80));
console.log(`Units to fix: ${unitsToFix.length}`);
console.log('='.repeat(80));
console.log('');

const results = {
  success: [],
  failed: [],
  skipped: []
};

function findSubordinateFile(designation, quarter, nation) {
  // Check if designation is valid
  if (!designation || typeof designation !== 'string') {
    return null;
  }

  // Normalize designation to filename format
  const normalized = designation
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, '_')
    .replace(/_+/g, '_')
    .trim();

  // Common variations to try
  const variations = [
    `${nation}_${quarter}_${normalized}_toe.json`,
    `${nation}_${quarter}_${normalized.replace('division', 'div')}_toe.json`,
    `${nation}_${quarter}_${normalized.replace('infantry', 'inf')}_toe.json`
  ];

  for (const variant of variations) {
    const filePath = path.join(outputDir, variant);
    if (fs.existsSync(filePath)) {
      return variant;
    }
  }

  // Try fuzzy match
  const files = fs.readdirSync(outputDir);
  const quarterNorm = quarter.replace('-', '');
  const pattern = new RegExp(`^${nation}_${quarterNorm}_.*_toe\\.json$`, 'i');

  for (const file of files) {
    if (pattern.test(file)) {
      const fileDesig = file
        .replace(`${nation}_${quarterNorm}_`, '')
        .replace('_toe.json', '')
        .replace(/_/g, ' ');

      const desigWords = new Set(designation.toLowerCase().split(/\s+/));
      const fileWords = new Set(fileDesig.toLowerCase().split(/\s+/));
      const intersection = new Set([...desigWords].filter(x => fileWords.has(x)));

      if (intersection.size >= 2) {
        return file;
      }
    }
  }

  return null;
}

function aggregateEquipment(equipment1, equipment2) {
  if (!equipment1 && !equipment2) return null;
  if (!equipment1) return JSON.parse(JSON.stringify(equipment2));
  if (!equipment2) return JSON.parse(JSON.stringify(equipment1));

  const result = JSON.parse(JSON.stringify(equipment1));

  for (const [category, data] of Object.entries(equipment2)) {
    if (!result[category]) {
      result[category] = JSON.parse(JSON.stringify(data));
    } else if (typeof data === 'object' && data !== null) {
      if (data.total !== undefined) {
        result[category].total = (result[category].total || 0) + data.total;
      }
      if (data.operational !== undefined) {
        result[category].operational = (result[category].operational || 0) + data.operational;
      }
      if (data.variants && Array.isArray(data.variants)) {
        result[category].variants = result[category].variants || [];
        for (const variant of data.variants) {
          const existing = result[category].variants.find(v => v.model === variant.model);
          if (existing) {
            existing.count = (existing.count || 0) + (variant.count || 0);
            existing.operational = (existing.operational || 0) + (variant.operational || 0);
          } else {
            result[category].variants.push(JSON.parse(JSON.stringify(variant)));
          }
        }
      }
    }
  }

  return result;
}

for (const filename of unitsToFix) {
  console.log(`\nProcessing: ${filename}`);
  console.log('-'.repeat(80));

  const filePath = path.join(outputDir, filename);

  if (!fs.existsSync(filePath)) {
    console.log('  ERROR: File not found');
    results.failed.push({ filename, error: 'File not found' });
    continue;
  }

  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const subordinates = data.subordinate_units || [];

  if (subordinates.length === 0) {
    console.log('  SKIP: No subordinate units listed');
    results.skipped.push({ filename, reason: 'No subordinates' });
    continue;
  }

  // Extract quarter and nation from filename
  const match = filename.match(/^([a-z]+)_(\d{4}q\d)/);
  if (!match) {
    console.log('  ERROR: Could not parse nation/quarter from filename');
    results.failed.push({ filename, error: 'Parse error' });
    continue;
  }

  const nation = match[1];
  const quarter = match[2];

  console.log(`  Nation: ${nation}, Quarter: ${quarter}`);
  console.log(`  Subordinates: ${subordinates.length}`);

  // Aggregate from subordinates
  let totalPersonnel = 0;
  let totalTanks = 0;
  let totalGroundVehicles = 0;
  let totalArtillery = 0;
  let totalAircraft = 0;
  let aggregatedEquipment = {};
  let foundSubordinates = 0;
  let missingSubordinates = [];

  for (const sub of subordinates) {
    const subFile = findSubordinateFile(sub.unit_designation, quarter, nation);

    if (!subFile) {
      console.log(`  WARNING: Subordinate not found: ${sub.unit_designation}`);
      missingSubordinates.push(sub.unit_designation);
      continue;
    }

    const subPath = path.join(outputDir, subFile);
    const subData = JSON.parse(fs.readFileSync(subPath, 'utf8'));

    foundSubordinates++;

    // Add personnel
    const personnel = subData.total_personnel || 0;
    totalPersonnel += personnel;

    // Add tanks
    const tanks = subData.tanks?.total || 0;
    totalTanks += tanks;

    // Add ground vehicles
    const gv = subData.ground_vehicles?.total || 0;
    totalGroundVehicles += gv;

    // Add artillery
    const arty = subData.artillery?.total || 0;
    totalArtillery += arty;

    // Add aircraft
    const aircraft = subData.aircraft?.total || 0;
    totalAircraft += aircraft;

    // Update subordinate entry with actual data
    sub.strength = personnel;
    sub.tanks = tanks;
    sub.reference_file = subFile;

    // Aggregate equipment
    if (subData.tanks) {
      aggregatedEquipment.tanks = aggregateEquipment(aggregatedEquipment.tanks, subData.tanks);
    }
    if (subData.ground_vehicles) {
      aggregatedEquipment.ground_vehicles = aggregateEquipment(aggregatedEquipment.ground_vehicles, subData.ground_vehicles);
    }
    if (subData.artillery) {
      aggregatedEquipment.artillery = aggregateEquipment(aggregatedEquipment.artillery, subData.artillery);
    }
  }

  console.log(`  Found ${foundSubordinates}/${subordinates.length} subordinate files`);

  if (missingSubordinates.length > 0) {
    console.log(`  Missing subordinates: ${missingSubordinates.join(', ')}`);
  }

  if (foundSubordinates === 0) {
    console.log('  SKIP: No subordinate files found');
    results.skipped.push({ filename, reason: 'No subordinate files' });
    continue;
  }

  // Create backup
  const backupPath = filePath + '.backup.' + Date.now();
  fs.writeFileSync(backupPath, JSON.stringify(data, null, 2));
  console.log(`  Backup created: ${path.basename(backupPath)}`);

  // Update totals
  const oldPersonnel = data.total_personnel || 0;
  const oldTanks = data.tanks?.total || 0;

  data.total_personnel = totalPersonnel;

  // Update equipment with aggregated totals
  if (totalTanks > 0) {
    data.tanks = aggregatedEquipment.tanks || { total: totalTanks, operational: totalTanks };
  }

  if (totalGroundVehicles > 0) {
    data.ground_vehicles = aggregatedEquipment.ground_vehicles || { total: totalGroundVehicles };
  }

  if (totalArtillery > 0) {
    data.artillery = aggregatedEquipment.artillery || { total: totalArtillery };
  }

  if (totalAircraft > 0 && !data.aircraft) {
    data.aircraft = { total: totalAircraft };
  }

  // Update aggregation metadata
  data.aggregation_status = 'calculated_from_subordinates';
  data.aggregation_date = new Date().toISOString();
  data.aggregation_notes = `Aggregated from ${foundSubordinates} subordinate units. Previous totals: ${oldPersonnel} personnel, ${oldTanks} tanks.`;

  // Write updated file
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));

  console.log(`  OLD: ${oldPersonnel.toLocaleString()} personnel, ${oldTanks} tanks`);
  console.log(`  NEW: ${totalPersonnel.toLocaleString()} personnel, ${totalTanks} tanks`);
  console.log('  SUCCESS: File updated');

  results.success.push({
    filename,
    old: { personnel: oldPersonnel, tanks: oldTanks },
    new: { personnel: totalPersonnel, tanks: totalTanks },
    subordinates_found: foundSubordinates
  });
}

// Summary
console.log('\n' + '='.repeat(80));
console.log('SUMMARY');
console.log('='.repeat(80));
console.log(`Total processed: ${unitsToFix.length}`);
console.log(`  Success: ${results.success.length}`);
console.log(`  Failed: ${results.failed.length}`);
console.log(`  Skipped: ${results.skipped.length}`);
console.log('');

if (results.success.length > 0) {
  console.log('SUCCESSFULLY UPDATED:');
  console.log('-'.repeat(80));
  for (const item of results.success) {
    console.log(`  ${item.filename}`);
    console.log(`    ${item.old.personnel.toLocaleString()} → ${item.new.personnel.toLocaleString()} personnel`);
    console.log(`    ${item.old.tanks} → ${item.new.tanks} tanks`);
    console.log(`    Aggregated from ${item.subordinates_found} subordinate units`);
    console.log('');
  }
}

if (results.failed.length > 0) {
  console.log('FAILED:');
  console.log('-'.repeat(80));
  for (const item of results.failed) {
    console.log(`  ${item.filename}: ${item.error}`);
  }
  console.log('');
}

if (results.skipped.length > 0) {
  console.log('SKIPPED:');
  console.log('-'.repeat(80));
  for (const item of results.skipped) {
    console.log(`  ${item.filename}: ${item.reason}`);
  }
  console.log('');
}

// Save report
const reportPath = path.join(__dirname, '..', 'ARMY_CORPS_AGGREGATION_FIX_REPORT.json');
fs.writeFileSync(reportPath, JSON.stringify({
  date: new Date().toISOString(),
  total_processed: unitsToFix.length,
  results
}, null, 2));

console.log(`Detailed results saved to: ARMY_CORPS_AGGREGATION_FIX_REPORT.json`);
