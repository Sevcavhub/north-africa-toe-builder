#!/usr/bin/env node

/**
 * Nafziger Air Forces PDF Extractor
 *
 * Extracts quarterly air OOB data from Nafziger Collection PDFs
 * Converts tabular data to air_summary schema JSON
 *
 * Usage: node extract_nafziger_air_pdf.js <pdf_path> <output_json_path>
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const NAFZIGER_AIR_PDFS = [
  {
    file: '941gdmc.pdf',
    path: 'Resource Documents/Nafziger Collection/WWII/1941-1942/Pt_I_1941-1942/941gdmc.pdf',
    title: 'Fliegerfuhrer Afrika, May 1941',
    nation: 'german',
    quarter: '1941q2',
    date: '1941-05-01'
  },
  {
    file: '942game.pdf',
    path: 'Resource Documents/Nafziger Collection/WWII/1941-1942/Pt_I_1941-1942/942game.pdf',
    title: 'Axis Air Force in North Africa, 18 January 1942',
    nations: ['german', 'italian'],
    quarter: '1942q1',
    date: '1942-01-18'
  },
  {
    file: '942geme.pdf',
    path: 'Resource Documents/Nafziger Collection/WWII/1941-1942/Pt_I_1941-1942/942geme.pdf',
    title: 'Axis Air Forces in North Africa, 10 May 1942',
    nations: ['german', 'italian'],
    quarter: '1942q2',
    date: '1942-05-10'
  },
  {
    file: '942bema.pdf',
    path: 'Resource Documents/Nafziger Collection/WWII/1941-1942/Pt_I_1941-1942/942bema.pdf',
    title: 'British Western Desert Air Force, 26 May 1942',
    nation: 'british',
    quarter: '1942q2',
    date: '1942-05-26'
  },
  {
    file: '942bima.pdf',
    path: 'Resource Documents/Nafziger Collection/WWII/1941-1942/Pt_I_1941-1942/942bima.pdf',
    title: 'British Western Desert Air Force, 1 September 1942',
    nation: 'british',
    quarter: '1942q3',
    date: '1942-09-01'
  }
];

/**
 * Extract text from PDF using pdftotext
 */
function extractPdfText(pdfPath) {
  try {
    const fullPath = path.resolve(__dirname, '..', pdfPath);

    // Check if file exists
    if (!fs.existsSync(fullPath)) {
      throw new Error(`PDF file not found: ${fullPath}`);
    }

    // Extract text using pdftotext with layout preservation
    const text = execSync(`pdftotext -layout "${fullPath}" -`, { encoding: 'utf-8' });
    return text;
  } catch (error) {
    console.error(`Error extracting PDF: ${error.message}`);
    throw error;
  }
}

/**
 * Parse unit line from Nafziger tabular format (with -layout flag)
 * Format with layout preservation:
 *   "2.(H)/14                HS126/Bf110    Ain El Gazala   18/13"
 *   "7./Jagdgruppe 26        Bf109E-7/Trop  Ain El Gazala   17/13"
 *
 * Columns separated by 2+ spaces
 */
