#!/usr/bin/env node

/**
 * Phase 1.3: Cross-Reference Seed File Against Authoritative Sources
 *
 * Purpose: Validate seed file units against:
 * 1. Nafziger Collection North Africa Index (205 entries, 1939-1942)
 * 2. Completed canonical units (152 files, 85 unique units)
 * 3. PROJECT_SCOPE.md "Modified Hybrid" criteria
 *
 * Output: Validation report with recommendations
 */

const fs = require('fs');
const path = require('path');

// Load all source data
const seedFile = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));
const nafzigerIndex = JSON.parse(fs.readFileSync('Resource Documents/Nafziger Collection/WWII/North_Africa_Index/NORTH_AFRICA_FILES.json', 'utf8'));
const completedAnalysis = JSON.parse(fs.readFileSync('data/output/COMPLETED_UNITS_ANALYSIS.json', 'utf8'));

console.log('='.repeat(80));
console.log('PHASE 1.3: CROSS-REFERENCE SEED FILE VALIDATION');
console.log('='.repeat(80));
console.log();

// Step 1: Extract Nafziger unit references
console.log('Step 1: Extracting Nafziger unit references...');
const nafzigerUnits = {
    german: new Set(),
    italian: new Set(),
    british: new Set(),
    french: new Set(),
    american: new Set()
};

for (const period of nafzigerIndex) {
    for (const entry of period.entries) {
        const title = entry.title.toLowerCase();

        // German units
        if (title.includes('15th panzer') || title.includes('15 panzer')) nafzigerUnits.german.add('15. Panzer-Division');
        if (title.includes('21st panzer') || title.includes('21 panzer')) nafzigerUnits.german.add('21. Panzer-Division');
        if (title.includes('5th light') || title.includes('5 light')) nafzigerUnits.german.add('5. leichte Division');
        if (title.includes('90th light') || title.includes('90 light')) nafzigerUnits.german.add('90. leichte Division');
        if (title.includes('164th light') || title.includes('164 light')) nafzigerUnits.german.add('164. leichte Division');
        if (title.includes('afrika korps') || title.includes('afrika corps')) nafzigerUnits.german.add('Deutsches Afrikakorps');
        if (title.includes('panzer army afrika') || title.includes('panzerarmee afrika')) nafzigerUnits.german.add('Panzerarmee Afrika');

        // Italian units
        if (title.includes('ariete')) nafzigerUnits.italian.add('Ariete Division');
        if (title.includes('trieste')) nafzigerUnits.italian.add('Trieste Division');
        if (title.includes('brescia')) nafzigerUnits.italian.add('Brescia Division');
        if (title.includes('bologna')) nafzigerUnits.italian.add('Bologna Division');
        if (title.includes('pavia')) nafzigerUnits.italian.add('Pavia Division');
        if (title.includes('trento')) nafzigerUnits.italian.add('Trento Division');
        if (title.includes('savona')) nafzigerUnits.italian.add('Savona Division');
        if (title.includes('littorio')) nafzigerUnits.italian.add('Littorio Division');
        if (title.includes('folgore')) nafzigerUnits.italian.add('Folgore Division');
        if (title.includes('superga')) nafzigerUnits.italian.add('Superga Division');
        if (title.includes('centauro')) nafzigerUnits.italian.add('Centauro Division');

        // British units
        if (title.includes('7th armoured') || title.includes('7 armoured')) nafzigerUnits.british.add('7th Armoured Division');
        if (title.includes('1st armoured') || title.includes('1 armoured')) nafzigerUnits.british.add('1st Armoured Division');
        if (title.includes('10th armoured') || title.includes('10 armoured')) nafzigerUnits.british.add('10th Armoured Division');
        if (title.includes('4th indian') || title.includes('4 indian')) nafzigerUnits.british.add('4th Indian Division');
        if (title.includes('5th indian') || title.includes('5 indian')) nafzigerUnits.british.add('5th Indian Division');
        if (title.includes('50th') && title.includes('infantry')) nafzigerUnits.british.add('50th Infantry Division');
        if (title.includes('51st') && title.includes('highland')) nafzigerUnits.british.add('51st Highland Division');
        if (title.includes('2nd new zealand') || title.includes('2 new zealand')) nafzigerUnits.british.add('2nd New Zealand Division');
        if (title.includes('9th australian') || title.includes('9 australian')) nafzigerUnits.british.add('9th Australian Division');
        if (title.includes('south african')) {
            if (title.includes('1st') || title.includes('1 ')) nafzigerUnits.british.add('1st South African Division');
            if (title.includes('2nd') || title.includes('2 ')) nafzigerUnits.british.add('2nd South African Division');
        }
        if (title.includes('8th army') || title.includes('eighth army')) nafzigerUnits.british.add('8th Army');
        if (title.includes('western desert force')) nafzigerUnits.british.add('Western Desert Force');

        // French units
        if (title.includes('vichy french') && title.includes('north africa')) nafzigerUnits.french.add('Vichy French Forces');
    }
}

