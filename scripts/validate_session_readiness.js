#!/usr/bin/env node

/**
 * Pre-Flight Validation - Check session readiness
 *
 * Validates environment before starting new session:
 * - WORKFLOW_STATE.json exists and valid
 * - WORK_QUEUE.md exists
 * - No active session (SESSION_ACTIVE.txt)
 * - Canonical directories exist
 * - Warns about uncommitted changes
 *
 * Usage: npm run session:ready
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');
const paths = require('./lib/canonical_paths');

const PROJECT_ROOT = path.join(__dirname, '..');
const WORKFLOW_STATE_PATH = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');
const WORK_QUEUE_PATH = path.join(PROJECT_ROOT, 'WORK_QUEUE.md');
const SESSION_ACTIVE_PATH = path.join(PROJECT_ROOT, 'SESSION_ACTIVE.txt');

let errors = [];
let warnings = [];

async function checkWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE_PATH, 'utf-8');
        const state = JSON.parse(data);

        // Validate structure
        if (!state.completed || !Array.isArray(state.completed)) {
            errors.push('WORKFLOW_STATE.json: missing or invalid "completed" array');
        }
        if (typeof state.completed_count !== 'number') {
            warnings.push('WORKFLOW_STATE.json: completed_count missing (auto-repair will fix)');
        }

        console.log(`✅ WORKFLOW_STATE.json valid (${state.completed_count || state.completed.length}/420 units)`);
        return true;
    } catch (error) {
        errors.push(`WORKFLOW_STATE.json: ${error.message}`);
        return false;
    }
}

async function checkWorkQueue() {
    try {
        await fs.access(WORK_QUEUE_PATH);
        const content = await fs.readFile(WORK_QUEUE_PATH, 'utf-8');

        if (content.length < 100) {
            errors.push('WORK_QUEUE.md: file too small, may be corrupted');
        } else if (!content.includes('Next Up')) {
            warnings.push('WORK_QUEUE.md: may need regeneration (missing "Next Up" section)');
        }

        console.log('✅ WORK_QUEUE.md exists');
        return true;
    } catch (error) {
        errors.push(`WORK_QUEUE.md: ${error.message} - run "npm run queue:generate"`);
        return false;
    }
}

async function checkNoActiveSession() {
    try {
        await fs.access(SESSION_ACTIVE_PATH);
        errors.push('SESSION_ACTIVE.txt exists - session already running or unclean exit');
        errors.push('  Run "npm run session:end" or manually delete SESSION_ACTIVE.txt');
        return false;
    } catch (error) {
        console.log('✅ No active session');
        return true;
    }
}

async function checkCanonicalDirectories() {
    const dirs = [
        { path: paths.UNITS_DIR, name: 'Units' },
        { path: paths.CHAPTERS_DIR, name: 'Chapters' }
    ];

    for (const dir of dirs) {
        try {
            await fs.access(dir.path);
            console.log(`✅ ${dir.name} directory exists: ${dir.path}`);
        } catch (error) {
            warnings.push(`${dir.name} directory missing: ${dir.path} (will be created)`);
        }
    }

    return true;
}

function checkUncommittedChanges() {
    try {
        const status = execSync('git status --porcelain', {
            cwd: PROJECT_ROOT,
            encoding: 'utf-8'
        }).trim();

        if (status.length > 0) {
            const fileCount = status.split('\n').length;
            warnings.push(`${fileCount} uncommitted files - consider committing before session`);
            return false;
        }

        console.log('✅ Working tree clean');
        return true;
    } catch (error) {
        warnings.push('Could not check git status');
        return true;
    }
}

async function main() {
    console.log('');
    console.log('🔍 Pre-Flight Validation\n');
    console.log('─'.repeat(60));
    console.log('');

    // Run all checks
    await checkWorkflowState();
    await checkWorkQueue();
    await checkNoActiveSession();
    await checkCanonicalDirectories();
    checkUncommittedChanges();

    console.log('');
    console.log('─'.repeat(60));
    console.log('');

    // Report results
    if (errors.length > 0) {
        console.log('❌ VALIDATION FAILED\n');
        errors.forEach(err => console.log(`   • ${err}`));
        console.log('');
        console.log('Fix these issues before starting session.\n');
        process.exit(1);
    }

    if (warnings.length > 0) {
        console.log('⚠️  WARNINGS\n');
        warnings.forEach(warn => console.log(`   • ${warn}`));
        console.log('');
    }

    console.log('✅ SESSION READY\n');
    console.log('Run: npm run session:start\n');
}

main().catch(error => {
    console.error('❌ Pre-flight check failed:', error.message);
    process.exit(1);
});
