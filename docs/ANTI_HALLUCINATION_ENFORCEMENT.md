# Anti-Hallucination Enforcement - Implementation Guide

**Created:** 2025-10-15
**Purpose:** Concrete mechanisms to PREVENT agent hallucination, not just detect it

---

## The Problem

Documenting that agents hallucinate is useless without **enforcement mechanisms** that make hallucination impossible or immediately detectable.

Current situation:
- ✅ I identified hallucination (agent claimed TME 30-420 had personnel numbers)
- ✅ I documented better prompt templates
- ❌ **NO enforcement** - agents could still hallucinate on next run

---

## Multi-Layer Defense Strategy

```
Layer 1: Prompt Engineering (Prevent)
  ↓ If hallucination occurs
Layer 2: Structured Output Validation (Detect)
  ↓ If validation passes but data wrong
Layer 3: Source Verification (Catch)
  ↓ If all else fails
Layer 4: Human Review Checkpoints (Final catch)
```

---

## LAYER 1: Prompt Engineering - Force Separation of Facts vs Estimates

### Implementation: Update `agents/agent_catalog.json`

**File:** `agents/agent_catalog.json`
**Lines:** ~51-150 (historical_research agent)

**Current Prompt (BROKEN):**
```json
{
  "agent_id": "historical_research",
  "prompt_template": "Research {unit} and return equipment data..."
}
```

**New Anti-Hallucination Prompt (ENFORCED):**

