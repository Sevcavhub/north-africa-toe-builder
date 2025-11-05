#!/usr/bin/env node

/**
 * Prepare Source Document for Agent Processing
 *
 * Automatically extracts and formats source documents for agent consumption.
 * Handles PDF, .gz, and text files from Resource Documents folder.
 */

const fs = require('fs').promises;
const zlib = require('zlib');
const { promisify } = require('util');
const path = require('path');

const gunzip = promisify(zlib.gunzip);

const RESOURCE_DIR = 'D:\\north-africa-toe-builder\\Resource Documents';

/**
 * Extract content from gzipped text file
 */
async function extractGzFile(filePath) {
  const compressed = await fs.readFile(filePath);
  const decompressed = await gunzip(compressed);
  return decompressed.toString('utf-8');
}

/**
 * Extract content from text file
 */
async function extractTextFile(filePath) {
  return await fs.readFile(filePath, 'utf-8');
}

/**
 * Search for a unit/topic in source content
 */
function extractRelevantSection(content, searchTerm, contextLines = 100) {
  const lines = content.split('\n');
  const searchRegex = new RegExp(searchTerm, 'gi');

  const relevantSections = [];

  for (let i = 0; i < lines.length; i++) {
    if (searchRegex.test(lines[i])) {
      const startLine = Math.max(0, i - contextLines);
      const endLine = Math.min(lines.length - 1, i + contextLines);

      const section = lines.slice(startLine, endLine + 1).join('\n');
      relevantSections.push({
        startLine: startLine + 1,
        endLine: endLine + 1,
        content: section
      });

      // Skip ahead to avoid overlapping sections
      i = endLine;
    }
  }

  return relevantSections;
}

/**
 * Create agent task for document_parser
 */
async function createDocumentParserTask(options) {
  const {
    sourceFile,
    documentType,
    nation,
    quarter,
    searchTerm = null,
    contextLines = 100
  } = options;

  console.log(`\nPreparing source: ${path.basename(sourceFile)}`);
  console.log(`Document type: ${documentType}`);
  console.log(`Nation: ${nation}, Quarter: ${quarter}`);

  // Extract content based on file type
  let content;
  const ext = path.extname(sourceFile).toLowerCase();

  if (ext === '.gz') {
    console.log('Extracting gzipped file...');
    content = await extractGzFile(sourceFile);
  } else if (ext === '.txt') {
    console.log('Reading text file...');
    content = await extractTextFile(sourceFile);
  } else if (ext === '.pdf') {
    console.log('Note: PDF extraction requires external tool. Please extract to .txt first.');
    return null;
  } else {
    throw new Error(`Unsupported file type: ${ext}`);
  }

  // If search term provided, extract only relevant sections
  if (searchTerm) {
    console.log(`Searching for: "${searchTerm}"`);
    const sections = extractRelevantSection(content, searchTerm, contextLines);
    console.log(`Found ${sections.length} relevant section(s)`);

    if (sections.length === 0) {
      console.log('Warning: No matches found. Using full document.');
    } else {
      // Combine all relevant sections
      content = sections.map((s, i) =>
        `--- Section ${i + 1} (lines ${s.startLine}-${s.endLine}) ---\n${s.content}`
      ).join('\n\n');
    }
  }

  // Truncate if too long (max 100k chars for agent processing)
  if (content.length > 100000) {
    console.log(`Warning: Content truncated from ${content.length} to 100000 characters`);
    content = content.substring(0, 100000);
  }

  // Create task
  const taskId = `task_${Date.now()}_parser_${nation.toLowerCase()}`;
  const task = {
    task_id: taskId,
    agent_id: 'document_parser',
    inputs: {
      source_content: content,
      document_type: documentType,
      nation: nation,
      quarter: quarter
    },
    dependencies: [],
    created_at: new Date().toISOString(),
    status: 'pending',
    metadata: {
      source_file: sourceFile,
      search_term: searchTerm,
      content_length: content.length
    }
  };

  // Save task to pending directory
  const taskFile = path.join(process.cwd(), 'tasks', 'pending', `${taskId}.json`);
  await fs.writeFile(taskFile, JSON.stringify(task, null, 2));

  console.log(`\n✓ Task created: ${taskId}`);
  console.log(`✓ Task file: tasks/pending/${taskId}.json`);
  console.log(`✓ Content length: ${content.length} characters`);

  if (searchTerm) {
    console.log(`✓ Extracted sections for: "${searchTerm}"`);
  }

  console.log('\nNext steps:');
  console.log('1. Terminal 2: npm run agent document_parser');
  console.log('2. VS Code Window 2: Process the task in Claude Code chat');
  console.log('3. Agent will output: outputs/${taskId}_output.json\n');

  return task;
}

/**
 * Create task for historical_research using previous output
 */
