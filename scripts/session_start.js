#!/usr/bin/env node

/**
 * Session Start - Initialize new work session with strategy selection
 *
 * Prepares for autonomous work by:
 * 1. Reading WORKFLOW_STATE.json to find resume point
 * 2. Querying Memory MCP for project knowledge (if available)
 * 3. Showing quarter completion dashboard
 * 4. Offering strategy choice: Chronological vs Quarter Completion
 * 5. Generating appropriate next batch (3 units)
 *
 * Usage:
 *   node scripts/session_start.js               # Interactive (prompts for strategy)
 *   node scripts/session_start.js chronological # Earliest quarter
 *   node scripts/session_start.js quarter       # Highest completion %
 *   node scripts/session_start.js 1941-Q2       # Specific quarter
 */

const fs = require('fs').promises;
const fssync = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { queryProjectKnowledge } = require('./memory_mcp_helpers');
const naming = require('./lib/naming_standard');
const paths = require('./lib/canonical_paths');
const matching = require('./lib/matching');
const { validateAndRepairState } = require('./lib/state_validator');

const PROJECT_ROOT = path.join(__dirname, '..');
const WORKFLOW_STATE_PATH = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');

async function readWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE_PATH, 'utf-8');
        const parsedState = JSON.parse(data);
        
        // Validate and auto-repair if needed
        const { state, repairs } = validateAndRepairState(parsedState, true);
        
        // If repairs were made, save the corrected state
        if (repairs.length > 0) {
            await fs.writeFile(WORKFLOW_STATE_PATH, JSON.stringify(state, null, 2));
            console.log('✅ WORKFLOW_STATE.json has been auto-repaired and saved\n');
        }
        
        return state;
    } catch (error) {
        return null;
    }
}

async function getCompletedUnits() {
    const canonicalUnitsDir = paths.UNITS_DIR;
    const completed = [];

    try {
        const files = await fs.readdir(canonicalUnitsDir);

        for (const filename of files) {
            if (filename.endsWith('_toe.json') && !filename.startsWith('unit_')) {
                const parsed = naming.parseFilename(filename);
                if (parsed) {
                    completed.push({
                        nation: parsed.nation,
                        quarter: parsed.quarter,
                        unit: parsed.designation,
                        filename: filename
                    });
                }
            }
        }
    } catch (error) {
        console.warn('⚠️  Could not scan canonical units directory:', error.message);
    }

    const uniqueMap = new Map();
    for (const unit of completed) {
        const unitId = `${unit.nation}_${unit.quarter}_${unit.unit}`;
        if (!uniqueMap.has(unitId)) {
            uniqueMap.set(unitId, unit);
        }
    }

    return Array.from(uniqueMap.values());
}

async function syncWorkflowState(scannedUnits, currentState) {
    const scannedIds = scannedUnits.map(u => `${u.nation}_${u.quarter}_${u.unit}`);
    const stateIds = currentState ? currentState.completed : [];

    if (scannedIds.length !== stateIds.length) {
        const newState = currentState || {
            last_updated: new Date().toISOString(),
            total_unit_quarters: 420,
            total_unique_units: 117,
            completed_count: 0,
            completion_percentage: 0,
            completed: [],
            in_progress: [],
            pending: [],
            session_id: `session_${Date.now()}`,
            last_commit: null,
            seed_file: 'projects/north_africa_seed_units_COMPLETE.json'
        };

        newState.completed = scannedIds;
        newState.last_updated = new Date().toISOString();

        await fs.writeFile(WORKFLOW_STATE_PATH, JSON.stringify(newState, null, 2));

        return {
            synced: true,
            oldCount: stateIds.length,
            newCount: scannedIds.length,
            state: newState
        };
    }

    return {
        synced: false,
        state: currentState
    };
}

