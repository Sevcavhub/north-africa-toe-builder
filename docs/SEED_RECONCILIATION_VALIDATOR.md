# Seed Reconciliation Validator - Learning Agent

**Version:** 1.0.0
**Pattern:** Anthropic Evaluator-Optimizer with Learning
**Status:** ✅ Implemented, Ready for Integration
**Date:** October 15, 2025

---

## Overview

The Seed Reconciliation Validator is a specialized agent that ensures ALL seed units are properly extracted and learns from edge cases to gradually automate decisions.

**Key Innovation:** This agent implements the Anthropic **Evaluator-Optimizer pattern with cumulative learning**, enabling it to get smarter over time without hardcoding rules.

---

## The Problem

### What Happened with XX Corps Q2 1941:

1. **Seed said:** "XX Mobile Corps Q2 1941" (95% confidence, Tobruk siege)
2. **Agent found:** "Formal establishment Q3 1941 (August 15)"
3. **Agent decided:** "Unit didn't exist Q2, I'll extract Q3 instead"
4. **Result:** Agent autonomously contradicted validated seed data

**This is wrong because:**
- Seed validated from **authoritative sources** (US Army CMH, Imperial War Museum)
- Agent used **secondary web sources** (generals.dk, dbpedia)
- **Seed sources > Agent sources**, but agent overruled anyway
- No human-in-loop checkpoint
- Unit actually DID exist informally and fought at Tobruk Q2!

### Root Cause:

**Missing workflow checkpoint** - no mechanism to detect seed-agent contradictions and flag for human review.

---

## The Solution: Anthropic Evaluator-Optimizer Pattern

### Pattern Reference

From [Anthropic Claude Cookbooks - Agents](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents):

**Evaluator-Optimizer Workflow:**
```
Loop:
  ↓
  Generate (Agent extracts units)
  ↓
  Evaluate (Validator compares vs seed)
  ↓
  Check Pattern Database (Is this known case?)
  ├─ Known Pattern (≥95% confidence)?
  │  └─ Auto-apply learned resolution
  │
  ├─ Similar Pattern (75-94% confidence)?
  │  └─ Recommend action, flag for review
  │
  └─ Unknown Pattern (<75% confidence)?
     └─ Human review required
  ↓
  Store Human Decision
  ↓
  Update Pattern Database
  ↓
  Increase Confidence for Future Cases
```

### Three Core Components

**1. Evaluator (Seed Reconciliation Validator)**
- Compares extracted units vs seed list
- Detects: missing units, wrong quarters, contradictions
- Checks pattern database for known cases
- Generates human review queue for unknowns

**2. Pattern Database (Cumulative Memory)**
- Stores learned patterns from previous human decisions
- Tracks confidence scores based on occurrence frequency
- Enables automation as patterns become clear

**3. Optimizer (Learning Mechanism)**
- After each human decision: stores pattern
- Next similar case: applies pattern if confidence ≥95%
- Gradual automation: 0% → 50% → 95% over multiple cases

---

## How It Works

### Phase 1: Evaluation (Systematic Comparison)

**Input:**
- Seed units: 117 units from validated sources
- Extracted units: All completed TO&E files
- Pattern database: Previously learned patterns

**Process:**

```javascript
for (each seed_unit) {
  extracted = find_extracted_unit(seed_unit);

  if (!extracted) {
    // Missing unit
    discrepancy = {
      type: "MISSING",
      seed: seed_unit,
      agent_conclusion: check_agent_logs(),
      pattern_match: check_pattern_database("missing_unit"),
      recommendation: generate_options()
    };

    if (pattern_match.confidence >= 95) {
      auto_resolve(discrepancy, pattern_match);
    } else if (pattern_match.confidence >= 75) {
      recommend_action(discrepancy, pattern_match);
    } else {
      flag_for_human_review(discrepancy);
    }
  }

  else if (extracted.quarter !== seed_unit.quarter) {
    // Quarter mismatch
    discrepancy = {
      type: "QUARTER_MISMATCH",
      seed_quarter: seed_unit.quarter,
      extracted_quarter: extracted.quarter,
      seed_battles: seed_unit.battles,
      pattern_match: check_pattern_database("quarter_mismatch"),
      recommendation: generate_options()
    };

    // Same logic: auto, recommend, or human review
  }

  else if (extracted.confidence < seed_unit.confidence) {
    // Confidence drop
    flag_for_review("Lower confidence than seed");
  }
}
```

