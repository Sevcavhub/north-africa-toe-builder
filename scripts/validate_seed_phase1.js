#!/usr/bin/env node

/**
 * Phase 1.1: Analyze Completed Canonical Units
 *
 * Purpose: Analyze all 152 completed units in data/output/units/ to:
 * - Identify what nations, quarters, unit types are represented
 * - Extract deployment information (when units arrived/departed Africa)
 * - Document battle participation
 * - Identify patterns for seed file validation
 *
 * Output: Analysis JSON for seed validation
 */

const fs = require('fs');
const path = require('path');

// Canonical unit directory
const CANONICAL_DIR = 'data/output/units';

// Helper: Read JSON file safely
function readJSON(filePath) {
    try {
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (err) {
        console.error(`Error reading ${filePath}:`, err.message);
        return null;
    }
}

// Helper: Extract deployment dates from unit JSON
function extractDeploymentInfo(unitData) {
    const info = {
        arrived_africa: null,
        departed_africa: null,
        location: null,
        battles: []
    };

    // Check headquarters_location for Africa references
    if (unitData.command?.headquarters_location) {
        const hq = unitData.command.headquarters_location.toLowerCase();
        if (hq.includes('libya') || hq.includes('egypt') || hq.includes('tunisia') ||
            hq.includes('tripoli') || hq.includes('tobruk') || hq.includes('benghazi') ||
            hq.includes('africa')) {
            info.location = unitData.command.headquarters_location;
        }
    }

    // Extract battles from historical_engagements
    if (unitData.validation?.historical_engagements) {
        info.battles = unitData.validation.historical_engagements;
    }

    return info;
}

// Main analysis
async function analyzeCompletedUnits() {
    console.log('='.repeat(80));
    console.log('PHASE 1.1: ANALYZING COMPLETED CANONICAL UNITS');
    console.log('='.repeat(80));
    console.log();

    // Step 1: Get all canonical unit files
    console.log('Step 1: Loading canonical unit files...');
    const canonicalFiles = fs.readdirSync(CANONICAL_DIR)
        .filter(f => f.endsWith('_toe.json'))
        .sort();

    console.log(`  Found ${canonicalFiles.length} unit files`);
    console.log();

    // Step 2: Parse each unit and extract metadata
    console.log('Step 2: Extracting unit metadata...');
    const units = [];
    let successCount = 0;
    let failCount = 0;

    for (const fileName of canonicalFiles) {
        const filePath = path.join(CANONICAL_DIR, fileName);
        const unitData = readJSON(filePath);

        if (!unitData) {
            failCount++;
            continue;
        }

        const deployment = extractDeploymentInfo(unitData);

        units.push({
            file_name: fileName,
            unit_id: fileName.replace('_toe.json', ''),
            nation: unitData.nation || 'unknown',
            quarter: unitData.quarter || 'unknown',
            unit_designation: unitData.unit_designation || 'unknown',
            unit_type: unitData.organizational_level || 'unknown',
            commander: unitData.command?.supreme_commander || 'unknown',
            deployment: deployment,
            in_africa: !!deployment.location,
            has_battles: deployment.battles.length > 0
        });

        successCount++;
    }

    console.log(`  Successfully parsed: ${successCount}`);
    console.log(`  Failed to parse: ${failCount}`);
    console.log();

    // Step 3: Analyze by nation
    console.log('Step 3: Analyzing by nation...');
    const byNation = {};
    for (const unit of units) {
        if (!byNation[unit.nation]) {
            byNation[unit.nation] = [];
        }
        byNation[unit.nation].push(unit);
    }

    console.log('  Nation breakdown:');
    for (const [nation, unitList] of Object.entries(byNation)) {
        const uniqueUnits = new Set(unitList.map(u => u.unit_designation)).size;
        const inAfrica = unitList.filter(u => u.in_africa).length;
        const withBattles = unitList.filter(u => u.has_battles).length;

        console.log(`    ${nation}: ${unitList.length} unit-quarters, ${uniqueUnits} unique units`);
        console.log(`      - In Africa: ${inAfrica} (${(inAfrica/unitList.length*100).toFixed(1)}%)`);
        console.log(`      - With battles: ${withBattles} (${(withBattles/unitList.length*100).toFixed(1)}%)`);
    }
    console.log();

    // Step 4: Analyze by quarter
    console.log('Step 4: Analyzing by quarter...');
    const byQuarter = {};
    for (const unit of units) {
        if (!byQuarter[unit.quarter]) {
            byQuarter[unit.quarter] = [];
        }
        byQuarter[unit.quarter].push(unit);
    }

    console.log('  Quarter coverage:');
    const sortedQuarters = Object.keys(byQuarter).sort();
    for (const quarter of sortedQuarters) {
        const unitCount = byQuarter[quarter].length;
        console.log(`    ${quarter}: ${unitCount} units`);
    }
    console.log();

    // Step 5: Identify unique units across all quarters
    console.log('Step 5: Identifying unique units...');
    const uniqueUnitsByNation = {};

    for (const [nation, unitList] of Object.entries(byNation)) {
        const uniqueDesignations = [...new Set(unitList.map(u => u.unit_designation))].sort();
        uniqueUnitsByNation[nation] = uniqueDesignations;

        console.log(`  ${nation}: ${uniqueDesignations.length} unique units`);
        for (const designation of uniqueDesignations) {
            const quarters = unitList
                .filter(u => u.unit_designation === designation)
                .map(u => u.quarter)
                .sort();
            console.log(`    - ${designation}: ${quarters.join(', ')}`);
        }
        console.log();
    }

    // Step 6: Check Africa deployment
    console.log('Step 6: Africa deployment check...');
    const notInAfrica = units.filter(u => !u.in_africa);
    if (notInAfrica.length > 0) {
        console.log(`  ⚠️ WARNING: ${notInAfrica.length} units have no Africa location in HQ field:`);
        for (const unit of notInAfrica.slice(0, 10)) {
            console.log(`    - ${unit.unit_id}`);
        }
        if (notInAfrica.length > 10) {
            console.log(`    ... and ${notInAfrica.length - 10} more`);
        }
    } else {
        console.log(`  ✅ All units show Africa deployment`);
    }
    console.log();

    // Step 7: Generate analysis report
    console.log('Step 7: Generating analysis report...');
    const report = {
        analysis_date: new Date().toISOString(),
        total_units: units.length,
        summary: {
            by_nation: Object.entries(byNation).map(([nation, unitList]) => ({
                nation,
                unit_quarters: unitList.length,
                unique_units: new Set(unitList.map(u => u.unit_designation)).size,
                in_africa: unitList.filter(u => u.in_africa).length,
                with_battles: unitList.filter(u => u.has_battles).length
            })),
            by_quarter: Object.entries(byQuarter).map(([quarter, unitList]) => ({
                quarter,
                unit_count: unitList.length
            })).sort((a, b) => a.quarter.localeCompare(b.quarter)),
            unique_units_by_nation: uniqueUnitsByNation
        },
        units: units,
        not_in_africa: notInAfrica.map(u => ({
            unit_id: u.unit_id,
            designation: u.unit_designation,
            quarter: u.quarter,
            nation: u.nation
        }))
    };

    // Write report
    const reportPath = 'data/output/COMPLETED_UNITS_ANALYSIS.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`  ✅ Report written to: ${reportPath}`);
    console.log();

    // Step 8: Print summary
    console.log('='.repeat(80));
    console.log('SUMMARY');
    console.log('='.repeat(80));
    console.log();
    console.log(`Total unit-quarters: ${units.length}`);
    console.log(`Total unique units: ${Object.values(uniqueUnitsByNation).flat().length}`);
    console.log();
    console.log('By Nation:');
    for (const [nation, unitList] of Object.entries(byNation)) {
        console.log(`  ${nation}: ${uniqueUnitsByNation[nation].length} unique units, ${unitList.length} unit-quarters`);
    }
    console.log();
    console.log(`Units in Africa: ${units.filter(u => u.in_africa).length}/${units.length} (${(units.filter(u => u.in_africa).length/units.length*100).toFixed(1)}%)`);
    console.log(`Units with battles: ${units.filter(u => u.has_battles).length}/${units.length} (${(units.filter(u => u.has_battles).length/units.length*100).toFixed(1)}%)`);
    console.log();
    console.log('Next: Search Nafziger Collection for North Africa units');
    console.log('='.repeat(80));
}

// Run analysis
analyzeCompletedUnits().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
