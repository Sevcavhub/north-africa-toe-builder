#!/usr/bin/env node

/**
 * Safe Checkpoint Wrapper
 *
 * Runs checkpoint + reconciliation to ensure WORKFLOW_STATE stays clean
 *
 * Flow:
 * 1. Run standard checkpoint (stores filename-based IDs)
 * 2. Run reconciliation (converts to canonical IDs)
 * 3. Regenerate work queue (uses canonical IDs)
 *
 * This prevents ID drift while keeping validation working.
 */

const { execSync } = require('child_process');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..', '..', '..');

console.log('🔒 Running SAFE checkpoint with reconciliation...\n');
console.log('═'.repeat(80));

// Step 1: Run standard checkpoint
console.log('\n📍 Step 1/3: Creating checkpoint...\n');
try {
    execSync('node scripts/create_checkpoint.js', {
        cwd: PROJECT_ROOT,
        stdio: 'inherit'
    });
} catch (error) {
    console.error('\n❌ Checkpoint failed:', error.message);
    console.error('\n⚠️  Fix errors above and try again\n');
    process.exit(1);
}

// Step 2: Reconcile to canonical IDs
console.log('\n═'.repeat(80));
console.log('\n🔄 Step 2/3: Reconciling to canonical IDs...\n');
try {
    execSync('node scripts/reconcile_workflow_state.js', {
        cwd: PROJECT_ROOT,
        stdio: 'inherit'
    });
} catch (error) {
    console.error('\n❌ Reconciliation failed:', error.message);
    console.error('\n⚠️  WORKFLOW_STATE may have non-canonical IDs\n');
    process.exit(1);
}

// Step 3: Regenerate work queue
console.log('\n═'.repeat(80));
console.log('\n📋 Step 3/3: Regenerating work queue...\n');
try {
    execSync('node scripts/generate_work_queue.js', {
        cwd: PROJECT_ROOT,
        stdio: 'inherit'
    });
} catch (error) {
    console.warn('\n⚠️  Queue generation failed (non-critical)');
    console.warn('   You can regenerate manually: npm run queue:generate\n');
}

console.log('\n═'.repeat(80));
console.log('\n✅ SAFE CHECKPOINT COMPLETE!\n');
console.log('   ✓ Progress saved');
console.log('   ✓ IDs reconciled to canonical format');
console.log('   ✓ Work queue updated');
console.log('   ✓ Ready to continue extraction\n');
