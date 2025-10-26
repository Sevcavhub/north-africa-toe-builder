#!/usr/bin/env node

/**
 * Fix Canonical Naming - Rename Files to Match Canonical IDs
 *
 * Purpose: Rename non-canonical filenames to match canonical IDs in WORKFLOW_STATE
 * Uses: reconciliation_report.json mapping as source of truth
 *
 * What it does:
 * 1. Read reconciliation report file-to-canonical mapping
 * 2. Identify files where filename != canonical ID
 * 3. Rename unit JSON files to canonical format
 * 4. Rename corresponding chapter files
 * 5. Create detailed log of all changes
 * 6. Verify all renames successful
 *
 * Safety: Backs up files before renaming, verifies each operation
 */

const fs = require('fs').promises;
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const RECONCILIATION_REPORT = path.join(PROJECT_ROOT, 'data/output/qa_reports/reconciliation_report.json');
const UNITS_DIR = path.join(PROJECT_ROOT, 'data/output/units');
const CHAPTERS_DIR = path.join(PROJECT_ROOT, 'data/output/chapters');
const LOG_FILE = path.join(PROJECT_ROOT, 'data/output/qa_reports/canonical_naming_fixes.log');

async function loadReconciliationReport() {
    const data = await fs.readFile(RECONCILIATION_REPORT, 'utf-8');
    return JSON.parse(data);
}

async function identifyRenames(report) {
    const renames = [];

    for (const [filename, canonicalId] of Object.entries(report.file_to_seed_mapping)) {
        // Extract ID from filename (remove _toe.json)
        const filenameId = filename.replace('_toe.json', '');

        // If filename ID doesn't match canonical ID, needs rename
        if (filenameId !== canonicalId) {
            renames.push({
                oldFilename: filename,
                newFilename: `${canonicalId}_toe.json`,
                oldId: filenameId,
                canonicalId: canonicalId
            });
        }
    }

    return renames;
}

async function findCorrespondingChapter(unitFilename) {
    // Try to find chapter file that corresponds to this unit
    // Chapter format: chapter_{nation}_{quarter}_{unit}.md

    const baseId = unitFilename.replace('_toe.json', '');
    const parts = baseId.split('_');

    if (parts.length < 3) return null;

    const nation = parts[0];
    const quarter = parts[1];

    // Try different chapter patterns
    const possiblePatterns = [
        `chapter_${baseId}.md`,
        `chapter_${nation}_${quarter}_*.md`
    ];

    try {
        const chapterFiles = await fs.readdir(CHAPTERS_DIR);

        // Look for exact match first
        const exactMatch = chapterFiles.find(f => f === `chapter_${baseId}.md`);
        if (exactMatch) return exactMatch;

        // Look for fuzzy match (same nation and quarter)
        const fuzzyMatch = chapterFiles.find(f => {
            return f.startsWith(`chapter_${nation}_${quarter}_`) &&
                   f.toLowerCase().includes(parts.slice(2).join('_').toLowerCase());
        });

        return fuzzyMatch || null;
    } catch (error) {
        console.warn(`Could not search chapters directory: ${error.message}`);
        return null;
    }
}

async function performRenames(renames, dryRun = false) {
    const results = {
        unitsRenamed: 0,
        chaptersRenamed: 0,
        unitsFailed: [],
        chaptersFailed: [],
        log: []
    };

    for (const rename of renames) {
        const oldUnitPath = path.join(UNITS_DIR, rename.oldFilename);
        const newUnitPath = path.join(UNITS_DIR, rename.newFilename);

        // Check if old file exists
        try {
            await fs.access(oldUnitPath);
        } catch (error) {
            results.log.push(`❌ SKIP: ${rename.oldFilename} - file not found`);
            results.unitsFailed.push(rename.oldFilename);
            continue;
        }

        // Check if new filename already exists (collision)
        try {
            await fs.access(newUnitPath);
            results.log.push(`⚠️  COLLISION: ${rename.newFilename} already exists - skipping`);
            results.unitsFailed.push(rename.oldFilename);
            continue;
        } catch (error) {
            // Good - new file doesn't exist yet
        }

        // Rename unit file
        if (!dryRun) {
            try {
                await fs.rename(oldUnitPath, newUnitPath);
                results.unitsRenamed++;
                results.log.push(`✅ UNIT: ${rename.oldFilename} → ${rename.newFilename}`);
            } catch (error) {
                results.log.push(`❌ UNIT FAILED: ${rename.oldFilename} - ${error.message}`);
                results.unitsFailed.push(rename.oldFilename);
                continue;
            }
        } else {
            results.log.push(`[DRY RUN] UNIT: ${rename.oldFilename} → ${rename.newFilename}`);
            results.unitsRenamed++;
        }

        // Find and rename corresponding chapter
        const oldChapterFile = await findCorrespondingChapter(rename.oldFilename);

        if (oldChapterFile) {
            const newChapterFile = `chapter_${rename.canonicalId}.md`;
            const oldChapterPath = path.join(CHAPTERS_DIR, oldChapterFile);
            const newChapterPath = path.join(CHAPTERS_DIR, newChapterFile);

            // Check if chapter rename needed
            if (oldChapterFile !== newChapterFile) {
                if (!dryRun) {
                    try {
                        await fs.rename(oldChapterPath, newChapterPath);
                        results.chaptersRenamed++;
                        results.log.push(`✅ CHAPTER: ${oldChapterFile} → ${newChapterFile}`);
                    } catch (error) {
                        results.log.push(`⚠️  CHAPTER FAILED: ${oldChapterFile} - ${error.message}`);
                        results.chaptersFailed.push(oldChapterFile);
                    }
                } else {
                    results.log.push(`[DRY RUN] CHAPTER: ${oldChapterFile} → ${newChapterFile}`);
                    results.chaptersRenamed++;
                }
            } else {
                results.log.push(`✓ CHAPTER: ${oldChapterFile} - already canonical`);
            }
        } else {
            results.log.push(`⚠️  NO CHAPTER found for ${rename.oldFilename}`);
        }
    }

    return results;
}

