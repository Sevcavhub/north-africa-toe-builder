#!/usr/bin/env node

/**
 * Unit Quality Audit - Deep Analysis
 *
 * Performs detailed quality checks on all unit JSONs:
 * - Schema v3.0 compliance
 * - Template v2.0 compliance
 * - Equipment variant detail (NO rollups)
 * - Supply/logistics data
 * - Weather/environmental data
 * - Confidence scores
 */

const fs = require('fs');
const path = require('path');

const UNITS_DIR = path.join(__dirname, '../data/output/units');
const unitFiles = fs.readdirSync(UNITS_DIR).filter(f => f.endsWith('.json'));

console.log('════════════════════════════════════════════════════════════════════════════════');
console.log('  🔍 UNIT QUALITY AUDIT - DETAILED ANALYSIS');
console.log('════════════════════════════════════════════════════════════════════════════════\n');

console.log(`Auditing ${unitFiles.length} units...\n`);

const audit = {
  total: 0,
  schemaIssues: {
    topLevelFields: 0,           // Missing nation, quarter, organization_level
    nestedCommander: 0,          // Commander not nested object
    missingConfidence: 0,        // No metadata.confidence_score
    invalidNation: 0,            // Nation not lowercase (german, italian, etc.)
  },
  equipmentIssues: {
    missingVariants: 0,          // Tanks with rollup counts instead of variants
    hasRollups: 0,               // Has "total" fields in equipment (should only be top-level)
    artilleryNoVariants: 0,      // Artillery without variant breakdown
  },
  supplyIssues: {
    noSupplyStatus: 0,           // Missing supply_status
    noFuelReserves: 0,           // Missing fuel_reserves
    noAmmoReserves: 0,           // Missing ammunition
    noOperationalRadius: 0,      // Missing operational_radius
  },
  weatherIssues: {
    noSeasonQuarter: 0,          // Missing season_quarter
    noTemperature: 0,            // Missing temperature_range
    noTerrain: 0,                // Missing terrain_type
  },
  validationTotals: {
    tankTotalMismatch: 0,        // tanks.total != heavy + medium + light
    personnelMismatch: 0,        // personnel total != officers + ncos + enlisted
  },
  goodUnits: 0,
  samples: {
    excellent: [],               // Units with >90% compliance
    needsWork: [],               // Units with <50% compliance
  }
};

// Schema v3.0 required top-level fields
const requiredFields = ['nation', 'quarter', 'organization_level', 'unit_designation'];