### Phase 2: Pattern Matching (Memory Lookup)

**Pattern Database Structure:**

```json
{
  "pattern_id": "informal_italian_corps_q2_1941",
  "pattern_type": "informal_units",
  "confidence": 95,
  "occurrences": 3,

  "conditions": {
    "nation": "Italy",
    "unit_type": "corps",
    "quarter_mismatch": true,
    "seed_has_battles": true,
    "agent_found_later_quarter": true
  },

  "resolution": "EXTRACT_AS_INFORMAL",
  "reasoning": "Seed authoritative. Unit fought in battles listed. Extract as informal/transitional status.",

  "human_decisions": [
    {
      "date": "2025-10-15",
      "user": "chapm",
      "decision": "EXTRACT_Q2_AS_INFORMAL",
      "unit": "XX Mobile Corps 1941-Q2"
    },
    {
      "date": "2025-10-16",
      "user": "chapm",
      "decision": "EXTRACT_Q2_AS_INFORMAL",
      "unit": "XXI Corps 1940-Q4"
    },
    {
      "date": "2025-10-18",
      "user": "chapm",
      "decision": "EXTRACT_Q2_AS_INFORMAL",
      "unit": "XIX Corps 1943-Q1"
    }
  ],

  "applicable_to": ["Italian corps", "Informal units", "Q1-Q2 1941"],
  "automation_status": "READY (confidence ≥95%)"
}
```

**Pattern Matching Logic:**

```python
def check_pattern(discrepancy):
    for pattern in pattern_database:
        match_score = 0

        # Check conditions
        if discrepancy.nation == pattern.conditions.nation:
            match_score += 25
        if discrepancy.unit_type == pattern.conditions.unit_type:
            match_score += 25
        if discrepancy.seed_has_battles == pattern.conditions.seed_has_battles:
            match_score += 25
        if discrepancy.agent_reason == pattern.conditions.agent_reason:
            match_score += 25

        if match_score >= 75:
            return {
                "pattern": pattern,
                "match_score": match_score,
                "confidence": pattern.confidence,
                "recommendation": pattern.resolution
            }

    return {"pattern": "UNKNOWN", "confidence": 0}
```

### Phase 3: Human Review (Unknown Patterns)

**When pattern confidence < 75%:**

**Output to Human Review Queue:**

```json
{
  "priority": "HIGH",
  "unit": "Italian XX Mobile Corps 1941-Q2",
  "issue": "Seed-agent contradiction on existence quarter",

  "seed_evidence": {
    "designation": "XX Mobile Corps",
    "quarter": "1941-Q2",
    "battles": ["Tobruk siege"],
    "confidence": 95,
    "sources": ["US Army CMH", "Imperial War Museum", "Comando Supremo"]
  },

  "agent_findings": {
    "found_quarter": "1941-Q3",
    "reason": "Formal establishment August 15, 1941",
    "confidence": 90,
    "sources": ["generals.dk", "dbpedia.org"]
  },

  "analysis": {
    "conflict": "Seed claims Q2 combat operations (Tobruk), agent claims unit didn't exist until Q3",
    "source_hierarchy": "Seed sources (CMH > Comando Supremo) > Agent sources (dbpedia)",
    "battle_evidence": "Tobruk siege April-June 1941 matches Q2 timing"
  },

  "options": [
    {
      "option": "A: EXTRACT_Q2_AS_INFORMAL",
      "reasoning": "Seed authoritative. Unit fought at Tobruk Q2. Informal before formal Q3 establishment.",
      "evidence_weight": "HIGH"
    },
    {
      "option": "B: EXTRACT_Q3_ONLY",
      "reasoning": "Agent found formal establishment Q3. Q2 ops may have been under different structure.",
      "evidence_weight": "MEDIUM"
    },
    {
      "option": "C: EXTRACT_BOTH_Q2_Q3",
      "reasoning": "Q2 informal/transitional, Q3 formal. Captures complete history.",
      "evidence_weight": "HIGH"
    },
    {
      "option": "D: MANUAL_RESEARCH",
      "reasoning": "Conflicting evidence. Requires Tessin/primary archives.",
      "evidence_weight": "MEDIUM"
    }
  ],

  "user_prompt": "Your decision? (A/B/C/D)",
  "pattern_learning_opportunity": true
}
```

