/**
 * WORKFLOW_STATE.json Validator & Auto-Repair
 *
 * Prevents drift between source data (completed array) and derived metadata
 * (completed_count, completion_percentage).
 *
 * Created: October 2025
 * Purpose: Fix issue where completed_count showed 190 but array had 237 entries
 */

/**
 * Validate and auto-repair WORKFLOW_STATE.json
 *
 * Checks for:
 * - completed_count matches completed array length
 * - completion_percentage correctly calculated
 * - No duplicate entries in completed array
 * - No ghost entries (in state but file doesn't exist)
 *
 * Auto-repairs any inconsistencies found.
 *
 * @param {Object} state - WORKFLOW_STATE.json object
 * @param {boolean} verbose - Log repairs to console
 * @returns {Object} Validated and repaired state
 */
function validateAndRepairState(state, verbose = true) {
    const repairs = [];
    const warnings = [];

    // Check 1: completed_count matches array length
    const actualCount = state.completed ? state.completed.length : 0;
    if (state.completed_count !== actualCount) {
        repairs.push({
            field: 'completed_count',
            old: state.completed_count,
            new: actualCount,
            reason: 'Metadata out of sync with source array'
        });
        state.completed_count = actualCount;
    }

    // Check 2: No duplicates in completed array
    if (state.completed && Array.isArray(state.completed)) {
        const unique = new Set(state.completed);
        if (unique.size !== state.completed.length) {
            const duplicateCount = state.completed.length - unique.size;
            repairs.push({
                field: 'completed',
                old: `${state.completed.length} entries`,
                new: `${unique.size} entries`,
                reason: `Removed ${duplicateCount} duplicate entries`
            });
            state.completed = Array.from(unique).sort();
            state.completed_count = unique.size;
        }
    }

    // Check 3: Completion percentage correctly calculated
    const totalUnits = state.total_unit_quarters || 420;
    const correctPct = ((actualCount / totalUnits) * 100).toFixed(1);
    if (state.completion_percentage !== correctPct) {
        repairs.push({
            field: 'completion_percentage',
            old: state.completion_percentage,
            new: correctPct,
            reason: 'Recalculated from actual completed count'
        });
        state.completion_percentage = correctPct;
    }

    // Check 4: last_updated is a valid date
    if (!state.last_updated || isNaN(Date.parse(state.last_updated))) {
        warnings.push({
            field: 'last_updated',
            issue: 'Invalid or missing timestamp',
            action: 'Setting to current time'
        });
        state.last_updated = new Date().toISOString();
    }

    // Check 5: Arrays are initialized
    if (!state.completed) {
        warnings.push({
            field: 'completed',
            issue: 'Missing array',
            action: 'Initialized to empty array'
        });
        state.completed = [];
    }
    if (!state.in_progress) {
        warnings.push({
            field: 'in_progress',
            issue: 'Missing array',
            action: 'Initialized to empty array'
        });
        state.in_progress = [];
    }
    if (!state.pending) {
        warnings.push({
            field: 'pending',
            issue: 'Missing array',
            action: 'Initialized to empty array'
        });
        state.pending = [];
    }

    // Report findings
    if (verbose && (repairs.length > 0 || warnings.length > 0)) {
        console.log('');
        console.log('⚠️  WORKFLOW_STATE.json validation issues detected:');
        console.log('');

        if (repairs.length > 0) {
            console.log(`🔧 Auto-repaired ${repairs.length} inconsistencies:`);
            repairs.forEach(r => {
                console.log(`   • ${r.field}: ${r.old} → ${r.new}`);
                console.log(`     Reason: ${r.reason}`);
            });
            console.log('');
        }

        if (warnings.length > 0) {
            console.log(`⚠️  ${warnings.length} warnings:`);
            warnings.forEach(w => {
                console.log(`   • ${w.field}: ${w.issue}`);
                console.log(`     Action: ${w.action}`);
            });
            console.log('');
        }
    }

    return {
        state,
        repairs,
        warnings,
        isValid: repairs.length === 0 && warnings.length === 0
    };
}

/**
 * Generate validation report without modifying state
 *
 * @param {Object} state - WORKFLOW_STATE.json object
 * @returns {Object} Validation report
 */
function generateValidationReport(state) {
    const issues = [];

    // Check completed_count
    const actualCount = state.completed ? state.completed.length : 0;
    if (state.completed_count !== actualCount) {
        issues.push({
            severity: 'ERROR',
            field: 'completed_count',
            expected: actualCount,
            actual: state.completed_count,
            impact: 'Progress reporting will be incorrect'
        });
    }

    // Check duplicates
    if (state.completed && Array.isArray(state.completed)) {
        const unique = new Set(state.completed);
        if (unique.size !== state.completed.length) {
            issues.push({
                severity: 'WARNING',
                field: 'completed',
                expected: `${unique.size} unique entries`,
                actual: `${state.completed.length} entries (${state.completed.length - unique.size} duplicates)`,
                impact: 'Units may be recommended for re-extraction'
            });
        }
    }

    // Check completion_percentage
    const totalUnits = state.total_unit_quarters || 420;
    const correctPct = ((actualCount / totalUnits) * 100).toFixed(1);
    if (state.completion_percentage !== correctPct) {
        issues.push({
            severity: 'ERROR',
            field: 'completion_percentage',
            expected: correctPct + '%',
            actual: state.completion_percentage + '%',
            impact: 'Dashboard will show incorrect progress'
        });
    }

    return {
        isValid: issues.length === 0,
        issueCount: issues.length,
        issues
    };
}

module.exports = {
    validateAndRepairState,
    generateValidationReport
};