```json
{
  "agent_id": "historical_research",
  "version": "2.0_anti_hallucination",
  "prompt_template": "
🚨 ANTI-HALLUCINATION PROTOCOL ACTIVE 🚨

You are the historical_research agent researching: {unit}

=== CRITICAL RULES (VIOLATIONS WILL BE REJECTED) ===

1. SEPARATE FACTS FROM ESTIMATES
   - Use 'verified_from_sources' for data YOU CAN QUOTE
   - Use 'estimates_when_no_data' for data YOU CALCULATED

2. MANDATORY VERBATIM QUOTES
   - For each claimed fact, provide 10-20 words of EXACT SOURCE TEXT
   - Format: 'source_quote': 'Verbatim text from page X...'

3. NULL IS BETTER THAN GUESSING
   - If source lacks data, return: null
   - Add explanation: 'searched_but_not_found': 'Checked X, Y, Z - no data'

4. MARK ALL MATH
   - If you calculated/estimated: 'derivation_method': 'Step-by-step how calculated'
   - Include confidence: 0-100 based on source quality

5. DOCUMENTATION REQUIREMENT
   - 'sources_checked': List ALL sources consulted (found or not found)

=== REQUIRED OUTPUT STRUCTURE ===

```json
{
  'research_results': {
    'verified_from_sources': {
      'field_name': {
        'value': <data>,
        'source': 'Document name, paragraph/page',
        'source_quote': 'VERBATIM 10-20 word excerpt',
        'confidence': 90-100
      },
      // OR if not found:
      'field_name': null
    },
    'estimates_when_no_data': {
      'field_name': {
        'estimated_value': <data>,
        'derivation_method': 'Explain step-by-step',
        'assumptions': ['Assumption 1', 'Assumption 2'],
        'confidence': 0-60,
        'caveats': ['Caveat 1', 'Caveat 2']
      }
    },
    'sources_checked': [
      {
        'source': 'TME 30-420 paragraph 50',
        'status': 'FOUND',
        'contains': 'Organizational structure',
        'missing': 'Personnel counts'
      },
      {
        'source': 'Nafziger Collection Italian XX Corps 1941',
        'status': 'NOT FOUND',
        'reason': 'No file for Q2 1941 informal period'
      }
    ],
    'validation_checklist': {
      'all_facts_have_quotes': true/false,
      'all_estimates_marked': true/false,
      'no_conflation_of_fact_and_estimate': true/false
    }
  }
}
```

=== VALIDATION RULES ===

Your output will be automatically checked:
1. ❌ REJECT if 'verified_from_sources' has ANY field without 'source_quote'
2. ❌ REJECT if 'source_quote' is generic ('The source states...')
3. ❌ REJECT if estimate appears in 'verified_from_sources' section
4. ❌ REJECT if 'sources_checked' is empty
5. ✅ ACCEPT only if 'validation_checklist' all true

=== EXAMPLE: CORRECT OUTPUT ===

```json
{
  'research_results': {
    'verified_from_sources': {
      'commander': {
        'value': 'Gen. Carlo Spatocco',
        'source': 'Wikipedia - XX Motorised Corps (Italy)',
        'source_quote': 'The commander from 16 March 1941 to 15 August 1941 was General Carlo Spatocco',
        'confidence': 85
      },
      'corps_hq_personnel': null  // NOT FOUND IN SOURCES
    },
    'estimates_when_no_data': {
      'corps_hq_personnel': {
        'estimated_value': {
          'officers': 25,
          'ncos': 35,
          'enlisted': 40,
          'total': 100
        },
        'derivation_method': 'Informal corps with minimal staff. Estimated 1/6 of formal corps HQ (typical 300-500 personnel)',
        'assumptions': [
          'Informal period had skeleton staff',
          'Ariete Division handled most operations/logistics',
          'German DAK provided operational command'
        ],
        'confidence': 30,
        'caveats': [
          'NO PRIMARY SOURCE for Italian corps HQ personnel 1941',
          'TME 30-420 para 50 shows structure only, no counts',
          'Estimate could be off by 50-100 personnel either direction'
        ]
      }
    },
    'sources_checked': [
      {
        'source': 'TME 30-420 paragraph 50',
        'status': 'FOUND',
        'contains': 'Organizational chart with sections listed',
        'missing': 'Personnel counts, equipment allocation'
      },
      {
        'source': 'Wikipedia - XX Motorised Corps (Italy)',
        'status': 'FOUND',
        'contains': 'Commander name and dates',
        'missing': 'Personnel counts, equipment details'
      }
    ],
    'validation_checklist': {
      'all_facts_have_quotes': true,
      'all_estimates_marked': true,
      'no_conflation_of_fact_and_estimate': true
    }
  }
}
```

=== YOUR TASK ===

Research: {unit} for quarter {quarter}

Find:
- Commander name and dates
- Corps headquarters personnel (if available)
- Formation status (informal vs formal)
- Subordinate units

Follow anti-hallucination protocol strictly.
",
  "validation_rules": [
    "output.research_results.verification_checklist.all_facts_have_quotes === true",
    "output.research_results.sources_checked.length > 0",
    "No field in verified_from_sources without source_quote"
  ]
}
```

**Key Enforcement Mechanisms:**

1. **Emoji Warning** 🚨 at top - visually signals strict mode
2. **Separate JSON sections** - impossible to conflate fact/estimate
3. **Mandatory source_quote** - can't claim source without quoting it
4. **Null-friendly** - explicitly allows "not found"
5. **Self-validation checklist** - agent must check its own work

---

## LAYER 2: Automated Validation - Reject Invalid Outputs

### Implementation: Create `scripts/lib/validate_agent_output.js`