async function queryMemoryMCP() {
    console.log('🧠 Querying project knowledge...');

    try {
        const knowledge = await queryProjectKnowledge();

        if (knowledge.available) {
            console.log('   ✅ Memory MCP available');
        } else {
            console.log('   💾 Using local cache (Memory MCP not available)');
        }

        if (knowledge.patterns.length === 0 && knowledge.decisions.length === 0) {
            console.log('   📝 Loading default knowledge base\n');
            return {
                available: knowledge.available,
                patterns: [
                    '80% of units have estimated battalion TO&E (acceptable)',
                    '100% missing WITW IDs (one-time batch fix needed)',
                    '93% have estimated supply status (reasonable from theater data)'
                ],
                decisions: [
                    'Use 2-3 agents max for stability (4-6 caused crashes)',
                    '75%+ confidence threshold for division-level units',
                    '3-3-3 rule: 3 units/batch, 3 batches/session, 3 hour blocks'
                ]
            };
        }

        console.log(`   📊 Loaded ${knowledge.patterns.length} patterns, ${knowledge.decisions.length} decisions\n`);
        return knowledge;
    } catch (error) {
        console.log('   ⚠️  Could not query knowledge:', error.message, '\n');
        return { available: false, patterns: [], decisions: [] };
    }
}

async function getSeedUnits() {
    try {
        const seedPath = path.join(PROJECT_ROOT, 'projects/north_africa_seed_units_COMPLETE.json');
        const data = await fs.readFile(seedPath, 'utf-8');
        const seeds = JSON.parse(data);

        const units = [];

        for (const [key, value] of Object.entries(seeds)) {
            if (key.endsWith('_units') && Array.isArray(value)) {
                for (const unit of value) {
                    if (!unit.quarters || !Array.isArray(unit.quarters)) {
                        console.warn(`⚠️  Skipping unit without quarters: ${unit.designation || 'unknown'}`);
                        continue;
                    }

                    for (const quarter of unit.quarters) {
                        const nation = naming.NATION_MAP[key] || key.replace('_units', '');
                        const unitId = naming.generateFilename(nation, quarter, unit.designation).replace('_toe.json', '');
                        units.push({
                            id: unitId,
                            nation: naming.normalizeNation(nation),
                            quarter: naming.normalizeQuarter(quarter),
                            designation: unit.designation,
                            type: unit.type || 'unknown'
                        });
                    }
                }
            }
        }

        return { units, seeds };
    } catch (error) {
        console.warn('⚠️  Could not load seed units:', error.message);
        return { units: [], seeds: {} };
    }
}

function isCompleted(nation, designation, quarter, aliases, completedSet) {
    // Use new matching library with alias support
    return matching.isUnitCompleted(nation, quarter, designation, aliases || [], completedSet);
}

