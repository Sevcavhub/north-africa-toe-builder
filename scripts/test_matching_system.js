#!/usr/bin/env node

/**
 * Test Matching System with Known Naming Variants
 *
 * Tests the new alias-aware matching library against known cases where:
 * - Seed file has abbreviated names
 * - Completed files have full official names
 * - Matching should work via aliases
 */

const fs = require('fs');
const path = require('path');
const matching = require('./lib/matching');
const naming = require('./lib/naming_standard');
const paths = require('./lib/canonical_paths');

console.log('=== TESTING NEW MATCHING SYSTEM ===\n');

// Load seed file
const seedPath = path.join(__dirname, '..', 'projects', 'north_africa_seed_units_COMPLETE.json');
const seed = JSON.parse(fs.readFileSync(seedPath, 'utf-8'));

// Load completed units
const completedSet = new Set();
const unitsDir = paths.UNITS_DIR;
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('_toe.json'));

files.forEach(filename => {
    const parsed = naming.parseFilename(filename);
    if (parsed) {
        const unitId = `${parsed.nation}_${parsed.quarter}_${parsed.designation}`;
        completedSet.add(unitId);
    }
});

console.log(`Loaded ${completedSet.size} completed units\n`);

// Test cases: Known naming variants that should match
const testCases = [
    {
        name: 'Italian 10th Army - Full official name vs abbreviated',
        nation: 'italian',
        quarter: '1940q2',
        designation: '10th Army',
        expected_match: true,
        reason: 'File has "10ª Armata (Italian 10th Army)", seed has "10th Army" in aliases'
    },
    {
        name: 'British 78th Infantry Division - Nickname variant',
        nation: 'british',
        quarter: '1942q4',
        designation: '78th Infantry Division',
        expected_match: true,
        reason: 'File has "78th Infantry Division \'Battleaxe\'", seed has "78th Infantry Division" in aliases'
    },
    {
        name: 'German DAK - Abbreviation',
        nation: 'german',
        quarter: '1941q1',
        designation: 'Deutsches Afrikakorps',
        expected_match: true,
        reason: 'File has "Deutsches Afrikakorps (DAK)", seed has aliases for both forms'
    },
    {
        name: 'British 4th Indian Division - Missing "Infantry"',
        nation: 'british',
        quarter: '1941q1',
        designation: '4th Indian Division',
        expected_match: true,
        reason: 'File has "4th Indian Infantry Division", seed has "4th Indian Division" - partial match'
    },
    {
        name: 'Non-existent unit - Should NOT match',
        nation: 'german',
        quarter: '1943q1',
        designation: 'Fake Division That Does Not Exist',
        expected_match: false,
        reason: 'Unit does not exist in completed files'
    },
    {
        name: 'Wrong quarter - Should NOT match',
        nation: 'german',
        quarter: '1940q1',
        designation: '15. Panzer-Division',
        expected_match: false,
        reason: '15. Panzer-Division exists but not in 1940-Q1'
    }
];

// Run test cases
let passed = 0;
let failed = 0;

testCases.forEach(test => {
    console.log(`\n📋 Test: ${test.name}`);
    console.log(`   Nation: ${test.nation}`);
    console.log(`   Quarter: ${test.quarter}`);
    console.log(`   Designation: ${test.designation}`);
    console.log(`   Expected: ${test.expected_match ? 'MATCH' : 'NO MATCH'}`);
    console.log(`   Reason: ${test.reason}`);

    // Get aliases from seed file
    const nationMap = {
        german: 'german_units',
        italian: 'italian_units',
        british: 'british_units',
        american: 'usa_units',
        french: 'french_units'
    };

    let aliases = [];
    const seedKey = nationMap[test.nation];
    if (seed[seedKey]) {
        const unit = seed[seedKey].find(u => {
            const normalized = matching.normalizeDesignation(u.designation);
            const testNormalized = matching.normalizeDesignation(test.designation);
            return normalized === testNormalized || (u.aliases || []).some(a =>
                matching.normalizeDesignation(a) === testNormalized
            );
        });
        if (unit) {
            aliases = unit.aliases || [];
        }
    }

    const result = matching.isUnitCompleted(
        test.nation,
        test.quarter,
        test.designation,
        aliases,
        completedSet
    );

    const success = result === test.expected_match;
    console.log(`   Result: ${result ? 'MATCH' : 'NO MATCH'} - ${success ? '✅ PASS' : '❌ FAIL'}`);

    if (success) {
        passed++;
    } else {
        failed++;

        // Debug: Show what files exist for this nation/quarter
        const prefix = `${test.nation}_${test.quarter}_`;
        const matching_files = Array.from(completedSet).filter(id => id.startsWith(prefix));
        console.log(`   Debug: Found ${matching_files.length} files for ${test.nation} ${test.quarter}`);
        if (matching_files.length > 0 && matching_files.length <= 5) {
            matching_files.forEach(f => console.log(`     - ${f}`));
        }
    }
});

console.log('\n\n=== TEST SUMMARY ===');
console.log(`✅ Passed: ${passed}/${testCases.length}`);
console.log(`❌ Failed: ${failed}/${testCases.length}`);
console.log(`Success Rate: ${Math.round((passed / testCases.length) * 100)}%`);

if (failed === 0) {
    console.log('\n🎉 All tests passed! The matching system is working correctly.\n');
} else {
    console.log('\n⚠️  Some tests failed. Review the output above for details.\n');
}

// Additional diagnostic: Show overall match rate improvement
console.log('\n=== OVERALL MATCH RATE (Seed vs Completed) ===\n');

const seedToFileMapping = matching.buildSeedToFileMapping(seed, completedSet);
const totalSeedUnits = Object.keys(seedToFileMapping).length;

let exactMatches = 0;
let aliasMatches = 0;
let partialMatches = 0;

for (const [seedId, data] of Object.entries(seedToFileMapping)) {
    if (data.matched_files.length > 0) {
        // Check if any match is exact
        const hasExact = data.matched_files.some(f => f === seedId);
        if (hasExact) {
            exactMatches++;
        } else if (data.aliases && data.aliases.length > 0) {
            aliasMatches++;
        } else {
            partialMatches++;
        }
    }
}

console.log(`Total seed unit-quarters: ${totalSeedUnits}`);
console.log(`Exact matches: ${exactMatches}`);
console.log(`Alias matches: ${aliasMatches}`);
console.log(`Partial matches: ${partialMatches}`);
console.log(`Total matches: ${exactMatches + aliasMatches + partialMatches}`);
console.log(`Match rate: ${Math.round(((exactMatches + aliasMatches + partialMatches) / totalSeedUnits) * 100)}%`);

process.exit(failed > 0 ? 1 : 0);
