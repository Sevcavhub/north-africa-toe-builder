#!/usr/bin/env node

/**
 * Phase 4: Canonical Master Matcher
 *
 * Purpose: Match completed canonical units against MASTER_UNIT_DIRECTORY.json
 *
 * Matching Strategy:
 * - Exact canonical ID matching (no fuzzy logic)
 * - Alias-based matching for naming variations
 * - Scans canonical output location: data/output/units/
 *
 * Output: Completion report showing which seed units are done
 */

const fs = require('fs');
const path = require('path');

console.log('='.repeat(80));
console.log('PHASE 4: CANONICAL MASTER MATCHER');
console.log('='.repeat(80));
console.log();

// Step 1: Load master directory
console.log('Step 1: Loading MASTER_UNIT_DIRECTORY.json...');
const masterDirectory = JSON.parse(fs.readFileSync('data/canonical/MASTER_UNIT_DIRECTORY.json', 'utf8'));

console.log(`  ✅ Loaded ${masterDirectory.canonical_units.length} unit-quarters`);
console.log(`  ✅ ${masterDirectory.metadata.total_units} unique units`);
console.log();

// Step 2: Scan canonical output location for completed units
console.log('Step 2: Scanning canonical output location (data/output/units/)...');

const canonicalUnitsDir = 'data/output/units/';
const completedFiles = [];

if (fs.existsSync(canonicalUnitsDir)) {
    const files = fs.readdirSync(canonicalUnitsDir);
    for (const file of files) {
        if (file.endsWith('_toe.json')) {
            completedFiles.push(file);
        }
    }
}

console.log(`  ✅ Found ${completedFiles.length} completed unit files`);
console.log();

// Step 3: Extract canonical IDs from completed files
console.log('Step 3: Extracting canonical IDs from completed files...');

const completedCanonicalIds = new Set();
const completedUnitData = [];

for (const file of completedFiles) {
    const filePath = path.join(canonicalUnitsDir, file);

    try {
        const unitData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        // Extract canonical ID from filename (format: nation_quarter_designation_toe.json)
        const canonicalId = file.replace('_toe.json', '');

        completedCanonicalIds.add(canonicalId);
        completedUnitData.push({
            canonical_id: canonicalId,
            file: file,
            unit_data: unitData
        });
    } catch (err) {
        console.log(`  ⚠️  Failed to read ${file}: ${err.message}`);
    }
}

console.log(`  ✅ Extracted ${completedCanonicalIds.size} canonical IDs`);
console.log();

// Step 4: Match completed units against master directory using ALIASES
console.log('Step 4: Matching completed units against master directory (using aliases)...');

const matches = {
    exact_matches: [],
    alias_matches: [],
    no_match: []
};

// Helper: Extract designation from JSON content (not filename!)
function extractDesignationFromUnit(unitData, filename) {
    // Remove _toe.json suffix
    const withoutSuffix = filename.replace('_toe.json', '');

    // Extract from JSON content
    const nation = unitData.nation;
    const quarter = (unitData.quarter || '').toLowerCase().replace(/-/g, ''); // Normalize: 1941-Q1 → 1941q1
    const designation = unitData.unit_designation || unitData.designation;

    if (!nation || !quarter || !designation) {
        console.log(`    ⚠️  Missing fields in ${filename}: nation=${nation}, quarter=${quarter}, designation=${designation}`);
        return null;
    }

    return { nation, quarter, designation, canonical_id: withoutSuffix };
}

// Create lookup map: completed file → extracted info from JSON content
const completedFilesMap = new Map();
for (const completedUnit of completedUnitData) {
    const info = extractDesignationFromUnit(completedUnit.unit_data, completedUnit.file);
    if (info) {
        completedFilesMap.set(completedUnit.file, info);
    }
}

