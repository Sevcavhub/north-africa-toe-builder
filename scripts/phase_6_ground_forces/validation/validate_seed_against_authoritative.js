const fs = require('fs');

// Load both files
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_VALIDATED.json', 'utf8'));
const authoritative = JSON.parse(fs.readFileSync('data/canonical/AUTHORITATIVE_NORTH_AFRICA_UNITS.json', 'utf8'));

console.log('═══════════════════════════════════════════════════════════');
console.log('SEED VALIDATION AGAINST AUTHORITATIVE SOURCES');
console.log('═══════════════════════════════════════════════════════════\n');

console.log('Authoritative sources:');
for (const source of authoritative.metadata.sources) {
    console.log(`  - ${source}`);
}
console.log();

// Build map of authoritative units
const authMap = new Map();

for (const unit of authoritative.american_units) {
    authMap.set(`american|${unit.designation}`, unit);
}
for (const unit of authoritative.british_commonwealth_units) {
    authMap.set(`british|${unit.designation}`, unit);
}
for (const unit of authoritative.german_units) {
    authMap.set(`german|${unit.designation}`, unit);
}
for (const unit of authoritative.italian_units) {
    authMap.set(`italian|${unit.designation}`, unit);
}
for (const unit of authoritative.french_units) {
    authMap.set(`french|${unit.designation}`, unit);
}

// Flatten seed units from multiple arrays
const allSeedUnits = [];
for (const unit of seed.german_units || []) {
    allSeedUnits.push({ nation: 'german', ...unit });
}
for (const unit of seed.italian_units || []) {
    allSeedUnits.push({ nation: 'italian', ...unit });
}
for (const unit of seed.british_units || []) {
    allSeedUnits.push({ nation: 'british', ...unit });
}
for (const unit of seed.usa_units || []) {
    allSeedUnits.push({ nation: 'american', ...unit });
}
for (const unit of seed.french_units || []) {
    allSeedUnits.push({ nation: 'french', ...unit });
}

console.log(`Authoritative units found: ${authMap.size}`);
console.log(`Seed unique units: ${allSeedUnits.length}\n`);

// Validate each seed unit
const validatedUnits = [];
const missingFromAuth = [];
const found = [];

for (const seedUnit of allSeedUnits) {
    const key = `${seedUnit.nation}|${seedUnit.designation}`;
    const authUnit = authMap.get(key);

    if (authUnit) {
        validatedUnits.push({
            ...seedUnit,
            authoritative_match: authUnit,
            validated: true
        });
        found.push(seedUnit.designation);
    } else {
        missingFromAuth.push(seedUnit);
    }
}

console.log('═══════════════════════════════════════════════════════════');
console.log('VALIDATION RESULTS');
console.log('═══════════════════════════════════════════════════════════\n');

console.log(`✅ Validated units: ${validatedUnits.length}/${allSeedUnits.length}`);
console.log(`⚠️  Not found in authoritative sources: ${missingFromAuth.length}\n`);

if (missingFromAuth.length > 0) {
    console.log('Units in seed but NOT in authoritative sources:\n');
    for (const unit of missingFromAuth) {
        console.log(`  - ${unit.nation}: ${unit.designation}`);
        console.log(`    Quarters: ${unit.quarters.length}`);
    }
    console.log();
}

// Check for units in authoritative sources but NOT in seed
console.log('═══════════════════════════════════════════════════════════');
console.log('MISSING FROM SEED');
console.log('═══════════════════════════════════════════════════════════\n');

const missingFromSeed = [];

for (const [key, authUnit] of authMap.entries()) {
    const [nation, designation] = key.split('|');
    const seedHas = allSeedUnits.some(u => u.nation === nation && u.designation === designation);

    if (!seedHas) {
        missingFromSeed.push(authUnit);
    }
}

console.log(`Units in authoritative sources but NOT in seed: ${missingFromSeed.length}\n`);

if (missingFromSeed.length > 0) {
    const byNation = {};
    for (const unit of missingFromSeed) {
        // Determine nation from original arrays
        let nation = 'unknown';
        if (authoritative.american_units.includes(unit)) nation = 'american';
        else if (authoritative.british_commonwealth_units.includes(unit)) nation = 'british';
        else if (authoritative.german_units.includes(unit)) nation = 'german';
        else if (authoritative.italian_units.includes(unit)) nation = 'italian';
        else if (authoritative.french_units.includes(unit)) nation = 'french';

        if (!byNation[nation]) byNation[nation] = [];
        byNation[nation].push(unit);
    }

    for (const [nation, units] of Object.entries(byNation).sort()) {
        console.log(`${nation.toUpperCase()} (${units.length} missing):`);
        for (const unit of units) {
            console.log(`  - ${unit.designation} (${unit.type})`);
            if (unit.period) console.log(`    Period: ${unit.period}`);
            if (unit.also_known_as) console.log(`    AKA: ${unit.also_known_as}`);
        }
        console.log();
    }
}

// Summary
console.log('═══════════════════════════════════════════════════════════');
console.log('SUMMARY');
console.log('═══════════════════════════════════════════════════════════\n');

console.log('Seed validation:');
console.log(`  ✅ Units validated: ${validatedUnits.length}/${allSeedUnits.length} (${(validatedUnits.length/allSeedUnits.length*100).toFixed(1)}%)`);
console.log(`  ⚠️  Units not in authoritative sources: ${missingFromAuth.length}`);
console.log(`  📝 Authoritative units not in seed: ${missingFromSeed.length}\n`);

console.log('Recommendation:');
if (missingFromSeed.length > 0) {
    console.log(`  Consider adding ${missingFromSeed.length} missing units to seed`);
}
if (missingFromAuth.length > 0) {
    console.log(`  Verify ${missingFromAuth.length} seed units against additional sources`);
}

// Save validation report
const report = {
    validated_at: new Date().toISOString(),
    seed_file: 'projects/north_africa_seed_units_VALIDATED.json',
    authoritative_file: 'data/canonical/AUTHORITATIVE_NORTH_AFRICA_UNITS.json',
    results: {
        seed_units: allSeedUnits.length,
        authoritative_units: authMap.size,
        validated_units: validatedUnits.length,
        validation_percentage: ((validatedUnits.length/allSeedUnits.length)*100).toFixed(1),
        units_in_seed_not_in_auth: missingFromAuth,
        units_in_auth_not_in_seed: missingFromSeed.map(u => ({
            designation: u.designation,
            type: u.type,
            period: u.period,
            campaigns: u.campaigns,
            source: u.source
        }))
    }
};

fs.writeFileSync('data/canonical/SEED_VALIDATION_REPORT.json', JSON.stringify(report, null, 2));
console.log('\n✅ Validation report saved: data/canonical/SEED_VALIDATION_REPORT.json');