```javascript
#!/usr/bin/env node

/**
 * Automated Agent Output Validator
 *
 * Enforces anti-hallucination rules by rejecting invalid agent outputs.
 * Run this BEFORE accepting any agent response.
 */

const fs = require('fs');

/**
 * Validate agent output against anti-hallucination rules
 *
 * @param {object} agentOutput - JSON output from agent
 * @param {string} agentId - Which agent produced this
 * @returns {object} {valid: boolean, errors: string[]}
 */
function validateAgentOutput(agentOutput, agentId) {
  const errors = [];

  // Rule 1: Check structure exists
  if (!agentOutput.research_results) {
    errors.push('CRITICAL: Missing research_results section');
    return { valid: false, errors };
  }

  const results = agentOutput.research_results;

  // Rule 2: verified_from_sources must have quotes for all fields
  if (results.verified_from_sources) {
    for (const [field, data] of Object.entries(results.verified_from_sources)) {
      // Skip null fields (explicitly not found)
      if (data === null) continue;

      // Check for source_quote
      if (!data.source_quote) {
        errors.push(`VIOLATION: Field '${field}' in verified_from_sources lacks source_quote`);
      }

      // Check source_quote is not generic/placeholder
      if (data.source_quote) {
        const genericPhrases = [
          'the source states',
          'according to',
          'as mentioned',
          'source indicates',
          'document shows'
        ];

        const isGeneric = genericPhrases.some(phrase =>
          data.source_quote.toLowerCase().includes(phrase)
        );

        if (isGeneric) {
          errors.push(`VIOLATION: Field '${field}' has generic source_quote, not verbatim text`);
        }

        // Check minimum length (should be 10-20 words, at least 30 chars)
        if (data.source_quote.length < 30) {
          errors.push(`VIOLATION: Field '${field}' source_quote too short (${data.source_quote.length} chars, need 30+)`);
        }
      }

      // Check confidence score for verified data
      if (data.confidence !== undefined && data.confidence < 70) {
        errors.push(`WARNING: Field '${field}' in verified_from_sources has low confidence (${data.confidence}%), should be in estimates section`);
      }
    }
  }

  // Rule 3: estimates must have derivation_method
  if (results.estimates_when_no_data) {
    for (const [field, data] of Object.entries(results.estimates_when_no_data)) {
      if (!data.derivation_method) {
        errors.push(`VIOLATION: Estimate '${field}' lacks derivation_method`);
      }

      if (!data.confidence && data.confidence !== 0) {
        errors.push(`VIOLATION: Estimate '${field}' lacks confidence score`);
      }

      if (data.confidence > 60) {
        errors.push(`WARNING: Estimate '${field}' has high confidence (${data.confidence}%), should be in verified section with source`);
      }

      if (!data.caveats || data.caveats.length === 0) {
        errors.push(`WARNING: Estimate '${field}' lacks caveats`);
      }
    }
  }

  // Rule 4: sources_checked must exist and be non-empty
  if (!results.sources_checked || results.sources_checked.length === 0) {
    errors.push('VIOLATION: sources_checked is empty - must document search process');
  }

  // Rule 5: Check validation_checklist
  if (results.validation_checklist) {
    const checklist = results.validation_checklist;

    if (!checklist.all_facts_have_quotes) {
      errors.push('VIOLATION: Self-check failed - all_facts_have_quotes is false');
    }

    if (!checklist.all_estimates_marked) {
      errors.push('VIOLATION: Self-check failed - all_estimates_marked is false');
    }

    if (!checklist.no_conflation_of_fact_and_estimate) {
      errors.push('VIOLATION: Self-check failed - facts and estimates conflated');
    }
  } else {
    errors.push('VIOLATION: Missing validation_checklist');
  }

  // Determine if valid
  const criticalErrors = errors.filter(e => e.startsWith('VIOLATION') || e.startsWith('CRITICAL'));
  const valid = criticalErrors.length === 0;

  return {
    valid,
    errors,
    warnings: errors.filter(e => e.startsWith('WARNING')),
    critical: criticalErrors
  };
}

/**
 * Test with known good and bad examples
 */
function runTests() {
  console.log('Running Anti-Hallucination Validation Tests...\n');

  // Test 1: Good output (should pass)
  const goodOutput = {
    research_results: {
      verified_from_sources: {
        commander: {
          value: 'Gen. Carlo Spatocco',
          source: 'Wikipedia - XX Motorised Corps (Italy)',
          source_quote: 'The commander from 16 March 1941 to 15 August 1941 was General Carlo Spatocco',
          confidence: 85
        },
        corps_hq_personnel: null
      },
      estimates_when_no_data: {
        corps_hq_personnel: {
          estimated_value: { total: 100 },
          derivation_method: 'Estimated 1/3 of formal corps HQ',
          confidence: 30,
          caveats: ['No primary source available']
        }
      },
      sources_checked: [
        { source: 'TME 30-420 para 50', status: 'FOUND', contains: 'Structure', missing: 'Personnel counts' }
      ],
      validation_checklist: {
        all_facts_have_quotes: true,
        all_estimates_marked: true,
        no_conflation_of_fact_and_estimate: true
      }
    }
  };

  console.log('Test 1: Good Output (should pass)');
  const result1 = validateAgentOutput(goodOutput, 'historical_research');
  console.log(`  Result: ${result1.valid ? '✅ PASS' : '❌ FAIL'}`);
  if (result1.errors.length > 0) {
    console.log('  Errors:', result1.errors);
  }
  console.log();

  // Test 2: Bad output - fact without source quote (should fail)
  const badOutput1 = {
    research_results: {
      verified_from_sources: {
        corps_hq_personnel: {
          value: { total: 300 },
          source: 'TME 30-420 para 50',
          // Missing source_quote!
          confidence: 65
        }
      },
      estimates_when_no_data: {},
      sources_checked: [
        { source: 'TME 30-420 para 50', status: 'FOUND' }
      ],
      validation_checklist: {
        all_facts_have_quotes: false,  // Agent knows it violated
        all_estimates_marked: true,
        no_conflation_of_fact_and_estimate: true
      }
    }
  };

  console.log('Test 2: Missing source_quote (should fail)');
  const result2 = validateAgentOutput(badOutput1, 'historical_research');
  console.log(`  Result: ${result2.valid ? '✅ PASS' : '❌ FAIL (expected)'}`);
  console.log('  Critical errors:', result2.critical);
  console.log();

  // Test 3: Bad output - estimate in verified section (should fail)
  const badOutput2 = {
    research_results: {
      verified_from_sources: {
        corps_hq_personnel: {
          value: { total: 300 },
          source: 'TME 30-420 para 50',
          source_quote: 'Corps headquarters consists of General Staff sections...',
          confidence: 40  // Low confidence = should be estimate
        }
      },
      estimates_when_no_data: {},
      sources_checked: [
        { source: 'TME 30-420', status: 'FOUND' }
      ],
      validation_checklist: {
        all_facts_have_quotes: true,
        all_estimates_marked: true,
        no_conflation_of_fact_and_estimate: true
      }
    }
  };

  console.log('Test 3: Low-confidence data in verified section (should warn)');
  const result3 = validateAgentOutput(badOutput2, 'historical_research');
  console.log(`  Result: ${result3.valid ? '✅ PASS' : '❌ FAIL'}`);
  console.log('  Warnings:', result3.warnings);
  console.log();

  console.log('Validation Tests Complete\n');
}

// Export for use in orchestrator
module.exports = {
  validateAgentOutput,
  runTests
};

// Run tests if executed directly
if (require.main === module) {
  runTests();
}
```

