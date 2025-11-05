#!/usr/bin/env node

/**
 * Add Air Support sections to existing MDBook chapters
 *
 * Inserts air support sections after "Organizational Structure" section
 */

const fs = require('fs');
const path = require('path');

const unitsDir = path.join(__dirname, '..', 'data', 'output', 'units');
const chaptersDir = path.join(__dirname, '..', 'data', 'output', 'chapters');

// Mappings: Unit JSON → Chapter Markdown
const integrations = [
  {
    unitJson: 'british_1942q2_eighth_army_8th_army_toe.json',
    chapterMd: 'chapter_british_1942q2_eighth_army_8th_army.md'
  },
  {
    unitJson: 'british_1942q3_eighth_army_8th_army_toe.json',
    chapterMd: 'chapter_british_1942q3_eighth_army_8th_army.md'
  },
  {
    unitJson: 'german_1942q2_panzerarmee_afrika_toe.json',
    chapterMd: 'chapter_german_1942q2_panzerarmee_afrika.md'
  },
  {
    unitJson: 'italian_1942q1_xxi_corpo_d_armata_xxi_corps_toe.json',
    chapterMd: 'chapter_italian_1942q1_xxi_corpo_d_armata_xxi_corps.md'
  },
  {
    unitJson: 'italian_1942q2_xxi_corpo_d_armata_xxi_corps_toe.json',
    chapterMd: 'chapter_italian_1942q2_xxi_corpo_d_armata_xxi_corps.md'
  }
];

/**
 * Generate Air Support section markdown from unit data
 */
function generateAirSupportSection(airSupport) {
  let section = '## Air Support\n\n';

  // Overview
  section += `**Theater Air Command:** ${airSupport.theater_air_command.designation}\n`;
  section += `**Air Commander:** ${airSupport.theater_air_command.commander}\n`;
  section += `**Headquarters:** ${airSupport.theater_air_command.headquarters}\n\n`;

  // Strength summary
  section += '### Aggregate Strength\n\n';
  section += '| Metric | Value |\n';
  section += '|--------|-------|\n';
  section += `| **Total Aircraft** | ${airSupport.aggregate_strength.total_aircraft} |\n`;
  section += `| **Operational Aircraft** | ${airSupport.aggregate_strength.operational_aircraft} |\n`;
  section += `| **Serviceability Rate** | ${airSupport.aggregate_strength.serviceability_rate} |\n`;
  section += `| **Operational Units** | ${airSupport.aggregate_strength.unit_count} squadrons/gruppi |\n\n`;

  if (airSupport.aggregate_strength.note) {
    section += `*${airSupport.aggregate_strength.note}*\n\n`;
  }

  // Key aircraft types
  if (airSupport.key_aircraft_types && airSupport.key_aircraft_types.length > 0) {
    section += '### Key Aircraft Types\n\n';
    airSupport.key_aircraft_types.forEach(aircraft => {
      section += `- ${aircraft}\n`;
    });
    section += '\n';
  }

  // Organizational summary
  section += '### Organization\n\n';
  section += `${airSupport.organizational_summary}\n\n`;

  // Source information
  section += '### Data Source\n\n';
  section += `**Source Document:** ${airSupport.source.title}\n`;
  section += `**Date:** ${airSupport.source.date}\n`;
  section += `**Confidence:** ${airSupport.source.confidence}%\n`;
  section += `**Tier:** ${airSupport.source.tier}\n\n`;

  if (airSupport.integration_note) {
    section += `*${airSupport.integration_note}*\n\n`;
  }

  return section;
}

console.log('Adding Air Support sections to MDBook chapters...\n');

let successCount = 0;
let errorCount = 0;

integrations.forEach(integration => {
  try {
    // Read unit JSON to get air_support data
    const unitPath = path.join(unitsDir, integration.unitJson);
    const unitData = JSON.parse(fs.readFileSync(unitPath, 'utf8'));

    if (!unitData.air_support) {
      console.log(`⚠ ${integration.chapterMd} - No air_support data in unit JSON, skipping`);
      return;
    }

    // Read existing chapter
    const chapterPath = path.join(chaptersDir, integration.chapterMd);
    if (!fs.existsSync(chapterPath)) {
      console.log(`⚠ ${integration.chapterMd} - Chapter file not found, skipping`);
      return;
    }

    let chapterContent = fs.readFileSync(chapterPath, 'utf8');

    // Check if already has Air Support section
    if (chapterContent.includes('## Air Support')) {
      console.log(`ℹ ${integration.chapterMd} - Already has Air Support section, skipping`);
      return;
    }

    // Generate Air Support section
    const airSupportSection = generateAirSupportSection(unitData.air_support);

    // Find insertion point: after "## Organizational Structure" section
    // Look for the next ## heading after "Organizational Structure"
    const orgStructureIndex = chapterContent.indexOf('## Organizational Structure');

    if (orgStructureIndex === -1) {
      // Try alternate heading
      const altIndex = chapterContent.indexOf('## Organization');
      if (altIndex === -1) {
        console.log(`⚠ ${integration.chapterMd} - Could not find organization section, inserting before Supply Status`);
        // Insert before Supply Status as fallback
        const supplyIndex = chapterContent.indexOf('## Supply Status');
        if (supplyIndex !== -1) {
          chapterContent = chapterContent.slice(0, supplyIndex) +
                          airSupportSection +
                          chapterContent.slice(supplyIndex);
        } else {
          console.log(`✗ ${integration.chapterMd} - Could not find insertion point`);
          errorCount++;
          return;
        }
      } else {
        // Find next ## heading after Organization
        const nextHeadingIndex = chapterContent.indexOf('\n## ', altIndex + 15);
        if (nextHeadingIndex !== -1) {
          chapterContent = chapterContent.slice(0, nextHeadingIndex + 1) +
                          airSupportSection +
                          chapterContent.slice(nextHeadingIndex + 1);
        }
      }
    } else {
      // Find next ## heading after Organizational Structure
      const nextHeadingIndex = chapterContent.indexOf('\n## ', orgStructureIndex + 27);

      if (nextHeadingIndex !== -1) {
        // Insert before the next heading
        chapterContent = chapterContent.slice(0, nextHeadingIndex + 1) +
                        airSupportSection +
                        chapterContent.slice(nextHeadingIndex + 1);
      } else {
        // No next heading found, append to end
        chapterContent += '\n' + airSupportSection;
      }
    }

    // Write updated chapter
    fs.writeFileSync(chapterPath, chapterContent, 'utf8');

    console.log(`✓ ${integration.chapterMd}`);
    console.log(`  - Added Air Support section`);
    console.log(`  - Total aircraft: ${unitData.air_support.aggregate_strength.total_aircraft}`);
    console.log(`  - Units: ${unitData.air_support.aggregate_strength.unit_count}`);
    console.log();

    successCount++;

  } catch (error) {
    console.error(`✗ ${integration.chapterMd}: ${error.message}`);
    console.log();
    errorCount++;
  }
});

console.log('='.repeat(60));
console.log(`✓ Complete: ${successCount} chapters updated`);
if (errorCount > 0) {
  console.log(`✗ Errors: ${errorCount} chapters failed`);
}
console.log('='.repeat(60));
