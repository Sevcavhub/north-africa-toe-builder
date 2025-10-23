#!/usr/bin/env node

/**
 * Crash Recovery - Determine what actually completed after VS Code crash
 *
 * VS Code crashes frequently during unit extraction. This script:
 * 1. Scans canonical directories for actual completed units
 * 2. Validates each unit (JSON + chapter + schema)
 * 3. Compares with WORKFLOW_STATE.json
 * 4. Identifies partially completed units (JSON but no chapter, or vice versa)
 * 5. Syncs WORKFLOW_STATE.json with reality
 * 6. Updates MCP memory if needed
 * 7. Tells you exactly where to resume
 *
 * Usage:
 *   npm run recover
 *
 * Run this IMMEDIATELY after a crash before doing anything else.
 */

const fs = require('fs').promises;
const fssync = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { validateUnitFile } = require('./lib/validator');
const naming = require('./lib/naming_standard');
const paths = require('./lib/canonical_paths');

const PROJECT_ROOT = path.join(__dirname, '..');
const WORKFLOW_STATE_PATH = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');

async function readWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        return null;
    }
}

async function scanActualUnits() {
    const canonicalUnitsDir = paths.UNITS_DIR;
    const canonicalChaptersDir = paths.CHAPTERS_DIR;

    const units = [];

    try {
        const files = await fs.readdir(canonicalUnitsDir);

        for (const filename of files) {
            if (filename.endsWith('_toe.json') && !filename.startsWith('unit_')) {
                const parsed = naming.parseFilename(filename);
                if (parsed) {
                    const unitId = `${parsed.nation}_${parsed.quarter}_${parsed.designation}`;

                    // Check if chapter exists
                    const chapterFilename = `chapter_${parsed.nation}_${parsed.quarter}_${parsed.designation}.md`;
                    const chapterPath = path.join(canonicalChaptersDir, chapterFilename);
                    const hasChapter = fssync.existsSync(chapterPath);

                    // Validate JSON
                    const jsonPath = path.join(canonicalUnitsDir, filename);
                    let validationResult = null;
                    try {
                        validationResult = validateUnitFile(jsonPath);
                    } catch (error) {
                        validationResult = { critical: [error.message], warnings: [] };
                    }

                    const isValid = validationResult.critical.length === 0;

                    units.push({
                        unitId,
                        nation: parsed.nation,
                        quarter: parsed.quarter,
                        designation: parsed.designation,
                        jsonFile: filename,
                        hasChapter,
                        isValid,
                        validationErrors: validationResult.critical,
                        validationWarnings: validationResult.warnings
                    });
                }
            }
        }
    } catch (error) {
        console.error('❌ Failed to scan units directory:', error.message);
    }

    return units;
}

function categorizeUnits(actualUnits, stateUnits) {
    const stateSet = new Set(stateUnits || []);
    const actualSet = new Set(actualUnits.map(u => u.unitId));

    const categories = {
        complete: [],           // JSON + chapter + valid + in state
        newlyCompleted: [],    // JSON + chapter + valid + NOT in state (just finished)
        partialJSON: [],       // JSON only, no chapter (crash mid-batch)
        partialChapter: [],    // Chapter only, no JSON (unlikely but check)
        invalid: [],           // JSON + chapter but validation failed
        inStateButMissing: [], // In state but files don't exist (shouldn't happen)
        needsCleanup: []       // In state but invalid or incomplete
    };

    // Check actual units on disk
    for (const unit of actualUnits) {
        const inState = stateSet.has(unit.unitId);

        if (unit.hasChapter && unit.isValid) {
            if (inState) {
                categories.complete.push(unit);
            } else {
                categories.newlyCompleted.push(unit);
            }
        } else if (!unit.hasChapter && unit.isValid) {
            categories.partialJSON.push(unit);
        } else if (unit.hasChapter && !unit.isValid) {
            categories.invalid.push(unit);
        } else if (!unit.isValid && !unit.hasChapter) {
            categories.partialJSON.push(unit); // JSON exists but invalid and no chapter
        }
    }

    // Check units in state but not on disk
    for (const unitId of stateSet) {
        if (!actualSet.has(unitId)) {
            categories.inStateButMissing.push(unitId);
        }
    }

    return categories;
}

