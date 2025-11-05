const fs = require('fs');

const masterDir = JSON.parse(fs.readFileSync('data/canonical/MASTER_UNIT_DIRECTORY.json', 'utf8'));
const matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf8'));

// Get the 10 false positives to exclude
const problematicMatches = new Set();
const aliasMatches = matchingReport.matches.alias_matches;

for (const match of aliasMatches) {
    const designationNum = match.designation.match(/\d+/g);
    const fileWithoutPrefix = match.matched_file.replace(/^(american|british|french|german|italian)_\d{4}q\d_/, '');
    const fileNum = fileWithoutPrefix.match(/\d+/g);

    const desgStr = designationNum ? designationNum.sort().join('_') : 'none';
    const fileStr = fileNum ? fileNum.sort().join('_') : 'none';

    if (desgStr !== fileStr) {
        problematicMatches.add(match.canonical_id);
    }
}

// Get all incomplete units (excluding false positives)
const incompleteUnits = matchingReport.matches.no_match.filter(u => !problematicMatches.has(u.canonical_id));

// Add the 10 false positives back to incomplete
for (const match of aliasMatches) {
    if (problematicMatches.has(match.canonical_id)) {
        incompleteUnits.push({
            canonical_id: match.canonical_id,
            nation: match.nation,
            quarter: match.quarter,
            designation: match.designation
        });
    }
}

// Group by nation
const byNation = {
    italian: incompleteUnits.filter(u => u.nation === 'italian'),
    french: incompleteUnits.filter(u => u.nation === 'french'),
    british: incompleteUnits.filter(u => u.nation === 'british'),
    german: incompleteUnits.filter(u => u.nation === 'german'),
    american: incompleteUnits.filter(u => u.nation === 'american')
};

console.log('═══════════════════════════════════════════════════════════');
console.log('EXTRACTION PLAN FOR 135 INCOMPLETE UNIT-QUARTERS');
console.log('═══════════════════════════════════════════════════════════\n');

console.log('📊 BREAKDOWN BY NATION:\n');
console.log(`   🇮🇹 Italian: ${byNation.italian.length} unit-quarters (${(byNation.italian.length / incompleteUnits.length * 100).toFixed(1)}%)`);
console.log(`   🇫🇷 French: ${byNation.french.length} unit-quarters (${(byNation.french.length / incompleteUnits.length * 100).toFixed(1)}%)`);
console.log(`   🇬🇧 British: ${byNation.british.length} unit-quarters (${(byNation.british.length / incompleteUnits.length * 100).toFixed(1)}%)`);
console.log(`   🇩🇪 German: ${byNation.german.length} unit-quarters (${(byNation.german.length / incompleteUnits.length * 100).toFixed(1)}%)`);
console.log(`   🇺🇸 American: ${byNation.american.length} unit-quarters (${(byNation.american.length / incompleteUnits.length * 100).toFixed(1)}%)`);

console.log('\n\n═══════════════════════════════════════════════════════════');
console.log('PRIORITY 1: ITALIAN UNITS (HIGHEST URGENCY)');
console.log('═══════════════════════════════════════════════════════════\n');

// Group Italian by unique unit
const italianByUnit = {};
for (const unit of byNation.italian) {
    if (!italianByUnit[unit.designation]) {
        italianByUnit[unit.designation] = [];
    }
    italianByUnit[unit.designation].push(unit.quarter);
}

for (const [designation, quarters] of Object.entries(italianByUnit).sort()) {
    console.log(`📌 ${designation}: ${quarters.length} quarters`);
    console.log(`   Quarters: ${quarters.sort().join(', ')}`);

    // Find source references
    const masterUnit = masterDir.canonical_units.find(u =>
        u.designation === designation && u.nation === 'italian'
    );
    if (masterUnit && masterUnit.authoritative_sources) {
        const sources = [];
        if (masterUnit.authoritative_sources.nafziger_refs.length > 0) {
            sources.push(`Nafziger (${masterUnit.authoritative_sources.nafziger_refs.length} refs)`);
        }
        if (masterUnit.authoritative_sources.italian_source_refs.length > 0) {
            sources.push(`Italian sources (${masterUnit.authoritative_sources.italian_source_refs.length} refs)`);
        }
        console.log(`   Sources: ${sources.join(', ')}`);
    }
    console.log();
}