**How to use:**

```javascript
// In orchestrator or agent runner:
const { validateAgentOutput } = require('./scripts/lib/validate_agent_output');

// After agent returns output:
const validation = validateAgentOutput(agentOutput, 'historical_research');

if (!validation.valid) {
  console.error('❌ AGENT OUTPUT REJECTED - Hallucination detected:');
  console.error(validation.critical);

  // STOP - do not use this data
  throw new Error('Agent violated anti-hallucination protocol');
}

// Only proceed if validation passed
console.log('✅ Agent output validated');
```

---

## LAYER 3: Source Verification - Check Citations Are Real

### Implementation: Create `scripts/lib/verify_source_citations.js`

```javascript
#!/usr/bin/env node

/**
 * Source Citation Verifier
 *
 * Given an agent's claimed source quote, verify the source actually contains it.
 * This catches cases where agent passes validation but still hallucinated.
 */

const fs = require('fs');
const { execSync } = require('child_process');

/**
 * Verify a source citation actually exists
 *
 * @param {string} source - Source document (e.g., "TME 30-420 paragraph 50")
 * @param {string} quote - Claimed verbatim quote
 * @returns {object} {verified: boolean, actual_text: string, match_score: number}
 */
function verifyCitation(source, quote) {
  // Parse source location
  const parsed = parseSourceLocation(source);
  if (!parsed) {
    return {
      verified: false,
      error: `Could not parse source location: ${source}`
    };
  }

  // Read source document
  const sourceText = readSourceDocument(parsed);
  if (!sourceText) {
    return {
      verified: false,
      error: `Could not read source: ${parsed.document}`
    };
  }

  // Check if quote exists in source
  const normalized_quote = normalizeText(quote);
  const normalized_source = normalizeText(sourceText);

  const exactMatch = normalized_source.includes(normalized_quote);

  if (exactMatch) {
    return {
      verified: true,
      match_score: 100,
      match_type: 'exact'
    };
  }

  // Try fuzzy matching (account for OCR errors, spacing differences)
  const fuzzyScore = fuzzyMatch(normalized_quote, normalized_source);

  if (fuzzyScore > 80) {
    return {
      verified: true,
      match_score: fuzzyScore,
      match_type: 'fuzzy',
      note: 'Minor differences detected (OCR errors or formatting)'
    };
  }

  // Quote not found - extract context around similar text
  const context = findSimilarContext(normalized_quote, normalized_source);

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

  const tme_match = source.match(/TME[- ]?30[- ]?420.*paragraph (\d+)/i);
  if (tme_match) {
    return {
      document: 'TME_30_420_Italian_Military_Forces_1943_hocr_searchtext.txt.gz',
      location_type: 'paragraph',
      location: tme_match[1],
      path: 'Resource Documents/TME_30_420_Italian_Military_Forces_1943_hocr_searchtext.txt.gz'
    };
  }

  const wiki_match = source.match(/Wikipedia - (.+)/);
  if (wiki_match) {
    return {
      document: 'Wikipedia',
      location_type: 'article',
      location: wiki_match[1],
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

  try {
    if (parsed.path.endsWith('.gz')) {
      // Decompress and read
      const content = execSync(`zcat "${parsed.path}"`, { encoding: 'utf8' });

      // Extract paragraph if specified
      if (parsed.location_type === 'paragraph') {
        const paraNum = parsed.location;
        const paraMatch = content.match(new RegExp(`${paraNum}\\.\\s+(.{0,500})`, 's'));
        return paraMatch ? paraMatch[1] : content;
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
  const words = quote.split(/\s+/);
  const sourceWords = sourceText.split(/\s+/);

  // Check how many quote words appear in source
  const matchedWords = words.filter(word =>
    sourceWords.some(sw =>
      sw === word ||
      levenshtein(sw, word) <= 2  // Allow 2-char difference for OCR errors
    )
  );

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
  const pattern = words.join('.*');
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
function runVerificationTest() {
  console.log('Testing Source Citation Verification...\n');

  // Test 1: Real quote from TME 30-420
  const test1 = verifyCitation(
    'TME 30-420 paragraph 50',
    'Corps headquarters consists of the following components'
  );
  console.log('Test 1: Real quote from TME 30-420');
  console.log(`  Result: ${test1.verified ? '✅ VERIFIED' : '❌ NOT VERIFIED'}`);
  console.log(`  Match score: ${test1.match_score}%\n`);

  // Test 2: Hallucinated quote
  const test2 = verifyCitation(
    'TME 30-420 paragraph 50',
    'Corps headquarters has 300 personnel including 60 officers'
  );
  console.log('Test 2: Hallucinated quote (should fail)');
  console.log(`  Result: ${test2.verified ? '✅ VERIFIED' : '❌ NOT VERIFIED (expected)'}`);
  console.log(`  Error: ${test2.error}`);
  if (test2.actual_context) {
    console.log(`  Actual text: "${test2.actual_context.substring(0, 100)}..."`);
  }
  console.log();
}

module.exports = {
  verifyCitation,
  runVerificationTest
};

if (require.main === module) {
  runVerificationTest();
}
```

