#!/usr/bin/env node

/**
 * Automated Queue Processing - Process units without manual confirmation
 *
 * Runs autonomous extraction in batches with automatic session:end after each batch.
 *
 * Usage:
 *   node scripts/process_queue_auto.js               # Interactive mode (asks for batch count)
 *   node scripts/process_queue_auto.js --batches 5   # Process 5 batches (15 units)
 *   node scripts/process_queue_auto.js --continuous  # Process until queue empty
 *   node scripts/process_queue_auto.js --quick       # Quick run: 1 batch (3 units)
 *   node scripts/process_queue_auto.js --standard    # Standard run: 3 batches (9 units)
 *   node scripts/process_queue_auto.js --extended    # Extended run: 5 batches (15 units)
 *   node scripts/process_queue_auto.js --marathon    # Marathon run: 10 batches (30 units)
 *
 * Features:
 * - Reads next 3 units from WORK_QUEUE.md
 * - Launches autonomous orchestration automatically
 * - Runs session:end after EACH batch (updates MCP memory + docs)
 * - Crash-resistant: MCP memory updated after every batch
 * - No manual "proceed" confirmation needed
 */

const fs = require('fs').promises;
const fssync = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const paths = require('./lib/canonical_paths');
const naming = require('./lib/naming_standard');

const PROJECT_ROOT = path.join(__dirname, '..');
const WORK_QUEUE_PATH = path.join(PROJECT_ROOT, 'WORK_QUEUE.md');
const WORKFLOW_STATE_PATH = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');

// Pre-configured batch sizes
const PRESET_BATCHES = {
    quick: 1,      // 3 units (~20-30 min)
    standard: 3,   // 9 units (~60-90 min)
    extended: 5,   // 15 units (~100-150 min)
    marathon: 10   // 30 units (~200-300 min)
};

async function parseArgs() {
    const args = process.argv.slice(2);

    // Check for preset modes
    if (args.includes('--quick')) return { mode: 'preset', batches: PRESET_BATCHES.quick };
    if (args.includes('--standard')) return { mode: 'preset', batches: PRESET_BATCHES.standard };
    if (args.includes('--extended')) return { mode: 'preset', batches: PRESET_BATCHES.extended };
    if (args.includes('--marathon')) return { mode: 'preset', batches: PRESET_BATCHES.marathon };
    if (args.includes('--continuous')) return { mode: 'continuous', batches: Infinity };

    // Check for --batches N parameter
    const batchIndex = args.indexOf('--batches');
    if (batchIndex !== -1 && args[batchIndex + 1]) {
        const batches = parseInt(args[batchIndex + 1], 10);
        if (isNaN(batches) || batches < 1) {
            console.error('❌ --batches must be a positive integer');
            process.exit(1);
        }
        return { mode: 'custom', batches };
    }

    // Interactive mode
    return { mode: 'interactive', batches: null };
}

async function promptForBatchCount() {
    console.log('\n🎯 Automated Queue Processing\n');
    console.log('Pre-configured options:');
    console.log('  1. Quick      - 1 batch  (3 units,  ~20-30 min)');
    console.log('  2. Standard   - 3 batches (9 units,  ~60-90 min)');
    console.log('  3. Extended   - 5 batches (15 units, ~100-150 min)');
    console.log('  4. Marathon   - 10 batches (30 units, ~200-300 min)');
    console.log('  5. Continuous - Until queue empty');
    console.log('  6. Custom     - Specify batch count\n');

    // For now, return standard (would need readline for true interactive)
    // This will be enhanced when called from session:start
    return PRESET_BATCHES.standard;
}

async function getNextBatch() {
    try {
        const queueContent = await fs.readFile(WORK_QUEUE_PATH, 'utf-8');

        // Parse the "Next Up" section
        const nextUpMatch = queueContent.match(/## 🎯 Next Up \(Next Session\)\n\n([\s\S]*?)\n---/);

        if (!nextUpMatch) {
            console.warn('⚠️  Could not find "Next Up" section in WORK_QUEUE.md');
            return [];
        }

        const nextUpSection = nextUpMatch[1];

        // Parse unit lines (format: "1. **NATION** - quarter - designation _(echelon)_")
        const unitRegex = /\d+\.\s+\*\*([A-Z]+)\*\*\s+-\s+(\S+)\s+-\s+([^_]+)_\(([^)]+)\)_/g;
        const batch = [];
        let match;

        while ((match = unitRegex.exec(nextUpSection)) !== null && batch.length < 3) {
            const [, nation, quarter, designation, echelon] = match;
            batch.push({
                nation: nation.charAt(0).toUpperCase() + nation.slice(1).toLowerCase(),
                quarter: quarter,
                designation: designation.trim(),
                type: echelon.trim()
            });
        }

        return batch;
    } catch (error) {
        console.error('❌ Failed to read work queue:', error.message);
        return [];
    }
}

