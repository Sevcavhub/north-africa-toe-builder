#!/usr/bin/env node
/**
 * Hermann Göring Style TO&E Diagram Generator
 *
 * Reads unit JSON files and generates SVG diagrams matching the
 * Hermann Göring Division reference style:
 * - Left-edge vertical lines with short horizontal stubs
 * - Organizational boxes on left, equipment silhouettes on right
 * - Clean, professional military document aesthetic
 *
 * Usage:
 *   node scripts/generate_toe_diagram.js <unit_json_file>
 *   node scripts/generate_toe_diagram.js data/output/units/german_1941q2_15_panzer_division_toe.json
 */

const fs = require('fs');
const path = require('path');

// Hermann Göring Layout Configuration
const LAYOUT = {
  // Canvas
  width: 1600,
  height: 1350,

  // Left column (organizational hierarchy)
  leftColumn: {
    x: 20,
    width: 250,
    boxHeight: 35,
    smallBoxWidth: 160,
  },

  // Spacing
  spacing: {
    regiment: 65,      // Space between major units
    battalion: 60,     // Space between battalions
    company: 60,       // Space between companies
  },

  // Connection lines (Hermann Göring style)
  lines: {
    leftEdgeX: 25,     // X position of vertical line on left
    stubLength: 5,     // Length of horizontal stubs
    strokeWidth: 1,
  },

  // Equipment column (right side)
  equipment: {
    startX: 270,       // Start of equipment column
    imageGap: 10,      // Gap between connection line and first image
    imageSpacing: 70,  // Space between images horizontally
  },

  // Image sizes
  images: {
    regiment: { width: 55, height: 28 },
    company: { width: 45, height: 23 },
  },

  // Typography
  fonts: {
    title: { size: 16, weight: 'bold' },
    subtitle: { size: 11, weight: 'normal' },
    unitName: { size: 10, weight: 'normal' },
    commander: { size: 8, weight: 'normal', style: 'italic' },
    equipment: { size: 9, weight: 'normal' },
  }
};

/**
 * Generate complete SVG diagram from unit JSON
 */
function generateDiagram(unitJson, options = {}) {
  const silhouettePath = options.silhouettePath || 'silhouettes';

  let svg = [];
  svg.push(`<?xml version="1.0" encoding="UTF-8"?>`);
  svg.push(`<svg width="${LAYOUT.width}" height="${LAYOUT.height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">`);
  svg.push('');

  // Title section
  let currentY = 20;
  svg.push(generateTitle(unitJson, currentY));
  currentY += 90;

  // Division overview (if present)
  if (unitJson.division_overview) {
    svg.push(generateDivisionOverview(unitJson.division_overview, currentY, silhouettePath));
    currentY += 300;
  }

  // Section divider
  svg.push(`  <line x1="20" y1="${currentY}" x2="${LAYOUT.width - 20}" y2="${currentY}" stroke="black" stroke-width="2"/>`);
  currentY += 30;

  // Detailed regiment breakout
  if (unitJson.regiments && unitJson.regiments.length > 0) {
    svg.push(generateRegimentDetail(unitJson.regiments[0], currentY, silhouettePath));
  }

  // Footer notes
  svg.push('');
  svg.push('  <!-- ==================== FOOTER NOTES ==================== -->');
  svg.push('');
  svg.push(generateFooter());

  svg.push('</svg>');

  return svg.join('\n');
}

/**
 * Generate title section
 */