// Check each unit
unitFiles.forEach(file => {
  try {
    const unitPath = path.join(UNITS_DIR, file);
    const unit = JSON.parse(fs.readFileSync(unitPath, 'utf-8'));
    audit.total++;

    let issueCount = 0;

    // 1. Schema compliance
    requiredFields.forEach(field => {
      if (!unit[field]) {
        audit.schemaIssues.topLevelFields++;
        issueCount++;
      }
    });

    // Check commander is nested object
    if (!unit.commander || typeof unit.commander !== 'object' || !unit.commander.name) {
      audit.schemaIssues.nestedCommander++;
      issueCount++;
    }

    // Check nation value is lowercase
    if (unit.nation && unit.nation !== unit.nation.toLowerCase()) {
      audit.schemaIssues.invalidNation++;
      issueCount++;
    }

    // Check confidence score exists
    if (!unit.metadata || !unit.metadata.confidence_score) {
      audit.schemaIssues.missingConfidence++;
      issueCount++;
    }

    // 2. Equipment variant detail
    if (unit.tanks) {
      // Check if tanks have variant breakdown
      const hasVariants = Object.keys(unit.tanks).some(k => k !== 'total' && k !== 'heavy' && k !== 'medium' && k !== 'light');
      if (!hasVariants && unit.tanks.total > 0) {
        audit.equipmentIssues.missingVariants++;
        issueCount++;
      }

      // Check for rollup fields (should only be at top level)
      if (unit.tanks.heavy && typeof unit.tanks.heavy === 'object' && unit.tanks.heavy.total) {
        audit.equipmentIssues.hasRollups++;
        issueCount++;
      }
    }

    // Check artillery variants
    if (unit.field_artillery) {
      const hasVariants = Object.keys(unit.field_artillery).some(k => k !== 'total');
      if (!hasVariants && (unit.field_artillery.total || Object.keys(unit.field_artillery).length > 1)) {
        audit.equipmentIssues.artilleryNoVariants++;
        issueCount++;
      }
    }

    // 3. Supply/logistics data (Schema v3.0 Section 6)
    if (!unit.supply_status) {
      audit.supplyIssues.noSupplyStatus++;
      issueCount++;
    }
    if (!unit.fuel_reserves) {
      audit.supplyIssues.noFuelReserves++;
      issueCount++;
    }
    if (!unit.ammunition) {
      audit.supplyIssues.noAmmoReserves++;
      issueCount++;
    }
    if (!unit.operational_radius) {
      audit.supplyIssues.noOperationalRadius++;
      issueCount++;
    }

    // 4. Weather/environmental data (Schema v3.0 Section 7)
    if (!unit.season_quarter) {
      audit.weatherIssues.noSeasonQuarter++;
      issueCount++;
    }
    if (!unit.temperature_range) {
      audit.weatherIssues.noTemperature++;
      issueCount++;
    }
    if (!unit.terrain_type) {
      audit.weatherIssues.noTerrain++;
      issueCount++;
    }

    // 5. Validation checks
    if (unit.tanks && unit.tanks.total) {
      const heavy = unit.tanks.heavy || 0;
      const medium = unit.tanks.medium || 0;
      const light = unit.tanks.light || 0;
      const calculated = heavy + medium + light;

      if (Math.abs(unit.tanks.total - calculated) > unit.tanks.total * 0.05) {
        audit.validationTotals.tankTotalMismatch++;
        issueCount++;
      }
    }

    // Track quality
    const complianceRate = 1 - (issueCount / 20); // Out of ~20 checks
    if (complianceRate > 0.9) {
      audit.goodUnits++;
      if (audit.samples.excellent.length < 5) {
        audit.samples.excellent.push(file);
      }
    } else if (complianceRate < 0.5) {
      if (audit.samples.needsWork.length < 5) {
        audit.samples.needsWork.push(file);
      }
    }

  } catch (err) {
    console.log(`❌ ${file}: ${err.message}`);
  }
});

// Report results
console.log('📊 **SCHEMA COMPLIANCE (v3.0)**\n');
console.log(`   Missing Top-Level Fields:  ${audit.schemaIssues.topLevelFields}/${audit.total} (${((audit.schemaIssues.topLevelFields/audit.total)*100).toFixed(1)}%)`);
console.log(`   Commander Not Nested:      ${audit.schemaIssues.nestedCommander}/${audit.total} (${((audit.schemaIssues.nestedCommander/audit.total)*100).toFixed(1)}%)`);
console.log(`   Missing Confidence Score:  ${audit.schemaIssues.missingConfidence}/${audit.total} (${((audit.schemaIssues.missingConfidence/audit.total)*100).toFixed(1)}%)`);
console.log(`   Invalid Nation Value:      ${audit.schemaIssues.invalidNation}/${audit.total} (${((audit.schemaIssues.invalidNation/audit.total)*100).toFixed(1)}%)`);

console.log('\n⚙️  **EQUIPMENT DETAIL COMPLIANCE**\n');
console.log(`   Missing Tank Variants:     ${audit.equipmentIssues.missingVariants}/${audit.total} (${((audit.equipmentIssues.missingVariants/audit.total)*100).toFixed(1)}%)`);
console.log(`   Has Rollup Fields:         ${audit.equipmentIssues.hasRollups}/${audit.total} (${((audit.equipmentIssues.hasRollups/audit.total)*100).toFixed(1)}%)`);
console.log(`   Artillery No Variants:     ${audit.equipmentIssues.artilleryNoVariants}/${audit.total} (${((audit.equipmentIssues.artilleryNoVariants/audit.total)*100).toFixed(1)}%)`);

