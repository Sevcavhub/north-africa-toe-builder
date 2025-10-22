const fs = require('fs');

// Sample different nations and quarters
const samples = [
    'german_1941q2_15_panzer_division_toe.json',
    'british_1941q1_4th_indian_infantry_division_toe.json',
    'italian_1941q1_ariete_division_toe.json',
    'american_1942q4_1st_armored_division_toe.json',
    'french_1942q3_1ere_brigade_francaise_libre_toe.json'
];

const sourceCounts = {
    tessin: 0,
    nafziger: 0,
    tm30: 0,
    army_lists: 0,
    field_manuals: 0,
    other: 0
};

const sourceExamples = {
    tessin: [],
    nafziger: [],
    tm30: [],
    army_lists: [],
    field_manuals: []
};

console.log('=== CHECKING SOURCE DOCUMENTATION IN UNIT FILES ===\n');

samples.forEach(filename => {
    const filepath = 'data/output/units/' + filename;
    if (!fs.existsSync(filepath)) {
        console.log('❌ File not found:', filename);
        return;
    }

    const unit = JSON.parse(fs.readFileSync(filepath, 'utf-8'));

    console.log('\n📁', filename);
    console.log('Unit:', unit.unit_designation);

    // Check various possible source locations
    const sources = unit.sources ||
                   unit.data_quality?.sources ||
                   unit.source_documentation?.sources ||
                   unit.validation?.sources ||
                   [];

    if (sources.length > 0) {
        console.log('Sources documented:');
        sources.forEach(s => {
            const name = (s.name || s.source_name || s.source || s).toLowerCase();
            console.log('  -', s.name || s.source_name || s.source || s);

            // Categorize source
            if (name.includes('tessin')) {
                sourceCounts.tessin++;
                if (sourceExamples.tessin.length < 3) sourceExamples.tessin.push(s.name || s);
            } else if (name.includes('nafziger')) {
                sourceCounts.nafziger++;
                if (sourceExamples.nafziger.length < 3) sourceExamples.nafziger.push(s.name || s);
            } else if (name.includes('tm') || name.includes('technical manual') || name.includes('intelligence')) {
                sourceCounts.tm30++;
                if (sourceExamples.tm30.length < 3) sourceExamples.tm30.push(s.name || s);
            } else if (name.includes('army list') || name.includes('ministry')) {
                sourceCounts.army_lists++;
                if (sourceExamples.army_lists.length < 3) sourceExamples.army_lists.push(s.name || s);
            } else if (name.includes('field manual') || name.includes('fm-')) {
                sourceCounts.field_manuals++;
                if (sourceExamples.field_manuals.length < 3) sourceExamples.field_manuals.push(s.name || s);
            } else {
                sourceCounts.other++;
            }
        });
    } else {
        console.log('⚠️  No sources array found');

        // Check if data_quality object exists with different structure
        if (unit.data_quality) {
            console.log('Has data_quality object with keys:', Object.keys(unit.data_quality).join(', '));
        }
    }
});

console.log('\n\n=== SOURCE USAGE SUMMARY ===\n');
console.log('Tessin volumes:', sourceCounts.tessin);
console.log('Nafziger Collection:', sourceCounts.nafziger);
console.log('TM30/US Intelligence:', sourceCounts.tm30);
console.log('British Army Lists:', sourceCounts.army_lists);
console.log('US Field Manuals:', sourceCounts.field_manuals);
console.log('Other sources:', sourceCounts.other);

console.log('\n=== SOURCE EXAMPLES ===\n');
for (const [category, examples] of Object.entries(sourceExamples)) {
    if (examples.length > 0) {
        console.log(`\n${category.toUpperCase()}:`);
        examples.forEach(ex => console.log('  -', ex));
    }
}
