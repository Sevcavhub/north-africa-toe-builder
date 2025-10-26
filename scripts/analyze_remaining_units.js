#!/usr/bin/env node

/**
 * Analyze Remaining Units
 *
 * Shows exactly which units remain to be extracted,
 * categorized by type and grouped by quarter
 */

const fs = require('fs');
const path = require('path');
const naming = require('./lib/naming_standard');

const PROJECT_ROOT = path.join(__dirname, '..');
const SEED_FILE = path.join(PROJECT_ROOT, 'projects/north_africa_seed_units_COMPLETE.json');
const STATE_FILE = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');

async function main() {
    // Load seed file
    const seedData = JSON.parse(fs.readFileSync(SEED_FILE, 'utf-8'));

    // Load completed units
    const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
    const completedSet = new Set(state.completed);

    // Extract all unit-quarters from seed
    const allUnits = [];

    for (const [nationKey, units] of Object.entries(seedData)) {
        if (!nationKey.endsWith('_units') || !Array.isArray(units)) continue;

        const nation = naming.NATION_MAP[nationKey];
        if (!nation) continue;

        for (const unit of units) {
            for (const quarter of unit.quarters) {
                const canonicalId = `${nation}_${naming.normalizeQuarter(quarter)}_${naming.normalizeDesignation(unit.designation)}`;

                const isCompleted = completedSet.has(canonicalId);

                allUnits.push({
                    nation: nation,
                    quarter: quarter,
                    designation: unit.designation,
                    type: unit.type,
                    canonicalId: canonicalId,
                    completed: isCompleted
                });
            }
        }
    }

    // Filter to only pending units
    const pending = allUnits.filter(u => !u.completed);

    // Categorize by type
    const divisions = pending.filter(u =>
        u.type.toLowerCase().includes('division') &&
        !u.type.toLowerCase().includes('corps') &&
        !u.type.toLowerCase().includes('army')
    );

    const brigades = pending.filter(u =>
        u.type.toLowerCase().includes('brigade') ||
        u.type.toLowerCase().includes('column')
    );

    const corps = pending.filter(u => u.type.toLowerCase().includes('corps'));
    const armies = pending.filter(u => u.type.toLowerCase().includes('army'));
    const other = pending.filter(u =>
        !divisions.includes(u) &&
        !brigades.includes(u) &&
        !corps.includes(u) &&
        !armies.includes(u)
    );

    console.log('');
    console.log('REMAINING UNITS ANALYSIS');
    console.log('='.repeat(80));
    console.log('');
    console.log('Total pending:', pending.length);
    console.log('  Combat Units (Divisions + Brigades):', divisions.length + brigades.length);
    console.log('    - Divisions:', divisions.length);
    console.log('    - Brigades:', brigades.length);
    console.log('  Aggregates (Corps + Armies):', corps.length + armies.length);
    console.log('    - Corps:', corps.length);
    console.log('    - Armies:', armies.length);
    if (other.length > 0) {
        console.log('  Other:', other.length);
    }
    console.log('');
    console.log('='.repeat(80));
    console.log('');

    // Group by quarter for display
    function groupByQuarter(units) {
        const byQuarter = {};
        for (const u of units) {
            if (!byQuarter[u.quarter]) byQuarter[u.quarter] = [];
            byQuarter[u.quarter].push(u);
        }
        return byQuarter;
    }

    // Show divisions (combat units)
    if (divisions.length > 0) {
        console.log('DIVISIONS (Combat Units - Extract First):');
        console.log('');
        const byQuarter = groupByQuarter(divisions);
        const quarters = Object.keys(byQuarter).sort();

        for (const quarter of quarters) {
            console.log(`  ${quarter} (${byQuarter[quarter].length} divisions):`);
            byQuarter[quarter].forEach(u => {
                console.log(`    - ${u.nation.toUpperCase().padEnd(8)} ${u.designation}`);
            });
            console.log('');
        }
    }

    // Show brigades
    if (brigades.length > 0) {
        console.log('BRIGADES/COLUMNS (Combat Units):');
        console.log('');
        const byQuarter = groupByQuarter(brigades);
        const quarters = Object.keys(byQuarter).sort();

        for (const quarter of quarters) {
            console.log(`  ${quarter} (${byQuarter[quarter].length} brigades):`);
            byQuarter[quarter].forEach(u => {
                console.log(`    - ${u.nation.toUpperCase().padEnd(8)} ${u.designation}`);
            });
            console.log('');
        }
    }

    // Show corps
    if (corps.length > 0) {
        console.log('CORPS (Aggregates - Extract After Divisions):');
        console.log('');
        const byQuarter = groupByQuarter(corps);
        const quarters = Object.keys(byQuarter).sort();

        for (const quarter of quarters) {
            console.log(`  ${quarter} (${byQuarter[quarter].length} corps):`);
            byQuarter[quarter].forEach(u => {
                console.log(`    - ${u.nation.toUpperCase().padEnd(8)} ${u.designation}`);
            });
            console.log('');
        }
    }

    // Show armies
    if (armies.length > 0) {
        console.log('ARMIES (Aggregates - Extract Last):');
        console.log('');
        const byQuarter = groupByQuarter(armies);
        const quarters = Object.keys(byQuarter).sort();

        for (const quarter of quarters) {
            console.log(`  ${quarter} (${byQuarter[quarter].length} armies):`);
            byQuarter[quarter].forEach(u => {
                console.log(`    - ${u.nation.toUpperCase().padEnd(8)} ${u.designation}`);
            });
            console.log('');
        }
    }

    // Output JSON for queue creation
    const queueData = {
        generated: new Date().toISOString(),
        total_pending: pending.length,
        combat_units_count: divisions.length + brigades.length,
        aggregates_count: corps.length + armies.length,
        divisions: divisions.map(u => ({
            nation: u.nation,
            quarter: u.quarter,
            designation: u.designation,
            type: u.type,
            canonical_id: u.canonicalId
        })),
        brigades: brigades.map(u => ({
            nation: u.nation,
            quarter: u.quarter,
            designation: u.designation,
            type: u.type,
            canonical_id: u.canonicalId
        })),
        corps: corps.map(u => ({
            nation: u.nation,
            quarter: u.quarter,
            designation: u.designation,
            type: u.type,
            canonical_id: u.canonicalId
        })),
        armies: armies.map(u => ({
            nation: u.nation,
            quarter: u.quarter,
            designation: u.designation,
            type: u.type,
            canonical_id: u.canonicalId
        }))
    };

    const outputPath = path.join(PROJECT_ROOT, 'remaining_units_analysis.json');
    fs.writeFileSync(outputPath, JSON.stringify(queueData, null, 2));

    console.log('');
    console.log('='.repeat(80));
    console.log('');
    console.log(`✅ Analysis complete`);
    console.log(`📝 JSON data written to: remaining_units_analysis.json`);
    console.log('');
}

main().catch(error => {
    console.error('Error:', error);
    process.exit(1);
});