async function readWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        return null;
    }
}

async function verifyBatchCompletion(units) {
    /**
     * Verify that all units in the batch were actually completed.
     * Returns an object with completion status and details.
     */
    const results = {
        allComplete: true,
        completed: [],
        incomplete: [],
        details: []
    };

    for (const unit of units) {
        // Use naming standard module to normalize all components
        const nation = naming.normalizeNation(unit.nation);
        const quarter = naming.normalizeQuarter(unit.quarter);
        const designation = naming.normalizeDesignation(unit.designation);

        // Generate expected filenames using naming standard
        const jsonFilename = `${nation}_${quarter}_${designation}_toe.json`;
        const chapterFilename = `chapter_${nation}_${quarter}_${designation}.md`;

        const jsonPath = path.join(paths.UNITS_DIR, jsonFilename);
        const chapterPath = path.join(paths.CHAPTERS_DIR, chapterFilename);

        const hasJson = fssync.existsSync(jsonPath);
        const hasChapter = fssync.existsSync(chapterPath);
        const isComplete = hasJson && hasChapter;

        const unitStatus = {
            unit: `${nation.toUpperCase()} - ${quarter} - ${designation}`,
            hasJson,
            hasChapter,
            isComplete,
            jsonPath,
            chapterPath
        };

        if (isComplete) {
            results.completed.push(unitStatus);
        } else {
            results.incomplete.push(unitStatus);
            results.allComplete = false;
        }

        results.details.push(unitStatus);
    }

    return results;
}