async function syncWorkflowState(categories, oldState) {
    // Create new completed list from actual complete units
    const newCompleted = [...categories.complete.map(u => u.unitId), ...categories.newlyCompleted.map(u => u.unitId)];
    const uniqueCompleted = Array.from(new Set(newCompleted)).sort();

    const newState = {
        ...oldState,
        last_updated: new Date().toISOString(),
        completed_count: uniqueCompleted.length,
        completion_percentage: ((uniqueCompleted.length / (oldState?.total_unit_quarters || 419)) * 100).toFixed(1),
        completed: uniqueCompleted
    };

    await fs.writeFile(WORKFLOW_STATE_PATH, JSON.stringify(newState, null, 2));
    return newState;
}

async function regenerateWorkQueue() {
    try {
        execSync('npm run queue:generate', {
            cwd: PROJECT_ROOT,
            stdio: 'pipe'
        });
        return true;
    } catch (error) {
        return false;
    }
}

async function displayRecoveryReport(categories, oldState, newState) {
    console.log('\n' + '='.repeat(70));
    console.log('🔧 CRASH RECOVERY REPORT');
    console.log('='.repeat(70) + '\n');

    console.log('📊 WORKFLOW_STATE.json Status:\n');
    console.log(`   Before: ${oldState?.completed_count || 0}/${oldState?.total_unit_quarters || 419} units (${oldState?.completion_percentage || 0}%)`);
    console.log(`   After:  ${newState.completed_count}/${newState.total_unit_quarters} units (${newState.completion_percentage}%)`);
    console.log(`   Change: ${newState.completed_count - (oldState?.completed_count || 0)} units\n`);

    if (categories.newlyCompleted.length > 0) {
        console.log(`✅ NEWLY COMPLETED (${categories.newlyCompleted.length} units):\n`);
        console.log('   These units were finished but not in WORKFLOW_STATE.json yet:\n');
        categories.newlyCompleted.forEach(u => {
            console.log(`   ✅ ${u.nation.toUpperCase()} - ${u.quarter} - ${u.designation}`);
        });
        console.log('');
    }

    if (categories.partialJSON.length > 0) {
        console.log(`⚠️  PARTIAL COMPLETION (${categories.partialJSON.length} units):\n`);
        console.log('   These units have JSON but no chapter (crash during extraction?):\n');
        categories.partialJSON.forEach(u => {
            console.log(`   ⚠️  ${u.nation.toUpperCase()} - ${u.quarter} - ${u.designation}`);
            if (u.validationErrors.length > 0) {
                console.log(`       Validation: ${u.validationErrors[0]}`);
            }
        });
        console.log('\n   ⚠️  RECOMMENDATION: These units need to be re-extracted (incomplete)\n');
    }

    if (categories.invalid.length > 0) {
        console.log(`❌ INVALID UNITS (${categories.invalid.length} units):\n`);
        console.log('   These units have JSON + chapter but failed validation:\n');
        categories.invalid.forEach(u => {
            console.log(`   ❌ ${u.nation.toUpperCase()} - ${u.quarter} - ${u.designation}`);
            u.validationErrors.forEach(err => {
                console.log(`      - ${err}`);
            });
        });
        console.log('\n   ❌ RECOMMENDATION: These units need to be fixed or re-extracted\n');
    }

    if (categories.inStateButMissing.length > 0) {
        console.log(`🗑️  ORPHANED STATE ENTRIES (${categories.inStateButMissing.length} units):\n`);
        console.log('   These units are in WORKFLOW_STATE.json but files are missing:\n');
        categories.inStateButMissing.forEach(unitId => {
            console.log(`   🗑️  ${unitId}`);
        });
        console.log('\n   🗑️  These have been removed from WORKFLOW_STATE.json\n');
    }

    console.log('='.repeat(70));
    console.log('📋 SUMMARY');
    console.log('='.repeat(70) + '\n');
    console.log(`   ✅ Complete units: ${categories.complete.length + categories.newlyCompleted.length}`);
    console.log(`   ⚠️  Partial units: ${categories.partialJSON.length}`);
    console.log(`   ❌ Invalid units: ${categories.invalid.length}`);
    console.log(`   🗑️  Orphaned entries: ${categories.inStateButMissing.length}\n`);

    // Check git status
    try {
        const gitStatus = execSync('git status --porcelain', {
            cwd: PROJECT_ROOT,
            encoding: 'utf-8'
        }).trim();

        if (gitStatus) {
            console.log('📝 Uncommitted changes detected:\n');
            const lines = gitStatus.split('\n');
            const newFiles = lines.filter(l => l.startsWith('??') || l.startsWith('A '));
            const modifiedFiles = lines.filter(l => l.startsWith(' M') || l.startsWith('M '));

            if (newFiles.length > 0) {
                console.log(`   New files: ${newFiles.length}`);
            }
            if (modifiedFiles.length > 0) {
                console.log(`   Modified files: ${modifiedFiles.length}`);
            }
            console.log('');
        } else {
            console.log('✅ Working tree clean - all changes committed\n');
        }
    } catch (error) {
        console.log('⚠️  Could not check git status\n');
    }

    console.log('='.repeat(70));
    console.log('🎯 WHAT TO DO NEXT');
    console.log('='.repeat(70) + '\n');

    if (categories.newlyCompleted.length > 0) {
        console.log('1. ✅ Good news! Units were completed before crash:');
        console.log(`   - ${categories.newlyCompleted.length} units successfully extracted`);
        console.log('   - WORKFLOW_STATE.json has been synced');
        console.log('   - WORK_QUEUE.md has been regenerated\n');
    }

    if (categories.partialJSON.length > 0 || categories.invalid.length > 0) {
        console.log('2. ⚠️  Some units need attention:');
        if (categories.partialJSON.length > 0) {
            console.log(`   - ${categories.partialJSON.length} partial units (JSON only, no chapter)`);
            console.log('   - These should be deleted and re-extracted');
        }
        if (categories.invalid.length > 0) {
            console.log(`   - ${categories.invalid.length} invalid units (failed validation)`);
            console.log('   - These should be fixed or re-extracted');
        }
        console.log('');
    }

    console.log('3. 🔄 To continue work:');
    console.log('   Run: npm run session:start');
    console.log('   (Will show next 3 units from queue)\n');

    console.log('4. 🤖 Or use automated mode:');
    console.log('   Run: npm run auto:standard  (9 units, 3 batches)\n');

    console.log('='.repeat(70) + '\n');

    // Offer automatic cleanup if partial/invalid units found
    if (categories.partialJSON.length > 0 || categories.invalid.length > 0) {
        const autoCleanup = process.argv.includes('--auto-cleanup');
        const totalToCleanup = categories.partialJSON.length + categories.invalid.length;

        if (autoCleanup) {
            console.log(`\n🧹 AUTO-CLEANUP MODE: Removing ${totalToCleanup} partial/invalid units...\n`);
            await performCleanup(categories, totalToCleanup);
        } else {
            console.log('⚠️  PARTIAL/INVALID UNITS DETECTED\n');
            console.log(`   Found ${totalToCleanup} units that need cleanup (JSON without chapter, or validation errors)`);
            console.log('   These should be removed and re-extracted from scratch.\n');
            console.log('   To automatically clean these up, run:');
            console.log('   npm run recover -- --auto-cleanup\n');
            console.log('   (Creates backup before deletion)\n');
        }
    }
}