function generateTitle(unitJson, startY) {
  const title = unitJson.unit_designation || unitJson.name || 'Unknown Unit';
  const subtitle = `${unitJson.quarter || ''} - ${unitJson.total_tanks || 0} tanks total`;
  const commander = unitJson.commander_name || '';

  let svg = [];
  svg.push('  <!-- ==================== TITLE ==================== -->');
  svg.push('');
  svg.push(`  <rect x="20" y="${startY}" width="400" height="50" fill="white" stroke="black" stroke-width="2"/>`);
  svg.push(`  <text x="220" y="${startY + 25}" font-family="Arial" font-size="${LAYOUT.fonts.title.size}" font-weight="${LAYOUT.fonts.title.weight}" text-anchor="middle">${title}</text>`);
  svg.push(`  <text x="220" y="${startY + 42}" font-family="Arial" font-size="${LAYOUT.fonts.subtitle.size}" text-anchor="middle">${subtitle}</text>`);

  if (commander) {
    svg.push('');
    svg.push(`  <text x="220" y="${startY + 60}" font-family="Arial" font-size="${LAYOUT.fonts.commander.size}" font-style="${LAYOUT.fonts.commander.style}" text-anchor="middle">${commander}</text>`);
  }

  return svg.join('\n');
}

/**
 * Generate division overview section (simplified, not detailed)
 */
function generateDivisionOverview(overview, startY, silhouettePath) {
  // Placeholder - would include major subordinate units
  return `  <!-- Division overview section would go here -->`;
}

/**
 * Generate detailed regiment breakout with companies
 */
function generateRegimentDetail(regiment, startY, silhouettePath) {
  let svg = [];
  let currentY = startY;

  svg.push('  <!-- ==================== DETAILED ORGANIZATION ==================== -->');
  svg.push('');

  // Section title
  const sectionTitle = `${regiment.designation || 'Regiment'} - Detailed Organization`;
  svg.push(`  <rect x="20" y="${currentY}" width="500" height="40" fill="white" stroke="black" stroke-width="2"/>`);
  svg.push(`  <text x="270" y="${currentY + 27}" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle">${sectionTitle}</text>`);
  currentY += 60;

  // Regiment HQ
  svg.push(generateBox('Regimental HQ', null, 20, currentY));
  currentY += 60;

  // Process each battalion
  if (regiment.battalions && regiment.battalions.length > 0) {
    regiment.battalions.forEach((battalion, bIndex) => {
      const bResult = generateBattalion(battalion, currentY, silhouettePath);
      svg.push(bResult.svg);
      currentY = bResult.endY + LAYOUT.spacing.battalion;
    });
  }

  return svg.join('\n');
}

/**
 * Generate a battalion with its companies (Hermann Göring style)
 */
function generateBattalion(battalion, startY, silhouettePath) {
  let svg = [];
  let currentY = startY;

  const battalionName = battalion.designation || battalion.name || 'Battalion';
  const commander = battalion.commander_name || '';

  svg.push(`  <!-- ==================== ${battalionName.toUpperCase()} ==================== -->`);
  svg.push('');

  // Battalion box
  const boxCenterY = currentY + (LAYOUT.leftColumn.boxHeight / 2);
  svg.push(generateBox(battalionName, commander, LAYOUT.leftColumn.x, currentY));

  // Equipment summary for battalion
  if (battalion.equipment_summary) {
    svg.push(generateEquipmentRow(battalion.equipment_summary, currentY, silhouettePath, 'regiment'));
  }

  currentY += LAYOUT.leftColumn.boxHeight;

  // Vertical line down from battalion
  const lineStartY = currentY;
  const lineEndY = lineStartY + 10;
  svg.push(`  <line x1="${LAYOUT.leftColumn.x + (LAYOUT.leftColumn.width / 2)}" y1="${lineStartY}" x2="${LAYOUT.leftColumn.x + (LAYOUT.leftColumn.width / 2)}" y2="${lineEndY}" stroke="black" stroke-width="${LAYOUT.lines.strokeWidth}"/>`);

  // Horizontal line to left edge
  svg.push(`  <line x1="${LAYOUT.lines.leftEdgeX}" y1="${lineEndY}" x2="${LAYOUT.leftColumn.x + (LAYOUT.leftColumn.width / 2)}" y2="${lineEndY}" stroke="black" stroke-width="${LAYOUT.lines.strokeWidth}"/>`);

  currentY = lineEndY;

  // Calculate vertical line extent for all companies
  const companies = battalion.companies || [];
  const numCompanies = companies.length;

  if (numCompanies > 0) {
    // Calculate where the last company will be
    const lastCompanyY = currentY + (numCompanies * LAYOUT.spacing.company) - LAYOUT.spacing.company + (LAYOUT.leftColumn.boxHeight / 2);

    // Draw vertical line down left edge
    svg.push('');
    svg.push(`  <!-- Vertical line down left edge connecting all companies -->`);
    svg.push(`  <line x1="${LAYOUT.lines.leftEdgeX}" y1="${currentY}" x2="${LAYOUT.lines.leftEdgeX}" y2="${lastCompanyY}" stroke="black" stroke-width="${LAYOUT.lines.strokeWidth}"/>`);
    svg.push('');

    // Draw each company
    companies.forEach((company, cIndex) => {
      const companyY = currentY + (cIndex * LAYOUT.spacing.company);
      const companyMidY = companyY + (LAYOUT.leftColumn.boxHeight / 2);

      // Horizontal stub from left line to box
      svg.push(`  <!-- ${company.designation || `Company ${cIndex + 1}`} -->`);
      svg.push(`  <line x1="${LAYOUT.leftColumn.x}" y1="${companyMidY}" x2="${LAYOUT.lines.leftEdgeX}" y2="${companyMidY}" stroke="black" stroke-width="${LAYOUT.lines.strokeWidth}"/>`);

      // Company box (smaller width)
      svg.push(generateBox(
        company.designation || company.name || `${cIndex + 1}. Kompanie`,
        company.commander_name || '',
        LAYOUT.leftColumn.x,
        companyY,
        LAYOUT.leftColumn.smallBoxWidth
      ));

      // Company equipment
      if (company.equipment) {
        svg.push(generateEquipmentRow(company.equipment, companyY, silhouettePath, 'company'));
      }

      svg.push('');
    });

    currentY += (numCompanies * LAYOUT.spacing.company);
  }

  return {
    svg: svg.join('\n'),
    endY: currentY
  };
}