async function verifyNoWikipediaSources(completedUnits) {
    /**
     * Verify that completed units do NOT contain Wikipedia sources.
     * Returns object with validation status and violations.
     */
    const WIKIPEDIA_PATTERNS = [
        /wikipedia\.org/i,
        /wikipedia\.com/i,
        /de\.wikipedia/i,
        /en\.wikipedia/i,
        /it\.wikipedia/i,
        /fr\.wikipedia/i,
        /wikia\.com/i,
        /fandom\.com/i,
        /\bwiki\b.*source/i,
        /Wikipedia:/i,
        /Wikipedia -/i,
        /Wikipedia\s+\(/i
    ];

    const results = {
        allClean: true,
        violations: [],
        clean: []
    };

    for (const unitStatus of completedUnits) {
        try {
            const content = await fs.readFile(unitStatus.jsonPath, 'utf-8');
            const data = JSON.parse(content);

            const violations = [];

            // Check sources array
            if (data.sources && Array.isArray(data.sources)) {
                for (let i = 0; i < data.sources.length; i++) {
                    const source = data.sources[i];
                    const sourceStr = typeof source === 'string' ? source : JSON.stringify(source);

                    for (const pattern of WIKIPEDIA_PATTERNS) {
                        if (pattern.test(sourceStr)) {
                            violations.push({
                                location: `sources[${i}]`,
                                source: sourceStr.substring(0, 100)
                            });
                            break;
                        }
                    }
                }
            }

            // Recursively check all string fields
            function checkObject(obj, pathParts = []) {
                if (!obj || typeof obj !== 'object') return;

                for (const [key, value] of Object.entries(obj)) {
                    const currentPath = [...pathParts, key];

                    if (typeof value === 'string') {
                        // Skip if saying "no Wikipedia" or "non-Wikipedia"
                        const lowerValue = value.toLowerCase();
                        if (lowerValue.includes('no wikipedia') ||
                            lowerValue.includes('non-wikipedia') ||
                            lowerValue.includes('without wikipedia')) {
                            continue;
                        }

                        for (const pattern of WIKIPEDIA_PATTERNS) {
                            if (pattern.test(value)) {
                                violations.push({
                                    location: currentPath.join('.'),
                                    source: value.substring(0, 100)
                                });
                                break;
                            }
                        }
                    } else if (Array.isArray(value)) {
                        value.forEach((item, idx) => {
                            checkObject(item, [...currentPath, idx]);
                        });
                    } else if (typeof value === 'object') {
                        checkObject(value, currentPath);
                    }
                }
            }

            const remainingData = {...data};
            delete remainingData.sources;
            checkObject(remainingData);

            if (violations.length > 0) {
                results.violations.push({
                    unit: unitStatus.unit,
                    file: unitStatus.jsonPath,
                    violations: violations
                });
                results.allClean = false;
            } else {
                results.clean.push(unitStatus.unit);
            }
        } catch (error) {
            console.warn(`   ⚠️  Could not validate ${unitStatus.unit}:`, error.message);
        }
    }

    return results;
}

async function runBatch(batchNumber, units) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`📦 BATCH ${batchNumber} - Processing 3 units`);
    console.log(`${'='.repeat(60)}\n`);

    units.forEach((u, i) => {
        console.log(`   ${i + 1}. ${u.nation.toUpperCase()} - ${u.quarter} - ${u.designation} (${u.type})`);
    });

    console.log('\n⚠️  **CLAUDE: YOU MUST PROCESS THIS BATCH AUTOMATICALLY**');
    console.log('⚠️  DO NOT ASK FOR CONFIRMATION - AUTOMATED MODE IS ACTIVE\n');
    console.log('Instructions for Claude:');
    console.log('1. Launch 3 parallel Task tool agents (one per unit above)');
    console.log('2. Each agent extracts unit using autonomous orchestration');
    console.log('3. Wait for all 3 agents to complete');
    console.log('4. This script will verify completion and run session:end');
    console.log('5. Script will continue to next batch automatically\n');

    // Wait a moment for Claude to see the instructions
    // In practice, Claude should have already started processing when this is called
    console.log('⏳ Checking if batch work is complete...\n');

    // Verify that the work was actually done
    const verification = await verifyBatchCompletion(units);

    if (verification.allComplete) {
        console.log(`✅ All ${units.length} units completed and verified!\n`);
        verification.completed.forEach(u => {
            console.log(`   ✅ ${u.unit}`);
        });

        // CRITICAL: Verify no Wikipedia sources (FORBIDDEN per project requirements)
        console.log('\n🔍 Validating sources (Wikipedia check)...\n');
        const wikiCheck = await verifyNoWikipediaSources(verification.completed);

        if (!wikiCheck.allClean) {
            console.log('❌ WIKIPEDIA VIOLATION DETECTED - BATCH REJECTED\n');
            console.log('⚠️  Wikipedia sources are FORBIDDEN per project requirements.\n');
            console.log('Violations found in:');
            wikiCheck.violations.forEach(v => {
                console.log(`\n   ❌ ${v.unit}`);
                v.violations.forEach(viol => {
                    console.log(`      Location: ${viol.location}`);
                    console.log(`      Source: ${viol.source}...`);
                });
            });
            console.log('\n📋 REQUIRED ACTION:');
            console.log('   1. DELETE the units with Wikipedia sources');
            console.log('   2. RE-EXTRACT using Tier 1/2 sources ONLY');
            console.log('   3. Run this batch again\n');
            console.log('⚠️  STOPPING: Cannot proceed with Wikipedia violations.\n');
            return false;
        }

        console.log(`✅ All ${units.length} units are Wikipedia-free!\n`);
        return true;
    } else {
        console.log(`\n❌ BATCH INCOMPLETE - Work has not been done yet!\n`);
        console.log('Completed units:');
        verification.completed.forEach(u => {
            console.log(`   ✅ ${u.unit}`);
        });
        console.log('\nIncomplete units:');
        verification.incomplete.forEach(u => {
            console.log(`   ❌ ${u.unit} (JSON: ${u.hasJson}, Chapter: ${u.hasChapter})`);
        });
        console.log('\n⚠️  STOPPING: Claude must extract these units before continuing.');
        console.log('⚠️  This script cannot auto-loop without actual extraction work.');
        console.log('\n📋 WHAT TO DO:');
        console.log('   1. Claude: Read the batch units listed above');
        console.log('   2. Claude: Launch 3 parallel Task tool agents to extract them');
        console.log('   3. Claude: Wait for all agents to complete');
        console.log('   4. Claude: Run this script again to verify and continue\n');
        return false;
    }
}

