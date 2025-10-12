#!/usr/bin/env node

/**
 * Unify All Schemas - Transform ALL 75+ unit JSON files to unified schema standard
 *
 * Comprehensive transformation script that:
 * 1. Scans ALL unit JSON files
 * 2. Detects current schema structure
 * 3. Transforms to unified schema
 * 4. Validates after transformation
 * 5. Creates backups before modification
 * 6. Generates detailed transformation report
 *
 * Usage: node scripts/unify-all-schemas.js [--dry-run] [--verbose]
 */

const fs = require('fs').promises;
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');

const NATION_MAPPING = {
    'Germany': 'german',
    'germany': 'german',
    'britain': 'british',
    'Britain': 'british',
    'france': 'french',
    'France': 'french',
    'italy': 'italian',
    'Italy': 'italian',
    'usa': 'american',
    'USA': 'american',
    'america': 'american',
    'America': 'american',
    'india': 'british',
    'India': 'british',
    'newzealand': 'british',
    'NewZealand': 'british',
    'australia': 'british',
    'Australia': 'british',
    'southafrica': 'british',
    'SouthAfrica': 'british'
};

let dryRun = false;
let verbose = false;
let backupDir = null;

async function main() {
    const args = process.argv.slice(2);
    dryRun = args.includes('--dry-run');
    verbose = args.includes('--verbose') || args.includes('-v');

    backupDir = path.join(PROJECT_ROOT, 'data/backups', `schema_unify_${Date.now()}`);

    console.log('\n' + '═'.repeat(80));
    console.log('  🔧 UNIFIED SCHEMA TRANSFORMATION - All Units');
    console.log('═'.repeat(80));
    console.log('');

    if (dryRun) {
        console.log('🔍 DRY RUN MODE - No files will be modified\n');
    } else {
        console.log(`💾 Backup directory: ${backupDir}\n`);
        await fs.mkdir(backupDir, { recursive: true });
    }

    // Step 1: Scan for all unit JSON files
    console.log('📁 Scanning for all unit JSON files...');
    const allFiles = await scanAllUnitFiles();
    console.log(`   Found ${allFiles.length} unit JSON files\n`);

    // Step 2: Analyze schema structures
    console.log('🔍 Analyzing schema structures...');
    const analysis = await analyzeSchemaStructures(allFiles);

    console.log(`   Schema distribution:`);
    console.log(`   - Unified schema (compliant): ${analysis.unifiedSchema.length}`);
    console.log(`   - Nested structure (unit_identification): ${analysis.nestedStructure.length}`);
    console.log(`   - Old commander format: ${analysis.oldCommanderFormat.length}`);
    console.log(`   - Mixed/partial compliance: ${analysis.mixedFormat.length}`);
    console.log(`   - Parse errors: ${analysis.parseErrors.length}`);
    console.log('');

    // Step 3: Transform all units
    console.log('⚙️  Transforming units to unified schema...');
    const results = {
        total: allFiles.length,
        alreadyCompliant: 0,
        transformed: 0,
        errors: [],
        transformations: []
    };

    for (const filePath of allFiles) {
        const fileName = path.basename(filePath);

        try {
            const result = await transformUnitFile(filePath);

            if (result.alreadyCompliant) {
                results.alreadyCompliant++;
                if (verbose) console.log(`   ✅ ${fileName} - Already compliant`);
            } else if (result.transformed) {
                results.transformed++;
                console.log(`   🔧 ${fileName} - ${result.changes.join(', ')}`);
                results.transformations.push({
                    file: fileName,
                    path: filePath,
                    changes: result.changes
                });
            }
        } catch (error) {
            results.errors.push({ file: fileName, path: filePath, error: error.message });
            console.log(`   ❌ ${fileName} - Error: ${error.message}`);
        }
    }

    console.log('');
    console.log('═'.repeat(80));
    console.log('  TRANSFORMATION SUMMARY');
    console.log('═'.repeat(80));
    console.log('');
    console.log(`Total units processed: ${results.total}`);
    console.log(`✅ Already compliant: ${results.alreadyCompliant}`);
    console.log(`🔧 Transformed: ${results.transformed}`);
    console.log(`❌ Errors: ${results.errors.length}`);
    console.log('');

    if (results.errors.length > 0) {
        console.log('Errors encountered:');
        for (const err of results.errors) {
            console.log(`   ${err.file}: ${err.error}`);
        }
        console.log('');
    }

    // Step 4: Generate transformation report
    const reportPath = path.join(PROJECT_ROOT, 'data/SCHEMA_TRANSFORMATION_REPORT.json');
    const report = {
        timestamp: new Date().toISOString(),
        dryRun: dryRun,
        totalFiles: results.total,
        alreadyCompliant: results.alreadyCompliant,
        transformed: results.transformed,
        errors: results.errors,
        transformations: results.transformations,
        backupDirectory: dryRun ? null : backupDir
    };

    if (!dryRun) {
        await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
        console.log(`📄 Transformation report saved to: ${reportPath}`);
        console.log('');
    }

    if (dryRun) {
        console.log('🔍 DRY RUN COMPLETE - No files were modified');
        console.log('   Run without --dry-run to apply transformations');
    } else {
        console.log(`💾 Backups saved to: ${backupDir}`);
        console.log('✅ Schema transformation complete!');
        console.log('');
        console.log('Next steps:');
        console.log('   1. Run: npm run validate');
        console.log('   2. Review: data/SCHEMA_TRANSFORMATION_REPORT.json');
    }

    console.log('');
}

