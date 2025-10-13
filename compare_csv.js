const fs = require('fs');

// Read both files
const torchFile = 'D:\\north-africa-toe-builder\\data\\iterations\\iteration_2\\Timeline_TOE_Reconstruction\\WIE_Dat\\Torch to Tunisia 42-43_unit.csv';
const witwFile = 'D:\\north-africa-toe-builder\\data\\iterations\\iteration_2\\Timeline_TOE_Reconstruction\\WIE_Dat\\WIW_CSVs\\_unit.csv';

const torchLines = fs.readFileSync(torchFile, 'utf-8').split('\n');
const witwLines = fs.readFileSync(witwFile, 'utf-8').split('\n');

console.log(`Torch file lines: ${torchLines.length}`);
console.log(`WITW file lines: ${witwLines.length}`);

// Create a map of unit IDs from each file
const torchUnits = new Map();
const witwUnits = new Map();

// Parse Torch units (skip header)
for (let i = 1; i < torchLines.length; i++) {
  if (!torchLines[i].trim()) continue;
  const parts = torchLines[i].split(',');
  if (parts.length > 2) {
    const unitId = parts[0];
    const unitName = parts[1];
    torchUnits.set(unitId, { name: unitName, line: torchLines[i] });
  }
}

// Parse WITW units (skip header)
for (let i = 1; i < witwLines.length; i++) {
  if (!witwLines[i].trim()) continue;
  const parts = witwLines[i].split(',');
  if (parts.length > 2) {
    const unitId = parts[0];
    const unitName = parts[1];
    witwUnits.set(unitId, { name: unitName, line: witwLines[i] });
  }
}

console.log(`\nTorch unique units: ${torchUnits.size}`);
console.log(`WITW unique units: ${witwUnits.size}`);

// Find units only in Torch
const onlyInTorch = [];
for (const [id, data] of torchUnits) {
  if (!witwUnits.has(id)) {
    onlyInTorch.push({ id, name: data.name });
  }
}

// Find units only in WITW
const onlyInWitw = [];
for (const [id, data] of witwUnits) {
  if (!torchUnits.has(id)) {
    onlyInWitw.push({ id, name: data.name });
  }
}

// Find units with differences
const differences = [];
for (const [id, torchData] of torchUnits) {
  if (witwUnits.has(id)) {
    const witwData = witwUnits.get(id);
    if (torchData.line !== witwData.line) {
      differences.push({ id, name: torchData.name });
    }
  }
}

console.log(`\n=== UNITS ONLY IN OPERATION TORCH ===`);
if (onlyInTorch.length === 0) {
  console.log('None');
} else {
  onlyInTorch.forEach(u => console.log(`ID ${u.id}: ${u.name}`));
}

console.log(`\n=== UNITS ONLY IN COMPLETE WITW ===`);
if (onlyInWitw.length === 0) {
  console.log('None');
} else {
  console.log(`Total: ${onlyInWitw.length} units`);
  onlyInWitw.slice(0, 50).forEach(u => console.log(`ID ${u.id}: ${u.name}`));
  if (onlyInWitw.length > 50) {
    console.log(`... and ${onlyInWitw.length - 50} more units`);
  }
}

console.log(`\n=== UNITS WITH DIFFERENCES ===`);
console.log(`Total units with differences: ${differences.length}`);
console.log(`(These are units that exist in both but have different data values)`);
