const fs = require('fs');

// Load current matching report
const matchingReport = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf8'));

// Define the 9 false positive matches to remove (different unit numbers)
const falsePositives = [
    // American: Different divisions matched to 1st Infantry
    'american_1943q1_1st_armored_division',    // 1st Armored ≠ 1st Infantry
    'american_1943q1_3rd_infantry_division',   // 3rd ≠ 1st
    'american_1943q1_9th_infantry_division',   // 9th ≠ 1st

    // British: Different division numbers
    'british_1941q1_5th_indian_division',      // 5th ≠ 4th
    'british_1941q3_1st_south_african_division', // 1st ≠ 2nd
    'british_1942q3_1st_armoured_division',    // 1st ≠ 10th

    // German: Different division numbers
    'german_1942q2_15_panzer_division',        // 15 ≠ 21
    'german_1943q1_15_panzer_division',        // 15 ≠ 10
    'german_1943q1_21_panzer_division'         // 21 ≠ 10
];

// Filter out false positives from alias_matches
const validAliasMatches = matchingReport.matches.alias_matches.filter(match => {
    return !falsePositives.includes(match.canonical_id);
});

console.log('Removed false positive matches:');
console.log(`  Before: ${matchingReport.matches.alias_matches.length} alias matches`);
console.log(`  After:  ${validAliasMatches.length} alias matches`);
console.log(`  Removed: ${matchingReport.matches.alias_matches.length - validAliasMatches.length} false positives\n`);

// Add false positives back to no_match array
const falsePositiveEntries = matchingReport.matches.alias_matches
    .filter(match => falsePositives.includes(match.canonical_id))
    .map(match => ({
        canonical_id: match.canonical_id,
        nation: match.nation,
        quarter: match.quarter,
        designation: match.designation
    }));

console.log('False positives moved to no_match:');
for (const entry of falsePositiveEntries) {
    console.log(`  - ${entry.canonical_id}`);
}
console.log();

// Update no_match array (add false positives back)
const updatedNoMatch = [...matchingReport.matches.no_match, ...falsePositiveEntries]
    .sort((a, b) => {
        // Sort by nation, then quarter, then designation
        if (a.nation !== b.nation) return a.nation.localeCompare(b.nation);
        if (a.quarter !== b.quarter) return a.quarter.localeCompare(b.quarter);
        return a.designation.localeCompare(b.designation);
    });

// Update statistics
const exactMatches = matchingReport.matches.exact_matches.length;
const validAliases = validAliasMatches.length;
const totalCompleted = exactMatches + validAliases;
const totalUnits = matchingReport.completion_stats.total_unit_quarters;
const incomplete = totalUnits - totalCompleted;
const completionPercentage = ((totalCompleted / totalUnits) * 100).toFixed(1);

// Calculate by-nation stats
const byNation = {
    american: { total: 14, completed: 0 },
    british: { total: 81, completed: 0 },
    french: { total: 7, completed: 0 },
    german: { total: 46, completed: 0 },
    italian: { total: 67, completed: 0 }
};

// Count exact matches by nation
for (const match of matchingReport.matches.exact_matches) {
    byNation[match.nation].completed++;
}

// Count valid alias matches by nation
for (const match of validAliasMatches) {
    byNation[match.nation].completed++;
}

// Update the report
matchingReport.completion_stats.completed = totalCompleted;
matchingReport.completion_stats.incomplete = incomplete;
matchingReport.completion_stats.completion_percentage = completionPercentage;
matchingReport.completion_stats.exact_matches = exactMatches;
matchingReport.completion_stats.alias_matches = validAliases;
matchingReport.completion_stats.by_nation = byNation;

matchingReport.matches.alias_matches = validAliasMatches;
matchingReport.matches.no_match = updatedNoMatch;

// Add metadata about validation
matchingReport.metadata.validation = {
    validated_at: new Date().toISOString(),
    false_positives_removed: falsePositiveEntries.length,
    validation_method: 'semantic_unit_reasoning',
    note: 'Fuzzy matches validated using military unit identity (unit numbers must match)'
};

// Save updated report
fs.writeFileSync(
    'data/canonical/CANONICAL_MATCHING_REPORT.json',
    JSON.stringify(matchingReport, null, 2)
);

console.log('═══════════════════════════════════════════════════════════');
console.log('UPDATED MATCHING REPORT');
console.log('═══════════════════════════════════════════════════════════\n');

console.log(`Total seed units: ${totalUnits}`);
console.log(`Exact matches: ${exactMatches}`);
console.log(`Valid alias matches: ${validAliases}`);
console.log(`─────────────────────────────────────────────────`);
console.log(`TRUE COMPLETION: ${totalCompleted}/${totalUnits} (${completionPercentage}%)`);
console.log(`Incomplete: ${incomplete}/${totalUnits} (${(100 - parseFloat(completionPercentage)).toFixed(1)}%)\n`);

console.log('Completion by nation:');
for (const [nation, stats] of Object.entries(byNation)) {
    const pct = ((stats.completed / stats.total) * 100).toFixed(1);
    console.log(`  ${nation}: ${stats.completed}/${stats.total} (${pct}%)`);
}

console.log('\n✅ Updated: data/canonical/CANONICAL_MATCHING_REPORT.json');
