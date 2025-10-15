#!/usr/bin/env node

/**
 * Enhance MASTER_UNIT_DIRECTORY.json with actual file designations as aliases
 *
 * Problem: Master directory only has seed designations as aliases (e.g., "Sirte Division")
 * but completed files have full names (e.g., "61ª Divisione di Fanteria 'Sirte'")
 *
 * Solution: Scan all completed files, extract actual unit_designation, and add as aliases
 */

const fs = require('fs');
const path = require('path');

console.log('═'.repeat(80));
console.log('ENHANCING MASTER UNIT DIRECTORY WITH ACTUAL FILE DESIGNATIONS');
console.log('═'.repeat(80));
console.log();

// Step 1: Load master directory
console.log('Step 1: Loading MASTER_UNIT_DIRECTORY.json...');
const masterDirectory = JSON.parse(fs.readFileSync('data/canonical/MASTER_UNIT_DIRECTORY.json', 'utf-8'));
console.log(`  ✅ Loaded ${masterDirectory.canonical_units.length} entries`);
console.log();

// Step 2: Scan completed files and extract actual designations
console.log('Step 2: Scanning completed files...');
const canonicalUnitsDir = 'data/output/units/';
const actualDesignations = new Map(); // canonical_id → actual designation from file

const files = fs.readdirSync(canonicalUnitsDir);
let scannedFiles = 0;

for (const file of files) {
    if (file.endsWith('_toe.json')) {
        try {
            const filePath = path.join(canonicalUnitsDir, file);
            const unitData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

            // Extract canonical ID from filename
            const canonicalId = file.replace('_toe.json', '');

            // Extract actual designation from unit data
            const actualDesignation = unitData.unit_designation || unitData.designation;

            if (actualDesignation) {
                actualDesignations.set(canonicalId, actualDesignation);
                scannedFiles++;
            }
        } catch (err) {
            console.log(`  ⚠️  Error reading ${file}: ${err.message}`);
        }
    }
}

console.log(`  ✅ Scanned ${scannedFiles} files`);
console.log(`  ✅ Extracted ${actualDesignations.size} actual designations`);
console.log();

// Step 3: Add actual designations as aliases
console.log('Step 3: Adding actual designations as aliases...');
let addedCount = 0;
let alreadyHadCount = 0;

for (const entry of masterDirectory.canonical_units) {
    const actualDesignation = actualDesignations.get(entry.canonical_id);

    if (actualDesignation) {
        // Check if this designation is already in aliases
        const aliasesLower = entry.aliases.map(a => a.toLowerCase());
        const actualLower = actualDesignation.toLowerCase();

        if (!aliasesLower.includes(actualLower)) {
            entry.aliases.push(actualDesignation);
            addedCount++;
        } else {
            alreadyHadCount++;
        }
    }
}

console.log(`  ✅ Added ${addedCount} new aliases from actual file designations`);
console.log(`  ℹ️  ${alreadyHadCount} already had the actual designation as alias`);
console.log();

// Step 4: Save enhanced master directory
console.log('Step 4: Saving enhanced master directory...');

// Backup original
const backupPath = `data/canonical/MASTER_UNIT_DIRECTORY.json.backup.${Date.now()}`;
fs.writeFileSync(backupPath, JSON.stringify(masterDirectory, null, 2));
console.log(`  ✅ Backup saved: ${backupPath}`);

// Save enhanced version
fs.writeFileSync('data/canonical/MASTER_UNIT_DIRECTORY.json', JSON.stringify(masterDirectory, null, 2));
console.log(`  ✅ Enhanced master directory saved`);
console.log();

// Step 5: Show examples
console.log('═'.repeat(80));
console.log('EXAMPLES OF ENHANCED ALIASES');
console.log('═'.repeat(80));
console.log();

// Show a few Italian examples
const italianExamples = masterDirectory.canonical_units
    .filter(u => u.nation === 'italian' && actualDesignations.has(u.canonical_id))
    .slice(0, 5);

italianExamples.forEach(ex => {
    console.log(`${ex.designation}:`);
    console.log(`  Canonical ID: ${ex.canonical_id}`);
    console.log(`  Aliases:`);
    ex.aliases.forEach(a => console.log(`    - ${a}`));
    console.log();
});

console.log('═'.repeat(80));
console.log('SUMMARY');
console.log('═'.repeat(80));
console.log();
console.log(`✅ Enhanced ${addedCount} master directory entries with actual file designations`);
console.log();
console.log('🎯 NEXT STEP: Rerun canonical matcher to get accurate matching:');
console.log('  node scripts/canonical_master_matcher.js');
console.log();
console.log('═'.repeat(80));
