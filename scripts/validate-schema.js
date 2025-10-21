#!/usr/bin/env node

/**
 * Schema Validator - Validate all unit JSON files against unified schema
 *
 * Checks:
 * 1. Required fields present
 * 2. Allowed values (nation, organization_level, etc.)
 * 3. Data types correct
 * 4. Math validation rules (tanks.total = sum of subtypes)
 * 5. Schema structure compliance
 * 6. Commander validation (not NULL unless confidence < 50%)
 *
 * Usage: node scripts/validate-schema.js [--fix] [--verbose]
 */

const fs = require('fs').promises;
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const SCHEMA_PATH = path.join(PROJECT_ROOT, 'schemas/unified_toe_schema.json');

// Validation configuration
const ALLOWED_NATIONS = ['german', 'italian', 'british', 'american', 'french'];
const ALLOWED_ORG_LEVELS = ['theater', 'corps', 'division', 'regiment', 'battalion', 'company', 'platoon', 'squad'];
const ALLOWED_SCHEMA_TYPES = ['theater_scm', 'corps_toe', 'division_toe', 'regiment_toe', 'battalion_toe', 'company_toe', 'platoon_toe', 'squad_toe'];

let verbose = false;

async function main() {
    const args = process.argv.slice(2);
    verbose = args.includes('--verbose') || args.includes('-v');

    console.log('\n' + '═'.repeat(80));
    console.log('  📋 SCHEMA VALIDATION - Checking Unit TO&E Files');
    console.log('═'.repeat(80));
    console.log('');

    // Load schema for reference
    console.log('📖 Loading unified schema...');
    const schema = JSON.parse(await fs.readFile(SCHEMA_PATH, 'utf-8'));
    console.log(`   Schema version: ${schema.schema_version}`);
    console.log('');

    // Scan for all unit JSON files
    console.log('🔍 Scanning for unit JSON files...');
    const unitFiles = await scanForUnitFiles();
    console.log(`   Found ${unitFiles.length} unit JSON files`);
    console.log('');

    // Validate each file
    console.log('✅ Validating units...');
    const results = {
        total: unitFiles.length,
        passed: 0,
        failed: 0,
        warnings: 0,
        violations: []
    };

    for (const filePath of unitFiles) {
        const fileName = path.basename(filePath);
        const result = await validateUnitFile(filePath, schema);

        if (result.critical.length === 0 && result.warnings.length === 0) {
            results.passed++;
            if (verbose) console.log(`   ✅ ${fileName}`);
        } else if (result.critical.length > 0) {
            results.failed++;
            console.log(`   ❌ ${fileName}`);
            results.violations.push({ file: fileName, path: filePath, ...result });
        } else {
            results.warnings++;
            if (verbose) console.log(`   ⚠️  ${fileName}`);
            results.violations.push({ file: fileName, path: filePath, ...result });
        }
    }

    console.log('');
    console.log('═'.repeat(80));
    console.log('  VALIDATION SUMMARY');
    console.log('═'.repeat(80));
    console.log('');
    console.log(`Total files validated: ${results.total}`);
    console.log(`✅ Passed: ${results.passed} (${((results.passed / results.total) * 100).toFixed(1)}%)`);
    console.log(`❌ Failed: ${results.failed} (${((results.failed / results.total) * 100).toFixed(1)}%)`);
    console.log(`⚠️  Warnings: ${results.warnings} (${((results.warnings / results.total) * 100).toFixed(1)}%)`);
    console.log('');

    // Report violations
    if (results.violations.length > 0) {
        console.log('═'.repeat(80));
        console.log('  VIOLATIONS REPORT');
        console.log('═'.repeat(80));
        console.log('');

        for (const violation of results.violations) {
            const severity = violation.critical.length > 0 ? '❌' : '⚠️';
            console.log(`${severity} ${violation.file}`);
            console.log(`   Path: ${violation.path}`);

            if (violation.critical.length > 0) {
                console.log(`   Critical Issues (${violation.critical.length}):`);
                for (const issue of violation.critical) {
                    console.log(`      • ${issue}`);
                }
            }

            if (violation.warnings.length > 0 && verbose) {
                console.log(`   Warnings (${violation.warnings.length}):`);
                for (const warning of violation.warnings) {
                    console.log(`      • ${warning}`);
                }
            }

            console.log('');
        }

        // Save detailed report
        const reportPath = path.join(PROJECT_ROOT, 'data/SCHEMA_VALIDATION_REPORT.json');
        await fs.writeFile(reportPath, JSON.stringify(results, null, 2));
        console.log(`📄 Detailed report saved to: ${reportPath}`);
        console.log('');
    }

    // Exit with error code if failures
    if (results.failed > 0) {
        console.log('❌ Validation failed. Please fix critical issues.');
        process.exit(1);
    } else if (results.warnings > 0) {
        console.log('⚠️  Validation passed with warnings. Review recommended.');
        process.exit(0);
    } else {
        console.log('✅ All units passed validation!');
        process.exit(0);
    }
}

