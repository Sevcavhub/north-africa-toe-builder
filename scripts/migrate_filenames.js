#!/usr/bin/env node

/**
 * Migrate Filenames - Rename all unit files to canonical naming standard
 *
 * Scans all unit files and renames them to follow the canonical naming standard:
 * - Nation: adjective form (german, italian, british, american, french)
 * - Quarter: lowercase, no hyphen (1941q2)
 * - Designation: normalized with underscores
 *
 * Usage:
 *   node scripts/migrate_filenames.js --dry-run    # Preview changes
 *   node scripts/migrate_filenames.js              # Execute rename
 *
 * IMPORTANT: This will rename files in place. Commit your work before running.
 */

const fs = require('fs');
const path = require('path');
const naming = require('./lib/naming_standard');

const PROJECT_ROOT = path.join(__dirname, '..');
const OUTPUT_DIR = path.join(PROJECT_ROOT, 'data/output');

const isDryRun = process.argv.includes('--dry-run');

function scanAllUnitFiles() {
    const files = [];

    function scanDir(dir) {
        try {
            const items = fs.readdirSync(dir, { withFileTypes: true });
            for (const item of items) {
                const fullPath = path.join(dir, item.name);
                if (item.isDirectory()) {
                    scanDir(fullPath);
                } else if (item.name.endsWith('_toe.json') && !item.name.startsWith('unit_')) {
                    files.push({
                        path: fullPath,
                        filename: item.name,
                        dir: dir
                    });
                }
            }
        } catch (error) {
            console.warn(`⚠️  Could not scan ${dir}: ${error.message}`);
        }
    }

    scanDir(OUTPUT_DIR);
    return files;
}

function analyzeFile(file) {
    // Parse the current filename
    const parsed = naming.parseFilename(file.filename);

    if (!parsed) {
        return {
            status: 'invalid',
            reason: 'Could not parse filename format',
            original: file.filename
        };
    }

    // Read the file to get actual unit data for verification
    let unitData = null;
    try {
        const content = fs.readFileSync(file.path, 'utf-8');
        unitData = JSON.parse(content);
    } catch (error) {
        return {
            status: 'error',
            reason: `Could not read JSON: ${error.message}`,
            original: file.filename
        };
    }

    // Verify filename matches content
    if (unitData.nation && unitData.quarter && unitData.unit_designation) {
        const canonicalFilename = naming.generateFilename(
            unitData.nation,
            unitData.quarter,
            unitData.unit_designation
        );

        if (canonicalFilename === file.filename) {
            return {
                status: 'correct',
                original: file.filename,
                canonical: canonicalFilename
            };
        } else {
            return {
                status: 'needs_rename',
                original: file.filename,
                canonical: canonicalFilename,
                path: file.path,
                dir: file.dir,
                changes: {
                    nation: naming.normalizeNation(parsed.nation) !== parsed.nation ? `${parsed.nation} → ${naming.normalizeNation(parsed.nation)}` : null,
                    quarter: naming.normalizeQuarter(parsed.quarter) !== parsed.quarter ? `${parsed.quarter} → ${naming.normalizeQuarter(parsed.quarter)}` : null
                }
            };
        }
    } else {
        // Filename parsed but JSON data incomplete - use parsed data to generate canonical
        const canonicalFilename = naming.generateFilename(
            parsed.nation,
            parsed.quarter,
            parsed.designation
        );

        if (canonicalFilename === file.filename) {
            return {
                status: 'correct',
                original: file.filename,
                canonical: canonicalFilename,
                warning: 'JSON data incomplete but filename correct'
            };
        } else {
            return {
                status: 'needs_rename',
                original: file.filename,
                canonical: canonicalFilename,
                path: file.path,
                dir: file.dir,
                warning: 'JSON data incomplete, using parsed filename data',
                changes: {
                    nation: naming.normalizeNation(parsed.nation) !== parsed.nation ? `${parsed.nation} → ${naming.normalizeNation(parsed.nation)}` : null,
                    quarter: naming.normalizeQuarter(parsed.quarter) !== parsed.quarter ? `${parsed.quarter} → ${naming.normalizeQuarter(parsed.quarter)}` : null
                }
            };
        }
    }
}

function renameFile(analysis) {
    const oldPath = analysis.path;
    const newPath = path.join(analysis.dir, analysis.canonical);

    // Check if target already exists
    if (fs.existsSync(newPath)) {
        console.error(`   ❌ CONFLICT: ${analysis.canonical} already exists!`);
        return false;
    }

    try {
        fs.renameSync(oldPath, newPath);
        return true;
    } catch (error) {
        console.error(`   ❌ FAILED: ${error.message}`);
        return false;
    }
}

