#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('═'.repeat(80));
console.log('INVESTIGATING "OUT-OF-SCOPE" UNITS');
console.log('═'.repeat(80));
console.log();

// Load canonical matching report
const matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf-8'));

// Get all matched canonical IDs
const matchedIds = new Set();
matchingReport.matches.exact_matches.forEach(m => matchedIds.add(m.canonical_id));
matchingReport.matches.alias_matches.forEach(m => matchedIds.add(m.canonical_id));

console.log(`✅ Matched units: ${matchedIds.size}`);
console.log();

// Scan canonical directory and find unmatched files
const canonicalUnitsDir = 'data/output/units/';
const unmatchedUnits = [];

const files = fs.readdirSync(canonicalUnitsDir);
for (const file of files) {
    if (file.endsWith('_toe.json')) {
        const canonicalId = file.replace('_toe.json', '');

        if (!matchedIds.has(canonicalId)) {
            // Read the unit to get actual designation
            try {
                const filePath = path.join(canonicalUnitsDir, file);
                const unitData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

                unmatchedUnits.push({
                    file: file,
                    canonical_id: canonicalId,
                    nation: unitData.nation,
                    quarter: unitData.quarter,
                    designation: unitData.unit_designation,
                    org_level: unitData.organization_level
                });
            } catch (err) {
                console.log(`⚠️  Could not read ${file}: ${err.message}`);
            }
        }
    }
}

console.log(`❌ Unmatched units: ${unmatchedUnits.length}`);
console.log();
console.log('═'.repeat(80));
console.log('UNMATCHED UNITS (sorted by nation/quarter):');
console.log('═'.repeat(80));
console.log();

// Group by nation
const byNation = {};
unmatchedUnits.forEach(u => {
    if (!byNation[u.nation]) byNation[u.nation] = [];
    byNation[u.nation].push(u);
});

Object.keys(byNation).sort().forEach(nation => {
    console.log(`${nation.toUpperCase()} (${byNation[nation].length} units):`);
    console.log('─'.repeat(80));

    byNation[nation].sort((a, b) => {
        if (a.quarter !== b.quarter) return a.quarter.localeCompare(b.quarter);
        return a.designation.localeCompare(b.designation);
    }).forEach(u => {
        console.log(`  ${u.quarter} | ${u.designation} (${u.org_level})`);
        console.log(`    File: ${u.file}`);
        console.log(`    Canonical ID: ${u.canonical_id}`);
        console.log();
    });
});

console.log('═'.repeat(80));
console.log('ANALYSIS QUESTIONS:');
console.log('═'.repeat(80));
console.log();
console.log('For each unmatched unit, ask:');
console.log('  1. Is this unit in the complete seed?');
console.log('  2. If yes, WHY isn\'t it matching?');
console.log('     - Designation mismatch?');
console.log('     - Alias not recognized?');
console.log('     - Quarter format issue?');
console.log('  3. If no, should it be ADDED to the seed?');
console.log();
console.log('═'.repeat(80));