function parseUnitLine(line) {
  // Skip header lines, empty lines, and footnotes
  if (!line ||
      line.match(/^(Unit|Aircraft|Base|Serviceable|Total|Formation|Copyright|Wood & Gunston)/i) ||
      line.trim().length === 0) {
    return null;
  }

  // Skip lines with only numbers (page numbers, footnotes)
  if (line.trim().match(/^\d+$/)) {
    return null;
  }

  // Split on multiple whitespace (2+ spaces) to get columns
  const columns = line.split(/\s{2,}/).map(col => col.trim()).filter(col => col.length > 0);

  // Need at least 2 columns (unit + something)
  if (columns.length < 2) {
    return null;
  }

  // Look for strength pattern in any column (format: number/number or "?")
  // Handle footnote markers like "18/13¹" by capturing only first digits after /
  let strengthCol = null;
  let strengthIndex = -1;
  let hasUnknownStrength = false;

  for (let i = 0; i < columns.length; i++) {
    // Check for "?" (unknown strength) - may be followed by base location
    if (columns[i].trim().startsWith('?')) {
      hasUnknownStrength = true;
      strengthIndex = i;
      break;
    }

    // Check for standard strength pattern (number/number)
    const match = columns[i].match(/(\d+)\/(\d+)/);
    if (match) {
      strengthCol = match;
      strengthIndex = i;
      break;
    }
  }

  // If no strength data found at all, skip this line
  if (strengthIndex === -1) {
    return null;
  }

  // Parse strength values
  const total = hasUnknownStrength ? null : parseInt(strengthCol[1]);
  const operational = hasUnknownStrength ? null : parseInt(strengthCol[2]);

  // First column is always unit designation
  const designation = columns[0];
  const normalized = normalizeUnitDesignation(designation);

  // Build result object
  const result = {
    designation: normalized,
    auto_nation: detectNationFromDesignation(normalized),
    total: total,
    operational: operational
  };

  // If strength is not in column 1, we have additional data
  if (strengthIndex > 1) {
    // Column 1 = Unit, Column 2 = Aircraft (if exists), Column 3 = Base (if exists), Last = Strength
    if (columns.length >= 3) {
      result.aircraft_types = [columns[1]];
    }
    if (columns.length >= 4) {
      result.base = columns[2];
    }
  }
  // If strength is in column 1, only unit + strength
  else if (strengthIndex === 1) {
    result.base = columns[1];
  }

  // Handle case where "?" is combined with base location (e.g., "? El Fetejah - Derna")
  if (hasUnknownStrength && columns[strengthIndex].includes(' ')) {
    // Extract base location after "?"
    result.base = columns[strengthIndex].replace(/^\?\s*/, '').trim();
  }

  return result;
}

/**
 * Normalize unit designation to canonical format
 * "Stab JG27" -> "Stab/JG 27"
 * "1/JG27" -> "I./JG 27"
 * "2.(H)/14" -> "2.(H)/14"
 */
function normalizeUnitDesignation(designation) {
  // Stab units
  if (designation.match(/^Stab\s+([A-Z]+)(\d+)/i)) {
    return designation.replace(/^Stab\s+([A-Z]+)(\d+)/i, 'Stab/$1 $2');
  }

  // Gruppe units (1/JG27 -> I./JG 27)
  if (designation.match(/^(\d)\/([A-Z]+)(\d+)/)) {
    const romanNumerals = ['I', 'II', 'III', 'IV'];
    return designation.replace(/^(\d)\/([A-Z]+)(\d+)/, (match, gruppe, type, number) => {
      return `${romanNumerals[parseInt(gruppe) - 1]}./${type} ${number}`;
    });
  }

  return designation;
}

/**
 * Auto-detect nation from unit designation
 */
function detectNationFromDesignation(designation) {
  // Italian patterns
  if (designation.match(/Gruppo|Stormo|Squadriglia|°/)) {
    return 'italian';
  }

  // German patterns
  if (designation.match(/^(Stab|I{1,3}\.|[0-9]+\/)(JG|ZG|KG|LG|StG|NJG|JaboG)/i) ||
      designation.match(/^(Jabo|Zerst[oö]rer|Stuka|Jagd)/i)) {
    return 'german';
  }

  // British/Commonwealth patterns
  if (designation.match(/^No\.\s+\d+.*?(Squadron|Wing|Group|RAAF|SAAF|RAF)/i)) {
    return 'british';
  }

  // American patterns
  if (designation.match(/^(USAAF|\d+th|\d+st|\d+nd|\d+rd).*?(Bomb|Fighter|Squadron|Group)/i)) {
    return 'american';
  }

  return null;
}

/**
 * Parse Format 2: Simple list format
 * Examples:
 *   "1/JG27 (23/6)" - unit with strength
 *   "6° Gruppo (MC202)" - unit with aircraft
 *   "Stab JG27 (3 aircraft, 2 servicable)" - descriptive format
 */
