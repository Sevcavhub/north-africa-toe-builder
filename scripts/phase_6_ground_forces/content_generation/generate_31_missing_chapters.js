#!/usr/bin/env node

/**
 * Generate MDBook chapters for 31 missing units
 * Batch chapter generation following template v3.1
 */

const fs = require('fs');
const path = require('path');

const UNITS_DIR = path.join(__dirname, '..', 'data', 'output', 'units');
const CHAPTERS_DIR = path.join(__dirname, '..', 'data', 'output', 'chapters');

// List of 31 units missing chapters
const MISSING_UNITS = [
  'british_1941q1_6th_australian_division',
  'british_1941q2_1st_south_african_division',
  'british_1941q2_5th_indian_division',
  'british_1941q4_70th_infantry_division',
  'german_1941q1_21_panzer_division',
  'german_1941q1_90_light_division',
  'german_1941q4_panzergruppe_afrika',
  'german_1942q2_deutsches_afrikakorps',
  'italian_1941q1_catanzaro_division',
  'italian_1941q1_cirene_division',
  'italian_1941q1_marmarica_division',
  'italian_1941q1_savona_division',
  'italian_1941q3_101_trieste_division',
  'italian_1941q3_102_trento_division',
  'italian_1941q3_132_ariete_division',
  'italian_1941q3_25_divisione_di_fanteria_bologna',
  'italian_1941q3_brescia_division',
  'italian_1941q3_pavia_division',
  'italian_1941q3_savona_division',
  'italian_1941q4_101_trieste_division',
  'italian_1941q4_102_trento_division',
  'italian_1941q4_132_ariete_division',
  'italian_1941q4_bologna_division',
  'italian_1941q4_brescia_division',
  'italian_1941q4_pavia_division',
  'italian_1941q4_xx_corps',
  'italian_1942q1_bologna_division',
  'italian_1942q1_pavia_division',
  'italian_1942q1_trieste_division',
  'italian_1942q2_xx_mobile_corps',
  'italian_1942q2_xxi_corps'
];

/**
 * Generate chapter content from unit JSON
 */