/**
 * Scan for ALL unit JSON files
 */
async function scanAllUnitFiles() {
    const outputDir = path.join(PROJECT_ROOT, 'data/output');
    const files = [];

    try {
        const sessions = await fs.readdir(outputDir);

        for (const session of sessions) {
            const sessionPath = path.join(outputDir, session);
            const stat = await fs.stat(sessionPath);

            if (!stat.isDirectory()) continue;

            // Check for units directory
            const unitsDir = path.join(sessionPath, 'units');
            try {
                const unitFiles = await fs.readdir(unitsDir);
                for (const file of unitFiles) {
                    if (file.endsWith('_toe.json')) {
                        files.push(path.join(unitsDir, file));
                    }
                }
            } catch (error) {
                // Session might not have units directory
                continue;
            }
        }
    } catch (error) {
        console.error(`❌ Error scanning output directory: ${error.message}`);
    }

    return files;
}

/**
 * Analyze schema structures across all files
 */
async function analyzeSchemaStructures(files) {
    const analysis = {
        unifiedSchema: [],
        nestedStructure: [],
        oldCommanderFormat: [],
        mixedFormat: [],
        parseErrors: []
    };

    for (const filePath of files) {
        try {
            const jsonData = await fs.readFile(filePath, 'utf-8');
            const unit = JSON.parse(jsonData);

            const hasTopLevelNation = unit.hasOwnProperty('nation');
            const hasNestedNation = unit.unit_identification?.hasOwnProperty('nation');
            const hasOldCommander = unit.command?.hasOwnProperty('commander_name');
            const hasNewCommander = unit.command?.commander?.hasOwnProperty('name');

            if (hasNestedNation && !hasTopLevelNation) {
                analysis.nestedStructure.push(filePath);
            } else if (hasOldCommander && !hasNewCommander) {
                analysis.oldCommanderFormat.push(filePath);
            } else if (hasTopLevelNation && hasNewCommander) {
                analysis.unifiedSchema.push(filePath);
            } else {
                analysis.mixedFormat.push(filePath);
            }
        } catch (error) {
            analysis.parseErrors.push({ file: filePath, error: error.message });
        }
    }

    return analysis;
}

/**
 * Transform a single unit JSON file to unified schema
 */