function calculateAllQuartersProgress(seedUnits, completedSet) {
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
                if (isCompleted(nation, u.designation, quarter, u.aliases || [], completedSet)) {
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

    return quarterStats;
}

/**
 * Read next batch from WORK_QUEUE.md
 *
 * Replaces dynamic strategy selection with simple queue reading.
 * Takes next 3 unchecked units from the queue.
 */
async function getNextBatchFromQueue(batchSize = 3) {
    try {
        const queuePath = path.join(PROJECT_ROOT, 'WORK_QUEUE.md');
        const queueContent = await fs.readFile(queuePath, 'utf-8');

        // Parse the "Next Up" section
        const nextUpMatch = queueContent.match(/## 🎯 Next Up \(Next Session\)\n\n([\s\S]*?)\n---/);

        if (!nextUpMatch) {
            console.warn('⚠️  Could not find "Next Up" section in WORK_QUEUE.md');
            return { batch: [], strategy: 'work_queue' };
        }

        const nextUpSection = nextUpMatch[1];

        // Parse unit lines (format: "1. **NATION** - quarter - designation _(echelon)_")
        const unitRegex = /\d+\.\s+\*\*([A-Z]+)\*\*\s+-\s+(\S+)\s+-\s+([^_]+)_\(([^)]+)\)_/g;
        const batch = [];
        let match;

        while ((match = unitRegex.exec(nextUpSection)) !== null && batch.length < batchSize) {
            const [, nation, quarter, designation, echelon] = match;
            batch.push({
                nation: nation.charAt(0).toUpperCase() + nation.slice(1).toLowerCase(),
                quarter: quarter,
                designation: designation.trim(),
                type: echelon.trim()
            });
        }

        return {
            batch,
            strategy: 'work_queue'
        };
    } catch (error) {
        console.warn('⚠️  Could not read WORK_QUEUE.md:', error.message);
        console.warn('   Falling back to empty batch');
        return { batch: [], strategy: 'work_queue' };
    }
}

/**
 * Initialize or reset session counter in workflow state
 */
async function initializeSessionCounter(state) {
    if (!state) return state;

    // Initialize session_count if it doesn't exist
    if (state.current_session_count === undefined) {
        state.current_session_count = 0;
    }

    return state;
}

function displayQuarterDashboard(quarterStats, totalCompleted) {
    const totalUnits = 420;
    const percentComplete = ((totalCompleted / totalUnits) * 100).toFixed(1);

    console.log('═'.repeat(80));
    console.log('  📊 QUARTER COMPLETION DASHBOARD');
    console.log('═'.repeat(80));
    console.log('');
    console.log(`📈 Seed Completion: ${totalCompleted}/${totalUnits} unit-quarters (${percentComplete}%)`);
    console.log('');

    const topCandidates = quarterStats
        .filter(q => q.percentage >= 40 && q.remaining <= 10 && q.remaining > 0)
        .slice(0, 3);

    if (topCandidates.length > 0) {
        console.log('🏆 **TOP CANDIDATES FOR COMPLETION:**\n');
        topCandidates.forEach((q, i) => {
            const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '  ';
            console.log(`   ${medal} ${q.quarter}: ${q.percentage}% Complete (${q.completed}/${q.total} units)`);
            console.log(`      Only ${q.remaining} units missing:`);
            q.missing.slice(0, 5).forEach((u, idx) => {
                const connector = idx === q.missing.length - 1 || idx === 4 ? '└─' : '├─';
                console.log(`      ${connector} ${u.nation} - ${u.designation}`);
            });
            if (q.missing.length > 5) {
                console.log(`      ... and ${q.missing.length - 5} more`);
            }
            console.log('');
        });
    }

    console.log('📋 **ALL QUARTERS RANKED:**\n');
    console.log('Quarter      | Progress         | Status');
    console.log('-------------|------------------|----------------------------------');
    quarterStats.forEach(q => {
        const status = q.percentage === 100 ? '✅ COMPLETE' :
                      q.percentage >= 80 ? `${q.remaining} missing ⭐ CLOSEST` :
                      q.percentage >= 50 ? `${q.remaining} missing` :
                      `${q.remaining} remaining`;
        const progressStr = `${q.completed}/${q.total} (${q.percentage}%)`;
        console.log(`${q.quarter.padEnd(12)} | ${progressStr.padEnd(16)} | ${status}`);
    });

    console.log('');
    console.log('─'.repeat(80));
    console.log('');
}

function displaySessionPrompt(state, memory, batchResult) {
    console.log('═'.repeat(80));
    console.log('  SESSION START - NORTH AFRICA TO&E BUILDER');
    console.log('═'.repeat(80));
    console.log('');

    if (state) {
        const completedCount = state.completed.length;
        const remaining = (state.total_unit_quarters || 420) - completedCount;
        const percentComplete = ((completedCount / (state.total_unit_quarters || 420)) * 100).toFixed(1);

        console.log('📊 **PROGRESS SUMMARY**\n');
        console.log(`   Total Unit-Quarters: ${state.total_unit_quarters || 420}`);
        console.log(`   Unique Units:        ${state.total_unique_units || 117}`);
        console.log(`   Completed:           ${completedCount} (${percentComplete}%)`);
        console.log(`   Remaining:           ${remaining}`);
        console.log(`   Last Updated:    ${new Date(state.last_updated).toLocaleString()}`);
        console.log(`   Last Commit:     ${state.last_commit || 'N/A'}`);
        console.log('');

        if (completedCount > 0) {
            console.log('🎯 **RECENT COMPLETIONS** (last 5)\n');
            state.completed.slice(-5).forEach(u => {
                console.log(`   ✅ ${u}`);
            });
            console.log('');
        }
    }

    if (memory.patterns.length > 0) {
        console.log('🧠 **KNOWN PATTERNS** (from Memory MCP)\n');
        memory.patterns.forEach(p => {
            console.log(`   • ${p}`);
        });
        console.log('');
    }

    if (memory.decisions.length > 0) {
        console.log('⚙️  **WORKFLOW DECISIONS**\n');
        memory.decisions.forEach(d => {
            console.log(`   • ${d}`);
        });
        console.log('');
    }

    // Show work queue session progress
    const sessionCount = state ? (state.current_session_count || 0) : 0;
    const canContinue = sessionCount < 12;

    console.log(`📋 **WORK QUEUE STATUS**`);
    console.log(`   Session Progress: ${sessionCount}/12 units this session`);
    console.log(`   Units Remaining: ${canContinue ? 'Ready for next batch' : '⚠️  Session limit reached (12 units)'}`);
    console.log('');

    if (batchResult.batch.length > 0) {
        console.log('🚀 **NEXT BATCH** (3 units from WORK_QUEUE.md)\n');
        batchResult.batch.forEach((unit, i) => {
            console.log(`   ${i + 1}. ${unit.nation.toUpperCase()} - ${unit.designation} (${unit.quarter})`);
        });
        console.log('');
    }

    console.log('═'.repeat(80));
    console.log('');
    console.log('📢 **COPY THE MESSAGE BELOW AND PASTE INTO CLAUDE CODE CHAT**');
    console.log('═'.repeat(80));
    console.log('');
    console.log('─'.repeat(80));
    console.log('');

    const completedCount = state ? (state.completed.length) : 0;
    const totalUnits = 420;
    const percentComplete = ((completedCount / totalUnits) * 100).toFixed(1);

    console.log(`Start autonomous orchestration session.

**CURRENT PROGRESS:**
- Overall: ${completedCount}/${totalUnits} units (${percentComplete}%)
- Session: ${sessionCount}/12 units this session${!canContinue ? ' ⚠️  LIMIT REACHED' : ''}
- Last scan: ${new Date().toLocaleString()}

**WORK QUEUE (Chronological + Echelon Order):**
- Processing units from WORK_QUEUE.md in order
- Divisions before corps before armies (bottom-up aggregation)
- Auto-marks complete on checkpoint

**NEXT BATCH (3 units):**
${batchResult.batch.length > 0 ? batchResult.batch.map((u, i) => `${i + 1}. ${u.nation} - ${u.designation} (${u.quarter})`).join('\n') : '✅ No units remaining!'}

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

**OUTPUT PATH (Architecture v4.0 - Canonical Locations):**
✅ Units: data/output/units/
✅ Chapters: data/output/chapters/

⚠️  **MANDATORY**: Save ALL files to CANONICAL locations:
   - Unit JSON: data/output/units/[unit_file].json
   - MDBook chapters: data/output/chapters/[chapter_file].md

   **NEVER** create session folders (data/output/autonomous_*/ or data/output/session_*/)

**STOP CONDITIONS:**
- Validation fails after 2 regeneration attempts
- Confidence score < 75% for any unit
- Critical gaps cannot be resolved (missing commander, no equipment data)
- Template violations detected in generated chapters
- Source documents unavailable for nation/quarter

**🤖 MULTI-AGENT ORCHESTRATION PROTOCOL**

⚠️ **CRITICAL**: You are the ORCHESTRATOR, not the extractor.

**Project Architecture** (agents/agent_catalog.json):
- **16 specialized agents** in 6 categories (document_parser, historical_research, org_hierarchy, toe_template, unit_instantiation, theater_allocator, division_cascader, equipment_reconciliation, bottom_up_aggregator, top3_calculator, schema_validator, historical_accuracy, seed_reconciliation_validator, book_chapter_generator, scenario_exporter, sql_populator)

**YOUR ROLE AS ORCHESTRATOR:**
1. 🚀 Launch 3 extraction agents IN PARALLEL using Task tool (one per unit)
2. 📦 Provide each agent with: unit name, quarter, nation, canonical output path
3. 🔧 Instruct agents to use MCP tools (mcp__filesystem__read_text_file, mcp__memory__create_entities, mcp__filesystem__write_file)
4. 📊 Use TodoWrite to track progress through all phases
5. 📝 Report results with PROOF of Task tool execution

**⚡ MANDATORY PARALLEL EXECUTION** (3x speed improvement):

YOU MUST launch all 3 agents in ONE message with 3 separate Task tool invocations.

**Each agent should:**
- Read sources using mcp__filesystem__read_text_file (Tessin, Army Lists from Resource Documents/)
- Follow 6-phase workflow: Source Extraction → Org Building → Equipment Distribution → Aggregation → Validation → Output
- Write to canonical location: data/output/units/[nation]_[quarter]_[unit]_toe.json
- Store findings in Memory MCP using mcp__memory__create_entities
- Generate MDBook chapter: data/output/chapters/chapter_[nation]_[quarter]_[unit].md
- Report: confidence score, sources used, MCP tool usage log

**After all 3 agents complete:**
- Run checkpoint: Bash('npm run checkpoint')
- Session end when done: Bash('npm run session:end')

**PROOF OF ORCHESTRATION REQUIRED:**
Report back with evidence of:
✅ 3 Task tool calls made (show agent launches)
✅ Execution mode: PARALLEL (all 3 launched simultaneously)
✅ MCP tool usage by sub-agents (filesystem reads, memory writes)
✅ Final outputs written to canonical locations

If you cannot launch sub-agents using Task tool, STOP and explain why.

Begin orchestration now - launch 3 Task agents in parallel.`);

    console.log('');
    console.log('─'.repeat(80));
    console.log('');
    console.log('═'.repeat(80));
    console.log('');
    console.log('💡 **TIPS:**');
    console.log('   - Claude will process units autonomously using Task tool');
    console.log('   - Checkpoint runs automatically after batch (updates state)');
    console.log('   - Session:end syncs final state and creates summary');
    console.log('   - Work queue processes units in chronological + echelon order');
    console.log('');
    console.log('📚 **FULL GUIDELINES:** See "STRICT AUTONOMOUS MODE - Ken Prompt.md"');
    console.log('');
    console.log('═'.repeat(80));
    console.log('');

    console.log('💡 **TIP:** Run `npm run session:end` when finished to save progress\n');
}

async function main() {
    console.log('');

    // Read workflow state
    let state = await readWorkflowState();

    // Scan actual files and sync state if needed
    console.log('🔍 Scanning for completed units...');
    const scannedUnits = await getCompletedUnits();
    const syncResult = await syncWorkflowState(scannedUnits, state);

    if (syncResult.synced) {
        console.log(`   ⚠️  State was out of sync: ${syncResult.oldCount} → ${syncResult.newCount} units`);
        console.log(`   ✅ WORKFLOW_STATE.json updated\n`);
        state = syncResult.state;
    } else {
        console.log(`   ✅ State in sync: ${scannedUnits.length} units\n`);
    }

    // Initialize session counter
    state = await initializeSessionCounter(state);

    // Check session limit
    const sessionCount = state.current_session_count || 0;
    if (sessionCount >= 12) {
        console.log('⚠️  **SESSION LIMIT REACHED**\n');
        console.log('   You have processed 12 units this session (4 batches of 3).');
        console.log('   This is the recommended limit to prevent AI drift/hallucination.\n');
        console.log('   To continue:');
        console.log('   1. Run: npm run checkpoint (to save current progress)');
        console.log('   2. Run: npm run session:end (to reset session counter)');
        console.log('   3. Start a new session: npm run session:start\n');
        return;
    }

    // Query Memory MCP
    const memory = await queryMemoryMCP();

    // Get all seed units (still needed for quarter dashboard)
    const { seeds: seedUnits } = await getSeedUnits();

    // Calculate quarter stats for dashboard display
    const completed = state ? state.completed : [];
    const completedSet = new Set(completed);
    const quarterStats = calculateAllQuartersProgress(seedUnits, completedSet);

    // Sort by completion percentage descending
    quarterStats.sort((a, b) => b.percentage - a.percentage);

    // Display quarter dashboard
    const totalCompleted = state ? (completed.length) : 0;
    displayQuarterDashboard(quarterStats, totalCompleted);

    // Read next batch from WORK_QUEUE.md
    console.log('📋 Reading work queue...\n');
    const batchResult = await getNextBatchFromQueue();

    // Display session prompt
    displaySessionPrompt(state, memory, batchResult);

    // Write session start marker
    const sessionLog = path.join(PROJECT_ROOT, 'SESSION_ACTIVE.txt');
    await fs.writeFile(sessionLog, `Session started: ${new Date().toISOString()}\nStrategy: work_queue\nSession count: ${sessionCount}/12\n`);
}

// Run
main().catch(error => {
    console.error('❌ Session start failed:', error.message);
    process.exit(1);
});
