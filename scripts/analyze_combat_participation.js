#!/usr/bin/env node

/**
 * Phase 2.1: Analyze Combat Participation
 *
 * Purpose: Filter orphaned units (particularly Italian garrison divisions)
 * to identify which participated in actual combat and should be added to seed.
 *
 * Criteria:
 * - Must be physically in Africa (HQ location check)
 * - Must have documented combat participation (historical_engagements)
 * - Garrison units with no combat = OUT OF SCOPE
 */

const fs = require('fs');
const path = require('path');

// Load data
const seedFile = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf8'));
const completedAnalysis = JSON.parse(fs.readFileSync('data/output/COMPLETED_UNITS_ANALYSIS.json', 'utf8'));

console.log('='.repeat(80));
console.log('PHASE 2.1: COMBAT PARTICIPATION ANALYSIS');
console.log('='.repeat(80));
console.log();

// Step 1: Build set of units already in seed
console.log('Step 1: Identifying units already in seed...');

const seedUnits = new Set();
for (const [key, units] of Object.entries(seedFile)) {
    if (!key.endsWith('_units')) continue;
    for (const unit of units) {
        seedUnits.add(unit.designation.toLowerCase());
    }
}

console.log(`  Seed contains: ${seedUnits.size} unique units`);
console.log();

// Step 2: Analyze all completed units for combat participation
console.log('Step 2: Analyzing combat participation in completed units...');

const combatAnalysis = {
    with_combat: [],
    no_combat: [],
    unclear: []
};

for (const unit of completedAnalysis.units) {
    // Skip if designation is invalid
    if (!unit.designation || unit.designation === 'unknown') continue;

    // Skip if already in seed (using fuzzy match)
    const inSeed = Array.from(seedUnits).some(seedUnit => {
        const unitWords = unit.designation.toLowerCase().split(/\s+/).filter(w => w.length > 2);
        const seedWords = seedUnit.split(/\s+/).filter(w => w.length > 2);
        const matches = unitWords.filter(uw => seedWords.includes(uw)).length;
        return matches / Math.min(unitWords.length, seedWords.length) >= 0.6;
    });

    if (inSeed) continue;

    // Check combat participation
    const hasBattles = unit.has_battles;
    const inAfrica = unit.in_africa;
    const battles = unit.deployment.battles || [];

    if (inAfrica && battles.length > 0) {
        combatAnalysis.with_combat.push({
            nation: unit.nation,
            designation: unit.designation,
            quarter: unit.quarter,
            unit_id: unit.unit_id,
            battles: battles,
            location: unit.deployment.location
        });
    } else if (inAfrica && battles.length === 0) {
        combatAnalysis.no_combat.push({
            nation: unit.nation,
            designation: unit.designation,
            quarter: unit.quarter,
            unit_id: unit.unit_id,
            location: unit.deployment.location,
            reason: 'No battles listed in historical_engagements'
        });
    } else {
        combatAnalysis.unclear.push({
            nation: unit.nation,
            designation: unit.designation,
            quarter: unit.quarter,
            unit_id: unit.unit_id,
            reason: 'Not confirmed in Africa or unclear location'
        });
    }
}

console.log(`  ✅ With combat: ${combatAnalysis.with_combat.length}`);
console.log(`  ⚠️ No combat documented: ${combatAnalysis.no_combat.length}`);
console.log(`  ❓ Unclear: ${combatAnalysis.unclear.length}`);
console.log();

// Step 3: Group by unique unit (across quarters)
console.log('Step 3: Grouping by unique units...');

const uniqueUnits = {};

for (const unit of combatAnalysis.with_combat) {
    const key = `${unit.nation}:${unit.designation}`;
    if (!uniqueUnits[key]) {
        uniqueUnits[key] = {
            nation: unit.nation,
            designation: unit.designation,
            quarters: [],
            battles: new Set(),
            locations: new Set()
        };
    }
    uniqueUnits[key].quarters.push(unit.quarter);
    unit.battles.forEach(b => uniqueUnits[key].battles.add(b));
    if (unit.location) uniqueUnits[key].locations.add(unit.location);
}