function main() {
    console.log('\n' + '═'.repeat(80));
    console.log('  🔄 FILENAME MIGRATION - Canonical Naming Standard');
    console.log('═'.repeat(80));
    console.log('');

    if (isDryRun) {
        console.log('🔍 DRY RUN MODE - No files will be changed\n');
    } else {
        console.log('⚠️  LIVE MODE - Files will be renamed!\n');
    }

    // Scan all files
    console.log('📂 Scanning for unit files...');
    const files = scanAllUnitFiles();
    console.log(`   Found ${files.length} unit files\n`);

    // Analyze each file
    console.log('🔍 Analyzing filenames...\n');
    const results = {
        correct: [],
        needsRename: [],
        invalid: [],
        errors: []
    };

    for (const file of files) {
        const analysis = analyzeFile(file);

        switch (analysis.status) {
            case 'correct':
                results.correct.push(analysis);
                break;
            case 'needs_rename':
                results.needsRename.push(analysis);
                break;
            case 'invalid':
                results.invalid.push(analysis);
                break;
            case 'error':
                results.errors.push(analysis);
                break;
        }
    }

    // Report summary
    console.log('═'.repeat(80));
    console.log('  📊 ANALYSIS SUMMARY');
    console.log('═'.repeat(80));
    console.log('');
    console.log(`✅ Correct:       ${results.correct.length}`);
    console.log(`🔄 Needs Rename:  ${results.needsRename.length}`);
    console.log(`⚠️  Invalid:       ${results.invalid.length}`);
    console.log(`❌ Errors:        ${results.errors.length}`);
    console.log('');

    // Show files that need renaming
    if (results.needsRename.length > 0) {
        console.log('═'.repeat(80));
        console.log('  🔄 FILES TO RENAME');
        console.log('═'.repeat(80));
        console.log('');

        for (const item of results.needsRename) {
            console.log(`📝 ${item.original}`);
            console.log(`   → ${item.canonical}`);
            if (item.changes.nation) {
                console.log(`   🌍 Nation: ${item.changes.nation}`);
            }
            if (item.changes.quarter) {
                console.log(`   📅 Quarter: ${item.changes.quarter}`);
            }
            if (item.warning) {
                console.log(`   ⚠️  ${item.warning}`);
            }
            console.log('');
        }
    }

    // Show invalid files
    if (results.invalid.length > 0) {
        console.log('═'.repeat(80));
        console.log('  ⚠️  INVALID FILENAMES (Cannot Parse)');
        console.log('═'.repeat(80));
        console.log('');

        for (const item of results.invalid) {
            console.log(`❌ ${item.original}`);
            console.log(`   Reason: ${item.reason}`);
            console.log('');
        }
    }

    // Show errors
    if (results.errors.length > 0) {
        console.log('═'.repeat(80));
        console.log('  ❌ ERRORS');
        console.log('═'.repeat(80));
        console.log('');

        for (const item of results.errors) {
            console.log(`❌ ${item.original}`);
            console.log(`   Error: ${item.reason}`);
            console.log('');
        }
    }

    // Execute renames if not dry run
    if (!isDryRun && results.needsRename.length > 0) {
        console.log('═'.repeat(80));
        console.log('  🚀 EXECUTING RENAMES');
        console.log('═'.repeat(80));
        console.log('');

        let successCount = 0;
        let failCount = 0;

        for (const item of results.needsRename) {
            console.log(`🔄 ${item.original} → ${item.canonical}`);
            const success = renameFile(item);
            if (success) {
                successCount++;
                console.log('   ✅ Success\n');
            } else {
                failCount++;
                console.log('');
            }
        }

        console.log('═'.repeat(80));
        console.log(`✅ Successfully renamed: ${successCount}`);
        console.log(`❌ Failed: ${failCount}`);
        console.log('═'.repeat(80));
        console.log('');

        if (successCount > 0) {
            console.log('🎉 Migration complete!\n');
            console.log('💡 Next steps:');
            console.log('   1. Run: npm run session:ready');
            console.log('   2. Verify all units are detected correctly');
            console.log('   3. Commit changes: git add . && git commit -m "refactor: Standardize unit filenames"');
            console.log('');
        }
    } else if (isDryRun && results.needsRename.length > 0) {
        console.log('═'.repeat(80));
        console.log('');
        console.log('🔍 DRY RUN COMPLETE - No files were changed');
        console.log('');
        console.log(`📊 ${results.needsRename.length} files would be renamed`);
        console.log('');
        console.log('To execute renames, run:');
        console.log('   node scripts/migrate_filenames.js');
        console.log('');
        console.log('═'.repeat(80));
        console.log('');
    } else if (results.needsRename.length === 0) {
        console.log('🎉 All filenames are already canonical! No migration needed.\n');
    }
}

// Run
main();
