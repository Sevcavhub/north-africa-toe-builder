#!/usr/bin/env node

/**
 * Source Scanner - Automatic Unit Discovery
 *
 * Scans primary sources to automatically discover units based on search patterns.
 * Used by the orchestrator to find all units in theater without manual specification.
 *
 * For each nation, scans designated sources for unit patterns (e.g., ".*Panzer.*Division")
 * and extracts unit designations with quarter/date information.
 */

const fs = require('fs').promises;
const path = require('path');
const zlib = require('zlib');
const { promisify } = require('util');

const gunzip = promisify(zlib.gunzip);

/**
 * Search sources for units matching patterns
 *
 * @param {string} sourceName - Name of source to search (e.g., "Tessin Band 03")
 * @param {string} pattern - Regex pattern to match (e.g., ".*Panzer.*Division")
 * @param {Array} quarters - List of quarters to look for
 * @returns {Array} - Array of discovered units
 */
async function search_sources(sourceName, pattern, quarters) {
  console.log(`    Scanning ${sourceName} for pattern: ${pattern}`);

  try {
    // Find the source file
    const sourceFile = await findSourceFile(sourceName);

    if (!sourceFile) {
      console.log(`      ✗ Source file not found: ${sourceName}`);
      return [];
    }

    // Extract content
    const content = await extractContent(sourceFile);

    // Search for pattern
    const units = await searchForPattern(content, pattern, quarters);

    console.log(`      ✓ Found ${units.length} unit(s)`);
    return units;
  } catch (error) {
    console.error(`      ✗ Error scanning ${sourceName}:`, error.message);
    return [];
  }
}

/**
 * Find source file by name
 */
async function findSourceFile(sourceName) {
  const basePath = path.join(process.cwd(), 'Resource Documents');

  // Map source names to file patterns
  if (sourceName.includes('Tessin Band 03')) {
    return await findFile(basePath, 'tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss', 'Band 03', 'searchtext');
  } else if (sourceName.includes('Tessin Band 08')) {
    return await findFile(basePath, 'tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss', 'Band 08', 'searchtext');
  } else if (sourceName.includes('British Army Lists')) {
    return await findFile(basePath, 'British Army Lists', null, '_text.txt');
  } else if (sourceName.includes('TM 30-410')) {
    return await findFile(basePath, null, 'TM30-410', '_text.txt');
  } else if (sourceName.includes('Desert Rats')) {
    return await findFile(basePath, null, 'Desert', null);
  }

  return null;
}

/**
 * Find file matching patterns
 */
async function findFile(basePath, dirPattern, filePattern1, filePattern2) {
  try {
    let searchDir = basePath;

    // If directory pattern specified, find matching directory
    if (dirPattern) {
      const dirs = await fs.readdir(basePath);
      const matchingDir = dirs.find(d => d.includes(dirPattern));

      if (!matchingDir) return null;
      searchDir = path.join(basePath, matchingDir);
    }

    // Find matching file
    const files = await fs.readdir(searchDir);

    let matchingFile = files.find(f => {
      if (filePattern1 && !f.includes(filePattern1)) return false;
      if (filePattern2 && !f.includes(filePattern2)) return false;
      return true;
    });

    if (matchingFile) return path.join(searchDir, matchingFile);

    return null;
  } catch (error) {
    return null;
  }
}

/**
 * Extract content from file
 */
async function extractContent(filePath) {
  const ext = path.extname(filePath).toLowerCase();

  if (ext === '.gz') {
    const compressed = await fs.readFile(filePath);
    const decompressed = await gunzip(compressed);
    return decompressed.toString('utf-8');
  } else if (ext === '.txt') {
    return await fs.readFile(filePath, 'utf-8');
  } else {
    throw new Error(`Unsupported file type: ${ext}`);
  }
}

/**
 * Search content for pattern and extract unit information
 */
async function searchForPattern(content, pattern, quarters) {
  const regex = new RegExp(pattern, 'gi');
  const lines = content.split('\n');
  const discovered = new Map(); // Use map to deduplicate

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const matches = line.match(regex);

    if (matches) {
      for (const match of matches) {
        // Extract quarter information from surrounding context
        const context = extractContext(lines, i, 20);
        const quarter = extractQuarter(context, quarters);

        // IMPORTANT: Only include units with valid quarters (skip unknown/out-of-scope)
        if (!quarter || quarter === 'unknown') continue;
        if (!quarters.includes(quarter)) continue;

        // Create unique key
        const key = `${match}_${quarter}`;

        if (!discovered.has(key)) {
          discovered.set(key, {
            designation: match.trim(),
            quarter: quarter,
            context_line: line.trim(),
            line_number: i
          });
        }
      }
    }
  }

  return Array.from(discovered.values());
}

/**
 * Extract context lines around match
 */
function extractContext(lines, index, contextLines) {
  const start = Math.max(0, index - contextLines);
  const end = Math.min(lines.length, index + contextLines);
  return lines.slice(start, end).join('\n');
}

/**
 * Extract quarter from context
 */
function extractQuarter(context, quarters) {
  // Try to find explicit quarter mention
  for (const quarter of quarters) {
    if (context.includes(quarter)) return quarter;
  }

  // Try to find year/month mentions
  const yearMonthPatterns = [
    /\b(1940|1941|1942|1943)\b/,
    /\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(1940|1941|1942|1943)/i,
    /\b(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+(1940|1941|1942|1943)/i
  ];

  for (const pattern of yearMonthPatterns) {
    const match = context.match(pattern);
    if (match) {
      const year = match[1] || match[2];
      const month = match[0];

      // Convert to quarter
      const quarter = convertToQuarter(year, month);
      if (quarter) return quarter;
    }
  }

  // Default to unknown
  return null;
}

/**
 * Convert year and month to quarter
 */
function convertToQuarter(year, monthStr) {
  const monthMap = {
    'jan': 'Q1', 'januar': 'Q1', 'february': 'Q1', 'februar': 'Q1', 'march': 'Q1', 'märz': 'Q1',
    'apr': 'Q2', 'april': 'Q2', 'may': 'Q2', 'mai': 'Q2', 'june': 'Q2', 'juni': 'Q2',
    'jul': 'Q3', 'juli': 'Q3', 'august': 'Q3', 'sep': 'Q3', 'september': 'Q3',
    'oct': 'Q4', 'oktober': 'Q4', 'november': 'Q4', 'dec': 'Q4', 'dezember': 'Q4'
  };

  const monthLower = monthStr.toLowerCase();
  for (const [key, quarter] of Object.entries(monthMap)) {
    if (monthLower.includes(key)) {
      return `${year}-${quarter}`;
    }
  }

  return null;
}

/**
 * Scan multiple sources for a nation's units
 */
async function scanNationSources(nationConfig, quarters) {
  const allUnits = [];

  for (const source of nationConfig.sources) {
    for (const pattern of nationConfig.search_patterns) {
      const units = await search_sources(source, pattern, quarters);

      units.forEach(unit => {
        allUnits.push({
          nation: nationConfig.nation,
          designation: unit.designation,
          quarter: unit.quarter,
          source: source,
          pattern: pattern,
          context: unit.context_line
        });
      });
    }
  }

  return allUnits;
}

module.exports = {
  search_sources,
  scanNationSources
};