async function createHistoricalResearchTask(rawFactsFile, additionalSources) {
  const rawFacts = JSON.parse(await fs.readFile(rawFactsFile, 'utf-8'));

  // Prepare additional sources
  const sourceList = [];
  for (const src of additionalSources) {
    let content;

    if (src.file) {
      // Extract from file
      const ext = path.extname(src.file).toLowerCase();
      if (ext === '.gz') {
        content = await extractGzFile(src.file);
      } else if (ext === '.txt') {
        content = await extractTextFile(src.file);
      }

      // Extract relevant section if search term provided
      if (src.searchTerm && content) {
        const sections = extractRelevantSection(content, src.searchTerm, 50);
        if (sections.length > 0) {
          content = sections[0].content;
        }
      }

      sourceList.push({
        source: src.name || path.basename(src.file),
        content: content ? content.substring(0, 10000) : '' // Limit per source
      });
    } else if (src.url) {
      // Web source - user needs to provide content
      sourceList.push({
        source: src.name || src.url,
        url: src.url,
        content: src.content || '(Content to be provided)'
      });
    }
  }

  const taskId = `task_${Date.now()}_research`;
  const task = {
    task_id: taskId,
    agent_id: 'historical_research',
    inputs: {
      raw_facts: rawFacts,
      source_list: sourceList
    },
    dependencies: [],
    created_at: new Date().toISOString(),
    status: 'pending'
  };

  const taskFile = path.join(process.cwd(), 'tasks', 'pending', `${taskId}.json`);
  await fs.writeFile(taskFile, JSON.stringify(task, null, 2));

  console.log(`\n✓ Research task created: ${taskId}`);
  console.log(`✓ Cross-referencing ${sourceList.length} additional sources`);
  console.log('\nNext steps:');
  console.log('1. Terminal 3: npm run agent historical_research');
  console.log('2. VS Code Window 3: Process the task in Claude Code chat\n');

  return task;
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help') {
    console.log(`
Prepare Source Document for Agent Processing

Usage:
  node prepare_source_for_agent.js <command> [options]

Commands:
  parse     Create document_parser task
  research  Create historical_research task

Parse Command:
  node prepare_source_for_agent.js parse \\
    --source "path/to/source.txt.gz" \\
    --type "Tessin Wehrmacht Encyclopedia" \\
    --nation Germany \\
    --quarter 1941-Q2 \\
    --search "21.*Panzer" \\
    --context 100

Research Command:
  node prepare_source_for_agent.js research \\
    --raw-facts "outputs/task_xxx_output.json" \\
    --add-source "path/to/source2.txt.gz:Search term" \\
    --add-source "path/to/source3.txt.gz:Different search"

Options:
  --source <path>         Path to source document (for parse)
  --type <string>         Document type description
  --nation <string>       Nation (Germany, Britain, USA, Italy, etc.)
  --quarter <string>      Time period (e.g., 1941-Q2)
  --search <string>       Search term to extract relevant sections
  --context <number>      Lines of context around matches (default: 100)

  --raw-facts <path>      Path to raw_facts.json (for research)
  --add-source <string>   Additional source (file:search or url)

Examples:
  # Extract German 21st Panzer from Tessin
  node prepare_source_for_agent.js parse \\
    --source "D:\\north-africa-toe-builder\\Resource Documents\\tessin...Band_08...txt.gz" \\
    --type "Tessin Band 08" \\
    --nation Germany \\
    --quarter 1941-Q2 \\
    --search "21.*Panzer"

  # Cross-reference with additional sources
  node prepare_source_for_agent.js research \\
    --raw-facts "outputs/task_123_output.json" \\
    --add-source "tessin_band_03.txt.gz:21.*Panzer" \\
    --add-source "feldgrau:http://feldgrau.com/21pzdiv.html"
`);
    process.exit(0);
  }

  const command = args[0];
  const options = {};
  const additionalSources = [];

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--source' && args[i + 1]) {
      options.sourceFile = args[i + 1];
      i++;
    } else if (args[i] === '--type' && args[i + 1]) {
      options.documentType = args[i + 1];
      i++;
    } else if (args[i] === '--nation' && args[i + 1]) {
      options.nation = args[i + 1];
      i++;
    } else if (args[i] === '--quarter' && args[i + 1]) {
      options.quarter = args[i + 1];
      i++;
    } else if (args[i] === '--search' && args[i + 1]) {
      options.searchTerm = args[i + 1];
      i++;
    } else if (args[i] === '--context' && args[i + 1]) {
      options.contextLines = parseInt(args[i + 1], 10);
      i++;
    } else if (args[i] === '--raw-facts' && args[i + 1]) {
      options.rawFactsFile = args[i + 1];
      i++;
    } else if (args[i] === '--add-source' && args[i + 1]) {
      const parts = args[i + 1].split(':');
      additionalSources.push({
        file: parts[0],
        searchTerm: parts[1] || null,
        name: path.basename(parts[0])
      });
      i++;
    }
  }

  if (command === 'parse') {
    createDocumentParserTask(options)
      .then(() => process.exit(0))
      .catch(err => {
        console.error('Error:', err.message);
        process.exit(1);
      });
  } else if (command === 'research') {
    createHistoricalResearchTask(options.rawFactsFile, additionalSources)
      .then(() => process.exit(0))
      .catch(err => {
        console.error('Error:', err.message);
        process.exit(1);
      });
  } else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

module.exports = { createDocumentParserTask, createHistoricalResearchTask };
