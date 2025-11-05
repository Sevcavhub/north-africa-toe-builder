#!/usr/bin/env node

/**
 * Execute Backfill via SQLite MCP
 *
 * Reads backfill_safe.sql and outputs individual INSERT statements
 * for execution via Claude Code's SQLite MCP integration
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const SQL_FILE = path.join(PROJECT_ROOT, 'data/backfill_safe.sql');

function main() {
    const sql = fs.readFileSync(SQL_FILE, 'utf-8');

    // Extract all INSERT OR IGNORE statements
    const statements = [];
    const regex = /INSERT OR IGNORE INTO[\s\S]*?\);/g;
    let match;

    while ((match = regex.exec(sql)) !== null) {
        statements.push(match[0]);
    }

    // Output statements as JSON array for easy parsing (no console logs)
    console.log(JSON.stringify(statements, null, 2));
}

main();