function parseListFormatLine(line) {
  // Trim line first
  line = line.trim();

  // Skip empty lines
  if (!line || line.length === 0) return null;

  // Skip headers and footers
  if (line.match(/^(Copyright|Wood & Gunston|Axis Air|British|Page|\d+$)/i)) {
    return null;
  }

  // Format 1: "1/JG27 (23/6)" or "Stab JG27 (3 aircraft, 2 servicable)"
  // First try descriptive format
  let match = line.match(/^(.+?)\s+\((\d+)\s+aircraft,\s+(\d+)\s+servic[ae]ble\)/i);
  if (match) {
    const designation = normalizeUnitDesignation(match[1].trim());
    return {
      designation: designation,
      auto_nation: detectNationFromDesignation(designation),
      total: parseInt(match[2]),
      operational: parseInt(match[3])
    };
  }

  // Then try simple strength format
  match = line.match(/^(.+?)\s+\((\d+)\/(\d+)\)/);
  if (match) {
    const designation = normalizeUnitDesignation(match[1].trim());
    return {
      designation: designation,
      auto_nation: detectNationFromDesignation(designation),
      total: parseInt(match[2]),
      operational: parseInt(match[3])
    };
  }

  // Format 2: "6° Gruppo (MC202)" - Italian units with aircraft type (no strength)
  // More flexible pattern to handle various aircraft name formats
  match = line.match(/^(.+?)\s+\(([A-Z0-9][A-Za-z0-9\-\/,\s]*)\)\s*$/);
  if (match) {
    const designation = match[1].trim();
    // Only parse if it looks like a valid Italian/German/Allied unit designation
    if (designation.match(/Gruppo|Stormo|Squadriglia|°|JG|ZG|Squadron/i)) {
      return {
        designation: designation,
        auto_nation: detectNationFromDesignation(designation),
        aircraft_types: [match[2].trim()],
        total: null,
        operational: null
      };
    }
  }

  return null;
}

/**
 * Parse Format 3: British hierarchical format
 * Example: "No. 4 (SAAF)(fighter) Squadron (GAMBUT) - Tomahawks"
 */
function parseBritishFormatLine(line) {
  // Skip empty lines and headers
  if (!line || line.trim().length === 0) return null;
  if (line.match(/^(A\.H\.Q|No\.\s+\d+\s+(Group|Wing):|Available to|HQ at)/i)) {
    return null;
  }

  // Pattern: "No. 4 (SAAF)(fighter) Squadron (BASE) - Aircraft"
  const match = line.match(/^\s*(No\.\s+\d+[A-Z]*\s+.*?Squadron)\s+\(([A-Z\s]+)\)\s+-\s+(.+)/i);
  if (match) {
    return {
      designation: match[1].trim(),
      base: match[2].trim(),
      aircraft_types: [match[3].trim()],
      total: null,
      operational: null
    };
  }

  return null;
}

/**
 * Detect format type from text
 */
function detectFormat(text) {
  // Check for tabular headers (handle typos like "Aiarcraft" and various column names)
  // Match "Unit" followed by any aircraft-like word, then strength/base/location
  if (text.match(/Unit\s+[Aa]\S*craft\s+(Base|Strength|Location)/i)) {
    return 'tabular';
  }

  // Check for British hierarchical format
  if (text.match(/No\.\s+\d+\s+\([A-Z]+\).*?Squadron/i)) {
    return 'british_hierarchical';
  }

  // Default to list format
  return 'list';
}

/**
 * Parse Nafziger air OOB text into structured data
 * Auto-detects format and uses appropriate parser
 */
