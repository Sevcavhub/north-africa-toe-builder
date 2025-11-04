const Database = require('better-sqlite3');
const db = new Database('database/master_database.db');

// Sample specs from enriched items
const samples = db.prepare(`
  SELECT
    em.master_id,
    em.display_name,
    em.confidence_score,
    em.historical_specs_json
  FROM equipment_master_new em
  JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
  WHERE etu.theater = 'north_africa'
  AND em.historical_specs_json IS NOT NULL
  ORDER BY em.confidence_score DESC
  LIMIT 5
`).all();

console.log('Sample North Africa Equipment with Specs:');
samples.forEach(s => {
  console.log('\n' + s.display_name + ' (confidence: ' + s.confidence_score + ')');
  try {
    const specs = JSON.parse(s.historical_specs_json);
    console.log('  Data sources:', specs.data_sources || 'none');
    console.log('  Fields:', Object.keys(specs).slice(0, 8).join(', '));
  } catch (e) {
    console.log('  Error parsing specs');
  }
});

db.close();