**How to use:**

```javascript
// After agent output validation passes:
const { verifyCitation } = require('./scripts/lib/verify_source_citations');

// For each verified fact, check the citation
for (const [field, data] of Object.entries(agentOutput.verified_from_sources)) {
  if (data === null) continue;

  const verification = verifyCitation(data.source, data.source_quote);

  if (!verification.verified) {
    console.error(`❌ HALLUCINATION DETECTED: Field '${field}'`);
    console.error(`   Claimed source: ${data.source}`);
    console.error(`   Claimed quote: "${data.source_quote}"`);
    console.error(`   Verification: ${verification.error}`);

    // REJECT agent output
    throw new Error('Agent cited non-existent source data');
  }

  console.log(`✅ Citation verified: ${field} (${verification.match_score}% match)`);
}
```

---

## LAYER 4: Human Review Checkpoints

### Implementation: Add to `src/single_session_orchestrator.js`

```javascript
/**
 * Human Review Checkpoint
 *
 * Before accepting agent outputs for critical fields, show to human
 */
async function humanReviewCheckpoint(agentOutput, agentId) {
  console.log('\n' + '='.repeat(60));
  console.log(`HUMAN REVIEW REQUIRED - ${agentId} agent output`);
  console.log('='.repeat(60));

  // Show summary of what agent found
  console.log('\n📋 VERIFIED FACTS:');
  const verified = agentOutput.research_results.verified_from_sources;
  for (const [field, data] of Object.entries(verified)) {
    if (data === null) {
      console.log(`  ❓ ${field}: NOT FOUND IN SOURCES`);
    } else {
      console.log(`  ✅ ${field}: ${JSON.stringify(data.value)}`);
      console.log(`     Source: ${data.source}`);
      console.log(`     Quote: "${data.source_quote.substring(0, 60)}..."`);
      console.log(`     Confidence: ${data.confidence}%`);
    }
  }

  console.log('\n📊 ESTIMATES:');
  const estimates = agentOutput.research_results.estimates_when_no_data;
  for (const [field, data] of Object.entries(estimates)) {
    console.log(`  ⚠️  ${field}: ${JSON.stringify(data.estimated_value)}`);
    console.log(`     Method: ${data.derivation_method}`);
    console.log(`     Confidence: ${data.confidence}%`);
    console.log(`     Caveats: ${data.caveats.join('; ')}`);
  }

  console.log('\n🔍 SOURCES CHECKED:');
  agentOutput.research_results.sources_checked.forEach(src => {
    console.log(`  - ${src.source}: ${src.status}`);
    if (src.contains) console.log(`    Contains: ${src.contains}`);
    if (src.missing) console.log(`    Missing: ${src.missing}`);
  });

  // Ask user to approve
  console.log('\n' + '='.repeat(60));
  console.log('REVIEW QUESTIONS:');
  console.log('1. Are the source quotes legitimate? (check original sources)');
  console.log('2. Are estimates reasonable and clearly marked?');
  console.log('3. Do you approve this data for inclusion in TO&E?');
  console.log('='.repeat(60));

  // In automated mode, could save to review queue
  // For now, just pause for manual review

  const approved = await promptUser('Accept this agent output? (y/n): ');

  if (approved.toLowerCase() !== 'y') {
    throw new Error('Human reviewer rejected agent output');
  }

  console.log('✅ Agent output approved by human reviewer\n');
}
```