/**
 * Scan for all unit JSON files
 * Updated for Architecture v4.0 - uses canonical locations
 */
async function scanForUnitFiles() {
    // Architecture v4.0: Use canonical location for all units
    const unitsDir = path.join(PROJECT_ROOT, 'data/output/units');
    const files = [];

    try {
        const unitFiles = await fs.readdir(unitsDir);
        for (const file of unitFiles) {
            if (file.endsWith('_toe.json')) {
                files.push(path.join(unitsDir, file));
            }
        }
    } catch (error) {
        console.error(`❌ Error scanning units directory: ${error.message}`);
    }

    return files;
}

/**
 * Validate a single unit JSON file
 */
async function validateUnitFile(filePath, schema) {
    const result = {
        critical: [],
        warnings: []
    };

    try {
        const jsonData = await fs.readFile(filePath, 'utf-8');
        const unit = JSON.parse(jsonData);

        // Check 1: Schema structure (unified vs nested)
        const isUnifiedStructure = hasTopLevelField(unit, 'nation') && hasTopLevelField(unit, 'quarter');
        const isNestedStructure = hasNestedField(unit, 'unit_identification.nation');

        if (!isUnifiedStructure && isNestedStructure) {
            result.critical.push('Uses nested structure (unit_identification.*) instead of unified schema top-level fields');
        } else if (!isUnifiedStructure && !isNestedStructure) {
            result.critical.push('Missing required fields: nation and quarter');
        }

        // Extract nation and quarter (handle both structures)
        let nation = unit.nation || unit.unit_identification?.nation || 'unknown';
        let quarter = unit.quarter || unit.unit_identification?.quarter || 'unknown';
        let confidence = unit.validation?.confidence || unit.data_quality?.confidence_score || 0;

        // Check 2: Nation allowed values
        if (!ALLOWED_NATIONS.includes(nation.toLowerCase())) {
            result.critical.push(`Invalid nation: "${nation}" (allowed: ${ALLOWED_NATIONS.join(', ')})`);
        }

        // Check 3: Quarter format
        if (quarter !== 'unknown' && !/^\d{4}-Q[1-4]$/.test(quarter)) {
            result.warnings.push(`Quarter format should be YYYY-QN: "${quarter}"`);
        }

        // Check 4: Organization level
        const orgLevel = unit.organization_level || unit.unit_identification?.organization_level;
        if (orgLevel && !ALLOWED_ORG_LEVELS.includes(orgLevel)) {
            result.warnings.push(`Invalid organization_level: "${orgLevel}"`);
        }

        // Check 5: Schema type
        const schemaType = unit.schema_type;
        if (schemaType && !ALLOWED_SCHEMA_TYPES.includes(schemaType)) {
            result.warnings.push(`Invalid schema_type: "${schemaType}"`);
        }

        // Check 6: Commander validation
        // Support schema v3.1.0 nested structure (commander.commander.name)
        const commanderName = unit.commander?.commander?.name ||
                              unit.command?.commander?.name ||
                              unit.command?.commander_name ||
                              unit.commander?.name ||
                              null;

        if (!commanderName && confidence >= 50) {
            result.critical.push(`Commander name is NULL but confidence is ${confidence}% (should have commander name when confidence ≥ 50%)`);
        } else if (commanderName === 'Unknown' && confidence >= 50) {
            result.warnings.push(`Commander is "Unknown" with ${confidence}% confidence`);
        }

        // Check 7: Personnel totals
        const totalPersonnel = unit.total_personnel || unit.personnel_summary?.total_personnel || 0;
        const officers = unit.officers || unit.personnel_summary?.officers || 0;
        const ncos = unit.ncos || unit.personnel_summary?.ncos || 0;
        const enlisted = unit.enlisted || unit.personnel_summary?.enlisted || 0;

        if (totalPersonnel > 0) {
            const sum = officers + ncos + enlisted;
            const diff = Math.abs(totalPersonnel - sum);
            const percentDiff = (diff / totalPersonnel) * 100;

            if (percentDiff > 5) {
                result.warnings.push(`Personnel sum mismatch: total=${totalPersonnel} but officers+ncos+enlisted=${sum} (${percentDiff.toFixed(1)}% diff)`);
            }
        } else if (confidence > 50) {
            result.warnings.push('Total personnel is 0 with confidence > 50%');
        }

        // Check 8: Tank totals
        const tanks = unit.tanks || unit.equipment_summary?.tanks || {};
        const tanksTotal = tanks.total || 0;

        // Handle both nested object {total: N} and direct value N formats
        const getTankCount = (tankType) => {
            if (!tankType) return 0;
            if (typeof tankType === 'number') return tankType;
            if (typeof tankType === 'object' && tankType.total !== undefined) return tankType.total;
            return 0;
        };

        const tanksHeavy = getTankCount(tanks.heavy) || getTankCount(tanks.heavy_tanks);
        const tanksMedium = getTankCount(tanks.medium) || getTankCount(tanks.medium_tanks);
        const tanksLight = getTankCount(tanks.light) || getTankCount(tanks.light_tanks);

        if (tanksTotal > 0) {
            const sum = tanksHeavy + tanksMedium + tanksLight;
            if (tanksTotal !== sum) {
                result.critical.push(`Tank total mismatch: total=${tanksTotal} but heavy+medium+light=${sum}`);
            }
        }

        // Check 9: Confidence score
        if (confidence < 75) {
            result.warnings.push(`Confidence score ${confidence}% is below recommended minimum of 75%`);
        }

        // Check 10: Required fields (unified schema)
        if (isUnifiedStructure) {
            const requiredFields = ['schema_type', 'schema_version', 'nation', 'quarter',
                                   'unit_designation', 'organization_level', 'validation'];

            for (const field of requiredFields) {
                if (!unit[field]) {
                    result.critical.push(`Missing required field: ${field}`);
                }
            }
        }

    } catch (error) {
        result.critical.push(`Failed to parse JSON: ${error.message}`);
    }

    return result;
}

/**
 * Check if object has top-level field
 */
function hasTopLevelField(obj, field) {
    return obj.hasOwnProperty(field) && obj[field] !== null && obj[field] !== undefined;
}

/**
 * Check if object has nested field (dot notation)
 */
function hasNestedField(obj, fieldPath) {
    const parts = fieldPath.split('.');
    let current = obj;

    for (const part of parts) {
        if (!current || !current.hasOwnProperty(part)) {
            return false;
        }
        current = current[part];
    }

    return current !== null && current !== undefined;
}

// Run
main().catch(error => {
    console.error('❌ Validation failed:', error.message);
    console.error(error.stack);
    process.exit(1);
});
