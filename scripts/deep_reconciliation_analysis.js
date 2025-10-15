#!/usr/bin/env node

/**
 * Deep Reconciliation Analysis
 *
 * Purpose: Comprehensive analysis to reconcile:
 * - Canonical directory count (152 files)
 * - WORKFLOW_STATE.json count (151 completed)
 * - PROJECT_SCOPE.md claims (151 completed, 211 total scope)
 * - Seed file expectations (213 units)
 * - Previous analysis showing 94 from seed + 56 orphaned
 *
 * Outputs detailed report on discrepancies, duplicates, and renamed units.
 */

const fs = require('fs');
const path = require('path');

// Helper: Read JSON file
function readJSON(filePath) {
    try {
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (err) {
        console.error(`Error reading ${filePath}:`, err.message);
        return null;
    }
}

// Helper: Fuzzy match unit names (60% word overlap threshold)
function fuzzyMatch(seedName, fileName) {
    const normalizeWords = (str) => {
        return str.toLowerCase()
            .replace(/[^a-z0-9\s]/g, ' ')
            .split(/\s+/)
            .filter(w => w.length > 2); // Only words > 2 chars
    };

    const seedWords = normalizeWords(seedName);
    const fileWords = normalizeWords(fileName);

    if (seedWords.length === 0 || fileWords.length === 0) return false;

    const matches = seedWords.filter(w => fileWords.includes(w)).length;
    const overlapPercent = matches / seedWords.length;

    return overlapPercent >= 0.6;
}

// Helper: Build unit ID from seed entry
function buildSeedUnitId(nation, quarter, designation) {
    const nationMap = {
        'german': 'german',
        'italian': 'italian',
        'british': 'british',
        'usa': 'american',
        'french': 'french'
    };

    const normalizedNation = nationMap[nation.toLowerCase()] || nation.toLowerCase();
    const normalizedQuarter = quarter.toLowerCase().replace('-', '');
    const normalizedDesignation = designation
        .toLowerCase()
        .replace(/\./g, '')
        .replace(/[^a-z0-9]/g, '_')
        .replace(/_+/g, '_')
        .replace(/^_|_$/g, '');

    return `${normalizedNation}_${normalizedQuarter}_${normalizedDesignation}`;
}

// Main analysis
async function analyzeProject() {
    console.log('='.repeat(80));
    console.log('DEEP RECONCILIATION ANALYSIS');
    console.log('='.repeat(80));
    console.log();

    // Step 1: Read all source data
    console.log('Step 1: Loading data sources...');

    const canonicalDir = 'data/output/units';
    const canonicalFiles = fs.existsSync(canonicalDir)
        ? fs.readdirSync(canonicalDir).filter(f => f.endsWith('_toe.json'))
        : [];

    const workflowState = readJSON('WORKFLOW_STATE.json');
    const seedFile = readJSON('projects/north_africa_seed_units.json');
    const projectScope = fs.readFileSync('PROJECT_SCOPE.md', 'utf8');

    console.log(`  - Canonical directory: ${canonicalFiles.length} files`);
    console.log(`  - WORKFLOW_STATE.json: ${workflowState?.completed?.length || 0} completed`);
    console.log(`  - Seed file loaded: ${seedFile ? 'Yes' : 'No'}`);
    console.log(`  - PROJECT_SCOPE.md: ${projectScope ? 'Loaded' : 'Failed'}`);
    console.log();

    // Step 2: Extract seed units
    console.log('Step 2: Building expected units from seed...');

    const expectedUnits = [];
    for (const [nationKey, units] of Object.entries(seedFile)) {
        if (!nationKey.endsWith('_units')) continue;

        const nation = nationKey.replace('_units', '');

        for (const unit of units) {
            for (const quarter of unit.quarters) {
                const unitId = buildSeedUnitId(nation, quarter, unit.designation);
                expectedUnits.push({
                    nation: nation === 'usa' ? 'american' : nation,
                    quarter: quarter,
                    designation: unit.designation,
                    unitId: unitId
                });
            }
        }
    }

    console.log(`  - Total expected units from seed: ${expectedUnits.length}`);
    console.log();

    // Step 3: Analyze canonical directory
    console.log('Step 3: Analyzing canonical directory files...');

    const canonicalUnits = canonicalFiles.map(fileName => {
        const baseName = fileName.replace('_toe.json', '');
        const filePath = path.join(canonicalDir, fileName);

        // Try to read unit data
        let unitData = null;
        try {
            unitData = readJSON(filePath);
        } catch (err) {
            // Ignore read errors
        }

        return {
            fileName: fileName,
            unitId: baseName,
            filePath: filePath,
            fileSize: fs.statSync(filePath).size,
            hasData: !!unitData,
            nation: unitData?.nation || baseName.split('_')[0],
            quarter: unitData?.quarter || baseName.split('_')[1],
            designation: unitData?.unit_designation || 'Unknown'
        };
    });

    console.log(`  - Total canonical files: ${canonicalUnits.length}`);
    console.log();

    // Step 4: Check for duplicates in canonical
    console.log('Step 4: Checking for duplicate unit IDs in canonical...');

    const unitIdCounts = {};
    for (const unit of canonicalUnits) {
        unitIdCounts[unit.unitId] = (unitIdCounts[unit.unitId] || 0) + 1;
    }

    const duplicates = Object.entries(unitIdCounts)
        .filter(([id, count]) => count > 1)
        .map(([id, count]) => ({ unitId: id, count }));

    if (duplicates.length > 0) {
        console.log(`  ⚠️ FOUND ${duplicates.length} DUPLICATE UNIT IDs:`);
        for (const dup of duplicates) {
            console.log(`     - ${dup.unitId} (${dup.count} times)`);
        }
    } else {
        console.log(`  ✅ No duplicate unit IDs found`);
    }
    console.log();

    // Step 5: Match canonical files to seed units
    console.log('Step 5: Matching canonical files to seed units...');

    const matchResults = {
        strictMatches: [],
        fuzzyMatches: [],
        noMatches: []
    };

    for (const canonUnit of canonicalUnits) {
        let matched = false;
        let matchType = null;
        let matchedSeed = null;

        // Try strict match first
        const strictMatch = expectedUnits.find(su => su.unitId === canonUnit.unitId);
        if (strictMatch) {
            matched = true;
            matchType = 'strict';
            matchedSeed = strictMatch;
        } else {
            // Try fuzzy match
            const fuzzyMatch = expectedUnits.find(su => {
                const sameNation = su.nation === canonUnit.nation;
                const sameQuarter = su.quarter.toLowerCase().replace('-', '') === canonUnit.quarter;
                const nameMatch = fuzzyMatchNames(su.designation, canonUnit.designation);
                return sameNation && sameQuarter && nameMatch;
            });

            if (fuzzyMatch) {
                matched = true;
                matchType = 'fuzzy';
                matchedSeed = fuzzyMatch;
            }
        }

        if (matchType === 'strict') {
            matchResults.strictMatches.push({ canonical: canonUnit, seed: matchedSeed });
        } else if (matchType === 'fuzzy') {
            matchResults.fuzzyMatches.push({ canonical: canonUnit, seed: matchedSeed });
        } else {
            matchResults.noMatches.push(canonUnit);
        }
    }

    console.log(`  - Strict matches: ${matchResults.strictMatches.length}`);
    console.log(`  - Fuzzy matches: ${matchResults.fuzzyMatches.length}`);
    console.log(`  - No matches (orphaned): ${matchResults.noMatches.length}`);
    console.log();

    // Helper for fuzzy name matching
    function fuzzyMatchNames(seedName, fileName) {
        const normalize = (str) => {
            return str.toLowerCase()
                .replace(/[^a-z0-9\s]/g, ' ')
                .split(/\s+/)
                .filter(w => w.length > 2);
        };

        const seedWords = normalize(seedName);
        const fileWords = normalize(fileName);

        if (seedWords.length === 0 || fileWords.length === 0) return false;

        const matches = seedWords.filter(w => fileWords.includes(w)).length;
        return matches / seedWords.length >= 0.6;
    }

    // Step 6: Identify seed units NOT yet completed
    console.log('Step 6: Identifying seed units NOT yet completed...');

    const completedSeedIds = [
        ...matchResults.strictMatches.map(m => m.seed.unitId),
        ...matchResults.fuzzyMatches.map(m => m.seed.unitId)
    ];

    const notCompletedSeeds = expectedUnits.filter(su => !completedSeedIds.includes(su.unitId));

    console.log(`  - Completed from seed: ${completedSeedIds.length}`);
    console.log(`  - Remaining from seed: ${notCompletedSeeds.length}`);
    console.log();

    // Step 7: Compare with WORKFLOW_STATE.json
    console.log('Step 7: Comparing with WORKFLOW_STATE.json...');

    const workflowCompleted = workflowState?.completed || [];
    const canonicalIds = canonicalUnits.map(u => u.unitId);

    const inWorkflowNotCanonical = workflowCompleted.filter(id => !canonicalIds.includes(id));
    const inCanonicalNotWorkflow = canonicalIds.filter(id => !workflowCompleted.includes(id));

    console.log(`  - Units in WORKFLOW_STATE but NOT in canonical: ${inWorkflowNotCanonical.length}`);
    if (inWorkflowNotCanonical.length > 0) {
        console.log(`    Examples: ${inWorkflowNotCanonical.slice(0, 5).join(', ')}`);
    }

    console.log(`  - Units in canonical but NOT in WORKFLOW_STATE: ${inCanonicalNotWorkflow.length}`);
    if (inCanonicalNotWorkflow.length > 0) {
        console.log(`    Examples: ${inCanonicalNotWorkflow.slice(0, 5).join(', ')}`);
    }
    console.log();

    // Step 8: Generate comprehensive report
    console.log('Step 8: Generating comprehensive report...');

    const report = {
        analysis_date: new Date().toISOString(),
        summary: {
            canonical_directory_count: canonicalFiles.length,
            workflow_state_count: workflowCompleted.length,
            seed_file_expected: expectedUnits.length,
            project_scope_claimed: 151, // From PROJECT_SCOPE.md
            total_scope_target: 211 // From PROJECT_SCOPE.md (revised from 213)
        },
        discrepancies: {
            canonical_vs_workflow: canonicalFiles.length - workflowCompleted.length,
            explanation: canonicalFiles.length > workflowCompleted.length
                ? 'Canonical has MORE files than WORKFLOW_STATE.json'
                : 'WORKFLOW_STATE.json has MORE entries than canonical files'
        },
        matching: {
            strict_matches: matchResults.strictMatches.length,
            fuzzy_matches: matchResults.fuzzyMatches.length,
            orphaned_units: matchResults.noMatches.length,
            completed_from_seed: completedSeedIds.length,
            remaining_from_seed: notCompletedSeeds.length
        },
        duplicates_found: duplicates.length,
        duplicates: duplicates,
        orphaned_units: matchResults.noMatches.map(u => ({
            unit_id: u.unitId,
            nation: u.nation,
            quarter: u.quarter,
            designation: u.designation,
            file_size: u.fileSize
        })),
        remaining_seed_units: notCompletedSeeds.map(u => ({
            nation: u.nation,
            quarter: u.quarter,
            designation: u.designation,
            expected_unit_id: u.unitId
        })),
        fuzzy_matches_detail: matchResults.fuzzyMatches.map(m => ({
            canonical_id: m.canonical.unitId,
            canonical_designation: m.canonical.designation,
            seed_designation: m.seed.designation,
            seed_expected_id: m.seed.unitId
        })),
        workflow_discrepancies: {
            in_workflow_not_canonical: inWorkflowNotCanonical,
            in_canonical_not_workflow: inCanonicalNotWorkflow
        },
        conclusions: []
    };

    // Add conclusions
    if (canonicalFiles.length === 152 && workflowCompleted.length === 151) {
        report.conclusions.push('DISCREPANCY: Canonical has 1 extra file not tracked in WORKFLOW_STATE.json');
    }

    if (duplicates.length > 0) {
        report.conclusions.push(`CRITICAL: ${duplicates.length} duplicate unit IDs found in canonical directory`);
    }

    if (matchResults.noMatches.length > 0) {
        report.conclusions.push(`ORPHANED: ${matchResults.noMatches.length} units in canonical are NOT in seed file`);
    }

    if (matchResults.fuzzyMatches.length > 0) {
        report.conclusions.push(`NAMING: ${matchResults.fuzzyMatches.length} units required fuzzy matching (naming variations)`);
    }

    const actualProgress = (completedSeedIds.length / expectedUnits.length * 100).toFixed(1);
    report.conclusions.push(`TRUE PROGRESS: ${completedSeedIds.length}/${expectedUnits.length} (${actualProgress}%) from seed file`);

    // Write report
    const reportPath = 'data/output/DEEP_RECONCILIATION_REPORT.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log(`  ✅ Report saved to: ${reportPath}`);
    console.log();

    // Step 9: Print summary
    console.log('='.repeat(80));
    console.log('SUMMARY');
    console.log('='.repeat(80));
    console.log();
    console.log('📊 COUNTS:');
    console.log(`  - Canonical directory:        ${canonicalFiles.length} files`);
    console.log(`  - WORKFLOW_STATE.json:        ${workflowCompleted.length} completed`);
    console.log(`  - Seed file expected:         ${expectedUnits.length} units`);
    console.log(`  - PROJECT_SCOPE.md claimed:   151 completed`);
    console.log(`  - Total scope target:         211 units`);
    console.log();
    console.log('🔍 MATCHING:');
    console.log(`  - Strict matches (exact ID):  ${matchResults.strictMatches.length}`);
    console.log(`  - Fuzzy matches (renamed):    ${matchResults.fuzzyMatches.length}`);
    console.log(`  - Orphaned (not in seed):     ${matchResults.noMatches.length}`);
    console.log(`  - Completed from seed:        ${completedSeedIds.length}/${expectedUnits.length}`);
    console.log(`  - Remaining from seed:        ${notCompletedSeeds.length}`);
    console.log();
    console.log('⚠️ ISSUES:');
    console.log(`  - Duplicate unit IDs:         ${duplicates.length}`);
    console.log(`  - Canonical vs WORKFLOW diff: ${Math.abs(canonicalFiles.length - workflowCompleted.length)}`);
    console.log();
    console.log('✅ TRUE PROGRESS:');
    console.log(`  - ${completedSeedIds.length}/${expectedUnits.length} (${actualProgress}%) of seed units complete`);
    console.log(`  - ${notCompletedSeeds.length} seed units remaining`);
    console.log(`  - ${matchResults.noMatches.length} orphaned units (not in current scope)`);
    console.log();
    console.log('='.repeat(80));
    console.log(`Full report: ${reportPath}`);
    console.log('='.repeat(80));
}

// Run analysis
analyzeProject().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
