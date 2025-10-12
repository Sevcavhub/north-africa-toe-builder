#!/usr/bin/env node

/**
 * Session Start - Initialize new work session
 *
 * Prepares for autonomous work by:
 * 1. Reading WORKFLOW_STATE.json to find resume point
 * 2. Querying Memory MCP for project knowledge (if available)
 * 3. Displaying session info and next units to process
 * 4. Generating suggested next batch
 *
 * Usage: node scripts/session_start.js
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');
const { queryProjectKnowledge } = require('./memory_mcp_helpers');

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

async function queryMemoryMCP() {
    // Query project knowledge using helper module
    console.log('🧠 Querying project knowledge...');

    try {
        const knowledge = await queryProjectKnowledge();

        if (knowledge.available) {
            console.log('   ✅ Memory MCP available');
        } else {
            console.log('   💾 Using local cache (Memory MCP not available)');
        }

        // If no patterns/decisions in cache, use defaults
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
    // Load seed units to know what we need to process
    try {
        const seedPath = path.join(PROJECT_ROOT, 'projects/north_africa_seed_units.json');
        const data = await fs.readFile(seedPath, 'utf-8');
        const seeds = JSON.parse(data);

        // Convert to flat list
        const units = [];
        const nationMap = {
            'german_units': 'germany',
            'italian_units': 'italy',
            'british_units': 'britain',
            'usa_units': 'usa',
            'french_units': 'france'
        };

        for (const [key, value] of Object.entries(seeds)) {
            if (Array.isArray(value)) {
                for (const unit of value) {
                    for (const quarter of unit.quarters) {
                        const nation = nationMap[key] || key.replace('_units', '');
                        const unitId = `${nation}_${quarter.toLowerCase().replace(/-/, '')}_${unit.designation.toLowerCase().replace(/[^a-z0-9]/g, '_')}`;
                        units.push({
                            id: unitId,
                            nation: nation,
                            quarter: quarter,
                            designation: unit.designation
                        });
                    }
                }
            }
        }

        return units;
    } catch (error) {
        console.warn('⚠️  Could not load seed units:', error.message);
        return [];
    }
}

function getNextBatch(allUnits, completed, batchSize = 3) {
    // Filter to pending units
    const pending = allUnits.filter(u => !completed.includes(u.id));

    // Group by quarter for logical batching
    const byQuarter = {};
    for (const unit of pending) {
        if (!byQuarter[unit.quarter]) {
            byQuarter[unit.quarter] = [];
        }
        byQuarter[unit.quarter].push(unit);
    }

    // Get next batch from earliest quarter
    const quarters = Object.keys(byQuarter).sort();
    if (quarters.length === 0) return [];

    return byQuarter[quarters[0]].slice(0, batchSize);
}

function displaySessionInfo(state, memory, nextBatch) {
    console.log('═'.repeat(80));
    console.log('  SESSION START - NORTH AFRICA TO&E BUILDER');
    console.log('═'.repeat(80));
    console.log('');

    if (state) {
        const completedCount = state.completed.length;
        const remaining = state.total_units - completedCount;
        const percentComplete = ((completedCount / state.total_units) * 100).toFixed(1);

        console.log('📊 **PROGRESS SUMMARY**\n');
        console.log(`   Total Units:     ${state.total_units}`);
        console.log(`   Completed:       ${completedCount} (${percentComplete}%)`);
        console.log(`   Remaining:       ${remaining}`);
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
    } else {
        console.log('🆕 **NEW SESSION**\n');
        console.log('   No previous progress found');
        console.log('   Starting from beginning');
        console.log('');
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

    if (nextBatch.length > 0) {
        console.log('🚀 **SUGGESTED NEXT BATCH** (3 units)\n');
        nextBatch.forEach((unit, i) => {
            console.log(`   ${i + 1}. ${unit.nation.toUpperCase()} - ${unit.designation} (${unit.quarter})`);
        });
        console.log('');
        console.log('   Run in Claude Code chat:');
        console.log('   ```');
        console.log('   npm run start:autonomous');
        console.log('   ```');
        console.log('   Then paste the autonomous prompt and specify these 3 units');
        console.log('');
    }

    console.log('═'.repeat(80));
    console.log('');
}

async function main() {
    console.log('');

    // Read workflow state
    const state = await readWorkflowState();

    // Query Memory MCP
    const memory = await queryMemoryMCP();

    // Get all seed units
    const allUnits = await getSeedUnits();

    // Calculate next batch
    const completed = state ? state.completed : [];
    const nextBatch = getNextBatch(allUnits, completed);

    // Display session info
    displaySessionInfo(state, memory, nextBatch);

    // Write session start marker
    const sessionLog = path.join(PROJECT_ROOT, 'SESSION_ACTIVE.txt');
    await fs.writeFile(sessionLog, `Session started: ${new Date().toISOString()}\n`);

    console.log('💡 **TIP:** Run `npm run session:end` when finished to save progress\n');
}

// Run
main().catch(error => {
    console.error('❌ Session start failed:', error.message);
    process.exit(1);
});
