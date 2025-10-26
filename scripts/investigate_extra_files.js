#!/usr/bin/env node

/**
 * Investigates extra files in data/output/units/
 * Compares actual files against seed file expectations
 */

const fs = require('fs').promises;
const path = require('path');
const naming = require('./lib/naming_standard');

async function main() {
    console.log('🔍 Investigating file count disparity...\n');

    // Load seed file
    const seedPath = path.join(process.cwd(), 'projects', 'north_africa_seed_units_COMPLETE.json');
    const seedData = JSON.parse(await fs.readFile(seedPath, 'utf-8'));

    console.log(`📋 Seed file expects: ${seedData.total_unit_quarters} unit-quarters\n`);

    // Build expected filenames from seed
    const expectedFiles = new Set();

    for (const [nationKey, units] of Object.entries(seedData)) {
        if (!nationKey.endsWith('_units') || !Array.isArray(units)) {
            continue;
        }

        const nation = naming.NATION_MAP[nationKey];
        if (!nation) continue;

        for (const unit of units) {
            const designation = unit.designation;

            for (const quarter of unit.quarters) {
                const cleanNation = naming.normalizeNation(nation);
                const cleanQuarter = naming.normalizeQuarter(quarter);
                const cleanDesignation = naming.normalizeDesignation(designation);

                const filename = `${cleanNation}_${cleanQuarter}_${cleanDesignation}_toe.json`;
                expectedFiles.add(filename);
            }
        }
    }

    console.log(`✅ Generated ${expectedFiles.size} expected filenames\n`);

    // Read actual files
    const unitsDir = path.join(process.cwd(), 'data', 'output', 'units');
    const actualFiles = (await fs.readdir(unitsDir))
        .filter(f => f.endsWith('_toe.json'));

    console.log(`📁 Found ${actualFiles.length} actual files\n`);

    // Find extras
    const extraFiles = actualFiles.filter(f => !expectedFiles.has(f));
    const missingFiles = Array.from(expectedFiles).filter(f => !actualFiles.includes(f));

    console.log(`\n⚠️  EXTRA FILES (${extraFiles.length}):\n`);
    extraFiles.sort().forEach((f, i) => {
        console.log(`${i + 1}. ${f}`);
    });

    console.log(`\n❌ MISSING FILES (${missingFiles.length}):\n`);
    missingFiles.sort().forEach((f, i) => {
        console.log(`${i + 1}. ${f}`);
    });

    console.log(`\n📊 Summary:`);
    console.log(`   Expected: ${expectedFiles.size}`);
    console.log(`   Actual:   ${actualFiles.length}`);
    console.log(`   Extra:    ${extraFiles.length}`);
    console.log(`   Missing:  ${missingFiles.length}`);
}

main().catch(console.error);