function generateChapter(unitData, unitName) {
  const nation = unitData.nation || 'unknown';
  const quarter = unitData.quarter || 'unknown';
  const unitDesignation = unitData.unit_designation || 'Unknown Unit';
  const orgLevel = unitData.organization_level || 'division';

  // Parse quarter for display
  let quarterDisplay = quarter;
  if (quarter.match(/^\d{4}[qQ]\d$/)) {
    const year = quarter.substring(0, 4);
    const q = quarter.substring(5);
    const months = {
      '1': 'January-March',
      '2': 'April-June',
      '3': 'July-September',
      '4': 'October-December'
    };
    quarterDisplay = `${year} Q${q} (${months[q]})`;
  } else if (quarter.match(/^\d{4}-[qQ]\d$/)) {
    const year = quarter.substring(0, 4);
    const q = quarter.substring(6);
    const months = {
      '1': 'January-March',
      '2': 'April-June',
      '3': 'July-September',
      '4': 'October-December'
    };
    quarterDisplay = `${year} Q${q} (${months[q]})`;
  }

  // Nation display
  const nationDisplay = nation.charAt(0).toUpperCase() + nation.slice(1);

  let chapter = `# ${unitDesignation}\n\n`;
  chapter += `**${nationDisplay} Forces • ${quarterDisplay} • North Africa**\n\n`;
  chapter += `---\n\n`;

  // Section 2: Overview
  chapter += `## Division/Unit Overview\n\n`;

  // Check if unit was not operational
  const isNotOperational = unitData.total_personnel === 0 ||
    (unitData.combat_status && unitData.combat_status.status &&
     (unitData.combat_status.status.includes('not yet formed') ||
      unitData.combat_status.status.includes('not yet deployed')));

  if (isNotOperational) {
    chapter += `**${unitDesignation}** was designated in ${quarterDisplay} but not yet operationally deployed to North Africa during this quarter. `;
    chapter += `The unit was either forming in its home country or reorganizing from a predecessor unit.\n\n`;
    if (unitData.historical_notes && unitData.historical_notes.formation) {
      chapter += `**Formation**: ${unitData.historical_notes.formation}\n\n`;
    }
  } else if (unitData.combat_status && unitData.combat_status.status && unitData.combat_status.status.includes('Destroyed')) {
    chapter += `**${unitDesignation}** was a ${unitData.historical_notes?.classification || orgLevel} that fought in North Africa during ${quarterDisplay}. `;
    chapter += `The division was destroyed during this quarter and never reconstituted.\n\n`;
  } else {
    const classif = unitData.historical_notes?.classification || `${orgLevel}`;
    chapter += `**${unitDesignation}** was a ${classif} that operated in North Africa during ${quarterDisplay}. `;
    if (unitData.unit_type) {
      chapter += `Classified as a **${unitData.unit_type}**.\n\n`;
    } else {
      chapter += `\n\n`;
    }
  }

  // Section 3: Command
  chapter += `## Command\n\n`;

  if (unitData.command && unitData.command.commander) {
    const cmd = unitData.command.commander;
    chapter += `**Commander**: ${cmd.name || 'Unknown'}\n`;
    chapter += `**Rank**: ${cmd.rank || 'Unknown'}\n`;
    if (cmd.appointment_date) {
      chapter += `**Appointed**: ${cmd.appointment_date}\n`;
    }
    if (cmd.service_notes) {
      chapter += `**Service**: ${cmd.service_notes}\n`;
    }
    if (cmd.decorations) {
      chapter += `**Decorations**: ${cmd.decorations}\n`;
    }
    chapter += `\n`;
  } else {
    chapter += `**Commander**: Unknown\n**Rank**: Unknown\n\n`;
  }

  if (unitData.command && unitData.command.headquarters_location) {
    chapter += `**Headquarters**: ${unitData.command.headquarters_location}\n`;
  }
  if (unitData.parent_unit) {
    chapter += `**Parent Formation**: ${unitData.parent_unit}\n`;
  }
  chapter += `\n`;

  if (unitData.command && unitData.command.staff_strength) {
    const staff = unitData.command.staff_strength;
    const totalStaff = (staff.officers || 0) + (staff.ncos || 0) + (staff.enlisted || 0);
    chapter += `**Staff Strength**: ${totalStaff} personnel\n`;
    chapter += `- Officers: ${staff.officers || 0}\n`;
    chapter += `- NCOs: ${staff.ncos || 0}\n`;
    chapter += `- Enlisted: ${staff.enlisted || 0}\n\n`;
  }

  // Section 4: Personnel Strength
  chapter += `## Personnel Strength\n\n`;

  const totalPersonnel = unitData.total_personnel || 0;
  const officers = unitData.officers || 0;
  const ncos = unitData.ncos || 0;
  const enlisted = unitData.enlisted || 0;

  chapter += `| Category | Count | Percentage |\n`;
  chapter += `|----------|-------|------------|\n`;
  chapter += `| **Total Personnel** | **${totalPersonnel}** | 100% |\n`;
  if (totalPersonnel > 0) {
    const offPct = ((officers / totalPersonnel) * 100).toFixed(1);
    const ncoPct = ((ncos / totalPersonnel) * 100).toFixed(1);
    const enlPct = ((enlisted / totalPersonnel) * 100).toFixed(1);
    chapter += `| Officers | ${officers} | ${offPct}% |\n`;
    chapter += `| NCOs | ${ncos} | ${ncoPct}% |\n`;
    chapter += `| Other Ranks | ${enlisted} | ${enlPct}% |\n`;
  }
  chapter += `\n`;

  if (unitData.personnel_notes) {
    chapter += `**Notes**: ${unitData.personnel_notes}\n\n`;
  }

  // Section 5: Armoured Strength (Tanks)
  chapter += `## Armoured Strength\n\n`;

  if (unitData.tanks && unitData.tanks.total > 0) {
    const tanks = unitData.tanks;
    const total = tanks.total || 0;
    const operational = tanks.operational || total;
    const readiness = total > 0 ? ((operational / total) * 100).toFixed(1) : '0.0';

    chapter += `### Summary\n\n`;
    chapter += `The division fielded **${total} tanks** with **${operational} operational** (${readiness}% readiness).\n\n`;

    chapter += `| Category | Total | Operational | Readiness |\n`;
    chapter += `|----------|-------|-------------|-----------|\ n`;
    chapter += `| **All Tanks** | **${total}** | **${operational}** | **${readiness}%** |\n`;

    if (tanks.heavy_tanks && tanks.heavy_tanks > 0) {
      const heavyOp = tanks.heavy_operational || tanks.heavy_tanks;
      const heavyRead = ((heavyOp / tanks.heavy_tanks) * 100).toFixed(1);
      chapter += `| **Heavy Tanks** | **${tanks.heavy_tanks}** | **${heavyOp}** | **${heavyRead}%** |\n`;
    }

    if (tanks.medium_tanks && tanks.medium_tanks > 0) {
      const medOp = tanks.medium_operational || tanks.medium_tanks;
      const medRead = ((medOp / tanks.medium_tanks) * 100).toFixed(1);
      chapter += `| **Medium Tanks** | **${tanks.medium_tanks}** | **${medOp}** | **${medRead}%** |\n`;
    }

    if (tanks.light_tanks && tanks.light_tanks > 0) {
      const lightOp = tanks.light_operational || tanks.light_tanks;
      const lightRead = ((lightOp / tanks.light_tanks) * 100).toFixed(1);
      chapter += `| **Light Tanks** | **${tanks.light_tanks}** | **${lightOp}** | **${lightRead}%** |\n`;
    }

    chapter += `\n`;

    if (tanks.notes) {
      chapter += `**Notes**: ${tanks.notes}\n\n`;
    }
  } else {
    chapter += `This unit had **no organic tank strength**.\n\n`;
    if (unitData.tanks && unitData.tanks.notes) {
      chapter += `**Notes**: ${unitData.tanks.notes}\n\n`;
    } else if (unitData.tanks && unitData.tanks.note) {
      chapter += `**Notes**: ${unitData.tanks.note}\n\n`;
    }
  }

  // Section 6: Artillery Strength
  chapter += `## Artillery Strength\n\n`;

  if (unitData.artillery) {
    const art = unitData.artillery;
    let totalGuns = 0;
    let totalOp = 0;

    chapter += `| Type | Total | Operational | Notes |\n`;
    chapter += `|------|-------|-------------|-------|\n`;

    // Field Artillery
    if (art.field_artillery && art.field_artillery.total_guns > 0) {
      const fieldTotal = art.field_artillery.total_guns;
      totalGuns += fieldTotal;
      chapter += `| **Field Artillery** | **${fieldTotal}** | - | - |\n`;

      if (art.field_artillery.units && Array.isArray(art.field_artillery.units)) {
        art.field_artillery.units.forEach(unit => {
          chapter += `| ↳ ${unit.designation} | ${unit.guns || '-'} | - | ${unit.notes || '-'} |\n`;
        });
      }
    } else if (art.field_guns) {
      // Alternative structure
      const fieldGuns = art.field_guns;
      const fieldTotal = fieldGuns.total || 0;
      totalGuns += fieldTotal;
      chapter += `| **Field Artillery** | **${fieldTotal}** | - | - |\n`;

      Object.keys(fieldGuns).forEach(key => {
        if (key !== 'total' && typeof fieldGuns[key] === 'object') {
          const gun = fieldGuns[key];
          const count = gun.count || 0;
          const op = gun.operational || count;
          totalOp += op;
          chapter += `| ↳ ${key.replace(/_/g, ' ')} | ${count} | ${op} | - |\n`;
        }
      });
    }

    // Anti-Tank
    if (art.anti_tank) {
      const atTotal = art.anti_tank.total || (art.anti_tank.guns ? Object.values(art.anti_tank.guns).reduce((sum, g) => sum + (g.count || 0), 0) : 0);
      totalGuns += atTotal;
      chapter += `| **Anti-Tank** | **${atTotal}** | - | - |\n`;

      if (art.anti_tank.guns) {
        Object.keys(art.anti_tank.guns).forEach(key => {
          const gun = art.anti_tank.guns[key];
          const count = gun.count || 0;
          const op = gun.operational || count;
          totalOp += op;
          chapter += `| ↳ ${gun.type || key} | ${count} | ${op} | ${gun.notes || '-'} |\n`;
        });
      } else {
        Object.keys(art.anti_tank).forEach(key => {
          if (key !== 'total' && key !== 'designation' && key !== 'personnel' && key !== 'organization' && key !== 'notes') {
            if (typeof art.anti_tank[key] === 'object') {
              const gun = art.anti_tank[key];
              const count = gun.count || 0;
              const op = gun.operational || count;
              totalOp += op;
              chapter += `| ↳ ${key.replace(/_/g, ' ')} | ${count} | ${op} | - |\n`;
            }
          }
        });
      }
    }

    // Anti-Aircraft
    if (art.anti_aircraft) {
      const aaTotal = art.anti_aircraft.total || (art.anti_aircraft.guns ? Object.values(art.anti_aircraft.guns).reduce((sum, g) => sum + (g.count || 0), 0) : 0);
      totalGuns += aaTotal;
      chapter += `| **Anti-Aircraft** | **${aaTotal}** | - | - |\n`;

      if (art.anti_aircraft.guns) {
        Object.keys(art.anti_aircraft.guns).forEach(key => {
          const gun = art.anti_aircraft.guns[key];
          const count = gun.count || 0;
          const op = gun.operational || count;
          totalOp += op;
          chapter += `| ↳ ${gun.type || key} | ${count} | ${op} | ${gun.notes || '-'} |\n`;
        });
      } else {
        Object.keys(art.anti_aircraft).forEach(key => {
          if (key !== 'total' && key !== 'designation' && key !== 'personnel' && key !== 'notes') {
            if (typeof art.anti_aircraft[key] === 'object') {
              const gun = art.anti_aircraft[key];
              const count = gun.count || 0;
              const op = gun.operational || count;
              totalOp += op;
              chapter += `| ↳ ${key.replace(/_/g, ' ')} | ${count} | ${op} | - |\n`;
            }
          }
        });
      }
    }

    chapter += `| **Total Artillery** | **${art.total_tubes || totalGuns}** | - | - |\n\n`;

    if (art.field_artillery && art.field_artillery.notes) {
      chapter += `**Field Artillery Notes**: ${art.field_artillery.notes}\n\n`;
    }
    if (art.anti_tank && art.anti_tank.notes) {
      chapter += `**Anti-Tank Notes**: ${art.anti_tank.notes}\n\n`;
    }
    if (art.anti_aircraft && art.anti_aircraft.notes) {
      chapter += `**Anti-Aircraft Notes**: ${art.anti_aircraft.notes}\n\n`;
    }
  } else {
    chapter += `No artillery data available.\n\n`;
  }

  // Section 7: Infantry Weapons
  chapter += `## Infantry Weapons\n\n`;

  if (unitData.top_3_infantry_weapons) {
    // Handle both array and object formats
    let weapons = [];
    if (Array.isArray(unitData.top_3_infantry_weapons)) {
      weapons = unitData.top_3_infantry_weapons;
    } else if (typeof unitData.top_3_infantry_weapons === 'object') {
      // Convert object to array
      weapons = Object.keys(unitData.top_3_infantry_weapons)
        .filter(key => !isNaN(key))
        .map(key => unitData.top_3_infantry_weapons[key]);
    }

    if (weapons.length > 0) {
      chapter += `### Top 3 Weapons by Count\n\n`;
      chapter += `| Rank | Weapon | Count | Type | Role |\n`;
      chapter += `|------|--------|-------|------|------|\n`;

      weapons.forEach((wpn, idx) => {
        chapter += `| #${idx + 1} | ${wpn.weapon} | ${wpn.count} | ${wpn.type} | ${wpn.specifications?.role || wpn.notes || '-'} |\n`;
      });

      chapter += `\n`;
    } else {
      chapter += `Infantry weapons data not detailed in TO&E.\n\n`;
    }
  } else {
    chapter += `Infantry weapons data not detailed in TO&E.\n\n`;
  }

  // Section 8: Transport & Vehicles
  chapter += `## Transport & Vehicles\n\n`;

  if (unitData.ground_vehicles) {
    const veh = unitData.ground_vehicles;
    const total = veh.total || 0;
    const operational = veh.operational || total;
    const opPct = total > 0 ? ((operational / total) * 100).toFixed(1) : '0.0';

    chapter += `| Category | Count | Operational | Readiness |\n`;
    chapter += `|----------|-------|-------------|-----------|\ n`;
    chapter += `| **Total Vehicles** | **${total}** | **${operational}** | **${opPct}%** |\n`;

    if (veh.trucks) {
      const truckCount = typeof veh.trucks === 'object' ? veh.trucks.count : veh.trucks;
      const truckOp = typeof veh.trucks === 'object' ? veh.trucks.operational || truckCount : truckCount;
      chapter += `| Trucks | ${truckCount} | ${truckOp} | - |\n`;
    }

    if (veh.carriers) {
      const carrierCount = typeof veh.carriers === 'object' ? veh.carriers.count : veh.carriers;
      const carrierOp = typeof veh.carriers === 'object' ? veh.carriers.operational || carrierCount : carrierCount;
      chapter += `| Carriers | ${carrierCount} | ${carrierOp} | - |\n`;
    }

    if (veh.motorcycles) {
      const motoCount = typeof veh.motorcycles === 'object' ? veh.motorcycles.count : veh.motorcycles;
      const motoOp = typeof veh.motorcycles === 'object' ? veh.motorcycles.operational || motoCount : motoCount;
      chapter += `| Motorcycles | ${motoCount} | ${motoOp} | - |\n`;
    }

    if (veh.staff_cars) {
      chapter += `| Staff Cars | ${veh.staff_cars} | - | - |\n`;
    }

    if (veh.ambulances) {
      const ambCount = typeof veh.ambulances === 'object' ? veh.ambulances.count : veh.ambulances;
      chapter += `| Ambulances | ${ambCount} | - | - |\n`;
    }

    chapter += `\n`;

    if (veh.notes) {
      chapter += `**Notes**: ${veh.notes}\n\n`;
    }
  } else {
    chapter += `No vehicle data available.\n\n`;
  }

  // Section 9: Supply & Logistics
  chapter += `## Supply & Logistics\n\n`;

  chapter += `### Logistics Status (${quarterDisplay})\n\n`;
  chapter += `| Resource | Quantity | Status | Notes |\n`;
  chapter += `|----------|----------|--------|-------|\n`;
  chapter += `| **Operational Radius** | ${unitData.operational_radius_km || 0} km | - | - |\n`;
  chapter += `| **Fuel Reserves** | ${unitData.fuel_days || 0} days | - | At current consumption rate |\n`;
  chapter += `| **Ammunition** | ${unitData.ammo_days || 0} days | - | Combat load basis |\n`;
  chapter += `| **Water Supply** | ${unitData.water_days || 0} days | - | Desert operations requirement |\n\n`;

  if (unitData.supply_notes) {
    chapter += `**Supply Notes**: ${unitData.supply_notes}\n\n`;
  }

  // Section 10: Operational Environment
  chapter += `## Operational Environment\n\n`;

  chapter += `### Environmental Conditions (${quarterDisplay})\n\n`;
  chapter += `| Factor | Value | Impact |\n`;
  chapter += `|--------|-------|--------|\n`;
  chapter += `| **Season** | ${unitData.season || 'Unknown'} | - |\n`;
  chapter += `| **Temperature Range** | ${unitData.temperature_range_c || 'Unknown'}°C | - |\n`;
  chapter += `| **Terrain Type** | ${unitData.terrain_conditions || 'Unknown'} | - |\n\n`;

  if (unitData.weather_impact) {
    chapter += `**Weather Impact**: ${unitData.weather_impact}\n\n`;
  }

  if (unitData.weather_environment) {
    if (typeof unitData.weather_environment === 'string') {
      chapter += `**Environment**: ${unitData.weather_environment}\n\n`;
    } else {
      Object.keys(unitData.weather_environment).forEach(key => {
        chapter += `**${key.replace(/_/g, ' ')}**: ${unitData.weather_environment[key]}\n\n`;
      });
    }
  }

  // Section 11: Organizational Structure
  chapter += `## Organizational Structure\n\n`;

  if (unitData.subordinate_units && unitData.subordinate_units.length > 0) {
    unitData.subordinate_units.forEach(sub => {
      chapter += `### ${sub.unit_designation || 'Unknown Unit'}\n\n`;
      if (sub.commander) chapter += `**Commander**: ${sub.commander}\n`;
      if (sub.unit_type) chapter += `**Type**: ${sub.unit_type}\n`;
      if (sub.strength) chapter += `**Strength**: ${sub.strength} personnel\n`;
      if (sub.battalions) {
        if (Array.isArray(sub.battalions)) {
          chapter += `**Battalions**: ${sub.battalions.join(', ')}\n`;
        } else {
          chapter += `**Battalions**: ${sub.battalions}\n`;
        }
      }
      if (sub.guns) chapter += `**Guns**: ${sub.guns}\n`;
      if (sub.notes) chapter += `**Notes**: ${sub.notes}\n`;
      chapter += `\n`;
    });
  } else if (unitData.infantry && unitData.infantry.brigades) {
    unitData.infantry.brigades.forEach(bde => {
      chapter += `### ${bde.designation}\n\n`;
      if (bde.commander) chapter += `**Commander**: ${bde.commander}\n`;
      if (bde.total_personnel) chapter += `**Strength**: ${bde.total_personnel} personnel\n`;
      if (bde.battalions && Array.isArray(bde.battalions)) {
        chapter += `**Battalions**:\n`;
        bde.battalions.forEach(bn => {
          if (typeof bn === 'object') {
            chapter += `- ${bn.designation} (${bn.personnel} personnel)\n`;
          } else {
            chapter += `- ${bn}\n`;
          }
        });
      }
      if (bde.notes) chapter += `**Notes**: ${bde.notes}\n`;
      chapter += `\n`;
    });
  } else {
    chapter += `Detailed organizational structure not documented in TO&E.\n\n`;
  }

  // Section 12: Tactical Doctrine & Capabilities
  chapter += `## Tactical Doctrine & Capabilities\n\n`;

  if (unitData.combat_status && unitData.combat_status.notes) {
    chapter += `${unitData.combat_status.notes}\n\n`;
  } else {
    chapter += `Tactical doctrine and capabilities not detailed in TO&E.\n\n`;
  }

  // Section 13: Critical Equipment Shortages
  chapter += `## Critical Equipment Shortages\n\n`;

  chapter += `Equipment shortage data not systematically documented for this unit.\n\n`;

  // Section 14: Historical Context
  chapter += `## Historical Context\n\n`;

  if (unitData.historical_notes) {
    const hist = unitData.historical_notes;
    if (hist.formation) chapter += `**Formation**: ${hist.formation}\n\n`;
    if (hist.deployment) chapter += `**Deployment**: ${hist.deployment}\n\n`;
    if (hist.q1_operations) chapter += `**Q1 Operations**: ${hist.q1_operations}\n\n`;
    if (hist.q2_operations) chapter += `**Q2 Operations**: ${hist.q2_operations}\n\n`;
    if (hist.q3_operations) chapter += `**Q3 Operations**: ${hist.q3_operations}\n\n`;
    if (hist.q4_operations) chapter += `**Q4 Operations**: ${hist.q4_operations}\n\n`;
    if (hist.significance) chapter += `**Significance**: ${hist.significance}\n\n`;
    if (hist.commander_notes) chapter += `**Commander Notes**: ${hist.commander_notes}\n\n`;
    if (hist.destruction) chapter += `**Destruction**: ${hist.destruction}\n\n`;
  }

  if (unitData.combat_status && unitData.combat_status.battle_experience) {
    chapter += `**Battle Experience**: ${unitData.combat_status.battle_experience}\n\n`;
  }

  // Section 15: Wargaming Data
  chapter += `## Wargaming Data\n\n`;

  if (unitData.combat_status) {
    const cs = unitData.combat_status;
    if (cs.morale) chapter += `**Morale**: ${cs.morale}\n`;
    if (cs.operational_readiness) chapter += `**Operational Readiness**: ${cs.operational_readiness}%\n`;
    if (cs.combat_effectiveness) chapter += `**Combat Effectiveness**: ${cs.combat_effectiveness}%\n`;
    if (cs.status) chapter += `**Status**: ${cs.status}\n`;
    chapter += `\n`;
  }

  chapter += `Suitable for wargaming scenarios set in North Africa ${quarterDisplay}.\n\n`;

  // Section 16: Data Quality & Known Gaps
  chapter += `## Data Quality & Known Gaps\n\n`;
  chapter += `---\n\n`;
  chapter += `### ⭐ EXTRACTION QUALITY\n\n`;

  if (unitData.validation) {
    const val = unitData.validation;
    const tier = val.tier || 1;
    const tierNames = {1: 'Production Ready', 2: 'Review Recommended', 3: 'Partial Needs Research', 4: 'Research Brief Created'};
    const tierName = tierNames[tier] || 'Unknown';
    const confidence = val.confidence_level || 0;
    const status = val.status || 'unknown';

    chapter += `**Tier**: ${tier} (${tierName})\n`;
    chapter += `**Status**: ${status}\n`;
    chapter += `**Confidence Score**: ${confidence}% \n\n`;

    chapter += `**Tier Definitions**:\n`;
    chapter += `- **Tier 1 (75-100%)**: Production Ready - All required fields present\n`;
    chapter += `- **Tier 2 (60-74%)**: Review Recommended - Minor documented gaps acceptable\n`;
    chapter += `- **Tier 3 (50-59%)**: Partial Needs Research - Substantial data, critical gaps remain\n`;
    chapter += `- **Tier 4 (<50%)**: Research Brief Created - Insufficient data for extraction\n\n`;

    chapter += `---\n\n`;
    chapter += `### Data Sources\n\n`;

    if (val.sources && val.sources.length > 0) {
      chapter += `This unit's TO&E was compiled from:\n`;
      val.sources.forEach(src => {
        chapter += `- **${src.type}**: ${src.name} (${src.confidence}% confidence)\n`;
        if (src.notes) chapter += `  - ${src.notes}\n`;
      });
      chapter += `\n`;
    }

    if (val.notes) {
      chapter += `### Research Notes\n\n`;
      if (Array.isArray(val.notes)) {
        val.notes.forEach(note => {
          chapter += `- ${note}\n`;
        });
      } else if (typeof val.notes === 'string') {
        chapter += `- ${val.notes}\n`;
      }
      chapter += `\n`;
    }
  }

  // Section 17: Conclusion
  chapter += `## Conclusion\n\n`;

  if (isNotOperational) {
    chapter += `**${unitDesignation}** was not operationally deployed during ${quarterDisplay}. `;
    chapter += `The unit was designated or forming during this period but did not participate in combat operations. `;
    chapter += `For operational data on German forces in North Africa during this quarter, consult the predecessor or successor units.\n\n`;
  } else if (unitData.combat_status && unitData.combat_status.status && unitData.combat_status.status.includes('Destroyed')) {
    chapter += `**${unitDesignation}** was destroyed during ${quarterDisplay} and never reconstituted. `;
    chapter += `The division's destruction contributed to the overall attrition of Axis forces in North Africa.\n\n`;
  } else {
    chapter += `**${unitDesignation}** represents a significant formation of the ${nationDisplay} forces in North Africa during ${quarterDisplay}. `;
    chapter += `The unit's organization, equipment, and operational status reflect the challenges and evolution of desert warfare during this period.\n\n`;
  }

  // Data Source Footer
  chapter += `---\n\n`;

  const extractionDate = new Date().toISOString().split('T')[0];
  const confidence = unitData.validation?.confidence_level || 0;
  const tier = unitData.validation?.tier || 1;
  const tierDesc = {1: 'Primary Sources', 2: 'Primary + Curated Web', 3: 'Mixed Sources', 4: 'Insufficient Data'}[tier] || 'Unknown';

  chapter += `**Data Source**: Autonomous TO&E Extraction System\n`;
  chapter += `**Confidence**: ${confidence}% (${tierDesc})\n`;
  chapter += `**Schema**: unified_toe_schema.json v${unitData.schema_version || '3.1.0'} (Ground Forces)\n`;
  chapter += `**Extraction Date**: ${extractionDate}\n\n`;

  chapter += `---\n\n`;

  chapter += `*For detailed equipment specifications and cross-references, see unit TO&E JSON file.*\n`;

  return chapter;
}

