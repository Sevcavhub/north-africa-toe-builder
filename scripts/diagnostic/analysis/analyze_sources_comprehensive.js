/**
 * Comprehensive Source Analysis
 *
 * Check ALL possible locations where sources might be stored:
 * - validation.source (array)
 * - sources (array)
 * - source_documentation
 * - data_quality.sources
 */

const fs = require('fs');
const path = require('path');

const unitsDir = 'data/output/units';
const files = fs.readdirSync(unitsDir).filter(f => f.endsWith('.json'));

console.log('=== COMPREHENSIVE SOURCE ANALYSIS ===\n');
console.log(`Analyzing ${files.length} unit files...\n`);

const sourceCounts = {
    tessin: new Set(),
    nafziger: new Set(),
    army_lists: new Set(),
    tm30: new Set(),
    field_manuals: new Set(),
    playfair: new Set(),       // Official British history
    prasad: new Set(),         // Official Indian history
    wikipedia: new Set(),      // Secondary source
    other_primary: new Set(),
    no_sources: new Set()
};

const sourceLocationStats = {
    validation_source: 0,
    sources_array: 0,
    source_documentation: 0,
    data_quality_sources: 0,
    no_field: 0
};

files.forEach(filename => {
    const filepath = path.join(unitsDir, filename);
    let unit;

    try {
        unit = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
    } catch (err) {
        console.log(`⚠️  Error reading ${filename}: ${err.message}`);
        return;
    }

    // Check all possible source locations
    let sourcesArray = null;
    let sourceLocation = null;

    if (unit.validation && unit.validation.source && Array.isArray(unit.validation.source)) {
        sourcesArray = unit.validation.source;
        sourceLocation = 'validation.source';
        sourceLocationStats.validation_source++;
    } else if (unit.sources && Array.isArray(unit.sources)) {
        sourcesArray = unit.sources;
        sourceLocation = 'sources';
        sourceLocationStats.sources_array++;
    } else if (unit.source_documentation) {
        sourcesArray = unit.source_documentation.sources || [];
        sourceLocation = 'source_documentation';
        sourceLocationStats.source_documentation++;
    } else if (unit.data_quality && unit.data_quality.sources) {
        sourcesArray = unit.data_quality.sources;
        sourceLocation = 'data_quality.sources';
        sourceLocationStats.data_quality_sources++;
    } else {
        sourceLocationStats.no_field++;
        sourceCounts.no_sources.add(filename);
        return;
    }

    // Analyze source content
    let hasSources = false;
    const sourceText = sourcesArray.join(' ').toLowerCase();

    if (sourceText.includes('tessin')) {
        sourceCounts.tessin.add(filename);
        hasSources = true;
    }
    if (sourceText.includes('nafziger')) {
        sourceCounts.nafziger.add(filename);
        hasSources = true;
    }
    if (sourceText.includes('army list') || sourceText.includes('ministry')) {
        sourceCounts.army_lists.add(filename);
        hasSources = true;
    }
    if (sourceText.includes('tm30') || sourceText.includes('tm-30') || sourceText.includes('technical manual')) {
        sourceCounts.tm30.add(filename);
        hasSources = true;
    }
    if (sourceText.includes('field manual') || sourceText.includes('fm-')) {
        sourceCounts.field_manuals.add(filename);
        hasSources = true;
    }
    if (sourceText.includes('playfair')) {
        sourceCounts.playfair.add(filename);
        hasSources = true;
    }
    if (sourceText.includes('prasad')) {
        sourceCounts.prasad.add(filename);
        hasSources = true;
    }
    if (sourceText.includes('wikipedia')) {
        sourceCounts.wikipedia.add(filename);
        hasSources = true;
    }

    if (!hasSources && sourcesArray.length > 0) {
        sourceCounts.other_primary.add(filename);
    }
});

console.log('=== SOURCE FIELD LOCATIONS ===\n');
console.log(`validation.source (array): ${sourceLocationStats.validation_source} files`);
console.log(`sources (array): ${sourceLocationStats.sources_array} files`);
console.log(`source_documentation: ${sourceLocationStats.source_documentation} files`);
console.log(`data_quality.sources: ${sourceLocationStats.data_quality_sources} files`);
console.log(`NO source field found: ${sourceLocationStats.no_field} files`);
console.log();