function parseNafzigerAirOOB(text, metadata) {
  const format = detectFormat(text);
  const lines = text.split('\n');

  console.log(`   📋 Detected format: ${format}`);

  const units = [];
  let currentSection = null;

  for (const line of lines) {
    // Detect section headers (ITALIAN UNITS, GERMAN UNITS, etc.)
    if (line.match(/^(ITALIAN|GERMAN|BRITISH|RAF|USAAF)\s+(UNITS|AIR FORCE)/i)) {
      currentSection = line.match(/^(ITALIAN|GERMAN|BRITISH|RAF|USAAF)/i)[1].toLowerCase();
      if (currentSection === 'raf') currentSection = 'british';
      continue;
    }

    // Parse based on format
    let unit = null;
    if (format === 'tabular') {
      unit = parseUnitLine(line);
    } else if (format === 'list') {
      unit = parseListFormatLine(line);
    } else if (format === 'british_hierarchical') {
      unit = parseBritishFormatLine(line);
    }

    if (unit) {
      // Use section header nation, then auto-detected nation, then metadata nation
      unit.nation = currentSection || unit.auto_nation || metadata.nation || 'unknown';
      delete unit.auto_nation; // Remove temporary field
      units.push(unit);
    }
  }

  return units;
}

/**
 * Build hierarchical organization from flat unit list
 */
