#!/usr/bin/env node

/**
 * Generate Re-Extraction Batch for 39 Weak-Source Units
 *
 * Creates structured batch list for session:start autonomous orchestration
 * with strict primary source requirements.
 */

const fs = require('fs');
const path = require('path');

console.log('=== GENERATING RE-EXTRACTION BATCH ===\n');

// Load seed file to get official designations and quarters
const seed = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf-8'));

const nationMap = {
    german: 'german_units',
    italian: 'italian_units',
    british: 'british_units',
    american: 'usa_units',
    french: 'french_units'
};

// Units to re-extract (39 total)
const unitsToReExtract = [
    // 1940-Q3 (3 units)
    { nation: 'british', quarter: '1940q3', seed_designation: '4th Indian Division' },
    { nation: 'italian', quarter: '1940q3', seed_designation: 'Pavia Division' },
    { nation: 'italian', quarter: '1940q3', seed_designation: 'Brescia Division' },

    // 1940-Q4 (4 units)
    { nation: 'british', quarter: '1940q4', seed_designation: '4th Indian Division' },
    { nation: 'italian', quarter: '1940q4', seed_designation: 'Pavia Division' },
    { nation: 'italian', quarter: '1940q4', seed_designation: 'Brescia Division' },
    { nation: 'italian', quarter: '1940q4', seed_designation: 'Savona Division' },

    // 1941-Q1 (9 units)
    { nation: 'british', quarter: '1941q1', seed_designation: '4th Indian Division' },
    { nation: 'british', quarter: '1941q1', seed_designation: '7th Armoured Division' },
    { nation: 'german', quarter: '1941q1', seed_designation: '21. Panzer-Division' },
    { nation: 'german', quarter: '1941q1', seed_designation: '5. leichte Division' },
    { nation: 'german', quarter: '1941q1', seed_designation: '90. leichte Division' },
    { nation: 'italian', quarter: '1941q1', seed_designation: 'Trieste Division' },
    { nation: 'italian', quarter: '1941q1', seed_designation: 'Trento Division' },
    { nation: 'italian', quarter: '1941q1', seed_designation: 'Pavia Division' },
    { nation: 'italian', quarter: '1941q1', seed_designation: 'Brescia Division' },

    // 1941-Q2 (1 unit)
    { nation: 'italian', quarter: '1941q2', seed_designation: 'Trieste Division' },

    // 1941-Q3 (9 units)
    { nation: 'italian', quarter: '1941q3', seed_designation: 'Trieste Division' },
    { nation: 'italian', quarter: '1941q3', seed_designation: 'Trento Division' },
    { nation: 'italian', quarter: '1941q3', seed_designation: 'Ariete Division' },
    { nation: 'italian', quarter: '1941q3', seed_designation: 'Pavia Division' },
    { nation: 'italian', quarter: '1941q3', seed_designation: 'Bologna Division' },
    { nation: 'italian', quarter: '1941q3', seed_designation: 'XX Mobile Corps' },

    // 1941-Q4 (5 units)
    { nation: 'british', quarter: '1941q4', seed_designation: '6th Australian Division' },
    { nation: 'italian', quarter: '1941q4', seed_designation: 'Trieste Division' },
    { nation: 'italian', quarter: '1941q4', seed_designation: 'Ariete Division' },
    { nation: 'italian', quarter: '1941q4', seed_designation: 'Pavia Division' },
    { nation: 'italian', quarter: '1941q4', seed_designation: 'Trento Division' },

    // 1942-Q1 (2 units)
    { nation: 'italian', quarter: '1942q1', seed_designation: 'Ariete Division' },
    { nation: 'french', quarter: '1942q1', seed_designation: '1re Brigade Française Libre' },

    // 1942-Q3 (1 unit)
    { nation: 'french', quarter: '1942q3', seed_designation: '1re Brigade Française Libre' },

    // 1942-Q4 (2 units)
    { nation: 'british', quarter: '1942q4', seed_designation: '1st Parachute Brigade' },
    { nation: 'british', quarter: '1942q4', seed_designation: '1st South African Division' },

    // 1943-Q1 (3 units)
    { nation: 'british', quarter: '1943q1', seed_designation: '51st Highland Division' },
    { nation: 'british', quarter: '1943q1', seed_designation: '6th Armoured Division' },
    { nation: 'german', quarter: '1943q1', seed_designation: '334. Infanterie-Division' }
];

console.log(`Total units for re-extraction: ${unitsToReExtract.length}\n`);

