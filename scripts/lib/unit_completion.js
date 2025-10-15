#!/usr/bin/env node

/**
 * Atomic Unit Completion Handler
 *
 * When a unit JSON is saved, IMMEDIATELY generate its MDBook chapter.
 * This ensures unit+chapter are always created together atomically.
 *
 * Usage:
 *   const { completeUnit } = require('./scripts/lib/unit_completion');
 *   await completeUnit(unitData, nation, quarter, designation);
 *
 * This will:
 * 1. Save unit JSON to canonical location
 * 2. Generate MDBook chapter from that JSON
 * 3. Save chapter to canonical location
 * 4. Update WORKFLOW_STATE.json
 * 5. Return paths to both files
 */

const fs = require('fs').promises;
const path = require('path');
const paths = require('./canonical_paths');
const naming = require('./naming_standard');

/**
 * Complete a unit: Save JSON + Generate Chapter atomically
 *
 * @param {object} unitData - Complete unit JSON (validated against schema)
 * @param {string} nation - Nation (german, italian, british, american, french)
 * @param {string} quarter - Quarter (1941q2, 1942q3, etc)
 * @param {string} designation - Unit designation (15_panzer_division, xx_corpo, etc)
 * @returns {object} {unitPath, chapterPath, updated: true/false}
 */
async function completeUnit(unitData, nation, quarter, designation) {
  console.log(`\n📦 Completing unit: ${nation} ${designation} (${quarter})`);

  // Ensure canonical directories exist
  await paths.ensureCanonicalDirectoriesExist();

  // 1. Save unit JSON to canonical location
  const unitPath = paths.getUnitPath(nation, quarter, designation);
  await fs.writeFile(unitPath, JSON.stringify(unitData, null, 2));
  console.log(`   ✅ Unit JSON: ${path.basename(unitPath)}`);

  // 2. Generate MDBook chapter from the JSON
  const chapterContent = generateChapterFromData(unitData);
  const chapterPath = paths.getChapterPath(nation, quarter, designation);
  await fs.writeFile(chapterPath, chapterContent);
  console.log(`   ✅ Chapter:    ${path.basename(chapterPath)}`);

  // 3. Update WORKFLOW_STATE.json
  const updated = await updateWorkflowState(nation, quarter, designation);

  console.log(`   🎯 Unit completion: ${updated ? 'NEW' : 'UPDATED'}`);

  return {
    unitPath,
    chapterPath,
    updated  // true if new, false if re-extraction
  };
}

/**
 * Generate MDBook chapter from unit data
 *
 * @param {object} data - Unit JSON data
 * @returns {string} Markdown chapter content
 */
