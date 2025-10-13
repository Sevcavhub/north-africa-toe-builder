#!/usr/bin/env node

/**
 * validate-no-wikipedia.js
 *
 * Validates that NO unit TO&E JSON files contain Wikipedia sources.
 * Part of v3.0.0 schema enforcement - Gap 3 fix.
 *
 * Usage:
 *   npm run validate:sources
 *   node scripts/validate-no-wikipedia.js [directory]
 *   node scripts/validate-no-wikipedia.js data/units/german_1941q2_dak_toe.json
 *
 * Exit codes:
 *   0 - No Wikipedia sources found
 *   1 - Wikipedia sources detected (BLOCKING)
 *   2 - Script error
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const BLUE = '\x1b[34m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

// Wikipedia patterns to detect
const WIKIPEDIA_PATTERNS = [
  /wikipedia\.org/i,
  /wikipedia\.com/i,
  /\.wikipedia\./i,
  /wikia\./i,
  /fandom\.com/i,
  /wikimedia\.org/i
];

class WikipediaValidator {
  constructor() {
    this.violations = [];
    this.filesScanned = 0;
    this.filesClean = 0;
    this.verbose = process.argv.includes('--verbose') || process.argv.includes('-v');
  }

  /**
   * Check if a string contains Wikipedia references
   */
  containsWikipedia(text) {
    if (!text || typeof text !== 'string') return false;
    return WIKIPEDIA_PATTERNS.some(pattern => pattern.test(text));
  }

  /**
   * Validate a single JSON file for Wikipedia sources
   */
  validateFile(filePath) {
    this.filesScanned++;

    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(content);

      // Check validation.source array
      if (data.validation && data.validation.source) {
        const sources = data.validation.source;

        if (Array.isArray(sources)) {
          sources.forEach((source, index) => {
            if (this.containsWikipedia(source)) {
              this.violations.push({
                file: filePath,
                field: `validation.source[${index}]`,
                value: source,
                unitDesignation: data.unit_designation || 'Unknown',
                nation: data.nation || 'Unknown',
                quarter: data.quarter || 'Unknown'
              });
            }
          });
        } else if (typeof sources === 'string') {
          if (this.containsWikipedia(sources)) {
            this.violations.push({
              file: filePath,
              field: 'validation.source',
              value: sources,
              unitDesignation: data.unit_designation || 'Unknown',
              nation: data.nation || 'Unknown',
              quarter: data.quarter || 'Unknown'
            });
          }
        }
      }

      // Also check validation.sources (alternate field name)
      if (data.validation && data.validation.sources) {
        const sources = data.validation.sources;

        if (Array.isArray(sources)) {
          sources.forEach((source, index) => {
            if (this.containsWikipedia(source)) {
              this.violations.push({
                file: filePath,
                field: `validation.sources[${index}]`,
                value: source,
                unitDesignation: data.unit_designation || 'Unknown',
                nation: data.nation || 'Unknown',
                quarter: data.quarter || 'Unknown'
              });
            }
          });
        }
      }

      if (this.violations.length === 0 || this.violations.every(v => v.file !== filePath)) {
        this.filesClean++;
        if (this.verbose) {
          console.log(`${GREEN}✓${RESET} ${path.basename(filePath)}`);
        }
      }

    } catch (error) {
      console.error(`${RED}ERROR${RESET} reading ${filePath}: ${error.message}`);
    }
  }

  /**
   * Recursively scan directory for JSON files
   */
  scanDirectory(dirPath) {
    if (!fs.existsSync(dirPath)) {
      console.error(`${RED}ERROR${RESET}: Directory not found: ${dirPath}`);
      process.exit(2);
    }

    const entries = fs.readdirSync(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);

      if (entry.isDirectory()) {
        this.scanDirectory(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('_toe.json')) {
        this.validateFile(fullPath);
      }
    }
  }

  /**
   * Print validation report
   */
  printReport() {
    console.log('\n' + '='.repeat(80));
    console.log(`${BOLD}Wikipedia Source Validation Report${RESET}`);
    console.log('='.repeat(80));
    console.log(`Files scanned: ${this.filesScanned}`);
    console.log(`Files clean:   ${GREEN}${this.filesClean}${RESET}`);
    console.log(`Violations:    ${this.violations.length > 0 ? RED : GREEN}${this.violations.length}${RESET}`);
    console.log('='.repeat(80));

    if (this.violations.length > 0) {
      console.log(`\n${RED}${BOLD}❌ WIKIPEDIA VIOLATIONS DETECTED${RESET}\n`);

      // Group by file
      const byFile = {};
      this.violations.forEach(v => {
        if (!byFile[v.file]) byFile[v.file] = [];
        byFile[v.file].push(v);
      });

      Object.keys(byFile).forEach(file => {
        const viols = byFile[file];
        const first = viols[0];

        console.log(`${RED}✗${RESET} ${BOLD}${path.basename(file)}${RESET}`);
        console.log(`  Unit: ${first.unitDesignation} (${first.nation}, ${first.quarter})`);
        console.log(`  Path: ${file}`);
        console.log(`  Violations:`);

        viols.forEach(v => {
          console.log(`    - ${v.field}: "${YELLOW}${v.value}${RESET}"`);
        });
        console.log('');
      });

      console.log(`${RED}${BOLD}REQUIRED ACTION:${RESET}`);
      console.log(`These ${this.violations.length} violations MUST be fixed before v3.0 compliance.`);
      console.log(`\nFix with:`);
      console.log(`1. Re-extract units using only Tier 1/2 authorized sources`);
      console.log(`2. Remove Wikipedia from validation.source arrays`);
      console.log(`3. Run: npm run validate:sources`);
      console.log('');
      console.log(`${BLUE}Authorized sources by nation:${RESET}`);
      console.log(`  German:  Tessin, Feldgrau, Lexikon der Wehrmacht`);
      console.log(`  Italian: TM E 30-420, Comando Supremo`);
      console.log(`  British: Army Lists, War Diaries, Regimental Histories`);
      console.log(`  American: Field Manuals, NARA records`);
      console.log('');

      return false;
    } else {
      console.log(`\n${GREEN}${BOLD}✓ ALL FILES CLEAN${RESET}`);
      console.log(`No Wikipedia sources detected. Schema v3.0 compliant.`);
      console.log('');
      return true;
    }
  }

  /**
   * Main validation entry point
   */
  run(targetPath = null) {
    console.log(`${BOLD}Wikipedia Source Validator v3.0.0${RESET}`);
    console.log('Scanning for forbidden Wikipedia sources...\n');

    // Determine target
    const target = targetPath || process.argv[2] || 'data/units';

    if (!fs.existsSync(target)) {
      console.error(`${RED}ERROR${RESET}: Target not found: ${target}`);
      console.log('\nUsage:');
      console.log('  npm run validate:sources');
      console.log('  node scripts/validate-no-wikipedia.js [directory|file]');
      console.log('  node scripts/validate-no-wikipedia.js --verbose');
      process.exit(2);
    }

    const stat = fs.statSync(target);

    if (stat.isDirectory()) {
      console.log(`Scanning directory: ${target}`);
      this.scanDirectory(target);
    } else if (stat.isFile()) {
      console.log(`Validating file: ${target}`);
      this.validateFile(target);
    }

    const success = this.printReport();
    process.exit(success ? 0 : 1);
  }
}

// Run validator if called directly
if (require.main === module) {
  const validator = new WikipediaValidator();
  validator.run();
}

module.exports = WikipediaValidator;