// Match each master unit
for (const masterUnit of masterDirectory.canonical_units) {
    let matched = false;
    let matchedFile = null;
    let matchType = null;

    // First: Try exact canonical ID match
    if (completedCanonicalIds.has(masterUnit.canonical_id)) {
        matched = true;
        matchedFile = `${masterUnit.canonical_id}_toe.json`;
        matchType = 'exact';
    }

    // Second: Try alias matching
    if (!matched) {
        for (const [file, fileInfo] of completedFilesMap.entries()) {
            // Must match nation and quarter first
            if (fileInfo.nation !== masterUnit.nation || fileInfo.quarter !== masterUnit.quarter) {
                continue;
            }

            // Check if file designation matches any alias
            let fileDesignationLower = fileInfo.designation.toLowerCase();

            // Special handling for Italian units: extract division name from patterns like:
            // "25ª Divisione di Fanteria 'Bologna'" → "bologna division"
            // "61ª Divisione di Fanteria "Sirte"" → "sirte division"
            // "132 Divisione Corazzata Ariete" → "ariete division"
            let extractedItalianName = null;
            if (fileInfo.nation === 'italian') {
                // Pattern 1: Name in quotes (BOTH single AND double quotes)
                const quotedMatch = fileDesignationLower.match(/['"]([^'"]+)['"]/);
                if (quotedMatch) {
                    extractedItalianName = quotedMatch[1] + ' division';
                } else {
                    // Pattern 2: Last word after division type (e.g., "Divisione Corazzata Ariete" → "ariete")
                    const divMatch = fileDesignationLower.match(/divisione?\s+\w+\s+(\w+)/);
                    if (divMatch) {
                        extractedItalianName = divMatch[1] + ' division';
                    }
                }
            }

            for (const alias of masterUnit.aliases) {
                const aliasLower = alias.toLowerCase();

                // Exact match
                if (fileDesignationLower === aliasLower) {
                    matched = true;
                    matchedFile = file;
                    matchType = 'alias_exact';
                    break;
                }

                // Italian: Try extracted name
                if (extractedItalianName && extractedItalianName === aliasLower) {
                    matched = true;
                    matchedFile = file;
                    matchType = 'alias_italian_extracted';
                    break;
                }

                // Fuzzy match: check if all significant words match
                const aliasWords = aliasLower.split(/\s+/).filter(w => w.length > 2);
                const fileWords = fileDesignationLower.split(/\s+/).filter(w => w.length > 2);

                const matchCount = aliasWords.filter(aw => fileWords.includes(aw)).length;
                const matchRatio = matchCount / Math.max(aliasWords.length, fileWords.length);

                if (matchRatio >= 0.6) { // 60% word overlap (lowered to catch variations like "4th Indian Infantry Division" vs "4th Indian Division")
                    matched = true;
                    matchedFile = file;
                    matchType = 'alias_fuzzy';
                    break;
                }
            }

            if (matched) break;
        }
    }

    if (matched) {
        const matchData = {
            canonical_id: masterUnit.canonical_id,
            nation: masterUnit.nation,
            quarter: masterUnit.quarter,
            designation: masterUnit.designation,
            matched_file: matchedFile,
            match_type: matchType
        };

        if (matchType === 'exact') {
            matches.exact_matches.push(matchData);
        } else {
            matches.alias_matches.push(matchData);
        }
    } else {
        matches.no_match.push({
            canonical_id: masterUnit.canonical_id,
            nation: masterUnit.nation,
            quarter: masterUnit.quarter,
            designation: masterUnit.designation
        });
    }
}

let totalMatches = matches.exact_matches.length + matches.alias_matches.length;
console.log(`  ✅ Exact canonical ID matches: ${matches.exact_matches.length}`);
console.log(`  ✅ Alias matches: ${matches.alias_matches.length}`);
console.log(`  ✅ Total matches: ${totalMatches}`);
console.log(`  ⚠️  No match: ${matches.no_match.length}`);
console.log();

// Step 5: Calculate completion statistics
console.log('Step 5: Calculating completion statistics...');

const completionStats = {
    total_unit_quarters: masterDirectory.canonical_units.length,
    completed: totalMatches,
    incomplete: matches.no_match.length,
    completion_percentage: (totalMatches / masterDirectory.canonical_units.length * 100).toFixed(1),
    exact_matches: matches.exact_matches.length,
    alias_matches: matches.alias_matches.length
};