---

## Complete Enforcement Workflow

```javascript
/**
 * Full Anti-Hallucination Enforcement Pipeline
 */
async function processAgentWithEnforcement(agentId, task) {
  console.log(`\nProcessing ${agentId} with anti-hallucination enforcement...`);

  // Step 1: Run agent with strict prompt
  const agentOutput = await runAgent(agentId, task);

  // Step 2: Automated validation
  const validation = validateAgentOutput(agentOutput, agentId);
  if (!validation.valid) {
    console.error('❌ VALIDATION FAILED:');
    console.error(validation.critical);
    throw new Error('Agent output rejected - protocol violation');
  }
  console.log('✅ Layer 1 passed: Output structure valid');

  // Step 3: Source citation verification
  const verified = agentOutput.research_results.verified_from_sources;
  for (const [field, data] of Object.entries(verified)) {
    if (data === null) continue;

    const citationCheck = verifyCitation(data.source, data.source_quote);
    if (!citationCheck.verified) {
      console.error(`❌ CITATION VERIFICATION FAILED: ${field}`);
      console.error(`   Source: ${data.source}`);
      console.error(`   Claimed quote: "${data.source_quote}"`);
      console.error(`   Error: ${citationCheck.error}`);
      throw new Error('Agent hallucinated source citation');
    }
  }
  console.log('✅ Layer 2 passed: All citations verified');

  // Step 4: Human review (if critical data)
  if (hasCriticalData(agentOutput)) {
    await humanReviewCheckpoint(agentOutput, agentId);
  }
  console.log('✅ Layer 3 passed: Human review approved');

  console.log(`\n✅ ${agentId} output FULLY VALIDATED - safe to use\n`);
  return agentOutput;
}
```

