#!/usr/bin/env node

/**
 * Session Ready - One-command workflow starter (FIXED VERSION)
 *
 * Combines session:start with accurate file scanning and quarter dashboard
 * to create a single copy-paste prompt for Claude Code.
 *
 * FIXES:
 * - Scans actual files in autonomous folders AND data output units
 * - Handles format variations (1941-Q2, 1941--Q2, 1941q2)
 * - Shows quarter completion dashboard
 * - Suggests correct next batch
 *
 * Usage: node scripts/session_ready.js [target_quarter]
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const naming = require('./lib/naming_standard');

const PROJECT_ROOT = path.join(__dirname, '..');
const KEN_PROMPT_PATH = path.join(PROJECT_ROOT, 'STRICT AUTONOMOUS MODE - Ken Prompt.md');

// Target quarter for showcase (can be overridden via CLI arg)
const TARGET_QUARTER = process.argv[2] || '1941-Q2';

async function main() {
    console.log('\n' + '═'.repeat(80));
    console.log('  🚀 SESSION READY - Autonomous Workflow Starter (FIXED)');
    console.log('═'.repeat(80));
    console.log('');

    // Step 1: Create autonomous session folder
    const sessionId = 'autonomous_' + Date.now();
    const sessionDir = path.join(PROJECT_ROOT, 'data/output', sessionId);
    const unitsDir = path.join(sessionDir, 'units');

    try {
        fs.mkdirSync(sessionDir, { recursive: true });
        fs.mkdirSync(unitsDir, { recursive: true });
        console.log(`📁 Created session folder: ${sessionId}\n`);
    } catch (error) {
        console.error(`❌ Failed to create session folder: ${error.message}`);
        process.exit(1);
    }

    // Step 2: Scan actual files
    console.log('📊 Scanning actual unit files...\n');
    const completedFiles = scanCompletedFiles();
    console.log(`   Found ${completedFiles.length} completed units\n`);

    // Step 3: Load seed units
    const seedUnits = JSON.parse(fs.readFileSync(path.join(PROJECT_ROOT, 'projects/north_africa_seed_units.json'), 'utf-8'));

    // Step 4: Calculate ALL quarter progress
    const allQuartersProgress = calculateAllQuartersProgress(seedUnits, completedFiles);

    // Step 5: Get target quarter progress
    const targetQuarterProgress = allQuartersProgress.find(q => q.quarter === TARGET_QUARTER);

    // Step 6: Get next 3 units for target quarter
    const nextBatch = getNextBatchForQuarter(TARGET_QUARTER, seedUnits, completedFiles);

    // Step 7: Read Ken's guidelines
    let kenPrompt = '';
    try {
        kenPrompt = fs.readFileSync(KEN_PROMPT_PATH, 'utf-8');
    } catch (error) {
        console.warn('⚠️  Ken prompt not found, skipping guidelines');
    }

    // Step 8: Generate ready-to-paste prompt
    displayReadyPrompt(completedFiles.length, allQuartersProgress, targetQuarterProgress, nextBatch, sessionId);
}

function scanCompletedFiles() {
    const completedFiles = [];
    const outputDir = path.join(PROJECT_ROOT, 'data/output');

    function scanDir(dir) {
        try {
            const items = fs.readdirSync(dir, { withFileTypes: true });
            for (const item of items) {
                const fullPath = path.join(dir, item.name);
                if (item.isDirectory()) {
                    scanDir(fullPath);
                } else if (item.name.endsWith('_toe.json') && !item.name.startsWith('unit_')) {
                    completedFiles.push(item.name);
                }
            }
        } catch (error) {
            // Ignore errors
        }
    }

    scanDir(outputDir);
    return completedFiles;
}

function isCompleted(nation, designation, quarter, completedFiles) {
    // Use canonical naming standard for matching
    return completedFiles.some(filename => {
        return naming.matchesUnit(filename, nation, quarter, designation);
    });
}

function calculateAllQuartersProgress(seedUnits, completedFiles) {
    // Use canonical naming standard
    const nations = naming.NATION_MAP;

    const quarters = [
        '1940-Q2', '1940-Q3', '1940-Q4',
        '1941-Q1', '1941-Q2', '1941-Q3', '1941-Q4',
        '1942-Q1', '1942-Q2', '1942-Q3', '1942-Q4',
        '1943-Q1', '1943-Q2'
    ];

    const quarterStats = [];

    quarters.forEach(quarter => {
        let totalUnits = 0;
        let completedUnits = 0;
        const missingUnits = [];

        for (const [key, nation] of Object.entries(nations)) {
            const units = seedUnits[key] || [];
            const quarterUnits = units.filter(u => u.quarters && u.quarters.includes(quarter));

            quarterUnits.forEach(u => {
                totalUnits++;
                if (isCompleted(nation, u.designation, quarter, completedFiles)) {
                    completedUnits++;
                } else {
                    missingUnits.push({
                        nation: nation.charAt(0).toUpperCase() + nation.slice(1),
                        designation: u.designation
                    });
                }
            });
        }

        if (totalUnits > 0) {
            const percentage = Math.round((completedUnits / totalUnits) * 100);
            quarterStats.push({
                quarter,
                total: totalUnits,
                completed: completedUnits,
                remaining: totalUnits - completedUnits,
                percentage,
                missing: missingUnits
            });
        }
    });

    // Sort by completion percentage (highest first)
    quarterStats.sort((a, b) => b.percentage - a.percentage);

    return quarterStats;
}

function getNextBatchForQuarter(quarter, seedUnits, completedFiles) {
    const needed = [];
    // Use canonical naming standard
    const nations = naming.NATION_MAP;

    for (const [key, nation] of Object.entries(nations)) {
        const units = seedUnits[key] || [];
        const quarterUnits = units.filter(u => u.quarters && u.quarters.includes(quarter));

        quarterUnits.forEach(u => {
            if (!isCompleted(nation, u.designation, quarter, completedFiles)) {
                needed.push({
                    nation: nation.charAt(0).toUpperCase() + nation.slice(1),
                    designation: u.designation,
                    quarter: quarter
                });
            }
        });
    }

    // Return first 3
    return needed.slice(0, 3);
}

function displayReadyPrompt(totalCompleted, allQuartersProgress, targetQuarterProgress, nextBatch, sessionId) {
    const totalUnits = 213; // From project config
    const percentComplete = ((totalCompleted / totalUnits) * 100).toFixed(1);

    console.log('═'.repeat(80));
    console.log('  📊 QUARTER COMPLETION DASHBOARD');
    console.log('═'.repeat(80));
    console.log('');

    // Show top candidates
    const topCandidates = allQuartersProgress.filter(q => q.percentage >= 40 && q.remaining <= 10);
    if (topCandidates.length > 0) {
        console.log('🏆 **TOP CANDIDATES FOR COMPLETION:**\n');
        topCandidates.forEach((q, i) => {
            const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '  ';
            console.log(`   ${medal} ${q.quarter}: ${q.percentage}% Complete (${q.completed}/${q.total} units)`);
            console.log(`      Only ${q.remaining} units missing:`);
            q.missing.forEach(u => {
                console.log(`      ${u.remaining === q.remaining ? '└─' : '├─'} ${u.nation} - ${u.designation}`);
            });
            console.log('');
        });
    }

    // Show all quarters table
    console.log('📋 **ALL QUARTERS RANKED:**\n');
    console.log('Quarter      | Progress       | Status');
    console.log('-------------|----------------|----------------------------------');
    allQuartersProgress.forEach(q => {
        const status = q.percentage === 100 ? '✅ COMPLETE' :
                      q.percentage >= 80 ? `${q.remaining} missing ⭐ CLOSEST` :
                      q.percentage >= 50 ? `${q.remaining} missing` :
                      `${q.remaining} remaining`;
        console.log(`${q.quarter.padEnd(12)} | ${q.completed}/${q.total} (${q.percentage}%)`.padEnd(15) + ' | ' + status);
    });

    console.log('');
    console.log('─'.repeat(80));
    console.log('');

    // Overall progress
    console.log(`📊 **OVERALL PROGRESS:** ${totalCompleted}/${totalUnits} units (${percentComplete}%)\n`);

    console.log('═'.repeat(80));
    console.log('  📢 COPY THE MESSAGE BELOW AND PASTE INTO CLAUDE CODE CHAT');
    console.log('═'.repeat(80));
    console.log('');
    console.log('─'.repeat(80));
    console.log('');

    // The prompt to copy-paste
    console.log(`Start autonomous orchestration session.

**CURRENT PROGRESS:**
- Overall: ${totalCompleted}/${totalUnits} units (${percentComplete}%)
- Last scan: ${new Date().toLocaleString()}

**STRATEGY: Complete ${TARGET_QUARTER}**
${targetQuarterProgress ? `Progress: ${targetQuarterProgress.completed}/${targetQuarterProgress.total} (${targetQuarterProgress.percentage}%)` : 'Quarter not found'}

**NEXT BATCH (3 units - filling ${TARGET_QUARTER} gaps):**
${nextBatch.length > 0 ? nextBatch.map((u, i) => `${i + 1}. ${u.nation} - ${u.designation} (${u.quarter})`).join('\n') : '✅ No units needed - quarter complete!'}

**SESSION PROTOCOL (Ken's 3-3-3 Rule):**
✅ Session started (progress loaded above)
🔄 Process these 3 units in parallel (batch of 3)
💾 After batch complete: Bash('npm run checkpoint')
📊 Check validation: Review SESSION_CHECKPOINT.md for chapter status
🏁 When done: Bash('npm run session:end')

**UNIFIED SCHEMA COMPLIANCE (schemas/UNIFIED_SCHEMA_EXAMPLES.md):**
- **CRITICAL**: Use top-level fields (nation, quarter, organization_level)
- **NEVER** nest unit_identification, personnel_summary, equipment_summary
- Commander MUST be nested object: commander.name, commander.rank
- Nation values lowercase only: german, italian, british, american, french
- Tank totals MUST match: total = heavy + medium + light
- **Validation**: Run scripts/lib/validator.js before saving
- **Examples**: See schemas/UNIFIED_SCHEMA_EXAMPLES.md for correct/incorrect structures

**TEMPLATE COMPLIANCE (v2.0 - 16 Sections from MDBOOK_CHAPTER_TEMPLATE.md):**
- Section 3: Command (commander, HQ, staff) - REQUIRED
- Section 5: Artillery (summary + detail for EVERY variant)
- Section 6: Armored Cars (separate section with details, NOT in transport)
- Section 7: Transport (NO tanks/armored cars, all variants detailed)
- Section 12: Critical Equipment Shortages (Priority 1/2/3)
- Section 15: Data Quality & Known Gaps (honest assessment)
- **Confidence threshold**: ≥ 75%

**OUTPUT PATH (ALREADY CREATED FOR YOU):**
✅ Session folder: data/output/${sessionId}/
✅ Units folder: data/output/${sessionId}/units/

⚠️  **MANDATORY**: Save ALL files to:
   data/output/${sessionId}/units/[unit_file].json

   **NEVER** write to: data/output/units/ (deprecated legacy location)

**STOP CONDITIONS:**
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
