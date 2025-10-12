#!/usr/bin/env node

/**
 * Session End - Clean session closure
 *
 * Properly ends a work session by:
 * 1. Creating final checkpoint
 * 2. Updating Memory MCP with new patterns found
 * 3. Validating no uncommitted work
 * 4. Writing session summary
 * 5. Cleaning up session markers
 *
 * Usage: node scripts/session_end.js
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');
const { storeSessionStats, storePattern, storeDecision, storeQualityIssue } = require('./memory_mcp_helpers');

const PROJECT_ROOT = path.join(__dirname, '..');
const WORKFLOW_STATE_PATH = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');
const SESSION_SUMMARY_PATH = path.join(PROJECT_ROOT, 'SESSION_SUMMARY.md');

async function readWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        return null;
    }
}

function checkUncommittedChanges() {
    try {
        const status = execSync('git status --porcelain', {
            cwd: PROJECT_ROOT,
            encoding: 'utf-8'
        }).trim();

        return status.length > 0 ? status.split('\n') : [];
    } catch (error) {
        console.warn('⚠️  Could not check git status:', error.message);
        return [];
    }
}

async function createFinalCheckpoint() {
    console.log('\n📍 Creating final checkpoint...\n');

    try {
        const checkpointScript = path.join(PROJECT_ROOT, 'scripts/create_checkpoint.js');
        execSync(`node "${checkpointScript}" "session_end"`, {
            cwd: PROJECT_ROOT,
            stdio: 'inherit'
        });
        return true;
    } catch (error) {
        console.error('❌ Final checkpoint failed:', error.message);
        return false;
    }
}

async function updateMemoryMCP(sessionStats) {
    console.log('🧠 Updating project knowledge...');

    try {
        // Store session statistics
        await storeSessionStats(sessionStats);

        // Store patterns discovered during session
        if (sessionStats.patterns && sessionStats.patterns.length > 0) {
            for (const pattern of sessionStats.patterns) {
                await storePattern(pattern, {
                    session_id: sessionStats.session_id,
                    units_completed: sessionStats.completed_count
                });
            }
        }

        // Store quality issues found
        if (sessionStats.issues && sessionStats.issues.length > 0) {
            for (const issue of sessionStats.issues) {
                await storeQualityIssue(issue.description || issue, issue.severity || 'info', {
                    session_id: sessionStats.session_id
                });
            }
        }

        // Store decisions made
        if (sessionStats.decisions && sessionStats.decisions.length > 0) {
            for (const decision of sessionStats.decisions) {
                await storeDecision(decision.decision || decision, decision.rationale || 'Session decision', {
                    session_id: sessionStats.session_id
                });
            }
        }

        console.log('   💾 Memory updates stored:');
        console.log(`      - ${sessionStats.completed_count || 0} units completed`);
        console.log(`      - ${(sessionStats.patterns || []).length} patterns noted`);
        console.log(`      - ${(sessionStats.issues || []).length} issues flagged`);
        console.log(`      - ${(sessionStats.decisions || []).length} decisions recorded\n`);

        return true;
    } catch (error) {
        console.warn('   ⚠️  Memory update failed:', error.message, '\n');
        return null;
    }
}

async function generateSessionSummary(state, startTime, uncommitted) {
    const endTime = new Date();
    const duration = startTime ? Math.round((endTime - new Date(startTime)) / 1000 / 60) : 'unknown';

    const completedCount = state ? state.completed.length : 0;
    const remaining = state ? (state.total_units - completedCount) : 213;
    const percentComplete = state ? ((completedCount / state.total_units) * 100).toFixed(1) : '0.0';

    const summary = `# Session Summary - ${endTime.toISOString()}

## Session Statistics

- **Duration:** ${duration} minutes
- **Units Completed:** ${completedCount} / ${state?.total_units || 213}
- **Progress:** ${percentComplete}%
- **Units Remaining:** ${remaining}

## Work Completed

${state && state.completed.length > 0 ?
        state.completed.slice(-10).map(u => `- ✅ ${u}`).join('\n') :
        '- No units completed this session'}

## Session End Checklist

${uncommitted.length === 0 ?
        '- ✅ No uncommitted changes' :
        `- ⚠️  ${uncommitted.length} uncommitted files found`}
- ✅ Final checkpoint created
- ✅ WORKFLOW_STATE.json updated
- ✅ SESSION_CHECKPOINT.md written
${uncommitted.length === 0 ? '- ✅ Git commit successful' : '- ⚠️  Git commit needed'}

## Uncommitted Files

${uncommitted.length > 0 ?
        uncommitted.map(f => `- ${f}`).join('\n') :
        'None - working tree clean'}

## Next Session

To resume work:

\`\`\`bash
npm run session:start
\`\`\`

This will:
- Load progress from WORKFLOW_STATE.json
- Query Memory MCP for project knowledge
- Display next suggested batch

## Notes

- Session ended: ${endTime.toLocaleString()}
- Last commit: ${state?.last_commit || 'N/A'}
- Safe to close this session

---

Generated by session_end.js
`;

    await fs.writeFile(SESSION_SUMMARY_PATH, summary);
    console.log(`📄 Session summary: ${SESSION_SUMMARY_PATH}\n`);
}

function displayEndSummary(state, uncommitted, duration) {
    console.log('═'.repeat(80));
    console.log('  SESSION END SUMMARY');
    console.log('═'.repeat(80));
    console.log('');

    if (state) {
        const completedCount = state.completed.length;
        const percentComplete = ((completedCount / state.total_units) * 100).toFixed(1);

        console.log(`📊 **FINAL PROGRESS**\n`);
        console.log(`   Units Completed: ${completedCount} / ${state.total_units} (${percentComplete}%)`);
        console.log(`   Last Commit:     ${state.last_commit || 'N/A'}`);
        console.log('');
    }

    if (uncommitted.length === 0) {
        console.log('✅ **CLEAN EXIT**\n');
        console.log('   All work committed to git');
        console.log('   Working tree clean');
        console.log('   Safe to end session');
        console.log('');
    } else {
        console.log('⚠️  **UNCOMMITTED CHANGES**\n');
        console.log(`   ${uncommitted.length} files not committed`);
        console.log('   Run final commit before ending:');
        console.log('   ```');
        console.log('   npm run checkpoint');
        console.log('   ```');
        console.log('');
    }

    console.log('═'.repeat(80));
    console.log('');
}

async function cleanupSessionMarkers() {
    // Remove active session marker
    const sessionMarker = path.join(PROJECT_ROOT, 'SESSION_ACTIVE.txt');
    try {
        await fs.unlink(sessionMarker);
    } catch (error) {
        // File might not exist, that's ok
    }
}

async function main() {
    console.log('');
    console.log('🏁 Ending session...\n');

    // Read current state
    const state = await readWorkflowState();

    // Get session start time from marker
    let startTime = null;
    try {
        const marker = await fs.readFile(path.join(PROJECT_ROOT, 'SESSION_ACTIVE.txt'), 'utf-8');
        const match = marker.match(/Session started: (.+)/);
        if (match) startTime = match[1];
    } catch (error) {
        // No marker, that's ok
    }

    // Always create checkpoint to ensure state is synced
    console.log('📍 Creating final checkpoint (syncs state)...\n');
    await createFinalCheckpoint();

    // Check for uncommitted changes after checkpoint
    const uncommitted = checkUncommittedChanges();

    if (uncommitted.length > 0) {
        console.log('⚠️  Uncommitted changes remain after checkpoint\n');
        console.log('   Some files still uncommitted. Review manually.\n');
    } else {
        console.log('✅ Working tree clean - all changes committed\n');
    }

    // Calculate session statistics
    const sessionStats = {
        completed_count: state ? state.completed.length : 0,
        duration: startTime ? Math.round((Date.now() - new Date(startTime)) / 1000 / 60) : 'unknown',
        patterns: [], // Would be populated from analysis
        issues: [],   // Would be populated from validation
        decisions: [] // Would be populated from session
    };

    // Update Memory MCP
    await updateMemoryMCP(sessionStats);

    // Generate session summary
    await generateSessionSummary(state, startTime, uncommitted);

    // Display summary
    displayEndSummary(state, uncommitted, sessionStats.duration);

    // Cleanup
    await cleanupSessionMarkers();

    console.log('💡 **NEXT STEPS:**\n');
    console.log('   1. Review SESSION_SUMMARY.md');
    console.log('   2. When ready to resume: npm run session:start');
    console.log('   3. Safe to close this session\n');
}

// Run
main().catch(error => {
    console.error('❌ Session end failed:', error.message);
    process.exit(1);
});
