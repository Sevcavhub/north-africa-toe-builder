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
                            designation: unit.designation
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

function isCompleted(nation, designation, quarter, completedSet) {
    const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');
    const normalizedDesignation = designation.toLowerCase()
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '');

    const canonicalId = `${nation}_${normalizedQuarter}_${normalizedDesignation}`;

    if (completedSet.has(canonicalId)) {
        return true;
    }

    const altCanonicalId = `${nation}_${quarter}_${normalizedDesignation}`;
    if (completedSet.has(altCanonicalId)) {
        return true;
    }

    const prefix = `${nation}_${normalizedQuarter}`;
    const prefixAlt = `${nation}_${quarter}`;
    // Keep ALL words including short ones like "XX", "XXI", "15", "5th"
    const designationWords = designation.toLowerCase().split(/\s+/).filter(w => w.length > 0);

    for (const completedId of completedSet) {
        if (completedId.startsWith(prefix) || completedId.startsWith(prefixAlt)) {
            // Match key identifiers (numbers, roman numerals, division names)
            const match = designationWords.some(word => {
                // Keep full word for short identifiers (XX, XXI, 15, etc.)
                const searchTerm = word.length <= 3 ? word : word.substring(0, 4);
                return completedId.includes(searchTerm);
            });
            if (match && designationWords.length > 0) {
                return true;
            }
        }
    }

    return false;
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
                if (isCompleted(nation, u.designation, quarter, completedSet)) {
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

function getNextBatchChronological(allUnits, completed, batchSize = 3) {
    const pending = allUnits.filter(u => !completed.includes(u.id));

    const byQuarter = {};
    for (const unit of pending) {
        if (!byQuarter[unit.quarter]) {
            byQuarter[unit.quarter] = [];
        }
        byQuarter[unit.quarter].push(unit);
    }

    const quarters = Object.keys(byQuarter).sort();
    if (quarters.length === 0) return { batch: [], quarter: null, strategy: 'chronological' };

    const selectedQuarter = quarters[0];
    return {
        batch: byQuarter[selectedQuarter].slice(0, batchSize),
        quarter: selectedQuarter,
        strategy: 'chronological'
    };
}

function getNextBatchQuarterCompletion(quarterStats, seedUnits, completedSet, batchSize = 3) {
    // Sort by completion percentage descending, then by remaining ascending
    const sorted = [...quarterStats]
        .filter(q => q.remaining > 0)
        .sort((a, b) => {
            if (b.percentage !== a.percentage) {
                return b.percentage - a.percentage;
            }
            return a.remaining - b.remaining;
        });

    if (sorted.length === 0) return { batch: [], quarter: null, strategy: 'quarter_completion' };

    const targetQuarter = sorted[0].quarter;
    const batch = getNextBatchForQuarter(targetQuarter, seedUnits, completedSet, batchSize);

    return {
        batch,
        quarter: targetQuarter,
        strategy: 'quarter_completion'
    };
}

function getNextBatchForQuarter(quarter, seedUnits, completedSet, batchSize = 3) {
    const needed = [];
    const nations = naming.NATION_MAP;

    for (const [key, nation] of Object.entries(nations)) {
        const units = seedUnits[key] || [];
        const quarterUnits = units.filter(u => u.quarters && u.quarters.includes(quarter));

        quarterUnits.forEach(u => {
            if (!isCompleted(nation, u.designation, quarter, completedSet)) {
                needed.push({
                    nation: nation.charAt(0).toUpperCase() + nation.slice(1),
                    designation: u.designation,
                    quarter: quarter
                });
            }
        });
    }

    return needed.slice(0, batchSize);
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

function displaySessionPrompt(state, memory, batchResult, quarterStats) {
    console.log('═'.repeat(80));
    console.log('  SESSION START - NORTH AFRICA TO&E BUILDER');
    console.log('═'.repeat(80));
    console.log('');

    if (state) {
        const completedCount = state.completed_count || state.completed.length;
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

    const strategyName = batchResult.strategy === 'chronological' ? 'CHRONOLOGICAL ORDER' : 'QUARTER COMPLETION';
    const targetQuarter = batchResult.quarter;
    const quarterProgress = quarterStats.find(q => q.quarter === targetQuarter);

    console.log(`🎯 **STRATEGY: ${strategyName}**`);
    if (targetQuarter) {
        console.log(`   Target Quarter: ${targetQuarter}`);
        if (quarterProgress) {
            console.log(`   Progress: ${quarterProgress.completed}/${quarterProgress.total} (${quarterProgress.percentage}%)`);
        }
    }
    console.log('');

    if (batchResult.batch.length > 0) {
        console.log('🚀 **NEXT BATCH** (3 units)\n');
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

    const completedCount = state ? (state.completed_count || state.completed.length) : 0;
    const totalUnits = 420;
    const percentComplete = ((completedCount / totalUnits) * 100).toFixed(1);

    console.log(`Start autonomous orchestration session.

**CURRENT PROGRESS:**
- Overall: ${completedCount}/${totalUnits} units (${percentComplete}%)
- Last scan: ${new Date().toLocaleString()}

**STRATEGY: ${strategyName}**${targetQuarter ? `
Target Quarter: ${targetQuarter}` : ''}${quarterProgress ? `
Progress: ${quarterProgress.completed}/${quarterProgress.total} (${quarterProgress.percentage}%)` : ''}

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

**GENERAL AGENT WORKFLOW:**
1. ✅ CONFIRM these units with user (or allow adjustments)
2. ✅ ONLY AFTER confirmation → Launch Task tool with autonomous orchestrator
3. ✅ Specialized agents do ALL extraction, validation, chapter generation
4. ❌ DO NOT perform extraction yourself as general agent

**When user confirms, launch autonomous orchestrator with:**
- Task tool (subagent_type='general-purpose')
- Prompt: "Run autonomous orchestration for these 3 units using specialized sub-agents"
- Extended thinking for complex source analysis
- TodoWrite to track progress
- Automatic checkpoint after batch completion

📋 **USER**: Review the 3 units above. Reply with:
   • "Proceed" → Start autonomous orchestration for these units
   • "Change to [quarter/strategy]" → Adjust selection first
   • "Use [specific units]" → Custom unit list`);

    console.log('');
    console.log('─'.repeat(80));
    console.log('');
    console.log('═'.repeat(80));
    console.log('');
    console.log('💡 **TIPS:**');
    console.log('   - Claude will process units autonomously using Task tool');
    console.log('   - Checkpoint runs automatically after batch (updates state)');
    console.log('   - Session:end syncs final state and creates summary');
    if (targetQuarter && quarterProgress) {
        console.log(`   - Once ${targetQuarter} complete, run QA agent for quality review`);
    }
    console.log('');
    console.log('📚 **FULL GUIDELINES:** See "STRICT AUTONOMOUS MODE - Ken Prompt.md"');
    console.log('');
    console.log('═'.repeat(80));
    console.log('');

    console.log('💡 **TIP:** Run `npm run session:end` when finished to save progress\n');
}

async function main() {
    console.log('');

    // Get strategy from CLI arg
    const strategyArg = process.argv[2];

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

    // Query Memory MCP
    const memory = await queryMemoryMCP();

    // Get all seed units
    const { units: allUnits, seeds: seedUnits } = await getSeedUnits();

    // Calculate quarter stats
    const completed = state ? state.completed : [];
    const completedSet = new Set(completed);
    const quarterStats = calculateAllQuartersProgress(seedUnits, completedSet);

    // Sort by completion percentage descending
    quarterStats.sort((a, b) => b.percentage - a.percentage);

    // Display quarter dashboard
    const totalCompleted = state ? (state.completed_count || completed.length) : 0;
    displayQuarterDashboard(quarterStats, totalCompleted);

    // Determine strategy and get batch
    let batchResult;

    if (!strategyArg) {
        // Interactive: show both options
        console.log('🎯 **STRATEGY SELECTION**\n');
        console.log('Choose extraction strategy:\n');
        console.log('  1. CHRONOLOGICAL - Process earliest quarter first');
        console.log('     (Systematic, complete timeline coverage)\n');
        console.log('  2. QUARTER COMPLETION - Target highest completion % quarter');
        console.log('     (Quick wins, complete quarters faster)\n');
        console.log('  3. SPECIFIC QUARTER - Choose a specific quarter to target\n');
        console.log('Default: Type "1" for chronological, "2" for quarter completion, or quarter like "1941-Q2"');
        console.log('You can also run: npm run session:start chronological|quarter|1941-Q2\n');

        // For now, default to quarter completion (highest %)
        batchResult = getNextBatchQuarterCompletion(quarterStats, seedUnits, completedSet);
        console.log(`Using default strategy: QUARTER COMPLETION (${batchResult.quarter})\n`);
    } else if (strategyArg === 'chronological' || strategyArg === '1') {
        batchResult = getNextBatchChronological(allUnits, completed);
    } else if (strategyArg === 'quarter' || strategyArg === '2') {
        batchResult = getNextBatchQuarterCompletion(quarterStats, seedUnits, completedSet);
    } else {
        // Assume it's a specific quarter
        batchResult = {
            batch: getNextBatchForQuarter(strategyArg, seedUnits, completedSet),
            quarter: strategyArg,
            strategy: 'specific_quarter'
        };
    }

    // Display session prompt
    displaySessionPrompt(state, memory, batchResult, quarterStats);

    // Write session start marker
    const sessionLog = path.join(PROJECT_ROOT, 'SESSION_ACTIVE.txt');
    await fs.writeFile(sessionLog, `Session started: ${new Date().toISOString()}\nStrategy: ${batchResult.strategy}\nTarget: ${batchResult.quarter}\n`);
}

// Run
main().catch(error => {
    console.error('❌ Session start failed:', error.message);
    process.exit(1);
});
