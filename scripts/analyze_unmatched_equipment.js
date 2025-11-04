const Database = require('better-sqlite3');
const db = new Database('database/master_database.db');

console.log('=' .repeat(80));
console.log('UNMATCHED EQUIPMENT ANALYSIS');
console.log('=' .repeat(80));

// Get unmatched items by category
const unmatchedByCategory = db.prepare(`
  SELECT
    em.equipment_category,
    COUNT(*) as count,
    GROUP_CONCAT(em.display_name, ' | ') as sample_names
  FROM equipment_master_new em
  WHERE (em.historical_specs_json IS NULL OR em.historical_specs_json = '{}')
     OR NOT EXISTS (
       SELECT 1 FROM json_each(em.historical_specs_json, '$.data_sources')
     )
  GROUP BY em.equipment_category
  ORDER BY count DESC
`).all();

console.log('\nUnmatched Items by Category:');
console.log('-'.repeat(80));
unmatchedByCategory.forEach(cat => {
  console.log(`\n${cat.equipment_category}: ${cat.count} items`);
  const samples = cat.sample_names.split(' | ').slice(0, 5);
  samples.forEach(s => console.log(`  - ${s}`));
  if (cat.sample_names.split(' | ').length > 5) {
    console.log(`  ... and ${cat.sample_names.split(' | ').length - 5} more`);
  }
});

// Get North Africa unmatched
const naUnmatched = db.prepare(`
  SELECT
    em.equipment_category,
    COUNT(*) as count
  FROM equipment_master_new em
  JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
  WHERE etu.theater = 'north_africa'
  AND (
    NOT EXISTS (
      SELECT 1 FROM json_each(em.historical_specs_json, '$.data_sources')
    )
    OR json_array_length(json_extract(em.historical_specs_json, '$.data_sources')) = 0
  )
  GROUP BY em.equipment_category
  ORDER BY count DESC
`).all();

console.log('\n' + '='.repeat(80));
console.log('NORTH AFRICA UNMATCHED (Need Reverse Engineering):');
console.log('='.repeat(80));
naUnmatched.forEach(cat => {
  console.log(`${cat.equipment_category}: ${cat.count} items`);
});

// Check reference database sizes
console.log('\n' + '='.repeat(80));
console.log('REFERENCE DATABASE SIZES:');
console.log('='.repeat(80));

const bgVehicles = db.prepare('SELECT COUNT(*) as count FROM bg_reference_vehicles').get();
console.log(`bg_reference_vehicles: ${bgVehicles.count} items`);

const wwiitanks = db.prepare('SELECT COUNT(*) as count FROM wwiitanks_afv_data').get();
console.log(`wwiitanks_afv_data: ${wwiitanks.count} items`);

const onwar = db.prepare('SELECT COUNT(*) as count FROM afv_data').get();
console.log(`afv_data (OnWar): ${onwar.count} items`);

const bgGuns = db.prepare('SELECT COUNT(*) as count FROM bg_reference_guns').get();
console.log(`bg_reference_guns: ${bgGuns.count} items`);

console.log(`\nTotal reference items: ${bgVehicles.count + wwiitanks.count + onwar.count + bgGuns.count}`);

// Get matched vs total by category
const matchRates = db.prepare(`
  SELECT
    em.equipment_category,
    COUNT(*) as total,
    SUM(CASE WHEN json_array_length(json_extract(em.historical_specs_json, '$.data_sources')) > 0 THEN 1 ELSE 0 END) as matched,
    ROUND(100.0 * SUM(CASE WHEN json_array_length(json_extract(em.historical_specs_json, '$.data_sources')) > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) as match_pct
  FROM equipment_master_new em
  GROUP BY em.equipment_category
  ORDER BY match_pct DESC
`).all();

console.log('\n' + '='.repeat(80));
console.log('MATCH RATES BY CATEGORY:');
console.log('='.repeat(80));
matchRates.forEach(cat => {
  console.log(`${cat.equipment_category}: ${cat.matched}/${cat.total} (${cat.match_pct}%)`);
});

db.close();
