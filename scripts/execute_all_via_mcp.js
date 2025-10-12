#!/usr/bin/env node

/**
 * Execute All Statements via MCP
 *
 * Reads backfill_statements.json and outputs a series of MCP write_query calls
 * for Claude Code to execute via copy-paste
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const STATEMENTS_FILE = path.join(PROJECT_ROOT, 'data/backfill_statements.json');

function main() {
    const statements = JSON.parse(fs.readFileSync(STATEMENTS_FILE, 'utf-8'));

    console.log(`// Total statements to execute: ${statements.length}\n`);
    console.log(`// Progress tracking:\n`);

    let inserted = 0;
    let skipped = 0;

    // Output statistics for already processed (based on previous runs)
    // We've processed 20 statements: 3 inserted, 17 skipped
    console.log(`// Already processed: 20 statements (3 inserted, 17 skipped)\n`);
    console.log(`// Remaining: ${statements.length - 20} statements\n\n`);

    // Start from statement 21 (index 20)
    console.log(`// Starting from statement 21...\n`);

    for (let i = 20; i < statements.length; i++) {
        const stmt = statements[i];
        console.log(`// Statement ${i + 1}/${statements.length}`);
        console.log(`mcp__sqlite__write_query: ${stmt.substring(0, 100)}...`);
        console.log('');
    }

    console.log(`\n// Execute the remaining ${statements.length - 20} statements via MCP`);
}

main();
