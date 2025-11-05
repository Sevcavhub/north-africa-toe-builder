#!/usr/bin/env node

/**
 * Diagnostic: WORKFLOW_STATE.json vs Actual Files Mismatch
 *
 * Problem: WORKFLOW_STATE.json shows 190 completed units
 *          But data/output/units/ contains 237 files
 *          That's a 47-file discrepancy!
 *
 * This script:
 * 1. Scans canonical directory for ALL unit files
 * 2. Compares to WORKFLOW_STATE.json completed list
 * 3. Identifies which files are "invisible" to the system
 * 4. Shows why they're not being detected (naming issues, parsing failures, etc.)
 */

const fs = require('fs').promises;
const path = require('path');
const naming = require('./lib/naming_standard');
const paths = require('./lib/canonical_paths');

const PROJECT_ROOT = path.join(__dirname, '..');
const WORKFLOW_STATE_PATH = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');

async function scanAllFiles() {
    const canonicalUnitsDir = paths.UNITS_DIR;
    const allFiles = [];
    const parseFailures = [];

    try {
        const files = await fs.readdir(canonicalUnitsDir);

        for (const filename of files) {
            // Only process *_toe.json files (exclude unit_*.json pattern)
            if (filename.endsWith('_toe.json') && !filename.startsWith('unit_')) {
                const parsed = naming.parseFilename(filename);

                if (parsed) {
                    const unitId = `${parsed.nation}_${parsed.quarter}_${parsed.designation}`;
                    allFiles.push({
                        filename,
                        unitId,
                        nation: parsed.nation,
                        quarter: parsed.quarter,
                        designation: parsed.designation,
                        parsed: true
                    });
                } else {
                    // Failed to parse - this is a problem!
                    parseFailures.push({
                        filename,
                        unitId: null,
                        parsed: false,
                        reason: 'naming.parseFilename() returned null'
                    });
                }
            }
        }
    } catch (error) {
        console.error('❌ Error scanning canonical directory:', error.message);
        process.exit(1);
    }

    return { allFiles, parseFailures };
}

async function readWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        console.error('❌ Error reading WORKFLOW_STATE.json:', error.message);
        process.exit(1);
    }
}

function compareFilesToState(allFiles, state) {
    const stateSet = new Set(state.completed || []);
    const fileIds = new Set(allFiles.map(f => f.unitId));

    // Files that exist but aren't in WORKFLOW_STATE.json
    const filesNotInState = allFiles.filter(f => !stateSet.has(f.unitId));

    // WORKFLOW_STATE entries that don't have corresponding files (ghost entries)
    const stateNotInFiles = Array.from(stateSet).filter(id => !fileIds.has(id));

    return {
        filesNotInState,
        stateNotInFiles,
        totalFiles: allFiles.length,
        totalState: stateSet.size,
        discrepancy: allFiles.length - stateSet.size
    };
}

