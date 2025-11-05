#!/usr/bin/env node

/**
 * MDBook Chapter Generator for 1941-Q2 North Africa Units
 *
 * Generates 18 MDBook chapters from JSON source files following template v2.0
 * with all 16 required sections.
 *
 * Usage: node scripts/generate_mdbook_chapters.js
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  sourceDir: 'data/output/1941-q2-showcase/consolidated_units',
  outputBaseDir: 'data/output/1941-q2-showcase/north-africa-toe-book/src/1941-q2',
  templateFile: 'docs/MDBOOK_CHAPTER_TEMPLATE.md',
  sampleFile: 'data/output/autonomous_1760133539236/mdbook_sample_7th_armoured.md'
};

// Unit mappings with nation and chapter name
const UNITS = [
  // British/Commonwealth (7 units)
  { json: 'britain_1941q2_7th_armoured_division_toe.json', nation: 'british', chapter: 'chapter_7th_armoured_division.md' },
  { json: 'britain_1941q2_50th_infantry_division_toe.json', nation: 'british', chapter: 'chapter_50th_infantry_division.md' },
  { json: 'britain_1941q2_2nd_new_zealand_division_toe.json', nation: 'british', chapter: 'chapter_2nd_new_zealand_division.md' },
  { json: 'britain_1941q2_4th_indian_division_toe.json', nation: 'british', chapter: 'chapter_4th_indian_division.md' },
  { json: 'britain_1941-q2_5th_indian_division_toe.json', nation: 'british', chapter: 'chapter_5th_indian_division.md' },
  { json: 'britain_1941-q2_9th_australian_division_toe.json', nation: 'british', chapter: 'chapter_9th_australian_division.md' },
  { json: 'britain_1941-q2_1st_south_african_division_toe.json', nation: 'british', chapter: 'chapter_1st_south_african_division.md' },

  // German (3 units)
  { json: 'germany_1941q2_deutsches_afrikakorps_toe.json', nation: 'german', chapter: 'chapter_deutsches_afrikakorps.md' },
  { json: 'germany_1941-Q2_15_panzer_division_toe.json', nation: 'german', chapter: 'chapter_15_panzer_division.md' },
  { json: 'germany_1941-q2_5_leichte_division_toe.json', nation: 'german', chapter: 'chapter_5_leichte_division.md' },

  // Italian (8 units)
  { json: 'italy_1941q2_132_ariete_division_toe.json', nation: 'italian', chapter: 'chapter_132_ariete_division.md' },
  { json: 'italy_1941q2_17_pavia_division_toe.json', nation: 'italian', chapter: 'chapter_17_pavia_division.md' },
  { json: 'italy_1941q2_27_brescia_division_toe.json', nation: 'italian', chapter: 'chapter_27_brescia_division.md' },
  { json: 'italy_1941q2_55_trento_division_toe.json', nation: 'italian', chapter: 'chapter_55_trento_division.md' },
  { json: 'italy_1941q2_sabratha_division_toe.json', nation: 'italian', chapter: 'chapter_sabratha_division.md' },
  { json: 'italy_1941q2_trieste_division_toe.json', nation: 'italian', chapter: 'chapter_trieste_division.md' },
  { json: 'italy_1941-q2_bologna_division_toe.json', nation: 'italian', chapter: 'chapter_bologna_division.md' },
  { json: 'italy_1941-q2_savona_division_toe.json', nation: 'italian', chapter: 'chapter_savona_division.md' }
];

/**
 * Helper function to format numbers with commas
 */
function formatNumber(num) {
  return num ? num.toLocaleString('en-US') : '0';
}

/**
 * Calculate readiness percentage
 */
function calculateReadiness(operational, total) {
  if (!total || total === 0) return 0;
  return Math.round((operational / total) * 100);
}

/**
 * Generate equipment variant detail section
 */
