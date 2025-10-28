#!/usr/bin/env node

/**
 * Batch regenerate all chapters with hardcoded conclusion bug
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Find all chapters with the hardcoded conclusion
const chaptersDir = path.join(__dirname, '..', 'data', 'output', 'chapters');
const unitsDir = path.join(__dirname, '..', 'data', 'output', 'units');

const files = fs.readdirSync(chaptersDir);
const affectedChapters = [];

for (const file of files) {
  if (!file.endsWith('.md')) continue;

  const content = fs.readFileSync(path.join(chaptersDir, file), 'utf8');
  if (content.includes('Italian XX Corpo d\'Armata Motorizzato in Q2 1941')) {
    affectedChapters.push(file);
  }
}

console.log(`Found ${affectedChapters.length} chapters with hardcoded conclusion bug`);
console.log('='.repeat(80));

let success = 0;
let failed = 0;
const failures = [];

for (const chapter of affectedChapters) {
  // Extract nation, quarter, designation from filename
  // Format: chapter_{nation}_{quarter}_{designation}.md
  const match = chapter.match(/^chapter_([a-z]+)_([0-9]{4}q[0-9])_(.+)\.md$/);

  if (!match) {
    console.log(`❌ SKIP: Could not parse filename: ${chapter}`);
    failed++;
    failures.push({ chapter, reason: 'Parse error' });
    continue;
  }

  const [, nation, quarter, designation] = match;

  // Check if unit file exists
  const unitFile = `${nation}_${quarter}_${designation}_toe.json`;
  const unitPath = path.join(unitsDir, unitFile);

  if (!fs.existsSync(unitPath)) {
    console.log(`❌ SKIP: Unit file not found: ${unitFile}`);
    failed++;
    failures.push({ chapter, reason: 'Unit file not found' });
    continue;
  }

  try {
    // Run generation
    const cmd = `node scripts/generate_single_chapter.js ${nation} ${quarter} ${designation}`;
    execSync(cmd, { cwd: path.join(__dirname, '..'), stdio: 'pipe' });
    console.log(`✅ ${chapter}`);
    success++;
  } catch (error) {
    console.log(`❌ FAILED: ${chapter}`);
    console.log(`   Error: ${error.message}`);
    failed++;
    failures.push({ chapter, reason: error.message });
  }
}

console.log('='.repeat(80));
console.log(`\nSUMMARY:`);
console.log(`  Success: ${success}`);
console.log(`  Failed: ${failed}`);
console.log(`  Total: ${affectedChapters.length}`);

if (failures.length > 0) {
  console.log(`\nFAILURES:`);
  for (const fail of failures) {
    console.log(`  - ${fail.chapter}: ${fail.reason}`);
  }
}