**User responds:** "A - Extract Q2 as informal"

### Phase 4: Learning (Store Decision)

**After human decision:**

```javascript
function storeLearning(discrepancy, user_decision) {
  // Create or update pattern
  pattern = {
    pattern_id: generate_id(discrepancy),
    pattern_type: classify_type(discrepancy),

    conditions: extract_conditions(discrepancy),
    resolution: user_decision.option,
    reasoning: user_decision.reasoning,

    occurrences: 1,
    confidence: calculate_initial_confidence(1), // = 45%

    human_decisions: [{
      date: today(),
      user: current_user,
      decision: user_decision.option,
      unit: discrepancy.unit
    }],

    automation_status: "PENDING (need 3+ consistent decisions)"
  };

  pattern_database.push(pattern);
  save(pattern_database);
}
```

**Confidence Calculation:**

```
Initial confidence (1 occurrence):  45%
After 2 occurrences (same decision): 70%
After 3 occurrences (same decision): 85%
After 5+ occurrences (same decision): 95%

Ready for automation: confidence ≥ 95%
```

### Phase 5: Automation (Future Cases)

**Next time similar pattern appears:**

```javascript
// New discrepancy: Italian XXI Corps Q2 1941, agent found Q3
discrepancy_new = {
  nation: "Italy",
  unit_type: "corps",
  seed_quarter: "1941-Q2",
  agent_found_quarter: "1941-Q3",
  seed_battles: ["Operation Compass"],
  seed_confidence: 95
};

// Check pattern database
pattern_match = check_pattern(discrepancy_new);

if (pattern_match.confidence >= 95) {
  // AUTO-RESOLVE!
  apply_resolution(pattern_match.resolution);

  report.auto_resolved.push({
    unit: "XXI Corps 1941-Q2",
    pattern_applied: "informal_italian_corps_q2_1941",
    resolution: "EXTRACT_Q2_AS_INFORMAL",
    confidence: 95,
    human_review_required: false
  });

  // Increment pattern occurrence counter
  pattern_match.pattern.occurrences++;
  pattern_match.pattern.confidence = Math.min(98, confidence + 1);

} else if (pattern_match.confidence >= 75) {
  // RECOMMEND (still flag for review but with suggestion)
  report.review_recommended.push({
    unit: "XXI Corps 1941-Q2",
    pattern_match: pattern_match,
    recommendation: "EXTRACT_Q2_AS_INFORMAL (similar to 3 previous cases)",
    confidence: 85,
    human_confirmation_requested: true
  });

} else {
  // HUMAN REQUIRED (confidence < 75%)
  report.human_required.push(discrepancy_new);
}
```

---

## Learning Progression Example

### Case: Italian Informal Corps

**Occurrence 1 (XX Corps Q2 1941):**
- Pattern: UNKNOWN
- Confidence: 0%
- Action: Human review required
- User decision: "Extract Q2 as informal"
- **After:** Pattern created, confidence = 45%

**Occurrence 2 (XXI Corps Q2 1941):**
- Pattern: MATCH (informal_italian_corps)
- Confidence: 70%
- Action: Recommend "Extract Q2 as informal"
- User decision: "Yes, extract as informal"
- **After:** Pattern confirmed, confidence = 85%

**Occurrence 3 (XIX Corps Q1 1943):**
- Pattern: MATCH (informal_italian_corps)
- Confidence: 85%
- Action: Recommend "Extract Q1 as informal"
- User decision: "Yes, extract as informal"
- **After:** Pattern solid, confidence = 95%

**Occurrence 4+ (Any Italian Corps informal):**
- Pattern: MATCH (informal_italian_corps)
- Confidence: 95%
- **Action: AUTO-RESOLVE** ✅
- No human review needed!
- Pattern confidence increases to 96%, 97%, 98% (caps at 98%)

**Automation achieved!** 🎉

---

## Integration into Orchestration Workflow

### Current Workflow (Missing Checkpoint):