console.log('\n🛢️  **SUPPLY/LOGISTICS DATA (Section 6)**\n');
console.log(`   Missing Supply Status:     ${audit.supplyIssues.noSupplyStatus}/${audit.total} (${((audit.supplyIssues.noSupplyStatus/audit.total)*100).toFixed(1)}%)`);
console.log(`   Missing Fuel Reserves:     ${audit.supplyIssues.noFuelReserves}/${audit.total} (${((audit.supplyIssues.noFuelReserves/audit.total)*100).toFixed(1)}%)`);
console.log(`   Missing Ammo Reserves:     ${audit.supplyIssues.noAmmoReserves}/${audit.total} (${((audit.supplyIssues.noAmmoReserves/audit.total)*100).toFixed(1)}%)`);
console.log(`   Missing Operational Radius:${audit.supplyIssues.noOperationalRadius}/${audit.total} (${((audit.supplyIssues.noOperationalRadius/audit.total)*100).toFixed(1)}%)`);

console.log('\n🌡️  **WEATHER/ENVIRONMENTAL DATA (Section 7)**\n');
console.log(`   Missing Season/Quarter:    ${audit.weatherIssues.noSeasonQuarter}/${audit.total} (${((audit.weatherIssues.noSeasonQuarter/audit.total)*100).toFixed(1)}%)`);
console.log(`   Missing Temperature Range: ${audit.weatherIssues.noTemperature}/${audit.total} (${((audit.weatherIssues.noTemperature/audit.total)*100).toFixed(1)}%)`);
console.log(`   Missing Terrain Type:      ${audit.weatherIssues.noTerrain}/${audit.total} (${((audit.weatherIssues.noTerrain/audit.total)*100).toFixed(1)}%)`);

console.log('\n✅ **VALIDATION CHECKS**\n');
console.log(`   Tank Total Mismatch:       ${audit.validationTotals.tankTotalMismatch}/${audit.total} (${((audit.validationTotals.tankTotalMismatch/audit.total)*100).toFixed(1)}%)`);
console.log(`   Personnel Mismatch:        ${audit.validationTotals.personnelMismatch}/${audit.total} (${((audit.validationTotals.personnelMismatch/audit.total)*100).toFixed(1)}%)`);

console.log('\n🏆 **OVERALL QUALITY**\n');
console.log(`   High Quality Units (>90%): ${audit.goodUnits}/${audit.total} (${((audit.goodUnits/audit.total)*100).toFixed(1)}%)`);

if (audit.samples.excellent.length > 0) {
  console.log('\n   📗 Excellent units (use as templates):');
  audit.samples.excellent.forEach(f => console.log(`      - ${f.replace('_toe.json', '')}`));
}

if (audit.samples.needsWork.length > 0) {
  console.log('\n   📙 Units needing work (<50% compliance):');
  audit.samples.needsWork.forEach(f => console.log(`      - ${f.replace('_toe.json', '')}`));
}

// Critical recommendations
console.log('\n🚨 **CRITICAL ISSUES REQUIRING ATTENTION**\n');

const criticalIssues = [];

if (audit.schemaIssues.nestedCommander / audit.total > 0.1) {
  criticalIssues.push(`   • ${((audit.schemaIssues.nestedCommander/audit.total)*100).toFixed(0)}% units missing nested commander object (Schema v3.0 violation)`);
}

if (audit.supplyIssues.noSupplyStatus / audit.total > 0.5) {
  criticalIssues.push(`   • ${((audit.supplyIssues.noSupplyStatus/audit.total)*100).toFixed(0)}% units missing supply_status (Section 6 required for scenarios)`);
}

if (audit.weatherIssues.noSeasonQuarter / audit.total > 0.5) {
  criticalIssues.push(`   • ${((audit.weatherIssues.noSeasonQuarter/audit.total)*100).toFixed(0)}% units missing season_quarter (Section 7 required for scenarios)`);
}

if (audit.equipmentIssues.missingVariants / audit.total > 0.2) {
  criticalIssues.push(`   • ${((audit.equipmentIssues.missingVariants/audit.total)*100).toFixed(0)}% units missing equipment variants (rollups instead of detail)`);
}

if (criticalIssues.length === 0) {
  console.log('   ✅ No critical issues detected!');
} else {
  criticalIssues.forEach(issue => console.log(issue));
}

console.log('\n════════════════════════════════════════════════════════════════════════════════');
console.log('📝 Audit completed: ' + new Date().toLocaleString());
console.log('════════════════════════════════════════════════════════════════════════════════\n');
