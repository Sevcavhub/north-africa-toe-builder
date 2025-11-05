#!/usr/bin/env node

/**
 * Archive 39 Units with Weak Source Documentation
 *
 * Moves units with Wikipedia-only or no sources to archive directory
 * for re-extraction with strict primary source requirements.
 *
 * Units archived:
 * - 27 Wikipedia-only units
 * - 12 no-source units
 */

const fs = require('fs');
const path = require('path');

// Units to archive (from analysis)
const unitsToArchive = [
    // Wikipedia-only units (27)
    'british_1940q3_4th_indian_infantry_division',
    'italian_1940q3_17a_divisione_di_fanteria_pavia',
    'italian_1940q3_27a_divisione_di_fanteria_brescia',
    'british_1940q4_4th_indian_infantry_division',
    'italian_1940q4_17_divisione_di_fanteria_pavia',
    'italian_1940q4_27a_divisione_di_fanteria_brescia',
    'italian_1940q4_55_divisione_di_fanteria_savona',
    'british_1941q1_4th_indian_infantry_division',
    'british_1941q1_7th_armoured_division_the_desert_rats',
    'italian_1941q1_101_divisione_motorizzata_trieste',
    'italian_1941q1_102_divisione_motorizzata_trento',
    'italian_1941q1_17_divisione_di_fanteria_pavia',
    'italian_1941q1_27_divisione_di_fanteria_brescia',
    'italian_1941q2_101_divisione_motorizzata_trieste',
    'italian_1941q3_102_divisione_di_fanteria_motorizzata_trento',
    'italian_1941q3_17_divisione_di_fanteria_pavia',
    'italian_1941q3_39_divisione_di_fanteria_bologna',
    'italian_1941q3_xx_corps',
    'italian_1941q4_17_divisione_di_fanteria_pavia',
    'italian_1941q4_61_divisione_motorizzata_trento',
    'french_1942q1_1re_brigade_francaise_libre',
    'french_1942q3_1st_free_french_brigade',
    'british_1942q4_1st_parachute_brigade',
    'british_1942q4_1st_south_african_division',
    'british_1943q1_51st_highland_infantry_division',
    'british_1943q1_6_armoured_division',
    'german_1943q1_334_infantry_division',

    // No-source units (12)
    'german_1941q1_21_panzer_division',
    'german_1941q1_5th_light_division',
    'german_1941q1_90_light_division',
    'italian_1941q3_101_divisione_motorizzata_trieste',
    'italian_1941q3_101_trieste_division',
    'italian_1941q3_102_trento_division',
    'italian_1941q3_132_ariete_division',
    'italian_1941q3_25_divisione_di_fanteria_bologna',
    'british_1941q4_6th_australian_division',
    'italian_1941q4_101_trieste_division',
    'italian_1941q4_132_ariete_division',
    'italian_1942q1_132_divisione_corazzata_ariete'
];

console.log('=== ARCHIVING 39 UNITS WITH WEAK SOURCE DOCUMENTATION ===\n');
console.log(`Units to archive: ${unitsToArchive.length}\n`);

// Create archive directory
const archiveDir = path.join('data', 'output', 'archive', 'weak_sources_' + Date.now());
fs.mkdirSync(archiveDir, { recursive: true });

console.log(`Archive directory: ${archiveDir}\n`);

// Archive each unit
let archivedCount = 0;
let notFoundCount = 0;
const archivedUnits = [];

unitsToArchive.forEach(canonicalId => {
    const filename = `${canonicalId}_toe.json`;
    const sourcePath = path.join('data', 'output', 'units', filename);
    const destPath = path.join(archiveDir, filename);

    if (fs.existsSync(sourcePath)) {
        fs.renameSync(sourcePath, destPath);
        archivedCount++;
        archivedUnits.push(canonicalId);
        console.log(`✅ Archived: ${filename}`);
    } else {
        notFoundCount++;
        console.log(`⚠️  Not found: ${filename}`);
    }
});

console.log(`\n=== ARCHIVE SUMMARY ===`);
console.log(`✅ Archived: ${archivedCount} units`);
console.log(`⚠️  Not found: ${notFoundCount} units`);
console.log(`📁 Location: ${archiveDir}\n`);

// Create archive manifest
const manifest = {
    archived_at: new Date().toISOString(),
    reason: 'Weak source documentation - Wikipedia-only or no sources',
    total_units: archivedCount,
    units: archivedUnits.map(id => {
        const parts = id.split('_');
        return {
            canonical_id: id,
            nation: parts[0],
            quarter: parts[1],
            designation: parts.slice(2).join('_')
        };
    }),
    re_extraction_requirements: [
        'PRIMARY SOURCES ONLY - NO Wikipedia allowed',
        'Tessin for German units (mandatory)',
        'Nafziger Collection for cross-nation reference',
        'British Army Lists for British/Commonwealth units',
        'TM E 30-420 for Italian units',
        'US Field Manuals for American units',
        'Official histories (Playfair, Prasad) when available',
        'Minimum 2 primary sources per unit',
        'Confidence threshold: 85%+ for divisions, 80%+ for brigades/corps'
    ]
};

fs.writeFileSync(
    path.join(archiveDir, 'ARCHIVE_MANIFEST.json'),
    JSON.stringify(manifest, null, 2)
);

console.log('📝 Manifest created: ARCHIVE_MANIFEST.json\n');

// Update WORKFLOW_STATE to remove archived units
console.log('📊 Updating WORKFLOW_STATE.json...');

const state = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf-8'));
const originalCount = state.completed.length;

// Remove archived units from completed array
state.completed = state.completed.filter(id => !archivedUnits.includes(id));

const newCount = state.completed.length;
const removedCount = originalCount - newCount;

// Update counts
state.completed_count = state.completed_count - removedCount;
state.completion_percentage = ((state.completed_count / state.total_unit_quarters) * 100).toFixed(1);
state.last_updated = new Date().toISOString();
state.notes = (state.notes || '') + `\n[${new Date().toISOString()}] Archived ${removedCount} units with weak sources for re-extraction.`;

// Backup and save
const backupPath = `WORKFLOW_STATE.json.backup.${Date.now()}`;
fs.copyFileSync('WORKFLOW_STATE.json', backupPath);
fs.writeFileSync('WORKFLOW_STATE.json', JSON.stringify(state, null, 2));

console.log(`✅ WORKFLOW_STATE updated:`);
console.log(`   - Removed ${removedCount} units from completed array`);
console.log(`   - New completion: ${state.completed_count}/${state.total_unit_quarters} (${state.completion_percentage}%)`);
console.log(`   - Backup: ${backupPath}\n`);

console.log('=== NEXT STEPS ===');
console.log('1. Run: node scripts/generate_reextraction_batch.js');
console.log('2. Use the generated prompt with session:start');
console.log('3. Agents will re-extract with strict primary source requirements\n');
