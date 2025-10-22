const fs = require('fs');
const path = require('path');

const unitsDir = 'data/output/units';
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('.json'));

const sourceCounts = {
    tessin: [],
    nafziger: [],
    army_lists: [],
    tm30: [],
    field_manuals: [],
    other_primary: [],
    no_sources: []
};

console.log('Analyzing', files.length, 'unit files...\n');

files.forEach(filename => {
    const filepath = path.join(unitsDir, filename);
    const content = fs.readFileSync(filepath, 'utf-8');

    let hasSources = false;

    if (content.includes('Tessin')) {
        sourceCounts.tessin.push(filename);
        hasSources = true;
    }
    if (content.includes('Nafziger')) {
        sourceCounts.nafziger.push(filename);
        hasSources = true;
    }
    if (content.includes('Army List') || content.includes('Ministry')) {
        sourceCounts.army_lists.push(filename);
        hasSources = true;
    }
    if (content.includes('TM30') || content.includes('TM-30') || content.includes('Technical Manual')) {
        sourceCounts.tm30.push(filename);
        hasSources = true;
    }
    if (content.includes('Field Manual') || content.includes('FM-')) {
        sourceCounts.field_manuals.push(filename);
        hasSources = true;
    }

    // Check for other primary sources
    if (content.includes('"source_type": "primary"') && !hasSources) {
        sourceCounts.other_primary.push(filename);
        hasSources = true;
    }

    if (!hasSources) {
        sourceCounts.no_sources.push(filename);
    }
});

console.log('=== SOURCE USAGE BREAKDOWN ===\n');
console.log('Tessin (German encyclopedia):', sourceCounts.tessin.length, 'files');
console.log('Nafziger Collection:', sourceCounts.nafziger.length, 'files');
console.log('British Army Lists:', sourceCounts.army_lists.length, 'files');
console.log('US Intelligence TM30:', sourceCounts.tm30.length, 'files');
console.log('US Field Manuals:', sourceCounts.field_manuals.length, 'files');
console.log('Other primary sources:', sourceCounts.other_primary.length, 'files');
console.log('No sources documented:', sourceCounts.no_sources.length, 'files');

console.log('\n=== BY NATION ===\n');

const byNation = {
    german: { tessin: 0, nafziger: 0, total: 0 },
    italian: { tessin: 0, nafziger: 0, total: 0 },
    british: { army_lists: 0, tm30: 0, nafziger: 0, total: 0 },
    american: { field_manuals: 0, nafziger: 0, total: 0 },
    french: { nafziger: 0, other: 0, total: 0 }
};

files.forEach(f => {
    if (f.startsWith('german_')) {
        byNation.german.total++;
        if (sourceCounts.tessin.includes(f)) byNation.german.tessin++;
        if (sourceCounts.nafziger.includes(f)) byNation.german.nafziger++;
    } else if (f.startsWith('italian_')) {
        byNation.italian.total++;
        if (sourceCounts.tessin.includes(f)) byNation.italian.tessin++;
        if (sourceCounts.nafziger.includes(f)) byNation.italian.nafziger++;
    } else if (f.startsWith('british_')) {
        byNation.british.total++;
        if (sourceCounts.army_lists.includes(f)) byNation.british.army_lists++;
        if (sourceCounts.tm30.includes(f)) byNation.british.tm30++;
        if (sourceCounts.nafziger.includes(f)) byNation.british.nafziger++;
    } else if (f.startsWith('american_')) {
        byNation.american.total++;
        if (sourceCounts.field_manuals.includes(f)) byNation.american.field_manuals++;
        if (sourceCounts.nafziger.includes(f)) byNation.american.nafziger++;
    } else if (f.startsWith('french_')) {
        byNation.french.total++;
        if (sourceCounts.nafziger.includes(f)) byNation.french.nafziger++;
    }
});

console.log('German units (total:', byNation.german.total + '):');
console.log('  - Tessin:', byNation.german.tessin);
console.log('  - Nafziger:', byNation.german.nafziger);

console.log('\nItalian units (total:', byNation.italian.total + '):');
console.log('  - Tessin:', byNation.italian.tessin);
console.log('  - Nafziger:', byNation.italian.nafziger);

console.log('\nBritish units (total:', byNation.british.total + '):');
console.log('  - Army Lists:', byNation.british.army_lists);
console.log('  - TM30:', byNation.british.tm30);
console.log('  - Nafziger:', byNation.british.nafziger);

console.log('\nAmerican units (total:', byNation.american.total + '):');
console.log('  - Field Manuals:', byNation.american.field_manuals);
console.log('  - Nafziger:', byNation.american.nafziger);

console.log('\nFrench units (total:', byNation.french.total + '):');
console.log('  - Nafziger:', byNation.french.nafziger);

console.log('\n=== SAMPLE FILES USING EACH SOURCE ===\n');

console.log('Tessin examples:');
sourceCounts.tessin.slice(0, 3).forEach(f => console.log('  -', f));

console.log('\nNafziger examples:');
sourceCounts.nafziger.slice(0, 3).forEach(f => console.log('  -', f));

console.log('\nArmy Lists examples:');
sourceCounts.army_lists.slice(0, 3).forEach(f => console.log('  -', f));

console.log('\nNo sources examples:');
sourceCounts.no_sources.slice(0, 5).forEach(f => console.log('  -', f));
