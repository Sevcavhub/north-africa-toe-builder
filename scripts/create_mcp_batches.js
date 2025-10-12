#!/usr/bin/env node

/**
 * Create MCP Batch Files
 *
 * Reads backfill_statements.json and creates batch SQL files
 * for execution via SQLite MCP write_query tool
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const STATEMENTS_FILE = path.join(PROJECT_ROOT, 'data/backfill_statements.json');
const OUTPUT_DIR = path.join(PROJECT_ROOT, 'data/mcp_batches');

const BATCH_SIZE = 10;

function main() {
    // Create output directory
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // Read statements
    const statements = JSON.parse(fs.readFileSync(STATEMENTS_FILE, 'utf-8'));

    console.log(`Total statements: ${statements.length}`);
    console.log(`Batch size: ${BATCH_SIZE}`);
    console.log(`Number of batches: ${Math.ceil(statements.length / BATCH_SIZE)}\n`);

    // Create batches
    let batchNum = 1;
    for (let i = 0; i < statements.length; i += BATCH_SIZE) {
        const batch = statements.slice(i, i + BATCH_SIZE);
        const batchSQL = `BEGIN TRANSACTION;\n\n${batch.join('\n\n')}\n\nCOMMIT;`;

        const filename = `batch_${String(batchNum).padStart(2, '0')}.sql`;
        const filepath = path.join(OUTPUT_DIR, filename);

        fs.writeFileSync(filepath, batchSQL, 'utf-8');
        console.log(`✓ Created ${filename} (${batch.length} statements)`);

        batchNum++;
    }

    console.log(`\n✅ Created ${batchNum - 1} batch files in ${OUTPUT_DIR}`);
}

main();