function generateVariantDetailSection(variants, categoryTitle, categoryType) {
  if (!variants || variants.length === 0) return '';

  let section = `\n### ${categoryTitle}\n\n`;

  variants.forEach(variant => {
    section += `#### ${variant.model || variant.weapon}`;
    if (variant.variant && variant.variant !== 'Standard') {
      section += ` (${variant.variant})`;
    }
    section += `\n\n`;

    // Specifications table based on type
    section += `| Specification | Details |\n`;
    section += `|--------------|----------|\n`;

    if (categoryType === 'tank' || categoryType === 'armored_car') {
      section += `| **Armament** | ${variant.armament || 'Unknown'} |\n`;

      // Fix armor - handle multiple field names
      let armorValue = 'Unknown';
      if (variant.armor && variant.armor !== 'Unknown') {
        armorValue = variant.armor;
      } else if (variant.armor_mm) {
        armorValue = variant.armor_mm + (typeof variant.armor_mm === 'string' && variant.armor_mm.includes('mm') ? '' : 'mm');
      }
      section += `| **Armor** | ${armorValue} |\n`;

      section += `| **Crew** | ${variant.crew || 'Unknown'} |\n`;

      // Fix speed
      let speedValue = 'Unknown';
      if (variant.speed && variant.speed !== 'Unknown') {
        speedValue = variant.speed;
      } else if (variant.speed_kmh) {
        speedValue = variant.speed_kmh + ' km/h';
      }
      section += `| **Speed** | ${speedValue} |\n`;

      section += `| **Quantity** | ${variant.quantity || variant.count || 0} |\n`;
      if (variant.operational) {
        section += `| **Operational** | ${variant.operational} (${calculateReadiness(variant.operational, variant.quantity || variant.count)}%) |\n`;
      }
    } else if (categoryType === 'artillery') {
      section += `| **Caliber** | ${variant.caliber || 'Unknown'} |\n`;
      section += `| **Type** | ${variant.type || 'Unknown'} |\n`;

      // Fix range - handle multiple field names
      let rangeValue = 'Unknown';
      if (variant.max_range && variant.max_range !== 'Unknown') {
        rangeValue = variant.max_range;
      } else if (variant.range_km) {
        rangeValue = variant.range_km + ' km';
      } else if (variant.range_m) {
        rangeValue = variant.range_m + ' m';
      } else if (variant.range_meters) {
        const rangeKm = (variant.range_meters / 1000).toFixed(1);
        rangeValue = rangeKm + ' km';
      }
      section += `| **Max Range** | ${rangeValue} |\n`;

      section += `| **Crew** | ${variant.crew || 'Unknown'} |\n`;
      section += `| **Quantity** | ${variant.quantity || variant.count || 0} |\n`;

      // Fix penetration
      if (variant.penetration || variant.penetration_mm) {
        const penValue = variant.penetration || (variant.penetration_mm + 'mm');
        section += `| **Penetration** | ${penValue} |\n`;
      }
    } else if (categoryType === 'vehicle') {
      section += `| **Type** | ${variant.model || variant.category || 'Unknown'} |\n`;
      section += `| **Capacity** | ${variant.capacity || 'Unknown'} |\n`;
      if (variant.speed || variant.speed_kmh) {
        section += `| **Speed** | ${variant.speed || variant.speed_kmh + ' km/h'} |\n`;
      }
      section += `| **Quantity** | ${variant.quantity || variant.count || 0} |\n`;
      if (variant.operational) {
        section += `| **Operational** | ${variant.operational} (${calculateReadiness(variant.operational, variant.quantity || variant.count)}%) |\n`;
      }
    }

    // Combat performance / Notes
    if (variant.notes) {
      section += `\n**Combat Performance:**\n${variant.notes}\n`;
    }

    section += `\n`;
  });

  return section;
}

/**
 * Generate a complete chapter from JSON data
 */
