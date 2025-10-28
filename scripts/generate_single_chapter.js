#!/usr/bin/env node

/**
 * Generate single MDBook chapter for specified unit
 * Uses canonical paths (Architecture v4.0)
 *
 * Usage: node scripts/generate_single_chapter.js <nation> <quarter> <designation>
 * Example: node scripts/generate_single_chapter.js italian 1941q2 xx_corpo_d_armata_motorizzato
 */

const fs = require('fs');
const path = require('path');
const paths = require('./lib/canonical_paths');

// Get command line arguments
const args = process.argv.slice(2);
if (args.length < 3) {
  console.error('Usage: node scripts/generate_single_chapter.js <nation> <quarter> <designation>');
  console.error('Example: node scripts/generate_single_chapter.js italian 1941q2 xx_corpo_d_armata_motorizzato');
  process.exit(1);
}

const [nation, quarter, designation] = args;

// Import the chapter generator
const { generateChapter } = require('./generate_mdbook_chapters');

// Get paths using canonical path helpers
const unitPath = paths.getUnitPath(nation, quarter, designation);
const chapterPath = paths.getChapterPath(nation, quarter, designation);

console.log('='.repeat(60));
console.log('Single MDBook Chapter Generator');
console.log('='.repeat(60));
console.log(`Nation: ${nation}`);
console.log(`Quarter: ${quarter}`);
console.log(`Designation: ${designation}`);
console.log();
console.log(`Reading from: ${unitPath}`);
console.log(`Writing to: ${chapterPath}`);
console.log();

try {
  // Check if unit file exists
  if (!fs.existsSync(unitPath)) {
    console.error(`❌ ERROR: Unit file not found at ${unitPath}`);
    process.exit(1);
  }

  // Read the unit JSON
  const unitData = JSON.parse(fs.readFileSync(unitPath, 'utf8'));
  console.log(`✓ Loaded unit data: ${unitData.unit_designation}`);

  // Generate chapter (need to adapt the function to accept data directly)
  // For now, let's generate manually
  const chapter = generateChapterFromData(unitData);

  // Ensure chapters directory exists
  const chaptersDir = path.dirname(chapterPath);
  if (!fs.existsSync(chaptersDir)) {
    fs.mkdirSync(chaptersDir, { recursive: true });
    console.log(`✓ Created directory: ${chaptersDir}`);
  }

  // Write chapter
  fs.writeFileSync(chapterPath, chapter, 'utf8');
  console.log(`✓ Generated chapter: ${chapterPath}`);
  console.log();
  console.log('='.repeat(60));
  console.log('Chapter generation complete!');
  console.log('='.repeat(60));

} catch (error) {
  console.error(`❌ ERROR: ${error.message}`);
  console.error(error.stack);
  process.exit(1);
}

/**
 * Generate chapter from unit data object
 */
