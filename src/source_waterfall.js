#!/usr/bin/env node

/**
 * Source Waterfall System
 *
 * Implements 3-tier source selection with automatic escalation:
 * - Tier 1: Local primary documents (Tessin, Army Lists, Field Manuals) - confidence 90%
 * - Tier 2: Curated web sources (Feldgrau, Niehorster, etc.) - confidence 75%
 * - Tier 3: General web search (NO Wikipedia) - confidence 60%
 *
 * Automatically escalates to next tier if data missing or confidence < threshold
 */

const fs = require('fs').promises;
const path = require('path');
const zlib = require('zlib');
const { promisify } = require('util');

const gunzip = promisify(zlib.gunzip);

class SourceWaterfall {
  constructor(sourceStrategy, sourcesDir = 'Resource Documents') {
    this.sourceStrategy = sourceStrategy;
    this.sourcesDir = sourcesDir;
    this.sourceCatalog = null;
  }

  /**
   * Load source catalog
   */
  async loadSourceCatalog() {
    if (this.sourceCatalog) return this.sourceCatalog;

    try {
      const catalogPath = path.join(process.cwd(), 'sources', 'sources_catalog.json');
      const catalogData = await fs.readFile(catalogPath, 'utf-8');
      this.sourceCatalog = JSON.parse(catalogData);
      return this.sourceCatalog;
    } catch (error) {
      console.error('Warning: Could not load source catalog:', error.message);
      this.sourceCatalog = { source_categories: {} };
      return this.sourceCatalog;
    }
  }

  /**
   * Prepare source content for a unit using waterfall strategy
   *
   * @param {Object} unit - Unit object with nation, designation, quarter
   * @param {Object} strategy - Source strategy from project config
   * @returns {Object} - { content, source_name, tier, confidence, fallback_tried, metadata }
   */
  async prepare_source(unit, strategy = null) {
    const sourceStrategy = strategy || this.sourceStrategy;
    await this.loadSourceCatalog();

    const fallbackTried = [];

    // Try each tier in order
    for (const tier of sourceStrategy.waterfall_priority) {
      console.log(`  Tier ${tier.tier}: Trying ${tier.name}...`);

      try {
        const result = await this.tryTier(tier, unit);

        if (result && result.content && result.content.length > 100) {
          console.log(`  ✓ Found data in ${tier.name} (${result.content.length} chars)`);

          return {
            content: result.content,
            source_name: result.source_name,
            tier: tier.tier,
            confidence: tier.confidence_base,
            fallback_tried: fallbackTried,
            metadata: {
              unit_designation: unit.unit_designation,
              nation: unit.nation,
              quarter: unit.quarter,
              extraction_method: result.extraction_method,
              timestamp: new Date().toISOString()
            }
          };
        } else {
          fallbackTried.push({
            tier: tier.tier,
            name: tier.name,
            reason: 'insufficient_data'
          });
        }
      } catch (error) {
        console.log(`  ✗ ${tier.name} failed: ${error.message}`);
        fallbackTried.push({
          tier: tier.tier,
          name: tier.name,
          reason: error.message
        });
      }
    }

    // If we get here, all tiers failed
    throw new Error(`No sources found for ${unit.nation} ${unit.unit_designation} (${unit.quarter}) after trying all tiers`);
  }

  /**
   * Try to get data from a specific tier
   */
  async tryTier(tier, unit) {
    if (tier.tier === 1) {
      return await this.tryLocalDocuments(tier, unit);
    } else if (tier.tier === 2) {
      return await this.tryCuratedWebSources(tier, unit);
    } else if (tier.tier === 3) {
      return await this.tryWebSearch(tier, unit);
    }

    throw new Error(`Unknown tier: ${tier.tier}`);
  }

  /**
   * Tier 1: Try local primary documents
   */
  async tryLocalDocuments(tier, unit) {
    const { nation, unit_designation, quarter } = unit;

    // Determine which local sources to try based on nation
    const sourcesToTry = this.getLocalSourcesForNation(nation, tier.sources);

    for (const sourceName of sourcesToTry) {
      try {
        const sourceFile = await this.findLocalSourceFile(sourceName, nation, quarter);

        if (!sourceFile) continue;

        console.log(`    Checking: ${path.basename(sourceFile)}`);

        // Extract content from file
        const content = await this.extractFromFile(sourceFile);

        // Search for unit in content
        const extracted = this.searchContent(content, unit_designation, nation);

        if (extracted && extracted.length > 100) {
          return {
            content: extracted,
            source_name: sourceName,
            extraction_method: 'local_document_search'
          };
        }
      } catch (error) {
        console.log(`    Skip ${sourceName}: ${error.message}`);
      }
    }

    return null;
  }