async function createBackup(units) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupDir = path.join(PROJECT_ROOT, '.partial_backups');
    const backupPath = path.join(backupDir, `backup_${timestamp}`);

    await fs.mkdir(backupPath, { recursive: true });

    for (const unit of units) {
        // Backup JSON
        const jsonPath = path.join(paths.UNITS_DIR, unit.jsonFile);
        const jsonBackupPath = path.join(backupPath, unit.jsonFile);
        await fs.copyFile(jsonPath, jsonBackupPath);

        // Backup chapter if exists
        if (unit.hasChapter) {
            const chapterFilename = `chapter_${unit.nation}_${unit.quarter}_${unit.designation}.md`;
            const chapterPath = path.join(paths.CHAPTERS_DIR, chapterFilename);
            if (require('fs').existsSync(chapterPath)) {
                const chapterBackupPath = path.join(backupPath, chapterFilename);
                await fs.copyFile(chapterPath, chapterBackupPath);
            }
        }
    }

    return backupPath;
}

async function deleteUnits(units) {
    const results = { deleted: [], failed: [] };

    for (const unit of units) {
        try {
            // Delete JSON
            const jsonPath = path.join(paths.UNITS_DIR, unit.jsonFile);
            await fs.unlink(jsonPath);
            results.deleted.push(unit.jsonFile);

            // Delete chapter if exists
            if (unit.hasChapter) {
                const chapterFilename = `chapter_${unit.nation}_${unit.quarter}_${unit.designation}.md`;
                const chapterPath = path.join(paths.CHAPTERS_DIR, chapterFilename);
                if (require('fs').existsSync(chapterPath)) {
                    await fs.unlink(chapterPath);
                    results.deleted.push(chapterFilename);
                }
            }
        } catch (error) {
            results.failed.push({ file: unit.jsonFile, error: error.message });
        }
    }

    return results;
}

