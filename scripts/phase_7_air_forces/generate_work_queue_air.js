#!/usr/bin/env node
/**
 * Generate WORK_QUEUE_AIR.md from air forces seed file
 */

const fs = require('fs');
const path = require('path');

// Parse command line args
const args = process.argv.slice(2);
const seedFlag = args.indexOf('--seed');
const seedPath = seedFlag !== -1 ? args[seedFlag + 1] : 'projects/north_africa_air_units_seed_ULTRA_FOCUSED.json';

console.log(`\n📋 Generating WORK_QUEUE_AIR.md from: ${seedPath}\n`);

// Read seed file
const fullSeedPath = path.join(__dirname, '..', seedPath);
const seed = JSON.parse(fs.readFileSync(fullSeedPath, 'utf8'));

// Flatten all units with quarters
const allUnits = [];

['luftwaffe_units', 'regia_aeronautica_units', 'raf_commonwealth_units', 'usaaf_units'].forEach(nationKey => {
  const units = seed[nationKey] || [];
  const nationMap = {
    'luftwaffe_units': 'GERMAN',
    'regia_aeronautica_units': 'ITALIAN',
    'raf_commonwealth_units': 'BRITISH',
    'usaaf_units': 'AMERICAN'
  };
  const nation = nationMap[nationKey];

  units.forEach(unit => {
    unit.quarters.forEach(quarter => {
      allUnits.push({
        nation,
        quarter,
        designation: unit.designation,
        type: unit.type,
        battles: unit.battles || [],
        confidence: unit.confidence,
        notes: unit.notes || '',
        sources: unit.sources || [],
        witw_id: unit.witw_id
      });
    });
  });
});

// Sort: Echelon-first (staffel/squadron before gruppe/group), then chronological
const ECHELON_PRIORITY = {
  // Smallest units first (echelon-first globally)
  'fighter_squadron': 1,
  'bomber_squadron': 1,
  'tactical_reconnaissance_squadron': 1,
  'army_cooperation': 1,
  'fighter_staffel': 1,
  'stuka_staffel': 1,
  'long_range_recon_staffel': 2,
  'zerstoerer_staffel': 2,
  'desert_rescue_staffel': 2,
  'bomber_squadriglia': 2,

  // Mid-level units
  'fighter_gruppe': 10,
  'bomber_gruppe': 10,
  'stuka_gruppe': 10,
  'zerstoerer_gruppe': 10,
  'fighter_gruppo': 10,
  'bomber_gruppo': 10,
  'assault_gruppo': 10,

  // Large units
  'fighter_group': 20,
  'bomber_group_light': 20,
  'bomber_group_medium': 20,
  'bomber_group_heavy': 20,
  'bomber_geschwader': 20,
  'bomber_stormo': 20,

  // Command units last
  'fighter_geschwader_staff': 30,
  'stuka_geschwader_staff': 30,
  'command_staff': 40,
  'command_korps': 40
};

allUnits.sort((a, b) => {
  // Sort by echelon priority first
  const echelonA = ECHELON_PRIORITY[a.type] || 50;
  const echelonB = ECHELON_PRIORITY[b.type] || 50;
  if (echelonA !== echelonB) return echelonA - echelonB;

  // Then by quarter
  if (a.quarter !== b.quarter) return a.quarter.localeCompare(b.quarter);

  // Then by nation
  if (a.nation !== b.nation) return a.nation.localeCompare(b.nation);

  // Then by designation
  return a.designation.localeCompare(b.designation);
});

// Generate markdown
let md = `# North Africa Air Forces Work Queue - ULTRA-FOCUSED

**Generated**: ${new Date().toISOString()}

**Progress**: 0/${allUnits.length} units complete (0.0%)
**Remaining**: ${allUnits.length} units

**Scope**: Major battles only - ONE quarter per unit (peak battle quarter)

---

## ⚙️ How This Queue Works

1. **Echelon-First Order**: Squadrons/Staffeln before Gruppen/Gruppi before Groups/Geschwader (GLOBAL)
2. **Chronological Within Echelon**: 1940-Q4 → 1943-Q1
3. **Hybrid Source Validation**: Wikipedia to identify, Tier 1/2 to extract
4. **Session Workflow**: Process 3 units at a time with parallel Task tool agents
5. **Auto-Update**: Checkpoints mark units complete

---

## 🎯 Next 3 Units (Start Here)

`;

// Show next 3
for (let i = 0; i < Math.min(3, allUnits.length); i++) {
  const u = allUnits[i];
  md += `${i + 1}. **${u.nation}** - ${u.quarter} - ${u.designation} _(${u.type})_\n`;
}

md += `\n---\n\n## 📋 Full Queue (${allUnits.length} units)\n\n`;

// Group by quarter
const byQuarter = {};
allUnits.forEach(u => {
  if (!byQuarter[u.quarter]) byQuarter[u.quarter] = [];
  byQuarter[u.quarter].push(u);
});

Object.keys(byQuarter).sort().forEach(quarter => {
  const units = byQuarter[quarter];
  md += `### ${quarter} (${units.length} units)\n\n`;

  units.forEach(u => {
    const battles = u.battles.length > 0 ? ` - ${u.battles.slice(0, 2).join(', ')}` : '';
    const witw = u.witw_id ? ` [WITW: ${u.witw_id}]` : '';
    md += `- [ ] **${u.nation}** - ${u.designation} _(${u.type})_${battles}${witw}\n`;
  });

  md += `\n`;
});

md += `---

## ✅ Completed Units

Track completion using checkpoint system.

---

**🚀 ULTRA-FOCUSED SCOPE**: ${allUnits.length} unit-quarters for Phase 7 proof-of-concept
**📊 HYBRID VALIDATION**: Wikipedia + Tier 1/2 corroboration required
`;

// Write file
const outputPath = path.join(__dirname, '..', 'WORK_QUEUE_AIR.md');
fs.writeFileSync(outputPath, md);

console.log(`✅ Generated: WORK_QUEUE_AIR.md`);
console.log(`📊 Total units: ${allUnits.length}`);
console.log(`🎯 Next 3 units listed at top`);
console.log(`\n🚀 Ready for /air-continuous with ultra-focused scope!\n`);