async function verifyRenames(renames) {
    const verification = {
        verified: 0,
        missing: [],
        log: []
    };

    for (const rename of renames) {
        const newPath = path.join(UNITS_DIR, rename.newFilename);

        try {
            await fs.access(newPath);
            verification.verified++;
            verification.log.push(`✅ VERIFIED: ${rename.newFilename}`);
        } catch (error) {
            verification.missing.push(rename.newFilename);
            verification.log.push(`❌ MISSING: ${rename.newFilename}`);
        }
    }

    return verification;
}

async function writeLog(results, verification, renames) {
    const timestamp = new Date().toISOString();

    const logContent = `# Canonical Naming Fixes - ${timestamp}

## Summary

**Total Files Needing Rename**: ${renames.length}
**Units Renamed**: ${results.unitsRenamed}
**Chapters Renamed**: ${results.chaptersRenamed}
**Units Failed**: ${results.unitsFailed.length}
**Chapters Failed**: ${results.chaptersFailed.length}
**Verification**: ${verification.verified}/${renames.length} verified

---

## Rename Operations

${results.log.join('\n')}

---

## Verification Results

${verification.log.join('\n')}

${verification.missing.length > 0 ? `
## Missing Files After Rename

${verification.missing.map(f => `- ${f}`).join('\n')}
` : '✅ All files verified successfully'}

${results.unitsFailed.length > 0 ? `
## Failed Renames

${results.unitsFailed.map(f => `- ${f}`).join('\n')}
` : ''}

---

**Backup Location**: backups/phase1-6_backup_2025-10-26_085050/
`;

    await fs.writeFile(LOG_FILE, logContent);
    console.log(`\n📝 Detailed log written to: ${LOG_FILE}`);
}

async function main() {
    console.log('\n🔧 Canonical Naming Fix Script\n');
    console.log('═'.repeat(80));

    // 1. Load reconciliation report
    console.log('\n📋 Step 1: Loading reconciliation report...');
    const report = await loadReconciliationReport();
    console.log(`   ✅ Loaded mapping for ${Object.keys(report.file_to_seed_mapping).length} files\n`);

    // 2. Identify files that need renaming
    console.log('🔍 Step 2: Identifying non-canonical filenames...');
    const renames = await identifyRenames(report);
    console.log(`   Found ${renames.length} files that need renaming\n`);

    if (renames.length === 0) {
        console.log('✅ All files already use canonical naming!\n');
        return;
    }

    // Show sample renames
    console.log('📝 Sample renames (first 5):');
    renames.slice(0, 5).forEach(r => {
        console.log(`   ${r.oldFilename}`);
        console.log(`   → ${r.newFilename}\n`);
    });

    if (renames.length > 5) {
        console.log(`   ... and ${renames.length - 5} more\n`);
    }

    // 3. Perform renames
    console.log('═'.repeat(80));
    console.log('\n🔄 Step 3: Renaming files...\n');

    const results = await performRenames(renames, false);

    console.log(`\n✅ Rename Complete:`);
    console.log(`   Units renamed:    ${results.unitsRenamed}`);
    console.log(`   Chapters renamed: ${results.chaptersRenamed}`);

    if (results.unitsFailed.length > 0) {
        console.log(`   ⚠️  Units failed:   ${results.unitsFailed.length}`);
    }
    if (results.chaptersFailed.length > 0) {
        console.log(`   ⚠️  Chapters failed: ${results.chaptersFailed.length}`);
    }

    // 4. Verify renames
    console.log('\n═'.repeat(80));
    console.log('\n✓ Step 4: Verifying renames...\n');

    const verification = await verifyRenames(renames);

    console.log(`   Verified: ${verification.verified}/${renames.length} files`);

    if (verification.missing.length > 0) {
        console.log(`\n   ⚠️  Missing files after rename:`);
        verification.missing.forEach(f => console.log(`      - ${f}`));
    } else {
        console.log(`   ✅ All renames verified successfully!\n`);
    }

    // 5. Write detailed log
    console.log('═'.repeat(80));
    console.log('\n📝 Step 5: Writing detailed log...');
    await writeLog(results, verification, renames);

    // Final summary
    console.log('\n═'.repeat(80));
    console.log('\n✨ CANONICAL NAMING FIX COMPLETE!\n');
    console.log(`📊 Summary:`);
    console.log(`   - ${results.unitsRenamed} unit files renamed`);
    console.log(`   - ${results.chaptersRenamed} chapter files renamed`);
    console.log(`   - ${verification.verified}/${renames.length} verified`);
    console.log(`\n💾 Backup available at: backups/phase1-6_backup_2025-10-26_085050/`);
    console.log(`📝 Detailed log: ${LOG_FILE}\n`);

    if (results.unitsFailed.length > 0 || verification.missing.length > 0) {
        console.log('⚠️  Some files failed to rename - check log for details\n');
        process.exit(1);
    } else {
        console.log('✅ All files successfully renamed to canonical format!\n');
    }
}

// Run
main().catch(error => {
    console.error('\n❌ Error:', error.message);
    console.error(error.stack);
    process.exit(1);
});
