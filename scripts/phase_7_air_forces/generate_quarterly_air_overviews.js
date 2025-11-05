#!/usr/bin/env node

/**
 * Generate quarterly theater-wide air forces overview chapters
 *
 * Creates multi-nation air strength comparison chapters for each quarter
 */

const fs = require('fs');
const path = require('path');

const airSummariesDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');
const chaptersDir = path.join(__dirname, '..', 'data', 'output', 'chapters');

// Read all air summary files
const summaryFiles = fs.readdirSync(airSummariesDir).filter(f => f.endsWith('.json'));

// Group by quarter
const quarterGroups = {};

summaryFiles.forEach(file => {
  const data = JSON.parse(fs.readFileSync(path.join(airSummariesDir, file), 'utf8'));
  const quarter = data.quarter;
  const nation = data.nation;

  if (!quarterGroups[quarter]) {
    quarterGroups[quarter] = {};
  }

  quarterGroups[quarter][nation] = data;
});

/**
 * Format numbers with commas
 */
function formatNumber(num) {
  return num ? num.toLocaleString('en-US') : '0';
}

/**
 * Generate theater overview chapter for a quarter
 */
function generateTheaterOverviewChapter(quarter, nationsData) {
  let chapter = '';

  // Header
  chapter += `# North Africa Air Forces - ${quarter.toUpperCase()}\n\n`;
  chapter += `**Theater:** North Africa\n`;
  chapter += `**Quarter:** ${quarter.toUpperCase()}\n`;
  chapter += `**Coverage:** ${Object.keys(nationsData).map(n => n.charAt(0).toUpperCase() + n.slice(1)).join(', ')}\n\n`;
  chapter += `---\n\n`;

  // Executive Summary
  chapter += `## Executive Summary\n\n`;

  let totalAircraft = 0;
  let totalOperational = 0;
  let totalUnits = 0;

  Object.values(nationsData).forEach(data => {
    totalAircraft += data.aggregate_strength.total_aircraft || 0;
    totalOperational += data.aggregate_strength.operational_aircraft || 0;
    totalUnits += data.aggregate_strength.by_unit?.length || 0;
  });

  chapter += `Quarterly snapshot of air forces operating in the North African theater as of ${quarter}.\n\n`;
  chapter += `**Theater-Wide Totals:**\n`;
  chapter += `- ${formatNumber(totalAircraft)} total aircraft\n`;
  chapter += `- ${formatNumber(totalOperational)} operational aircraft\n`;
  chapter += `- ${totalUnits} operational squadrons/gruppi\n\n`;

  // Axis vs Allies breakdown
  const axisNations = ['german', 'italian'];
  const alliedNations = ['british', 'american'];

  const axisTotal = Object.entries(nationsData)
    .filter(([nation]) => axisNations.includes(nation))
    .reduce((sum, [, data]) => sum + (data.aggregate_strength.total_aircraft || 0), 0);

  const alliedTotal = Object.entries(nationsData)
    .filter(([nation]) => alliedNations.includes(nation))
    .reduce((sum, [, data]) => sum + (data.aggregate_strength.total_aircraft || 0), 0);

  if (axisTotal > 0 && alliedTotal > 0) {
    chapter += `### Force Balance\n\n`;
    chapter += `| Side | Total Aircraft | Percentage |\n`;
    chapter += `|------|----------------|------------|\n`;
    chapter += `| **Axis** | ${formatNumber(axisTotal)} | ${Math.round((axisTotal/(axisTotal+alliedTotal))*100)}% |\n`;
    chapter += `| **Allies** | ${formatNumber(alliedTotal)} | ${Math.round((alliedTotal/(axisTotal+alliedTotal))*100)}% |\n\n`;
  }

  // Nation-by-Nation Breakdown
  chapter += `## Air Forces by Nation\n\n`;

  // Sort nations: German, Italian, British, American
  const nationOrder = ['german', 'italian', 'british', 'american'];
  const sortedNations = Object.keys(nationsData).sort((a, b) => {
    return nationOrder.indexOf(a) - nationOrder.indexOf(b);
  });

  sortedNations.forEach(nation => {
    const data = nationsData[nation];

    chapter += `### ${nation.charAt(0).toUpperCase() + nation.slice(1)} Air Forces\n\n`;

    // Command
    chapter += `**Command:** ${data.air_command_structure.theater_command.designation}\n`;
    if (data.air_command_structure.theater_command.commander !== 'Unknown') {
      chapter += `**Commander:** ${data.air_command_structure.theater_command.commander}\n`;
    }
    chapter += `**Headquarters:** ${data.air_command_structure.theater_command.headquarters}\n\n`;

    // Strength
    chapter += `**Aggregate Strength:**\n`;
    chapter += `- Total Aircraft: ${formatNumber(data.aggregate_strength.total_aircraft)}\n`;
    chapter += `- Operational: ${formatNumber(data.aggregate_strength.operational_aircraft)}\n`;

    if (data.aggregate_strength.serviceability_rate) {
      chapter += `- Serviceability: ${data.aggregate_strength.serviceability_rate}\n`;
    }

    const unitCount = data.aggregate_strength.by_unit?.length || 0;
    chapter += `- Units: ${unitCount} squadrons/gruppi\n\n`;

    // Key aircraft types (top 6)
    if (data.aggregate_strength.by_unit && data.aggregate_strength.by_unit.length > 0) {
      const typesSet = new Set();
      data.aggregate_strength.by_unit.forEach(unit => {
        unit.aircraft_types?.forEach(type => typesSet.add(type));
      });
      const types = Array.from(typesSet).slice(0, 6);

      if (types.length > 0) {
        chapter += `**Key Aircraft Types:** ${types.join(', ')}\n\n`;
      }
    } else if (data.aggregate_strength.aircraft_types) {
      // Italian format
      const types = data.aggregate_strength.aircraft_types;
      const allTypes = [
        ...(types.fighters || []).slice(0, 3),
        ...(types.bombers || []).slice(0, 2)
      ];
      if (allTypes.length > 0) {
        chapter += `**Key Aircraft Types:** ${allTypes.join(', ')}\n\n`;
      }
    }

    // Data source
    chapter += `**Source:** ${data.source_document.title} (${data.source_document.date})\n`;
    chapter += `**Confidence:** ${data.metadata.confidence}% (${data.metadata.tier})\n\n`;

    // Optional: Top bases
    if (data.aggregate_strength.by_unit && data.aggregate_strength.by_unit.length > 0) {
      const bases = new Set();
      data.aggregate_strength.by_unit.forEach(unit => {
        if (unit.base) bases.add(unit.base);
      });

      if (bases.size > 0 && bases.size <= 10) {
        chapter += `**Operating Bases:** ${Array.from(bases).join(', ')}\n\n`;
      } else if (bases.size > 10) {
        chapter += `**Operating Bases:** ${bases.size} different airbases\n\n`;
      }
    }

    chapter += `---\n\n`;
  });

  // Detailed Unit Lists
  chapter += `## Detailed Unit Lists\n\n`;

  sortedNations.forEach(nation => {
    const data = nationsData[nation];

    chapter += `### ${nation.charAt(0).toUpperCase() + nation.slice(1)} Units\n\n`;

    if (data.aggregate_strength.by_unit && data.aggregate_strength.by_unit.length > 0) {
      chapter += `| Unit | Base | Aircraft Type | Estimated Strength |\n`;
      chapter += `|------|------|---------------|--------------------|\n`;

      data.aggregate_strength.by_unit.forEach(unit => {
        const designation = unit.designation || 'Unknown';
        const base = unit.base || '-';
        const aircraftTypes = unit.aircraft_types?.join(', ') || '-';
        const strength = unit.estimated_strength || unit.total || '-';

        chapter += `| ${designation} | ${base} | ${aircraftTypes} | ${strength} |\n`;
      });

      chapter += '\n';
    } else if (data.aggregate_strength.known_units) {
      // Italian format
      chapter += `| Unit | Base | Aircraft Type | Estimated Strength |\n`;
      chapter += `|------|------|---------------|--------------------|\n`;

      data.aggregate_strength.known_units.forEach(unit => {
        const aircraftType = unit.aircraft_type || unit.aircraft_types?.join(', ') || '-';
        chapter += `| ${unit.unit} | ${unit.base} | ${aircraftType} | ${unit.estimated_strength} |\n`;
      });

      chapter += '\n';
    } else {
      chapter += `*Detailed unit breakdown not available*\n\n`;
    }
  });

  // Data Quality Notes
  chapter += `## Data Quality & Sources\n\n`;

  sortedNations.forEach(nation => {
    const data = nationsData[nation];
    chapter += `**${nation.charAt(0).toUpperCase() + nation.slice(1)}:** `;
    chapter += `${data.metadata.extraction_method}. `;
    chapter += `Confidence: ${data.metadata.confidence}% (${data.metadata.tier}).\n\n`;
  });

  chapter += `### Notes\n\n`;
  chapter += `- Strength data represents theater-wide aggregates where available\n`;
  chapter += `- Unit-level strength estimated using standard national establishments where exact data unavailable\n`;
  chapter += `- British data includes RAF, RAAF, SAAF, and other Commonwealth squadrons\n`;
  chapter += `- Italian gruppi typically 27 aircraft, stormi 54 aircraft (2 gruppi)\n`;
  chapter += `- RAF squadrons typically 16 aircraft establishment\n\n`;

  // Footer
  chapter += `---\n\n`;
  chapter += `*Generated from quarterly air summaries*\n`;

  return chapter;
}

console.log('Generating quarterly theater air overview chapters...\n');

let generatedCount = 0;

Object.entries(quarterGroups).forEach(([quarter, nationsData]) => {
  const chapterContent = generateTheaterOverviewChapter(quarter, nationsData);
  const filename = `chapter_air_overview_${quarter}.md`;
  const filepath = path.join(chaptersDir, filename);

  fs.writeFileSync(filepath, chapterContent, 'utf8');

  console.log(`✓ ${filename}`);
  console.log(`  - Quarter: ${quarter.toUpperCase()}`);
  console.log(`  - Nations: ${Object.keys(nationsData).join(', ')}`);

  const totalAircraft = Object.values(nationsData).reduce((sum, d) =>
    sum + (d.aggregate_strength.total_aircraft || 0), 0);
  console.log(`  - Total aircraft: ${totalAircraft}`);
  console.log();

  generatedCount++;
});

console.log('='.repeat(60));
console.log(`✓ Generated ${generatedCount} quarterly overview chapters`);
console.log('='.repeat(60));
