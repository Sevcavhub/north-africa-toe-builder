#!/usr/bin/env node

/**
 * Execute SQLite Backfill
 *
 * Executes the backfill SQL using better-sqlite3 or sqlite3 npm package
 *
 * Usage: npm install better-sqlite3 && node scripts/execute_sqlite_backfill.js
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const SQL_FILE = path.join(PROJECT_ROOT, 'data/backfill_safe.sql');
const DB_FILE = path.join(PROJECT_ROOT, 'data/toe_database.db');

async function main() {
    console.log('\n' + '═'.repeat(80));
    console.log('  💾 EXECUTING SQL BACKFILL');
    console.log('═'.repeat(80));
    console.log('');

    // Try to load sqlite3
    let Database;
    try {
        Database = require('better-sqlite3');
        console.log('✅ Using better-sqlite3\n');
    } catch (err) {
        try {
            const sqlite3 = require('sqlite3').verbose();
            console.log('✅ Using sqlite3\n');
            return executeSqlite3(sqlite3, SQL_FILE, DB_FILE);
        } catch (err2) {
            console.error('❌ Neither better-sqlite3 nor sqlite3 is installed');
            console.error('');
            console.error('Please install one of them:');
            console.error('   npm install better-sqlite3');
            console.error('   OR');
            console.error('   npm install sqlite3');
            console.error('');
            process.exit(1);
        }
    }

    // Execute with better-sqlite3
    return executeBetterSqlite3(Database, SQL_FILE, DB_FILE);
}

function executeBetterSqlite3(Database, sqlFile, dbFile) {
    console.log(`📊 Database: ${dbFile}`);
    console.log(`📄 SQL File: ${sqlFile}\n`);

    const db = new Database(dbFile);
    const sql = fs.readFileSync(sqlFile, 'utf-8');

    // Split into individual statements - match INSERT OR IGNORE through closing );
    const statements = [];
    const regex = /INSERT OR IGNORE INTO[\s\S]*?\);/g;
    let match;
    while ((match = regex.exec(sql)) !== null) {
        statements.push(match[0]);
    }

    console.log(`📝 Found ${statements.length} INSERT statements\n`);
    console.log('⏳ Executing inserts...\n');

    let inserted = 0;
    let skipped = 0;

    db.exec('BEGIN TRANSACTION;');

    for (let i = 0; i < statements.length; i++) {
        const stmt = statements[i];
        try {
            const result = db.prepare(stmt).run();
            if (result.changes > 0) {
                inserted++;
                process.stdout.write(`✓`);
            } else {
                skipped++;
                process.stdout.write(`·`);
            }
            if ((i + 1) % 10 === 0) {
                process.stdout.write(` ${i + 1}/${statements.length}\n`);
            }
        } catch (error) {
            console.error(`\n❌ Error on statement ${i + 1}:`, error.message);
        }
    }

    db.exec('COMMIT;');
    db.close();

    console.log('\n');
    console.log('═'.repeat(80));
    console.log('  ✅ BACKFILL COMPLETE');
    console.log('═'.repeat(80));
    console.log('');
    console.log(`✓ Inserted: ${inserted} new units`);
    console.log(`· Skipped: ${skipped} existing units`);
    console.log(`📊 Total: ${statements.length} units processed`);
    console.log('');
}

function executeSqlite3(sqlite3, sqlFile, dbFile) {
    return new Promise((resolve, reject) => {
        console.log(`📊 Database: ${dbFile}`);
        console.log(`📄 SQL File: ${sqlFile}\n`);

        const db = new sqlite3.Database(dbFile);
        const sql = fs.readFileSync(sqlFile, 'utf-8');

        const statements = sql
            .split(/;\s*\n/)
            .filter(s => s.trim().startsWith('INSERT OR IGNORE'))
            .map(s => s.trim() + ';');

        console.log(`📝 Found ${statements.length} INSERT statements\n`);
        console.log('⏳ Executing inserts...\n');

        let inserted = 0;
        let skipped = 0;
        let completed = 0;

        db.serialize(() => {
            db.run('BEGIN TRANSACTION;');

            statements.forEach((stmt, i) => {
                db.run(stmt, function(err) {
                    completed++;
                    if (err) {
                        console.error(`\n❌ Error on statement ${i + 1}:`, err.message);
                    } else {
                        if (this.changes > 0) {
                            inserted++;
                            process.stdout.write(`✓`);
                        } else {
                            skipped++;
                            process.stdout.write(`·`);
                        }
                        if ((i + 1) % 10 === 0) {
                            process.stdout.write(` ${i + 1}/${statements.length}\n`);
                        }
                    }

                    if (completed === statements.length) {
                        db.run('COMMIT;', () => {
                            db.close();
                            console.log('\n');
                            console.log('═'.repeat(80));
                            console.log('  ✅ BACKFILL COMPLETE');
                            console.log('═'.repeat(80));
                            console.log('');
                            console.log(`✓ Inserted: ${inserted} new units`);
                            console.log(`· Skipped: ${skipped} existing units`);
                            console.log(`📊 Total: ${statements.length} units processed`);
                            console.log('');
                            resolve();
                        });
                    }
                });
            });
        });
    });
}

main().catch(error => {
    console.error('❌ Error:', error.message);
    process.exit(1);
});