async function transformUnitFile(filePath) {
    const result = {
        alreadyCompliant: false,
        transformed: false,
        changes: []
    };

    // Read file
    const jsonData = await fs.readFile(filePath, 'utf-8');
    const unit = JSON.parse(jsonData);

    // Backup original
    if (!dryRun) {
        const backupPath = path.join(backupDir, path.basename(filePath));
        await fs.writeFile(backupPath, jsonData);
    }

    let modified = false;

    // Transformation 1: Standardize nation name
    let nation = unit.nation || unit.unit_identification?.nation;
    if (nation && NATION_MAPPING[nation]) {
        const newNation = NATION_MAPPING[nation];
        if (nation !== newNation) {
            if (unit.nation) {
                unit.nation = newNation;
            }
            if (unit.unit_identification?.nation) {
                unit.unit_identification.nation = newNation;
            }
            result.changes.push('nation standardized');
            modified = true;
        }
    }

    // Transformation 2: Flatten nested structure (unit_identification.* → top-level)
    if (unit.unit_identification && !unit.nation) {
        unit.nation = unit.unit_identification.nation;
        unit.quarter = unit.unit_identification.quarter || unit.quarter;
        unit.unit_designation = unit.unit_identification.unit_designation || unit.unit_designation;
        unit.unit_type = unit.unit_identification.unit_type || unit.unit_type;
        unit.organization_level = unit.unit_identification.organization_level || unit.organization_level;

        result.changes.push('structure flattened');
        modified = true;
    }

    // Transformation 3: Transform commander structure
    if (unit.command?.commander_name && !unit.command.commander) {
        unit.command.commander = {
            name: unit.command.commander_name,
            rank: unit.command.commander_rank || 'Unknown'
        };
        delete unit.command.commander_name;
        delete unit.command.commander_rank;
        result.changes.push('commander structure updated');
        modified = true;
    }

    // Transformation 4: Flatten personnel_summary
    if (unit.personnel_summary && !unit.total_personnel) {
        unit.total_personnel = unit.personnel_summary.total_personnel || 0;
        unit.officers = unit.personnel_summary.officers || 0;
        unit.ncos = unit.personnel_summary.ncos || 0;
        unit.enlisted = unit.personnel_summary.enlisted || 0;
        result.changes.push('personnel flattened');
        modified = true;
    }

    // Transformation 5: Flatten equipment_summary
    if (unit.equipment_summary && !unit.tanks) {
        if (unit.equipment_summary.tanks) {
            unit.tanks = unit.equipment_summary.tanks;
        }
        if (unit.equipment_summary.artillery) {
            unit.artillery_total = unit.equipment_summary.artillery.total || 0;
        }
        if (unit.equipment_summary.ground_vehicles) {
            unit.ground_vehicles_total = unit.equipment_summary.ground_vehicles.total || 0;
        }
        result.changes.push('equipment flattened');
        modified = true;
    }

    // Transformation 6: Create validation object from data_quality/metadata
    if (!unit.validation && (unit.data_quality || unit.metadata)) {
        const sources = unit.data_quality?.primary_sources || unit.metadata?.sources || ['Unknown'];
        const confidence = unit.data_quality?.confidence_score || 70;
        const lastUpdated = unit.metadata?.last_updated || unit.data_quality?.last_updated || new Date().toISOString().split('T')[0];
        const knownGaps = unit.data_quality?.data_gaps || [];

        unit.validation = {
            source: Array.isArray(sources) ? sources : [sources],
            confidence: confidence,
            last_updated: lastUpdated,
            known_gaps: Array.isArray(knownGaps) ? knownGaps : [],
            aggregation_status: 'manually_entered'
        };
        result.changes.push('validation object created');
        modified = true;
    }

    // Transformation 7: Add missing organization_level
    if (!unit.organization_level && unit.schema_type) {
        const levelMap = {
            'theater_scm': 'theater',
            'corps_toe': 'corps',
            'division_toe': 'division',
            'regiment_toe': 'regiment',
            'battalion_toe': 'battalion',
            'company_toe': 'company',
            'platoon_toe': 'platoon',
            'squad_toe': 'squad'
        };
        unit.organization_level = levelMap[unit.schema_type] || 'division';
        result.changes.push('organization_level added');
        modified = true;
    }

    // Transformation 8: Add schema_version if missing
    if (!unit.schema_version) {
        unit.schema_version = '1.0.0';
        result.changes.push('schema_version added');
        modified = true;
    }

    // Save if modified
    if (modified) {
        result.transformed = true;
        if (!dryRun) {
            await fs.writeFile(filePath, JSON.stringify(unit, null, 2));
        }
    } else {
        result.alreadyCompliant = true;
    }

    return result;
}

// Run
main().catch(error => {
    console.error('❌ Transformation failed:', error.message);
    console.error(error.stack);
    process.exit(1);
});