```
Phase 1: Source Extraction
  ↓
Phase 2: Organization Building
  ↓
Phase 3: Equipment Distribution
  ↓
Phase 4: Aggregation
  ↓
Phase 5: Validation (schema, historical accuracy)
  ↓
Phase 6: Output Generation
  ↓
[PROJECT COMPLETE] ❌ No seed reconciliation!
```

### Updated Workflow (With Checkpoint):

```
Phase 1-5: (same)
  ↓
Phase 6: Final Validation
  ├─ Schema Validator
  ├─ Historical Accuracy Validator
  └─ 🆕 SEED RECONCILIATION VALIDATOR
      ↓
      Evaluate all extracted vs seed
      ↓
      Check pattern database
      ↓
      Generate reconciliation report:
      ├─ ✅ Auto-resolved (confidence ≥95%)
      ├─ ⚠️  Review recommended (75-94%)
      └─ ❌ Human required (<75%)
      ↓
      [HUMAN REVIEW CHECKPOINT]
      ↓
      User resolves flagged items
      ↓
      Update pattern database
      ↓
      Increment confidence scores
  ↓
Phase 7: Output Generation
  ↓
[PROJECT COMPLETE] ✅ All seed units accounted for!
```

### Orchestrator Integration Code:

```javascript
// In orchestrator after Phase 5
async function runPhase6_FinalValidation() {
  console.log('\n📋 Phase 6: Final Validation with Seed Reconciliation');

  // Load inputs
  const seedUnits = await loadSeedUnits();
  const extractedUnits = await scanExtractedUnits();
  const patternDatabase = await loadPatternDatabase();
  const humanDecisions = await loadHumanDecisions();

  // Run seed reconciliation validator
  const reconciliation = await runAgent('seed_reconciliation_validator', {
    seed_units: seedUnits,
    extracted_units: extractedUnits,
    pattern_database: patternDatabase,
    human_decisions: humanDecisions
  });

  // Display results
  console.log(`\n✅ Fully matched: ${reconciliation.summary.fully_matched}`);
  console.log(`🤖 Auto-resolved: ${reconciliation.summary.auto_resolved}`);
  console.log(`⚠️  Review recommended: ${reconciliation.summary.review_recommended}`);
  console.log(`❌ Human required: ${reconciliation.summary.human_required}`);

  // If human review needed
  if (reconciliation.summary.human_required > 0) {
    console.log('\n⏸️  PAUSE: Human review required');
    await saveReviewQueue(reconciliation.human_review_queue);

    console.log(`\n📝 Review queue saved to: data/output/human_review_queue.json`);
    console.log(`   Please review ${reconciliation.summary.human_required} items`);

    // Wait for user
    const decisions = await promptUserDecisions(reconciliation.human_review_queue);

    // Store learning
    for (const decision of decisions) {
      await storePattern(decision.discrepancy, decision.user_choice);
    }

    // Update pattern database
    await savePatternDatabase(patternDatabase);

    console.log('\n✅ Learning stored, pattern database updated');
  }

  // Check if ready for completion
  if (!reconciliation.validation_checklist.ready_for_completion) {
    throw new Error('Seed reconciliation incomplete - resolve discrepancies first');
  }

  console.log('\n✅ Phase 6 Complete: All seed units accounted for');
}
```

---

## Files and Structure

### Created Files:

**1. Agent Definition:**
- `agents/seed_reconciliation_validator.json` - Full agent specification

**2. Pattern Database:**
- `data/pattern_database.json` - Learning memory (starts empty, grows over time)

**3. Human Decision Log:**
- `data/human_decisions.json` - Audit trail of all user decisions

**4. Output Files (per run):**
- `data/output/reconciliation_report.json` - Full comparison report
- `data/output/human_review_queue.json` - Items requiring user decisions
- `data/output/updated_pattern_database.json` - New patterns learned

---

## Benefits

### Immediate Benefits:

1. **✅ Catches seed-agent contradictions** - No more missed units like XX Corps Q2
2. **✅ Human-in-loop for uncertain cases** - Agent can't override seed autonomously
3. **✅ Comprehensive accountability** - Every seed unit tracked: extracted, skipped, or flagged
4. **✅ Clear decision prompts** - User gets evidence, options, recommendations

### Long-Term Benefits (After Learning):