console.log(`  Unique units with combat: ${Object.keys(uniqueUnits).length}`);
console.log();

// Step 4: Categorize by unit type
console.log('Step 4: Categorizing units by type...');

const categories = {
    italian_garrison: [],
    italian_mobile: [],
    german: [],
    british: [],
    american: [],
    french: []
};

for (const [key, unit] of Object.entries(uniqueUnits)) {
    const designation = unit.designation.toLowerCase();

    if (unit.nation === 'italian') {
        // Check if garrison division (numbered 60-64, or contains "Sirte", "Marmarica", "Cirene", etc.)
        if (designation.match(/6[0-4]/) ||
            designation.includes('sirte') ||
            designation.includes('marmarica') ||
            designation.includes('cirene') ||
            designation.includes('catanzaro') ||
            designation.includes('sabratha')) {
            categories.italian_garrison.push(unit);
        } else {
            categories.italian_mobile.push(unit);
        }
    } else {
        categories[unit.nation].push(unit);
    }
}

console.log('  Italian garrison divisions (with combat): ', categories.italian_garrison.length);
console.log('  Italian mobile divisions: ', categories.italian_mobile.length);
console.log('  German: ', categories.german.length);
console.log('  British: ', categories.british.length);
console.log('  American: ', categories.american.length);
console.log('  French: ', categories.french.length);
console.log();

// Step 5: Detailed Italian garrison analysis
console.log('Step 5: Italian garrison divisions with documented combat...');

for (const unit of categories.italian_garrison) {
    const battlesStr = Array.from(unit.battles).join(', ');
    console.log(`  - ${unit.designation}`);
    console.log(`    Quarters: ${unit.quarters.sort().join(', ')}`);
    console.log(`    Battles: ${battlesStr || 'Listed but no details'}`);
    console.log();
}

// Step 6: Identify Italian mobile divisions not in seed
console.log('Step 6: Italian mobile divisions NOT in seed...');

for (const unit of categories.italian_mobile) {
    const battlesStr = Array.from(unit.battles).join(', ');
    console.log(`  - ${unit.designation}`);
    console.log(`    Quarters: ${unit.quarters.sort().join(', ')}`);
    console.log(`    Battles: ${battlesStr || 'Listed but no details'}`);
    console.log();
}

// Step 7: Check for Superga Division specifically
console.log('Step 7: Checking for Superga Division...');

const supergaUnit = Object.values(uniqueUnits).find(u =>
    u.designation.toLowerCase().includes('superga')
);

if (supergaUnit) {
    console.log(`  ✅ FOUND: ${supergaUnit.designation}`);
    console.log(`    Quarters: ${supergaUnit.quarters.sort().join(', ')}`);
    console.log(`    Battles: ${Array.from(supergaUnit.battles).join(', ')}`);
} else {
    console.log(`  ⚠️ NOT FOUND in completed units`);
    console.log(`  ℹ️  Nafziger 942IFBA documents: "1st Superga Division, North Africa, 15 June 1942"`);
    console.log(`  Recommendation: ADD to seed for 1942-Q2, 1942-Q3`);
}
console.log();

// Step 8: Generate recommendations
console.log('Step 8: Generating recommendations...');

const recommendations = {
    add_to_seed: {
        high_priority: [],
        medium_priority: [],
        low_priority: []
    },
    exclude_from_seed: []
};

// Superga Division (from Nafziger, not in completed)
recommendations.add_to_seed.high_priority.push({
    nation: 'italian',
    designation: 'Superga Division',
    quarters: ['1942-Q2', '1942-Q3'],
    reason: 'Documented in Nafziger 942IFBA, North Africa June 1942',
    source: 'Nafziger Collection'
});

// Italian mobile divisions with combat (not in seed)
for (const unit of categories.italian_mobile) {
    recommendations.add_to_seed.medium_priority.push({
        nation: unit.nation,
        designation: unit.designation,
        quarters: unit.quarters.sort(),
        reason: `Documented combat: ${Array.from(unit.battles).slice(0, 3).join(', ')}`,
        source: 'Completed units with battle participation'
    });
}

