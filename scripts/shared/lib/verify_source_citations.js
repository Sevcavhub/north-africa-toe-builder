#!/usr/bin/env node

/**
 * Source Citation Verifier
 *
 * Given an agent's claimed source quote, verify the source actually contains it.
 * This catches cases where agent passes validation but still hallucinated.
 *
 * Usage:
 *   const { verifyCitation } = require('./scripts/lib/verify_source_citations');
 *   const result = verifyCitation('TME 30-420 paragraph 50', 'Corps headquarters consists of...');
 *   if (!result.verified) console.error('Hallucination detected!');
 */

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

/**
 * Verify a source citation actually exists
 *
 * @param {string} source - Source document (e.g., "TME 30-420 paragraph 50")
 * @param {string} quote - Claimed verbatim quote
 * @returns {object} {verified: boolean, actual_text?: string, match_score: number}
 */
function verifyCitation(source, quote) {
  // Parse source location
  const parsed = parseSourceLocation(source);
  if (!parsed) {
    return {
      verified: false,
      error: `Could not parse source location: ${source}`,
      match_score: 0
    };
  }

  // Read source document
  const sourceText = readSourceDocument(parsed);
  if (!sourceText) {
    return {
      verified: false,
      error: `Could not read source: ${parsed.document}`,
      match_score: 0
    };
  }

  // Check if quote exists in source
  const normalizedQuote = normalizeText(quote);
  const normalizedSource = normalizeText(sourceText);

  const exactMatch = normalizedSource.includes(normalizedQuote);

  if (exactMatch) {
    return {
      verified: true,
      match_score: 100,
      match_type: 'exact'
    };
  }

  // Try fuzzy matching (account for OCR errors, spacing differences)
  const fuzzyScore = fuzzyMatch(normalizedQuote, normalizedSource);

  if (fuzzyScore > 80) {
    // NEW RULE: If quote contains numbers, verify those numbers exist in source
    // This catches hallucinations where agent adds fake data to a real quote
    const quoteNumbers = quote.match(/\d+/g) || [];
    const sourceNumbers = new Set(sourceText.match(/\d+/g) || []);

    if (quoteNumbers.length > 0) {
      const missingNumbers = quoteNumbers.filter(num => !sourceNumbers.has(num));

      if (missingNumbers.length > 0) {
        return {
          verified: false,
          match_score: fuzzyScore,
          error: `Quote contains numbers (${missingNumbers.join(', ')}) NOT found in source`,
          suggestion: 'Agent likely added fabricated numerical data to a real quote',
          note: 'Text structure matches but numerical claims are hallucinated'
        };
      }
    }

    return {
      verified: true,
      match_score: fuzzyScore,
      match_type: 'fuzzy',
      note: 'Minor differences detected (OCR errors or formatting)'
    };
  }

  // Quote not found - extract context around similar text
  const context = findSimilarContext(normalizedQuote, normalizedSource);

  return {
    verified: false,
    match_score: fuzzyScore,
    error: 'Quote not found in source',
    actual_context: context,
    suggestion: 'Agent may have hallucinated or misquoted'
  };
}

/**
 * Parse source location string
 */
function parseSourceLocation(source) {
  // Examples:
  // "TME 30-420 paragraph 50"
  // "Wikipedia - XX Motorised Corps (Italy)"
  // "Nafziger Collection - Italian XX Corps 1941"

  const tmeMatch = source.match(/TME[- ]?30[- ]?420.*paragraph (\d+)/i);
  if (tmeMatch) {
    return {
      document: 'TME_30_420_Italian_Military_Forces_1943_hocr_searchtext.txt.gz',
      location_type: 'paragraph',
      location: tmeMatch[1],
      path: path.join(__dirname, '../../Resource Documents/TME_30_420_Italian_Military_Forces_1943_hocr_searchtext.txt.gz')
    };
  }

  const wikiMatch = source.match(/Wikipedia - (.+)/);
  if (wikiMatch) {
    return {
      document: 'Wikipedia',
      location_type: 'article',
      location: wikiMatch[1],
      path: null  // Web source - would need WebFetch
    };
  }

  return null;
}

/**
 * Read source document content
 */