// By nation
const byNation = {};
const allMatchedIds = new Set([
    ...matches.exact_matches.map(m => m.canonical_id),
    ...matches.alias_matches.map(m => m.canonical_id)
]);

for (const unit of masterDirectory.canonical_units) {
    if (!byNation[unit.nation]) {
        byNation[unit.nation] = { total: 0, completed: 0 };
    }
    byNation[unit.nation].total++;
    if (allMatchedIds.has(unit.canonical_id)) {
        byNation[unit.nation].completed++;
    }
}

// By unique unit
const uniqueUnits = {};
for (const unit of masterDirectory.canonical_units) {
    if (!uniqueUnits[unit.designation]) {
        uniqueUnits[unit.designation] = {
            nation: unit.nation,
            total_quarters: 0,
            completed_quarters: 0
        };
    }
    uniqueUnits[unit.designation].total_quarters++;
    if (allMatchedIds.has(unit.canonical_id)) {
        uniqueUnits[unit.designation].completed_quarters++;
    }
}

completionStats.by_nation = byNation;
completionStats.by_unique_unit = uniqueUnits;

console.log(`  ✅ Overall completion: ${completionStats.completion_percentage}%`);
console.log();

// Step 6: Save matching report
console.log('Step 6: Saving matching report...');

const report = {
    metadata: {
        created: new Date().toISOString(),
        master_directory_version: masterDirectory.metadata.version,
        total_unit_quarters: masterDirectory.canonical_units.length,
        completed_files_scanned: completedFiles.length
    },
    completion_stats: completionStats,
    matches: {
        exact_matches: matches.exact_matches,
        alias_matches: matches.alias_matches,
        no_match: matches.no_match
    }
};

fs.writeFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', JSON.stringify(report, null, 2));

console.log('  ✅ Report saved: data/canonical/CANONICAL_MATCHING_REPORT.json');
console.log();

// Step 7: Display summary
console.log('='.repeat(80));
console.log('SUMMARY');
console.log('='.repeat(80));
console.log();
console.log('📊 OVERALL COMPLETION:');
console.log(`  Total unit-quarters: ${completionStats.total_unit_quarters}`);
console.log(`  Completed: ${completionStats.completed} (${completionStats.exact_matches} exact + ${completionStats.alias_matches} alias)`);
console.log(`  Incomplete: ${completionStats.incomplete}`);
console.log(`  Completion: ${completionStats.completion_percentage}%`);
console.log();

console.log('🌍 COMPLETION BY NATION:');
for (const [nation, stats] of Object.entries(byNation)) {
    const pct = (stats.completed / stats.total * 100).toFixed(1);
    const status = stats.completed === stats.total ? '✅' :
                   stats.completed > 0 ? '⚠️' : '❌';
    console.log(`  ${status} ${nation}: ${stats.completed}/${stats.total} (${pct}%)`);
}
console.log();

console.log('📋 COMPLETION BY UNIQUE UNIT:');
const sortedUnits = Object.entries(uniqueUnits).sort((a, b) => {
    // Sort by nation first, then by completion percentage
    if (a[1].nation !== b[1].nation) return a[1].nation.localeCompare(b[1].nation);
    const pctA = a[1].completed_quarters / a[1].total_quarters;
    const pctB = b[1].completed_quarters / b[1].total_quarters;
    return pctB - pctA; // Higher completion first
});

for (const [designation, stats] of sortedUnits) {
    const pct = (stats.completed_quarters / stats.total_quarters * 100).toFixed(0);
    const status = stats.completed_quarters === stats.total_quarters ? '✅' :
                   stats.completed_quarters > 0 ? '⚠️' : '❌';
    console.log(`  ${status} ${designation}: ${stats.completed_quarters}/${stats.total_quarters} quarters (${pct}%)`);
}
console.log();

console.log('🎯 NEXT STEPS:');
if (completionStats.incomplete > 0) {
    console.log(`  - ${completionStats.incomplete} unit-quarters need extraction`);
    console.log(`  - Use autonomous extraction workflow for remaining units`);
} else {
    console.log('  - All seed units complete! Ready for Phase 5: Quality validation');
}
console.log();
console.log('='.repeat(80));
