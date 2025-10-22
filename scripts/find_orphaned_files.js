/**
 * Find files in units directory that are NOT in WORKFLOW_STATE.json
 */

const fs = require('fs');
const path = require('path');

const state = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf-8'));
const completedSet = new Set(state.completed);

const unitsDir = 'data/output/units';
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

console.log(`Files in directory: ${files.length}`);
console.log(`IDs in WORKFLOW_STATE: ${completedSet.size}\n`);

const orphaned = [];

files.forEach(filename => {
    const canonicalId = filename.replace('_toe.json', '');
    if (!completedSet.has(canonicalId)) {
        orphaned.push(filename);
    }
});

if (orphaned.length > 0) {
    console.log(`Found ${orphaned.length} orphaned files (in directory but NOT in WORKFLOW_STATE):\n`);
    orphaned.forEach(f => console.log(`  - ${f}`));
} else {
    console.log('✅ All files are tracked in WORKFLOW_STATE.json');
}