function buildOrganizationHierarchy(units) {
  // Group by formation type
  const formations = {};

  for (const unit of units) {
    // Detect formation type from designation
    let formationType = 'squadron'; // default
    let parent = null;

    if (unit.designation.match(/^Stab\//)) {
      formationType = 'geschwader_staff';
      parent = unit.designation.replace(/^Stab\//, '');
    } else if (unit.designation.match(/^(I{1,3})\.\//)) {
      formationType = 'gruppe';
      parent = unit.designation.replace(/^(I{1,3})\.\//, '');
    } else if (unit.designation.match(/^(\d+)\./)) {
      formationType = 'staffel';
    }

    // Group by parent formation
    if (parent) {
      if (!formations[parent]) {
        formations[parent] = {
          designation: parent,
          type: formationType === 'geschwader_staff' ? 'geschwader' : 'gruppe',
          subordinate_units: []
        };
      }
      formations[parent].subordinate_units.push(unit);
    }
  }

  return Object.values(formations);
}

/**
 * Generate air_summary JSON from parsed units
 */
function generateAirSummaryJSON(units, metadata) {
  const formations = buildOrganizationHierarchy(units);

  // Calculate aggregate strength (handle null values)
  const unitsWithStrength = units.filter(u => u.total !== null && u.operational !== null);
  const totalAircraft = unitsWithStrength.reduce((sum, u) => sum + (u.total || 0), 0);
  const operationalAircraft = unitsWithStrength.reduce((sum, u) => sum + (u.operational || 0), 0);
  const serviceabilityRate = totalAircraft > 0 ? (operationalAircraft / totalAircraft * 100).toFixed(1) : null;

  // Check if strength data is available
  const hasStrengthData = unitsWithStrength.length > 0;

  const summary = {
    schema_version: '3.1.0_air',
    nation: metadata.nation,
    quarter: metadata.quarter,
    theater: 'North Africa',
    source_document: {
      title: metadata.title,
      date: metadata.date,
      file: metadata.file,
      collection: 'Nafziger Collection',
      tier: 'tier_1'
    },
    air_command_structure: {
      theater_command: {
        designation: metadata.nation === 'german' ? 'Fliegerführer Afrika' :
                     metadata.nation === 'british' ? 'RAF Desert Air Force' :
                     metadata.nation === 'italian' ? 'Regia Aeronautica' : 'Unknown',
        commander: 'Unknown (not specified in source)',
        headquarters: 'Libya'
      },
      subordinate_formations: formations
    },
    aggregate_strength: hasStrengthData ? {
      total_aircraft: totalAircraft,
      operational_aircraft: operationalAircraft,
      serviceability_rate: parseFloat(serviceabilityRate),
      by_unit: units.map(u => ({
        designation: u.designation,
        total: u.total,
        operational: u.operational,
        base: u.base || 'Unknown',
        aircraft_types: u.aircraft_types || []
      }))
    } : {
      strength_data_unavailable: true,
      note: "Source document does not contain aircraft strength numbers",
      by_unit: units.map(u => ({
        designation: u.designation,
        base: u.base || 'Unknown',
        aircraft_types: u.aircraft_types || []
      }))
    },
    metadata: {
      sources: [`Nafziger Collection - ${metadata.file} (${metadata.title})`],
      confidence: hasStrengthData ? 90 : 70,
      tier: hasStrengthData ? 'production_ready' : 'review_recommended',
      extraction_date: new Date().toISOString().split('T')[0],
      extraction_method: 'Automated PDF parsing - Nafziger quarterly OOB snapshot',
      notes: hasStrengthData
        ? `Extracted from Nafziger Collection quarterly air forces OOB. Precise strength returns from historical source. ${units.length} units identified.`
        : `Extracted from Nafziger Collection quarterly air forces OOB. Organizational structure identified but source does not contain aircraft strength numbers. ${units.length} units identified.`
    }
  };

  return summary;
}

/**
 * Main extraction function
 */
function extractNafzigerAirPDF(pdfMetadata, outputDir) {
  console.log(`\n📄 Extracting: ${pdfMetadata.title}`);
  console.log(`   File: ${pdfMetadata.file}`);
  console.log(`   Quarter: ${pdfMetadata.quarter}`);

  // Extract PDF text
  console.log(`\n   🔍 Extracting PDF text...`);
  const text = extractPdfText(pdfMetadata.path);
  console.log(`   ✅ Extracted ${text.length} characters`);

  // Parse air OOB
  console.log(`\n   📊 Parsing air OOB data...`);
  const units = parseNafzigerAirOOB(text, pdfMetadata);
  console.log(`   ✅ Identified ${units.length} air units`);

  // Generate JSON for each nation (if multi-nation document)
  const nations = pdfMetadata.nations || [pdfMetadata.nation];

  for (const nation of nations) {
    const nationUnits = units.filter(u => u.nation === nation);

    if (nationUnits.length === 0) {
      console.log(`   ⚠️  No units found for ${nation}`);
      continue;
    }

    const metadata = { ...pdfMetadata, nation };
    const summary = generateAirSummaryJSON(nationUnits, metadata);

    // Write JSON
    const outputPath = path.join(outputDir, `${nation}_${metadata.quarter}_air_summary.json`);
    fs.writeFileSync(outputPath, JSON.stringify(summary, null, 2));
    console.log(`   ✅ Generated: ${outputPath}`);
    console.log(`      - ${nationUnits.length} units`);

    // Show strength info if available
    if (summary.aggregate_strength.strength_data_unavailable) {
      console.log(`      - Strength data not available in source`);
    } else {
      console.log(`      - ${summary.aggregate_strength.total_aircraft} aircraft (${summary.aggregate_strength.operational_aircraft} operational)`);
    }
  }
}

/**
 * Extract all Nafziger air PDFs
 */
function extractAllNafzigerAirPDFs() {
  console.log('🚀 Nafziger Air Forces PDF Extraction\n');
  console.log('=' .repeat(60));

  const outputDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');

  // Create output directory if needed
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log(`📁 Created output directory: ${outputDir}\n`);
  }

  let successCount = 0;
  let failCount = 0;

  for (const pdfMetadata of NAFZIGER_AIR_PDFS) {
    try {
      extractNafzigerAirPDF(pdfMetadata, outputDir);
      successCount++;
    } catch (error) {
      console.error(`   ❌ Error: ${error.message}`);
      failCount++;
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log(`\n✅ Extraction complete:`);
  console.log(`   Success: ${successCount}/${NAFZIGER_AIR_PDFS.length} PDFs`);
  console.log(`   Failed: ${failCount}/${NAFZIGER_AIR_PDFS.length} PDFs`);
  console.log(`\n📁 Output directory: ${outputDir}`);
}

// CLI execution
if (require.main === module) {
  try {
    extractAllNafzigerAirPDFs();
  } catch (error) {
    console.error(`\n❌ Fatal error: ${error.message}`);
    process.exit(1);
  }
}

module.exports = {
  extractPdfText,
  parseNafzigerAirOOB,
  parseUnitLine,
  parseListFormatLine,
  parseBritishFormatLine,
  buildOrganizationHierarchy,
  generateAirSummaryJSON,
  extractNafzigerAirPDF,
  NAFZIGER_AIR_PDFS
};
