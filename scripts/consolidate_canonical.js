#!/usr/bin/env node

/**
 * Consolidate to Canonical Locations - ONE-TIME MIGRATION
 *
 * Finds scattered unit files across autonomous_* session directories
 * and consolidates them to canonical locations (data/output/units/).
 *
 * For each unit:
 * - Finds ALL copies (may be in 5-7 different session directories)
 * - Determines latest version by modification time
 * - Copies latest to canonical location
 * - Generates consolidation report
 *
 * Usage: npm run consolidate
 *
 * Created: 2025-10-14
 * Part of: Architecture v4.0
 */

const fs = require('fs').promises;
const path = require('path');
const paths = require('./lib/canonical_paths');

/**
 * Scan entire output directory for all unit files
 */
async function findAllUnitFiles() {
    const outputDir = paths.OUTPUT_ROOT;
    const foundFiles = new Map(); // unitId -> [array of file locations]

    const scanDir = async (dir) => {
        try {
            const entries = await fs.readdir(dir, { withFileTypes: true });

            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);

                if (entry.isDirectory()) {
                    // Skip canonical directories (they're our target)
                    if (fullPath === paths.UNITS_DIR) continue;
                    if (fullPath === paths.CHAPTERS_DIR) continue;
                    if (fullPath === paths.AIR_UNITS_DIR) continue;
                    if (fullPath === paths.SESSIONS_DIR) continue;

                    // Recursively scan
                    await scanDir(fullPath);
                } else if (entry.name.endsWith('_toe.json') && !entry.name.startsWith('unit_')) {
                    // Found a unit file
                    const stats = await fs.stat(fullPath);

                    // Extract unit ID from filename
                    const match = entry.name.match(/^([a-z]+)_(\d{4}[-]?q\d)_(.+)_toe\.json$/i);
                    if (match) {
                        const unitId = `${match[1]}_${match[2]}_${match[3]}`.toLowerCase().replace('-q', 'q');

                        if (!foundFiles.has(unitId)) {
                            foundFiles.set(unitId, []);
                        }

                        foundFiles.get(unitId).push({
                            path: fullPath,
                            filename: entry.name,
                            mtime: stats.mtimeMs,
                            directory: path.dirname(fullPath)
                        });
                    }
                }
            }
        } catch (error) {
            // Ignore permission errors and continue
            if (error.code !== 'EACCES' && error.code !== 'EPERM') {
                console.warn(`⚠️  Error scanning ${dir}:`, error.message);
            }
        }
    };

    await scanDir(outputDir);
    return foundFiles;
}

/**
 * Consolidate files to canonical location
 */
async function consolidateFiles(foundFiles) {
    // Ensure canonical directory exists
    await paths.ensureCanonicalDirectoriesExist();

    const stats = {
        total_units: foundFiles.size,
        consolidated: 0,
        already_canonical: 0,
        duplicates_found: 0,
        errors: []
    };

    console.log(`\n📋 Found ${foundFiles.size} unique units\n`);

    for (const [unitId, locations] of foundFiles.entries()) {
        // Sort by modification time (newest first)
        locations.sort((a, b) => b.mtime - a.mtime);

        const latestFile = locations[0];
        const canonicalPath = path.join(paths.UNITS_DIR, latestFile.filename);

        // Check if already in canonical location
        if (latestFile.path === canonicalPath) {
            stats.already_canonical++;
            continue;
        }

        // Track duplicates
        if (locations.length > 1) {
            stats.duplicates_found++;
            console.log(`📦 ${unitId}: ${locations.length} copies found (using latest from ${path.basename(latestFile.directory)})`);
        }

        // Copy latest version to canonical location
        try {
            await fs.copyFile(latestFile.path, canonicalPath);
            stats.consolidated++;
        } catch (error) {
            stats.errors.push({
                unitId: unitId,
                error: error.message
            });
            console.error(`❌ Error consolidating ${unitId}:`, error.message);
        }
    }

    return stats;
}

/**
 * Generate consolidation report
 */
