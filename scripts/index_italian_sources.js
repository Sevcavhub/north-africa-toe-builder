#!/usr/bin/env node

/**
 * Index Italian Sources
 *
 * Purpose: Extract references to Italian divisions from US Army intelligence documents
 *
 * Sources:
 * 1. Order-of-battle-of-the-Italian-Army-USA-HQ-G2-July-1943.txt (800KB)
 * 2. TME_30_420_Italian_Military_Forces_1943_temp.txt (762KB)
 *
 * Target units (6 missing divisions from Nafziger coverage):
 * - Pavia Division
 * - Bologna Division
 * - Savona Division
 * - Trento Division
 * - Littorio Division
 * - Folgore Division
 */

const fs = require('fs');
const path = require('path');

console.log('='.repeat(80));
console.log('ITALIAN SOURCES INDEXING');
console.log('='.repeat(80));
console.log();

// Define target divisions
const targetDivisions = [
    { name: 'Pavia', patterns: ['pavia', '27th.*pavia', '28th.*pavia'] },
    { name: 'Bologna', patterns: ['bologna', '39th.*bologna', '40th.*bologna'] },
    { name: 'Savona', patterns: ['savona'] },
    { name: 'Trento', patterns: ['trento', '101st.*trento', '102nd.*trento'] },
    { name: 'Littorio', patterns: ['littorio', 'gioventui.*littorio'] },
    { name: 'Folgore', patterns: ['folgore', '185th.*folgore', '186th.*folgore', '187th.*folgore'] }
];

// Load source files
console.log('Step 1: Loading Italian source documents...');

const g2Report = fs.readFileSync(
    'Resource Documents/Order-of-battle-of-the-Italian-Army-USA-HQ-G2-July-1943.txt',
    'utf8'
);

const tme30420 = fs.readFileSync(
    'Resource Documents/TME_30_420_Italian_Military_Forces_1943_temp.txt',
    'utf8'
);

console.log(`  G2 Report: ${(g2Report.length / 1024).toFixed(1)} KB`);
console.log(`  TME 30-420: ${(tme30420.length / 1024).toFixed(1)} KB`);
console.log();

// Helper: Extract context around a match (±300 characters)
function extractContext(text, matchIndex, contextSize = 300) {
    const start = Math.max(0, matchIndex - contextSize);
    const end = Math.min(text.length, matchIndex + contextSize);

    let context = text.substring(start, end);

    // Try to find sentence or paragraph boundaries
    const sentences = context.split(/[.!?]\s+/);
    if (sentences.length > 1) {
        // Keep middle sentences
        context = sentences.slice(Math.max(0, sentences.length - 3)).join('. ');
    }

    return context.trim().replace(/\s+/g, ' ');
}

// Helper: Find all references to a division in a text
function findDivisionReferences(divisionName, patterns, text, sourceName) {
    const references = [];

    for (const pattern of patterns) {
        const regex = new RegExp(pattern, 'gi');
        let match;

        while ((match = regex.exec(text)) !== null) {
            const context = extractContext(text, match.index, 400);

            references.push({
                division: divisionName,
                source: sourceName,
                matched_text: match[0],
                context: context,
                position: match.index
            });
        }
    }

    return references;
}

// Step 2: Index G2 Report
console.log('Step 2: Indexing G2 Report (July 1943)...');

const g2Index = {};
let g2TotalRefs = 0;

for (const division of targetDivisions) {
    const refs = findDivisionReferences(division.name, division.patterns, g2Report, 'G2_Report_July_1943');
    g2Index[division.name] = refs;
    g2TotalRefs += refs.length;
    console.log(`  ${division.name}: ${refs.length} references`);
}

console.log(`  Total G2 references: ${g2TotalRefs}`);
console.log();

// Step 3: Index TME 30-420
console.log('Step 3: Indexing TME 30-420 (Italian Military Forces 1943)...');

const tmeIndex = {};
let tmeTotalRefs = 0;

