const fs = require('fs');

const report = JSON.parse(fs.readFileSync('data/canonical/CANONICAL_MATCHING_REPORT.json', 'utf8'));

console.log('═══════════════════════════════════════════════════════════');
console.log('ANALYZING ALIAS MATCH QUALITY');
console.log('═══════════════════════════════════════════════════════════\n');

const problematicMatches = [];
const goodMatches = [];

for (const match of report.matches.alias_matches) {
    // Extract unit numbers from designation and filename
    // For filename, skip the quarter part (e.g., "1941q2")
    const designationNum = match.designation.match(/\d+/g);

    // Remove nation_quarter_ prefix from filename before extracting numbers
    const fileWithoutPrefix = match.matched_file
        .replace(/^(american|british|french|german|italian)_\d{4}q\d_/, '');
    const fileNum = fileWithoutPrefix.match(/\d+/g);

    const desgStr = designationNum ? designationNum.sort().join('_') : 'none';
    const fileStr = fileNum ? fileNum.sort().join('_') : 'none';

    if (desgStr !== fileStr) {
        problematicMatches.push({
            ...match,
            desgNum: desgStr,
            fileNum: fileStr
        });
    } else {
        goodMatches.push(match);
    }
}

console.log('🚨 PROBLEMATIC FUZZY MATCHES (different unit numbers):');
console.log(`   Found ${problematicMatches.length} false positives\n`);
for (const m of problematicMatches) {
    console.log(`   ❌ ${m.canonical_id}`);
    console.log(`      Designation: ${m.designation} [nums: ${m.desgNum}]`);
    console.log(`      Matched file: ${m.matched_file} [nums: ${m.fileNum}]`);
    console.log();
}

console.log(`\n✅ VALID FUZZY MATCHES (same unit number, different wording):`);
console.log(`   Found ${goodMatches.length} correct alias matches\n`);
for (const m of goodMatches.slice(0, 10)) {
    console.log(`   ✓ ${m.designation} → ${m.matched_file}`);
}
if (goodMatches.length > 10) {
    console.log(`   ... and ${goodMatches.length - 10} more`);
}

console.log(`\n═══════════════════════════════════════════════════════════`);
console.log(`CORRECTED COMPLETION STATS:`);
console.log(`═══════════════════════════════════════════════════════════`);
console.log(`Exact matches: ${report.completion_stats.exact_matches}`);
console.log(`Valid alias matches: ${goodMatches.length}`);
console.log(`False positive matches: ${problematicMatches.length}`);
console.log(`\nTrue completion: ${report.completion_stats.exact_matches + goodMatches.length}/215 (${((report.completion_stats.exact_matches + goodMatches.length) / 215 * 100).toFixed(1)}%)`);
console.log(`Incomplete: ${215 - (report.completion_stats.exact_matches + goodMatches.length)}`);