function generateChapterFromData(data) {
  const lines = [];

  // Header
  lines.push(`# ${data.unit_designation}`);
  lines.push('');
  lines.push(`**Nation:** ${capitalizeNation(data.nation)}`);
  lines.push(`**Period:** ${data.quarter}`);
  lines.push(`**Type:** ${data.unit_type || 'N/A'}`);
  lines.push('');

  // Section 1: Overview
  lines.push('## 1. Overview');
  lines.push('');
  if (data.parent_formation) {
    lines.push(`**Parent Formation:** ${data.parent_formation}`);
    lines.push('');
  }
  if (data.unit_history) {
    lines.push(data.unit_history);
    lines.push('');
  }

  // Section 2: Command Structure
  lines.push('## 2. Command Structure');
  lines.push('');
  if (data.command && data.command.commander) {
    const cmd = data.command.commander;
    lines.push(`**Commander:** ${cmd.name || 'Unknown'}`);
    if (cmd.rank) lines.push(`**Rank:** ${cmd.rank}`);
    if (cmd.appointment_date) lines.push(`**Appointed:** ${cmd.appointment_date}`);
    if (cmd.relief_date) lines.push(`**Relieved:** ${cmd.relief_date}`);
    lines.push('');
  }
  if (data.command && data.command.staff_strength) {
    const staff = data.command.staff_strength;
    lines.push('**Staff Strength:**');
    lines.push('');
    lines.push('| Category | Count |');
    lines.push('|----------|-------|');
    if (staff.officers !== undefined) lines.push(`| Officers | ${staff.officers} |`);
    if (staff.ncos !== undefined) lines.push(`| NCOs | ${staff.ncos} |`);
    if (staff.enlisted !== undefined) lines.push(`| Enlisted | ${staff.enlisted} |`);
    if (staff.total !== undefined) lines.push(`| **Total** | **${staff.total}** |`);
    lines.push('');
    if (staff.note) {
      lines.push(`*${staff.note}*`);
      lines.push('');
    }
  }

  // Section 3: Personnel Summary
  lines.push('## 3. Personnel Summary');
  lines.push('');
  if (data.total_personnel !== undefined) {
    lines.push(`**Total Personnel:** ${data.total_personnel.toLocaleString()}`);
    lines.push('');
  }
  if (data.personnel_breakdown) {
    const pb = data.personnel_breakdown;
    lines.push('| Category | Count |');
    lines.push('|----------|-------|');
    if (pb.officers !== undefined) lines.push(`| Officers | ${pb.officers.toLocaleString()} |`);
    if (pb.ncos !== undefined) lines.push(`| NCOs | ${pb.ncos.toLocaleString()} |`);
    if (pb.enlisted !== undefined) lines.push(`| Enlisted | ${pb.enlisted.toLocaleString()} |`);
    lines.push('');
  }

  // Section 4: Tanks & Armored Vehicles
  if (data.tanks && data.tanks.total > 0) {
    lines.push('## 4. Tanks & Armored Vehicles');
    lines.push('');
    lines.push('| Type | Count |');
    lines.push('|------|-------|');
    if (data.tanks.heavy) lines.push(`| Heavy Tanks | ${data.tanks.heavy} |`);
    if (data.tanks.medium) lines.push(`| Medium Tanks | ${data.tanks.medium} |`);
    if (data.tanks.light) lines.push(`| Light Tanks | ${data.tanks.light} |`);
    if (data.tanks.other) lines.push(`| Other AFVs | ${data.tanks.other} |`);
    lines.push(`| **Total** | **${data.tanks.total}** |`);
    lines.push('');

    if (data.tanks.by_model && data.tanks.by_model.length > 0) {
      lines.push('### Tank Models:');
      lines.push('');
      data.tanks.by_model.forEach(model => {
        lines.push(`- **${model.model}**: ${model.quantity} units`);
      });
      lines.push('');
    }
  }

  // Section 5: Artillery
  if (data.artillery_total !== undefined && data.artillery_total > 0) {
    lines.push('## 5. Artillery');
    lines.push('');
    lines.push('| Type | Count |');
    lines.push('|------|-------|');
    if (data.field_artillery) lines.push(`| Field Artillery | ${data.field_artillery} |`);
    if (data.anti_tank) lines.push(`| Anti-Tank | ${data.anti_tank} |`);
    if (data.anti_aircraft) lines.push(`| Anti-Aircraft | ${data.anti_aircraft} |`);
    if (data.mortars) lines.push(`| Mortars | ${data.mortars} |`);
    lines.push(`| **Total** | **${data.artillery_total}** |`);
    lines.push('');
  }

  // Section 6: Ground Vehicles
  if (data.ground_vehicles_total !== undefined && data.ground_vehicles_total > 0) {
    lines.push('## 6. Ground Vehicles');
    lines.push('');
    lines.push(`**Total Ground Vehicles:** ${data.ground_vehicles_total.toLocaleString()}`);
    lines.push('');

    if (data.trucks || data.cars || data.motorcycles) {
      lines.push('| Type | Count |');
      lines.push('|------|-------|');
      if (data.trucks) lines.push(`| Trucks | ${data.trucks} |`);
      if (data.cars) lines.push(`| Cars | ${data.cars} |`);
      if (data.motorcycles) lines.push(`| Motorcycles | ${data.motorcycles} |`);
      lines.push('');
    }
  }

  // Section 7: Subordinate Units
  if (data.subordinate_units && data.subordinate_units.length > 0) {
    lines.push('## 7. Subordinate Units');
    lines.push('');
    data.subordinate_units.forEach(sub => {
      lines.push(`- **${sub.unit_designation}**`);
      if (sub.unit_type) lines.push(`  - Type: ${sub.unit_type}`);
      if (sub.note) lines.push(`  - Note: ${sub.note}`);
    });
    lines.push('');
  }

  // Section 8: Validation & Sources
  lines.push('## 8. Data Quality');
  lines.push('');
  if (data.validation) {
    const val = data.validation;
    lines.push(`**Confidence:** ${val.confidence}%`);
    if (val.aggregation_status) {
      lines.push(`**Aggregation Status:** ${val.aggregation_status}`);
    }
    lines.push('');

    if (val.sources && val.sources.length > 0) {
      lines.push('**Sources:**');
      lines.push('');
      val.sources.forEach(source => {
        lines.push(`- ${source}`);
      });
      lines.push('');
    }

    if (val.notes && val.notes.length > 0) {
      lines.push('**Notes:**');
      lines.push('');
      val.notes.forEach(note => {
        lines.push(`- ${note}`);
      });
      lines.push('');
    }
  }

  // Footer
  lines.push('---');
  lines.push('');
  lines.push('*Generated automatically from validated TO&E data*');
  lines.push('');

  return lines.join('\n');
}

/**
 * Update WORKFLOW_STATE.json with completed unit
 *
 * @param {string} nation
 * @param {string} quarter
 * @param {string} designation
 * @returns {boolean} true if new unit, false if updated existing
 */
async function updateWorkflowState(nation, quarter, designation) {
  const workflowPath = path.join(__dirname, '../../WORKFLOW_STATE.json');

  try {
    const data = await fs.readFile(workflowPath, 'utf-8');
    const workflow = JSON.parse(data);

    const unitId = `${nation}_${quarter}_${designation}`;

    // Check if already completed
    const isNew = !workflow.completed.includes(unitId);

    if (isNew) {
      workflow.completed.push(unitId);
      workflow.completed.sort();

      // Update counts
      workflow.completed_count = workflow.completed.length;
      workflow.progress_percent = Math.round(
        (workflow.completed_count / workflow.total_units) * 100
      );
      workflow.last_updated = new Date().toISOString();

      await fs.writeFile(workflowPath, JSON.stringify(workflow, null, 2));
    }

    return isNew;
  } catch (error) {
    console.warn(`   ⚠️  Could not update WORKFLOW_STATE.json: ${error.message}`);
    return false;
  }
}

/**
 * Capitalize nation name for display
 */
function capitalizeNation(nation) {
  const map = {
    'german': 'Germany',
    'italian': 'Italy',
    'british': 'Britain (Commonwealth)',
    'american': 'United States',
    'french': 'France (Free French)'
  };
  return map[nation] || nation;
}

module.exports = {
  completeUnit,
  generateChapterFromData
};

if (require.main === module) {
  console.log('Atomic Unit Completion Handler');
  console.log('Usage: const { completeUnit } = require("./unit_completion");');
  console.log('       await completeUnit(unitData, nation, quarter, designation);');
}