function readSourceDocument(parsed) {
  if (!parsed.path) {
    return null;  // Web sources not supported yet
  }

  if (!fs.existsSync(parsed.path)) {
    console.warn(`Source file not found: ${parsed.path}`);
    return null;
  }

  try {
    if (parsed.path.endsWith('.gz')) {
      // Decompress and read using Node.js zlib (Windows compatible)
      const compressedData = fs.readFileSync(parsed.path);
      const content = zlib.gunzipSync(compressedData).toString('utf8');

      // Extract paragraph if specified
      if (parsed.location_type === 'paragraph') {
        const paraNum = parsed.location;
        // Look for paragraph number followed by period and content
        const paraRegex = new RegExp(`${paraNum}\\.\\s+(.{0,2000})`, 's');
        const paraMatch = content.match(paraRegex);
        if (paraMatch) {
          return paraMatch[0];  // Return paragraph and some context
        }
        // If specific paragraph not found, return entire content for fuzzy matching
        return content;
      }

      return content;
    } else {
      return fs.readFileSync(parsed.path, 'utf8');
    }
  } catch (err) {
    console.error(`Error reading source: ${err.message}`);
    return null;
  }
}

/**
 * Normalize text for comparison
 */
function normalizeText(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')  // Remove punctuation
    .replace(/\s+/g, ' ')           // Normalize whitespace
    .trim();
}

/**
 * Fuzzy match - account for OCR errors
 */
function fuzzyMatch(quote, sourceText) {
  const words = quote.split(/\s+/).filter(w => w.length > 2);  // Only words > 2 chars
  const sourceWords = new Set(sourceText.split(/\s+/).filter(w => w.length > 2));

  // Check how many quote words appear in source
  const matchedWords = words.filter(word => {
    // Exact match
    if (sourceWords.has(word)) return true;

    // Check for similar words (Levenshtein distance <= 2)
    for (const sw of sourceWords) {
      if (levenshtein(sw, word) <= 2) return true;
    }

    return false;
  });

  return (matchedWords.length / words.length) * 100;
}

/**
 * Simple Levenshtein distance
 */
function levenshtein(a, b) {
  const matrix = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Find similar context in source
 */
function findSimilarContext(quote, sourceText) {
  const words = quote.split(/\s+/).slice(0, 5);  // First 5 words
  const pattern = words.join('.*?');
  const regex = new RegExp(pattern, 'i');

  const match = sourceText.match(regex);
  if (match) {
    const startIdx = Math.max(0, match.index - 50);
    const endIdx = Math.min(sourceText.length, match.index + match[0].length + 50);
    return sourceText.substring(startIdx, endIdx);
  }

  return null;
}

/**
 * Test verification
 */
function runVerificationTests() {
  console.log('='.repeat(60));
  console.log('Source Citation Verification Tests');
  console.log('='.repeat(60));
  console.log();

  // Test 1: Real quote from TME 30-420
  console.log('Test 1: Real quote from TME 30-420 (should VERIFY)');
  console.log('-'.repeat(60));

  const test1 = verifyCitation(
    'TME 30-420 paragraph 50',
    'Corps headquarters consists of the following components'
  );
  console.log(`Result: ${test1.verified ? '✅ VERIFIED' : '❌ NOT VERIFIED'}`);
  console.log(`Match score: ${test1.match_score}%`);
  console.log(`Match type: ${test1.match_type || 'none'}`);
  console.log();

  // Test 2: Hallucinated quote (should FAIL)
  console.log('Test 2: Hallucinated quote (should FAIL)');
  console.log('-'.repeat(60));

  const test2 = verifyCitation(
    'TME 30-420 paragraph 50',
    'Corps headquarters has 60 officers, 90 NCOs, and 150 enlisted personnel totaling 300 staff'
  );
  console.log(`Result: ${test2.verified ? '✅ VERIFIED' : '❌ NOT VERIFIED (expected)'}`);
  console.log(`Match score: ${test2.match_score}%`);
  console.log(`Error: ${test2.error}`);
  if (test2.actual_context) {
    console.log(`Actual text found: "${test2.actual_context.substring(0, 100)}..."`);
  }
  console.log();

  // Test 3: Partial match with OCR errors (should verify with fuzzy)
  console.log('Test 3: Quote with minor OCR differences (should VERIFY fuzzy)');
  console.log('-'.repeat(60));

  const test3 = verifyCitation(
    'TME 30-420 paragraph 50',
    'Corps headquarters consists of following components General Staff'
  );
  console.log(`Result: ${test3.verified ? '✅ VERIFIED' : '❌ NOT VERIFIED'}`);
  console.log(`Match score: ${test3.match_score}%`);
  console.log(`Match type: ${test3.match_type || 'none'}`);
  if (test3.note) console.log(`Note: ${test3.note}`);
  console.log();

  console.log('='.repeat(60));
  console.log('Citation Verification Tests Complete');
  console.log('='.repeat(60));
}

module.exports = {
  verifyCitation,
  runVerificationTests
};

if (require.main === module) {
  runVerificationTests();
}
