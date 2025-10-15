#!/usr/bin/env node

/**
 * Automated Agent Output Validator
 *
 * Enforces anti-hallucination rules by rejecting invalid agent outputs.
 * Run this BEFORE accepting any agent response.
 *
 * Usage:
 *   const { validateAgentOutput } = require('./scripts/lib/validate_agent_output');
 *   const validation = validateAgentOutput(agentOutput, 'historical_research');
 *   if (!validation.valid) throw new Error('Agent output REJECTED');
 */

const fs = require('fs');

/**
 * Validate agent output against anti-hallucination rules
 *
 * @param {object} agentOutput - JSON output from agent
 * @param {string} agentId - Which agent produced this
 * @returns {object} {valid: boolean, errors: string[], warnings: string[], critical: string[]}
 */
function validateAgentOutput(agentOutput, agentId) {
  const errors = [];

  // Rule 1: Check structure exists
  if (!agentOutput.research_results) {
    errors.push('CRITICAL: Missing research_results section');
    return { valid: false, errors, warnings: [], critical: errors };
  }

  const results = agentOutput.research_results;

  // Rule 2: verified_from_sources must have quotes for all non-null fields
  if (results.verified_from_sources) {
    for (const [field, data] of Object.entries(results.verified_from_sources)) {
      // Skip null fields (explicitly not found)
      if (data === null) {
        console.log(`  ℹ️  Field '${field}' marked as NOT FOUND (null) - OK`);
        continue;
      }

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
          'document shows',
          'the document says'
        ];

        const isGeneric = genericPhrases.some(phrase =>
          data.source_quote.toLowerCase().includes(phrase)
        );

        if (isGeneric) {
          errors.push(`VIOLATION: Field '${field}' has generic source_quote (not verbatim): "${data.source_quote.substring(0, 50)}..."`);
        }

        // Check minimum length (should be 10-30 words, at least 50 chars for meaningful quote)
        if (data.source_quote.length < 50) {
          errors.push(`VIOLATION: Field '${field}' source_quote too short (${data.source_quote.length} chars, need 50+ for verbatim quote)`);
        }

        // NEW RULE: Check if quote supports numerical claims
        // If value contains numbers, quote must also contain numbers
        if (data.value && typeof data.value === 'object') {
          const hasNumericalValue = Object.values(data.value).some(v => typeof v === 'number');
          const quoteHasNumbers = /\d+/.test(data.source_quote);

          if (hasNumericalValue && !quoteHasNumbers) {
            errors.push(`VIOLATION: Field '${field}' claims numerical data (${JSON.stringify(data.value)}) but source_quote contains NO NUMBERS - likely hallucination`);
          }
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

      if (data.confidence === undefined) {
        errors.push(`VIOLATION: Estimate '${field}' lacks confidence score`);
      }

      if (data.confidence > 60) {
        errors.push(`WARNING: Estimate '${field}' has high confidence (${data.confidence}%), should be in verified section with source quote`);
      }

      if (!data.caveats || data.caveats.length === 0) {
        errors.push(`WARNING: Estimate '${field}' lacks caveats explaining limitations`);
      }
    }
  }

  // Rule 4: sources_checked must exist and be non-empty
  if (!results.sources_checked || results.sources_checked.length === 0) {
    errors.push('VIOLATION: sources_checked is empty - must document search process');
  }

  // Rule 4b: WIKIPEDIA ABSOLUTELY FORBIDDEN
  // Check all source fields for Wikipedia/wiki references
  const wikiPatterns = [/wikipedia/i, /\bwiki\b/i, /wikia/i, /fandom\.com/i];

  // Check verified_from_sources
  if (results.verified_from_sources) {
    for (const [field, data] of Object.entries(results.verified_from_sources)) {
      if (data && data.source) {
        const hasWiki = wikiPatterns.some(pattern => pattern.test(data.source));
        if (hasWiki) {
          errors.push(`VIOLATION: Field '${field}' cites WIKIPEDIA/WIKI source: "${data.source}" - FORBIDDEN per Rule 6`);
        }
      }
    }
  }

  // Check sources_checked
  if (results.sources_checked) {
    for (const sourceEntry of results.sources_checked) {
      if (sourceEntry.source) {
        const hasWiki = wikiPatterns.some(pattern => pattern.test(sourceEntry.source));
        if (hasWiki && sourceEntry.status === 'FOUND') {
          // Wiki found and USED = violation
          errors.push(`VIOLATION: sources_checked includes WIKIPEDIA/WIKI as FOUND source: "${sourceEntry.source}" - must be EXCLUDED`);
        }
      }
    }
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
  const warnings = errors.filter(e => e.startsWith('WARNING'));
  const valid = criticalErrors.length === 0;

  return {
    valid,
    errors,
    warnings,
    critical: criticalErrors
  };
}

/**
 * Test with known good and bad examples
 */
function runTests() {
  console.log('='.repeat(60));
  console.log('Anti-Hallucination Validation Tests');
  console.log('='.repeat(60));
  console.log();

  // Test 1: Good output (should pass)
  console.log('Test 1: Good Output (should PASS)');
  console.log('-'.repeat(60));

  const goodOutput = {
    research_results: {
      verified_from_sources: {
        commander: {
          value: 'Gen. Carlo Spatocco',
          source: 'Lewin (1998) Rommel as Military Commander, page 47',
          source_quote: 'The Italian XX Motorised Corps under General Spatocco was placed under German operational control in March 1941',
          confidence: 85
        },
        corps_hq_personnel: null
      },
      estimates_when_no_data: {
        corps_hq_personnel: {
          estimated_value: { total: 100 },
          derivation_method: 'Estimated 1/3 of formal corps HQ based on minimal informal structure',
          confidence: 30,
          caveats: ['No primary source available', 'Could be ±50 personnel']
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

  const result1 = validateAgentOutput(goodOutput, 'historical_research');
  console.log(`Result: ${result1.valid ? '✅ PASS' : '❌ FAIL'}`);
  if (result1.errors.length > 0) {
    console.log('Issues:', result1.errors);
  }
  console.log();

  // Test 2: Bad output - fact without source quote (should fail)
  console.log('Test 2: Missing source_quote (should FAIL)');
  console.log('-'.repeat(60));

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

  const result2 = validateAgentOutput(badOutput1, 'historical_research');
  console.log(`Result: ${result2.valid ? '✅ PASS' : '❌ FAIL (expected)'}`);
  console.log('Critical errors:', result2.critical);
  console.log();

  // Test 3: Bad output - generic quote (should fail)
  console.log('Test 3: Generic source_quote (should FAIL)');
  console.log('-'.repeat(60));

  const badOutput2 = {
    research_results: {
      verified_from_sources: {
        corps_hq_personnel: {
          value: { total: 300 },
          source: 'TME 30-420 para 50',
          source_quote: 'The source states that corps headquarters has staff.',  // Generic!
          confidence: 65
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

  const result3 = validateAgentOutput(badOutput2, 'historical_research');
  console.log(`Result: ${result3.valid ? '✅ PASS' : '❌ FAIL (expected)'}`);
  console.log('Critical errors:', result3.critical);
  console.log();

  // Test 4: Bad output - estimate in verified section (should warn)
  console.log('Test 4: Low-confidence data in verified section (should WARN)');
  console.log('-'.repeat(60));

  const badOutput3 = {
    research_results: {
      verified_from_sources: {
        corps_hq_personnel: {
          value: { total: 300 },
          source: 'TME 30-420 para 50',
          source_quote: 'Corps headquarters consists of General Staff sections including Operations, Intelligence, and Personnel departments plus support elements',
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

  const result4 = validateAgentOutput(badOutput3, 'historical_research');
  console.log(`Result: ${result4.valid ? '✅ PASS' : '❌ FAIL'}`);
  console.log('Warnings:', result4.warnings);
  console.log();

  console.log('='.repeat(60));
  console.log('Validation Tests Complete');
  console.log('='.repeat(60));
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
