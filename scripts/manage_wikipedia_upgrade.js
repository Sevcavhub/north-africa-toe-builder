#!/usr/bin/env node

/**
 * Wikipedia Source Upgrade Manager
 *
 * Helper script to track and manage Wikipedia source upgrade batches.
 *
 * Usage:
 *   npm run wikipedia:next       - Show next batch to process
 *   npm run wikipedia:validate   - Validate current batch after upgrade
 *   npm run wikipedia:status     - Show overall progress
 */

const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const QUEUE_FILE = path.join(PROJECT_ROOT, 'WIKIPEDIA_UPGRADE_QUEUE.md');
const UNITS_DIR = path.join(PROJECT_ROOT, 'data/output/units');
const WORKFLOW_STATE = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');

// Batch definitions (97 units, 33 batches)
const BATCHES = [
  ['british_1943q1_v_corps_toe.json', 'british_1943q2_v_corps_toe.json', 'british_1943q1_x_corps_toe.json'],
  ['french_1943q2_1st_moroccan_march_division_toe.json', 'british_1943q2_1st_armoured_division_toe.json', 'british_1943q2_10th_armoured_division_toe.json'],
  ['italian_1943q1_trento_division_toe.json', 'british_1943q2_2nd_new_zealand_division_toe.json', 'american_1943q2_2nd_armored_division_toe.json'],
  ['italian_1943q2_la_spezia_division_toe.json', 'french_1943q2_1re_division_fran_aise_libre_toe.json', 'british_1943q2_4th_infantry_division_toe.json'],
  ['british_1943q2_50th_infantry_division_toe.json', 'british_1943q2_46th_infantry_division_toe.json', 'american_1943q2_1st_infantry_division_toe.json'],
  ['american_1943q2_34th_infantry_division_toe.json', 'american_1943q2_1st_armored_division_toe.json', 'british_1943q1_1st_armoured_division_toe.json'],
  ['american_1943q1_2nd_armored_division_toe.json', 'italian_1943q1_giovani_fascisti_division_toe.json', 'american_1942q4_2nd_armored_division_toe.json'],
  ['italian_1942q3_pavia_division_toe.json', 'french_1942q3_1re_division_fran_aise_libre_toe.json', 'british_1942q3_1st_armoured_division_toe.json'],
  ['italian_1942q2_101st_trieste_division_toe.json', 'italian_1942q2_brescia_division_toe.json', 'italian_1942q2_pavia_division_toe.json'],
  ['british_1942q2_50th_infantry_division_toe.json', 'british_1942q2_2nd_south_african_division_toe.json', 'british_1942q2_4th_indian_division_toe.json'],
  ['british_1942q2_2nd_new_zealand_division_toe.json', 'british_1942q2_1st_south_african_division_toe.json', 'british_1942q1_50th_infantry_division_toe.json'],
  ['british_1942q1_1st_south_african_division_toe.json', 'italian_1941q3_trento_division_toe.json', 'british_1941q3_4th_indian_division_toe.json'],
  ['british_1941q3_1st_south_african_division_toe.json', 'italian_1941q1_2nd_ccnn_division_28_ottobre_toe.json', 'french_1943q2_force_l_toe.json'],
  ['italian_1941q1_1st_ccnn_division_23_marzo_toe.json', 'italian_1940q4_pavia_division_toe.json', 'italian_1940q4_4th_ccnn_division_3_gennaio_toe.json'],
  ['italian_1940q4_brescia_division_toe.json', 'italian_1940q4_1st_ccnn_division_23_marzo_toe.json', 'italian_1940q3_4th_ccnn_division_3_gennaio_toe.json'],
  ['italian_1940q4_catanzaro_division_toe.json', 'italian_1940q3_pavia_division_toe.json', 'british_1940q4_1st_south_african_division_toe.json'],
  ['british_1943q2_1st_greek_brigade_toe.json', 'french_1942q1_1re_brigade_fran_aise_libre_toe.json', 'french_1943q1_force_l_toe.json'],
  ['italian_1941q1_brescia_division_toe.json', 'italian_1940q3_catanzaro_division_toe.json', 'italian_1943q1_centauro_division_toe.json'],
  ['italian_1942q4_ariete_division_toe.json', 'italian_1942q3_ariete_division_toe.json', 'italian_1942q1_xxi_corpo_d_armata_xxi_corps_toe.json'],
  ['italian_1942q1_brescia_division_toe.json', 'italian_1941q4_littorio_division_toe.json', 'italian_1941q4_ariete_division_toe.json'],
  ['italian_1941q2_brescia_division_toe.json', 'italian_1941q1_sirte_division_toe.json', 'italian_1941q1_savona_division_toe.json'],
  ['italian_1940q4_xxii_corpo_d_armata_xxii_corps_toe.json', 'italian_1940q4_xxi_corpo_d_armata_xxi_corps_toe.json', 'italian_1940q4_10_armata_italian_10th_army_toe.json'],
  ['german_1943q1_21_panzer_division_toe.json', 'german_1942q4_21_panzer_division_toe.json', 'german_1942q3_panzerarmee_afrika_toe.json'],
  ['french_1943q1_1re_division_fran_aise_libre_toe.json', 'french_1942q2_1re_brigade_fran_aise_libre_toe.json', 'british_1943q1_2nd_new_zealand_division_toe.json'],
  ['british_1943q1_50th_infantry_division_toe.json', 'british_1942q4_xiii_corps_toe.json', 'british_1942q4_78th_infantry_division_battleaxe_toe.json'],
  ['british_1942q4_6th_armoured_division_toe.json', 'british_1942q4_4th_indian_division_toe.json', 'british_1942q4_4th_infantry_division_toe.json'],
  ['british_1942q2_9th_australian_division_toe.json', 'british_1942q1_xxx_corps_toe.json', 'british_1942q1_xiii_corps_toe.json'],
  ['british_1941q4_czechoslovakian_11th_infantry_battalion_toe.json', 'british_1941q4_polish_carpathian_brigade_karpacka_brygada_strzelc_w_toe.json', 'british_1941q4_70th_infantry_division_toe.json'],
  ['british_1941q4_2nd_south_african_division_toe.json', 'british_1941q3_polish_carpathian_brigade_karpacka_brygada_strzelc_w_toe.json', 'british_1941q3_eighth_army_8th_army_toe.json'],
  ['british_1941q2_5th_indian_division_toe.json', 'british_1941q2_2nd_south_african_division_toe.json', 'british_1941q1_xiii_corps_toe.json'],
  ['british_1941q2_1st_south_african_division_toe.json', 'british_1941q1_4th_indian_division_toe.json', 'british_1940q4_western_desert_force_toe.json'],
  ['british_1940q4_7th_armoured_division_toe.json', 'british_1940q3_western_desert_force_toe.json', 'british_1940q2_7th_armoured_division_toe.json'],
  ['british_1940q2_4th_indian_division_toe.json']
];

