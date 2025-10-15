#!/usr/bin/env node

/**
 * Generate Complete Seed from Combat Units Research
 *
 * Transforms COMPLETE_NORTH_AFRICA_COMBAT_UNITS.json into seed format
 * with all units expanded into quarter-by-quarter entries.
 */

const fs = require('fs');
const path = require('path');

console.log('='.repeat(80));
console.log('GENERATING COMPLETE NORTH AFRICA SEED');
console.log('='.repeat(80));
console.log();

// Load complete combat units
const completeUnitsPath = 'data/canonical/COMPLETE_NORTH_AFRICA_COMBAT_UNITS.json';
const completeUnits = JSON.parse(fs.readFileSync(completeUnitsPath, 'utf8'));

console.log('Loaded complete combat units:');
console.log(`  Total units: ${completeUnits.summary.total_combat_units}`);
console.log();

// Helper: Parse period string into array of quarters
function parseQuarters(period) {
    // period format: "1940q2-1943q2" or "1941q1-1941q4"
    const match = period.match(/(\d{4}q\d)-(\d{4}q\d)/);
    if (!match) {
        console.warn(`  Warning: Could not parse period "${period}"`);
        return [];
    }

    const [_, start, end] = match;
    const startYear = parseInt(start.substring(0, 4));
    const startQuarter = parseInt(start.substring(5, 6));
    const endYear = parseInt(end.substring(0, 4));
    const endQuarter = parseInt(end.substring(5, 6));

    const quarters = [];
    for (let year = startYear; year <= endYear; year++) {
        const qStart = (year === startYear) ? startQuarter : 1;
        const qEnd = (year === endYear) ? endQuarter : 4;

        for (let q = qStart; q <= qEnd; q++) {
            quarters.push(`${year}-Q${q}`);
        }
    }

    return quarters;
}

// Helper: Map nation names to seed format
function mapNationName(nationKey) {
    const mapping = {
        'american_units': 'american',
        'british_commonwealth_units': 'british',
        'german_units': 'german',
        'italian_units': 'italian',
        'french_units': 'french'
    };
    return mapping[nationKey] || nationKey.replace('_units', '');
}

// Transform units by nation
const seedData = {
    comment: "Complete North Africa Combat Units - ALL units that fought in battles 1940-1943",
    description: "Comprehensive list of ALL units that participated in North Africa combat operations. Includes divisions, corps, armies, brigades across all major battles from Operation Compass through Tunisia Campaign.",
    validation_date: new Date().toISOString().split('T')[0],
    validation_sources: completeUnits.metadata.sources,
    battles_covered: completeUnits.metadata.battles_covered,
    scope_rule: "ALL units that participated in documented North Africa battles (offensive or defensive). Includes mobile, garrison, and static divisions that saw combat.",
    total_units: completeUnits.summary.total_combat_units,
    total_unit_quarters: 0, // Will calculate

    german_units: [],
    italian_units: [],
    british_units: [],
    usa_units: [],
    french_units: []
};

// Track unit counts
let totalQuarters = 0;
const unitsByNation = {
    german: 0,
    italian: 0,
    british: 0,
    american: 0,
    french: 0
};

// Process each nation's units
for (const [nationKey, units] of Object.entries(completeUnits)) {
    if (!nationKey.endsWith('_units')) continue;

    console.log(`Processing ${nationKey}...`);

    const nation = mapNationName(nationKey);
    let processedCount = 0;

    for (const unit of units) {
        // Parse quarters from period
        const quarters = parseQuarters(unit.period);

        if (quarters.length === 0) {
            console.log(`  ⚠️  Skipping ${unit.designation} - no quarters parsed from "${unit.period}"`);
            continue;
        }

        // Determine which seed array to add to
        let targetArray;
        if (nation === 'american') {
            targetArray = seedData.usa_units;
            unitsByNation.american++;
        } else if (nation === 'british') {
            targetArray = seedData.british_units;
            unitsByNation.british++;
        } else if (nation === 'german') {
            targetArray = seedData.german_units;
            unitsByNation.german++;
        } else if (nation === 'italian') {
            targetArray = seedData.italian_units;
            unitsByNation.italian++;
        } else if (nation === 'french') {
            targetArray = seedData.french_units;
            unitsByNation.french++;
        } else {
            // Other nations (Polish, Greek, Czech) - add to british_units as Commonwealth
            targetArray = seedData.british_units;
            unitsByNation.british++;
        }

        // Add unit with quarters
        targetArray.push({
            designation: unit.designation,
            type: unit.type,
            quarters: quarters,
            battles: unit.battles,
            confidence: unit.confidence,
            ...(unit.nickname && { nickname: unit.nickname }),
            ...(unit.official_name && { official_name: unit.official_name }),
            ...(unit.also_known_as && { also_known_as: unit.also_known_as }),
            ...(unit.note && { note: unit.note })
        });

        totalQuarters += quarters.length;
        processedCount++;
    }

    console.log(`  ✅ Processed ${processedCount} units`);
}