async function generateReport(stats, foundFiles) {
    const reportPath = path.join(paths.OUTPUT_ROOT, 'CONSOLIDATION_REPORT.md');

    const duplicatesList = [];
    for (const [unitId, locations] of foundFiles.entries()) {
        if (locations.length > 1) {
            duplicatesList.push({
                unitId,
                count: locations.length,
                locations: locations.map(l => ({
                    directory: path.basename(l.directory),
                    mtime: new Date(l.mtime).toISOString()
                }))
            });
        }
    }

    const report = `# Canonical Consolidation Report

**Date**: ${new Date().toISOString()}
**Status**: ✅ Consolidation Complete

---

## Summary Statistics

- **Total Unique Units**: ${stats.total_units}
- **Consolidated to Canonical**: ${stats.consolidated}
- **Already in Canonical**: ${stats.already_canonical}
- **Units with Duplicates**: ${stats.duplicates_found}
- **Errors**: ${stats.errors.length}

---

## Duplicate Analysis

${stats.duplicates_found} units had multiple copies across session directories.

### Example Duplicates (showing first 10):

${duplicatesList.slice(0, 10).map(d => `
**${d.unitId}** - ${d.count} copies found:
${d.locations.map(l => `  - ${l.directory} (modified: ${l.mtime})`).join('\n')}
`).join('\n')}

${duplicatesList.length > 10 ? `\n... and ${duplicatesList.length - 10} more units with duplicates.\n` : ''}

---

## Canonical Structure

All units now consolidated to:

\`\`\`
data/output/units/
├── american_1942q4_1st_armored_division_toe.json
├── american_1942q4_1st_infantry_division_toe.json
├── ... (${stats.total_units} total unique files)
\`\`\`

---

## Next Steps

1. ✅ Run \`npm run archive:sessions\` to archive old session directories
2. ✅ Run \`npm run checkpoint\` to update WORKFLOW_STATE.json
3. ✅ Verify: \`ls data/output/units/*.json | wc -l\` should show ${stats.total_units}

---

${stats.errors.length > 0 ? `## Errors

${stats.errors.map(e => `- **${e.unitId}**: ${e.error}`).join('\n')}

` : ''}

Generated by scripts/consolidate_canonical.js
`;

    await fs.writeFile(reportPath, report);
    console.log(`\n📄 Report saved: ${reportPath}\n`);
}

/**
 * Main execution
 */
async function main() {
    console.log('\n' + '='.repeat(80));
    console.log('  📦 CONSOLIDATE TO CANONICAL LOCATIONS');
    console.log('  Architecture v4.0 Migration');
    console.log('='.repeat(80) + '\n');

    console.log('🔍 Scanning for all unit files...');
    const foundFiles = await findAllUnitFiles();

    console.log(`✅ Scan complete: ${foundFiles.size} unique units found\n`);

    // Show duplicate statistics
    let totalFiles = 0;
    let duplicateCount = 0;
    for (const [, locations] of foundFiles.entries()) {
        totalFiles += locations.length;
        if (locations.length > 1) {
            duplicateCount++;
        }
    }

    console.log(`📊 Statistics:`);
    console.log(`   Total file copies: ${totalFiles}`);
    console.log(`   Unique units: ${foundFiles.size}`);
    console.log(`   Units with duplicates: ${duplicateCount}`);
    console.log(`   Average copies per unit: ${(totalFiles / foundFiles.size).toFixed(2)}\n`);

    console.log('📋 Consolidating to canonical location...\n');
    const stats = await consolidateFiles(foundFiles);

    console.log('\n' + '='.repeat(80));
    console.log('  ✅ CONSOLIDATION COMPLETE');
    console.log('='.repeat(80));
    console.log('');
    console.log(`📊 Results:`);
    console.log(`   Total units: ${stats.total_units}`);
    console.log(`   Consolidated: ${stats.consolidated}`);
    console.log(`   Already canonical: ${stats.already_canonical}`);
    console.log(`   Duplicates found: ${stats.duplicates_found}`);
    console.log(`   Errors: ${stats.errors.length}\n`);

    // Generate report
    await generateReport(stats, foundFiles);

    console.log('💡 Next steps:');
    console.log('   1. Run: npm run archive:sessions');
    console.log('   2. Run: npm run checkpoint');
    console.log('   3. Verify: ls data/output/units/*.json | wc -l\n');
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error('\n❌ Consolidation failed:', error.message);
        console.error(error.stack);
        process.exit(1);
    });
}

module.exports = { findAllUnitFiles, consolidateFiles };
