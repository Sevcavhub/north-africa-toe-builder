#!/usr/bin/env node

/**
 * Rebuild WORKFLOW_STATE.json with correct canonical IDs
 *
 * Fixes the quarter format issue where WORKFLOW_STATE.json was storing
 * canonical IDs using JSON format (1942-Q4) instead of filename format (1942q4)
 */

const fs = require('fs');
const path = require('path');

console.log('═'.repeat(80));
console.log('REBUILDING WORKFLOW_STATE.json');
console.log('═'.repeat(80));
console.log();

// Step 1: Load current workflow state (to preserve metadata)
console.log('Step 1: Loading current WORKFLOW_STATE.json...');
const currentState = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf-8'));
console.log(`  ✅ Loaded (last updated: ${currentState.last_updated})`);
console.log();

// Step 2: Scan canonical units directory
console.log('Step 2: Scanning canonical units directory...');
const canonicalUnitsDir = 'data/output/units/';
const completedCanonicalIds = [];

if (!fs.existsSync(canonicalUnitsDir)) {
    console.error('  ❌ Canonical units directory does not exist!');
    process.exit(1);
}

const files = fs.readdirSync(canonicalUnitsDir);
for (const file of files) {
    if (file.endsWith('_toe.json')) {
        // Extract canonical ID from FILENAME (correct format)
        const canonicalId = file.replace('_toe.json', '');

        // Verify file is valid JSON
        try {
            const filePath = path.join(canonicalUnitsDir, file);
            const unitData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

            // Verify it has required fields
            if (unitData.nation && unitData.quarter && unitData.unit_designation) {
                completedCanonicalIds.push(canonicalId);
            } else {
                console.log(`  ⚠️  Skipping ${file}: Missing required fields`);
            }
        } catch (err) {
            console.log(`  ⚠️  Skipping ${file}: Invalid JSON (${err.message})`);
        }
    }
}

completedCanonicalIds.sort(); // Sort for consistency

console.log(`  ✅ Found ${completedCanonicalIds.length} valid unit files`);
console.log();

// Step 3: Load complete seed to calculate actual completion percentage
console.log('Step 3: Loading complete seed file...');
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf-8'));

// Count total unit-quarters in seed
let totalUnitQuarters = 0;
const nationKeys = ['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'];
nationKeys.forEach(key => {
    const units = seed[key] || [];
    units.forEach(unit => {
        totalUnitQuarters += unit.quarters.length;
    });
});

console.log(`  ✅ Total unit-quarters in seed: ${totalUnitQuarters}`);
console.log();

// Step 4: Use canonical matcher's authoritative matching report
console.log('Step 4: Loading canonical matching report...');

let matchingReport;
try {
    matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf-8'));
    console.log(`  ✅ Loaded matching report`);
} catch (err) {
    console.log('  ⚠️  Matching report not found, running canonical matcher...');
    const { execSync } = require('child_process');
    execSync('node scripts/canonical_master_matcher.js', { stdio: 'inherit' });
    matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf-8'));
}

// Extract matched canonical IDs from report (exact + alias matches)
const matchedIds = new Set();
matchingReport.matches.exact_matches.forEach(m => matchedIds.add(m.canonical_id));
matchingReport.matches.alias_matches.forEach(m => matchedIds.add(m.canonical_id));

const matchedCount = matchedIds.size;

console.log(`  ✅ Authoritative matches: ${matchedCount}/${totalUnitQuarters} (${matchingReport.completion_stats.completion_percentage}%)`);
console.log(`     - Exact matches: ${matchingReport.matches.exact_matches.length}`);
console.log(`     - Alias matches: ${matchingReport.matches.alias_matches.length}`);

// Identify which completed files are out-of-scope (not in matched list)
const unmatchedIds = completedCanonicalIds.filter(id => !matchedIds.has(id));

if (unmatchedIds.length > 0) {
    console.log(`  ⚠️  Out-of-scope units: ${unmatchedIds.length}`);
    console.log(`      (These will be included in completed array but not counted in percentage)`);
}
console.log();

// Step 5: Build new workflow state
console.log('Step 5: Building new workflow state...');

const completionPercentage = ((matchedCount / totalUnitQuarters) * 100).toFixed(1);

const newState = {
    last_updated: new Date().toISOString(),
    total_unit_quarters: totalUnitQuarters,
    total_unique_units: seed.total_units || 117,
    completed_count: matchedCount,
    completion_percentage: parseFloat(completionPercentage),
    completed: completedCanonicalIds, // All files, using correct filename format
    in_progress: currentState.in_progress || [],
    pending: currentState.pending || [],
    session_id: currentState.session_id || 'workflow_state_rebuilt',
    last_commit: currentState.last_commit || 'pending',
    seed_file: 'projects/north_africa_seed_units_COMPLETE.json',
    notes: `WORKFLOW STATE REBUILT (${new Date().toISOString().split('T')[0]}): Fixed canonical ID format (1942-Q4 → 1942q4). Scanned ${completedCanonicalIds.length} files in canonical directory. ${matchedCount}/${totalUnitQuarters} match complete seed (${completionPercentage}%). ${unmatchedIds.length} out-of-scope units preserved.`
};

console.log(`  ✅ New state created:`);
console.log(`     - Total unit-quarters: ${newState.total_unit_quarters}`);
console.log(`     - Completed (matched to seed): ${newState.completed_count}`);
console.log(`     - Completion percentage: ${newState.completion_percentage}%`);
console.log(`     - Total files in completed array: ${newState.completed.length}`);
console.log();

// Step 6: Backup old state
console.log('Step 6: Backing up old WORKFLOW_STATE.json...');
const backupPath = `WORKFLOW_STATE.json.backup.${Date.now()}`;
fs.writeFileSync(backupPath, JSON.stringify(currentState, null, 2));
console.log(`  ✅ Backup saved: ${backupPath}`);
console.log();

// Step 7: Save new state
console.log('Step 7: Saving new WORKFLOW_STATE.json...');
fs.writeFileSync('WORKFLOW_STATE.json', JSON.stringify(newState, null, 2));
console.log(`  ✅ WORKFLOW_STATE.json updated!`);
console.log();

// Step 8: Summary
console.log('═'.repeat(80));
console.log('SUMMARY');
console.log('═'.repeat(80));
console.log();
console.log('✅ Canonical ID format FIXED!');
console.log();
console.log('BEFORE:');
console.log(`  - Format: american_1942-Q4_1st_armored_division (WRONG)`);
console.log(`  - Completion: ${currentState.completion_percentage}% (${currentState.completed_count}/${currentState.total_unit_quarters})`);
console.log();
console.log('AFTER:');
console.log(`  - Format: american_1942q4_1st_armored_division (CORRECT)`);
console.log(`  - Completion: ${newState.completion_percentage}% (${newState.completed_count}/${newState.total_unit_quarters})`);
console.log();
console.log('📊 FILES:');
console.log(`  - Canonical directory: ${completedCanonicalIds.length} files`);
console.log(`  - Matched to seed: ${matchedCount} files`);
console.log(`  - Out-of-scope: ${unmatchedIds.length} files`);
console.log();

if (unmatchedIds.length > 0 && unmatchedIds.length <= 10) {
    console.log('📦 OUT-OF-SCOPE UNITS:');
    unmatchedIds.forEach(id => console.log(`  - ${id}`));
    console.log();
}

console.log('🎯 NEXT STEPS:');
console.log(`  - ${totalUnitQuarters - matchedCount} unit-quarters remaining to complete Phase 1-6`);
console.log(`  - Run 'npm run session:ready' to start autonomous extraction`);
console.log();
console.log('═'.repeat(80));
