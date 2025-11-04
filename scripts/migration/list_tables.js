#!/usr/bin/env node
const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '../../database/master_database.db');
const db = new Database(dbPath, { readonly: true });

console.log('=== ALL TABLES IN master_database.db ===\n');

const tables = db.prepare(`
  SELECT name, type
  FROM sqlite_master
  WHERE type='table'
  ORDER BY name
`).all();

tables.forEach(t => console.log(`  ${t.type}: ${t.name}`));

console.log(`\nTotal: ${tables.length} tables`);

// Check for equipment-related tables
console.log('\n=== EQUIPMENT-RELATED TABLES ===\n');
const equipmentTables = tables.filter(t => t.name.toLowerCase().includes('equipment') || t.name.toLowerCase().includes('afv') || t.name.toLowerCase().includes('gun') || t.name.toLowerCase().includes('bg_'));
equipmentTables.forEach(t => {
  console.log(`\n${t.name}:`);
  const count = db.prepare(`SELECT COUNT(*) as count FROM ${t.name}`).get();
  console.log(`  Rows: ${count.count}`);

  const schema = db.prepare(`PRAGMA table_info(${t.name})`).all();
  console.log(`  Columns: ${schema.map(s => s.name).join(', ')}`);
});

db.close();
