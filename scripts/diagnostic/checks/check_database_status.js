#!/usr/bin/env node

/**
 * Check Database Status - Quick status check for master_database.db
 */

const Database = require('better-sqlite3');
const path = require('path');

const DB_PATH = path.join(__dirname, '../database/master_database.db');

try {
    const db = new Database(DB_PATH, { readonly: true });

    console.log('\n=== DATABASE STATUS CHECK ===\n');

    // Get all tables
    const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
    console.log('📊 Tables in database:', tables.map(t => t.name).join(', '));
    console.log('');

    // Check each major table
    const checks = [
        { table: 'units', description: 'Ground units' },
        { table: 'equipment', description: 'WITW equipment items' },
        { table: 'guns', description: 'Gun specifications' },
        { table: 'aircraft', description: 'Aircraft specifications' },
        { table: 'match_reviews', description: 'Equipment matches' }
    ];

    for (const check of checks) {
        try {
            const count = db.prepare(`SELECT COUNT(*) as count FROM ${check.table}`).get();
            console.log(`✓ ${check.table.padEnd(20)} ${count.count.toString().padStart(5)} rows (${check.description})`);
        } catch (e) {
            console.log(`✗ ${check.table.padEnd(20)} ERROR: ${e.message}`);
        }
    }

    console.log('');

    // Sample a few units to see what's in there
    console.log('📋 Sample units in database:');
    const sampleUnits = db.prepare('SELECT unit_id, nation, quarter FROM units LIMIT 5').all();
    sampleUnits.forEach(u => {
        console.log(`   - ${u.unit_id} (${u.nation}, ${u.quarter})`);
    });

    // Check nation distribution
    console.log('');
    console.log('🌍 Unit distribution by nation:');
    const nationDist = db.prepare('SELECT nation, COUNT(*) as count FROM units GROUP BY nation ORDER BY count DESC').all();
    nationDist.forEach(n => {
        console.log(`   - ${n.nation.padEnd(15)} ${n.count.toString().padStart(3)} units`);
    });

    db.close();
    console.log('\n✅ Database check complete\n');
} catch (error) {
    console.error('❌ Error checking database:', error.message);
    process.exit(1);
}
