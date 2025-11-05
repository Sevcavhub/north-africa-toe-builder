#!/usr/bin/env node

/**
 * Execute Backfill SQL - Safely insert units into database
 *
 * Reads the generated SQL file and provides instructions for executing
 * via SQLite MCP in Claude Code.
 *
 * Usage: node scripts/execute_backfill.js
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const SQL_FILE = path.join(PROJECT_ROOT, 'data/backfill_inserts.sql');

async function main() {
    console.log('\n' + '═'.repeat(80));
    console.log('  💾 EXECUTE BACKFILL - Database Population');
    console.log('═'.repeat(80));
    console.log('');

    // Read SQL file
    const sql = fs.readFileSync(SQL_FILE, 'utf-8');

    // Split into individual INSERT statements
    const statements = sql
        .split(/;\s*\n/)
        .filter(s => s.trim().startsWith('INSERT INTO'))
        .map(s => s.trim() + ';');

    console.log(`📊 Found ${statements.length} INSERT statements\n`);

    // Convert to INSERT OR IGNORE to skip duplicates
    const safeStatements = statements.map(stmt =>
        stmt.replace('INSERT INTO', 'INSERT OR IGNORE INTO')
    );

    console.log('✅ Converted to INSERT OR IGNORE (skips duplicates)\n');

    // Write modified SQL
    const safeSQL = safeStatements.join('\n\n');
    const safeSQLFile = path.join(PROJECT_ROOT, 'data/backfill_safe.sql');
    fs.writeFileSync(safeSQLFile, safeSQL);

    console.log(`💾 Safe SQL written to: ${safeSQLFile}`);
    console.log('');
    console.log('═'.repeat(80));
    console.log('  EXECUTION METHOD');
    console.log('═'.repeat(80));
    console.log('');
    console.log('Option 1: Execute via Node.js script (requires sqlite3)');
    console.log('  npm install sqlite3');
    console.log('  node scripts/execute_sqlite.js');
    console.log('');
    console.log('Option 2: Execute via Claude Code MCP');
    console.log('  Use Claude Code with SQLite MCP to run:');
    console.log(`  - Read ${safeSQLFile}`);
    console.log('  - Execute each INSERT OR IGNORE statement');
    console.log('  - Report how many were inserted vs skipped');
    console.log('');
    console.log('Option 3: Batch execution');
    console.log('  sqlite3 data/toe_database.db < data/backfill_safe.sql');
    console.log('');
    console.log('═'.repeat(80));
    console.log('');

    // Create summary report
    console.log('📋 UNIT SUMMARY:');
    const nations = {};
    statements.forEach(stmt => {
        const match = stmt.match(/VALUES\s*\(\s*'([^']+)',\s*'([^']+)',\s*'([^']+)'/);
        if (match) {
            const [, nation, quarter, unit] = match;
            if (!nations[nation]) nations[nation] = 0;
            nations[nation]++;
        }
    });

    for (const [nation, count] of Object.entries(nations).sort()) {
        console.log(`   ${nation}: ${count} units`);
    }
    console.log('');
}

main().catch(error => {
    console.error('❌ Error:', error.message);
    process.exit(1);
});
