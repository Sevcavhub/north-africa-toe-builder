#!/usr/bin/env node

/**
 * Workflow State Reconciliation Script
 *
 * Fixes WORKFLOW_STATE.json by:
 * 1. Reading all actual files in data/output/units/
 * 2. Using fuzzy matching to map them to seed units
 * 3. Identifying and removing duplicates
 * 4. Storing canonical normalized IDs only
 * 5. Identifying orphaned files (not in seed)
 */

const fs = require('fs').promises;
const path = require('path');
const naming = require('./lib/naming_standard');
const matching = require('./lib/matching');

async function main() {
    console.log('🔄 Reconciling WORKFLOW_STATE.json with actual files...\n');

    // 1. Load seed file
    const seedPath = path.join(process.cwd(), 'projects', 'north_africa_seed_units_COMPLETE.json');
    const seedData = JSON.parse(await fs.readFile(seedPath, 'utf-8'));

    console.log(`📋 Seed file: ${seedData.total_unit_quarters} unit-quarters expected\n`);

    // 2. Build expected units from seed (with canonical IDs)
    const expectedUnits = [];
    const seedUnitsMap = new Map(); // canonical_id -> seed unit info

    for (const [nationKey, units] of Object.entries(seedData)) {
        if (!nationKey.endsWith('_units') || !Array.isArray(units)) continue;

        const nation = naming.NATION_MAP[nationKey];
        if (!nation) continue;

        for (const unit of units) {
            for (const quarter of unit.quarters) {
                const canonicalId = `${nation}_${naming.normalizeQuarter(quarter)}_${naming.normalizeDesignation(unit.designation)}`;

                expectedUnits.push({
                    nation,
                    quarter,
                    designation: unit.designation,
                    aliases: unit.aliases || [],
                    canonicalId
                });

                seedUnitsMap.set(canonicalId, {
                    designation: unit.designation,
                    aliases: unit.aliases || [],
                    type: unit.type
                });
            }
        }
    }

    console.log(`✅ Generated ${expectedUnits.length} expected canonical IDs\n`);

    // 3. Read all actual files
    const unitsDir = path.join(process.cwd(), 'data', 'output', 'units');
    const actualFiles = (await fs.readdir(unitsDir))
        .filter(f => f.endsWith('_toe.json'));

    console.log(`📁 Found ${actualFiles.length} actual files\n`);

    // 4. Map actual files to seed units using fuzzy matching
    const fileToSeedMap = new Map(); // filename -> canonical seed ID
    const seedToFilesMap = new Map(); // canonical seed ID -> array of filenames
    const orphanedFiles = []; // files not matching any seed unit

    for (const filename of actualFiles) {
        const parsed = naming.parseFilename(filename);
        if (!parsed) {
            console.warn(`⚠️  Could not parse: ${filename}`);
            orphanedFiles.push(filename);
            continue;
        }

        // Try to find matching seed unit
        let matchFound = false;

        for (const expected of expectedUnits) {
            // Use fuzzy matching (checks aliases, partial words)
            if (matching.isUnitCompleted(
                expected.nation,
                expected.quarter,
                expected.designation,
                expected.aliases,
                new Set([filename.replace('_toe.json', '')])
            )) {
                fileToSeedMap.set(filename, expected.canonicalId);

                if (!seedToFilesMap.has(expected.canonicalId)) {
                    seedToFilesMap.set(expected.canonicalId, []);
                }
                seedToFilesMap.get(expected.canonicalId).push(filename);

                matchFound = true;
                break;
            }
        }

        if (!matchFound) {
            orphanedFiles.push(filename);
        }
    }

    // 5. Report duplicates
    console.log('📊 Duplicate Analysis:\n');
    let duplicateCount = 0;
    const duplicates = [];

    for (const [canonicalId, files] of seedToFilesMap.entries()) {
        if (files.length > 1) {
            duplicateCount += files.length - 1;
            const seedInfo = seedUnitsMap.get(canonicalId);
            duplicates.push({
                canonicalId,
                designation: seedInfo?.designation || 'unknown',
                fileCount: files.length,
                files: files
            });
        }
    }

    if (duplicates.length > 0) {
        console.log(`⚠️  Found ${duplicates.length} seed units with ${duplicateCount} duplicate files:\n`);
        for (const dup of duplicates.slice(0, 10)) {
            console.log(`   ${dup.designation} (${dup.canonicalId})`);
            console.log(`   Files (${dup.fileCount}):`);
            dup.files.forEach(f => console.log(`     - ${f}`));
            console.log('');
        }
        if (duplicates.length > 10) {
            console.log(`   ... and ${duplicates.length - 10} more\n`);
        }
    } else {
        console.log('✅ No duplicates found\n');
    }

    // 6. Report orphaned files
    console.log(`📊 Orphaned Files (${orphanedFiles.length}):\n`);
    if (orphanedFiles.length > 0) {
        orphanedFiles.slice(0, 20).forEach(f => console.log(`   - ${f}`));
        if (orphanedFiles.length > 20) {
            console.log(`   ... and ${orphanedFiles.length - 20} more\n`);
        }
    } else {
        console.log('✅ No orphaned files\n');
    }

    // 7. Build clean WORKFLOW_STATE.json with canonical IDs only
    const completedCanonicalIds = Array.from(seedToFilesMap.keys()).sort();

    const newWorkflowState = {
        last_updated: new Date().toISOString(),
        total_unit_quarters: seedData.total_unit_quarters,
        total_unique_units: seedData.total_units,
        completed_count: completedCanonicalIds.length,
        completion_percentage: ((completedCanonicalIds.length / seedData.total_unit_quarters) * 100).toFixed(1),
        data_quality_correction: seedData.data_quality_note,
        note: "Reconciled 2025-10-26: Removed duplicates, normalized all IDs to canonical format",
        completed: completedCanonicalIds
    };

    // 8. Show summary
    console.log('\n📊 Summary:\n');
    console.log(`   Expected (seed):      ${expectedUnits.length}`);
    console.log(`   Actual files:         ${actualFiles.length}`);
    console.log(`   Matched to seed:      ${completedCanonicalIds.length}`);
    console.log(`   Orphaned files:       ${orphanedFiles.length}`);
    console.log(`   Duplicate files:      ${duplicateCount}`);
    console.log(`   Completion:           ${newWorkflowState.completion_percentage}%\n`);

    // 9. Save reconciled WORKFLOW_STATE.json
    const workflowStatePath = path.join(process.cwd(), 'WORKFLOW_STATE.json');
    const backupPath = path.join(process.cwd(), 'WORKFLOW_STATE.json.backup');

    // Backup old version
    await fs.copyFile(workflowStatePath, backupPath);
    console.log(`✅ Backed up old WORKFLOW_STATE.json to WORKFLOW_STATE.json.backup\n`);

    // Write new version
    await fs.writeFile(
        workflowStatePath,
        JSON.stringify(newWorkflowState, null, 2)
    );
    console.log(`✅ Wrote reconciled WORKFLOW_STATE.json\n`);

    // 10. Save detailed report
    const reportPath = path.join(process.cwd(), 'data', 'output', 'qa_reports', 'reconciliation_report.json');
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            expected: expectedUnits.length,
            actual_files: actualFiles.length,
            matched: completedCanonicalIds.length,
            orphaned: orphanedFiles.length,
            duplicates: duplicateCount
        },
        duplicates: duplicates,
        orphaned_files: orphanedFiles,
        file_to_seed_mapping: Object.fromEntries(fileToSeedMap),
        seed_to_files_mapping: Object.fromEntries(
            Array.from(seedToFilesMap.entries()).map(([k, v]) => [k, {
                files: v,
                count: v.length
            }])
        )
    };

    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    console.log(`✅ Wrote detailed report to data/output/qa_reports/reconciliation_report.json\n`);
}

main().catch(error => {
    console.error('❌ Error:', error);
    process.exit(1);
});
