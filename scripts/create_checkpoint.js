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
            total_units: 213,
            completed: [],
            in_progress: [],
            pending: [],
            session_id: `session_${Date.now()}`,
            last_commit: null
        };
    }
}

async function getCompletedUnits() {
    // Scan for completed unit files
    const unitsDir = path.join(PROJECT_ROOT, 'data/output');
    const completed = [];

    try {
        // Find all unit JSON files recursively
        const findUnits = (dir) => {
            const items = require('fs').readdirSync(dir, { withFileTypes: true });
            for (const item of items) {
                const fullPath = path.join(dir, item.name);
                if (item.isDirectory()) {
                    findUnits(fullPath);
                } else if (item.name.endsWith('_toe.json') && !item.name.startsWith('unit_')) {
                    // Extract unit info from filename
                    const match = item.name.match(/^([a-z]+)_(\d{4}[-]?q\d)_(.+)_toe\.json$/i);
                    if (match) {
                        completed.push({
                            nation: match[1],
                            quarter: match[2].toUpperCase().replace(/Q/, '-Q'),
                            unit: match[3],
                            filename: item.name
                        });
                    }
                }
            }
        };

        findUnits(unitsDir);
    } catch (error) {
        console.warn('⚠️  Could not scan units directory:', error.message);
    }

    return completed;
}

async function checkChapterStatus(completedUnits) {
    // Check if corresponding MDBook chapters exist for each JSON file
    const chapterStatus = {
        total: completedUnits.length,
        found: 0,
        missing: []
    };

    for (const unit of completedUnits) {
        // Look for chapter files in all autonomous session directories
        const outputDir = path.join(PROJECT_ROOT, 'data/output');
        let chapterFound = false;

        try {
            const checkDir = (dir) => {
                const items = require('fs').readdirSync(dir, { withFileTypes: true });
                for (const item of items) {
                    if (item.isDirectory()) {
                        const fullPath = path.join(dir, item.name);
                        if (item.name === 'north_africa_book') {
                            // Check for chapter file
                            const srcDir = path.join(fullPath, 'src');
                            if (require('fs').existsSync(srcDir)) {
                                const chapterPattern = new RegExp(`chapter_${unit.nation}_.*${unit.unit.replace(/_/g, '.*')}\\.md`, 'i');
                                const files = require('fs').readdirSync(srcDir);
                                if (files.some(f => chapterPattern.test(f))) {
                                    chapterFound = true;
                                    return true;
                                }
                            }
                        } else if (!item.name.startsWith('.')) {
                            checkDir(fullPath);
                        }
                    }
                }
                return false;
            };

            checkDir(outputDir);
        } catch (error) {
            // Ignore errors, just mark as not found
        }

        if (chapterFound) {
            chapterStatus.found++;
        } else {
            chapterStatus.missing.push(`${unit.nation}_${unit.quarter}_${unit.unit}`);
        }
    }

    return chapterStatus;
}

async function updateWorkflowState(completedUnits) {
    const state = await readWorkflowState();

    // Update completed list
    state.completed = completedUnits.map(u => `${u.nation}_${u.quarter}_${u.unit}`);
    state.last_updated = new Date().toISOString();

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

    await fs.writeFile(WORKFLOW_STATE_PATH, JSON.stringify(state, null, 2));

    return state;
}

async function createCheckpointFile(state, chapterStatus, validationStatus) {
    const completedCount = state.completed.length;
    const remaining = state.total_units - completedCount;
    const percentComplete = ((completedCount / state.total_units) * 100).toFixed(1);

    const checkpoint = `# Session Checkpoint - ${new Date().toISOString()}

## Progress Summary

- **Total Units:** ${state.total_units}
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
    // Validate all completed unit JSON files
    const validationStatus = {
        total: completedUnits.length,
        passed: 0,
        failed: 0,
        warnings: 0,
        violations: []
    };

    for (const unit of completedUnits) {
        // Find the file path
        const outputDir = path.join(PROJECT_ROOT, 'data/output');
        let filePath = null;

        try {
            const findFile = (dir) => {
                const items = require('fs').readdirSync(dir, { withFileTypes: true });
                for (const item of items) {
                    const fullPath = path.join(dir, item.name);
                    if (item.isDirectory()) {
                        const found = findFile(fullPath);
                        if (found) return found;
                    } else if (item.name === unit.filename) {
                        return fullPath;
                    }
                }
                return null;
            };

            filePath = findFile(outputDir);
        } catch (error) {
            // Ignore search errors
        }

        if (!filePath) continue;

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

    // Update workflow state
    console.log('💾 Updating WORKFLOW_STATE.json...');
    const state = await updateWorkflowState(completedUnits);
    console.log(`   ${state.completed.length} / ${state.total_units} units complete (${((state.completed.length / state.total_units) * 100).toFixed(1)}%)\n`);

    // Create checkpoint file
    console.log('📝 Writing SESSION_CHECKPOINT.md...');
    await createCheckpointFile(state, chapterStatus, validationStatus);
    console.log('   ✅ Checkpoint file created\n');

    // Commit to git
    console.log('🚀 Committing to git...');
    const committed = await commitCheckpoint(batchName);

    if (committed) {
        console.log('\n✨ Checkpoint complete!\n');
        console.log(`📊 Progress: ${state.completed.length}/${state.total_units} units`);
        console.log(`📍 Commit: ${state.last_commit}`);
        console.log(`💾 Safe to continue or start new session\n`);
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