// Enrich with seed data
const enrichedBatch = unitsToReExtract.map(unit => {
    const seedKey = nationMap[unit.nation];
    const seedUnits = seed[seedKey] || [];

    // Find matching seed unit
    const seedUnit = seedUnits.find(su => {
        const designationMatch = su.designation.toLowerCase() === unit.seed_designation.toLowerCase() ||
                                (su.aliases || []).some(a => a.toLowerCase() === unit.seed_designation.toLowerCase());
        const quarterMatch = su.quarters.some(q => q.toLowerCase().replace(/-/g, '') === unit.quarter);
        return designationMatch && quarterMatch;
    });

    return {
        nation: unit.nation,
        quarter: unit.quarter,
        designation: seedUnit ? seedUnit.designation : unit.seed_designation,
        type: seedUnit ? seedUnit.type : 'unknown',
        aliases: seedUnit ? seedUnit.aliases : [],
        required_sources: getRequiredSources(unit.nation, unit.seed_designation),
        priority: getPriority(seedUnit ? seedUnit.type : 'unknown')
    };
});

// Group by priority and quarter
const byPriority = {
    high: enrichedBatch.filter(u => u.priority === 'high'),
    medium: enrichedBatch.filter(u => u.priority === 'medium'),
    low: enrichedBatch.filter(u => u.priority === 'low')
};

console.log('=== BATCH BREAKDOWN ===');
console.log(`High priority (divisions): ${byPriority.high.length}`);
console.log(`Medium priority (brigades/corps): ${byPriority.medium.length}`);
console.log(`Low priority (other): ${byPriority.low.length}\n`);

// Create batches of 3 units each (session:start standard)
const batches = [];
const allUnits = [...byPriority.high, ...byPriority.medium, ...byPriority.low];

for (let i = 0; i < allUnits.length; i += 3) {
    batches.push(allUnits.slice(i, i + 3));
}

console.log(`Created ${batches.length} batches of 3 units each\n`);

// Generate output files
const outputDir = path.join('data', 'output', 'reextraction_batches');
fs.mkdirSync(outputDir, { recursive: true });

// Save batch manifest
const manifest = {
    created_at: new Date().toISOString(),
    total_units: enrichedBatch.length,
    total_batches: batches.length,
    source_requirements: {
        mandatory: [
            'NO Wikipedia sources allowed',
            'Minimum 2 primary sources per unit',
            'Cross-reference all facts between sources',
            'Document confidence levels for all data points'
        ],
        by_nation: {
            german: ['Tessin (mandatory for all German units)', 'Nafziger Collection', 'Feldgrau.net (curated)'],
            italian: ['TM E 30-420 Italian Military Forces', 'Order of Battle Italian Army (US G-2 1943)', 'Nafziger Collection'],
            british: ['British Army Lists (quarterly)', 'Playfair Official History', 'Prasad (Indian forces)', 'Nafziger Collection'],
            american: ['US Field Manuals', 'US Army organizational records', 'Nafziger Collection'],
            french: ['Free French records', 'Nafziger Collection', 'Playfair Official History']
        }
    },
    batches: batches.map((batch, idx) => ({
        batch_number: idx + 1,
        units: batch.map(u => ({
            nation: u.nation,
            quarter: u.quarter,
            designation: u.designation,
            type: u.type,
            required_sources: u.required_sources
        }))
    }))
};

fs.writeFileSync(
    path.join(outputDir, 'REEXTRACTION_MANIFEST.json'),
    JSON.stringify(manifest, null, 2)
);

console.log(`✅ Manifest saved: ${outputDir}/REEXTRACTION_MANIFEST.json\n`);

// Generate session:start prompt
const prompt = generateSessionStartPrompt(batches[0], manifest);

fs.writeFileSync(
    path.join(outputDir, 'SESSION_START_PROMPT.txt'),
    prompt
);

console.log(`✅ Prompt saved: ${outputDir}/SESSION_START_PROMPT.txt\n`);

console.log('=== READY FOR RE-EXTRACTION ===');
console.log('1. Review the manifest and prompt files');
console.log('2. Run: npm run session:start');
console.log('3. Paste the prompt from SESSION_START_PROMPT.txt');
console.log('4. Agents will process Batch 1 (first 3 units) with strict source requirements\n');

// Helper functions
function getRequiredSources(nation, designation) {
    const sources = {
        german: ['Tessin (mandatory)', 'Nafziger Collection'],
        italian: ['TM E 30-420', 'Order of Battle Italian Army', 'Nafziger Collection'],
        british: ['British Army Lists', 'Playfair/Prasad', 'Nafziger Collection'],
        american: ['US Field Manuals', 'Nafziger Collection'],
        french: ['Free French records', 'Nafziger Collection', 'Playfair']
    };
    return sources[nation] || ['Nafziger Collection', 'Primary documents'];
}

function getPriority(type) {
    if (!type) return 'low';
    const t = type.toLowerCase();
    if (t.includes('division')) return 'high';
    if (t.includes('brigade') || t.includes('corps')) return 'medium';
    return 'low';
}

