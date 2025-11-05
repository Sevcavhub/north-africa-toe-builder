const fs = require('fs');
const path = require('path');

// Read the list of missing chapters
const missingList = JSON.parse(fs.readFileSync('temp_missing_chapters.json', 'utf8'));

console.log(`\nGenerating ${missingList.length} missing MDBook chapters...`);

let generated = 0;
let errors = 0;

missingList.forEach((entry, index) => {
  try {
    // Read the JSON TOE file
    const jsonPath = entry.path.replace(/\\/g, '/');
    if (!fs.existsSync(jsonPath)) {
      console.log(`❌ [${index+1}/${missingList.length}] JSON not found: ${jsonPath}`);
      errors++;
      return;
    }

    const toeData = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

    // Generate chapter content
    const chapter = generateChapter(toeData);

    // Determine output path (same session folder)
    const sessionFolder = path.dirname(path.dirname(jsonPath));
    const chaptersFolder = path.join(sessionFolder, 'chapters');

    // Create chapters folder if it doesn't exist
    if (!fs.existsSync(chaptersFolder)) {
      fs.mkdirSync(chaptersFolder, { recursive: true });
    }

    // Generate chapter filename
    const chapterFilename = `chapter_${entry.unit}.md`;
    const chapterPath = path.join(chaptersFolder, chapterFilename);

    // Write chapter file
    fs.writeFileSync(chapterPath, chapter, 'utf8');

    console.log(`✅ [${index+1}/${missingList.length}] Generated: ${chapterFilename}`);
    generated++;

  } catch (error) {
    console.log(`❌ [${index+1}/${missingList.length}] Error: ${entry.unit} - ${error.message}`);
    errors++;
  }
});

console.log(`\n📊 Summary:`);
console.log(`   Generated: ${generated}`);
console.log(`   Errors: ${errors}`);
console.log(`   Total: ${missingList.length}\n`);