async function main() {
    console.log('═'.repeat(80));
    console.log('  DIAGNOSTIC: WORKFLOW_STATE.json Mismatch Analysis');
    console.log('═'.repeat(80));
    console.log('');

    // Step 1: Scan all files in canonical directory
    console.log('📂 Step 1: Scanning canonical directory...');
    const { allFiles, parseFailures } = await scanAllFiles();
    console.log(`   ✅ Found ${allFiles.length} parseable unit files`);
    if (parseFailures.length > 0) {
        console.log(`   ⚠️  Found ${parseFailures.length} files that failed to parse`);
    }
    console.log('');

    // Step 2: Read WORKFLOW_STATE.json
    console.log('📋 Step 2: Reading WORKFLOW_STATE.json...');
    const state = await readWorkflowState();
    console.log(`   ✅ WORKFLOW_STATE.json shows ${state.completed_count || state.completed.length} completed units`);
    console.log('');

    // Step 3: Compare
    console.log('🔍 Step 3: Comparing files to state...');
    const comparison = compareFilesToState(allFiles, state);
    console.log(`   📊 Files in directory:          ${comparison.totalFiles}`);
    console.log(`   📊 Entries in WORKFLOW_STATE:   ${comparison.totalState}`);
    console.log(`   📊 Discrepancy:                 ${comparison.discrepancy} files`);
    console.log('');

    // Step 4: Report findings
    if (comparison.discrepancy !== 0) {
        console.log('═'.repeat(80));
        console.log('  ⚠️  MISMATCH DETECTED');
        console.log('═'.repeat(80));
        console.log('');

        if (comparison.filesNotInState.length > 0) {
            console.log(`❌ ${comparison.filesNotInState.length} FILES EXIST BUT NOT IN WORKFLOW_STATE.json:`);
            console.log('   (These are "invisible" to /kstart - will be recommended again!)');
            console.log('');

            // Group by nation for easier reading
            const byNation = {};
            for (const file of comparison.filesNotInState) {
                if (!byNation[file.nation]) byNation[file.nation] = [];
                byNation[file.nation].push(file);
            }

            for (const [nation, files] of Object.entries(byNation)) {
                console.log(`   ${nation.toUpperCase()} (${files.length} missing):`);
                files.slice(0, 5).forEach(f => {
                    console.log(`      • ${f.quarter} - ${f.designation}`);
                    console.log(`        File: ${f.filename}`);
                    console.log(`        ID:   ${f.unitId}`);
                });
                if (files.length > 5) {
                    console.log(`      ... and ${files.length - 5} more`);
                }
                console.log('');
            }
        }

        if (comparison.stateNotInFiles.length > 0) {
            console.log(`👻 ${comparison.stateNotInFiles.length} WORKFLOW_STATE ENTRIES WITH NO MATCHING FILE:`);
            console.log('   (Ghost entries - should be removed from state)');
            console.log('');
            comparison.stateNotInFiles.slice(0, 10).forEach(id => {
                console.log(`      • ${id}`);
            });
            if (comparison.stateNotInFiles.length > 10) {
                console.log(`      ... and ${comparison.stateNotInFiles.length - 10} more`);
            }
            console.log('');
        }

        if (parseFailures.length > 0) {
            console.log(`🔴 ${parseFailures.length} FILES FAILED TO PARSE:`);
            console.log('   (These files exist but naming.parseFilename() can\'t process them)');
            console.log('');
            parseFailures.forEach(f => {
                console.log(`      • ${f.filename}`);
                console.log(`        Reason: ${f.reason}`);
            });
            console.log('');
        }
    } else {
        console.log('✅ No mismatch detected - files and state are in sync!');
        console.log('');
    }

    // Step 5: Recommendations
    console.log('═'.repeat(80));
    console.log('  RECOMMENDATIONS');
    console.log('═'.repeat(80));
    console.log('');

    if (comparison.filesNotInState.length > 0) {
        console.log('1. **Run state sync**:');
        console.log('   The session_start.js script should detect and sync these automatically.');
        console.log('   Try running: npm run session:start');
        console.log('');
        console.log('   If that doesn\'t work, the parsing logic may need fixes for these filenames.');
        console.log('');
    }

    if (comparison.stateNotInFiles.length > 0) {
        console.log('2. **Clean ghost entries**:');
        console.log('   WORKFLOW_STATE.json has entries for files that don\'t exist.');
        console.log('   These should be removed to prevent confusion.');
        console.log('');
    }

    if (parseFailures.length > 0) {
        console.log('3. **Fix parsing failures**:');
        console.log('   Some files have naming patterns that naming.parseFilename() can\'t handle.');
        console.log('   These need to be renamed or the parser needs to be updated.');
        console.log('');
    }

    // Generate detailed report
    const reportPath = path.join(PROJECT_ROOT, 'MISMATCH_DIAGNOSTIC_REPORT.json');
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            total_files_in_directory: comparison.totalFiles,
            total_entries_in_state: comparison.totalState,
            discrepancy: comparison.discrepancy
        },
        files_not_in_state: comparison.filesNotInState.map(f => ({
            filename: f.filename,
            unit_id: f.unitId,
            nation: f.nation,
            quarter: f.quarter,
            designation: f.designation
        })),
        state_not_in_files: comparison.stateNotInFiles,
        parse_failures: parseFailures
    };

    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    console.log(`📄 Detailed report saved: ${reportPath}`);
    console.log('');
    console.log('═'.repeat(80));
}

main().catch(error => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});