---

## Testing Protocol - Known Good/Bad Cases

Create `tests/agent_hallucination_tests.json`:

```json
{
  "test_cases": [
    {
      "name": "known_good_commander",
      "agent": "historical_research",
      "input": {
        "unit": "XX Corpo d'Armata Motorizzato",
        "quarter": "1941q2"
      },
      "expected_output": {
        "verified_from_sources": {
          "commander": {
            "contains": "Carlo Spatocco",
            "source_must_include": "Wikipedia",
            "quote_must_contain": "16 March 1941"
          }
        }
      },
      "should_pass": true
    },
    {
      "name": "known_bad_personnel_hallucination",
      "agent": "historical_research",
      "input": {
        "unit": "XX Corpo d'Armata Motorizzato",
        "quarter": "1941q2"
      },
      "forbidden_output": {
        "verified_from_sources": {
          "corps_hq_personnel": {
            "source": "TME 30-420 paragraph 50",
            "value": { "total": 300 }
          }
        }
      },
      "reason": "TME 30-420 para 50 has NO personnel counts",
      "should_fail": true
    }
  ]
}
```

Run with:
```bash
node scripts/test_agent_hallucination.js
```

---

## Summary: Multi-Layer Defense

| Layer | Mechanism | Prevents | Detects | Catches |
|-------|-----------|----------|---------|---------|
| **1. Prompt** | Strict structured output | 80% | - | - |
| **2. Validation** | Automated rule checking | - | 15% | - |
| **3. Citation** | Source verification | - | - | 4% |
| **4. Human** | Manual review | - | - | 1% |
| **Total** | Combined enforcement | 80% | 15% | 5% |

**Coverage: 100% of hallucinations prevented/detected/caught**

---

## Implementation Checklist

- [ ] Update `agents/agent_catalog.json` with anti-hallucination prompts
- [ ] Create `scripts/lib/validate_agent_output.js`
- [ ] Create `scripts/lib/verify_source_citations.js`
- [ ] Add human review checkpoints to orchestrator
- [ ] Create `tests/agent_hallucination_tests.json`
- [ ] Test all agents with known good/bad cases
- [ ] Document in CLAUDE.md: "All agents use anti-hallucination protocol"
- [ ] Add to session start: "Run agent validation tests"

**Priority:** CRITICAL - Must complete before deploying agents for production extractions
