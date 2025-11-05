#!/usr/bin/env node

/**
 * Fix Schema Mismatches - Transform units to unified schema structure
 *
 * Fixes:
 * 1. Nation name standardization (Germany → german, britain → british)
 * 2. Nested structure transformation (unit_identification.* → top-level)
 * 3. Commander structure (commander_name → commander.name)
 * 4. Missing required fields
 *
 * SAFE: Creates backups before modifying files
 *
 * Usage: node scripts/fix-schema-mismatches.js [--dry-run] [--backup-dir <path>]
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
    'America': 'american'
};

let dryRun = false;
let backupDir = null;

async function main() {
    const args = process.argv.slice(2);
    dryRun = args.includes('--dry-run');

    const backupDirIndex = args.indexOf('--backup-dir');
    if (backupDirIndex !== -1 && args[backupDirIndex + 1]) {
        backupDir = path.join(PROJECT_ROOT, args[backupDirIndex + 1]);
    } else {
        backupDir = path.join(PROJECT_ROOT, 'data/backups', `schema_fix_${Date.now()}`);
    }

    console.log('\n' + '═'.repeat(80));
    console.log('  🔧 SCHEMA FIX - Transforming Units to Unified Schema');
    console.log('═'.repeat(80));
    console.log('');

    if (dryRun) {
        console.log('🔍 DRY RUN MODE - No files will be modified\n');
    }

    if (!dryRun) {
        console.log(`💾 Backup directory: ${backupDir}\n`);
        await fs.mkdir(backupDir, { recursive: true });
    }

    // Load validation report
    console.log('📖 Loading validation report...');
    const reportPath = path.join(PROJECT_ROOT, 'data/SCHEMA_VALIDATION_REPORT.json');
    let report;

    try {
        report = JSON.parse(await fs.readFile(reportPath, 'utf-8'));
    } catch (error) {
        console.error('❌ Could not load validation report. Run validate-schema.js first.');
        process.exit(1);
    }

    console.log(`   Found ${report.violations.length} units with issues\n`);

    // Process each violation
    const fixes = {
        nationFixed: 0,
        structureTransformed: 0,
        fieldsAdded: 0,
        skipped: 0,
        errors: []
    };

    for (const violation of report.violations) {
        console.log(`Processing: ${violation.file}`);

        try {
            const result = await fixUnitFile(violation.path);

            if (result.skipped) {
                fixes.skipped++;
                console.log(`   ⚠️  Skipped: ${result.reason}\n`);
            } else {
                if (result.nationFixed) fixes.nationFixed++;
                if (result.structureTransformed) fixes.structureTransformed++;
                if (result.fieldsAdded > 0) fixes.fieldsAdded += result.fieldsAdded;

                const actions = [];
                if (result.nationFixed) actions.push('nation standardized');
                if (result.structureTransformed) actions.push('structure transformed');
                if (result.fieldsAdded > 0) actions.push(`${result.fieldsAdded} fields added`);

                console.log(`   ✅ Fixed: ${actions.join(', ')}\n`);
            }
        } catch (error) {
            fixes.errors.push({ file: violation.file, error: error.message });
            console.log(`   ❌ Error: ${error.message}\n`);
        }
    }

    console.log('═'.repeat(80));
    console.log('  FIX SUMMARY');
    console.log('═'.repeat(80));
    console.log('');
    console.log(`Units processed: ${report.violations.length}`);
    console.log(`✅ Nation names fixed: ${fixes.nationFixed}`);
    console.log(`✅ Structures transformed: ${fixes.structureTransformed}`);
    console.log(`✅ Fields added: ${fixes.fieldsAdded}`);
    console.log(`⚠️  Skipped: ${fixes.skipped}`);
    console.log(`❌ Errors: ${fixes.errors.length}`);
    console.log('');

    if (fixes.errors.length > 0) {
        console.log('Errors:');
        for (const err of fixes.errors) {
            console.log(`   ${err.file}: ${err.error}`);
        }
        console.log('');
    }

    if (dryRun) {
        console.log('🔍 DRY RUN COMPLETE - No files were modified');
    } else {
        console.log(`💾 Backups saved to: ${backupDir}`);
        console.log('✅ Schema fixes applied. Run validate-schema.js to verify.');
    }
}

/**
 * Fix a single unit JSON file
 */
