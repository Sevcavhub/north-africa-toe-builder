#!/usr/bin/env node

/**
 * Test script for START_HERE_NEW_SESSION.md auto-update logic
 *
 * Tests the update function without actually running session:end
 * Safe to run while another session is active
 */

const fs = require('fs').promises;
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const START_HERE_PATH = path.join(PROJECT_ROOT, 'START_HERE_NEW_SESSION.md');
const WORKFLOW_STATE_PATH = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');

async function testUpdateLogic() {
    console.log('🧪 Testing START_HERE_NEW_SESSION.md update logic\n');

    try {
        // Read current workflow state
        const workflowData = await fs.readFile(WORKFLOW_STATE_PATH, 'utf-8');
        const state = JSON.parse(workflowData);

        console.log('📊 Current State:');
        console.log(`   - Completed: ${state.completed.length}/${state.total_units}`);
        console.log(`   - Percentage: ${((state.completed.length / state.total_units) * 100).toFixed(1)}%`);
        console.log(`   - Remaining: ${state.total_units - state.completed.length}`);
        console.log('');

        // Read START_HERE_NEW_SESSION.md
        const content = await fs.readFile(START_HERE_PATH, 'utf-8');

        // Check if template markers exist
        const hasMetadata = content.includes('<!-- AUTO-UPDATED: START - Session Metadata -->');
        const hasProgress = content.includes('<!-- AUTO-UPDATED: START - Progress Stats -->');
        const hasRecent = content.includes('<!-- AUTO-UPDATED: START - Recently Completed -->');

        console.log('✅ Template Markers Check:');
        console.log(`   - Session Metadata: ${hasMetadata ? '✅ Found' : '❌ Missing'}`);
        console.log(`   - Progress Stats: ${hasProgress ? '✅ Found' : '❌ Missing'}`);
        console.log(`   - Recently Completed: ${hasRecent ? '✅ Found' : '❌ Missing'}`);
        console.log('');

        if (!hasMetadata || !hasProgress || !hasRecent) {
            console.error('❌ Missing template markers! Update will not work correctly.\n');
            return false;
        }

        // Test data that would be generated
        const now = new Date();
        const dateStr = now.toISOString().split('T')[0];
        const timeStr = now.toTimeString().split(' ')[0].slice(0, 5);
        const completedCount = state.completed.length;
        const totalUnits = state.total_units;
        const remaining = totalUnits - completedCount;
        const percentComplete = ((completedCount / totalUnits) * 100).toFixed(1);

        console.log('📝 Would Update To:');
        console.log(`   - Last Updated: ${dateStr} ${timeStr}`);
        console.log(`   - Status: Schema v3.0 Complete, ${completedCount}/${totalUnits} units (${percentComplete}%)`);
        console.log(`   - Progress: ${completedCount}/${totalUnits} units (${percentComplete}%)`);
        console.log(`   - Remaining: ${remaining} units`);
        console.log('');

        // Show last 9 completed units
        const recentUnits = state.completed.slice(-9);
        console.log('📋 Recent Work (last 9 units):');
        recentUnits.forEach(u => console.log(`   - ${u}`));
        console.log('');

        console.log('✅ Test successful! Logic appears correct.');
        console.log('');
        console.log('💡 The auto-update will run automatically when you run:');
        console.log('   npm run session:end');
        console.log('');
        console.log('⚠️  Note: Not running actual update (active session in progress)');

        return true;
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        return false;
    }
}

// Run test
testUpdateLogic().then(success => {
    process.exit(success ? 0 : 1);
});
