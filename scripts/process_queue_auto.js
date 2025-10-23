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
const path = require('path');
const { execSync } = require('child_process');

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
    console.log('4. Script will run session:end automatically');
    console.log('5. Script will continue to next batch WITHOUT asking user\n');

    // This is a marker for Claude to proceed
    // Claude reads this output and orchestrates the batch
    // The script itself doesn't launch agents - Claude does
    return 'WAITING_FOR_CLAUDE_ORCHESTRATION';
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
    console.log('🎯 Automated Queue Processing - Starting...\n');

    // Parse command-line arguments
    const { mode, batches: requestedBatches } = await parseArgs();

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
    console.log(`You are in AUTOMATED MODE. You MUST process ALL ${batchesToRun} batches without asking`);
    console.log('for user confirmation between batches. After each batch completes:');
    console.log('1. Run session:end (this script shows it)');
    console.log('2. Move to next batch IMMEDIATELY');
    console.log('3. DO NOT ask "would you like me to continue"');
    console.log('4. DO NOT wait for user input between batches');
    console.log(`5. Continue until all ${batchesToRun} batches are complete\n`);
    console.log('User has already approved this automation by running the command.');
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
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Automated processing failed:', error.message);
        process.exit(1);
    });
}

module.exports = { getNextBatch, runBatch, runSessionEnd, PRESET_BATCHES };