function generateChapterFromData(data) {
  let chapter = '';

  // Helper: Format numbers
  function formatNumber(num) {
    return num ? num.toLocaleString('en-US') : '0';
  }

  // Helper: Calculate readiness
  function calculateReadiness(operational, total) {
    if (!total || total === 0) return 0;
    return Math.round((operational / total) * 100);
  }

  // Section 1: Header
  const unitDesignation = data.unit_designation || 'Unknown Unit';
  const nation = data.nation || 'unknown';
  const quarter = data.quarter || 'Unknown';
  const unitType = data.unit_type || 'unknown';
  const parentFormation = data.parent_formation || 'Unknown';

  chapter += `# ${unitDesignation}\n\n`;
  chapter += `**Nation:** ${nation.charAt(0).toUpperCase() + nation.slice(1)}\n`;
  chapter += `**Quarter:** ${quarter}\n`;
  chapter += `**Type:** ${unitType}\n`;
  chapter += `**Parent Formation:** ${parentFormation}\n\n`;
  chapter += `---\n\n`;

  // Section 2: Corps Overview
  chapter += `## Corps Overview\n\n`;

  if (data.historical_context?.operational_situation) {
    chapter += `${data.historical_context.operational_situation}\n\n`;
  }

  if (data.tactical_doctrine?.role) {
    chapter += `**Role:** ${data.tactical_doctrine.role}\n\n`;
  }

  // Section 3: Command
  chapter += `## Command\n\n`;
  chapter += `| Position | Name | Rank |\n`;
  chapter += `|----------|------|------|\n`;

  const commanderName = data.command?.commander?.name || 'Unknown';
  const commanderRank = data.command?.commander?.rank || 'Unknown';
  chapter += `| **Commanding Officer** | ${commanderName} | ${commanderRank} |\n`;

  const chiefStaff = data.command?.chief_of_staff;
  if (chiefStaff && chiefStaff.name) {
    chapter += `| **Chief of Staff** | ${chiefStaff.name} | ${chiefStaff.rank || '-'} |\n`;
  }

  chapter += `\n`;
  chapter += `**Headquarters:** ${data.command?.headquarters_location || 'Unknown'}\n\n`;

  if (data.command?.commander?.note) {
    chapter += `**Command Notes:** ${data.command.commander.note}\n\n`;
  }

  if (data.command?.staff_strength) {
    chapter += `**Headquarters Staff:**\n`;
    chapter += `- Officers: ${data.command.staff_strength.officers}\n`;
    chapter += `- NCOs: ${data.command.staff_strength.ncos}\n`;
    chapter += `- Enlisted: ${data.command.staff_strength.enlisted}\n`;
    chapter += `- Total: ${data.command.staff_strength.total}\n\n`;
    if (data.command.staff_strength.note) {
      chapter += `*${data.command.staff_strength.note}*\n\n`;
    }
  }

  // Section 4: Personnel Strength
  chapter += `## Personnel Strength\n\n`;

  const totalPersonnel = data.total_personnel || 0;
  const officers = data.officers || 0;
  const ncos = data.ncos || 0;
  const enlisted = data.enlisted || 0;

  chapter += `| Category | Count | Percentage |\n`;
  chapter += `|----------|-------|------------|\n`;
  chapter += `| **Total Personnel** | ${formatNumber(totalPersonnel)} | 100% |\n`;
  chapter += `| Officers | ${formatNumber(officers)} | ${totalPersonnel ? ((officers/totalPersonnel)*100).toFixed(1) : 0}% |\n`;
  chapter += `| NCOs | ${formatNumber(ncos)} | ${totalPersonnel ? ((ncos/totalPersonnel)*100).toFixed(1) : 0}% |\n`;
  chapter += `| Enlisted | ${formatNumber(enlisted)} | ${totalPersonnel ? ((enlisted/totalPersonnel)*100).toFixed(1) : 0}% |\n`;
  chapter += `\n`;

  // Section 5: Armoured Strength
  if (data.tanks && data.tanks.total > 0) {
    chapter += `## Armoured Strength\n\n`;
    chapter += `### Tank Summary\n\n`;
    chapter += `| Category | Total | Operational | Readiness |\n`;
    chapter += `|----------|-------|-------------|----------|\n`;

    // Medium tanks
    if (data.tanks.medium_tanks && data.tanks.medium_tanks.total > 0) {
      const mediumTanks = data.tanks.medium_tanks;
      const readiness = calculateReadiness(mediumTanks.operational, mediumTanks.total);
      chapter += `| **Medium Tanks** | ${mediumTanks.total} | ${mediumTanks.operational} | ${readiness}% |\n`;

      if (mediumTanks.variants) {
        Object.entries(mediumTanks.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} | ${variant.count} | ${variant.operational} | - |\n`;
        });
      }
    }

    // Light tanks
    if (data.tanks.light_tanks && data.tanks.light_tanks.total > 0) {
      const lightTanks = data.tanks.light_tanks;
      const readiness = calculateReadiness(lightTanks.operational, lightTanks.total);
      chapter += `| **Light Tanks** | ${lightTanks.total} | ${lightTanks.operational} | ${readiness}% |\n`;

      if (lightTanks.variants) {
        Object.entries(lightTanks.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} | ${variant.count} | ${variant.operational} | - |\n`;
        });
      }
    }

    chapter += `\n`;
  }

  // Section 6: Artillery Strength
  if (data.artillery_total > 0) {
    chapter += `## Artillery Strength\n\n`;
    chapter += `| Category | Quantity |\n`;
    chapter += `|----------|----------|\n`;
    chapter += `| **Total Artillery** | ${data.artillery_total} |\n`;

    if (data.field_artillery && data.field_artillery.total > 0) {
      chapter += `| **Field Artillery** | ${data.field_artillery.total} |\n`;
      if (data.field_artillery.variants) {
        Object.entries(data.field_artillery.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} (${variant.caliber}) | ${variant.count} |\n`;
        });
      }
    }

    if (data.anti_tank && data.anti_tank.total > 0) {
      chapter += `| **Anti-Tank Guns** | ${data.anti_tank.total} |\n`;
      if (data.anti_tank.variants) {
        Object.entries(data.anti_tank.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} (${variant.caliber}) | ${variant.count} |\n`;
        });
      }
    }

    if (data.anti_aircraft && data.anti_aircraft.total > 0) {
      chapter += `| **Anti-Aircraft Guns** | ${data.anti_aircraft.total} |\n`;
      if (data.anti_aircraft.variants) {
        Object.entries(data.anti_aircraft.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} (${variant.caliber}) | ${variant.count} |\n`;
        });
      }
    }

    if (data.mortars && data.mortars.total > 0) {
      chapter += `| **Mortars** | ${data.mortars.total} |\n`;
      if (data.mortars.variants) {
        Object.entries(data.mortars.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} (${variant.caliber}) | ${variant.count} |\n`;
        });
      }
    }

    chapter += `\n`;
  }

  // Section 7: Armoured Cars
  if (data.armored_cars && data.armored_cars.total > 0) {
    chapter += `## Armoured Cars\n\n`;
    chapter += `| Category | Quantity |\n`;
    chapter += `|----------|----------|\n`;
    chapter += `| **Total Armoured Cars** | ${data.armored_cars.total} |\n`;

    if (data.armored_cars.variants) {
      Object.entries(data.armored_cars.variants).forEach(([name, variant]) => {
        chapter += `| ↳ ${name} | ${variant.count} |\n`;
      });
    }

    chapter += `\n`;
  }

  // Section 8: Infantry Weapons
  if (data.top_3_infantry_weapons) {
    chapter += `## Infantry Weapons\n\n`;
    chapter += `### Top 3 Weapons by Count\n\n`;
    chapter += `| Rank | Weapon | Count | Type |\n`;
    chapter += `|------|--------|-------|------|\n`;

    for (let i = 1; i <= 3; i++) {
      if (data.top_3_infantry_weapons[i.toString()]) {
        const weapon = data.top_3_infantry_weapons[i.toString()];
        chapter += `| #${i} | ${weapon.weapon} | ${formatNumber(weapon.count)} | ${weapon.type} |\n`;
      }
    }

    chapter += `\n`;
  }

  // Section 9: Transport & Vehicles
  if (data.ground_vehicles_total > 0) {
    chapter += `## Transport & Vehicles\n\n`;
    chapter += `**Total Ground Vehicles:** ${formatNumber(data.ground_vehicles_total)}\n\n`;
    chapter += `| Category | Quantity |\n`;
    chapter += `|----------|----------|\n`;

    if (data.trucks && data.trucks.total > 0) {
      chapter += `| **Trucks** | ${data.trucks.total} |\n`;
      if (data.trucks.variants) {
        Object.entries(data.trucks.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} (${variant.capacity}) | ${variant.count} |\n`;
        });
      }
    }

    if (data.motorcycles && data.motorcycles.total > 0) {
      chapter += `| **Motorcycles** | ${data.motorcycles.total} |\n`;
      if (data.motorcycles.variants) {
        Object.entries(data.motorcycles.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} | ${variant.count} |\n`;
        });
      }
    }

    if (data.halftracks && data.halftracks.total > 0) {
      chapter += `| **Half-tracks** | ${data.halftracks.total} |\n`;
      if (data.halftracks.variants) {
        Object.entries(data.halftracks.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} | ${variant.count} |\n`;
        });
      }
    }

    if (data.support_vehicles && data.support_vehicles.total > 0) {
      chapter += `| **Support Vehicles** | ${data.support_vehicles.total} |\n`;
      if (data.support_vehicles.variants) {
        Object.entries(data.support_vehicles.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} | ${variant.count} |\n`;
        });
      }
    }

    chapter += `\n`;
  }

  // Section 10: Organizational Structure
  chapter += `## Organizational Structure\n\n`;
  if (data.subordinate_units && data.subordinate_units.length > 0) {
    chapter += `### Subordinate Units\n\n`;
    data.subordinate_units.forEach((unit, idx) => {
      chapter += `${idx + 1}. **${unit.unit_designation}**\n`;
      chapter += `   - Type: ${unit.unit_type}\n`;
      chapter += `   - Commander: ${unit.commander}\n`;
      chapter += `   - Strength: ${formatNumber(unit.strength)} personnel\n`;
      chapter += `   - Status: ${unit.status}\n`;
      if (unit.note) {
        chapter += `   - Notes: ${unit.note}\n`;
      }
      chapter += `\n`;
    });
  }

  // Section 11: Supply Status
  chapter += `## Supply Status\n\n`;
  if (data.supply_status) {
    const supply = data.supply_status;
    chapter += `| Resource | Days on Hand |\n`;
    chapter += `|----------|---------------|\n`;
    chapter += `| **Fuel** | ${supply.fuel_days || '-'} |\n`;
    chapter += `| **Ammunition** | ${supply.ammunition_days || '-'} |\n`;
    chapter += `| **Food** | ${supply.food_days || '-'} |\n`;
    chapter += `| **Water** | ${supply.water_liters_per_day || '-'} L/day |\n`;
    chapter += `\n`;

    if (supply.note) {
      chapter += `**Notes:** ${supply.note}\n\n`;
    }
  }

  // Section 12: Tactical Doctrine
  chapter += `## Tactical Doctrine & Capabilities\n\n`;
  if (data.tactical_doctrine) {
    if (data.tactical_doctrine.role) {
      chapter += `**Primary Role:** ${data.tactical_doctrine.role}\n\n`;
    }

    if (data.tactical_doctrine.special_capabilities && data.tactical_doctrine.special_capabilities.length > 0) {
      chapter += `### Special Capabilities\n\n`;
      data.tactical_doctrine.special_capabilities.forEach(cap => {
        chapter += `- ${cap}\n`;
      });
      chapter += `\n`;
    }

    if (data.tactical_doctrine.tactical_innovations && data.tactical_doctrine.tactical_innovations.length > 0) {
      chapter += `### Tactical Innovations\n\n`;
      data.tactical_doctrine.tactical_innovations.forEach(innov => {
        chapter += `- ${innov}\n`;
      });
      chapter += `\n`;
    }

    if (data.tactical_doctrine.known_issues && data.tactical_doctrine.known_issues.length > 0) {
      chapter += `### Known Issues\n\n`;
      data.tactical_doctrine.known_issues.forEach(issue => {
        chapter += `- ${issue}\n`;
      });
      chapter += `\n`;
    }

    if (data.tactical_doctrine.desert_adaptations) {
      chapter += `**Desert Adaptations:** ${data.tactical_doctrine.desert_adaptations}\n\n`;
    }
  }

  // Section 13: Historical Context
  chapter += `## Historical Context\n\n`;
  if (data.historical_context) {
    if (data.historical_context.period) {
      chapter += `**Period:** ${data.historical_context.period}\n\n`;
    }

    if (data.historical_context.theater) {
      chapter += `**Theater:** ${data.historical_context.theater}\n\n`;
    }

    if (data.historical_context.key_events && data.historical_context.key_events.length > 0) {
      chapter += `### Key Events\n\n`;
      data.historical_context.key_events.forEach(event => {
        chapter += `- ${event}\n`;
      });
      chapter += `\n`;
    }

    if (data.historical_context.formation_history) {
      chapter += `### Formation History\n\n`;
      const fh = data.historical_context.formation_history;
      if (fh.informal_period) chapter += `**Informal Period:** ${fh.informal_period}\n\n`;
      if (fh.formal_establishment) chapter += `**Formal Establishment:** ${fh.formal_establishment}\n\n`;
      if (fh.name_evolution) chapter += `**Name Evolution:** ${fh.name_evolution}\n\n`;
      if (fh.final_designation) chapter += `**Final Designation:** ${fh.final_designation}\n\n`;
    }

    if (data.historical_context.combat_effectiveness) {
      chapter += `### Combat Effectiveness\n\n`;
      const ce = data.historical_context.combat_effectiveness;
      if (ce.early_q2) chapter += `**Early Q2:** ${ce.early_q2}\n\n`;
      if (ce.mid_q2) chapter += `**Mid Q2:** ${ce.mid_q2}\n\n`;
      if (ce.end_q2) chapter += `**End Q2:** ${ce.end_q2}\n\n`;
    }
  }

  // Section 14: Wargaming Data
  chapter += `## Wargaming Data\n\n`;
  if (data.wargaming_data) {
    chapter += `| Attribute | Value |\n`;
    chapter += `|-----------|-------|\n`;
    chapter += `| **Morale** | ${data.wargaming_data.morale_rating || 'Unknown'}/10 |\n`;
    chapter += `| **Experience** | ${data.wargaming_data.experience_level || 'Unknown'} |\n`;
    chapter += `\n`;

    if (data.wargaming_data.special_rules && data.wargaming_data.special_rules.length > 0) {
      chapter += `### Special Rules\n\n`;
      data.wargaming_data.special_rules.forEach(rule => {
        chapter += `- ${rule}\n`;
      });
      chapter += `\n`;
    }

    if (data.wargaming_data.scenario_suitability && data.wargaming_data.scenario_suitability.length > 0) {
      chapter += `### Scenario Suitability\n\n`;
      data.wargaming_data.scenario_suitability.forEach(scenario => {
        chapter += `- ${scenario}\n`;
      });
      chapter += `\n`;
    }

    if (data.wargaming_data.historical_engagements && data.wargaming_data.historical_engagements.length > 0) {
      chapter += `### Historical Engagements\n\n`;
      data.wargaming_data.historical_engagements.forEach(eng => {
        chapter += `- ${eng}\n`;
      });
      chapter += `\n`;
    }
  }

  // Section 15: Data Quality
  chapter += `## Data Quality & Known Gaps\n\n`;
  if (data.validation) {
    chapter += `**Overall Confidence:** ${data.validation.confidence}%\n\n`;

    if (data.validation.source && data.validation.source.length > 0) {
      chapter += `### Primary Sources\n\n`;
      data.validation.source.forEach(src => {
        chapter += `- ${src}\n`;
      });
      chapter += `\n`;
    }

    if (data.validation.known_gaps && data.validation.known_gaps.length > 0) {
      chapter += `### Known Data Gaps\n\n`;
      data.validation.known_gaps.forEach(gap => {
        chapter += `- ${gap}\n`;
      });
      chapter += `\n`;
    }

    if (data.validation.notes && data.validation.notes.length > 0) {
      chapter += `### Additional Notes\n\n`;
      data.validation.notes.forEach(note => {
        chapter += `${note}\n\n`;
      });
    }
  }

  // Section 16: Conclusion
  chapter += `## Conclusion\n\n`;

  // Generate dynamic conclusion based on unit data
  if (data.conclusion) {
    chapter += `${data.conclusion}\n\n`;
  } else {
    // Generate generic conclusion from unit data
    const nationName = nation.charAt(0).toUpperCase() + nation.slice(1);
    const yearQuarter = quarter.replace('q', ' Q');
    chapter += `${unitDesignation} in ${yearQuarter} represents `;

    if (data.organization_level === 'division') {
      chapter += `a significant formation in the ${nationName} order of battle during the North Africa Campaign. `;
      if (data.total_personnel) {
        chapter += `With ${formatNumber(data.total_personnel)} personnel `;
        if (data.tanks && data.tanks.total > 0) {
          chapter += `and ${data.tanks.total} tanks, `;
        }
        chapter += `this division played an important role in the theater. `;
      }
    } else if (data.organization_level === 'corps') {
      chapter += `a critical corps-level formation coordinating multiple divisions. `;
      if (data.subordinate_units && data.subordinate_units.length > 0) {
        chapter += `Commanding ${data.subordinate_units.length} subordinate units `;
        if (data.total_personnel) {
          chapter += `totaling ${formatNumber(data.total_personnel)} personnel, `;
        }
        chapter += `this corps formed a major component of ${nationName} operations. `;
      }
    } else if (data.organization_level === 'army' || data.organization_level === 'theater') {
      chapter += `the highest operational formation in this sector. `;
      if (data.subordinate_units && data.subordinate_units.length > 0) {
        chapter += `Controlling ${data.subordinate_units.length} subordinate formations `;
        if (data.total_personnel) {
          chapter += `with combined strength of ${formatNumber(data.total_personnel)} personnel, `;
        }
        chapter += `this army directed major operations in the North Africa theater. `;
      }
    } else {
      chapter += `an important formation in ${nationName} North African operations. `;
    }

    if (data.validation && data.validation.overall_confidence) {
      chapter += `Data confidence: ${data.validation.overall_confidence}%.`;
    }
    chapter += `\n\n`;
  }

  // Footer
  chapter += `---\n\n`;
  const yearOnly = quarter.substring(0, 4);
  chapter += `*Data compiled from historical records for ${yearOnly} North Africa Campaign*\n\n`;

  return chapter;
}
