#!/usr/bin/env node

/**
 * remove-wikipedia-sources.js
 *
 * Removes Wikipedia sources from validation.source arrays in TO&E JSON files.
 * Part of v3.0.0 schema compliance - Gap 3 fix.
 *
 * IMPORTANT: Run after backing up files to wikipedia_versions/ directory.
 *
 * Usage:
 *   node scripts/remove-wikipedia-sources.js [file1.json file2.json ...]
 */

const fs = require('fs');
const path = require('path');

// Wikipedia patterns to remove
const WIKIPEDIA_PATTERNS = [
  /wikipedia\.org/i,
  /wikipedia\.com/i,
  /\.wikipedia\./i,
  /\bwikipedia\b/i,
  /wikia\./i,
  /fandom\.com/i,
  /\bmilitary\s+wiki\b/i,
  /wikimedia\.org/i
];

// ANSI colors
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const BLUE = '\x1b[34m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

class WikipediaCleaner {
  constructor() {
    this.filesProcessed = 0;
    this.sourcesRemoved = 0;
  }

  /**
   * Check if a string contains Wikipedia references
   */
  containsWikipedia(text) {
    if (!text || typeof text !== 'string') return false;
    return WIKIPEDIA_PATTERNS.some(pattern => pattern.test(text));
  }

  /**
   * Clean a single JSON file
   */
  cleanFile(filePath) {
    console.log(`\n${BLUE}Processing:${RESET} ${path.basename(filePath)}`);

    try {
      // Read JSON
      const content = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(content);
      let removed = 0;

      // Clean validation.source array
      if (data.validation && data.validation.source) {
        const originalLength = Array.isArray(data.validation.source)
          ? data.validation.source.length
          : 1;

        if (Array.isArray(data.validation.source)) {
          const cleaned = data.validation.source.filter(source => {
            const isWiki = this.containsWikipedia(source);
            if (isWiki) {
              console.log(`  ${RED}✗${RESET} Removing: "${YELLOW}${source.substring(0, 60)}...${RESET}"`);
              removed++;
            }
            return !isWiki;
          });
          data.validation.source = cleaned;
        } else if (typeof data.validation.source === 'string') {
          if (this.containsWikipedia(data.validation.source)) {
            console.log(`  ${RED}✗${RESET} Removing: "${YELLOW}${data.validation.source.substring(0, 60)}...${RESET}"`);
            data.validation.source = [];
            removed++;
          }
        }

        console.log(`  ${GREEN}✓${RESET} validation.source: ${originalLength} → ${data.validation.source.length} (removed ${removed})`);
      }

      // Clean validation.sources (alternate field)
      if (data.validation && data.validation.sources) {
        const originalLength = Array.isArray(data.validation.sources)
          ? data.validation.sources.length
          : 1;
        let sourcesRemoved = 0;

        if (Array.isArray(data.validation.sources)) {
          const cleaned = data.validation.sources.filter(source => {
            const isWiki = this.containsWikipedia(source);
            if (isWiki) {
              console.log(`  ${RED}✗${RESET} Removing from sources: "${YELLOW}${source.substring(0, 60)}...${RESET}"`);
              sourcesRemoved++;
            }
            return !isWiki;
          });
          data.validation.sources = cleaned;
        }

        if (sourcesRemoved > 0) {
          console.log(`  ${GREEN}✓${RESET} validation.sources: ${originalLength} → ${data.validation.sources.length} (removed ${sourcesRemoved})`);
          removed += sourcesRemoved;
        }
      }

      // Clean data_quality.primary_sources (if present)
      if (data.data_quality && data.data_quality.primary_sources) {
        const originalLength = data.data_quality.primary_sources.length;
        let dqRemoved = 0;

        const cleaned = data.data_quality.primary_sources.filter(source => {
          const isWiki = this.containsWikipedia(source);
          if (isWiki) {
            console.log(`  ${RED}✗${RESET} Removing from data_quality: "${YELLOW}${source.substring(0, 60)}...${RESET}"`);
            dqRemoved++;
          }
          return !isWiki;
        });
        data.data_quality.primary_sources = cleaned;

        if (dqRemoved > 0) {
          console.log(`  ${GREEN}✓${RESET} data_quality.primary_sources: ${originalLength} → ${cleaned.length} (removed ${dqRemoved})`);
          removed += dqRemoved;
        }
      }

      // Write cleaned JSON
      if (removed > 0) {
        const cleanedJson = JSON.stringify(data, null, 2);
        fs.writeFileSync(filePath, cleanedJson, 'utf-8');
        console.log(`  ${GREEN}${BOLD}✓ CLEANED${RESET} - Removed ${removed} Wikipedia source(s)`);

        this.filesProcessed++;
        this.sourcesRemoved += removed;
      } else {
        console.log(`  ${GREEN}✓ ALREADY CLEAN${RESET} - No Wikipedia sources found`);
      }

    } catch (error) {
      console.error(`  ${RED}${BOLD}ERROR${RESET}: ${error.message}`);
    }
  }

  /**
   * Print summary report
   */
  printSummary() {
    console.log('\n' + '='.repeat(70));
    console.log(`${BOLD}Wikipedia Removal Summary${RESET}`);
    console.log('='.repeat(70));
    console.log(`Files processed:    ${this.filesProcessed}`);
    console.log(`Sources removed:    ${this.sourcesRemoved}`);
    console.log('='.repeat(70));

    if (this.filesProcessed > 0) {
      console.log(`\n${GREEN}${BOLD}✓ CLEANING COMPLETE${RESET}`);
      console.log(`\nNext steps:`);
      console.log(`1. Verify: npm run validate:sources data/output/1941-q2-showcase/consolidated_units/`);
      console.log(`2. Regenerate chapters: node scripts/generate_mdbook_chapters.js`);
      console.log(`3. Backups available: data/output/1941-q2-showcase/wikipedia_versions/`);
    }
  }

  /**
   * Main execution
   */
  run() {
    console.log(`${BOLD}Wikipedia Source Cleaner v1.0${RESET}`);
    console.log(`Removing Wikipedia citations for v3.0 compliance\n`);

    // Get file list from command line or use defaults
    const files = process.argv.slice(2);

    if (files.length === 0) {
      console.error(`${RED}ERROR${RESET}: No files specified`);
      console.log('\nUsage:');
      console.log('  node scripts/remove-wikipedia-sources.js file1.json file2.json ...');
      console.log('\nExample:');
      console.log('  node scripts/remove-wikipedia-sources.js data/output/1941-q2-showcase/consolidated_units/*.json');
      process.exit(1);
    }

    // Process each file
    files.forEach(file => {
      if (!fs.existsSync(file)) {
        console.error(`${RED}ERROR${RESET}: File not found: ${file}`);
        return;
      }

      this.cleanFile(file);
    });

    this.printSummary();
  }
}

// Run if called directly
if (require.main === module) {
  const cleaner = new WikipediaCleaner();
  cleaner.run();
}

module.exports = WikipediaCleaner;