/**
 * Load workflow state
 */
async function loadWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        console.error(`WARNING: Could not load workflow state: ${error.message}`);
        return { wikipedia_upgrade: { current_batch: 0, completed_batches: [] } };
    }
}

/**
 * Save workflow state
 */
async function saveWorkflowState(state) {
    try {
        await fs.writeFile(WORKFLOW_STATE, JSON.stringify(state, null, 2));
    } catch (error) {
        console.error(`ERROR: Could not save workflow state: ${error.message}`);
    }
}

/**
 * Check if unit has Wikipedia sources
 */
async function hasWikipediaSource(unitFile) {
    const filepath = path.join(UNITS_DIR, unitFile);
    try {
        const content = await fs.readFile(filepath, 'utf-8');
        const unit = JSON.parse(content);

        const sources = unit.validation?.source || [];
        const sourceArray = Array.isArray(sources) ? sources : [sources];

        const wikipediaPatterns = [
            'wikipedia.org',
            'wikipedia.com',
            'wikia',
            'fandom',
            'wiki/',
            'wikipedia'
        ];

        for (const source of sourceArray) {
            const sourceText = typeof source === 'string' ? source : JSON.stringify(source);
            const lowerText = sourceText.toLowerCase();

            if (wikipediaPatterns.some(pattern => lowerText.includes(pattern))) {
                return true;
            }
        }

        return false;
    } catch (error) {
        console.error(`ERROR checking ${unitFile}: ${error.message}`);
        return false;
    }
}

