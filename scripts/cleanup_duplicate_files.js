#!/usr/bin/env node

/**
 * Cleanup Duplicate and Orphaned Files
 *
 * Uses the reconciliation report to:
 * 1. Delete duplicate files (keep canonical version only)
 * 2. Delete orphaned files (confirmed not in seed)
 * 3. Move deleted files to _archived for safety
 */

const fs = require('fs').promises;
const path = require('path');

// Known orphaned files to DELETE (confirmed issues)
const ORPHANED_TO_DELETE = [
    // Units destroyed in 1940-Q4 (should NOT exist in 1941-Q1)
    'italian_1941q1_1_divisione_ccnn_23_marzo_toe.json',
    'italian_1941q1_2_divisione_ccnn_28_ottobre_toe.json',
    'italian_1941q1_4_divisione_ccnn_3_gennaio_toe.json',
    'italian_1941q1_1_divisione_libica_toe.json',
    'italian_1941q1_2_divisione_libica_toe.json',

    // German naming variants (should use "90. leichte Division" not "Afrika-Division")
    'german_1941q3_90_leichte_afrika_division_toe.json',
    'german_1941q4_90_leichte_afrika_division_toe.json',
    'german_1942q1_90_leichte_afrika_division_toe.json',
    'german_1942q3_90_leichte_afrika_division_toe.json',
    'german_1942q3_164_leichte_afrika_division_toe.json',
    'german_1942q4_90_leichte_afrika_division_toe.json',

    // Italian naming variants (use English canonical names)
    'italian_1940q2_10_armata_toe.json',
    'italian_1940q3_10a_armata_toe.json',
    'italian_1940q3_10_armata_toe.json',
    'italian_1941q1_xxi_corpo_d_armata_toe.json',
    'italian_1941q2_60_divisione_di_fanteria_sabratha_toe.json',
    'italian_1941q3_101_divisione_motorizzata_trieste_toe.json',
    'italian_1941q4_101_divisione_motorizzata_trieste_toe.json',
    'italian_1941q4_divisione_motorizzata_trieste_toe.json',
    'italian_1941q4_xx_corps_toe.json',
    'italian_1942q3_101_divisione_motorizzata_trieste_toe.json',
    'italian_1942q4_101_divisione_motorizzata_trieste_toe.json',

    // Other naming issues
    'british_1940q4_1_south_african_division_toe.json',  // Missing "st"
    'british_1942q4_46_infantry_division_toe.json',      // Missing "th"
    'french_1942q3_1ere_brigade_francaise_libre_toe.json',  // Accent variation
    'french_1943q1_division_de_marche_du_maroc_toe.json',  // Naming variant

    // Pavia squad file (way too granular for project scope)
    'italian_1941q1_1_squadra_1_compagnia_i_battaglione_27_reggimento_fanteria_pavia_toe.json'
];

async function main() {
    console.log('🧹 Cleaning up duplicate and orphaned files...\n');

    // Load reconciliation report
    const reportPath = path.join(process.cwd(), 'data', 'output', 'qa_reports', 'reconciliation_report.json');
    const report = JSON.parse(await fs.readFile(reportPath, 'utf-8'));

    const unitsDir = path.join(process.cwd(), 'data', 'output', 'units');
    const chaptersDir = path.join(process.cwd(), 'data', 'output', 'chapters');
    const archiveDir = path.join(process.cwd(), 'data', 'output', '_archived', 'cleanup_2025-10-26');

    // Ensure archive directory exists
    await fs.mkdir(path.join(archiveDir, 'units'), { recursive: true });
    await fs.mkdir(path.join(archiveDir, 'chapters'), { recursive: true });

    console.log(`📁 Archive directory: ${archiveDir}\n`);

    // 1. Process duplicates (delete non-canonical versions)
    console.log('🔄 Processing duplicates...\n');
    let duplicatesDeleted = 0;

    for (const dup of report.duplicates) {
        // Keep first file (canonical), delete others
        const toKeep = dup.files[0];
        const toDelete = dup.files.slice(1);

        console.log(`   ${dup.designation} (${dup.canonicalId})`);
        console.log(`   ✅ Keep: ${toKeep}`);

        for (const filename of toDelete) {
            console.log(`   ❌ Delete: ${filename}`);

            const unitFile = path.join(unitsDir, filename);
            const archiveFile = path.join(archiveDir, 'units', filename);

            // Move to archive
            try {
                await fs.rename(unitFile, archiveFile);
                duplicatesDeleted++;
            } catch (err) {
                console.log(`   ⚠️  Could not archive: ${err.message}`);
            }

            // Also archive corresponding chapter file
            const chapterFilename = filename.replace('_toe.json', '.md').replace(/^([a-z]+_\d{4}q\d)_/, 'chapter_$1_');
            const chapterFile = path.join(chaptersDir, chapterFilename);
            const archiveChapter = path.join(archiveDir, 'chapters', chapterFilename);

            try {
                await fs.rename(chapterFile, archiveChapter);
            } catch (err) {
                // Chapter might not exist, that's OK
            }
        }
        console.log('');
    }

    console.log(`✅ Archived ${duplicatesDeleted} duplicate files\n`);

    // 2. Delete confirmed orphaned files
    console.log('🔄 Processing orphaned files...\n');
    let orphansDeleted = 0;

    for (const filename of ORPHANED_TO_DELETE) {
        if (report.orphaned_files.includes(filename)) {
            console.log(`   ❌ Delete orphan: ${filename}`);

            const unitFile = path.join(unitsDir, filename);
            const archiveFile = path.join(archiveDir, 'units', filename);

            try {
                await fs.rename(unitFile, archiveFile);
                orphansDeleted++;
            } catch (err) {
                console.log(`   ⚠️  Could not archive: ${err.message}`);
            }

            // Archive corresponding chapter
            const chapterFilename = filename.replace('_toe.json', '.md').replace(/^([a-z]+_\d{4}q\d)_/, 'chapter_$1_');
            const chapterFile = path.join(chaptersDir, chapterFilename);
            const archiveChapter = path.join(archiveDir, 'chapters', chapterFilename);

            try {
                await fs.rename(chapterFile, archiveChapter);
            } catch (err) {
                // Chapter might not exist, that's OK
            }
        }
    }

    console.log(`✅ Archived ${orphansDeleted} orphaned files\n`);

    // 3. Report remaining orphans (for manual review)
    const remainingOrphans = report.orphaned_files.filter(f => !ORPHANED_TO_DELETE.includes(f));
    if (remainingOrphans.length > 0) {
        console.log(`⚠️  ${remainingOrphans.length} orphaned files require manual review:\n`);
        remainingOrphans.forEach(f => console.log(`   - ${f}`));
        console.log('\nThese files were NOT deleted. Review manually.\n');
    }

    // 4. Summary
    console.log('📊 Cleanup Summary:\n');
    console.log(`   Duplicates archived:      ${duplicatesDeleted}`);
    console.log(`   Orphans archived:         ${orphansDeleted}`);
    console.log(`   Total files archived:     ${duplicatesDeleted + orphansDeleted}`);
    console.log(`   Orphans for review:       ${remainingOrphans.length}\n`);

    console.log('✅ Cleanup complete!\n');
    console.log('Next steps:');
    console.log('1. Run: npm run queue:generate   (regenerate work queue)');
    console.log('2. Review remaining orphans manually');
    console.log('3. Continue extraction with clean state\n');
}

main().catch(error => {
    console.error('❌ Error:', error);
    process.exit(1);
});
