#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

async function main() {
    // Read WORKFLOW_STATE
    const workflowPath = path.join(process.cwd(), 'WORKFLOW_STATE.json');
    const workflow = JSON.parse(await fs.readFile(workflowPath, 'utf-8'));
    const tracked = new Set(workflow.completed);

    // Read actual files
    const unitsDir = path.join(process.cwd(), 'data', 'output', 'units');
    const actualFiles = (await fs.readdir(unitsDir))
        .filter(f => f.endsWith('_toe.json'))
        .map(f => f.replace('_toe.json', ''));

    // Find untracked
    const untracked = actualFiles.filter(f => !tracked.has(f));

    console.log(`Tracked in WORKFLOW_STATE: ${tracked.size}`);
    console.log(`Actual files: ${actualFiles.length}`);
    console.log(`Untracked files: ${untracked.length}\n`);

    if (untracked.length > 0) {
        console.log('Files not in WORKFLOW_STATE.json:');
        untracked.forEach((f, i) => console.log(`${i + 1}. ${f}`));
    }
}

main().catch(console.error);