  /**
   * Tier 2: Try curated web sources
   */
  async tryCuratedWebSources(tier, unit) {
    // Placeholder for web source integration
    // In production, this would:
    // 1. Check if web sources are available
    // 2. Query Feldgrau.com, Niehorster.org, etc.
    // 3. Extract relevant sections
    // 4. Return content with metadata

    console.log(`    Web sources not yet implemented - would query: ${tier.sources.join(', ')}`);
    return null;
  }

  /**
   * Tier 3: Try general web search
   */
  async tryWebSearch(tier, unit) {
    // Placeholder for web search integration
    // In production, this would:
    // 1. Construct search query
    // 2. Query search engines
    // 3. Filter out Wikipedia
    // 4. Extract content from results
    // 5. Return content with low confidence flag

    console.log(`    Web search not yet implemented - would search for: ${unit.nation} ${unit.unit_designation}`);
    return null;
  }

  /**
   * Get local source files for a nation
   */
  getLocalSourcesForNation(nation, availableSources) {
    // Normalize nation name (accept both lowercase and capitalized)
    const nationKey = nation.toLowerCase();

    const sourceMap = {
      'german': ['Tessin Wehrmacht Encyclopedia (German)'],
      'germany': ['Tessin Wehrmacht Encyclopedia (German)'],
      'italian': ['TM 30-410 British Army Handbook', 'British Army Lists (British/Commonwealth)'],
      'italy': ['TM 30-410 British Army Handbook', 'British Army Lists (British/Commonwealth)'],
      'british': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'britain': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'commonwealth': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'india': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'australia': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'new zealand': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'canada': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'south africa': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'american': ['US Field Manuals (USA)', 'TM 30-410 British Army Handbook'],
      'usa': ['US Field Manuals (USA)', 'TM 30-410 British Army Handbook'],
      'french': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook'],
      'france': ['British Army Lists (British/Commonwealth)', 'TM 30-410 British Army Handbook']
    };

    return sourceMap[nationKey] || [];
  }

  /**
   * Find a local source file
   */
  async findLocalSourceFile(sourceName, nation, quarter) {
    const basePath = path.join(process.cwd(), this.sourcesDir);

    // Map source names to directory patterns
    const dirMap = {
      'Tessin Wehrmacht Encyclopedia (German)': 'tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss',
      'British Army Lists (British/Commonwealth)': 'British Army Lists',
      'US Field Manuals (USA)': 'US Field Manuals',
      'TM 30-410 British Army Handbook': ''
    };

    const dirPattern = dirMap[sourceName];
    if (!dirPattern) return null;

    try {
      // For Tessin, use Band 03 (Afrika formations)
      if (sourceName.includes('Tessin')) {
        const tessinDir = path.join(basePath, dirPattern);
        const files = await fs.readdir(tessinDir);

        // Prefer Band 03 for North Africa, Band 08 for Panzer divisions
        const band03 = files.find(f => f.includes('Band 03') && f.includes('searchtext'));
        const band08 = files.find(f => f.includes('Band 08') && f.includes('searchtext'));

        // Return both - we'll try Band 03 first, then Band 08
        if (band03) return path.join(tessinDir, band03);
        if (band08) return path.join(tessinDir, band08);
      }

      // For British Army Lists, find the one for the quarter
      if (sourceName.includes('British Army Lists')) {
        const armyListsDir = path.join(basePath, dirPattern);
        const files = await fs.readdir(armyListsDir);

        // Map quarter to month
        const quarterMonthMap = {
          'Q1': ['jan', 'feb', 'mar'],
          'Q2': ['apr', 'may', 'jun'],
          'Q3': ['jul', 'aug', 'sep'],
          'Q4': ['oct', 'nov', 'dec']
        };

        const [year, q] = quarter.split('-');
        const months = quarterMonthMap[q] || [];

        // Find file matching year and quarter
        for (const month of months) {
          const file = files.find(f =>
            f.toLowerCase().includes(month) &&
            f.includes(year.slice(2)) &&
            f.includes('_text.txt')
          );

          if (file) return path.join(armyListsDir, file);
        }
      }

      // For TM 30-410, look in base directory
      if (sourceName.includes('TM 30-410')) {
        const files = await fs.readdir(basePath);
        const tm30410 = files.find(f => f.includes('TM30-410') && f.includes('_text.txt'));

        if (tm30410) return path.join(basePath, tm30410);
      }

      return null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Extract content from file (handles .gz, .txt, .pdf)
   */
  async extractFromFile(filePath) {
    const ext = path.extname(filePath).toLowerCase();

    if (ext === '.gz') {
      // Decompress gzip file
      const compressed = await fs.readFile(filePath);
      const decompressed = await gunzip(compressed);
      return decompressed.toString('utf-8');
    } else if (ext === '.txt') {
      // Read text file
      return await fs.readFile(filePath, 'utf-8');
    } else {
      throw new Error(`Unsupported file type: ${ext}`);
    }
  }

  /**
   * Search content for unit designation with context
   * Handles abbreviations and variations
   */
  searchContent(content, unitDesignation, nation) {
    // Generate search patterns with abbreviations and variations
    const patterns = this.generateSearchPatterns(unitDesignation, nation);

    const lines = content.split('\n');
    const contextLines = 50; // Lines before and after match
    const matchedSections = new Set(); // Avoid duplicates

    for (const pattern of patterns) {
      const regex = new RegExp(pattern, 'gi');

      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          // Found match - extract context
          const start = Math.max(0, i - contextLines);
          const end = Math.min(lines.length, i + contextLines);

          const section = lines.slice(start, end).join('\n');
          const sectionKey = `${start}-${end}`;

          if (!matchedSections.has(sectionKey)) {
            matchedSections.add(sectionKey);
          }
        }
      }
    }

    if (matchedSections.size === 0) return null;

    // Extract unique sections
    const uniqueSections = Array.from(matchedSections).map(key => {
      const [start, end] = key.split('-').map(Number);
      return lines.slice(start, end).join('\n');
    });

    // Combine all matches with separators
    return uniqueSections.map((m, idx) =>
      `--- Section ${idx + 1}: ${unitDesignation} ---\n${m}`
    ).join('\n\n');
  }

