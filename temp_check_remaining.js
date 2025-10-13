const fs = require('fs');

const state = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf8'));
const project = JSON.parse(fs.readFileSync('projects/north_africa_campaign.json', 'utf8'));

// Get all units from project
const allUnits = project.quarters.flatMap(q =>
  q.units.map(u => {
    const nation = u.nation.toLowerCase();
    const quarter = q.quarter.toLowerCase().replace('-', '--');
    const designation = u.designation.toLowerCase().replace(/[^a-z0-9]+/g, '_');
    return `${nation}_${quarter}_${designation}`;
  })
);

// Find remaining units
const remaining = allUnits.filter(u => !state.completed.includes(u));

console.log('Total project units:', allUnits.length);
console.log('Completed in WORKFLOW_STATE:', state.completed.length);
console.log('Remaining:', remaining.length);
console.log('\nNext 10 remaining units:');
remaining.slice(0, 10).forEach((u, i) => console.log(`  ${i+1}. ${u}`));