// Italian garrison divisions with combat
for (const unit of categories.italian_garrison) {
    if (unit.battles.size > 0) {
        recommendations.add_to_seed.medium_priority.push({
            nation: unit.nation,
            designation: unit.designation,
            quarters: unit.quarters.sort(),
            reason: `Garrison division with combat: ${Array.from(unit.battles).slice(0, 3).join(', ')}`,
            source: 'Completed units with battle participation'
        });
    }
}

// Units with no combat documentation
for (const unit of combatAnalysis.no_combat) {
    recommendations.exclude_from_seed.push({
        nation: unit.nation,
        designation: unit.designation,
        quarter: unit.quarter,
        unit_id: unit.unit_id,
        reason: 'No documented combat participation'
    });
}

console.log(`  HIGH priority additions: ${recommendations.add_to_seed.high_priority.length}`);
console.log(`  MEDIUM priority additions: ${recommendations.add_to_seed.medium_priority.length}`);
console.log(`  Exclusions (no combat): ${recommendations.exclude_from_seed.length}`);
console.log();

// Step 9: Save report
console.log('Step 9: Saving analysis report...');

const report = {
    analysis_date: new Date().toISOString(),
    scope_rule: 'Units in Africa + documented combat participation',
    summary: {
        completed_units_analyzed: completedAnalysis.units.length,
        units_with_combat: combatAnalysis.with_combat.length,
        units_without_combat: combatAnalysis.no_combat.length,
        unclear: combatAnalysis.unclear.length,
        unique_units_with_combat: Object.keys(uniqueUnits).length
    },
    categories: {
        italian_garrison_with_combat: categories.italian_garrison.length,
        italian_mobile: categories.italian_mobile.length,
        german: categories.german.length,
        british: categories.british.length,
        american: categories.american.length,
        french: categories.french.length
    },
    detailed_units: {
        italian_garrison: categories.italian_garrison.map(u => ({
            designation: u.designation,
            quarters: u.quarters.sort(),
            battles: Array.from(u.battles)
        })),
        italian_mobile: categories.italian_mobile.map(u => ({
            designation: u.designation,
            quarters: u.quarters.sort(),
            battles: Array.from(u.battles)
        })),
        other_nations: {
            german: categories.german.map(u => u.designation),
            british: categories.british.map(u => u.designation),
            american: categories.american.map(u => u.designation),
            french: categories.french.map(u => u.designation)
        }
    },
    recommendations: recommendations
};

fs.writeFileSync('COMBAT_PARTICIPATION_ANALYSIS.json', JSON.stringify(report, null, 2));
console.log('  ✅ Report saved: COMBAT_PARTICIPATION_ANALYSIS.json');
console.log();

// Step 10: Summary
console.log('='.repeat(80));
console.log('SUMMARY');
console.log('='.repeat(80));
console.log();
console.log('📊 COMBAT PARTICIPATION:');
console.log(`  Units with documented combat: ${combatAnalysis.with_combat.length}`);
console.log(`  Units without combat docs: ${combatAnalysis.no_combat.length}`);
console.log(`  Unique units with combat: ${Object.keys(uniqueUnits).length}`);
console.log();
console.log('🎯 RECOMMENDATIONS:');
console.log(`  HIGH priority adds: ${recommendations.add_to_seed.high_priority.length} (Superga)`);
console.log(`  MEDIUM priority adds: ${recommendations.add_to_seed.medium_priority.length} (mobile + garrison with combat)`);
console.log(`  Exclusions: ${recommendations.exclude_from_seed.length} (no combat)`);
console.log();
console.log('📋 ITALIAN GARRISON DIVISIONS (with combat):');
for (const unit of categories.italian_garrison) {
    console.log(`  - ${unit.designation} (${unit.quarters.length} quarters)`);
}
console.log();
console.log('Next: Create validated seed file with combat-verified units');
console.log('='.repeat(80));