  /**
   * Generate search patterns with abbreviations
   */
  generateSearchPatterns(unitDesignation, nation) {
    const patterns = [];
    const nationKey = nation.toLowerCase();

    if (nationKey === 'german' || nationKey === 'germany') {
      // German abbreviations
      let pattern = unitDesignation;

      // Handle common abbreviations
      const abbreviations = {
        'Panzer-Division': ['Panzer-Division', 'Pz\\.?-?Div\\.?', 'Panzer Division'],
        'leichte Division': ['leichte Division', 'le\\.? Div\\.?', 'leichte Div\\.?', 'l\\.Div\\.?'],
        'Panzergrenadier': ['Panzergrenadier', 'Pz\\.?Gren\\.?', 'PzGren'],
        'Infanterie-Division': ['Infanterie-Division', 'Inf\\.?-?Div\\.?', 'ID'],
        'Afrikakorps': ['Afrikakorps', 'Afrika-Korps', 'Afrika Korps', 'DAK'],
        'Panzerarmee': ['Panzerarmee', 'Pz\\.?Armee', 'Panzer-Armee']
      };

      // Apply abbreviations
      for (const [full, abbrevs] of Object.entries(abbreviations)) {
        if (unitDesignation.includes(full)) {
          for (const abbrev of abbrevs) {
            const abbrevPattern = unitDesignation.replace(full, abbrev);
            patterns.push(abbrevPattern);
          }
        }
      }

      // Extract number and create flexible patterns
      const numberMatch = unitDesignation.match(/(\d+)/);
      if (numberMatch) {
        const number = numberMatch[1];

        // Add patterns like "15. Pz.Div.", "15.Pz.-Div.", etc.
        patterns.push(`${number}\\.?\\s*Pz\\.?-?Div\\.?`);
        patterns.push(`${number}\\.?\\s*le\\.?\\s*Div\\.?`);
        patterns.push(`${number}\\.?\\s*Panzer-Division`);
        patterns.push(`${number}\\.?\\s*leichte\\s*Division`);
      }
    } else if (nationKey === 'italian' || nationKey === 'italy') {
      // Italian patterns
      let pattern = unitDesignation;

      // Handle Italian unit types
      if (unitDesignation.includes('Division')) {
        const baseName = unitDesignation.replace(' Division', '');
        patterns.push(`${baseName}\\s*Divisione?`);
        patterns.push(`${baseName}\\s*Division`);
        patterns.push(`Div\\.?\\s*${baseName}`);
      }
    } else if (nationKey === 'british' || nationKey === 'britain' || nationKey === 'commonwealth') {
      // British/Commonwealth patterns
      const numberMatch = unitDesignation.match(/(\d+)(st|nd|rd|th)?/);
      if (numberMatch) {
        const number = numberMatch[1];

        // Add both "7th Armoured" and "7 Armoured" variants
        patterns.push(unitDesignation);
        patterns.push(unitDesignation.replace(/(\d+)(st|nd|rd|th)/, `$1`));
        patterns.push(unitDesignation.replace('Armoured', 'Armo?u?red')); // UK/US spelling
      }
    } else if (nationKey === 'american' || nationKey === 'usa') {
      // US patterns
      patterns.push(unitDesignation);
      patterns.push(unitDesignation.replace('Armored', 'Armo?u?red')); // US/UK spelling
    }

    // Always include original designation
    if (!patterns.includes(unitDesignation)) {
      patterns.unshift(unitDesignation);
    }

    return patterns;
  }
}

/**
 * Exported function for use by orchestrator
 */
async function prepare_source(unit, sourceStrategy) {
  const waterfall = new SourceWaterfall(sourceStrategy);
  return await waterfall.prepare_source(unit, sourceStrategy);
}

module.exports = {
  SourceWaterfall,
  prepare_source
};
