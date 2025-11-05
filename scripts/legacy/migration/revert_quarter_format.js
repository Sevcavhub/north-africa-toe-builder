#!/usr/bin/env node

/**
 * Revert Quarter Format - Fix incorrect YYYY-QN back to yyyyqn
 *
 * Reverts incorrect changes that converted lowercase format to uppercase.
 * Converts: "1942-Q4" → "1942q4"
 *
 * Context: The schema was incorrect. The actual standard used by the orchestrator
 * is lowercase with no hyphen (1942q4), not uppercase with hyphen (1942-Q4).
 *
 * Usage: node scripts/revert_quarter_format.js
 */

const fs = require('fs').promises;
const path = require('path');

const UNITS_DIR = path.join(__dirname, '../data/output/units');

async function revertQuarterFormat() {
    console.log('🔄 Reverting quarter format to correct standard (yyyyqn)...\n');

    const files = await fs.readdir(UNITS_DIR);
    const jsonFiles = files.filter(f => f.endsWith('.json'));

    let fixedCount = 0;
    let errorCount = 0;
    let alreadyCorrectCount = 0;

    for (const file of jsonFiles) {
        const filePath = path.join(UNITS_DIR, file);

        try {
            const content = await fs.readFile(filePath, 'utf-8');
            const data = JSON.parse(content);

            // Check if quarter needs reverting (YYYY-QN format)
            if (data.quarter && /^\d{4}-Q[1-4]$/.test(data.quarter)) {
                const oldQuarter = data.quarter;

                // Convert: 1942-Q4 → 1942q4
                const year = data.quarter.substring(0, 4);
                const quarterNum = data.quarter.substring(6); // Get "4" from "1942-Q4"
                data.quarter = `${year}q${quarterNum}`;

                // Write back
                await fs.writeFile(filePath, JSON.stringify(data, null, 2) + '\n');

                console.log(`✓ ${file}`);
                console.log(`  ${oldQuarter} → ${data.quarter}`);
                fixedCount++;
            } else if (data.quarter && /^\d{4}q[1-4]$/.test(data.quarter)) {
                // Already in correct format
                alreadyCorrectCount++;
            }
        } catch (error) {
            console.error(`✗ ${file}: ${error.message}`);
            errorCount++;
        }
    }

    console.log('\n' + '='.repeat(60));
    console.log(`✅ Reverted: ${fixedCount} files`);
    console.log(`✓  Already correct: ${alreadyCorrectCount} files`);
    console.log(`❌ Errors: ${errorCount} files`);
    console.log('='.repeat(60));

    if (fixedCount > 0) {
        console.log('\n📝 Summary:');
        console.log('   Quarter format has been reverted to the correct standard:');
        console.log('   - Format: yyyyqn (lowercase, no hyphen)');
        console.log('   - Example: 1942q4');
        console.log('   - This matches the orchestrator output standard.');
    }
}

revertQuarterFormat().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