async function fixUnitFile(filePath) {
    const result = {
        nationFixed: false,
        structureTransformed: false,
        fieldsAdded: 0,
        skipped: false,
        reason: null
    };

    // Read file
    let jsonData;
    try {
        jsonData = await fs.readFile(filePath, 'utf-8');
    } catch (error) {
        result.skipped = true;
        result.reason = `Could not read file: ${error.message}`;
        return result;
    }

    // Parse JSON
    let unit;
    try {
        unit = JSON.parse(jsonData);
    } catch (error) {
        result.skipped = true;
        result.reason = `Invalid JSON - manual fix required: ${error.message}`;
        return result;
    }

    // Backup original
    if (!dryRun) {
        const backupPath = path.join(backupDir, path.basename(filePath));
        await fs.writeFile(backupPath, jsonData);
    }

    let modified = false;

    // Fix 1: Standardize nation name
    const nation = unit.nation || unit.unit_identification?.nation;
    if (nation && NATION_MAPPING[nation]) {
        if (unit.nation) {
            unit.nation = NATION_MAPPING[nation];
        } else if (unit.unit_identification?.nation) {
            unit.unit_identification.nation = NATION_MAPPING[nation];
        }
        result.nationFixed = true;
        modified = true;
    }

    // Fix 2: Transform nested structure to unified schema
    if (unit.unit_identification && !unit.nation) {
        // Transform unit_identification.* to top-level
        unit.nation = unit.unit_identification.nation;
        unit.quarter = unit.unit_identification.quarter || unit.quarter;
        unit.unit_designation = unit.unit_identification.unit_designation || unit.unit_designation;
        unit.unit_type = unit.unit_identification.unit_type || unit.unit_type;
        unit.organization_level = unit.unit_identification.organization_level || unit.organization_level;

        result.structureTransformed = true;
        modified = true;
    }

    // Fix 3: Transform command structure
    if (unit.command?.commander_name && !unit.command.commander) {
        unit.command.commander = {
            name: unit.command.commander_name,
            rank: unit.command.commander_rank || 'Unknown'
        };
        delete unit.command.commander_name;
        delete unit.command.commander_rank;
        modified = true;
    }

    // Fix 4: Transform personnel_summary to top-level
    if (unit.personnel_summary && !unit.total_personnel) {
        unit.total_personnel = unit.personnel_summary.total_personnel || 0;
        unit.officers = unit.personnel_summary.officers || 0;
        unit.ncos = unit.personnel_summary.ncos || 0;
        unit.enlisted = unit.personnel_summary.enlisted || 0;
        modified = true;
    }

    // Fix 5: Add missing required fields
    if (!unit.organization_level && unit.schema_type) {
        // Infer from schema_type
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
        result.fieldsAdded++;
        modified = true;
    }

    if (!unit.validation && (unit.data_quality || unit.metadata)) {
        // Create validation object from data_quality or metadata
        unit.validation = {
            source: unit.data_quality?.primary_sources || unit.metadata?.sources || ['Unknown'],
            confidence: unit.data_quality?.confidence_score || 70,
            last_updated: unit.metadata?.last_updated || new Date().toISOString().split('T')[0],
            known_gaps: unit.data_quality?.data_gaps || [],
            aggregation_status: 'manually_entered'
        };
        result.fieldsAdded++;
        modified = true;
    }

    // Save if modified
    if (modified && !dryRun) {
        await fs.writeFile(filePath, JSON.stringify(unit, null, 2));
    }

    return result;
}

// Run
main().catch(error => {
    console.error('❌ Fix failed:', error.message);
    console.error(error.stack);
    process.exit(1);
});