/**
 * Show next batch to process
 */
async function showNextBatch() {
    console.log('Wikipedia Source Upgrade - Next Batch');
    console.log('='.repeat(80));
    console.log('');

    const state = await loadWorkflowState();
    const currentBatch = state.wikipedia_upgrade?.current_batch || 0;

    if (currentBatch >= BATCHES.length) {
        console.log('All batches completed!');
        console.log('');
        console.log(`Total batches: ${BATCHES.length}`);
        console.log(`Completed: ${currentBatch}`);
        console.log('');
        return;
    }

    const batchNum = currentBatch + 1;
    const units = BATCHES[currentBatch];

    console.log(`Current Batch: ${batchNum}/${BATCHES.length}`);
    console.log(`Units in batch: ${units.length}`);
    console.log('');

    console.log('Units to upgrade:');
    for (let i = 0; i < units.length; i++) {
        const unitFile = units[i];
        const filepath = path.join(UNITS_DIR, unitFile);

        if (!fsSync.existsSync(filepath)) {
            console.log(`  ${i + 1}. ${unitFile} [FILE NOT FOUND]`);
            continue;
        }

        try {
            const content = await fs.readFile(filepath, 'utf-8');
            const unit = JSON.parse(content);

            const nation = unit.nation || 'unknown';
            const quarter = unit.quarter || 'unknown';
            const designation = unit.unit_designation || 'Unknown';
            const confidence = unit.validation?.confidence || 0;
            const tier = unit.validation?.tier || 'unknown';

            console.log(`  ${i + 1}. ${unitFile}`);
            console.log(`      Nation: ${nation}, Quarter: ${quarter}`);
            console.log(`      Unit: ${designation}`);
            console.log(`      Tier: ${tier}, Confidence: ${confidence}%`);
            console.log('');
        } catch (error) {
            console.log(`  ${i + 1}. ${unitFile} [PARSE ERROR: ${error.message}]`);
        }
    }

    console.log('='.repeat(80));
    console.log('Next steps:');
    console.log('  1. Launch 3 source_upgrader agents in parallel (Task tool)');
    console.log('  2. Wait for completion');
    console.log('  3. Run: npm run wikipedia:validate');
    console.log('  4. If validation passes: npm run checkpoint && npm run session:end');
    console.log('  5. Batch will auto-advance on next npm run wikipedia:next');
    console.log('');
}

/**
 * Validate current batch (check if Wikipedia removed)
 */