console.log(`  German units in Nafziger: ${nafzigerUnits.german.size}`);
console.log(`  Italian units in Nafziger: ${nafzigerUnits.italian.size}`);
console.log(`  British units in Nafziger: ${nafzigerUnits.british.size}`);
console.log(`  French units in Nafziger: ${nafzigerUnits.french.size}`);
console.log();

// Step 2: Extract seed file units
console.log('Step 2: Analyzing seed file units...');
const seedUnits = {
    german: [],
    italian: [],
    british: [],
    american: [],
    french: []
};

for (const [key, units] of Object.entries(seedFile)) {
    if (!key.endsWith('_units')) continue;
    const nation = key.replace('_units', '');
    const nationKey = nation === 'usa' ? 'american' : nation;

    for (const unit of units) {
        seedUnits[nationKey].push({
            designation: unit.designation,
            quarters: unit.quarters,
            quarterCount: unit.quarters.length
        });
    }
}

console.log('  Seed file breakdown:');
for (const [nation, units] of Object.entries(seedUnits)) {
    const totalQuarters = units.reduce((sum, u) => sum + u.quarterCount, 0);
    console.log(`    ${nation}: ${units.length} unique units, ${totalQuarters} unit-quarters`);
}
console.log();

// Step 3: Extract completed units
console.log('Step 3: Analyzing completed canonical units...');
const completed = completedAnalysis.summary.unique_units_by_nation;

console.log('  Completed units breakdown:');
for (const [nation, units] of Object.entries(completed)) {
    if (nation !== 'unknown') {
        console.log(`    ${nation}: ${units.length} unique units`);
    }
}
console.log();

// Step 4: Cross-reference seed against Nafziger
console.log('Step 4: Validating seed against Nafziger Collection...');
const validation = {
    confirmed: [],
    not_in_nafziger: [],
    in_nafziger_not_seed: []
};

// Check German units
for (const seedUnit of seedUnits.german) {
    const designation = seedUnit.designation;
    const inNafziger = Array.from(nafzigerUnits.german).some(naf => {
        return designation.includes(naf.split('.')[0]) || naf.includes(designation.split('.')[0]);
    });

    if (inNafziger) {
        validation.confirmed.push({ nation: 'german', unit: designation, quarters: seedUnit.quarters });
    } else {
        validation.not_in_nafziger.push({ nation: 'german', unit: designation, quarters: seedUnit.quarters });
    }
}

// Check Italian units
for (const seedUnit of seedUnits.italian) {
    const designation = seedUnit.designation;
    const inNafziger = Array.from(nafzigerUnits.italian).some(naf => {
        const nafLower = naf.toLowerCase();
        const seedLower = designation.toLowerCase();
        return nafLower.includes(seedLower.split(' ')[0]) || seedLower.includes(nafLower.split(' ')[0]);
    });

    if (inNafziger) {
        validation.confirmed.push({ nation: 'italian', unit: designation, quarters: seedUnit.quarters });
    } else {
        validation.not_in_nafziger.push({ nation: 'italian', unit: designation, quarters: seedUnit.quarters });
    }
}

