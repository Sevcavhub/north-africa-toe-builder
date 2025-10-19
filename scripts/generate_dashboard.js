#!/usr/bin/env node

/**
 * Dashboard Generator - Comprehensive Unit JSON Review
 *
 * Analyzes all completed unit JSONs and generates a dashboard report
 * showing progress, quality metrics, and compliance status.
 */

const fs = require('fs');
const path = require('path');

const UNITS_DIR = path.join(__dirname, '../data/output/units');
const CHAPTERS_DIR = path.join(__dirname, '../data/output/chapters');

// Read all unit files
const unitFiles = fs.readdirSync(UNITS_DIR).filter(f => f.endsWith('.json'));
const chapterFiles = fs.readdirSync(CHAPTERS_DIR).filter(f => f.endsWith('.md'));

console.log('════════════════════════════════════════════════════════════════════════════════');
console.log('  📊 NORTH AFRICA TO&E BUILDER - UNIT DASHBOARD');
console.log('════════════════════════════════════════════════════════════════════════════════\n');

// Overall summary
console.log('📈 **OVERALL PROGRESS**\n');
console.log(`   Total Unit JSONs: ${unitFiles.length}`);
console.log(`   Total Chapters:   ${chapterFiles.length}`);
console.log(`   Target (Phase 6): 420 unit-quarters`);
console.log(`   Completion:       ${((unitFiles.length / 420) * 100).toFixed(1)}%\n`);

// Breakdown by nation
console.log('🌍 **BREAKDOWN BY NATION**\n');
const byNation = {};
unitFiles.forEach(f => {
  const nation = f.split('_')[0];
  byNation[nation] = (byNation[nation] || 0) + 1;
});

Object.entries(byNation).sort((a, b) => b[1] - a[1]).forEach(([nation, count]) => {
  const bar = '█'.repeat(Math.floor(count / 5));
  console.log(`   ${nation.padEnd(10)}: ${count.toString().padStart(3)} ${bar}`);
});

// Breakdown by quarter
console.log('\n📅 **BREAKDOWN BY QUARTER**\n');
const byQuarter = {};
unitFiles.forEach(f => {
  const quarter = f.split('_')[1].toUpperCase();
  byQuarter[quarter] = (byQuarter[quarter] || 0) + 1;
});

const sortedQuarters = Object.entries(byQuarter).sort((a, b) => {
  // Sort by year then quarter
  const [yearA, qA] = a[0].split('Q');
  const [yearB, qB] = b[0].split('Q');
  if (yearA !== yearB) return parseInt(yearA) - parseInt(yearB);
  return parseInt(qA) - parseInt(qB);
});

sortedQuarters.forEach(([quarter, count]) => {
  const bar = '█'.repeat(Math.floor(count / 2));
  console.log(`   ${quarter}: ${count.toString().padStart(3)} ${bar}`);
});

// Sample detailed analysis (read first 10 files)
console.log('\n🔍 **QUALITY METRICS** (sample of 10 units)\n');

const sampleFiles = unitFiles.slice(0, 10);
const issues = {
  missingCommander: 0,
  lowConfidence: 0,
  missingSupply: 0,
  missingWeather: 0,
  invalidSchema: 0,
  total: 0
};

sampleFiles.forEach((file, idx) => {
  try {
    const unitPath = path.join(UNITS_DIR, file);
    const unit = JSON.parse(fs.readFileSync(unitPath, 'utf-8'));

    // Check for common issues
    if (!unit.commander || !unit.commander.name) {
      issues.missingCommander++;
    }

    if (unit.metadata && unit.metadata.confidence_score < 75) {
      issues.lowConfidence++;
    }

    if (!unit.supply_status && !unit.logistics) {
      issues.missingSupply++;
    }

    if (!unit.weather && !unit.environmental_conditions) {
      issues.missingWeather++;
    }

    issues.total++;

  } catch (err) {
    issues.invalidSchema++;
    console.log(`   ⚠️  ${file}: Parse error - ${err.message}`);
  }
});

console.log(`   Missing Commander:     ${issues.missingCommander}/${issues.total} (${((issues.missingCommander/issues.total)*100).toFixed(0)}%)`);
console.log(`   Low Confidence (<75%): ${issues.lowConfidence}/${issues.total} (${((issues.lowConfidence/issues.total)*100).toFixed(0)}%)`);
console.log(`   Missing Supply Data:   ${issues.missingSupply}/${issues.total} (${((issues.missingSupply/issues.total)*100).toFixed(0)}%)`);
console.log(`   Missing Weather Data:  ${issues.missingWeather}/${issues.total} (${((issues.missingWeather/issues.total)*100).toFixed(0)}%)`);
console.log(`   Schema Parse Errors:   ${issues.invalidSchema}/${issues.total} (${((issues.invalidSchema/issues.total)*100).toFixed(0)}%)`);

// Recent completions
console.log('\n⏰ **RECENT COMPLETIONS** (last 10 by modification time)\n');
const recentFiles = unitFiles
  .map(f => ({
    name: f,
    time: fs.statSync(path.join(UNITS_DIR, f)).mtime
  }))
  .sort((a, b) => b.time - a.time)
  .slice(0, 10);

recentFiles.forEach((file, idx) => {
  const date = file.time.toLocaleDateString();
  const time = file.time.toLocaleTimeString();
  console.log(`   ${(idx+1).toString().padStart(2)}. ${file.name.replace('_toe.json', '')} (${date} ${time})`);
});

// Chapter matching
console.log('\n📖 **CHAPTER GENERATION STATUS**\n');
const unitsWithChapters = unitFiles.filter(f => {
  const chapterName = f.replace('_toe.json', '.md').replace(/^(.*)$/, 'chapter_$1');
  return chapterFiles.includes(chapterName);
}).length;

console.log(`   Units with Chapters:   ${unitsWithChapters}/${unitFiles.length} (${((unitsWithChapters/unitFiles.length)*100).toFixed(1)}%)`);
console.log(`   Missing Chapters:      ${unitFiles.length - unitsWithChapters}`);

// Units without chapters
if (unitFiles.length - unitsWithChapters > 0) {
  console.log('\n   Units missing chapters (first 10):');
  let count = 0;
  for (const file of unitFiles) {
    const chapterName = file.replace('_toe.json', '.md').replace(/^(.*)$/, 'chapter_$1');
    if (!chapterFiles.includes(chapterName)) {
      console.log(`      - ${file.replace('_toe.json', '')}`);
      count++;
      if (count >= 10) break;
    }
  }
}

// Top priorities based on PROJECT_SCOPE.md
console.log('\n🎯 **PRIORITIES FROM PROJECT_SCOPE.md**\n');
console.log('   Priority 1: Italian Units (11.5% complete - largest gap)');
console.log('   Priority 2: French Units (15.8% complete)');
console.log('   Priority 3: British Corps/Army Formations (large formations at 0%)');
console.log('   Priority 4: German Tunisia Campaign (late war gaps)');

console.log('\n════════════════════════════════════════════════════════════════════════════════');
console.log('📝 Dashboard generated: ' + new Date().toLocaleString());
console.log('════════════════════════════════════════════════════════════════════════════════\n');
