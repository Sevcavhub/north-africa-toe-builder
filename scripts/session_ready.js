#!/usr/bin/env node

/**
 * Session Ready - One-command workflow starter
 *
 * Combines session:start with year-based priority and Ken's guidelines
 * to create a single copy-paste prompt for Claude Code.
 *
 * Usage: node scripts/session_ready.js
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const KEN_PROMPT_PATH = path.join(PROJECT_ROOT, 'STRICT AUTONOMOUS MODE - Ken Prompt.md');

// Target quarter for showcase (can be made configurable later)
const TARGET_QUARTER = '1941-Q2';

async function main() {
    console.log('\n' + '═'.repeat(80));
    console.log('  🚀 SESSION READY - Autonomous Workflow Starter');
    console.log('═'.repeat(80));
    console.log('');

    // Step 1: Run session:start (which now includes auto-sync)
    console.log('📊 Loading session state and scanning files...\n');
    try {
        execSync('node scripts/session_start.js', {
            cwd: PROJECT_ROOT,
            stdio: 'inherit'
        });
    } catch (error) {
        console.error('❌ Session start failed:', error.message);
        process.exit(1);
    }

    console.log('\n' + '─'.repeat(80));
    console.log('  📋 GENERATING AUTONOMOUS PROMPT');
    console.log('─'.repeat(80) + '\n');

    // Step 2: Load state and seed units
    const state = JSON.parse(fs.readFileSync(path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json'), 'utf-8'));
    const seedUnits = JSON.parse(fs.readFileSync(path.join(PROJECT_ROOT, 'projects/north_africa_seed_units.json'), 'utf-8'));

    // Step 3: Calculate quarter progress
    const quarterProgress = calculateQuarterProgress(TARGET_QUARTER, seedUnits, state.completed);

    // Step 4: Get next 3 units prioritizing target quarter
    const nextBatch = getNextBatchForQuarter(TARGET_QUARTER, seedUnits, state.completed);

    // Step 5: Read Ken's guidelines
    const kenPrompt = fs.readFileSync(KEN_PROMPT_PATH, 'utf-8');
    const keyGuidelines = extractKeyGuidelines(kenPrompt);

    // Step 6: Generate ready-to-paste prompt
    displayReadyPrompt(state, quarterProgress, nextBatch, keyGuidelines);
}

function calculateQuarterProgress(quarter, seedUnits, completed) {
    const byNation = {
        german: { total: 0, completed: 0 },
        italian: { total: 0, completed: 0 },
        british: { total: 0, completed: 0 },
        usa: { total: 0, completed: 0 },
        french: { total: 0, completed: 0 }
    };

    const nationMap = {
        'german_units': 'german',
        'italian_units': 'italian',
        'british_units': 'british',
        'usa_units': 'usa',
        'french_units': 'french'
    };

    // Count units in target quarter
    for (const [key, units] of Object.entries(seedUnits)) {
        const nation = nationMap[key] || key.replace('_units', '');
        if (!byNation[nation]) continue;
        if (!Array.isArray(units)) continue; // Skip non-array entries

        for (const unit of units) {
            if (!unit.quarters || !Array.isArray(unit.quarters)) continue;
            if (unit.quarters.includes(quarter)) {
                byNation[nation].total++;

                // Check if completed
                const unitId = createUnitId(nation, unit.designation, quarter);
                if (completed.includes(unitId)) {
                    byNation[nation].completed++;
                }
            }
        }
    }

    return byNation;
}

function getNextBatchForQuarter(quarter, seedUnits, completed) {
    const needed = [];
    const nationMap = {
        'german_units': 'germany',
        'italian_units': 'italy',
        'british_units': 'britain',
        'usa_units': 'usa',
        'french_units': 'france'
    };

    for (const [key, units] of Object.entries(seedUnits)) {
        const nation = nationMap[key] || key.replace('_units', '');
        if (!Array.isArray(units)) continue; // Skip non-array entries

        for (const unit of units) {
            if (!unit.quarters || !Array.isArray(unit.quarters)) continue;
            if (unit.quarters.includes(quarter)) {
                const unitId = createUnitId(nation, unit.designation, quarter);
                if (!completed.includes(unitId)) {
                    needed.push({
                        nation: nation.charAt(0).toUpperCase() + nation.slice(1),
                        designation: unit.designation,
                        quarter: quarter
                    });
                }
            }
        }
    }

    // Return first 3
    return needed.slice(0, 3);
}

function createUnitId(nation, designation, quarter) {
    // Create ID matching WORKFLOW_STATE.json format
    const cleanNation = nation.toLowerCase();
    const cleanQuarter = quarter.toUpperCase().replace('-', '');
    const cleanDesignation = designation.toLowerCase()
        .replace(/[^a-z0-9]/g, '_')
        .replace(/_+/g, '_')
        .replace(/^_|_$/g, '');
    return `${cleanNation}_${cleanQuarter}_${cleanDesignation}`;
}

function extractKeyGuidelines(kenPrompt) {
    // Extract key sections from Ken's .md file
    const guidelines = {
        sessionProtocol: '',
        validation: '',
        stopConditions: ''
    };

    // Simple extraction (can be made more robust)
    const protocolMatch = kenPrompt.match(/## SESSION MANAGEMENT PROTOCOL([\s\S]*?)(?=##|$)/);
    if (protocolMatch) {
        guidelines.sessionProtocol = protocolMatch[1].trim().substring(0, 500) + '...';
    }

    const validationMatch = kenPrompt.match(/## MANDATORY VALIDATION CHECKLIST([\s\S]*?)(?=##|$)/);
    if (validationMatch) {
        guidelines.validation = validationMatch[1].trim().substring(0, 500) + '...';
    }

    const stopMatch = kenPrompt.match(/## STOP CONDITIONS([\s\S]*?)(?=##|$)/);
    if (stopMatch) {
        guidelines.stopConditions = stopMatch[1].trim().substring(0, 300) + '...';
    }

    return guidelines;
}

function displayReadyPrompt(state, quarterProgress, nextBatch, guidelines) {
    const completedCount = state.completed.length;
    const percentComplete = ((completedCount / state.total_units) * 100).toFixed(1);

    // Calculate total for target quarter
    let quarterTotal = 0;
    let quarterCompleted = 0;
    for (const nation in quarterProgress) {
        quarterTotal += quarterProgress[nation].total;
        quarterCompleted += quarterProgress[nation].completed;
    }
    const quarterPercent = quarterTotal > 0 ? ((quarterCompleted / quarterTotal) * 100).toFixed(0) : 0;

    console.log('═'.repeat(80));
    console.log('  📢 COPY THE MESSAGE BELOW AND PASTE INTO CLAUDE CODE CHAT');
    console.log('═'.repeat(80));
    console.log('');
    console.log('─'.repeat(80));
    console.log('');

    // The prompt to copy-paste
    console.log(`Start autonomous orchestration session following Ken's guidelines.

**CURRENT PROGRESS:**
- Overall: ${completedCount}/${state.total_units} units (${percentComplete}%)
- Last updated: ${new Date(state.last_updated).toLocaleString()}

**SHOWCASE STRATEGY: Complete ${TARGET_QUARTER} snapshot**
Goal: Build one complete quarter as quality reference before scaling to full campaign.

**${TARGET_QUARTER} PROGRESS (Target Showcase Quarter):**
${Object.entries(quarterProgress).map(([nation, data]) => {
    if (data.total === 0) return null;
    const pct = data.total > 0 ? ((data.completed / data.total) * 100).toFixed(0) : 0;
    const status = pct == 100 ? '✅ COMPLETE' : `${pct}%`;
    return `- ${nation.charAt(0).toUpperCase() + nation.slice(1)}: ${data.completed}/${data.total} (${status})`;
}).filter(Boolean).join('\n')}
- **Quarter Total**: ${quarterCompleted}/${quarterTotal} units (${quarterPercent}%)

**NEXT BATCH (3 units - filling ${TARGET_QUARTER} gaps):**
${nextBatch.length > 0 ? nextBatch.map((u, i) => `${i + 1}. ${u.nation} - ${u.designation} (${u.quarter})`).join('\n') : 'No units needed - quarter complete!'}

**SESSION PROTOCOL (Ken's 3-3-3 Rule):**
✅ Session started (progress loaded above)
🔄 Process these 3 units in parallel (batch of 3)
💾 After batch complete: Bash('npm run checkpoint')
📊 Check validation: Review SESSION_CHECKPOINT.md for chapter status
🏁 When done: Bash('npm run session:end')

**TEMPLATE COMPLIANCE (v2.0 - 16 Sections from MDBOOK_CHAPTER_TEMPLATE.md):**
- Section 3: Command (commander, HQ, staff) - REQUIRED
- Section 5: Artillery (summary + detail for EVERY variant)
- Section 6: Armored Cars (separate section with details, NOT in transport)
- Section 7: Transport (NO tanks/armored cars, all variants detailed)
- Section 12: Critical Equipment Shortages (Priority 1/2/3)
- Section 15: Data Quality & Known Gaps (honest assessment)
- **Confidence threshold**: ≥ 75%

**QUALITY REVIEW (After ${TARGET_QUARTER} complete):**
Run existing QA agent to review all work:
\`\`\`bash
npm run qa:audit
\`\`\`
This generates GAP_TRACKER.md with quality metrics.

Review chapters via MDBook:
\`\`\`bash
cd data/output/autonomous_[session_id]/north_africa_book
mdbook serve --open
\`\`\`

**STOP CONDITIONS (from Ken's guidelines):**
- Validation fails after 2 regeneration attempts
- Confidence score < 75% for any unit
- Critical gaps cannot be resolved (missing commander, no equipment data)
- Template violations detected in generated chapters
- Source documents unavailable for nation/quarter

**AUTONOMOUS EXECUTION:**
Begin processing the 3-unit batch now using:
- Task tool for parallel agent processing
- Extended thinking for complex source analysis
- TodoWrite to track progress
- Automatic checkpoint after batch completion

Ready to start? Confirm and I'll begin autonomous orchestration.`);

    console.log('');
    console.log('─'.repeat(80));
    console.log('');
    console.log('═'.repeat(80));
    console.log('');
    console.log('💡 **TIPS:**');
    console.log('   - Claude will process units autonomously using Task tool');
    console.log('   - Checkpoint runs automatically after batch (updates state)');
    console.log('   - Session:end syncs final state and creates summary');
    console.log(`   - Once ${TARGET_QUARTER} complete, run QA agent for quality review`);
    console.log('');
    console.log('📚 **FULL GUIDELINES:** See "STRICT AUTONOMOUS MODE - Ken Prompt.md"');
    console.log('');
    console.log('═'.repeat(80));
    console.log('');
}

// Run
main().catch(error => {
    console.error('❌ Session ready failed:', error.message);
    process.exit(1);
});