function generateChapter(unit) {
  const jsonPath = path.join(CONFIG.sourceDir, unit.json);
  const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

  let chapter = '';

  // Section 1: Header
  const unitDesignation = data.unit_designation || data.unit_identification?.unit_designation || 'Unknown Unit';
  const nation = data.nation || data.unit_identification?.nation || 'unknown';
  const quarter = data.quarter || data.unit_identification?.quarter || 'Unknown';
  const location = data.geographic_location || data.unit_identification?.geographic_location || 'Unknown';
  const unitType = data.unit_type || data.unit_identification?.unit_type || 'unknown';

  chapter += `# ${unitDesignation}\n\n`;
  chapter += `**Nation:** ${nation.charAt(0).toUpperCase() + nation.slice(1)}\n`;
  chapter += `**Quarter:** ${quarter}\n`;
  chapter += `**Location:** ${location}\n`;
  chapter += `**Type:** ${unitType.replace(/_/g, ' ')}\n\n`;
  chapter += `---\n\n`;

  // Section 2: Division/Unit Overview (2-3 paragraphs)
  chapter += `## Division Overview\n\n`;

  // Formation info
  if (data.operational_history?.formation) {
    if (typeof data.operational_history.formation === 'string') {
      chapter += `${data.operational_history.formation}\n\n`;
    } else if (typeof data.operational_history.formation === 'object') {
      if (data.operational_history.formation.original_designation) {
        chapter += `Formed as ${data.operational_history.formation.original_designation}`;
        if (data.operational_history.formation.redesignated) {
          chapter += `, redesignated ${data.operational_history.formation.redesignated}`;
        }
        chapter += `.`;
        if (data.operational_history.formation.nickname) {
          chapter += ` Known as "${data.operational_history.formation.nickname}".`;
        }
        chapter += `\n\n`;
      }
    }
  }

  // Quarterly assessment
  if (data.operational_history?.quarterly_assessment) {
    chapter += `${data.operational_history.quarterly_assessment}\n\n`;
  }

  // Deployment to theater
  if (data.operational_history?.deployment_to_theater) {
    chapter += `${data.operational_history.deployment_to_theater}\n\n`;
  }

  // Section 3: Command
  chapter += `## Command\n\n`;
  chapter += `| Position | Name | Rank |\n`;
  chapter += `|----------|------|------|\n`;

  // Safely extract commander info
  const commanderName = data.command?.commander?.name || 'Unknown';
  const commanderRank = data.command?.commander?.rank || 'Unknown';
  chapter += `| **Commanding Officer** | ${commanderName} | ${commanderRank} |\n`;

  const deputyCmd = data.command?.deputy_commander;
  if (deputyCmd && typeof deputyCmd === 'object' && deputyCmd.name) {
    chapter += `| **Deputy Commander** | ${deputyCmd.name} | ${deputyCmd.rank || '-'} |\n`;
  } else if (deputyCmd && typeof deputyCmd === 'string' && deputyCmd !== 'Unknown') {
    chapter += `| **Deputy Commander** | ${deputyCmd} | - |\n`;
  }

  const chiefStaff = data.command?.chief_of_staff;
  if (chiefStaff && typeof chiefStaff === 'object' && chiefStaff.name) {
    chapter += `| **Chief of Staff** | ${chiefStaff.name} | ${chiefStaff.rank || '-'} |\n`;
  } else if (chiefStaff && typeof chiefStaff === 'string' && chiefStaff !== 'Unknown') {
    chapter += `| **Chief of Staff** | ${chiefStaff} | - |\n`;
  }

  chapter += `\n`;
  chapter += `**Headquarters:** ${data.command?.command_post_location || data.command?.headquarters_location || 'Unknown'}\n\n`;

  const cmdNotes = data.command?.commander_tenure_notes || data.command?.commander?.previous_service || data.command?.commander?.notes;
  if (cmdNotes) {
    chapter += `**Command Notes:** ${cmdNotes}\n\n`;
  }

  // Section 4: Personnel Strength
  chapter += `## Personnel Strength\n\n`;

  // Handle both direct fields and personnel_summary structure
  const totalPersonnel = data.total_personnel || data.personnel_summary?.total_personnel || 0;
  const officers = data.officers || data.personnel_summary?.officers || 0;
  const ncos = data.ncos || data.personnel_summary?.ncos || 0;
  const enlisted = data.enlisted || data.personnel_summary?.enlisted || 0;
  const authorizedStrength = data.authorized_strength || data.personnel_summary?.authorized_strength;
  const actualPercentage = data.actual_percentage || data.personnel_summary?.actual_percentage;

  chapter += `| Category | Count | Percentage |\n`;
  chapter += `|----------|-------|------------|\n`;
  chapter += `| **Total Personnel** | ${formatNumber(totalPersonnel)} | 100% |\n`;
  chapter += `| Officers | ${formatNumber(officers)} | ${totalPersonnel ? ((officers/totalPersonnel)*100).toFixed(1) : 0}% |\n`;
  chapter += `| NCOs | ${formatNumber(ncos)} | ${totalPersonnel ? ((ncos/totalPersonnel)*100).toFixed(1) : 0}% |\n`;
  chapter += `| Enlisted | ${formatNumber(enlisted)} | ${totalPersonnel ? ((enlisted/totalPersonnel)*100).toFixed(1) : 0}% |\n`;
  if (authorizedStrength) {
    chapter += `| **Authorized Strength** | ${formatNumber(authorizedStrength)} | - |\n`;
    chapter += `| **Actual %** | ${actualPercentage || Math.round((totalPersonnel/authorizedStrength)*100)}% | - |\n`;
  }
  chapter += `\n`;

  const personnelNotes = data.personnel_notes || data.personnel_summary?.notes;
  if (personnelNotes) {
    chapter += `**Personnel Notes:** ${personnelNotes}\n\n`;
  }

  // Section 5: Armoured Strength (if applicable)
  const tanksData = data.tanks || data.equipment_summary?.tanks;
  if (tanksData && tanksData.total > 0) {
    chapter += `## Armoured Strength\n\n`;

    // Summary table
    chapter += `### Tank Summary\n\n`;
    chapter += `| Category | Total | Operational | Readiness |\n`;
    chapter += `|----------|-------|-------------|----------|\n`;

    // Helper to get tank category count/operational
    function getTankCat(cat) {
      if (!cat) return null;
      // Handle both structures: {count, operational} and {total, operational}
      const total = cat.count || cat.total || cat || 0;
      const operational = cat.operational || total;
      return { total, operational };
    }

    // Heavy tanks
    const heavyTanks = getTankCat(tanksData.heavy_tanks);
    if (heavyTanks && heavyTanks.total > 0) {
      const readiness = calculateReadiness(heavyTanks.operational, heavyTanks.total);
      chapter += `| **Heavy Tanks** | ${heavyTanks.total} | ${heavyTanks.operational} | ${readiness}% |\n`;

      // Variants
      if (tanksData.heavy_tanks?.variants) {
        Object.entries(tanksData.heavy_tanks.variants).forEach(([name, variant]) => {
          const count = variant.count || variant.total || variant;
          chapter += `| ↳ ${name} | ${count} | - | - |\n`;
        });
      }
    }

    // Medium tanks
    const mediumTanks = getTankCat(tanksData.medium_tanks);
    if (mediumTanks && mediumTanks.total > 0) {
      const readiness = calculateReadiness(mediumTanks.operational, mediumTanks.total);
      chapter += `| **Medium Tanks** | ${mediumTanks.total} | ${mediumTanks.operational} | ${readiness}% |\n`;

      // Variants
      if (tanksData.medium_tanks?.variants) {
        Object.entries(tanksData.medium_tanks.variants).forEach(([name, variant]) => {
          const count = variant.count || variant.total || variant;
          const operational = variant.operational || count;
          chapter += `| ↳ ${name} | ${count} | ${operational} | - |\n`;
        });
      }
    }

    // Light tanks
    const lightTanks = getTankCat(tanksData.light_tanks);
    if (lightTanks && lightTanks.total > 0) {
      const readiness = calculateReadiness(lightTanks.operational, lightTanks.total);
      chapter += `| **Light Tanks** | ${lightTanks.total} | ${lightTanks.operational} | ${readiness}% |\n`;

      // Variants
      if (tanksData.light_tanks?.variants) {
        Object.entries(tanksData.light_tanks.variants).forEach(([name, variant]) => {
          const count = variant.count || variant.total || variant;
          chapter += `| ↳ ${name} | ${count} | - | - |\n`;
        });
      }
    }

    chapter += `\n`;
    if (tanksData.notes) {
      chapter += `**Notes:** ${tanksData.notes}\n\n`;
    }

    // Detail sections for each variant
    if (data.equipment_detail && data.equipment_detail.tanks_detail) {
      chapter += generateVariantDetailSection(data.equipment_detail.tanks_detail, 'Tank Specifications', 'tank');
    }
  }

  // Section 6: Artillery Strength
  if (data.artillery && (data.artillery.total > 0 || data.artillery_total > 0)) {
    chapter += `## Artillery Strength\n\n`;

    const artTotal = data.artillery.total || data.artillery_total || 0;
    chapter += `### Artillery Summary\n\n`;
    chapter += `| Category | Quantity |\n`;
    chapter += `|----------|----------|\n`;
    chapter += `| **Total Artillery** | ${artTotal} |\n`;

    if (data.artillery.field_artillery || data.field_artillery) {
      const fieldArt = data.artillery.field_artillery || data.field_artillery.total || 0;
      chapter += `| **Field Artillery** | ${fieldArt} |\n`;

      // Variants from equipment_detail
      if (data.equipment_detail && data.equipment_detail.artillery_detail) {
        const fieldVariants = data.equipment_detail.artillery_detail.filter(v => v.category === 'field_artillery');
        fieldVariants.forEach(v => {
          chapter += `| ↳ ${v.weapon} (${v.caliber}) | ${v.quantity} |\n`;
        });
      }
    }

    if (data.artillery.anti_tank_guns || data.anti_tank) {
      const atGuns = data.artillery.anti_tank_guns || data.anti_tank.total || 0;
      chapter += `| **Anti-Tank Guns** | ${atGuns} |\n`;

      // Variants
      if (data.equipment_detail && data.equipment_detail.artillery_detail) {
        const atVariants = data.equipment_detail.artillery_detail.filter(v => v.category === 'anti_tank_guns' || v.category === 'anti_tank');
        atVariants.forEach(v => {
          chapter += `| ↳ ${v.weapon} (${v.caliber}) | ${v.quantity} |\n`;
        });
      }
    }

    if (data.artillery.anti_aircraft_guns || data.anti_aircraft) {
      const aaGuns = data.artillery.anti_aircraft_guns || data.anti_aircraft.total || 0;
      chapter += `| **Anti-Aircraft Guns** | ${aaGuns} |\n`;

      // Variants
      if (data.equipment_detail && data.equipment_detail.artillery_detail) {
        const aaVariants = data.equipment_detail.artillery_detail.filter(v => v.category === 'anti_aircraft_guns' || v.category === 'anti_aircraft');
        aaVariants.forEach(v => {
          chapter += `| ↳ ${v.weapon} (${v.caliber}) | ${v.quantity} |\n`;
        });
      }
    }

    if (data.artillery.mortars || data.mortars) {
      const mortars = data.artillery.mortars || data.mortars.total || 0;
      chapter += `| **Mortars** | ${mortars} |\n`;

      // Variants
      if (data.mortars && data.mortars.variants) {
        Object.entries(data.mortars.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} (${variant.caliber}) | ${variant.count} |\n`;
        });
      }
    }

    chapter += `\n`;
    if (data.artillery.notes) {
      chapter += `**Notes:** ${data.artillery.notes}\n\n`;
    }

    // Detail sections
    if (data.equipment_detail && data.equipment_detail.artillery_detail) {
      chapter += generateVariantDetailSection(data.equipment_detail.artillery_detail, 'Artillery Specifications', 'artillery');
    }
  }

  // Section 7: Armoured Cars (separate from transport)
  if (data.armored_cars && data.armored_cars.total > 0) {
    chapter += `## Armoured Cars\n\n`;

    chapter += `| Category | Quantity |\n`;
    chapter += `|----------|----------|\n`;
    chapter += `| **Total Armoured Cars** | ${data.armored_cars.total} |\n`;

    if (data.armored_cars.heavy_armored_cars > 0) {
      chapter += `| **Heavy Armoured Cars** | ${data.armored_cars.heavy_armored_cars} |\n`;
    }
    if (data.armored_cars.medium_armored_cars > 0) {
      chapter += `| **Medium Armoured Cars** | ${data.armored_cars.medium_armored_cars} |\n`;
    }
    if (data.armored_cars.light_armored_cars > 0) {
      chapter += `| **Light Armoured Cars** | ${data.armored_cars.light_armored_cars} |\n`;
    }

    // Variants from equipment_detail or variants
    if (data.armored_cars.variants) {
      Object.entries(data.armored_cars.variants).forEach(([name, variant]) => {
        chapter += `| ↳ ${name} | ${variant.count} |\n`;
      });
    } else if (data.equipment_detail && data.equipment_detail.armored_cars_detail) {
      data.equipment_detail.armored_cars_detail.forEach(v => {
        chapter += `| ↳ ${v.model} | ${v.quantity} |\n`;
      });
    }

    chapter += `\n`;
    if (data.armored_cars.notes) {
      chapter += `**Notes:** ${data.armored_cars.notes}\n\n`;
    }

    // Detail sections
    if (data.equipment_detail && data.equipment_detail.armored_cars_detail) {
      chapter += generateVariantDetailSection(data.equipment_detail.armored_cars_detail, 'Armoured Car Specifications', 'armored_car');
    }
  }

  // Section 8: Infantry Weapons (NEW in v3.0)
  if (data.top_3_infantry_weapons) {
    chapter += `## Infantry Weapons\n\n`;
    chapter += `### Top 3 Weapons by Count\n\n`;
    chapter += `| Rank | Weapon | Count | Type | Role |\n`;
    chapter += `|------|--------|-------|------|------|\n`;

    // Extract top 3 weapons
    const top3 = data.top_3_infantry_weapons;
    for (let i = 1; i <= 3; i++) {
      if (top3[i.toString()]) {
        const weapon = top3[i.toString()];
        const weaponName = weapon.weapon || 'Unknown';
        const count = formatNumber(weapon.count || 0);
        const type = (weapon.type || 'unknown').replace(/_/g, ' ');

        // Determine role from type
        let role = 'Unknown';
        if (weapon.type === 'rifle') role = 'Primary infantry weapon';
        else if (weapon.type === 'light_machine_gun' || weapon.type === 'lmg') role = 'Squad automatic weapon';
        else if (weapon.type === 'heavy_machine_gun' || weapon.type === 'hmg') role = 'Heavy support weapon';
        else if (weapon.type === 'anti_tank_rifle') role = 'Infantry anti-tank capability';
        else if (weapon.type === 'submachine_gun' || weapon.type === 'smg') role = 'Close quarters combat';
        else if (weapon.type === 'pistol') role = 'Officer/NCO sidearm';
        else if (weapon.type === 'grenade_launcher') role = 'Infantry fire support';

        chapter += `| #${i} | ${weaponName} | ${count} | ${type} | ${role} |\n`;
      }
    }

    chapter += `\n`;
    if (data.infantry_weapons_notes) {
      chapter += `**Notes:** ${data.infantry_weapons_notes}\n\n`;
    }
  }

  // Section 9: Transport & Vehicles (NO tanks/armored cars)
  if (data.ground_vehicles || data.trucks) {
    chapter += `## Transport & Vehicles\n\n`;

    const totalVehicles = data.ground_vehicles?.total || data.ground_vehicles_total || 0;
    chapter += `**Total Ground Vehicles:** ${formatNumber(totalVehicles)}\n\n`;

    chapter += `| Category | Quantity |\n`;
    chapter += `|----------|----------|\n`;

    if (data.ground_vehicles?.trucks || data.trucks) {
      const trucks = data.ground_vehicles?.trucks || data.trucks.total || 0;
      chapter += `| **Trucks** | ${trucks} |\n`;

      // Truck variants
      if (data.trucks && data.trucks.variants) {
        Object.entries(data.trucks.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} (${variant.capacity}) | ${variant.count} |\n`;
        });
      } else if (data.equipment_detail && data.equipment_detail.ground_vehicles_detail) {
        const truckVariants = data.equipment_detail.ground_vehicles_detail.filter(v => v.category === 'trucks');
        truckVariants.forEach(v => {
          chapter += `| ↳ ${v.model} | ${v.quantity} |\n`;
        });
      }
    }

    if (data.ground_vehicles?.motorcycles || data.motorcycles) {
      const motorcycles = data.ground_vehicles?.motorcycles || data.motorcycles.total || 0;
      chapter += `| **Motorcycles** | ${motorcycles} |\n`;

      // Motorcycle variants
      if (data.motorcycles && data.motorcycles.variants) {
        Object.entries(data.motorcycles.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} | ${variant.count} |\n`;
        });
      }
    }

    if (data.ground_vehicles?.prime_movers > 0) {
      chapter += `| **Prime Movers** | ${data.ground_vehicles.prime_movers} |\n`;
    }
    if (data.ground_vehicles?.trailers > 0) {
      chapter += `| **Trailers** | ${data.ground_vehicles.trailers} |\n`;
    }
    if (data.ground_vehicles?.staff_cars > 0) {
      chapter += `| **Staff Cars** | ${data.ground_vehicles.staff_cars} |\n`;
    }

    // Support vehicles
    if (data.support_vehicles && data.support_vehicles.total > 0) {
      chapter += `| **Support Vehicles** | ${data.support_vehicles.total} |\n`;
      if (data.support_vehicles.variants) {
        Object.entries(data.support_vehicles.variants).forEach(([name, variant]) => {
          chapter += `| ↳ ${name} | ${variant.count} |\n`;
        });
      }
    }

    chapter += `\n`;
    if (data.ground_vehicles?.notes) {
      chapter += `**Notes:** ${data.ground_vehicles.notes}\n\n`;
    }

    // Vehicle detail sections
    if (data.equipment_detail && data.equipment_detail.ground_vehicles_detail) {
      chapter += generateVariantDetailSection(data.equipment_detail.ground_vehicles_detail, 'Vehicle Specifications', 'vehicle');
    }
  }

  // Section 9: Organizational Structure
  chapter += `## Organizational Structure\n\n`;
  if (data.subordinate_units && data.subordinate_units.length > 0) {
    chapter += `### Subordinate Units\n\n`;
    data.subordinate_units.forEach((unit, idx) => {
      chapter += `${idx + 1}. **${unit.unit_designation}**\n`;
      chapter += `   - Type: ${unit.unit_type}\n`;
      if (unit.strength) {
        chapter += `   - Strength: ${formatNumber(unit.strength)} personnel\n`;
      }
      if (unit.notes) {
        chapter += `   - Notes: ${unit.notes}\n`;
      }
      chapter += `\n`;
    });
  }

  // Section 10: Supply Status
  chapter += `## Supply Status\n\n`;
  if (data.logistics || data.supply_status) {
    const supply = data.supply_status || data.logistics;
    chapter += `| Resource | Status | Days on Hand |\n`;
    chapter += `|----------|--------|---------------|\n`;

    if (supply.fuel_days || supply.fuel_status) {
      chapter += `| **Fuel** | ${supply.fuel_status || 'Unknown'} | ${supply.fuel_days || '-'} |\n`;
    }
    if (supply.ammunition_days || supply.ammunition_status) {
      chapter += `| **Ammunition** | ${supply.ammunition_status || 'Unknown'} | ${supply.ammunition_days || '-'} |\n`;
    }
    if (supply.food_days) {
      chapter += `| **Food** | ${supply.supply_status || 'Unknown'} | ${supply.food_days || '-'} |\n`;
    }
    if (supply.water_liters_per_day) {
      chapter += `| **Water** | ${supply.water_liters_per_day} L/day | - |\n`;
    }

    chapter += `\n`;

    if (supply.supply_lines || data.logistics?.supply_lines) {
      chapter += `**Supply Lines:** ${supply.supply_lines || data.logistics.supply_lines}\n\n`;
    }
    if (supply.special_notes || data.logistics?.special_notes) {
      chapter += `**Special Considerations:** ${supply.special_notes || data.logistics.special_notes}\n\n`;
    }
  }

  // Section 11: Operational Environment (NEW in v3.0)
  if (data.weather_environment) {
    chapter += `## Operational Environment\n\n`;

    const weather = data.weather_environment;
    chapter += `### Environmental Conditions\n\n`;
    chapter += `| Factor | Value |\n`;
    chapter += `|--------|-------|\n`;

    if (weather.season_quarter) {
      chapter += `| **Season/Quarter** | ${weather.season_quarter} |\n`;
    }
    if (weather.temperature_range_c) {
      const tempRange = `${weather.temperature_range_c.min}°C to ${weather.temperature_range_c.max}°C`;
      chapter += `| **Temperature Range** | ${tempRange} |\n`;
    }
    if (weather.terrain_type) {
      chapter += `| **Terrain Type** | ${weather.terrain_type} |\n`;
    }
    if (weather.storm_frequency_days !== undefined) {
      chapter += `| **Storm Frequency** | ${weather.storm_frequency_days} days/month |\n`;
    }
    if (weather.daylight_hours) {
      chapter += `| **Daylight Hours** | ${weather.daylight_hours} hours/day |\n`;
    }

    chapter += `\n`;

    if (weather.environmental_impact) {
      chapter += `**Environmental Impact:** ${weather.environmental_impact}\n\n`;
    }
    if (weather.tactical_considerations) {
      chapter += `**Tactical Considerations:** ${weather.tactical_considerations}\n\n`;
    }
  }

  // Section 12: Tactical Doctrine & Capabilities
  chapter += `## Tactical Doctrine & Capabilities\n\n`;
  if (data.tactical_doctrine || data.combat_effectiveness) {
    if (data.tactical_doctrine?.role) {
      chapter += `**Primary Role:** ${data.tactical_doctrine.role}\n\n`;
    }

    if (data.combat_effectiveness?.strengths || data.tactical_doctrine?.special_capabilities) {
      chapter += `### Strengths\n\n`;
      const strengths = data.combat_effectiveness?.strengths || data.tactical_doctrine?.special_capabilities || [];
      strengths.forEach(s => {
        chapter += `- ${s}\n`;
      });
      chapter += `\n`;
    }

    if (data.combat_effectiveness?.weaknesses || data.tactical_doctrine?.known_issues) {
      chapter += `### Weaknesses\n\n`;
      const weaknesses = data.combat_effectiveness?.weaknesses || data.tactical_doctrine?.known_issues || [];
      weaknesses.forEach(w => {
        chapter += `- ${w}\n`;
      });
      chapter += `\n`;
    }

    if (data.tactical_doctrine?.desert_adaptations) {
      chapter += `**Desert Adaptations:** ${data.tactical_doctrine.desert_adaptations}\n\n`;
    }
  }

  // Section 13: Critical Equipment Shortages
  chapter += `## Critical Equipment Shortages\n\n`;

  // Analyze shortages from data
  let priority1 = [];
  let priority2 = [];
  let priority3 = [];

  if (data.actual_percentage && data.actual_percentage < 80) {
    priority1.push(`Personnel deficit: ${100 - data.actual_percentage}% below authorized strength`);
  }

  if (data.ground_vehicles && data.ground_vehicles.trucks && data.trucks?.operational) {
    const truckReadiness = calculateReadiness(data.trucks.operational, data.trucks.total);
    if (truckReadiness < 75) {
      priority2.push(`Transport: Only ${truckReadiness}% of trucks operational`);
    }
  }

  // Parse from combat_effectiveness weaknesses or tactical_doctrine known_issues
  if (data.combat_effectiveness?.weaknesses) {
    data.combat_effectiveness.weaknesses.forEach(w => {
      if (w.toLowerCase().includes('artillery') || w.toLowerCase().includes('no organic')) {
        priority1.push(w);
      } else if (w.toLowerCase().includes('anti-tank') || w.toLowerCase().includes('ammunition')) {
        priority2.push(w);
      } else if (w.toLowerCase().includes('spare parts') || w.toLowerCase().includes('maintenance')) {
        priority3.push(w);
      }
    });
  }

  if (priority1.length > 0) {
    chapter += `### Priority 1 (Critical)\n\n`;
    priority1.forEach(p => chapter += `- ${p}\n`);
    chapter += `\n`;
  }

  if (priority2.length > 0) {
    chapter += `### Priority 2 (High)\n\n`;
    priority2.forEach(p => chapter += `- ${p}\n`);
    chapter += `\n`;
  }

  if (priority3.length > 0) {
    chapter += `### Priority 3 (Medium)\n\n`;
    priority3.forEach(p => chapter += `- ${p}\n`);
    chapter += `\n`;
  }

  if (priority1.length === 0 && priority2.length === 0 && priority3.length === 0) {
    chapter += `No critical equipment shortages identified for this quarter.\n\n`;
  }

  // Section 14: Historical Context
  chapter += `## Historical Context\n\n`;

  // Major engagements
  if (data.operational_history?.major_engagements_this_quarter && data.operational_history.major_engagements_this_quarter.length > 0) {
    chapter += `### Major Operations (Q2 1941)\n\n`;
    data.operational_history.major_engagements_this_quarter.forEach(eng => {
      chapter += `**${eng.engagement_name}** (${eng.date_start} to ${eng.date_end})\n`;
      chapter += `- Role: ${eng.role}\n`;
      chapter += `- Outcome: ${eng.outcome}\n`;
      if (eng.casualties) {
        chapter += `- Casualties: ${eng.casualties}\n`;
      }
      if (eng.notes) {
        chapter += `- ${eng.notes}\n`;
      }
      chapter += `\n`;
    });
  }

  // Operation Battleaxe details (from different structure)
  if (data.operational_history?.operation_battleaxe) {
    chapter += `### Operation Battleaxe\n\n`;
    const battleaxe = data.operational_history.operation_battleaxe;
    if (battleaxe.dates) chapter += `**Dates:** ${battleaxe.dates}\n\n`;
    if (battleaxe.objective) chapter += `**Objective:** ${battleaxe.objective}\n\n`;
    if (battleaxe.participation) chapter += `**Participation:** ${battleaxe.participation}\n\n`;
    if (battleaxe.outcome) chapter += `**Outcome:** ${battleaxe.outcome}\n\n`;
    if (battleaxe.losses) chapter += `**Losses:** ${battleaxe.losses}\n\n`;
    if (battleaxe.lessons) chapter += `**Lessons Learned:** ${battleaxe.lessons}\n\n`;
  }

  // 1940 operations
  if (data.operational_history?.['1940_operations']) {
    const ops1940 = data.operational_history['1940_operations'];
    if (ops1940.operation_compass || ops1940.battles) {
      chapter += `### 1940-1941 Background\n\n`;
      if (ops1940.operation_compass) chapter += `${ops1940.operation_compass}\n\n`;
      if (ops1940.battles) chapter += `**Key Battles:** ${ops1940.battles}\n\n`;
      if (ops1940.achievements) chapter += `**Achievements:** ${ops1940.achievements}\n\n`;
    }
  }

  // Q2 status
  if (data.operational_history?.['1941_q2_status']) {
    const q2 = data.operational_history['1941_q2_status'];
    chapter += `### Q2 1941 Status\n\n`;
    Object.entries(q2).forEach(([key, value]) => {
      const title = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      chapter += `**${title}:** ${value}\n\n`;
    });
  }

  // Historical engagements list
  if (data.wargaming_data?.historical_engagements && data.wargaming_data.historical_engagements.length > 0) {
    chapter += `### Historical Engagements\n\n`;
    data.wargaming_data.historical_engagements.forEach(eng => {
      chapter += `- ${eng}\n`;
    });
    chapter += `\n`;
  }

  // Strategic situation
  if (data.historical_context?.strategic_situation) {
    chapter += `### Strategic Situation\n\n${data.historical_context.strategic_situation}\n\n`;
  }

  // Section 15: Wargaming Data
  chapter += `## Wargaming Data\n\n`;
  if (data.wargaming_data) {
    chapter += `| Attribute | Value |\n`;
    chapter += `|-----------|-------|\n`;
    chapter += `| **Morale** | ${data.wargaming_data.morale_rating || 'Unknown'}/10 |\n`;
    chapter += `| **Experience** | ${data.wargaming_data.experience_level || 'Unknown'} |\n`;
    chapter += `\n`;

    if (data.wargaming_data.special_rules) {
      chapter += `### Special Rules\n\n`;
      data.wargaming_data.special_rules.forEach(rule => {
        chapter += `- ${rule}\n`;
      });
      chapter += `\n`;
    }

    if (data.wargaming_data.scenario_suitability) {
      chapter += `### Scenario Suitability\n\n`;
      data.wargaming_data.scenario_suitability.forEach(scenario => {
        chapter += `- ${scenario}\n`;
      });
      chapter += `\n`;
    }
  }

  // Section 16: Data Quality & Known Gaps
  chapter += `## Data Quality & Known Gaps\n\n`;
  if (data.data_quality || data.validation) {
    const quality = data.data_quality || data.validation;

    chapter += `**Overall Confidence:** ${quality.confidence || quality.confidence_score}%\n\n`;

    if (quality.primary_sources || quality.source) {
      chapter += `### Primary Sources\n\n`;
      const sources = quality.primary_sources || quality.source || [];
      sources.forEach(src => {
        chapter += `- ${src}\n`;
      });
      chapter += `\n`;
    }

    if (quality.data_gaps || quality.known_gaps) {
      chapter += `### Known Data Gaps\n\n`;
      const gaps = quality.data_gaps || quality.known_gaps || [];
      gaps.forEach(gap => {
        chapter += `- ${gap}\n`;
      });
      chapter += `\n`;
    }

    if (quality.source_tier) {
      chapter += `**Source Tier:** ${quality.source_tier}\n\n`;
    }
  }

  // Section 17: Conclusion
  chapter += `## Conclusion\n\n`;
  if (data.combat_effectiveness?.notes) {
    chapter += `${data.combat_effectiveness.notes}\n\n`;
  } else if (data.operational_history?.quarterly_assessment) {
    // Use first 200 chars of quarterly assessment as conclusion
    const assessment = data.operational_history.quarterly_assessment;
    chapter += `${assessment.substring(0, 200)}...\n\n`;
  }

  // Footer
  chapter += `---\n\n`;
  chapter += `*Data compiled from historical records for 1941-Q2 North Africa Campaign*\n\n`;
  chapter += `**Primary Sources:**\n`;
  if (data.data_quality?.primary_sources || data.validation?.source) {
    const sources = data.data_quality?.primary_sources || data.validation?.source || [];
    sources.slice(0, 3).forEach(src => {
      chapter += `- ${src}\n`;
    });
  }

  return chapter;
}