// Check British units
for (const seedUnit of seedUnits.british) {
    const designation = seedUnit.designation;
    const inNafziger = Array.from(nafzigerUnits.british).some(naf => {
        const nafLower = naf.toLowerCase();
        const seedLower = designation.toLowerCase();
        return nafLower.includes(seedLower.split(' ')[0]) || seedLower.includes(nafLower.split(' ')[0]);
    });

    if (inNafziger) {
        validation.confirmed.push({ nation: 'british', unit: designation, quarters: seedUnit.quarters });
    } else {
        validation.not_in_nafziger.push({ nation: 'british', unit: designation, quarters: seedUnit.quarters });
    }
}

// American units (1942-1943, won't be in 1939-1942 Nafziger index)
for (const seedUnit of seedUnits.american) {
    validation.not_in_nafziger.push({
        nation: 'american',
        unit: seedUnit.designation,
        quarters: seedUnit.quarters,
        reason: '1942-1943 arrivals (post-Nafziger index period)'
    });
}

// French units
for (const seedUnit of seedUnits.french) {
    validation.not_in_nafziger.push({
        nation: 'french',
        unit: seedUnit.designation,
        quarters: seedUnit.quarters,
        reason: 'Free French 1942-1943 (post-Nafziger index period)'
    });
}

console.log(`  ✅ Confirmed in Nafziger: ${validation.confirmed.length}`);
console.log(`  ⚠️ Not in Nafziger index: ${validation.not_in_nafziger.length}`);
console.log();

// Step 5: Check for units in Nafziger but not in seed
console.log('Step 5: Identifying units in Nafziger but NOT in seed...');

// Check if Nafziger units are in seed
for (const [nation, nafUnits] of Object.entries(nafzigerUnits)) {
    for (const nafUnit of Array.from(nafUnits)) {
        const nationKey = nation === 'american' ? 'usa' : nation;
        const inSeed = seedUnits[nation]?.some(s => {
            const nafLower = nafUnit.toLowerCase();
            const seedLower = s.designation.toLowerCase();
            return nafLower.includes(seedLower.split(' ')[0]) || seedLower.includes(nafLower.split(' ')[0]);
        });

        if (!inSeed) {
            validation.in_nafziger_not_seed.push({ nation, unit: nafUnit });
        }
    }
}

console.log(`  ⚠️ Units in Nafziger but NOT in seed: ${validation.in_nafziger_not_seed.length}`);
if (validation.in_nafziger_not_seed.length > 0) {
    console.log('  Missing units:');
    for (const missing of validation.in_nafziger_not_seed) {
        console.log(`    - ${missing.nation}: ${missing.unit}`);
    }
}
console.log();

// Step 6: Compare seed with completed units
console.log('Step 6: Comparing seed with completed canonical units...');

const seedVsCompleted = {
    in_seed_completed: [],
    in_seed_not_completed: [],
    completed_not_in_seed: []
};

// Check seed units against completed
for (const [nation, units] of Object.entries(seedUnits)) {
    if (nation === 'american') continue; // Skip comparison for now

    for (const seedUnit of units) {
        const completedUnits = completed[nation] || [];
        const isCompleted = completedUnits.some(c => {
            const cLower = c.toLowerCase();
            const sLower = seedUnit.designation.toLowerCase();
            // Fuzzy match: check if 60%+ words overlap
            const cWords = cLower.split(/\s+/).filter(w => w.length > 2);
            const sWords = sLower.split(/\s+/).filter(w => w.length > 2);
            const matches = sWords.filter(sw => cWords.includes(sw)).length;
            return matches / sWords.length >= 0.6;
        });

        if (isCompleted) {
            seedVsCompleted.in_seed_completed.push({ nation, unit: seedUnit.designation });
        } else {
            seedVsCompleted.in_seed_not_completed.push({ nation, unit: seedUnit.designation, quarters: seedUnit.quarters });
        }
    }
}

