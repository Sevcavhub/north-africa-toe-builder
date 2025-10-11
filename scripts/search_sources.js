#!/usr/bin/env node

/**
 * Source Document Search Helper
 *
 * Searches across all local source documents for a given query.
 * Useful for finding specific units, commanders, or equipment across sources.
 */

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const { promisify } = require('util');

const gunzip = promisify(zlib.gunzip);
const readFile = promisify(fs.readFile);
const readdir = promisify(fs.readdir);

const RESOURCE_DIR = 'D:\\north-africa-toe-builder\\Resource Documents';

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

/**
 * Search a gzipped text file
 */
async function searchGzFile(filePath, query, options = {}) {
  try {
    const compressed = await readFile(filePath);
    const decompressed = await gunzip(compressed);
    const content = decompressed.toString('utf-8');

    return searchContent(content, query, filePath, options);
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error.message);
    return [];
  }
}

/**
 * Search a regular text file
 */
async function searchTextFile(filePath, query, options = {}) {
  try {
    const content = await readFile(filePath, 'utf-8');
    return searchContent(content, query, filePath, options);
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error.message);
    return [];
  }
}

/**
 * Search content for query
 */
function searchContent(content, query, filePath, options = {}) {
  const {
    contextLines = 2,
    caseSensitive = false,
    maxResults = 5
  } = options;

  const results = [];
  const lines = content.split('\n');
  const searchRegex = new RegExp(
    caseSensitive ? query : query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
    caseSensitive ? 'g' : 'gi'
  );

  for (let i = 0; i < lines.length; i++) {
    if (searchRegex.test(lines[i])) {
      const startLine = Math.max(0, i - contextLines);
      const endLine = Math.min(lines.length - 1, i + contextLines);

      const contextBefore = lines.slice(startLine, i);
      const matchLine = lines[i];
      const contextAfter = lines.slice(i + 1, endLine + 1);

      results.push({
        file: path.basename(filePath),
        fullPath: filePath,
        lineNumber: i + 1,
        contextBefore,
        matchLine,
        contextAfter
      });

      if (results.length >= maxResults) {
        break;
      }
    }
  }

  return results;
}

/**
 * Get all searchable files from a directory
 */
async function getSearchableFiles(dir) {
  const files = [];

  try {
    const entries = await readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        // Recursively search subdirectories
        const subFiles = await getSearchableFiles(fullPath);
        files.push(...subFiles);
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase();
        if (ext === '.gz' && entry.name.includes('searchtext.txt')) {
          files.push({ path: fullPath, type: 'gz' });
        } else if (ext === '.txt') {
          files.push({ path: fullPath, type: 'txt' });
        }
      }
    }
  } catch (error) {
    console.error(`Error reading directory ${dir}:`, error.message);
  }

  return files;
}

/**
 * Display search results
 */
function displayResults(results, query) {
  if (results.length === 0) {
    console.log(colorize('\nNo results found.', 'yellow'));
    return;
  }

  console.log(colorize(`\nFound ${results.length} results for "${query}":\n`, 'green'));

  results.forEach((result, index) => {
    console.log(colorize(`\n[Result ${index + 1}] ${result.file}:${result.lineNumber}`, 'cyan'));
    console.log(colorize('-'.repeat(80), 'blue'));

    // Context before
    if (result.contextBefore.length > 0) {
      result.contextBefore.forEach(line => {
        console.log(colorize(line, 'reset'));
      });
    }

    // Match line (highlighted)
    console.log(colorize(result.matchLine, 'bright'));

    // Context after
    if (result.contextAfter.length > 0) {
      result.contextAfter.forEach(line => {
        console.log(colorize(line, 'reset'));
      });
    }

    console.log(colorize('-'.repeat(80), 'blue'));
  });
}

/**
 * Main search function
 */
async function searchSources(query, options = {}) {
  console.log(colorize(`\nSearching sources for: "${query}"`, 'bright'));
  console.log(colorize(`Resource directory: ${RESOURCE_DIR}\n`, 'cyan'));

  const {
    sourceType = 'all',  // 'all', 'british', 'german', 'us'
    contextLines = 2,
    maxResultsPerFile = 5,
    maxTotalResults = 20,
    caseSensitive = false
  } = options;

  // Get all searchable files
  let allFiles = await getSearchableFiles(RESOURCE_DIR);

  // Filter by source type
  if (sourceType !== 'all') {
    allFiles = allFiles.filter(file => {
      const filePath = file.path.toLowerCase();
      if (sourceType === 'british') {
        return filePath.includes('british') || filePath.includes('great britain');
      } else if (sourceType === 'german') {
        return filePath.includes('tessin') || filePath.includes('wehrmacht');
      } else if (sourceType === 'us') {
        return filePath.includes('fm');
      }
      return true;
    });
  }

  console.log(colorize(`Searching ${allFiles.length} files...`, 'yellow'));

  const allResults = [];

  for (const file of allFiles) {
    let results = [];

    if (file.type === 'gz') {
      results = await searchGzFile(file.path, query, {
        contextLines,
        maxResults: maxResultsPerFile,
        caseSensitive
      });
    } else if (file.type === 'txt') {
      results = await searchTextFile(file.path, query, {
        contextLines,
        maxResults: maxResultsPerFile,
        caseSensitive
      });
    }

    allResults.push(...results);

    if (allResults.length >= maxTotalResults) {
      break;
    }
  }

  displayResults(allResults.slice(0, maxTotalResults), query);

  if (allResults.length > maxTotalResults) {
    console.log(colorize(`\n(${allResults.length - maxTotalResults} more results not shown)`, 'yellow'));
  }

  return allResults;
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
${colorize('Source Document Search Helper', 'bright')}

${colorize('Usage:', 'cyan')}
  node search_sources.js <query> [options]

${colorize('Options:', 'cyan')}
  --type <british|german|us|all>     Filter by source type (default: all)
  --context <number>                  Lines of context (default: 2)
  --max <number>                      Max total results (default: 20)
  --case-sensitive                    Case-sensitive search

${colorize('Examples:', 'cyan')}
  node search_sources.js "21st Panzer"
  node search_sources.js "7th Armoured" --type british
  node search_sources.js "Rommel" --type german --context 5
  node search_sources.js "M4 Sherman" --type us --max 10
  node search_sources.js "XXI Corpo" --case-sensitive
`);
    process.exit(0);
  }

  const query = args[0];
  const options = {
    sourceType: 'all',
    contextLines: 2,
    maxTotalResults: 20,
    caseSensitive: false
  };

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--type' && args[i + 1]) {
      options.sourceType = args[i + 1];
      i++;
    } else if (args[i] === '--context' && args[i + 1]) {
      options.contextLines = parseInt(args[i + 1], 10);
      i++;
    } else if (args[i] === '--max' && args[i + 1]) {
      options.maxTotalResults = parseInt(args[i + 1], 10);
      i++;
    } else if (args[i] === '--case-sensitive') {
      options.caseSensitive = true;
    }
  }

  searchSources(query, options)
    .then(() => process.exit(0))
    .catch(error => {
      console.error(colorize('Error:', 'red'), error.message);
      process.exit(1);
    });
}

module.exports = { searchSources };