seedData.total_unit_quarters = totalQuarters;

console.log();
console.log('='.repeat(80));
console.log('SEED GENERATION COMPLETE');
console.log('='.repeat(80));
console.log();
console.log('Units by nation:');
console.log(`  German: ${unitsByNation.german}`);
console.log(`  Italian: ${unitsByNation.italian}`);
console.log(`  British/Commonwealth: ${unitsByNation.british}`);
console.log(`  American: ${unitsByNation.american}`);
console.log(`  French: ${unitsByNation.french}`);
console.log();
console.log(`Total unique units: ${seedData.total_units}`);
console.log(`Total unit-quarters: ${totalQuarters}`);
console.log();

// Add notes
seedData.notes = {
    generation: "Auto-generated from comprehensive battle research",
    expansion: `Expanded from 36 units (215 quarters) to ${seedData.total_units} units (${totalQuarters} quarters)`,
    methodology: "All units verified against authoritative sources for actual combat participation",
    comparison_to_previous: "Previous seed had 36 units covering major mobile divisions only. This seed includes ALL combat units: divisions, corps, armies, brigades, and specialized formations.",
    quarter_format: "Uses hyphenated format 'YYYY-QN' to match historical sources"
};

// Save new seed
const outputPath = 'projects/north_africa_seed_units_COMPLETE.json';
fs.writeFileSync(outputPath, JSON.stringify(seedData, null, 2));

console.log('✅ Complete seed saved: ' + outputPath);
console.log();

// Generate comparison report
console.log('='.repeat(80));
console.log('COMPARISON: OLD SEED vs NEW SEED');
console.log('='.repeat(80));
console.log();

const oldSeed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_VALIDATED.json', 'utf8'));

console.log('OLD SEED (VALIDATED):');
console.log(`  Total units: 36`);
console.log(`  Total quarters: 215`);
console.log();

console.log('NEW SEED (COMPLETE):');
console.log(`  Total units: ${seedData.total_units}`);
console.log(`  Total quarters: ${totalQuarters}`);
console.log();

console.log('INCREASE:');
console.log(`  Units: +${seedData.total_units - 36} (${((seedData.total_units / 36 - 1) * 100).toFixed(0)}% increase)`);
console.log(`  Quarters: +${totalQuarters - 215} (${((totalQuarters / 215 - 1) * 100).toFixed(0)}% increase)`);
console.log();

// Save comparison report
const comparison = {
    generated: new Date().toISOString(),
    old_seed: {
        file: 'projects/north_africa_seed_units_VALIDATED.json',
        units: 36,
        quarters: 215,
        scope: 'Major mobile combat divisions only'
    },
    new_seed: {
        file: outputPath,
        units: seedData.total_units,
        quarters: totalQuarters,
        scope: 'ALL units that fought in North Africa battles'
    },
    increase: {
        units: seedData.total_units - 36,
        quarters: totalQuarters - 215,
        percentage_units: ((seedData.total_units / 36 - 1) * 100).toFixed(1),
        percentage_quarters: ((totalQuarters / 215 - 1) * 100).toFixed(1)
    },
    by_nation: {
        german: {
            old: 7,
            new: unitsByNation.german,
            increase: unitsByNation.german - 7
        },
        italian: {
            old: 10,
            new: unitsByNation.italian,
            increase: unitsByNation.italian - 10
        },
        british: {
            old: 13,
            new: unitsByNation.british,
            increase: unitsByNation.british - 13
        },
        american: {
            old: 5,
            new: unitsByNation.american,
            increase: unitsByNation.american - 5
        },
        french: {
            old: 2,
            new: unitsByNation.french,
            increase: unitsByNation.french - 2
        }
    }
};

fs.writeFileSync('data/canonical/SEED_COMPARISON_REPORT.json', JSON.stringify(comparison, null, 2));
console.log('✅ Comparison report saved: data/canonical/SEED_COMPARISON_REPORT.json');
console.log();
console.log('='.repeat(80));