// Chapter generation function
function generateChapter(toe) {
  const nation = capitalize(toe.nation);
  const quarter = toe.quarter;
  const unitName = toe.unit_designation;
  const unitType = toe.unit_type || 'Division';
  const orgLevel = capitalize(toe.organization_level || 'division');

  let chapter = '';

  // Section 1: Header
  chapter += `# ${unitName}\n\n`;
  chapter += `**${nation} Forces • ${quarter} • North Africa**\n\n`;
  chapter += `---\n\n`;

  // Section 2: Unit Overview
  chapter += `## Unit Overview\n\n`;
  chapter += `The ${unitName} was a ${nation} ${unitType} deployed in North Africa during ${quarter}. `;

  if (toe.historical_context) {
    if (toe.historical_context.purpose) {
      chapter += `${toe.historical_context.purpose} `;
    }
    if (toe.historical_context.formation_date) {
      chapter += `Formed on ${toe.historical_context.formation_date}. `;
    }
  }

  chapter += `\n\n`;

  // Section 3: Command
  chapter += `## Command\n\n`;
  if (toe.command && toe.command.commander) {
    const cmd = toe.command.commander;
    chapter += `**${orgLevel} Commander**: ${cmd.name || 'Unknown'}\n`;
    chapter += `**Rank**: ${cmd.rank || 'Unknown'}\n`;
    if (cmd.appointment_date) {
      chapter += `**Appointed**: ${cmd.appointment_date}\n`;
    }
    if (cmd.previous_service) {
      chapter += `**Previous Service**: ${cmd.previous_service}\n`;
    }
    chapter += `\n`;
  }

  if (toe.command) {
    if (toe.command.headquarters_location) {
      chapter += `**Headquarters**: ${toe.command.headquarters_location}\n`;
    }
    if (toe.parent_formation) {
      chapter += `**Parent Formation**: ${toe.parent_formation}\n`;
    }
    chapter += `\n`;

    if (toe.command.staff_strength) {
      const staff = toe.command.staff_strength;
      const total = (staff.officers || 0) + (staff.ncos || 0) + (staff.enlisted || 0);
      chapter += `**${orgLevel} Staff**: ${total} personnel\n`;
      chapter += `- Officers: ${staff.officers || 0}\n`;
      chapter += `- NCOs: ${staff.ncos || 0}\n`;
      chapter += `- Enlisted: ${staff.enlisted || 0}\n\n`;
    }
  }

  // Section 4: Personnel Strength
  chapter += `## Personnel Strength\n\n`;
  chapter += `| Category | Count | Percentage |\n`;
  chapter += `|----------|-------|------------|\n`;

  const total = toe.total_personnel || 0;
  const officers = toe.officers || 0;
  const ncos = toe.ncos || 0;
  const enlisted = toe.enlisted || 0;

  chapter += `| **Total Personnel** | **${total}** | 100% |\n`;
  if (total > 0) {
    chapter += `| Officers | ${officers} | ${((officers/total)*100).toFixed(1)}% |\n`;
    chapter += `| NCOs | ${ncos} | ${((ncos/total)*100).toFixed(1)}% |\n`;
    chapter += `| Other Ranks | ${enlisted} | ${((enlisted/total)*100).toFixed(1)}% |\n`;
  }
  chapter += `\n`;

  // Section 5: Top 3 Infantry Weapons
  chapter += `## Top 3 Infantry Weapons\n\n`;
  if (toe.top_3_infantry_weapons) {
    const weapons = toe.top_3_infantry_weapons;
    chapter += `| Rank | Weapon | Count | Type |\n`;
    chapter += `|------|--------|-------|------|\n`;
    ['1', '2', '3'].forEach(rank => {
      if (weapons[rank]) {
        chapter += `| ${rank} | ${weapons[rank].weapon} | ${weapons[rank].count} | ${capitalize(weapons[rank].type || 'unknown')} |\n`;
      }
    });
  }
  chapter += `\n`;

  // Section 6: Armoured Strength (Tanks)
  chapter += `## Armoured Strength\n\n`;
  if (toe.tanks && toe.tanks.total > 0) {
    chapter += `### Tank Summary\n\n`;
    chapter += `| Category | Total | Operational | Readiness |\n`;
    chapter += `|----------|-------|-------------|--------|\n`;

    const tanks = toe.tanks;
    const readiness = tanks.total > 0 ? ((tanks.operational / tanks.total) * 100).toFixed(1) : '0.0';
    chapter += `| **All Tanks** | **${tanks.total}** | **${tanks.operational}** | **${readiness}%** |\n`;

    // Heavy tanks
    if (tanks.heavy_tanks && tanks.heavy_tanks.total > 0) {
      const htReadiness = ((tanks.heavy_tanks.operational || tanks.heavy_tanks.total) / tanks.heavy_tanks.total * 100).toFixed(1);
      chapter += `| **Heavy Tanks** | **${tanks.heavy_tanks.total}** | **${tanks.heavy_tanks.operational || tanks.heavy_tanks.total}** | **${htReadiness}%** |\n`;
      if (tanks.heavy_tanks.variants) {
        Object.entries(tanks.heavy_tanks.variants).forEach(([name, data]) => {
          const vOp = data.operational || data.count;
          const vReadiness = ((vOp / data.count) * 100).toFixed(1);
          chapter += `| ↳ ${name} | ${data.count} | ${vOp} | ${vReadiness}% |\n`;
        });
      }
    }

    // Medium tanks
    if (tanks.medium_tanks && tanks.medium_tanks.total > 0) {
      const mtReadiness = ((tanks.medium_tanks.operational || tanks.medium_tanks.total) / tanks.medium_tanks.total * 100).toFixed(1);
      chapter += `| **Medium Tanks** | **${tanks.medium_tanks.total}** | **${tanks.medium_tanks.operational || tanks.medium_tanks.total}** | **${mtReadiness}%** |\n`;
      if (tanks.medium_tanks.variants) {
        Object.entries(tanks.medium_tanks.variants).forEach(([name, data]) => {
          const vOp = data.operational || data.count;
          const vReadiness = ((vOp / data.count) * 100).toFixed(1);
          chapter += `| ↳ ${name} | ${data.count} | ${vOp} | ${vReadiness}% |\n`;
        });
      }
    }

    // Light tanks
    if (tanks.light_tanks && tanks.light_tanks.total > 0) {
      const ltReadiness = ((tanks.light_tanks.operational || tanks.light_tanks.total) / tanks.light_tanks.total * 100).toFixed(1);
      chapter += `| **Light Tanks** | **${tanks.light_tanks.total}** | **${tanks.light_tanks.operational || tanks.light_tanks.total}** | **${ltReadiness}%** |\n`;
      if (tanks.light_tanks.variants) {
        Object.entries(tanks.light_tanks.variants).forEach(([name, data]) => {
          const vOp = data.operational || data.count;
          const vReadiness = ((vOp / data.count) * 100).toFixed(1);
          chapter += `| ↳ ${name} | ${data.count} | ${vOp} | ${vReadiness}% |\n`;
        });
      }
    }
  } else {
    chapter += `No organic tank units.\n`;
  }
  chapter += `\n`;

  // Section 7: Artillery
  chapter += `## Artillery Strength\n\n`;
  const artTotal = toe.artillery_total || 0;
  if (artTotal > 0) {
    chapter += `| Type | Total | Caliber |\n`;
    chapter += `|------|-------|----------|\n`;

    // Field artillery
    if (toe.field_artillery && toe.field_artillery.total > 0) {
      chapter += `| **Field Artillery** | **${toe.field_artillery.total}** | - |\n`;
      if (toe.field_artillery.variants) {
        Object.entries(toe.field_artillery.variants).forEach(([name, data]) => {
          chapter += `| ↳ ${name} | ${data.count} | ${data.caliber || 'N/A'} |\n`;
        });
      }
    }

    // Anti-tank
    if (toe.anti_tank && toe.anti_tank.total > 0) {
      chapter += `| **Anti-Tank** | **${toe.anti_tank.total}** | - |\n`;
      if (toe.anti_tank.variants) {
        Object.entries(toe.anti_tank.variants).forEach(([name, data]) => {
          chapter += `| ↳ ${name} | ${data.count} | ${data.caliber || 'N/A'} |\n`;
        });
      }
    }

    // Anti-aircraft
    if (toe.anti_aircraft && toe.anti_aircraft.total > 0) {
      chapter += `| **Anti-Aircraft** | **${toe.anti_aircraft.total}** | - |\n`;
      if (toe.anti_aircraft.variants) {
        Object.entries(toe.anti_aircraft.variants).forEach(([name, data]) => {
          chapter += `| ↳ ${name} | ${data.count} | ${data.caliber || 'N/A'} |\n`;
        });
      }
    }

    chapter += `| **Total Artillery** | **${artTotal}** | - |\n`;
  } else {
    chapter += `No organic artillery units.\n`;
  }
  chapter += `\n`;

  // Section 8: Armored Cars
  chapter += `## Armoured Cars\n\n`;
  if (toe.armored_cars && toe.armored_cars.total > 0) {
    chapter += `| Type | Count | Armament |\n`;
    chapter += `|------|-------|----------|\n`;
    chapter += `| **Total Armoured Cars** | **${toe.armored_cars.total}** | - |\n`;
    if (toe.armored_cars.variants) {
      Object.entries(toe.armored_cars.variants).forEach(([name, data]) => {
        chapter += `| ↳ ${name} | ${data.count} | ${data.armament || 'N/A'} |\n`;
      });
    }
  } else {
    chapter += `No organic armoured car units.\n`;
  }
  chapter += `\n`;

  // Section 9: Transport & Vehicles
  chapter += `## Transport & Vehicles\n\n`;
  const vehicleTotal = toe.ground_vehicles_total || 0;
  if (vehicleTotal > 0) {
    chapter += `**Total Ground Vehicles**: ${vehicleTotal}\n\n`;

    // Trucks
    if (toe.trucks && toe.trucks.total > 0) {
      chapter += `### Trucks (${toe.trucks.total})\n\n`;
      if (toe.trucks.variants) {
        Object.entries(toe.trucks.variants).forEach(([name, data]) => {
          chapter += `- **${name}**: ${data.count} (${data.capacity || 'N/A'})\n`;
        });
      }
      chapter += `\n`;
    }

    // Motorcycles
    if (toe.motorcycles && toe.motorcycles.total > 0) {
      chapter += `### Motorcycles (${toe.motorcycles.total})\n\n`;
      if (toe.motorcycles.variants) {
        Object.entries(toe.motorcycles.variants).forEach(([name, data]) => {
          chapter += `- **${name}**: ${data.count}\n`;
        });
      }
      chapter += `\n`;
    }

    // Halftracks
    if (toe.halftracks && toe.halftracks.total > 0) {
      chapter += `### Halftracks (${toe.halftracks.total})\n\n`;
      if (toe.halftracks.variants) {
        Object.entries(toe.halftracks.variants).forEach(([name, data]) => {
          chapter += `- **${name}**: ${data.count} - ${data.role || 'N/A'}\n`;
        });
      }
      chapter += `\n`;
    }
  } else {
    chapter += `Vehicle data not available.\n\n`;
  }

  // Section 10: Organizational Structure
  chapter += `## Organizational Structure\n\n`;
  if (toe.subordinate_units && toe.subordinate_units.length > 0) {
    toe.subordinate_units.forEach((sub, idx) => {
      chapter += `### ${idx + 1}. ${sub.unit_designation}\n\n`;
      if (sub.commander) {
        chapter += `- **Commander**: ${sub.commander_rank || ''} ${sub.commander}\n`;
      }
      if (sub.strength) {
        chapter += `- **Strength**: ${sub.strength} personnel\n`;
      }
      if (sub.notes) {
        chapter += `- **Notes**: ${sub.notes}\n`;
      }
      chapter += `\n`;
    });
  } else {
    chapter += `Subordinate unit details not available.\n\n`;
  }

  // Section 11: Supply Status
  chapter += `## Supply Status\n\n`;
  if (toe.supply_status) {
    chapter += `| Resource | Days of Supply | Status |\n`;
    chapter += `|----------|----------------|--------|\n`;
    chapter += `| Fuel | ${toe.supply_status.fuel_days || 'N/A'} | ${assessSupply(toe.supply_status.fuel_days)} |\n`;
    chapter += `| Ammunition | ${toe.supply_status.ammunition_days || 'N/A'} | ${assessSupply(toe.supply_status.ammunition_days)} |\n`;
    chapter += `| Food | ${toe.supply_status.food_days || 'N/A'} | ${assessSupply(toe.supply_status.food_days)} |\n`;

    if (toe.supply_status.water_liters_per_day) {
      chapter += `| Water | ${toe.supply_status.water_liters_per_day} L/day | ${assessWater(toe.supply_status.water_liters_per_day, total)} |\n`;
    }

    if (toe.supply_status.notes) {
      chapter += `\n**Assessment**: ${toe.supply_status.notes}\n`;
    }
  } else {
    chapter += `Supply status data not available.\n`;
  }
  chapter += `\n`;

  // Section 12: Tactical Doctrine
  chapter += `## Tactical Doctrine & Capabilities\n\n`;
  if (toe.tactical_doctrine) {
    if (toe.tactical_doctrine.role) {
      chapter += `**Role**: ${toe.tactical_doctrine.role}\n\n`;
    }

    if (toe.tactical_doctrine.special_capabilities && toe.tactical_doctrine.special_capabilities.length > 0) {
      chapter += `**Special Capabilities**:\n`;
      toe.tactical_doctrine.special_capabilities.forEach(cap => {
        chapter += `- ${cap}\n`;
      });
      chapter += `\n`;
    }

    if (toe.tactical_doctrine.tactical_innovations && toe.tactical_doctrine.tactical_innovations.length > 0) {
      chapter += `**Tactical Innovations**:\n`;
      toe.tactical_doctrine.tactical_innovations.forEach(inn => {
        chapter += `- ${inn}\n`;
      });
      chapter += `\n`;
    }

    if (toe.tactical_doctrine.known_issues && toe.tactical_doctrine.known_issues.length > 0) {
      chapter += `**Known Issues**:\n`;
      toe.tactical_doctrine.known_issues.forEach(issue => {
        chapter += `- ${issue}\n`;
      });
      chapter += `\n`;
    }

    if (toe.tactical_doctrine.desert_adaptations) {
      chapter += `**Desert Adaptations**: ${toe.tactical_doctrine.desert_adaptations}\n\n`;
    }
  } else {
    chapter += `Tactical doctrine data not available.\n\n`;
  }

  // Section 13: Critical Equipment Shortages
  chapter += `## Critical Equipment Shortages\n\n`;
  chapter += `*Data to be updated from detailed operational reports.*\n\n`;

  // Section 14: Historical Context
  chapter += `## Historical Context\n\n`;
  if (toe.historical_context) {
    if (toe.historical_context.theater) {
      chapter += `**Theater**: ${toe.historical_context.theater}\n\n`;
    }
    if (toe.historical_context.evolution) {
      chapter += `**Evolution**: ${toe.historical_context.evolution}\n\n`;
    }
    if (toe.historical_context.purpose) {
      chapter += `**Purpose**: ${toe.historical_context.purpose}\n\n`;
    }
  } else {
    chapter += `Historical context data not available.\n\n`;
  }

  // Section 15: Wargaming Data
  chapter += `## Wargaming Data\n\n`;
  if (toe.wargaming_data) {
    if (toe.wargaming_data.morale_rating) {
      chapter += `**Morale Rating**: ${toe.wargaming_data.morale_rating}/10\n`;
    }
    if (toe.wargaming_data.experience_level) {
      chapter += `**Experience Level**: ${toe.wargaming_data.experience_level}\n\n`;
    }

    if (toe.wargaming_data.special_rules && toe.wargaming_data.special_rules.length > 0) {
      chapter += `**Special Rules**:\n`;
      toe.wargaming_data.special_rules.forEach(rule => {
        chapter += `- ${rule}\n`;
      });
      chapter += `\n`;
    }

    if (toe.wargaming_data.scenario_suitability && toe.wargaming_data.scenario_suitability.length > 0) {
      chapter += `**Suitable Scenarios**:\n`;
      toe.wargaming_data.scenario_suitability.forEach(scenario => {
        chapter += `- ${scenario}\n`;
      });
      chapter += `\n`;
    }
  } else {
    chapter += `Wargaming data not available.\n\n`;
  }

  // Section 16: Data Quality & Known Gaps
  chapter += `## Data Quality & Known Gaps\n\n`;
  if (toe.validation) {
    const confidence = toe.validation.confidence || 0;
    chapter += `**Confidence Score**: ${confidence}% (${assessConfidence(confidence)})\n\n`;

    if (toe.validation.source && toe.validation.source.length > 0) {
      chapter += `**Data Sources**:\n`;
      toe.validation.source.forEach(src => {
        chapter += `- ${src}\n`;
      });
      chapter += `\n`;
    }

    if (toe.validation.known_gaps && toe.validation.known_gaps.length > 0) {
      chapter += `**Known Gaps**:\n`;
      toe.validation.known_gaps.forEach(gap => {
        chapter += `- ${gap}\n`;
      });
      chapter += `\n`;
    }

    if (toe.validation.confidence_notes) {
      chapter += `**Research Notes**: ${toe.validation.confidence_notes}\n\n`;
    }
  } else {
    chapter += `Data quality assessment not available.\n\n`;
  }

  // Section 17: Conclusion
  chapter += `## Conclusion\n\n`;
  chapter += `The ${unitName} represents a significant ${nation} formation in North Africa during ${quarter}. `;
  chapter += `This TO&E provides a comprehensive snapshot of the unit's organization, equipment, and capabilities during this period.\n\n`;

  // Data Source Footer
  chapter += `---\n\n`;
  chapter += `**Data Source**: Autonomous TO&E Extraction System\n`;
  chapter += `**Confidence**: ${toe.validation?.confidence || 0}%\n`;
  chapter += `**Schema**: ${toe.schema_type} v${toe.schema_version}\n`;
  chapter += `**Extraction Date**: ${toe.validation?.last_updated || new Date().toISOString().split('T')[0]}\n\n`;
  chapter += `---\n`;

  return chapter;
}

// Helper functions
function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function assessSupply(days) {
  if (!days || days === 'N/A') return 'Unknown';
  if (days >= 30) return 'Good';
  if (days >= 15) return 'Adequate';
  if (days >= 7) return 'Low';
  return 'Critical';
}

function assessWater(litersPerDay, personnel) {
  if (!litersPerDay || !personnel || personnel === 0) return 'Unknown';
  const litersPerPerson = litersPerDay / personnel;
  if (litersPerPerson >= 5) return 'Adequate';
  if (litersPerPerson >= 3) return 'Minimal';
  return 'Critical';
}

function assessConfidence(confidence) {
  if (confidence >= 90) return 'Very High';
  if (confidence >= 80) return 'High';
  if (confidence >= 75) return 'Acceptable';
  if (confidence >= 60) return 'Moderate';
  return 'Low';
}
