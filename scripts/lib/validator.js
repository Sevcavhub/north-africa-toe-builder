/**
 * Validation Library - Reusable schema validation for unit JSON files
 *
 * Usage:
 *   const { validateUnit, validateUnitFile } = require('./lib/validator');
 *   const result = validateUnit(unitObject);
 *   if (result.critical.length > 0) {
 *     console.error('Validation failed:', result.critical);
 *   }
 */

const fs = require('fs');
const path = require('path');

// Validation configuration
const ALLOWED_NATIONS = ['german', 'italian', 'british', 'american', 'french'];
const ALLOWED_ORG_LEVELS = ['theater', 'corps', 'division', 'regiment', 'battalion', 'company', 'platoon', 'squad'];
const ALLOWED_SCHEMA_TYPES = ['theater_scm', 'corps_toe', 'division_toe', 'regiment_toe', 'battalion_toe', 'company_toe', 'platoon_toe', 'squad_toe'];

/**
 * Validate a unit object against unified schema
 * @param {Object} unit - Unit object to validate
 * @returns {Object} { critical: [], warnings: [] }
 */
function validateUnit(unit) {
    const result = {
        critical: [],
        warnings: []
    };

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
    const commanderName = unit.command?.commander?.name ||
                          unit.command?.commander_name ||
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

    const tanksHeavy = getTankCount(tanks.heavy_tanks);
    const tanksMedium = getTankCount(tanks.medium_tanks);
    const tanksLight = getTankCount(tanks.light_tanks);

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

    return result;
}

/**
 * Validate a unit JSON file
 * @param {string} filePath - Path to JSON file
 * @returns {Object} { critical: [], warnings: [] }
 */
function validateUnitFile(filePath) {
    const result = {
        critical: [],
        warnings: []
    };

    try {
        const jsonData = fs.readFileSync(filePath, 'utf-8');
        const unit = JSON.parse(jsonData);
        return validateUnit(unit);
    } catch (error) {
        result.critical.push(`Failed to parse JSON: ${error.message}`);
        return result;
    }
}

/**
 * Validate and save unit JSON (only saves if validation passes)
 * @param {string} filePath - Path to save JSON file
 * @param {Object} unit - Unit object to validate and save
 * @param {Object} options - { force: boolean, verbose: boolean }
 * @returns {Object} { success: boolean, critical: [], warnings: [] }
 */
function validateAndSave(filePath, unit, options = {}) {
    const { force = false, verbose = false } = options;

    const validation = validateUnit(unit);

    if (validation.critical.length > 0 && !force) {
        if (verbose) {
            console.error(`❌ Validation failed for ${path.basename(filePath)}:`);
            validation.critical.forEach(issue => console.error(`   • ${issue}`));
        }
        return {
            success: false,
            ...validation
        };
    }

    // Validation passed or forced - save file
    fs.writeFileSync(filePath, JSON.stringify(unit, null, 2));

    if (verbose) {
        if (validation.critical.length > 0) {
            console.log(`⚠️  ${path.basename(filePath)} saved with CRITICAL issues (forced)`);
        } else if (validation.warnings.length > 0) {
            console.log(`✅ ${path.basename(filePath)} saved (${validation.warnings.length} warnings)`);
        } else {
            console.log(`✅ ${path.basename(filePath)} saved successfully`);
        }
    }

    return {
        success: true,
        ...validation
    };
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

module.exports = {
    validateUnit,
    validateUnitFile,
    validateAndSave,
    ALLOWED_NATIONS,
    ALLOWED_ORG_LEVELS,
    ALLOWED_SCHEMA_TYPES
};