console.log(`  ✅ Seed units that ARE completed: ${seedVsCompleted.in_seed_completed.length}`);
console.log(`  ⏳ Seed units NOT YET completed: ${seedVsCompleted.in_seed_not_completed.length}`);
console.log();

// Step 7: Generate final validation report
console.log('Step 7: Generating validation report...');

const report = {
    analysis_date: new Date().toISOString(),
    sources: {
        seed_file: 'projects/north_africa_seed_units_COMPLETE.json',
        nafziger_index: 'Resource Documents/Nafziger Collection/WWII/North_Africa_Index/NORTH_AFRICA_FILES.json',
        completed_units: 'data/output/COMPLETED_UNITS_ANALYSIS.json'
    },
    seed_summary: {
        total_unique_units: Object.values(seedUnits).reduce((sum, units) => sum + units.length, 0),
        total_unit_quarters: Object.values(seedUnits).reduce((sum, units) => {
            return sum + units.reduce((s, u) => s + u.quarterCount, 0);
        }, 0),
        by_nation: Object.entries(seedUnits).map(([nation, units]) => ({
            nation,
            unique_units: units.length,
            unit_quarters: units.reduce((s, u) => s + u.quarterCount, 0)
        }))
    },
    validation_results: {
        confirmed_by_nafziger: validation.confirmed.length,
        not_in_nafziger: validation.not_in_nafziger.length,
        in_nafziger_not_seed: validation.in_nafziger_not_seed.length,
        seed_completed: seedVsCompleted.in_seed_completed.length,
        seed_not_completed: seedVsCompleted.in_seed_not_completed.length
    },
    detailed_validation: {
        confirmed: validation.confirmed,
        not_in_nafziger: validation.not_in_nafziger,
        missing_from_seed: validation.in_nafziger_not_seed,
        not_yet_completed: seedVsCompleted.in_seed_not_completed
    },
    recommendations: []
};

// Generate recommendations
if (validation.in_nafziger_not_seed.length > 0) {
    report.recommendations.push({
        priority: 'HIGH',
        action: 'ADD_TO_SEED',
        reason: `${validation.in_nafziger_not_seed.length} units found in Nafziger Collection but missing from seed file`,
        units: validation.in_nafziger_not_seed
    });
}

if (seedVsCompleted.in_seed_not_completed.length > 0) {
    report.recommendations.push({
        priority: 'MEDIUM',
        action: 'COMPLETE_EXTRACTION',
        reason: `${seedVsCompleted.in_seed_not_completed.length} seed units not yet completed`,
        count: seedVsCompleted.in_seed_not_completed.length
    });
}

// Write report
const reportPath = 'SEED_VALIDATION_REPORT.json';
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log(`  ✅ Report saved to: ${reportPath}`);
console.log();

// Step 8: Print summary
console.log('='.repeat(80));
console.log('SUMMARY');
console.log('='.repeat(80));
console.log();
console.log('📊 SEED FILE STATUS:');
console.log(`  Total unique units: ${report.seed_summary.total_unique_units}`);
console.log(`  Total unit-quarters: ${report.seed_summary.total_unit_quarters}`);
console.log();
console.log('✅ VALIDATION RESULTS:');
console.log(`  Confirmed by Nafziger: ${validation.confirmed.length}`);
console.log(`  Not in Nafziger (1942-1943): ${validation.not_in_nafziger.length}`);
console.log(`  In Nafziger, missing from seed: ${validation.in_nafziger_not_seed.length}`);
console.log();
console.log('📝 COMPLETION STATUS:');
console.log(`  Seed units completed: ${seedVsCompleted.in_seed_completed.length}`);
console.log(`  Seed units remaining: ${seedVsCompleted.in_seed_not_completed.length}`);
console.log();

if (report.recommendations.length > 0) {
    console.log('⚠️ RECOMMENDATIONS:');
    for (const rec of report.recommendations) {
        console.log(`  [${rec.priority}] ${rec.action}: ${rec.reason}`);
    }
    console.log();
}

console.log('Next: Create SEED_VALIDATION_REPORT.md');
console.log('='.repeat(80));