/**
 * Main execution
 */
function main() {
  console.log(`📚 GENERATING MDBOOK CHAPTERS FOR 31 MISSING UNITS\n`);

  let generated = 0;
  let errors = 0;
  const generatedFiles = [];

  MISSING_UNITS.forEach(unitName => {
    try {
      // Read unit JSON
      const unitPath = path.join(UNITS_DIR, `${unitName}_toe.json`);
      if (!fs.existsSync(unitPath)) {
        console.log(`⚠️  SKIP: ${unitName} (JSON file not found)`);
        errors++;
        return;
      }

      const unitData = JSON.parse(fs.readFileSync(unitPath, 'utf8'));

      // Generate chapter
      const chapter = generateChapter(unitData, unitName);

      // Save chapter
      const chapterPath = path.join(CHAPTERS_DIR, `chapter_${unitName}.md`);
      fs.writeFileSync(chapterPath, chapter, 'utf8');

      console.log(`✅ Generated: chapter_${unitName}.md`);
      generated++;
      generatedFiles.push(`chapter_${unitName}.md`);

    } catch (error) {
      console.log(`❌ ERROR: ${unitName} - ${error.message}`);
      errors++;
    }
  });

  console.log(`\n${'='.repeat(60)}\n`);
  console.log(`📊 GENERATION SUMMARY\n`);
  console.log(`Total Units: ${MISSING_UNITS.length}`);
  console.log(`Chapters Generated: ${generated}`);
  console.log(`Errors: ${errors}`);
  console.log(`\n${'='.repeat(60)}\n`);

  if (generated > 0) {
    console.log(`✅ SUCCESS: Generated ${generated} chapters\n`);
    console.log(`📁 Files saved to: ${CHAPTERS_DIR}\n`);
    console.log(`Generated chapters:\n`);
    generatedFiles.forEach(file => {
      console.log(`  - ${file}`);
    });
  }

  if (errors > 0) {
    console.log(`\n⚠️  ${errors} units had errors\n`);
  }

  console.log(`\nRun 'node scripts/find_missing_chapters.js' to verify all chapters generated.\n`);
}

// Execute
main();