for (const division of targetDivisions) {
    const refs = findDivisionReferences(division.name, division.patterns, tme30420, 'TME_30-420_1943');
    tmeIndex[division.name] = refs;
    tmeTotalRefs += refs.length;
    console.log(`  ${division.name}: ${refs.length} references`);
}

console.log(`  Total TME references: ${tmeTotalRefs}`);
console.log();

// Step 4: Combine and deduplicate
console.log('Step 4: Combining and deduplicating references...');

const combinedIndex = {};

for (const division of targetDivisions) {
    const allRefs = [
        ...(g2Index[division.name] || []),
        ...(tmeIndex[division.name] || [])
    ];

    // Deduplicate based on similar context (simple approach: first 100 chars)
    const seen = new Set();
    const uniqueRefs = [];

    for (const ref of allRefs) {
        const key = ref.context.substring(0, 100).toLowerCase();
        if (!seen.has(key)) {
            seen.add(key);
            uniqueRefs.push(ref);
        }
    }

    combinedIndex[division.name] = uniqueRefs;
    console.log(`  ${division.name}: ${uniqueRefs.length} unique references`);
}

console.log();

// Step 5: Create structured output
console.log('Step 5: Creating structured index...');

const index = {
    metadata: {
        created: new Date().toISOString(),
        sources: [
            {
                name: 'G2_Report_July_1943',
                full_title: 'Order of Battle of the Italian Army (USA HQ G2, July 1943)',
                path: 'Resource Documents/Order-of-battle-of-the-Italian-Army-USA-HQ-G2-July-1943.txt',
                confidence: 90,
                type: 'intelligence_report'
            },
            {
                name: 'TME_30-420_1943',
                full_title: 'Technical Manual E 30-420: Italian Military Forces (1943)',
                path: 'Resource Documents/TME_30_420_Italian_Military_Forces_1943_temp.txt',
                confidence: 90,
                type: 'technical_manual'
            }
        ],
        target_divisions: targetDivisions.map(d => d.name),
        total_references: Object.values(combinedIndex).reduce((sum, refs) => sum + refs.length, 0)
    },
    divisions: {}
};

for (const division of targetDivisions) {
    const refs = combinedIndex[division.name] || [];

    index.divisions[division.name] = {
        name: `${division.name} Division`,
        reference_count: refs.length,
        sources: [...new Set(refs.map(r => r.source))],
        references: refs.map(r => ({
            source: r.source,
            matched_text: r.matched_text,
            context: r.context.substring(0, 500) // Limit context length
        }))
    };
}

// Step 6: Save index
console.log('Step 6: Saving Italian sources index...');

const outputPath = 'data/canonical/ITALIAN_SOURCES_INDEX.json';
fs.writeFileSync(outputPath, JSON.stringify(index, null, 2));

console.log(`  ✅ Index saved: ${outputPath}`);
console.log();

// Step 7: Summary report
console.log('='.repeat(80));
console.log('SUMMARY');
console.log('='.repeat(80));
console.log();
console.log('📊 COVERAGE:');
for (const division of targetDivisions) {
    const count = combinedIndex[division.name].length;
    const status = count > 0 ? '✅' : '❌';
    console.log(`  ${status} ${division.name}: ${count} references`);
}
console.log();
console.log('📚 SOURCES:');
console.log(`  G2 Report (July 1943): ${g2TotalRefs} total references`);
console.log(`  TME 30-420 (1943): ${tmeTotalRefs} total references`);
console.log(`  Combined unique: ${index.metadata.total_references} references`);
console.log();
console.log('🎯 RESULT:');
const coveredDivisions = targetDivisions.filter(d => combinedIndex[d.name].length > 0).length;
console.log(`  ${coveredDivisions}/${targetDivisions.length} divisions have source references`);
console.log();
console.log('Next: Integrate Italian sources index into MASTER_UNIT_DIRECTORY.json');
console.log('='.repeat(80));
