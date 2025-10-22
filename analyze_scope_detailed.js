const fs = require('fs');
const state = require('./WORKFLOW_STATE.json');
const seed = require('./projects/north_africa_seed_units_COMPLETE.json');

// Build set of all seed unit IDs - CORRECTED with usa_units
const seedUnitIds = new Set();
const nations = {
    german_units: 'german',
    italian_units: 'italian',
    british_units: 'british',
    usa_units: 'american',  // ✅ CORRECTED: seed uses usa_units, files use american
    french_units: 'french'
};

for (const [key, nation] of Object.entries(nations)) {
    const units = seed[key] || [];
    units.forEach(unit => {
        unit.quarters.forEach(quarter => {
            const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');
            const normalizedDesignation = unit.designation.toLowerCase()
                .replace(/[^a-z0-9]+/g, '_')
                .replace(/^_+|_+$/g, '');
            const unitId = `${nation}_${normalizedQuarter}_${normalizedDesignation}`;
            seedUnitIds.add(unitId);
        });
    });
}

console.log('Total seed unit-quarters:', seedUnitIds.size);
console.log('Total completed files:', state.completed.length);

// Categorize completed units
const inScope = [];
const outOfScope = [];

state.completed.forEach(unitId => {
    if (seedUnitIds.has(unitId)) {
        inScope.push(unitId);
    } else {
        outOfScope.push(unitId);
    }
});

console.log('\n✅ In-scope (match seed):', inScope.length);
console.log('❌ Out-of-scope (NOT in seed):', outOfScope.length);

// Analyze out-of-scope patterns
console.log('\n=== ANALYZING OUT-OF-SCOPE UNITS ===\n');

const categories = {
    naming_variants: [],
    possible_duplicates: [],
    truly_unknown: []
};

outOfScope.forEach(id => {
    const parts = id.split('_');
    const nation = parts[0];
    const quarter = parts[1];
    const designation = parts.slice(2).join('_');

    // Check if there's a similar unit in seed (possible naming variant)
    let foundSimilar = false;
    for (const seedId of seedUnitIds) {
        if (seedId.startsWith(`${nation}_${quarter}_`)) {
            const seedDesignation = seedId.split('_').slice(2).join('_');

            // Check for common naming patterns
            if (designation.includes(seedDesignation) || seedDesignation.includes(designation)) {
                categories.naming_variants.push({
                    file: id,
                    seedMatch: seedId
                });
                foundSimilar = true;
                break;
            }
        }
    }

    if (!foundSimilar) {
        // Check if there's another file with similar name (duplicate)
        const similar = state.completed.filter(otherId => {
            if (otherId === id) return false;
            const otherParts = otherId.split('_');
            const otherNation = otherParts[0];
            const otherQuarter = otherParts[1];
            const otherDesignation = otherParts.slice(2).join('_');

            return otherNation === nation &&
                   otherQuarter === quarter &&
                   (designation.includes(otherDesignation) || otherDesignation.includes(designation));
        });

        if (similar.length > 0) {
            categories.possible_duplicates.push({
                file: id,
                duplicateOf: similar
            });
        } else {
            categories.truly_unknown.push(id);
        }
    }
});

console.log('📝 Naming variants (file name differs from seed):', categories.naming_variants.length);
console.log('🔄 Possible duplicates (multiple files for same unit):', categories.possible_duplicates.length);
console.log('❓ Truly unknown (not in seed at all):', categories.truly_unknown.length);

console.log('\n=== NAMING VARIANTS (first 15) ===');
categories.naming_variants.slice(0, 15).forEach(item => {
    console.log(`\nFile:     ${item.file}`);
    console.log(`Seed:     ${item.seedMatch}`);
});

console.log('\n\n=== POSSIBLE DUPLICATES (first 10) ===');
categories.possible_duplicates.slice(0, 10).forEach(item => {
    console.log(`\nOut-of-scope: ${item.file}`);
    console.log(`Duplicates:   ${item.duplicateOf.join(', ')}`);
});

console.log('\n\n=== TRULY UNKNOWN UNITS (first 15) ===');
categories.truly_unknown.slice(0, 15).forEach(id => {
    console.log(`  - ${id}`);
});
