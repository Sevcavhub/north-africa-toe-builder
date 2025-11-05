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
    if (quarter !== 'unknown' && !/^\d{4}q[1-4]$/.test(quarter)) {
        result.warnings.push(`Quarter format should be yyyyqn (e.g., 1943q1): "${quarter}"`);
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
    // Support both schema v3.1.0 (command.commander.name) and v3.0.0 (commander.name)
    const commanderName = unit.command?.commander?.name ||
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

    // Check 11: v3.0.0+ supply_logistics validation
    const supplyLogistics = unit.supply_logistics;
    if (!supplyLogistics) {
        result.warnings.push('Missing supply_logistics object (required in schema v3.0.0+)');
    } else {
        const requiredSupplyFields = ['fuel_reserves_days', 'ammunition_days', 'water_reserves_days', 'operational_radius_km', 'supply_status'];
        for (const field of requiredSupplyFields) {
            if (supplyLogistics[field] === undefined || supplyLogistics[field] === null) {
                result.warnings.push(`Missing supply_logistics.${field} (required in schema v3.0.0+)`);
            }
        }

        // Validate ranges
        if (supplyLogistics.operational_radius_km !== undefined && (supplyLogistics.operational_radius_km <= 0 || supplyLogistics.operational_radius_km > 2000)) {
            result.warnings.push(`operational_radius_km (${supplyLogistics.operational_radius_km}) should be 1-2000 km`);
        }
        if (supplyLogistics.fuel_reserves_days !== undefined && (supplyLogistics.fuel_reserves_days < 0 || supplyLogistics.fuel_reserves_days > 60)) {
            result.warnings.push(`fuel_reserves_days (${supplyLogistics.fuel_reserves_days}) should be 0-60 days`);
        }
    }

    // Check 12: v3.0.0+ weather_environment validation
    const weatherEnv = unit.weather_environment;
    if (!weatherEnv) {
        result.warnings.push('Missing weather_environment object (required in schema v3.0.0+)');
    } else {
        const requiredWeatherFields = ['primary_terrain', 'temperature_range_c', 'seasonal_impacts', 'environmental_challenges'];
        for (const field of requiredWeatherFields) {
            if (!weatherEnv[field]) {
                result.warnings.push(`Missing weather_environment.${field} (required in schema v3.0.0+)`);
            }
        }

        // Validate temperature range
        if (weatherEnv.temperature_range_c) {
            const tempMin = weatherEnv.temperature_range_c.min;
            const tempMax = weatherEnv.temperature_range_c.max;
            if (tempMin !== undefined && tempMax !== undefined && tempMin >= tempMax) {
                result.warnings.push(`temperature_range_c.min (${tempMin}) must be < max (${tempMax})`);
            }
        }
    }

    // Check 13: v3.1.0+ tiered extraction validation
    const validation = unit.validation;
    if (validation) {
        // Tier field (1-4)
        if (validation.tier !== undefined) {
            if (![1, 2, 3, 4].includes(validation.tier)) {
                result.warnings.push(`validation.tier must be 1-4, got: ${validation.tier}`);
            }
        }

        // Status field
        const allowedStatuses = ['production_ready', 'review_recommended', 'partial_needs_research', 'research_brief_created'];
        if (validation.status && !allowedStatuses.includes(validation.status)) {
            result.warnings.push(`validation.status must be one of: ${allowedStatuses.join(', ')}, got: ${validation.status}`);
        }

        // required_field_gaps should be array if present
        if (validation.required_field_gaps && !Array.isArray(validation.required_field_gaps)) {
            result.warnings.push('validation.required_field_gaps must be an array');
        }

        // gap_documentation should be object if present
        if (validation.gap_documentation && typeof validation.gap_documentation !== 'object') {
            result.warnings.push('validation.gap_documentation must be an object');
        }
    }

    // Check 14: discovered_units combat_evidence validation
    const discoveredUnits = unit.discovered_units;
    if (discoveredUnits && Array.isArray(discoveredUnits)) {
        for (let i = 0; i < discoveredUnits.length; i++) {
            const du = discoveredUnits[i];

            // combat_evidence is REQUIRED
            if (!du.combat_evidence || du.combat_evidence.trim() === '') {
                result.critical.push(`discovered_units[${i}] (${du.designation || 'unknown'}) missing required combat_evidence field`);
            }

            // Check for garrison/reserve keywords (should be excluded)
            const combatEvidence = (du.combat_evidence || '').toLowerCase();
            const excludedKeywords = ['garrison', 'reserve formation', 'rear-area', 'administrative', 'never engaged', 'in transit'];
            for (const keyword of excludedKeywords) {
                if (combatEvidence.includes(keyword)) {
                    result.critical.push(`discovered_units[${i}] (${du.designation || 'unknown'}) combat_evidence suggests non-combat unit (contains "${keyword}") - should be excluded`);
                }
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