/**
 * Main execution
 */
function main() {
  console.log('MDBook Chapter Generator - 1941-Q2 North Africa Campaign');
  console.log('='.repeat(60));

  let generatedCount = 0;
  let errorCount = 0;

  UNITS.forEach(unit => {
    try {
      console.log(`\nGenerating: ${unit.chapter} (${unit.nation})`);

      // Create output directory if it doesn't exist
      const outputDir = path.join(CONFIG.outputBaseDir, unit.nation);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
        console.log(`  Created directory: ${outputDir}`);
      }

      // Generate chapter
      const chapter = generateChapter(unit);

      // Write to file
      const outputPath = path.join(outputDir, unit.chapter);
      fs.writeFileSync(outputPath, chapter, 'utf8');

      console.log(`  ✓ Generated: ${outputPath}`);
      generatedCount++;

    } catch (error) {
      console.error(`  ✗ Error generating ${unit.chapter}: ${error.message}`);
      errorCount++;
    }
  });

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log(`\nGeneration Complete!`);
  console.log(`  Successfully generated: ${generatedCount}/18 chapters`);
  console.log(`  Errors: ${errorCount}`);

  if (generatedCount === 18) {
    console.log(`\n✓ All 18 chapters generated successfully!`);
    console.log(`\nOutput locations:`);
    console.log(`  - British: ${path.join(CONFIG.outputBaseDir, 'british')}`);
    console.log(`  - German: ${path.join(CONFIG.outputBaseDir, 'german')}`);
    console.log(`  - Italian: ${path.join(CONFIG.outputBaseDir, 'italian')}`);
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = { generateChapter };