console.log('=== SOURCE USAGE BREAKDOWN ===\n');
console.log(`Tessin (German encyclopedia): ${sourceCounts.tessin.size} files`);
console.log(`Nafziger Collection: ${sourceCounts.nafziger.size} files`);
console.log(`British Army Lists: ${sourceCounts.army_lists.size} files`);
console.log(`US Intelligence TM30: ${sourceCounts.tm30.size} files`);
console.log(`US Field Manuals: ${sourceCounts.field_manuals.size} files`);
console.log(`Playfair (Official British History): ${sourceCounts.playfair.size} files`);
console.log(`Prasad (Official Indian History): ${sourceCounts.prasad.size} files`);
console.log(`Wikipedia (secondary source): ${sourceCounts.wikipedia.size} files`);
console.log(`Other primary sources: ${sourceCounts.other_primary.size} files`);
console.log(`NO sources documented: ${sourceCounts.no_sources.size} files`);
console.log();

console.log('=== BY NATION ===\n');

const byNation = {
    german: { tessin: 0, nafziger: 0, total: 0 },
    italian: { tessin: 0, nafziger: 0, total: 0 },
    british: { army_lists: 0, playfair: 0, prasad: 0, nafziger: 0, total: 0 },
    american: { field_manuals: 0, nafziger: 0, total: 0 },
    french: { nafziger: 0, other: 0, total: 0 }
};

files.forEach(f => {
    if (f.startsWith('german_')) {
        byNation.german.total++;
        if (sourceCounts.tessin.has(f)) byNation.german.tessin++;
        if (sourceCounts.nafziger.has(f)) byNation.german.nafziger++;
    } else if (f.startsWith('italian_')) {
        byNation.italian.total++;
        if (sourceCounts.tessin.has(f)) byNation.italian.tessin++;
        if (sourceCounts.nafziger.has(f)) byNation.italian.nafziger++;
    } else if (f.startsWith('british_')) {
        byNation.british.total++;
        if (sourceCounts.army_lists.has(f)) byNation.british.army_lists++;
        if (sourceCounts.playfair.has(f)) byNation.british.playfair++;
        if (sourceCounts.prasad.has(f)) byNation.british.prasad++;
        if (sourceCounts.nafziger.has(f)) byNation.british.nafziger++;
    } else if (f.startsWith('american_')) {
        byNation.american.total++;
        if (sourceCounts.field_manuals.has(f)) byNation.american.field_manuals++;
        if (sourceCounts.nafziger.has(f)) byNation.american.nafziger++;
    } else if (f.startsWith('french_')) {
        byNation.french.total++;
        if (sourceCounts.nafziger.has(f)) byNation.french.nafziger++;
    }
});

console.log(`German units (total: ${byNation.german.total}):`);
console.log(`  - Tessin: ${byNation.german.tessin} (${Math.round(byNation.german.tessin/byNation.german.total*100)}%)`);
console.log(`  - Nafziger: ${byNation.german.nafziger} (${Math.round(byNation.german.nafziger/byNation.german.total*100)}%)`);

console.log(`\nItalian units (total: ${byNation.italian.total}):`);
console.log(`  - Tessin: ${byNation.italian.tessin} (${Math.round(byNation.italian.tessin/byNation.italian.total*100)}%)`);
console.log(`  - Nafziger: ${byNation.italian.nafziger} (${Math.round(byNation.italian.nafziger/byNation.italian.total*100)}%)`);

console.log(`\nBritish units (total: ${byNation.british.total}):`);
console.log(`  - Army Lists: ${byNation.british.army_lists} (${Math.round(byNation.british.army_lists/byNation.british.total*100)}%)`);
console.log(`  - Playfair (Official History): ${byNation.british.playfair} (${Math.round(byNation.british.playfair/byNation.british.total*100)}%)`);
console.log(`  - Prasad (Indian History): ${byNation.british.prasad} (${Math.round(byNation.british.prasad/byNation.british.total*100)}%)`);
console.log(`  - Nafziger: ${byNation.british.nafziger} (${Math.round(byNation.british.nafziger/byNation.british.total*100)}%)`);

console.log(`\nAmerican units (total: ${byNation.american.total}):`);
console.log(`  - Field Manuals: ${byNation.american.field_manuals} (${Math.round(byNation.american.field_manuals/byNation.american.total*100)}%)`);
console.log(`  - Nafziger: ${byNation.american.nafziger} (${Math.round(byNation.american.nafziger/byNation.american.total*100)}%)`);

console.log(`\nFrench units (total: ${byNation.french.total}):`);
console.log(`  - Nafziger: ${byNation.french.nafziger} (${Math.round(byNation.french.nafziger/byNation.french.total*100)}%)`);