console.log('\n═══════════════════════════════════════════════════════════');
console.log('PRIORITY 2: FRENCH UNITS');
console.log('═══════════════════════════════════════════════════════════\n');

const frenchByUnit = {};
for (const unit of byNation.french) {
    if (!frenchByUnit[unit.designation]) {
        frenchByUnit[unit.designation] = [];
    }
    frenchByUnit[unit.designation].push(unit.quarter);
}

for (const [designation, quarters] of Object.entries(frenchByUnit).sort()) {
    console.log(`📌 ${designation}: ${quarters.length} quarters (${quarters.sort().join(', ')})`);
}

console.log('\n\n═══════════════════════════════════════════════════════════');
console.log('PRIORITY 3: BRITISH, GERMAN, AMERICAN UNITS');
console.log('═══════════════════════════════════════════════════════════\n');

console.log(`🇬🇧 British: ${byNation.british.length} incomplete quarters across multiple units`);
console.log(`🇩🇪 German: ${byNation.german.length} incomplete quarters across multiple units`);
console.log(`🇺🇸 American: ${byNation.american.length} incomplete quarters across multiple units`);

console.log('\n\n═══════════════════════════════════════════════════════════');
console.log('RECOMMENDED EXTRACTION SEQUENCE:');
console.log('═══════════════════════════════════════════════════════════\n');

console.log('PHASE A: Italian Divisions (65 unit-quarters)');
console.log('  - Highest gap: Only 3% complete vs 60%+ for other nations');
console.log('  - All 8 Italian divisions have source coverage (Nafziger + G2 + TME)');
console.log('  - Start with: Brescia, Pavia, Bologna, Savona, Trento\n');

console.log('PHASE B: French Units (6 unit-quarters)');
console.log('  - Quick wins: Only 2 unique units');
console.log('  - 1re Division Française Libre: 4 quarters');
console.log('  - 2e Division d\'Infanterie Marocaine: 2 quarters\n');

console.log('PHASE C: British/German/American Remaining Gaps (64 unit-quarters)');
console.log('  - Fill remaining quarters for partially complete units');
console.log('  - Focus on 1942-1943 period (highest concentration)\n');

console.log('═══════════════════════════════════════════════════════════');
console.log(`TOTAL INCOMPLETE: ${incompleteUnits.length} unit-quarters`);
console.log('═══════════════════════════════════════════════════════════\n');

// Save detailed extraction list
const extractionPlan = {
    metadata: {
        created: new Date().toISOString(),
        total_incomplete: incompleteUnits.length,
        breakdown_by_nation: {
            italian: byNation.italian.length,
            french: byNation.french.length,
            british: byNation.british.length,
            german: byNation.german.length,
            american: byNation.american.length
        }
    },
    priority_a_italian: byNation.italian.map(u => ({
        canonical_id: u.canonical_id,
        designation: u.designation,
        quarter: u.quarter
    })),
    priority_b_french: byNation.french.map(u => ({
        canonical_id: u.canonical_id,
        designation: u.designation,
        quarter: u.quarter
    })),
    priority_c_others: [
        ...byNation.british,
        ...byNation.german,
        ...byNation.american
    ].map(u => ({
        canonical_id: u.canonical_id,
        nation: u.nation,
        designation: u.designation,
        quarter: u.quarter
    }))
};

fs.writeFileSync(
    'data/canonical/EXTRACTION_PLAN.json',
    JSON.stringify(extractionPlan, null, 2)
);

console.log('✅ Detailed extraction plan saved to: data/canonical/EXTRACTION_PLAN.json\n');