/**
 * Generate a unit box with optional commander name
 */
function generateBox(name, commanderName, x, y, width = LAYOUT.leftColumn.width) {
  const centerX = x + (width / 2);
  const textY = y + 23;
  const commanderY = y + LAYOUT.leftColumn.boxHeight + 13;

  let svg = [];
  svg.push(`  <rect x="${x}" y="${y}" width="${width}" height="${LAYOUT.leftColumn.boxHeight}" fill="white" stroke="black" stroke-width="2"/>`);
  svg.push(`  <text x="${centerX}" y="${textY}" font-family="Arial" font-size="${LAYOUT.fonts.unitName.size}" text-anchor="middle">${name}</text>`);

  if (commanderName) {
    svg.push(`  <text x="${centerX}" y="${commanderY}" font-family="Arial" font-size="${LAYOUT.fonts.commander.size}" font-style="${LAYOUT.fonts.commander.style}" text-anchor="middle">${commanderName}</text>`);
  }

  return svg.join('\n');
}

/**
 * Generate equipment row with silhouettes
 */
function generateEquipmentRow(equipment, y, silhouettePath, level = 'regiment') {
  let svg = [];

  const boxMidY = y + (LAYOUT.leftColumn.boxHeight / 2);
  const imageSize = LAYOUT.images[level];

  // Connection line from box to equipment
  const lineStartX = LAYOUT.leftColumn.x + LAYOUT.leftColumn.width;
  const lineEndX = LAYOUT.equipment.startX;
  svg.push(`  <line x1="${lineStartX}" y1="${boxMidY}" x2="${lineEndX}" y2="${boxMidY}" stroke="black" stroke-width="${LAYOUT.lines.strokeWidth}"/>`);

  let currentX = lineEndX + LAYOUT.equipment.imageGap;

  // Parse equipment (simplified - assumes structure like { "Panzer III": 60, "Panzer IV": 20 })
  Object.entries(equipment).forEach(([vehicleType, data]) => {
    const count = typeof data === 'number' ? data : data.count || 0;
    const variant = typeof data === 'object' ? data.variant : null;

    // Try to map to silhouette file
    const silhouetteFile = mapVehicleToSilhouette(vehicleType, variant);

    if (silhouetteFile) {
      const imageY = boxMidY - (imageSize.height / 2);
      const imageCenterX = currentX + (imageSize.width / 2);
      const labelY = boxMidY + 22;

      svg.push(`  <image x="${currentX}" y="${imageY}" width="${imageSize.width}" height="${imageSize.height}" xlink:href="${silhouettePath}/${silhouetteFile}" preserveAspectRatio="xMidYMid meet"/>`);
      svg.push(`  <text x="${imageCenterX}" y="${labelY}" font-family="Arial" font-size="${LAYOUT.fonts.equipment.size}" text-anchor="middle">${count}x ${vehicleType}</text>`);

      currentX += imageSize.width + LAYOUT.equipment.imageSpacing;
    } else {
      // No silhouette - use text only
      svg.push(`  <text x="${currentX}" y="${boxMidY}" font-family="Arial" font-size="${LAYOUT.fonts.equipment.size}">${count}x ${vehicleType}</text>`);
      currentX += 150;
    }
  });

  return svg.join('\n');
}