async function validateBatch() {
    console.log('Wikipedia Source Upgrade - Batch Validation');
    console.log('='.repeat(80));
    console.log('');

    const state = await loadWorkflowState();
    const currentBatch = state.wikipedia_upgrade?.current_batch || 0;

    if (currentBatch >= BATCHES.length) {
        console.log('No active batch to validate.');
        return;
    }

    const batchNum = currentBatch + 1;
    const units = BATCHES[currentBatch];

    console.log(`Validating Batch ${batchNum}/${BATCHES.length}...`);
    console.log('');

    let allPassed = true;
    const results = [];

    for (const unitFile of units) {
        const hasWiki = await hasWikipediaSource(unitFile);
        const status = hasWiki ? 'FAILED - Wikipedia still present' : 'PASSED';
        results.push({ unitFile, hasWiki, status });

        if (hasWiki) {
            allPassed = false;
        }
    }

    console.log('Validation Results:');
    for (const result of results) {
        const icon = result.hasWiki ? '✗' : '✓';
        console.log(`  ${icon} ${result.unitFile}: ${result.status}`);
    }
    console.log('');

    if (allPassed) {
        console.log('SUCCESS: All units in batch passed Wikipedia validation');
        console.log('');
        console.log('Next steps:');
        console.log('  1. Run: npm run checkpoint');
        console.log('  2. Run: npm run session:end');
        console.log('  3. Batch will auto-advance on next npm run wikipedia:next');
        console.log('');

        // Mark batch as complete
        state.wikipedia_upgrade = state.wikipedia_upgrade || {};
        state.wikipedia_upgrade.current_batch = currentBatch + 1;
        state.wikipedia_upgrade.completed_batches = state.wikipedia_upgrade.completed_batches || [];
        state.wikipedia_upgrade.completed_batches.push({
            batch: batchNum,
            completed: new Date().toISOString(),
            units: units
        });

        await saveWorkflowState(state);
        console.log(`Batch ${batchNum} marked as complete.`);
        console.log('');
    } else {
        console.log('FAILED: Some units still contain Wikipedia sources');
        console.log('');
        console.log('Options:');
        console.log('  1. Review failed units manually');
        console.log('  2. Re-run source upgrade for failed units');
        console.log('  3. Annotate as NEEDS_RESEARCH if no Tier 1/2 sources available');
        console.log('');
    }

    console.log('='.repeat(80));
}

/**
 * Show overall progress
 */
async function showStatus() {
    console.log('Wikipedia Source Upgrade - Overall Status');
    console.log('='.repeat(80));
    console.log('');

    const state = await loadWorkflowState();
    const currentBatch = state.wikipedia_upgrade?.current_batch || 0;
    const completedBatches = state.wikipedia_upgrade?.completed_batches || [];

    const totalBatches = BATCHES.length;
    const totalUnits = BATCHES.reduce((sum, batch) => sum + batch.length, 0);
    const completedUnits = completedBatches.reduce((sum, batch) => sum + batch.units.length, 0);

    const pctBatches = ((currentBatch / totalBatches) * 100).toFixed(1);
    const pctUnits = ((completedUnits / totalUnits) * 100).toFixed(1);

    console.log(`Batches: ${currentBatch}/${totalBatches} (${pctBatches}%)`);
    console.log(`Units: ${completedUnits}/${totalUnits} (${pctUnits}%)`);
    console.log('');

    if (currentBatch > 0) {
        console.log('Recently Completed Batches:');
        const recent = completedBatches.slice(-5);
        for (const batch of recent) {
            const date = new Date(batch.completed).toLocaleString();
            console.log(`  Batch ${batch.batch}: ${batch.units.length} units (${date})`);
        }
        console.log('');
    }

    if (currentBatch < totalBatches) {
        const remaining = totalBatches - currentBatch;
        console.log(`Remaining: ${remaining} batches (${totalUnits - completedUnits} units)`);
        console.log('');
        console.log('Run: npm run wikipedia:next');
    } else {
        console.log('All batches completed!');
    }

    console.log('');
    console.log('='.repeat(80));
}

// CLI
const command = process.argv[2] || 'next';

switch (command) {
    case 'next':
        showNextBatch().catch(error => {
            console.error('ERROR:', error.message);
            process.exit(1);
        });
        break;

    case 'validate':
        validateBatch().catch(error => {
            console.error('ERROR:', error.message);
            process.exit(1);
        });
        break;

    case 'status':
        showStatus().catch(error => {
            console.error('ERROR:', error.message);
            process.exit(1);
        });
        break;

    default:
        console.error(`Unknown command: ${command}`);
        console.error('Usage: npm run wikipedia:next|validate|status');
        process.exit(1);
}