function generateSessionStartPrompt(firstBatch, manifest) {
    return `# RE-EXTRACTION SESSION: Weak Source Units - Batch 1

## 🚨 CRITICAL SOURCE REQUIREMENTS

**ABSOLUTE RULES:**
- ❌ **NO WIKIPEDIA SOURCES ALLOWED** - Any Wikipedia citation = immediate rejection
- ✅ **MINIMUM 2 PRIMARY SOURCES** - Required for all data points
- ✅ **Cross-reference all facts** - No single-source claims
- ✅ **Document confidence levels** - 85%+ for divisions, 80%+ for brigades/corps

## 📚 APPROVED PRIMARY SOURCES BY NATION

**German Units:**
- **Tessin** - Verbände und Truppen der deutschen Wehrmacht (MANDATORY for all German units)
- Nafziger Collection
- Feldgrau.net (curated tier-1 only)

**Italian Units:**
- **TM E 30-420** - Handbook on Italian Military Forces (August 1943)
- Order of Battle of the Italian Army - USA HQ G-2 (July 1943)
- Nafziger Collection

**British Units:**
- **British Army Lists** - Quarterly publications (local Resource Documents/)
- Playfair - Official History Mediterranean & Middle East
- Prasad - Official History Indian Armed Forces
- Nafziger Collection

**American Units:**
- **US Field Manuals** - FM 101-10, TO&E documents
- US Army organizational records
- Nafziger Collection

**French Units:**
- Free French Brigade/Division records
- Nafziger Collection
- Playfair Official History

## 📋 BATCH 1 - UNITS TO EXTRACT (3 units)

${firstBatch.map((unit, idx) => `
### Unit ${idx + 1}: ${unit.designation}

- **Nation**: ${unit.nation.charAt(0).toUpperCase() + unit.nation.slice(1)}
- **Quarter**: ${unit.quarter.toUpperCase().replace(/Q/, '-Q')}
- **Type**: ${unit.type}
- **Required Sources**: ${unit.required_sources.join(', ')}

**Extraction Checklist:**
- [ ] Located ${unit.required_sources[0]} coverage
- [ ] Located ${unit.required_sources[1]} coverage
- [ ] Cross-referenced all equipment counts
- [ ] Verified commander name from 2+ sources
- [ ] Documented all confidence levels
- [ ] NO Wikipedia citations
`).join('\n')}

## 🎯 QUALITY STANDARDS

**validation.source Array Must Include:**
1. Full citation with page numbers/document identifiers
2. Confidence percentage (85%+ required)
3. Tier classification (Tier 1 = 90%+, Tier 2 = 75-89%)
4. Cross-reference notes for conflicting data

**Example Good Source Entry:**
\`\`\`json
"validation": {
  "source": [
    "Tessin, Georg - Verbände und Truppen Band 06, pages 140-141 - 90. leichte Division organization (Tier 1, 95% confidence)",
    "Nafziger Collection OOB 941JKOC - 90. leichte Division Nov 1941 - Equipment counts cross-referenced (Tier 1, 92% confidence)",
    "Feldgrau.net - 90. leichte Division commanders verified against Tessin (Tier 1, 88% confidence)"
  ],
  "confidence": 92
}
\`\`\`

**Example BAD Source Entry (REJECT):**
\`\`\`json
"validation": {
  "source": [
    "Wikipedia: 90th Light Division - formation history",  // ❌ REJECT - Wikipedia not allowed
    "Web search results"  // ❌ REJECT - Not specific enough
  ]
}
\`\`\`

## 🔄 WORKFLOW

1. **Load Source Documents**
   - German: Check Resource Documents/tessin-georg-verbande.../
   - British: Check Resource Documents/Great Britain Ministry of Defense Books/
   - All: Check Resource Documents/Nafziger Collection/

2. **Extract with Cross-Reference**
   - Find unit in Source A → note all data points
   - Find unit in Source B → verify/reconcile with Source A
   - Document any conflicts with resolution reasoning

3. **Validate Output**
   - Run: \`npm run validate\` on each generated file
   - Verify: NO Wikipedia citations
   - Verify: Minimum 2 primary sources
   - Verify: Confidence ≥85% (divisions) or ≥80% (brigades)

4. **Save and Checkpoint**
   - Save to data/output/units/
   - Run: \`npm run checkpoint\`
   - Verify: Validation passes

## 📊 EXPECTED OUTPUT

**Total Time**: 30-45 minutes for 3 units (thorough source cross-referencing)
**Success Criteria**:
- ✅ 3 units extracted
- ✅ 0 Wikipedia citations
- ✅ All units pass validation
- ✅ Average confidence ≥85%

---

**Ready to begin re-extraction with strict source requirements?**

Respond "proceed" to start autonomous extraction of Batch 1.
`;
}