async function runSessionEnd() {
    console.log('\n📍 Running session:end (updates MCP memory + docs)...\n');

    try {
        execSync('npm run session:end', {
            cwd: PROJECT_ROOT,
            stdio: 'inherit'
        });
        return true;
    } catch (error) {
        console.error('❌ session:end failed:', error.message);
        return false;
    }
}

async function main() {
    console.log('🎯 Automated Queue Processing\n');

    // Check if being run directly or through Claude
    const runningDirectly = process.stdout.isTTY && !process.env.CLAUDE_ORCHESTRATED;

    if (runningDirectly) {
        console.log('⚠️  WARNING: This command should be invoked through Claude Code, not run directly.\n');
        console.log('This script provides instructions for Claude to follow. It cannot launch');
        console.log('extraction agents by itself - only Claude can use the Task tool.\n');
        console.log('CORRECT USAGE:\n');
        console.log('  1. In a Claude Code session, say: "Run auto:standard"');
        console.log('  2. Claude will read this script and orchestrate the extraction');
        console.log('  3. Claude will launch 3 parallel Task tool agents per batch');
        console.log('  4. Claude will run session:end after each batch\n');
        console.log('INCORRECT USAGE:\n');
        console.log('  ❌ Running: npm run auto:standard (this is what you just did)');
        console.log('  ❌ Result: Script loops but no extraction happens\n');
        console.log('TO PROCEED:\n');
        console.log('  Tell Claude in your session: "Process the next 3 units from queue"');
        console.log('  Or say: "Run automated mode with 3 batches"\n');
        process.exit(0);
    }

    console.log('Starting...\n');

    // Parse command-line arguments
    const { mode, batches: requestedBatches } = await parseArgs();

    // Create CONTINUOUS_MODE_ACTIVE flag file for continuous mode
    if (mode === 'continuous') {
        const flagPath = path.join(PROJECT_ROOT, 'CONTINUOUS_MODE_ACTIVE.txt');
        const flagContent = `# CONTINUOUS MODE ACTIVE\n\nStarted: ${new Date().toISOString()}\n\n⚠️ CLAUDE: Continue processing until queue is empty. DO NOT STOP EARLY.\n`;
        await fs.writeFile(flagPath, flagContent, 'utf-8');
        console.log('📝 CONTINUOUS_MODE_ACTIVE.txt created - Claude MUST continue until queue empty\n');
    }

    let batchesToRun = requestedBatches;

    if (mode === 'interactive') {
        batchesToRun = await promptForBatchCount();
    }

    console.log(`\n📋 Mode: ${mode}`);
    console.log(`📊 Batches to process: ${batchesToRun === Infinity ? 'Continuous (until queue empty)' : batchesToRun}`);
    console.log(`📦 Units per batch: 3`);
    console.log(`📈 Total units: ${batchesToRun === Infinity ? 'Until queue empty' : batchesToRun * 3}\n`);

    console.log(`${'='.repeat(60)}`);
    console.log('⚠️  AUTOMATED MODE - NO USER CONFIRMATIONS REQUIRED');
    console.log(`${'='.repeat(60)}`);
    console.log('\n🤖 INSTRUCTIONS FOR CLAUDE:\n');

    if (batchesToRun === Infinity) {
        console.log('You are in CONTINUOUS MODE. You MUST process batches until the queue is empty,');
        console.log('without asking for user confirmation between batches.');
    } else {
        console.log(`You are in AUTOMATED MODE. You MUST process ALL ${batchesToRun} batches without asking`);
        console.log('for user confirmation between batches.');
    }

    console.log('\nAfter each batch completes:');
    console.log('1. Run session:end (this script shows it)');

    if (batchesToRun === Infinity) {
        console.log('2. **NO TOKEN MONITORING** - Continuous mode runs until queue empty');
        console.log('   - Compaction/crashes expected on long runs (overnight)');
        console.log('   - session:end saves work after each batch (crash-resistant)');
        console.log('   - User will run "npm run recover" in morning to check status');
    } else {
        console.log('2. **CHECK TOKEN USAGE** (see system warnings)');
        console.log('   - If > 160,000 tokens (80%): STOP and warn user about compaction');
        console.log('   - session:end has saved work, safe to continue in new thread');
        console.log('   - Tell user: "Context approaching limit, resume with same command"');
    }

    console.log('3. Move to next batch IMMEDIATELY');
    console.log('4. DO NOT ask "would you like me to continue"');
    console.log('5. DO NOT wait for user input between batches');

    if (batchesToRun === Infinity) {
        console.log('6. Continue until WORK_QUEUE.md is empty (no units left)\n');
        console.log('⚠️  CONTINUOUS MODE: Designed for overnight unattended runs');
        console.log('⚠️  Current remaining: Check WORK_QUEUE.md for count');
        console.log('⚠️  NO COMPACTION SAFETY: Will run until queue empty or crash');
        console.log('⚠️  If crash/compaction occurs: Use "npm run recover" to assess damage');
        console.log('⚠️  session:end after each batch = max 1-2 units lost per crash');
    } else {
        console.log(`6. Continue until all ${batchesToRun} batches are complete\n`);
        console.log(`📊 Estimated time: ~${batchesToRun * 20}-${batchesToRun * 30} minutes`);
        console.log(`⚠️  COMPACTION SAFETY: Will pause at 80% token usage if needed`);
    }

    console.log('\nUser has already approved this automation by running the command.');
    console.log('Your job is to execute all batches to completion.\n');

    // Read initial state
    const initialState = await readWorkflowState();
    const initialCount = initialState ? initialState.completed_count : 0;

    console.log(`✅ Current progress: ${initialCount}/${initialState ? initialState.total_unit_quarters : '???'} units\n`);
    console.log(`${'='.repeat(60)}\n`);

    let batchNumber = 1;
    let completedBatches = 0;
    let failedBatches = 0;

    while (completedBatches < batchesToRun) {
        // Get next batch from queue
        const nextBatch = await getNextBatch();

        if (nextBatch.length === 0) {
            console.log('\n✅ Queue is empty - no more units to process!');
            break;
        }

        if (nextBatch.length < 3) {
            console.log(`\n⚠️  Only ${nextBatch.length} units remaining in queue`);
        }

        // Run the batch
        const success = await runBatch(batchNumber, nextBatch);

        if (!success) {
            console.log(`\n❌ Batch ${batchNumber} failed - stopping processing`);
            failedBatches++;
            break;
        }

        // Run session:end after each batch
        const sessionEndSuccess = await runSessionEnd();

        if (!sessionEndSuccess) {
            console.log(`\n❌ session:end failed after batch ${batchNumber} - stopping processing`);
            failedBatches++;
            break;
        }

        completedBatches++;
        batchNumber++;

        console.log(`\n✅ Batch ${completedBatches} complete - MCP memory and docs updated!`);

        if (completedBatches < batchesToRun) {
            console.log(`\n⏭️  Proceeding to next batch...\n`);
        }
    }

    // Final summary
    const finalState = await readWorkflowState();
    const finalCount = finalState ? finalState.completed_count : 0;
    const unitsCompleted = finalCount - initialCount;

    console.log(`\n${'='.repeat(60)}`);
    console.log('📊 AUTOMATED PROCESSING COMPLETE');
    console.log(`${'='.repeat(60)}\n`);
    console.log(`✅ Batches completed: ${completedBatches}`);
    console.log(`❌ Batches failed: ${failedBatches}`);
    console.log(`📦 Units completed this run: ${unitsCompleted}`);
    console.log(`📈 Total progress: ${finalCount}/${finalState ? finalState.total_unit_quarters : '???'} (${finalState ? finalState.completion_percentage : '???'}%)\n`);

    if (completedBatches > 0) {
        console.log('🧠 MCP Memory: Updated after each batch');
        console.log('📄 Documentation: START_HERE and PROJECT_SCOPE synced\n');
    }

    // Remove continuous mode flag if queue is empty or processing complete
    if (mode === 'continuous') {
        const flagPath = path.join(PROJECT_ROOT, 'CONTINUOUS_MODE_ACTIVE.txt');
        try {
            await fs.unlink(flagPath);
            console.log('✅ CONTINUOUS_MODE_ACTIVE.txt removed - continuous mode complete\n');
        } catch (error) {
            // Ignore if file doesn't exist
        }
    }
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Automated processing failed:', error.message);
        process.exit(1);
    });
}

module.exports = { getNextBatch, runBatch, runSessionEnd, PRESET_BATCHES };