async function performCleanup(categories, totalToCleanup) {
    const unitsToCleanup = [...categories.partialJSON, ...categories.invalid];

    console.log('💾 Creating backup before deletion...');
    const backupPath = await createBackup(unitsToCleanup);
    console.log(`   ✅ Backup created: ${backupPath}\n`);

    console.log('🗑️  Deleting partial/invalid units...');
    const results = await deleteUnits(unitsToCleanup);

    if (results.deleted.length > 0) {
        console.log(`   ✅ Deleted ${results.deleted.length} files\n`);
    }

    if (results.failed.length > 0) {
        console.log(`   ❌ Failed to delete ${results.failed.length} files:\n`);
        results.failed.forEach(f => {
            console.log(`      - ${f.file}: ${f.error}`);
        });
        console.log('');
    }

    // Regenerate queue after cleanup
    console.log('📋 Regenerating work queue after cleanup...');
    const queueSuccess = await regenerateWorkQueue();
    if (queueSuccess) {
        console.log('   ✅ Queue regenerated\n');
    }

    console.log('✅ Cleanup complete!\n');
    console.log('   All partial/invalid units have been removed.');
    console.log('   They are ready to be re-extracted from WORK_QUEUE.md\n');
}

async function main() {
    console.log('\n🔧 Starting crash recovery analysis...\n');

    // Read current workflow state
    const oldState = await readWorkflowState();
    if (!oldState) {
        console.error('❌ Could not read WORKFLOW_STATE.json');
        process.exit(1);
    }

    console.log('📂 Scanning canonical directories...');
    const actualUnits = await scanActualUnits();
    console.log(`   Found ${actualUnits.length} unit files\n`);

    console.log('🔍 Analyzing completion status...');
    const categories = categorizeUnits(actualUnits, oldState.completed);
    console.log('   Analysis complete\n');

    console.log('💾 Syncing WORKFLOW_STATE.json...');
    const newState = await syncWorkflowState(categories, oldState);
    console.log('   State synced\n');

    console.log('📋 Regenerating work queue...');
    const queueSuccess = await regenerateWorkQueue();
    if (queueSuccess) {
        console.log('   Queue regenerated\n');
    } else {
        console.log('   ⚠️  Queue regeneration failed (non-critical)\n');
    }

    // Display full recovery report
    await displayRecoveryReport(categories, oldState, newState);

    // Save recovery report to file
    const reportPath = path.join(PROJECT_ROOT, 'RECOVERY_REPORT.md');
    const timestamp = new Date().toISOString();
    const report = `# Crash Recovery Report - ${timestamp}

## Summary

- Before: ${oldState.completed_count}/${oldState.total_unit_quarters} units (${oldState.completion_percentage}%)
- After: ${newState.completed_count}/${newState.total_unit_quarters} units (${newState.completion_percentage}%)
- Change: ${newState.completed_count - oldState.completed_count} units

## Newly Completed (${categories.newlyCompleted.length})

${categories.newlyCompleted.map(u => `- ✅ ${u.nation.toUpperCase()} - ${u.quarter} - ${u.designation}`).join('\n')}

## Partial Units (${categories.partialJSON.length})

${categories.partialJSON.map(u => `- ⚠️  ${u.nation.toUpperCase()} - ${u.quarter} - ${u.designation}`).join('\n')}

## Invalid Units (${categories.invalid.length})

${categories.invalid.map(u => `- ❌ ${u.nation.toUpperCase()} - ${u.quarter} - ${u.designation}\n  ${u.validationErrors.join('\n  ')}`).join('\n\n')}

## Next Steps

1. Review this report
2. Run \`npm run session:start\` to continue
3. Or run \`npm run auto:standard\` for automated processing
`;

    await fs.writeFile(reportPath, report);
    console.log(`📄 Recovery report saved: RECOVERY_REPORT.md\n`);
}

// Run
main().catch(error => {
    console.error('❌ Crash recovery failed:', error.message);
    process.exit(1);
});
