#!/usr/bin/env node

/**
 * Cleanup Partial Units - Remove incomplete units after crash
 *
 * Removes partial units (JSON without chapter, or invalid files) so they
 * can be cleanly re-extracted.
 *
 * Usage:
 *   npm run cleanup:partial        # Interactive - shows list, asks for confirmation
 *   npm run cleanup:partial --auto # Automatic - removes all partial units
 *
 * Safety: Creates backup before deletion
 */

const fs = require('fs').promises;
const fssync = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { validateUnitFile } = require('./lib/validator');
const naming = require('./lib/naming_standard');
const paths = require('./lib/canonical_paths');

const PROJECT_ROOT = path.join(__dirname, '..');
const BACKUP_DIR = path.join(PROJECT_ROOT, '.partial_backups');

async function scanPartialUnits() {
    const canonicalUnitsDir = paths.UNITS_DIR;
    const canonicalChaptersDir = paths.CHAPTERS_DIR;

    const partialUnits = [];

    try {
        const files = await fs.readdir(canonicalUnitsDir);

        for (const filename of files) {
            if (filename.endsWith('_toe.json') && !filename.startsWith('unit_')) {
                const parsed = naming.parseFilename(filename);
                if (parsed) {
                    const unitId = `${parsed.nation}_${parsed.quarter}_${parsed.designation}`;

                    // Check if chapter exists
                    const chapterFilename = `chapter_${parsed.nation}_${parsed.quarter}_${parsed.designation}.md`;
                    const chapterPath = path.join(canonicalChaptersDir, chapterFilename);
                    const hasChapter = fssync.existsSync(chapterPath);

                    // Validate JSON
                    const jsonPath = path.join(canonicalUnitsDir, filename);
                    let validationResult = null;
                    try {
                        validationResult = validateUnitFile(jsonPath);
                    } catch (error) {
                        validationResult = { critical: [error.message], warnings: [] };
                    }

                    const isValid = validationResult.critical.length === 0;

                    // Identify partial or invalid units
                    if (!hasChapter || !isValid) {
                        partialUnits.push({
                            unitId,
                            nation: parsed.nation,
                            quarter: parsed.quarter,
                            designation: parsed.designation,
                            jsonFile: filename,
                            jsonPath,
                            chapterPath: hasChapter ? chapterPath : null,
                            hasChapter,
                            isValid,
                            reason: !hasChapter ? 'No chapter' : 'Invalid validation',
                            validationErrors: validationResult.critical
                        });
                    }
                }
            }
        }
    } catch (error) {
        console.error('❌ Failed to scan units directory:', error.message);
    }

    return partialUnits;
}

async function createBackup(partialUnits) {
    // Create backup directory with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = path.join(BACKUP_DIR, `backup_${timestamp}`);

    await fs.mkdir(backupPath, { recursive: true });

    for (const unit of partialUnits) {
        // Backup JSON
        const jsonBackupPath = path.join(backupPath, unit.jsonFile);
        await fs.copyFile(unit.jsonPath, jsonBackupPath);

        // Backup chapter if exists
        if (unit.hasChapter && unit.chapterPath) {
            const chapterFilename = path.basename(unit.chapterPath);
            const chapterBackupPath = path.join(backupPath, chapterFilename);
            await fs.copyFile(unit.chapterPath, chapterBackupPath);
        }
    }

    return backupPath;
}

async function deletePartialUnits(partialUnits) {
    const results = {
        deleted: [],
        failed: []
    };

    for (const unit of partialUnits) {
        try {
            // Delete JSON
            await fs.unlink(unit.jsonPath);
            results.deleted.push(unit.jsonFile);

            // Delete chapter if exists
            if (unit.hasChapter && unit.chapterPath) {
                await fs.unlink(unit.chapterPath);
                results.deleted.push(path.basename(unit.chapterPath));
            }
        } catch (error) {
            results.failed.push({ file: unit.jsonFile, error: error.message });
        }
    }

    return results;
}

async function main() {
    const autoMode = process.argv.includes('--auto');

    console.log('\n🧹 Cleanup Partial Units\n');

    console.log('📂 Scanning for partial/invalid units...');
    const partialUnits = await scanPartialUnits();

    if (partialUnits.length === 0) {
        console.log('✅ No partial or invalid units found - nothing to clean up!\n');
        return;
    }

    console.log(`\n⚠️  Found ${partialUnits.length} partial/invalid units:\n`);

    partialUnits.forEach((u, i) => {
        console.log(`   ${i + 1}. ${u.nation.toUpperCase()} - ${u.quarter} - ${u.designation}`);
        console.log(`      Reason: ${u.reason}`);
        if (u.validationErrors.length > 0) {
            console.log(`      Error: ${u.validationErrors[0]}`);
        }
    });

    console.log('');

    if (!autoMode) {
        console.log('⚠️  These units will be DELETED (backup will be created first)');
        console.log('⚠️  You will need to re-extract them from scratch');
        console.log('\n❓ Do you want to proceed?');
        console.log('   Run with --auto flag to skip this confirmation\n');
        console.log('   Press Ctrl+C to cancel, or run again with --auto to proceed\n');
        return;
    }

    console.log('💾 Creating backup...');
    const backupPath = await createBackup(partialUnits);
    console.log(`   ✅ Backup created: ${backupPath}\n`);

    console.log('🗑️  Deleting partial units...');
    const results = await deletePartialUnits(partialUnits);

    if (results.deleted.length > 0) {
        console.log(`   ✅ Deleted ${results.deleted.length} files\n`);
    }

    if (results.failed.length > 0) {
        console.log(`   ❌ Failed to delete ${results.failed.length} files:\n`);
        results.failed.forEach(f => {
            console.log(`      - ${f.file}: ${f.error}`);
        });
        console.log('');
    }

    console.log('✅ Cleanup complete!\n');
    console.log('📋 Next steps:');
    console.log('   1. Run: npm run recover (verify cleanup)');
    console.log('   2. Run: npm run session:start (to re-extract these units)\n');
}

main().catch(error => {
    console.error('❌ Cleanup failed:', error.message);
    process.exit(1);
});