/**
 * Map vehicle type to silhouette filename
 */
function mapVehicleToSilhouette(vehicleType, variant) {
  // Simplified mapping - would need to be expanded based on your actual silhouettes
  const mapping = {
    'Panzer III': 'panzer_iii_ausf_g.png',
    'Panzer IV': 'panzer_iv_ausf_f1.png',
    'Panzer II': 'panzer_ii_ausf_c.png',
    'SdKfz 231': 'sd_kfz_231_8_rad.png',
    'SdKfz 251': 'sd_kfz_251.png',
    'SdKfz 250': 'sd_kfz_250_3.png',
  };

  // Check for exact match first
  if (mapping[vehicleType]) {
    return mapping[vehicleType];
  }

  // Check for partial match
  for (const [key, file] of Object.entries(mapping)) {
    if (vehicleType.includes(key)) {
      return file;
    }
  }

  return null;
}

/**
 * Generate footer notes
 */
function generateFooter() {
  const footerY = 1230;
  let svg = [];

  svg.push(`  <text x="20" y="${footerY}" font-family="Arial" font-size="9" font-style="italic">Note: ONE silhouette represents each vehicle TYPE with count (not individual vehicles). Commander names shown below each unit.</text>`);
  svg.push(`  <text x="20" y="${footerY + 15}" font-family="Arial" font-size="9" font-style="italic">Silhouettes marked with variant notes indicate similar type used as placeholder.</text>`);
  svg.push(`  <text x="20" y="${footerY + 30}" font-family="Arial" font-size="9" font-style="italic">Diagram generated automatically from unit JSON using Hermann Göring style layout.</text>`);

  return svg.join('\n');
}

/**
 * Main execution
 */
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Usage: node scripts/generate_toe_diagram.js <unit_json_file>');
    console.log('Example: node scripts/generate_toe_diagram.js data/output/units/german_1941q2_15_panzer_division_toe.json');
    process.exit(1);
  }

  const unitJsonPath = args[0];

  if (!fs.existsSync(unitJsonPath)) {
    console.error(`Error: File not found: ${unitJsonPath}`);
    process.exit(1);
  }

  // Read unit JSON
  const unitJson = JSON.parse(fs.readFileSync(unitJsonPath, 'utf8'));

  // Generate SVG
  const svg = generateDiagram(unitJson);

  // Determine output path
  const baseName = path.basename(unitJsonPath, '.json');
  const outputDir = path.join(__dirname, '..', 'data', 'output', 'diagrams');
  const outputPath = path.join(outputDir, `${baseName}_diagram.svg`);

  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Write SVG file
  fs.writeFileSync(outputPath, svg, 'utf8');

  console.log(`✅ Generated diagram: ${outputPath}`);
  console.log(`📝 To convert to PNG: cd ${outputDir} && magick ${path.basename(outputPath)} ${baseName}_diagram.png`);
}

// Run if called directly
if (require.main === module) {
  main();
}

// Export for use as module
module.exports = {
  generateDiagram,
  LAYOUT
};
