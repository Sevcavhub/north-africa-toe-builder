#!/usr/bin/env node

/**
 * Fix Quarter Format - Convert lowercase quarter to YYYY-QN format
 *
 * Converts: "1942q4" → "1942-Q4"
 *
 * Usage: node scripts/fix_quarter_format.js
 */

const fs = require('fs').promises;
const path = require('path');

const UNITS_DIR = path.join(__dirname, '../data/output/units');

async function fixQuarterFormat() {
    console.log('🔧 Fixing quarter format in unit files...\n');

    const files = await fs.readdir(UNITS_DIR);
    const jsonFiles = files.filter(f => f.endsWith('.json'));

    let fixedCount = 0;
    let errorCount = 0;

    for (const file of jsonFiles) {
        const filePath = path.join(UNITS_DIR, file);

        try {
            const content = await fs.readFile(filePath, 'utf-8');
            const data = JSON.parse(content);

            // Check if quarter needs fixing (both lowercase and missing Q)
            const needsFix =
                (data.quarter && /^\d{4}q[1-4]$/.test(data.quarter)) || // 1942q4
                (data.quarter && /^\d{4}-[1-4]$/.test(data.quarter));    // 1942-4

            if (needsFix) {
                const oldQuarter = data.quarter;

                // Extract year and quarter number
                const year = data.quarter.substring(0, 4);
                const quarterNum = data.quarter.match(/[1-4]$/)[0];

                // Convert to: 1942-Q4
                data.quarter = `${year}-Q${quarterNum}`;

                // Write back
                await fs.writeFile(filePath, JSON.stringify(data, null, 2) + '\n');

                console.log(`✓ ${file}`);
                console.log(`  ${oldQuarter} → ${data.quarter}`);
                fixedCount++;
            }
        } catch (error) {
            console.error(`✗ ${file}: ${error.message}`);
            errorCount++;
        }
    }

    console.log('\n' + '='.repeat(60));
    console.log(`✅ Fixed: ${fixedCount} files`);
    console.log(`❌ Errors: ${errorCount} files`);
    console.log('='.repeat(60));
}

fixQuarterFormat().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