1. **📈 Gradual automation** - Common patterns become automatic
2. **🧠 Knowledge accumulation** - Pattern database grows smarter over time
3. **⚡ Faster processing** - High-confidence patterns auto-resolved
4. **📊 Audit trail** - Full history of decisions and reasoning
5. **🔁 Reusable patterns** - Learning transfers to similar projects

---

## Success Metrics

**Tracking automation growth:**

```json
{
  "statistics": {
    "total_runs": 10,
    "total_discrepancies": 47,

    "resolution_breakdown": {
      "auto_resolved": 23,
      "review_recommended": 8,
      "human_required": 16
    },

    "automation_rate": "48.9%",
    "automation_trend": [
      {"run": 1, "rate": "0%"},
      {"run": 2, "rate": "15%"},
      {"run": 5, "rate": "35%"},
      {"run": 10, "rate": "48.9%"}
    ],

    "patterns_learned": 12,
    "automation_ready_patterns": 5
  }
}
```

**Goal:** 80%+ automation rate after 20-30 extractions

---

## Testing Plan

### Test 1: XX Corps Q2 1941 Case

**Input:**
- Seed: XX Corps Q2 1941 (Tobruk siege, 95% confidence)
- Extracted: None (agent found Q3 only)

**Expected Output:**
- Discrepancy type: MISSING
- Pattern match: UNKNOWN (0% confidence)
- Action: HUMAN_REVIEW_REQUIRED
- Options: Extract Q2 informal, Extract Q3, Extract both, Manual research

**User Decision:** "A - Extract Q2 as informal"

**Expected Learning:**
- New pattern created: "informal_italian_corps_q2_1941"
- Initial confidence: 45%
- Applicable to: Italian corps, informal units, Q1-Q2 1941

### Test 2: Similar Case (After Learning)

**Input:**
- Seed: XXI Corps Q2 1941
- Extracted: None (agent found Q3)

**Expected Output:**
- Discrepancy type: MISSING
- Pattern match: informal_italian_corps (70% confidence)
- Action: REVIEW_RECOMMENDED
- Recommendation: "Extract Q2 as informal (matches 1 previous case)"

**User Decision:** "Yes, extract Q2 as informal"

**Expected Learning:**
- Pattern confidence: 70% → 85%
- Occurrences: 1 → 2
- Status: "Approaching automation threshold"

### Test 3: Automation Ready (After 3+ Cases)

**Input:**
- Seed: X Corps Q1 1941
- Extracted: None (agent found Q2)

**Expected Output:**
- Pattern match: informal_italian_corps (95% confidence)
- Action: **AUTO_RESOLVED**
- Resolution: "EXTRACT_Q1_AS_INFORMAL"
- Human review: NOT REQUIRED

**Expected Learning:**
- Pattern confidence: 95% → 96%
- Occurrences: 3 → 4
- Status: "AUTOMATION_ACTIVE"

---

## Next Steps

### Implementation Checklist:

- [x] Design agent using Anthropic patterns
- [x] Create pattern database structure
- [x] Add agent to agent_catalog.json
- [ ] Integrate into orchestrator workflow
- [ ] Test with XX Corps Q2 1941 case
- [ ] Run full seed reconciliation
- [ ] Process human review queue
- [ ] Validate pattern learning
- [ ] Monitor automation rate growth

### User Actions Required:

1. **Review and approve agent design** (this document)
2. **Test single case** (XX Corps Q2 1941)
3. **Process human review queue** (make decisions on flagged items)
4. **Validate pattern storage** (check pattern_database.json updated correctly)
5. **Run second case** (verify pattern matching works)

---

## Conclusion

The Seed Reconciliation Validator implements Anthropic's Evaluator-Optimizer pattern to solve a critical workflow gap: ensuring all seed units are properly extracted while learning from edge cases like informal units.

**Key Innovation:** The agent doesn't require hardcoded rules for every edge case. Instead, it learns from human decisions and gradually automates common patterns, achieving 80%+ automation after sufficient learning.

**Critical Safety:** The agent NEVER overrides seed data autonomously. It only auto-resolves when pattern confidence ≥95% based on 3+ consistent human decisions.

**Result:** A smart validation checkpoint that gets smarter over time, prevents missing units, and reduces human workload as patterns become clear.

---

**Status:** ✅ Ready for integration and testing
**Contact:** See orchestrator implementation for integration details
**Version:** 1.0.0 (2025-10-15)
