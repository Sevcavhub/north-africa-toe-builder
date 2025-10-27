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

// Parse command-line arguments for mode selection
function parseArgs() {
    const args = process.argv.slice(2);
    const isAirMode = args.includes('--air-forces');
    return {
        mode: isAirMode ? 'air' : 'ground',
        isAirMode
    };
}

// Mode-specific configuration
function getModeConfig(mode) {
    if (mode === 'air') {
        return {
            workQueueFile: 'WORK_QUEUE_AIR.md',
            seedFile: 'projects/north_africa_air_units_seed_COMPLETE.json',
            totalUnits: 761,
            totalUniqueUnits: 142,
            schemaFile: 'schemas/air_force_schema.json',
            modeLabel: 'AIR FORCES',
            unitsLabel: 'squadrons/gruppi/gruppen'
        };
    } else {
        return {
            workQueueFile: 'WORK_QUEUE.md',
            seedFile: 'projects/north_africa_seed_units_COMPLETE.json',
            totalUnits: 420,
            totalUniqueUnits: 117,
            schemaFile: 'schemas/unified_toe_schema.json',
            modeLabel: 'GROUND FORCES',
            unitsLabel: 'divisions/corps/armies'
        };
    }
}

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

async function syncWorkflowState(scannedUnits, currentState, config) {
    const scannedIds = scannedUnits.map(u => `${u.nation}_${u.quarter}_${u.unit}`);
    const stateIds = currentState ? currentState.completed : [];

    if (scannedIds.length !== stateIds.length) {
        const newState = currentState || {
            last_updated: new Date().toISOString(),
            total_unit_quarters: config.totalUnits,
            total_unique_units: config.totalUniqueUnits,
            completed_count: 0,
            completion_percentage: 0,
            completed: [],
            in_progress: [],
            pending: [],
            session_id: `session_${Date.now()}`,
            last_commit: null,
            seed_file: config.seedFile
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
 * Read next batch from work queue file
 *
 * Replaces dynamic strategy selection with simple queue reading.
 * Takes next 3 unchecked units from the queue.
 *
 * @param {string} queueFile - Work queue filename (WORK_QUEUE.md or WORK_QUEUE_AIR.md)
 * @param {number} batchSize - Number of units to fetch (default: 3)
 */
async function getNextBatchFromQueue(queueFile = 'WORK_QUEUE.md', batchSize = 3) {
    try {
        const queuePath = path.join(PROJECT_ROOT, queueFile);
        const queueContent = await fs.readFile(queuePath, 'utf-8');

        // Parse the "Next Up" section
        const nextUpMatch = queueContent.match(/## 🎯 Next Up \(Next Session\)\n\n([\s\S]*?)\n---/);

        if (!nextUpMatch) {
            console.warn(`⚠️  Could not find "Next Up" section in ${queueFile}`);
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
        console.warn(`⚠️  Could not read ${queueFile}:`, error.message);
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

function displaySessionPrompt(state, memory, batchResult, config) {
    console.log('═'.repeat(80));
    console.log(`  SESSION START - ${config.modeLabel}`);
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
    const totalUnits = config.totalUnits;
    const percentComplete = ((completedCount / totalUnits) * 100).toFixed(1);

    // Mode-specific instructions
    const isAirMode = config.modeLabel === 'AIR FORCES';
    const workQueueDesc = isAirMode
        ? 'Staffel/Squadron before Gruppe/Gruppo before Groups/Geschwader (bottom-up)'
        : 'Divisions before corps before armies (bottom-up aggregation)';

    console.log(`Start autonomous orchestration session${isAirMode ? ' for AIR FORCES extraction' : ''}.

**CURRENT PROGRESS:**
- Overall: ${completedCount}/${totalUnits} units (${percentComplete}%)
- Mode: ${config.modeLabel}
- Session: ${sessionCount}/12 units this session${!canContinue ? ' ⚠️  LIMIT REACHED' : ''}
- Last scan: ${new Date().toLocaleString()}

**WORK QUEUE (Echelon-First Order):**
- Processing ${config.unitsLabel} from ${config.workQueueFile} in order
- ${workQueueDesc}
- Auto-marks complete on checkpoint

**NEXT BATCH (3 units):**
${batchResult.batch.length > 0 ? batchResult.batch.map((u, i) => `${i + 1}. ${u.nation} - ${u.designation} (${u.quarter})`).join('\n') : '✅ No units remaining!'}

**SESSION PROTOCOL:**
✅ Session started (progress loaded above)
🔄 Process these 3 units in parallel (batch of 3)
💾 After batch complete: Bash('npm run checkpoint')
📊 Check validation: Review SESSION_CHECKPOINT.md for status
🏁 When done: Bash('npm run session:end')

${isAirMode ? `**AIR FORCE SCHEMA COMPLIANCE (${config.schemaFile}):**
- **CRITICAL**: Required fields: unit_designation, unit_type, nation, quarter, base, personnel, aircraft, metadata
- **AIRCRAFT VARIANTS MUST BE SPECIFIC**: ✅ "Bf 109E-7/Trop", ❌ "Bf 109"
- **NO GENERIC AIRCRAFT ENTRIES**: Every variant must have full designation
- **WITW Integration**: Include WITW IDs from _airgroup.csv database (4,097 air groups)
- Nation values lowercase: german, italian, british, american
- Aircraft totals MUST match: total = operational + damaged + reserve
- Variant counts MUST sum to total aircraft
- **Validation**: Use ${config.schemaFile} before saving

**AIR FORCE AGENT CATALOG (agents/air_forces_agent_catalog.json):**
- **6 specialized air agents**: air_document_parser, air_historical_research, air_org_hierarchy, air_operations_analyzer, air_json_generator, air_chapter_generator
- **Sources**: Shores' Air War series, WITW database (_airgroup.csv, _aircraft.csv), Asisbiz.com, squadron histories
- **Data Focus**: Aircraft variants, sorties, aerial victories, losses, base locations, operational radius

**OUTPUT PATH (Air Forces Canonical):**
✅ Air Units: data/output/air_units/
✅ Air Chapters: data/output/air_chapters/

⚠️  **MANDATORY**: Save ALL air force files to AIR CANONICAL locations:
   - Air Unit JSON: data/output/air_units/{nation}_{quarter}_{unit}_air_toe.json
   - MDBook chapters: data/output/air_chapters/chapter_air_{nation}_{quarter}_{unit}.md

**CRITICAL AIR FORCES RULES:**
- ✅ Seed authority: Only extract from north_africa_air_units_seed_COMPLETE.json
- ✅ Aircraft specificity: MUST use variant-level detail (Bf 109E-7/Trop, NOT Bf 109)
- ✅ WITW integration: Cross-reference with _airgroup.csv (4,097 air groups)
- ✅ Operational data: Extract sorties, claims, losses, mission types
- ✅ Base locations: Exact airfield names (Gazala, El Adem, LG 05, etc.)

**STOP CONDITIONS (Air Forces):**
- Aircraft variants are generic (not specific)
- WITW IDs missing when database available
- Critical gaps: commander unknown, no aircraft data, base location missing
` : `**UNIFIED SCHEMA COMPLIANCE (${config.schemaFile}):**
- **CRITICAL**: Use top-level fields (nation, quarter, organization_level)
- **NEVER** nest unit_identification, personnel_summary, equipment_summary
- Commander MUST be nested object: commander.name, commander.rank
- Nation values lowercase only: german, italian, british, american, french
- Tank totals MUST match: total = heavy + medium + light
- **Validation**: Run scripts/lib/validator.js before saving

**TEMPLATE COMPLIANCE (v2.0 - 16 Sections):**
- Section 3: Command (commander, HQ, staff) - REQUIRED
- Section 5: Artillery (summary + detail for EVERY variant)
- Section 6: Armored Cars (separate section with details, NOT in transport)
- Section 7: Transport (NO tanks/armored cars, all variants detailed)
- Section 12: Critical Equipment Shortages (Priority 1/2/3)
- Section 15: Data Quality & Known Gaps (honest assessment)
- **Confidence threshold**: ≥ 75%

**OUTPUT PATH (Architecture v4.0):**
✅ Units: data/output/units/
✅ Chapters: data/output/chapters/

⚠️  **MANDATORY**: Save ALL files to CANONICAL locations:
   - Unit JSON: data/output/units/[unit_file].json
   - MDBook chapters: data/output/chapters/[chapter_file].md

   **NEVER** create session folders (data/output/autonomous_*/ or data/output/session_*/)
`}
${isAirMode ? `
**STOP CONDITIONS (Air Forces):**
- Aircraft variants are generic (not specific)
- WITW IDs missing when database was checked
- Confidence score < 75%
- Critical gaps: commander unknown, no aircraft data, base location missing
- Validation fails after 2 attempts

**🤖 AIR FORCES ORCHESTRATION PROTOCOL**

⚠️ **CRITICAL**: You are the ORCHESTRATOR for AIR FORCES extraction.

**Project Architecture** (agents/air_forces_agent_catalog.json):
- **6 specialized air agents**: air_document_parser, air_historical_research, air_org_hierarchy, air_operations_analyzer, air_json_generator, air_chapter_generator

**YOUR ROLE AS ORCHESTRATOR:**
1. 🚀 Launch 3 air extraction agents IN PARALLEL using Task tool (one per squadron/gruppe)
2. 📦 Provide each agent with: squadron/gruppe name, quarter, nation, air canonical path
3. 🔧 Instruct agents to use MCP tools (read Shores Air War, WITW database, write outputs)
4. 📊 Use TodoWrite to track progress
5. 📝 Report results with PROOF of Task tool execution

**CRITICAL AIR FORCES RULES:**
- ✅ Seed authority: Only extract from north_africa_air_units_seed_COMPLETE.json
- ✅ Aircraft specificity: MUST use variant-level detail (Bf 109E-7/Trop, NOT Bf 109)
- ✅ WITW integration: Cross-reference _airgroup.csv (4,097 air groups) and _aircraft.csv
- ✅ Operational data: Extract sorties, claims, losses, mission types
- ✅ Air canonical paths: data/output/air_units/ and data/output/air_chapters/

**⚡ MANDATORY PARALLEL EXECUTION** (3 air units simultaneously):

YOU MUST launch all 3 agents in ONE message with 3 separate Task tool invocations.

**Each air agent should:**
- Read Shores Air War series using mcp__filesystem__read_text_file
- Cross-reference WITW _airgroup.csv and _aircraft.csv databases
- Extract: unit designation, aircraft variants (SPECIFIC), base, personnel, operations
- **Aircraft Variant Resolution**: Convert generic names to specific variants
  - ✅ "Messerschmitt Bf 109E-7/Trop", "Hawker Hurricane Mk IIB", "Macchi MC.202 Folgore"
  - ❌ "Bf 109", "Hurricane", "MC.202"
- **Store in MCP Memory**: Squadron operations, aircraft transitions, ace pilots, combat records
- Write JSON: data/output/air_units/{nation}_{quarter}_{unit}_air_toe.json
- Write chapter: data/output/air_chapters/chapter_air_{nation}_{quarter}_{unit}.md
- Report: confidence, sources, WITW validation status, aircraft variant specificity

**After EACH batch of 3 air units:**
- Run checkpoint: Bash('npm run checkpoint')
  - Validates air units (JSON + chapter + air_force_schema.json compliance)
  - Checks aircraft variants are specific (NO generic entries)
  - Updates WORKFLOW_STATE.json with new count
  - Commits to git
  - Regenerates WORK_QUEUE_AIR.md
` : `
**STOP CONDITIONS (Ground Forces):**
- Validation fails after 2 regeneration attempts
- Confidence score < 75% for any unit
- Critical gaps: missing commander, no equipment data
- Template violations detected
- Source documents unavailable

**🤖 MULTI-AGENT ORCHESTRATION PROTOCOL**

⚠️ **CRITICAL**: You are the ORCHESTRATOR, not the extractor.

**Project Architecture** (agents/agent_catalog.json):
- **16 specialized agents** in 6 categories

**YOUR ROLE AS ORCHESTRATOR:**
1. 🚀 Launch 3 extraction agents IN PARALLEL using Task tool (one per unit)
2. 📦 Provide each agent with: unit name, quarter, nation, canonical output path
3. 🔧 Instruct agents to use MCP tools (mcp__filesystem__read_text_file, mcp__memory__create_entities)
4. 📊 Use TodoWrite to track progress
5. 📝 Report results with PROOF of Task tool execution

**CRITICAL RULES:**
- ✅ Seed authority: Only extract from north_africa_seed_units_COMPLETE.json
- ✅ Combat criteria: discovered_units require combat_evidence field
- ✅ Canonical paths: data/output/units/ and data/output/chapters/
- ✅ Validation: Unit complete = JSON + chapter + passes validation

**⚡ MANDATORY PARALLEL EXECUTION:**

YOU MUST launch all 3 agents in ONE message with 3 separate Task tool invocations.

**Each agent should:**
- Read sources using mcp__filesystem__read_text_file (Tessin, Army Lists)
- Follow 6-phase workflow: Source Extraction → Org Building → Equipment Distribution → Aggregation → Validation → Output
- Write to: data/output/units/[nation]_[quarter]_[unit]_toe.json
- **Store in MCP Memory**: organization structure, equipment patterns, command chain, tactical doctrine
- Generate chapter: data/output/chapters/chapter_[nation]_[quarter]_[unit].md
- Report: confidence score, sources used, MCP tool usage

**After EACH batch of 3 units:**
- Run checkpoint: Bash('npm run checkpoint')
  - Validates units (JSON + chapter + schema compliance)
  - Updates WORKFLOW_STATE.json
  - Commits to git
  - Regenerates WORK_QUEUE.md
`}

**After ALL batches complete (end of session):**
- Run session end: Bash('npm run session:end')
  - Runs final checkpoint
  - **Updates MCP Memory** with session patterns, statistics, and unit observations
  - Creates SESSION_SUMMARY.md with session report
  - Removes SESSION_ACTIVE.txt marker
  - Prepares for next session

⚠️ **CRITICAL**: You MUST run session:end when finished for the day - it stores knowledge in MCP memory for future sessions!

**PROOF OF ORCHESTRATION REQUIRED:**
Report back with evidence of:
✅ 3 Task tool calls made (show ${isAirMode ? 'squadron/gruppe' : 'unit'} extractions)
✅ Execution mode: PARALLEL (all 3 launched simultaneously)
${isAirMode ? '✅ Aircraft variants SPECIFIC (no generic entries)\n✅ WITW database integration (show cross-reference)' : '✅ MCP tool usage by sub-agents (filesystem reads, memory writes)'}
✅ Final outputs written to ${isAirMode ? 'air canonical' : 'canonical'} locations

If you cannot launch sub-agents using Task tool, STOP and explain why.

Begin ${isAirMode ? 'AIR FORCES' : ''} orchestration now - launch 3 Task agents in parallel.`);

    console.log('');
    console.log('─'.repeat(80));
    console.log('');
    console.log('═'.repeat(80));
    console.log('');
    console.log('💡 **TIPS:**');
    console.log(`   - Claude will process ${config.unitsLabel} autonomously using Task tool`);
    console.log('   - Checkpoint runs automatically after batch (updates state)');
    console.log('   - Session:end syncs final state and creates summary');
    console.log(`   - Work queue processes ${config.unitsLabel} in echelon-first order`);
    console.log('');
    console.log('📚 **FULL GUIDELINES:** See "START_HERE_NEW_SESSION.md" → Session Management Protocol section');
    console.log('');
    console.log('═'.repeat(80));
    console.log('');

    console.log('💡 **TIP:** Run `npm run session:end` when finished to save progress\n');
}

async function main() {
    console.log('');

    // Parse command-line arguments and get mode-specific configuration
    const { mode } = parseArgs();
    const config = getModeConfig(mode);

    console.log(`🚀 **SESSION START - ${config.modeLabel}**\n`);
    console.log(`   Mode: ${config.modeLabel}`);
    console.log(`   Work Queue: ${config.workQueueFile}`);
    console.log(`   Seed File: ${config.seedFile}`);
    console.log(`   Total Units: ${config.totalUnits} unit-quarters\n`);

    // Read workflow state
    let state = await readWorkflowState();

    // Scan actual files and sync state if needed
    console.log('🔍 Scanning for completed units...');
    const scannedUnits = await getCompletedUnits();
    const syncResult = await syncWorkflowState(scannedUnits, state, config);

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

    // Read next batch from work queue
    console.log('📋 Reading work queue...\n');
    const batchResult = await getNextBatchFromQueue(config.workQueueFile);

    // Display session prompt
    displaySessionPrompt(state, memory, batchResult, config);

    // Write session start marker
    const sessionLog = path.join(PROJECT_ROOT, 'SESSION_ACTIVE.txt');
    await fs.writeFile(sessionLog, `Session started: ${new Date().toISOString()}\nMode: ${config.modeLabel}\nStrategy: work_queue\nSession count: ${sessionCount}/12\n`);
}

// Run
main().catch(error => {
    console.error('❌ Session start failed:', error.message);
    process.exit(1);
});
