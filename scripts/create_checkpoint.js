#!/usr/bin/env node

/**
 * Create Checkpoint - Save progress and commit
 *
 * Creates a checkpoint after batch completion:
 * 1. Updates WORKFLOW_STATE.json with current progress
 * 2. Creates SESSION_CHECKPOINT.md with recovery info
 * 3. Commits changes to git
 *
 * Usage: node scripts/create_checkpoint.js [batch_name]
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');
const { validateUnitFile } = require('./lib/validator');
const naming = require('./lib/naming_standard');
const paths = require('./lib/canonical_paths');

const PROJECT_ROOT = path.join(__dirname, '..');
const WORKFLOW_STATE_PATH = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');
const CHECKPOINT_PATH = path.join(PROJECT_ROOT, 'SESSION_CHECKPOINT.md');

async function readWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        // Initialize if doesn't exist
        return {
            last_updated: new Date().toISOString(),
            total_unit_quarters: 420,
            total_unique_units: 117,
            completed_count: 0,
            completion_percentage: 0,
            completed: [],
            in_progress: [],
            pending: [],
            session_id: `session_${Date.now()}`,
            last_commit: null
        };
    }
}

async function getCompletedUnits() {
    // Scan CANONICAL units directory ONLY (Architecture v4.0)
    const canonicalUnitsDir = paths.UNITS_DIR;
    const completed = [];

    try {
        // Simple flat scan of canonical directory (NO recursion)
        const files = await fs.readdir(canonicalUnitsDir);

        for (const filename of files) {
            if (filename.endsWith('_toe.json') && !filename.startsWith('unit_')) {
                // Extract unit info from filename using naming standard
                const parsed = naming.parseFilename(filename);
                if (parsed) {
                    completed.push({
                        nation: parsed.nation,
                        quarter: parsed.quarter, // Keep normalized format (1942q4)
                        unit: parsed.designation,
                        filename: filename
                    });
                }
            }
        }
    } catch (error) {
        console.warn('⚠️  Could not scan canonical units directory:', error.message);
        console.warn(`   Location: ${canonicalUnitsDir}`);
    }

    // Deduplicate by unit ID (should not have duplicates in canonical, but safety check)
    const uniqueMap = new Map();
    for (const unit of completed) {
        const unitId = `${unit.nation}_${unit.quarter}_${unit.unit}`;
        if (!uniqueMap.has(unitId)) {
            uniqueMap.set(unitId, unit);
        }
    }

    return Array.from(uniqueMap.values());
}

async function checkChapterStatus(completedUnits) {
    // Check if corresponding MDBook chapters exist in CANONICAL location (Architecture v4.0)
    const chapterStatus = {
        total: completedUnits.length,
        found: 0,
        missing: []
    };

    try {
        // Check canonical chapters directory only
        const canonicalChaptersDir = paths.CHAPTERS_DIR;
        const chapterFiles = await fs.readdir(canonicalChaptersDir);

        for (const unit of completedUnits) {
            // Build expected chapter filename (quarter already normalized)
            const expectedPattern = new RegExp(`chapter_${unit.nation}_${unit.quarter}_.*${unit.unit.replace(/_/g, '.*')}\\.md`, 'i');

            const chapterFound = chapterFiles.some(f => expectedPattern.test(f));

            if (chapterFound) {
                chapterStatus.found++;
            } else {
                chapterStatus.missing.push(`${unit.nation}_${unit.quarter}_${unit.unit}`);
            }
        }
    } catch (error) {
        console.warn('⚠️  Could not check canonical chapters directory:', error.message);
    }

    return chapterStatus;
}

async function updateWorkflowState(completedUnits, validationStatus, chapterStatus) {
    const state = await readWorkflowState();

    // CRITICAL: Only count units that meet ALL 3 requirements:
    // 1. JSON file exists (completedUnits from scan)
    // 2. Validation passes (no critical errors)
    // 3. Chapter file exists

    const validatedUnits = new Set();
    for (const violation of validationStatus.violations || []) {
        if (violation.critical && violation.critical.length > 0) {
            validatedUnits.add(violation.unit);
        }
    }

    const unitsWithChapters = new Set();
    for (const unit of completedUnits) {
        const unitId = `${unit.nation}_${unit.quarter}_${unit.unit}`;
        const chapterFilename = `chapter_${unit.nation}_${unit.quarter}_${unit.unit}.md`;
        if (!chapterStatus.missing.some(m => m.includes(chapterFilename))) {
            unitsWithChapters.add(unitId);
        }
    }

    // Filter to only units that pass validation AND have chapters
    const fullyCompletedUnits = completedUnits.filter(u => {
        const unitId = `${u.nation}_${u.quarter}_${u.unit}`;
        return !validatedUnits.has(unitId) && unitsWithChapters.has(unitId);
    });

    // Update completed list with VALIDATED units only
    const oldCompleted = new Set(state.completed || []);
    state.completed = fullyCompletedUnits.map(u => `${u.nation}_${u.quarter}_${u.unit}`);
    state.last_updated = new Date().toISOString();

    // Calculate units completed in this batch
    const newCompleted = state.completed.filter(u => !oldCompleted.has(u));
    const batchSize = newCompleted.length;

    // Get last git commit
    try {
        const commit = execSync('git rev-parse HEAD', {
            cwd: PROJECT_ROOT,
            encoding: 'utf-8'
        }).trim().substring(0, 7);
        state.last_commit = commit;
    } catch (error) {
        state.last_commit = 'unknown';
    }

    // Clear in_progress (checkpoint means batch is done)
    state.in_progress = [];

    // Ensure total_unit_quarters field exists
    if (!state.total_unit_quarters) {
        state.total_unit_quarters = 420;
        state.total_unique_units = 117;
    }

    // completed_count and completion_percentage are calculated by rebuild_workflow_state.js
    // based on matching to seed file. Preserve existing values if they exist.
    // If missing, just use completed.length as fallback
    if (!state.completed_count) {
        state.completed_count = state.completed.length;
        state.completion_percentage = ((state.completed.length / state.total_unit_quarters) * 100).toFixed(1);
    }

    // Increment session counter by batch size
    if (!state.current_session_count) {
        state.current_session_count = 0;
    }
    state.current_session_count += batchSize;

    await fs.writeFile(WORKFLOW_STATE_PATH, JSON.stringify(state, null, 2));

    return { state, batchSize };
}

async function regenerateWorkQueue() {
    try {
        const generateScript = path.join(PROJECT_ROOT, 'scripts/generate_work_queue.js');
        execSync(`node "${generateScript}"`, {
            cwd: PROJECT_ROOT,
            stdio: 'pipe',
            encoding: 'utf-8'
        });
        return true;
    } catch (error) {
        console.warn('⚠️  Failed to regenerate work queue:', error.message);
        return false;
    }
}

async function createCheckpointFile(state, chapterStatus, validationStatus) {
    const completedCount = state.completed_count || state.completed.length;
    const remaining = state.total_unit_quarters - completedCount;
    const percentComplete = ((completedCount / state.total_unit_quarters) * 100).toFixed(1);

    const checkpoint = `# Session Checkpoint - ${new Date().toISOString()}

## Progress Summary

- **Total Unit-Quarters:** ${state.total_unit_quarters}
- **Completed:** ${completedCount} (${percentComplete}%)
- **Remaining:** ${remaining}
- **Last Commit:** ${state.last_commit}

## Validation Status

- **Total Validated:** ${validationStatus.total}
- **✅ Passed:** ${validationStatus.passed} (${validationStatus.total > 0 ? ((validationStatus.passed / validationStatus.total) * 100).toFixed(1) : 0}%)
- **❌ Failed:** ${validationStatus.failed} ${validationStatus.failed === 0 ? '✅' : '⚠️'}
- **⚠️ Warnings:** ${validationStatus.warnings}

${validationStatus.violations.length > 0 ? `### Critical Validation Failures

${validationStatus.violations.slice(0, 3).map(v => `**${v.unit}:**\n${v.critical.map(c => `  - ❌ ${c}`).join('\n')}`).join('\n\n')}${validationStatus.violations.length > 3 ? `\n\n... and ${validationStatus.violations.length - 3} more. Run \`npm run validate\` for full report.` : ''}
` : '**All units passed validation** ✅\n'}
## Chapter Status

- **JSON Files:** ${chapterStatus.total}
- **MDBook Chapters:** ${chapterStatus.found} ${chapterStatus.found === chapterStatus.total ? '✅' : '⚠️'}
${chapterStatus.missing.length > 0 ? `- **Missing Chapters:** ${chapterStatus.missing.length}\n${chapterStatus.missing.slice(0, 5).map(u => `  - ❌ ${u}`).join('\n')}${chapterStatus.missing.length > 5 ? `\n  - ... and ${chapterStatus.missing.length - 5} more` : ''}` : '- **All chapters present** ✅'}

## Recent Completions

${state.completed.slice(-5).map(u => `- ✅ ${u}`).join('\n')}

## Recovery Instructions

If this session crashes or needs to resume:

1. **Check last commit:**
   \`\`\`bash
   git log -1 --oneline
   \`\`\`

2. **Resume from this checkpoint:**
   \`\`\`bash
   npm run session:start
   \`\`\`

3. **View full progress:**
   - See WORKFLOW_STATE.json for complete list
   - ${completedCount} units saved successfully

## Session Info

- **Session ID:** ${state.session_id}
- **Checkpoint Time:** ${state.last_updated}
- **Git Commit:** ${state.last_commit}

---

**Safe to start new batch** - All work committed to git.
`;

    await fs.writeFile(CHECKPOINT_PATH, checkpoint);
}

async function validateCompletedUnits(completedUnits) {
    // Validate all completed unit JSON files from CANONICAL location (Architecture v4.0)
    const validationStatus = {
        total: completedUnits.length,
        passed: 0,
        failed: 0,
        warnings: 0,
        violations: []
    };

    for (const unit of completedUnits) {
        // File path is in canonical location (simple join, no search needed)
        const filePath = path.join(paths.UNITS_DIR, unit.filename);

        try {
            // Check file exists
            await fs.access(filePath);

            // Validate the file
            const result = validateUnitFile(filePath);

            if (result.critical.length === 0 && result.warnings.length === 0) {
                validationStatus.passed++;
            } else if (result.critical.length > 0) {
                validationStatus.failed++;
                validationStatus.violations.push({
                    unit: `${unit.nation}_${unit.quarter}_${unit.unit}`,
                    critical: result.critical,
                    warnings: result.warnings
                });
            } else {
                validationStatus.warnings++;
            }
        } catch (error) {
            // File not found or validation error
            console.warn(`⚠️  Could not validate ${unit.filename}:`, error.message);
        }
    }

    return validationStatus;
}

async function commitCheckpoint(batchName) {
    try {
        // Call the existing git auto-commit script
        const gitScript = path.join(PROJECT_ROOT, 'scripts/git_auto_commit.js');
        execSync(`node "${gitScript}" "${batchName || 'checkpoint'}"`, {
            cwd: PROJECT_ROOT,
            stdio: 'inherit'
        });
        return true;
    } catch (error) {
        console.error('⚠️  Git commit failed:', error.message);
        console.log('💾 Progress saved locally - commit manually later');
        return false;
    }
}

async function main() {
    const batchName = process.argv[2];

    console.log('\n📍 Creating checkpoint...\n');

    // Get completed units
    console.log('🔍 Scanning for completed units...');
    const completedUnits = await getCompletedUnits();
    console.log(`   Found ${completedUnits.length} completed units\n`);

    // Validate completed units
    console.log('✅ Validating completed units...');
    const validationStatus = await validateCompletedUnits(completedUnits);
    console.log(`   ${validationStatus.passed}/${validationStatus.total} passed${validationStatus.failed > 0 ? `, ${validationStatus.failed} failed ⚠️` : ' ✅'}\n`);

    // Check chapter status
    console.log('📚 Checking MDBook chapters...');
    const chapterStatus = await checkChapterStatus(completedUnits);
    console.log(`   ${chapterStatus.found}/${chapterStatus.total} chapters found${chapterStatus.missing.length > 0 ? ` (${chapterStatus.missing.length} missing)` : ' ✅'}\n`);

    // Update workflow state (only count units that pass ALL requirements)
    console.log('💾 Updating WORKFLOW_STATE.json (validated units only)...');
    const { state, batchSize } = await updateWorkflowState(completedUnits, validationStatus, chapterStatus);
    const skippedCount = completedUnits.length - state.completed.length;
    console.log(`   ${state.completed_count || state.completed.length} / ${state.total_unit_quarters || 420} units complete (${((state.completed_count || state.completed.length) / (state.total_unit_quarters || 420) * 100).toFixed(1)}%)`);
    if (skippedCount > 0) {
        console.log(`   ⚠️  ${skippedCount} units skipped (failed validation or missing chapter)`);
    }
    console.log(`   Session counter: ${state.current_session_count || 0} units this session${batchSize > 0 ? ` (+${batchSize} validated)` : ''}\n`);

    // Regenerate work queue
    console.log('📋 Regenerating work queue...');
    const queueRegenerated = await regenerateWorkQueue();
    if (queueRegenerated) {
        console.log('   ✅ WORK_QUEUE.md updated with latest progress\n');
    } else {
        console.log('   ⚠️  Work queue regeneration failed (non-critical)\n');
    }

    // Create checkpoint file
    console.log('📝 Writing SESSION_CHECKPOINT.md...');
    await createCheckpointFile(state, chapterStatus, validationStatus);
    console.log('   ✅ Checkpoint file created\n');

    // Commit to git
    console.log('🚀 Committing to git...');
    const committed = await commitCheckpoint(batchName);

    if (committed) {
        console.log('\n✨ Checkpoint complete!\n');
        console.log(`📊 Progress: ${state.completed_count || state.completed.length}/${state.total_unit_quarters || 420} units`);
        console.log(`📍 Commit: ${state.last_commit}`);
        console.log(`🔢 Session: ${state.current_session_count || 0}/12 units this session`);

        // NO automatic session limit enforcement per user directive Oct 23, 2025

        console.log(`\n💾 Safe to continue or start new session\n`);
    } else {
        console.log('\n⚠️  Checkpoint saved locally (git commit failed)');
        console.log('   Run `git add . && git commit` manually\n');
    }
}

// Run
main().catch(error => {
    console.error('❌ Checkpoint failed:', error.message);
    process.exit(1);
});
